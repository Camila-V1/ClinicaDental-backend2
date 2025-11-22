# 📊 Guía de Actualización Frontend - Estadísticas Completas

## 🎯 Resumen de Cambios Backend

Se ha ampliado el endpoint `/api/reportes/reportes/estadisticas-generales/` para incluir **TODAS** las métricas necesarias para el dashboard.

### ✅ Commit Backend
- **Commit**: `affb140`
- **Desplegado**: Render auto-deploy en progreso
- **Endpoint**: `GET /api/reportes/reportes/estadisticas-generales/`

---

## 📡 Nueva Estructura de Respuesta del Backend

```json
{
  // ===== PACIENTES =====
  "total_pacientes_activos": 5,
  "pacientes_nuevos_mes": 2,
  
  // ===== ODONTÓLOGOS =====
  "total_odontologos": 1,
  
  // ===== CITAS =====
  "citas_mes_actual": 7,
  "citas_completadas": 3,
  "citas_pendientes": 4,
  "citas_canceladas": 1,
  
  // ===== TRATAMIENTOS =====
  "tratamientos_completados": 0,
  "planes_activos": 5,
  "total_procedimientos": 12,
  
  // ===== FINANCIERO =====
  "ingresos_mes_actual": 280.00,
  "monto_pendiente": 75.00,
  "facturas_vencidas": 2,
  "promedio_factura": 118.33,
  
  // ===== OCUPACIÓN =====
  "tasa_ocupacion": 85.71
}
```

---

## 🛠️ Cambios Necesarios en el Frontend

### 1️⃣ Actualizar Interface TypeScript

**Archivo**: `src/types/reportes.ts` (o donde tengan las interfaces)

```typescript
export interface EstadisticasGenerales {
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
  tratamientos_completados: number;
  planes_activos: number;
  total_procedimientos: number;
  
  // Financiero
  ingresos_mes_actual: number;
  monto_pendiente: number;
  facturas_vencidas: number;
  promedio_factura: number;
  
  // Ocupación
  tasa_ocupacion: number;
}
```

---

### 2️⃣ Actualizar Componente de Estadísticas Generales

**Archivo**: `src/components/dashboard/EstadisticasGenerales.tsx`

```typescript
import React from 'react';
import { EstadisticasGenerales } from '@/types/reportes';

interface Props {
  estadisticas: EstadisticasGenerales | undefined;
  loading: boolean;
}

const EstadisticasGeneralesCard: React.FC<Props> = ({ estadisticas, loading }) => {
  if (loading) {
    return <div>Cargando estadísticas...</div>;
  }

  if (!estadisticas) {
    return <div>No hay datos disponibles</div>;
  }

  return (
    <div className="estadisticas-grid">
      {/* ===== SECCIÓN PACIENTES ===== */}
      <div className="stats-section">
        <h3>👥 Pacientes</h3>
        <div className="stat-item">
          <label>Total:</label>
          <span>{estadisticas.total_pacientes_activos}</span>
        </div>
        <div className="stat-item">
          <label>Nuevos (mes):</label>
          <span>{estadisticas.pacientes_nuevos_mes}</span>
        </div>
        <div className="stat-item">
          <label>Activos:</label>
          <span>{estadisticas.total_pacientes_activos}</span>
        </div>
      </div>

      {/* ===== SECCIÓN CITAS ===== */}
      <div className="stats-section">
        <h3>📅 Citas (Mes)</h3>
        <div className="stat-item">
          <label>Total:</label>
          <span>{estadisticas.citas_mes_actual}</span>
        </div>
        <div className="stat-item">
          <label>Completadas:</label>
          <span className="text-success">{estadisticas.citas_completadas}</span>
        </div>
        <div className="stat-item">
          <label>Pendientes:</label>
          <span className="text-warning">{estadisticas.citas_pendientes}</span>
        </div>
        <div className="stat-item">
          <label>Canceladas:</label>
          <span className="text-danger">{estadisticas.citas_canceladas}</span>
        </div>
      </div>

      {/* ===== SECCIÓN FINANCIERO ===== */}
      <div className="stats-section">
        <h3>💰 Financiero</h3>
        <div className="stat-item">
          <label>Ingresos (mes):</label>
          <span>Bs. {estadisticas.ingresos_mes_actual.toFixed(2)}</span>
        </div>
        <div className="stat-item">
          <label>Pendiente:</label>
          <span className="text-warning">
            Bs. {estadisticas.monto_pendiente.toFixed(2)}
          </span>
        </div>
        <div className="stat-item">
          <label>Vencidas:</label>
          <span className="text-danger">{estadisticas.facturas_vencidas}</span>
        </div>
        <div className="stat-item">
          <label>Promedio factura:</label>
          <span>Bs. {estadisticas.promedio_factura.toFixed(2)}</span>
        </div>
      </div>

      {/* ===== SECCIÓN TRATAMIENTOS ===== */}
      <div className="stats-section">
        <h3>🦷 Tratamientos</h3>
        <div className="stat-item">
          <label>Planes activos:</label>
          <span>{estadisticas.planes_activos}</span>
        </div>
        <div className="stat-item">
          <label>Completados:</label>
          <span>{estadisticas.tratamientos_completados}</span>
        </div>
        <div className="stat-item">
          <label>Procedimientos:</label>
          <span>{estadisticas.total_procedimientos}</span>
        </div>
      </div>

      {/* ===== SECCIÓN OCUPACIÓN ===== */}
      <div className="stats-section">
        <h3>📊 Ocupación</h3>
        <div className="stat-item">
          <label>Tasa de ocupación:</label>
          <span className={estadisticas.tasa_ocupacion > 70 ? 'text-success' : 'text-warning'}>
            {estadisticas.tasa_ocupacion.toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default EstadisticasGeneralesCard;
```

