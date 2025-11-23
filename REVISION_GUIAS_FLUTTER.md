# 🔍 REVISIÓN: Guías Flutter vs Código Backend

## 📋 Discrepancias Encontradas

### 1. **Rutas de Autenticación** ❌

**Guía Flutter:** `04_login_registro.md`

```dart
// ❌ INCORRECTO en la guía:
Uri.parse('$baseUrl/api/auth/login/')           // NO EXISTE
Uri.parse('$baseUrl/api/auth/registro/')        // NO EXISTE
Uri.parse('$baseUrl/api/auth/token/refresh/')   // NO EXISTE
Uri.parse('$baseUrl/api/auth/recuperar-password/') // NO EXISTE
```

**Backend Real:** `core/urls_public.py` y `usuarios/urls.py`

```python
# ✅ RUTAS CORRECTAS:
path('api/token/', CustomTokenObtainPairView.as_view())     # Login JWT
path('api/token/refresh/', TokenRefreshView.as_view())      # Refresh token
path('api/usuarios/register/', RegisterView.as_view())      # Registro
# NO existe endpoint de recuperar contraseña
```

**Corrección Flutter:**
```dart
// ✅ CORRECTO:
Uri.parse('$baseUrl/api/token/')                    // Login
Uri.parse('$baseUrl/api/token/refresh/')            // Refresh token
Uri.parse('$baseUrl/api/usuarios/register/')        // Registro
```

---

### 2. **Endpoint de "Mis Citas"** ❌

**Guía Flutter:** `06_mis_citas.md`

```dart
// ❌ INCORRECTO en la guía:
String url = '$baseUrl/api/agenda/mis-citas/';   // NO EXISTE
```

**Backend Real:** `agenda/urls.py` y `agenda/views.py`

```python
# ✅ RUTAS EXISTENTES:
GET /api/agenda/citas/           # Lista TODAS las citas (filtradas por usuario automáticamente)
GET /api/agenda/citas/proximas/  # Citas futuras (PENDIENTE o CONFIRMADA)
GET /api/agenda/citas/hoy/       # Citas de hoy
GET /api/agenda/citas/{id}/      # Detalle de una cita específica
```

**Corrección Flutter:**
```dart
// ✅ CORRECTO - Opciones disponibles:

// Opción 1: Usar lista general (ya filtra por usuario automáticamente)
String url = '$baseUrl/api/agenda/citas/';

// Opción 2: Usar endpoint de próximas citas
String url = '$baseUrl/api/agenda/citas/proximas/';

// Opción 3: Filtrar por estado en lista general
String url = '$baseUrl/api/agenda/citas/?estado=PENDIENTE';
```

---

### 3. **Estructura de Respuesta de Login** ⚠️

**Guía Flutter:** `04_login_registro.md`

```dart
// ⚠️ REVISAR estructura esperada:
factory AuthResponse.fromJson(Map<String, dynamic> json) {
  return AuthResponse(
    accessToken: json['access'],
    refreshToken: json['refresh'],
    usuario: Usuario.fromJson(json['usuario']),  // ¿Backend envía 'usuario'?
  );
}
```

**Backend Real:** `usuarios/jwt_views.py`

El backend usa `CustomTokenObtainPairSerializer` que extiende `TokenObtainPairSerializer`. Necesito verificar qué retorna exactamente.

**Acción Requerida:** 
- Verificar si el login retorna datos del usuario o solo tokens
- Si solo retorna tokens, el flujo correcto sería:
  1. POST `/api/token/` → Obtener access y refresh tokens
  2. GET `/api/usuarios/me/` → Obtener datos del usuario con el token

---

### 4. **Estados de Cita** ✅

**Guía Flutter:** `06_mis_citas.md`

```dart
// ✅ CORRECTO:
bool get isPendiente => estado == 'PENDIENTE';
bool get isConfirmada => estado == 'CONFIRMADA';
bool get isCompletada => estado == 'COMPLETADA';    // ⚠️ Pero backend usa 'ATENDIDA'
bool get isCancelada => estado == 'CANCELADA';
```

**Backend Real:** `agenda/models.py`

```python
ESTADO_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('CONFIRMADA', 'Confirmada'),
    ('ATENDIDA', 'Atendida'),      # ⚠️ NO 'COMPLETADA'
    ('CANCELADA', 'Cancelada'),
]
```

