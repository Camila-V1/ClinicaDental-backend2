import requests
import json

BASE_URL = "https://clinica-dental-backend.onrender.com"

print("=" * 80)
print("PRUEBA COMPLETA DE ENDPOINTS DE BACKUPS")
print("=" * 80)

# ============================================================================
# PASO 1: LOGIN
# ============================================================================
print("\n🔐 PASO 1: Login con admin@clinicademo1.com")
print("-" * 80)

login_data = {
    "email": "admin@clinicademo1.com",
    "password": "admin123"
}

login_response = requests.post(
    f"{BASE_URL}/api/token/",
    headers={
        "Content-Type": "application/json",
        "X-Tenant-ID": "clinica_demo"
    },
    json=login_data
)

print(f"Status Code: {login_response.status_code}")

if login_response.status_code == 200:
    tokens = login_response.json()
    access_token = tokens.get("access")
    print(f"✅ Login exitoso")
    print(f"Token (primeros 50 chars): {access_token[:50]}...")
else:
    print(f"❌ Login falló")
    print(f"Response: {login_response.text}")
    exit(1)

# ============================================================================
# PASO 2: VERIFICAR TENANT
# ============================================================================
print("\n🏥 PASO 2: Verificar que clinica_demo existe")
print("-" * 80)

# Headers comunes para todas las peticiones
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "X-Tenant-ID": "clinica_demo"
}

# Probar endpoint de usuarios para confirmar que el tenant funciona
me_response = requests.get(
    f"{BASE_URL}/api/usuarios/me/",
    headers=headers
)

print(f"Status Code: {me_response.status_code}")

if me_response.status_code == 200:
    user_data = me_response.json()
    print(f"✅ Tenant clinica_demo verificado")
    print(f"Usuario: {user_data.get('email')} ({user_data.get('rol')})")
else:
    print(f"❌ No se pudo verificar el tenant")
    print(f"Response: {me_response.text}")
    exit(1)

# ============================================================================
# PASO 3: GET /api/backups/history/
# ============================================================================
print("\n📋 PASO 3: GET /api/backups/history/")
print("-" * 80)

history_response = requests.get(
    f"{BASE_URL}/api/backups/history/",
    headers=headers
)

print(f"Status Code: {history_response.status_code}")
print(f"Response Headers: {dict(history_response.headers)}")

if history_response.status_code == 200:
    try:
        backups = history_response.json()
        print(f"✅ Backups obtenidos exitosamente")
        print(f"Cantidad de backups: {len(backups)}")
        
        if backups:
            print("\nPrimeros 3 backups:")
            for i, backup in enumerate(backups[:3], 1):
                print(f"\n  Backup #{i}:")
                print(f"    - ID: {backup.get('id')}")
                print(f"    - Nombre: {backup.get('file_name')}")
                print(f"    - Tamaño: {backup.get('file_size')} bytes")
                print(f"    - Tipo: {backup.get('backup_type')}")
                print(f"    - Creado: {backup.get('created_at')}")
        else:
            print("  ⚠️ No hay backups registrados aún")
    except json.JSONDecodeError:
        print(f"❌ Respuesta no es JSON válido")
        print(f"Response: {history_response.text[:500]}")
elif history_response.status_code == 404:
    print(f"❌ Endpoint no encontrado (404)")
    print(f"Response: {history_response.text[:500]}")
    print("\n⚠️ ESTO SIGNIFICA:")
    print("   - El endpoint /api/backups/history/ NO existe en Render")
    print("   - Las migraciones de backups NO se aplicaron al tenant")
    print("   - Necesitas hacer deploy para aplicar los cambios")
else:
    print(f"❌ Error {history_response.status_code}")
    print(f"Response: {history_response.text[:500]}")

# ============================================================================
# PASO 4: POST /api/backups/create/
# ============================================================================
print("\n💾 PASO 4: POST /api/backups/create/ (crear backup manual)")
print("-" * 80)

create_response = requests.post(
    f"{BASE_URL}/api/backups/create/",
    headers=headers
)

print(f"Status Code: {create_response.status_code}")

if create_response.status_code == 201:
    try:
        backup_info = create_response.json()
        print(f"✅ Backup creado exitosamente")
        print(f"Mensaje: {backup_info.get('message')}")
        
        if 'backup_info' in backup_info:
            info = backup_info['backup_info']
            print(f"\nDetalles del backup:")
            print(f"  - ID: {info.get('id')}")
            print(f"  - Nombre: {info.get('file_name')}")
            print(f"  - Tamaño: {info.get('file_size')} bytes")
            print(f"  - Tipo: {info.get('backup_type')}")
    except json.JSONDecodeError:
        print(f"❌ Respuesta no es JSON válido")
        print(f"Response: {create_response.text[:500]}")
elif create_response.status_code == 404:
    print(f"❌ Endpoint no encontrado (404)")
    print(f"Response: {create_response.text[:500]}")
elif create_response.status_code == 403:
    print(f"❌ Sin permisos (403) - solo ADMIN puede crear backups")
    print(f"Response: {create_response.text[:500]}")
else:
    print(f"❌ Error {create_response.status_code}")
    print(f"Response: {create_response.text[:500]}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE PRUEBAS")
print("=" * 80)

results = {
    "Login": "✅" if login_response.status_code == 200 else "❌",
    "Verificar Tenant": "✅" if me_response.status_code == 200 else "❌",
    "GET /api/backups/history/": "✅" if history_response.status_code == 200 else "❌",
    "POST /api/backups/create/": "✅" if create_response.status_code == 201 else "❌"
}

for test, status in results.items():
    print(f"{status} {test}")

if history_response.status_code == 404:
    print("\n" + "!" * 80)
    print("⚠️  PROBLEMA DETECTADO")
    print("!" * 80)
    print("\nEl endpoint de backups NO existe en producción.")
    print("\n📝 SOLUCIÓN:")
    print("   1. Haz commit de los cambios en build.sh")
    print("   2. Push a GitHub para trigger el deploy")
    print("   3. Espera 5-10 minutos a que Render re-despliegue")
    print("   4. Vuelve a ejecutar este script")
    print("\n💡 Comandos:")
    print('   git add build.sh')
    print('   git commit -m "fix: Actualizar build.sh para migrar backups"')
    print('   git push origin main')

print("\n" + "=" * 80)