---

### 3️⃣ Actualizar KPIs del Dashboard Principal

**Archivo**: `src/components/dashboard/DashboardKPIs.tsx`

```typescript
interface KPIProps {
  estadisticas: EstadisticasGenerales | undefined;
  loading: boolean;
}

const DashboardKPIs: React.FC<KPIProps> = ({ estadisticas, loading }) => {
  if (loading || !estadisticas) {
    return <SkeletonLoader />;
  }

  const kpis = [
    {
      titulo: 'Total Pacientes',
      valor: estadisticas.total_pacientes_activos,
      icono: '👥',
      color: 'blue'
    },
    {
      titulo: 'Citas Hoy',
      valor: estadisticas.citas_pendientes, // O filtrar por hoy
      icono: '📅',
      color: 'green'
    },
    {
      titulo: 'Ingresos del Mes',
      valor: `Bs. ${estadisticas.ingresos_mes_actual.toFixed(2)}`,
      icono: '💰',
      color: 'yellow'
    },
    {
      titulo: 'Tratamientos Activos',
      valor: estadisticas.planes_activos,
      icono: '🦷',
      color: 'purple'
    },
    {
      titulo: 'Pacientes Nuevos (Mes)',
      valor: estadisticas.pacientes_nuevos_mes,
      icono: '🆕',
      color: 'teal'
    },
    {
      titulo: 'Tasa de Ocupación',
      valor: `${estadisticas.tasa_ocupacion.toFixed(1)}%`,
      icono: '📊',
      color: 'indigo'
    },
    {
      titulo: 'Citas Pendientes',
      valor: estadisticas.citas_pendientes,
      icono: '⏰',
      color: 'orange'
    },
    {
      titulo: 'Facturas Pendientes',
      valor: estadisticas.facturas_vencidas,
      icono: '📄',
      color: 'red'
    }
  ];

  return (
    <div className="kpis-grid">
      {kpis.map((kpi, index) => (
        <KPICard key={index} {...kpi} />
      ))}
    </div>
  );
};
```

---

## 🔧 Cambios en Servicios/Hooks

### Si usan React Query:

**Archivo**: `src/hooks/useEstadisticas.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { reportesService } from '@/services/reportesService';

export const useEstadisticasGenerales = () => {
  return useQuery({
    queryKey: ['estadisticas-generales'],
    queryFn: () => reportesService.getEstadisticasGenerales(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: true
  });
};
```

### Si usan Axios directamente:

**Archivo**: `src/services/reportesService.ts`

```typescript
import axios from '@/lib/axios';
import { EstadisticasGenerales } from '@/types/reportes';

export const reportesService = {
  async getEstadisticasGenerales(): Promise<EstadisticasGenerales> {
    const { data } = await axios.get('/api/reportes/reportes/estadisticas-generales/');
    return data;
  }
};
```

---

## 📋 Checklist de Implementación

### ✅ Pasos a Seguir:

1. **Actualizar Types/Interfaces** ✅
   - Añadir todos los campos nuevos a `EstadisticasGenerales`
   - Verificar que los tipos coincidan con el backend

2. **Actualizar Componentes** ✅
   - `EstadisticasGenerales.tsx` - Sección completa
   - `DashboardKPIs.tsx` - Tarjetas principales
   - Cualquier otro componente que use estas estadísticas

3. **Probar con Datos Reales** ✅
   - Hacer login en la app
   - Navegar al dashboard
   - Verificar que todos los valores se muestren correctamente

4. **Manejo de Errores** ✅
   - Agregar fallbacks para datos `undefined`
   - Mostrar loaders mientras carga
   - Manejar casos de error en requests

