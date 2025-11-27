# 🔐 GUÍA COMPLETA: AUTENTICACIÓN, ROLES Y PERMISOS EN FLUTTER

## 📋 ÍNDICE

1. [Arquitectura de Autenticación](#arquitectura)
2. [Flujo de Login](#flujo-login)
3. [Reconocimiento de Usuario y Roles](#reconocimiento-roles)
4. [Sistema de Permisos](#sistema-permisos)
5. [Implementación Práctica](#implementacion)
6. [Protección de Rutas](#proteccion-rutas)
7. [Manejo de Tokens](#manejo-tokens)
8. [Best Practices](#best-practices)

---

## 1. ARQUITECTURA DE AUTENTICACIÓN {#arquitectura}

### 🏗️ Estructura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FLUTTER APP                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Login Screen │→ │ Auth Service │→ │ Auth Context │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↓                 ↓                  ↓          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Secure Storage (Tokens + User)           │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Route Guards (Role-based Protection)         │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Admin Views  │  │ Doctor Views │  │Patient Views │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↓
              ┌──────────────────────┐
              │   BACKEND API        │
              │  /api/token/         │
              │  /api/usuarios/me/   │
              └──────────────────────┘
```

---

## 2. FLUJO DE LOGIN {#flujo-login}

### 📝 Paso a Paso del Login

```dart
// ============================================
// PASO 1: USUARIO INGRESA CREDENCIALES
// ============================================

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String? _selectedClinica;
  
  List<Map<String, dynamic>> _clinicas = [];

  @override
  void initState() {
    super.initState();
    _cargarClinicas();
  }

  // Cargar lista de clínicas disponibles
  Future<void> _cargarClinicas() async {
    try {
      final response = await http.get(
        Uri.parse('$BASE_URL/api/tenants/'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _clinicas = List<Map<String, dynamic>>.from(
            data['clinicas']
          );
        });
      }
    } catch (e) {
      print('Error al cargar clínicas: $e');
    }
  }

  // ============================================
  // PASO 2: VALIDAR Y ENVIAR CREDENCIALES
  // ============================================
  
  Future<void> _handleLogin() async {
    if (_emailController.text.isEmpty || 
        _passwordController.text.isEmpty ||
        _selectedClinica == null) {
      _mostrarError('Complete todos los campos');
      return;
    }

    setState(() => _isLoading = true);

    try {
      print('🔐 [LoginScreen] Iniciando login...');
      print('🔐 [LoginScreen] Email: ${_emailController.text}');
      print('🔐 [LoginScreen] Clínica: $_selectedClinica');

      // Llamar al servicio de autenticación
      final success = await context.read<AuthContext>().login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        clinicaDominio: _selectedClinica!,
      );

      if (success) {
        print('✅ Login exitoso');
        // La navegación se maneja automáticamente en AuthContext
      } else {
        _mostrarError('Credenciales incorrectas');
      }
    } catch (e) {
      print('❌ [LoginScreen] Error en login: $e');
      _mostrarError('Error de conexión: $e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Image.asset('assets/logo.png', height: 100),
            SizedBox(height: 40),

            // Selector de Clínica
            DropdownButtonFormField<String>(
              value: _selectedClinica,
              decoration: InputDecoration(
                labelText: 'Seleccione Clínica',
                prefixIcon: Icon(Icons.business),
              ),
              items: _clinicas.map((clinica) {
                return DropdownMenuItem(
                  value: clinica['dominio'],
                  child: Text(clinica['nombre']),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedClinica = value);
              },
            ),
            SizedBox(height: 16),

            // Email
            TextFormField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Icons.email),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),

            // Password
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Contraseña',
                prefixIcon: Icon(Icons.lock),
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),

            // Botón Login
            ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('INGRESAR'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 🔄 Servicio de Autenticación

```dart
// ============================================
// PASO 3: AUTH SERVICE - COMUNICACIÓN CON API
// ============================================

class AuthService {
  final String baseUrl;
  final http.Client client;

  AuthService({
    required this.baseUrl,
    http.Client? client,
  }) : client = client ?? http.Client();

  /// Login - Obtener tokens JWT
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String clinicaDominio,
  }) async {
    try {
      print('📡 Enviando request de login...');
      
      // Headers específicos para multi-tenant
      final headers = {
        'Content-Type': 'application/json',
        'X-Tenant': clinicaDominio, // Importante para multi-tenant
      };

      final body = jsonEncode({
        'email': email,
        'password': password,
      });

      final response = await client.post(
        Uri.parse('$baseUrl/api/token/'),
        headers: headers,
        body: body,
      );

      print('Login response status: ${response.statusCode}');
      print('Login response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // La respuesta contiene:
        // - access: Token de acceso (JWT)
        // - refresh: Token de refresco
        // - user: Datos básicos del usuario
        
        return {
          'success': true,
          'access_token': data['access'],
          'refresh_token': data['refresh'],
          'user': data['user'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Error desconocido',
        };
      }
    } catch (e) {
      print('❌ Error en AuthService.login: $e');
      return {
        'success': false,
        'error': 'Error de conexión: $e',
      };
    }
  }

  /// Obtener datos completos del usuario autenticado
  Future<Map<String, dynamic>?> getCurrentUser(String token) async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/usuarios/me/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Error al obtener usuario: $e');
      return null;
    }
  }

  /// Refrescar token de acceso
  Future<String?> refreshToken(String refreshToken) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['access'];
      }
      return null;
    } catch (e) {
      print('Error al refrescar token: $e');
      return null;
    }
  }

  /// Logout (opcional: invalidar token en backend)
  Future<void> logout(String token) async {
    try {
      await client.post(
        Uri.parse('$baseUrl/api/logout/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
    } catch (e) {
      print('Error en logout: $e');
    }
  }
}
```

---

## 3. RECONOCIMIENTO DE USUARIO Y ROLES {#reconocimiento-roles}

### 👤 Modelo de Usuario

```dart
// ============================================
// MODELO DE USUARIO CON TODOS LOS DATOS
// ============================================

class Usuario {
  final int id;
  final String email;
  final String nombreCompleto;
  final TipoUsuario tipo;
  final String? telefono;
  final String? direccion;
  final bool activo;
  final DateTime? fechaRegistro;
  final PerfilPaciente? perfilPaciente;
  final PerfilOdontologo? perfilOdontologo;

  Usuario({
    required this.id,
    required this.email,
    required this.nombreCompleto,
    required this.tipo,
    this.telefono,
    this.direccion,
    this.activo = true,
    this.fechaRegistro,
    this.perfilPaciente,
    this.perfilOdontologo,
  });

  // ============================================
  // MÉTODOS DE RECONOCIMIENTO DE ROL
  // ============================================

  bool get isAdmin => tipo == TipoUsuario.admin;
  bool get isOdontologo => tipo == TipoUsuario.odontologo;
  bool get isPaciente => tipo == TipoUsuario.paciente;

  // Permisos derivados del rol
  bool get canManageUsers => isAdmin;
  bool get canViewReports => isAdmin || isOdontologo;
  bool get canCreateCitas => isAdmin || isOdontologo;
  bool get canViewAllCitas => isAdmin || isOdontologo;
  bool get canManageInventory => isAdmin;
  bool get canManageTreatments => isAdmin || isOdontologo;
  bool get canViewOwnData => true; // Todos los usuarios

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'],
      email: json['email'],
      nombreCompleto: json['nombre_completo'] ?? json['full_name'],
      tipo: TipoUsuario.fromString(json['tipo_usuario']),
      telefono: json['telefono'],
      direccion: json['direccion'],
      activo: json['activo'] ?? true,
      fechaRegistro: json['fecha_registro'] != null
          ? DateTime.parse(json['fecha_registro'])
          : null,
      perfilPaciente: json['perfil_paciente'] != null
          ? PerfilPaciente.fromJson(json['perfil_paciente'])
          : null,
      perfilOdontologo: json['perfil_odontologo'] != null
          ? PerfilOdontologo.fromJson(json['perfil_odontologo'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nombre_completo': nombreCompleto,
      'tipo_usuario': tipo.value,
      'telefono': telefono,
      'direccion': direccion,
      'activo': activo,
      'fecha_registro': fechaRegistro?.toIso8601String(),
      'perfil_paciente': perfilPaciente?.toJson(),
      'perfil_odontologo': perfilOdontologo?.toJson(),
    };
  }
}

// ============================================
// ENUM DE TIPOS DE USUARIO
// ============================================

enum TipoUsuario {
  admin('ADMIN', 'Administrador'),
  odontologo('ODONTOLOGO', 'Odontólogo'),
  paciente('PACIENTE', 'Paciente');

  final String value;
  final String displayName;

  const TipoUsuario(this.value, this.displayName);

  static TipoUsuario fromString(String value) {
    return TipoUsuario.values.firstWhere(
      (tipo) => tipo.value == value.toUpperCase(),
      orElse: () => TipoUsuario.paciente,
    );
  }
}

// ============================================
// PERFIL DE PACIENTE
// ============================================

class PerfilPaciente {
  final int id;
  final String? grupoSanguineo;
  final String? alergias;
  final String? enfermedadesCronicas;
  final String? contactoEmergencia;
  final String? telefonoEmergencia;

  PerfilPaciente({
    required this.id,
    this.grupoSanguineo,
    this.alergias,
    this.enfermedadesCronicas,
    this.contactoEmergencia,
    this.telefonoEmergencia,
  });

  factory PerfilPaciente.fromJson(Map<String, dynamic> json) {
    return PerfilPaciente(
      id: json['id'],
      grupoSanguineo: json['grupo_sanguineo'],
      alergias: json['alergias'],
      enfermedadesCronicas: json['enfermedades_cronicas'],
      contactoEmergencia: json['contacto_emergencia'],
      telefonoEmergencia: json['telefono_emergencia'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'grupo_sanguineo': grupoSanguineo,
      'alergias': alergias,
      'enfermedades_cronicas': enfermedadesCronicas,
      'contacto_emergencia': contactoEmergencia,
      'telefono_emergencia': telefonoEmergencia,
    };
  }
}

// ============================================
// PERFIL DE ODONTÓLOGO
// ============================================

class PerfilOdontologo {
  final int id;
  final String? numeroLicencia;
  final String? especialidad;
  final int? aniosExperiencia;
  final String? universidad;
  final int? anoGraduacion;

  PerfilOdontologo({
    required this.id,
    this.numeroLicencia,
    this.especialidad,
    this.aniosExperiencia,
    this.universidad,
    this.anoGraduacion,
  });

  factory PerfilOdontologo.fromJson(Map<String, dynamic> json) {
    return PerfilOdontologo(
      id: json['id'],
      numeroLicencia: json['numero_licencia'],
      especialidad: json['especialidad'],
      aniosExperiencia: json['anios_experiencia'],
      universidad: json['universidad'],
      anoGraduacion: json['ano_graduacion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'numero_licencia': numeroLicencia,
      'especialidad': especialidad,
      'anios_experiencia': aniosExperiencia,
      'universidad': universidad,
      'ano_graduacion': anoGraduacion,
    };
  }
}
```

---

## 4. SISTEMA DE PERMISOS {#sistema-permisos}

### 🔒 Permission Manager

```dart
// ============================================
// GESTOR DE PERMISOS CENTRALIZADO
// ============================================

class PermissionManager {
  final Usuario usuario;

  PermissionManager(this.usuario);

  // ============================================
  // PERMISOS DE USUARIOS
  // ============================================

  bool canCreateUser() => usuario.isAdmin;
  bool canEditUser(int userId) => usuario.isAdmin || usuario.id == userId;
  bool canDeleteUser() => usuario.isAdmin;
  bool canViewAllUsers() => usuario.isAdmin;

  // ============================================
  // PERMISOS DE CITAS
  // ============================================

  bool canCreateCita() => usuario.isAdmin || usuario.isOdontologo;
  bool canEditCita(Cita cita) {
    if (usuario.isAdmin) return true;
    if (usuario.isOdontologo && cita.odontologoId == usuario.id) return true;
    if (usuario.isPaciente && cita.pacienteId == usuario.id) return true;
    return false;
  }
  bool canDeleteCita() => usuario.isAdmin;
  bool canViewAllCitas() => usuario.isAdmin || usuario.isOdontologo;
  bool canConfirmCita() => usuario.isAdmin || usuario.isOdontologo;

  // ============================================
  // PERMISOS DE TRATAMIENTOS
  // ============================================

  bool canCreateTreatment() => usuario.isAdmin || usuario.isOdontologo;
  bool canEditTreatment() => usuario.isAdmin || usuario.isOdontologo;
  bool canDeleteTreatment() => usuario.isAdmin;
  bool canViewAllTreatments() => usuario.isAdmin || usuario.isOdontologo;
  bool canApproveTreatmentPlan() => usuario.isAdmin || usuario.isOdontologo;

  // ============================================
  // PERMISOS DE INVENTARIO
  // ============================================

  bool canManageInventory() => usuario.isAdmin;
  bool canViewInventory() => usuario.isAdmin || usuario.isOdontologo;
  bool canRequestMaterials() => usuario.isOdontologo;

  // ============================================
  // PERMISOS DE FACTURACIÓN
  // ============================================

  bool canCreateInvoice() => usuario.isAdmin;
  bool canViewAllInvoices() => usuario.isAdmin;
  bool canViewOwnInvoices() => true;
  bool canProcessPayment() => usuario.isAdmin;

  // ============================================
  // PERMISOS DE REPORTES
  // ============================================

  bool canViewReports() => usuario.isAdmin || usuario.isOdontologo;
  bool canViewFinancialReports() => usuario.isAdmin;
  bool canExportReports() => usuario.isAdmin;

  // ============================================
  // PERMISOS DE HISTORIAL CLÍNICO
  // ============================================

  bool canViewClinicalHistory(int pacienteId) {
    if (usuario.isAdmin) return true;
    if (usuario.isOdontologo) return true;
    if (usuario.isPaciente && usuario.id == pacienteId) return true;
    return false;
  }
  bool canEditClinicalHistory() => usuario.isOdontologo || usuario.isAdmin;
  bool canDeleteClinicalHistory() => usuario.isAdmin;

  // ============================================
  // PERMISOS DE CONFIGURACIÓN
  // ============================================

  bool canAccessSettings() => usuario.isAdmin;
  bool canManageBackups() => usuario.isAdmin;
  bool canManageClinics() => usuario.isAdmin;

  // ============================================
  // MÉTODO GENÉRICO DE VERIFICACIÓN
  // ============================================

  bool hasPermission(String permission) {
    final permissionMap = {
      // Usuarios
      'user:create': canCreateUser(),
      'user:delete': canDeleteUser(),
      'user:view_all': canViewAllUsers(),
      
      // Citas
      'cita:create': canCreateCita(),
      'cita:delete': canDeleteCita(),
      'cita:view_all': canViewAllCitas(),
      'cita:confirm': canConfirmCita(),
      
      // Tratamientos
      'treatment:create': canCreateTreatment(),
      'treatment:edit': canEditTreatment(),
      'treatment:delete': canDeleteTreatment(),
      'treatment:approve': canApproveTreatmentPlan(),
      
      // Inventario
      'inventory:manage': canManageInventory(),
      'inventory:view': canViewInventory(),
      'inventory:request': canRequestMaterials(),
      
      // Facturación
      'invoice:create': canCreateInvoice(),
      'invoice:view_all': canViewAllInvoices(),
      'payment:process': canProcessPayment(),
      
      // Reportes
      'report:view': canViewReports(),
      'report:financial': canViewFinancialReports(),
      'report:export': canExportReports(),
      
      // Configuración
      'settings:access': canAccessSettings(),
      'backups:manage': canManageBackups(),
      'clinics:manage': canManageClinics(),
    };

    return permissionMap[permission] ?? false;
  }
}
```

---

## 5. IMPLEMENTACIÓN PRÁCTICA {#implementacion}

### 🔄 Auth Context (Provider)

```dart
// ============================================
// CONTEXT DE AUTENTICACIÓN CON PROVIDER
// ============================================

class AuthContext with ChangeNotifier {
  final AuthService _authService;
  final SecureStorageService _storage;

  Usuario? _currentUser;
  String? _accessToken;
  String? _refreshToken;
  bool _isAuthenticated = false;
  PermissionManager? _permissionManager;

  // Getters
  Usuario? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;
  TipoUsuario? get userType => _currentUser?.tipo;
  PermissionManager? get permissions => _permissionManager;

  // Getters de roles
  bool get isAdmin => _currentUser?.isAdmin ?? false;
  bool get isOdontologo => _currentUser?.isOdontologo ?? false;
  bool get isPaciente => _currentUser?.isPaciente ?? false;

  AuthContext({
    required AuthService authService,
    required SecureStorageService storage,
  })  : _authService = authService,
        _storage = storage;

  // ============================================
  // INICIALIZAR - VERIFICAR SESIÓN EXISTENTE
  // ============================================

  Future<void> initialize() async {
    try {
      print('🔄 Inicializando AuthContext...');
      
      // Cargar tokens guardados
      _accessToken = await _storage.getAccessToken();
      _refreshToken = await _storage.getRefreshToken();

      if (_accessToken != null) {
        print('✅ Token encontrado, validando...');
        
        // Obtener datos del usuario
        final userData = await _authService.getCurrentUser(_accessToken!);
        
        if (userData != null) {
          _currentUser = Usuario.fromJson(userData);
          _isAuthenticated = true;
          _permissionManager = PermissionManager(_currentUser!);
          
          print('✅ Sesión restaurada para: ${_currentUser!.email}');
          print('👤 Rol: ${_currentUser!.tipo.displayName}');
        } else {
          // Token inválido, intentar refrescar
          await _tryRefreshToken();
        }
      } else {
        print('ℹ️ No hay sesión activa');
      }
      
      notifyListeners();
    } catch (e) {
      print('❌ Error al inicializar AuthContext: $e');
      await logout();
    }
  }

  // ============================================
  // LOGIN
  // ============================================

  Future<bool> login({
    required String email,
    required String password,
    required String clinicaDominio,
  }) async {
    try {
      print('🔐 Intentando login...');
      
      final result = await _authService.login(
        email: email,
        password: password,
        clinicaDominio: clinicaDominio,
      );

      if (result['success'] == true) {
        _accessToken = result['access_token'];
        _refreshToken = result['refresh_token'];
        _currentUser = Usuario.fromJson(result['user']);
        _isAuthenticated = true;
        _permissionManager = PermissionManager(_currentUser!);

        // Guardar tokens
        await _storage.saveAccessToken(_accessToken!);
        await _storage.saveRefreshToken(_refreshToken!);
        await _storage.saveUser(_currentUser!.toJson());

        print('✅ Login exitoso');
        print('👤 Usuario: ${_currentUser!.email}');
        print('🎭 Rol: ${_currentUser!.tipo.displayName}');

        notifyListeners();
        return true;
      } else {
        print('❌ Login fallido: ${result['error']}');
        return false;
      }
    } catch (e) {
      print('❌ Error en login: $e');
      return false;
    }
  }

  // ============================================
  // LOGOUT
  // ============================================

  Future<void> logout() async {
    try {
      print('👋 Cerrando sesión...');
      
      if (_accessToken != null) {
        await _authService.logout(_accessToken!);
      }

      _currentUser = null;
      _accessToken = null;
      _refreshToken = null;
      _isAuthenticated = false;
      _permissionManager = null;

      await _storage.clearAll();

      print('✅ Sesión cerrada');
      notifyListeners();
    } catch (e) {
      print('Error al cerrar sesión: $e');
    }
  }

  // ============================================
  // REFRESCAR TOKEN
  // ============================================

  Future<bool> _tryRefreshToken() async {
    try {
      if (_refreshToken == null) return false;

      print('🔄 Intentando refrescar token...');
      
      final newAccessToken = await _authService.refreshToken(_refreshToken!);
      
      if (newAccessToken != null) {
        _accessToken = newAccessToken;
        await _storage.saveAccessToken(newAccessToken);
        
        print('✅ Token refrescado exitosamente');
        return true;
      } else {
        print('❌ No se pudo refrescar el token');
        await logout();
        return false;
      }
    } catch (e) {
      print('Error al refrescar token: $e');
      await logout();
      return false;
    }
  }

  // ============================================
  // VERIFICAR PERMISOS
  // ============================================

  bool hasPermission(String permission) {
    return _permissionManager?.hasPermission(permission) ?? false;
  }

  bool canAccess(String route) {
    if (!_isAuthenticated) return false;

    final routePermissions = {
      '/admin/users': 'user:view_all',
      '/admin/settings': 'settings:access',
      '/admin/backups': 'backups:manage',
      '/reportes': 'report:view',
      '/reportes/financiero': 'report:financial',
      '/inventario': 'inventory:view',
      '/tratamientos/crear': 'treatment:create',
      '/citas/crear': 'cita:create',
    };

    final requiredPermission = routePermissions[route];
    if (requiredPermission == null) return true; // Ruta pública

    return hasPermission(requiredPermission);
  }
}
```

---

## 6. PROTECCIÓN DE RUTAS {#proteccion-rutas}

### 🛡️ Route Guards

```dart
// ============================================
// GUARD GENÉRICO PARA PROTEGER RUTAS
// ============================================

class AuthGuard extends StatelessWidget {
  final Widget child;
  final List<TipoUsuario>? allowedRoles;
  final String? requiredPermission;
  final Widget? fallback;

  const AuthGuard({
    Key? key,
    required this.child,
    this.allowedRoles,
    this.requiredPermission,
    this.fallback,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authContext = context.watch<AuthContext>();

    // Verificar autenticación
    if (!authContext.isAuthenticated) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pushReplacementNamed('/login');
      });
      return Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    // Verificar roles
    if (allowedRoles != null && authContext.currentUser != null) {
      if (!allowedRoles!.contains(authContext.currentUser!.tipo)) {
        return fallback ?? _buildAccessDenied(context);
      }
    }

    // Verificar permiso específico
    if (requiredPermission != null) {
      if (!authContext.hasPermission(requiredPermission!)) {
        return fallback ?? _buildAccessDenied(context);
      }
    }

    return child;
  }

  Widget _buildAccessDenied(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Acceso Denegado')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.block, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(
              'No tienes permisos para acceder a esta sección',
              style: Theme.of(context).textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('Volver'),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================
// EJEMPLO DE USO EN RUTAS
// ============================================

MaterialApp(
  routes: {
    '/': (context) => AuthGuard(
      child: HomeScreen(),
    ),
    
    '/admin/users': (context) => AuthGuard(
      allowedRoles: [TipoUsuario.admin],
      child: UsersManagementScreen(),
    ),
    
    '/reportes': (context) => AuthGuard(
      allowedRoles: [TipoUsuario.admin, TipoUsuario.odontologo],
      child: ReportesScreen(),
    ),
    
    '/mi-perfil': (context) => AuthGuard(
      child: ProfileScreen(),
    ),
    
    '/tratamientos/crear': (context) => AuthGuard(
      requiredPermission: 'treatment:create',
      child: CreateTreatmentScreen(),
    ),
  },
);
```

### 🔀 Router Dinámico por Rol

```dart
// ============================================
// ROUTER QUE REDIRIGE SEGÚN ROL
// ============================================

class RoleBasedRouter {
  static String getHomeRoute(Usuario usuario) {
    switch (usuario.tipo) {
      case TipoUsuario.admin:
        return '/admin/dashboard';
      case TipoUsuario.odontologo:
        return '/doctor/dashboard';
      case TipoUsuario.paciente:
        return '/patient/dashboard';
      default:
        return '/';
    }
  }

  static List<NavigationDestination> getNavigationItems(Usuario usuario) {
    if (usuario.isAdmin) {
      return [
        NavigationDestination(
          icon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        NavigationDestination(
          icon: Icon(Icons.people),
          label: 'Usuarios',
        ),
        NavigationDestination(
          icon: Icon(Icons.calendar_today),
          label: 'Citas',
        ),
        NavigationDestination(
          icon: Icon(Icons.inventory),
          label: 'Inventario',
        ),
        NavigationDestination(
          icon: Icon(Icons.attach_money),
          label: 'Facturación',
        ),
        NavigationDestination(
          icon: Icon(Icons.bar_chart),
          label: 'Reportes',
        ),
        NavigationDestination(
          icon: Icon(Icons.settings),
          label: 'Configuración',
        ),
      ];
    } else if (usuario.isOdontologo) {
      return [
        NavigationDestination(
          icon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        NavigationDestination(
          icon: Icon(Icons.calendar_today),
          label: 'Mi Agenda',
        ),
        NavigationDestination(
          icon: Icon(Icons.people),
          label: 'Pacientes',
        ),
        NavigationDestination(
          icon: Icon(Icons.medical_services),
          label: 'Tratamientos',
        ),
        NavigationDestination(
          icon: Icon(Icons.bar_chart),
          label: 'Reportes',
        ),
      ];
    } else if (usuario.isPaciente) {
      return [
        NavigationDestination(
          icon: Icon(Icons.home),
          label: 'Inicio',
        ),
        NavigationDestination(
          icon: Icon(Icons.calendar_today),
          label: 'Mis Citas',
        ),
        NavigationDestination(
          icon: Icon(Icons.medical_services),
          label: 'Tratamientos',
        ),
        NavigationDestination(
          icon: Icon(Icons.receipt),
          label: 'Facturas',
        ),
        NavigationDestination(
          icon: Icon(Icons.person),
          label: 'Mi Perfil',
        ),
      ];
    }
    return [];
  }
}
```

---

## 7. MANEJO DE TOKENS {#manejo-tokens}

### 💾 Secure Storage

```dart
// ============================================
// ALMACENAMIENTO SEGURO DE TOKENS
// ============================================

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  final FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );

  // Claves
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userKey = 'user_data';
  static const String _clinicaKey = 'clinica_dominio';

  // ============================================
  // TOKENS
  // ============================================

  Future<void> saveAccessToken(String token) async {
    await _storage.write(key: _accessTokenKey, value: token);
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: _accessTokenKey);
  }

  Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  // ============================================
  // USUARIO
  // ============================================

  Future<void> saveUser(Map<String, dynamic> userData) async {
    await _storage.write(
      key: _userKey,
      value: jsonEncode(userData),
    );
  }

  Future<Map<String, dynamic>?> getUser() async {
    final data = await _storage.read(key: _userKey);
    if (data != null) {
      return jsonDecode(data);
    }
    return null;
  }

  // ============================================
  // CLÍNICA
  // ============================================

  Future<void> saveClinica(String dominio) async {
    await _storage.write(key: _clinicaKey, value: dominio);
  }

  Future<String?> getClinica() async {
    return await _storage.read(key: _clinicaKey);
  }

  // ============================================
  // LIMPIAR TODO
  // ============================================

  Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
```

### 🔄 Interceptor para Auto-refresh

```dart
// ============================================
// INTERCEPTOR PARA MANEJAR TOKENS AUTOMÁTICAMENTE
// ============================================

class AuthInterceptor extends Interceptor {
  final AuthContext authContext;

  AuthInterceptor(this.authContext);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Agregar token a todas las requests
    final token = authContext._accessToken;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    
    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Si el error es 401 (Unauthorized)
    if (err.response?.statusCode == 401) {
      print('🔄 Token expirado, intentando refrescar...');
      
      // Intentar refrescar el token
      final refreshed = await authContext._tryRefreshToken();
      
      if (refreshed) {
        // Reintentar la request original
        final options = err.requestOptions;
        options.headers['Authorization'] = 
          'Bearer ${authContext._accessToken}';
        
        try {
          final response = await Dio().fetch(options);
          return handler.resolve(response);
        } catch (e) {
          return handler.next(err);
        }
      } else {
        // No se pudo refrescar, cerrar sesión
        await authContext.logout();
      }
    }
    
    handler.next(err);
  }
}

// ============================================
// CONFIGURAR INTERCEPTOR
// ============================================

Dio createDioWithAuth(AuthContext authContext) {
  final dio = Dio(BaseOptions(
    baseUrl: 'https://clinica-dental-backend.onrender.com',
    connectTimeout: Duration(seconds: 30),
    receiveTimeout: Duration(seconds: 30),
  ));

  dio.interceptors.add(AuthInterceptor(authContext));
  
  return dio;
}
```

---

## 8. BEST PRACTICES {#best-practices}

### ✅ Mejores Prácticas

```dart
// ============================================
// 1. SIEMPRE VERIFICAR AUTENTICACIÓN ANTES DE USAR DATOS
// ============================================

// ❌ MAL
Widget build(BuildContext context) {
  final user = context.read<AuthContext>().currentUser;
  return Text(user!.email); // Puede crashear si user es null
}

// ✅ BIEN
Widget build(BuildContext context) {
  final authContext = context.watch<AuthContext>();
  
  if (!authContext.isAuthenticated || authContext.currentUser == null) {
    return CircularProgressIndicator();
  }
  
  return Text(authContext.currentUser!.email);
}

// ============================================
// 2. USAR GUARDS EN TODAS LAS RUTAS PROTEGIDAS
// ============================================

// ❌ MAL
'/admin/users': (context) => UsersScreen(),

// ✅ BIEN
'/admin/users': (context) => AuthGuard(
  allowedRoles: [TipoUsuario.admin],
  child: UsersScreen(),
),

// ============================================
// 3. MOSTRAR UI CONDICIONAL SEGÚN PERMISOS
// ============================================

Widget build(BuildContext context) {
  final authContext = context.watch<AuthContext>();
  
  return Column(
    children: [
      // Visible para todos
      Text('Bienvenido ${authContext.currentUser?.nombreCompleto}'),
      
      // Solo para admins
      if (authContext.hasPermission('user:create'))
        ElevatedButton(
          onPressed: () => Navigator.pushNamed(context, '/users/create'),
          child: Text('Crear Usuario'),
        ),
      
      // Solo para odontólogos y admins
      if (authContext.hasPermission('report:view'))
        ListTile(
          title: Text('Ver Reportes'),
          onTap: () => Navigator.pushNamed(context, '/reportes'),
        ),
    ],
  );
}

// ============================================
// 4. MANEJAR ERRORES DE AUTENTICACIÓN GRACEFULLY
// ============================================

Future<void> fetchData() async {
  try {
    final response = await apiClient.get('/api/data/');
    // Procesar datos
  } on DioException catch (e) {
    if (e.response?.statusCode == 401) {
      // Token expirado o inválido
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Sesión Expirada'),
          content: Text('Por favor, inicie sesión nuevamente'),
          actions: [
            TextButton(
              onPressed: () {
                context.read<AuthContext>().logout();
                Navigator.pushReplacementNamed(context, '/login');
              },
              child: Text('OK'),
            ),
          ],
        ),
      );
    } else if (e.response?.statusCode == 403) {
      // Sin permisos
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No tienes permisos para esta acción')),
      );
    }
  }
}

// ============================================
// 5. LOGOUT CON CONFIRMACIÓN
// ============================================

Future<void> _handleLogout(BuildContext context) async {
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('Cerrar Sesión'),
      content: Text('¿Estás seguro que deseas cerrar sesión?'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: Text('Cancelar'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, true),
          child: Text('Cerrar Sesión'),
        ),
      ],
    ),
  );

  if (confirmed == true) {
    await context.read<AuthContext>().logout();
    Navigator.pushReplacementNamed(context, '/login');
  }
}

// ============================================
// 6. PERSISTIR ÚLTIMA CLÍNICA SELECCIONADA
// ============================================

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  String? _selectedClinica;

  @override
  void initState() {
    super.initState();
    _loadLastClinica();
  }

  Future<void> _loadLastClinica() async {
    final storage = SecureStorageService();
    final lastClinica = await storage.getClinica();
    if (lastClinica != null && mounted) {
      setState(() => _selectedClinica = lastClinica);
    }
  }

  Future<void> _handleLogin() async {
    // ... login logic ...
    
    // Guardar clínica seleccionada
    if (_selectedClinica != null) {
      await SecureStorageService().saveClinica(_selectedClinica!);
    }
  }
}

// ============================================
// 7. WIDGET CONDICIONAL POR ROL
// ============================================

class RoleBasedWidget extends StatelessWidget {
  final Widget? adminWidget;
  final Widget? odontologoWidget;
  final Widget? pacienteWidget;
  final Widget? fallback;

  const RoleBasedWidget({
    Key? key,
    this.adminWidget,
    this.odontologoWidget,
    this.pacienteWidget,
    this.fallback,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthContext>().currentUser;

    if (user == null) return fallback ?? SizedBox.shrink();

    switch (user.tipo) {
      case TipoUsuario.admin:
        return adminWidget ?? fallback ?? SizedBox.shrink();
      case TipoUsuario.odontologo:
        return odontologoWidget ?? fallback ?? SizedBox.shrink();
      case TipoUsuario.paciente:
        return pacienteWidget ?? fallback ?? SizedBox.shrink();
      default:
        return fallback ?? SizedBox.shrink();
    }
  }
}

// Uso:
RoleBasedWidget(
  adminWidget: AdminDashboard(),
  odontologoWidget: DoctorDashboard(),
  pacienteWidget: PatientDashboard(),
)
```

---

## 📊 DIAGRAMA DE FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│                      APP FLUTTER                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │    ¿Usuario Autenticado?        │
        └─────────────────────────────────┘
                 │                 │
                NO                YES
                 │                 │
                 ▼                 ▼
        ┌──────────────┐   ┌──────────────────┐
        │ Login Screen │   │ Home (Por Rol)   │
        └──────────────┘   └──────────────────┘
                 │                 │
                 ▼                 ▼
        ┌──────────────┐   ┌──────────────────────────────┐
        │ Auth Service │   │  ADMIN    DOCTOR   PACIENTE  │
        └──────────────┘   │   │         │         │       │
                 │         │   ▼         ▼         ▼       │
                 ▼         │ Admin   Doctor   Patient     │
        ┌──────────────┐   │ View    View     View        │
        │ Get /me/     │   └──────────────────────────────┘
        └──────────────┘            │
                 │                  ▼
                 ▼         ┌─────────────────────┐
        ┌──────────────┐   │ Permission Manager  │
        │ Save Tokens  │   │  - canCreate?       │
        │ & User Data  │   │  - canEdit?         │
        └──────────────┘   │  - canDelete?       │
                 │         │  - canView?         │
                 ▼         └─────────────────────┘
        ┌──────────────┐            │
        │ Navigate to  │            ▼
        │ Role Home    │   ┌─────────────────────┐
        └──────────────┘   │   Protected Routes  │
                           │   with AuthGuard    │
                           └─────────────────────┘
```

---

## 🎯 CHECKLIST DE IMPLEMENTACIÓN

```markdown
### Backend (Ya implementado)
- [✅] Endpoint /api/token/ (JWT)
- [✅] Endpoint /api/token/refresh/
- [✅] Endpoint /api/usuarios/me/
- [✅] Tipos de usuario: ADMIN, ODONTOLOGO, PACIENTE
- [✅] Perfiles: PerfilPaciente, PerfilOdontologo
- [✅] Permisos por rol en cada endpoint

### Flutter (Por implementar)
- [ ] Modelo Usuario
- [ ] Modelo PerfilPaciente
- [ ] Modelo PerfilOdontologo
- [ ] Enum TipoUsuario
- [ ] AuthService
- [ ] SecureStorageService
- [ ] AuthContext (Provider)
- [ ] PermissionManager
- [ ] LoginScreen
- [ ] AuthGuard
- [ ] RoleBasedRouter
- [ ] Interceptor para auto-refresh
- [ ] Manejo de errores 401/403
- [ ] UI condicional por roles
- [ ] Logout con confirmación
```

---

## 📚 RESUMEN DE CREDENCIALES DE PRUEBA

```dart
// Según CREDENCIALES.md

const testCredentials = {
  'admin': {
    'email': 'admin@clinicademo1.com',
    'password': 'admin123',
    'tipo': 'ADMIN',
  },
  'odontologo': {
    'email': 'odontologo@clinica-demo.com',
    'password': 'odontologo123',
    'tipo': 'ODONTOLOGO',
  },
  'paciente': {
    'email': 'paciente1@test.com',
    'password': 'paciente123',
    'tipo': 'PACIENTE',
  },
};

const clinica = {
  'dominio': 'clinicademo1',
  'nombre': 'Clínica Demo',
};
```

---

## 🔗 ENDPOINTS IMPORTANTES

```dart
// Base URL
const BASE_URL = 'https://clinica-dental-backend.onrender.com';

// Autenticación
POST   /api/token/                    // Login
POST   /api/token/refresh/            // Refresh token
GET    /api/usuarios/me/              // Usuario actual
POST   /api/usuarios/registrar-fcm-token/  // FCM token

// Multi-tenant
GET    /api/tenants/                  // Lista de clínicas

// Headers importantes
headers: {
  'X-Tenant': 'clinicademo1',         // Seleccionar clínica
  'Authorization': 'Bearer <token>',   // Autenticación
}
```

---

¡Con esta guía tienes todo lo necesario para implementar un sistema completo de autenticación, roles y permisos en Flutter! 🚀
