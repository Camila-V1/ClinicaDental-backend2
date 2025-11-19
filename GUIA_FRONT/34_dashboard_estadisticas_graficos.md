# Guía 34: Dashboard Completo con Estadísticas y Gráficos

## 📋 Información General

**Caso de Uso**: CU01 - Dashboard del Paciente  
**Actor**: Paciente  
**Objetivo**: Visualizar resumen ejecutivo con estadísticas, gráficos y accesos rápidos

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver estadísticas generales (citas, tratamientos, pagos)
- ✅ Visualizar gráficos de evolución temporal
- ✅ Ver timeline de actividad reciente
- ✅ Acceder a alertas urgentes (citas próximas, pagos pendientes)
- ✅ Ver mini calendario con citas marcadas
- ✅ Ver progreso de tratamientos activos
- ✅ Accesos rápidos a secciones principales

---

## 🔌 API Endpoints Necesarios

Los endpoints ya existen, solo necesitamos combinarlos:

```
GET /api/agenda/citas/?fecha_inicio={hoy}&ordering=fecha_hora&limit=5
GET /api/historial/historiales/mi_historial/
GET /api/tratamientos/planes/?estado=en_progreso
GET /api/tratamientos/planes/propuestos/?estado=propuesto
GET /api/facturacion/facturas/estado_cuenta/
GET /api/facturacion/facturas/mis_facturas/?estado=pendiente
```

---

## 📦 Librerías de Gráficos

### Opción 1: Recharts (Recomendada)
```bash
npm install recharts
```

**Pros**:
- ✅ Componentes React nativos
- ✅ Responsive automático
- ✅ API simple y declarativa
- ✅ Animaciones suaves

### Opción 2: Chart.js con react-chartjs-2
```bash
npm install chart.js react-chartjs-2
```

**Pros**:
- ✅ Más tipos de gráficos
- ✅ Altamente personalizable
- ✅ Documentación extensa

---

## 🔧 Implementación Frontend

### 1. Service - `dashboardService.ts`

