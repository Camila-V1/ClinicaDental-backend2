# 13 - Ver Detalle Completo de Factura

## 🎯 Objetivo
Implementar la vista de detalle de una factura con información completa: items del presupuesto, historial de pagos, información del plan de tratamiento, y opciones de descarga.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver lista de facturas (Guía 12)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/facturacion/facturas/{id}/`
Obtiene detalle completo de una factura con pagos e items

**Headers:**
```
Authorization: Bearer {access_token}
```

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
      "precio_total_plan": "450.00",
      "odontologo": {
        "usuario": {
          "nombre": "Dr. Carlos",
          "apellido": "López"
        }
      }
    },
    "items": [
      {
        "id": 1,
        "item_plan": {
          "servicio": {
            "nombre": "Restauración con Resina Premium",
            "codigo": "REST-001"
          },
          "pieza_dental": "16"
        },
        "cantidad": 1,
        "precio_unitario": "150.00",
        "subtotal": "150.00"
      },
      {
        "id": 2,
        "item_plan": {
          "servicio": {
            "nombre": "Restauración con Resina Premium",
            "codigo": "REST-001"
          },
          "pieza_dental": "26"
        },
        "cantidad": 1,
        "precio_unitario": "150.00",
        "subtotal": "150.00"
      },
      {
        "id": 3,
        "item_plan": {
          "servicio": {
            "nombre": "Restauración con Resina Premium",
            "codigo": "REST-001"
          },
          "pieza_dental": "36"
        },
        "cantidad": 1,
        "precio_unitario": "150.00",
        "subtotal": "150.00"
      }
    ],
    "total_presupuestado": "450.00"
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
      "observaciones": "Pago inicial en efectivo"
    },
    {
      "id": 2,
      "fecha_pago": "2025-11-10T11:00:00-05:00",
      "monto": "100.00",
      "metodo_pago": "transferencia",
      "referencia": "TRANS-12345",
      "observaciones": "Segundo abono por transferencia bancaria"
    }
  ],
  "observaciones": "Plan de pago en 5 cuotas mensuales acordado con el paciente",
  "creado": "2025-11-01T10:00:00-05:00"
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── DetalleFactura.tsx            ← Nuevo
├── components/
│   └── paciente/
│       ├── PagoCard.tsx                  ← Nuevo
│       ├── ItemPresupuestoCard.tsx       ← Nuevo
│       └── InfoPlanFactura.tsx           ← Nuevo
└── services/
    └── facturasService.ts                ← Ya existe (extender)
```

---

## 💻 Código Paso a Paso

### **Paso 1: Componente PagoCard**

**Archivo:** `src/components/paciente/PagoCard.tsx` (nuevo)

