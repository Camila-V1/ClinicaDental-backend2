"""
Script para probar endpoints de facturación y backups
Verifica que los errores 500 y 404 estén resueltos
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "https://clinica-dental-backend.onrender.com"
TENANT_ID = "clinica_demo"

# Credenciales del admin
ADMIN_EMAIL = "admin@clinicademo1.com"
ADMIN_PASSWORD = "admin123"

def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def login():
    """Autenticar y obtener token JWT"""
    print_separator("🔐 AUTENTICACIÓN")
    
    url = f"{BASE_URL}/api/token/"
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    print(f"📡 POST {url}")
    print(f"📦 Tenant: {TENANT_ID}")
    print(f"👤 Usuario: {ADMIN_EMAIL}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            print(f"✅ Login exitoso")
            print(f"🎫 Token obtenido: {token[:50]}...")
            return token
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Excepción en login: {str(e)}")
        return None

def test_pagos(token):
    """Probar endpoint de pagos (antes daba error 500)"""
    print_separator("💰 TEST: /api/facturacion/pagos/")
    
    url = f"{BASE_URL}/api/facturacion/pagos/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    
    print(f"📡 GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ÉXITO - Endpoint funcionando correctamente")
            print(f"📦 Datos recibidos: {len(data)} pagos")
            if data:
                print(f"📄 Primer pago: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
            else:
                print(f"ℹ️  No hay pagos registrados (array vacío es correcto)")
            return True
        elif response.status_code == 500:
            print(f"❌ ERROR 500 - Internal Server Error (PROBLEMA PERSISTE)")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return False

def test_backups(token):
    """Probar endpoint de backups (antes daba error 404)"""
    print_separator("💾 TEST: /api/backups/history/")
    
    url = f"{BASE_URL}/api/backups/history/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    
    print(f"📡 GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ÉXITO - Endpoint funcionando correctamente")
            print(f"📦 Datos recibidos: {len(data)} backups")
            if data:
                print(f"📄 Primer backup: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
            else:
                print(f"ℹ️  No hay backups registrados (array vacío es correcto)")
            return True
        elif response.status_code == 404:
            print(f"❌ ERROR 404 - Not Found (PROBLEMA PERSISTE)")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return False

def test_facturas(token):
    """Probar endpoint de facturas (para contexto adicional)"""
    print_separator("📋 TEST ADICIONAL: /api/facturacion/facturas/")
    
    url = f"{BASE_URL}/api/facturacion/facturas/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    
    print(f"📡 GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Facturas funcionando correctamente")
            print(f"📦 Total facturas: {len(data)}")
            return True
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return False

def main():
    """Función principal"""
    print("\n" + "🏥"*40)
    print("  PRUEBA DE ENDPOINTS - CLINICA DENTAL")
    print("  Verificando correcciones de errores 500 y 404")
    print("  Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🏥"*40)
    
    # 1. Login
    token = login()
    if not token:
        print("\n❌ No se pudo obtener el token. Abortando pruebas.")
        return
    
    # 2. Probar endpoints
    result_pagos = test_pagos(token)
    result_backups = test_backups(token)
    result_facturas = test_facturas(token)
    
    # 3. Resumen final
    print_separator("📊 RESUMEN DE RESULTADOS")
    
    print(f"\n{'Endpoint':<40} {'Resultado':<20}")
    print("-" * 60)
    print(f"{'🔐 Autenticación':<40} {'✅ OK' if token else '❌ FALLO':<20}")
    print(f"{'💰 /api/facturacion/pagos/':<40} {'✅ OK (200)' if result_pagos else '❌ FALLO':<20}")
    print(f"{'💾 /api/backups/history/':<40} {'✅ OK (200)' if result_backups else '❌ FALLO':<20}")
    print(f"{'📋 /api/facturacion/facturas/':<40} {'✅ OK (200)' if result_facturas else '❌ FALLO':<20}")
    
    print("\n" + "="*60)
    
    if result_pagos and result_backups:
        print("✅ TODOS LOS TESTS PASARON - Errores corregidos exitosamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON - Revisar logs de Render")
        if not result_pagos:
            print("   - Error 500 en /api/facturacion/pagos/ persiste")
        if not result_backups:
            print("   - Error 404 en /api/backups/history/ persiste")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
