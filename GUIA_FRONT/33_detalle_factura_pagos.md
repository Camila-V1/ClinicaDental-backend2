# Guía 33: Detalle de Factura y Pagos (Paciente)

## 📋 Información General

**Caso de Uso**: CU31 - Gestión de Facturas y Pagos  
**Actor**: Paciente  
**Objetivo**: Ver detalle completo de una factura, historial de pagos y saldo pendiente

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver detalle completo de una factura específica
- ✅ Ver líneas de items facturados (procedimientos realizados)
- ✅ Ver historial de pagos aplicados a la factura
- ✅ Ver saldo pendiente actualizado
- ✅ Ver métodos de pago utilizados
- ✅ Filtrar facturas por estado (Pendiente/Pagada)
- ✅ Ver información de emisión y fechas

---

## 🔌 API Endpoints

### 1. Obtener Detalle de Factura
```
GET /api/facturacion/facturas/{id}/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Respuesta exitosa** (200 OK):
```json
{
  "id": 15,
  "estado": "PENDIENTE",
  "estado_display": "Pendiente",
  "fecha_emision": "2025-11-16T10:00:00Z",
  "fecha_anulacion": null,
  "paciente": 104,
  "paciente_nombre": "María García",
  "paciente_email": "paciente1@test.com",
  "paciente_ci": "7654321",
  "paciente_telefono": "555123456",
  "presupuesto": 22,
  "presupuesto_numero": 22,
  "presupuesto_token": "abc123xyz",
  "nit_ci": "7654321",
  "razon_social": "María García",
  "monto_total": "710.00",
  "monto_pagado": "260.00",
  "saldo_pendiente": "450.00",
  "total_pagos": 2,
  "porcentaje_pagado": 36.62,
  "pagos": [
    {
      "id": 8,
      "factura": 15,
      "factura_numero": 15,
      "factura_total": "710.00",
      "monto_pagado": "200.00",
      "metodo_pago": "EFECTIVO",
      "estado_pago": "COMPLETADO",
      "fecha_pago": "2025-11-16T14:30:00Z",
      "referencia_transaccion": null,
      "notas": "Pago inicial en efectivo"
    },
    {
      "id": 9,
      "factura": 15,
      "factura_numero": 15,
      "factura_total": "710.00",
      "monto_pagado": "60.00",
      "metodo_pago": "TRANSFERENCIA",
      "estado_pago": "COMPLETADO",
      "fecha_pago": "2025-11-17T09:15:00Z",
      "referencia_transaccion": "TRF-2025-001234",
      "notas": "Transferencia bancaria"
    }
  ]
}
```

---

### 2. Listar Mis Facturas
```
GET /api/facturacion/facturas/mis_facturas/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Query params opcionales**:
```
?estado=PENDIENTE    → Solo facturas pendientes
?estado=PAGADA       → Solo facturas pagadas
?estado=CANCELADA    → Solo facturas canceladas
```

**Respuesta exitosa** (200 OK):
```json
[
  {
    "id": 15,
    "numero": 15,
    "paciente_nombre": "María García",
    "estado": "PENDIENTE",
    "estado_display": "Pendiente",
    "monto_total": "710.00",
    "monto_pagado": "260.00",
    "saldo_pendiente": "450.00",
    "fecha_emision": "2025-11-16T10:00:00Z",
    "total_pagos": 2,
    "fecha": "2025-11-16T10:00:00Z",
    "monto": "710.00",
    "total": "710.00",
    "saldo": "450.00",
    "descripcion": "Factura por tratamiento - Presupuesto #22"
  },
  {
    "id": 14,
    "numero": 14,
    "paciente_nombre": "María García",
    "estado": "PAGADA",
    "estado_display": "Pagada",
    "monto_total": "320.00",
    "monto_pagado": "320.00",
    "saldo_pendiente": "0.00",
    "fecha_emision": "2025-11-10T15:30:00Z",
    "total_pagos": 1,
    "fecha": "2025-11-10T15:30:00Z",
    "monto": "320.00",
    "total": "320.00",
    "saldo": "0.00",
    "descripcion": "Factura por tratamiento - Presupuesto #21"
  }
]
```

---

