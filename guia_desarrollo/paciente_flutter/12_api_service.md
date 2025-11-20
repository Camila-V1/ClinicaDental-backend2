# 🌐 API Service (Centralizado)

## 🎯 Objetivo
Centralizar todas las llamadas HTTP con interceptores, manejo de errores y refresh token automático.

---

## 🔧 API Client Base

### `lib/core/api_client.dart`

```dart
import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clinica_dental_app/config/constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  
  late Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrlDev,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Agregar tenant ID
          final prefs = await SharedPreferences.getInstance();
          final tenantId = prefs.getString(AppConstants.keyClinicaId);
          if (tenantId != null) {
            options.headers['X-Tenant-ID'] = tenantId;
          }

          // Agregar token de autorización
          final token = await _storage.read(key: AppConstants.keyAccessToken);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }

          print('→ ${options.method} ${options.path}');
          print('  Headers: ${options.headers}');
          if (options.data != null) {
            print('  Body: ${options.data}');
          }

          return handler.next(options);
        },
        onResponse: (response, handler) {
          print('← ${response.statusCode} ${response.requestOptions.path}');
          return handler.next(response);
        },
        onError: (error, handler) async {
          print('✗ Error ${error.response?.statusCode} ${error.requestOptions.path}');
          print('  Message: ${error.message}');
          
          // Manejar errores 401 (token expirado)
          if (error.response?.statusCode == 401) {
            // Intentar refrescar el token
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Reintentar la petición original
              return handler.resolve(await _retry(error.requestOptions));
            }
          }

          return handler.next(error);
        },
      ),
    );
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: AppConstants.keyRefreshToken);
      if (refreshToken == null) return false;

      final response = await _dio.post(
        '/api/usuarios/token/refresh/',
        data: {'refresh': refreshToken},
        options: Options(
          headers: {
            'Authorization': null, // No enviar token en refresh
          },
        ),
      );

      if (response.statusCode == 200) {
        final newAccessToken = response.data['access'];
        await _storage.write(
          key: AppConstants.keyAccessToken,
          value: newAccessToken,
        );
        return true;
      }
      return false;
    } catch (e) {
      print('Error refreshing token: $e');
      return false;
    }
  }

  Future<Response> _retry(RequestOptions requestOptions) async {
    final options = Options(
      method: requestOptions.method,
      headers: requestOptions.headers,
    );

    return _dio.request(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
  }

  // Métodos HTTP
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Manejo de errores
  Exception _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return TimeoutException('Tiempo de espera agotado');
      
      case DioExceptionType.badResponse:
        return _handleResponseError(error.response!);
      
      case DioExceptionType.cancel:
        return Exception('Petición cancelada');
      
      default:
        if (error.error is SocketException) {
          return NetworkException('Sin conexión a internet');
        }
        return Exception('Error desconocido: ${error.message}');
    }
  }

  Exception _handleResponseError(Response response) {
    switch (response.statusCode) {
      case 400:
        return BadRequestException(_extractErrorMessage(response));
      case 401:
        return UnauthorizedException('Sesión expirada');
      case 403:
        return ForbiddenException('No tienes permisos');
      case 404:
        return NotFoundException('Recurso no encontrado');
      case 500:
        return ServerException('Error del servidor');
      default:
        return Exception('Error ${response.statusCode}');
    }
  }

  String _extractErrorMessage(Response response) {
    try {
      final data = response.data;
      if (data is Map) {
        if (data.containsKey('detail')) return data['detail'];
        if (data.containsKey('message')) return data['message'];
        if (data.containsKey('error')) return data['error'];
        
        // Errores de validación
        final firstKey = data.keys.first;
        final firstValue = data[firstKey];
        if (firstValue is List && firstValue.isNotEmpty) {
          return firstValue.first.toString();
        }
      }
      return response.statusMessage ?? 'Error desconocido';
    } catch (e) {
      return 'Error al procesar la respuesta';
    }
  }

  // Limpiar tokens (logout)
  Future<void> clearTokens() async {
    await _storage.delete(key: AppConstants.keyAccessToken);
    await _storage.delete(key: AppConstants.keyRefreshToken);
  }
}

// Excepciones personalizadas
class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
  @override
  String toString() => message;
}

class TimeoutException implements Exception {
  final String message;
  TimeoutException(this.message);
  @override
  String toString() => message;
}

class BadRequestException implements Exception {
  final String message;
  BadRequestException(this.message);
  @override
  String toString() => message;
}

class UnauthorizedException implements Exception {
  final String message;
  UnauthorizedException(this.message);
  @override
  String toString() => message;
}

class ForbiddenException implements Exception {
  final String message;
  ForbiddenException(this.message);
  @override
  String toString() => message;
}

class NotFoundException implements Exception {
  final String message;
  NotFoundException(this.message);
  @override
  String toString() => message;
}

class ServerException implements Exception {
  final String message;
  ServerException(this.message);
  @override
  String toString() => message;
}
```

---

## 🔄 Refactorización de Servicios

### Ejemplo: `lib/services/auth_service.dart` (Refactorizado)

