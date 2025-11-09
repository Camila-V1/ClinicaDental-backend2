# 📊 FASE 6: REPORTES Y DASHBOARD - ANÁLISIS DE DATOS

## 📋 Endpoints de Reportes

### Sistema de reportes, métricas y dashboard ejecutivo

```javascript
// Endpoints reportes (solo los implementados en backend)
const REPORTS_ENDPOINTS = {
  // Dashboard KPIs principales
  dashboardKpis: '/api/reportes/dashboard-kpis/',
  
  // Estadísticas generales del sistema
  generalStats: '/api/reportes/estadisticas-generales/',
  
  // Tendencia de citas (gráfico)
  trendCitas: '/api/reportes/tendencia-citas/',
  
  // Top procedimientos más realizados
  topProcedures: '/api/reportes/top-procedimientos/',
  
  // Reporte financiero por período
  financialReport: '/api/reportes/reporte-financiero/',
  
  // Ocupación por odontólogo
  doctorOccupancy: '/api/reportes/ocupacion-odontologos/'
};
```

## 🔧 1. Servicio de Reportes

```javascript
// services/reportsService.js
import api from './apiConfig';

class ReportsService {
  // Dashboard KPIs principales
  async getDashboardKpis() {
    try {
      const response = await api.get('/api/reportes/dashboard-kpis/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener KPIs del dashboard' };
    }
  }

  // Estadísticas generales del sistema
  async getGeneralStats() {
    try {
      const response = await api.get('/api/reportes/estadisticas-generales/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener estadísticas generales' };
    }
  }

  // Tendencia de citas (gráfico)
  async getTrendCitas(dias = 15) {
    try {
      const params = { dias };
      const response = await api.get('/api/reportes/tendencia-citas/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener tendencia de citas' };
    }
  }

  // Top procedimientos más realizados
  async getTopProcedures(limite = 5) {
    try {
      const params = { limite };
      const response = await api.get('/api/reportes/top-procedimientos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener procedimientos más realizados' };
    }
  }

  // Reporte financiero por período
  async getFinancialReport(periodo = null) {
    try {
      const params = periodo ? { periodo } : {};
      const response = await api.get('/api/reportes/reporte-financiero/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener reporte financiero' };
    }
  }

  // Ocupación por odontólogo
  async getDoctorOccupancy(mes = null) {
    try {
      const params = mes ? { mes } : {};
      const response = await api.get('/api/reportes/ocupacion-odontologos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener ocupación de odontólogos' };
    }
  }
}

export default new ReportsService();
```

## 📊 2. Hook de Reportes

```javascript
// hooks/useReports.js
import { useState, useEffect } from 'react';
import reportsService from '../services/reportsService';

export function useDashboardKpis() {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchKpis = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getDashboardKpis();
    
    if (result.success) {
      setKpis(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchKpis();
  }, []);

  return {
    kpis,
    loading,
    error,
    refetch: fetchKpis
  };
}

export function useGeneralStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getGeneralStats();
    
    if (result.success) {
      setStats(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
}

export function useTrendCitas(dias = 15) {
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTrend = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getTrendCitas(dias);
    
    if (result.success) {
      setTrend(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTrend();
  }, [dias]);

  return {
    trend,
    loading,
    error,
    refetch: fetchTrend
  };
}

export function useTopProcedures(limite = 5) {
  const [procedures, setProcedures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchProcedures = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getTopProcedures(limite);
    
    if (result.success) {
      setProcedures(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchProcedures();
  }, [limite]);

  return {
    procedures,
    loading,
    error,
    refetch: fetchProcedures
  };
}

export function useFinancialReport(periodo = null) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchReport = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getFinancialReport(periodo);
    
    if (result.success) {
      setReport(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchReport();
  }, [periodo]);

  return {
    report,
    loading,
    error,
    refetch: fetchReport
  };
}

export function useDoctorOccupancy(mes = null) {
  const [occupancy, setOccupancy] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchOccupancy = async () => {
    setLoading(true);
    setError('');
    
    const result = await reportsService.getDoctorOccupancy(mes);
    
    if (result.success) {
      setOccupancy(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOccupancy();
  }, [mes]);

  return {
    occupancy,
    loading,
    error,
    refetch: fetchOccupancy
  };
}
```

