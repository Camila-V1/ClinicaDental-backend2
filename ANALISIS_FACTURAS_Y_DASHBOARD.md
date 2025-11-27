# 📊 Análisis: Implementación de Facturas y Dashboard

**Fecha:** 27 de noviembre de 2025  
**Contexto:** El usuario reporta que el backend está funcionando correctamente (200 OK en endpoints) pero el dashboard muestra datos en 0.

---

## 🎯 Resumen Ejecutivo

### ✅ Lo que SÍ funciona:
- Backend devuelve `/api/facturacion/pagos/` → **200 OK** (20 pagos)
- Backend devuelve `/api/facturacion/facturas/` → **200 OK** (20 facturas)
- Backend devuelve KPIs con "Ingresos Este Mes = 510 Bs."
- Todos los pagos tienen `cita_info` correctamente asociada

### ❌ Problemas detectados:
1. **Dashboard muestra "Ingresos del Mes: 0.00 US$"** aunque el backend retorna 510
2. **Total Procedimientos = 0** (no hay lógica para contar tratamientos)
3. **Planes Completados = 0** (no implementado)
4. **Promedio por Factura = 0.00 US$** (no calculado en frontend)
5. **Facturas Vencidas = 0** (no se consulta el endpoint correspondiente)

### 🔍 Causa raíz:
- **Conversión de moneda incorrecta o inexistente** (Bs. → US$)
- **Adaptación de datos del backend al frontend incompleta**
- **KPIs del dashboard esperan estructura de objeto, pero el backend envía array**

---

## 📋 PARTE 1: Implementación de Facturas (`facturacionService.ts`)

### 🏗️ Arquitectura

```typescript
// Archivo: src/services/facturacionService.ts
// Propósito: Gestión de facturas y pagos para módulo de pacientes
```

### 📦 Interfaces TypeScript

#### **Factura**
```typescript
export interface Factura {
  id: number;
  numero: string;
  paciente_id: number;
  paciente_nombre: string;
  fecha_emision: string;
  fecha_vencimiento: string;
  subtotal: string;           // ⚠️ String, no Number
  descuento: string;
  total: string;              // ⚠️ String, no Number
  pagado: string;
  saldo: string;
  saldo_pendiente?: string | null;
  estado: 'PENDIENTE' | 'PAGADA' | 'PARCIAL' | 'VENCIDA' | 'ANULADA';
  notas?: string;
  created_at: string;
  items: ItemFactura[];
  pagos?: Pago[];
}
```

**Observación:** Los montos son `string` para evitar pérdida de precisión en decimales (patrón común en Django con `DecimalField`).

#### **ItemFactura**
```typescript
export interface ItemFactura {
  id: number;
  servicio_nombre: string;
  cantidad: number;
  precio_unitario: string;    // ⚠️ String
  subtotal: string;           // ⚠️ String
  descripcion?: string;
}
```

#### **Pago**
```typescript
export interface Pago {
  id: number;
  factura_id: number;
  fecha_pago: string;
  monto: string;              // ⚠️ String
  metodo_pago: 'EFECTIVO' | 'TARJETA' | 'TRANSFERENCIA' | 'CHEQUE';
  referencia?: string;
  notas?: string;
  created_at: string;
}
```

#### **EstadoCuenta**
```typescript
export interface EstadoCuenta {
  paciente_id: number;
  paciente_nombre: string;
  total_facturas: number;
  total_facturado: string;
  total_pagado: string;
  saldo_pendiente: string;
  facturas_pendientes: number;
  facturas_vencidas: number;
  ultima_factura?: {
    id: number;
    numero: string;
    fecha_emision: string;
    total: string;
    estado: string;
  };
  proximo_vencimiento?: {
    factura_id: number;
    factura_numero: string;
    fecha_vencimiento: string;
    monto: string;
  };
}
```

---

### 🔧 Métodos Implementados

#### **1. obtenerMisFacturas(filtros?)**

**Endpoint:** `GET /api/facturacion/facturas/mis_facturas/`

**Características:**
- ✅ Soporta filtros por estado, fecha_inicio, fecha_fin
- ✅ Tiene **fallback** para endpoint con guion medio (`mis-facturas`)
- ✅ **Logs detallados** agregados recientemente:
  - Muestra filtros aplicados
  - Cuenta facturas recibidas
  - Verifica tipo de datos (Array)
  - **Muestra resumen por estado**
  - **Detalla primera factura** como ejemplo

