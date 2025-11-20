"""
Script para asociar clinica_demo existente con el subdominio clinicademo1
Uso: python asociar_subdominio_demo.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain

def asociar_subdominio():
    """Asociar el tenant clinica_demo con clinicademo1.dentaabcxy.store"""
    
    print("=" * 60)
    print("🔗 ASOCIANDO SUBDOMINIO A CLINICA_DEMO")
    print("=" * 60)
    
    # 1. Verificar que clinica_demo existe
    try:
        tenant = Clinica.objects.get(schema_name='clinica_demo')
        print(f"\n✅ Tenant encontrado: {tenant.nombre} (schema: {tenant.schema_name})")
    except Clinica.DoesNotExist:
        print("\n❌ Error: No existe el tenant 'clinica_demo'")
        print("   Ejecuta primero: python poblar_sistema_completo.py")
        return
    
    # 2. Actualizar el dominio del tenant (si es necesario)
    if tenant.dominio != 'clinicademo1':
        tenant.dominio = 'clinicademo1'
        tenant.save()
        print(f"✅ Dominio del tenant actualizado: {tenant.dominio}")
    else:
        print(f"✅ Dominio del tenant ya está correcto: {tenant.dominio}")
    
    # 3. Agregar dominio para el subdominio en producción
    dominio_produccion = 'clinicademo1.dentaabcxy.store'
    
    if Domain.objects.filter(domain=dominio_produccion).exists():
        print(f"⚠️  Dominio '{dominio_produccion}' ya existe")
    else:
        Domain.objects.create(
            domain=dominio_produccion,
            tenant=tenant,
            is_primary=True
        )
        print(f"✅ Dominio creado: {dominio_produccion}")
    
    # 4. Verificar/Agregar dominio localhost para desarrollo
    dominio_local = 'clinicademo1.localhost'
    
    if Domain.objects.filter(domain=dominio_local).exists():
        print(f"⚠️  Dominio '{dominio_local}' ya existe")
    else:
        Domain.objects.create(
            domain=dominio_local,
            tenant=tenant,
            is_primary=False
        )
        print(f"✅ Dominio creado: {dominio_local}")
    
    # 5. Mostrar todos los dominios del tenant
    print(f"\n📋 Dominios asociados a '{tenant.nombre}':")
    dominios = Domain.objects.filter(tenant=tenant)
    for d in dominios:
        primary = "⭐ Principal" if d.is_primary else ""
        print(f"   - {d.domain} {primary}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print(f"\n🌐 URLs disponibles:")
    print(f"   Frontend: https://clinicademo1.dentaabcxy.store")
    print(f"   Backend:  https://clinica-dental-backend.onrender.com")
    print(f"\n🔑 Credenciales existentes:")
    print(f"   Odontólogo: odontologo@clinica-demo.com / odontologo123")
    print(f"   Pacientes:  paciente1-5@test.com / paciente123")
    print(f"\n✅ NO necesitas poblar datos nuevamente, usa los existentes!")

if __name__ == '__main__':
    asociar_subdominio()
