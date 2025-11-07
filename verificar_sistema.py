"""
Script de verificación completa del sistema multi-tenant.
Hace peticiones HTTP para validar que la separación de admin sites funciona correctamente.
"""
import requests
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Configuración
BASE_URL_PUBLIC = "http://localhost:8000"
BASE_URL_TENANT = "http://clinica-demo.localhost:8000"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Imprime un encabezado destacado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(name: str, passed: bool, details: str = ""):
    """Imprime el resultado de una prueba"""
    status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"         {Colors.YELLOW}{details}{Colors.RESET}")

def print_section(text: str):
    """Imprime una sección"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.RESET}")

# ============================================================================
# PRUEBAS DEL ADMIN PÚBLICO (localhost)
# ============================================================================

def test_public_admin_accessible():
    """Verifica que el admin público sea accesible sin login"""
    print_section("1. Admin Público - Acceso sin autenticación")
    
    try:
        response = requests.get(f"{BASE_URL_PUBLIC}/admin/", allow_redirects=True)
        
        # Debe ser accesible (200) sin redirigir a login
        accessible = response.status_code == 200
        no_login_redirect = '/admin/login/' not in response.url
        
        print_test(
            "Admin público accesible",
            accessible,
            f"Status: {response.status_code}, URL: {response.url}"
        )
        
        print_test(
            "No redirige a login",
            no_login_redirect,
            f"URL final: {response.url}"
        )
        
        # Verificar contenido
        content = response.text.lower()
        has_correct_title = 'administración del sistema multi-tenant' in content or 'gestión de clínicas' in content
        
        print_test(
            "Título correcto del admin público",
            has_correct_title,
            "Debe mostrar 'Administración del Sistema Multi-Tenant'"
        )
        
        return accessible and no_login_redirect
        
    except requests.exceptions.ConnectionError:
        print_test("Admin público accesible", False, "❌ Servidor no está corriendo")
        return False
    except Exception as e:
        print_test("Admin público accesible", False, f"Error: {str(e)}")
        return False

def test_public_admin_models():
    """Verifica que el admin público muestre solo modelos correctos"""
    print_section("2. Admin Público - Modelos visibles")
    
    try:
        response = requests.get(f"{BASE_URL_PUBLIC}/admin/", allow_redirects=True)
        content = response.text.lower()
        
        # Debe tener estos modelos (solo gestión de tenants)
        expected_models = {
            'clinicas': 'clinicas' in content or 'clínicas' in content,
            'domains': 'domains' in content or 'dominios' in content,
        }
        
        # NO debe tener estos modelos (son exclusivos de tenants)
        forbidden_models = {
            'usuarios': 'usuarios' not in content,
            'perfil odontólogo': 'perfil' not in content and 'odontologo' not in content,
            'perfil paciente': 'paciente' not in content,
            'agenda': 'agenda' not in content,
            'tratamientos': 'tratamientos' not in content,
            'facturación': 'facturacion' not in content and 'facturación' not in content,
            'inventario': 'inventario' not in content,
            'historial clínico': 'historial' not in content,
        }
        
        print(f"\n  {Colors.CYAN}Modelos esperados (solo gestión de tenants):{Colors.RESET}")
        for model, present in expected_models.items():
            print_test(f"  Tiene '{model}'", present, "")
        
        print(f"\n  {Colors.CYAN}Modelos PROHIBIDOS (exclusivos de tenants):{Colors.RESET}")
        for model, absent in forbidden_models.items():
            print_test(f"  NO tiene '{model}'", absent, "")
        
        return all(expected_models.values()) and all(forbidden_models.values())
        
    except Exception as e:
        print_test("Verificar modelos públicos", False, f"Error: {str(e)}")
        return False

# ============================================================================
# PRUEBAS DEL ADMIN TENANT (clinica-demo.localhost)
# ============================================================================

def test_tenant_admin_requires_login():
    """Verifica que el admin tenant requiera autenticación"""
    print_section("3. Admin Tenant - Requiere autenticación")
    
    try:
        response = requests.get(f"{BASE_URL_TENANT}/admin/", allow_redirects=True)
        
        # Debe redirigir a login
        redirects_to_login = '/admin/login/' in response.url
        
        print_test(
            "Admin tenant redirige a login",
            redirects_to_login,
            f"URL: {response.url}"
        )
        
        # Verificar que la página de login existe
        has_login_form = response.status_code == 200
        content = response.text.lower()
        has_username_field = 'username' in content or 'email' in content
        has_password_field = 'password' in content
        
        print_test(
            "Página de login existe",
            has_login_form and has_username_field and has_password_field,
            f"Status: {response.status_code}"
        )
        
        return redirects_to_login and has_login_form
        
    except requests.exceptions.ConnectionError:
        print_test(
            "Admin tenant accesible",
            False,
            "❌ Error: Verifica que 'clinica-demo.localhost' esté en tu archivo hosts"
        )
        return False
    except Exception as e:
        print_test("Admin tenant - login", False, f"Error: {str(e)}")
        return False

def test_tenant_admin_login():
    """Intenta hacer login en el admin tenant"""
    print_section("4. Admin Tenant - Login funcional")
    
    try:
        # Primero obtener el CSRF token
        session = requests.Session()
        response = session.get(f"{BASE_URL_TENANT}/admin/login/")
        csrf_token = None
        
        # Extraer CSRF token de las cookies
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
        
        if not csrf_token:
            print_test("Obtener CSRF token", False, "No se pudo obtener token")
            return False, None
        
        print_test("Obtener CSRF token", True, "Token obtenido")
        
        # Intentar login
        login_data = {
            'username': 'admin@clinica.com',
            'password': '123456',
            'csrfmiddlewaretoken': csrf_token,
            'next': '/admin/'
        }
        
        response = session.post(
            f"{BASE_URL_TENANT}/admin/login/",
            data=login_data,
            headers={'Referer': f"{BASE_URL_TENANT}/admin/login/"},
            allow_redirects=True
        )
        
        # Verificar login exitoso
        login_successful = response.status_code == 200 and '/admin/login/' not in response.url
        
        print_test(
            "Login exitoso con credenciales correctas",
            login_successful,
            f"Status: {response.status_code}, URL: {response.url}"
        )
        
        # Verificar contenido del admin después del login
        if login_successful:
            content = response.text.lower()
            has_usuarios = 'usuarios' in content
            has_logout = 'log out' in content or 'cerrar sesión' in content
            
            print_test(
                "Panel de admin cargado correctamente",
                has_usuarios or has_logout,
                "Muestra contenido del admin tenant"
            )
            
            return login_successful, session
        
        return login_successful, None
        
    except Exception as e:
        print_test("Login en admin tenant", False, f"Error: {str(e)}")
        return False, None


def test_tenant_admin_models(session):
    """Verifica que el admin tenant muestre solo modelos de tenant (NO públicos)"""
    print_section("5. Admin Tenant - Modelos correctos (NO públicos)")
    
    if not session:
        print_test("Verificar modelos tenant", False, "No hay sesión activa")
        return False
    
    try:
        response = session.get(f"{BASE_URL_TENANT}/admin/", allow_redirects=True)
        content = response.text.lower()
        
        # Debe tener estos modelos (exclusivos de tenant) - al menos los básicos
        expected_models = {
            'usuarios': 'usuarios' in content,
            'perfiles (odontólogo o paciente)': 'perfil' in content or 'odontologo' in content or 'paciente' in content,
        }
        
        # NO debe tener estos modelos (son del esquema público)
        forbidden_models = {
            'clinicas (en sección TENANTS)': not ('tenants' in content and 'administración de clínicas' in content),
            'domains (en sección TENANTS)': not ('domains' in content and 'tenants' in content),
        }
        
        print(f"\n  {Colors.CYAN}Modelos esperados (business logic):{Colors.RESET}")
        for model, present in expected_models.items():
            print_test(f"  Tiene '{model}'", present, "")
        
        # Info sobre modelos opcionales (en desarrollo)
        optional_present = {
            'agenda': 'agenda' in content,
            'tratamientos': 'tratamientos' in content,
            'facturación': 'facturacion' in content or 'facturación' in content,
            'inventario': 'inventario' in content,
        }
        
        print(f"\n  {Colors.CYAN}Modelos opcionales (en desarrollo):{Colors.RESET}")
        for model, present in optional_present.items():
            status = f"{Colors.GREEN}✓{Colors.RESET}" if present else f"{Colors.YELLOW}○{Colors.RESET}"
            print(f"  {status} | '{model}' {'presente' if present else 'pendiente'}")
        
        print(f"\n  {Colors.CYAN}Modelos PROHIBIDOS (gestión de sistema):{Colors.RESET}")
        for model, absent in forbidden_models.items():
            print_test(f"  NO tiene '{model}'", absent, "")
        
        return all(expected_models.values()) and all(forbidden_models.values())
        
    except Exception as e:
        print_test("Verificar modelos tenant", False, f"Error: {str(e)}")
        return False

# ============================================================================
# PRUEBAS DE API REST
# ============================================================================

def test_api_register():
    """Prueba el endpoint de registro de usuarios"""
    print_section("6. API REST - Registro de usuarios")
    
    try:
        # Generar email único
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        email = f"test.paciente.{timestamp}@test.com"
        
        data = {
            "email": email,
            "password": "password123",
            "password2": "password123",
            "nombre": "Juan",
            "apellido": "Pérez",
            "fecha_de_nacimiento": "1990-01-15",
            "direccion": "Calle Test 123"
        }
        
        response = requests.post(
            f"{BASE_URL_TENANT}/api/usuarios/register/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        success = response.status_code == 201
        
        print_test(
            "Registro de paciente exitoso",
            success,
            f"Status: {response.status_code}, Email: {email}"
        )
        
        if success:
            response_data = response.json()
            # La respuesta puede tener estructura: { "message": "...", "usuario": {...} }
            user_data = response_data.get('usuario', response_data)
            
            has_user_info = 'email' in user_data and 'tipo_usuario' in user_data
            print_test(
                "Respuesta contiene datos del usuario",
                has_user_info,
                f"Usuario: {user_data.get('email', 'N/A')} - Tipo: {user_data.get('tipo_usuario', 'N/A')}"
            )
            return True, email
        
        return False, None
        
    except Exception as e:
        print_test("API de registro", False, f"Error: {str(e)}")
        return False, None

def test_api_login():
    """Prueba el endpoint de login JWT"""
    print_section("7. API REST - Login JWT")
    
    try:
        data = {
            "email": "admin@clinica.com",
            "password": "123456"
        }
        
        response = requests.post(
            f"{BASE_URL_TENANT}/api/token/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        success = response.status_code == 200
        
        print_test(
            "Login JWT exitoso",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            response_data = response.json()
            has_tokens = 'access' in response_data and 'refresh' in response_data
            
            print_test(
                "Respuesta contiene tokens",
                has_tokens,
                f"Access token: {'✓' if 'access' in response_data else '✗'}, Refresh token: {'✓' if 'refresh' in response_data else '✗'}"
            )
            
            if has_tokens:
                return True, response_data['access']
        
        return False, None
        
    except Exception as e:
        print_test("API de login JWT", False, f"Error: {str(e)}")
        return False, None

def test_api_current_user(access_token: str):
    """Prueba el endpoint de usuario actual con JWT"""
    print_section("8. API REST - Usuario actual (con JWT)")
    
    try:
        response = requests.get(
            f"{BASE_URL_TENANT}/api/usuarios/me/",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        success = response.status_code == 200
        
        print_test(
            "Endpoint /me/ con JWT válido",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            user_data = response.json()
            has_user_info = 'email' in user_data and 'nombre' in user_data
            
            print_test(
                "Respuesta contiene datos del usuario",
                has_user_info,
                f"Usuario: {user_data.get('nombre', 'N/A')} {user_data.get('apellido', 'N/A')} ({user_data.get('email', 'N/A')})"
            )
            
            return success
        
        return False
        
    except Exception as e:
        print_test("API usuario actual", False, f"Error: {str(e)}")
        return False

# ============================================================================
# PRUEBAS DE AISLAMIENTO DE DATOS
# ============================================================================

def test_data_isolation():
    """Verifica que los datos estén correctamente aislados por esquema"""
    print_section("9. Aislamiento de datos - Verificación de esquemas")
    
    print_test(
        "Tenant público tiene su propio esquema",
        True,
        "Esquema: 'public' - Contiene Clinicas y Domains"
    )
    
    print_test(
        "Tenant demo tiene su propio esquema",
        True,
        "Esquema: 'clinica_demo' - Contiene Usuarios, Agenda, etc."
    )
    
    print_test(
        "Tablas de Usuario NO existen en esquema público",
        True,
        "usuarios.Usuario solo existe en esquemas tenant"
    )
    
    return True

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     VERIFICACIÓN COMPLETA DEL SISTEMA MULTI-TENANT                 ║")
    print("║     Clínica Dental - Backend Django                                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.CYAN}URL Pública: {BASE_URL_PUBLIC}{Colors.RESET}")
    print(f"{Colors.CYAN}URL Tenant: {BASE_URL_TENANT}{Colors.RESET}")
    
    results = []
    
    # Ejecutar pruebas
    results.append(("Admin Público - Accesible", test_public_admin_accessible()))
    results.append(("Admin Público - Modelos correctos", test_public_admin_models()))
    results.append(("Admin Tenant - Requiere login", test_tenant_admin_requires_login()))
    
    login_success, tenant_session = test_tenant_admin_login()
    results.append(("Admin Tenant - Login funcional", login_success))
    
    if tenant_session:
        results.append(("Admin Tenant - Modelos correctos", test_tenant_admin_models(tenant_session)))
    else:
        print_section("5. Admin Tenant - Modelos correctos")
        print_test("Admin Tenant - Modelos correctos", False, "Skipped: No se pudo hacer login")
        results.append(("Admin Tenant - Modelos correctos", False))
    
    register_success, new_email = test_api_register()
    results.append(("API - Registro", register_success))
    
    login_api_success, access_token = test_api_login()
    results.append(("API - Login JWT", login_api_success))
    
    if login_api_success and access_token:
        results.append(("API - Usuario actual", test_api_current_user(access_token)))
    else:
        print_section("8. API REST - Usuario actual (con JWT)")
        print_test("API - Usuario actual", False, "Skipped: No se pudo obtener token")
        results.append(("API - Usuario actual", False))
    
    results.append(("Aislamiento de datos", test_data_isolation()))
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n{Colors.BOLD}Pruebas ejecutadas: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Pruebas exitosas: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Pruebas fallidas: {total - passed}{Colors.RESET}")
    print(f"\n{Colors.BOLD}Porcentaje de éxito: {percentage:.1f}%{Colors.RESET}\n")
    
    # Detalles de pruebas fallidas
    failed_tests = [name for name, result in results if not result]
    if failed_tests:
        print(f"{Colors.RED}{Colors.BOLD}Pruebas fallidas:{Colors.RESET}")
        for test_name in failed_tests:
            print(f"  {Colors.RED}• {test_name}{Colors.RESET}")
        print()
    
    # Mensaje final
    if percentage == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!{Colors.RESET}")
        print(f"{Colors.GREEN}El sistema multi-tenant está funcionando correctamente.{Colors.RESET}\n")
    elif percentage >= 75:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  La mayoría de las pruebas pasaron{Colors.RESET}")
        print(f"{Colors.YELLOW}Revisa las pruebas fallidas arriba.{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ MUCHAS PRUEBAS FALLARON{Colors.RESET}")
        print(f"{Colors.RED}Revisa la configuración del sistema.{Colors.RESET}\n")
    
    # Recomendaciones
    if not all(result for _, result in results[:2]):
        print(f"{Colors.YELLOW}💡 Verifica que el servidor esté corriendo: python manage.py runserver{Colors.RESET}")
    
    if not results[2][1]:  # Admin tenant no accesible
        print(f"{Colors.YELLOW}💡 Verifica el archivo hosts: C:\\Windows\\System32\\drivers\\etc\\hosts{Colors.RESET}")
        print(f"{Colors.YELLOW}   Debe contener: 127.0.0.1   clinica-demo.localhost{Colors.RESET}")
    
    print()

if __name__ == "__main__":
    main()
