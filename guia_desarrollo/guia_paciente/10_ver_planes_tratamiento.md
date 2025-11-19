# 10 - Ver Mis Planes de Tratamiento

## 🎯 Objetivo
Implementar la visualización de los planes de tratamiento del paciente, mostrando estado, progreso, servicios incluidos y presupuesto de forma clara y comprensible.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Dashboard funcional (Guía 02)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/tratamientos/planes/`
Lista planes de tratamiento (paciente ve solo los suyos)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado` (opcional): BORRADOR, PRESENTADO, ACEPTADO, EN_PROCESO, FINALIZADO, CANCELADO

**Response 200:**
```json
[
  {
    "id": 1,
    "titulo": "Plan de Restauración Dental Integral",
    "descripcion": "Restauración de piezas 16, 26 y 36 con resina premium",
    "paciente": {
      "id": 3,
      "usuario": {
        "nombre": "María",
        "apellido": "García"
      }
    },
    "odontologo": {
      "id": 5,
      "usuario": {
        "nombre": "Carlos",
        "apellido": "López"
      },
      "especialidad": "Odontología General"
    },
    "estado": "ACEPTADO",
    "prioridad": "MEDIA",
    "precio_total_plan": "450.00",
    "progreso_porcentaje": 33.33,
    "items_completados": 1,
    "items_totales": 3,
    "fecha_creacion": "2025-11-01T10:00:00-05:00",
    "fecha_presentacion": "2025-11-02T14:00:00-05:00",
    "fecha_aceptacion": "2025-11-03T09:00:00-05:00"
  }
]
```

### **GET** `/tenant/api/tratamientos/planes/{id}/`
Detalle completo de un plan

**Response 200:**
```json
{
  "id": 1,
  "titulo": "Plan de Restauración Dental Integral",
  "descripcion": "Restauración de piezas 16, 26 y 36 con resina premium",
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
      "nombre": "Carlos",
      "apellido": "López"
    },
    "especialidad": "Odontología General"
  },
  "estado": "ACEPTADO",
  "prioridad": "MEDIA",
  "precio_total_plan": "450.00",
  "progreso_porcentaje": 33.33,
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
      "observaciones": "Restauración MO exitosa",
      "fecha_completado": "2025-11-10T10:30:00-05:00"
    },
    {
      "id": 11,
      "servicio": {
        "id": 5,
        "nombre": "Restauración con Resina Premium"
      },
      "pieza_dental": "26",
      "cantidad": 1,
      "precio_congelado": "150.00",
      "estado_item": "PENDIENTE"
    },
    {
      "id": 12,
      "servicio": {
        "id": 5,
        "nombre": "Restauración con Resina Premium"
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
  "observaciones": "Paciente con buena higiene dental"
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Planes.tsx                    ← Nuevo
│       └── DetallePlan.tsx               ← Nuevo
├── components/
│   └── paciente/
│       ├── PlanCard.tsx                  ← Nuevo
│       ├── ItemPlanCard.tsx              ← Nuevo
│       └── BarraProgreso.tsx             ← Nuevo
├── services/
│   └── planesService.ts                  ← Nuevo
└── types/
    └── planes.types.ts                   ← Nuevo
```

---

## 💻 Código Paso a Paso

### **Paso 1: Crear tipos de Planes**

**Archivo:** `src/types/planes.types.ts` (nuevo)

```typescript
export type EstadoPlan = 
  | 'BORRADOR'
  | 'PRESENTADO'
  | 'ACEPTADO'
  | 'EN_PROCESO'
  | 'FINALIZADO'
  | 'CANCELADO';

export type PrioridadPlan = 'BAJA' | 'MEDIA' | 'ALTA' | 'URGENTE';

export type EstadoItem = 
  | 'PENDIENTE'
  | 'EN_PROCESO'
  | 'COMPLETADO'
  | 'CANCELADO';

export interface Servicio {
  id: number;
  nombre: string;
  codigo: string;
  categoria: string;
}

export interface Insumo {
  id: number;
  nombre: string;
  precio_unitario: string;
}

export interface ItemPlan {
  id: number;
  servicio: Servicio;
  pieza_dental?: string;
  insumo_seleccionado?: Insumo;
  cantidad: number;
  precio_congelado: string;
  estado_item: EstadoItem;
  observaciones?: string;
  fecha_completado?: string;
}

export interface PlanTratamientoLista {
  id: number;
  titulo: string;
  descripcion: string;
  paciente: {
    id: number;
    usuario: {
      nombre: string;
      apellido: string;
    };
  };
  odontologo: {
    id: number;
    usuario: {
      nombre: string;
      apellido: string;
    };
    especialidad?: string;
  };
  estado: EstadoPlan;
  prioridad: PrioridadPlan;
  precio_total_plan: string;
  progreso_porcentaje: number;
  items_completados: number;
  items_totales: number;
  fecha_creacion: string;
  fecha_presentacion?: string;
  fecha_aceptacion?: string;
}

export interface PlanTratamientoDetalle extends PlanTratamientoLista {
  items: ItemPlan[];
  fecha_inicio_tratamiento?: string;
  fecha_fin_tratamiento?: string;
  observaciones?: string;
}
```

