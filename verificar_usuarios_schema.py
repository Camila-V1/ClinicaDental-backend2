import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import PerfilPaciente
from tenants.models import Clinica
from django_tenants.utils import schema_context

Usuario = get_user_model()

print("\n" + "="*80)
print("VERIFICACIÓN DE USUARIOS EN CLINICA_DEMO")
print("="*80)

# Obtener clínica
try:
    clinica = Clinica.objects.get(schema_name="clinica_demo")
    print(f"\n✅ Clínica encontrada: {clinica.nombre} (schema: {clinica.schema_name})")
except Clinica.DoesNotExist:
    print("❌ Clínica 'clinica_demo' no existe")
    exit()

# Usar el contexto del schema de la clínica
with schema_context(clinica.schema_name):
    usuarios = Usuario.objects.all()
    print(f"\n📊 Total de usuarios en {clinica.schema_name}: {usuarios.count()}")
    
    if usuarios.count() == 0:
        print("\n⚠️ NO HAY USUARIOS EN ESTA CLÍNICA")
        print("Necesitas ejecutar un script de población de datos.")
        exit()
    
    print("\n" + "-"*80)
    print("DETALLE DE USUARIOS:")
    print("-"*80)
    
    for user in usuarios:
        print(f"\n{'='*60}")
        print(f"👤 Username: {user.username if hasattr(user, 'username') else user.email}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Tipo: {user.tipo_usuario}")
        print(f"✓ Activo: {user.is_active}")
        print(f"🔐 Has password: {user.has_usable_password()}")
        
        # Verificar perfil de paciente si corresponde
        if user.tipo_usuario == 'PACIENTE':
            try:
                perfil = PerfilPaciente.objects.get(usuario=user)
                print(f"👥 Perfil: {user.nombre} {user.apellido}")
                print(f"📱 Teléfono: {user.telefono}")
                print(f"📅 Fecha nac: {perfil.fecha_de_nacimiento}")
                print(f"📍 Dirección: {perfil.direccion}")
            except PerfilPaciente.DoesNotExist:
                print("⚠️ No tiene perfil de paciente")
    
    print("\n" + "="*80)
    print("RESUMEN - USUARIOS PACIENTES ACTIVOS:")
    print("="*80)
    
    pacientes = usuarios.filter(tipo_usuario='PACIENTE', is_active=True)
    if pacientes.count() == 0:
        print("\n⚠️ NO HAY PACIENTES ACTIVOS")
    else:
        for i, paciente in enumerate(pacientes, 1):
            print(f"\n{i}. 📧 Email: {paciente.email}")
            print(f"   👤 Nombre: {paciente.nombre} {paciente.apellido}")
            print(f"   🔐 Password válido: {paciente.has_usable_password()}")
            try:
                perfil = PerfilPaciente.objects.get(usuario=paciente)
                print(f"   ✅ Tiene perfil")
            except:
                print("   ⚠️ Sin perfil")

print("\n" + "="*80)
