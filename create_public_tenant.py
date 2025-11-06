"""
Script para crear el tenant público (public schema).
Este es necesario para el sitio de administración principal.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Domain, Clinica

print("=" * 60)
print("CREANDO TENANT PÚBLICO")
print("=" * 60)

try:
    # Verificar si ya existe el tenant público
    public_tenant = Clinica.objects.filter(schema_name='public').first()
    
    if not public_tenant:
        # Crear el tenant público
        public_tenant = Clinica(
            schema_name='public',
            nombre='Sitio Público - Administración',
            dominio='public',
            activo=True
        )
        public_tenant.save()
        print(f"\n✅ Tenant público creado: {public_tenant.nombre}")
    else:
        print(f"\n✅ Tenant público ya existe: {public_tenant.nombre}")
    
    # Crear o verificar el dominio localhost para el tenant público
    localhost_domain = Domain.objects.filter(domain='localhost').first()
    
    if not localhost_domain:
        localhost_domain = Domain(
            domain='localhost',
            tenant=public_tenant,
            is_primary=True
        )
        localhost_domain.save()
        print(f"✅ Dominio 'localhost' creado para el tenant público")
    else:
        if localhost_domain.tenant.schema_name != 'public':
            print(f"⚠️  El dominio 'localhost' está asignado a: {localhost_domain.tenant.schema_name}")
            print(f"   Reasignando al tenant público...")
            localhost_domain.tenant = public_tenant
            localhost_domain.save()
            print(f"✅ Dominio 'localhost' reasignado al tenant público")
        else:
            print(f"✅ Dominio 'localhost' ya está configurado correctamente")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("CONFIGURACIÓN FINAL DE DOMINIOS:")
print("=" * 60)

# Mostrar todos los dominios configurados
for domain in Domain.objects.all().order_by('domain'):
    primary = "★" if domain.is_primary else " "
    print(f"  {primary} {domain.domain:30s} -> {domain.tenant.nombre} ({domain.tenant.schema_name})")

print("\n✅ Configuración completada")
