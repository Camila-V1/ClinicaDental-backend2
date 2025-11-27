# 🔐 Guía: Reconocer Usuario Administrador en Flutter

## 📋 Resumen

En el sistema multi-tenant de la clínica dental, los usuarios tienen un campo `tipo_usuario` que puede ser:
- **ADMIN** - Administrador (acceso total)
- **ODONTOLOGO** - Odontólogo (acceso profesional)
- **PACIENTE** - Paciente (acceso limitado)

## 🎯 Objetivo

Hacer que Flutter reconozca el tipo de usuario para:
1. Mostrar/ocultar opciones del menú
2. Habilitar/deshabilitar funcionalidades
3. Personalizar la interfaz según el rol
4. Controlar acceso a pantallas

---

## 📱 Implementación en Flutter

### 1. Modelo de Usuario

```dart
// lib/models/usuario_model.dart

class Usuario {
  final int id;
  final String email;
  final String nombre;
  final String apellido;
  final String ci;
  final String? telefono;
  final String tipoUsuario; // 'ADMIN', 'ODONTOLOGO', 'PACIENTE'
  final bool isActive;
  final DateTime? createdAt;

  Usuario({
    required this.id,
    required this.email,
    required this.nombre,
    required this.apellido,
    required this.ci,
    this.telefono,
    required this.tipoUsuario,
    required this.isActive,
    this.createdAt,
  });

  // Métodos de conveniencia para verificar rol
  bool get isAdmin => tipoUsuario == 'ADMIN';
  bool get isOdontologo => tipoUsuario == 'ODONTOLOGO';
  bool get isPaciente => tipoUsuario == 'PACIENTE';
  
  // Verificar si tiene permisos administrativos
  bool get hasAdminPrivileges => isAdmin;
  
  // Verificar si es personal de la clínica (Admin u Odontólogo)
  bool get isStaff => isAdmin || isOdontologo;

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'],
      email: json['email'],
      nombre: json['nombre'],
      apellido: json['apellido'],
      ci: json['ci'],
      telefono: json['telefono'],
      tipoUsuario: json['tipo_usuario'], // Importante: snake_case del backend
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nombre': nombre,
      'apellido': apellido,
      'ci': ci,
      'telefono': telefono,
      'tipo_usuario': tipoUsuario,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  String get nombreCompleto => '$nombre $apellido';
  
  String get tipoUsuarioDisplay {
    switch (tipoUsuario) {
      case 'ADMIN':
        return 'Administrador';
      case 'ODONTOLOGO':
        return 'Odontólogo';
      case 'PACIENTE':
        return 'Paciente';
      default:
        return tipoUsuario;
    }
  }
}
```

---

### 2. AuthService con Detección de Rol

```dart
// lib/services/auth_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/usuario_model.dart';

class AuthService {
  final String baseUrl;
  final String tenantId;

  AuthService({
    required this.baseUrl,
    required this.tenantId,
  });

  // Guardar información del usuario
  Future<void> _saveUserInfo(Usuario usuario, String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    await prefs.setString('user_data', jsonEncode(usuario.toJson()));
    await prefs.setString('tipo_usuario', usuario.tipoUsuario);
    await prefs.setInt('user_id', usuario.id);
  }

  // Obtener usuario actual
  Future<Usuario?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString('user_data');
    
    if (userDataString == null) return null;
    
    try {
      final userData = jsonDecode(userDataString);
      return Usuario.fromJson(userData);
    } catch (e) {
      print('Error al obtener usuario: $e');
      return null;
    }
  }

  // Verificar si es admin
  Future<bool> isAdmin() async {
    final prefs = await SharedPreferences.getInstance();
    final tipoUsuario = prefs.getString('tipo_usuario');
    return tipoUsuario == 'ADMIN';
  }

  // Verificar si es staff (Admin u Odontólogo)
  Future<bool> isStaff() async {
    final prefs = await SharedPreferences.getInstance();
    final tipoUsuario = prefs.getString('tipo_usuario');
    return ['ADMIN', 'ODONTOLOGO'].contains(tipoUsuario);
  }

  // Obtener tipo de usuario
  Future<String?> getTipoUsuario() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('tipo_usuario');
  }

  // Login
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
        },
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Obtener perfil del usuario
        final perfilResponse = await http.get(
          Uri.parse('$baseUrl/api/usuarios/me/'),
          headers: {
            'Authorization': 'Bearer ${data['access']}',
            'X-Tenant-ID': tenantId,
          },
        );

        if (perfilResponse.statusCode == 200) {
          final perfilData = jsonDecode(perfilResponse.body);
          final usuario = Usuario.fromJson(perfilData);
          
          // Guardar datos
          await _saveUserInfo(usuario, data['access']);
          
          return {
            'success': true,
            'usuario': usuario,
            'token': data['access'],
          };
        }
      }

      return {
        'success': false,
        'error': 'Credenciales inválidas',
      };
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión: $e',
      };
    }
  }

  // Logout
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
```

