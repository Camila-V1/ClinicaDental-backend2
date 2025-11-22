/**
 * 📊 Servicio de Reportes y Dashboard - CORREGIDO
 * 
 * Fecha: 22 de Noviembre 2025
 * Cambios aplicados:
 * - Tendencia Citas: Mapea 'cantidad' del backend a 'total' del frontend
 * - Top Procedimientos: Calcula porcentajes en el frontend (backend no los envía)
 * - Ocupación Odontólogos: Usa 'usuario_id' en lugar de 'odontologo_id'
 * - Estadísticas Generales: Mapeo correcto de nombres de campos
 */

import api from '../config/apiConfig';

// ==================== INTERFACES ====================

export interface DashboardKPIs {
  total_pacientes: number;
  citas_hoy: number;
  ingresos_mes: string;
  tratamientos_activos: number;
  pacientes_nuevos_mes: number;
  tasa_ocupacion: string;
  citas_pendientes: number;
  facturas_pendientes: number;
}

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

export interface TendenciaCitas {
  fecha: string;
  total: number;
  completadas: number;
  canceladas: number;
}

export interface TopProcedimiento {
  nombre: string;
  cantidad: number;
  porcentaje: string;
}

export interface ReporteFinanciero {
  periodo: string;
  total_facturado: string;
  total_pagado: string;
  saldo_pendiente: string;
  numero_facturas: number;
  facturas_emitidas?: number;
  facturas_pagadas?: number;
  facturas_pendientes?: number;
  ingresos_por_metodo?: {
    EFECTIVO: string;
    TARJETA: string;
    TRANSFERENCIA: string;
    CHEQUE: string;
  };
  detalle_por_mes?: Array<{
    mes: string;
    facturado: string;
    cobrado: string;
    pendiente: string;
  }>;
}

export interface OcupacionOdontologo {
  odontologo_id: number;
  odontologo_nombre: string;
  total_citas: number;
  citas_completadas: number;
  citas_canceladas: number;
  horas_ocupadas: number;
  tasa_ocupacion: string;
  pacientes_atendidos: number;
}

// ==================== SERVICIO ====================

class ReportesService {
  // Dashboard KPIs principales
  async getDashboardKpis(): Promise<DashboardKPIs> {
    try {
      const response = await api.get('/api/reportes/reportes/dashboard-kpis/');
      const data = response.data;

      // Inicializar objeto con valores por defecto
      let kpisFormatted: DashboardKPIs = {
        total_pacientes: 0,
        citas_hoy: 0,
        ingresos_mes: "0",
        tratamientos_activos: 0,
        pacientes_nuevos_mes: 0,
        tasa_ocupacion: "0",
        citas_pendientes: 0,
        facturas_pendientes: 0
      };

      // Si viene como array, convertir a objeto
      if (Array.isArray(data)) {
        data.forEach((item: any) => {
          const rawKey = item.key || item.label || '';
          const key = String(rawKey).toLowerCase().replace(/ /g, '_');
          const value = item.value;

          if (key.includes('pacientes') && key.includes('total')) {
            kpisFormatted.total_pacientes = Number(value);
          } else if (key.includes('citas') && key.includes('hoy')) {
            kpisFormatted.citas_hoy = Number(value);
          } else if (key.includes('ingresos')) {
            kpisFormatted.ingresos_mes = String(value);
          } else if (key.includes('tratamientos')) {
            kpisFormatted.tratamientos_activos = Number(value);
          } else if (key.includes('nuevos')) {
            kpisFormatted.pacientes_nuevos_mes = Number(value);
          } else if (key.includes('ocupacion') || key.includes('ocupación')) {
            kpisFormatted.tasa_ocupacion = String(value);
          } else if (key.includes('citas') && key.includes('pendientes')) {
            kpisFormatted.citas_pendientes = Number(value);
          } else if (key.includes('facturas')) {
            kpisFormatted.facturas_pendientes = Number(value);
          }
        });
      } else if (typeof data === 'object' && data !== null) {
        // Si viene como objeto directo, mezclar con defaults
        kpisFormatted = { ...kpisFormatted, ...data };
      }

      return kpisFormatted;
    } catch (error) {
      console.error('🔴 Error getDashboardKpis:', error);
      throw error;
    }
  }

