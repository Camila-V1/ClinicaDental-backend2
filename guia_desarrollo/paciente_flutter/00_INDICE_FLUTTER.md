# 📱 App Móvil Flutter - Portal del Paciente

> **✅ GUÍAS ACTUALIZADAS** - 23/11/2025  
> **CAMBIO IMPORTANTE:** Ahora usamos los **mismos endpoints individuales que el web**  
> **Razón:** El endpoint consolidado `/api/usuarios/dashboard/` daba error 500  
> **Solución:** Usar endpoints probados y funcionando en producción
> 
> **Cambios críticos:**
> - ✅ `04_login_registro.md` - Rutas de autenticación corregidas
> - ✅ `05_home_dashboard.md` - **ACTUALIZADO** - Usa endpoints individuales como el web
> - ✅ `06_mis_citas.md` - Endpoints y estados actualizados
> - ✅ `ACTUALIZACION_ENDPOINTS_WEB.md` - **NUEVO** - Guía sobre el cambio de arquitectura
> 
> Ver `ACTUALIZACION_ENDPOINTS_WEB.md` para detalles completos del cambio.

## 🎯 Objetivo
Crear una aplicación móvil Flutter para que los pacientes puedan gestionar sus citas, ver su historial clínico, facturas y más, desde sus dispositivos móviles.

---

## 📋 Índice de Guías

### 🏗️ Configuración Inicial
1. **[01_setup_proyecto.md](01_setup_proyecto.md)** - Crear proyecto Flutter y estructura
2. **[02_configuracion_dependencias.md](02_configuracion_dependencias.md)** - Paquetes y configuración
2a. **[02a_selector_clinica_conexion.md](02a_selector_clinica_conexion.md)** - ✅ Selector de clínicas y conexión a Render

### 📍 Guías de Endpoints (NUEVO)
- **[ENDPOINTS_POR_PANTALLA.md](ENDPOINTS_POR_PANTALLA.md)** - ⭐ **REFERENCIA COMPLETA** - Todos los endpoints por pantalla
- **[ACTUALIZACION_ENDPOINTS_WEB.md](ACTUALIZACION_ENDPOINTS_WEB.md)** - ⭐ Explicación del cambio a patrón web

### 🔐 Autenticación
3. **[03_selector_clinica.md](03_selector_clinica.md)** - Pantalla inicial para seleccionar clínica
4. **[04_login_registro.md](04_login_registro.md)** - ✅ **ACTUALIZADA** - Login, registro y tokens JWT

### 📱 Vistas Principales
5. **[05_home_dashboard.md](05_home_dashboard.md)** - ✅ **ACTUALIZADA** - Dashboard con endpoints individuales
6. **[06_mis_citas.md](06_mis_citas.md)** - ✅ **ACTUALIZADA** - Ver y gestionar citas
7. **[07_agendar_cita.md](07_agendar_cita.md)** - Crear nueva cita
8. **[08_historial_clinico.md](08_historial_clinico.md)** - ✅ **ACTUALIZADA** - Ver historial médico (endpoint web)
9. **[09_tratamientos.md](09_tratamientos.md)** - ✅ **ACTUALIZADA** - Planes de tratamiento (endpoint web)
10. **[10_facturas_pagos.md](10_facturas_pagos.md)** - ✅ **ACTUALIZADA** - Ver facturas (endpoint web)
11. **[11_perfil_configuracion.md](11_perfil_configuracion.md)** - Editar perfil y notificaciones

### 🛠️ Servicios y Utilidades
12. **[12_api_service.md](12_api_service.md)** - Servicio HTTP con autenticación
13. **[13_state_management.md](13_state_management.md)** - Provider/Riverpod para estado
14. **[14_notificaciones.md](14_notificaciones.md)** - Push notifications

---

## 🏛️ Arquitectura de la App