---

### 3. AuthProvider con Estado del Usuario

```dart
// lib/providers/auth_provider.dart

import 'package:flutter/foundation.dart';
import '../models/usuario_model.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService;
  
  Usuario? _usuario;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _error;

  AuthProvider(this._authService) {
    _loadUserFromCache();
  }

  // Getters
  Usuario? get usuario => _usuario;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Verificadores de rol
  bool get isAdmin => _usuario?.isAdmin ?? false;
  bool get isOdontologo => _usuario?.isOdontologo ?? false;
  bool get isPaciente => _usuario?.isPaciente ?? false;
  bool get isStaff => _usuario?.isStaff ?? false;

  String? get tipoUsuario => _usuario?.tipoUsuario;
  String? get nombreCompleto => _usuario?.nombreCompleto;

  // Cargar usuario desde caché
  Future<void> _loadUserFromCache() async {
    _isLoading = true;
    notifyListeners();

    try {
      _usuario = await _authService.getCurrentUser();
      _isAuthenticated = _usuario != null;
    } catch (e) {
      print('Error al cargar usuario: $e');
      _isAuthenticated = false;
    }

    _isLoading = false;
    notifyListeners();
  }

  // Login
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _authService.login(email, password);

      if (result['success']) {
        _usuario = result['usuario'];
        _isAuthenticated = true;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = result['error'];
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Logout
  Future<void> logout() async {
    await _authService.logout();
    _usuario = null;
    _isAuthenticated = false;
    notifyListeners();
  }

  // Actualizar usuario
  void updateUsuario(Usuario usuario) {
    _usuario = usuario;
    notifyListeners();
  }
}
```

---

### 4. Uso en la UI - Menú Condicional

```dart
// lib/widgets/app_drawer.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final usuario = authProvider.usuario;

    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          // Header con información del usuario
          UserAccountsDrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor,
            ),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                usuario?.nombre.substring(0, 1).toUpperCase() ?? 'U',
                style: TextStyle(
                  fontSize: 40,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ),
            accountName: Text(usuario?.nombreCompleto ?? 'Usuario'),
            accountEmail: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(usuario?.email ?? ''),
                SizedBox(height: 4),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: _getRolColor(authProvider.tipoUsuario),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    usuario?.tipoUsuarioDisplay ?? '',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),

          // Dashboard (Todos)
          ListTile(
            leading: Icon(Icons.dashboard),
            title: Text('Dashboard'),
            onTap: () => Navigator.pushNamed(context, '/dashboard'),
          ),

          // ========== OPCIONES SOLO ADMIN ==========
          if (authProvider.isAdmin) ...[
            Divider(),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                'ADMINISTRACIÓN',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey,
                ),
              ),
            ),
            ListTile(
              leading: Icon(Icons.people, color: Colors.blue),
              title: Text('Gestión de Usuarios'),
              onTap: () => Navigator.pushNamed(context, '/usuarios'),
            ),
            ListTile(
              leading: Icon(Icons.inventory, color: Colors.orange),
              title: Text('Inventario'),
              onTap: () => Navigator.pushNamed(context, '/inventario'),
            ),
            ListTile(
              leading: Icon(Icons.medical_services, color: Colors.green),
              title: Text('Tratamientos'),
              onTap: () => Navigator.pushNamed(context, '/tratamientos'),
            ),
            ListTile(
              leading: Icon(Icons.backup, color: Colors.purple),
              title: Text('Backups'),
              onTap: () => Navigator.pushNamed(context, '/backups'),
            ),
            ListTile(
              leading: Icon(Icons.bar_chart, color: Colors.red),
              title: Text('Reportes'),
              onTap: () => Navigator.pushNamed(context, '/reportes'),
            ),
          ],

          // ========== OPCIONES PARA ODONTÓLOGO ==========
          if (authProvider.isOdontologo) ...[
            Divider(),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                'PROFESIONAL',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey,
                ),
              ),
            ),
            ListTile(
              leading: Icon(Icons.calendar_today, color: Colors.blue),
              title: Text('Agenda'),
              onTap: () => Navigator.pushNamed(context, '/agenda'),
            ),
            ListTile(
              leading: Icon(Icons.people_outline, color: Colors.teal),
              title: Text('Pacientes'),
              onTap: () => Navigator.pushNamed(context, '/pacientes'),
            ),
          ],

          // ========== OPCIONES PARA PACIENTES ==========
          if (authProvider.isPaciente) ...[
            Divider(),
            ListTile(
              leading: Icon(Icons.event_available),
              title: Text('Mis Citas'),
              onTap: () => Navigator.pushNamed(context, '/mis-citas'),
            ),
            ListTile(
              leading: Icon(Icons.medical_information),
              title: Text('Mi Historial Clínico'),
              onTap: () => Navigator.pushNamed(context, '/mi-historial'),
            ),
            ListTile(
              leading: Icon(Icons.receipt),
              title: Text('Mis Facturas'),
              onTap: () => Navigator.pushNamed(context, '/mis-facturas'),
            ),
          ],

          // ========== OPCIONES COMUNES ==========
          Divider(),
          ListTile(
            leading: Icon(Icons.chat),
            title: Text('Chatbot'),
            onTap: () => Navigator.pushNamed(context, '/chatbot'),
          ),
          ListTile(
            leading: Icon(Icons.settings),
            title: Text('Configuración'),
            onTap: () => Navigator.pushNamed(context, '/configuracion'),
          ),

          Divider(),
          ListTile(
            leading: Icon(Icons.logout, color: Colors.red),
            title: Text('Cerrar Sesión', style: TextStyle(color: Colors.red)),
            onTap: () async {
              final confirm = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text('Cerrar Sesión'),
                  content: Text('¿Estás seguro que deseas cerrar sesión?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: Text('Cancelar'),
                    ),
                    ElevatedButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: Text('Cerrar Sesión'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                      ),
                    ),
                  ],
                ),
              );

              if (confirm == true) {
                await authProvider.logout();
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),
    );
  }

  Color _getRolColor(String? tipoUsuario) {
    switch (tipoUsuario) {
      case 'ADMIN':
        return Colors.red;
      case 'ODONTOLOGO':
        return Colors.blue;
      case 'PACIENTE':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}
```