### 3. Estado de Cuenta del Paciente
```
GET /api/facturacion/facturas/estado_cuenta/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Respuesta exitosa** (200 OK):
```json
{
  "saldo_pendiente": 450.0,
  "monto_total": 1030.0,
  "monto_pagado": 580.0,
  "saldo_pendiente_formatted": "$450.00",
  "monto_total_formatted": "$1,030.00",
  "monto_pagado_formatted": "$580.00",
  "total_facturado": 1030.0,
  "total_pagado": 580.0,
  "total_pendiente": 450.0,
  "total_facturas": 3,
  "facturas_pendientes": 1,
  "facturas_pagadas": 2,
  "facturas": [
    {
      "id": 15,
      "numero": 15,
      "estado": "PENDIENTE",
      "monto_total": "710.00",
      "saldo_pendiente": "450.00",
      "descripcion": "Factura por tratamiento - Presupuesto #22"
    }
  ]
}
```

---

### 4. Obtener Pagos de una Factura
```
GET /api/facturacion/pagos/por_factura/?factura_id={id}
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Respuesta exitosa** (200 OK):
```json
{
  "factura": {
    "id": 15,
    "numero": 15,
    "total": 710.0,
    "monto_pagado": 260.0,
    "saldo_pendiente": 450.0
  },
  "pagos": [
    {
      "id": 8,
      "factura": 15,
      "monto_pagado": "200.00",
      "metodo_pago": "EFECTIVO",
      "estado_pago": "COMPLETADO",
      "fecha_pago": "2025-11-16T14:30:00Z",
      "notas": "Pago inicial en efectivo"
    },
    {
      "id": 9,
      "factura": 15,
      "monto_pagado": "60.00",
      "metodo_pago": "TRANSFERENCIA",
      "estado_pago": "COMPLETADO",
      "fecha_pago": "2025-11-17T09:15:00Z",
      "notas": "Transferencia bancaria"
    }
  ],
  "total_pagos": 2,
  "suma_pagos": 260.0
}
```

---

## 🔧 Implementación Frontend

### 1. Service - `facturacionService.ts`

```typescript
// src/services/facturacionService.ts

import apiClient from '../config/apiConfig';

/**
 * Obtiene todas las facturas del paciente autenticado
 */
export const obtenerMisFacturas = async (estado?: string): Promise<any[]> => {
  console.log('📋 Obteniendo mis facturas...');
  
  const params: any = {};
  if (estado) {
    params.estado = estado.toUpperCase();
  }
  
  const response = await apiClient.get('/api/facturacion/facturas/mis_facturas/', { params });
  
  console.log('✅ Facturas obtenidas:', response.data.length);
  return response.data;
};

/**
 * Obtiene detalle de una factura específica
 */
export const obtenerDetalleFactura = async (facturaId: number): Promise<any> => {
  console.log('📄 Obteniendo detalle de factura:', facturaId);
  
  const response = await apiClient.get(`/api/facturacion/facturas/${facturaId}/`);
  
  console.log('✅ Detalle de factura obtenido');
  return response.data;
};

/**
 * Obtiene el estado de cuenta del paciente
 */
export const obtenerEstadoCuenta = async (): Promise<any> => {
  console.log('📊 Obteniendo estado de cuenta...');
  
  const response = await apiClient.get('/api/facturacion/facturas/estado_cuenta/');
  
  console.log('✅ Estado de cuenta obtenido');
  return response.data;
};

/**
 * Obtiene pagos de una factura específica
 */
export const obtenerPagosFactura = async (facturaId: number): Promise<any> => {
  console.log('💰 Obteniendo pagos de factura:', facturaId);
  
  const response = await apiClient.get('/api/facturacion/pagos/por_factura/', {
    params: { factura_id: facturaId }
  });
  
  console.log('✅ Pagos obtenidos:', response.data.total_pagos);
  return response.data;
};

/**
 * Formatea una fecha a formato legible
 */
export const formatearFecha = (fechaISO: string): string => {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

/**
 * Formatea un monto a formato de moneda
 */
export const formatearMonto = (monto: string | number): string => {
  const numero = typeof monto === 'string' ? parseFloat(monto) : monto;
  return `$${numero.toFixed(2)}`;
};

/**
 * Obtiene el color del badge según el estado de la factura
 */
export const getEstadoFacturaColor = (estado: string): string => {
  switch (estado.toUpperCase()) {
    case 'PENDIENTE':
      return 'bg-yellow-100 text-yellow-800';
    case 'PAGADA':
      return 'bg-green-100 text-green-800';
    case 'CANCELADA':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Obtiene el color del badge según el método de pago
 */
export const getMetodoPagoColor = (metodo: string): string => {
  switch (metodo.toUpperCase()) {
    case 'EFECTIVO':
      return 'bg-green-100 text-green-800';
    case 'TRANSFERENCIA':
      return 'bg-blue-100 text-blue-800';
    case 'TARJETA':
      return 'bg-purple-100 text-purple-800';
    case 'CHEQUE':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Obtiene el ícono según el método de pago
 */
export const getMetodoPagoIcono = (metodo: string): string => {
  switch (metodo.toUpperCase()) {
    case 'EFECTIVO':
      return '💵';
    case 'TRANSFERENCIA':
      return '🏦';
    case 'TARJETA':
      return '💳';
    case 'CHEQUE':
      return '📝';
    default:
      return '💰';
  }
};
```