```typescript
import type { Pago, MetodoPago } from '../../types/facturacion.types';

interface PagoCardProps {
  pago: Pago;
  index: number;
}

const PagoCard = ({ pago, index }: PagoCardProps) => {
  const getMetodoPagoConfig = (metodo: MetodoPago) => {
    const configs: Record<MetodoPago, { icon: string; texto: string; color: string }> = {
      'efectivo': { icon: '💵', texto: 'Efectivo', color: '#10b981' },
      'tarjeta': { icon: '💳', texto: 'Tarjeta', color: '#3b82f6' },
      'transferencia': { icon: '🏦', texto: 'Transferencia', color: '#8b5cf6' },
      'cheque': { icon: '📝', texto: 'Cheque', color: '#f59e0b' },
      'otro': { icon: '💰', texto: 'Otro', color: '#6b7280' }
    };
    return configs[metodo];
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const metodoConfig = getMetodoPagoConfig(pago.metodo_pago);

  return (
    <div style={{
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '12px'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px'
      }}>
        <div style={{ flex: 1 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '4px'
          }}>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '24px',
              height: '24px',
              backgroundColor: '#10b981',
              borderRadius: '50%',
              fontSize: '12px',
              fontWeight: '700',
              color: 'white'
            }}>
              {index + 1}
            </span>
            <h4 style={{
              fontSize: '15px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Pago #{pago.id}
            </h4>
          </div>

          <p style={{
            fontSize: '13px',
            color: '#6b7280',
            margin: '0 0 0 32px'
          }}>
            {formatearFecha(pago.fecha_pago)}
          </p>
        </div>

        <p style={{
          fontSize: '20px',
          fontWeight: '700',
          color: '#10b981',
          margin: 0
        }}>
          ${parseFloat(pago.monto).toFixed(2)}
        </p>
      </div>

      {/* Método de Pago */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '10px',
        backgroundColor: '#f9fafb',
        borderRadius: '6px',
        marginBottom: pago.referencia || pago.observaciones ? '12px' : '0'
      }}>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          backgroundColor: `${metodoConfig.color}20`,
          color: metodoConfig.color,
          borderRadius: '12px',
          fontSize: '13px',
          fontWeight: '600'
        }}>
          {metodoConfig.icon} {metodoConfig.texto}
        </span>

        {pago.referencia && (
          <span style={{
            fontSize: '12px',
            color: '#6b7280'
          }}>
            Ref: <strong>{pago.referencia}</strong>
          </span>
        )}
      </div>

      {/* Observaciones */}
      {pago.observaciones && (
        <div style={{
          padding: '10px',
          backgroundColor: '#f0fdf4',
          borderRadius: '6px',
          border: '1px solid #bbf7d0'
        }}>
          <p style={{
            fontSize: '12px',
            color: '#15803d',
            margin: 0,
            lineHeight: '1.5'
          }}>
            💬 {pago.observaciones}
          </p>
        </div>
      )}
    </div>
  );
};

export default PagoCard;
```

---

### **Paso 2: Componente ItemPresupuestoCard**

**Archivo:** `src/components/paciente/ItemPresupuestoCard.tsx` (nuevo)

```typescript
import type { ItemPresupuesto } from '../../types/facturacion.types';

interface ItemPresupuestoCardProps {
  item: ItemPresupuesto;
  index: number;
}

const ItemPresupuestoCard = ({ item, index }: ItemPresupuestoCardProps) => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '12px',
      backgroundColor: index % 2 === 0 ? '#f9fafb' : 'white',
      borderRadius: '6px'
    }}>
      <div style={{ flex: 1 }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '4px'
        }}>
          <span style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#111827'
          }}>
            {item.item_plan.servicio.nombre}
          </span>
          
          {item.item_plan.pieza_dental && (
            <span style={{
              fontSize: '11px',
              padding: '2px 8px',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              borderRadius: '10px',
              fontWeight: '600'
            }}>
              🦷 {item.item_plan.pieza_dental}
            </span>
          )}
        </div>

        <p style={{
          fontSize: '12px',
          color: '#6b7280',
          margin: 0
        }}>
          {item.item_plan.servicio.codigo} • {item.cantidad} {item.cantidad === 1 ? 'unidad' : 'unidades'} × ${parseFloat(item.precio_unitario).toFixed(2)}
        </p>
      </div>

      <p style={{
        fontSize: '16px',
        fontWeight: '700',
        color: '#111827',
        margin: 0
      }}>
        ${parseFloat(item.subtotal).toFixed(2)}
      </p>
    </div>
  );
};

export default ItemPresupuestoCard;
```

---

### **Paso 3: Componente InfoPlanFactura**

**Archivo:** `src/components/paciente/InfoPlanFactura.tsx` (nuevo)

```typescript
import { useNavigate } from 'react-router-dom';

interface InfoPlanFacturaProps {
  planId: number;
  titulo: string;
  odontologo?: {
    usuario: {
      nombre: string;
      apellido: string;
    };
  };
}

const InfoPlanFactura = ({ planId, titulo, odontologo }: InfoPlanFacturaProps) => {
  const navigate = useNavigate();

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '20px',
      border: '1px solid #e5e7eb'
    }}>
      <h3 style={{
        fontSize: '16px',
        fontWeight: '700',
        color: '#111827',
        margin: '0 0 12px 0'
      }}>
        📋 Plan de Tratamiento
      </h3>

      <div style={{
        padding: '12px',
        backgroundColor: '#f9fafb',
        borderRadius: '6px',
        marginBottom: '12px'
      }}>
        <p style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#111827',
          margin: '0 0 8px 0'
        }}>
          {titulo}
        </p>

        {odontologo && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '16px' }}>👨‍⚕️</span>
            <p style={{
              fontSize: '13px',
              color: '#6b7280',
              margin: 0
            }}>
              {odontologo.usuario.nombre} {odontologo.usuario.apellido}
            </p>
          </div>
        )}
      </div>

      <button
        onClick={() => navigate(`/paciente/planes/${planId}`)}
        style={{
          width: '100%',
          padding: '10px',
          backgroundColor: 'transparent',
          color: '#10b981',
          border: '1px solid #10b981',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: 'pointer',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#f0fdf4';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        Ver Plan Completo →
      </button>
    </div>
  );
};

export default InfoPlanFactura;
```