**Corrección Flutter:**
```dart
// ✅ CORRECTO:
bool get isPendiente => estado == 'PENDIENTE';
bool get isConfirmada => estado == 'CONFIRMADA';
bool get isAtendida => estado == 'ATENDIDA';       // ✅ Cambiar de COMPLETADA a ATENDIDA
bool get isCancelada => estado == 'CANCELADA';
```

---

### 5. **Estructura de Odontólogo** ⚠️

**Guía Flutter:** `06_mis_citas.md`

```dart
factory Odontologo.fromJson(Map<String, dynamic> json) {
  return Odontologo(
    id: json['id'],
    nombre: json['usuario']['full_name'] ?? '',    // ⚠️ Anidamiento
    especialidad: json['especialidad'],
    foto: json['usuario']['foto'],                 // ⚠️ Anidamiento
  );
}
```

**Backend Real:** Necesito verificar cómo serializa `CitaSerializer` el campo `odontologo`.

**Acción Requerida:**
- Revisar `agenda/serializers.py` para ver estructura exacta de odontologo
- Posibles formatos:
  - Si usa `OdontologoSerializer`: Tendrá estructura completa
  - Si solo retorna ID: Necesitará endpoint separado para obtener detalles

---

## 📊 Resumen de Correcciones Necesarias

### Guía `04_login_registro.md`

| Línea Aprox | Cambio Requerido |
|-------------|------------------|
| ~88 | Cambiar `/api/auth/login/` → `/api/token/` |
| ~106 | Cambiar `/api/auth/registro/` → `/api/usuarios/register/` |
| ~127 | Cambiar `/api/auth/token/refresh/` → `/api/token/refresh/` |
| ~156 | Eliminar o marcar como NO IMPLEMENTADO: `recuperar-password` |

**Código Correcto:**
```dart
// Login
final response = await http.post(
  Uri.parse('$baseUrl/api/token/'),  // ✅ Ruta correcta
  headers: {
    'Content-Type': 'application/json',
    'Host': '$tenantId.localhost',  // ✅ O usar X-Tenant-ID
  },
  body: json.encode({
    'email': email,  // ✅ Backend espera email, NO username
    'password': password,
  }),
);

// Registro
final response = await http.post(
  Uri.parse('$baseUrl/api/usuarios/register/'),  // ✅ Ruta correcta
  headers: {
    'Content-Type': 'application/json',
    'Host': '$tenantId.localhost',
  },
  body: json.encode({
    'email': email,
    'password': password,
    'full_name': fullName,  // ✅ Campo correcto
    'telefono': telefono,
    'fecha_nacimiento': fechaNacimiento,
  }),
);

// Refresh Token
final response = await http.post(
  Uri.parse('$baseUrl/api/token/refresh/'),  // ✅ Ruta correcta
  headers: {
    'Content-Type': 'application/json',
    'Host': '$tenantId.localhost',
  },
  body: json.encode({'refresh': refreshToken}),
);
```

---

### Guía `06_mis_citas.md`

| Línea Aprox | Cambio Requerido |
|-------------|------------------|
| ~82 | Cambiar `/api/agenda/mis-citas/` → `/api/agenda/citas/` |
| ~26 | Cambiar `isCompletada` → `isAtendida` |
| ~28 | Cambiar `estado == 'COMPLETADA'` → `estado == 'ATENDIDA'` |

**Código Correcto:**
```dart
// Obtener citas
Future<List<CitaDetallada>> getMisCitas({
  required String token,
  required String tenantId,
  String? estado,
  bool soloProximas = false,
}) async {
  try {
    // ✅ Opciones de endpoints disponibles:
    String url;
    if (soloProximas) {
      url = '$baseUrl/api/agenda/citas/proximas/';  // ✅ Custom action
    } else {
      url = '$baseUrl/api/agenda/citas/';  // ✅ Lista general (ya filtra por usuario)
      if (estado != null) {
        url += '?estado=$estado';  // ✅ Filtro por estado
      }
    }

    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
        'Host': '$tenantId.localhost',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List<dynamic> citas = data['results'] ?? data;
      return citas.map((json) => CitaDetallada.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar citas');
    }
  } catch (e) {
    throw Exception('Error de conexión: $e');
  }
}

// Estados correctos
class CitaDetallada {
  // ...
  bool get isPendiente => estado == 'PENDIENTE';
  bool get isConfirmada => estado == 'CONFIRMADA';
  bool get isAtendida => estado == 'ATENDIDA';      // ✅ Cambio de COMPLETADA a ATENDIDA
  bool get isCancelada => estado == 'CANCELADA';
  // ...
}
```

---

## 🔍 Verificaciones Pendientes

