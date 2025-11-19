# 11 - Ver Detalle Completo del Plan de Tratamiento

## 🎯 Objetivo
Implementar la vista de detalle de un plan de tratamiento con información completa: servicios incluidos, progreso por ítem, observaciones del odontólogo, y línea de tiempo del tratamiento.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver lista de planes (Guía 10)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/tratamientos/planes/{id}/`
Obtiene detalle completo de un plan

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "id": 1,
  "titulo": "Plan de Restauración Dental Integral",
  "descripcion": "Restauración de piezas 16, 26 y 36 con resina premium. Plan integral para recuperar función masticatoria.",
  "paciente": {
    "id": 3,
    "usuario": {
      "nombre": "María",
      "apellido": "García",
      "email": "maria@test.com"
    }
  },
  "odontologo": {
    "id": 5,
    "usuario": {
      "nombre": "Dr. Carlos",
      "apellido": "López"
    },
    "especialidad": "Odontología General"
  },
  "estado": "EN_PROCESO",
  "prioridad": "MEDIA",
  "precio_total_plan": "450.00",
  "progreso_porcentaje": 33.33,
  "items_completados": 1,
  "items_totales": 3,
  "items": [
    {
      "id": 10,
      "servicio": {
        "id": 5,
        "nombre": "Restauración con Resina Premium",
        "codigo": "REST-001",
        "categoria": "OPERATORIA"
      },
      "pieza_dental": "16",
      "insumo_seleccionado": {
        "id": 8,
        "nombre": "Resina 3M A1",
        "precio_unitario": "15.00"
      },
      "cantidad": 1,
      "precio_congelado": "150.00",
      "estado_item": "COMPLETADO",
      "observaciones": "Restauración MO exitosa. Paciente tolera bien.",
      "fecha_completado": "2025-11-10T10:30:00-05:00"
    },
    {
      "id": 11,
      "servicio": {
        "id": 5,
        "nombre": "Restauración con Resina Premium",
        "codigo": "REST-001",
        "categoria": "OPERATORIA"
      },
      "pieza_dental": "26",
      "insumo_seleccionado": {
        "id": 8,
        "nombre": "Resina 3M A1",
        "precio_unitario": "15.00"
      },
      "cantidad": 1,
      "precio_congelado": "150.00",
      "estado_item": "EN_PROCESO",
      "observaciones": "Programado para próxima sesión"
    },
    {
      "id": 12,
      "servicio": {
        "id": 5,
        "nombre": "Restauración con Resina Premium",
        "codigo": "REST-001",
        "categoria": "OPERATORIA"
      },
      "pieza_dental": "36",
      "cantidad": 1,
      "precio_congelado": "150.00",
      "estado_item": "PENDIENTE"
    }
  ],
  "fecha_creacion": "2025-11-01T10:00:00-05:00",
  "fecha_presentacion": "2025-11-02T14:00:00-05:00",
  "fecha_aceptacion": "2025-11-03T09:00:00-05:00",
  "fecha_inicio_tratamiento": "2025-11-10T08:00:00-05:00",
  "observaciones": "Paciente con buena higiene dental. Requiere control en 3 meses."
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── DetallePlan.tsx               ← Nuevo
├── components/
│   └── paciente/
│       ├── ItemPlanCard.tsx              ← Nuevo
│       ├── LineaTiempoPlan.tsx           ← Nuevo
│       └── ResumenPresupuesto.tsx        ← Nuevo
└── services/
    └── planesService.ts                  ← Extender
```

---

## 💻 Código Paso a Paso

### **Paso 1: Componente ItemPlanCard**

**Archivo:** `src/components/paciente/ItemPlanCard.tsx` (nuevo)