---

### **Paso 4: Página DetalleFactura**

**Archivo:** `src/pages/paciente/DetalleFactura.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import facturasService from '../../services/facturasService';
import AlertaVencimiento from '../../components/paciente/AlertaVencimiento';
import PagoCard from '../../components/paciente/PagoCard';
import ItemPresupuestoCard from '../../components/paciente/ItemPresupuestoCard';
import InfoPlanFactura from '../../components/paciente/InfoPlanFactura';
import type { FacturaDetalle, EstadoFactura } from '../../types/facturacion.types';

const DetalleFactura = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [factura, setFactura] = useState<FacturaDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      cargarDetalleFactura();
    }
  }, [id]);

  const cargarDetalleFactura = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);

      const data = await facturasService.getFacturaDetalle(Number(id));
      setFactura(data);

    } catch (err: any) {
      console.error('Error cargando detalle:', err);
      setError('No se pudo cargar el detalle de la factura');

    } finally {
      setLoading(false);
    }
  };

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
      month: 'long',
      year: 'numeric'
    });
  };

  const calcularPorcentajePagado = (): number => {
    if (!factura) return 0;
    const total = parseFloat(factura.monto_total);
    const pagado = parseFloat(factura.monto_pagado);
    return (pagado / total) * 100;
  };

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
            ⏳ Cargando detalle de la factura...
          </p>
        </div>
      </div>
    );
  }

  if (error || !factura) {
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
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <p style={{ fontSize: '48px', margin: '0 0 16px 0' }}>⚠️</p>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 8px 0'
          }}>
            Error al cargar
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '0 0 20px 0'
          }}>
            {error || 'Factura no encontrada'}
          </p>
          <button
            onClick={() => navigate('/paciente/facturas')}
            style={{
              padding: '10px 20px',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            ← Volver a Facturas
          </button>
        </div>
      </div>
    );
  }

  const estadoConfig = getEstadoConfig(factura.estado);
  const porcentajePagado = calcularPorcentajePagado();

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
          <button
            onClick={() => navigate('/paciente/facturas')}
            style={{
              padding: '6px 12px',
              backgroundColor: 'transparent',
              color: '#10b981',
              border: '1px solid #10b981',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              marginBottom: '12px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f0fdf4';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            ← Volver a Facturas
          </button>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start'
          }}>
            <div>
              <h1 style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#111827',
                margin: '0 0 4px 0'
              }}>
                {factura.numero_factura}
              </h1>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                margin: 0
              }}>
                Emitida el {formatearFecha(factura.fecha_emision)}
              </p>
            </div>

            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 14px',
              backgroundColor: estadoConfig.bg,
              color: estadoConfig.color,
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              {estadoConfig.icon} {estadoConfig.texto}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Alerta de Vencimiento */}
        {(factura.estado === 'pendiente' || factura.estado === 'vencida') && (
          <div style={{ marginBottom: '24px' }}>
            <AlertaVencimiento 
              diasParaVencimiento={factura.dias_para_vencimiento}
              fechaVencimiento={factura.fecha_vencimiento}
            />
          </div>
        )}

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 350px',
          gap: '24px'
        }}>
          {/* Columna Izquierda */}
          <div>
            {/* Resumen de Montos */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb',
              marginBottom: '20px'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: '0 0 16px 0'
              }}>
                💰 Resumen de Factura
              </h3>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <div style={{
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 6px 0'
                  }}>
                    TOTAL
                  </p>
                  <p style={{
                    fontSize: '22px',
                    fontWeight: '700',
                    color: '#111827',
                    margin: 0
                  }}>
                    ${parseFloat(factura.monto_total).toFixed(2)}
                  </p>
                </div>

                <div style={{
                  padding: '16px',
                  backgroundColor: '#d1fae5',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#065f46',
                    margin: '0 0 6px 0'
                  }}>
                    PAGADO
                  </p>
                  <p style={{
                    fontSize: '22px',
                    fontWeight: '700',
                    color: '#10b981',
                    margin: 0
                  }}>
                    ${parseFloat(factura.monto_pagado).toFixed(2)}
                  </p>
                </div>

                <div style={{
                  padding: '16px',
                  backgroundColor: '#fef3c7',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#92400e',
                    margin: '0 0 6px 0'
                  }}>
                    PENDIENTE
                  </p>
                  <p style={{
                    fontSize: '22px',
                    fontWeight: '700',
                    color: '#f59e0b',
                    margin: 0
                  }}>
                    ${parseFloat(factura.saldo_pendiente).toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Barra de Progreso */}
              <div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '6px'
                }}>
                  <p style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: 0
                  }}>
                    PROGRESO DE PAGO
                  </p>
                  <p style={{
                    fontSize: '12px',
                    color: '#6b7280',
                    margin: 0
                  }}>
                    {porcentajePagado.toFixed(1)}%
                  </p>
                </div>
                <div style={{
                  width: '100%',
                  height: '8px',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '4px',
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
            </div>

            {/* Items del Presupuesto */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb',
              marginBottom: '20px'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: '0 0 16px 0'
              }}>
                📋 Servicios Facturados ({factura.presupuesto.items.length})
              </h3>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                {factura.presupuesto.items.map((item, index) => (
                  <ItemPresupuestoCard key={item.id} item={item} index={index} />
                ))}
              </div>

              <div style={{
                marginTop: '16px',
                paddingTop: '16px',
                borderTop: '2px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <p style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  TOTAL
                </p>
                <p style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  ${parseFloat(factura.presupuesto.total_presupuestado).toFixed(2)}
                </p>
              </div>
            </div>

            {/* Historial de Pagos */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb',
              marginBottom: '20px'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: '0 0 16px 0'
              }}>
                💳 Historial de Pagos ({factura.pagos.length})
              </h3>

              {factura.pagos.length === 0 ? (
                <div style={{
                  padding: '32px',
                  textAlign: 'center',
                  backgroundColor: '#f9fafb',
                  borderRadius: '6px'
                }}>
                  <p style={{ fontSize: '32px', margin: '0 0 8px 0' }}>💳</p>
                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    margin: 0
                  }}>
                    Aún no se han registrado pagos para esta factura
                  </p>
                </div>
              ) : (
                <>
                  {factura.pagos.map((pago, index) => (
                    <PagoCard key={pago.id} pago={pago} index={index} />
                  ))}
                </>
              )}
            </div>

            {/* Observaciones */}
            {factura.observaciones && (
              <div style={{
                backgroundColor: '#fefce8',
                borderRadius: '8px',
                padding: '16px',
                border: '1px solid #fef08a'
              }}>
                <h4 style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#854d0e',
                  margin: '0 0 8px 0'
                }}>
                  📌 Observaciones
                </h4>
                <p style={{
                  fontSize: '13px',
                  color: '#713f12',
                  margin: 0,
                  lineHeight: '1.6'
                }}>
                  {factura.observaciones}
                </p>
              </div>
            )}
          </div>

          {/* Columna Derecha */}
          <div>
            {/* Info del Plan */}
            <div style={{ marginBottom: '20px' }}>
              <InfoPlanFactura
                planId={factura.presupuesto.plan_tratamiento.id}
                titulo={factura.presupuesto.plan_tratamiento.titulo}
                odontologo={factura.presupuesto.plan_tratamiento.odontologo}
              />
            </div>

            {/* Información Adicional */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '20px',
              border: '1px solid #e5e7eb'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: '0 0 16px 0'
              }}>
                📄 Información
              </h3>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}>
                <div>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0'
                  }}>
                    FECHA DE EMISIÓN
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0
                  }}>
                    📅 {formatearFecha(factura.fecha_emision)}
                  </p>
                </div>

                <div>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0'
                  }}>
                    FECHA DE VENCIMIENTO
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0
                  }}>
                    ⏰ {formatearFecha(factura.fecha_vencimiento)}
                  </p>
                </div>

                <div>
                  <p style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0'
                  }}>
                    PACIENTE
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0
                  }}>
                    👤 {factura.paciente.usuario.nombre} {factura.paciente.usuario.apellido}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DetalleFactura;
```

