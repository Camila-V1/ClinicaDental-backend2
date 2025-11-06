"""
Script para corregir los dominios del sistema multi-tenant.
- Corrige el dominio del tenant clinica_demo
- Crea el dominio público para localhost
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Domain, Clinica

print("=" * 60)
print("CORRIGIENDO CONFIGURACIÓN DE DOMINIOS")
print("=" * 60)

try:
    # 1. Encontrar el tenant 'clinica_demo'
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    print(f"\n✅ Tenant encontrado: '{tenant.nombre}' (schema: {tenant.schema_name})")
    
    # 2. Buscar el dominio actual
    try:
        domain = Domain.objects.get(tenant=tenant, domain='localhost')
        print(f"   ⚠️  Dominio incorrecto encontrado: '{domain.domain}'")
        
        # 3. Corregir el dominio
        domain.domain = 'clinica-demo.localhost'
        domain.is_primary = True
        domain.save()
        
        print(f"   ✅ Dominio corregido a: '{domain.domain}'")
        
    except Domain.DoesNotExist:
        print("   ℹ️  No se encontró el dominio 'localhost', verificando...")
        
        # Verificar si ya tiene el dominio correcto
        correct_domain = Domain.objects.filter(tenant=tenant, domain='clinica-demo.localhost').first()
        if correct_domain:
            print(f"   ✅ El dominio ya está correcto: '{correct_domain.domain}'")
        else:
            # Crear el dominio correcto
            new_domain = Domain.objects.create(
                domain='clinica-demo.localhost',
                tenant=tenant,
                is_primary=True
            )
            print(f"   ✅ Dominio creado: '{new_domain.domain}'")

except Clinica.DoesNotExist:
    print("   ❌ No se encontró el tenant 'clinica_demo'.")

print("\n" + "=" * 60)
print("CONFIGURACIÓN FINAL DE DOMINIOS:")
print("=" * 60)

# Mostrar todos los dominios configurados
for domain in Domain.objects.all():
    print(f"  • {domain.domain} -> {domain.tenant.nombre} (schema: {domain.tenant.schema_name})")

print("\n" + "=" * 60)
print("PRÓXIMOS PASOS:")
print("=" * 60)
print("1. Agregar al archivo hosts de Windows:")
print("   C:\\Windows\\System32\\drivers\\etc\\hosts")
print("   Línea: 127.0.0.1   clinica-demo.localhost")
print("\n2. Reiniciar el servidor: python manage.py runserver")
print("\n3. Acceder a:")
print("   - Sitio público: http://localhost:8000/admin/")
print("   - Clínica demo:  http://clinica-demo.localhost:8000/admin/")
print("=" * 60)