## 📊 3. Dashboard Principal (PARTE 1/2)

```javascript
// components/Dashboard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useDashboardKpis, useTrendCitas, useTopProcedures } from '../hooks/useReports';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const { kpis, loading: kpisLoading, error: kpisError } = useDashboardKpis();
  const { trend, loading: trendLoading } = useTrendCitas(7);
  const { procedures, loading: proceduresLoading } = useTopProcedures(5);
  const { user } = useAuth();

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 0
    }).format(amount || 0);
  };

  const getKpiIcon = (label) => {
    if (label.includes('Pacientes')) return '👥';
    if (label.includes('Citas')) return '📅';
    if (label.includes('Ingresos')) return '💰';
    if (label.includes('Saldo')) return '💵';
    return '📊';
  };

  if (kpisLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (kpisError) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {kpisError}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard - Clínica Dental
          </h1>
          <p className="text-gray-600">
            Bienvenido/a, {user?.nombre} {user?.apellido} | {user?.tipo_usuario}
          </p>
        </div>
      </div>

      {/* KPIs principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpis.map((kpi, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{kpi.etiqueta}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpi.etiqueta.includes('Ingresos') || kpi.etiqueta.includes('Saldo') 
                    ? formatCurrency(kpi.valor) 
                    : kpi.valor}
                </p>
              </div>
              <div className="text-3xl">{getKpiIcon(kpi.etiqueta)}</div>
            </div>
          </div>
        ))}
      </div>
```

## 📊 3. Dashboard Principal (PARTE 2/2)

