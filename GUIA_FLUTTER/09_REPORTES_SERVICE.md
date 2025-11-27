# 📊 Servicio de Reportes - API Client

## 🎯 Archivo: `lib/services/reportes_service.dart`

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../config/env.dart';
import 'auth_service.dart';

class ReportesService {
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
  // ENDPOINTS DE REPORTES
  // =====================================================

  /// GET /api/reportes/reportes/dashboard-kpis/
  Future<Map<String, dynamic>> obtenerDashboardKPIs() async {
    final url = Uri.parse('${AppConfig.baseUrl}/api/reportes/reportes/dashboard-kpis/');
    final headers = await _getHeaders();
    
    final response = await http.get(url, headers: headers);
    
    if (response.statusCode == 200) {
      final List<dynamic> kpisArray = json.decode(response.body);
      
      // Convertir array a mapa con claves normalizadas
      Map<String, dynamic> kpis = {};
      for (var item in kpisArray) {
        String key = _normalizeKey(item['metrica']);
        kpis[key] = item['valor'];
      }
      
      return kpis;
    } else {
      throw Exception('Error al obtener KPIs: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/reportes/estadisticas-generales/
  Future<Map<String, dynamic>> obtenerEstadisticasGenerales() async {
    final url = Uri.parse('${AppConfig.baseUrl}/api/reportes/reportes/estadisticas-generales/');
    final headers = await _getHeaders();
    
    final response = await http.get(url, headers: headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error al obtener estadísticas: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/reportes/tendencia-citas/?dias=15
  Future<List<Map<String, dynamic>>> obtenerTendenciaCitas({int dias = 15}) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/api/reportes/reportes/tendencia-citas/?dias=$dias'
    );
    final headers = await _getHeaders();
    
    final response = await http.get(url, headers: headers);
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Error al obtener tendencia: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/reportes/top-procedimientos/?limite=5
  Future<List<Map<String, dynamic>>> obtenerTopProcedimientos({int limite = 5}) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/api/reportes/reportes/top-procedimientos/?limite=$limite'
    );
    final headers = await _getHeaders();
    
    final response = await http.get(url, headers: headers);
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Error al obtener procedimientos: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/reportes/ocupacion-odontologos/
  Future<List<Map<String, dynamic>>> obtenerOcupacionOdontologos() async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/api/reportes/reportes/ocupacion-odontologos/'
    );
    final headers = await _getHeaders();
    
    final response = await http.get(url, headers: headers);
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Error al obtener ocupación: ${response.statusCode}');
    }
  }

  /// GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11
  Future<Map<String, dynamic>> obtenerReporteFinanciero({String? periodo}) async {
    String url = '${AppConfig.baseUrl}/api/reportes/reportes/reporte-financiero/';
    if (periodo != null) {
      url += '?periodo=$periodo';
    }
    
    final headers = await _getHeaders();
    final response = await http.get(Uri.parse(url), headers: headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error al obtener reporte financiero: ${response.statusCode}');
    }
  }

  // =====================================================
  // EXPORTACIÓN DE REPORTES (PDF/EXCEL)
  // =====================================================

  /// Exportar reporte a PDF o Excel y guardar en dispositivo
  Future<bool> exportarReporte({
    required String tipoReporte,
    required String formato,
    Map<String, String>? parametros,
  }) async {
    // Validar formato
    if (!['pdf', 'excel'].contains(formato)) {
      throw Exception('Formato inválido. Usar "pdf" o "excel"');
    }

    // Solicitar permisos de almacenamiento
    if (!await _solicitarPermisosAlmacenamiento()) {
      throw Exception('Permisos de almacenamiento denegados');
    }

    // Construir URL con parámetros
    String url = '${AppConfig.baseUrl}/api/reportes/reportes/$tipoReporte/';
    
    Map<String, String> params = {'formato': formato};
    if (parametros != null) {
      params.addAll(parametros);
    }
    
    final uri = Uri.parse(url).replace(queryParameters: params);
    
    // Obtener headers
    final headers = await _getHeaders();
    
    // Hacer petición
    final response = await http.get(uri, headers: headers);
    
    if (response.statusCode == 200) {
      // Verificar Content-Type
      final contentType = response.headers['content-type'] ?? '';
      
      if (formato == 'pdf' && !contentType.contains('pdf')) {
        throw Exception('El servidor devolvió JSON en lugar de PDF');
      }
      
      if (formato == 'excel' && !contentType.contains('spreadsheet') && !contentType.contains('excel')) {
        throw Exception('El servidor devolvió JSON en lugar de Excel');
      }
      
      // Guardar archivo
      final fileName = _generarNombreArchivo(tipoReporte, formato);
      final filePath = await _guardarArchivo(response.bodyBytes, fileName);
      
      print('✅ Archivo guardado en: $filePath');
      return true;
    } else {
      throw Exception('Error al exportar: ${response.statusCode}');
    }
  }

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
    
    // iOS no requiere permisos especiales para Documents
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

  /// Generar nombre de archivo con timestamp
  String _generarNombreArchivo(String tipoReporte, String formato) {
    final timestamp = DateTime.now().toIso8601String().split('T')[0];
    final extension = formato == 'pdf' ? 'pdf' : 'xlsx';
    return 'reporte_${tipoReporte}_$timestamp.$extension';
  }

  /// Normalizar claves de KPIs (ej: "Pacientes Activos" -> "total_pacientes")
  String _normalizeKey(String metrica) {
    final Map<String, String> mappings = {
      'pacientes activos': 'total_pacientes',
      'citas hoy': 'citas_hoy',
      'ingresos este mes': 'ingresos_mes',
      'saldo pendiente': 'facturas_pendientes',
      'tratamientos activos': 'tratamientos_activos',
      'planes completados': 'planes_completados',
    };
    
    final key = metrica.toLowerCase();
    return mappings[key] ?? key.replaceAll(' ', '_');
  }
}
```

---

## 🔑 Métodos Principales

### 1. Obtener Datos
- `obtenerDashboardKPIs()` - KPIs principales
- `obtenerEstadisticasGenerales()` - Estadísticas completas
- `obtenerTendenciaCitas(dias)` - Tendencia de citas
- `obtenerTopProcedimientos(limite)` - Procedimientos más realizados
- `obtenerOcupacionOdontologos()` - Ocupación por doctor
- `obtenerReporteFinanciero(periodo)` - Reporte financiero

### 2. Exportación
- `exportarReporte()` - Descarga PDF o Excel
- `_solicitarPermisosAlmacenamiento()` - Permisos Android/iOS
- `_guardarArchivo()` - Guardar en Downloads o Documents
- `_generarNombreArchivo()` - Nombre con timestamp

---

## 📱 Manejo de Archivos

### Android
```dart
// Guarda en: /storage/emulated/0/Download/
// Requiere permisos: WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
```

### iOS
```dart
// Guarda en: Documents directory
// Visible en app Files
```

---

## 🎯 Uso en Widgets

```dart
final ReportesService _reportesService = ReportesService();

// Cargar datos
final kpis = await _reportesService.obtenerDashboardKPIs();
final tendencia = await _reportesService.obtenerTendenciaCitas(dias: 30);

// Exportar
await _reportesService.exportarReporte(
  tipoReporte: 'estadisticas-generales',
  formato: 'pdf',
);
```

---

## 🎯 Siguiente Paso

Implementar pantalla de bitácora:
👉 **[11_BITACORA_SCREEN.md](11_BITACORA_SCREEN.md)**
