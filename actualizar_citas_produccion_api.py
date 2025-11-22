"""
Script para actualizar estados de citas en PRODUCCIÓN usando la API REST.

Este script se conecta a Render (producción) usando el token de autenticación
y actualiza estados de citas para generar datos visuales en el dashboard.

Ejecución:
    python actualizar_citas_produccion_api.py
"""

import requests
import json
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ============================================================================

BASE_URL = "https://clinica-dental-backend.onrender.com"
TENANT_ID = "clinica_demo"

# Token de autenticación del admin (obtener desde credenciales)
# Debes hacer login primero para obtener el token
ADMIN_EMAIL = "admin@clinica-demo.com"
ADMIN_PASSWORD = "admin123"

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_token():
    """Obtiene el token JWT del admin haciendo login."""
    print("🔐 Obteniendo token de autenticación...")
    
    url = f"{BASE_URL}/api/token/"
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        token = result.get('access')
        
        if token:
            print("✅ Token obtenido exitosamente")
            return token
        else:
            print("❌ Error: No se recibió token en la respuesta")
            print(f"Respuesta: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Respuesta del servidor: {e.response.text}")
        return None

def obtener_citas(token):
    """Obtiene todas las citas del sistema."""
    print("\n📋 Obteniendo lista de citas...")
    
    url = f"{BASE_URL}/api/agenda/citas/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        citas = response.json()
        print(f"✅ {len(citas)} citas encontradas")
        return citas
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener citas: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Respuesta del servidor: {e.response.text}")
        return []

def actualizar_estado_cita(token, cita_id, nuevo_estado):
    """Actualiza el estado de una cita específica."""
    url = f"{BASE_URL}/api/agenda/citas/{cita_id}/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "estado": nuevo_estado
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers)
        response.raise_for_status()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error al actualizar cita {cita_id}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text}")
        return False

def actualizar_estados_distribuidos(token, citas):
    """
    Actualiza estados de citas con distribución:
    - 40% ATENDIDA (era COMPLETADA)
    - 20% CANCELADA
    - 40% sin cambiar (PENDIENTE/CONFIRMADA)
    """
    print("\n" + "=" * 70)
    print("🔄 ACTUALIZANDO ESTADOS DE CITAS EN PRODUCCIÓN")
    print("=" * 70)
    
    # Filtrar solo citas PENDIENTE o CONFIRMADA
    citas_pendientes = [
        c for c in citas 
        if c.get('estado') in ['PENDIENTE', 'CONFIRMADA']
    ]
    
    total = len(citas_pendientes)
    if total == 0:
        print("⚠️ No hay citas pendientes o confirmadas para actualizar")
        return
    
    # Calcular distribución
    num_atendidas = int(total * 0.4)
    num_canceladas = int(total * 0.2)
    
    print(f"\n📊 Distribución objetivo:")
    print(f"   - Total citas pendientes/confirmadas: {total}")
    print(f"   - Actualizar a ATENDIDA: {num_atendidas} (40%)")
    print(f"   - Actualizar a CANCELADA: {num_canceladas} (20%)")
    print(f"   - Mantener sin cambios: {total - num_atendidas - num_canceladas} (40%)")
    
    # Estados antes
    print(f"\n📋 Estados ANTES de actualizar:")
    estados_antes = {}
    for cita in citas:
        estado = cita.get('estado', 'DESCONOCIDO')
        estados_antes[estado] = estados_antes.get(estado, 0) + 1
    
    for estado, count in estados_antes.items():
        print(f"   {estado}: {count}")
    
    # Actualizar a ATENDIDA
    print(f"\n✅ Actualizando {num_atendidas} citas a ATENDIDA...")
    count_atendidas = 0
    for i, cita in enumerate(citas_pendientes[:num_atendidas]):
        if actualizar_estado_cita(token, cita['id'], 'ATENDIDA'):
            fecha = cita.get('fecha_hora', 'N/A')
            print(f"   ✅ Cita #{cita['id']} → ATENDIDA (Fecha: {fecha[:16]})")
            count_atendidas += 1
    
    # Actualizar a CANCELADA
    print(f"\n❌ Actualizando {num_canceladas} citas a CANCELADA...")
    count_canceladas = 0
    for cita in citas_pendientes[num_atendidas:num_atendidas + num_canceladas]:
        if actualizar_estado_cita(token, cita['id'], 'CANCELADA'):
            fecha = cita.get('fecha_hora', 'N/A')
            print(f"   ❌ Cita #{cita['id']} → CANCELADA (Fecha: {fecha[:16]})")
            count_canceladas += 1
    
    print(f"\n" + "=" * 70)
    print(f"✅ ACTUALIZACIÓN COMPLETADA")
    print(f"=" * 70)
    print(f"📈 Resumen:")
    print(f"   ✅ Citas actualizadas a ATENDIDA: {count_atendidas}")
    print(f"   ❌ Citas actualizadas a CANCELADA: {count_canceladas}")
    print(f"\n🎯 Ahora refresca el dashboard en:")
    print(f"   https://clinica-dental-frontend.vercel.app/reportes")
    print(f"\n   Verás:")
    print(f"   - 🟢 Línea verde de citas atendidas")
    print(f"   - 🔴 Línea roja de citas canceladas")
    print(f"   - 📊 Ocupación de odontólogos > 0%")
    print("=" * 70)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("🚀 SCRIPT DE ACTUALIZACIÓN DE CITAS EN PRODUCCIÓN")
    print("=" * 70)
    print(f"🌐 Backend: {BASE_URL}")
    print(f"🏥 Tenant: {TENANT_ID}")
    print(f"👤 Admin: {ADMIN_EMAIL}")
    print("=" * 70)
    
    # Paso 1: Obtener token
    token = obtener_token()
    if not token:
        print("\n❌ No se pudo obtener el token. Verifica las credenciales.")
        return
    
    # Paso 2: Obtener citas
    citas = obtener_citas(token)
    if not citas:
        print("\n⚠️ No se encontraron citas o hubo un error.")
        return
    
    # Paso 3: Actualizar estados
    actualizar_estados_distribuidos(token, citas)
    
    print("\n✅ Proceso completado exitosamente")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
