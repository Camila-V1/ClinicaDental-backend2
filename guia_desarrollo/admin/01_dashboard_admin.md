# 📊 Dashboard del Administrador

## 🎯 Objetivo
Crear el dashboard principal del administrador que muestre un resumen ejecutivo de la clínica con KPIs, gráficos y alertas importantes.

---

## 📋 Requisitos Funcionales

### Datos que debe mostrar:
1. **KPIs principales** (4 tarjetas)
   - Total de pacientes activos
   - Citas del día
   - Ingresos del mes actual
   - Saldo pendiente de cobro

2. **Gráfico de tendencia de citas** (últimos 15 días)

3. **Top 5 procedimientos más realizados**

4. **Estadísticas generales** (resumen completo)

5. **Alertas importantes**
   - Insumos con stock bajo
   - Citas pendientes de confirmación
   - Facturas vencidas

6. **Actividad reciente** (últimas acciones del equipo)

---

## 🔌 Endpoints a Consumir

```typescript
// 1. KPIs principales
GET /api/reportes/reportes/dashboard-kpis/
Response: [
  { etiqueta: "Pacientes Activos", valor: 150 },
  { etiqueta: "Citas Hoy", valor: 8 },
  { etiqueta: "Ingresos Este Mes", valor: "$25,000.00" },
  { etiqueta: "Saldo Pendiente", valor: "$5,000.00" }
]

// 2. Tendencia de citas
GET /api/reportes/reportes/tendencia-citas/?dias=15
Response: [
  { fecha: "2025-11-01", cantidad: 5 },
  { fecha: "2025-11-02", cantidad: 8 },
  ...
]

// 3. Top procedimientos
GET /api/reportes/reportes/top-procedimientos/?limite=5
Response: [
  { etiqueta: "Limpieza Dental", valor: 25 },
  { etiqueta: "Endodoncia", valor: 15 },
  ...
]

// 4. Estadísticas generales
GET /api/reportes/reportes/estadisticas-generales/
Response: {
  total_pacientes_activos: 150,
  total_odontologos: 5,
  citas_mes_actual: 120,
  tratamientos_completados: 45,
  ingresos_mes_actual: 25000.00,
  promedio_factura: 555.55,
  tasa_ocupacion: 85.50
}

// 5. Inventario con stock bajo
GET /api/inventario/insumos/bajo_stock/
Response: {
  count: 3,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      nombre: "Resina 3M Filtek",
      stock_actual: 5,
      stock_minimo: 10,
      categoria: { id: 1, nombre: "Materiales Restaurativos" },
      ...
    }
  ]
}

// 6. Actividad reciente (bitácora)
GET /api/reportes/bitacora/?page=1&page_size=10
Response: {
  count: 1250,
  results: [
    {
      id: 1,
      usuario_nombre: "Dr. Juan Pérez",
      accion_display: "Crear",
      descripcion: "Creó nuevo paciente María García",
      fecha_hora: "2025-11-20T14:30:00Z"
    }
  ]
}
```

---

## 💻 Implementación Frontend

### 1. Página Dashboard

