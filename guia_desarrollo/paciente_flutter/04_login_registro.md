# 🔐 Login y Registro

## 🎯 Objetivo
Implementar autenticación segura con JWT para pacientes.

---

## 📡 Modelos

### `lib/models/usuario.dart`

```dart
class Usuario {
  final int id;
  final String email;
  final String fullName;
  final String? telefono;
  final String? fechaNacimiento;
  final String? direccion;

  Usuario({
    required this.id,
    required this.email,
    required this.fullName,
    this.telefono,
    this.fechaNacimiento,
    this.direccion,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'] ?? '',
      telefono: json['telefono'],
      fechaNacimiento: json['fecha_nacimiento'],
      direccion: json['direccion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'telefono': telefono,
      'fecha_nacimiento': fechaNacimiento,
      'direccion': direccion,
    };
  }
}

class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final Usuario usuario;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.usuario,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access'],
      refreshToken: json['refresh'],
      usuario: Usuario.fromJson(json['usuario']),
    );
  }
}
```

---

## 🔌 Servicio de Autenticación

### `lib/services/auth_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/usuario.dart';

class AuthService {
  final String baseUrl = AppConstants.baseUrlDev;

  // Login
  Future<AuthResponse> login({
    required String tenantId,
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
        },
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw Exception(error['message'] ?? 'Error al iniciar sesión');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Registro
  Future<AuthResponse> registro({
    required String tenantId,
    required String email,
    required String password,
    required String fullName,
    String? telefono,
    String? fechaNacimiento,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/registro/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
        },
        body: json.encode({
          'email': email,
          'password': password,
          'full_name': fullName,
          'telefono': telefono,
          'fecha_nacimiento': fechaNacimiento,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw Exception(error['message'] ?? 'Error al registrarse');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Refresh Token
  Future<String> refreshToken(String refreshToken, String tenantId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/token/refresh/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
        },
        body: json.encode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['access'];
      } else {
        throw Exception('Error al renovar token');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Verificar email
  Future<void> verificarEmail(String email) async {
    // Implementar según backend
  }

  // Recuperar contraseña
  Future<void> recuperarPassword(String email, String tenantId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/recuperar-password/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
        },
        body: json.encode({'email': email}),
      );

      if (response.statusCode != 200) {
        throw Exception('Error al enviar email de recuperación');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}
```

---

## 🗄️ Provider de Autenticación

### `lib/providers/auth_provider.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/usuario.dart';
import 'package:clinica_dental_app/services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  Usuario? _usuario;
  String? _accessToken;
  String? _refreshToken;
  bool _isAuthenticated = false;

  Usuario? get usuario => _usuario;
  bool get isAuthenticated => _isAuthenticated;
  String? get accessToken => _accessToken;

  // Login
  Future<void> login({
    required String tenantId,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _authService.login(
        tenantId: tenantId,
        email: email,
        password: password,
      );

      await _guardarSesion(response);
      
      _usuario = response.usuario;
      _accessToken = response.accessToken;
      _refreshToken = response.refreshToken;
      _isAuthenticated = true;
      
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  // Registro
  Future<void> registro({
    required String tenantId,
    required String email,
    required String password,
    required String fullName,
    String? telefono,
    String? fechaNacimiento,
  }) async {
    try {
      final response = await _authService.registro(
        tenantId: tenantId,
        email: email,
        password: password,
        fullName: fullName,
        telefono: telefono,
        fechaNacimiento: fechaNacimiento,
      );

      await _guardarSesion(response);
      
      _usuario = response.usuario;
      _accessToken = response.accessToken;
      _refreshToken = response.refreshToken;
      _isAuthenticated = true;
      
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  // Guardar sesión
  Future<void> _guardarSesion(AuthResponse response) async {
    // Tokens en secure storage
    await _secureStorage.write(
      key: AppConstants.keyAccessToken,
      value: response.accessToken,
    );
    await _secureStorage.write(
      key: AppConstants.keyRefreshToken,
      value: response.refreshToken,
    );

    // Usuario en SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(AppConstants.keyUserId, response.usuario.id);
    await prefs.setString(AppConstants.keyUserEmail, response.usuario.email);
    await prefs.setString(AppConstants.keyUserName, response.usuario.fullName);
  }

  // Cargar sesión guardada
  Future<void> cargarSesion() async {
    try {
      final accessToken = await _secureStorage.read(key: AppConstants.keyAccessToken);
      final refreshToken = await _secureStorage.read(key: AppConstants.keyRefreshToken);
      
      if (accessToken != null && refreshToken != null) {
        final prefs = await SharedPreferences.getInstance();
        final userId = prefs.getInt(AppConstants.keyUserId);
        final userEmail = prefs.getString(AppConstants.keyUserEmail);
        final userName = prefs.getString(AppConstants.keyUserName);

        if (userId != null && userEmail != null && userName != null) {
          _usuario = Usuario(
            id: userId,
            email: userEmail,
            fullName: userName,
          );
          _accessToken = accessToken;
          _refreshToken = refreshToken;
          _isAuthenticated = true;
          notifyListeners();
        }
      }
    } catch (e) {
      debugPrint('Error al cargar sesión: $e');
    }
  }

  // Logout
  Future<void> logout() async {
    // Limpiar tokens
    await _secureStorage.delete(key: AppConstants.keyAccessToken);
    await _secureStorage.delete(key: AppConstants.keyRefreshToken);
    
    // Limpiar usuario
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.keyUserId);
    await prefs.remove(AppConstants.keyUserEmail);
    await prefs.remove(AppConstants.keyUserName);
    
    _usuario = null;
    _accessToken = null;
    _refreshToken = null;
    _isAuthenticated = false;
    
    notifyListeners();
  }

  // Refresh token
  Future<void> renovarToken(String tenantId) async {
    if (_refreshToken == null) {
      await logout();
      return;
    }

    try {
      final newAccessToken = await _authService.refreshToken(_refreshToken!, tenantId);
      
      await _secureStorage.write(
        key: AppConstants.keyAccessToken,
        value: newAccessToken,
      );
      
      _accessToken = newAccessToken;
      notifyListeners();
    } catch (e) {
      await logout();
    }
  }
}
```

---

## 📱 Pantalla de Login

### `lib/screens/login_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/custom_button.dart';
import 'package:clinica_dental_app/widgets/common/custom_text_field.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    if (clinicaProvider.clinicaSeleccionada == null) {
      _showError('No hay clínica seleccionada');
      return;
    }

    setState(() => _isLoading = true);

    try {
      await authProvider.login(
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );

      if (mounted) {
        context.go('/home');
      }
    } catch (e) {
      _showError(e.toString());
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final clinicaProvider = Provider.of<ClinicaProvider>(context);

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 40),
                
                // Logo o ícono
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    Icons.local_hospital_rounded,
                    size: 48,
                    color: Theme.of(context).primaryColor,
                  ),
                ),
                const SizedBox(height: 32),
                
                // Clínica seleccionada
                if (clinicaProvider.clinicaSeleccionada != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: Theme.of(context).primaryColor.withOpacity(0.2),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.business,
                          size: 20,
                          color: Theme.of(context).primaryColor,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            clinicaProvider.clinicaSeleccionada!.nombre,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: () => context.go('/selector-clinica'),
                          child: const Text('Cambiar'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
                
                // Título
                Text(
                  'Iniciar Sesión',
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  'Ingresa tus credenciales para continuar',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 32),
                
                // Email
                CustomTextField(
                  controller: _emailController,
                  label: 'Email',
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.email_outlined,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Ingresa tu email';
                    }
                    if (!value.contains('@')) {
                      return 'Email inválido';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                // Contraseña
                CustomTextField(
                  controller: _passwordController,
                  label: 'Contraseña',
                  obscureText: _obscurePassword,
                  prefixIcon: Icons.lock_outlined,
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_off : Icons.visibility,
                    ),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Ingresa tu contraseña';
                    }
                    if (value.length < 6) {
                      return 'Mínimo 6 caracteres';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                
                // Olvidé mi contraseña
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {
                      // Navegar a recuperar contraseña
                    },
                    child: const Text('¿Olvidaste tu contraseña?'),
                  ),
                ),
                const SizedBox(height: 24),
                
                // Botón de login
                CustomButton(
                  text: 'Iniciar Sesión',
                  onPressed: _handleLogin,
                  isLoading: _isLoading,
                ),
                const SizedBox(height: 24),
                
                // Registrarse
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '¿No tienes cuenta? ',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    TextButton(
                      onPressed: () => context.go('/registro'),
                      child: const Text('Regístrate'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

---

## 🎨 Widgets Personalizados

### `lib/widgets/common/custom_text_field.dart`

```dart
import 'package:flutter/material.dart';

class CustomTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String? hint;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;
  final int maxLines;

  const CustomTextField({
    super.key,
    required this.controller,
    required this.label,
    this.hint,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.validator,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      validator: validator,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: prefixIcon != null ? Icon(prefixIcon) : null,
        suffixIcon: suffixIcon,
      ),
    );
  }
}
```

### `lib/widgets/common/custom_button.dart`

```dart
import 'package:flutter/material.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final bool isLoading;
  final bool isOutlined;
  final IconData? icon;

  const CustomButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.isOutlined = false,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    if (isOutlined) {
      return OutlinedButton(
        onPressed: isLoading ? null : onPressed,
        child: _buildChild(),
      );
    }

    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      child: _buildChild(),
    );
  }

  Widget _buildChild() {
    if (isLoading) {
      return const SizedBox(
        height: 20,
        width: 20,
        child: LoadingIndicator(size: 20, color: Colors.white),
      );
    }

    if (icon != null) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon),
          const SizedBox(width: 8),
          Text(text),
        ],
      );
    }

    return Text(text);
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelos `Usuario` y `AuthResponse`
- [ ] Crear `AuthService`
- [ ] Crear `AuthProvider`
- [ ] Crear `LoginScreen`
- [ ] Crear `RegistroScreen` (similar a LoginScreen)
- [ ] Crear widgets `CustomTextField` y `CustomButton`
- [ ] Implementar validaciones de formulario
- [ ] Probar login con credenciales reales
- [ ] Verificar guardado de tokens
- [ ] Probar navegación después del login

---

**Siguiente:** [05_home_dashboard.md](05_home_dashboard.md)