**Ejemplo de log:**
```javascript
💰 [FacturacionService] Obteniendo facturas del paciente...
   - Filtros: { estado: 'PENDIENTE' }
   - Params URL: estado=PENDIENTE
✅ [FacturacionService] Facturas recibidas: 12
   - Tipo de datos: Array
   - Primera factura: { id: 45, numero: 'F-2025-045', estado: 'PENDIENTE', total: '150.00' }
   - Resumen por estado:
      PENDIENTE: 8 facturas
      PAGADA: 4 facturas
```

**Problema actual:** ❌ **NO convierte montos de Bs. a US$**

---

#### **2. obtenerDetalleFactura(id)**

**Endpoint:** `GET /api/facturacion/facturas/{id}/`

**Características:**
- ✅ Obtiene factura completa con items y pagos
- ✅ **Logs mejorados:**
  - Muestra resumen de la factura (id, número, estado, total, pagado, saldo)
  - **Lista todos los items** con formato: `1. Limpieza Dental - $60.00 x 1 = $60.00`
  - Cuenta items y pagos asociados

**Ejemplo de log:**
```javascript
🔍 [FacturacionService] Obteniendo detalle de factura: 45
✅ [FacturacionService] Factura obtenida: { id: 45, numero: 'F-2025-045', estado: 'PENDIENTE', total: '150.00', pagado: '60.00', saldo: '90.00', items_count: 3, pagos_count: 1 }
   - Items de la factura:
      1. Limpieza Dental - $60.00 x 1 = $60.00
      2. Extracción Simple - $80.00 x 1 = $80.00
      3. Consulta - $10.00 x 1 = $10.00
```

---

#### **3. obtenerPagosFactura(facturaId)**

**Endpoint:** `GET /api/facturacion/facturas/{facturaId}/pagos/`

**Características:**
- ✅ Lista todos los pagos de una factura
- ✅ **Logs detallados:**
  - Muestra cada pago con método, monto, fecha y referencia
  - **Calcula total pagado** sumando todos los pagos

**Ejemplo de log:**
```javascript
💳 [FacturacionService] Obteniendo pagos de factura: 45
✅ [FacturacionService] Pagos recibidos: 1
   - Tipo de datos: Array
   - Detalle de pagos:
      1. EFECTIVO: $60.00 - 2025-11-20
   - Total pagado: $60.00
```

---

#### **4. obtenerEstadoCuenta()**

**Endpoint:** `GET /api/facturacion/facturas/estado_cuenta/`

**Características:**
- ✅ Retorna resumen financiero del paciente
- ✅ **Logs completos:**
  - Total facturas, facturado, pagado, saldo pendiente
  - Facturas pendientes y vencidas
  - Última factura y próximo vencimiento (si existen)

**Ejemplo de log:**
```javascript
📊 [FacturacionService] Obteniendo estado de cuenta...
✅ [FacturacionService] Estado de cuenta obtenido: {
  paciente_nombre: 'María García',
  total_facturas: 12,
  total_facturado: '1800.00',
  total_pagado: '1200.00',
  saldo_pendiente: '600.00',
  facturas_pendientes: 5,
  facturas_vencidas: 2
}
   - Última factura: { id: 45, numero: 'F-2025-045', fecha_emision: '2025-11-15', total: '150.00', estado: 'PENDIENTE' }
   - Próximo vencimiento: { factura_id: 40, factura_numero: 'F-2025-040', fecha_vencimiento: '2025-12-01', monto: '200.00' }
```

---

#### **5. verificarFacturasVencidas()**

**Endpoint:** `GET /api/facturacion/facturas/verificar-vencidas/`

**Características:**
- ✅ Retorna facturas vencidas del paciente
- ⚠️ **NO tiene logs detallados** (solo básicos)
- ⚠️ **NO se usa en el dashboard actual**

---

## 📊 PARTE 2: Implementación del Dashboard

### 🏗️ Arquitectura de Componentes

