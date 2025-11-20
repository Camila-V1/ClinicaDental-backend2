# 🔄 State Management Avanzado

## 🎯 Objetivo
Implementar patrones avanzados de Provider para gestión de estado escalable.

---

## 📦 Providers Completos

### `lib/providers/clinica_provider.dart` (Completo)

```dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clinica_dental_app/models/clinica.dart';
import 'package:clinica_dental_app/config/constants.dart';

class ClinicaProvider with ChangeNotifier {
  Clinica? _clinicaSeleccionada;
  List<Clinica> _clinicasDisponibles = [];
  bool _isLoading = false;
  String? _error;

  // Getters
  Clinica? get clinicaSeleccionada => _clinicaSeleccionada;
  List<Clinica> get clinicasDisponibles => _clinicasDisponibles;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasClinica => _clinicaSeleccionada != null;

  // Seleccionar clínica
  Future<void> seleccionarClinica(Clinica clinica) async {
    _clinicaSeleccionada = clinica;
    
    // Guardar en SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyClinicaId, clinica.id);
    await prefs.setString(AppConstants.keyClinicaNombre, clinica.nombre);
    
    notifyListeners();
  }

  // Cargar clínica guardada
  Future<void> cargarClinicaGuardada() async {
    final prefs = await SharedPreferences.getInstance();
    final clinicaId = prefs.getString(AppConstants.keyClinicaId);
    final clinicaNombre = prefs.getString(AppConstants.keyClinicaNombre);

    if (clinicaId != null && clinicaNombre != null) {
      _clinicaSeleccionada = Clinica(
        id: clinicaId,
        nombre: clinicaNombre,
        logo: null,
        direccion: null,
        telefono: null,
        descripcion: null,
      );
      notifyListeners();
    }
  }

  // Limpiar clínica
  Future<void> limpiarClinica() async {
    _clinicaSeleccionada = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.keyClinicaId);
    await prefs.remove(AppConstants.keyClinicaNombre);
    
    notifyListeners();
  }

  // Cargar clínicas disponibles
  Future<void> cargarClinicas(List<Clinica> clinicas) async {
    _clinicasDisponibles = clinicas;
    notifyListeners();
  }

  // Estado de carga
  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Error
  void setError(String? error) {
    _error = error;
    notifyListeners();
  }
}
```

---

