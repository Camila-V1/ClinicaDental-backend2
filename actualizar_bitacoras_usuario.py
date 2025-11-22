"""
Script para actualizar registros de bitácora con usuario admin.
"""

import requests

# Configuración
BASE_URL = "https://clinica-dental-backend.onrender.com"
TENANT_ID = "clinica_demo"
ADMIN_EMAIL = "admin@clinica-demo.com"
ADMIN_PASSWORD = "admin123"

def obtener_token():
    """Obtiene el token JWT del admin."""
    print("🔐 Obteniendo token...")
    
    url = f"{BASE_URL}/api/token/"
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    token = response.json().get('access')
    print("✅ Token obtenido")
    return token

def obtener_bitacoras(token):
    """Obtiene todas las bitácoras."""
    url = f"{BASE_URL}/api/reportes/bitacora/"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def actualizar_bitacora(token, bitacora_id, usuario_id):
    """Actualiza una bitácora con usuario admin."""
    url = f"{BASE_URL}/api/reportes/bitacora/{bitacora_id}/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "usuario": usuario_id,
        "accion": None,  # Mantener valores existentes
        "descripcion": None
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def obtener_admin_id(token):
    """Obtiene el ID del usuario admin."""
    url = f"{BASE_URL}/api/usuarios/me/"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['id']

def main():
    print("=" * 70)
    print("🔄 ACTUALIZANDO BITÁCORAS CON USUARIO ADMIN")
    print("=" * 70)
    
    token = obtener_token()
    admin_id = obtener_admin_id(token)
    print(f"👤 Admin ID: {admin_id}")
    
    bitacoras = obtener_bitacoras(token)
    print(f"\n📋 {len(bitacoras)} registros encontrados\n")
    
    actualizados = 0
    for bitacora in bitacoras:
        if bitacora['usuario']['id'] is None:
            print(f"Actualizando bitácora #{bitacora['id']} - {bitacora['descripcion'][:50]}...")
            if actualizar_bitacora(token, bitacora['id'], admin_id):
                print(f"   ✅ Actualizado")
                actualizados += 1
            else:
                print(f"   ⚠️ No se pudo actualizar")
        else:
            print(f"✓ Bitácora #{bitacora['id']} ya tiene usuario")
    
    print(f"\n" + "=" * 70)
    print(f"✅ COMPLETADO: {actualizados} registros actualizados")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