---

## 🐛 Solución de Problemas Comunes

### Problema: "Los valores aparecen en 0 o undefined"

**Causa**: El componente está accediendo a propiedades con nombres antiguos

**Solución**: Verificar el mapeo de propiedades:

```typescript
// ❌ INCORRECTO
const pacientes = stats.total_pacientes; // No existe

// ✅ CORRECTO
const pacientes = stats.total_pacientes_activos; // Existe
```

### Problema: "Cannot read property 'X' of undefined"

**Causa**: El componente se renderiza antes de que lleguen los datos

**Solución**: Agregar validaciones:

```typescript
const valor = estadisticas?.ingresos_mes_actual || 0;
// O usar optional chaining con nullish coalescing
```

### Problema: "NaN en valores numéricos"

**Causa**: Intentar hacer operaciones matemáticas con `undefined`

**Solución**: Parsear y validar:

```typescript
const ingresos = parseFloat(estadisticas?.ingresos_mes_actual?.toString() || "0");
```

---

## 🔍 Verificación de Datos

### Endpoint de Prueba

```bash
# Probar el endpoint directamente
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "X-Tenant-ID: clinica_demo" \
     https://clinica-dental-backend.onrender.com/api/reportes/reportes/estadisticas-generales/
```

### Datos Actuales en Producción (clinica_demo):

```json
{
  "total_pacientes_activos": 5,
  "pacientes_nuevos_mes": 0,  // Ninguno registrado en noviembre
  "total_odontologos": 1,
  "citas_mes_actual": 7,
  "citas_completadas": 3,
  "citas_pendientes": 4,
  "citas_canceladas": 1,
  "tratamientos_completados": 0,
  "planes_activos": 5,
  "total_procedimientos": 12,
  "ingresos_mes_actual": 280.00,
  "monto_pendiente": 75.00,
  "facturas_vencidas": 0,
  "promedio_factura": 118.33,
  "tasa_ocupacion": 87.5
}
```

---

## 📚 Mapeo Completo de Propiedades

| Campo Frontend | Campo Backend | Tipo | Descripción |
|---------------|---------------|------|-------------|
| Total Pacientes | `total_pacientes_activos` | number | Pacientes activos en sistema |
| Nuevos (mes) | `pacientes_nuevos_mes` | number | Registrados en mes actual |
| Citas Total | `citas_mes_actual` | number | Citas del mes (sin canceladas) |
| Citas Completadas | `citas_completadas` | number | Citas finalizadas |
| Citas Pendientes | `citas_pendientes` | number | Pendientes o confirmadas |
| Citas Canceladas | `citas_canceladas` | number | Canceladas en el mes |
| Ingresos (mes) | `ingresos_mes_actual` | number | Pagos completados del mes |
| Pendiente | `monto_pendiente` | number | Facturado pero no cobrado |
| Vencidas | `facturas_vencidas` | number | Facturas pasadas de fecha |
| Planes activos | `planes_activos` | number | Tratamientos en progreso |
| Completados | `tratamientos_completados` | number | Tratamientos finalizados |
| Procedimientos | `total_procedimientos` | number | Items completados |

---

## 🚀 Deployment

### Backend (Render):
- ✅ **Commit**: `affb140`
- ✅ **Push**: Completado
- ⏳ **Auto-deploy**: En progreso (5-10 minutos)
- 🔗 **URL**: `https://clinica-dental-backend.onrender.com`

### Frontend:
- Implementar los cambios según esta guía
- Probar localmente
- Hacer commit y push
- Verificar en producción

---

## ✅ Resultado Esperado

Después de implementar estos cambios, el dashboard debe mostrar:

- ✅ **Total Pacientes**: 5 (no 0)
- ✅ **Pacientes Nuevos**: 0 (correcto - ninguno en nov)
- ✅ **Citas Hoy**: Valor dinámico
- ✅ **Ingresos del Mes**: Bs. 280.00 (no "NaN")
- ✅ **Tratamientos Activos**: 5 (no 0)
- ✅ **Tasa de Ocupación**: 87.5% (no 0%)
- ✅ **Citas Pendientes**: 4 (no 0)
- ✅ **Facturas Pendientes**: 0 (correcto)

---

## 📞 Soporte

Si encuentran problemas:

1. Verificar que el backend esté desplegado (esperar 5-10 min después del push)
2. Verificar que las propiedades del frontend coincidan con el backend
3. Revisar la consola del navegador para errores
4. Verificar que el token JWT sea válido
5. Verificar que el header `X-Tenant-ID` esté presente

---

**Última actualización**: 22 de noviembre de 2025  
**Versión Backend**: `affb140`  
**Estado**: ✅ Listo para implementar
