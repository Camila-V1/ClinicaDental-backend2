# 📱 Guía 02a - Selector de Clínicas y Conexión al Backend

> **⚠️ GUÍA NUEVA** - 22/11/2025  
> Esta guía complementa las anteriores explicando cómo conectarse al backend de Render y seleccionar clínicas.

## 🎯 Objetivos

1. Configurar la conexión al backend de producción (Render)
2. Implementar el selector de clínicas disponibles
3. Gestionar el almacenamiento de la clínica seleccionada
4. Preparar los headers correctos para todas las peticiones

---

## 🌐 Configuración del Backend

### 1. URLs del Backend

El backend está desplegado en **Render** y soporta múltiples clínicas (multi-tenant):

```dart
// lib/core/api/endpoints.dart

class ApiConfig {
  // Backend de Producción (Render)
  static const String prodUrl = 'https://clinica-dental-backend.onrender.com';
  
  // Backend de Desarrollo (Local)
  static const String devUrl = 'http://localhost:8000';  // iOS Simulator
  static const String devUrlAndroid = 'http://10.0.2.2:8000';  // Android Emulator
  
  // URL activa según el entorno
  static String get baseUrl {
    // Cambiar a true para usar producción
    const bool useProduction = true;
    
    if (useProduction) {
      return prodUrl;
    } else {
      // Detectar si es Android o iOS
      return Platform.isAndroid ? devUrlAndroid : devUrl;
    }
  }
  
  // Endpoints públicos (sin tenant)
  static const String planesDisponibles = '/api/tenants/planes/';
  static const String infoRegistro = '/api/tenants/info-registro/';
  static const String solicitudRegistro = '/api/tenants/solicitudes/';
  
  // Endpoints de autenticación (con tenant)
  static const String login = '/api/token/';
  static const String refresh = '/api/token/refresh/';
  static const String register = '/api/usuarios/register/';
  static const String userMe = '/api/usuarios/me/';
  
  // Endpoints de citas (con tenant)
  static const String citas = '/api/agenda/citas/';
  static const String citasProximas = '/api/agenda/citas/proximas/';
  static const String citasHoy = '/api/agenda/citas/hoy/';
  
  // Endpoints de tratamientos (con tenant)
  static const String tratamientos = '/api/tratamientos/planes-tratamiento/';
  
  // Endpoints de facturas (con tenant)
  static const String facturas = '/api/facturacion/facturas/';
  
  // Endpoints de historial (con tenant)
  static const String historialClinico = '/api/historial/historiales/';
}
```

### 2. Clínicas Disponibles

En el backend actual hay **una clínica demo** configurada:

```dart
// lib/core/api/clinicas_disponibles.dart

class ClinicaDisponible {
  final String id;
  final String nombre;
  final String dominio;  // Usado en el header Host
  final String descripcion;
  final String logoUrl;
  final String telefono;
  final String direccion;
  
  const ClinicaDisponible({
    required this.id,
    required this.nombre,
    required this.dominio,
    required this.descripcion,
    this.logoUrl = '',
    this.telefono = '',
    this.direccion = '',
  });
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'dominio': dominio,
      'descripcion': descripcion,
      'logoUrl': logoUrl,
      'telefono': telefono,
      'direccion': direccion,
    };
  }
  
  factory ClinicaDisponible.fromJson(Map<String, dynamic> json) {
    return ClinicaDisponible(
      id: json['id'].toString(),
      nombre: json['nombre'] ?? '',
      dominio: json['dominio'] ?? '',
      descripcion: json['descripcion'] ?? '',
      logoUrl: json['logoUrl'] ?? '',
      telefono: json['telefono'] ?? '',
      direccion: json['direccion'] ?? '',
    );
  }
}

// Clínicas disponibles en el sistema
class ClinicasDisponibles {
  static const List<ClinicaDisponible> clinicas = [
    ClinicaDisponible(
      id: '1',
      nombre: 'Clínica Demo',
      dominio: 'clinica_demo',  // ⚠️ IMPORTANTE: Sin guiones en el schema
      descripcion: 'Clínica dental de demostración',
      telefono: '+591 XXXX-XXXX',
      direccion: 'Dirección de ejemplo',
    ),
    // Agregar más clínicas aquí cuando estén disponibles
  ];
  
  static ClinicaDisponible? getByDominio(String dominio) {
    try {
      return clinicas.firstWhere((c) => c.dominio == dominio);
    } catch (e) {
      return null;
    }
  }
}
```

