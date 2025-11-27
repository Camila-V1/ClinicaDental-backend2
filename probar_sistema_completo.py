#!/usr/bin/env python
"""
Script para probar el sistema completo de notificaciones automáticas.
Simula completar una cita y verifica que se envíe la notificación.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario
from agenda.models import Cita
from django.db import connection
from tenants.models import Clinica
from django.utils import timezone

print("=" * 80)
print("🧪 PROBAR NOTIFICACIÓN AUTOMÁTICA AL COMPLETAR CITA")
print("=" * 80)
print()

# Conectar al tenant
try:
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    connection.set_tenant(tenant)
    print(f"✅ Conectado al tenant: {tenant.schema_name}")
    print()
except Clinica.DoesNotExist:
    print("❌ No se encontró el tenant 'clinica_demo'")
    sys.exit(1)

# Verificar que María García tenga el token FCM
paciente = Usuario.objects.filter(email='paciente@clinica-demo.com').first()

if not paciente:
    print("❌ No se encontró el paciente María García")
    sys.exit(1)

if not paciente.fcm_token:
    print("❌ María García no tiene token FCM registrado")
    print()
    print("Ejecuta primero: python probar_notificacion.py")
    sys.exit(1)

print(f"👤 Paciente: {paciente.full_name}")
print(f"📱 Token FCM: {paciente.fcm_token[:50]}...")
print()

# Buscar citas pendientes o en progreso del paciente
print("─" * 80)
print("🔍 BUSCANDO CITAS DISPONIBLES PARA COMPLETAR")
print("─" * 80)
print()

citas_disponibles = Cita.objects.filter(
    paciente=paciente,
    estado__in=['PENDIENTE', 'EN_PROGRESO', 'CONFIRMADA']
).order_by('fecha_hora')

if not citas_disponibles.exists():
    print("⚠️  No hay citas disponibles para completar")
    print()
    print("Opciones:")
    print("1. Crear una cita nueva")
    print("2. Usar una cita que ya fue completada (para re-probar)")
    print()
    
    # Buscar alguna cita completada
    citas_completadas = Cita.objects.filter(
        paciente=paciente,
        estado='COMPLETADA'
    ).order_by('-fecha_hora')[:3]
    
    if citas_completadas.exists():
        print("Citas completadas encontradas:")
        for idx, cita in enumerate(citas_completadas, 1):
            tiene_valoracion = hasattr(cita, 'valoracion')
            valoracion_text = "✅ Ya valorada" if tiene_valoracion else "❌ Sin valoración"
            print(f"  {idx}. Cita #{cita.id} - {cita.fecha_hora.strftime('%d/%m/%Y %H:%M')} - {valoracion_text}")
        
        print()
        try:
            seleccion = int(input("Selecciona una cita para re-probar (o 0 para salir): "))
            if seleccion == 0:
                sys.exit(0)
            
            if seleccion < 1 or seleccion > citas_completadas.count():
                print("❌ Selección inválida")
                sys.exit(1)
            
            cita = list(citas_completadas)[seleccion - 1]
            
            # Si tiene valoración, eliminarla para poder re-probar
            if hasattr(cita, 'valoracion'):
                print(f"\n⚠️  La cita ya tiene una valoración. ¿Eliminarla para re-probar? (s/n)")
                respuesta = input().lower()
                if respuesta == 's':
                    cita.valoracion.delete()
                    print("✅ Valoración eliminada")
                else:
                    print("❌ Cancelado")
                    sys.exit(0)
            
            # Cambiar el estado para forzar la señal
            print(f"\n🔄 Cambiando estado de COMPLETADA a EN_PROGRESO temporalmente...")
            cita.estado = 'EN_PROGRESO'
            cita.save(update_fields=['estado'])
            print("✅ Estado cambiado")
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Cancelado")
            sys.exit(0)
    else:
        print("❌ No hay citas disponibles")
        sys.exit(1)
else:
    # Mostrar citas disponibles
    print(f"Encontradas {citas_disponibles.count()} citas:")
    print()
    
    for idx, cita in enumerate(citas_disponibles, 1):
        print(f"{idx}. Cita #{cita.id}")
        print(f"   Fecha: {cita.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Odontólogo: {cita.odontologo.full_name}")
        print(f"   Estado: {cita.get_estado_display()}")
        print()
    
    try:
        seleccion = int(input("Selecciona el número de la cita a completar: "))
        if seleccion < 1 or seleccion > citas_disponibles.count():
            print("❌ Selección inválida")
            sys.exit(1)
        
        cita = list(citas_disponibles)[seleccion - 1]
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Cancelado")
        sys.exit(1)

# Completar la cita
print()
print("=" * 80)
print("⚙️  COMPLETANDO CITA Y ACTIVANDO NOTIFICACIÓN AUTOMÁTICA")
print("=" * 80)
print()

print(f"📋 Cita #{cita.id}")
print(f"👤 Paciente: {paciente.full_name}")
print(f"🦷 Odontólogo: {cita.odontologo.full_name}")
print(f"📅 Fecha: {cita.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
print()

print("🔄 Cambiando estado a COMPLETADA...")

# Esta acción debería disparar la señal automáticamente
cita.estado = 'COMPLETADA'
cita.save()

print()
print("=" * 80)
print("✅ CITA COMPLETADA")
print("=" * 80)
print()
print("📲 La señal de Django debería haber enviado la notificación automáticamente")
print()
print("🔔 REVISA:")
print("  1. Los logs arriba para ver si la notificación se envió")
print("  2. Tu dispositivo móvil para ver la notificación")
print()
print("Si ves el log:")
print('  "✅ Notificación enviada exitosamente a paciente@clinica-demo.com"')
print()
print("Significa que el sistema funciona perfectamente! 🎉")
print()
print("=" * 80)
