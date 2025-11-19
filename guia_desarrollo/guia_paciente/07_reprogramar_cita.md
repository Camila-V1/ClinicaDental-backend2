# 07 - Reprogramar Cita

## 🎯 Objetivo
Implementar la funcionalidad para que el paciente pueda modificar la fecha/hora de una cita PENDIENTE o CONFIRMADA, manteniendo el mismo odontólogo y motivo.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver citas funcional (Guía 04)
- ✅ Servicio de citas existe (citasService.ts)

---

## 🔌 Endpoints del Backend

### **PATCH** `/tenant/api/agenda/citas/{id}/`
Actualiza parcialmente una cita (usado para cambiar fecha/hora)

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Path Parameters:**
- `id` (int): ID de la cita a reprogramar

**Request Body:**
```json
{
  "fecha_hora": "2025-11-25T14:00:00-05:00"
}
```

**Campos permitidos para actualizar:**
- `fecha_hora` (datetime, opcional): Nueva fecha y hora
- `odontologo` (int, opcional): Cambiar odontólogo
- `motivo` (string, opcional): Cambiar motivo
- `observaciones` (string, opcional): Cambiar observaciones

**Response 200:**
```json
{
  "id": 50,
  "paciente": 3,
  "paciente_nombre": "María García",
  "odontologo": 5,
  "odontologo_nombre": "Dr. Carlos López",
  "odontologo_especialidad": "Ortodoncia",
  "fecha_hora": "2025-11-25T14:00:00-05:00",
  "motivo_tipo": "CONSULTA",
  "motivo": "Dolor en muela del juicio",
  "estado": "PENDIENTE",
  "precio": "0.00",
  "actualizado": "2025-11-15T17:00:00-05:00"
}
```

**Response 400:**
```json
{
  "fecha_hora": ["La fecha debe ser futura"]
}
```

**Response 403:**
```json
{
  "detail": "No tiene permiso para realizar esta acción."
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Citas.tsx                     ← Modificar (agregar botón reprogramar)
│       └── ReprogramarCita.tsx           ← Nuevo
├── components/
│   └── paciente/
│       └── CitaCard.tsx                  ← Agregar botón reprogramar
└── services/
    └── citasService.ts                   ← Agregar método actualizar
```

---

## 💻 Código Paso a Paso

### **Paso 1: Extender servicio de Citas**

**Archivo:** `src/services/citasService.ts` (agregar al objeto existente)

```typescript
// ... métodos existentes ...

/**
 * Actualizar (reprogramar) una cita
 */
async actualizarCita(
  citaId: number,
  data: Partial<CrearCitaData>
): Promise<Cita> {
  console.group('✏️ [citasService] actualizarCita');
  console.log('ID de cita:', citaId);
  console.log('Datos a actualizar:', data);
  
  try {
    const response = await apiClient.patch<Cita>(
      `/tenant/api/agenda/citas/${citaId}/`,
      data
    );
    
    console.log('✅ Cita actualizada exitosamente');
    console.log('Nueva fecha:', response.data.fecha_hora);
    console.groupEnd();
    
    return response.data;
    
  } catch (error: any) {
    console.error('❌ Error actualizando cita:', error);
    console.error('Response:', error.response?.data);
    console.groupEnd();
    throw error;
  }
}
```

---

### **Paso 2: Página ReprogramarCita**

**Archivo:** `src/pages/paciente/ReprogramarCita.tsx` (nuevo)