```
Dashboard.tsx (Página)
    ├── adminDashboardService.ts (Servicio API)
    │   ├── getKPIs()
    │   ├── getTendenciaCitas()
    │   ├── getTopProcedimientos()
    │   ├── getEstadisticasGenerales()
    │   ├── getReporteFinanciero()
    │   ├── getOcupacionOdontologos()
    │   ├── getStockBajo()
    │   └── getActividadReciente()
    │
    └── Componentes UI
        ├── KPICard (Tarjetas métricas)
        ├── LineChart (Gráfico de tendencia)
        ├── BarChart (Gráfico de barras)
        ├── StatsGrid (Grid de estadísticas)
        ├── AlertList (Lista de alertas)
        └── ActivityTimeline (Timeline de actividad)
```

---

### 🔧 Servicio: `adminDashboardService.ts`

#### **Método 1: getKPIs()** ⚠️ **PROBLEMA AQUÍ**

**Endpoint:** `GET /api/reportes/reportes/dashboard-kpis/`

**Problema:** Backend envía **array**, frontend espera **objeto**

**Respuesta del backend (actual):**
```json
[
  { "etiqueta": "Total Pacientes", "valor": 150 },
  { "etiqueta": "Citas Hoy", "valor": 8 },
  { "etiqueta": "Ingresos Este Mes", "valor": 510 },  // ⚠️ En Bs.
  { "etiqueta": "Saldo Pendiente", "valor": 200 }
]
```

**Lo que el frontend espera:**
```typescript
{
  total_pacientes: 150,
  citas_hoy: 8,
  ingresos_mes: "510",
  tratamientos_activos: 0,
  pacientes_nuevos_mes: 0,
  tasa_ocupacion: 0,
  citas_pendientes: 0,
  facturas_pendientes: 0
}
```

**Adaptador implementado:**
```typescript
async getKPIs(): Promise<any> {
  const { data } = await api.get('/api/reportes/reportes/dashboard-kpis/');
  
  let kpisFormatted = {
    total_pacientes: 0,
    citas_hoy: 0,
    ingresos_mes: "0",
    tratamientos_activos: 0,
    // ... otros campos en 0
  };

  if (Array.isArray(data)) {
    data.forEach((item: any) => {
      const rawKey = item.etiqueta || item.key || item.label || ''; 
      const key = String(rawKey).toLowerCase().replace(/ /g, '_');
      const value = Number(item.valor || item.value || 0);

      // 🔍 Busca palabras clave en la etiqueta
      if (key.includes('pacientes') && key.includes('total')) {
        kpisFormatted.total_pacientes = value;
      } else if (key.includes('citas') && key.includes('hoy')) {
        kpisFormatted.citas_hoy = value;
      } else if (key.includes('ingresos')) {
        kpisFormatted.ingresos_mes = String(value); // ⚠️ NO convierte Bs. → US$
      }
      // ... otros mapeos
    });
  }

  return kpisFormatted;
}
```

**Problemas identificados:**

1. ❌ **NO convierte moneda:** `ingresos_mes` queda en Bs. pero UI muestra "US$"
2. ❌ **Mapeo por palabras clave frágil:** Si backend cambia "Ingresos Este Mes" a "Ingresos Mensuales", falla
3. ❌ **Campos siempre en 0:** `tratamientos_activos`, `pacientes_nuevos_mes`, etc. no tienen datos del backend

---

#### **Método 2: getTendenciaCitas()**

**Endpoint:** `GET /api/reportes/reportes/tendencia-citas/?dias=15`

**Estado:** ✅ **Funciona correctamente**
- Retorna array de tendencia de citas por día
- Frontend lo grafica sin problemas

---

#### **Método 3: getTopProcedimientos()** ✅ **Mejorado recientemente**

**Endpoint:** `GET /api/reportes/reportes/top-procedimientos/?limite=5`

**Logs actuales:**
```javascript
🏆 [ReportesService] Solicitando top-procedimientos con params: { limite: 5 }
✅ [ReportesService] Top procedimientos recibidos: 5
   - Tipo de datos: Array
   - Cantidad de items: 5
📊 [ReportesService] Total cantidad de procedimientos: 48
   1. Limpieza Dental: 12 realizados (25.0%)
   2. Extracción Simple: 10 realizados (20.8%)
   3. Consulta General: 8 realizados (16.7%)
   - Top 3 procedimientos más frecuentes:
      1. Limpieza Dental: 12 (25.0%)
      2. Extracción Simple: 10 (20.8%)
      3. Consulta General: 8 (16.7%)
```

