import requests

BASE_URL = 'https://clinica-dental-backend.onrender.com'

# Login
print("="*80)
print("TEST: ¿Qué schema está activo en producción?")
print("="*80)

response = requests.post(
    f'{BASE_URL}/api/token/',
    json={'email': 'admin@clinicademo1.com', 'password': 'admin123'}
)

if response.status_code == 200:
    token = response.json()['access']
    print(f"✅ Login exitoso")
    
    # Probar endpoint de usuarios (que SÍ funciona)
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Tenant-ID': 'clinica_demo'
    }
    
    print(f"\n📍 Probando /api/usuarios/me/ (funciona)")
    r = requests.get(f'{BASE_URL}/api/usuarios/me/', headers=headers)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.json()}")
    
    print(f"\n📍 Probando /api/reportes/dashboard/ (NO funciona)")
    r = requests.get(f'{BASE_URL}/api/reportes/dashboard/', headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
    
    print(f"\n📍 Probando /api/backups/history/ (NO funciona)")
    r = requests.get(f'{BASE_URL}/api/backups/history/', headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
    
    print(f"\n📍 Probando /api/inventario/materiales/ (¿funciona?)")
    r = requests.get(f'{BASE_URL}/api/inventario/materiales/', headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
    
else:
    print(f"❌ Login falló: {response.status_code}")
