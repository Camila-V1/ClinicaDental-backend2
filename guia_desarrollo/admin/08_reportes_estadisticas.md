# 📊 Reportes y Estadísticas

## 🎯 Objetivo
Visualizar reportes dinámicos, estadísticas y exportarlos en PDF/Excel.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Dashboard con KPIs** principales
2. **Reportes dinámicos** con filtros personalizables
3. **Gráficas interactivas** (Chart.js)
4. **Exportar** reportes en PDF y Excel
5. **Filtros avanzados**: fecha, odontólogo, servicio, etc.
6. **Reportes disponibles**:
   - Tendencia de citas
   - Top procedimientos
   - Estadísticas generales
   - Reporte financiero
   - Ocupación de odontólogos
   - Pacientes nuevos vs recurrentes
   - Tratamientos en progreso
   - Ingresos diarios
   - Servicios más populares

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Dashboard KPIs
GET /api/reportes/dashboard-kpis/
Response: {
  total_pacientes: 150,
  pacientes_nuevos_mes: 12,
  citas_hoy: 8,
  citas_mes: 120,
  ingresos_mes: 45000.00,
  tratamientos_activos: 25,
  ocupacion_promedio: 75.5
}

// 2. Tendencia de citas
GET /api/reportes/tendencia-citas/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30
Response: {
  tendencia: [
    { fecha: "2025-11-01", total_citas: 12, confirmadas: 10, completadas: 8 },
    { fecha: "2025-11-02", total_citas: 15, confirmadas: 13, completadas: 12 }
  ]
}

// 3. Top procedimientos
GET /api/reportes/top-procedimientos/?limite=10
Response: {
  procedimientos: [
    { servicio: "Limpieza Dental", cantidad: 145, ingresos: 21750.00 },
    { servicio: "Resina", cantidad: 89, ingresos: 22250.00 }
  ]
}

// 4. Estadísticas generales
GET /api/reportes/estadisticas-generales/
Response: {
  pacientes: { total: 150, activos: 140, nuevos_mes: 12 },
  citas: { total: 500, pendientes: 50, completadas: 400 },
  tratamientos: { total: 80, en_progreso: 25, completados: 50 },
  financiero: { ingresos_totales: 150000.00, por_cobrar: 25000.00 }
}

// 5. Reporte financiero
GET /api/reportes/reporte-financiero/?periodo=mensual&formato=pdf
Response: Binary PDF file

// 6. Ocupación de odontólogos
GET /api/reportes/ocupacion-odontologos/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30
Response: {
  odontologos: [
    {
      odontologo: "Dr. Juan Pérez",
      total_citas: 85,
      horas_trabajadas: 120,
      porcentaje_ocupacion: 80.5
    }
  ]
}

