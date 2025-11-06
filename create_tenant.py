"""
Script para crear el primer tenant (clínica) de prueba.
Ejecutar con: python manage.py shell < create_tenant.py
"""
from tenants.models import Clinica, Domain

# Verificar si ya existe
if not Clinica.objects.filter(schema_name='clinica_demo').exists():
    # Crear la clínica (tenant)
    tenant = Clinica(
        schema_name='clinica_demo',  # Nombre del esquema en PostgreSQL
        nombre='Clínica Dental Demo',
        dominio='clinica-demo',
        activo=True
    )
    tenant.save()
    print(f"✅ Tenant creado: {tenant.nombre} (schema: {tenant.schema_name})")
    
    # Crear el dominio principal para este tenant
    domain = Domain()
    domain.domain = 'localhost'  # Dominio base
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    print(f"✅ Dominio principal creado: {domain.domain}")
    
    print("\n🎉 ¡Tenant creado exitosamente!")
    print(f"📍 Puedes acceder en: http://localhost:8000")
else:
    print("⚠️  El tenant 'clinica_demo' ya existe.")
