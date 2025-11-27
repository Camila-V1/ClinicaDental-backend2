#!/usr/bin/env python
"""
Script para ver información completa de todos los usuarios y sus datos asociados.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo
from agenda.models import Cita
from historial_clinico.models import HistorialClinico
from tratamientos.models import PlanDeTratamiento
from facturacion.models import Pago
from django.db import connection
from tenants.models import Clinica

print("=" * 100)
print("🔐 CREDENCIALES Y DATOS DE TODOS LOS USUARIOS")
print("=" * 100)
print()

# Conectar al tenant
try:
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    connection.set_tenant(tenant)
    print(f"✅ Conectado al tenant: {tenant.nombre}")
    print()
except Clinica.DoesNotExist:
    print("❌ No se encontró el tenant 'clinica_demo'")
    sys.exit(1)

usuarios = Usuario.objects.all().order_by('tipo_usuario', 'email')

print(f"Total de usuarios: {usuarios.count()}")
print()

for usuario in usuarios:
    print("─" * 100)
    print(f"👤 {usuario.full_name}")
    print("─" * 100)
    print(f"📧 Email:        {usuario.email}")
    
    # Password según tipo de usuario
    if usuario.tipo_usuario == 'PACIENTE':
        password = "paciente123"
    elif usuario.tipo_usuario == 'ODONTOLOGO':
        password = "odontologo123"
    else:
        password = "admin123"
    
    print(f"🔑 Password:     {password}")
    print(f"👥 Tipo:         {usuario.get_tipo_usuario_display()}")
    print(f"📱 FCM Token:    {'✅ REGISTRADO' if usuario.fcm_token else '❌ NO REGISTRADO'}")
    print(f"🆔 ID:           {usuario.id}")
    print()
    
    if usuario.tipo_usuario == 'PACIENTE':
        # Obtener perfil de paciente
        try:
            perfil_paciente = PerfilPaciente.objects.get(usuario=usuario)
        except PerfilPaciente.DoesNotExist:
            print("⚠️  Este usuario no tiene perfil de paciente creado")
            print()
            continue
        
        # Citas
        citas = Cita.objects.filter(paciente=perfil_paciente)
        print(f"📅 CITAS: {citas.count()} total")
        if citas.exists():
            pendientes = citas.filter(estado='PENDIENTE').count()
            confirmadas = citas.filter(estado='CONFIRMADA').count()
            completadas = citas.filter(estado='COMPLETADA').count()
            canceladas = citas.filter(estado='CANCELADA').count()
            print(f"   • Pendientes:   {pendientes}")
            print(f"   • Confirmadas:  {confirmadas}")
            print(f"   • Completadas:  {completadas}")
            print(f"   • Canceladas:   {canceladas}")
        else:
            print("   ❌ NO TIENE CITAS")
        print()
        
        # Historial Clínico
        historial = HistorialClinico.objects.filter(paciente=perfil_paciente).first()
        if historial:
            print(f"📋 HISTORIAL CLÍNICO: ✅ EXISTE")
            episodios_count = historial.episodios.count()
            print(f"   • Episodios: {episodios_count}")
            if episodios_count > 0:
                ultimo_episodio = historial.episodios.order_by('-fecha_atencion').first()
                print(f"   • Última atención: {ultimo_episodio.fecha_atencion.strftime('%d/%m/%Y')}")
        else:
            print(f"📋 HISTORIAL CLÍNICO: ❌ NO EXISTE")
        print()
        
        # Planes de Tratamiento
        planes = PlanDeTratamiento.objects.filter(paciente=perfil_paciente)
        print(f"🦷 PLANES DE TRATAMIENTO: {planes.count()} total")
        if planes.exists():
            for plan in planes:
                items = plan.items.count()
                completados = plan.items.filter(estado='COMPLETADO').count()
                print(f"   • Plan #{plan.id} ({plan.get_estado_display()}):")
                print(f"     - Items: {items} total, {completados} completados")
                print(f"     - Costo: Bs. {plan.costo_total}")
        else:
            print("   ❌ NO TIENE PLANES DE TRATAMIENTO")
        print()
        
        # Pagos
        pagos = Pago.objects.filter(paciente=perfil_paciente)
        print(f"💰 PAGOS: {pagos.count()} total")
        if pagos.exists():
            completados = pagos.filter(estado='COMPLETADO')
            pendientes = pagos.filter(estado='PENDIENTE')
            total_pagado = sum(p.monto for p in completados)
            total_pendiente = sum(p.monto for p in pendientes)
            print(f"   • Completados: {completados.count()} (Bs. {total_pagado})")
            print(f"   • Pendientes:  {pendientes.count()} (Bs. {total_pendiente})")
        else:
            print("   ❌ NO TIENE PAGOS")
        print()
    
    elif usuario.tipo_usuario == 'ODONTOLOGO':
        # Obtener perfil de odontólogo
        try:
            perfil_odontologo = PerfilOdontologo.objects.get(usuario=usuario)
        except PerfilOdontologo.DoesNotExist:
            print("⚠️  Este usuario no tiene perfil de odontólogo creado")
            print()
            continue
        
        # Citas como odontólogo
        citas = Cita.objects.filter(odontologo=perfil_odontologo)
        print(f"📅 CITAS ASIGNADAS: {citas.count()} total")
        if citas.exists():
            pendientes = citas.filter(estado='PENDIENTE').count()
            confirmadas = citas.filter(estado='CONFIRMADA').count()
            completadas = citas.filter(estado='COMPLETADA').count()
            canceladas = citas.filter(estado='CANCELADA').count()
            print(f"   • Pendientes:   {pendientes}")
            print(f"   • Confirmadas:  {confirmadas}")
            print(f"   • Completadas:  {completadas}")
            print(f"   • Canceladas:   {canceladas}")
        else:
            print("   ❌ NO TIENE CITAS")
        print()
        
        # Planes de tratamiento creados
        planes = PlanDeTratamiento.objects.filter(odontologo=perfil_odontologo)
        print(f"🦷 PLANES CREADOS: {planes.count()} total")
        if planes.exists():
            propuestos = planes.filter(estado='PROPUESTO').count()
            aceptados = planes.filter(estado='ACEPTADO').count()
            en_progreso = planes.filter(estado='EN_PROGRESO').count()
            completados = planes.filter(estado='COMPLETADO').count()
            print(f"   • Propuestos:   {propuestos}")
            print(f"   • Aceptados:    {aceptados}")
            print(f"   • En Progreso:  {en_progreso}")
            print(f"   • Completados:  {completados}")
        else:
            print("   ❌ NO HA CREADO PLANES")
        print()
    
    elif usuario.tipo_usuario == 'ADMIN':
        print(f"👨‍💼 ADMINISTRADOR - Acceso completo al sistema")
        print()

print("=" * 100)
print()
print("💡 NOTAS:")
print("   • Todas las contraseñas son de prueba")
print("   • PACIENTES: password = 'paciente123'")
print("   • ODONTOLOGOS: password = 'odontologo123'")
print("   • ADMIN: password = 'admin123'")
print()
print("=" * 100)