---

### **Paso 2: Crear servicio de Planes**

**Archivo:** `src/services/planesService.ts` (nuevo)

```typescript
import apiClient from '../config/apiClient';
import type { PlanTratamientoLista, PlanTratamientoDetalle } from '../types/planes.types';

const planesService = {
  /**
   * Obtener todos los planes del paciente
   */
  async getMisPlanes(): Promise<PlanTratamientoLista[]> {
    console.group('📋 [planesService] getMisPlanes');
    
    try {
      const response = await apiClient.get<PlanTratamientoLista[]>(
        '/tenant/api/tratamientos/planes/'
      );
      
      console.log('✅ Planes obtenidos:', response.data.length);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo planes:', error);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Obtener detalle de un plan específico
   */
  async getPlanDetalle(planId: number): Promise<PlanTratamientoDetalle> {
    console.group('🔍 [planesService] getPlanDetalle');
    console.log('ID:', planId);
    
    try {
      const response = await apiClient.get<PlanTratamientoDetalle>(
        `/tenant/api/tratamientos/planes/${planId}/`
      );
      
      console.log('✅ Plan obtenido');
      console.log('Items:', response.data.items.length);
      console.log('Progreso:', response.data.progreso_porcentaje + '%');
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo detalle:', error);
      console.groupEnd();
      throw error;
    }
  }
};

export default planesService;
```

---

### **Paso 3: Componente BarraProgreso**

**Archivo:** `src/components/paciente/BarraProgreso.tsx` (nuevo)

```typescript
interface BarraProgresoProps {
  progreso: number; // 0-100
  altura?: number;
  mostrarPorcentaje?: boolean;
}

const BarraProgreso = ({ 
  progreso, 
  altura = 8, 
  mostrarPorcentaje = true 
}: BarraProgresoProps) => {
  const porcentaje = Math.min(Math.max(progreso, 0), 100);
  
  const getColor = (): string => {
    if (porcentaje === 0) return '#e5e7eb';
    if (porcentaje < 30) return '#ef4444';
    if (porcentaje < 70) return '#f59e0b';
    if (porcentaje < 100) return '#3b82f6';
    return '#10b981';
  };

  return (
    <div>
      <div style={{
        width: '100%',
        height: `${altura}px`,
        backgroundColor: '#e5e7eb',
        borderRadius: `${altura / 2}px`,
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${porcentaje}%`,
          height: '100%',
          backgroundColor: getColor(),
          transition: 'width 0.3s ease, background-color 0.3s ease'
        }} />
      </div>
      
      {mostrarPorcentaje && (
        <p style={{
          fontSize: '12px',
          color: '#6b7280',
          margin: '4px 0 0 0',
          textAlign: 'right'
        }}>
          {porcentaje.toFixed(1)}% completado
        </p>
      )}
    </div>
  );
};

export default BarraProgreso;
```

---

### **Paso 4: Componente PlanCard**

**Archivo:** `src/components/paciente/PlanCard.tsx` (nuevo)

```typescript
import { useNavigate } from 'react-router-dom';
import BarraProgreso from './BarraProgreso';
import type { PlanTratamientoLista, EstadoPlan, PrioridadPlan } from '../../types/planes.types';

interface PlanCardProps {
  plan: PlanTratamientoLista;
}