---

## 🏥 Selector de Clínicas

### 1. Modelo de Clínica

Ya definido arriba en `ClinicaDisponible`.

### 2. Servicio de Clínicas

```dart
// lib/services/clinica_service.dart

import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/api/endpoints.dart';
import '../core/api/clinicas_disponibles.dart';

class ClinicaService {
  /// Obtener clínicas disponibles
  /// En esta versión, retorna las clínicas hardcodeadas.
  /// En el futuro, podría consultar un endpoint público del backend.
  Future<List<ClinicaDisponible>> getClinicasDisponibles() async {
    // Simular delay de red
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Retornar clínicas hardcodeadas
    return ClinicasDisponibles.clinicas;
    
    /* ALTERNATIVA: Consultar endpoint público del backend
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/api/tenants/clinicas-publicas/'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => ClinicaDisponible.fromJson(json)).toList();
      }
      
      throw Exception('Error al cargar clínicas');
    } catch (e) {
      print('Error: $e');
      // Fallback a clínicas hardcodeadas
      return ClinicasDisponibles.clinicas;
    }
    */
  }
  
  /// Verificar si una clínica está activa y disponible
  Future<bool> verificarClinicaActiva(String dominio) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/'),
        headers: {
          'Host': '$dominio.localhost',
          'Content-Type': 'application/json',
        },
      );
      
      return response.statusCode == 200;
    } catch (e) {
      print('Error verificando clínica: $e');
      return false;
    }
  }
  
  /// Obtener información de planes disponibles (público)
  Future<List<Map<String, dynamic>>> getPlanesDisponibles() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.planesDisponibles}'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.cast<Map<String, dynamic>>();
      }
      
      return [];
    } catch (e) {
      print('Error obteniendo planes: $e');
      return [];
    }
  }
}
```

### 3. Provider de Clínica Seleccionada

```dart
// lib/providers/clinica_provider.dart

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/api/clinicas_disponibles.dart';
import '../services/clinica_service.dart';

class ClinicaProvider with ChangeNotifier {
  ClinicaDisponible? _clinicaSeleccionada;
  final ClinicaService _clinicaService = ClinicaService();
  bool _isLoading = false;
  String? _error;
  
  ClinicaDisponible? get clinicaSeleccionada => _clinicaSeleccionada;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get tieneClinicaSeleccionada => _clinicaSeleccionada != null;
  
  /// Cargar clínica guardada al iniciar la app
  Future<void> cargarClinicaGuardada() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final dominio = prefs.getString('clinica_dominio');
      
      if (dominio != null) {
        final clinica = ClinicasDisponibles.getByDominio(dominio);
        if (clinica != null) {
          _clinicaSeleccionada = clinica;
        }
      }
    } catch (e) {
      _error = 'Error cargando clínica guardada: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Seleccionar una clínica
  Future<bool> seleccionarClinica(ClinicaDisponible clinica) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      // Verificar que la clínica esté activa
      final activa = await _clinicaService.verificarClinicaActiva(clinica.dominio);
      
      if (!activa) {
        _error = 'La clínica no está disponible en este momento';
        _isLoading = false;
        notifyListeners();
        return false;
      }
      
      // Guardar en SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('clinica_dominio', clinica.dominio);
      await prefs.setString('clinica_nombre', clinica.nombre);
      await prefs.setString('clinica_id', clinica.id);
      
      _clinicaSeleccionada = clinica;
      _isLoading = false;
      notifyListeners();
      
      return true;
    } catch (e) {
      _error = 'Error al seleccionar clínica: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  /// Cambiar de clínica (requiere logout)
  Future<void> cambiarClinica() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('clinica_dominio');
    await prefs.remove('clinica_nombre');
    await prefs.remove('clinica_id');
    
    _clinicaSeleccionada = null;
    notifyListeners();
  }
  
  /// Obtener el dominio para usar en headers HTTP
  String getDominioHeader() {
    if (_clinicaSeleccionada == null) {
      throw Exception('No hay clínica seleccionada');
    }
    
    // ✅ FORMATO CORRECTO: dominio.localhost
    return '${_clinicaSeleccionada!.dominio}.localhost';
  }
}
```