```typescript
// src/pages/admin/Dashboard.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import KPICard from '@/components/admin/KPICard';
import LineChart from '@/components/admin/LineChart';
import BarChart from '@/components/admin/BarChart';
import AlertList from '@/components/admin/AlertList';
import ActivityTimeline from '@/components/admin/ActivityTimeline';
import StatsGrid from '@/components/admin/StatsGrid';
import { dashboardService } from '@/services/admin/dashboardService';

export default function Dashboard() {
  // Fetch de datos
  const { data: kpis, isLoading: loadingKpis } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: dashboardService.getKPIs,
    refetchInterval: 30000, // Refetch cada 30 segundos
  });

  const { data: tendencia } = useQuery({
    queryKey: ['tendencia-citas', 15],
    queryFn: () => dashboardService.getTendenciaCitas(15),
  });

  const { data: topProcedimientos } = useQuery({
    queryKey: ['top-procedimientos', 5],
    queryFn: () => dashboardService.getTopProcedimientos(5),
  });

  const { data: estadisticas } = useQuery({
    queryKey: ['estadisticas-generales'],
    queryFn: dashboardService.getEstadisticasGenerales,
  });

  const { data: stockBajo } = useQuery({
    queryKey: ['stock-bajo'],
    queryFn: dashboardService.getStockBajo,
  });

  const { data: actividad } = useQuery({
    queryKey: ['actividad-reciente'],
    queryFn: dashboardService.getActividadReciente,
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Bienvenido al panel de administración</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {loadingKpis ? (
          <KPISkeleton count={4} />
        ) : (
          kpis?.map((kpi, index) => (
            <KPICard
              key={index}
              label={kpi.etiqueta}
              value={kpi.valor}
              icon={getKPIIcon(index)}
              color={getKPIColor(index)}
            />
          ))
        )}
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencia de Citas */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tendencia de Citas</h2>
          {tendencia && (
            <LineChart
              data={tendencia}
              xKey="fecha"
              yKey="cantidad"
              color="#3b82f6"
            />
          )}
        </div>

        {/* Top Procedimientos */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Top Procedimientos</h2>
          {topProcedimientos && (
            <BarChart
              data={topProcedimientos}
              xKey="etiqueta"
              yKey="valor"
              color="#10b981"
            />
          )}
        </div>
      </div>

      {/* Estadísticas y Alertas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Estadísticas */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Estadísticas Generales</h2>
          {estadisticas && <StatsGrid stats={estadisticas} />}
        </div>

        {/* Alertas */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Alertas</h2>
          <AlertList alerts={[
            {
              type: 'warning',
              title: 'Stock Bajo',
              message: `${stockBajo?.count || 0} insumos con stock bajo`,
              link: '/admin/inventario?stock_bajo=true'
            },
            // Más alertas...
          ]} />
        </div>
      </div>

      {/* Actividad Reciente */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Actividad Reciente</h2>
        {actividad && <ActivityTimeline activities={actividad.results} />}
      </div>
    </div>
  );
}

// Helpers
function getKPIIcon(index: number) {
  const icons = ['Users', 'Calendar', 'DollarSign', 'AlertCircle'];
  return icons[index];
}

function getKPIColor(index: number) {
  const colors = ['blue', 'green', 'purple', 'orange'];
  return colors[index];
}
```

---

### 2. Componente KPICard

```typescript
// src/components/admin/KPICard.tsx
import React from 'react';
import * as Icons from 'lucide-react';
import { cn } from '@/lib/utils';

interface KPICardProps {
  label: string;
  value: string | number;
  icon: keyof typeof Icons;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export default function KPICard({ 
  label, 
  value, 
  icon, 
  color = 'blue',
  trend 
}: KPICardProps) {
  const Icon = Icons[icon] as React.ElementType;

  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 font-medium">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          
          {trend && (
            <div className="flex items-center mt-2">
              <span className={cn(
                'text-sm font-medium',
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              )}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-xs text-gray-500 ml-2">vs mes anterior</span>
            </div>
          )}
        </div>

        <div className={cn(
          'w-12 h-12 rounded-lg flex items-center justify-center',
          colorClasses[color]
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}
```

---

### 3. Servicio Dashboard

```typescript
// src/services/admin/dashboardService.ts
import api from '@/lib/axios';

export const dashboardService = {
  // KPIs principales
  async getKPIs() {
    const { data } = await api.get('/reportes/reportes/dashboard-kpis/');
    return data;
  },

  // Tendencia de citas
  async getTendenciaCitas(dias: number = 15) {
    const { data } = await api.get('/reportes/reportes/tendencia-citas/', {
      params: { dias }
    });
    return data;
  },

  // Top procedimientos
  async getTopProcedimientos(limite: number = 5) {
    const { data } = await api.get('/reportes/reportes/top-procedimientos/', {
      params: { limite }
    });
    return data;
  },

  // Estadísticas generales
  async getEstadisticasGenerales() {
    const { data } = await api.get('/reportes/reportes/estadisticas-generales/');
    return data;
  },

  // Stock bajo (usando acción custom)
  async getStockBajo() {
    const { data } = await api.get('/inventario/insumos/bajo_stock/', {
      params: { page_size: 10 }
    });
    return data;
  },

  // Actividad reciente
  async getActividadReciente() {
    const { data } = await api.get('/reportes/bitacora/', {
      params: { page: 1, page_size: 10 }
    });
    return data;
  },
};
```