### `lib/providers/auth_provider.dart` (Completo)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:clinica_dental_app/models/usuario.dart';
import 'package:clinica_dental_app/services/auth_service.dart';
import 'package:clinica_dental_app/config/constants.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Usuario? _usuario;
  String? _accessToken;
  String? _refreshToken;
  bool _isLoading = false;
  String? _error;

  // Getters
  Usuario? get usuario => _usuario;
  String? get accessToken => _accessToken;
  String? get refreshToken => _refreshToken;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _accessToken != null && _usuario != null;

  // Login
  Future<bool> login(String email, String password) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _authService.login(
        email: email,
        password: password,
      );

      await _guardarSesion(response);
      
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Registro
  Future<bool> registro({
    required String email,
    required String password,
    required String fullName,
    String? telefono,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _authService.registro(
        email: email,
        password: password,
        fullName: fullName,
        telefono: telefono,
      );

      await _guardarSesion(response);
      
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Cargar sesión guardada
  Future<bool> cargarSesion() async {
    try {
      final token = await _storage.read(key: AppConstants.keyAccessToken);
      final refresh = await _storage.read(key: AppConstants.keyRefreshToken);
      final usuarioJson = await _storage.read(key: AppConstants.keyUsuario);

      if (token != null && refresh != null && usuarioJson != null) {
        _accessToken = token;
        _refreshToken = refresh;
        _usuario = Usuario.fromJson(usuarioJson as Map<String, dynamic>);
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Renovar token
  Future<bool> renovarToken() async {
    try {
      if (_refreshToken == null) return false;

      final response = await _authService.refreshToken(_refreshToken!);
      
      _accessToken = response.accessToken;
      await _storage.write(
        key: AppConstants.keyAccessToken,
        value: response.accessToken,
      );
      
      notifyListeners();
      return true;
    } catch (e) {
      await logout();
      return false;
    }
  }

  // Logout
  Future<void> logout() async {
    _usuario = null;
    _accessToken = null;
    _refreshToken = null;

    await _storage.delete(key: AppConstants.keyAccessToken);
    await _storage.delete(key: AppConstants.keyRefreshToken);
    await _storage.delete(key: AppConstants.keyUsuario);

    notifyListeners();
  }

  // Guardar sesión
  Future<void> _guardarSesion(AuthResponse response) async {
    _usuario = response.usuario;
    _accessToken = response.accessToken;
    _refreshToken = response.refreshToken;

    await _storage.write(
      key: AppConstants.keyAccessToken,
      value: response.accessToken,
    );
    await _storage.write(
      key: AppConstants.keyRefreshToken,
      value: response.refreshToken,
    );
    await _storage.write(
      key: AppConstants.keyUsuario,
      value: response.usuario.toJson().toString(),
    );
  }

  // Limpiar error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
```

---

## 🎯 Provider de Citas

### `lib/providers/citas_provider.dart`

```dart
import 'package:flutter/material.dart';
import 'package:clinica_dental_app/models/cita.dart';
import 'package:clinica_dental_app/services/citas_service.dart';

class CitasProvider with ChangeNotifier {
  final CitasService _service = CitasService();
  
  List<CitaDetallada> _citas = [];
  CitaDetallada? _citaSeleccionada;
  bool _isLoading = false;
  String? _error;

  // Getters
  List<CitaDetallada> get citas => _citas;
  List<CitaDetallada> get citasProximas =>
      _citas.where((c) => c.fechaHora.isAfter(DateTime.now())).toList();
  List<CitaDetallada> get citasPasadas =>
      _citas.where((c) => c.fechaHora.isBefore(DateTime.now())).toList();
  CitaDetallada? get citaSeleccionada => _citaSeleccionada;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Cargar citas
  Future<void> cargarCitas({
    required String token,
    required String tenantId,
    bool forceRefresh = false,
  }) async {
    if (_isLoading) return;
    if (!forceRefresh && _citas.isNotEmpty) return;

    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final citas = await _service.getMisCitas(
        token: token,
        tenantId: tenantId,
      );

      _citas = citas;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  // Seleccionar cita
  void seleccionarCita(CitaDetallada cita) {
    _citaSeleccionada = cita;
    notifyListeners();
  }

  // Cancelar cita
  Future<bool> cancelarCita({
    required String token,
    required String tenantId,
    required int citaId,
    String? motivo,
  }) async {
    try {
      await _service.cancelarCita(
        token: token,
        tenantId: tenantId,
        citaId: citaId,
        motivo: motivo,
      );

      // Actualizar lista local
      _citas = _citas.map((c) {
        if (c.id == citaId) {
          return CitaDetallada(
            id: c.id,
            fechaHora: c.fechaHora,
            duracionMinutos: c.duracionMinutos,
            motivo: c.motivo,
            estado: 'CANCELADA',
            notas: motivo,
            odontologo: c.odontologo,
          );
        }
        return c;
      }).toList();

      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  // Limpiar
  void clear() {
    _citas = [];
    _citaSeleccionada = null;
    _error = null;
    notifyListeners();
  }
}
```

---

## 🎯 Provider de Notificaciones

### `lib/providers/notificaciones_provider.dart`

```dart
import 'package:flutter/material.dart';

class NotificacionesProvider with ChangeNotifier {
  List<Notificacion> _notificaciones = [];
  int _noLeidas = 0;
  bool _pushEnabled = true;
  bool _emailEnabled = true;

  // Getters
  List<Notificacion> get notificaciones => _notificaciones;
  List<Notificacion> get noLeidas =>
      _notificaciones.where((n) => !n.leida).toList();
  int get cantidadNoLeidas => _noLeidas;
  bool get pushEnabled => _pushEnabled;
  bool get emailEnabled => _emailEnabled;

  // Agregar notificación
  void agregarNotificacion(Notificacion notificacion) {
    _notificaciones.insert(0, notificacion);
    if (!notificacion.leida) {
      _noLeidas++;
    }
    notifyListeners();
  }

  // Marcar como leída
  void marcarComoLeida(int id) {
    final index = _notificaciones.indexWhere((n) => n.id == id);
    if (index != -1 && !_notificaciones[index].leida) {
      _notificaciones[index] = Notificacion(
        id: _notificaciones[index].id,
        titulo: _notificaciones[index].titulo,
        mensaje: _notificaciones[index].mensaje,
        fecha: _notificaciones[index].fecha,
        leida: true,
        tipo: _notificaciones[index].tipo,
      );
      _noLeidas--;
      notifyListeners();
    }
  }

  // Marcar todas como leídas
  void marcarTodasComoLeidas() {
    _notificaciones = _notificaciones.map((n) {
      return Notificacion(
        id: n.id,
        titulo: n.titulo,
        mensaje: n.mensaje,
        fecha: n.fecha,
        leida: true,
        tipo: n.tipo,
      );
    }).toList();
    _noLeidas = 0;
    notifyListeners();
  }

  // Toggle push
  void togglePush(bool enabled) {
    _pushEnabled = enabled;
    notifyListeners();
    // TODO: Actualizar en backend
  }

  // Toggle email
  void toggleEmail(bool enabled) {
    _emailEnabled = enabled;
    notifyListeners();
    // TODO: Actualizar en backend
  }
}

class Notificacion {
  final int id;
  final String titulo;
  final String mensaje;
  final DateTime fecha;
  final bool leida;
  final String tipo;

  Notificacion({
    required this.id,
    required this.titulo,
    required this.mensaje,
    required this.fecha,
    required this.leida,
    required this.tipo,
  });
}
```

---

## 🎯 Provider de UI/UX

### `lib/providers/ui_provider.dart`

```dart
import 'package:flutter/material.dart';

class UiProvider with ChangeNotifier {
  int _selectedTab = 0;
  bool _isDarkMode = false;
  String _locale = 'es';

  // Getters
  int get selectedTab => _selectedTab;
  bool get isDarkMode => _isDarkMode;
  String get locale => _locale;

  // Cambiar tab
  void setSelectedTab(int index) {
    _selectedTab = index;
    notifyListeners();
  }

  // Toggle dark mode
  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
    // TODO: Guardar en SharedPreferences
  }

  // Cambiar idioma
  void setLocale(String newLocale) {
    _locale = newLocale;
    notifyListeners();
    // TODO: Guardar en SharedPreferences
  }
}
```

---

## 🎯 Combo Provider (Multi-Provider)

### `lib/main.dart` (Configuración completa)

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/providers/citas_provider.dart';
import 'package:clinica_dental_app/providers/notificaciones_provider.dart';
import 'package:clinica_dental_app/providers/ui_provider.dart';
import 'package:clinica_dental_app/config/theme.dart';
import 'package:clinica_dental_app/config/routes.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Auth Provider
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        
        // Clinica Provider
        ChangeNotifierProvider(create: (_) => ClinicaProvider()),
        
        // Citas Provider
        ChangeNotifierProvider(create: (_) => CitasProvider()),
        
        // Notificaciones Provider
        ChangeNotifierProvider(create: (_) => NotificacionesProvider()),
        
        // UI Provider
        ChangeNotifierProvider(create: (_) => UiProvider()),
      ],
      child: Consumer<UiProvider>(
        builder: (context, uiProvider, child) {
          return MaterialApp.router(
            title: 'Clínica Dental',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: uiProvider.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            routerConfig: AppRouter.router,
          );
        },
      ),
    );
  }
}
```

---

## 🎯 Uso en Widgets

### Ejemplo: Consumir múltiples providers

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/citas_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';

class MiWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Opción 1: Consumer múltiple
    return Consumer3<AuthProvider, ClinicaProvider, CitasProvider>(
      builder: (context, auth, clinica, citas, child) {
        return Column(
          children: [
            Text('Usuario: ${auth.usuario?.fullName}'),
            Text('Clínica: ${clinica.clinicaSeleccionada?.nombre}'),
            Text('Citas: ${citas.citas.length}'),
          ],
        );
      },
    );

    // Opción 2: Provider.of
    final auth = Provider.of<AuthProvider>(context);
    final clinica = Provider.of<ClinicaProvider>(context);
    final citas = Provider.of<CitasProvider>(context);

    // Opción 3: context.watch/read
    final auth = context.watch<AuthProvider>();
    final clinica = context.read<ClinicaProvider>(); // No reconstruye
  }
}
```

---

## ✅ Checklist

- [ ] Implementar `ClinicaProvider` completo
- [ ] Implementar `AuthProvider` completo
- [ ] Crear `CitasProvider`
- [ ] Crear `NotificacionesProvider`
- [ ] Crear `UiProvider`
- [ ] Configurar MultiProvider en main.dart
- [ ] Migrar widgets a usar providers
- [ ] Testing de providers

---

**Completado:** Todas las guías de Flutter creadas ✅
