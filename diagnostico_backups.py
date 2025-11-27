#!/usr/bin/env python
"""
Script de diagnóstico para el módulo de backups.
Ejecutar en Render Shell: python diagnostico_backups.py
"""

import sys
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("=" * 60)
print("🔍 DIAGNÓSTICO DEL MÓDULO DE BACKUPS")
print("=" * 60)
print()

# 1. Verificar que el módulo se puede importar
print("1️⃣ Verificando importación del módulo...")
try:
    import backups
    print("   ✅ Módulo 'backups' importado correctamente")
    print(f"   📁 Ubicación: {backups.__file__}")
except ImportError as e:
    print(f"   ❌ Error al importar módulo: {e}")
    sys.exit(1)

print()

# 2. Verificar que el modelo se puede importar
print("2️⃣ Verificando modelo BackupRecord...")
try:
    from backups.models import BackupRecord
    print("   ✅ Modelo BackupRecord importado correctamente")
    print(f"   📋 Campos: {[f.name for f in BackupRecord._meta.fields]}")
except ImportError as e:
    print(f"   ❌ Error al importar modelo: {e}")
    sys.exit(1)

print()

# 3. Verificar que las vistas se pueden importar
print("3️⃣ Verificando vistas...")
try:
    from backups.views import (
        CreateBackupView,
        BackupHistoryListView,
        DownloadBackupView,
        DeleteBackupView
    )
    print("   ✅ CreateBackupView importada")
    print("   ✅ BackupHistoryListView importada")
    print("   ✅ DownloadBackupView importada")
    print("   ✅ DeleteBackupView importada")
except ImportError as e:
    print(f"   ❌ Error al importar vistas: {e}")
    sys.exit(1)

print()

# 4. Verificar migraciones
print("4️⃣ Verificando migraciones...")
try:
    from django.core.management import call_command
    from io import StringIO
    
    output = StringIO()
    call_command('showmigrations', 'backups', stdout=output)
    migrations_output = output.getvalue()
    
    if '[X]' in migrations_output:
        print("   ✅ Migraciones aplicadas:")
        for line in migrations_output.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print("   ⚠️ Migraciones no aplicadas")
        print(migrations_output)
except Exception as e:
    print(f"   ❌ Error al verificar migraciones: {e}")

print()

# 5. Verificar tabla en base de datos
print("5️⃣ Verificando tabla en base de datos...")
try:
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema()
            AND table_name LIKE '%backup%'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print("   ✅ Tablas encontradas:")
            for table in tables:
                print(f"      - {table[0]}")
        else:
            print("   ❌ No se encontraron tablas de backups")
except Exception as e:
    print(f"   ❌ Error al verificar tablas: {e}")

print()

# 6. Verificar URLs
print("6️⃣ Verificando configuración de URLs...")
try:
    from django.urls import get_resolver
    from django.urls.resolvers import URLPattern, URLResolver
    
    def list_urls(lis, acc=''):
        for entry in lis:
            if isinstance(entry, URLPattern):
                yield acc + str(entry.pattern)
            elif isinstance(entry, URLResolver):
                yield from list_urls(entry.url_patterns, acc + str(entry.pattern))
    
    urls = list(list_urls(get_resolver().url_patterns))
    backup_urls = [url for url in urls if 'backup' in url.lower()]
    
    if backup_urls:
        print("   ✅ URLs de backups encontradas:")
        for url in backup_urls:
            print(f"      - {url}")
    else:
        print("   ❌ No se encontraron URLs de backups")
        print("   💡 Mostrando todas las URLs de 'api/':")
        api_urls = [url for url in urls if 'api/' in url]
        for url in api_urls[:10]:
            print(f"      - {url}")
except Exception as e:
    print(f"   ❌ Error al verificar URLs: {e}")

print()

# 7. Verificar INSTALLED_APPS
print("7️⃣ Verificando INSTALLED_APPS...")
try:
    from django.conf import settings
    
    if 'backups' in settings.INSTALLED_APPS:
        print("   ✅ 'backups' está en INSTALLED_APPS")
    else:
        print("   ❌ 'backups' NO está en INSTALLED_APPS")
        
    # Verificar si está en TENANT_APPS
    if hasattr(settings, 'TENANT_APPS'):
        if 'backups' in settings.TENANT_APPS:
            print("   ✅ 'backups' está en TENANT_APPS")
        else:
            print("   ⚠️ 'backups' NO está en TENANT_APPS")
except Exception as e:
    print(f"   ❌ Error al verificar settings: {e}")

print()

# 8. Probar acceso al modelo
print("8️⃣ Probando acceso al modelo...")
try:
    from backups.models import BackupRecord
    
    count = BackupRecord.objects.count()
    print(f"   ✅ Registros en BackupRecord: {count}")
    
    if count > 0:
        latest = BackupRecord.objects.latest('created_at')
        print(f"   📄 Último backup: {latest.file_name}")
except Exception as e:
    print(f"   ❌ Error al acceder al modelo: {e}")

print()

# 9. Verificar serializer
print("9️⃣ Verificando serializer...")
try:
    from backups.serializers import BackupRecordSerializer
    print("   ✅ BackupRecordSerializer importado correctamente")
except ImportError as e:
    print(f"   ❌ Error al importar serializer: {e}")

print()

# 10. Test de vista
print("🔟 Test de vista BackupHistoryListView...")
try:
    from backups.views import BackupHistoryListView
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    factory = RequestFactory()
    
    # Crear request simulado
    request = factory.get('/api/backups/history/')
    
    # Obtener primer usuario para simular autenticación
    user = User.objects.first()
    if user:
        request.user = user
        print(f"   👤 Usuario de prueba: {user.email}")
        
        # Intentar instanciar la vista
        view = BackupHistoryListView.as_view()
        print("   ✅ Vista instanciada correctamente")
    else:
        print("   ⚠️ No hay usuarios en la base de datos")
        
except Exception as e:
    print(f"   ❌ Error en test de vista: {e}")

print()
print("=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
print()
print("📝 RECOMENDACIONES:")
print()
print("Si todos los checks son ✅ pero sigue el 404:")
print("1. Reiniciar el servidor de Django")
print("2. Verificar que el tenant_id en el header es correcto")
print("3. Revisar los logs de Django para errores de importación")
print("4. Verificar que la URL no tiene typos: /api/backups/history/")
print()
print("Si hay ❌ en algún check:")
print("1. Aplicar migraciones: python manage.py migrate backups")
print("2. Verificar que backups/__init__.py existe")
print("3. Revisar que no hay errores de sintaxis en los archivos")
print()