### 4. Pantalla de Selector de Clínicas

```dart
// lib/screens/selector_clinica_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/clinica_provider.dart';
import '../services/clinica_service.dart';
import '../core/api/clinicas_disponibles.dart';
import '../widgets/common/loading_indicator.dart';

class SelectorClinicaScreen extends StatefulWidget {
  const SelectorClinicaScreen({Key? key}) : super(key: key);

  @override
  State<SelectorClinicaScreen> createState() => _SelectorClinicaScreenState();
}

class _SelectorClinicaScreenState extends State<SelectorClinicaScreen> {
  final ClinicaService _clinicaService = ClinicaService();
  List<ClinicaDisponible> _clinicas = [];
  bool _isLoading = true;
  String? _error;
  
  @override
  void initState() {
    super.initState();
    _cargarClinicas();
  }
  
  Future<void> _cargarClinicas() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      final clinicas = await _clinicaService.getClinicasDisponibles();
      setState(() {
        _clinicas = clinicas;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al cargar clínicas: $e';
        _isLoading = false;
      });
    }
  }
  
  Future<void> _seleccionarClinica(ClinicaDisponible clinica) async {
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);
    
    // Mostrar loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );
    
    final exito = await clinicaProvider.seleccionarClinica(clinica);
    
    // Cerrar loading
    if (mounted) Navigator.pop(context);
    
    if (exito) {
      // Navegar a login
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
      }
    } else {
      // Mostrar error
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(clinicaProvider.error ?? 'Error al seleccionar clínica'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              
              // Logo y título
              Icon(
                Icons.local_hospital,
                size: 80,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(height: 24),
              
              Text(
                'Bienvenido',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              
              Text(
                'Selecciona tu clínica dental',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              
              const SizedBox(height: 40),
              
              // Lista de clínicas
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _error != null
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.error_outline, size: 60, color: Colors.red),
                                const SizedBox(height: 16),
                                Text(_error!, textAlign: TextAlign.center),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: _cargarClinicas,
                                  child: const Text('Reintentar'),
                                ),
                              ],
                            ),
                          )
                        : _clinicas.isEmpty
                            ? Center(
                                child: Text(
                                  'No hay clínicas disponibles',
                                  style: TextStyle(color: Colors.grey[600]),
                                ),
                              )
                            : ListView.builder(
                                itemCount: _clinicas.length,
                                itemBuilder: (context, index) {
                                  final clinica = _clinicas[index];
                                  return Card(
                                    elevation: 2,
                                    margin: const EdgeInsets.only(bottom: 16),
                                    child: InkWell(
                                      onTap: () => _seleccionarClinica(clinica),
                                      borderRadius: BorderRadius.circular(12),
                                      child: Padding(
                                        padding: const EdgeInsets.all(16.0),
                                        child: Row(
                                          children: [
                                            // Logo o ícono
                                            Container(
                                              width: 60,
                                              height: 60,
                                              decoration: BoxDecoration(
                                                color: Theme.of(context).primaryColor.withOpacity(0.1),
                                                borderRadius: BorderRadius.circular(12),
                                              ),
                                              child: Icon(
                                                Icons.local_hospital,
                                                size: 32,
                                                color: Theme.of(context).primaryColor,
                                              ),
                                            ),
                                            
                                            const SizedBox(width: 16),
                                            
                                            // Información
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  Text(
                                                    clinica.nombre,
                                                    style: const TextStyle(
                                                      fontSize: 18,
                                                      fontWeight: FontWeight.bold,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 4),
                                                  Text(
                                                    clinica.descripcion,
                                                    style: TextStyle(
                                                      color: Colors.grey[600],
                                                      fontSize: 14,
                                                    ),
                                                  ),
                                                  if (clinica.telefono.isNotEmpty) ...[
                                                    const SizedBox(height: 4),
                                                    Row(
                                                      children: [
                                                        Icon(Icons.phone, size: 14, color: Colors.grey[600]),
                                                        const SizedBox(width: 4),
                                                        Text(
                                                          clinica.telefono,
                                                          style: TextStyle(
                                                            color: Colors.grey[600],
                                                            fontSize: 12,
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                                  ],
                                                ],
                                              ),
                                            ),
                                            
                                            // Ícono de flecha
                                            Icon(Icons.arrow_forward_ios, color: Colors.grey[400]),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),
              ),
              
              // Información adicional
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue[700]),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '¿No encuentras tu clínica? Contacta al administrador.',
                        style: TextStyle(
                          color: Colors.blue[700],
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## 🔧 Cliente HTTP con Header Automático

### Cliente HTTP Base con Tenant

```dart
// lib/core/api/api_client.dart

