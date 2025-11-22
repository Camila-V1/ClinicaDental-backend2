"""
Script para poblar la bitácora con registros de ejemplo en PRODUCCIÓN.
"""

import requests
from datetime import datetime, timedelta
import random

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

def crear_bitacora(token, accion, descripcion, detalles=None):
    """Crea un registro de bitácora."""
    url = f"{BASE_URL}/api/reportes/bitacora/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "accion": accion,
        "descripcion": descripcion,
    }
    
    if detalles:
        data["detalles"] = detalles
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text[:300]}")
        return None

def main():
    print("=" * 70)
    print("🚀 POBLANDO BITÁCORA CON REGISTROS DE EJEMPLO")
    print("=" * 70)
    
    token = obtener_token()
    
    # Registros de ejemplo
    registros = [
        {
            "accion": "LOGIN",
            "descripcion": "Inicio de sesión exitoso - Administrador Principal",
            "detalles": {"ip": "192.168.1.100", "navegador": "Chrome 120"}
        },
        {
            "accion": "CREAR",
            "descripcion": "Creó nueva cita para paciente María García - 22/11/2025 10:00",
            "detalles": {"paciente_id": 403, "odontologo_id": 402, "tipo": "Consulta"}
        },
        {
            "accion": "EDITAR",
            "descripcion": "Actualizó estado de cita #658 a ATENDIDA",
            "detalles": {"cita_id": 658, "estado_anterior": "PENDIENTE", "estado_nuevo": "ATENDIDA"}
        },
        {
            "accion": "CREAR",
            "descripcion": "Registró nuevo paciente: Ana Torres (paciente5@test.com)",
            "detalles": {"paciente_id": 407, "email": "paciente5@test.com"}
        },
        {
            "accion": "VER",
            "descripcion": "Consultó historial clínico del paciente María García",
            "detalles": {"paciente_id": 403, "modulo": "Historial Clínico"}
        },
        {
            "accion": "EDITAR",
            "descripcion": "Actualizó plan de tratamiento #38 - Cambió estado a EN_PROGRESO",
            "detalles": {"plan_id": 38, "paciente": "María García", "progreso": "25%"}
        },
        {
            "accion": "CREAR",
            "descripcion": "Generó factura #183 para paciente Laura Rodríguez - $225.00",
            "detalles": {"factura_id": 183, "monto": "225.00", "paciente_id": 405}
        },
        {
            "accion": "EXPORTAR",
            "descripcion": "Exportó reporte financiero del mes 11/2025 en formato PDF",
            "detalles": {"tipo": "Reporte Financiero", "periodo": "2025-11", "formato": "PDF"}
        },
        {
            "accion": "EDITAR",
            "descripcion": "Actualizó stock del insumo AML-001 (Amalgama Dental) - Nuevo stock: 48",
            "detalles": {"insumo_id": 604, "stock_anterior": 50, "stock_nuevo": 48}
        },
        {
            "accion": "VER",
            "descripcion": "Visualizó dashboard de reportes - Ocupación de odontólogos",
            "detalles": {"modulo": "Dashboard Admin", "seccion": "Reportes"}
        },
        {
            "accion": "CREAR",
            "descripcion": "Agendó 7 nuevas citas para semana del 16-22 nov 2025",
            "detalles": {"cantidad": 7, "fecha_inicio": "2025-11-16", "fecha_fin": "2025-11-22"}
        },
        {
            "accion": "EDITAR",
            "descripcion": "Canceló cita #656 - Motivo: Paciente solicitó reprogramación",
            "detalles": {"cita_id": 656, "estado": "CANCELADA", "motivo": "Reprogramación"}
        },
    ]
    
    print(f"\n📝 Creando {len(registros)} registros de bitácora...\n")
    
    creados = 0
    for i, registro in enumerate(registros, 1):
        print(f"{i}. {registro['accion']}: {registro['descripcion'][:60]}...")
        
        resultado = crear_bitacora(
            token,
            registro['accion'],
            registro['descripcion'],
            registro.get('detalles')
        )
        
        if resultado:
            print(f"   ✅ Creado ID: {resultado.get('id')}")
            creados += 1
        else:
            print(f"   ⚠️ No se pudo crear")
    
    print(f"\n" + "=" * 70)
    print(f"✅ COMPLETADO: {creados} de {len(registros)} registros creados")
    print("=" * 70)
    print(f"\n🎯 Refresca el dashboard:")
    print(f"   https://clinica-dental-frontend.vercel.app/reportes")
    print(f"\nVerás actividad reciente en la sección de bitácora 📋")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
