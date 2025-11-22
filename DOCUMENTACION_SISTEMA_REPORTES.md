# 📊 DOCUMENTACIÓN DEL SISTEMA DE REPORTES

**Fecha de Generación:** 22 de noviembre de 2025, 18:48  
**Proyecto:** Clínica Dental - Dashboard Administrador  
**Objetivo:** Mapeo completo del flujo de datos desde Backend → Frontend → UI

---

## 📋 TABLA DE CONTENIDOS

1. [Arquitectura General](#arquitectura-general)
2. [Endpoints del Backend](#endpoints-del-backend)
3. [Servicios Frontend](#servicios-frontend)
4. [Componentes UI](#componentes-ui)
5. [Flujo de Datos Completo](#flujo-de-datos-completo)
6. [Problemas Conocidos](#problemas-conocidos)
7. [Soluciones Implementadas](#soluciones-implementadas)

---

## 🏗️ ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Django)                       │
│                 https://clinica-dental-backend              │
│                     .onrender.com                           │
├─────────────────────────────────────────────────────────────┤
│  📡 API Endpoints                                           │
│  ├── /api/reportes/reportes/dashboard-kpis/                │
│  ├── /api/reportes/reportes/estadisticas-generales/        │
│  ├── /api/reportes/reportes/tendencia-citas/               │
│  ├── /api/reportes/reportes/top-procedimientos/            │
│  ├── /api/reportes/reportes/ocupacion-odontologos/         │
│  ├── /api/reportes/reportes/reporte-financiero/            │
│  └── /api/reportes/bitacora/                               │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE SERVICIOS (Frontend)               │
│  📁 src/services/                                           │
├─────────────────────────────────────────────────────────────┤
│  🔷 adminDashboardService.ts                                │
│     - getKPIs()                                             │
│     - getTendenciaCitas()                                   │
│     - getTopProcedimientos()                                │
│     - getEstadisticasGenerales()                            │
│     - getOcupacionOdontologos()                             │
│     - getReporteFinanciero()                                │
│     - getStockBajo()                                        │
│     - getActividadReciente()                                │
│                                                             │
│  🔷 reportesService.ts                                      │
│     - getDashboardKpis()                                    │
│     - getEstadisticasGenerales()                            │
│     - getTendenciaCitas()                                   │
│     - getTopProcedimientos()                                │
│     - getReporteFinanciero()                                │
│     - getOcupacionOdontologos()                             │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│                    COMPONENTES UI (React)                   │
│  📁 src/pages/admin/ & src/components/admin/                │
├─────────────────────────────────────────────────────────────┤
│  🎨 Dashboard.tsx (Página Principal)                        │
│     ├── DashboardKPIs.tsx (Tarjetas superiores)            │
│     ├── StatsGrid.tsx (Estadísticas generales)             │
│     ├── TendenciaCitasChart.tsx (Gráfico de líneas)        │
│     ├── TopProcedimientosChart.tsx (Top 5)                 │
│     ├── ReporteFinanciero.tsx (Resumen financiero)         │
│     ├── OcupacionOdontologos.tsx (Tabla ocupación)         │
│     ├── AlertList.tsx (Stock bajo)                         │
│     └── ActivityTimeline.tsx (Bitácora)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 ENDPOINTS DEL BACKEND

### 1. Dashboard KPIs

**URL:** `GET /api/reportes/reportes/dashboard-kpis/`

**Descripción:** Retorna los KPIs principales del dashboard (tarjetas superiores).

**Respuesta Real del Backend:**
```json
[
  {"etiqueta": "Pacientes Activos", "valor": "5.00"},
  {"etiqueta": "Citas Hoy", "valor": "1.00"},
  {"etiqueta": "Ingresos Este Mes", "valor": "280.00"},
  {"etiqueta": "Saldo Pendiente", "valor": "75.00"}
]
```

**Estructura Esperada por Frontend:**
```typescript
interface DashboardKPIs {
  total_pacientes: number;      // Mapeado de "Pacientes Activos"
  citas_hoy: number;            // Mapeado de "Citas Hoy"
  ingresos_mes: string;         // Mapeado de "Ingresos Este Mes"
  tratamientos_activos: number; // NO viene del backend (se obtiene de estadisticas-generales)
  pacientes_nuevos_mes: number; // NO viene del backend (se obtiene de estadisticas-generales)
  tasa_ocupacion: string;       // NO viene del backend (se obtiene de estadisticas-generales)
  citas_pendientes: number;     // NO viene del backend (se obtiene de estadisticas-generales)
  facturas_pendientes: number;  // Mapeado de "Saldo Pendiente"
}
```

**⚠️ PROBLEMA IDENTIFICADO:**
- Backend envía `etiqueta` y `valor`, pero inicialmente el frontend buscaba `key` y `value`
- **Solución:** Actualizado mapeo en `adminDashboardService.ts` línea 52

---

### 2. Estadísticas Generales

**URL:** `GET /api/reportes/reportes/estadisticas-generales/`

**Descripción:** Estadísticas completas del sistema (grid inferior del dashboard).

**Respuesta Real del Backend:**
```json
{
  "total_pacientes_activos": 5,
  "pacientes_nuevos_mes": 5,
  "total_odontologos": 1,
  "citas_mes_actual": 7,
  "citas_completadas": 0,
  "citas_pendientes": 4,
  "citas_canceladas": 0,
  "facturas_vencidas": 1,
  "ingresos_mes_actual": 280,
  "monto_pendiente": 75,
  "pacientes_nuevos_mes": 5,
  "planes_activos": 1,
  "promedio_factura": 118.33333333333333,
  "tasa_ocupacion": 28.57,
  "total_procedimientos": 1,
  "tratamientos_completados": 0
}
```

**Estructura Frontend:**
```typescript
interface EstadisticasGenerales {
  // Pacientes
  total_pacientes_activos: number;
  pacientes_nuevos_mes: number;
  
  // Odontólogos
  total_odontologos: number;
  
  // Citas
  citas_mes_actual: number;
  citas_completadas: number;
  citas_pendientes: number;
  citas_canceladas: number;
  
  // Tratamientos
  planes_activos: number;
  planes_completados: number;
  total_procedimientos: number;
  
  // Financiero
  total_pagado_mes: string;
  monto_pendiente: string;
  facturas_vencidas: number;
  promedio_factura: string;
  
  // Ocupación
  tasa_ocupacion: string;
}
```

**✅ CORRECTO:** No requiere mapeo, el backend ya envía el formato exacto.

---

### 3. Tendencia de Citas

**URL:** `GET /api/reportes/reportes/tendencia-citas/?dias=15`

**Descripción:** Datos para el gráfico de tendencia de citas por día.

**Respuesta ACTUAL del Backend (INCOMPLETA):**
```json
[
  {"fecha": "2025-11-08", "cantidad": 0},
  {"fecha": "2025-11-09", "cantidad": 0},
  {"fecha": "2025-11-10", "cantidad": 0}
]
```

**Respuesta ESPERADA (Después de corrección backend):**
```json
[
  {
    "fecha": "2025-11-08",
    "cantidad": 3,
    "completadas": 2,
    "canceladas": 1
  }
]
```

**Estructura Frontend:**
```typescript
interface TendenciaCitas {
  fecha: string;
  total: number;        // Mapeado de "cantidad"
  completadas: number;  // ❌ Falta en backend actual
  canceladas: number;   // ❌ Falta en backend actual
}
```

**⚠️ PROBLEMA IDENTIFICADO:**
- Backend NO envía `completadas` ni `canceladas` separadas
- **Solución:** Actualizar `reportes/views.py` línea 206 (ver CORRECCION_REPORTES_BACKEND.md)

---

### 4. Top Procedimientos

**URL:** `GET /api/reportes/reportes/top-procedimientos/?limite=5`

**Descripción:** Top 5 procedimientos más realizados.

**Respuesta Real del Backend:**
```json
[
  {"etiqueta": "Control Ortodoncia", "valor": "6.00"},
  {"etiqueta": "Corona Dental", "valor": "2.00"},
  {"etiqueta": "Consulta General", "valor": "1.00"},
  {"etiqueta": "Endodoncia", "valor": "1.00"},
  {"etiqueta": "Instalación Ortodoncia", "valor": "1.00"}
]
```

**Estructura Frontend:**
```typescript
interface TopProcedimiento {
  nombre: string;       // Mapeado de "etiqueta"
  cantidad: number;     // Mapeado de "valor"
  porcentaje: string;   // ✅ Calculado en frontend
}
```

**✅ SOLUCIÓN IMPLEMENTADA:**
- Frontend calcula el porcentaje: `(cantidad / totalCantidad) * 100`
- Ver `reportesService.ts` línea 200

---

### 5. Ocupación de Odontólogos

**URL:** `GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-11`

**Descripción:** Tasa de ocupación y estadísticas por odontólogo.

**Respuesta Real del Backend:**
```json
[
  {
    "usuario_id": 360,
    "nombre_completo": "Dr. Juan Pérez",
    "total_citas": 7,
    "citas_completadas": 0,
    "citas_canceladas": 0,
    "horas_ocupadas": 0,
    "tasa_ocupacion": "0.00",
    "pacientes_atendidos": 0
  }
]
```

**Estructura Frontend:**
```typescript
interface OcupacionOdontologo {
  usuario_id: number;          // ✅ Correcto
  nombre_completo: string;     // ✅ Correcto
  total_citas: number;
  citas_completadas: number;
  citas_canceladas: number;
  horas_ocupadas: number;
  tasa_ocupacion: string;
  pacientes_atendidos: number;
}
```

**⚠️ NOTA:**
- `citas_completadas = 0` es CORRECTO porque no hay citas con estado "COMPLETADA"
- Para ver datos reales, cambiar el estado de algunas citas a "COMPLETADA" en la agenda

---

### 6. Reporte Financiero

**URL:** `GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11`

**Descripción:** Resumen financiero del mes.

**Respuesta Real del Backend:**
```json
{
  "periodo": "2025-11",
  "total_facturado": "355.00",
  "total_pagado": "280.00",
  "saldo_pendiente": "75.00",
  "numero_facturas": 3
}
```

**Estructura Frontend:**
```typescript
interface ReporteFinanciero {
  periodo: string;
  total_facturado: string;
  total_pagado: string;
  saldo_pendiente: string;
  numero_facturas: number;
  ingresos_por_metodo?: {
    EFECTIVO: string;
    TARJETA: string;
    TRANSFERENCIA: string;
    CHEQUE: string;
  };
}
```

**✅ CORRECTO:** No requiere mapeo especial.

---

### 7. Stock Bajo

**URL:** `GET /api/inventario/insumos/bajo_stock/?page_size=10`

**Descripción:** Insumos con stock por debajo del mínimo.

**Respuesta Real del Backend:**
```json
[]  // Sin insumos con stock bajo actualmente
```

---

### 8. Actividad Reciente (Bitácora)

**URL:** `GET /api/reportes/bitacora/?page=1&page_size=10`

**Descripción:** Últimas acciones registradas en el sistema (auditoría).

**Respuesta Real del Backend:**
```json
[
  {
    "id": 13,
    "usuario": {
      "id": 436,
      "nombre_completo": "Administrador Principal",
      "email": "admin@clinica-demo.com",
      "tipo_usuario": "ADMIN"
    },
    "accion": "LOGIN",
    "accion_display": "Inicio de sesión",
    "descripcion": "Inicio de sesión exitoso - Administrador Principal",
    "detalles": {
      "email": "admin@clinica-demo.com",
      "tipo_usuario": "ADMIN"
    },
    "fecha_hora": "2025-11-22T23:27:35.259677Z",
    "ip_address": "189.28.77.175",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "modelo": null,
    "object_id": null
  }
]
```

**Estructura Frontend CORRECTA:**
```typescript
interface BitacoraLog {
  id: number;
  usuario: {                    // ✅ OBJECT, no string
    id: number;
    nombre_completo: string;
    email: string;
    tipo_usuario: string;
  };
  accion: string;               // LOGIN, CREAR, EDITAR, ELIMINAR
  accion_display: string;       // "Inicio de sesión", "Crear", etc.
  descripcion: string;          // Descripción detallada
  detalles: object;             // JSON con información adicional
  fecha_hora: string;           // ✅ "fecha_hora", NO "timestamp"
  ip_address: string | null;    // IP del usuario
  user_agent: string | null;    // Navegador del usuario
  modelo: string | null;        // Modelo afectado (Cita, Factura, etc.)
  object_id: string | null;     // ID del objeto afectado
}
```

**⚠️ PROBLEMA COMÚN - Bitácora no se muestra:**

**Síntoma:**
- Backend envía 13 registros correctamente
- Console.log muestra: `Array(13)` con datos completos
- Frontend muestra: "📋 No hay registros"

**Causas posibles:**

1. **Mapeo incorrecto en el servicio:**
   ```typescript
   // ❌ INCORRECTO - Backend NO envía estos campos
   const logs = response.data.map(item => ({
     usuario: item.usuario.nombre_completo,  // ❌ Convierte object → string
     timestamp: item.fecha_hora               // ❌ Renombra campo
   }));
   
   // ✅ CORRECTO - Usar datos tal como los envía backend
   const logs = response.data.map(item => ({
     ...item,  // Mantener estructura original
     // Solo transformar si el componente lo requiere específicamente
   }));
   ```

2. **Filtro incorrecto en componente:**
   ```typescript
   // ❌ INCORRECTO - Filtra registros válidos
   const registrosValidos = bitacoras.filter(b => b.usuario?.id);
   
   // ✅ CORRECTO - No filtrar
   const registrosValidos = bitacoras;
   ```

3. **Componente espera campos diferentes:**
   ```typescript
   // Si el componente renderiza:
   <div>{log.timestamp}</div>  // ❌ Campo no existe
   
   // Debe usar:
   <div>{log.fecha_hora}</div>  // ✅ Campo correcto
   
   // O si el componente espera:
   <div>{log.usuario}</div>     // ❌ Renderizaría [object Object]
   
   // Debe usar:
   <div>{log.usuario.nombre_completo}</div>  // ✅ Acceso correcto
   ```

**Componentes Frontend:**
- `ActivityTimeline.tsx` - Timeline visual en Dashboard
- `BitacoraLogsList.tsx` - Lista completa con paginación

**Verificación en Consola:**
```javascript
// Buscar estos logs:
console.log('📊 Bitácora recibida:', bitacoras);
console.log('📊 Cantidad:', bitacoras.length);
console.log('📊 Primer registro:', bitacoras[0]);

// Si ves:
// ✅ "Cantidad: 13" pero UI muestra "No hay registros"
// → Problema: Componente filtra/valida incorrectamente

// Si ves que bitacoras[0].usuario es un OBJECT:
// → ✅ Backend correcto, componente debe acceder a .nombre_completo

// Si ves que bitacoras[0].usuario es un STRING:
// → ❌ Servicio transformó incorrectamente, eliminar mapeo
```

**✅ CORRECTO (adminDashboardService.ts):**
```typescript
async getActividadReciente() {
  try {
    const { data } = await api.get('/api/reportes/bitacora/', { 
      params: { page: 1, page_size: 10 } 
    });
    
    // NO transformar - backend envía formato correcto
    if (data && Array.isArray(data.results)) return data.results;
    if (Array.isArray(data)) return data;
    return [];
  } catch (error: any) {
    console.error('🔴 Error Bitácora:', error);
    return [];
  }
}
```

**✅ CORRECTO (Componente de renderizado):**
```tsx
{bitacoras.map((log) => (
  <div key={log.id}>
    {/* ✅ Acceso correcto al objeto usuario */}
    <p>{log.usuario.nombre_completo}</p>
    <p>{log.usuario.email}</p>
    
    {/* ✅ Campo correcto de fecha */}
    <p>{new Date(log.fecha_hora).toLocaleString()}</p>
    
    {/* ✅ Acción con display legible */}
    <p>{log.accion_display}</p>
    
    {/* ✅ Descripción */}
    <p>{log.descripcion}</p>
    
    {/* ✅ Información técnica (opcional) */}
    {log.ip_address && <p>IP: {log.ip_address}</p>}
    {log.user_agent && <p className="text-xs">{log.user_agent}</p>}
  </div>
))}
```

---

## 🔷 SERVICIOS FRONTEND

### 1. adminDashboardService.ts

**Ubicación:** `src/services/admin/adminDashboardService.ts`

**Función:** Servicio principal que consolida todos los datos del dashboard.

#### Método: `getKPIs()`

**Líneas:** 26-103

**Entrada:** Ninguna

**Proceso:**
1. Llama a `/api/reportes/reportes/dashboard-kpis/`
2. Recibe array de objetos con `etiqueta` y `valor`
3. Aplica **ADAPTADOR** para convertir Array → Objeto
4. Mapea cada etiqueta a su campo correspondiente:
   - "Pacientes Activos" → `total_pacientes`
   - "Citas Hoy" → `citas_hoy`
   - "Ingresos Este Mes" → `ingresos_mes`
   - "Saldo Pendiente" → `facturas_pendientes`

**Salida:**
```typescript
{
  total_pacientes: 5,
  citas_hoy: 1,
  ingresos_mes: "280.00",
  tratamientos_activos: 0,
  pacientes_nuevos_mes: 0,
  tasa_ocupacion: 0,
  citas_pendientes: 0,
  facturas_pendientes: 75
}
```

**Código Clave (Línea 52-79):**
```typescript
if (Array.isArray(data)) {
  data.forEach((item: any) => {
    const rawKey = item.etiqueta || item.key || item.label || ''; 
    const key = String(rawKey).toLowerCase().replace(/ /g, '_');
    const value = Number(item.valor || item.value || 0);

    if (key.includes('pacientes') && (key.includes('activos') || key.includes('total'))) {
      kpisFormatted.total_pacientes = value;
    } else if (key.includes('citas') && key.includes('hoy')) {
      kpisFormatted.citas_hoy = value;
    }
    // ... más mapeos
  });
}
```

---

#### Método: `getTendenciaCitas(dias: number)`

**Líneas:** 109-116

**Entrada:** `dias` (número de días hacia atrás, default: 15)

**Proceso:**
1. Llama a `/api/reportes/reportes/tendencia-citas/?dias={dias}`
2. Retorna el array directamente (NO mapea porque backend ya envía el formato correcto)

**Salida:**
```typescript
[
  {fecha: '2025-11-08', cantidad: 0},
  {fecha: '2025-11-09', cantidad: 0}
]
```

---

#### Método: `getOcupacionOdontologos()`

**Líneas:** 159-194

**Entrada:** Ninguna

**Proceso:**
1. Llama a `/api/reportes/reportes/ocupacion-odontologos/`
2. Mapea campos del backend al formato UI:
   - `usuario_id` → `odontologo_id`
   - `nombre_completo` → `odontologo_nombre`

**Salida:**
```typescript
[
  {
    odontologo_id: 360,
    odontologo_nombre: "Dr. Juan Pérez",
    total_citas: 7,
    citas_completadas: 0,
    horas_ocupadas: 0,
    tasa_ocupacion: "0.00",
    pacientes_atendidos: 0
  }
]
```

---

### 2. reportesService.ts

**Ubicación:** `src/services/reportesService.ts`

**Función:** Servicio alternativo con lógica duplicada (usado en algunos componentes).

**Nota:** Algunos componentes llaman directamente a `reportesService` en lugar de `adminDashboardService`. Ambos tienen lógica similar pero con logs diferentes.

---

## 🎨 COMPONENTES UI

### 1. Dashboard.tsx

**Ubicación:** `src/pages/admin/Dashboard.tsx`

**Función:** Página principal del dashboard que orquesta todos los componentes.

**React Query Keys:**
```typescript
['dashboard-kpis']                 // KPIs principales
['tendencia-citas', 15]            // Tendencia de 15 días
['top-procedimientos', 5]          // Top 5 procedimientos
['estadisticas-generales']         // Grid de estadísticas
['ocupacion-odontologos']          // Tabla de ocupación
['reporte-financiero', periodo]    // Resumen financiero
['stock-bajo']                     // Alertas de inventario
['actividad-reciente']             // Bitácora
```

**Estructura Visual:**
```
┌────────────────────────────────────────────────────┐
│  📊 Dashboard Administrador              🔄 Refetch │
├────────────────────────────────────────────────────┤
│  [DashboardKPIs] - Tarjetas superiores (4 KPIs)   │
├────────────────────────────────────────────────────┤
│  [StatsGrid] - Grid de estadísticas (15 items)    │
├────────────────────────────────────────────────────┤
│  [TendenciaCitasChart]  │  [TopProcedimientos]    │
│  Gráfico de líneas      │  Lista con barras       │
├─────────────────────────┼─────────────────────────┤
│  [ReporteFinanciero]    │  [OcupacionOdontologos] │
│  Card financiero        │  Tabla de odontólogos   │
├─────────────────────────┴─────────────────────────┤
│  [AlertList]           │  [ActivityTimeline]      │
│  Stock bajo            │  Bitácora                │
└────────────────────────────────────────────────────┘
```

---

### 2. DashboardKPIs.tsx

**Ubicación:** `src/components/admin/DashboardKPIs.tsx`

**Props:**
```typescript
interface Props {
  kpis: DashboardKPIs;
  loading: boolean;
}
```

**Renderiza:**
- 4 tarjetas con iconos:
  1. 👥 Total Pacientes
  2. 📅 Citas Hoy
  3. 💰 Ingresos del Mes
  4. ⚡ Tratamientos Activos

**Código Clave:**
```tsx
<div className="...">
  <Users className="w-8 h-8 text-blue-500" />
  <div>
    <p className="text-sm text-gray-600">Total Pacientes</p>
    <p className="text-2xl font-bold">{kpis.total_pacientes}</p>
  </div>
</div>
```

---

### 3. TendenciaCitasChart.tsx

**Ubicación:** `src/components/admin/TendenciaCitasChart.tsx`

**Props:**
```typescript
interface Props {
  data: TendenciaCita[];
  loading: boolean;
}
```

**Renderiza:**
- ✅ Gráfico de barras agrupadas (NO líneas)
- ✅ **3 barras por fecha:** Total (azul), Completadas (verde), Canceladas (rojo)
- ✅ Leyenda superior con indicadores de color
- ✅ Etiquetas de fecha formateadas (mes corto + día)
- ✅ Tooltips con valores al hacer hover

**Estado Actual:**
- ✅ **Componente CORRECTO:** Ya renderiza las 3 barras
- ⚠️ **Backend INCOMPLETO:** Solo envía `cantidad` (falta `completadas` y `canceladas`)
- 🔄 **Resultado Visual:** Solo la barra "Total" tiene altura, las otras están en 0

**Código Actual del Componente (Líneas 70-108):**
```tsx
{data.map((item, index) => {
  const totalHeight = (item.total / maxValue) * chartHeight;
  const completadasHeight = (item.completadas / maxValue) * chartHeight;  // ✅
  const canceladasHeight = (item.canceladas / maxValue) * chartHeight;    // ✅

  return (
    <div key={index} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{ width: '100%', display: 'flex', gap: '2px' }}>
        {/* Total Bar (Azul) */}
        <div style={{ width: '30%', height: totalHeight, background: '#3b82f6' }}>
          {item.total > 0 && <span>{item.total}</span>}
        </div>
        
        {/* Completadas Bar (Verde) ✅ */}
        <div style={{ width: '30%', height: completadasHeight, background: '#10b981' }} />
        
        {/* Canceladas Bar (Rojo) ✅ */}
        <div style={{ width: '30%', height: canceladasHeight, background: '#ef4444' }} />
      </div>
      
      <div style={{ fontSize: '10px' }}>
        {formatFecha(item.fecha)}
      </div>
    </div>
  );
})}
```

**Conclusión:**
- ✅ Frontend **NO necesita cambios**
- ❌ Backend debe actualizar endpoint `tendencia-citas` para incluir campos faltantes
- 📋 Ver sección "Corrección Backend Requerida" más abajo

**Datos que el componente espera recibir:**
```typescript
interface TendenciaCitas {
  fecha: string;        // "2025-11-22"
  total: number;        // Todas las citas del día
  completadas: number;  // ❌ Backend NO envía (siempre 0)
  canceladas: number;   // ❌ Backend NO envía (siempre 0)
}
```

**Datos que el backend actualmente envía:**
```json
{
  "fecha": "2025-11-22",
  "cantidad": 1  // Solo este campo
}
```

**Mapeo en reportesService.ts (Línea 175-179):**
```typescript
const resultado = data.map((item: any) => ({
  fecha: item.fecha,
  total: Number(item.cantidad || item.total || 0),  // ✅ Mapea cantidad → total
  completadas: Number(item.completadas || 0),        // ⚠️ Siempre 0 (backend no envía)
  canceladas: Number(item.canceladas || 0)           // ⚠️ Siempre 0 (backend no envía)
}));
```

---

### 4. OcupacionOdontologos.tsx

**Ubicación:** `src/components/admin/OcupacionOdontologos.tsx`

**Props:**
```typescript
interface Props {
  ocupacion: OcupacionOdontologo[];
  loading: boolean;
}
```

**Renderiza:**
- Tabla con columnas:
  1. Odontólogo (ID + Nombre)
  2. Total Citas
  3. Completadas
  4. Tasa de Ocupación (%)
  5. Horas Trabajadas
  6. Pacientes Atendidos

**Código Clave (Línea 45-60):**
```tsx
{ocupacion.map((odontologo) => (
  <tr key={odontologo.usuario_id}>
    <td>
      {odontologo.nombre_completo}
      <span className="text-xs">ID: {odontologo.usuario_id}</span>
    </td>
    <td>{odontologo.total_citas}</td>
    <td>{odontologo.citas_completadas} / {odontologo.total_citas}</td>
    <td>{odontologo.tasa_ocupacion}%</td>
    <td>{odontologo.horas_ocupadas}h</td>
    <td>{odontologo.pacientes_atendidos}</td>
  </tr>
))}
```

---

## 🔄 FLUJO DE DATOS COMPLETO

### Ejemplo: Dashboard KPIs

```
1. Usuario abre /dashboard
   ⬇️
2. Dashboard.tsx se monta
   ⬇️
3. useQuery ejecuta adminDashboardService.getKPIs()
   ⬇️
4. Service hace fetch a /api/reportes/reportes/dashboard-kpis/
   ⬇️
5. Backend Django retorna:
   [
     {"etiqueta": "Pacientes Activos", "valor": "5.00"},
     {"etiqueta": "Citas Hoy", "valor": "1.00"}
   ]
   ⬇️
6. Service aplica adaptador Array → Objeto:
   {
     total_pacientes: 5,
     citas_hoy: 1,
     ingresos_mes: "280.00"
   }
   ⬇️
7. Dashboard.tsx recibe data en variable 'kpis'
   ⬇️
8. Pasa kpis a <DashboardKPIs kpis={kpis} />
   ⬇️
9. DashboardKPIs.tsx renderiza 4 tarjetas con los valores
   ⬇️
10. Usuario ve:
    👥 Total Pacientes: 5
    📅 Citas Hoy: 1
    💰 Ingresos: $280.00
```

---

## ⚠️ PROBLEMAS CONOCIDOS

### 1. KPIs mostrando 0 (SOLUCIONADO ✅)

**Síntoma:**
```
total_pacientes: 0
citas_hoy: 0
ingresos_mes: "0"
```

**Causa:**
- Backend envía `etiqueta` y `valor`
- Frontend buscaba `key` y `value`

**Solución:**
- Actualizado `adminDashboardService.ts` línea 52
- Ahora busca `item.etiqueta` primero, luego `item.key` como fallback

---

### 2. Tendencia sin completadas/canceladas

**Síntoma:**
```json
{"fecha": "2025-11-08", "cantidad": 0}
// ❌ Falta: completadas, canceladas
```

**Causa:**
- Backend solo cuenta citas totales
- `reportes/views.py` línea 206 excluye canceladas sin contarlas

**Solución:**
- Ver `CORRECCION_REPORTES_BACKEND.md`
- Actualizar función `tendencia_citas` en Django

---

### 3. Ocupación en 0% (NO ES ERROR ✅)

**Síntoma:**
```json
{
  "citas_completadas": 0,
  "horas_ocupadas": 0,
  "tasa_ocupacion": "0.00"
}
```

**Causa:**
- NO hay citas con estado "COMPLETADA" en la base de datos
- `tasa_ocupacion = citas_completadas / total_citas = 0 / 7 = 0%`

**Solución:**
- Cambiar el estado de algunas citas a "COMPLETADA" en la agenda
- NO es un bug del frontend o backend

---

## ✅ SOLUCIONES IMPLEMENTADAS

### Commits Recientes:

1. **101b2e8** - "fix: corregir mapeo en adminDashboardService para usar usuario_id y nombre_completo del backend"
   - Corrige mapeo de ocupación de odontólogos

2. **30f298c** - "fix: corregir mapeo de KPIs para usar etiqueta/valor del backend en lugar de key/value"
   - Corrige adaptador de KPIs en adminDashboardService

---

## 🔍 DEBUGGING

### Logs en Consola del Navegador:

**Dashboard KPIs:**
```
🔵 [adminDashboardService.getKPIs] Iniciando petición...
🟢 [adminDashboardService.getKPIs] Respuesta RAW: [{etiqueta: '...', valor: '...'}]
  Procesando KPI: "Pacientes Activos" = 5 (key normalizado: "pacientes_activos")
✅ [adminDashboardService.getKPIs] Datos Adaptados: {total_pacientes: 5, ...}
```

**Tendencia de Citas:**
```
📈 [ReportesService] Solicitando tendencia-citas con params: {dias: 7}
✅ [ReportesService] Tendencia recibida: [{fecha: '...', cantidad: 0}]
📦 [ReportesService] Tendencia mapeada: 7 registros
```

**Ocupación de Odontólogos:**
```
👨‍⚕️ [ReportesService] Solicitando ocupacion-odontologos (ENDPOINT CORRECTO)
✅ [ReportesService] Ocupación recibida del backend: [{usuario_id: 360, ...}]
📋 Odontólogo 1: {usuario_id: 360, nombre_completo: 'Dr. Juan Pérez', ...}
```

---

## 📊 RESUMEN DE ESTADO ACTUAL

| Componente | Estado | Observaciones |
|------------|--------|---------------|
| Dashboard KPIs | ✅ CORRECTO | Mapeo corregido en commit 30f298c |
| Estadísticas Generales | ✅ CORRECTO | Backend envía formato exacto |
| Tendencia de Citas | ⚠️ INCOMPLETO | Falta completadas/canceladas en backend |
| Top Procedimientos | ✅ CORRECTO | Porcentajes calculados en frontend |
| Ocupación Odontólogos | ✅ CORRECTO | Datos en 0% porque no hay citas completadas |
| Reporte Financiero | ✅ CORRECTO | No requiere mapeo especial |
| Stock Bajo | ✅ CORRECTO | Actualmente vacío (sin alertas) |
| Actividad Reciente | ✅ CORRECTO | Actualmente vacío (sin bitácora) |

---

## 📂 ARCHIVOS CLAVE

### Backend (Django):
- `reportes/views.py` (línea 206: tendencia_citas)
- `reportes/views.py` (línea 504: ocupacion_odontologos)
- `reportes/serializers.py`

### Frontend (React):
- `src/services/admin/adminDashboardService.ts`
- `src/services/reportesService.ts`
- `src/pages/admin/Dashboard.tsx`
- `src/components/admin/DashboardKPIs.tsx`
- `src/components/admin/OcupacionOdontologos.tsx`
- `src/components/admin/TendenciaCitasChart.tsx`

---

## 🎯 PRÓXIMOS PASOS

1. ✅ **Frontend:** Mapeo de KPIs corregido
2. ⏳ **Backend:** Actualizar `tendencia_citas` para incluir completadas/canceladas
3. ⏳ **Backend:** Esperar despliegue de Render (2-3 minutos después del push)
4. ✅ **Testing:** Verificar que los KPIs muestren valores correctos
5. 📊 **Datos:** Cambiar estado de algunas citas a "COMPLETADA" para ver ocupación real

---

**Generado automáticamente por el Sistema de Documentación de Reportes**  
**Para regenerar este documento, haz clic en el botón "📄 Imprimir Documentación" en el Dashboard**