```
lib/
├── main.dart                          # Entry point
├── config/
│   ├── theme.dart                     # Tema y colores
│   ├── routes.dart                    # Rutas de navegación
│   └── constants.dart                 # Constantes globales
├── core/
│   ├── api/
│   │   ├── api_client.dart            # Cliente HTTP base
│   │   ├── endpoints.dart             # URLs de endpoints
│   │   └── interceptors.dart          # Interceptores JWT
│   ├── storage/
│   │   └── secure_storage.dart        # Almacenamiento seguro (tokens)
│   └── utils/
│       ├── validators.dart            # Validadores de formularios
│       ├── formatters.dart            # Formateadores de fecha/moneda
│       └── helpers.dart               # Funciones auxiliares
├── models/
│   ├── clinica.dart                   # Modelo de clínica
│   ├── usuario.dart                   # Modelo de usuario/paciente
│   ├── cita.dart                      # Modelo de cita
│   ├── tratamiento.dart               # Modelo de plan de tratamiento
│   ├── factura.dart                   # Modelo de factura
│   └── historial.dart                 # Modelo de historial clínico
├── providers/
│   ├── auth_provider.dart             # Estado de autenticación
│   ├── clinica_provider.dart          # Estado de clínica seleccionada
│   ├── citas_provider.dart            # Estado de citas
│   ├── tratamientos_provider.dart     # Estado de tratamientos
│   └── perfil_provider.dart           # Estado de perfil
├── services/
│   ├── auth_service.dart              # Servicio de autenticación
│   ├── clinica_service.dart           # Servicio de clínicas
│   ├── citas_service.dart             # Servicio de citas
│   ├── tratamientos_service.dart      # Servicio de tratamientos
│   ├── facturas_service.dart          # Servicio de facturas
│   └── notificaciones_service.dart    # Servicio de notificaciones
├── screens/
│   ├── splash_screen.dart             # Pantalla de carga
│   ├── selector_clinica_screen.dart   # Selección de clínica
│   ├── login_screen.dart              # Login
│   ├── registro_screen.dart           # Registro
│   ├── home_screen.dart               # Dashboard principal
│   ├── citas/
│   │   ├── mis_citas_screen.dart      # Lista de citas
│   │   ├── detalle_cita_screen.dart   # Detalle de cita
│   │   └── agendar_cita_screen.dart   # Agendar nueva cita
│   ├── tratamientos/
│   │   ├── tratamientos_screen.dart   # Planes activos
│   │   └── detalle_tratamiento_screen.dart
│   ├── historial/
│   │   ├── historial_screen.dart      # Lista de historial
│   │   └── detalle_historial_screen.dart
│   ├── facturas/
│   │   ├── facturas_screen.dart       # Lista de facturas
│   │   ├── detalle_factura_screen.dart
│   │   └── pago_screen.dart           # Realizar pago
│   └── perfil/
│       ├── perfil_screen.dart         # Editar perfil
│       └── configuracion_screen.dart  # Configuración
├── widgets/
│   ├── common/
│   │   ├── custom_app_bar.dart        # AppBar personalizado
│   │   ├── custom_button.dart         # Botón personalizado
│   │   ├── custom_text_field.dart     # Campo de texto personalizado
│   │   ├── loading_indicator.dart     # Indicador de carga
│   │   └── error_widget.dart          # Widget de error
│   ├── citas/
│   │   ├── cita_card.dart             # Card de cita
│   │   └── calendario_widget.dart     # Calendario
│   ├── tratamientos/
│   │   └── tratamiento_card.dart      # Card de tratamiento
│   └── facturas/
│       └── factura_card.dart          # Card de factura
└── l10n/                              # Internacionalización (opcional)
    ├── app_es.arb                     # Español
    └── app_en.arb                     # Inglés
```

---

## 🎨 Diseño UI/UX

### Paleta de Colores
```dart
// Colores principales
Primary: #3B82F6 (Blue 500)
Secondary: #10B981 (Green 500)
Accent: #8B5CF6 (Purple 500)
Background: #F9FAFB (Gray 50)
Surface: #FFFFFF
Error: #EF4444 (Red 500)
Text Primary: #111827 (Gray 900)
Text Secondary: #6B7280 (Gray 500)
```

### Componentes Reutilizables
- **CustomAppBar**: AppBar con título y acciones personalizadas
- **CustomButton**: Botón con loading state
- **CustomTextField**: Input con validación
- **CitaCard**: Card para mostrar citas
- **TratamientoCard**: Card para tratamientos
- **FacturaCard**: Card para facturas
- **LoadingIndicator**: Spinner de carga
- **EmptyState**: Estado vacío con ilustración

---

## 🔐 Flujo de Autenticación Multi-Tenant

### 1. Selector de Clínica
```
Usuario abre app
    ↓
Splash Screen (verifica si hay sesión)
    ↓
¿Tiene sesión guardada?
    ├── Sí → Ir al Home (con clínica guardada)
    └── No → Mostrar Selector de Clínica
         ↓
    Lista de clínicas disponibles
         ↓
    Usuario selecciona clínica
         ↓
    Guardar clínica seleccionada en memoria
         ↓
    Ir a Login/Registro
```

