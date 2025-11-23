import requests
import json

# URL de Render
url = 'https://clinica-dental-backend.onrender.com/api/token/'

# Headers con tenant y User-Agent
headers = {
    'Host': 'clinicademo1.localhost',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Credenciales
data = {
    'email': 'paciente1@test.com',
    'password': 'password123'
}

print("🔄 Probando login en Render...")
print(f"URL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Body: {json.dumps(data, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=data, headers=headers, timeout=10)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📄 Response Body:")
    print(response.text)
    
    if response.status_code == 200:
        print("\n🎉 ¡LOGIN EXITOSO!")
        tokens = response.json()
        print(f"Access Token: {tokens.get('access')[:50]}...")
        print(f"Refresh Token: {tokens.get('refresh')[:50]}...")
    elif response.status_code == 401:
        print("\n❌ Credenciales incorrectas o usuario no existe")
    elif response.status_code == 403:
        print("\n❌ Cloudflare sigue bloqueando")
    else:
        print(f"\n⚠️ Error inesperado: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error en la petición: {e}")
