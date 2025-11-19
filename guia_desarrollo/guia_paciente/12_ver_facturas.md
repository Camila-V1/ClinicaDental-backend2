# 12 - Ver Mis Facturas y Pagos

## 🎯 Objetivo
Implementar la visualización de facturas del paciente, mostrando estado de pago, monto pendiente, historial de abonos y desglose detallado de cada factura.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Dashboard funcional (Guía 02)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/facturacion/facturas/`
Lista facturas del paciente (automáticamente filtradas)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado` (opcional): pendiente, pagada, vencida, cancelada

**Response 200:**
```json
[
  {
    "id": 1,
    "numero_factura": "FAC-2025-001",
    "fecha_emision": "2025-11-01T10:00:00-05:00",
    "fecha_vencimiento": "2025-11-30T23:59:59-05:00",
    "paciente": {
      "id": 3,
      "usuario": {
        "nombre": "María",
        "apellido": "García"
      }
    },
    "presupuesto": {
      "id": 1,
      "plan_tratamiento": {
        "id": 1,
        "titulo": "Plan de Restauración Dental Integral"
      }
    },
    "monto_total": "450.00",
    "monto_pagado": "200.00",
    "saldo_pendiente": "250.00",
    "estado": "pendiente",
    "dias_para_vencimiento": 15,
    "cantidad_pagos": 2
  }
]
```

### **GET** `/tenant/api/facturacion/facturas/{id}/`
Detalle completo de una factura con pagos

**Response 200:**
```json
{
  "id": 1,
  "numero_factura": "FAC-2025-001",
  "fecha_emision": "2025-11-01T10:00:00-05:00",
  "fecha_vencimiento": "2025-11-30T23:59:59-05:00",
  "paciente": {
    "id": 3,
    "usuario": {
      "nombre": "María",
      "apellido": "García",
      "email": "maria@test.com"
    }
  },
  "presupuesto": {
    "id": 1,
    "plan_tratamiento": {
      "id": 1,
      "titulo": "Plan de Restauración Dental Integral",
      "precio_total_plan": "450.00"
    },
    "items": [
      {
        "item_plan": {
          "servicio": {
            "nombre": "Restauración con Resina Premium"
          }
        },
        "cantidad": 3,
        "precio_unitario": "150.00",
        "subtotal": "450.00"
      }
    ]
  },
  "monto_total": "450.00",
  "monto_pagado": "200.00",
  "saldo_pendiente": "250.00",
  "estado": "pendiente",
  "pagos": [
    {
      "id": 1,
      "fecha_pago": "2025-11-03T14:00:00-05:00",
      "monto": "100.00",
      "metodo_pago": "efectivo",
      "referencia": "PAGO-001",
      "observaciones": "Pago inicial"
    },
    {
      "id": 2,
      "fecha_pago": "2025-11-10T11:00:00-05:00",
      "monto": "100.00",
      "metodo_pago": "transferencia",
      "referencia": "TRANS-12345",
      "observaciones": "Segundo abono"
    }
  ],
  "observaciones": "Pago en 5 cuotas acordado",
  "creado": "2025-11-01T10:00:00-05:00"
}
```

### **GET** `/tenant/api/facturacion/pagos/`
Lista todos los pagos del paciente

**Response 200:**
```json
[
  {
    "id": 1,
    "factura": {
      "id": 1,
      "numero_factura": "FAC-2025-001"
    },
    "fecha_pago": "2025-11-03T14:00:00-05:00",
    "monto": "100.00",
    "metodo_pago": "efectivo",
    "referencia": "PAGO-001",
    "observaciones": "Pago inicial"
  }
]
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Facturas.tsx                  ← Nuevo
│       └── DetalleFactura.tsx            ← Nuevo
├── components/
│   └── paciente/
│       ├── FacturaCard.tsx               ← Nuevo
│       ├── PagoCard.tsx                  ← Nuevo
│       ├── AlertaVencimiento.tsx         ← Nuevo
│       └── ResumenPagos.tsx              ← Nuevo
├── services/
│   ├── facturasService.ts                ← Nuevo
│   └── pagosService.ts                   ← Nuevo
└── types/
    └── facturacion.types.ts              ← Nuevo
```

---

## 💻 Código Paso a Paso

### **Paso 1: Crear tipos de Facturación**

**Archivo:** `src/types/facturacion.types.ts` (nuevo)

