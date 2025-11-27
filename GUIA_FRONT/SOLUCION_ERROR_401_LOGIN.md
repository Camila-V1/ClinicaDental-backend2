# 🔧 SOLUCIÓN: ERROR 401 EN LOGIN FLUTTER

## ❌ PROBLEMA

Tu app Flutter está recibiendo error 401 al intentar hacer login:

```
Login response status: 401
Login response body: {"detail":"No active account found with the given credentials"}
```

## ✅ CAUSA

El problema está en el **header X-Tenant**. Estás enviando el **nombre de la clínica** cuando debes enviar el **dominio**.

### ❌ INCORRECTO:
```dart
headers: {
  'Content-Type': 'application/json',
  'X-Tenant': 'Clínica Demo',  // ❌ NOMBRE DE LA CLÍNICA
}
```

### ✅ CORRECTO:
```dart
headers: {
  'Content-Type': 'application/json',
  'X-Tenant': 'clinica-demo.localhost',  // ✅ DOMINIO
}
```

---

## 📊 INFORMACIÓN VERIFICADA DEL SISTEMA

### 🏥 Clínica en la Base de Datos:

```
Nombre:  Clínica Dental Demo
Schema:  clinica_demo
Dominio: clinica-demo.localhost
```

### 👥 Usuarios Activos (Todos con password válido):

| Email                  | Nombre            | Tipo      | Estado |
|------------------------|-------------------|-----------|--------|
| paciente1@test.com     | María García      | PACIENTE  | ✅ Activo |
| paciente2@test.com     | Carlos López      | PACIENTE  | ✅ Activo |
| paciente3@test.com     | Laura Rodríguez   | PACIENTE  | ✅ Activo |
| paciente4@test.com     | Pedro Martínez    | PACIENTE  | ✅ Activo |
| paciente5@test.com     | Ana Torres        | PACIENTE  | ✅ Activo |
| odontologo@clinica-demo.com | Dr. Carlos Rodríguez | ODONTOLOGO | ✅ Activo |

### 🔑 Passwords:
- **Pacientes**: `paciente123`
- **Odontólogo**: `odontologo123`
- **Admin**: `admin123`

---

## 🔧 SOLUCIÓN PASO A PASO

### 1. Verificar la URL Base

```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://clinica-dental-backend.onrender.com';
  
  // NO uses URLs con subdominios para multi-tenant
  // El routing se hace con X-Tenant header
}
```

### 2. Corregir Headers en AuthService

```dart
// lib/services/auth_service.dart

class AuthService {
  final String baseUrl = ApiConfig.baseUrl;
  final http.Client client;

  AuthService({http.Client? client}) : client = client ?? http.Client();

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String clinicaDominio, // Debe ser el DOMINIO, no el nombre
  }) async {
    try {
      print('🔐 [AuthService] Iniciando login...');
      print('📧 Email: $email');
      print('🏥 Dominio: $clinicaDominio');
      
      // ✅ HEADERS CORRECTOS
      final headers = {
        'Content-Type': 'application/json',
        'X-Tenant': clinicaDominio, // Enviar DOMINIO
      };

      final body = jsonEncode({
        'email': email,
        'password': password,
      });

      print('📡 Enviando request a: $baseUrl/api/token/');
      print('📋 Headers: $headers');
      print('📋 Body: $body');

      final response = await client.post(
        Uri.parse('$baseUrl/api/token/'),
        headers: headers,
        body: body,
      );

      print('📊 Status: ${response.statusCode}');
      print('📄 Response: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        print('✅ Login exitoso!');
        
        return {
          'success': true,
          'access_token': data['access'],
          'refresh_token': data['refresh'],
        };
      } else {
        final error = jsonDecode(response.body);
        print('❌ Error en login: ${error['detail']}');
        
        return {
          'success': false,
          'error': error['detail'] ?? 'Error desconocido',
        };
      }
    } catch (e) {
      print('❌ Exception en login: $e');
      return {
        'success': false,
        'error': 'Error de conexión: $e',
      };
    }
  }

  // Obtener información del usuario autenticado
  Future<Map<String, dynamic>?> getCurrentUser({
    required String accessToken,
    required String clinicaDominio,
  }) async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/usuarios/me/'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'X-Tenant': clinicaDominio,
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Error obteniendo usuario: $e');
      return null;
    }
  }
}
```

### 3. Actualizar LoginScreen

