"""
Script para poblar datos en producción usando peticiones HTTP a la API
Esto permite crear datos sin acceder directamente a la base de datos
"""
import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "https://clinica-dental-backend.onrender.com"
TENANT_ID = "clinica_demo"

# Credenciales (usar María García directamente)
USER_EMAIL = "maria.garcia@email.com"
USER_PASSWORD = "password123"

# Headers base
headers = {
    "Content-Type": "application/json",
    "X-Tenant-ID": TENANT_ID,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("="*80)
print("🦷 POBLANDO DATOS EN PRODUCCIÓN VIA API")
print("="*80)

# 1. Login como admin
print("\n🔐 Iniciando sesión como usuario...")
response = requests.post(
    f"{BASE_URL}/api/token/",
    headers=headers,
    json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    }
)

if response.status_code != 200:
    print(f"❌ Error en login: {response.status_code}")
    print(response.text)
    exit(1)

tokens = response.json()
access_token = tokens['access']
print(f"✅ Token obtenido: {access_token[:20]}...")

# Agregar token a headers
auth_headers = headers.copy()
auth_headers["Authorization"] = f"Bearer {access_token}"

# 2. Obtener datos del usuario actual
print("\n👤 Obteniendo datos del usuario actual...")
response = requests.get(
    f"{BASE_URL}/api/usuarios/me/",
    headers=auth_headers
)

if response.status_code != 200:
    print(f"❌ Error obteniendo usuario: {response.status_code}")
    exit(1)

usuario_actual = response.json()
maria_id = usuario_actual['id']
print(f"✅ Usuario: {usuario_actual.get('email')} - ID: {maria_id}")

# 3. Obtener ID del perfil paciente
print("\n📋 Obteniendo perfil de paciente...")
# El perfil paciente ID suele ser el mismo que el usuario ID o está en perfil_paciente_id
maria_perfil_id = usuario_actual.get('perfil_paciente_id') or maria_id
print(f"✅ Perfil paciente ID: {maria_perfil_id}")

# 4. Obtener un odontólogo
print("\n👨‍⚕️ Buscando odontólogo...")
# Usar ID fijo del odontólogo que sabemos existe (del script anterior)
odontologo_id = 577  # Dr. Juan Pérez según los logs
print(f"✅ Usando Odontólogo ID: {odontologo_id}")

