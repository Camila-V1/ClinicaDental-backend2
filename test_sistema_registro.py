"""
Script de prueba para el sistema de registro multi-tenant.
Prueba los endpoints públicos de registro.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/tenants"

def separador():
    print("\n" + "=" * 80 + "\n")

def test_info_registro():
    """Probar endpoint de información de registro."""
    print("📋 TEST 1: Información del Proceso de Registro")
    separador()
    
    url = f"{BASE_URL}/registro/info/"
    response = requests.get(url)
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mensaje: {data.get('mensaje')}")
        print(f"\n📝 Pasos del proceso:")
        for paso in data.get('pasos', []):
            print(f"   {paso}")
        
        print(f"\n💰 Planes disponibles:")
        for plan in data.get('planes_disponibles', []):
            print(f"   - {plan['nombre']}: ${plan['precio']} ({plan['duracion_dias']} días)")
    else:
        print(f"❌ Error: {response.text}")


def test_listar_planes():
    """Probar endpoint de listado de planes."""
    print("💎 TEST 2: Listar Planes de Suscripción")
    separador()
    
    url = f"{BASE_URL}/planes/"
    response = requests.get(url)
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        planes = response.json()
        print(f"✅ Total de planes: {len(planes)}")
        
        for plan in planes:
            print(f"\n🎯 {plan['nombre']}")
            print(f"   Tipo: {plan['tipo_display']}")
            print(f"   Precio: ${plan['precio']}")
            print(f"   Duración: {plan['duracion_dias']} días")
            print(f"   Max Usuarios: {plan['max_usuarios']}")
            print(f"   Max Pacientes: {plan['max_pacientes']}")
    else:
        print(f"❌ Error: {response.text}")


def test_crear_solicitud():
    """Probar endpoint de creación de solicitud."""
    print("📝 TEST 3: Crear Solicitud de Registro")
    separador()
    
    url = f"{BASE_URL}/solicitudes/"
    
    # Primero obtener un plan
    planes_response = requests.get(f"{BASE_URL}/planes/")
    if planes_response.status_code != 200:
        print("❌ No se pudieron obtener los planes")
        return
    
    planes = planes_response.json()
    plan_prueba = next((p for p in planes if p['tipo'] == 'PRUEBA'), planes[0])
    
    # Datos de la solicitud
    solicitud_data = {
        "nombre_clinica": "Clínica Dental Ejemplo",
        "dominio_deseado": "clinica-ejemplo",
        "nombre_contacto": "Dr. Juan Pérez",
        "email": "juan.perez@example.com",
        "telefono": "+57 300 1234567",
        "cargo": "Director Médico",
        "direccion": "Calle 100 #15-20",
        "ciudad": "Bogotá",
        "pais": "Colombia",
        "plan_solicitado": plan_prueba['id']
    }
    
    print(f"URL: {url}")
    print(f"\n📤 Datos de la solicitud:")
    print(json.dumps(solicitud_data, indent=2, ensure_ascii=False))
    
    response = requests.post(
        url,
        json=solicitud_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ {data.get('message')}")
        
        solicitud = data.get('solicitud', {})
        print(f"\n📋 Solicitud creada:")
        print(f"   ID: {solicitud.get('id')}")
        print(f"   Clínica: {solicitud.get('nombre_clinica')}")
        print(f"   Dominio: {solicitud.get('dominio_deseado')}")
        print(f"   Estado: {solicitud.get('estado')}")
        print(f"   Plan: {solicitud.get('plan_info', {}).get('nombre')}")
        
        return solicitud.get('id')
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_validacion_dominio_duplicado():
    """Probar validación de dominio duplicado."""
    print("🔍 TEST 4: Validación de Dominio Duplicado")
    separador()
    
    url = f"{BASE_URL}/solicitudes/"
    
    planes_response = requests.get(f"{BASE_URL}/planes/")
    planes = planes_response.json()
    plan = planes[0]
    
    # Intentar crear con el mismo dominio
    solicitud_data = {
        "nombre_clinica": "Otra Clínica",
        "dominio_deseado": "clinica-ejemplo",  # Mismo dominio que antes
        "nombre_contacto": "Maria García",
        "email": "maria@example.com",
        "telefono": "+57 300 9876543",
        "cargo": "Gerente",
        "ciudad": "Medellín",
        "pais": "Colombia",
        "plan_solicitado": plan['id']
    }
    
    print(f"URL: {url}")
    print(f"Intentando crear con dominio duplicado: {solicitud_data['dominio_deseado']}")
    
    response = requests.post(
        url,
        json=solicitud_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Validación funcionando correctamente")
        print(f"Error esperado: {response.json()}")
    else:
        print(f"⚠️  Respuesta inesperada: {response.text}")


def test_validacion_email_duplicado():
    """Probar validación de email duplicado."""
    print("🔍 TEST 5: Validación de Email Duplicado")
    separador()
    
    url = f"{BASE_URL}/solicitudes/"
    
    planes_response = requests.get(f"{BASE_URL}/planes/")
    planes = planes_response.json()
    plan = planes[0]
    
    # Intentar crear con el mismo email
    solicitud_data = {
        "nombre_clinica": "Clínica Nueva",
        "dominio_deseado": "clinica-nueva-test",
        "nombre_contacto": "Juan Pérez",
        "email": "juan.perez@example.com",  # Mismo email que antes
        "telefono": "+57 300 1111111",
        "cargo": "Director",
        "ciudad": "Cali",
        "pais": "Colombia",
        "plan_solicitado": plan['id']
    }
    
    print(f"URL: {url}")
    print(f"Intentando crear con email duplicado: {solicitud_data['email']}")
    
    response = requests.post(
        url,
        json=solicitud_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Validación funcionando correctamente")
        print(f"Error esperado: {response.json()}")
    else:
        print(f"⚠️  Respuesta inesperada: {response.text}")


def test_validacion_dominio_invalido():
    """Probar validación de formato de dominio."""
    print("🔍 TEST 6: Validación de Formato de Dominio")
    separador()
    
    url = f"{BASE_URL}/solicitudes/"
    
    planes_response = requests.get(f"{BASE_URL}/planes/")
    planes = planes_response.json()
    plan = planes[0]
    
    dominios_invalidos = [
        "-dominio-invalido",  # Empieza con guion
        "dominio-invalido-",  # Termina con guion
        "dominio@invalido",   # Carácter inválido
        "Dominio-Invalido",   # Mayúsculas
    ]
    
    for dominio in dominios_invalidos:
        solicitud_data = {
            "nombre_clinica": "Test Clínica",
            "dominio_deseado": dominio,
            "nombre_contacto": "Test",
            "email": f"test{dominio}@example.com",
            "telefono": "123456789",
            "cargo": "Test",
            "ciudad": "Test",
            "pais": "Test",
            "plan_solicitado": plan['id']
        }
        
        print(f"\n🧪 Probando dominio: '{dominio}'")
        
        response = requests.post(
            url,
            json=solicitud_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print(f"   ✅ Rechazado correctamente")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")


def main():
    """Ejecutar todas las pruebas."""
    print("\n" + "🚀 INICIANDO PRUEBAS DEL SISTEMA DE REGISTRO MULTI-TENANT " + "\n")
    
    try:
        # Prueba 1: Info del registro
        test_info_registro()
        
        # Prueba 2: Listar planes
        test_listar_planes()
        
        # Prueba 3: Crear solicitud válida
        solicitud_id = test_crear_solicitud()
        
        # Prueba 4: Validación dominio duplicado
        if solicitud_id:
            test_validacion_dominio_duplicado()
        
        # Prueba 5: Validación email duplicado
        if solicitud_id:
            test_validacion_email_duplicado()
        
        # Prueba 6: Validación formato de dominio
        test_validacion_dominio_invalido()
        
        separador()
        print("✅ PRUEBAS COMPLETADAS")
        print("\n📝 Próximos pasos:")
        print("   1. Ir al panel de admin: http://localhost:8000/admin/")
        print("   2. Ver 'Solicitudes de Registro'")
        print("   3. Aprobar la solicitud creada")
        print("   4. Verificar que se creó la clínica en 'Clínicas'")
        separador()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté corriendo: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
