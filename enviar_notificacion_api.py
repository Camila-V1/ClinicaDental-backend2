import requests
import json

BASE_URL = "https://clinica-dental-backend.onrender.com"

print("\n" + "="*80)
print("📱 ENVIAR NOTIFICACIÓN DE PRUEBA VÍA API")
print("="*80)

# 1. Login
print("\n🔐 Paso 1: Login...")
login_response = requests.post(
    f"{BASE_URL}/api/token/",
    json={
        "email": "paciente1@test.com",
        "password": "paciente123"
    },
    headers={
        "Content-Type": "application/json",
        "X-Tenant": "clinica-demo.localhost"
    }
)

if login_response.status_code != 200:
    print(f"❌ Error en login: {login_response.status_code}")
    exit()

tokens = login_response.json()
access_token = tokens['access']
print(f"✅ Login exitoso")

# 2. Obtener datos del usuario
print("\n👤 Paso 2: Obteniendo datos del usuario...")
user_response = requests.get(
    f"{BASE_URL}/api/usuarios/me/",
    headers={
        "Authorization": f"Bearer {access_token}",
        "X-Tenant": "clinica-demo.localhost"
    }
)

if user_response.status_code != 200:
    print(f"❌ Error obteniendo usuario: {user_response.status_code}")
    exit()

user_data = user_response.json()
print(f"✅ Usuario: {user_data['nombre']} {user_data['apellido']}")
print(f"📧 Email: {user_data['email']}")

# 3. Registrar FCM token (el que la app ya registró)
fcm_token = "fQGD1g-FTde_3JU4QIRGyv:APA91bFvUoRyORaB2ThzxjfExLnEqsYmBInKoT_c7YMZa13ckq-2_pHC5XvF26uZteBSyzeyoIoFQSUZyXaYqH4glzhl7akW4mz0ta2BLxGvLDSXwrqLKcA"

print(f"\n📱 Paso 3: FCM Token (de la app)...")
print(f"Token: {fcm_token[:50]}...")

# 4. Enviar notificación de prueba
print("\n📤 Paso 4: Enviando notificación de prueba...")

notif_data = {
    "fcm_token": fcm_token,
    "titulo": "🦷 Prueba de Notificación",
    "mensaje": "¡Hola María! Esta es una notificación de prueba desde tu clínica dental. El sistema de notificaciones está funcionando correctamente. 🎉",
    "data": {
        "tipo": "PRUEBA",
        "usuario_id": str(user_data['id']),
        "clinica": "Clínica Demo"
    }
}

# Intentar enviar notificación usando diferentes endpoints
print("\n🔍 Buscando endpoint de notificaciones...")

# Opción 1: Endpoint de valoraciones
try:
    notif_response = requests.post(
        f"{BASE_URL}/api/valoraciones/enviar-notificacion-prueba/",
        json=notif_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Tenant": "clinica-demo.localhost",
            "Content-Type": "application/json"
        }
    )
    
    print(f"📊 Status: {notif_response.status_code}")
    print(f"📄 Response: {notif_response.text[:200]}")
    
    if notif_response.status_code == 200:
        print("✅ NOTIFICACIÓN ENVIADA EXITOSAMENTE")
    else:
        print(f"❌ Error: {notif_response.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*80)
print("🎯 Verifica tu celular - Deberías recibir la notificación")
print("="*80)