```typescript
import type { ItemPlan, EstadoItem } from '../../types/planes.types';

interface ItemPlanCardProps {
  item: ItemPlan;
  index: number;
}

const ItemPlanCard = ({ item, index }: ItemPlanCardProps) => {
  const getEstadoConfig = (estado: EstadoItem) => {
    const configs: Record<EstadoItem, { color: string; bg: string; icon: string; texto: string }> = {
      'PENDIENTE': { color: '#6b7280', bg: '#f3f4f6', icon: '⏸️', texto: 'Pendiente' },
      'EN_PROCESO': { color: '#f59e0b', bg: '#fef3c7', icon: '⏳', texto: 'En Proceso' },
      'COMPLETADO': { color: '#10b981', bg: '#d1fae5', icon: '✓', texto: 'Completado' },
      'CANCELADO': { color: '#ef4444', bg: '#fee2e2', icon: '✗', texto: 'Cancelado' }
    };
    return configs[estado];
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const estadoConfig = getEstadoConfig(item.estado_item);

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
              backgroundColor: '#f3f4f6',
              borderRadius: '50%',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280'
            }}>
              {index + 1}
            </span>
            <h4 style={{
              fontSize: '15px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              {item.servicio.nombre}
            </h4>
          </div>

          <div style={{
            display: 'flex',
            gap: '12px',
            fontSize: '13px',
            color: '#6b7280',
            marginLeft: '32px'
          }}>
            <span>📋 {item.servicio.codigo}</span>
            {item.pieza_dental && (
              <span>🦷 Pieza {item.pieza_dental}</span>
            )}
            {item.insumo_seleccionado && (
              <span>💊 {item.insumo_seleccionado.nombre}</span>
            )}
          </div>
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
          fontWeight: '600',
          flexShrink: 0
        }}>
          {estadoConfig.icon} {estadoConfig.texto}
        </span>
      </div>

      {/* Observaciones */}
      {item.observaciones && (
        <div style={{
          backgroundColor: '#f9fafb',
          padding: '10px',
          borderRadius: '6px',
          marginBottom: '12px'
        }}>
          <p style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            margin: '0 0 4px 0'
          }}>
            NOTAS DEL ODONTÓLOGO:
          </p>
          <p style={{
            fontSize: '13px',
            color: '#374151',
            margin: 0,
            lineHeight: '1.5'
          }}>
            {item.observaciones}
          </p>
        </div>
      )}

      {/* Footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: '12px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <div>
          {item.fecha_completado ? (
            <p style={{
              fontSize: '12px',
              color: '#10b981',
              margin: 0
            }}>
              ✓ Completado el {formatearFecha(item.fecha_completado)}
            </p>
          ) : (
            <p style={{
              fontSize: '12px',
              color: '#6b7280',
              margin: 0
            }}>
              {item.estado_item === 'EN_PROCESO' 
                ? '⏳ En progreso' 
                : '⏸️ Por realizar'}
            </p>
          )}
        </div>

        <p style={{
          fontSize: '16px',
          fontWeight: '700',
          color: '#111827',
          margin: 0
        }}>
          ${parseFloat(item.precio_congelado).toFixed(2)}
        </p>
      </div>
    </div>
  );
};

export default ItemPlanCard;
```

---

### **Paso 2: Componente LineaTiempoPlan**

**Archivo:** `src/components/paciente/LineaTiempoPlan.tsx` (nuevo)

```typescript
import type { PlanTratamientoDetalle } from '../../types/planes.types';

interface LineaTiempoPlanProps {
  plan: PlanTratamientoDetalle;
}

const LineaTiempoPlan = ({ plan }: LineaTiempoPlanProps) => {
  const formatearFecha = (fecha?: string): string => {
    if (!fecha) return '---';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  interface Evento {
    fecha?: string;
    titulo: string;
    descripcion: string;
    icon: string;
    color: string;
    completado: boolean;
  }

  const eventos: Evento[] = [
    {
      fecha: plan.fecha_creacion,
      titulo: 'Plan Creado',
      descripcion: `Creado por Dr. ${plan.odontologo.usuario.apellido}`,
      icon: '📝',
      color: '#6b7280',
      completado: true
    },
    {
      fecha: plan.fecha_presentacion,
      titulo: 'Plan Presentado',
      descripcion: 'Plan presentado al paciente',
      icon: '📋',
      color: '#3b82f6',
      completado: !!plan.fecha_presentacion
    },
    {
      fecha: plan.fecha_aceptacion,
      titulo: 'Plan Aceptado',
      descripcion: 'Paciente aceptó el plan',
      icon: '✓',
      color: '#10b981',
      completado: !!plan.fecha_aceptacion
    },
    {
      fecha: plan.fecha_inicio_tratamiento,
      titulo: 'Tratamiento Iniciado',
      descripcion: 'Primera sesión realizada',
      icon: '🏥',
      color: '#f59e0b',
      completado: !!plan.fecha_inicio_tratamiento
    }
  ];

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
        margin: '0 0 20px 0'
      }}>
        ⏱️ Línea de Tiempo
      </h3>

      <div style={{ position: 'relative' }}>
        {/* Línea vertical */}
        <div style={{
          position: 'absolute',
          left: '15px',
          top: '0',
          bottom: '0',
          width: '2px',
          backgroundColor: '#e5e7eb'
        }} />

        {eventos.map((evento, index) => (
          <div
            key={index}
            style={{
              position: 'relative',
              paddingLeft: '48px',
              paddingBottom: index < eventos.length - 1 ? '24px' : '0'
            }}
          >
            {/* Círculo indicador */}
            <div style={{
              position: 'absolute',
              left: '0',
              top: '0',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: evento.completado ? evento.color : '#e5e7eb',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '16px',
              border: '3px solid white',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}>
              {evento.completado ? evento.icon : '○'}
            </div>

            {/* Contenido */}
            <div style={{
              opacity: evento.completado ? 1 : 0.5
            }}>
              <p style={{
                fontSize: '14px',
                fontWeight: '600',
                color: evento.completado ? '#111827' : '#9ca3af',
                margin: '0 0 2px 0'
              }}>
                {evento.titulo}
              </p>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '0 0 4px 0'
              }}>
                {evento.descripcion}
              </p>
              <p style={{
                fontSize: '11px',
                color: '#9ca3af',
                margin: 0
              }}>
                {formatearFecha(evento.fecha)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LineaTiempoPlan;
```

