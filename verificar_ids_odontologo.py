import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario, PerfilOdontologo
from django_tenants.utils import schema_context

# Usar el schema de la clínica demo
with schema_context('clinica_demo'):
    print("\n" + "="*60)
    print("🔍 VERIFICANDO IDs DE ODONTÓLOGOS")
    print("="*60)
    
    # Obtener todos los odontólogos
    odontologos = Usuario.objects.filter(tipo_usuario='ODONTOLOGO', is_active=True)
    
    print(f"\n📊 Total odontólogos: {odontologos.count()}\n")
    
    for odontologo in odontologos:
        print(f"👨‍⚕️ {odontologo.nombre} {odontologo.apellido}")
        print(f"   📧 Email: {odontologo.email}")
        print(f"   🆔 Usuario ID: {odontologo.id}")
        
        if hasattr(odontologo, 'perfil_odontologo'):
            perfil = odontologo.perfil_odontologo
            print(f"   ✅ PerfilOdontologo ID (PK): {perfil.pk}")
            print(f"   ✅ Usuario relacionado: {perfil.usuario.id}")
            print(f"   🎓 Especialidad: {perfil.especialidad.nombre if perfil.especialidad else 'No especificada'}")
        else:
            print(f"   ❌ No tiene PerfilOdontologo")
        
        print()
    
    print("="*60)
    print("⚠️ IMPORTANTE:")
    print("El endpoint /api/agenda/citas/ espera el ID del PerfilOdontologo,")
    print("NO el ID del Usuario.")
    print("="*60)