---

### **Paso 5: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import DetalleFacturaPaciente from './pages/paciente/DetalleFactura'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ... rutas anteriores ... */}
        <Route path="/paciente/facturas" element={<FacturasPaciente />} />
        <Route path="/paciente/facturas/:id" element={<DetalleFacturaPaciente />} /> {/* ← NUEVO */}
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Detalle Completo**
1. Login con `paciente1@test.com`
2. Ir a "Facturas" → Click en una factura
3. **Esperado**:
   - Header con número de factura y estado
   - Resumen con 3 montos (Total, Pagado, Pendiente)
   - Lista de items del presupuesto
   - Historial de pagos
   - Info del plan relacionado

### **Caso 2: Ver Historial de Pagos**
1. Ver factura con múltiples pagos
2. **Esperado**:
   - Cada pago con método, monto, fecha
   - Referencias visibles
   - Observaciones mostradas
   - Numeración secuencial

### **Caso 3: Ver Items del Presupuesto**
1. Ver factura con varios servicios
2. **Esperado**:
   - Cada item con nombre de servicio
   - Pieza dental si aplica
   - Cantidad y precio unitario
   - Subtotal calculado
   - Total general correcto

### **Caso 4: Factura sin Pagos**
1. Ver factura recién emitida sin pagos
2. **Esperado**: 
   - Mensaje "Aún no se han registrado pagos"
   - Sección de pagos vacía pero visible