---

### 4. Componente LineChart

```typescript
// src/components/admin/LineChart.tsx
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface LineChartProps {
  data: Array<{ [key: string]: any }>;
  xKey: string;
  yKey: string;
  color?: string;
  label?: string;
}

export default function LineChart({ 
  data, 
  xKey, 
  yKey, 
  color = '#3b82f6',
  label = 'Datos'
}: LineChartProps) {
  const chartData = {
    labels: data.map(item => item[xKey]),
    datasets: [
      {
        label,
        data: data.map(item => item[yKey]),
        borderColor: color,
        backgroundColor: `${color}20`,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Line data={chartData} options={options} />
    </div>
  );
}
```

---

### 5. Componente BarChart

```typescript
// src/components/admin/BarChart.tsx
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BarChartProps {
  data: Array<{ [key: string]: any }>;
  xKey: string;
  yKey: string;
  color?: string;
  label?: string;
}

export default function BarChart({ 
  data, 
  xKey, 
  yKey, 
  color = '#10b981',
  label = 'Cantidad'
}: BarChartProps) {
  const chartData = {
    labels: data.map(item => item[xKey]),
    datasets: [
      {
        label,
        data: data.map(item => item[yKey]),
        backgroundColor: color,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
}
```

---

## 🎨 Diseño Visual

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ Dashboard                                    [Refresh] │
│ Bienvenido al panel de administración                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │ 150  │  │  8   │  │$25K  │  │ $5K  │              │
│  │Pacien│  │Citas │  │Ingre │  │Saldo │              │
│  └──────┘  └──────┘  └──────┘  └──────┘              │
│                                                         │
│  ┌────────────────────┐  ┌────────────────────┐       │
│  │ Tendencia Citas    │  │ Top Procedimientos │       │
│  │                    │  │                    │       │
│  │   [Gráfico Línea]  │  │   [Gráfico Barras] │       │
│  └────────────────────┘  └────────────────────┘       │
│                                                         │
│  ┌──────────────────────────────┐  ┌──────────┐       │
│  │ Estadísticas Generales       │  │ Alertas  │       │
│  │ • Total odontólogos: 5       │  │ ⚠ Stock  │       │
│  │ • Tratamientos: 45           │  │   Bajo   │       │
│  │ • Tasa ocupación: 85.5%      │  │          │       │
│  └──────────────────────────────┘  └──────────┘       │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │ Actividad Reciente                          │       │
│  │ ○ Dr. Pérez creó paciente María García      │       │
│  │ ○ Ana López registró pago de $500           │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Actualización en Tiempo Real

```typescript
// Refetch automático cada 30 segundos
const { data: kpis } = useQuery({
  queryKey: ['dashboard-kpis'],
  queryFn: dashboardService.getKPIs,
  refetchInterval: 30000, // 30 segundos
  refetchOnWindowFocus: true, // Refetch al volver a la ventana
});

// Invalidación manual
const queryClient = useQueryClient();

function handleRefresh() {
  queryClient.invalidateQueries({ queryKey: ['dashboard-kpis'] });
  queryClient.invalidateQueries({ queryKey: ['tendencia-citas'] });
  // ...más queries
}
```

---

## 📱 Versión Móvil

### Ajustes Responsive
```typescript
// Cambiar grid en móvil
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* KPIs */}
</div>

// Stack vertical en móvil
<div className="flex flex-col lg:flex-row gap-6">
  {/* Gráficos */}
</div>
```

---

## ✅ Checklist de Implementación

- [ ] Crear página Dashboard.tsx
- [ ] Crear componente KPICard
- [ ] Crear componente LineChart
- [ ] Crear componente BarChart
- [ ] Crear componente StatsGrid
- [ ] Crear componente AlertList
- [ ] Crear componente ActivityTimeline
- [ ] Crear dashboardService.ts
- [ ] Configurar React Query
- [ ] Configurar Chart.js
- [ ] Implementar loading states
- [ ] Implementar error handling
- [ ] Añadir refetch automático
- [ ] Probar en móvil/tablet/desktop
- [ ] Optimizar performance

---

**Siguiente:** `02_gestion_usuarios.md` - Gestión de equipo de trabajo