  // Estadísticas generales del sistema
  async getEstadisticasGenerales(): Promise<EstadisticasGenerales> {
    const response = await api.get<EstadisticasGenerales>('/api/reportes/reportes/estadisticas-generales/');
    return response.data;
  }

  // ✅ CORREGIDO: Tendencia de citas
  async getTendenciaCitas(params?: { dias?: number }): Promise<TendenciaCitas[]> {
    try {
      const response = await api.get('/api/reportes/reportes/tendencia-citas/', { params });
      const data = response.data;
      
      if (!Array.isArray(data)) {
        console.warn('⚠️ Tendencia citas: respuesta no es array', data);
        return [];
      }

      // ✅ CORRECCIÓN: Backend envía 'cantidad', frontend espera 'total'
      return data.map((item: any) => ({
        fecha: item.fecha || '',
        total: Number(item.cantidad || item.total || 0),  // ← CAMBIO CRÍTICO
        completadas: Number(item.completadas || 0),
        canceladas: Number(item.canceladas || 0)
      }));
    } catch (error) {
      console.error('🔴 Error getTendenciaCitas:', error);
      return [];
    }
  }

  // ✅ CORREGIDO: Top procedimientos CON CÁLCULO DE PORCENTAJE
  async getTopProcedimientos(params?: { limite?: number }): Promise<TopProcedimiento[]> {
    try {
      const response = await api.get('/api/reportes/reportes/top-procedimientos/', { params });
      const data = response.data;

      if (!Array.isArray(data)) {
        console.warn('⚠️ Top procedimientos: respuesta no es array', data);
        return [];
      }

      // ✅ CALCULAR EL TOTAL para porcentajes (backend NO envía porcentaje)
      const totalCantidad = data.reduce((sum, item) => sum + (Number(item.cantidad) || 0), 0);

      console.log(`📊 Top Procedimientos - Total: ${totalCantidad}`, data);

      return data.map((item: any) => {
        const cantidad = Number(item.cantidad || 0);
        const porcentaje = totalCantidad > 0 
          ? ((cantidad / totalCantidad) * 100).toFixed(1)
          : "0";

        return {
          nombre: item.nombre || item.procedimiento || item.servicio_nombre || 'Procedimiento',
          cantidad: cantidad,
          porcentaje: porcentaje  // ← AHORA SÍ TIENE VALOR
        };
      });
    } catch (error) {
      console.error('🔴 Error getTopProcedimientos:', error);
      return [];
    }
  }

  // Reporte financiero por período
  async getReporteFinanciero(params?: { 
    periodo?: string; 
    fecha_inicio?: string; 
    fecha_fin?: string 
  }): Promise<ReporteFinanciero> {
    const response = await api.get<ReporteFinanciero>('/api/reportes/reportes/reporte-financiero/', { params });
    return response.data;
  }

  // ✅ CORREGIDO: Ocupación por odontólogo
  async getOcupacionOdontologos(params?: { mes?: string }): Promise<OcupacionOdontologo[]> {
    try {
      const response = await api.get('/api/reportes/reportes/ocupacion-odontologos/', { params });
      const data = response.data;

      if (!Array.isArray(data)) {
        console.warn('⚠️ Ocupación odontólogos: respuesta no es array', data);
        return [];
      }

      console.log('📋 Datos brutos ocupación:', data);

      return data.map((item: any) => {
        // ✅ CORRECCIÓN: Backend envía 'usuario_id' no 'odontologo_id'
        const resultado = {
          odontologo_id: Number(item.usuario_id || item.odontologo_id || 0),  // ← CAMBIO CRÍTICO
          odontologo_nombre: item.nombre_completo || item.odontologo_nombre || item.nombre || 'Odontólogo',
          total_citas: Number(item.total_citas || 0),
          citas_completadas: Number(item.citas_completadas || 0),
          citas_canceladas: Number(item.citas_canceladas || 0),
          horas_ocupadas: Number(item.horas_ocupadas || 0),
          tasa_ocupacion: String(item.tasa_ocupacion || "0"),
          pacientes_atendidos: Number(item.pacientes_atendidos || 0)
        };

        console.log('🔄 Ocupación mapeada:', resultado);
        return resultado;
      });
    } catch (error) {
      console.error('🔴 Error getOcupacionOdontologos:', error);
      return [];
    }
  }
}

export default new ReportesService();