```typescript
export type EstadoFactura = 'pendiente' | 'pagada' | 'vencida' | 'cancelada';
export type MetodoPago = 'efectivo' | 'tarjeta' | 'transferencia' | 'cheque' | 'otro';

export interface Factura {
  id: number;
  numero_factura: string;
  fecha_emision: string;
  fecha_vencimiento: string;
  paciente: {
    id: number;
    usuario: {
      nombre: string;
      apellido: string;
      email?: string;
    };
  };
  presupuesto: {
    id: number;
    plan_tratamiento: {
      id: number;
      titulo: string;
      precio_total_plan?: string;
    };
  };
  monto_total: string;
  monto_pagado: string;
  saldo_pendiente: string;
  estado: EstadoFactura;
  dias_para_vencimiento?: number;
  cantidad_pagos?: number;
  observaciones?: string;
  creado?: string;
}

export interface ItemPresupuesto {
  item_plan: {
    servicio: {
      nombre: string;
    };
  };
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
}

export interface FacturaDetalle extends Factura {
  presupuesto: {
    id: number;
    plan_tratamiento: {
      id: number;
      titulo: string;
      precio_total_plan: string;
    };
    items: ItemPresupuesto[];
  };
  pagos: Pago[];
}

export interface Pago {
  id: number;
  factura?: {
    id: number;
    numero_factura: string;
  };
  fecha_pago: string;
  monto: string;
  metodo_pago: MetodoPago;
  referencia?: string;
  observaciones?: string;
}
```

---

### **Paso 2: Crear servicio de Facturas**

**Archivo:** `src/services/facturasService.ts` (nuevo)

```typescript
import apiClient from '../config/apiClient';
import type { Factura, FacturaDetalle } from '../types/facturacion.types';

const facturasService = {
  /**
   * Obtener todas las facturas del paciente
   */
  async getMisFacturas(): Promise<Factura[]> {
    console.group('💰 [facturasService] getMisFacturas');
    
    try {
      const response = await apiClient.get<Factura[]>(
        '/tenant/api/facturacion/facturas/'
      );
      
      console.log('✅ Facturas obtenidas:', response.data.length);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo facturas:', error);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Obtener detalle de una factura específica
   */
  async getFacturaDetalle(facturaId: number): Promise<FacturaDetalle> {
    console.group('🔍 [facturasService] getFacturaDetalle');
    console.log('ID:', facturaId);
    
    try {
      const response = await apiClient.get<FacturaDetalle>(
        `/tenant/api/facturacion/facturas/${facturaId}/`
      );
      
      console.log('✅ Factura obtenida');
      console.log('Pagos:', response.data.pagos.length);
      console.log('Saldo:', response.data.saldo_pendiente);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo detalle:', error);
      console.groupEnd();
      throw error;
    }
  }
};

export default facturasService;
```

---

### **Paso 3: Crear servicio de Pagos**

**Archivo:** `src/services/pagosService.ts` (nuevo)

```typescript
import apiClient from '../config/apiClient';
import type { Pago } from '../types/facturacion.types';

const pagosService = {
  /**
   * Obtener todos los pagos del paciente
   */
  async getMisPagos(): Promise<Pago[]> {
    console.group('💳 [pagosService] getMisPagos');
    
    try {
      const response = await apiClient.get<Pago[]>(
        '/tenant/api/facturacion/pagos/'
      );
      
      console.log('✅ Pagos obtenidos:', response.data.length);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo pagos:', error);
      console.groupEnd();
      throw error;
    }
  }
};

export default pagosService;
```

---

### **Paso 4: Componente AlertaVencimiento**

**Archivo:** `src/components/paciente/AlertaVencimiento.tsx` (nuevo)

```typescript
interface AlertaVencimientoProps {
  diasParaVencimiento?: number;
  fechaVencimiento: string;
}

const AlertaVencimiento = ({ diasParaVencimiento, fechaVencimiento }: AlertaVencimientoProps) => {
  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  if (diasParaVencimiento === undefined || diasParaVencimiento < 0) {
    return (
      <div style={{
        padding: '12px',
        backgroundColor: '#fee2e2',
        border: '1px solid #fecaca',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span style={{ fontSize: '20px' }}>⚠️</span>
        <div>
          <p style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#991b1b',
            margin: 0
          }}>
            Factura Vencida
          </p>
          <p style={{
            fontSize: '12px',
            color: '#7f1d1d',
            margin: 0
          }}>
            Venció el {formatearFecha(fechaVencimiento)}
          </p>
        </div>
      </div>
    );
  }

  if (diasParaVencimiento <= 7) {
    return (
      <div style={{
        padding: '12px',
        backgroundColor: '#fef3c7',
        border: '1px solid #fde68a',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span style={{ fontSize: '20px' }}>⏰</span>
        <div>
          <p style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#92400e',
            margin: 0
          }}>
            Próxima a vencer
          </p>
          <p style={{
            fontSize: '12px',
            color: '#78350f',
            margin: 0
          }}>
            Vence en {diasParaVencimiento} {diasParaVencimiento === 1 ? 'día' : 'días'} 
            ({formatearFecha(fechaVencimiento)})
          </p>
        </div>
      </div>
    );
  }

  return null;
};

export default AlertaVencimiento;
```

