# 📱 Guía Flutter - App Administrador Clínica Dental

## 📋 Índice de Documentos

### 🚀 Configuración Inicial
- **[01_CONFIGURACION_PROYECTO.md](01_CONFIGURACION_PROYECTO.md)** - Setup inicial de Flutter y dependencias
- **[02_ESTRUCTURA_PROYECTO.md](02_ESTRUCTURA_PROYECTO.md)** - Organización de carpetas y arquitectura

### 🔐 Autenticación y Networking
- **[03_API_SERVICE.md](03_API_SERVICE.md)** - Cliente HTTP con interceptores y multi-tenant
- **[04_AUTH_SERVICE.md](04_AUTH_SERVICE.md)** - Servicio de autenticación JWT
- **[05_AUTH_PROVIDER.md](05_AUTH_PROVIDER.md)** - Provider de estado de autenticación

### 📊 Dashboard de Reportes (ADMIN)
- **[06_DASHBOARD_SCREEN.md](06_DASHBOARD_SCREEN.md)** - Pantalla principal con estadísticas
- **[07_KPI_CARDS.md](07_KPI_CARDS.md)** - Tarjetas de métricas clave
- **[08_CHARTS_WIDGETS.md](08_CHARTS_WIDGETS.md)** - Gráficos (tendencia, procedimientos, ocupación)
- **[09_REPORTES_SERVICE.md](09_REPORTES_SERVICE.md)** - Servicio para consumir endpoints de reportes
- **[10_EXPORTAR_REPORTES.md](10_EXPORTAR_REPORTES.md)** - Descargar PDF/Excel desde Flutter

### 🔍 Bitácora de Auditoría
- **[11_BITACORA_SCREEN.md](11_BITACORA_SCREEN.md)** - Pantalla de bitácora con filtros
- **[12_BITACORA_SERVICE.md](12_BITACORA_SERVICE.md)** - Servicio para consumir API de bitácora
- **[13_FILTROS_BITACORA.md](13_FILTROS_BITACORA.md)** - Widgets de filtrado avanzado
- **[14_EXPORTAR_BITACORA.md](14_EXPORTAR_BITACORA.md)** - Exportación de registros de auditoría

### 🎨 UI y Temas
- **[15_THEME_CONFIG.md](15_THEME_CONFIG.md)** - Configuración de temas y colores
- **[16_WIDGETS_COMUNES.md](16_WIDGETS_COMUNES.md)** - Componentes reutilizables

---

## 🎯 Objetivo

Esta guía implementa una **app móvil para administradores** con:

1. **Dashboard de Estadísticas**
   - KPIs principales (pacientes, citas, ingresos)
   - Gráfico de tendencia de citas
   - Top procedimientos más realizados
   - Ocupación de odontólogos
   - Exportación a PDF/Excel

2. **Bitácora de Auditoría**
   - Lista de todas las acciones del sistema
   - Filtros avanzados (usuario, acción, fecha, modelo)
   - Búsqueda en tiempo real
   - Estadísticas de actividad
   - Exportación filtrada

---

## 📡 Endpoints del Backend

### Reportes (Dashboard)
```
GET /api/reportes/reportes/dashboard-kpis/
GET /api/reportes/reportes/estadisticas-generales/?formato=pdf
GET /api/reportes/reportes/tendencia-citas/?dias=15&formato=excel
GET /api/reportes/reportes/top-procedimientos/?limite=5&formato=pdf
GET /api/reportes/reportes/ocupacion-odontologos/
GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11
```

### Bitácora (Auditoría)
```
GET /api/reportes/bitacora/?page=1&page_size=20
GET /api/reportes/bitacora/?usuario=1&accion=CREAR&desde=2025-01-01&hasta=2025-12-31
GET /api/reportes/bitacora/estadisticas/?dias=7
GET /api/reportes/bitacora/exportar/?formato=excel&desde=2025-01-01
```

---

## 🔧 Tecnologías

- **Flutter 3.24+** - Framework principal
- **http/dio** - Cliente HTTP
- **provider** - Estado global
- **fl_chart** - Gráficos interactivos
- **path_provider** - Manejo de archivos
- **permission_handler** - Permisos de descarga
- **intl** - Formateo de fechas y moneda

---

## 📱 Pantallas Principales