---

### **Paso 3: Componente ResumenPresupuesto**

**Archivo:** `src/components/paciente/ResumenPresupuesto.tsx` (nuevo)

```typescript
import type { PlanTratamientoDetalle } from '../../types/planes.types';

interface ResumenPresupuestoProps {
  plan: PlanTratamientoDetalle;
}

const ResumenPresupuesto = ({ plan }: ResumenPresupuestoProps) => {
  const totalPlan = parseFloat(plan.precio_total_plan);
  const completados = plan.items.filter(item => item.estado_item === 'COMPLETADO');
  const totalGastado = completados.reduce((sum, item) => sum + parseFloat(item.precio_congelado), 0);
  const totalPendiente = totalPlan - totalGastado;

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
        margin: '0 0 16px 0'
      }}>
        💰 Resumen de Presupuesto
      </h3>

      {/* Total del Plan */}
      <div style={{
        backgroundColor: '#f0fdf4',
        padding: '16px',
        borderRadius: '8px',
        marginBottom: '12px',
        border: '1px solid #bbf7d0'
      }}>
        <p style={{
          fontSize: '12px',
          color: '#15803d',
          fontWeight: '600',
          margin: '0 0 4px 0'
        }}>
          PRESUPUESTO TOTAL
        </p>
        <p style={{
          fontSize: '28px',
          fontWeight: '700',
          color: '#15803d',
          margin: 0
        }}>
          ${totalPlan.toFixed(2)}
        </p>
      </div>

      {/* Desglose */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        {/* Gastado */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '16px' }}>✓</span>
            <span style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#374151'
            }}>
              Invertido
            </span>
          </div>
          <span style={{
            fontSize: '15px',
            fontWeight: '700',
            color: '#10b981'
          }}>
            ${totalGastado.toFixed(2)}
          </span>
        </div>

        {/* Pendiente */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '16px' }}>⏳</span>
            <span style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#374151'
            }}>
              Pendiente
            </span>
          </div>
          <span style={{
            fontSize: '15px',
            fontWeight: '700',
            color: '#f59e0b'
          }}>
            ${totalPendiente.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Progreso visual */}
      <div style={{ marginTop: '16px' }}>
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
            PROGRESO DEL GASTO
          </p>
          <p style={{
            fontSize: '12px',
            color: '#6b7280',
            margin: 0
          }}>
            {((totalGastado / totalPlan) * 100).toFixed(1)}%
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
            width: `${(totalGastado / totalPlan) * 100}%`,
            height: '100%',
            backgroundColor: '#10b981',
            transition: 'width 0.3s ease'
          }} />
        </div>
      </div>

      {/* Información adicional */}
      <div style={{
        marginTop: '16px',
        paddingTop: '16px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <p style={{
          fontSize: '12px',
          color: '#6b7280',
          margin: 0,
          lineHeight: '1.5'
        }}>
          💡 <strong>Nota:</strong> Los precios se congelaron al momento de crear el plan.
          Los costos de materiales ya están incluidos.
        </p>
      </div>
    </div>
  );
};

export default ResumenPresupuesto;
```

---

### **Paso 4: Página DetallePlan**