import 'package:http/http.dart' as http;
import 'dart:convert';
import '../storage/secure_storage.dart';
import '../../providers/clinica_provider.dart';
import 'endpoints.dart';

class ApiClient {
  final SecureStorage _storage = SecureStorage();
  final ClinicaProvider _clinicaProvider;
  
  ApiClient(this._clinicaProvider);
  
  /// Obtener headers base con autenticación y tenant
  Future<Map<String, String>> _getHeaders({bool includeAuth = true}) async {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    // Agregar header de tenant (clínica)
    try {
      final tenantHost = _clinicaProvider.getDominioHeader();
      headers['Host'] = tenantHost;  // ✅ CORRECTO: clinica_demo.localhost
    } catch (e) {
      print('Warning: No hay clínica seleccionada');
    }
    
    // Agregar token de autenticación si se requiere
    if (includeAuth) {
      final token = await _storage.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    
    return headers;
  }
  
  /// GET request
  Future<http.Response> get(
    String endpoint, {
    bool requireAuth = true,
    Map<String, String>? queryParameters,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final uriWithParams = queryParameters != null
        ? uri.replace(queryParameters: queryParameters)
        : uri;
    
    final headers = await _getHeaders(includeAuth: requireAuth);
    
    print('GET $uriWithParams');
    print('Headers: $headers');
    
    return await http.get(uriWithParams, headers: headers);
  }
  
  /// POST request
  Future<http.Response> post(
    String endpoint,
    Map<String, dynamic> body, {
    bool requireAuth = true,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final headers = await _getHeaders(includeAuth: requireAuth);
    
    print('POST $uri');
    print('Headers: $headers');
    print('Body: ${json.encode(body)}');
    
    return await http.post(
      uri,
      headers: headers,
      body: json.encode(body),
    );
  }
  
  /// PUT request
  Future<http.Response> put(
    String endpoint,
    Map<String, dynamic> body, {
    bool requireAuth = true,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final headers = await _getHeaders(includeAuth: requireAuth);
    
    return await http.put(
      uri,
      headers: headers,
      body: json.encode(body),
    );
  }
  
  /// PATCH request
  Future<http.Response> patch(
    String endpoint,
    Map<String, dynamic> body, {
    bool requireAuth = true,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final headers = await _getHeaders(includeAuth: requireAuth);
    
    return await http.patch(
      uri,
      headers: headers,
      body: json.encode(body),
    );
  }
  
  /// DELETE request
  Future<http.Response> delete(
    String endpoint, {
    bool requireAuth = true,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final headers = await _getHeaders(includeAuth: requireAuth);
    
    return await http.delete(uri, headers: headers);
  }
}
```

---

## 🧪 Prueba de Conexión

### Script de Prueba

```dart
// lib/core/api/test_connection.dart

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'endpoints.dart';

class ConnectionTester {
  /// Probar conexión al backend
  static Future<Map<String, dynamic>> testBackendConnection() async {
    try {
      print('🔍 Probando conexión a: ${ApiConfig.baseUrl}');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      print('✅ Status: ${response.statusCode}');
      print('📦 Body: ${response.body}');
      
      return {
        'success': true,
        'statusCode': response.statusCode,
        'body': response.body,
      };
    } catch (e) {
      print('❌ Error: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Probar conexión con tenant específico
  static Future<Map<String, dynamic>> testTenantConnection(String tenantDominio) async {
    try {
      print('🔍 Probando conexión a tenant: $tenantDominio');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': '$tenantDominio.localhost',
        },
      ).timeout(const Duration(seconds: 10));
      
      print('✅ Status: ${response.statusCode}');
      print('📦 Body: ${response.body}');
      
      return {
        'success': true,
        'statusCode': response.statusCode,
        'body': response.body,
      };
    } catch (e) {
      print('❌ Error: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Obtener planes disponibles (endpoint público)
  static Future<void> testPlanesEndpoint() async {
    try {
      print('🔍 Obteniendo planes disponibles...');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.planesDisponibles}'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      print('✅ Status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final List<dynamic> planes = json.decode(response.body);
        print('📋 Planes encontrados: ${planes.length}');
        for (var plan in planes) {
          print('  - ${plan['nombre']}: \$${plan['precio']}');
        }
      }
    } catch (e) {
      print('❌ Error: $e');
    }
  }
}
```

---

## 🔐 Flujo Completo: Selector → Login → App

```dart
// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/clinica_provider.dart';
import 'providers/auth_provider.dart';
import 'screens/splash_screen.dart';
import 'screens/selector_clinica_screen.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ClinicaProvider()),
        ChangeNotifierProxyProvider<ClinicaProvider, AuthProvider>(
          create: (context) => AuthProvider(
            Provider.of<ClinicaProvider>(context, listen: false),
          ),
          update: (context, clinicaProvider, authProvider) =>
              authProvider ?? AuthProvider(clinicaProvider),
        ),
      ],
      child: MaterialApp(
        title: 'Clínica Dental',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/selector-clinica': (context) => const SelectorClinicaScreen(),
          '/login': (context) => const LoginScreen(),
          '/home': (context) => const HomeScreen(),
        },
      ),
    );
  }
}
```

---

## ✅ Checklist de Implementación

- [ ] Configurar `ApiConfig` con URL de Render
- [ ] Definir `ClinicasDisponibles` con clínica demo
- [ ] Crear `ClinicaService` para cargar clínicas
- [ ] Implementar `ClinicaProvider` con almacenamiento
- [ ] Diseñar `SelectorClinicaScreen`
- [ ] Crear `ApiClient` con header automático
- [ ] Actualizar `AuthService` para usar `ApiClient`
- [ ] Probar conexión con `ConnectionTester`
- [ ] Verificar flujo completo: Selector → Login → Home

---

## 🚀 Notas Importantes

### Headers Correctos

```dart
// ✅ CORRECTO - Formato del header
headers: {
  'Host': 'clinica_demo.localhost',  // En producción: clinica_demo.tudominio.com
  'Authorization': 'Bearer $token',
  'Content-Type': 'application/json',
}

// ❌ INCORRECTO - No usar X-Tenant-ID
headers: {
  'X-Tenant-ID': 'clinica_demo',  // ⚠️ Este formato ya NO se usa
}
```

### Dominio vs Schema

```dart
// En el backend:
// - Schema: tenant_clinica_demo (con guiones bajos)
// - Dominio: clinica_demo (identificador)
// - Host header: clinica_demo.localhost

// En Flutter, siempre usar el dominio:
String tenantHost = '${clinica.dominio}.localhost';
```

### Producción vs Desarrollo

```dart
// Desarrollo (localhost/emulator)
Host: clinica_demo.localhost

// Producción (Render)
Host: clinica_demo.onrender.com
// O con dominio personalizado:
Host: clinica_demo.tudominio.com
```

---

## 📚 Próximos Pasos

1. **Implementar selector de clínicas** según esta guía
2. **Actualizar AuthService** para usar `ApiClient` con headers automáticos
3. **Probar conexión** con `ConnectionTester`
4. **Continuar con login/registro** (guía 04)

---

**Siguiente:** [04_login_registro.md](04_login_registro.md) - Autenticación con JWT
