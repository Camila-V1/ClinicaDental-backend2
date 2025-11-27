# 🔧 Instrucciones para Corregir el Frontend

**Fecha:** 27 de noviembre de 2025  
**Backend:** ✅ **LISTO Y FUNCIONANDO**  
**Frontend:** ❌ **REQUIERE CORRECCIONES**

---

## 📊 Resumen de la Situación

### ✅ Lo que YA está funcionando en el BACKEND:

1. **Endpoint de KPIs:** `/api/reportes/reportes/dashboard-kpis/`
   - ✅ Retorna **10 KPIs completos** (antes solo 4)
   - ✅ Todos los valores son correctos
   - ✅ Formato: `[{ "etiqueta": "...", "valor": ... }]`

2. **Datos reales en Render:**
   - ✅ 5 Pacientes Activos
   - ✅ Bs. 280.00 de Ingresos Este Mes
   - ✅ Bs. 525.00 de Saldo Pendiente
   - ✅ Bs. 176.25 Promedio por Factura
   - ✅ 1 Factura Vencida

### ❌ Lo que está FALLANDO en el FRONTEND:

El dashboard muestra **0 en todos los valores** a pesar de que el backend retorna datos correctos.

---

## 🐛 PROBLEMAS IDENTIFICADOS Y SOLUCIONES

### **PROBLEMA 1: Dashboard.tsx - Acceso Incorrecto a KPIs**

**Ubicación:** `src/pages/admin/Dashboard.tsx` (o similar)

**Código ACTUAL (INCORRECTO):**
```tsx
{kpis && kpis[0] && (
  <KPICard
    label={kpis[0].etiqueta}  // ❌ ERROR: kpis es OBJETO, no array
    value={kpis[0].valor}     // ❌ kpis[0] es undefined
    icon="Users"
    color="blue"
  />
)}
```

**Código CORRECTO:**
```tsx
{kpis && (
  <>
    <KPICard
      label="Pacientes Activos"
      value={kpis.total_pacientes}  // ✅ Acceso directo a la propiedad
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
      value={kpis.ingresos_mes}
      icon="DollarSign"
      color="purple"
      prefix="Bs. "  // ✅ Mostrar en Bolivianos
      format="currency"
    />
    <KPICard
      label="Saldo Pendiente"
      value={kpis.saldo_pendiente}
      icon="AlertCircle"
      color="orange"
      prefix="Bs. "
      format="currency"
    />
    <KPICard
      label="Tratamientos Activos"
      value={kpis.tratamientos_activos}
      icon="Activity"
      color="indigo"
    />
    <KPICard
      label="Planes Completados"
      value={kpis.planes_completados}
      icon="CheckCircle"
      color="teal"
    />
    <KPICard
      label="Promedio por Factura"
      value={kpis.promedio_factura}
      icon="TrendingUp"
      color="cyan"
      prefix="Bs. "
      format="currency"
    />
    <KPICard
      label="Facturas Vencidas"
      value={kpis.facturas_vencidas}
      icon="AlertTriangle"
      color="red"
    />
    <KPICard
      label="Total Procedimientos"
      value={kpis.total_procedimientos}
      icon="Clipboard"
      color="yellow"
    />
    <KPICard
      label="Pacientes Nuevos"
      value={kpis.pacientes_nuevos_mes}
      icon="UserPlus"
      color="lime"
    />
  </>
)}
```

---

### **PROBLEMA 2: adminDashboardService.ts - Adaptador Incompleto**

**Ubicación:** `src/services/admin/adminDashboardService.ts`

**Código ACTUAL (INCORRECTO):**
```typescript
async getKPIs(): Promise<any> {
  const { data } = await api.get('/api/reportes/reportes/dashboard-kpis/');
  
  let kpisFormatted = {
    total_pacientes: 0,
    citas_hoy: 0,
    ingresos_mes: "0",
    // ... otros campos en 0
  };

  // ❌ Mapeo frágil basado en palabras clave
  if (Array.isArray(data)) {
    data.forEach((item: any) => {
      const key = String(item.etiqueta).toLowerCase().replace(/ /g, '_');
      
      if (key.includes('pacientes') && key.includes('total')) {
        kpisFormatted.total_pacientes = item.valor;
      }
      // ... más if statements frágiles
    });
  }

  return kpisFormatted;
}
```