```typescript
// src/services/dashboardService.ts

import apiClient from '../config/apiConfig';

/**
 * Obtiene estadísticas completas del dashboard
 */
export const obtenerEstadisticasDashboard = async (): Promise<any> => {
  console.log('📊 Obteniendo estadísticas del dashboard...');
  
  try {
    // Hacer todas las peticiones en paralelo
    const [
      citasResponse,
      historialResponse,
      planesActivosResponse,
      planesPropuestosResponse,
      estadoCuentaResponse
    ] = await Promise.all([
      apiClient.get('/api/agenda/citas/', {
        params: { 
          fecha_inicio: new Date().toISOString().split('T')[0],
          ordering: 'fecha_hora',
          limit: 5
        }
      }),
      apiClient.get('/api/historial/historiales/mi_historial/'),
      apiClient.get('/api/tratamientos/planes/', { 
        params: { estado: 'en_progreso' } 
      }),
      apiClient.get('/api/tratamientos/planes/propuestos/', { 
        params: { estado: 'propuesto' } 
      }),
      apiClient.get('/api/facturacion/facturas/estado_cuenta/')
    ]);

    const estadisticas = {
      // Citas
      proximasCitas: citasResponse.data || [],
      totalCitasProximas: (citasResponse.data || []).length,
      
      // Historial clínico
      historial: historialResponse.data || {},
      totalDocumentos: historialResponse.data?.documentos?.length || 0,
      totalEpisodios: historialResponse.data?.episodios_count || 0,
      
      // Planes de tratamiento
      planesActivos: planesActivosResponse.data || [],
      totalPlanesActivos: (planesActivosResponse.data || []).length,
      
      planesPropuestos: planesPropuestosResponse.data?.results || planesPropuestosResponse.data || [],
      totalPlanesPropuestos: (planesPropuestosResponse.data?.results || planesPropuestosResponse.data || []).length,
      
      // Finanzas
      estadoCuenta: estadoCuentaResponse.data || {},
      saldoPendiente: estadoCuentaResponse.data?.saldo_pendiente || 0,
      totalFacturado: estadoCuentaResponse.data?.monto_total || 0,
      totalPagado: estadoCuentaResponse.data?.monto_pagado || 0,
      facturasPendientes: estadoCuentaResponse.data?.facturas_pendientes || 0
    };

    console.log('✅ Estadísticas obtenidas exitosamente');
    return estadisticas;
  } catch (error) {
    console.error('❌ Error obteniendo estadísticas:', error);
    throw error;
  }
};

/**
 * Obtiene datos para el gráfico de citas por mes (últimos 6 meses)
 */
export const obtenerGraficoCitas = async (): Promise<any[]> => {
  console.log('📈 Obteniendo datos para gráfico de citas...');
  
  try {
    // Calcular rango de fechas (últimos 6 meses)
    const fechaFin = new Date();
    const fechaInicio = new Date();
    fechaInicio.setMonth(fechaInicio.getMonth() - 6);

    const response = await apiClient.get('/api/agenda/citas/', {
      params: {
        fecha_inicio: fechaInicio.toISOString().split('T')[0],
        fecha_fin: fechaFin.toISOString().split('T')[0]
      }
    });

    const citas = response.data || [];
    
    // Agrupar por mes
    const citasPorMes = agruparCitasPorMes(citas);
    
    console.log('✅ Datos del gráfico obtenidos');
    return citasPorMes;
  } catch (error) {
    console.error('❌ Error obteniendo gráfico:', error);
    return [];
  }
};

/**
 * Agrupa citas por mes
 */
const agruparCitasPorMes = (citas: any[]): any[] => {
  const mesesMap = new Map<string, number>();
  
  // Inicializar últimos 6 meses
  const meses = [];
  for (let i = 5; i >= 0; i--) {
    const fecha = new Date();
    fecha.setMonth(fecha.getMonth() - i);
    const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
    const mesNombre = fecha.toLocaleDateString('es-ES', { month: 'short', year: 'numeric' });
    mesesMap.set(mesKey, 0);
    meses.push({ mes: mesNombre, key: mesKey });
  }
  
  // Contar citas por mes
  citas.forEach(cita => {
    const fecha = new Date(cita.fecha_hora);
    const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
    if (mesesMap.has(mesKey)) {
      mesesMap.set(mesKey, (mesesMap.get(mesKey) || 0) + 1);
    }
  });
  
  // Convertir a array para el gráfico
  return meses.map(m => ({
    mes: m.mes,
    citas: mesesMap.get(m.key) || 0
  }));
};

/**
 * Obtiene timeline de actividad reciente
 */
export const obtenerTimelineActividad = async (): Promise<any[]> => {
  console.log('📜 Obteniendo timeline de actividad...');
  
  try {
    const [citasResponse, planesResponse, facturasResponse] = await Promise.all([
      apiClient.get('/api/agenda/citas/', { params: { limit: 5 } }),
      apiClient.get('/api/tratamientos/planes/', { params: { limit: 3 } }),
      apiClient.get('/api/facturacion/facturas/mis_facturas/', { params: { limit: 3 } })
    ]);

    const actividades: any[] = [];

    // Agregar citas
    (citasResponse.data || []).forEach((cita: any) => {
      actividades.push({
        tipo: 'cita',
        icono: '📅',
        titulo: `Cita: ${cita.motivo || 'Consulta'}`,
        descripcion: `Dr. ${cita.odontologo_nombre}`,
        fecha: cita.fecha_hora,
        estado: cita.estado
      });
    });

    // Agregar planes
    (planesResponse.data || []).forEach((plan: any) => {
      actividades.push({
        tipo: 'plan',
        icono: '🦷',
        titulo: plan.titulo,
        descripcion: `Plan de tratamiento - ${plan.estado_display}`,
        fecha: plan.fecha_creacion,
        estado: plan.estado
      });
    });

    // Agregar facturas
    (facturasResponse.data || []).forEach((factura: any) => {
      actividades.push({
        tipo: 'factura',
        icono: '💰',
        titulo: `Factura #${factura.numero}`,
        descripcion: `${factura.estado_display} - $${factura.monto_total}`,
        fecha: factura.fecha_emision,
        estado: factura.estado
      });
    });

    // Ordenar por fecha descendente
    actividades.sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime());

    console.log('✅ Timeline obtenido:', actividades.length, 'actividades');
    return actividades.slice(0, 10); // Máximo 10
  } catch (error) {
    console.error('❌ Error obteniendo timeline:', error);
    return [];
  }
};