// 7. Exportar reporte
GET /api/reportes/reporte-pacientes/?formato=excel
Response: Binary Excel file
```

---

## 💻 Implementación Frontend

### 1. Página de Reportes

```typescript
// src/pages/admin/Reportes.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportesService } from '@/services/admin/reportesService';
import TendenciaCitasChart from '@/components/admin/reportes/TendenciaCitasChart';
import TopProcedimientosChart from '@/components/admin/reportes/TopProcedimientosChart';
import OcupacionChart from '@/components/admin/reportes/OcupacionChart';
import { Download } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function Reportes() {
  const [periodo, setPeriodo] = useState<'semanal' | 'mensual' | 'anual'>('mensual');
  const [fechaInicio, setFechaInicio] = useState(
    new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]
  );
  const [fechaFin, setFechaFin] = useState(
    new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().split('T')[0]
  );

  // Fetch KPIs
  const { data: kpis } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: reportesService.getDashboardKPIs,
  });

  // Fetch tendencia citas
  const { data: tendencia } = useQuery({
    queryKey: ['tendencia-citas', fechaInicio, fechaFin],
    queryFn: () => reportesService.getTendenciaCitas({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }),
  });

  // Fetch top procedimientos
  const { data: topProcedimientos } = useQuery({
    queryKey: ['top-procedimientos'],
    queryFn: () => reportesService.getTopProcedimientos({ limite: 10 }),
  });

  // Fetch ocupación odontólogos
  const { data: ocupacion } = useQuery({
    queryKey: ['ocupacion-odontologos', fechaInicio, fechaFin],
    queryFn: () =>
      reportesService.getOcupacionOdontologos({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }),
  });

  // Exportar reporte
  const handleExport = async (tipo: string, formato: 'pdf' | 'excel') => {
    try {
      const blob = await reportesService.exportarReporte(tipo, formato, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `reporte_${tipo}_${new Date().toISOString().split('T')[0]}.${formato === 'pdf' ? 'pdf' : 'xlsx'}`;
      a.click();
      toast.success('Reporte descargado');
    } catch (error) {
      toast.error('Error al descargar reporte');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reportes y Estadísticas</h1>
        <p className="text-gray-600">Visualiza métricas y exporta reportes</p>
      </div>

      {/* Filtros globales */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Periodo</label>
            <select
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value as any)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="semanal">Semanal</option>
              <option value="mensual">Mensual</option>
              <option value="anual">Anual</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Desde</label>
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hasta</label>
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* KPIs */}
      {kpis && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
            <p className="text-sm opacity-90">Pacientes Totales</p>
            <p className="text-3xl font-bold">{kpis.total_pacientes}</p>
            <p className="text-sm opacity-75 mt-1">+{kpis.pacientes_nuevos_mes} este mes</p>
          </div>
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
            <p className="text-sm opacity-90">Citas del Mes</p>
            <p className="text-3xl font-bold">{kpis.citas_mes}</p>
            <p className="text-sm opacity-75 mt-1">{kpis.citas_hoy} hoy</p>
          </div>
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
            <p className="text-sm opacity-90">Ingresos del Mes</p>
            <p className="text-3xl font-bold">${kpis.ingresos_mes.toLocaleString()}</p>
          </div>
          <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow p-6 text-white">
            <p className="text-sm opacity-90">Tratamientos Activos</p>
            <p className="text-3xl font-bold">{kpis.tratamientos_activos}</p>
            <p className="text-sm opacity-75 mt-1">{kpis.ocupacion_promedio}% ocupación</p>
          </div>
        </div>
      )}

      {/* Gráficas */}
      <div className="grid grid-cols-2 gap-6">
        {/* Tendencia de citas */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Tendencia de Citas</h2>
            <div className="flex gap-2">
              <button
                onClick={() => handleExport('tendencia-citas', 'pdf')}
                className="p-2 text-gray-600 hover:text-gray-800"
                title="Exportar PDF"
              >
                <Download className="w-5 h-5" />
              </button>
            </div>
          </div>
          {tendencia && <TendenciaCitasChart data={tendencia.tendencia} />}
        </div>

        {/* Top procedimientos */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Procedimientos Más Realizados</h2>
            <button
              onClick={() => handleExport('top-procedimientos', 'excel')}
              className="p-2 text-gray-600 hover:text-gray-800"
              title="Exportar Excel"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
          {topProcedimientos && <TopProcedimientosChart data={topProcedimientos.procedimientos} />}
        </div>

        {/* Ocupación odontólogos */}
        <div className="bg-white rounded-lg shadow p-6 col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Ocupación de Odontólogos</h2>
            <button
              onClick={() => handleExport('ocupacion-odontologos', 'pdf')}
              className="p-2 text-gray-600 hover:text-gray-800"
              title="Exportar PDF"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
          {ocupacion && <OcupacionChart data={ocupacion.odontologos} />}
        </div>
      </div>

      {/* Exportaciones rápidas */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Exportar Reportes</h2>
        <div className="grid grid-cols-3 gap-4">
          <button
            onClick={() => handleExport('reporte-financiero', 'pdf')}
            className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left"
          >
            <p className="font-semibold">Reporte Financiero</p>
            <p className="text-sm text-gray-600">Ingresos y cuentas por cobrar</p>
          </button>
          <button
            onClick={() => handleExport('reporte-pacientes', 'excel')}
            className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left"
          >
            <p className="font-semibold">Reporte de Pacientes</p>
            <p className="text-sm text-gray-600">Listado completo de pacientes</p>
          </button>
          <button
            onClick={() => handleExport('reporte-tratamientos', 'pdf')}
            className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left"
          >
            <p className="font-semibold">Reporte de Tratamientos</p>
            <p className="text-sm text-gray-600">Planes en progreso y completados</p>
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### 2. Componente de Gráfica de Tendencia

```typescript
// src/components/admin/reportes/TendenciaCitasChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface TendenciaCitasChartProps {
  data: any[];
}

export default function TendenciaCitasChart({ data }: TendenciaCitasChartProps) {
  const chartData = {
    labels: data.map((d) => new Date(d.fecha).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })),
    datasets: [
      {
        label: 'Total Citas',
        data: data.map((d) => d.total_citas),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3,
      },
      {
        label: 'Confirmadas',
        data: data.map((d) => d.confirmadas),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.3,
      },
      {
        label: 'Completadas',
        data: data.map((d) => d.completadas),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
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

### 3. Componente de Gráfica de Procedimientos

```typescript
// src/components/admin/reportes/TopProcedimientosChart.tsx
import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface TopProcedimientosChartProps {
  data: any[];
}

export default function TopProcedimientosChart({ data }: TopProcedimientosChartProps) {
  const chartData = {
    labels: data.map((d) => d.servicio),
    datasets: [
      {
        label: 'Cantidad',
        data: data.map((d) => d.cantidad),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
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

### 4. Servicio de Reportes

```typescript
// src/services/admin/reportesService.ts
import api from '@/lib/axios';

export const reportesService = {
  // KPIs
  async getDashboardKPIs() {
    const { data } = await api.get('/reportes/dashboard-kpis/');
    return data;
  },

  // Tendencia de citas
  async getTendenciaCitas(params: any) {
    const { data } = await api.get('/reportes/tendencia-citas/', { params });
    return data;
  },

  // Top procedimientos
  async getTopProcedimientos(params: any) {
    const { data } = await api.get('/reportes/top-procedimientos/', { params });
    return data;
  },

  // Estadísticas generales
  async getEstadisticasGenerales() {
    const { data } = await api.get('/reportes/estadisticas-generales/');
    return data;
  },

  // Ocupación odontólogos
  async getOcupacionOdontologos(params: any) {
    const { data } = await api.get('/reportes/ocupacion-odontologos/', { params });
    return data;
  },

  // Exportar reporte
  async exportarReporte(tipo: string, formato: 'pdf' | 'excel', params: any = {}) {
    const { data } = await api.get(`/reportes/${tipo}/`, {
      params: { ...params, formato },
      responseType: 'blob',
    });
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Instalar Chart.js y react-chartjs-2
- [ ] Crear página Reportes.tsx
- [ ] Crear TendenciaCitasChart
- [ ] Crear TopProcedimientosChart
- [ ] Crear OcupacionChart
- [ ] Crear reportesService
- [ ] Implementar filtros de fecha
- [ ] Exportación PDF/Excel
- [ ] KPIs visuales con gradientes
- [ ] Gráficas interactivas

---

**Siguiente:** `09_bitacora_auditoria.md`