### 2. Login
```
Pantalla de Login
    ↓
Usuario ingresa email y password
    ↓
POST /api/token/ (✅ CORRECTO - con Host: {tenant}.localhost)
    ↓
Recibir tokens (access, refresh)
    ↓
GET /api/usuarios/me/ (obtener datos del usuario)
    ↓
Guardar tokens en SecureStorage
Guardar clínica en SharedPreferences
    ↓
Ir a Home Screen
```

### 3. Registro
```
Pantalla de Registro
    ↓
Usuario ingresa datos (email, password, full_name, etc.)
    ↓
POST /api/usuarios/register/ (✅ CORRECTO - con Host: {tenant}.localhost)
    ↓
Auto-login con POST /api/token/
    ↓
Ir a Home Screen
```

---

## 🌐 Comunicación con API

### Backend de Producción (Render)

```dart
// URL de producción
const String prodUrl = 'https://clinica-dental-backend.onrender.com';

// Clínica demo disponible
const String clinicaDemo = 'clinica_demo';
```

### Configuración de Clínica (Tenant)

El backend usa **subdominios** para identificar clínicas. En Flutter, usamos el **header Host**:

```dart
// ✅ CORRECTO - Usar el dominio exacto de la clínica
// Obtener primero las clínicas desde GET /
// Ejemplo: dominio = 'clinicademo1'
headers: {
  'Host': '$dominio.localhost',  // ej: 'clinicademo1.localhost'
  'Authorization': 'Bearer $accessToken',
  'Content-Type': 'application/json',
}

// ⚠️ En producción Render (sin subdominios):
headers: {
  'Host': 'clinica-dental-backend.onrender.com',
  'X-Tenant': '$dominio',  // Opcional, el backend lo manejará
}
```

### Endpoints Base
```dart
// ✅ Backend en Render (Producción)
const String baseUrl = 'https://clinica-dental-backend.onrender.com';

// Desarrollo (Local)
const String baseUrlDev = 'http://10.0.2.2:8000'; // Android Emulator
const String baseUrlDevIOS = 'http://localhost:8000'; // iOS Simulator
```

### Clínicas Disponibles
```dart
// ⚠️ IMPORTANTE: Obtener desde el backend GET /
// El backend retorna: {"clinicas": [...]}
{
  "clinicas": [
    {
      "id": 1,
      "nombre": "Clínica Demo",
      "dominio": "clinicademo1",  // Usar este dominio en headers
      "activo": true
    }
  ]
}

// Filtrar clínicas activas y excluir "public"
final clinicasActivas = data['clinicas']
    .where((c) => c['activo'] == true && c['dominio'] != 'public')
    .toList();
```

### Endpoints Principales (ACTUALIZADOS)

**⚠️ IMPORTANTE:** 
- Todas las peticiones (excepto `/api/tenants/*`) requieren header `Host: {dominio}.localhost`
- El dominio debe ser el obtenido desde `GET /` (ej: `clinicademo1`)
- En producción Render, usar el host principal sin subdominios

**Endpoints Públicos (sin tenant):**
- ✅ `GET /api/tenants/planes/` - Planes de suscripción disponibles
- ✅ `GET /api/tenants/info-registro/` - Información sobre registro
- ✅ `POST /api/tenants/solicitudes/` - Crear solicitud de nueva clínica

**Autenticación (con tenant):**
- ✅ `POST /api/token/` - Login (retorna access + refresh tokens)
- ✅ `POST /api/token/refresh/` - Renovar access token
- ✅ `POST /api/usuarios/register/` - Registro de nuevo paciente
- ✅ `GET /api/usuarios/me/` - Obtener datos del usuario autenticado

**Citas (con tenant):**
- ✅ `GET /api/agenda/citas/` - Lista de citas (filtra por usuario automáticamente)
- ✅ `GET /api/agenda/citas/proximas/` - Solo citas futuras (PENDIENTE/CONFIRMADA)
- ✅ `GET /api/agenda/citas/hoy/` - Citas de hoy
- ✅ `GET /api/agenda/citas/{id}/` - Detalle de una cita
- ✅ `POST /api/agenda/citas/{id}/confirmar/` - Confirmar cita
- ✅ `POST /api/agenda/citas/{id}/cancelar/` - Cancelar cita

**Estados de Cita:**
- `PENDIENTE` - Cita creada, no confirmada
- `CONFIRMADA` - Cita confirmada por el paciente
- `ATENDIDA` - ✅ Cita completada (NO usar `COMPLETADA`)
- `CANCELADA` - Cita cancelada

---

