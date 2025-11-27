import requests
import json

# URL del backend
BASE_URL = "https://clinica-dental-backend.onrender.com"

# Credenciales a probar
credenciales = [
    {"email": "paciente1@test.com", "password": "paciente123"},
    {"email": "paciente2@test.com", "password": "paciente123"},
    {"email": "paciente3@test.com", "password": "paciente123"},
]

print("\n" + "="*80)
print("TEST DE LOGIN - API BACKEND")
print("="*80)

for cred in credenciales:
    print(f"\n{'='*60}")
    print(f"🧪 Probando: {cred['email']}")
    print(f"{'='*60}")
    
    # Probar con header X-Tenant
    headers = {
        "Content-Type": "application/json",
        "X-Tenant": "clinica-demo.localhost"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/token/",
        json=cred,
        headers=headers
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ LOGIN EXITOSO")
    else:
        print("❌ LOGIN FALLIDO")
        
        # Probar sin X-Tenant
        print("\n🔄 Probando sin X-Tenant header...")
        response2 = requests.post(
            f"{BASE_URL}/api/token/",
            json=cred,
            headers={"Content-Type": "application/json"}
        )
        print(f"📊 Status Code: {response2.status_code}")
        print(f"📄 Response: {json.dumps(response2.json(), indent=2)}")

print("\n" + "="*80)