---

### 5. Protección de Rutas

```dart
// lib/utils/route_guard.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class RouteGuard extends StatelessWidget {
  final Widget child;
  final bool requiresAuth;
  final bool requiresAdmin;
  final bool requiresStaff; // Admin u Odontólogo
  final List<String>? allowedRoles; // ['ADMIN', 'ODONTOLOGO', 'PACIENTE']

  const RouteGuard({
    Key? key,
    required this.child,
    this.requiresAuth = true,
    this.requiresAdmin = false,
    this.requiresStaff = false, // Admin u Odontólogo solamente
    this.allowedRoles,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, _) {
        // Verificar autenticación
        if (requiresAuth && !authProvider.isAuthenticated) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacementNamed(context, '/login');
          });
          return Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Verificar si requiere admin
        if (requiresAdmin && !authProvider.isAdmin) {
          return Scaffold(
            appBar: AppBar(title: Text('Acceso Denegado')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.lock, size: 80, color: Colors.red),
                  SizedBox(height: 16),
                  Text(
                    'Acceso Restringido',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Solo administradores pueden acceder a esta sección',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                  SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Volver'),
                  ),
                ],
              ),
            ),
          );
        }

        // Verificar si requiere staff (Admin u Odontólogo)
        if (requiresStaff && !authProvider.isStaff) {
          return Scaffold(
            appBar: AppBar(title: Text('Acceso Denegado')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.lock, size: 80, color: Colors.orange),
                  SizedBox(height: 16),
                  Text(
                    'Acceso Restringido',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Solo administradores y odontólogos pueden acceder',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                  SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Volver'),
                  ),
                ],
              ),
            ),
          );
        }

        // Verificar roles específicos
        if (allowedRoles != null && 
            !allowedRoles!.contains(authProvider.tipoUsuario)) {
          return Scaffold(
            appBar: AppBar(title: Text('Acceso Denegado')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.lock, size: 80, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No tienes permisos',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Tu rol no tiene acceso a esta funcionalidad',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                  SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Volver'),
                  ),
                ],
              ),
            ),
          );
        }

        // Si pasa todas las verificaciones, mostrar el widget
        return child;
      },
    );
  }
}

// Uso:
// RouteGuard(
//   requiresAdmin: true,
//   child: BackupsScreen(),
// )
```

---

### 6. Ejemplo de Rutas Protegidas

