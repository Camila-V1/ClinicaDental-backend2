"""
Script para crear la clínica demo (clinica_demo tenant).
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Domain, Clinica

print("=" * 60)
print("CREANDO TENANT: CLÍNICA DEMO")
print("=" * 60)

try:
    # Verificar si ya existe el tenant
    demo_tenant = Clinica.objects.filter(schema_name='clinica_demo').first()
    
    if not demo_tenant:
        # Crear el tenant
        demo_tenant = Clinica(
            schema_name='clinica_demo',
            nombre='Clínica Dental Demo',
            dominio='clinica-demo',
            activo=True
        )
        demo_tenant.save(verbosity=2)  # verbosity=2 para ver las migraciones
        print(f"\n✅ Tenant creado: {demo_tenant.nombre}")
        print(f"   Schema: {demo_tenant.schema_name}")
    else:
        print(f"\n✅ Tenant ya existe: {demo_tenant.nombre}")
    
    # Crear o verificar el dominio para el tenant
    demo_domain = Domain.objects.filter(domain='clinica-demo.localhost').first()
    
    if not demo_domain:
        demo_domain = Domain(
            domain='clinica-demo.localhost',
            tenant=demo_tenant,
            is_primary=True
        )
        demo_domain.save()
        print(f"✅ Dominio 'clinica-demo.localhost' creado")
    else:
        if demo_domain.tenant.schema_name != 'clinica_demo':
            print(f"⚠️  El dominio 'clinica-demo.localhost' está asignado a: {demo_domain.tenant.schema_name}")
            print(f"   Reasignando...")
            demo_domain.tenant = demo_tenant
            demo_domain.save()
            print(f"✅ Dominio reasignado a clinica_demo")
        else:
            print(f"✅ Dominio 'clinica-demo.localhost' ya está configurado correctamente")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("CONFIGURACIÓN FINAL DE DOMINIOS:")
print("=" * 60)

# Mostrar todos los dominios configurados
for domain in Domain.objects.all().order_by('domain'):
    primary = "★" if domain.is_primary else " "
    print(f"  {primary} {domain.domain:35s} -> {domain.tenant.nombre} ({domain.tenant.schema_name})")

print("\n✅ Script completado")
