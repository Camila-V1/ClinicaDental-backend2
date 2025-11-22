"""
Script para crear citas en los últimos 7 días en PRODUCCIÓN.
Esto generará datos visuales para el gráfico de tendencia.
"""

import requests
from datetime import datetime, timedelta

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

def obtener_pacientes(token):
    """Obtiene lista de pacientes."""
    url = f"{BASE_URL}/api/usuarios/pacientes/"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    pacientes = response.json()
    print(f"✅ {len(pacientes)} pacientes encontrados")
    return pacientes

def obtener_odontologos(token):
    """Obtiene lista de odontólogos."""
    url = f"{BASE_URL}/api/usuarios/odontologos/"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    odontologos = response.json()
    print(f"✅ {len(odontologos)} odontólogos encontrados")
    return odontologos

def crear_cita(token, fecha_hora, paciente_id, odontologo_id, estado):
    """Crea una cita sin plan de tratamiento."""
    url = f"{BASE_URL}/api/agenda/citas/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    data = {
        "fecha_hora": fecha_hora,
        "paciente": paciente_id,
        "odontologo": odontologo_id,
        "estado": estado,
        "motivo": "Consulta general - Datos de prueba",
        "notas": "Cita creada para visualización del dashboard"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text[:200]}")
        return None

def main():
    print("=" * 70)
    print("🚀 CREANDO CITAS PARA GRÁFICO DE TENDENCIA")
    print("=" * 70)
    
    # Obtener token y datos
    token = obtener_token()
    pacientes = obtener_pacientes(token)
    odontologos = obtener_odontologos(token)
    
    if not pacientes or not odontologos:
        print("❌ No hay pacientes u odontólogos")
        return
    
    paciente_id = pacientes[0]['id']
    odontologo_id = odontologos[0]['id']
    
    print(f"\n📅 Creando citas para últimos 7 días...")
    print(f"👤 Paciente ID: {paciente_id}")
    print(f"👨‍⚕️ Odontólogo ID: {odontologo_id}\n")
    
    # Crear citas para los últimos 7 días
    hoy = datetime.now()
    estados_distribucion = [
        'ATENDIDA', 'ATENDIDA', 'ATENDIDA',  # 3 atendidas
        'CANCELADA',                          # 1 cancelada
        'PENDIENTE', 'CONFIRMADA', 'PENDIENTE'  # 3 pendientes
    ]
    
    citas_creadas = 0
    for i in range(7):
        dia = hoy - timedelta(days=i)
        fecha_hora = dia.replace(hour=10 + (i % 8), minute=0, second=0).isoformat()
        estado = estados_distribucion[i % len(estados_distribucion)]
        
        print(f"📌 Día {i+1}: {dia.strftime('%d/%m')} - Estado: {estado}")
        cita = crear_cita(token, fecha_hora, paciente_id, odontologo_id, estado)
        
        if cita:
            print(f"   ✅ Cita #{cita['id']} creada")
            citas_creadas += 1
        else:
            print(f"   ⚠️ No se pudo crear cita")
    
    print(f"\n" + "=" * 70)
    print(f"✅ COMPLETADO: {citas_creadas} citas creadas")
    print("=" * 70)
    print(f"\n🎯 Refresca el dashboard:")
    print(f"   https://clinica-dental-frontend.vercel.app/reportes")
    print(f"\nVerás datos en todos los días del gráfico 📊")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