/**
 * Formatea fecha relativa (ej: "hace 2 días")
 */
export const formatearFechaRelativa = (fechaISO: string): string => {
  const fecha = new Date(fechaISO);
  const ahora = new Date();
  const diffMs = ahora.getTime() - fecha.getTime();
  const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDias === 0) return 'Hoy';
  if (diffDias === 1) return 'Ayer';
  if (diffDias < 7) return `Hace ${diffDias} días`;
  if (diffDias < 30) return `Hace ${Math.floor(diffDias / 7)} semanas`;
  return fecha.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
};
```

---

### 2. Componente - `DashboardPaciente.tsx` (Mejorado)

```tsx
// src/pages/paciente/DashboardPaciente.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  obtenerEstadisticasDashboard,
  obtenerGraficoCitas,
  obtenerTimelineActividad,
  formatearFechaRelativa
} from '../../services/dashboardService';

// Componentes de Dashboard
import EstadisticasCards from '../../components/dashboard/EstadisticasCards';
import GraficoCitas from '../../components/dashboard/GraficoCitas';
import ProximasCitas from '../../components/dashboard/ProximasCitas';
import AlertasUrgentes from '../../components/dashboard/AlertasUrgentes';
import TimelineActividad from '../../components/dashboard/TimelineActividad';
import ProgresoTratamientos from '../../components/dashboard/ProgresoTratamientos';
import AccesosRapidos from '../../components/dashboard/AccesosRapidos';

export default function DashboardPaciente() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [estadisticas, setEstadisticas] = useState<any>(null);
  const [graficoCitas, setGraficoCitas] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarDashboard();
  }, []);

  const cargarDashboard = async () => {
    try {
      setCargando(true);
      setError(null);

      // Cargar todo en paralelo
      const [stats, grafico, timelineData] = await Promise.all([
        obtenerEstadisticasDashboard(),
        obtenerGraficoCitas(),
        obtenerTimelineActividad()
      ]);

      setEstadisticas(stats);
      setGraficoCitas(grafico);
      setTimeline(timelineData);
    } catch (err: any) {
      console.error('❌ Error cargando dashboard:', err);
      setError('Error al cargar el dashboard');
    } finally {
      setCargando(false);
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={cargarDashboard}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            🔄 Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header con Saludo */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800">
          ¡Hola, {user?.nombre}! 👋
        </h1>
        <p className="text-gray-600 mt-2">
          Bienvenido a tu portal de salud dental
        </p>
      </div>

      {/* Alertas Urgentes (si existen) */}
      <AlertasUrgentes estadisticas={estadisticas} />

      {/* Cards de Estadísticas Principales */}
      <EstadisticasCards estadisticas={estadisticas} />

      {/* Grid Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        
        {/* Columna Izquierda (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Gráfico de Citas */}
          <GraficoCitas datos={graficoCitas} />

          {/* Próximas Citas */}
          <ProximasCitas citas={estadisticas?.proximasCitas || []} />

          {/* Progreso de Tratamientos */}
          {estadisticas?.planesActivos?.length > 0 && (
            <ProgresoTratamientos planes={estadisticas.planesActivos} />
          )}

        </div>

        {/* Columna Derecha (1/3) */}
        <div className="space-y-6">
          
          {/* Accesos Rápidos */}
          <AccesosRapidos estadisticas={estadisticas} />

          {/* Timeline de Actividad */}
          <TimelineActividad actividades={timeline} />

        </div>

      </div>

    </div>
  );
}
```

---

### 3. Componente - `EstadisticasCards.tsx`

```tsx
// src/components/dashboard/EstadisticasCards.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';

