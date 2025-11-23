# 📍 Endpoints por Pantalla - Flutter App

> **✅ Todos estos endpoints están probados y funcionando en el web**  
> Usa exactamente estos endpoints para cada pantalla de Flutter

---

## 🏠 1. Dashboard (Home Screen)

### Datos Necesarios:
- Número de citas próximas
- Próxima cita con detalles
- Tratamientos activos
- Saldo pendiente

### Endpoints:
```dart
// 1. Citas próximas (filtra automáticamente por usuario)
GET /api/agenda/citas/?ordering=fecha_hora&limit=5
// Respuesta: { results: [...citas], count: N }

// 2. Planes de tratamiento activos
GET /api/tratamientos/planes/?estado=en_progreso
// Respuesta: { results: [...planes], count: N }

// 3. Estado de cuenta
GET /api/facturacion/facturas/estado_cuenta/
// Respuesta: { saldo_pendiente: 202.80, facturas_pendientes: 1, ... }
```

### Implementación:
```dart
// DashboardService.getDashboard()
final citasData = await _getCitas(token, tenantId);
final planesData = await _getPlanes(token, tenantId);
final estadoCuentaData = await _getEstadoCuenta(token, tenantId);

return DashboardData(
  proximasCitas: citasData['results'].length,
  tratamientosActivos: planesData['results'].length,
  saldoPendiente: estadoCuentaData['saldo_pendiente'],
  proximaCita: citasData['results'].isNotEmpty 
      ? Cita.fromJson(citasData['results'][0]) 
      : null,
);
```

---

## 📅 2. Mis Citas (Citas Screen)

### Datos Necesarios:
- Lista de todas las citas
- Filtros por estado
- Detalle de cita individual

### Endpoints:
```dart
// Lista de citas (ordenadas por fecha)
GET /api/agenda/citas/?ordering=fecha_hora
// Respuesta: { results: [...], count: N, next: null, previous: null }

// Filtrar por estado
GET /api/agenda/citas/?estado=PENDIENTE
GET /api/agenda/citas/?estado=CONFIRMADA
GET /api/agenda/citas/?estado=ATENDIDA

// Solo citas futuras
GET /api/agenda/citas/?fecha_inicio=2025-11-23&ordering=fecha_hora

// Detalle de una cita
GET /api/agenda/citas/{id}/

// Confirmar cita
POST /api/agenda/citas/{id}/confirmar/
// Body: {}

// Cancelar cita
POST /api/agenda/citas/{id}/cancelar/
// Body: { "motivo_cancelacion": "No puedo asistir" }
```

### Estados Válidos:
- `PENDIENTE` - Creada, no confirmada
- `CONFIRMADA` - Confirmada por paciente
- `ATENDIDA` - Ya completada (no usar COMPLETADA)
- `CANCELADA` - Cancelada

### Modelo de Cita:
```dart
class Cita {
  final int id;
  final String fechaHora;           // "2025-11-23T10:00:00Z"
  final String motivo;              // Descripción
  final String motivoTipo;          // CONSULTA_GENERAL, LIMPIEZA, etc.
  final String estado;              // PENDIENTE, CONFIRMADA, etc.
  final Odontologo? odontologo;
  
  factory Cita.fromJson(Map<String, dynamic> json) {
    return Cita(
      id: json['id'],
      fechaHora: json['fecha_hora'],
      motivo: json['motivo'] ?? '',
      motivoTipo: json['motivo_tipo'] ?? 'CONSULTA_GENERAL',
      estado: json['estado'] ?? 'PENDIENTE',
      odontologo: json['odontologo'] != null 
          ? Odontologo.fromJson(json['odontologo'])
          : null,
    );
  }
}

class Odontologo {
  final int id;
  final String nombre;
  final String especialidad;
  
  factory Odontologo.fromJson(Map<String, dynamic> json) {
    return Odontologo(
      id: json['id'],
      nombre: json['usuario']['nombre'] ?? 'Sin nombre',
      especialidad: json['especialidad'] ?? 'General',
    );
  }
}
```

---

