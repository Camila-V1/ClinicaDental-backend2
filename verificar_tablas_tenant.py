#!/usr/bin/env python
"""
Script para verificar y crear tablas en el esquema del tenant.
Ejecutar: python verificar_tablas_tenant.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import tenant_context, get_tenant_model
from backups.models import BackupRecord

print("=" * 70)
print("🔍 VERIFICACIÓN DE TABLAS EN TENANT")
print("=" * 70)
print()

# Obtener el tenant
TenantModel = get_tenant_model()
try:
    tenant = TenantModel.objects.get(schema_name='clinica_demo')
    print(f"✅ Tenant encontrado: {tenant.schema_name} - {tenant.nombre}")
except TenantModel.DoesNotExist:
    print("❌ No existe tenant 'clinica_demo'")
    print("\n📋 Tenants disponibles:")
    for t in TenantModel.objects.all():
        print(f"   - {t.schema_name}: {t.nombre}")
    sys.exit(1)

print()

# Cambiar al contexto del tenant
with tenant_context(tenant):
    print(f"📍 Conectado al esquema: {connection.schema_name}")
    print()
    
    # 1. Listar todas las tablas en el esquema
    print("1️⃣ Tablas existentes en el esquema:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema()
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            for table in tables:
                table_name = table[0]
                if 'backup' in table_name.lower():
                    print(f"   ✅ {table_name}")
                else:
                    print(f"   - {table_name}")
        else:
            print("   ⚠️ No hay tablas en el esquema")
    
    print()
    
    # 2. Verificar tabla de backups específicamente
    print("2️⃣ Verificando tabla backups_backuprecord:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = current_schema()
                AND table_name = 'backups_backuprecord'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("   ✅ La tabla backups_backuprecord EXISTE")
            
            # Contar registros
            try:
                count = BackupRecord.objects.count()
                print(f"   📊 Registros en la tabla: {count}")
            except Exception as e:
                print(f"   ⚠️ Error al contar registros: {e}")
        else:
            print("   ❌ La tabla backups_backuprecord NO EXISTE")
            print()
            print("   🔧 SOLUCIÓN:")
            print("   Ejecuta estos comandos en Render Shell:")
            print()
            print("   # Opción 1: Forzar re-aplicación de migraciones")
            print("   python manage.py migrate_schemas --tenant --fake-initial")
            print()
            print("   # Opción 2: Crear tabla manualmente")
            print("   python crear_tabla_backups.py")
    
    print()
    
    # 3. Verificar migraciones aplicadas
    print("3️⃣ Migraciones de backups aplicadas:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT app, name, applied 
            FROM django_migrations 
            WHERE app = 'backups'
            ORDER BY applied;
        """)
        migrations = cursor.fetchall()
        
        if migrations:
            for mig in migrations:
                print(f"   ✅ {mig[0]}.{mig[1]} (aplicada: {mig[2]})")
        else:
            print("   ❌ No hay migraciones de backups registradas")
            print("   💡 Esto explica por qué la tabla no existe")

print()
print("=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 70)
print()

# Dar recomendaciones finales
with tenant_context(tenant):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = current_schema()
                AND table_name = 'backups_backuprecord'
            );
        """)
        tabla_existe = cursor.fetchone()[0]

if not tabla_existe:
    print("🚨 PROBLEMA DETECTADO:")
    print("   La tabla backups_backuprecord NO existe en el esquema del tenant")
    print()
    print("📋 PASOS PARA SOLUCIONAR:")
    print()
    print("   1. Ejecutar en Render Shell:")
    print("      python crear_tabla_backups.py")
    print()
    print("   2. O alternativamente:")
    print("      python manage.py migrate backups --database=default --schema=clinica_demo")
    print()
else:
    print("✅ TODO CORRECTO:")
    print("   La tabla existe y el sistema de backups debería funcionar")
    print()

