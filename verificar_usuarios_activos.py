import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import PerfilPaciente
from tenants.models import Clinica

Usuario = get_user_model()

print("\n" + "="*80)
print("VERIFICACIÓN DE USUARIOS ACTIVOS EN CLINICADEMO1")
print("="*80)

# Obtener tenant
try:
    tenant = Clinica.objects.get(schema_name="clinica_demo")
    print(f"\n✅ Clínica encontrada: {tenant.nombre} (schema: {tenant.schema_name})")
except Clinica.DoesNotExist:
    print("❌ Clínica 'clinica_demo' no existe")
    exit()

# Verificar usuarios
usuarios = Usuario.objects.filter(clinica=tenant)
print(f"\n📊 Total de usuarios en clinicademo1: {usuarios.count()}")

print("\n" + "-"*80)
print("DETALLE DE USUARIOS:")
print("-"*80)

for user in usuarios:
    print(f"\n{'='*60}")
    print(f"👤 Username: {user.username}")
    print(f"📧 Email: {user.email}")
    print(f"🔑 Tipo: {user.tipo_usuario}")
    print(f"✓ Activo: {user.is_active}")
    print(f"🔐 Has password: {user.has_usable_password()}")
    print(f"📅 Fecha registro: {user.date_joined}")
    
    # Verificar perfil de paciente si corresponde
    if user.tipo_usuario == 'PACIENTE':
        try:
            perfil = PerfilPaciente.objects.get(usuario=user)
            print(f"👥 Perfil Paciente: {perfil.nombre} {perfil.apellido}")
            print(f"📱 Teléfono: {perfil.telefono}")
        except PerfilPaciente.DoesNotExist:
            print("⚠️ No tiene perfil de paciente asociado")

print("\n" + "="*80)
print("USUARIOS PACIENTES (para login):")
print("="*80)

pacientes = usuarios.filter(tipo_usuario='PACIENTE', is_active=True)
for paciente in pacientes:
    print(f"\n✅ Email: {paciente.email}")
    print(f"   Username: {paciente.username}")
    print(f"   Password válido: {paciente.has_usable_password()}")
    try:
        perfil = PerfilPaciente.objects.get(usuario=paciente)
        print(f"   Nombre: {perfil.nombre} {perfil.apellido}")
    except:
        print("   ⚠️ Sin perfil")

print("\n" + "="*80)