```typescript
import { useEffect, useState, FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import citasService from '../../services/citasService';
import type { Cita } from '../../types/citas.types';

const ReprogramarCita = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  // Estados
  const [cita, setCita] = useState<Cita | null>(null);
  const [nuevaFechaHora, setNuevaFechaHora] = useState('');
  const [loading, setLoading] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorFecha, setErrorFecha] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      cargarCita(Number(id));
    } else {
      setError('ID de cita no válido');
      setLoading(false);
    }
  }, [id]);

  const cargarCita = async (citaId: number) => {
    try {
      setLoading(true);
      setError(null);

      const citasData = await citasService.getMisCitas();
      const citaEncontrada = citasData.find(c => c.id === citaId);

      if (!citaEncontrada) {
        setError('Cita no encontrada');
        return;
      }

      // Verificar que la cita puede ser reprogramada
      if (citaEncontrada.estado === 'ATENDIDA') {
        setError('No se puede reprogramar una cita ya atendida');
        return;
      }

      if (citaEncontrada.estado === 'CANCELADA') {
        setError('No se puede reprogramar una cita cancelada');
        return;
      }

      setCita(citaEncontrada);

      // Inicializar fecha/hora actual de la cita
      const fechaActual = new Date(citaEncontrada.fecha_hora);
      const fechaFormatted = fechaActual.toISOString().slice(0, 16);
      setNuevaFechaHora(fechaFormatted);

    } catch (err: any) {
      console.error('Error cargando cita:', err);
      setError('No se pudo cargar la cita');

    } finally {
      setLoading(false);
    }
  };

  const getMinDateTime = (): string => {
    const ahora = new Date();
    ahora.setHours(ahora.getHours() + 1);
    return ahora.toISOString().slice(0, 16);
  };

  const validarFecha = (): boolean => {
    if (!nuevaFechaHora) {
      setErrorFecha('La fecha y hora son requeridas');
      return false;
    }

    const fechaSeleccionada = new Date(nuevaFechaHora);
    const ahora = new Date();

    if (fechaSeleccionada <= ahora) {
      setErrorFecha('La fecha debe ser futura');
      return false;
    }

    // Verificar que sea diferente a la fecha actual
    if (cita && nuevaFechaHora === new Date(cita.fecha_hora).toISOString().slice(0, 16)) {
      setErrorFecha('Debes seleccionar una fecha diferente');
      return false;
    }

    setErrorFecha(null);
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!cita) return;

    console.group('🔄 Reprogramar Cita');
    console.log('ID de cita:', cita.id);
    console.log('Fecha actual:', cita.fecha_hora);
    console.log('Nueva fecha:', nuevaFechaHora);

    if (!validarFecha()) {
      console.warn('⚠️ Validación de fecha falló');
      console.groupEnd();
      return;
    }

    setGuardando(true);
    setError(null);

    try {
      // Convertir a formato ISO completo con timezone
      const fechaISO = new Date(nuevaFechaHora).toISOString();

      const citaActualizada = await citasService.actualizarCita(cita.id, {
        fecha_hora: fechaISO
      } as any);

      console.log('✅ Cita reprogramada exitosamente');
      console.log('Nueva fecha confirmada:', citaActualizada.fecha_hora);
      console.groupEnd();

      alert(`✅ Cita reprogramada exitosamente!\n\nNueva fecha: ${new Date(citaActualizada.fecha_hora).toLocaleString('es-ES')}`);
      
      navigate('/paciente/citas');

    } catch (err: any) {
      console.error('❌ Error reprogramando cita');
      console.groupEnd();

      const errorData = err.response?.data;
      let errorMsg = 'Error al reprogramar la cita';

      if (errorData) {
        if (errorData.fecha_hora) {
          setErrorFecha(errorData.fecha_hora[0] || errorData.fecha_hora);
        } else if (typeof errorData === 'string') {
          errorMsg = errorData;
        } else if (typeof errorData === 'object') {
          errorMsg = Object.values(errorData).flat().join(', ');
        }
        setError(errorMsg);
      }

    } finally {
      setGuardando(false);
    }
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleString('es-ES', {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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
            ⏳ Cargando cita...
          </p>
        </div>
      </div>
    );
  }

  if (error && !cita) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <p style={{
            fontSize: '48px',
            margin: '0 0 16px 0'
          }}>
            ⚠️
          </p>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 8px 0'
          }}>
            Error
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            marginBottom: '20px'
          }}>
            {error}
          </p>
          <button
            onClick={() => navigate('/paciente/citas')}
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
            Volver a Mis Citas
          </button>
        </div>
      </div>
    );
  }

  if (!cita) return null;

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
          gap: '16px',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <button
            onClick={() => navigate('/paciente/citas')}
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
              🔄 Reprogramar Cita
            </h1>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: '4px 0 0 0'
            }}>
              Selecciona una nueva fecha y hora
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Error Global */}
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

        {/* Información Actual de la Cita */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          padding: '24px',
          marginBottom: '20px'
        }}>
          <h2 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 16px 0'
          }}>
            📋 Información Actual
          </h2>

          <div style={{
            display: 'grid',
            gap: '16px'
          }}>
            {/* Fecha Actual */}
            <div style={{
              padding: '12px',
              backgroundColor: '#fef3c7',
              border: '1px solid #fde68a',
              borderRadius: '6px'
            }}>
              <p style={{
                fontSize: '12px',
                color: '#78350f',
                margin: '0 0 4px 0',
                fontWeight: '600'
              }}>
                📅 FECHA Y HORA ACTUAL
              </p>
              <p style={{
                fontSize: '14px',
                color: '#78350f',
                margin: 0,
                fontWeight: '700'
              }}>
                {formatearFecha(cita.fecha_hora)}
              </p>
            </div>

            {/* Odontólogo */}
            {cita.odontologo_nombre && (
              <div>
                <p style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  margin: '0 0 4px 0',
                  fontWeight: '600'
                }}>
                  👨‍⚕️ ODONTÓLOGO
                </p>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {cita.odontologo_nombre}
                  {cita.odontologo_especialidad && (
                    <span style={{ color: '#6b7280' }}>
                      {' '}- {cita.odontologo_especialidad}
                    </span>
                  )}
                </p>
              </div>
            )}

            {/* Motivo */}
            <div>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '0 0 4px 0',
                fontWeight: '600'
              }}>
                🦷 MOTIVO
              </p>
              <p style={{
                fontSize: '14px',
                color: '#111827',
                margin: 0
              }}>
                {cita.motivo || 'Sin especificar'}
              </p>
            </div>
          </div>
        </div>

        {/* Formulario de Reprogramación */}
        <form onSubmit={handleSubmit}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            padding: '24px'
          }}>
            <h2 style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 16px 0'
            }}>
              📅 Nueva Fecha y Hora
            </h2>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Selecciona la nueva fecha y hora <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="datetime-local"
                value={nuevaFechaHora}
                onChange={(e) => {
                  setNuevaFechaHora(e.target.value);
                  setErrorFecha(null);
                }}
                min={getMinDateTime()}
                disabled={guardando}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: `1px solid ${errorFecha ? '#ef4444' : '#d1d5db'}`,
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              {errorFecha && (
                <p style={{
                  fontSize: '12px',
                  color: '#ef4444',
                  margin: '4px 0 0 0'
                }}>
                  {errorFecha}
                </p>
              )}
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                Selecciona una fecha y hora futura
              </p>
            </div>

            {/* Nota Informativa */}
            <div style={{
              padding: '16px',
              backgroundColor: '#eff6ff',
              border: '1px solid #bfdbfe',
              borderRadius: '8px',
              marginBottom: '24px'
            }}>
              <p style={{
                fontSize: '14px',
                color: '#1e40af',
                margin: 0,
                lineHeight: '1.5'
              }}>
                ℹ️ <strong>Nota:</strong> Solo cambiarás la fecha y hora. El odontólogo y motivo se mantendrán igual. Si la cita estaba CONFIRMADA, volverá a estado PENDIENTE hasta que la clínica confirme la nueva fecha.
              </p>
            </div>

            {/* Botones */}
            <div style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-end'
            }}>
              <button
                type="button"
                onClick={() => navigate('/paciente/citas')}
                disabled={guardando}
                style={{
                  padding: '12px 24px',
                  backgroundColor: 'white',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: guardando ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!guardando) e.currentTarget.style.backgroundColor = '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                }}
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={guardando}
                style={{
                  padding: '12px 24px',
                  backgroundColor: guardando ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: guardando ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!guardando) e.currentTarget.style.backgroundColor = '#2563eb';
                }}
                onMouseLeave={(e) => {
                  if (!guardando) e.currentTarget.style.backgroundColor = '#3b82f6';
                }}
              >
                {guardando ? '⏳ Guardando...' : '✓ Reprogramar Cita'}
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};

export default ReprogramarCita;
```

