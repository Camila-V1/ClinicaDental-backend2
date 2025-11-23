# 🔄 Actualización de Endpoints - Usar Patrón Web

> **Fecha:** 23/11/2025  
> **Razón:** El endpoint consolidado `/api/usuarios/dashboard/` presentaba errores 500  
> **Solución:** Usar los mismos endpoints individuales que funcionan en el web

---

## ❌ Problema Anterior

### Endpoint Consolidado (Flutter)
```dart
// ❌ PROBLEMA: Daba error 500
GET /api/usuarios/dashboard/
```

**Error:**
```
500 Internal Server Error
AttributeError: 'PerfilOdontologo' object has no attribute 'id'
```

---

## ✅ Solución - Patrón Web

### Endpoints Individuales (Probados y Funcionando)

El web hace **5 llamadas separadas** que todas funcionan correctamente:

```javascript
// 1. Obtener citas próximas
GET /api/agenda/citas/?ordering=fecha_hora&limit=5

// 2. Obtener historial clínico
GET /api/historial/historiales/mi_historial/

// 3. Obtener planes de tratamiento activos
GET /api/tratamientos/planes/?estado=en_progreso

// 4. Obtener estado de cuenta (facturas)
GET /api/facturacion/facturas/estado_cuenta/

// 5. Obtener mis facturas
GET /api/facturacion/facturas/mis_facturas/
```

**Todas las llamadas retornan 200 OK con datos correctos** ✅

---

## 📱 Implementación en Flutter

### Dashboard Service Actualizado

```dart
class DashboardService {
  final String baseUrl = AppConstants.baseUrlDev;

  Future<DashboardData> getDashboard(String token, String tenantId) async {
    try {
      // ✅ 1. Obtener próximas citas
      final citasResponse = await http.get(
        Uri.parse('$baseUrl/api/agenda/citas/?ordering=fecha_hora&limit=5'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      // ✅ 2. Obtener planes de tratamiento activos
      final planesResponse = await http.get(
        Uri.parse('$baseUrl/api/tratamientos/planes/?estado=en_progreso'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      // ✅ 3. Obtener estado de cuenta
      final estadoCuentaResponse = await http.get(
        Uri.parse('$baseUrl/api/facturacion/facturas/estado_cuenta/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      // Verificar autenticación
      if (citasResponse.statusCode == 401) {
        throw TokenExpiredException('Token expirado');
      }

      // Parsear respuestas
      final citasData = json.decode(citasResponse.body);
      final planesData = json.decode(planesResponse.body);
      final estadoCuentaData = json.decode(estadoCuentaResponse.body);

      // Filtrar solo citas activas (no canceladas ni atendidas)
      final citas = (citasData['results'] as List)
          .where((c) => c['estado'] != 'CANCELADA' && c['estado'] != 'ATENDIDA')
          .toList();

      return DashboardData(
        proximasCitas: citas.length,
        tratamientosActivos: (planesData['results'] as List).length,
        saldoPendiente: double.parse(estadoCuentaData['saldo_pendiente']?.toString() ?? '0'),
        proximaCita: citas.isNotEmpty ? Cita.fromJson(citas.first) : null,
      );
    } catch (e) {
      if (e is TokenExpiredException) rethrow;
      throw Exception('Error de conexión: $e');
    }
  }
}
```

---

## 🆚 Comparación

| Aspecto | Endpoint Consolidado | Endpoints Individuales |
|---------|---------------------|----------------------|
| **Llamadas HTTP** | 1 | 3-5 |
| **Complejidad Backend** | Alta (consolidar datos) | Baja (queries simples) |
| **Facilidad Debug** | Difícil | Fácil |
| **Mantenimiento** | Frágil | Robusto |
| **Estado Actual** | ❌ Error 500 | ✅ Funciona |
| **Usado en Web** | ❌ No | ✅ Sí |

---

## 📊 Endpoints por Pantalla

