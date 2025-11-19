#!/usr/bin/env python
"""
Script para verificar el modelo Tenant y crear el tenant de prueba si no existe
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain
from django.db import connection

def verificar_modelo():
    """Verifica los campos del modelo Clinica"""
    print("="*80)
    print("🔍 VERIFICANDO MODELO CLINICA")
    print("="*80)
    
    # Obtener campos del modelo
    campos = [f.name for f in Clinica._meta.get_fields()]
    print("\n📋 Campos disponibles en Clinica:")
    for campo in sorted(campos):
        print(f"   - {campo}")
    
    print("\n" + "="*80)
    print("📊 TENANTS EXISTENTES")
    print("="*80)
    
    clinicas = Clinica.objects.all()
    if clinicas.exists():
        for clinica in clinicas:
            print(f"\n✓ {clinica.nombre}")
            print(f"  Schema: {clinica.schema_name}")
            print(f"  Dominio: {clinica.dominio}")
            print(f"  Activo: {clinica.activo}")
            print(f"  Creado: {clinica.creado}")
            
            # Mostrar dominios asociados
            dominios = Domain.objects.filter(tenant=clinica)
            if dominios.exists():
                print(f"  Dominios:")
                for dom in dominios:
                    primary = "🌟 Primary" if dom.is_primary else ""
                    print(f"    → {dom.domain} {primary}")
    else:
        print("\n⚠️  No hay tenants en la base de datos")
    
    print("\n" + "="*80)

def crear_tenant_demo():
    """Crea el tenant de demostración si no existe"""
    print("\n🏥 CREANDO TENANT DE DEMOSTRACIÓN")
    print("="*80)
    
    # Verificar si ya existe
    if Clinica.objects.filter(dominio='clinica-demo').exists():
        print("✓ El tenant 'clinica-demo' ya existe")
        tenant = Clinica.objects.get(dominio='clinica-demo')
    else:
        print("➕ Creando tenant 'clinica-demo'...")
        tenant = Clinica.objects.create(
            schema_name='clinica_demo',
            nombre='Clínica Demo',
            dominio='clinica-demo',
            activo=True
        )
        print(f"✓ Tenant creado: {tenant.nombre}")
    
    # Verificar/crear dominio para desarrollo
    domain_localhost = 'clinica-demo.localhost'
    if not Domain.objects.filter(domain=domain_localhost).exists():
        print(f"➕ Creando dominio: {domain_localhost}")
        Domain.objects.create(
            domain=domain_localhost,
            tenant=tenant,
            is_primary=True
        )
    else:
        print(f"✓ Dominio {domain_localhost} ya existe")
    
    # Verificar/crear dominio para Render (si aplica)
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if render_hostname:
        domain_render = f'clinica-demo.{render_hostname}'
        if not Domain.objects.filter(domain=domain_render).exists():
            print(f"➕ Creando dominio: {domain_render}")
            Domain.objects.create(
                domain=domain_render,
                tenant=tenant,
                is_primary=False
            )
        else:
            print(f"✓ Dominio {domain_render} ya existe")
    
    print("\n✅ Tenant de demostración listo")
    print("="*80)

if __name__ == '__main__':
    try:
        verificar_modelo()
        crear_tenant_demo()
        
        print("\n" + "="*80)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
