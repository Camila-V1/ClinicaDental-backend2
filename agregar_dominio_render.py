"""
Script para agregar el dominio de Render a la clínica demo
Ejecutar esto en Render Console o localmente apuntando a la DB de producción
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain

def agregar_dominio_render():
    """Agregar dominio de Render a clinica_demo"""
    
    # Obtener la clínica demo
    try:
        clinica = Clinica.objects.filter(schema_name='clinica_demo').first()
        
        if not clinica:
            print("❌ No se encontró la clínica con schema_name='clinica_demo'")
            print("Clínicas disponibles:")
            for c in Clinica.objects.all():
                print(f"  - {c.schema_name}: {c.nombre}")
            return
        
        print(f"✅ Clínica encontrada: {clinica.nombre} ({clinica.schema_name})")
        
        # Agregar dominio de Render
        domain_name = 'clinica-dental-backend-4wyd.onrender.com'
        domain, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': clinica,
                'is_primary': False
            }
        )
        
        if created:
            print(f"✅ Dominio creado: {domain_name}")
        else:
            print(f"ℹ️  Dominio ya existía: {domain_name}")
        
        # Mostrar todos los dominios de la clínica
        print(f"\nDominios registrados para {clinica.nombre}:")
        for d in Domain.objects.filter(tenant=clinica):
            primary_mark = " (principal)" if d.is_primary else ""
            print(f"  - {d.domain}{primary_mark}")
        
        print("\n✅ Configuración completada")
        print("Ahora puedes hacer requests a https://clinica-dental-backend-4wyd.onrender.com/api/token/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    agregar_dominio_render()