## 📦 Dependencias Principales

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # HTTP & API
  http: ^1.1.0
  dio: ^5.4.0                    # Cliente HTTP robusto
  
  # State Management
  provider: ^6.1.1               # Provider (alternativa: riverpod)
  
  # Storage
  shared_preferences: ^2.2.2     # Preferencias locales
  flutter_secure_storage: ^9.0.0 # Almacenamiento seguro (tokens)
  
  # UI & Navigation
  go_router: ^12.1.1             # Navegación declarativa
  intl: ^0.18.1                  # Internacionalización y formatos
  
  # Forms & Validation
  flutter_form_builder: ^9.1.1   # Formularios
  
  # Date & Time
  table_calendar: ^3.0.9         # Calendario
  
  # Notifications
  firebase_messaging: ^14.7.6    # Push notifications
  flutter_local_notifications: ^16.3.0
  
  # UI Enhancements
  flutter_svg: ^2.0.9            # Imágenes SVG
  cached_network_image: ^3.3.0   # Caché de imágenes
  shimmer: ^3.0.0                # Efecto shimmer
  pull_to_refresh: ^2.0.0        # Pull to refresh
  
  # Utils
  url_launcher: ^6.2.2           # Abrir URLs externas
  share_plus: ^7.2.1             # Compartir contenido
```

---

## 🚀 Flujo de Navegación

```
Splash Screen
    ↓
¿Tiene sesión?
    ├── Sí → Home Screen
    └── No → Selector de Clínica → Login/Registro → Home

Home Screen (Tab Navigation)
├── Dashboard (Tab 1)
├── Mis Citas (Tab 2)
├── Tratamientos (Tab 3)
└── Perfil (Tab 4)

Desde cualquier pantalla:
- Agendar Cita (FloatingActionButton)
- Ver Facturas
- Ver Historial Clínico
```

---

## ✅ Características Principales

### Para el Paciente:
1. ✅ **Seleccionar clínica** al inicio (multi-tenant)
2. ✅ **Login/Registro** seguro
3. ✅ **Ver próximas citas** y historial de citas
4. ✅ **Agendar nuevas citas** con disponibilidad en tiempo real
5. ✅ **Cancelar/Reagendar** citas (si está permitido)
6. ✅ **Ver historial clínico** (diagnósticos, procedimientos)
7. ✅ **Ver planes de tratamiento** activos y progreso
8. ✅ **Ver facturas** pendientes y pagadas
9. ✅ **Recibir notificaciones** de recordatorios de citas
10. ✅ **Editar perfil** y cambiar contraseña

### Funcionalidades Técnicas:
- 🔐 Autenticación JWT con refresh token
- 🏢 Multi-tenant (selección de clínica)
- 💾 Almacenamiento seguro de credenciales
- 📱 Notificaciones push
- 🔄 Pull to refresh
- ⚡ Caché de datos
- 🌐 Manejo de estados (loading, error, success)
- 📡 Offline mode (básico)

---

## 🎯 Próximos Pasos

1. **Setup inicial**: Crear proyecto Flutter
2. **Estructura de carpetas**: Organizar arquitectura
3. **Selector de clínica**: Primera pantalla funcional
4. **Autenticación**: Login y registro
5. **Home Dashboard**: Pantalla principal
6. **Citas**: Ver y agendar citas
7. **Tratamientos y Facturas**: Vistas adicionales
8. **Perfil**: Editar información
9. **Notificaciones**: Integrar Firebase
10. **Testing**: Pruebas en Android e iOS

---

## 📝 Notas Importantes

### Multi-Tenant en Flutter:
```dart
// ✅ CORRECTO: Obtener clínicas desde el backend
final response = await http.get(Uri.parse('$baseUrl/'));
final data = json.decode(response.body);
final clinicas = data['clinicas'];  // Array de clínicas

// Al seleccionar clínica, guardamos el dominio REAL
await SharedPreferences.getInstance().then((prefs) {
  prefs.setString('tenant_dominio', clinica['dominio']);  // ej: 'clinicademo1'
  prefs.setString('tenant_name', clinica['nombre']);
});

// En cada petición HTTP, usar el dominio real
headers: {
  'Host': '$dominio.localhost',  // ej: 'clinicademo1.localhost'
  'Authorization': 'Bearer $token',
}

// ❌ INCORRECTO: No usar X-Tenant-ID
```

### Seguridad:
- Tokens JWT en `flutter_secure_storage`
- Preferencias básicas en `shared_preferences`
- Refresh token automático antes de expiración
- Logout automático si el token no se puede renovar

---

**Siguiente:** [01_setup_proyecto.md](01_setup_proyecto.md) - Crear el proyecto Flutter
