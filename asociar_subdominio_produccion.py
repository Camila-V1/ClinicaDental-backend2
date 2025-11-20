"""
Script para asociar subdominio en producción usando DATABASE_URL de Render
Ejecuta desde local pero modifica la BD de producción
"""
import os
import sys

# DATABASE_URL de producción (external connection)
database_url = "postgresql://clinica_user:XNZolIFdBz58JffoGdZgfVV5mRIS9xLX@dpg-d4ev7oq4d50c73e44fig-a.oregon-postgres.render.com/clinica_dental_prod"

print("=" * 60)
print("🔗 CONFIGURAR SUBDOMINIO EN PRODUCCIÓN")
print("=" * 60)
print(f"\n🗄️  Conectando a: dpg-d4ev7oq4d50c73e44fig-a.oregon-postgres.render.com")

# Configurar para usar la BD de producción
os.environ['DATABASE_URL'] = database_url
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# Importar Django
import django
django.setup()

from tenants.models import Clinica, Domain

print("\n🔄 Conectando a la base de datos de producción...")

try:
    # 1. Encontrar el tenant clinica_demo
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    print(f"✅ Tenant encontrado: {tenant.nombre} (schema: {tenant.schema_name})")
    
    # 2. Actualizar el dominio del tenant si es necesario
    if tenant.dominio != 'clinicademo1':
        tenant.dominio = 'clinicademo1'
        tenant.save()
        print(f"✅ Dominio del tenant actualizado: {tenant.dominio}")
    else:
        print(f"✅ Dominio del tenant ya correcto: {tenant.dominio}")
    
    # 3. Agregar dominio del subdominio
    dominio_produccion = 'clinicademo1.dentaabcxy.store'
    
    if Domain.objects.filter(domain=dominio_produccion).exists():
        print(f"⚠️  Dominio '{dominio_produccion}' ya existe")
        domain_obj = Domain.objects.get(domain=dominio_produccion)
        # Asegurar que apunte al tenant correcto
        if domain_obj.tenant != tenant:
            domain_obj.tenant = tenant
            domain_obj.save()
            print(f"✅ Dominio reasignado a {tenant.nombre}")
    else:
        Domain.objects.create(
            domain=dominio_produccion,
            tenant=tenant,
            is_primary=True
        )
        print(f"✅ Dominio creado: {dominio_produccion}")
    
    # 4. Verificar todos los dominios
    print(f"\n📋 Dominios asociados a '{tenant.nombre}':")
    dominios = Domain.objects.filter(tenant=tenant)
    for d in dominios:
        primary = "⭐ Principal" if d.is_primary else ""
        print(f"   - {d.domain} {primary}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA EN PRODUCCIÓN")
    print("=" * 60)
    print(f"\n🌐 URLs disponibles:")
    print(f"   Frontend: https://clinicademo1.dentaabcxy.store")
    print(f"   Backend:  https://clinica-dental-backend.onrender.com/api/")
    print(f"\n🔑 Credenciales existentes (sin cambios):")
    print(f"   Odontólogo: odontologo@clinica-demo.com / odontologo123")
    print(f"   Pacientes:  paciente1-5@test.com / paciente123")
    print(f"\n✅ Ahora haz commit del middleware y el frontend!")
    
except Clinica.DoesNotExist:
    print("\n❌ Error: No existe el tenant 'clinica_demo' en producción")
    print("   Verifica que el tenant fue creado correctamente")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