**Estado:** ✅ **Funciona bien** con logs detallados

---

#### **Método 4: getEstadisticasGenerales()**

**Endpoint:** `GET /api/reportes/reportes/estadisticas-generales/`

**Estado:** ⚠️ **Depende del backend**
- Frontend solo hace el fetch, no transforma datos
- Si backend no envía `promedio_por_factura`, se mostrará en 0

---

#### **Método 5: getOcupacionOdontologos()**

**Endpoint:** `GET /api/reportes/reportes/ocupacion-odontologos/`

**Estado:** ✅ **Funciona correctamente**
- Mapea `usuario_id` → `odontologo_id`
- Mapea `nombre_completo` → `odontologo_nombre`

---

#### **Método 6: getStockBajo()**

**Endpoint:** `GET /api/inventario/insumos/bajo_stock/`

**Estado:** ✅ **Funciona correctamente**
- Retorna lista de insumos con stock bajo
- Se muestra en "Alertas" del dashboard

---

#### **Método 7: getActividadReciente()**

**Endpoint:** `GET /api/reportes/bitacora/`

**Estado:** ✅ **Funciona correctamente**
- Obtiene logs de bitácora del sistema
- Transforma formato del backend al frontend
- Maneja paginación (`results`)

---

### 🎨 Componente: `Dashboard.tsx`

**Flujo de datos:**
```
1. useQuery() → llama a adminDashboardService.getKPIs()
2. getKPIs() → GET /api/reportes/reportes/dashboard-kpis/
3. Backend retorna: [{ etiqueta: "...", valor: ... }]
4. Adaptador convierte array → objeto
5. Dashboard.tsx recibe kpis como objeto
6. Renderiza KPICard con kpis[0].etiqueta y kpis[0].valor ❌ ERROR
```

**Problema actual:**

```tsx
{kpis && kpis[0] && (
  <KPICard
    label={kpis[0].etiqueta}  // ❌ kpis es objeto, no array
    value={kpis[0].valor}     // ❌ No existen estas propiedades
    icon="Users"
    color="blue"
  />
)}
```

**El código asume que `kpis` es un array**, pero `getKPIs()` retorna un **objeto**.

**Debería ser:**
```tsx
{kpis && (
  <>
    <KPICard
      label="Total Pacientes"
      value={kpis.total_pacientes}
      icon="Users"
      color="blue"
    />
    <KPICard
      label="Citas Hoy"
      value={kpis.citas_hoy}
      icon="Calendar"
      color="green"
    />
    <KPICard
      label="Ingresos del Mes"
      value={convertirADolares(kpis.ingresos_mes)}  // ⚠️ Convertir Bs → US$
      icon="DollarSign"
      color="purple"
      prefix="$"
    />
    <KPICard
      label="Saldo Pendiente"
      value={convertirADolares(kpis.facturas_pendientes)}
      icon="AlertCircle"
      color="orange"
    />
  </>
)}
```

---

## 🐛 Problemas Identificados y Soluciones

### **Problema 1: Ingresos muestran 0.00 US$ pero backend envía 510 Bs.**

**Causa:**
1. El adaptador de `getKPIs()` sí recibe 510 del backend
2. Pero lo asigna a `ingresos_mes: "510"` (como string)
3. El componente `Dashboard.tsx` intenta acceder a `kpis[0].valor` cuando `kpis` es un objeto
4. Como `kpis[0]` es `undefined`, muestra 0

**Solución:**
1. ✅ Corregir el renderizado de `Dashboard.tsx` para usar `kpis.ingresos_mes` en vez de `kpis[0].valor`
2. ⚠️ Agregar conversión de Bs. a US$ (requiere tasa de cambio)

---

### **Problema 2: Total Procedimientos = 0**

**Causa:**
- No hay campo `total_procedimientos` en los KPIs del backend
- El adaptador no mapea nada a este campo

**Solución:**
- ✅ Backend debe agregar KPI "Total Procedimientos" a `/api/reportes/reportes/dashboard-kpis/`
- O calcular en frontend sumando `topProcedimientos.reduce((sum, p) => sum + p.cantidad, 0)`

