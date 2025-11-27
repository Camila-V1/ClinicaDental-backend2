import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica

print("\n" + "="*80)
print("LISTADO DE CLÍNICAS EN EL SISTEMA")
print("="*80)

clinicas = Clinica.objects.all()
print(f"\n📊 Total de clínicas: {clinicas.count()}")

for clinica in clinicas:
    print(f"\n{'='*60}")
    print(f"🏥 Nombre: {clinica.nombre}")
    print(f"🔑 Schema: {clinica.schema_name}")
    print(f"🌐 Schema público: {clinica.schema_name == 'public'}")
    print(f"📄 RUC: {getattr(clinica, 'ruc', 'N/A')}")
    
    # Obtener dominios
    dominios = clinica.domains.all()
    if dominios.exists():
        print(f"🌍 Dominios:")
        for dominio in dominios:
            print(f"   - {dominio.domain} {'(principal)' if dominio.is_primary else ''}")
    else:
        print("⚠️ Sin dominios configurados")

print("\n" + "="*80)
