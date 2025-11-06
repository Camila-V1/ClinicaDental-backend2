"""
Script para crear el superusuario en el esquema PÚBLICO.
IMPORTANTE: El esquema público NO tiene el modelo Usuario, usa django.contrib.auth.User
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection

print("=" * 60)
print("CREANDO SUPERUSUARIO EN ESQUEMA PÚBLICO")
print("=" * 60)

# Forzar conexión al esquema público
connection.set_schema_to_public()
print(f"Esquema actual: {connection.schema_name}")

try:
    email = 'superadmin@sistema.com'
    password = 'superadmin123'
    
    # Verificar si ya existe
    if User.objects.filter(username=email).exists():
        print(f"\n⚠️  El usuario '{email}' ya existe")
        user = User.objects.get(username=email)
    else:
        # Crear superusuario
        user = User.objects.create_superuser(
            username=email,
            email=email,
            password=password
        )
        print(f"\n✅ Superusuario creado exitosamente!")
    
    print(f"\n📋 CREDENCIALES:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🌐 Acceso: http://localhost:8000/admin/")
    print(f"   (Este admin mostrará SOLO: Clinicas, Dominios, Grupos)")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Script completado")
