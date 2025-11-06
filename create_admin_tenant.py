"""
Script para crear el superusuario administrador en el tenant clinica_demo.
Este usuario podrá acceder a http://clinica-demo.localhost:8000/admin/
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica
from django.db import connection

print("=" * 60)
print("CREANDO ADMINISTRADOR EN TENANT: clinica_demo")
print("=" * 60)

try:
    # Obtener el tenant
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    
    # Cambiar al esquema del tenant
    connection.set_tenant(tenant)
    print(f"Esquema actual: {connection.schema_name}")
    
    # AHORA sí podemos importar Usuario (porque estamos en un esquema tenant)
    from usuarios.models import Usuario
    
    email = 'admin@clinica.com'
    password = '123456'
    
    # Verificar si ya existe
    if Usuario.objects.filter(email=email).exists():
        print(f"\n⚠️  El usuario '{email}' ya existe")
        user = Usuario.objects.get(email=email)
    else:
        # Crear superusuario
        user = Usuario.objects.create_superuser(
            email=email,
            password=password,
            tipo_usuario='ADMIN',
            nombre='Administrador',
            apellido='Demo'
        )
        print(f"\n✅ Administrador creado exitosamente!")
    
    print(f"\n📋 CREDENCIALES:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Tipo: {user.tipo_usuario}")
    print(f"\n🌐 Acceso: http://clinica-demo.localhost:8000/admin/")
    print(f"   (Este admin mostrará: Usuarios, Agenda, Tratamientos, etc.)")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Script completado")