interface Props {
  estadisticas: any;
}

export default function EstadisticasCards({ estadisticas }: Props) {
  const navigate = useNavigate();

  const cards = [
    {
      titulo: 'Próximas Citas',
      valor: estadisticas?.totalCitasProximas || 0,
      icono: '📅',
      color: 'bg-blue-500',
      ruta: '/paciente/citas'
    },
    {
      titulo: 'Tratamientos Activos',
      valor: estadisticas?.totalPlanesActivos || 0,
      icono: '🦷',
      color: 'bg-green-500',
      ruta: '/paciente/planes'
    },
    {
      titulo: 'Solicitudes Pendientes',
      valor: estadisticas?.totalPlanesPropuestos || 0,
      icono: '📋',
      color: 'bg-yellow-500',
      ruta: '/paciente/solicitudes'
    },
    {
      titulo: 'Saldo Pendiente',
      valor: `$${estadisticas?.saldoPendiente?.toFixed(2) || '0.00'}`,
      icono: '💰',
      color: 'bg-red-500',
      ruta: '/paciente/facturas'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div
          key={index}
          onClick={() => navigate(card.ruta)}
          className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow duration-300"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">{card.titulo}</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{card.valor}</p>
            </div>
            <div className={`${card.color} rounded-full p-4 text-white text-3xl`}>
              {card.icono}
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-blue-600 font-medium hover:text-blue-800">
              Ver detalles →
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

### 4. Componente - `GraficoCitas.tsx`

```tsx
// src/components/dashboard/GraficoCitas.tsx

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface Props {
  datos: any[];
}

export default function GraficoCitas({ datos }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        📈 Citas por Mes (Últimos 6 meses)
      </h2>
      
      {datos.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={datos}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mes" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="citas" fill="#3B82F6" name="Citas Realizadas" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <span className="text-6xl">📊</span>
            <p className="mt-4">No hay datos suficientes para el gráfico</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### 5. Componente - `AlertasUrgentes.tsx`

```tsx
// src/components/dashboard/AlertasUrgentes.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';

interface Props {
  estadisticas: any;
}

export default function AlertasUrgentes({ estadisticas }: Props) {
  const navigate = useNavigate();
  const alertas = [];

  // Verificar solicitudes pendientes
  if (estadisticas?.totalPlanesPropuestos > 0) {
    alertas.push({
      tipo: 'warning',
      icono: '⚠️',
      titulo: 'Solicitudes Pendientes',
      mensaje: `Tienes ${estadisticas.totalPlanesPropuestos} ${
        estadisticas.totalPlanesPropuestos === 1 ? 'solicitud' : 'solicitudes'
      } de tratamiento pendientes de aprobar`,
      accion: 'Ver Solicitudes',
      ruta: '/paciente/solicitudes',
      color: 'bg-yellow-50 border-yellow-200'
    });
  }

  // Verificar saldo pendiente
  if (estadisticas?.saldoPendiente > 0) {
    alertas.push({
      tipo: 'error',
      icono: '💳',
      titulo: 'Saldo Pendiente',
      mensaje: `Tienes un saldo pendiente de $${estadisticas.saldoPendiente.toFixed(2)}`,
      accion: 'Ver Facturas',
      ruta: '/paciente/facturas',
      color: 'bg-red-50 border-red-200'
    });
  }

  // Verificar citas próximas (menos de 48 horas)
  const citasProximas = estadisticas?.proximasCitas?.filter((cita: any) => {
    const fechaCita = new Date(cita.fecha_hora);
    const ahora = new Date();
    const diffHoras = (fechaCita.getTime() - ahora.getTime()) / (1000 * 60 * 60);
    return diffHoras > 0 && diffHoras < 48;
  });

  if (citasProximas?.length > 0) {
    alertas.push({
      tipo: 'info',
      icono: '📅',
      titulo: 'Citas Próximas',
      mensaje: `Tienes ${citasProximas.length} ${
        citasProximas.length === 1 ? 'cita' : 'citas'
      } en las próximas 48 horas`,
      accion: 'Ver Citas',
      ruta: '/paciente/citas',
      color: 'bg-blue-50 border-blue-200'
    });
  }

  if (alertas.length === 0) return null;

  return (
    <div className="space-y-4 mb-6">
      {alertas.map((alerta, index) => (
        <div
          key={index}
          className={`${alerta.color} border rounded-lg p-4`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start">
              <span className="text-3xl mr-3">{alerta.icono}</span>
              <div>
                <h3 className="font-bold text-gray-800">{alerta.titulo}</h3>
                <p className="text-gray-700 text-sm mt-1">{alerta.mensaje}</p>
              </div>
            </div>
            <button
              onClick={() => navigate(alerta.ruta)}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-sm"
            >
              {alerta.accion}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

### 6. Componente - `TimelineActividad.tsx`

```tsx
// src/components/dashboard/TimelineActividad.tsx

import React from 'react';
import { formatearFechaRelativa } from '../../services/dashboardService';

interface Props {
  actividades: any[];
}

export default function TimelineActividad({ actividades }: Props) {
  const getColorEstado = (estado: string) => {
    switch (estado?.toLowerCase()) {
      case 'completado':
      case 'pagada':
      case 'aprobado':
        return 'bg-green-100 text-green-800';
      case 'pendiente':
      case 'propuesto':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelado':
      case 'rechazado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        📜 Actividad Reciente
      </h2>

      {actividades.length > 0 ? (
        <div className="space-y-4">
          {actividades.map((actividad, index) => (
            <div key={index} className="flex items-start gap-3">
              <span className="text-2xl flex-shrink-0">{actividad.icono}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 text-sm truncate">
                  {actividad.titulo}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {actividad.descripcion}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-gray-500">
                    {formatearFechaRelativa(actividad.fecha)}
                  </span>
                  {actividad.estado && (
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getColorEstado(actividad.estado)}`}>
                      {actividad.estado}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <span className="text-4xl">📭</span>
          <p className="mt-2 text-sm">No hay actividad reciente</p>
        </div>
      )}
    </div>
  );
}
```

---

### 7. Componente - `ProgresoTratamientos.tsx`

```tsx
// src/components/dashboard/ProgresoTratamientos.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';

interface Props {
  planes: any[];
}

export default function ProgresoTratamientos({ planes }: Props) {
  const navigate = useNavigate();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          🦷 Tratamientos en Progreso
        </h2>
        <button
          onClick={() => navigate('/paciente/planes')}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Ver todos →
        </button>
      </div>

      <div className="space-y-4">
        {planes.slice(0, 3).map((plan: any) => {
          const progreso = plan.porcentaje_completado || 0;
          
          return (
            <div
              key={plan.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
              onClick={() => navigate(`/paciente/planes/${plan.id}`)}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-gray-800">{plan.titulo}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Dr. {plan.odontologo_nombre}
                  </p>
                </div>
                <span className="text-sm font-bold text-blue-600">
                  {progreso}%
                </span>
              </div>

              {/* Barra de Progreso */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${progreso}%` }}
                  />
                </div>
              </div>

              {/* Items Info */}
              <div className="mt-2 flex items-center justify-between text-xs text-gray-600">
                <span>
                  {plan.items_completados || 0} de {plan.total_items || 0} procedimientos
                </span>
                <span className="text-blue-600 font-medium">Ver detalles →</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

---

## 📦 Instalación de Dependencias

```bash
# En tu proyecto frontend
npm install recharts
```

---

## 🎨 Características de la UI

### 1. Cards de Estadísticas
- **4 métricas principales**: Citas, Tratamientos, Solicitudes, Saldo
- **Colores distintivos**: Azul, Verde, Amarillo, Rojo
- **Hover effect**: Sombra expandida
- **Clickeable**: Navega a sección correspondiente

### 2. Gráfico de Barras
- **Últimos 6 meses**: Evolución temporal de citas
- **Responsive**: Se adapta al tamaño de pantalla
- **Tooltips**: Información al hacer hover
- **Animaciones**: Transiciones suaves

### 3. Alertas Urgentes
- **Colores por tipo**: Amarillo (warning), Rojo (error), Azul (info)
- **Actionable**: Botón para ir a la sección
- **Condicionales**: Solo se muestran si hay alertas

### 4. Timeline de Actividad
- **Iconos por tipo**: 📅 Citas, 🦷 Planes, 💰 Facturas
- **Fechas relativas**: "Hoy", "Ayer", "Hace 3 días"
- **Badges de estado**: Colores según estado
- **Scroll automático**: Máximo 10 items

### 5. Progreso de Tratamientos
- **Barras de progreso**: Visual del porcentaje
- **Clickeable**: Navega al detalle del plan
- **Info rápida**: Items completados/totales
- **Limitado a 3**: Los más recientes

---

## 🔗 Estructura de Archivos

```
src/
├── services/
│   └── dashboardService.ts          ← Nuevo
├── components/
│   └── dashboard/                   ← Nuevo directorio
│       ├── EstadisticasCards.tsx
│       ├── GraficoCitas.tsx
│       ├── AlertasUrgentes.tsx
│       ├── TimelineActividad.tsx
│       ├── ProgresoTratamientos.tsx
│       ├── ProximasCitas.tsx        ← Ya existe (reutilizar)
│       └── AccesosRapidos.tsx       ← Ya existe (reutilizar)
└── pages/
    └── paciente/
        └── DashboardPaciente.tsx    ← Actualizar
```

---

## 📝 Notas Importantes

### 1. Optimización de Rendimiento
- ✅ Todas las peticiones en paralelo con `Promise.all()`
- ✅ Estado de carga único para todo el dashboard
- ✅ Componentes separados para mejor tree-shaking
- ✅ Lazy loading de gráficos (opcional)

### 2. Manejo de Errores
- ✅ Try-catch en cada petición
- ✅ Fallback a arrays vacíos si falla
- ✅ Botón de reintentar
- ✅ Mensajes de error descriptivos

### 3. Responsive Design
- ✅ Grid adaptativo (1 col móvil, 2-4 desktop)
- ✅ Gráficos con ResponsiveContainer
- ✅ Layout de 2 columnas en desktop (2/3 + 1/3)

---

## 🧪 Testing

### Casos de Prueba

1. ✅ **Usuario nuevo**: Sin datos, estado vacío
2. ✅ **Con alertas**: Mostrar alertas urgentes
3. ✅ **Sin alertas**: No mostrar sección de alertas
4. ✅ **Gráfico vacío**: Mensaje de no data
5. ✅ **Múltiples tratamientos**: Máximo 3 visibles
6. ✅ **Timeline vacío**: Mensaje de no actividad
7. ✅ **Navegación**: Clic en cards funciona
8. ✅ **Error de red**: Mensaje y botón reintentar
9. ✅ **Responsive**: Mobile y desktop correcto
10. ✅ **Recarga**: Datos actualizados

---

## 🎯 Mejoras Futuras

1. **Gráfico de Pastel**: Distribución de tipos de tratamiento
2. **Calendario Completo**: Vista mensual con todas las citas
3. **Notificaciones Push**: Alertas en tiempo real
4. **Modo Oscuro**: Toggle para tema oscuro
5. **Exportar Reportes**: PDF de actividad mensual
6. **Comparativas**: Mes actual vs anterior
7. **Metas de Salud**: Progreso de objetivos dentales
8. **Integración con Wearables**: Datos de salud general

---

**Siguiente**: Guía 35 - Agendar Cita Interactiva con Calendario
