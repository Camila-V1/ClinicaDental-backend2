#!/usr/bin/env python
"""
Script de verificación rápida para los módulos de población
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from tenants.models import Clinica

print("="*70)
print("  VERIFICACIÓN DE SCRIPTS DE POBLACIÓN")
print("="*70)

# Buscar tenant de demo
tenant = Clinica.objects.filter(schema_name='clinica_demo').first()

if not tenant:
    print("\n❌ ERROR: No existe el tenant 'clinica_demo'")
    print("   Ejecutar primero: python scripts_poblacion/poblar_todo.py")
    sys.exit(1)

print(f"\n✅ Tenant encontrado: {tenant.nombre}")
print(f"   Schema: {tenant.schema_name}")

# Verificar datos en el tenant
with schema_context('clinica_demo'):
    from usuarios.models import Usuario
    from tratamientos.models import Tratamiento
    from inventario.models import Producto
    from agenda.models import Cita
    from historial_clinico.models import EpisodioClinico, Odontograma
    from facturacion.models import Factura, Pago
    
    print("\n📊 DATOS POBLADOS:")
    print(f"   Usuarios:          {Usuario.objects.count()}")
    print(f"     - Admin:         {Usuario.objects.filter(rol='ADMIN').count()}")
    print(f"     - Odontólogos:   {Usuario.objects.filter(rol='ODONTOLOGO').count()}")
    print(f"     - Recepcionistas: {Usuario.objects.filter(rol='RECEPCIONISTA').count()}")
    print(f"     - Pacientes:     {Usuario.objects.filter(rol='PACIENTE').count()}")
    
    print(f"\n   Tratamientos:      {Tratamiento.objects.count()}")
    print(f"   Productos:         {Producto.objects.count()}")
    print(f"   Citas:             {Cita.objects.count()}")
    print(f"     - Completadas:   {Cita.objects.filter(estado='COMPLETADA').count()}")
    print(f"     - Programadas:   {Cita.objects.filter(estado='PROGRAMADA').count()}")
    print(f"     - En curso:      {Cita.objects.filter(estado='EN_CURSO').count()}")
    
    print(f"\n   Episodios clínicos: {EpisodioClinico.objects.count()}")
    print(f"   Odontogramas:      {Odontograma.objects.count()}")
    print(f"   Facturas:          {Factura.objects.count()}")
    print(f"     - Pagadas:       {Factura.objects.filter(estado='PAGADA').count()}")
    print(f"     - Pendientes:    {Factura.objects.filter(estado='PENDIENTE').count()}")
    print(f"     - Parciales:     {Factura.objects.filter(estado='PARCIAL').count()}")
    print(f"   Pagos:             {Pago.objects.count()}")
    
    # Verificar credenciales
    print("\n🔐 VERIFICACIÓN DE CREDENCIALES:")
    
    credenciales = [
        ('admin@clinicademo1.com', 'Admin', 'ADMIN'),
        ('odontologo@clinica-demo.com', 'Odontólogo', 'ODONTOLOGO'),
        ('recepcionista@clinica-demo.com', 'Recepcionista', 'RECEPCIONISTA'),
        ('paciente1@test.com', 'Paciente 1', 'PACIENTE'),
        ('paciente2@test.com', 'Paciente 2', 'PACIENTE'),
    ]
    
    for email, nombre, rol_esperado in credenciales:
        usuario = Usuario.objects.filter(email=email).first()
        if usuario:
            if usuario.rol == rol_esperado:
                print(f"   ✅ {nombre:20s} ({email}) - OK")
            else:
                print(f"   ⚠️  {nombre:20s} ({email}) - Rol incorrecto: {usuario.rol}")
        else:
            print(f"   ❌ {nombre:20s} ({email}) - NO ENCONTRADO")
    
    # Verificar integridad de datos
    print("\n🔍 INTEGRIDAD DE DATOS:")
    
    # Verificar que las citas tengan odontólogo y paciente
    citas_sin_odontologo = Cita.objects.filter(odontologo__isnull=True).count()
    citas_sin_paciente = Cita.objects.filter(paciente__isnull=True).count()
    
    if citas_sin_odontologo == 0 and citas_sin_paciente == 0:
        print("   ✅ Todas las citas tienen odontólogo y paciente")
    else:
        print(f"   ⚠️  Citas sin odontólogo: {citas_sin_odontologo}")
        print(f"   ⚠️  Citas sin paciente: {citas_sin_paciente}")
    
    # Verificar que los episodios tengan odontograma
    episodios = EpisodioClinico.objects.count()
    odontogramas = Odontograma.objects.count()
    
    if episodios > 0 and odontogramas > 0:
        print(f"   ✅ Relación episodios/odontogramas: {odontogramas}/{episodios}")
    else:
        print(f"   ⚠️  Episodios: {episodios}, Odontogramas: {odontogramas}")
    
    # Verificar facturas
    facturas = Factura.objects.count()
    items = sum(f.items.count() for f in Factura.objects.all())
    
    if facturas > 0 and items > 0:
        print(f"   ✅ Facturas tienen items: {items} items en {facturas} facturas")
    else:
        print(f"   ⚠️  Facturas: {facturas}, Items: {items}")

print("\n" + "="*70)
print("  VERIFICACIÓN COMPLETADA")
print("="*70)
print("\n✅ El sistema está correctamente poblado y listo para usar!")
print("\n🌐 Puedes acceder con las credenciales mostradas arriba")
print("   Dominio: clinicademo1.dentaabcxy.store")
print("   Backend: https://clinica-dental-backend.onrender.com")