**Archivo:** `src/pages/paciente/DetallePlan.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import planesService from '../../services/planesService';
import BarraProgreso from '../../components/paciente/BarraProgreso';
import ItemPlanCard from '../../components/paciente/ItemPlanCard';
import LineaTiempoPlan from '../../components/paciente/LineaTiempoPlan';
import ResumenPresupuesto from '../../components/paciente/ResumenPresupuesto';
import type { PlanTratamientoDetalle, EstadoPlan, PrioridadPlan } from '../../types/planes.types';

const DetallePlan = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [plan, setPlan] = useState<PlanTratamientoDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      cargarDetallePlan();
    }
  }, [id]);

  const cargarDetallePlan = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);

      const data = await planesService.getPlanDetalle(Number(id));
      setPlan(data);

    } catch (err: any) {
      console.error('Error cargando detalle:', err);
      setError('No se pudo cargar el detalle del plan');

    } finally {
      setLoading(false);
    }
  };

  const getEstadoConfig = (estado: EstadoPlan) => {
    const configs: Record<EstadoPlan, { color: string; bg: string; icon: string; texto: string }> = {
      'BORRADOR': { color: '#6b7280', bg: '#f3f4f6', icon: '📝', texto: 'Borrador' },
      'PRESENTADO': { color: '#3b82f6', bg: '#dbeafe', icon: '📋', texto: 'Presentado' },
      'ACEPTADO': { color: '#10b981', bg: '#d1fae5', icon: '✓', texto: 'Aceptado' },
      'EN_PROCESO': { color: '#f59e0b', bg: '#fef3c7', icon: '⏳', texto: 'En Proceso' },
      'FINALIZADO': { color: '#8b5cf6', bg: '#ede9fe', icon: '✓✓', texto: 'Finalizado' },
      'CANCELADO': { color: '#ef4444', bg: '#fee2e2', icon: '✗', texto: 'Cancelado' }
    };
    return configs[estado];
  };

  const getPrioridadConfig = (prioridad: PrioridadPlan) => {
    const configs: Record<PrioridadPlan, { color: string; icon: string; texto: string }> = {
      'BAJA': { color: '#6b7280', icon: '⬇️', texto: 'Baja' },
      'MEDIA': { color: '#3b82f6', icon: '➡️', texto: 'Media' },
      'ALTA': { color: '#f59e0b', icon: '⬆️', texto: 'Alta' },
      'URGENTE': { color: '#ef4444', icon: '🔥', texto: 'Urgente' }
    };
    return configs[prioridad];
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
            ⏳ Cargando detalle del plan...
          </p>
        </div>
      </div>
    );
  }

  if (error || !plan) {
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
            {error || 'Plan no encontrado'}
          </p>
          <button
            onClick={() => navigate('/paciente/planes')}
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
            ← Volver a Planes
          </button>
        </div>
      </div>
    );
  }

  const estadoConfig = getEstadoConfig(plan.estado);
  const prioridadConfig = getPrioridadConfig(plan.prioridad);

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
            onClick={() => navigate('/paciente/planes')}
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
            ← Volver a Planes
          </button>

          <h1 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#111827',
            margin: '0 0 8px 0'
          }}>
            {plan.titulo}
          </h1>

          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
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

            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              backgroundColor: `${prioridadConfig.color}20`,
              color: prioridadConfig.color,
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {prioridadConfig.icon} Prioridad {prioridadConfig.texto}
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
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 350px',
          gap: '24px'
        }}>
          {/* Columna Izquierda */}
          <div>
            {/* Descripción del Plan */}
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
                margin: '0 0 8px 0'
              }}>
                📝 Descripción
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#374151',
                margin: 0,
                lineHeight: '1.6'
              }}>
                {plan.descripcion}
              </p>
            </div>

            {/* Odontólogo */}
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
                margin: '0 0 12px 0'
              }}>
                👨‍⚕️ Profesional Asignado
              </h3>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  backgroundColor: '#10b981',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  color: 'white',
                  fontWeight: '700'
                }}>
                  {plan.odontologo.usuario.nombre.charAt(0)}
                </div>
                <div>
                  <p style={{
                    fontSize: '15px',
                    fontWeight: '600',
                    color: '#111827',
                    margin: 0
                  }}>
                    {plan.odontologo.usuario.nombre} {plan.odontologo.usuario.apellido}
                  </p>
                  {plan.odontologo.especialidad && (
                    <p style={{
                      fontSize: '13px',
                      color: '#6b7280',
                      margin: 0
                    }}>
                      {plan.odontologo.especialidad}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Progreso General */}
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
                margin: '0 0 12px 0'
              }}>
                📊 Progreso General
              </h3>
              <BarraProgreso 
                progreso={plan.progreso_porcentaje} 
                altura={12}
              />
              <p style={{
                fontSize: '13px',
                color: '#6b7280',
                margin: '8px 0 0 0'
              }}>
                {plan.items_completados} de {plan.items_totales} servicios completados
              </p>
            </div>

            {/* Servicios del Plan */}
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
                🦷 Servicios Incluidos ({plan.items.length})
              </h3>

              {plan.items.map((item, index) => (
                <ItemPlanCard key={item.id} item={item} index={index} />
              ))}
            </div>

            {/* Observaciones Generales */}
            {plan.observaciones && (
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
                  📌 Observaciones Generales
                </h4>
                <p style={{
                  fontSize: '13px',
                  color: '#713f12',
                  margin: 0,
                  lineHeight: '1.6'
                }}>
                  {plan.observaciones}
                </p>
              </div>
            )}
          </div>

          {/* Columna Derecha */}
          <div>
            {/* Resumen de Presupuesto */}
            <div style={{ marginBottom: '20px' }}>
              <ResumenPresupuesto plan={plan} />
            </div>

            {/* Línea de Tiempo */}
            <LineaTiempoPlan plan={plan} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default DetallePlan;
```

