"""
Corregir el odontólogo en Render (ID 199)
Cambiar tipo_usuario a ODONTOLOGO y activarlo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario

connection.set_schema('clinica_demo')

print("\n" + "="*70)
print("🔧 CORRIGIENDO ODONTÓLOGO EN RENDER")
print("="*70 + "\n")

# Buscar el usuario con email de odontólogo
try:
    usuario = Usuario.objects.get(email='odontologo@clinica-demo.com')
    
    print(f"📋 Usuario encontrado:")
    print(f"   ID: {usuario.id}")
    print(f"   Email: {usuario.email}")
    print(f"   Nombre: {usuario.nombre} {usuario.apellido}")
    print(f"   Tipo actual: {usuario.tipo_usuario}")
    print(f"   Activo: {usuario.is_active}")
    print()
    
    # Corregir tipo_usuario y activar
    cambios = []
    
    if usuario.tipo_usuario != 'ODONTOLOGO':
        usuario.tipo_usuario = 'ODONTOLOGO'
        cambios.append("tipo_usuario → ODONTOLOGO")
    
    if not usuario.is_active:
        usuario.is_active = True
        cambios.append("is_active → True")
    
    if cambios:
        usuario.save()
        print(f"✅ Usuario corregido:")
        for cambio in cambios:
            print(f"   ✓ {cambio}")
    else:
        print(f"ℹ️  El usuario ya está correctamente configurado")
    
    print()
    print(f"📊 Estado final:")
    print(f"   Tipo: {usuario.tipo_usuario}")
    print(f"   Activo: {usuario.is_active}")
    
except Usuario.DoesNotExist:
    print("❌ Usuario con email 'odontologo@clinica-demo.com' no encontrado")

print("\n" + "="*70 + "\n")