## 📅 3. Agendar Cita (Crear Cita)

### Datos Necesarios:
- Lista de odontólogos
- Horarios disponibles
- Crear nueva cita

### Endpoints:
```dart
// Listar odontólogos
GET /api/usuarios/odontologos/
// Respuesta: [{ id: 1, usuario: {...}, especialidad: "..." }, ...]

// Disponibilidad de odontólogo
GET /api/agenda/citas/disponibilidad/?odontologo_id=1&fecha=2025-11-25
// Respuesta: { horarios_disponibles: ["09:00", "10:00", "11:00", ...] }

// Crear cita
POST /api/agenda/citas/
// Body:
{
  "odontologo": 1,
  "fecha_hora": "2025-11-25T10:00:00",
  "motivo": "Revisión general",
  "motivo_tipo": "CONSULTA_GENERAL",
  "estado": "PENDIENTE"
}
```

### Tipos de Motivo Válidos:
- `CONSULTA_GENERAL`
- `LIMPIEZA`
- `ENDODONCIA`
- `ORTODONCIA`
- `CIRUGIA`
- `EMERGENCIA`
- `CONTROL`
- `OTRO`

---

## 📋 4. Historial Clínico

### Datos Necesarios:
- Mi historial clínico
- Episodios de atención

### Endpoints:
```dart
// Mi historial (retorna 1 objeto con episodios)
GET /api/historial/historiales/mi_historial/
// Respuesta:
{
  "id": 1,
  "numero_historial": "HC-000001",
  "fecha_creacion": "2025-11-20",
  "episodios_atencion": [
    {
      "id": 1,
      "fecha": "2025-11-20",
      "motivo_consulta": "Dolor molar",
      "diagnostico": "Caries dental",
      "tratamiento_realizado": "Obturación",
      "odontologo": {...}
    }
  ]
}

// Detalle de un episodio
GET /api/historial/episodios/{id}/
```

### Modelo:
```dart
class HistorialClinico {
  final int id;
  final String numeroHistorial;
  final String fechaCreacion;
  final List<Episodio> episodios;
}

class Episodio {
  final int id;
  final String fecha;
  final String motivoConsulta;
  final String diagnostico;
  final String tratamientoRealizado;
  final Odontologo odontologo;
}
```

---

## 🦷 5. Tratamientos (Planes de Tratamiento)

### Datos Necesarios:
- Lista de planes de tratamiento
- Items del plan
- Progreso

### Endpoints:
```dart
// Todos mis planes
GET /api/tratamientos/planes/
// Respuesta: { results: [...planes], count: N }

// Solo planes activos
GET /api/tratamientos/planes/?estado=en_progreso

// Detalle de un plan
GET /api/tratamientos/planes/{id}/
// Respuesta:
{
  "id": 1,
  "nombre": "Tratamiento Completo",
  "descripcion": "...",
  "fecha_inicio": "2025-11-20",
  "estado": "en_progreso",
  "progreso": 33.33,
  "total": 750.00,
  "items": [
    {
      "id": 1,
      "tratamiento_nombre": "Limpieza dental",
      "precio": 150.00,
      "estado": "completado",
      "orden": 1
    },
    ...
  ]
}

// Items del plan
GET /api/tratamientos/planes/{id}/items/
```

### Estados de Plan:
- `propuesto` - Creado pero no iniciado
- `en_progreso` - En tratamiento
- `completado` - Terminado
- `cancelado` - Cancelado

### Estados de Item:
- `pendiente` - No iniciado
- `en_curso` - En progreso
- `completado` - Terminado

---

## 💰 6. Facturas y Pagos

### Datos Necesarios:
- Lista de facturas
- Estado de cuenta
- Detalle de factura
- Pagos