```dart
// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AuthProvider(
            AuthService(
              baseUrl: 'https://clinica-dental-backend.onrender.com',
              tenantId: 'clinica_demo',
            ),
          ),
        ),
      ],
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Clínica Dental',
      theme: ThemeData(primarySwatch: Colors.blue),
      initialRoute: '/login',
      routes: {
        '/login': (context) => LoginScreen(),
        '/dashboard': (context) => DashboardScreen(),
        
        // Rutas solo para ADMIN
        '/usuarios': (context) => RouteGuard(
          requiresAdmin: true,
          child: UsuariosScreen(),
        ),
        '/inventario': (context) => RouteGuard(
          requiresAdmin: true,
          child: InventarioScreen(),
        ),
        '/backups': (context) => RouteGuard(
          requiresAdmin: true,
          child: BackupsScreen(),
        ),
        '/reportes': (context) => RouteGuard(
          requiresAdmin: true,
          child: ReportesScreen(),
        ),
        
        // Rutas para STAFF (Admin u Odontólogo)
        '/agenda': (context) => RouteGuard(
          requiresStaff: true,
          child: AgendaScreen(),
        ),
        '/pacientes': (context) => RouteGuard(
          requiresStaff: true,
          child: PacientesScreen(),
        ),
        
        // Rutas para PACIENTES
        '/mis-citas': (context) => RouteGuard(
          allowedRoles: ['PACIENTE'],
          child: MisCitasScreen(),
        ),
        '/mi-historial': (context) => RouteGuard(
          allowedRoles: ['PACIENTE'],
          child: MiHistorialScreen(),
        ),
        
        // Rutas públicas (autenticadas)
        '/chatbot': (context) => RouteGuard(
          child: ChatScreen(),
        ),
        '/configuracion': (context) => RouteGuard(
          child: ConfiguracionScreen(),
        ),
      },
    );
  }
}
```

---

### 7. Botones Condicionales en la UI

```dart
// Ejemplo en una pantalla

class DashboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard'),
        actions: [
          // Botón solo visible para admin
          if (authProvider.isAdmin)
            IconButton(
              icon: Icon(Icons.settings),
              onPressed: () {
                Navigator.pushNamed(context, '/configuracion-admin');
              },
              tooltip: 'Configuración Admin',
            ),
        ],
      ),
      body: ListView(
        children: [
          // Card de estadísticas para admin
          if (authProvider.isAdmin)
            Card(
              child: ListTile(
                leading: Icon(Icons.admin_panel_settings, color: Colors.red),
                title: Text('Panel de Administración'),
                subtitle: Text('Gestionar usuarios, inventario y backups'),
                trailing: Icon(Icons.arrow_forward_ios),
                onTap: () => Navigator.pushNamed(context, '/admin-panel'),
              ),
            ),

          // Card de agenda para staff
          if (authProvider.isStaff)
            Card(
              child: ListTile(
                leading: Icon(Icons.calendar_today, color: Colors.blue),
                title: Text('Agenda del Día'),
                subtitle: Text('Ver citas programadas'),
                trailing: Icon(Icons.arrow_forward_ios),
                onTap: () => Navigator.pushNamed(context, '/agenda'),
              ),
            ),

          // Card de citas para pacientes
          if (authProvider.isPaciente)
            Card(
              child: ListTile(
                leading: Icon(Icons.event, color: Colors.green),
                title: Text('Mis Próximas Citas'),
                subtitle: Text('Ver y gestionar tus citas'),
                trailing: Icon(Icons.arrow_forward_ios),
                onTap: () => Navigator.pushNamed(context, '/mis-citas'),
              ),
            ),

          // Chatbot (todos)
          Card(
            child: ListTile(
              leading: Icon(Icons.chat, color: Colors.purple),
              title: Text('Chatbot'),
              subtitle: Text('Asistente virtual'),
              trailing: Icon(Icons.arrow_forward_ios),
              onTap: () => Navigator.pushNamed(context, '/chatbot'),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear modelo `Usuario` con getters `isAdmin`, `isStaff`, etc.
- [ ] Actualizar `AuthService` para guardar `tipo_usuario`
- [ ] Crear `AuthProvider` con verificadores de rol
- [ ] Implementar `RouteGuard` para proteger rutas
- [ ] Actualizar menú lateral con opciones condicionales
- [ ] Agregar verificaciones en botones y acciones
- [ ] Configurar rutas protegidas en `main.dart`
- [ ] Probar con diferentes tipos de usuario

---

## 🧪 Pruebas

```dart
// Probar con diferentes usuarios:

// 1. Admin
email: admin@clinicademo1.com
password: admin123
✅ Debe ver: Gestión Usuarios, Inventario, Backups, Reportes

// 2. Paciente
email: paciente1@test.com
password: paciente123
✅ Debe ver: Mis Citas, Mi Historial, Mis Facturas

// 3. Odontólogo
email: odontologo@clinica-demo.com
password: odontologo123
✅ Debe ver: Agenda, Pacientes
```

---

## 🔑 Puntos Clave

- El backend retorna `tipo_usuario` en formato **ADMIN, ODONTOLOGO, PACIENTE**
- Flutter guarda este valor en `SharedPreferences`
- Se verifica con `authProvider.isAdmin`, `authProvider.isOdontologo`, `authProvider.isPaciente`
- `isStaff` = Admin u Odontólogo (personal de la clínica)
- El menú y rutas se adaptan automáticamente al rol

La guía está lista para implementar. Solo necesitas agregar las dependencias `provider` y `shared_preferences` a tu proyecto Flutter.

---

¡Listo! Ahora Flutter puede reconocer y controlar el acceso según el tipo de usuario. 🔐
