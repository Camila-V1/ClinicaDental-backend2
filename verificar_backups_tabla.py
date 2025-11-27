import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

# Cambiar al schema del tenant
connection.set_schema('clinica_demo')

# Ejecutar consulta
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'clinica_demo' 
        AND table_name LIKE '%backup%'
    """)
    tables = cursor.fetchall()
    
    print("=== TABLAS DE BACKUPS EN clinica_demo ===")
    if tables:
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("  ❌ NO HAY TABLAS DE BACKUPS")
    
    # Verificar todas las tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'clinica_demo' 
        ORDER BY table_name
    """)
    all_tables = cursor.fetchall()
    
    print("\n=== TODAS LAS TABLAS ===")
    for table in all_tables:
        print(f"  - {table[0]}")
