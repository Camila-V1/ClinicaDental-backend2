# 📋 Índice de Guías para Panel de Administración

## 🎯 Objetivo
Este directorio contiene las guías para implementar el panel completo de administración de la clínica dental, donde cada administrador verá y gestionará únicamente la información de su propia clínica (multi-tenant).

---

## 📚 Guías Disponibles

### 1. Dashboard Principal
- **Archivo:** `01_dashboard_admin.md`
- **Contenido:** Vista principal con KPIs, gráficos y resumen ejecutivo
- **Componentes:** Tarjetas de métricas, gráficos de tendencias, alertas

### 2. Gestión de Usuarios
- **Archivo:** `02_gestion_usuarios.md`
- **Contenido:** CRUD de odontólogos, recepcionistas y administradores
- **Componentes:** Tabla de usuarios, formularios, asignación de permisos

### 3. Gestión de Pacientes
- **Archivo:** `03_gestion_pacientes.md`
- **Contenido:** Listado, búsqueda y visualización de pacientes
- **Componentes:** Tabla filtrable, perfiles detallados, historial resumido

### 4. Agenda y Citas
- **Archivo:** `04_agenda_citas.md`
- **Contenido:** Calendario, gestión de citas, disponibilidad
- **Componentes:** Vista calendario, modal de citas, filtros por odontólogo

### 5. Tratamientos y Servicios
- **Archivo:** `05_tratamientos_servicios.md`
- **Contenido:** Catálogo de servicios, planes de tratamiento activos
- **Componentes:** Gestión de servicios, seguimiento de tratamientos

### 6. Facturación y Pagos
- **Archivo:** `06_facturacion_pagos.md`
- **Contenido:** Facturas, pagos, cuentas por cobrar
- **Componentes:** Lista de facturas, registros de pagos, reportes financieros

### 7. Inventario
- **Archivo:** `07_inventario.md`
- **Contenido:** Control de insumos, alertas de stock, movimientos
- **Componentes:** Lista de productos, registro de movimientos, alertas

### 8. Reportes y Estadísticas
- **Archivo:** `08_reportes_estadisticas.md`
- **Contenido:** Todos los reportes dinámicos con exportación
- **Componentes:** Filtros dinámicos, gráficos, exportación PDF/Excel

### 9. Bitácora de Auditoría
- **Archivo:** `09_bitacora_auditoria.md`
- **Contenido:** Registro de acciones, búsqueda de eventos
- **Componentes:** Timeline de eventos, filtros avanzados, exportación

### 10. Configuración de Clínica
- **Archivo:** `10_configuracion_clinica.md`
- **Contenido:** Datos de la clínica, horarios, personalización
- **Componentes:** Formulario de configuración, logo, temas

---

## 🏗️ Arquitectura del Panel Admin

### Estructura de Componentes
```
src/
├── pages/
│   └── admin/
│       ├── Dashboard.tsx
│       ├── Usuarios.tsx
│       ├── Pacientes.tsx
│       ├── Agenda.tsx
│       ├── Tratamientos.tsx
│       ├── Facturacion.tsx
│       ├── Inventario.tsx
│       ├── Reportes.tsx
│       ├── Bitacora.tsx
│       └── Configuracion.tsx
├── components/
│   └── admin/
│       ├── Sidebar.tsx
│       ├── Header.tsx
│       ├── KPICard.tsx
│       ├── ChartWidget.tsx
│       ├── DataTable.tsx
│       └── FilterPanel.tsx
└── services/
    └── admin/
        ├── dashboardService.ts
        ├── usuariosService.ts
        ├── reportesService.ts
        └── bitacoraService.ts
```

### Flujo de Datos Multi-Tenant
```
1. Usuario hace login
2. Backend valida credenciales y retorna:
   - Token JWT
   - Datos del usuario
   - Información del tenant (clínica)
3. Frontend almacena:
   - Token en localStorage
   - Tenant info en context
4. Todas las peticiones incluyen:
   - Header: Authorization: Bearer {token}
   - Subdomain detectado automáticamente
5. Backend filtra datos por tenant automáticamente
```

---

## 🎨 Diseño y UX