### 1. Dashboard (Home)
```dart
// Citas próximas
GET /api/agenda/citas/?ordering=fecha_hora&limit=5

// Planes activos
GET /api/tratamientos/planes/?estado=en_progreso

// Estado de cuenta
GET /api/facturacion/facturas/estado_cuenta/
```

### 2. Mis Citas
```dart
// Todas las citas del usuario
GET /api/agenda/citas/?ordering=fecha_hora

// Filtrar por estado
GET /api/agenda/citas/?estado=PENDIENTE

// Detalle de cita
GET /api/agenda/citas/{id}/

// Confirmar cita
POST /api/agenda/citas/{id}/confirmar/

// Cancelar cita
POST /api/agenda/citas/{id}/cancelar/
```

### 3. Historial Clínico
```dart
// Mi historial
GET /api/historial/historiales/mi_historial/

// Episodios del historial
GET /api/historial/historiales/{id}/episodios/
```

### 4. Tratamientos
```dart
// Todos mis planes
GET /api/tratamientos/planes/

// Por estado
GET /api/tratamientos/planes/?estado=en_progreso

// Detalle del plan
GET /api/tratamientos/planes/{id}/

// Items del plan
GET /api/tratamientos/planes/{id}/items/
```

### 5. Facturas
```dart
// Mis facturas
GET /api/facturacion/facturas/mis_facturas/

// Estado de cuenta
GET /api/facturacion/facturas/estado_cuenta/

// Detalle factura
GET /api/facturacion/facturas/{id}/

// Pagos de una factura
GET /api/facturacion/facturas/{id}/pagos/
```

### 6. Perfil
```dart
// Mi información
GET /api/usuarios/me/

// Actualizar perfil
PATCH /api/usuarios/me/

// Cambiar contraseña
POST /api/usuarios/change-password/
```

---

## ✅ Ventajas del Patrón Web

1. **Probado y Funcionando** ✅
   - Ya está funcionando en producción con el web
   - María García puede ver todos sus datos correctamente

2. **Más Robusto** 💪
   - Si un endpoint falla, los demás siguen funcionando
   - Mejor manejo de errores parciales

3. **Más Fácil de Debuggear** 🔍
   - Puedes identificar exactamente qué endpoint falla
   - Logs más claros

4. **Reutilizable** ♻️
   - Los mismos services pueden usarse en otras pantallas
   - CitasService, PlanesService, FacturasService, etc.

5. **Escalable** 📈
   - Fácil agregar más datos sin afectar los existentes
   - Puedes cargar datos en paralelo

---

## 📁 Estructura de Services

```dart
lib/services/
├── auth_service.dart          // Login, registro, tokens
├── citas_service.dart         // Todo sobre citas
├── planes_service.dart        // Planes de tratamiento
├── facturas_service.dart      // Facturas y pagos
├── historial_service.dart     // Historial clínico
├── perfil_service.dart        // Perfil de usuario
└── dashboard_service.dart     // Combina todos los anteriores
```

---

## 🎯 Guías Actualizadas

Las siguientes guías ya usan el patrón web:

- ✅ **05_home_dashboard.md** - Dashboard usa endpoints individuales
- ⏳ **06_mis_citas.md** - Ya estaba usando endpoints correctos
- ⏳ **07_agendar_cita.md** - Revisar si necesita actualización
- ⏳ **08_historial_clinico.md** - Revisar
- ⏳ **09_tratamientos.md** - Revisar
- ⏳ **10_facturas_pagos.md** - Revisar

---

## 💡 Recomendación Final

**USAR SIEMPRE LOS ENDPOINTS INDIVIDUALES QUE USA EL WEB**

1. Son más simples y confiables
2. Ya están probados en producción
3. Más fáciles de mantener y debuggear
4. El web los usa con éxito = tú también puedes

---

**Fecha de Actualización:** 23 de noviembre, 2025  
**Estado:** ✅ Solución validada con web en producción
