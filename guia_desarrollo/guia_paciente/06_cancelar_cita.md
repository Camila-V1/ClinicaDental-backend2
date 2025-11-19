# 06 - Cancelar Cita

## 🎯 Objetivo
Implementar la funcionalidad para que el paciente pueda cancelar sus citas que aún no han sido atendidas, con confirmación previa y restricciones de seguridad.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver citas funcional (Guía 04)
- ✅ Servicio de citas existe (citasService.ts)

---

## 🔌 Endpoints del Backend

### **POST** `/tenant/api/agenda/citas/{id}/cancelar/`
Cancela una cita específica

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Path Parameters:**
- `id` (int): ID de la cita a cancelar

**Request Body:**
```json
{}
```
*No requiere body, solo autenticación*

**Response 200:**
```json
{
  "message": "Cita cancelada exitosamente.",
  "cita": {
    "id": 50,
    "paciente": 3,
    "paciente_nombre": "María García",
    "odontologo": 5,
    "odontologo_nombre": "Dr. Carlos López",
    "fecha_hora": "2025-11-20T10:00:00-05:00",
    "motivo_tipo": "CONSULTA",
    "motivo": "Dolor en muela del juicio",
    "estado": "CANCELADA",
    "creado": "2025-11-15T16:30:00-05:00"
  }
}
```

**Response 400 (Ya cancelada):**
```json
{
  "error": "La cita ya está cancelada."
}
```

**Response 400 (Ya atendida):**
```json
{
  "error": "No se puede cancelar una cita ya atendida."
}
```

**Response 404:**
```json
{
  "detail": "No encontrada."
}
```

---

## 🧩 Componentes a Modificar

```
src/
├── pages/
│   └── paciente/
│       └── Citas.tsx                 ← Agregar botón de cancelar
├── components/
│   └── paciente/
│       ├── CitaCard.tsx              ← Agregar botón de cancelar
│       └── ModalConfirmarCancelar.tsx ← Nuevo
└── services/
    └── citasService.ts               ← Agregar método cancelar
```

---

## 💻 Código Paso a Paso

### **Paso 1: Extender servicio de Citas**

**Archivo:** `src/services/citasService.ts` (agregar al objeto existente)

```typescript
// ... métodos existentes ...

/**
 * Cancelar una cita
 */
async cancelarCita(citaId: number): Promise<{ message: string; cita: Cita }> {
  console.group('❌ [citasService] cancelarCita');
  console.log('ID de cita:', citaId);
  
  try {
    const response = await apiClient.post<{ message: string; cita: Cita }>(
      `/tenant/api/agenda/citas/${citaId}/cancelar/`
    );
    
    console.log('✅ Cita cancelada exitosamente');
    console.log('Nuevo estado:', response.data.cita.estado);
    console.groupEnd();
    
    return response.data;
    
  } catch (error: any) {
    console.error('❌ Error cancelando cita:', error);
    console.error('Response:', error.response?.data);
    console.groupEnd();
    throw error;
  }
}
```

---

### **Paso 2: Componente Modal de Confirmación**

**Archivo:** `src/components/paciente/ModalConfirmarCancelar.tsx` (nuevo)

