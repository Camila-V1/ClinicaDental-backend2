import requests
import json

# URL del backend EN RENDER
BASE_URL = "https://clinica-dental-backend.onrender.com"

print("\n" + "="*80)
print("🌐 VERIFICACIÓN DE USUARIOS EN RENDER")
print("="*80)
print(f"Backend: {BASE_URL}")

# Credenciales a probar
credenciales = [
    {"email": "paciente1@test.com", "password": "paciente123", "nombre": "María García"},
    {"email": "paciente2@test.com", "password": "paciente123", "nombre": "Carlos López"},
    {"email": "paciente3@test.com", "password": "paciente123", "nombre": "Laura Rodríguez"},
    {"email": "paciente4@test.com", "password": "paciente123", "nombre": "Pedro Martínez"},
    {"email": "paciente5@test.com", "password": "paciente123", "nombre": "Ana Torres"},
    {"email": "odontologo@clinica-demo.com", "password": "odontologo123", "nombre": "Dr. Carlos Rodríguez"},
    {"email": "admin@clinicademo1.com", "password": "admin123", "nombre": "Administrador"},
]

# Diferentes combinaciones de X-Tenant a probar
tenants_a_probar = [
    "clinica-demo.localhost",
    "clinicademo1.dentaabcxy.store",
    "clinica_demo",
    "clinicademo1",
]

print(f"\n🧪 Probando {len(credenciales)} usuarios con {len(tenants_a_probar)} configuraciones de tenant")

resultados_exitosos = []
resultados_fallidos = []

for tenant in tenants_a_probar:
    print(f"\n{'='*80}")
    print(f"🏥 Probando con X-Tenant: '{tenant}'")
    print(f"{'='*80}")
    
    for cred in credenciales:
        print(f"\n{'─'*60}")
        print(f"👤 Usuario: {cred['nombre']} ({cred['email']})")
        
        headers = {
            "Content-Type": "application/json",
            "X-Tenant": tenant
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/token/",
                json={"email": cred['email'], "password": cred['password']},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LOGIN EXITOSO")
                print(f"   Access token: {data['access'][:50]}...")
                print(f"   Refresh token: {data['refresh'][:50]}...")
                
                # Intentar obtener datos del usuario
                try:
                    user_response = requests.get(
                        f"{BASE_URL}/api/usuarios/me/",
                        headers={
                            "Authorization": f"Bearer {data['access']}",
                            "X-Tenant": tenant
                        },
                        timeout=10
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        print(f"   📊 Datos usuario: {user_data.get('nombre')} {user_data.get('apellido')}")
                        print(f"   🔑 Tipo: {user_data.get('tipo_usuario')}")
                        
                        resultados_exitosos.append({
                            'tenant': tenant,
                            'email': cred['email'],
                            'nombre': cred['nombre'],
                            'tipo': user_data.get('tipo_usuario')
                        })
                    else:
                        print(f"   ⚠️ No se pudo obtener datos del usuario: {user_response.status_code}")
                except Exception as e:
                    print(f"   ⚠️ Error obteniendo datos: {e}")
                    
            else:
                error_detail = response.json().get('detail', 'Error desconocido') if response.headers.get('content-type') == 'application/json' else response.text
                print(f"❌ LOGIN FALLIDO - Status: {response.status_code}")
                print(f"   Error: {error_detail}")
                
                resultados_fallidos.append({
                    'tenant': tenant,
                    'email': cred['email'],
                    'nombre': cred['nombre'],
                    'status': response.status_code,
                    'error': error_detail
                })
                
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT - El servidor no respondió en 10 segundos")
            resultados_fallidos.append({
                'tenant': tenant,
                'email': cred['email'],
                'nombre': cred['nombre'],
                'error': 'Timeout'
            })
        except Exception as e:
            print(f"💥 EXCEPCIÓN: {e}")
            resultados_fallidos.append({
                'tenant': tenant,
                'email': cred['email'],
                'nombre': cred['nombre'],
                'error': str(e)
            })

# Resumen final
print("\n" + "="*80)
print("📊 RESUMEN DE RESULTADOS")
print("="*80)

print(f"\n✅ LOGINS EXITOSOS: {len(resultados_exitosos)}")
if resultados_exitosos:
    print("\nConfiguración que funciona:")
    tenant_exitoso = None
    for resultado in resultados_exitosos:
        if tenant_exitoso != resultado['tenant']:
            tenant_exitoso = resultado['tenant']
            print(f"\n🏥 X-Tenant: '{tenant_exitoso}'")
        print(f"   ✅ {resultado['email']} ({resultado['tipo']})")

print(f"\n❌ LOGINS FALLIDOS: {len(resultados_fallidos)}")

print("\n" + "="*80)
print("💡 CONCLUSIÓN")
print("="*80)

if resultados_exitosos:
    tenant_correcto = resultados_exitosos[0]['tenant']
    print(f"\n✅ El X-Tenant correcto para tu app Flutter es:")
    print(f"\n   '{tenant_correcto}'")
    print(f"\n📝 Úsalo así en tu código:")
    print(f"""
    final headers = {{
      'Content-Type': 'application/json',
      'X-Tenant': '{tenant_correcto}',
    }};
    """)
else:
    print("\n⚠️ No se encontró ninguna configuración exitosa.")
    print("   Verifica que el backend esté funcionando correctamente.")

print("\n" + "="*80)
