# 🔍 Servicio de Bitácora - API Client

## 🎯 Archivo: `lib/services/bitacora_service.dart`

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../config/env.dart';
import 'auth_service.dart';

class BitacoraService {
  final AuthService _authService = AuthService();

  /// Headers comunes para todas las peticiones
  Future<Map<String, String>> _getHeaders() async {
    final token = await _authService.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
      'X-Tenant': AppConfig.defaultTenant,
    };
  }

  // =====================================================
  // ENDPOINTS DE BITÁCORA
  // =====================================================

  /// GET /api/reportes/bitacora/?page=1&page_size=20
  /// 
  /// Obtiene registros paginados de la bitácora
  /// 
  /// Parámetros:
  /// - pagina: Número de página (default: 1)
  /// - tamanoPagina: Registros por página (default: 20)
  /// - filtros: Map con filtros opcionales:
  ///   - usuario: ID del usuario
  ///   - accion: CREAR/EDITAR/ELIMINAR/VER/LOGIN/LOGOUT/EXPORTAR
  ///   - desde: Fecha desde (YYYY-MM-DD)
  ///   - hasta: Fecha hasta (YYYY-MM-DD)
  ///   - modelo: Nombre del modelo (ej: 'cita', 'paciente')
  ///   - ip: Dirección IP
  ///   - descripcion: Búsqueda en descripción
  Future<Map<String, dynamic>> obtenerBitacora({
    int pagina = 1,
    int tamanoPagina = 20,
    Map<String, dynamic>? filtros,
  }) async {
    // Construir query parameters
    Map<String, String> queryParams = {
      'page': pagina.toString(),
      'page_size': tamanoPagina.toString(),
    };

    // Agregar filtros si existen
    if (filtros != null) {
      filtros.forEach((key, value) {
        if (value != null && value.toString().isNotEmpty) {
          queryParams[key] = value.toString();
        }
      });
    }

    final uri = Uri.parse('${AppConfig.baseUrl}/api/reportes/bitacora/')
        .replace(queryParameters: queryParams);
    
    final headers = await _getHeaders();
    final response = await http.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      
      return {
        'count': data['count'],
        'next': data['next'],
        'previous': data['previous'],
        'results': data['results'],
      };
    } else {
      throw Exception('Error al obtener bitácora: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/bitacora/estadisticas/?dias=7
  /// 
  /// Obtiene estadísticas de actividad de la bitácora
  Future<Map<String, dynamic>> obtenerEstadisticas({int dias = 7}) async {
    final uri = Uri.parse(
      '${AppConfig.baseUrl}/api/reportes/bitacora/estadisticas/?dias=$dias'
    );
    
    final headers = await _getHeaders();
    final response = await http.get(uri, headers: headers);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error al obtener estadísticas: ${response.statusCode}');
    }
  }

  // =====================================================
  // EXPORTACIÓN DE BITÁCORA
  // =====================================================

  /// GET /api/reportes/bitacora/exportar/?formato=pdf
  /// 
  /// Exporta la bitácora filtrada a PDF o Excel
  Future<bool> exportarBitacora({
    required String formato,
    Map<String, dynamic>? filtros,
  }) async {
    // Validar formato
    if (!['pdf', 'excel'].contains(formato)) {
      throw Exception('Formato inválido. Usar "pdf" o "excel"');
    }

    // Solicitar permisos
    if (!await _solicitarPermisosAlmacenamiento()) {
      throw Exception('Permisos de almacenamiento denegados');
    }

    // Construir URL con filtros
    Map<String, String> queryParams = {'formato': formato};
    
    if (filtros != null) {
      filtros.forEach((key, value) {
        if (value != null && value.toString().isNotEmpty) {
          queryParams[key] = value.toString();
        }
      });
    }

    final uri = Uri.parse('${AppConfig.baseUrl}/api/reportes/bitacora/exportar/')
        .replace(queryParameters: queryParams);
    
    final headers = await _getHeaders();
    final response = await http.get(uri, headers: headers);

    if (response.statusCode == 200) {
      // Verificar Content-Type
      final contentType = response.headers['content-type'] ?? '';
      
      if (formato == 'pdf' && !contentType.contains('pdf')) {
        throw Exception('El servidor devolvió JSON en lugar de PDF');
      }
      
      if (formato == 'excel' && !contentType.contains('spreadsheet')) {
        throw Exception('El servidor devolvió JSON en lugar de Excel');
      }

      // Guardar archivo
      final fileName = _generarNombreArchivo(formato, filtros);
      final filePath = await _guardarArchivo(response.bodyBytes, fileName);
      
      print('✅ Bitácora guardada en: $filePath');
      return true;
    } else {
      throw Exception('Error al exportar bitácora: ${response.statusCode}');
    }
  }

  // =====================================================
  // MÉTODOS AUXILIARES
  // =====================================================

  /// Solicitar permisos de almacenamiento
  Future<bool> _solicitarPermisosAlmacenamiento() async {
    if (Platform.isAndroid) {
      var status = await Permission.storage.status;
      
      if (!status.isGranted) {
        status = await Permission.storage.request();
      }
      
      // Android 11+ requiere MANAGE_EXTERNAL_STORAGE
      if (!status.isGranted) {
        status = await Permission.manageExternalStorage.request();
      }
      
      return status.isGranted;
    }
    
    // iOS no requiere permisos para Documents
    return true;
  }

  /// Guardar archivo en el dispositivo
  Future<String> _guardarArchivo(List<int> bytes, String fileName) async {
    Directory? directory;
    
    if (Platform.isAndroid) {
      // Android: Guardar en Downloads
      directory = Directory('/storage/emulated/0/Download');
      
      if (!await directory.exists()) {
        directory = await getExternalStorageDirectory();
      }
    } else {
      // iOS: Guardar en Documents
      directory = await getApplicationDocumentsDirectory();
    }
    
    final filePath = '${directory!.path}/$fileName';
    final file = File(filePath);
    
    await file.writeAsBytes(bytes);
    
    return filePath;
  }

  /// Generar nombre de archivo descriptivo
  String _generarNombreArchivo(String formato, Map<String, dynamic>? filtros) {
    final timestamp = DateTime.now().toIso8601String().split('T')[0];
    final extension = formato == 'pdf' ? 'pdf' : 'xlsx';
    
    String nombre = 'bitacora';
    
    // Agregar filtros al nombre si existen
    if (filtros != null && filtros.isNotEmpty) {
      if (filtros.containsKey('accion')) {
        nombre += '_${filtros['accion']}';
      }
      if (filtros.containsKey('desde')) {
        nombre += '_desde_${filtros['desde']}';
      }
      if (filtros.containsKey('hasta')) {
        nombre += '_hasta_${filtros['hasta']}';
      }
    }
    
    return '${nombre}_$timestamp.$extension';
  }

  // =====================================================
  // MÉTODOS DE FILTRADO
  // =====================================================

  /// Construir filtros desde Map genérico
  Map<String, String> construirFiltros({
    int? usuarioId,
    String? accion,
    String? fechaDesde,
    String? fechaHasta,
    String? modelo,
    String? ip,
    String? descripcion,
  }) {
    final Map<String, String> filtros = {};
    
    if (usuarioId != null) filtros['usuario'] = usuarioId.toString();
    if (accion != null && accion.isNotEmpty) filtros['accion'] = accion;
    if (fechaDesde != null && fechaDesde.isNotEmpty) filtros['desde'] = fechaDesde;
    if (fechaHasta != null && fechaHasta.isNotEmpty) filtros['hasta'] = fechaHasta;
    if (modelo != null && modelo.isNotEmpty) filtros['modelo'] = modelo;
    if (ip != null && ip.isNotEmpty) filtros['ip'] = ip;
    if (descripcion != null && descripcion.isNotEmpty) filtros['descripcion'] = descripcion;
    
    return filtros;
  }
}
```

---

## 🔑 Métodos Principales

### 1. Consultas
- `obtenerBitacora()` - Lista paginada con filtros
- `obtenerEstadisticas()` - Resumen de actividad

### 2. Exportación
- `exportarBitacora()` - Descarga PDF o Excel con filtros aplicados

### 3. Filtros Disponibles
```dart
final filtros = {
  'usuario': '1',                    // ID del usuario
  'accion': 'CREAR',                 // CREAR/EDITAR/ELIMINAR/VER/etc
  'desde': '2025-01-01',             // Fecha desde
  'hasta': '2025-12-31',             // Fecha hasta
  'modelo': 'cita',                  // Modelo (cita, paciente, etc)
  'ip': '192.168.1.1',               // Dirección IP
  'descripcion': 'Cita creada',      // Búsqueda en texto
};
```

---

## 📊 Estructura de Respuesta

### `obtenerBitacora()`
```dart
{
  'count': 150,                      // Total de registros
  'next': 'http://...?page=2',       // URL siguiente página
  'previous': null,                   // URL página anterior
  'results': [                        // Registros actuales
    {
      'id': 1,
      'usuario': 5,
      'usuario_nombre': 'Admin',
      'accion': 'CREAR',
      'descripcion': 'Cita #123 creada',
      'fecha_hora': '2025-11-27T10:30:00Z',
      'ip_address': '192.168.1.1',
      'content_type': 12,
      'content_type_nombre': 'cita',
      'object_id': 123,
    },
    // ...
  ]
}
```

### `obtenerEstadisticas()`
```dart
{
  'periodo': 'Últimos 7 días',
  'total_acciones': 45,
  'acciones_por_tipo': [
    {'accion': 'CREAR', 'total': 15},
    {'accion': 'EDITAR', 'total': 10},
    {'accion': 'VER', 'total': 20},
  ],
  'usuarios_mas_activos': [
    {'usuario__first_name': 'Admin', 'usuario__last_name': '', 'total': 30},
  ],
  'actividad_diaria': [
    {'fecha_hora__date': '2025-11-27', 'total': 10},
    {'fecha_hora__date': '2025-11-26', 'total': 8},
  ]
}
```

---

## 🎯 Uso en Widgets

```dart
final BitacoraService _bitacoraService = BitacoraService();

// Obtener registros paginados
final resultado = await _bitacoraService.obtenerBitacora(
  pagina: 1,
  tamanoPagina: 20,
  filtros: {
    'accion': 'CREAR',
    'desde': '2025-11-01',
  },
);

print('Total registros: ${resultado['count']}');
print('Resultados: ${resultado['results'].length}');

// Exportar con filtros
await _bitacoraService.exportarBitacora(
  formato: 'pdf',
  filtros: {
    'usuario': '1',
    'desde': '2025-11-01',
  },
);
```

---

## 🎯 Siguiente Paso

Crear widget de filtros avanzados:
👉 **[13_FILTROS_BITACORA.md](13_FILTROS_BITACORA.md)**