### 1. Dashboard (Admin)
```
┌─────────────────────────────┐
│  📊 Dashboard Estadísticas  │
├─────────────────────────────┤
│  [KPI1]  [KPI2]  [KPI3]    │
│  [KPI4]  [KPI5]  [KPI6]    │
│                             │
│  📈 Tendencia de Citas      │
│  ┌───────────────────────┐  │
│  │   [Gráfico Línea]     │  │
│  └───────────────────────┘  │
│  [📄 PDF] [📊 Excel]        │
│                             │
│  🏆 Top Procedimientos      │
│  ┌───────────────────────┐  │
│  │   [Gráfico Barras]    │  │
│  └───────────────────────┘  │
│  [📄 PDF] [📊 Excel]        │
│                             │
│  👨‍⚕️ Ocupación Odontólogos  │
│  ┌───────────────────────┐  │
│  │   [Tabla Progreso]    │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### 2. Bitácora (Auditoría)
```
┌─────────────────────────────┐
│  🔍 Bitácora del Sistema    │
├─────────────────────────────┤
│  [Buscar...]  [🔽 Filtros]  │
│                             │
│  Filtros Activos:           │
│  [Usuario: Admin] [✕]       │
│  [Acción: CREAR] [✕]        │
│  [Fecha: Hoy] [✕]           │
│                             │
│  ┌─────────────────────────┐│
│  │ 🟢 CREAR - Cita #123    ││
│  │ Dr. Juan - 10:30 AM     ││
│  │ IP: 192.168.1.1         ││
│  ├─────────────────────────┤│
│  │ 🔵 EDITAR - Paciente #45││
│  │ Admin - 09:15 AM        ││
│  │ IP: 192.168.1.5         ││
│  └─────────────────────────┘│
│                             │
│  [📄 Exportar PDF]          │
│  [📊 Exportar Excel]        │
└─────────────────────────────┘
```

---

## 🚀 Inicio Rápido

### 1. Crear proyecto Flutter
```bash
flutter create clinica_dental_admin
cd clinica_dental_admin
```

### 2. Agregar dependencias en `pubspec.yaml`
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.1
  fl_chart: ^0.65.0
  intl: ^0.18.1
  path_provider: ^2.1.1
  permission_handler: ^11.0.1
  shared_preferences: ^2.2.2
```

### 3. Instalar dependencias
```bash
flutter pub get
```

### 4. Seguir guías en orden
Empieza por **01_CONFIGURACION_PROYECTO.md** y sigue secuencialmente.

---

## 📝 Notas Importantes

### Multi-Tenant
- Todas las peticiones requieren header `X-Tenant: clinica_demo`
- Configurado automáticamente en `ApiService`

### Autenticación JWT
- Token almacenado en `SharedPreferences`
- Auto-refresh con interceptor
- Header: `Authorization: Bearer <token>`

### Exportación de Archivos
- PDF: `Content-Type: application/pdf`
- Excel: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Descarga a carpeta `Downloads` del dispositivo

### Permisos Android
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
```

---

## 🔗 URLs del Backend

- **Producción:** `https://clinica-dental-backend.onrender.com`
- **Tenant:** `clinica_demo`
- **Credenciales Admin:**
  - Email: `admin@clinicademo1.com`
  - Password: `admin123`

---

## 📚 Recursos Adicionales

- [Documentación Flutter](https://docs.flutter.dev/)
- [fl_chart Examples](https://github.com/imaNNeo/fl_chart)
- [Provider Pattern](https://docs.flutter.dev/data-and-backend/state-mgmt/simple)
- [HTTP Requests in Flutter](https://docs.flutter.dev/cookbook/networking/fetch-data)

---

## ✅ Checklist de Implementación

- [ ] 01 - Configurar proyecto Flutter
- [ ] 02 - Definir estructura de carpetas
- [ ] 03 - Implementar ApiService
- [ ] 04 - Implementar AuthService
- [ ] 05 - Configurar AuthProvider
- [ ] 06 - Crear DashboardScreen
- [ ] 07 - Implementar KPI Cards
- [ ] 08 - Agregar gráficos (fl_chart)
- [ ] 09 - Implementar ReportesService
- [ ] 10 - Función de exportación PDF/Excel
- [ ] 11 - Crear BitacoraScreen
- [ ] 12 - Implementar BitacoraService
- [ ] 13 - Widgets de filtros avanzados
- [ ] 14 - Exportación de bitácora
- [ ] 15 - Configurar tema y colores
- [ ] 16 - Widgets comunes reutilizables

---

**🏥 ¡Comienza con la documentación y construye tu app de administración!**