**Código CORRECTO:**
```typescript
async getKPIs(): Promise<DashboardKPIs> {
  const { data } = await api.get('/api/reportes/reportes/dashboard-kpis/');
  
  console.log('🔍 [AdminDashboardService] KPIs recibidos del backend:', data);
  
  // Crear un mapa para acceso rápido por etiqueta
  const kpisMap = new Map<string, number>();
  if (Array.isArray(data)) {
    data.forEach((item: any) => {
      kpisMap.set(item.etiqueta, Number(item.valor));
    });
  }
  
  // Mapeo EXACTO por etiquetas del backend
  const kpis: DashboardKPIs = {
    total_pacientes: kpisMap.get('Pacientes Activos') || 0,
    citas_hoy: kpisMap.get('Citas Hoy') || 0,
    ingresos_mes: kpisMap.get('Ingresos Este Mes') || 0,
    saldo_pendiente: kpisMap.get('Saldo Pendiente') || 0,
    tratamientos_activos: kpisMap.get('Tratamientos Activos') || 0,
    planes_completados: kpisMap.get('Planes Completados') || 0,
    promedio_factura: kpisMap.get('Promedio por Factura') || 0,
    facturas_vencidas: kpisMap.get('Facturas Vencidas') || 0,
    total_procedimientos: kpisMap.get('Total Procedimientos') || 0,
    pacientes_nuevos_mes: kpisMap.get('Pacientes Nuevos Mes') || 0,
  };
  
  console.log('✅ [AdminDashboardService] KPIs mapeados:', kpis);
  
  return kpis;
}
```

**Interfaz TypeScript:**
```typescript
export interface DashboardKPIs {
  total_pacientes: number;
  citas_hoy: number;
  ingresos_mes: number;
  saldo_pendiente: number;
  tratamientos_activos: number;
  planes_completados: number;
  promedio_factura: number;
  facturas_vencidas: number;
  total_procedimientos: number;
  pacientes_nuevos_mes: number;
}
```

---

### **PROBLEMA 3: Conversión de Moneda**

**Contexto:**
- Backend envía valores en **Bolivianos (Bs.)**
- Frontend muestra etiquetas en **US$**
- **NO hay conversión automática**

**Soluciones:**

#### **Opción A: Cambiar etiquetas a Bolivianos (MÁS RÁPIDO)**

```tsx
<KPICard
  label="Ingresos del Mes"
  value={kpis.ingresos_mes}
  prefix="Bs. "  // ✅ Cambiar US$ → Bs.
  format="currency"
/>
```

#### **Opción B: Implementar conversión (MÁS COMPLEJO)**

**1. Crear utilidad de conversión:**

```typescript
// src/utils/currency.ts

const EXCHANGE_RATE_BOB_TO_USD = 0.14; // 1 BOB ≈ 0.14 USD (actualizar según tasa real)

export function convertBobToUsd(bob: number): number {
  return bob * EXCHANGE_RATE_BOB_TO_USD;
}

export function formatCurrency(amount: number, currency: 'BOB' | 'USD' = 'BOB'): string {
  const locale = currency === 'USD' ? 'en-US' : 'es-BO';
  const symbol = currency === 'USD' ? 'US$' : 'Bs.';
  
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount) + ' ' + symbol;
}
```

**2. Usar en el servicio:**

```typescript
import { convertBobToUsd } from '@/utils/currency';

async getKPIs(): Promise<DashboardKPIs> {
  // ... obtener datos del backend ...
  
  const kpis: DashboardKPIs = {
    // ... otros campos ...
    ingresos_mes: convertBobToUsd(kpisMap.get('Ingresos Este Mes') || 0),
    saldo_pendiente: convertBobToUsd(kpisMap.get('Saldo Pendiente') || 0),
    promedio_factura: convertBobToUsd(kpisMap.get('Promedio por Factura') || 0),
  };
  
  return kpis;
}
```

---

## 🧪 CÓMO VERIFICAR LOS CAMBIOS

### **1. Probar el Backend (desde navegador o Postman):**