```typescript
import type { Cita } from '../../types/citas.types';

interface ModalConfirmarCancelarProps {
  cita: Cita;
  onConfirmar: () => void;
  onCancelar: () => void;
  loading?: boolean;
}

const ModalConfirmarCancelar = ({
  cita,
  onConfirmar,
  onCancelar,
  loading = false
}: ModalConfirmarCancelarProps) => {
  
  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Overlay */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}
        onClick={loading ? undefined : onCancelar}
      >
        {/* Modal */}
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '100%',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{
            padding: '24px',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: '#fee2e2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px'
              }}>
                ⚠️
              </div>
              <div>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  Confirmar Cancelación
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: '4px 0 0 0'
                }}>
                  Esta acción no se puede deshacer
                </p>
              </div>
            </div>
          </div>

          {/* Body */}
          <div style={{ padding: '24px' }}>
            <p style={{
              fontSize: '14px',
              color: '#374151',
              marginBottom: '16px',
              lineHeight: '1.5'
            }}>
              ¿Estás seguro que deseas cancelar la siguiente cita?
            </p>

            {/* Información de la Cita */}
            <div style={{
              backgroundColor: '#f9fafb',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <div style={{ marginBottom: '12px' }}>
                <p style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  margin: '0 0 4px 0',
                  fontWeight: '600'
                }}>
                  📅 FECHA Y HORA
                </p>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {formatearFecha(cita.fecha_hora)}
                </p>
              </div>

              {cita.odontologo_nombre && (
                <div style={{ marginBottom: '12px' }}>
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

            {/* Advertencia */}
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: '#fff7ed',
              border: '1px solid #fed7aa',
              borderRadius: '6px'
            }}>
              <p style={{
                fontSize: '13px',
                color: '#92400e',
                margin: 0,
                lineHeight: '1.5'
              }}>
                💡 <strong>Nota:</strong> Si necesitas reagendar, cancela esta cita y luego solicita una nueva con la fecha deseada.
              </p>
            </div>
          </div>

          {/* Footer */}
          <div style={{
            padding: '16px 24px',
            backgroundColor: '#f9fafb',
            borderTop: '1px solid #e5e7eb',
            borderRadius: '0 0 12px 12px',
            display: 'flex',
            gap: '12px',
            justifyContent: 'flex-end'
          }}>
            <button
              type="button"
              onClick={onCancelar}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: 'white',
                color: '#374151',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#f3f4f6';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
              }}
            >
              No, mantener cita
            </button>

            <button
              type="button"
              onClick={onConfirmar}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#9ca3af' : '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#dc2626';
              }}
              onMouseLeave={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#ef4444';
              }}
            >
              {loading ? '⏳ Cancelando...' : 'Sí, cancelar cita'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default ModalConfirmarCancelar;
```

---

### **Paso 3: Modificar CitaCard con botón de cancelar**

**Archivo:** `src/components/paciente/CitaCard.tsx` (modificar)

```typescript
import type { Cita } from '../../types/citas.types';

interface CitaCardProps {
  cita: Cita;
  onCancelar?: (cita: Cita) => void; // ← NUEVO
}

const CitaCard = ({ cita, onCancelar }: CitaCardProps) => {
  const getEstadoColor = (estado: string): string => {
    const colores: Record<string, string> = {
      'PENDIENTE': '#fbbf24',
      'CONFIRMADA': '#10b981',
      'ATENDIDA': '#3b82f6',
      'CANCELADA': '#ef4444'
    };
    return colores[estado] || '#6b7280';
  };

  const getEstadoIcon = (estado: string): string => {
    const iconos: Record<string, string> = {
      'PENDIENTE': '🕐',
      'CONFIRMADA': '✓',
      'ATENDIDA': '✓✓',
      'CANCELADA': '✗'
    };
    return iconos[estado] || '•';
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleString('es-ES', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const puedeSerCancelada = (): boolean => {
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
      {/* Header con estado */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px'
      }}>
        <div>
          <h3 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 4px 0'
          }}>
            📅 {formatearFecha(cita.fecha_hora)}
          </h3>
          {cita.motivo_tipo_display && (
            <p style={{
              fontSize: '13px',
              color: '#6b7280',
              margin: 0
            }}>
              {cita.motivo_tipo_display}
            </p>
          )}
        </div>

        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: '4px 12px',
          backgroundColor: `${getEstadoColor(cita.estado)}20`,
          color: getEstadoColor(cita.estado),
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          {getEstadoIcon(cita.estado)} {cita.estado}
        </span>
      </div>

      {/* Odontólogo */}
      {cita.odontologo_nombre && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '14px' }}>👨‍⚕️</span>
          <div>
            <p style={{
              fontSize: '14px',
              color: '#374151',
              margin: 0
            }}>
              {cita.odontologo_nombre}
            </p>
            {cita.odontologo_especialidad && (
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: 0
              }}>
                {cita.odontologo_especialidad}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Motivo */}
      {cita.motivo && (
        <div style={{
          marginTop: '12px',
          padding: '12px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px'
        }}>
          <p style={{
            fontSize: '13px',
            color: '#6b7280',
            margin: '0 0 4px 0',
            fontWeight: '600'
          }}>
            Motivo:
          </p>
          <p style={{
            fontSize: '14px',
            color: '#374151',
            margin: 0,
            lineHeight: '1.4'
          }}>
            {cita.motivo}
          </p>
        </div>
      )}

      {/* Botón de cancelar - NUEVO */}
      {puedeSerCancelada() && onCancelar && (
        <div style={{
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #e5e7eb'
        }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onCancelar(cita);
            }}
            style={{
              width: '100%',
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
            ✗ Cancelar esta cita
          </button>
        </div>
      )}
    </div>
  );
};

export default CitaCard;
```