```dart
import 'package:clinica_dental_app/core/api_client.dart';
import 'package:clinica_dental_app/models/usuario.dart';

class AuthService {
  final ApiClient _client = ApiClient();

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _client.post(
      '/api/usuarios/login/',
      data: {
        'email': email,
        'password': password,
      },
    );

    return AuthResponse.fromJson(response.data);
  }

  Future<AuthResponse> registro({
    required String email,
    required String password,
    required String fullName,
    String? telefono,
  }) async {
    final response = await _client.post(
      '/api/usuarios/registro-paciente/',
      data: {
        'email': email,
        'password': password,
        'full_name': fullName,
        'telefono': telefono,
      },
    );

    return AuthResponse.fromJson(response.data);
  }

  Future<void> cambiarPassword({
    required String token,
    required String passwordActual,
    required String passwordNueva,
  }) async {
    await _client.post(
      '/api/usuarios/cambiar-password/',
      data: {
        'password_actual': passwordActual,
        'password_nueva': passwordNueva,
      },
    );
  }

  Future<void> recuperarPassword({required String email}) async {
    await _client.post(
      '/api/usuarios/recuperar-password/',
      data: {'email': email},
    );
  }
}
```

---

## 🎯 Ventajas del API Client Centralizado

### 1. **Interceptores Automáticos**
- ✅ Token automático en todas las peticiones
- ✅ Tenant-ID automático
- ✅ Refresh token automático al expirar
- ✅ Logs de todas las peticiones

### 2. **Manejo de Errores Unificado**
- ✅ Excepciones tipadas por código HTTP
- ✅ Mensajes de error extraídos del backend
- ✅ Manejo de timeouts
- ✅ Detección de sin conexión

### 3. **Configuración Centralizada**
- ✅ Base URL única
- ✅ Timeouts configurables
- ✅ Headers globales
- ✅ Fácil de modificar

### 4. **Retry Automático**
- ✅ Reintenta peticiones tras refresh token
- ✅ No pierde la petición original
- ✅ Transparente para el usuario

---

## 🔄 Migración de Servicios Existentes

### Antes (con http):
```dart
Future<List<Cita>> getMisCitas() async {
  final prefs = await SharedPreferences.getInstance();
  final tenantId = prefs.getString('clinica_id');
  final storage = FlutterSecureStorage();
  final token = await storage.read(key: 'access_token');

  final response = await http.get(
    Uri.parse('$baseUrl/api/agenda/mis-citas/'),
    headers: {
      'Content-Type': 'application/json',
      'X-Tenant-ID': tenantId!,
      'Authorization': 'Bearer $token',
    },
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return (data as List).map((e) => Cita.fromJson(e)).toList();
  } else {
    throw Exception('Error al cargar citas');
  }
}
```

### Después (con ApiClient):
```dart
Future<List<Cita>> getMisCitas() async {
  final response = await _client.get('/api/agenda/mis-citas/');
  return (response.data as List).map((e) => Cita.fromJson(e)).toList();
}
```

**Beneficios:**
- 🔥 **80% menos código**
- ✅ Token y Tenant-ID automáticos
- ✅ Refresh token automático
- ✅ Manejo de errores incluido
- ✅ Logs automáticos

---

## 🧪 Testing del API Client

### `test/api_client_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:clinica_dental_app/core/api_client.dart';

void main() {
  group('ApiClient Tests', () {
    late ApiClient client;

    setUp(() {
      client = ApiClient();
    });

    test('GET request successful', () async {
      final response = await client.get('/api/test/');
      expect(response.statusCode, 200);
    });

    test('POST request with data', () async {
      final response = await client.post(
        '/api/test/',
        data: {'key': 'value'},
      );
      expect(response.statusCode, 201);
    });

    test('Handles 401 error', () async {
      expect(
        () => client.get('/api/unauthorized/'),
        throwsA(isA<UnauthorizedException>()),
      );
    });

    test('Handles network error', () async {
      expect(
        () => client.get('/api/nonexistent-server/'),
        throwsA(isA<NetworkException>()),
      );
    });
  });
}
```

---

## ✅ Checklist de Migración

- [ ] Crear `ApiClient` centralizado
- [ ] Agregar interceptores (token, tenant-ID, logs)
- [ ] Implementar refresh token automático
- [ ] Crear excepciones personalizadas
- [ ] Migrar `AuthService`
- [ ] Migrar `CitasService`
- [ ] Migrar `TratamientosService`
- [ ] Migrar `FacturasService`
- [ ] Migrar `HistorialService`
- [ ] Eliminar código duplicado de http

---

## 📚 Uso en Nuevos Servicios

```dart
class NuevoServicio {
  final ApiClient _client = ApiClient();

  Future<MiModelo> getData() async {
    final response = await _client.get('/api/mi-endpoint/');
    return MiModelo.fromJson(response.data);
  }

  Future<void> postData(MiModelo modelo) async {
    await _client.post(
      '/api/mi-endpoint/',
      data: modelo.toJson(),
    );
  }
}
```

---

**Siguiente:** [13_state_management.md](13_state_management.md)