```bash
# Endpoint de KPIs
GET https://clinicadental-backend2.onrender.com/api/reportes/reportes/dashboard-kpis/
Authorization: Bearer <tu_token_jwt>
Host: clinica-demo.clinicadental-backend2.onrender.com

# Respuesta esperada:
[
  { "etiqueta": "Pacientes Activos", "valor": 5 },
  { "etiqueta": "Citas Hoy", "valor": 0 },
  { "etiqueta": "Ingresos Este Mes", "valor": 280.0 },
  { "etiqueta": "Saldo Pendiente", "valor": 525.0 },
  { "etiqueta": "Tratamientos Activos", "valor": 0 },
  { "etiqueta": "Planes Completados", "valor": 0 },
  { "etiqueta": "Promedio por Factura", "valor": 176.25 },
  { "etiqueta": "Facturas Vencidas", "valor": 1 },
  { "etiqueta": "Total Procedimientos", "valor": 0 },
  { "etiqueta": "Pacientes Nuevos Mes", "valor": 0 }
]
```

### **2. Verificar logs del frontend:**

Después de aplicar los cambios, deberías ver en la consola del navegador:

```
🔍 [AdminDashboardService] KPIs recibidos del backend: [{...}]
✅ [AdminDashboardService] KPIs mapeados: { total_pacientes: 5, ingresos_mes: 280, ... }
```

### **3. Resultado esperado en el dashboard:**

```
┌─────────────────────────┐  ┌─────────────────────────┐
│ Pacientes Activos       │  │ Citas Hoy               │
│        5                │  │        0                │
└─────────────────────────┘  └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│ Ingresos del Mes        │  │ Saldo Pendiente         │
│   Bs. 280.00            │  │   Bs. 525.00            │
└─────────────────────────┘  └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│ Promedio por Factura    │  │ Facturas Vencidas       │
│   Bs. 176.25            │  │        1                │
└─────────────────────────┘  └─────────────────────────┘
```

---

## 📝 RESUMEN DE ARCHIVOS A MODIFICAR

1. **`src/services/admin/adminDashboardService.ts`**
   - ✅ Corregir método `getKPIs()`
   - ✅ Mapear TODOS los KPIs del backend
   - ✅ Usar nombres de etiquetas EXACTOS

2. **`src/pages/admin/Dashboard.tsx`**
   - ✅ Cambiar acceso de `kpis[0].valor` a `kpis.total_pacientes`
   - ✅ Renderizar todos los KPICards correctamente
   - ✅ Agregar prefijo "Bs." en lugar de "US$"

3. **`src/utils/currency.ts`** (opcional - si quieres conversión)
   - Crear helper `convertBobToUsd()`
   - Crear helper `formatCurrency()`

---

## 🚀 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### **PASO 1: Corregir el adaptador (5 min)**
Editar `adminDashboardService.ts` con el mapeo exacto de etiquetas.

### **PASO 2: Corregir el renderizado (10 min)**
Editar `Dashboard.tsx` para acceder correctamente a `kpis.campo`.

### **PASO 3: Cambiar moneda a Bs. (2 min)**
Cambiar todos los `prefix="US$"` por `prefix="Bs. "`.

### **PASO 4: Probar en desarrollo (5 min)**
```bash
npm run dev
# Abrir http://localhost:5173 y verificar dashboard
```

### **PASO 5: Deploy a producción**
```bash
git add .
git commit -m "fix: corregir dashboard - mapear todos los KPIs correctamente"
git push
```

---

## ⚠️ ERRORES COMUNES A EVITAR

1. ❌ **NO usar `kpis[0]`, `kpis[1]`** → El adaptador retorna OBJETO, no array
2. ❌ **NO buscar por palabras clave** → Usar etiquetas EXACTAS del backend
3. ❌ **NO asumir conversión automática** → El backend envía Bs., no US$
4. ❌ **NO olvidar console.logs** → Ayudan a debuggear el flujo de datos

---

## 🎯 RESULTADO FINAL ESPERADO

Después de aplicar todos los cambios:

✅ Dashboard muestra valores reales del backend  
✅ Todos los KPIs se renderizan correctamente  
✅ Moneda mostrada es Bolivianos (Bs.)  
✅ No hay errores en la consola  
✅ Los datos coinciden con los del backend  

---

**Documentación generada por el análisis del código backend.**  
**Backend funcionando al 100% - Solo falta ajustar el frontend.**