---

### **Paso 4: Modificar página Citas con lógica de cancelación**

**Archivo:** `src/pages/paciente/Citas.tsx` (modificar)

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import citasService from '../../services/citasService';
import CitaCard from '../../components/paciente/CitaCard';
import CitasFiltros from '../../components/paciente/CitasFiltros';
import ModalConfirmarCancelar from '../../components/paciente/ModalConfirmarCancelar'; // ← NUEVO
import type { Cita, EstadoCita } from '../../types/citas.types';

const Citas = () => {
  const navigate = useNavigate();

  const [citas, setCitas] = useState<Cita[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<EstadoCita | 'TODAS'>('TODAS');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados del modal de cancelación - NUEVO
  const [citaACancelar, setCitaACancelar] = useState<Cita | null>(null);
  const [cancelando, setCancelando] = useState(false);

  useEffect(() => {
    cargarCitas();
  }, []);

  const cargarCitas = async () => {
    try {
      setLoading(true);
      setError(null);

      const citasData = await citasService.getMisCitas();
      setCitas(citasData);

    } catch (err: any) {
      console.error('Error cargando citas:', err);
      setError('No se pudieron cargar las citas');

    } finally {
      setLoading(false);
    }
  };

  const citasFiltradas = citas.filter(cita => {
    if (filtroEstado === 'TODAS') return true;
    return cita.estado === filtroEstado;
  });

  // Ordenar por fecha descendente (más reciente primero)
  const citasOrdenadas = [...citasFiltradas].sort((a, b) => {
    return new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime();
  });

  // NUEVO: Abrir modal de confirmación
  const handleAbrirModalCancelar = (cita: Cita) => {
    console.log('Abriendo modal para cancelar cita:', cita.id);
    setCitaACancelar(cita);
  };

  // NUEVO: Cerrar modal
  const handleCerrarModal = () => {
    if (!cancelando) {
      setCitaACancelar(null);
    }
  };

  // NUEVO: Confirmar cancelación
  const handleConfirmarCancelar = async () => {
    if (!citaACancelar) return;

    console.group('❌ Cancelar Cita');
    console.log('ID:', citaACancelar.id);

    setCancelando(true);

    try {
      await citasService.cancelarCita(citaACancelar.id);

      console.log('✅ Cita cancelada exitosamente');
      console.groupEnd();

      // Actualizar la lista de citas
      setCitas(prevCitas => 
        prevCitas.map(cita => 
          cita.id === citaACancelar.id 
            ? { ...cita, estado: 'CANCELADA' as EstadoCita }
            : cita
        )
      );

      // Cerrar modal
      setCitaACancelar(null);

      // Mostrar mensaje de éxito
      alert('✅ Cita cancelada exitosamente');

    } catch (err: any) {
      console.error('❌ Error cancelando cita');
      console.groupEnd();

      const errorData = err.response?.data;
      let errorMsg = 'Error al cancelar la cita';

      if (errorData?.error) {
        errorMsg = errorData.error;
      }

      alert(`⚠️ ${errorMsg}`);

    } finally {
      setCancelando(false);
    }
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
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{
              fontSize: '24px',
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
              {citas.length} {citas.length === 1 ? 'cita' : 'citas'} en total
            </p>
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
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#059669'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
          >
            + Solicitar Cita
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
            <p style={{ fontSize: '14px', color: '#991b1b', margin: 0 }}>
              ⚠️ {error}
            </p>
          </div>
        )}

        {/* Filtros */}
        <CitasFiltros
          estadoActivo={filtroEstado}
          onChange={setFiltroEstado}
        />

        {/* Lista de Citas */}
        {citasOrdenadas.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '48px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <p style={{
              fontSize: '48px',
              margin: '0 0 16px 0'
            }}>
              📅
            </p>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 8px 0'
            }}>
              No hay citas
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {filtroEstado === 'TODAS'
                ? 'Aún no tienes citas agendadas'
                : `No tienes citas con estado ${filtroEstado}`}
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '16px'
          }}>
            {citasOrdenadas.map((cita) => (
              <CitaCard
                key={cita.id}
                cita={cita}
                onCancelar={handleAbrirModalCancelar} // ← NUEVO
              />
            ))}
          </div>
        )}
      </main>

      {/* Modal de Confirmación - NUEVO */}
      {citaACancelar && (
        <ModalConfirmarCancelar
          cita={citaACancelar}
          onConfirmar={handleConfirmarCancelar}
          onCancelar={handleCerrarModal}
          loading={cancelando}
        />
      )}
    </div>
  );
};

