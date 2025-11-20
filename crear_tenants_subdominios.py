"""
Script para crear los 3 tenants con subdominios
Uso: python crear_tenants_subdominios.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain
from django.core.management import call_command

def crear_tenant(dominio, nombre, schema_name):
    """Crear un nuevo tenant con su schema y dominios"""
    
    # 1. Verificar si ya existe
    if Clinica.objects.filter(schema_name=schema_name).exists():
        print(f"⚠️  Tenant '{schema_name}' ya existe, omitiendo...")
        return Clinica.objects.get(schema_name=schema_name)
    
    # 2. Crear el tenant
    print(f"\n📝 Creando tenant: {nombre}")
    tenant = Clinica.objects.create(
        schema_name=schema_name,
        nombre=nombre,
        dominio=dominio,
        activo=True
    )
    print(f"✅ Tenant creado: {tenant.schema_name}")
    
    # 3. Crear dominios para frontend
    dominios = [
        f"{dominio}.dentaabcxy.store",  # Frontend production
        f"{dominio}.localhost",         # Desarrollo local
    ]
    
    for domain_name in dominios:
        # Verificar si ya existe
        if not Domain.objects.filter(domain=domain_name).exists():
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=(domain_name == f"{dominio}.dentaabcxy.store")
            )
            print(f"✅ Dominio creado: {domain_name}")
    
    # 4. Ejecutar migraciones para el nuevo schema
    print(f"🔄 Ejecutando migraciones para {schema_name}...")
    call_command('migrate_schemas', schema=schema_name)
    print(f"✅ Migraciones completadas")
    
    print(f"\n🎉 Tenant '{nombre}' creado exitosamente!")
    print(f"   📍 URL Frontend: https://{dominio}.dentaabcxy.store")
    print(f"   🗄️  Schema DB: {schema_name}")
    
    return tenant


if __name__ == '__main__':
    print("=" * 60)
    print("🏥 CREACIÓN DE TENANTS PARA SUBDOMINIOS")
    print("=" * 60)
    
    # Tenant 1: Clínica Demo 1
    crear_tenant(
        dominio='clinicademo1',
        nombre='Clínica Demo 1',
        schema_name='clinica_demo1'
    )
    
    # Tenant 2: Clínica ABC
    crear_tenant(
        dominio='clinicaabc',
        nombre='Clínica ABC',
        schema_name='clinica_abc'
    )
    
    # Tenant 3: Clínica XYZ
    crear_tenant(
        dominio='clinicaxyz',
        nombre='Clínica XYZ',
        schema_name='clinica_xyz'
    )
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TENANTS CREADOS EXITOSAMENTE")
    print("=" * 60)
    print("\n📋 RESUMEN:")
    print("   1. clinicademo1.dentaabcxy.store → Schema: clinica_demo1")
    print("   2. clinicaabc.dentaabcxy.store   → Schema: clinica_abc")
    print("   3. clinicaxyz.dentaabcxy.store   → Schema: clinica_xyz")
    print("\n⚠️  IMPORTANTE: Ahora debes poblar datos en cada tenant")
    print("   Ejemplo: python poblar_sistema_completo.py (dentro del schema)")