const PlanCard = ({ plan }: PlanCardProps) => {
  const navigate = useNavigate();

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
    const configs: Record<PrioridadPlan, { color: string; icon: string }> = {
      'BAJA': { color: '#6b7280', icon: '⬇️' },
      'MEDIA': { color: '#3b82f6', icon: '➡️' },
      'ALTA': { color: '#f59e0b', icon: '⬆️' },
      'URGENTE': { color: '#ef4444', icon: '🔥' }
    };
    return configs[prioridad];
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const estadoConfig = getEstadoConfig(plan.estado);
  const prioridadConfig = getPrioridadConfig(plan.prioridad);

  return (
    <div
      onClick={() => navigate(`/paciente/planes/${plan.id}`)}
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
        <div style={{ flex: 1 }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 4px 0'
          }}>
            {plan.titulo}
          </h3>
          <p style={{
            fontSize: '13px',
            color: '#6b7280',
            margin: 0,
            lineHeight: '1.4'
          }}>
            {plan.descripcion}
          </p>
        </div>

        <div style={{
          display: 'flex',
          gap: '6px',
          flexShrink: 0,
          marginLeft: '12px'
        }}>
          {/* Badge Estado */}
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

          {/* Badge Prioridad */}
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            padding: '4px 8px',
            backgroundColor: `${prioridadConfig.color}20`,
            color: prioridadConfig.color,
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            {prioridadConfig.icon}
          </span>
        </div>
      </div>

      {/* Odontólogo */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '12px',
        padding: '8px',
        backgroundColor: '#f9fafb',
        borderRadius: '6px'
      }}>
        <span style={{ fontSize: '14px' }}>👨‍⚕️</span>
        <div>
          <p style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#374151',
            margin: 0
          }}>
            {plan.odontologo.usuario.nombre} {plan.odontologo.usuario.apellido}
          </p>
          {plan.odontologo.especialidad && (
            <p style={{
              fontSize: '12px',
              color: '#6b7280',
              margin: 0
            }}>
              {plan.odontologo.especialidad}
            </p>
          )}
        </div>
      </div>

      {/* Progreso */}
      <div style={{ marginBottom: '12px' }}>
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
            PROGRESO
          </p>
          <p style={{
            fontSize: '12px',
            color: '#6b7280',
            margin: 0
          }}>
            {plan.items_completados} / {plan.items_totales} servicios
          </p>
        </div>
        <BarraProgreso progreso={plan.progreso_porcentaje} />
      </div>

      {/* Footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: '12px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <div>
          <p style={{
            fontSize: '11px',
            color: '#9ca3af',
            margin: '0 0 2px 0'
          }}>
            Creado el {formatearFecha(plan.fecha_creacion)}
          </p>
          {plan.fecha_aceptacion && (
            <p style={{
              fontSize: '11px',
              color: '#10b981',
              margin: 0
            }}>
              ✓ Aceptado el {formatearFecha(plan.fecha_aceptacion)}
            </p>
          )}
        </div>

        <div style={{ textAlign: 'right' }}>
          <p style={{
            fontSize: '11px',
            color: '#6b7280',
            margin: '0 0 2px 0'
          }}>
            Presupuesto
          </p>
          <p style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#10b981',
            margin: 0
          }}>
            ${parseFloat(plan.precio_total_plan).toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PlanCard;
```

---

### **Paso 5: Página Planes**

**Archivo:** `src/pages/paciente/Planes.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import planesService from '../../services/planesService';
import PlanCard from '../../components/paciente/PlanCard';
import type { PlanTratamientoLista, EstadoPlan } from '../../types/planes.types';

const Planes = () => {
  const navigate = useNavigate();

  const [planes, setPlanes] = useState<PlanTratamientoLista[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<EstadoPlan | 'TODOS'>('TODOS');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarPlanes();
  }, []);

  const cargarPlanes = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await planesService.getMisPlanes();
      setPlanes(data);

    } catch (err: any) {
      console.error('Error cargando planes:', err);
      setError('No se pudieron cargar los planes');

    } finally {
      setLoading(false);
    }
  };

  const planesFiltrados = filtroEstado === 'TODOS'
    ? planes
    : planes.filter(plan => plan.estado === filtroEstado);

  const planesOrdenados = [...planesFiltrados].sort((a, b) => {
    return new Date(b.fecha_creacion).getTime() - new Date(a.fecha_creacion).getTime();
  });

  const estadosFiltro: Array<{ valor: EstadoPlan | 'TODOS'; texto: string; icon: string }> = [
    { valor: 'TODOS', texto: 'Todos', icon: '📋' },
    { valor: 'PRESENTADO', texto: 'Presentados', icon: '📋' },
    { valor: 'ACEPTADO', texto: 'Aceptados', icon: '✓' },
    { valor: 'EN_PROCESO', texto: 'En Proceso', icon: '⏳' },
    { valor: 'FINALIZADO', texto: 'Finalizados', icon: '✓✓' }
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
            ⏳ Cargando planes...
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
            🦷 Mis Planes de Tratamiento
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '4px 0 0 0'
          }}>
            {planes.length} {planes.length === 1 ? 'plan' : 'planes'} en total
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

        {/* Lista de Planes */}
        {planesOrdenados.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '48px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <p style={{ fontSize: '48px', margin: '0 0 16px 0' }}>🦷</p>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 8px 0'
            }}>
              No hay planes
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {filtroEstado === 'TODOS'
                ? 'Aún no tienes planes de tratamiento'
                : `No tienes planes con estado ${filtroEstado}`}
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gap: '16px'
          }}>
            {planesOrdenados.map((plan) => (
              <PlanCard key={plan.id} plan={plan} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Planes;
```

---

### **Paso 6: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import PlanesPaciente from './pages/paciente/Planes'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        <Route path="/paciente/perfil" element={<PerfilPaciente />} />
        <Route path="/paciente/citas" element={<CitasPaciente />} />
        <Route path="/paciente/citas/solicitar" element={<SolicitarCitaPaciente />} />
        <Route path="/paciente/citas/:id/reprogramar" element={<ReprogramarCitaPaciente />} />
        <Route path="/paciente/historial" element={<HistorialClinicoPaciente />} />
        <Route path="/paciente/documentos" element={<DocumentosPaciente />} />
        <Route path="/paciente/planes" element={<PlanesPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Lista de Planes**
1. Login con `paciente1@test.com` / `paciente123`
2. Navegar a "Planes de Tratamiento"
3. **Esperado**:
   - Lista de planes ordenados por fecha
   - Cada plan muestra: título, descripción, estado, progreso
   - Badges de estado y prioridad
   - Barra de progreso con porcentaje

### **Caso 2: Filtrar por Estado**
1. Click en "⏳ En Proceso"
2. **Esperado**: Solo planes EN_PROCESO
3. Click en "📋 Todos"
4. **Esperado**: Todos los planes

### **Caso 3: Ver Progreso**
1. Buscar plan con items completados
2. **Esperado**:
   - Barra de progreso coloreada según porcentaje
   - Contador "X / Y servicios"
   - Porcentaje numérico

### **Caso 4: Ver Detalles del Plan**
1. Click en un plan
2. **Esperado**: Navegación a `/paciente/planes/{id}` (próxima guía)

### **Caso 5: Sin Planes**
1. Paciente sin planes
2. **Esperado**: Mensaje "Aún no tienes planes de tratamiento"

### **Caso 6: Estados Visuales**
1. Ver planes con diferentes estados
2. **Esperado**:
   - PRESENTADO: azul
   - ACEPTADO: verde
   - EN_PROCESO: amarillo
   - FINALIZADO: morado
   - Colores consistentes

---

## ✅ Checklist de Verificación

- [ ] Lista de planes carga correctamente
- [ ] Filtros por estado funcionan
- [ ] Cards muestran toda la información
- [ ] Barra de progreso funciona
- [ ] Badges de estado con colores correctos
- [ ] Badges de prioridad visibles
- [ ] Información de odontólogo se muestra
- [ ] Precios formateados correctamente
- [ ] Fechas formateadas correctamente
- [ ] Click en plan navega a detalle
- [ ] Estado vacío funciona
- [ ] Ordenamiento por fecha funciona
- [ ] Hover effects funcionan
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: Planes vacíos**
**Síntoma**: No aparecen planes aunque existen
**Causa**: Backend filtra automáticamente por paciente
**Solución**: Verificar que los planes estén asignados al paciente correcto

### **Error 2: Progreso incorrecto**
**Síntoma**: Barra de progreso no coincide
**Causa**: Backend no calcula `progreso_porcentaje` correctamente
**Solución**: Verificar cálculo en serializer del backend

### **Error 3: Estado no reconocido**
**Síntoma**: Badge sin color o con error
**Causa**: Estado no está en los configs
**Solución**: Agregar nuevo estado a `getEstadoConfig()`

---

## 🔄 Siguiente Paso

✅ Ver lista de planes completado → Continuar con **`11_ver_detalle_plan.md`** (Detalle completo con items)