Para completar la revisión, necesito verificar:

### 1. ¿Qué retorna el login? ✅ VERIFICAR

**Opción A:** Backend retorna tokens + usuario
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "id": 123,
    "email": "paciente@example.com",
    "full_name": "Juan Pérez"
  }
}
```

**Opción B:** Backend solo retorna tokens
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Si es Opción B**, el flujo correcto en Flutter sería:
```dart
// 1. Login
final authResponse = await login(email, password);
final accessToken = authResponse.access;

// 2. Obtener datos del usuario
final userResponse = await http.get(
  Uri.parse('$baseUrl/api/usuarios/me/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Host': '$tenantId.localhost',
  },
);
final usuario = Usuario.fromJson(json.decode(userResponse.body));
```

---

### 2. ¿Cómo serializa el odontólogo? ✅ VERIFICAR

Revisar `agenda/serializers.py` línea donde define el campo `odontologo`.

**Posibles formatos:**

**Formato A:** ID simple
```json
{
  "id": 123,
  "fecha_hora": "2025-11-23T10:00:00Z",
  "odontologo": 45  // ← Solo ID
}
```

**Formato B:** Objeto completo
```json
{
  "id": 123,
  "fecha_hora": "2025-11-23T10:00:00Z",
  "odontologo": {
    "id": 45,
    "usuario": {
      "id": 50,
      "full_name": "Dr. María González",
      "email": "maria@clinica.com"
    },
    "especialidad": "Ortodoncia"
  }
}
```

**Si es Formato A**, necesitarías endpoint adicional:
```dart
GET /api/usuarios/odontologos/{id}/
```

---

### 3. ¿Header correcto para multi-tenant? ✅ VERIFICAR

**Opción A:** Usar subdomain en Host header
```dart
headers: {
  'Host': 'clinica_demo.localhost',
}
```

**Opción B:** Usar custom header
```dart
headers: {
  'X-Tenant-ID': 'clinica_demo',
}
```

**Opción C:** Ambos (recomendado)
```dart
headers: {
  'Host': 'clinica_demo.localhost',
  'X-Tenant-ID': 'clinica_demo',
}
```

---

## ✅ Checklist de Actualización de Guías

- [ ] Actualizar `04_login_registro.md`:
  - [ ] Cambiar ruta de login a `/api/token/`
  - [ ] Cambiar ruta de registro a `/api/usuarios/register/`
  - [ ] Cambiar ruta de refresh a `/api/token/refresh/`
  - [ ] Verificar estructura de respuesta de login
  - [ ] Agregar flujo de obtener usuario con `/api/usuarios/me/`
  - [ ] Marcar recuperar-password como NO IMPLEMENTADO o eliminarlo

- [ ] Actualizar `06_mis_citas.md`:
  - [ ] Cambiar endpoint a `/api/agenda/citas/`
  - [ ] Agregar documentación de `/api/agenda/citas/proximas/`
  - [ ] Cambiar `COMPLETADA` → `ATENDIDA` en todos los lugares
  - [ ] Verificar estructura del serializer de odontólogo
  - [ ] Actualizar `Odontologo.fromJson()` según formato real

- [ ] Revisar otras guías pendientes:
  - [ ] `07_agendar_cita.md` - Endpoints de creación
  - [ ] `08_historial_clinico.md` - Endpoints de historial
  - [ ] `09_tratamientos.md` - Endpoints de planes
  - [ ] `10_facturas_pagos.md` - Endpoints de facturación
  - [ ] `12_api_service.md` - Configuración general de API

---

## 🎯 Recomendaciones

### 1. Crear script de verificación

Agregar al backend un endpoint de documentación automática:

```python
# core/urls.py
path('api/docs/', include('rest_framework.urls')),  # Browsable API
```

### 2. Generar especificación OpenAPI

```python
# settings.py
INSTALLED_APPS += ['drf_spectacular']

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

Esto generaría documentación automática y actualizada de todos los endpoints.

### 3. Crear tests de integración

Agregar tests que verifiquen que las rutas documentadas en las guías existen:

```python
# tests/test_guias_flutter.py
def test_rutas_login_existen():
    """Verifica que las rutas documentadas en guías Flutter existan"""
    response = client.post('/api/token/')  # Debe existir
    assert response.status_code != 404
```

---

**Última actualización:** 22/11/2025 23:55  
**Estado:** ⚠️ Discrepancias encontradas, requiere actualización de guías  
**Prioridad:** Alta - Las rutas incorrectas impedirán que la app Flutter funcione