```javascript
      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Tendencia de citas */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Tendencia de Citas (7 días)</h3>
            <Link 
              to="/agenda"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver agenda →
            </Link>
          </div>
          
          {trendLoading ? (
            <div className="text-center text-gray-500 py-8">Cargando...</div>
          ) : trend.length > 0 ? (
            <div className="space-y-3">
              {trend.map((day, index) => {
                const maxCitas = Math.max(...trend.map(d => d.cantidad));
                const percentage = maxCitas > 0 ? (day.cantidad / maxCitas * 100) : 0;
                
                return (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 w-24">
                      {new Date(day.fecha).toLocaleDateString('es-BO', { 
                        weekday: 'short', 
                        day: 'numeric',
                        month: 'short'
                      })}
                    </span>
                    <div className="flex items-center space-x-2 flex-1 ml-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-8 text-right">
                        {day.cantidad}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">No hay datos disponibles</div>
          )}
        </div>

        {/* Top procedimientos */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Procedimientos Más Realizados</h3>
            <Link 
              to="/tratamientos"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver tratamientos →
            </Link>
          </div>
          
          {proceduresLoading ? (
            <div className="text-center text-gray-500 py-8">Cargando...</div>
          ) : procedures.length > 0 ? (
            <div className="space-y-3">
              {procedures.map((proc, index) => {
                const maxVal = Math.max(...procedures.map(p => p.valor));
                const percentage = maxVal > 0 ? (proc.valor / maxVal * 100) : 0;
                
                return (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 flex-1 truncate mr-2">
                      {proc.etiqueta}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-8 text-right">
                        {proc.valor}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">No hay datos disponibles</div>
          )}
        </div>
      </div>

      {/* Acciones rápidas */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Acciones Rápidas</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <Link 
            to="/agenda/nueva-cita"
            className="block bg-blue-600 text-white text-center py-3 px-4 rounded-lg hover:bg-blue-700 text-sm"
          >
            📅 Nueva Cita
          </Link>
          
          <Link 
            to="/usuarios/pacientes/crear"
            className="block bg-green-600 text-white text-center py-3 px-4 rounded-lg hover:bg-green-700 text-sm"
          >
            👤 Registrar Paciente
          </Link>
          
          <Link 
            to="/facturacion"
            className="block bg-purple-600 text-white text-center py-3 px-4 rounded-lg hover:bg-purple-700 text-sm"
          >
            💰 Facturación
          </Link>
          
          <Link 
            to="/inventario"
            className="block bg-orange-600 text-white text-center py-3 px-4 rounded-lg hover:bg-orange-700 text-sm"
          >
            📦 Inventario
          </Link>
          
          <Link 
            to="/reportes"
            className="block bg-gray-600 text-white text-center py-3 px-4 rounded-lg hover:bg-gray-700 text-sm"
          >
            📊 Ver Reportes
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
```
    );
  }

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard - Clínica Dental
          </h1>
          <p className="text-gray-600">
            Bienvenido/a, {user?.nombre} | {user?.tipo_usuario}
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Desde:</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value }))}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            />
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Hasta:</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value }))}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            />
          </div>
        </div>
      </div>

      {/* Alertas de rendimiento */}
      {alerts.length > 0 && (
        <div className="mb-6">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className="text-yellow-400 text-xl">⚠️</span>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-yellow-800">
                  Alertas de Rendimiento ({alerts.length})
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <ul className="list-disc list-inside space-y-1">
                    {alerts.slice(0, 3).map((alert, index) => (
                      <li key={index}>{alert.mensaje}</li>
                    ))}
                    {alerts.length > 3 && (
                      <li>
                        <Link to="/reportes/alertas" className="font-medium underline">
                          Ver {alerts.length - 3} alertas más...
                        </Link>
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total de pacientes */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Pacientes</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.total_pacientes || 0}
              </p>
            </div>
            <div className="text-3xl">👥</div>
          </div>
          {dashboardData?.pacientes_nuevos_periodo && (
            <div className="mt-2 flex items-center text-sm">
              <span className={getChangeColor(dashboardData.pacientes_cambio_porcentaje)}>
                {getChangeIcon(dashboardData.pacientes_cambio_porcentaje)}
                {Math.abs(dashboardData.pacientes_cambio_porcentaje)}%
              </span>
              <span className="text-gray-500 ml-1">vs período anterior</span>
            </div>
          )}
        </div>

        {/* Citas del día */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Citas Hoy</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.citas_hoy || 0}
              </p>
            </div>
            <div className="text-3xl">📅</div>
          </div>
          <div className="mt-2 text-sm">
            <span className="text-green-600">
              {dashboardData?.citas_confirmadas_hoy || 0} confirmadas
            </span>
            <span className="text-gray-500 mx-1">•</span>
            <span className="text-yellow-600">
              {dashboardData?.citas_pendientes_hoy || 0} pendientes
            </span>
          </div>
        </div>

        {/* Ingresos del mes */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ingresos del Mes</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(dashboardData?.ingresos_mes || 0)}
              </p>
            </div>
            <div className="text-3xl">💰</div>
          </div>
          {dashboardData?.ingresos_cambio_porcentaje && (
            <div className="mt-2 flex items-center text-sm">
              <span className={getChangeColor(dashboardData.ingresos_cambio_porcentaje)}>
                {getChangeIcon(dashboardData.ingresos_cambio_porcentaje)}
                {Math.abs(dashboardData.ingresos_cambio_porcentaje)}%
              </span>
              <span className="text-gray-500 ml-1">vs mes anterior</span>
            </div>
          )}
        </div>

        {/* Tratamientos completados */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tratamientos Mes</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.tratamientos_mes || 0}
              </p>
            </div>
            <div className="text-3xl">🦷</div>
          </div>
          <div className="mt-2 text-sm">
            <span className="text-blue-600">
              {dashboardData?.tratamientos_completados || 0} completados
            </span>
            <span className="text-gray-500 mx-1">•</span>
            <span className="text-orange-600">
              {dashboardData?.tratamientos_en_proceso || 0} en proceso
            </span>
          </div>
        </div>
      </div>

      {/* Gráficos y reportes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Ingresos mensuales */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Ingresos Mensuales</h3>
            <Link 
              to="/reportes/financieros"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver detalle →
            </Link>
          </div>
          
          {dashboardData?.ingresos_por_mes ? (
            <div className="space-y-3">
              {dashboardData.ingresos_por_mes.slice(-6).map((month, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{month.mes}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ 
                          width: `${(month.ingresos / Math.max(...dashboardData.ingresos_por_mes.map(m => m.ingresos))) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-20 text-right">
                      {formatCurrency(month.ingresos)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              No hay datos disponibles
            </div>
          )}
        </div>

        {/* Citas por estado */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Citas por Estado</h3>
            <Link 
              to="/reportes/citas"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver detalle →
            </Link>
          </div>
          
          {dashboardData?.citas_por_estado ? (
            <div className="space-y-3">
              {Object.entries(dashboardData.citas_por_estado).map(([estado, cantidad]) => {
                const colors = {
                  'CONFIRMADA': 'bg-green-500',
                  'PENDIENTE': 'bg-yellow-500',
                  'COMPLETADA': 'bg-blue-500',
                  'CANCELADA': 'bg-red-500',
                  'NO_ASISTIO': 'bg-gray-500'
                };
                
                const total = Object.values(dashboardData.citas_por_estado).reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? (cantidad / total * 100) : 0;
                
                return (
                  <div key={estado} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">
                      {estado.toLowerCase().replace('_', ' ')}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${colors[estado] || 'bg-gray-400'}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-12 text-right">
                        {cantidad}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              No hay datos disponibles
            </div>
          )}
        </div>
      </div>

      {/* Accesos rápidos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Pacientes recientes */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Pacientes Recientes</h3>
            <Link 
              to="/usuarios/pacientes"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver todos →
            </Link>
          </div>
          
          {dashboardData?.pacientes_recientes ? (
            <div className="space-y-3">
              {dashboardData.pacientes_recientes.slice(0, 5).map((patient, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-sm font-medium">
                      {patient.nombre?.charAt(0) || 'P'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {patient.nombre}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(patient.fecha_registro).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-4">
              No hay pacientes recientes
            </div>
          )}
        </div>

        {/* Próximas citas */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Próximas Citas</h3>
            <Link 
              to="/agenda"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Ver agenda →
            </Link>
          </div>
          
          {dashboardData?.proximas_citas ? (
            <div className="space-y-3">
              {dashboardData.proximas_citas.slice(0, 5).map((appointment, index) => (
                <div key={index} className="border-l-4 border-blue-500 pl-3">
                  <p className="text-sm font-medium text-gray-900">
                    {appointment.paciente_nombre}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(appointment.fecha).toLocaleDateString()} - {appointment.hora}
                  </p>
                  <p className="text-xs text-blue-600">
                    {appointment.tratamiento || 'Consulta general'}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-4">
              No hay citas próximas
            </div>
          )}
        </div>

        {/* Acciones rápidas */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Acciones Rápidas</h3>
          
          <div className="space-y-3">
            <Link 
              to="/agenda/nueva-cita"
              className="block w-full bg-blue-600 text-white text-center py-2 px-4 rounded-lg hover:bg-blue-700 text-sm"
            >
              📅 Nueva Cita
            </Link>
            
            <Link 
              to="/usuarios/pacientes/crear"
              className="block w-full bg-green-600 text-white text-center py-2 px-4 rounded-lg hover:bg-green-700 text-sm"
            >
              👤 Registrar Paciente
            </Link>
            
            <Link 
              to="/facturacion/facturas/generar"
              className="block w-full bg-purple-600 text-white text-center py-2 px-4 rounded-lg hover:bg-purple-700 text-sm"
            >
              💰 Generar Factura
            </Link>
            
            <Link 
              to="/inventario"
              className="block w-full bg-orange-600 text-white text-center py-2 px-4 rounded-lg hover:bg-orange-700 text-sm"
            >
              📦 Revisar Inventario
            </Link>
            
            <Link 
              to="/reportes"
              className="block w-full bg-gray-600 text-white text-center py-2 px-4 rounded-lg hover:bg-gray-700 text-sm"
            >
              📊 Ver Reportes
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
```

## 📈 4. Estadísticas Generales y Reportes Avanzados

```javascript
// components/ReportsPage.jsx - Página de reportes avanzados
import React, { useState } from 'react';
import { useGeneralStats, useFinancialReport, useDoctorOccupancy } from '../hooks/useReports';

function ReportsPage() {
  const [periodo, setPeriodo] = useState('');
  const [mes, setMes] = useState('');
  
  const { stats, loading: statsLoading, error: statsError } = useGeneralStats();
  const { report, loading: reportLoading, refetch: refetchReport } = useFinancialReport(periodo);
  const { occupancy, loading: occupancyLoading } = useDoctorOccupancy(mes);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 2
    }).format(amount || 0);
  };

  const handleGenerateFinancialReport = () => {
    refetchReport();
  };

  if (statsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (statsError) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {statsError}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Reportes y Estadísticas</h1>

      {/* Estadísticas Generales */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Estadísticas Generales del Sistema</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="text-sm text-gray-600">Pacientes Activos</p>
            <p className="text-2xl font-bold">{stats?.total_pacientes_activos || 0}</p>
          </div>
          
          <div className="border-l-4 border-green-500 pl-4">
            <p className="text-sm text-gray-600">Odontólogos</p>
            <p className="text-2xl font-bold">{stats?.total_odontologos || 0}</p>
          </div>
          
          <div className="border-l-4 border-yellow-500 pl-4">
            <p className="text-sm text-gray-600">Citas Mes Actual</p>
            <p className="text-2xl font-bold">{stats?.citas_mes_actual || 0}</p>
          </div>
          
          <div className="border-l-4 border-purple-500 pl-4">
            <p className="text-sm text-gray-600">Tratamientos Completados</p>
            <p className="text-2xl font-bold">{stats?.tratamientos_completados || 0}</p>
          </div>
          
          <div className="border-l-4 border-red-500 pl-4">
            <p className="text-sm text-gray-600">Ingresos Mes Actual</p>
            <p className="text-2xl font-bold">{formatCurrency(stats?.ingresos_mes_actual || 0)}</p>
          </div>
          
          <div className="border-l-4 border-indigo-500 pl-4">
            <p className="text-sm text-gray-600">Promedio Factura</p>
            <p className="text-2xl font-bold">{formatCurrency(stats?.promedio_factura || 0)}</p>
          </div>
          
          <div className="border-l-4 border-pink-500 pl-4">
            <p className="text-sm text-gray-600">Tasa de Ocupación</p>
            <p className="text-2xl font-bold">{stats?.tasa_ocupacion || 0}%</p>
          </div>
        </div>
      </div>

      {/* Reporte Financiero */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Reporte Financiero</h2>
        
        <div className="mb-4 flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Período (YYYY-MM o YYYY)
            </label>
            <input
              type="text"
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value)}
              placeholder="2025-11 o 2025"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="pt-6">
            <button
              onClick={handleGenerateFinancialReport}
              disabled={reportLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {reportLoading ? 'Generando...' : 'Generar Reporte'}
            </button>
          </div>
        </div>
        
        {report && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600">Período</p>
              <p className="text-lg font-semibold">{report.periodo}</p>
            </div>
            
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-600">Total Facturado</p>
              <p className="text-lg font-semibold text-green-700">
                {formatCurrency(report.total_facturado)}
              </p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm text-gray-600">Total Pagado</p>
              <p className="text-lg font-semibold text-blue-700">
                {formatCurrency(report.total_pagado)}
              </p>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded">
              <p className="text-sm text-gray-600">Saldo Pendiente</p>
              <p className="text-lg font-semibold text-yellow-700">
                {formatCurrency(report.saldo_pendiente)}
              </p>
            </div>
            
            <div className="bg-purple-50 p-4 rounded col-span-full md:col-span-2 lg:col-span-1">
              <p className="text-sm text-gray-600">Número de Facturas</p>
              <p className="text-lg font-semibold text-purple-700">
                {report.numero_facturas}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Ocupación de Odontólogos */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Ocupación por Odontólogo</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mes (YYYY-MM)
          </label>
          <input
            type="text"
            value={mes}
            onChange={(e) => setMes(e.target.value)}
            placeholder="2025-11"
            className="w-64 px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        {occupancyLoading ? (
          <div className="text-center py-8">Cargando...</div>
        ) : occupancy.length > 0 ? (
          <div className="space-y-3">
            {occupancy.map((doc, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 flex-1">
                  {doc.etiqueta}
                </span>
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-blue-600 h-3 rounded-full"
                      style={{ width: `${doc.valor}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-bold text-gray-900 w-16 text-right">
                    {doc.valor}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-8">
            No hay datos disponibles
          </div>
        )}
      </div>
    </div>
  );
}

export default ReportsPage;
```

## ✅ Próximos Pasos

1. Implementar gráficos con Chart.js o D3.js para visualizaciones avanzadas
2. Continuar con **09_configuracion_avanzada.md**

---
**Endpoints implementados**: ✅ Dashboard KPIs ✅ Estadísticas generales ✅ Tendencia de citas ✅ Top procedimientos ✅ Reporte financiero ✅ Ocupación de odontólogos