---

### **Paso 5: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import DetallePlanPaciente from './pages/paciente/DetallePlan'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ... rutas anteriores ... */}
        <Route path="/paciente/planes" element={<PlanesPaciente />} />
        <Route path="/paciente/planes/:id" element={<DetallePlanPaciente />} /> {/* ← NUEVO */}
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Detalle Completo**
1. Login con `paciente1@test.com`
2. Ir a "Planes" → Click en un plan
3. **Esperado**:
   - Header con título, estado, prioridad
   - Descripción completa
   - Información del odontólogo
   - Lista de todos los servicios
   - Resumen de presupuesto
   - Línea de tiempo

### **Caso 2: Ver Items con Diferentes Estados**
1. Ver plan con items en progreso
2. **Esperado**:
   - Items COMPLETADO con fecha y check verde
   - Items EN_PROCESO con reloj amarillo
   - Items PENDIENTE con círculo gris
   - Observaciones visibles en cada item

### **Caso 3: Ver Progreso de Presupuesto**
1. Ver plan parcialmente completado
2. **Esperado**:
   - Total del plan destacado
   - Monto invertido calculado correctamente
   - Monto pendiente correcto
   - Barra de progreso de gasto

### **Caso 4: Línea de Tiempo Completa**
1. Ver plan EN_PROCESO
2. **Esperado**:
   - Eventos completados con check e icono
   - Eventos pendientes en gris con círculo vacío
   - Fechas formateadas correctamente
   - Línea vertical conectando eventos

### **Caso 5: Plan sin Observaciones**
1. Ver plan simple sin observaciones
2. **Esperado**: 
   - Sección de observaciones no se muestra
   - Items sin observaciones no muestran caja de notas

### **Caso 6: Navegación de Regreso**
1. Click en "← Volver a Planes"
2. **Esperado**: Navegación a `/paciente/planes`

### **Caso 7: Plan No Encontrado**
1. Navegar a `/paciente/planes/99999`
2. **Esperado**: 
   - Mensaje de error
   - Botón para volver a la lista

---

## ✅ Checklist de Verificación

- [ ] Detalle del plan carga correctamente
- [ ] Información del plan se muestra completa
- [ ] Lista de servicios renderiza correctamente
- [ ] Estados de items con colores adecuados
- [ ] Observaciones se muestran cuando existen
- [ ] Resumen de presupuesto calcula correctamente
- [ ] Línea de tiempo muestra eventos correctos
- [ ] Progreso general funciona
- [ ] Información del odontólogo visible
- [ ] Botón "Volver" funciona
- [ ] Error handling para plan inexistente
- [ ] Responsive en pantallas pequeñas
- [ ] Fechas formateadas correctamente
- [ ] Precios formateados correctamente

---

## 🐛 Errores Comunes

### **Error 1: Plan no carga**
**Síntoma**: Loading infinito o error 404
**Causa**: ID incorrecto o plan no pertenece al paciente
**Solución**: Verificar que el plan existe y pertenece al paciente autenticado

### **Error 2: Cálculo de presupuesto incorrecto**
**Síntoma**: Totales no coinciden
**Causa**: parseFloat no maneja decimales correctamente
**Solución**: Verificar que todos los precios son strings válidos

### **Error 3: Línea de tiempo desordenada**
**Síntoma**: Eventos en orden incorrecto
**Causa**: Fechas opcionales undefined
**Solución**: Validar fechas antes de ordenar

### **Error 4: Layout roto en móvil**
**Síntoma**: Columnas superpuestas
**Causa**: Grid no responsive
**Solución**: Agregar media query para cambiar a una columna en pantallas pequeñas

---

## 🔄 Siguiente Paso

✅ Detalle completo del plan → Continuar con **`12_ver_presupuesto_detallado.md`** (Desglose de costos y pagos)
