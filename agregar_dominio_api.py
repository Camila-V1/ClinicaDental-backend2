#!/usr/bin/env python
"""
🔧 Script para agregar api.dentaabcxy.store al tenant clinica_demo
Ejecutar en Render Shell después de cada deploy
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Tenant, Domain

def agregar_dominio_api():
    """Agregar api.dentaabcxy.store a clinica_demo si no existe"""
    
    DOMINIO_API = 'api.dentaabcxy.store'
    TENANT_SCHEMA = 'clinica_demo'
    
    try:
        # Buscar el tenant
        tenant = Tenant.objects.get(schema_name=TENANT_SCHEMA)
        print(f"✅ Tenant encontrado: {tenant.schema_name}")
        
        # Verificar si el dominio ya existe
        dominio_existente = Domain.objects.filter(
            domain=DOMINIO_API,
            tenant=tenant
        ).first()
        
        if dominio_existente:
            print(f"ℹ️  El dominio {DOMINIO_API} ya existe para {TENANT_SCHEMA}")
            return
        
        # Crear el dominio
        nuevo_dominio = Domain.objects.create(
            domain=DOMINIO_API,
            tenant=tenant,
            is_primary=False  # No es primario
        )
        
        print(f"✅ Dominio {DOMINIO_API} agregado exitosamente a {TENANT_SCHEMA}")
        
        # Listar todos los dominios del tenant
        dominios = Domain.objects.filter(tenant=tenant).values_list('domain', 'is_primary')
        print(f"\n📋 Dominios configurados para {TENANT_SCHEMA}:")
        for dominio, es_primario in dominios:
            primary_flag = "⭐ (primario)" if es_primario else ""
            print(f"  - {dominio} {primary_flag}")
        
    except Tenant.DoesNotExist:
        print(f"❌ ERROR: No existe el tenant con schema_name '{TENANT_SCHEMA}'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Agregando dominio API a tenant...")
    agregar_dominio_api()
    print("\n✅ Proceso completado")