### **Caso 5: Navegar al Plan**
1. Click en "Ver Plan Completo"
2. **Esperado**: Navegación a `/paciente/planes/{id}`

### **Caso 6: Factura Pagada**
1. Ver factura con estado "pagada"
2. **Esperado**:
   - Badge verde "✓ Pagada"
   - Barra de progreso al 100%
   - Sin alertas de vencimiento

### **Caso 7: Factura Vencida**
1. Ver factura vencida
2. **Esperado**: Alerta roja con fecha de vencimiento

---

## ✅ Checklist de Verificación

- [ ] Detalle de factura carga correctamente
- [ ] Resumen de montos calculado correctamente
- [ ] Items del presupuesto se muestran todos
- [ ] Historial de pagos renderiza correctamente
- [ ] Métodos de pago con iconos adecuados
- [ ] Referencias de pago visibles
- [ ] Observaciones se muestran cuando existen
- [ ] Barra de progreso funciona
- [ ] Info del plan visible
- [ ] Botón "Ver Plan" funciona
- [ ] Botón "Volver" funciona
- [ ] Alertas de vencimiento funcionan
- [ ] Fechas formateadas correctamente
- [ ] Precios formateados correctamente

---

## 🐛 Errores Comunes

### **Error 1: Items no se muestran**
**Síntoma**: Sección de items vacía
**Causa**: `presupuesto.items` es undefined
**Solución**: Validar que el presupuesto tenga items antes de mapear

### **Error 2: Progreso incorrecto**
**Síntoma**: Barra de progreso desbordada
**Causa**: Monto pagado > monto total
**Solución**: Limitar porcentaje a máximo 100%

### **Error 3: Layout roto en móvil**
**Síntoma**: Columnas superpuestas
**Causa**: Grid no responsive
**Solución**: Agregar media query para una columna en pantallas pequeñas

---

## 🔄 Siguiente Paso

✅ Detalle completo de factura → Hemos completado **Phase 4 (Planes)** y parte de **Phase 5 (Facturación)**. El módulo de paciente tiene funcionalidad completa de consulta. Las fases restantes (notificaciones, configuración) son opcionales según necesidades del proyecto.

**Progreso actual: 13/24 guías (54.2%)**