---

### **Paso 3: Modificar CitaCard con botón de reprogramar**

**Archivo:** `src/components/paciente/CitaCard.tsx` (modificar)

```typescript
import { useNavigate } from 'react-router-dom'; // ← AGREGAR
import type { Cita } from '../../types/citas.types';

interface CitaCardProps {
  cita: Cita;
  onCancelar?: (cita: Cita) => void;
}

const CitaCard = ({ cita, onCancelar }: CitaCardProps) => {
  const navigate = useNavigate(); // ← AGREGAR
  
  // ... resto del código existente ...

  const puedeSerCancelada = (): boolean => {
    return cita.estado === 'PENDIENTE' || cita.estado === 'CONFIRMADA';
  };

  // NUEVO: Verificar si puede ser reprogramada
  const puedeSerReprogramada = (): boolean => {
    return cita.estado === 'PENDIENTE' || cita.estado === 'CONFIRMADA';
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '16px',
      border: '1px solid #e5e7eb',
      transition: 'box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.boxShadow = 'none';
    }}
    >
      {/* ... código existente del header, odontólogo, motivo ... */}

      {/* Botones de acción - MODIFICADO */}
      {(puedeSerReprogramada() || puedeSerCancelada()) && (
        <div style={{
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #e5e7eb',
          display: 'flex',
          gap: '8px'
        }}>
          {/* Botón Reprogramar - NUEVO */}
          {puedeSerReprogramada() && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/paciente/citas/${cita.id}/reprogramar`);
              }}
              style={{
                flex: 1,
                padding: '8px 16px',
                backgroundColor: '#dbeafe',
                color: '#1e40af',
                border: '1px solid #93c5fd',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#bfdbfe';
                e.currentTarget.style.borderColor = '#60a5fa';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#dbeafe';
                e.currentTarget.style.borderColor = '#93c5fd';
              }}
            >
              🔄 Reprogramar
            </button>
          )}

          {/* Botón Cancelar - EXISTENTE */}
          {puedeSerCancelada() && onCancelar && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onCancelar(cita);
              }}
              style={{
                flex: 1,
                padding: '8px 16px',
                backgroundColor: '#fee2e2',
                color: '#991b1b',
                border: '1px solid #fecaca',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#fecaca';
                e.currentTarget.style.borderColor = '#fca5a5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fee2e2';
                e.currentTarget.style.borderColor = '#fecaca';
              }}
            >
              ✗ Cancelar
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default CitaCard;
```

---

### **Paso 4: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import ReprogramarCitaPaciente from './pages/paciente/ReprogramarCita'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        <Route path="/paciente/perfil" element={<PerfilPaciente />} />
        <Route path="/paciente/citas" element={<CitasPaciente />} />
        <Route path="/paciente/citas/solicitar" element={<SolicitarCitaPaciente />} />
        <Route path="/paciente/citas/:id/reprogramar" element={<ReprogramarCitaPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Reprogramar Cita Exitosamente**
1. Login con `paciente1@test.com` / `paciente123`
2. Ir a "Mis Citas"
3. Buscar cita con estado PENDIENTE o CONFIRMADA
4. Click "🔄 Reprogramar"
5. Ver información actual de la cita
6. Cambiar fecha y hora (debe ser futura)
7. Click "Reprogramar Cita"
8. **Esperado**:
   - Alert de confirmación
   - Redirección a lista de citas
   - Cita muestra nueva fecha/hora

### **Caso 2: Validación de Fecha Futura**
1. Entrar a reprogramar cita
2. Seleccionar fecha/hora pasada
3. Click "Reprogramar Cita"
4. **Esperado**: Error "La fecha debe ser futura"

### **Caso 3: Fecha Igual a la Actual**
1. Entrar a reprogramar cita
2. Dejar la misma fecha/hora
3. Click "Reprogramar Cita"
4. **Esperado**: Error "Debes seleccionar una fecha diferente"

### **Caso 4: Cancelar Reprogramación**
1. Entrar a reprogramar cita
2. Cambiar fecha
3. Click "Cancelar"
4. **Esperado**: Volver a lista sin cambios

### **Caso 5: Cita No Reprogramable (ATENDIDA)**
1. Intentar acceder a `/paciente/citas/{id}/reprogramar` con ID de cita ATENDIDA
2. **Esperado**: Mensaje "No se puede reprogramar una cita ya atendida"

### **Caso 6: Cita No Reprogramable (CANCELADA)**
1. Intentar acceder con ID de cita CANCELADA
2. **Esperado**: Mensaje "No se puede reprogramar una cita cancelada"

### **Caso 7: ID Inválido**
1. Acceder a `/paciente/citas/99999/reprogramar`
2. **Esperado**: Mensaje "Cita no encontrada"

---

## ✅ Checklist de Verificación

- [ ] Botón "Reprogramar" aparece solo en citas PENDIENTE/CONFIRMADA
- [ ] Click en botón navega a página de reprogramación
- [ ] Página carga información correcta de la cita
- [ ] Fecha/hora actual se muestra resaltada
- [ ] Input de fecha/hora funciona
- [ ] Validación de fecha futura funciona
- [ ] Validación de fecha diferente funciona
- [ ] Botón "Reprogramar" actualiza la cita
- [ ] Alert de éxito se muestra
- [ ] Redirección a lista funciona
- [ ] Cita muestra nueva fecha en la lista
- [ ] Botón "Cancelar" vuelve sin cambios
- [ ] Citas ATENDIDA no permiten reprogramación
- [ ] Citas CANCELADA no permiten reprogramación
- [ ] Console logs funcionan correctamente
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: "No tiene permiso para realizar esta acción"**
**Síntoma**: Error 403 del backend
**Causa**: Intentar reprogramar cita de otro paciente
**Solución**: Backend valida automáticamente que la cita pertenezca al usuario

### **Error 2: Fecha no se actualiza en la lista**
**Síntoma**: Cita reprogramada pero lista muestra fecha antigua
**Causa**: Lista no se recarga después de actualizar
**Solución**: La redirección hace que el componente Citas se recargue

### **Error 3: Input datetime-local no funciona**
**Síntoma**: No se puede seleccionar fecha
**Causa**: Formato de fecha inicial incorrecto
**Solución**: Usar `.toISOString().slice(0, 16)` para formato correcto

### **Error 4: Timezone inconsistente**
**Síntoma**: Hora guardada diferente a la seleccionada
**Causa**: Conversión de timezone incorrecta
**Solución**: Backend debe manejar timezone correctamente

---

## 💡 Notas Importantes

### **Diferencia entre Reprogramar y Editar**
- **Reprogramar**: Solo cambia fecha/hora, mantiene odontólogo y motivo
- **Editar completo**: Cambiaría todos los campos (no implementado en este módulo)

### **Estado después de Reprogramar**
El backend puede:
- Mantener el estado actual (PENDIENTE/CONFIRMADA)
- O resetear a PENDIENTE si una cita CONFIRMADA cambia de fecha

Verificar la lógica del backend para ajustar mensajes.

---

## 🔄 Siguiente Paso

✅ Reprogramar cita completado → ✅ **Fase 2 (Citas) completada!**

Continuar con **`08_ver_historial_clinico.md`** (Inicio de Fase 3 - Historial Clínico)