---

### 2. Componente - `DetalleFactura.tsx`

```tsx
// src/pages/paciente/DetalleFactura.tsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  obtenerDetalleFactura,
  obtenerPagosFactura,
  formatearFecha,
  formatearMonto,
  getEstadoFacturaColor,
  getMetodoPagoColor,
  getMetodoPagoIcono
} from '../../services/facturacionService';

export default function DetalleFactura() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [factura, setFactura] = useState<any>(null);
  const [pagosInfo, setPagosInfo] = useState<any>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError(null);

      const facturaId = parseInt(id || '0');
      
      // Cargar factura y pagos en paralelo
      const [facturaData, pagosData] = await Promise.all([
        obtenerDetalleFactura(facturaId),
        obtenerPagosFactura(facturaId)
      ]);

      setFactura(facturaData);
      setPagosInfo(pagosData);
    } catch (err: any) {
      console.error('❌ Error cargando factura:', err);
      setError(err.response?.data?.detail || 'Error al cargar los datos de la factura');
    } finally {
      setCargando(false);
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando factura...</p>
        </div>
      </div>
    );
  }

  if (error || !factura) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error || 'Factura no encontrada'}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/paciente/facturas')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            ← Volver a Facturas
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/paciente/facturas')}
            className="text-blue-600 hover:text-blue-800 font-medium mb-2 flex items-center"
          >
            ← Volver a Facturas
          </button>
          <h1 className="text-3xl font-bold text-gray-800">
            Factura #{factura.id}
          </h1>
          <p className="text-gray-600 mt-1">
            Emitida el {formatearFecha(factura.fecha_emision)}
          </p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getEstadoFacturaColor(factura.estado)}`}>
          {factura.estado_display}
        </span>
      </div>

      {/* Información del Paciente */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          👤 Datos del Paciente
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Nombre Completo</p>
            <p className="font-medium text-gray-800">{factura.paciente_nombre}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">CI/NIT</p>
            <p className="font-medium text-gray-800">{factura.nit_ci || factura.paciente_ci}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Email</p>
            <p className="font-medium text-gray-800">{factura.paciente_email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Teléfono</p>
            <p className="font-medium text-gray-800">{factura.paciente_telefono}</p>
          </div>
        </div>
      </div>

      {/* Resumen Financiero */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          💰 Resumen Financiero
        </h2>
        
        <div className="space-y-3">
          {/* Total */}
          <div className="flex justify-between items-center pb-3 border-b border-gray-200">
            <span className="text-gray-700">Total de la Factura</span>
            <span className="text-xl font-bold text-gray-800">
              {formatearMonto(factura.monto_total)}
            </span>
          </div>

          {/* Pagado */}
          <div className="flex justify-between items-center">
            <span className="text-gray-700">Monto Pagado</span>
            <span className="text-lg font-semibold text-green-600">
              {formatearMonto(factura.monto_pagado)}
            </span>
          </div>

          {/* Saldo Pendiente */}
          <div className="flex justify-between items-center pt-3 border-t border-gray-200">
            <span className="text-gray-700 font-medium">Saldo Pendiente</span>
            <span className={`text-2xl font-bold ${
              parseFloat(factura.saldo_pendiente) > 0 ? 'text-red-600' : 'text-green-600'
            }`}>
              {formatearMonto(factura.saldo_pendiente)}
            </span>
          </div>
        </div>

        {/* Barra de Progreso */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progreso de Pago</span>
            <span>{factura.porcentaje_pagado.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-green-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${factura.porcentaje_pagado}%` }}
            />
          </div>
        </div>
      </div>

      {/* Historial de Pagos */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">
            📋 Historial de Pagos
          </h2>
          <span className="text-sm text-gray-600">
            {pagosInfo?.total_pagos || 0} {pagosInfo?.total_pagos === 1 ? 'pago' : 'pagos'}
          </span>
        </div>

        {pagosInfo && pagosInfo.pagos && pagosInfo.pagos.length > 0 ? (
          <div className="space-y-3">
            {pagosInfo.pagos.map((pago: any) => (
              <div
                key={pago.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <span className="text-3xl">
                    {getMetodoPagoIcono(pago.metodo_pago)}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-gray-800">
                        {formatearMonto(pago.monto_pagado)}
                      </p>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getMetodoPagoColor(pago.metodo_pago)}`}>
                        {pago.metodo_pago}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {formatearFecha(pago.fecha_pago)}
                    </p>
                    {pago.referencia_transaccion && (
                      <p className="text-xs text-gray-500 mt-1">
                        Ref: {pago.referencia_transaccion}
                      </p>
                    )}
                    {pago.notas && (
                      <p className="text-sm text-gray-600 mt-1 italic">
                        "{pago.notas}"
                      </p>
                    )}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  pago.estado_pago === 'COMPLETADO' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {pago.estado_pago}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <span className="text-4xl">📭</span>
            <p className="mt-2">No hay pagos registrados aún</p>
          </div>
        )}
      </div>

      {/* Información Adicional */}
      {factura.presupuesto && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <span className="text-xl mr-3">ℹ️</span>
            <div>
              <p className="text-sm text-blue-800 font-medium">
                Información del Presupuesto
              </p>
              <p className="text-sm text-blue-600 mt-1">
                Esta factura corresponde al Presupuesto #{factura.presupuesto_numero}
              </p>
              {factura.presupuesto_token && (
                <p className="text-xs text-blue-500 mt-1">
                  Token: {factura.presupuesto_token}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="mt-6 flex gap-3">
        <button
          onClick={() => navigate('/paciente/facturas')}
          className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
        >
          ← Volver a Facturas
        </button>
        
        {parseFloat(factura.saldo_pendiente) > 0 && (
          <button
            onClick={() => alert('Funcionalidad de pago en desarrollo')}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            💳 Realizar Pago
          </button>
        )}
        
        <button
          onClick={() => alert('Descarga de PDF en desarrollo')}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
        >
          📥 Descargar PDF
        </button>
      </div>

    </div>
  );
}
```

---

### 3. Componente - `ListaFacturas.tsx`

```tsx
// src/pages/paciente/ListaFacturas.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  obtenerMisFacturas,
  formatearFecha,
  formatearMonto,
  getEstadoFacturaColor
} from '../../services/facturacionService';

export default function ListaFacturas() {
  const navigate = useNavigate();

  const [facturas, setFacturas] = useState<any[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarFacturas();
  }, [filtroEstado]);

  const cargarFacturas = async () => {
    try {
      setCargando(true);
      setError(null);

      const data = await obtenerMisFacturas(filtroEstado);
      setFacturas(data);
    } catch (err: any) {
      console.error('❌ Error cargando facturas:', err);
      setError('Error al cargar las facturas');
    } finally {
      setCargando(false);
    }
  };

  const calcularTotales = () => {
    const total = facturas.reduce((sum, f) => sum + parseFloat(f.monto_total), 0);
    const pagado = facturas.reduce((sum, f) => sum + parseFloat(f.monto_pagado), 0);
    const pendiente = facturas.reduce((sum, f) => sum + parseFloat(f.saldo_pendiente), 0);
    
    return { total, pagado, pendiente };
  };

  const totales = calcularTotales();

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando facturas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Mis Facturas</h1>
        <p className="text-gray-600 mt-2">
          Historial completo de tus facturas y pagos
        </p>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Facturado</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">
                {formatearMonto(totales.total)}
              </p>
            </div>
            <span className="text-3xl">📊</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Pagado</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {formatearMonto(totales.pagado)}
              </p>
            </div>
            <span className="text-3xl">✅</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Saldo Pendiente</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {formatearMonto(totales.pendiente)}
              </p>
            </div>
            <span className="text-3xl">⏳</span>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filtrar por estado:</label>
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Todas</option>
            <option value="pendiente">Pendientes</option>
            <option value="pagada">Pagadas</option>
            <option value="cancelada">Canceladas</option>
          </select>
          <span className="text-sm text-gray-600">
            {facturas.length} {facturas.length === 1 ? 'factura' : 'facturas'}
          </span>
        </div>
      </div>

      {/* Lista de Facturas */}
      {facturas.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <span className="text-6xl">📭</span>
          <h3 className="text-xl font-semibold text-gray-800 mt-4">
            No hay facturas
          </h3>
          <p className="text-gray-600 mt-2">
            {filtroEstado 
              ? 'No hay facturas con el estado seleccionado'
              : 'Aún no tienes facturas registradas'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {facturas.map((factura) => (
            <div
              key={factura.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/paciente/facturas/${factura.id}`)}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-gray-800">
                        Factura #{factura.numero}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getEstadoFacturaColor(factura.estado)}`}>
                        {factura.estado_display}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {factura.descripcion}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Emitida el {formatearFecha(factura.fecha_emision)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-800">
                      {formatearMonto(factura.monto_total)}
                    </p>
                    {parseFloat(factura.saldo_pendiente) > 0 && (
                      <p className="text-sm text-red-600 mt-1">
                        Pendiente: {formatearMonto(factura.saldo_pendiente)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Barra de Progreso */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Pagado: {formatearMonto(factura.monto_pagado)}</span>
                    <span>
                      {((parseFloat(factura.monto_pagado) / parseFloat(factura.monto_total)) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${(parseFloat(factura.monto_pagado) / parseFloat(factura.monto_total)) * 100}%` 
                      }}
                    />
                  </div>
                </div>

                {/* Info de Pagos */}
                <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                  <span>
                    {factura.total_pagos} {factura.total_pagos === 1 ? 'pago realizado' : 'pagos realizados'}
                  </span>
                  <span className="text-blue-600 font-medium">
                    Ver Detalles →
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
```

---

## 🎨 Características de la UI

### 1. DetalleFactura
- **Header con breadcrumb**: Botón volver + número de factura + badge de estado
- **Card de paciente**: Información completa (nombre, CI, email, teléfono)
- **Resumen financiero**: Total, pagado, pendiente con barra de progreso
- **Historial de pagos**: Cards por cada pago con método, fecha, referencia
- **Acciones**: Volver, Realizar Pago (si hay saldo), Descargar PDF

### 2. ListaFacturas
- **Cards resumen**: Total facturado, pagado, pendiente
- **Filtros**: Dropdown por estado (todas, pendientes, pagadas, canceladas)
- **Lista de facturas**: Cards con hover effect, clic para ver detalle
- **Barra de progreso**: Visual del porcentaje pagado
- **Badges de estado**: Colores distintivos (amarillo, verde, rojo)

### 3. Elementos Visuales
- **Iconos**: Emojis para métodos de pago (💵 efectivo, 🏦 transferencia, 💳 tarjeta)
- **Colores de estado**: 
  - Pendiente: Amarillo
  - Pagada: Verde
  - Cancelada: Rojo
- **Barras de progreso**: Animadas con transición suave
- **Hover effects**: Sombra en cards al pasar el mouse

---

## 🔗 Integración con Rutas

```tsx
// src/routes/pacienteRoutes.tsx

import ListaFacturas from '../pages/paciente/ListaFacturas';
import DetalleFactura from '../pages/paciente/DetalleFactura';

export const pacienteRoutes = [
  // ... otras rutas
  {
    path: '/paciente/facturas',
    element: <ListaFacturas />
  },
  {
    path: '/paciente/facturas/:id',
    element: <DetalleFactura />
  }
];
```

---

## 📝 Notas Importantes

### 1. Estados de Factura

```
PENDIENTE  → Tiene saldo por pagar
PAGADA     → Completamente pagada (saldo = 0)
CANCELADA  → Anulada (solo admin)
```

### 2. Métodos de Pago

```
EFECTIVO       → Pago en efectivo
TRANSFERENCIA  → Transferencia bancaria
TARJETA        → Tarjeta de crédito/débito
CHEQUE         → Pago con cheque
```

### 3. Permisos

- ✅ Paciente solo ve sus propias facturas
- ✅ No puede modificar facturas
- ✅ No puede eliminar pagos
- ✅ Puede ver detalle completo y historial

---

## 🧪 Testing

### Casos de Prueba

1. ✅ **Lista vacía**: Sin facturas registradas
2. ✅ **Factura pendiente**: Saldo > 0, color amarillo
3. ✅ **Factura pagada**: Saldo = 0, color verde
4. ✅ **Múltiples pagos**: Ver historial completo
5. ✅ **Barra de progreso**: Calcular porcentaje correcto
6. ✅ **Filtros**: Cambiar estado y actualizar lista
7. ✅ **Navegación**: Clic en card → detalle
8. ✅ **Métodos de pago**: Iconos y colores correctos
9. ✅ **Error de conexión**: Mensaje de error
10. ✅ **Factura no encontrada**: 404 con botón volver

---

## 🎯 Mejoras Futuras

1. **Descargar PDF**: Generar comprobante descargable
2. **Registrar Pago**: Modal para que paciente registre pago realizado
3. **Notificaciones**: Email al registrar pago
4. **Recordatorios**: Alertar facturas vencidas
5. **Gráficos**: Visualización de historial de pagos
6. **Exportar Excel**: Descargar reporte de facturas

---

**Siguiente**: Guía 34 - Dashboard con Gráficos y Estadísticas
