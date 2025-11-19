# 04 - Ver Mis Citas (Paciente)

## 🎯 Objetivo
Implementar la página donde el paciente puede ver todas sus citas médicas, con filtros por estado y ordenamiento cronológico.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Dashboard funcional (Guía 02)
- ✅ Servicio de citas ya creado en Dashboard (reutilizar)

---

## 🔌 Endpoint del Backend

### **GET** `/tenant/api/agenda/citas/`
Lista las citas del paciente autenticado

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado`: Filtrar por estado (PENDIENTE, CONFIRMADA, COMPLETADA, CANCELADA, NO_ASISTIO)
- `fecha_desde`: Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta`: Filtrar hasta fecha (YYYY-MM-DD)
- `page`: Número de página (paginación automática)

**Response 200:**
```json
{
  "count": 15,
  "next": "http://...?page=2",
  "previous": null,
  "results": [
    {
      "id": 45,
      "fecha_hora": "2025-11-18T10:00:00-05:00",
      "duracion_minutos": 60,
      "estado": "CONFIRMADA",
      "motivo": "Control de ortodoncia",
      "observaciones": "Traer radiografías previas",
      "odontologo": {
        "id": 5,
        "nombre": "Carlos",
        "apellido": "López",
        "full_name": "Dr. Carlos López",
        "especialidad": "Ortodoncia"
      },
      "paciente": {
        "id": 104,
        "full_name": "María García"
      },
      "creado": "2025-11-10T14:30:00-05:00",
      "modificado": "2025-11-10T14:30:00-05:00"
    }
  ]
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Citas.tsx               ← Nuevo (página principal)
│       └── components/
│           ├── CitaCard.tsx        ← Nuevo (tarjeta de cita)
│           └── CitasFiltros.tsx    ← Nuevo (filtros)
```

**Nota:** El servicio `citasService.ts` ya fue creado en la Guía 02, lo reutilizaremos.

---

## 💻 Código Paso a Paso

### **Paso 1: Componente CitaCard**

**Archivo:** `src/pages/paciente/components/CitaCard.tsx`

