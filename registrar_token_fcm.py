#!/usr/bin/env python
"""
Script para registrar un token FCM de prueba en un usuario.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario
from django.db import connection
from tenants.models import Clinica

print("=" * 80)
print("📝 REGISTRAR TOKEN FCM DE PRUEBA")
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

# Listar pacientes disponibles
print("👥 PACIENTES DISPONIBLES:")
print()
pacientes = Usuario.objects.filter(tipo_usuario='PACIENTE').order_by('email')

if not pacientes.exists():
    print("⚠️  No hay pacientes registrados")
    sys.exit(1)

for idx, paciente in enumerate(pacientes, 1):
    token_status = "✅ Con token" if paciente.fcm_token else "❌ Sin token"
    print(f"{idx}. {paciente.nombre_completo} ({paciente.email}) - {token_status}")

print()
print("─" * 80)
print()

# Solicitar selección
try:
    seleccion = int(input("Selecciona el número del paciente (o 0 para salir): "))
    if seleccion == 0:
        print("Cancelado")
        sys.exit(0)
    
    if seleccion < 1 or seleccion > pacientes.count():
        print("❌ Selección inválida")
        sys.exit(1)
    
    paciente = list(pacientes)[seleccion - 1]
    
except ValueError:
    print("❌ Debes ingresar un número")
    sys.exit(1)

print()
print(f"📱 Paciente seleccionado: {paciente.nombre_completo}")
print()

# Solicitar token
print("Opciones:")
print("1. Generar token de prueba automático")
print("2. Ingresar token FCM real")
print()

try:
    opcion = int(input("Selecciona una opción: "))
except ValueError:
    print("❌ Opción inválida")
    sys.exit(1)

if opcion == 1:
    # Generar token de prueba
    import uuid
    token = f"test_token_{uuid.uuid4().hex[:16]}"
    print(f"\n🔑 Token generado: {token}")
elif opcion == 2:
    # Solicitar token real
    token = input("\nIngresa el token FCM: ").strip()
    if not token:
        print("❌ Token vacío")
        sys.exit(1)
else:
    print("❌ Opción inválida")
    sys.exit(1)

# Registrar el token
paciente.fcm_token = token
paciente.save()

print()
print("=" * 80)
print("✅ TOKEN FCM REGISTRADO EXITOSAMENTE")
print("=" * 80)
print()
print(f"👤 Usuario:  {paciente.nombre_completo}")
print(f"📧 Email:    {paciente.email}")
print(f"📱 Token:    {token}")
print()
print("🧪 Ahora puedes probar enviando una notificación:")
print()
print("python probar_notificacion.py")
print()
print("=" * 80)