---

### **Problema 3: Planes Completados = 0**

**Causa:**
- No existe KPI en el backend para "Planes Completados"

**Solución:**
- ✅ Backend debe agregar:
  ```python
  planes_completados = PlanTratamiento.objects.filter(
      clinica=clinica,
      estado='completado'
  ).count()
  ```
- Frontend lo mapea en el adaptador

---

### **Problema 4: Promedio por Factura = 0.00 US$**

**Causa:**
- El endpoint `/api/reportes/reportes/estadisticas-generales/` no calcula `promedio_por_factura`

**Solución:**
- ✅ Backend debe agregar:
  ```python
  total_facturado = Factura.objects.filter(clinica=clinica).aggregate(Sum('total'))['total__sum'] or 0
  total_facturas = Factura.objects.filter(clinica=clinica).count()
  promedio = total_facturado / total_facturas if total_facturas > 0 else 0
  ```

---

### **Problema 5: Facturas Vencidas = 0**

**Causa:**
- El KPI de "Facturas Vencidas" no se está mapeando correctamente
- Backend sí lo envía como "Saldo Pendiente" pero con valor 200

**Solución:**
- ✅ Revisar que el backend envíe KPI con etiqueta exacta "Facturas Vencidas"
- El adaptador debe buscar `key.includes('facturas') && key.includes('vencidas')`

---

## 📝 Resumen de Logs Implementados

### ✅ Logs en `facturacionService.ts`:

1. **obtenerMisFacturas:**
   - Filtros aplicados
   - Cantidad de facturas
   - Resumen por estado
   - Detalle de primera factura

2. **obtenerDetalleFactura:**
   - Resumen de factura (id, número, estado, total, pagado, saldo)
   - Lista completa de items con precios

3. **obtenerPagosFactura:**
   - Cantidad de pagos
   - Detalle de cada pago (método, monto, fecha)
   - Total pagado calculado

4. **obtenerEstadoCuenta:**
   - Resumen financiero completo
   - Última factura
   - Próximo vencimiento

### ✅ Logs en `reportesService.ts`:

1. **getTopProcedimientos:**
   - Tipo de datos recibido
   - Cantidad de items
   - Total de procedimientos realizados
   - Top 3 procedimientos con porcentajes

### ✅ Logs en `adminDashboardService.ts`:

1. **Todos los métodos tienen logs:**
   - Inicio de petición
   - Respuesta RAW del backend
   - Datos adaptados/mapeados
   - Errores con detalles

---

## 🎯 Recomendaciones Finales

### **Inmediatas (Frontend):**
1. ✅ Corregir renderizado de KPIs en `Dashboard.tsx` (usar objeto en vez de array)
2. ⚠️ Agregar helper de conversión Bs. → US$ con tasa de cambio
3. ✅ Calcular "Total Procedimientos" en frontend desde `topProcedimientos`

### **Corto plazo (Backend):**
1. ✅ Agregar KPIs faltantes:
   - `tratamientos_activos`
   - `planes_completados`
   - `promedio_por_factura`
   - `pacientes_nuevos_mes`
   - `facturas_vencidas` (con count real)

2. ✅ Estandarizar formato de respuesta de `/api/reportes/reportes/dashboard-kpis/`:
   - Opción A: Retornar objeto en vez de array
   - Opción B: Usar siempre mismas etiquetas (keys) para mapeo confiable

### **Mediano plazo:**
1. ✅ Implementar sistema de conversión de moneda multi-divisa
2. ✅ Agregar cache de tasa de cambio Bs./US$
3. ✅ Crear componente `MoneyDisplay` que maneje automáticamente la conversión

---

## 📚 Referencias

- **Archivo de servicio facturas:** `src/services/facturacionService.ts`
- **Archivo de servicio dashboard:** `src/services/admin/adminDashboardService.ts`
- **Archivo de página dashboard:** `src/pages/admin/Dashboard.tsx`
- **Archivo de reportes:** `src/services/reportesService.ts`
- **Commit de mejora de logs:** `da2c757` (27 Nov 2025)

---

**Documento generado automáticamente por el análisis del código.**  
**Última actualización:** 27 de noviembre de 2025
