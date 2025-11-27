#!/usr/bin/env python
"""
Script de diagnóstico para ejecutar en Render
Verifica configuración de Django y apps instaladas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from django.db import connection

print("="*80)
print("  DIAGNÓSTICO DEL SISTEMA")
print("="*80)

print("\n1️⃣ APPS INSTALADAS:")
print("-" * 80)
for app in settings.INSTALLED_APPS:
    try:
        app_config = apps.get_app_config(app.split('.')[-1])
        print(f"✅ {app:<40} OK")
    except:
        print(f"❌ {app:<40} ERROR")

print("\n2️⃣ TENANT_APPS:")
print("-" * 80)
if hasattr(settings, 'TENANT_APPS'):
    for app in settings.TENANT_APPS:
        try:
            app_config = apps.get_app_config(app.split('.')[-1])
            print(f"✅ {app:<40} OK")
        except Exception as e:
            print(f"❌ {app:<40} ERROR: {str(e)}")
else:
    print("❌ TENANT_APPS no definido")

print("\n3️⃣ URLS CONFIGURADAS:")
print("-" * 80)
try:
    from django.urls import get_resolver
    from core import urls_tenant
    
    resolver = get_resolver(urls_tenant)
    url_patterns = resolver.url_patterns
    
    print(f"Total URL patterns: {len(url_patterns)}")
    for pattern in url_patterns:
        pattern_str = str(pattern.pattern)
        if 'backups' in pattern_str or 'facturacion' in pattern_str:
            print(f"  📍 {pattern_str}")
except Exception as e:
    print(f"❌ Error obteniendo URLs: {str(e)}")

print("\n4️⃣ VERIFICAR APP BACKUPS:")
print("-" * 80)
try:
    from backups.models import BackupRecord
    print("✅ BackupRecord importado correctamente")
    print(f"   Modelo: {BackupRecord._meta.db_table}")
except Exception as e:
    print(f"❌ Error importando BackupRecord: {str(e)}")

try:
    from backups.views import BackupHistoryListView
    print("✅ BackupHistoryListView importado correctamente")
except Exception as e:
    print(f"❌ Error importando BackupHistoryListView: {str(e)}")

try:
    from backups.urls import urlpatterns as backup_urls
    print(f"✅ URLs de backups cargadas: {len(backup_urls)} patterns")
    for pattern in backup_urls:
        print(f"   📍 {pattern.pattern}")
except Exception as e:
    print(f"❌ Error importando URLs de backups: {str(e)}")

print("\n5️⃣ VERIFICAR APP FACTURACION:")
print("-" * 80)
try:
    from facturacion.views_pagos import PagoViewSet
    print("✅ PagoViewSet importado correctamente")
    
    # Verificar serializer_class sin ejecutar queryset
    serializer = getattr(PagoViewSet, 'serializer_class', None)
    if serializer:
        print(f"   serializer_class: {serializer}")
    else:
        print("   ❌ serializer_class: NO DEFINIDO")
    
    # Verificar que queryset está definido sin ejecutarlo
    if hasattr(PagoViewSet, 'queryset'):
        print(f"   queryset: DEFINIDO (model={PagoViewSet.queryset.model.__name__})")
    else:
        print("   ❌ queryset: NO DEFINIDO")
        
except Exception as e:
    print(f"❌ Error importando PagoViewSet: {str(e)}")

print("\n6️⃣ VERIFICAR TABLAS EN BD:")
print("-" * 80)
try:
    # Conectar al schema del tenant
    from django_tenants.utils import schema_context
    from tenants.models import Clinica
    
    tenant = Clinica.objects.filter(schema_name='clinica_demo').first()
    if tenant:
        print(f"✅ Tenant encontrado: {tenant.nombre}")
        
        with schema_context(tenant.schema_name):
            with connection.cursor() as cursor:
                # Verificar tabla de backups
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'clinica_demo'
                        AND table_name = 'backups_backuprecord'
                    );
                """)
                exists = cursor.fetchone()[0]
                if exists:
                    print("✅ Tabla backups_backuprecord existe")
                    
                    # Contar registros
                    cursor.execute("SELECT COUNT(*) FROM backups_backuprecord;")
                    count = cursor.fetchone()[0]
                    print(f"   Registros: {count}")
                else:
                    print("❌ Tabla backups_backuprecord NO existe")
                
                # Verificar tabla de pagos
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'clinica_demo'
                        AND table_name = 'facturacion_pago'
                    );
                """)
                exists = cursor.fetchone()[0]
                if exists:
                    print("✅ Tabla facturacion_pago existe")
                    
                    cursor.execute("SELECT COUNT(*) FROM facturacion_pago;")
                    count = cursor.fetchone()[0]
                    print(f"   Registros: {count}")
                else:
                    print("❌ Tabla facturacion_pago NO existe")
    else:
        print("❌ Tenant 'clinica_demo' no encontrado")
        
except Exception as e:
    print(f"❌ Error verificando BD: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("  FIN DEL DIAGNÓSTICO")
print("="*80)