### Endpoints:
```dart
// Mis facturas
GET /api/facturacion/facturas/mis_facturas/
// Respuesta: [{ id: 1, numero_factura: "F-001", total: 280.00, ... }, ...]

// Estado de cuenta (resumen)
GET /api/facturacion/facturas/estado_cuenta/
// Respuesta:
{
  "saldo_pendiente": 202.80,
  "facturas_pendientes": 1,
  "total_pagado": 280.00,
  "total_facturado": 632.80
}

// Detalle de factura
GET /api/facturacion/facturas/{id}/
// Respuesta:
{
  "id": 255,
  "numero_factura": "F-000255",
  "fecha_emision": "2025-11-20",
  "total": 352.80,
  "monto_pagado": 150.00,
  "saldo_pendiente": 202.80,
  "estado": "pendiente",
  "items": [...]
}

// Pagos de una factura
GET /api/facturacion/facturas/{id}/pagos/
// Respuesta: [{ id: 1, monto: 150.00, fecha_pago: "...", metodo: "efectivo" }, ...]
```

### Estados de Factura:
- `pendiente` - No pagada completamente
- `pagada` - Pagada totalmente
- `parcial` - Pago parcial
- `cancelada` - Cancelada

---

## 👤 7. Perfil de Usuario

### Datos Necesarios:
- Información del usuario
- Actualizar datos
- Cambiar contraseña

### Endpoints:
```dart
// Mi información
GET /api/usuarios/me/
// Respuesta:
{
  "id": 615,
  "email": "maria.garcia@email.com",
  "nombre": "María",
  "apellido": "García",
  "full_name": "María García",
  "rol": "paciente",
  "perfil_paciente": {
    "telefono": "555-0123",
    "fecha_nacimiento": "1990-05-15",
    "direccion": "Calle Principal 123",
    "alergias": "Ninguna",
    "condiciones_medicas": "Ninguna"
  }
}

// Actualizar perfil
PATCH /api/usuarios/me/
// Body: { "nombre": "María Elena", "apellido": "García López" }

// Cambiar contraseña
POST /api/usuarios/change-password/
// Body: { "old_password": "...", "new_password": "..." }
```

---

## 🔐 8. Autenticación

### Endpoints:
```dart
// Login
POST /api/token/
// Body: { "email": "maria.garcia@email.com", "password": "password123" }
// Respuesta: { "access": "...", "refresh": "..." }

// Refresh token
POST /api/token/refresh/
// Body: { "refresh": "..." }
// Respuesta: { "access": "..." }

// Registro
POST /api/usuarios/register/
// Body:
{
  "email": "nuevo@example.com",
  "password": "password123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "555-1234",
  "fecha_nacimiento": "1995-01-01"
}
```

---

## 📋 Headers Requeridos

Todas las peticiones (excepto login/register) necesitan:

```dart
headers: {
  'Content-Type': 'application/json',
  'Host': '$tenantDominio.localhost',  // ej: 'clinicademo1.localhost'
  'Authorization': 'Bearer $accessToken',
}
```

---

## ✅ Resumen por Service

| Service | Endpoints Principales | Pantallas |
|---------|----------------------|-----------|
| **AuthService** | `/api/token/`, `/api/token/refresh/`, `/api/usuarios/register/` | Login, Registro |
| **DashboardService** | Combina CitasService + PlanesService + FacturasService | Home Dashboard |
| **CitasService** | `/api/agenda/citas/`, `/disponibilidad/`, `/confirmar/`, `/cancelar/` | Mis Citas, Agendar |
| **HistorialService** | `/api/historial/historiales/mi_historial/` | Historial Clínico |
| **PlanesService** | `/api/tratamientos/planes/`, `/planes/{id}/items/` | Tratamientos |
| **FacturasService** | `/api/facturacion/facturas/mis_facturas/`, `/estado_cuenta/` | Facturas y Pagos |
| **PerfilService** | `/api/usuarios/me/`, `/change-password/` | Perfil |

---

## 🎯 Próximos Pasos

1. **Copiar estos endpoints exactos** en cada service de Flutter
2. **No inventar nuevos endpoints** - usar solo los documentados aquí
3. **Probar con María García** (maria.garcia@email.com / password123)
4. **Validar respuestas** antes de parsear JSON

---

**Fecha:** 23 de noviembre, 2025  
**Estado:** ✅ Todos los endpoints validados en producción con el web