export default Citas;
```

---

## 🧪 Pruebas

### **Caso 1: Cancelar Cita Pendiente**
1. Login con `paciente1@test.com` / `paciente123`
2. Ir a "Mis Citas"
3. Buscar una cita con estado PENDIENTE
4. Click "Cancelar esta cita"
5. Modal de confirmación aparece
6. Verificar información de la cita
7. Click "Sí, cancelar cita"
8. **Esperado**:
   - Modal se cierra
   - Alert "Cita cancelada exitosamente"
   - Estado de la cita cambia a CANCELADA en la lista
   - Botón de cancelar desaparece de esa cita

### **Caso 2: Cancelar Cita Confirmada**
1. Buscar cita con estado CONFIRMADA
2. Click "Cancelar esta cita"
3. Confirmar en modal
4. **Esperado**: Cita se cancela correctamente (mismo flujo)

### **Caso 3: No Cancelar desde Modal**
1. Click "Cancelar esta cita"
2. Modal aparece
3. Click "No, mantener cita"
4. **Esperado**:
   - Modal se cierra
   - Cita sigue en su estado original
   - No hay cambios

### **Caso 4: Cerrar Modal con Overlay**
1. Click "Cancelar esta cita"
2. Modal aparece
3. Click en el área oscura fuera del modal
4. **Esperado**: Modal se cierra sin cancelar

### **Caso 5: Intentar Cancelar Cita Atendida**
1. Buscar cita con estado ATENDIDA
2. **Esperado**: No aparece botón "Cancelar esta cita"

### **Caso 6: Intentar Cancelar Cita ya Cancelada**
1. Buscar cita con estado CANCELADA
2. **Esperado**: No aparece botón "Cancelar esta cita"

---

## ✅ Checklist de Verificación

- [ ] Botón "Cancelar" aparece solo en citas PENDIENTE/CONFIRMADA
- [ ] Click en botón abre modal de confirmación
- [ ] Modal muestra información correcta de la cita
- [ ] Botón "No, mantener cita" cierra modal sin cambios
- [ ] Click en overlay cierra modal
- [ ] Botón "Sí, cancelar cita" ejecuta cancelación
- [ ] Estado de loading funciona (botón deshabilitado)
- [ ] Alert de éxito se muestra
- [ ] Cita actualiza su estado a CANCELADA en la lista
- [ ] Botón desaparece de cita cancelada
- [ ] Citas ATENDIDA no muestran botón
- [ ] Citas CANCELADA no muestran botón
- [ ] Console logs funcionan correctamente
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: "La cita ya está cancelada"**
**Síntoma**: Error 400 con mensaje del backend
**Causa**: Intentar cancelar una cita que ya tiene estado CANCELADA
**Solución**: Verificado - el botón no aparece en citas canceladas

### **Error 2: "No se puede cancelar una cita ya atendida"**
**Síntoma**: Error 400 del backend
**Causa**: Intentar cancelar cita ATENDIDA
**Solución**: Verificado - el botón no aparece en citas atendidas

### **Error 3: Modal no se cierra**
**Síntoma**: Modal sigue abierto después de cancelar
**Causa**: Estado `citaACancelar` no se limpia
**Solución**: Verificar que `setCitaACancelar(null)` se ejecute

### **Error 4: Estado no se actualiza en la lista**
**Síntoma**: Cita cancelada pero sigue mostrando estado anterior
**Causa**: Lista no se actualiza con nuevo estado
**Solución**: Verificar mapeo de estado en `handleConfirmarCancelar`

---

## 🔄 Siguiente Paso

✅ Cancelar cita completado → Continuar con **`07_reprogramar_cita.md`** (Editar fecha/hora de cita)
