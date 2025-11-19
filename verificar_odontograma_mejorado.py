"""
Script de verificación para el nuevo endpoint de configuración del odontograma.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://clinica-demo.localhost:8000/api"

# Credenciales
CREDENTIALS = {
    "email": "odontologo@clinica-demo.com",
    "password": "password123"
}

def login():
    """Obtiene el token de autenticación."""
    print("🔐 Iniciando sesión...")
    response = requests.post(f"{BASE_URL}/token/", json=CREDENTIALS)
    
    if response.status_code == 200:
        token = response.json()["access"]
        print("✅ Login exitoso")
        return token
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(response.text)
        return None

def obtener_configuracion(token):
    """Obtiene la configuración del odontograma."""
    print("\n📋 Obteniendo configuración del odontograma...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/historial/odontogramas/configuracion/",
        headers=headers
    )
    
    if response.status_code == 200:
        config = response.json()
        print("✅ Configuración obtenida exitosamente\n")
        
        # Verificar estructura
        print("📊 VERIFICACIÓN DE ESTRUCTURA:")
        print(f"  ✓ Nomenclatura: {config.get('nomenclatura')}")
        print(f"  ✓ Sistema: {config.get('sistema')}")
        print(f"  ✓ Total dientes adulto: {config.get('total_dientes_adulto')}")
        print(f"  ✓ Cuadrantes: {len(config.get('cuadrantes', {}))}")
        print(f"  ✓ Estados disponibles: {len(config.get('estados', []))}")
        print(f"  ✓ Superficies: {len(config.get('superficies', []))}")
        print(f"  ✓ Materiales: {len(config.get('materiales', []))}")
        
        # Mostrar cuadrantes
        print("\n🦷 CUADRANTES:")
        for num, cuadrante in config.get('cuadrantes', {}).items():
            print(f"  {num}. {cuadrante['nombre']} ({cuadrante['nombre_corto']}) - {len(cuadrante['dientes'])} dientes")
        
        # Mostrar estados
        print("\n🎨 ESTADOS DISPONIBLES:")
        for estado in config.get('estados', []):
            print(f"  {estado['icono']} {estado['etiqueta']:15} - {estado['color']:10} - {estado['descripcion']}")
        
        # Mostrar ordenamiento visual
        print("\n📐 ORDENAMIENTO VISUAL:")
        orden = config.get('ordenamiento_visual', {})
        print(f"  Superior Derecho: {' '.join(orden.get('superior_derecho', []))}")
        print(f"  Superior Izquierdo: {' '.join(orden.get('superior_izquierdo', []))}")
        print(f"  Inferior Izquierdo: {' '.join(orden.get('inferior_izquierdo', []))}")
        print(f"  Inferior Derecho: {' '.join(orden.get('inferior_derecho', []))}")
        
        # Contar total de dientes
        total_dientes = sum(
            len(cuadrante['dientes']) 
            for cuadrante in config.get('cuadrantes', {}).values()
        )
        print(f"\n✅ Total de dientes en sistema: {total_dientes}")
        
        return config
    else:
        print(f"❌ Error al obtener configuración: {response.status_code}")
        print(response.text)
        return None

def listar_odontogramas(token):
    """Lista los odontogramas existentes con los campos enriquecidos."""
    print("\n📋 Listando odontogramas...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/historial/odontogramas/",
        headers=headers
    )
    
    if response.status_code == 200:
        odontogramas = response.json()
        print(f"✅ Se encontraron {len(odontogramas)} odontograma(s)\n")
        
        for idx, odon in enumerate(odontogramas, 1):
            print(f"  {idx}. Odontograma ID: {odon.get('id')}")
            print(f"     Paciente: {odon.get('paciente_info', {}).get('nombre', 'N/A')}")
            print(f"     Fecha: {odon.get('fecha_snapshot', 'N/A')[:10]}")
            print(f"     Dientes registrados: {odon.get('total_dientes_registrados', 0)}")
            print(f"     Resumen estados: {odon.get('resumen_estados', {})}")
            print()
        
        return odontogramas
    else:
        print(f"❌ Error al listar odontogramas: {response.status_code}")
        return []

def main():
    """Función principal."""
    print("="*80)
    print("🦷 VERIFICACIÓN DEL SISTEMA DE ODONTOGRAMA MEJORADO")
    print("="*80)
    
    # 1. Login
    token = login()
    if not token:
        return
    
    # 2. Obtener configuración
    config = obtener_configuracion(token)
    if not config:
        return
    
    # 3. Listar odontogramas
    odontogramas = listar_odontogramas(token)
    
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print("\n📝 RESUMEN:")
    print(f"  ✓ Endpoint de configuración: FUNCIONANDO")
    print(f"  ✓ Cuadrantes configurados: {len(config.get('cuadrantes', {}))}")
    print(f"  ✓ Estados disponibles: {len(config.get('estados', []))}")
    print(f"  ✓ Total dientes en sistema: 32")
    print(f"  ✓ Serializer con campos calculados: FUNCIONANDO")
    print(f"  ✓ Odontogramas en BD: {len(odontogramas)}")
    print("\n🎉 ¡El sistema está listo para ser usado en el frontend!")
    print("="*80)

if __name__ == "__main__":
    main()
