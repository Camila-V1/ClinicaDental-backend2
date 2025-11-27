"""
Script para verificar estado del sistema de backups en producción
Diagnostica si la tabla existe y si las URLs están configuradas
"""
import requests
import json

# Configuración
BASE_URL = 'https://clinica-dental-backend.onrender.com'
EMAIL = 'admin@clinicademo1.com'
PASSWORD = 'admin123'
TENANT_ID = 'clinica_demo'

def verificar_sistema_backups():
    """Verifica el estado completo del sistema de backups"""
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE BACKUPS EN PRODUCCIÓN")
    print("=" * 70)
    
    # Headers que simulan un navegador real
    headers_navegador = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://clinica-dental-backend.onrender.com',
        'Referer': 'https://clinica-dental-backend.onrender.com/',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    # Paso 1: Login
    print("\n1️⃣  AUTENTICACIÓN")
    print("-" * 70)
    try:
        login_headers = headers_navegador.copy()
        login_headers['Content-Type'] = 'application/json'
        login_headers['Host'] = TENANT_ID
        
        response = requests.post(
            f'{BASE_URL}/api/token/',
            json={'email': EMAIL, 'password': PASSWORD},
            headers=login_headers,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Error en login: {response.text}")
            return
        
        data = response.json()
        token = data.get('access')
        print(f"   ✅ Login exitoso")
        print(f"   Token: {token[:50]}...")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return
    
    # Headers para las siguientes requests (con simulación de navegador)
    headers = headers_navegador.copy()
    headers['Content-Type'] = 'application/json'
    headers['Host'] = TENANT_ID
    headers['Authorization'] = f'Bearer {token}'
    
    # Paso 2: Verificar usuario
    print("\n2️⃣  VERIFICACIÓN DE USUARIO Y TENANT")
    print("-" * 70)
    try:
        response = requests.get(
            f'{BASE_URL}/api/usuarios/me/',
            headers=headers,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Usuario verificado")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Tipo: {user_data.get('tipo_usuario')}")
            print(f"   ID: {user_data.get('id')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Paso 3: Probar endpoints de backups
    print("\n3️⃣  PRUEBA DE ENDPOINTS DE BACKUPS")
    print("-" * 70)
    
    endpoints = [
        ('GET', '/api/backups/history/', 'Listar historial'),
        ('POST', '/api/backups/create/', 'Crear backup'),
    ]
    
    for method, endpoint, descripcion in endpoints:
        print(f"\n   📡 {method} {endpoint}")
        print(f"       {descripcion}")
        try:
            if method == 'GET':
                response = requests.get(
                    f'{BASE_URL}{endpoint}',
                    headers=headers,
                    timeout=10
                )
            else:
                response = requests.post(
                    f'{BASE_URL}{endpoint}',
                    headers=headers,
                    json={'descripcion': 'Test backup desde verificación'},
                    timeout=10
                )
            
            print(f"       Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"       ✅ FUNCIONANDO")
                try:
                    data = response.json()
                    print(f"       Response: {json.dumps(data, indent=6)[:200]}")
                except:
                    print(f"       Response (text): {response.text[:200]}")
            elif response.status_code == 404:
                print(f"       ❌ 404 - ENDPOINT NO ENCONTRADO")
                print(f"       Esto significa que:")
                print(f"          • La app 'backups' no está en TENANT_APPS, O")
                print(f"          • Las URLs no están incluidas en urls_tenant.py, O")
                print(f"          • Las migraciones no se ejecutaron")
            elif response.status_code == 403:
                print(f"       ⚠️  403 - PERMISOS INSUFICIENTES")
                print(f"       El usuario no tiene rol ADMIN")
            elif response.status_code == 500:
                print(f"       ❌ 500 - ERROR INTERNO")
                print(f"       Probablemente la tabla no existe en la BD")
                try:
                    error = response.json()
                    print(f"       Error: {error}")
                except:
                    print(f"       Response: {response.text[:300]}")
            else:
                print(f"       ⚠️  Status inesperado: {response.status_code}")
                print(f"       Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"       ❌ Excepción: {e}")
    
    # Paso 4: Recomendaciones
    print("\n" + "=" * 70)
    print("📋 DIAGNÓSTICO Y RECOMENDACIONES")
    print("=" * 70)
    print("""
Si ves 404 en los endpoints de backups, las posibles causas son:

1. ❌ Migraciones no ejecutadas en tenant clinica_demo
   → Solución: Conectarse al shell de Render y ejecutar:
     python manage.py migrate_schemas --schema=clinica_demo

2. ❌ El tenant clinica_demo no existe en producción
   → Solución: Ejecutar el script de población:
     python scripts_poblacion/poblar_todo.py

3. ❌ La app 'backups' no está en TENANT_APPS (poco probable)
   → Verificar: core/settings.py línea 85

4. ❌ Las URLs no están incluidas (poco probable)
   → Verificar: core/urls_tenant.py línea 34

Para conectarse al shell de Render:
1. Ir al dashboard de Render
2. Seleccionar el servicio
3. Shell → Connect
4. Ejecutar los comandos de diagnóstico

Comandos útiles en el shell de Render:
```bash
# Ver si la tabla existe
python manage.py shell
>>> from django_tenants.utils import schema_context
>>> with schema_context('clinica_demo'):
...     from backups.models import BackupRecord
...     print(BackupRecord.objects.count())

# Ejecutar migraciones manualmente
python manage.py migrate_schemas --schema=clinica_demo

# Ver todos los tenants
python manage.py shell
>>> from tenants.models import Tenant
>>> for t in Tenant.objects.all():
...     print(f"{t.schema_name}: {t.name}")
```
    """)
    print("=" * 70)

if __name__ == '__main__':
    verificar_sistema_backups()