```dart
// lib/screens/auth/login_screen.dart

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  bool _isLoading = false;

  // ✅ CONFIGURACIÓN CORRECTA
  final String _clinicaDominio = 'clinica-demo.localhost';
  final String _clinicaNombre = 'Clínica Dental Demo';

  Future<void> _handleLogin() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _showError('Por favor ingrese email y contraseña');
      return;
    }

    setState(() => _isLoading = true);

    try {
      print('🔐 [LoginScreen] Iniciando login...');
      print('📧 Email: ${_emailController.text}');
      print('🏥 Clínica: $_clinicaNombre');
      print('🌐 Dominio: $_clinicaDominio');

      final result = await _authService.login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        clinicaDominio: _clinicaDominio, // ✅ Usar DOMINIO
      );

      if (result['success'] == true) {
        print('✅ [LoginScreen] Login exitoso!');
        
        // Guardar tokens
        await _saveTokens(
          accessToken: result['access_token'],
          refreshToken: result['refresh_token'],
        );

        // Obtener datos del usuario
        final userData = await _authService.getCurrentUser(
          accessToken: result['access_token'],
          clinicaDominio: _clinicaDominio,
        );

        if (userData != null) {
          // Guardar info del usuario
          await _saveUserData(userData);
          
          // Navegar según el rol
          _navigateByRole(userData['tipo_usuario']);
        }
      } else {
        print('❌ [LoginScreen] Error: ${result['error']}');
        _showError(result['error'] ?? 'Error en login');
      }
    } catch (e) {
      print('❌ [LoginScreen] Exception: $e');
      _showError('Error de conexión: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    final storage = FlutterSecureStorage();
    await storage.write(key: 'access_token', value: accessToken);
    await storage.write(key: 'refresh_token', value: refreshToken);
    await storage.write(key: 'clinica_dominio', value: _clinicaDominio);
  }

  Future<void> _saveUserData(Map<String, dynamic> userData) async {
    final storage = FlutterSecureStorage();
    await storage.write(key: 'user_data', value: jsonEncode(userData));
  }

  void _navigateByRole(String tipoUsuario) {
    switch (tipoUsuario) {
      case 'ADMIN':
        Navigator.pushReplacementNamed(context, '/admin/dashboard');
        break;
      case 'ODONTOLOGO':
        Navigator.pushReplacementNamed(context, '/odontologo/dashboard');
        break;
      case 'PACIENTE':
        Navigator.pushReplacementNamed(context, '/paciente/dashboard');
        break;
      default:
        _showError('Tipo de usuario no reconocido');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_clinicaNombre),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo o imagen
            Icon(Icons.local_hospital, size: 100, color: Colors.blue),
            SizedBox(height: 20),
            
            // Email
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Icons.email),
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),
            
            // Password
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Contraseña',
                prefixIcon: Icon(Icons.lock),
                border: OutlineInputBorder(),
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),
            
            // Botón de login
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _handleLogin,
                child: _isLoading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text('Iniciar Sesión', style: TextStyle(fontSize: 16)),
              ),
            ),
            
            // Credenciales de prueba
            SizedBox(height: 20),
            Text(
              'Usuarios de prueba:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text('paciente1@test.com / paciente123'),
            Text('paciente2@test.com / paciente123'),
            Text('paciente3@test.com / paciente123'),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
```

---

## 🧪 PRUEBA DE CONCEPTO

Verifica que tu código esté enviando exactamente esto:

```dart
// Request esperado
POST https://clinica-dental-backend.onrender.com/api/token/
Headers: {
  'Content-Type': 'application/json',
  'X-Tenant': 'clinica-demo.localhost'  // ✅ DOMINIO
}
Body: {
  "email": "paciente1@test.com",
  "password": "paciente123"
}

// Respuesta esperada (200 OK)
{
  "refresh": "eyJhbGc...",
  "access": "eyJhbGc..."
}
```

---

## 🔍 DEBUG CHECKLIST

### ✅ Verificaciones:

1. **URL correcta**:
   - ✅ `https://clinica-dental-backend.onrender.com/api/token/`
   - ❌ NO uses subdominios como `https://clinica-demo.localhost/api/token/`

2. **Header X-Tenant**:
   - ✅ `'X-Tenant': 'clinica-demo.localhost'`
   - ❌ `'X-Tenant': 'Clínica Demo'`
   - ❌ `'X-Tenant': 'clinicademo1'`

3. **Email y Password**:
   - ✅ Email sin espacios: `email.trim()`
   - ✅ Password exacto (case-sensitive)
   - ✅ Credenciales verificadas:
     - `paciente1@test.com` / `paciente123` ✅
     - `paciente2@test.com` / `paciente123` ✅
     - `paciente3@test.com` / `paciente123` ✅

4. **Headers HTTP**:
   - ✅ `'Content-Type': 'application/json'`
   - ✅ Body serializado con `jsonEncode()`

5. **Logs**:
   - Agrega `print()` en cada paso para ver exactamente qué se envía

---

## 📝 RESUMEN

### El problema era:
```dart
❌ 'X-Tenant': 'Clínica Demo'  // Nombre de la clínica
```

### La solución es:
```dart
✅ 'X-Tenant': 'clinica-demo.localhost'  // Dominio del tenant
```

### Valores correctos para tu sistema:

```dart
// Configuración de la clínica
const CLINICA_NOMBRE = 'Clínica Dental Demo';
const CLINICA_DOMINIO = 'clinica-demo.localhost';  // ⚠️ IMPORTANTE
const CLINICA_SCHEMA = 'clinica_demo';

// Usar CLINICA_DOMINIO en el header X-Tenant
final headers = {
  'X-Tenant': CLINICA_DOMINIO,  // ✅ NO el nombre
};
```

---

## 🚀 SIGUIENTE PASO

1. Actualiza tu código con el dominio correcto: `clinica-demo.localhost`
2. Prueba con cualquiera de estos usuarios:
   - `paciente1@test.com` / `paciente123`
   - `paciente2@test.com` / `paciente123`
   - `paciente3@test.com` / `paciente123`
3. Verifica los logs de debug que agregamos
4. Deberías recibir los tokens exitosamente

---

## 💡 INFORMACIÓN ADICIONAL

### Todos los usuarios verificados en la base de datos:

```
✅ paciente1@test.com  →  María García
✅ paciente2@test.com  →  Carlos López
✅ paciente3@test.com  →  Laura Rodríguez
✅ paciente4@test.com  →  Pedro Martínez
✅ paciente5@test.com  →  Ana Torres
✅ odontologo@clinica-demo.com  →  Dr. Carlos Rodríguez
```

Todos tienen:
- ✅ Contraseñas válidas configuradas
- ✅ Usuarios activos (`is_active = True`)
- ✅ Perfiles completos
- ✅ Vinculados a la clínica correcta

**El backend funciona al 100%**, solo necesitas corregir el header X-Tenant en tu app Flutter.
