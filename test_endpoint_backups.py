#!/usr/bin/env python
"""
Script para probar que el endpoint de backups funciona correctamente.
Ejecutar: python test_endpoint_backups.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django_tenants.utils import tenant_context, get_tenant_model
from backups.views import BackupHistoryListView
from usuarios.models import Usuario

print("=" * 70)
print("🧪 TEST DEL ENDPOINT DE BACKUPS")
print("=" * 70)
print()

# Obtener el tenant
TenantModel = get_tenant_model()
tenant = TenantModel.objects.get(schema_name='clinica_demo')
print(f"✅ Tenant: {tenant.nombre}")
print()

# Cambiar al contexto del tenant
with tenant_context(tenant):
    # Obtener primer usuario para simular autenticación
    user = Usuario.objects.first()
    
    if not user:
        print("❌ No hay usuarios en la base de datos")
        print("   Ejecuta: python scripts_poblacion/poblar_todo.py")
        sys.exit(1)
    
    print(f"👤 Usuario de prueba: {user.email}")
    print()
    
    # Crear request simulado
    factory = RequestFactory()
    request = factory.get('/api/backups/history/')
    request.user = user
    
    # Ejecutar la vista
    print("🔄 Ejecutando vista BackupHistoryListView...")
    
    try:
        view = BackupHistoryListView.as_view()
        response = view(request)
        
        print()
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ÉXITO: El endpoint responde correctamente")
            
            if hasattr(response, 'data'):
                print(f"📦 Datos devueltos: {response.data}")
                print(f"📈 Cantidad de backups: {len(response.data)}")
            else:
                print("⚠️  La respuesta no tiene 'data' (posible issue con el renderer)")
        else:
            print(f"❌ ERROR: Status code inesperado: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"   Detalles: {response.data}")
                
    except Exception as e:
        print(f"❌ ERROR al ejecutar la vista: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print()
print("=" * 70)
print("✅ TEST COMPLETADO")
print("=" * 70)
print()
print("💡 CONCLUSIÓN:")
print("   Si el status es 200, el endpoint /api/backups/history/ funciona")
print("   Ahora prueba desde el frontend:")
print()
print("   GET https://tu-app.onrender.com/api/backups/history/")
print("   Headers:")
print("     - Authorization: Bearer <tu-token>")
print("     - x-tenant-id: <id-del-tenant>")
print()

