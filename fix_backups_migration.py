#!/usr/bin/env python
"""
Script para verificar y crear la tabla backups_backuprecord en todos los schemas de tenant.

Este script:
1. Verifica si la tabla existe en cada schema
2. Si no existe, ejecuta la migración específica de backups
3. Valida que la tabla se haya creado correctamente
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from django.core.management import call_command

def table_exists(schema_name, table_name):
    """Verificar si una tabla existe en un schema."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = %s
            );
        """, [schema_name, table_name])
        return cursor.fetchone()[0]

def create_backups_table(schema_name):
    """Crear tabla backups_backuprecord en el schema."""
    print(f"\n🔧 Creando tabla backups_backuprecord en schema: {schema_name}")
    
    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {schema_name}")
        
        # Crear tabla manualmente si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups_backuprecord (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT NOT NULL,
                backup_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by_id INTEGER REFERENCES usuarios_usuario(id) ON DELETE SET NULL
            );
        """)
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS backups_backuprecord_created_by_id_idx 
            ON backups_backuprecord(created_by_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS backups_backuprecord_created_at_idx 
            ON backups_backuprecord(created_at);
        """)
        
        print(f"✅ Tabla backups_backuprecord creada en {schema_name}")

def main():
    """Ejecutar verificación y creación de tabla backups."""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN Y CREACIÓN DE TABLA BACKUPS")
    print("="*70)
    
    TenantModel = get_tenant_model()
    public_schema = get_public_schema_name()
    
    # Obtener todos los tenants (excluyendo public)
    tenants = TenantModel.objects.exclude(schema_name=public_schema)
    
    print(f"\n📋 Total de clínicas encontradas: {tenants.count()}\n")
    
    for tenant in tenants:
        schema_name = tenant.schema_name
        print(f"\n{'='*70}")
        print(f"🏥 Procesando: {tenant.nombre} (schema: {schema_name})")
        print(f"{'='*70}")
        
        # Verificar si la tabla existe
        if table_exists(schema_name, 'backups_backuprecord'):
            print(f"✅ La tabla backups_backuprecord ya existe en {schema_name}")
        else:
            print(f"⚠️  La tabla backups_backuprecord NO existe en {schema_name}")
            try:
                create_backups_table(schema_name)
            except Exception as e:
                print(f"❌ Error al crear tabla en {schema_name}: {e}")
                continue
        
        # Verificar nuevamente
        if table_exists(schema_name, 'backups_backuprecord'):
            print(f"✅ Verificación exitosa: tabla presente en {schema_name}")
        else:
            print(f"❌ Error: tabla no se creó en {schema_name}")
    
    print(f"\n{'='*70}")
    print("✅ PROCESO COMPLETADO")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