# 5. Crear Citas
print("\n📅 CREANDO CITAS...")
ahora = datetime.now()
citas_data = [
    {
        "paciente": maria_perfil_id,
        "odontologo": odontologo_id,
        "fecha_hora": (ahora + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"),
        "motivo_tipo": "CONSULTA",
        "motivo": "Limpieza dental y revisión general",
        "estado": "CONFIRMADA",
        "observaciones": "Primera cita de control"
    },
    {
        "paciente": maria_perfil_id,
        "odontologo": odontologo_id,
        "fecha_hora": (ahora - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
        "motivo_tipo": "URGENCIA",
        "motivo": "Control de tratamiento de conducto",
        "estado": "ATENDIDA",
        "observaciones": "Cita completada exitosamente"
    },
    {
        "paciente": maria_perfil_id,
        "odontologo": odontologo_id,
        "fecha_hora": (ahora + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S"),
        "motivo_tipo": "TRATAMIENTO",
        "motivo": "Seguimiento de endodoncia",
        "estado": "PENDIENTE",
        "observaciones": "Cita de seguimiento"
    }
]

citas_creadas = []
for i, cita_data in enumerate(citas_data, 1):
    response = requests.post(
        f"{BASE_URL}/api/agenda/citas/",
        headers=auth_headers,
        json=cita_data
    )
    
    if response.status_code in [200, 201]:
        cita = response.json()
        citas_creadas.append(cita)
        print(f"  ✅ Cita {i}: {cita.get('fecha_hora')} - {cita.get('estado')}")
    else:
        print(f"  ❌ Error creando cita {i}: {response.status_code}")
        print(f"     {response.text[:200]}")

print(f"\n✅ Citas creadas: {len(citas_creadas)}")

# 6. Crear Plan de Tratamiento
print("\n💊 CREANDO PLAN DE TRATAMIENTO...")

# Primero obtener servicios disponibles
response = requests.get(
    f"{BASE_URL}/api/inventario/servicios/",
    headers=auth_headers
)

servicios = []
if response.status_code == 200:
    servicios = response.json()
    print(f"  📋 Servicios disponibles: {len(servicios)}")

if servicios:
    # Crear plan
    plan_data = {
        "paciente": maria_perfil_id,
        "odontologo": odontologo_id,
        "titulo": "Tratamiento Integral",
        "estado": "EN_PROGRESO",
        "prioridad": "MEDIA",
        "observaciones": "Plan de tratamiento completo"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tratamientos/planes/",
        headers=auth_headers,
        json=plan_data
    )
    
    if response.status_code in [200, 201]:
        plan = response.json()
        plan_id = plan['id']
        print(f"  ✅ Plan creado - ID: {plan_id}")
        
        # Agregar items al plan (si el endpoint lo permite)
        for servicio in servicios[:3]:  # Primeros 3 servicios
            item_data = {
                "plan": plan_id,
                "servicio": servicio['id'],
                "orden": servicios.index(servicio) + 1,
                "estado": "PENDIENTE"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/tratamientos/items/",
                headers=auth_headers,
                json=item_data
            )
            
            if response.status_code in [200, 201]:
                print(f"    ✅ Item: {servicio.get('nombre')}")
    else:
        print(f"  ❌ Error creando plan: {response.status_code}")
        print(f"     {response.text[:200]}")
else:
    print("  ⚠️ No hay servicios disponibles, saltando creación de plan")

# 7. Crear Facturas
print("\n💰 CREANDO FACTURAS...")
facturas_data = [
    {
        "paciente": maria_perfil_id,
        "monto_total": "280.00",
        "monto_pagado": "280.00",
        "estado": "PAGADA",
        "nit_ci": "12345678",
        "razon_social": "María García López"
    },
    {
        "paciente": maria_perfil_id,
        "monto_total": "450.00",
        "monto_pagado": "200.00",
        "estado": "PENDIENTE",
        "nit_ci": "12345678",
        "razon_social": "María García López"
    }
]

for i, factura_data in enumerate(facturas_data, 1):
    response = requests.post(
        f"{BASE_URL}/api/facturacion/facturas/",
        headers=auth_headers,
        json=factura_data
    )
    
    if response.status_code in [200, 201]:
        factura = response.json()
        print(f"  ✅ Factura {i}: ${factura.get('monto_total')} - {factura.get('estado')}")
    else:
        print(f"  ❌ Error creando factura {i}: {response.status_code}")
        print(f"     {response.text[:200]}")

# 8. Verificar datos creados
print("\n" + "="*80)
print("✅ VERIFICANDO DATOS CREADOS")
print("="*80)

response = requests.get(
    f"{BASE_URL}/api/agenda/citas/",
    headers=auth_headers,
    params={"paciente": maria_perfil_id}
)
print(f"📅 Citas: {len(response.json()) if response.status_code == 200 else 'Error'}")

response = requests.get(
    f"{BASE_URL}/api/tratamientos/planes/",
    headers=auth_headers
)
if response.status_code == 200:
    planes = [p for p in response.json() if p.get('paciente_id') == maria_perfil_id]
    print(f"💊 Planes: {len(planes)}")

response = requests.get(
    f"{BASE_URL}/api/facturacion/facturas/",
    headers=auth_headers
)
if response.status_code == 200:
    facturas = [f for f in response.json() if f.get('paciente') == maria_perfil_id]
    print(f"💰 Facturas: {len(facturas)}")

print("\n" + "="*80)
print("🎯 DATOS POBLADOS EXITOSAMENTE")
print("="*80)
print(f"\n👤 Usuario: maria.garcia@email.com")
print(f"🔐 Password: password123")
print(f"🏥 Tenant: {TENANT_ID}")
print("\n✨ ¡Listo para probar en Flutter y Web!")
