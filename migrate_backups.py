#!/usr/bin/env python
"""
Script para ejecutar migraciones del modelo BackupRecord en todos los schemas de tenants.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context, get_tenant_model
from django.core.management import call_command

def migrate_backups_in_all_tenants():
    """Ejecuta migraciones de backups en todos los schemas de tenants."""
    
    Clinica = get_tenant_model()
    
    # Obtener todas las clínicas
    clinicas = Clinica.objects.all()
    
    print(f"📋 Total de clínicas encontradas: {clinicas.count()}")
    
    for clinica in clinicas:
        schema_name = clinica.schema_name
        
        # Saltar el schema public
        if schema_name == 'public':
            continue
        
        print(f"\n{'='*60}")
        print(f"🔧 Ejecutando migraciones en schema: {schema_name}")
        print(f"{'='*60}")
        
        try:
            with schema_context(schema_name):
                # Ejecutar migrate específicamente para la app backups
                call_command('migrate', 'backups', '--database=default', verbosity=2)
                print(f"✅ Migraciones ejecutadas exitosamente en {schema_name}")
        
        except Exception as e:
            print(f"❌ Error al ejecutar migraciones en {schema_name}: {str(e)}")
            continue
    
    print("\n" + "="*60)
    print("✅ Proceso completado")
    print("="*60)


if __name__ == '__main__':
    migrate_backups_in_all_tenants()