### Paleta de Colores Sugerida
```css
/* Colores principales */
--primary: #1e3a8a;      /* Azul oscuro */
--secondary: #3b82f6;    /* Azul medio */
--success: #10b981;      /* Verde */
--warning: #f59e0b;      /* Naranja */
--danger: #ef4444;       /* Rojo */
--info: #06b6d4;         /* Cyan */

/* Neutros */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-800: #1f2937;
--gray-900: #111827;
```

### Componentes UI Recomendados
- **Tablas:** TanStack Table (React Table v8)
- **Gráficos:** Chart.js + react-chartjs-2
- **Formularios:** React Hook Form + Zod
- **Calendario:** FullCalendar
- **Iconos:** Lucide React o Heroicons
- **Notificaciones:** React Hot Toast
- **Modales:** Headless UI

---

## 🔐 Seguridad y Permisos

### Niveles de Acceso
```typescript
enum UserRole {
  ADMIN = 'ADMIN',           // Acceso total a su clínica
  ODONTOLOGO = 'ODONTOLOGO', // Solo sus pacientes y citas
  RECEPCIONISTA = 'RECEPCIONISTA', // Citas, pagos, pacientes
  PACIENTE = 'PACIENTE'      // Solo datos propios
}
```

### Guards de Rutas
```typescript
// Ejemplo de protección
<Route 
  path="/admin/*" 
  element={
    <RequireAuth roles={['ADMIN']}>
      <AdminLayout />
    </RequireAuth>
  } 
/>
```

---

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile first */
sm: 640px   /* Tablets */
md: 768px   /* Tablets landscape */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

### Adaptaciones
- **Mobile:** Sidebar colapsable, tablas con scroll horizontal
- **Tablet:** Sidebar semi-colapsado, grid de 2 columnas
- **Desktop:** Sidebar completo, grid de 3-4 columnas

---

## 🚀 Orden de Implementación Sugerido

1. ✅ **Dashboard** - Vista principal con datos básicos
2. ✅ **Gestión de Usuarios** - CRUD de equipo de trabajo
3. ✅ **Gestión de Pacientes** - Visualización y búsqueda
4. ✅ **Agenda** - Calendario y gestión de citas
5. ✅ **Facturación** - Control financiero básico
6. ✅ **Inventario** - Control de stock
7. ✅ **Tratamientos** - Seguimiento de planes
8. ✅ **Reportes** - Análisis y exportación
9. ✅ **Bitácora** - Auditoría de acciones
10. ✅ **Configuración** - Personalización final

---

## 📦 Dependencias Frontend Necesarias

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.0",
    "@tanstack/react-table": "^8.10.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@headlessui/react": "^1.7.17",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0",
    "lucide-react": "^0.294.0",
    "react-hot-toast": "^2.4.1",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "@fullcalendar/react": "^6.1.9",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

---

## 🔄 Estado Global Sugerido

```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials) => Promise<void>;
  logout: () => void;
}

// stores/adminStore.ts
interface AdminState {
  kpis: KPIData | null;
  loadingKpis: boolean;
  fetchKpis: () => Promise<void>;
}
```

---

## 📝 Notas Importantes

### Multi-Tenancy
- **Automático:** El backend filtra datos por subdomain automáticamente
- **No necesitas:** Enviar tenant_id en cada request
- **Solo necesitas:** Token JWT válido en headers

### Errores Comunes
1. ❌ No incluir token en headers → 401 Unauthorized
2. ❌ Acceder sin login → Redirect a /login
3. ❌ Usuario sin permisos → 403 Forbidden
4. ❌ Subdomain incorrecto → 404 Tenant not found

### Best Practices
- ✅ Usar React Query para cache de datos
- ✅ Validar formularios con Zod
- ✅ Manejar errores con try-catch
- ✅ Mostrar loading states
- ✅ Implementar paginación en tablas grandes
- ✅ Usar debounce en búsquedas
- ✅ Optimizar re-renders con memo/callback

---

## 🎓 Recursos Útiles

- **React Query:** https://tanstack.com/query/latest
- **React Table:** https://tanstack.com/table/v8
- **React Hook Form:** https://react-hook-form.com/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Chart.js:** https://www.chartjs.org/docs/latest/
- **FullCalendar:** https://fullcalendar.io/docs/react

---

**Última actualización:** 20/11/2025  
**Versión:** 1.0
