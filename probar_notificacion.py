#!/usr/bin/env python
"""
Script para probar notificaciones push con un token FCM real.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario
from django.db import connection
from django.utils import timezone
from tenants.models import Clinica
from valoraciones.firebase_service import FirebaseNotificationService

print("=" * 80)
print("🧪 PROBAR NOTIFICACIÓN PUSH")
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

# Token FCM del log
FCM_TOKEN = "ebcoULuuRDGQKHsPSR8ZuH:APA91bEySRt4-PvrjC-5FSu_OfgPPohPlxxagoquHxc8gy3UGZzcHmaASd0iWXd9YUAe4FDpOzgm9HZeBuNEQuE4UAMbnoCmWKPKzdiuMg_OiM3ShIi2Bmo"

print("🔑 Token FCM detectado:")
print(f"   {FCM_TOKEN}")
print()

# Buscar usuario para asignar el token
print("👥 Selecciona un usuario para asignar el token:")
print()

usuarios = Usuario.objects.filter(tipo_usuario='PACIENTE').order_by('email')[:5]

if not usuarios.exists():
    print("❌ No hay usuarios disponibles")
    sys.exit(1)

for idx, usuario in enumerate(usuarios, 1):
    print(f"{idx}. {usuario.full_name} ({usuario.email})")

print()

try:
    seleccion = int(input("Selecciona el número del usuario: "))
    if seleccion < 1 or seleccion > usuarios.count():
        print("❌ Selección inválida")
        sys.exit(1)
    
    usuario = list(usuarios)[seleccion - 1]
except (ValueError, KeyboardInterrupt):
    print("\n❌ Cancelado")
    sys.exit(1)

# Registrar el token
print()
print(f"📝 Asignando token a: {usuario.full_name}")
usuario.fcm_token = FCM_TOKEN
usuario.save()
print("✅ Token registrado")
print()

# Enviar notificación de prueba
print("─" * 80)
print("📤 ENVIANDO NOTIFICACIÓN DE PRUEBA...")
print("─" * 80)
print()

try:
    # Primero verificar si el token es válido
    print("🔍 Verificando token FCM...")
    firebase_service = FirebaseNotificationService()
    
    token_valido = firebase_service.verificar_token(FCM_TOKEN)
    
    if not token_valido:
        print("❌ El token FCM no es válido o ha expirado")
        print("   El usuario debe volver a abrir la app para obtener un token nuevo")
        sys.exit(1)
    
    print("✅ Token válido")
    print()
    
    # Enviar la notificación
    print("📡 Enviando notificación push...")
    resultado = firebase_service.enviar_notificacion_valoracion(
        device_token=FCM_TOKEN,
        cita_id=1,
        odontologo_nombre="Dr. Test"
    )
    
    print()
    print("=" * 80)
    
    if resultado:
        print("✅ ¡NOTIFICACIÓN ENVIADA EXITOSAMENTE!")
        print("=" * 80)
        print()
        print(f"👤 Usuario:  {usuario.full_name}")
        print(f"📧 Email:    {usuario.email}")
        print(f"📱 Token:    {FCM_TOKEN[:50]}...")
        print()
        print("🔔 REVISA TU DISPOSITIVO MÓVIL")
        print()
        print("Deberías ver:")
        print("  • Título: \"¿Cómo fue tu atención? 🦷\"")
        print("  • Mensaje: \"Valora la atención del Dr. Test...\"")
        print()
    else:
        print("❌ ERROR AL ENVIAR LA NOTIFICACIÓN")
        print("=" * 80)
        print()
        print("Posibles causas:")
        print("  1. El token FCM ha expirado")
        print("  2. La app no está instalada en el dispositivo")
        print("  3. Firebase tiene problemas de conectividad")
        print("  4. El proyecto de Firebase está mal configurado")
        print()
        print("Solución:")
        print("  • Abre la app móvil nuevamente")
        print("  • Verifica que aparezca el nuevo token en los logs")
        print("  • Ejecuta este script nuevamente")
        
except ValueError as ve:
    print()
    print("=" * 80)
    print("❌ ERROR DE VALIDACIÓN")
    print("=" * 80)
    print()
    print(f"Detalle: {ve}")
    print()
    print("El token FCM no tiene el formato correcto")
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ ERROR INESPERADO")
    print("=" * 80)
    print()
    print(f"Tipo de error: {type(e).__name__}")
    print(f"Mensaje: {e}")
    print()
    print("Stack trace completo:")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print()
print("💡 SIGUIENTE PASO:")
print()
print("Si la notificación llegó, puedes probar el sistema completo:")
print("1. En la app, completa una cita")
print("2. El sistema enviará automáticamente una notificación")
print("3. El paciente podrá valorar la cita desde la app")
print()
print("=" * 80)
