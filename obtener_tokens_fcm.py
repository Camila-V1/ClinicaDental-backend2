#!/usr/bin/env python
"""
Script para obtener los tokens FCM de usuarios con dispositivos móviles registrados.
Útil para probar notificaciones push.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario
from django.db import connection
from tenants.models import Clinica

print("=" * 80)
print("📱 TOKENS FCM DE USUARIOS CON DISPOSITIVOS MÓVILES")
print("=" * 80)
print()

# Cambiar al schema del tenant clinica_demo
try:
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    connection.set_tenant(tenant)
    print(f"✅ Conectado al tenant: {tenant.schema_name} ({tenant.nombre})")
    print()
except Clinica.DoesNotExist:
    print("❌ No se encontró el tenant 'clinica_demo'")
    print()
    print("Tenants disponibles:")
    for t in Clinica.objects.all():
        print(f"   - {t.schema_name} ({t.nombre})")
    sys.exit(1)
print()

# Obtener todos los usuarios con token FCM
usuarios_con_token = Usuario.objects.filter(
    fcm_token__isnull=False
).exclude(
    fcm_token=''
).order_by('tipo_usuario', 'email')

if not usuarios_con_token.exists():
    print("⚠️  No hay usuarios con tokens FCM registrados.")
    print()
    print("Para registrar un token, el usuario debe:")
    print("1. Abrir la app móvil")
    print("2. Iniciar sesión")
    print("3. La app automáticamente registrará el token FCM")
    print()
    print("O usar el endpoint manualmente:")
    print("POST /api/usuarios/registrar-fcm-token/")
    print('Body: {"fcm_token": "tu_token_aqui"}')
    print()
else:
    print(f"✅ Encontrados {usuarios_con_token.count()} usuarios con tokens FCM\n")
    
    for usuario in usuarios_con_token:
        print(f"{'─' * 80}")
        print(f"👤 Usuario:      {usuario.full_name}")
        print(f"📧 Email:        {usuario.email}")
        print(f"🏷️  Tipo:         {usuario.get_tipo_usuario_display()}")
        print(f"📱 Token FCM:    {usuario.fcm_token}")
        print()

print("=" * 80)
print()
print("🧪 COMANDOS PARA PROBAR NOTIFICACIONES:")
print()
print("1️⃣  Enviar notificación de prueba desde Python:")
print()
print("from valoraciones.firebase_service import enviar_notificacion_push")
print("enviar_notificacion_push(")
print('    fcm_token="TOKEN_DEL_USUARIO",')
print('    titulo="Prueba de Notificación",')
print('    cuerpo="Esta es una notificación de prueba",')
print("    data={'tipo': 'test'}")
print(")")
print()
print("2️⃣  Completar una cita para enviar notificación automática:")
print()
print("# En el admin de Django o con este código:")
print("from agenda.models import Cita")
print("cita = Cita.objects.get(id=TU_CITA_ID)")
print("cita.estado = 'COMPLETADA'")
print("cita.save()  # Esto enviará la notificación automáticamente")
print()
print("3️⃣  Usar el endpoint de test (si existe):")
print()
print("POST /api/valoraciones/test-notificacion/")
print("Headers: Authorization: Bearer {token}")
print('Body: {"fcm_token": "TOKEN_DEL_USUARIO"}')
print()
print("=" * 80)
print()
print("📄 SCHEMA DEL TENANT ACTUAL:")

# Mostrar el schema actual
with connection.cursor() as cursor:
    cursor.execute("SELECT current_schema();")
    schema = cursor.fetchone()[0]
    print(f"   {schema}")
print()
print("=" * 80)
