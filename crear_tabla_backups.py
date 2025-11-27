#!/usr/bin/env python
"""
Script para crear la tabla de backups en el tenant si no existe.
Ejecutar: python crear_tabla_backups.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import tenant_context, get_tenant_model
from django.core.management import call_command

print("=" * 70)
print("🔧 CREACIÓN DE TABLA BACKUPS EN TENANT")
print("=" * 70)
print()

# Obtener el tenant
TenantModel = get_tenant_model()
try:
    tenant = TenantModel.objects.get(schema_name='clinica_demo')
    print(f"✅ Tenant encontrado: {tenant.schema_name} - {tenant.name}")
except TenantModel.DoesNotExist:
    print("❌ No existe tenant 'clinica_demo'")
    sys.exit(1)

print()

# Cambiar al contexto del tenant
with tenant_context(tenant):
    print(f"📍 Trabajando en esquema: {connection.schema_name}")
    print()
    
    # Verificar si la tabla ya existe
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = current_schema()
                AND table_name = 'backups_backuprecord'
            );
        """)
        ya_existe = cursor.fetchone()[0]
    
    if ya_existe:
        print("ℹ️  La tabla backups_backuprecord ya existe")
        print()
        
        # Verificar estructura
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = current_schema()
                AND table_name = 'backups_backuprecord'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print("📋 Columnas existentes:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
        
        print()
        print("✅ No es necesario crear la tabla")
        
    else:
        print("⚠️  La tabla no existe. Creándola...")
        print()
        
        # Crear la tabla usando SQL directo
        with connection.cursor() as cursor:
            print("1️⃣ Creando tabla backups_backuprecord...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups_backuprecord (
                    id SERIAL PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size BIGINT NOT NULL,
                    backup_type VARCHAR(20) NOT NULL CHECK (backup_type IN ('manual', 'automatico')),
                    created_by_id INTEGER NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT backups_backuprecord_created_by_id_fkey 
                        FOREIGN KEY (created_by_id) 
                        REFERENCES usuarios_usuario(id) 
                        ON DELETE SET NULL
                );
            """)
            print("   ✅ Tabla creada")
            
            print()
            print("2️⃣ Creando índices...")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS backups_backuprecord_created_by_id_idx 
                ON backups_backuprecord(created_by_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS backups_backuprecord_created_at_idx 
                ON backups_backuprecord(created_at DESC);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS backups_backuprecord_backup_type_idx 
                ON backups_backuprecord(backup_type);
            """)
            
            print("   ✅ Índices creados")
            
            print()
            print("3️⃣ Registrando migración en django_migrations...")
            
            # Registrar la migración como aplicada
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('backups', '0001_initial', NOW())
                ON CONFLICT DO NOTHING;
            """)
            
            print("   ✅ Migración registrada")
        
        print()
        print("=" * 70)
        print("✅ TABLA CREADA EXITOSAMENTE")
        print("=" * 70)
        print()
        
        # Verificar que todo quedó bien
        from backups.models import BackupRecord
        
        try:
            count = BackupRecord.objects.count()
            print(f"✅ Verificación: La tabla está accesible")
            print(f"📊 Registros actuales: {count}")
        except Exception as e:
            print(f"❌ Error al verificar: {e}")

print()
print("🎉 Proceso completado")
print()
print("💡 Ahora prueba:")
print("   GET https://tu-app.onrender.com/api/backups/history/")
print("   Headers: Authorization: Bearer <token>, x-tenant-id: <id>")
print()