```typescript
import type { Cita } from '../../../types/citas.types';

interface CitaCardProps {
  cita: Cita;
  onClick?: () => void;
}

const CitaCard = ({ cita, onClick }: CitaCardProps) => {
  const formatearFecha = (fechaISO: string) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-ES', {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatearHora = (fechaISO: string) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'CONFIRMADA': return { bg: '#d1fae5', text: '#065f46', border: '#6ee7b7' };
      case 'PENDIENTE': return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
      case 'EN_CURSO': return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
      case 'COMPLETADA': return { bg: '#e0e7ff', text: '#3730a3', border: '#a5b4fc' };
      case 'CANCELADA': return { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' };
      case 'NO_ASISTIO': return { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
      default: return { bg: '#f3f4f6', text: '#6b7280', border: '#d1d5db' };
    }
  };

  const getEstadoTexto = (estado: string) => {
    switch (estado) {
      case 'CONFIRMADA': return 'Confirmada';
      case 'PENDIENTE': return 'Pendiente';
      case 'EN_CURSO': return 'En Curso';
      case 'COMPLETADA': return 'Completada';
      case 'CANCELADA': return 'Cancelada';
      case 'NO_ASISTIO': return 'No Asistió';
      default: return estado;
    }
  };

  const estadoColors = getEstadoColor(cita.estado);
  const esFutura = new Date(cita.fecha_hora) > new Date();
  const esCancelable = esFutura && ['PENDIENTE', 'CONFIRMADA'].includes(cita.estado);

  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '20px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        display: 'flex',
        gap: '20px'
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.borderColor = '#3b82f6';
          e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = '#e5e7eb';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Fecha Visual */}
      <div style={{
        backgroundColor: '#f3f4f6',
        borderRadius: '8px',
        padding: '16px',
        textAlign: 'center',
        minWidth: '90px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <div style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#111827',
          lineHeight: '1'
        }}>
          {new Date(cita.fecha_hora).getDate()}
        </div>
        <div style={{
          fontSize: '14px',
          color: '#6b7280',
          marginTop: '4px',
          fontWeight: '500'
        }}>
          {new Date(cita.fecha_hora).toLocaleDateString('es-ES', {
            month: 'short'
          }).toUpperCase()}
        </div>
      </div>

      {/* Contenido */}
      <div style={{ flex: 1 }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '12px',
          gap: '12px'
        }}>
          <div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>
              {formatearHora(cita.fecha_hora)}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {formatearFecha(cita.fecha_hora)}
            </p>
          </div>

          <span style={{
            fontSize: '13px',
            padding: '6px 12px',
            borderRadius: '6px',
            backgroundColor: estadoColors.bg,
            color: estadoColors.text,
            border: `1px solid ${estadoColors.border}`,
            fontWeight: '600',
            whiteSpace: 'nowrap'
          }}>
            {getEstadoTexto(cita.estado)}
          </span>
        </div>

        {/* Motivo */}
        <p style={{
          fontSize: '15px',
          color: '#111827',
          margin: '0 0 12px 0',
          fontWeight: '500'
        }}>
          {cita.motivo}
        </p>

        {/* Detalles */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            color: '#6b7280'
          }}>
            <span>👨‍⚕️</span>
            <span>{cita.odontologo.full_name}</span>
            {cita.odontologo.especialidad && (
              <span style={{
                fontSize: '12px',
                padding: '2px 6px',
                backgroundColor: '#f3f4f6',
                borderRadius: '4px'
              }}>
                {cita.odontologo.especialidad}
              </span>
            )}
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            color: '#6b7280'
          }}>
            <span>⏱️</span>
            <span>Duración: {cita.duracion_minutos} minutos</span>
          </div>

          {cita.observaciones && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px',
              fontSize: '14px',
              color: '#6b7280',
              marginTop: '4px'
            }}>
              <span>📝</span>
              <span>{cita.observaciones}</span>
            </div>
          )}
        </div>

        {/* Indicador de acción disponible */}
        {esCancelable && (
          <div style={{
            marginTop: '12px',
            fontSize: '13px',
            color: '#3b82f6',
            fontWeight: '500'
          }}>
            Click para ver opciones →
          </div>
        )}
      </div>
    </div>
  );
};

export default CitaCard;
```

---

### **Paso 2: Componente CitasFiltros**

**Archivo:** `src/pages/paciente/components/CitasFiltros.tsx`

```typescript
import type { EstadoCita } from '../../../types/citas.types';

interface CitasFiltrosProps {
  estadoSeleccionado: EstadoCita | 'TODAS';
  onEstadoChange: (estado: EstadoCita | 'TODAS') => void;
}

const CitasFiltros = ({ estadoSeleccionado, onEstadoChange }: CitasFiltrosProps) => {
  const estados: Array<{ valor: EstadoCita | 'TODAS'; texto: string; emoji: string }> = [
    { valor: 'TODAS', texto: 'Todas', emoji: '📋' },
    { valor: 'PENDIENTE', texto: 'Pendientes', emoji: '⏳' },
    { valor: 'CONFIRMADA', texto: 'Confirmadas', emoji: '✅' },
    { valor: 'COMPLETADA', texto: 'Completadas', emoji: '✓' },
    { valor: 'CANCELADA', texto: 'Canceladas', emoji: '❌' },
  ];

  return (
    <div style={{
      display: 'flex',
      gap: '8px',
      flexWrap: 'wrap',
      padding: '16px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      marginBottom: '20px'
    }}>
      <label style={{
        fontSize: '14px',
        fontWeight: '600',
        color: '#374151',
        display: 'flex',
        alignItems: 'center',
        marginRight: '12px'
      }}>
        Filtrar por:
      </label>

      {estados.map((estado) => (
        <button
          key={estado.valor}
          onClick={() => onEstadoChange(estado.valor)}
          style={{
            padding: '8px 16px',
            backgroundColor: estadoSeleccionado === estado.valor ? '#3b82f6' : 'white',
            color: estadoSeleccionado === estado.valor ? 'white' : '#374151',
            border: `1px solid ${estadoSeleccionado === estado.valor ? '#3b82f6' : '#d1d5db'}`,
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
          onMouseEnter={(e) => {
            if (estadoSeleccionado !== estado.valor) {
              e.currentTarget.style.backgroundColor = '#f3f4f6';
            }
          }}
          onMouseLeave={(e) => {
            if (estadoSeleccionado !== estado.valor) {
              e.currentTarget.style.backgroundColor = 'white';
            }
          }}
        >
          <span>{estado.emoji}</span>
          <span>{estado.texto}</span>
        </button>
      ))}
    </div>
  );
};

export default CitasFiltros;
```