---

### **Paso 5: Componente FacturaCard**

**Archivo:** `src/components/paciente/FacturaCard.tsx` (nuevo)

```typescript
import { useNavigate } from 'react-router-dom';
import AlertaVencimiento from './AlertaVencimiento';
import type { Factura, EstadoFactura } from '../../types/facturacion.types';

interface FacturaCardProps {
  factura: Factura;
}

const FacturaCard = ({ factura }: FacturaCardProps) => {
  const navigate = useNavigate();

  const getEstadoConfig = (estado: EstadoFactura) => {
    const configs: Record<EstadoFactura, { color: string; bg: string; icon: string; texto: string }> = {
      'pendiente': { color: '#f59e0b', bg: '#fef3c7', icon: '⏳', texto: 'Pendiente' },
      'pagada': { color: '#10b981', bg: '#d1fae5', icon: '✓', texto: 'Pagada' },
      'vencida': { color: '#ef4444', bg: '#fee2e2', icon: '⚠️', texto: 'Vencida' },
      'cancelada': { color: '#6b7280', bg: '#f3f4f6', icon: '✗', texto: 'Cancelada' }
    };
    return configs[estado];
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const calcularPorcentajePagado = (): number => {
    const total = parseFloat(factura.monto_total);
    const pagado = parseFloat(factura.monto_pagado);
    return (pagado / total) * 100;
  };

  const estadoConfig = getEstadoConfig(factura.estado);
  const porcentajePagado = calcularPorcentajePagado();

  return (
    <div
      onClick={() => navigate(`/paciente/facturas/${factura.id}`)}
      style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        border: '1px solid #e5e7eb',
        cursor: 'pointer',
        transition: 'all 0.2s'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px'
      }}>
        <div>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#111827',
            margin: '0 0 4px 0'
          }}>
            {factura.numero_factura}
          </h3>
          <p style={{
            fontSize: '13px',
            color: '#6b7280',
            margin: 0
          }}>
            {factura.presupuesto.plan_tratamiento.titulo}
          </p>
        </div>

        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: '4px 10px',
          backgroundColor: estadoConfig.bg,
          color: estadoConfig.color,
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          {estadoConfig.icon} {estadoConfig.texto}
        </span>
      </div>

      {/* Alerta de Vencimiento */}
      {(factura.estado === 'pendiente' || factura.estado === 'vencida') && (
        <div style={{ marginBottom: '12px' }}>
          <AlertaVencimiento 
            diasParaVencimiento={factura.dias_para_vencimiento}
            fechaVencimiento={factura.fecha_vencimiento}
          />
        </div>
      )}

      {/* Montos */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px',
        marginBottom: '12px'
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px'
        }}>
          <p style={{
            fontSize: '11px',
            color: '#6b7280',
            fontWeight: '600',
            margin: '0 0 4px 0'
          }}>
            TOTAL
          </p>
          <p style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            ${parseFloat(factura.monto_total).toFixed(2)}
          </p>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#d1fae5',
          borderRadius: '6px'
        }}>
          <p style={{
            fontSize: '11px',
            color: '#065f46',
            fontWeight: '600',
            margin: '0 0 4px 0'
          }}>
            PAGADO
          </p>
          <p style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#10b981',
            margin: 0
          }}>
            ${parseFloat(factura.monto_pagado).toFixed(2)}
          </p>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#fef3c7',
          borderRadius: '6px'
        }}>
          <p style={{
            fontSize: '11px',
            color: '#92400e',
            fontWeight: '600',
            margin: '0 0 4px 0'
          }}>
            PENDIENTE
          </p>
          <p style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#f59e0b',
            margin: 0
          }}>
            ${parseFloat(factura.saldo_pendiente).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Barra de Progreso */}
      <div style={{ marginBottom: '12px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '6px'
        }}>
          <p style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#6b7280',
            margin: 0
          }}>
            PROGRESO DE PAGO
          </p>
          <p style={{
            fontSize: '11px',
            color: '#6b7280',
            margin: 0
          }}>
            {porcentajePagado.toFixed(1)}%
          </p>
        </div>
        <div style={{
          width: '100%',
          height: '6px',
          backgroundColor: '#e5e7eb',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${porcentajePagado}%`,
            height: '100%',
            backgroundColor: '#10b981',
            transition: 'width 0.3s ease'
          }} />
        </div>
      </div>

      {/* Footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: '12px',
        borderTop: '1px solid #e5e7eb',
        fontSize: '12px',
        color: '#6b7280'
      }}>
        <div>
          <span>📅 Emitida: {formatearFecha(factura.fecha_emision)}</span>
        </div>
        {factura.cantidad_pagos !== undefined && factura.cantidad_pagos > 0 && (
          <div>
            <span>💳 {factura.cantidad_pagos} {factura.cantidad_pagos === 1 ? 'pago' : 'pagos'}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FacturaCard;
```

---

### **Paso 6: Página Facturas**

**Archivo:** `src/pages/paciente/Facturas.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import facturasService from '../../services/facturasService';
import FacturaCard from '../../components/paciente/FacturaCard';
import type { Factura, EstadoFactura } from '../../types/facturacion.types';

const Facturas = () => {
  const navigate = useNavigate();

  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<EstadoFactura | 'TODAS'>('TODAS');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarFacturas();
  }, []);

  const cargarFacturas = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await facturasService.getMisFacturas();
      setFacturas(data);

    } catch (err: any) {
      console.error('Error cargando facturas:', err);
      setError('No se pudieron cargar las facturas');

    } finally {
      setLoading(false);
    }
  };

  const facturasFiltradas = filtroEstado === 'TODAS'
    ? facturas
    : facturas.filter(factura => factura.estado === filtroEstado);

  const facturasOrdenadas = [...facturasFiltradas].sort((a, b) => {
    return new Date(b.fecha_emision).getTime() - new Date(a.fecha_emision).getTime();
  });

  // Calcular totales
  const totalFacturado = facturas.reduce((sum, f) => sum + parseFloat(f.monto_total), 0);
  const totalPagado = facturas.reduce((sum, f) => sum + parseFloat(f.monto_pagado), 0);
  const totalPendiente = facturas.reduce((sum, f) => sum + parseFloat(f.saldo_pendiente), 0);

  const estadosFiltro: Array<{ valor: EstadoFactura | 'TODAS'; texto: string; icon: string }> = [
    { valor: 'TODAS', texto: 'Todas', icon: '📋' },
    { valor: 'pendiente', texto: 'Pendientes', icon: '⏳' },
    { valor: 'pagada', texto: 'Pagadas', icon: '✓' },
    { valor: 'vencida', texto: 'Vencidas', icon: '⚠️' }
  ];

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          textAlign: 'center'
        }}>
          <p style={{ fontSize: '16px', color: '#6b7280' }}>
            ⏳ Cargando facturas...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f3f4f6'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 24px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            💰 Mis Facturas y Pagos
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '4px 0 0 0'
          }}>
            {facturas.length} {facturas.length === 1 ? 'factura' : 'facturas'} en total
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Error */}
        {error && (
          <div style={{
            padding: '16px',
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <p style={{ fontSize: '14px', color: '#991b1b', margin: 0 }}>
              ⚠️ {error}
            </p>
          </div>
        )}

        {/* Resumen Financiero */}
        {facturas.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb'
            }}>
              <p style={{
                fontSize: '12px',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0'
              }}>
                TOTAL FACTURADO
              </p>
              <p style={{
                fontSize: '28px',
                fontWeight: '700',
                color: '#111827',
                margin: 0
              }}>
                ${totalFacturado.toFixed(2)}
              </p>
            </div>

            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb'
            }}>
              <p style={{
                fontSize: '12px',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0'
              }}>
                TOTAL PAGADO
              </p>
              <p style={{
                fontSize: '28px',
                fontWeight: '700',
                color: '#10b981',
                margin: 0
              }}>
                ${totalPagado.toFixed(2)}
              </p>
            </div>

            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb'
            }}>
              <p style={{
                fontSize: '12px',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0'
              }}>
                SALDO PENDIENTE
              </p>
              <p style={{
                fontSize: '28px',
                fontWeight: '700',
                color: '#f59e0b',
                margin: 0
              }}>
                ${totalPendiente.toFixed(2)}
              </p>
            </div>
          </div>
        )}

        {/* Filtros */}
        <div style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginBottom: '20px'
        }}>
          {estadosFiltro.map((estado) => {
            const activo = filtroEstado === estado.valor;
            
            return (
              <button
                key={estado.valor}
                onClick={() => setFiltroEstado(estado.valor)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: activo ? '#10b981' : 'white',
                  color: activo ? 'white' : '#374151',
                  border: `1px solid ${activo ? '#10b981' : '#d1d5db'}`,
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
                onMouseEnter={(e) => {
                  if (!activo) e.currentTarget.style.backgroundColor = '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  if (!activo) e.currentTarget.style.backgroundColor = 'white';
                }}
              >
                <span>{estado.icon}</span>
                <span>{estado.texto}</span>
              </button>
            );
          })}
        </div>

        {/* Lista de Facturas */}
        {facturasOrdenadas.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '48px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <p style={{ fontSize: '48px', margin: '0 0 16px 0' }}>💰</p>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 8px 0'
            }}>
              No hay facturas
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {filtroEstado === 'TODAS'
                ? 'Aún no tienes facturas registradas'
                : `No tienes facturas con estado ${filtroEstado}`}
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gap: '16px'
          }}>
            {facturasOrdenadas.map((factura) => (
              <FacturaCard key={factura.id} factura={factura} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Facturas;
```

---

### **Paso 7: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import FacturasPaciente from './pages/paciente/Facturas'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ... rutas anteriores ... */}
        <Route path="/paciente/planes/:id" element={<DetallePlanPaciente />} />
        <Route path="/paciente/facturas" element={<FacturasPaciente />} /> {/* ← NUEVO */}
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Lista de Facturas**
1. Login con `paciente1@test.com`
2. Navegar a "Facturas y Pagos"
3. **Esperado**:
   - Resumen financiero con 3 totales
   - Lista de facturas ordenadas por fecha
   - Estado de cada factura con color

### **Caso 2: Filtrar por Estado**
1. Click en "⏳ Pendientes"
2. **Esperado**: Solo facturas pendientes
3. Click en "✓ Pagadas"
4. **Esperado**: Solo facturas completamente pagadas

### **Caso 3: Ver Alertas de Vencimiento**
1. Ver factura próxima a vencer (< 7 días)
2. **Esperado**: Alerta amarilla con días restantes
3. Ver factura vencida
4. **Esperado**: Alerta roja indicando vencimiento

### **Caso 4: Ver Progreso de Pago**
1. Ver factura parcialmente pagada
2. **Esperado**:
   - Barra de progreso con porcentaje
   - Montos: Total, Pagado, Pendiente
   - Porcentaje calculado correctamente

### **Caso 5: Sin Facturas**
1. Paciente nuevo sin facturas
2. **Esperado**: Mensaje "Aún no tienes facturas registradas"

### **Caso 6: Ver Detalle de Factura**
1. Click en una factura
2. **Esperado**: Navegación a `/paciente/facturas/{id}` (próxima guía)

---

## ✅ Checklist de Verificación

- [ ] Lista de facturas carga correctamente
- [ ] Resumen financiero calcula correctamente
- [ ] Filtros por estado funcionan
- [ ] Alertas de vencimiento se muestran
- [ ] Barra de progreso funciona
- [ ] Estados con colores correctos
- [ ] Montos formateados correctamente
- [ ] Fechas formateadas correctamente
- [ ] Click en factura navega a detalle
- [ ] Estado vacío funciona
- [ ] Ordenamiento por fecha
- [ ] Hover effects funcionan
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: Cálculos incorrectos**
**Síntoma**: Totales no coinciden
**Causa**: parseFloat no maneja strings vacíos
**Solución**: Validar que los montos sean válidos antes de sumar

### **Error 2: Alertas no aparecen**
**Síntoma**: No se muestran alertas de vencimiento
**Causa**: `dias_para_vencimiento` es null
**Solución**: Validar que el campo existe antes de renderizar

### **Error 3: Progreso mayor a 100%**
**Síntoma**: Barra de progreso desbordada
**Causa**: Monto pagado > monto total
**Solución**: Limitar porcentaje a máximo 100%

---

## 🔄 Siguiente Paso

✅ Ver lista de facturas → Continuar con **`13_ver_detalle_factura.md`** (Detalle con pagos e items)