---

### **Paso 3: Página Principal de Citas**

**Archivo:** `src/pages/paciente/Citas.tsx`

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import citasService from '../../services/citasService';
import type { Cita, EstadoCita, MisCitasParams } from '../../types/citas.types';
import CitaCard from './components/CitaCard';
import CitasFiltros from './components/CitasFiltros';

const Citas = () => {
  const navigate = useNavigate();
  const [citas, setCitas] = useState<Cita[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [estadoFiltro, setEstadoFiltro] = useState<EstadoCita | 'TODAS'>('TODAS');
  const [totalCitas, setTotalCitas] = useState(0);

  useEffect(() => {
    cargarCitas();
  }, [estadoFiltro]);

  const cargarCitas = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: MisCitasParams = {
        limit: 50 // Mostrar hasta 50 citas
      };

      // Agregar filtro de estado si no es "TODAS"
      if (estadoFiltro !== 'TODAS') {
        params.estado = estadoFiltro;
      }

      const response = await citasService.getMisCitas(params);
      setCitas(response.results);
      setTotalCitas(response.count);

    } catch (err: any) {
      console.error('Error cargando citas:', err);

      if (err.response?.status === 401) {
        navigate('/paciente/login');
      } else {
        setError('No se pudieron cargar las citas');
      }

    } finally {
      setLoading(false);
    }
  };

  const handleCitaClick = (cita: Cita) => {
    console.log('Cita seleccionada:', cita);
    // TODO: Navegar a detalle de cita o mostrar modal
    // navigate(`/paciente/citas/${cita.id}`);
  };

  const ordenarCitasPorFecha = (citasArray: Cita[]) => {
    return [...citasArray].sort((a, b) => {
      const fechaA = new Date(a.fecha_hora).getTime();
      const fechaB = new Date(b.fecha_hora).getTime();
      return fechaB - fechaA; // Más recientes primero
    });
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
            ⏳ Cargando citas...
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
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <button
              onClick={() => navigate('/paciente/dashboard')}
              style={{
                padding: '8px 12px',
                backgroundColor: '#f3f4f6',
                color: '#374151',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            >
              ← Volver
            </button>

            <div>
              <h1 style={{
                fontSize: '20px',
                fontWeight: '700',
                color: '#111827',
                margin: 0
              }}>
                📅 Mis Citas
              </h1>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                {totalCitas} {totalCitas === 1 ? 'cita' : 'citas'} en total
              </p>
            </div>
          </div>

          <button
            onClick={() => navigate('/paciente/citas/solicitar')}
            style={{
              padding: '10px 20px',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#059669'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
          >
            <span>➕</span>
            <span>Solicitar Cita</span>
          </button>
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
            <p style={{
              fontSize: '14px',
              color: '#991b1b',
              margin: 0
            }}>
              ⚠️ {error}
            </p>
          </div>
        )}

        {/* Filtros */}
        <CitasFiltros
          estadoSeleccionado={estadoFiltro}
          onEstadoChange={setEstadoFiltro}
        />

        {/* Lista de Citas */}
        {citas.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '60px 20px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '8px'
            }}>
              No hay citas {estadoFiltro !== 'TODAS' && `en estado "${estadoFiltro.toLowerCase()}"`}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              marginBottom: '20px'
            }}>
              {estadoFiltro === 'TODAS'
                ? 'Solicita tu primera cita para comenzar'
                : 'Intenta cambiar el filtro o solicita una nueva cita'}
            </p>
            <button
              onClick={() => navigate('/paciente/citas/solicitar')}
              style={{
                padding: '10px 20px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              ➕ Solicitar Cita
            </button>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            {ordenarCitasPorFecha(citas).map((cita) => (
              <CitaCard
                key={cita.id}
                cita={cita}
                onClick={() => handleCitaClick(cita)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Citas;
```

---

### **Paso 4: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import CitasPaciente from './pages/paciente/Citas'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        <Route path="/paciente/perfil" element={<PerfilPaciente />} />
        <Route path="/paciente/citas" element={<CitasPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### **Paso 5: Actualizar componente AccesosRapidos (Dashboard)**

En el Dashboard (Guía 02), el botón de "Mis Citas" debe navegar a `/paciente/citas`:

```typescript
{
  id: 1,
  titulo: 'Mis Citas',
  descripcion: 'Ver y gestionar citas',
  icono: '📅',
  url: '/paciente/citas', // ← Verificar esta URL
  color: '#3b82f6'
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Todas las Citas**
1. Login con `paciente1@test.com` / `paciente123`
2. Navegar a "Mis Citas"
3. **Esperado**:
   - Lista de todas las citas del paciente
   - Ordenadas por fecha (más recientes primero)
   - Badge de estado visible en cada cita
   - Botón "Solicitar Cita" en header
4. **Verificar consola**: Logs de carga exitosa

### **Caso 2: Filtrar por Estado**
1. Click en filtro "Pendientes"
2. **Esperado**: Solo citas con estado PENDIENTE
3. Click en "Confirmadas"
4. **Esperado**: Solo citas CONFIRMADA
5. Click en "Todas"
6. **Esperado**: Todas las citas de nuevo

### **Caso 3: Sin Citas**
1. Login con paciente que no tiene citas
2. **Esperado**:
   - Mensaje "No hay citas"
   - Icono 📭
   - Botón para solicitar cita

### **Caso 4: Click en Cita**
1. Click en cualquier tarjeta de cita
2. **Esperado**: Log en consola con info de la cita
3. (Placeholder para futura navegación a detalle)

---

## ✅ Checklist de Verificación

- [ ] Página de citas carga correctamente
- [ ] Citas se muestran en tarjetas
- [ ] Filtros funcionan correctamente
- [ ] Estado de cada cita es visible
- [ ] Ordenamiento por fecha funciona
- [ ] Contador de citas es correcto
- [ ] Botón "Volver" funciona
- [ ] Botón "Solicitar Cita" navega (placeholder)
- [ ] Click en cita muestra log
- [ ] Vista vacía funciona
- [ ] Estados de loading se muestran
- [ ] Manejo de errores funciona
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: Citas no se cargan**
**Síntoma**: Lista vacía siempre
**Causa**: Endpoint incorrecto o filtro muy restrictivo
**Solución**: Verificar URL `/tenant/api/agenda/citas/` y remover filtros

### **Error 2: Fecha mal formateada**
**Síntoma**: Fecha muestra "Invalid Date"
**Causa**: Timezone o formato ISO incorrecto
**Solución**: Usar `new Date(fechaISO)` directamente

### **Error 3: Filtro no funciona**
**Síntoma**: Al cambiar filtro, no se actualizan las citas
**Causa**: `useEffect` no tiene `estadoFiltro` en dependencias
**Solución**: Verificar `useEffect([estadoFiltro])`

---

## 🔄 Siguiente Paso

✅ Ver citas completado → Continuar con **`05_solicitar_cita.md`** (Crear nueva cita)
