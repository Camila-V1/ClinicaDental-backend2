# 08 - Ver Mi Historial Clínico

## 🎯 Objetivo
Implementar la visualización del historial clínico del paciente, mostrando episodios de atención, documentos clínicos y odontograma de forma organizada y fácil de entender.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Dashboard funcional (Guía 02)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/historial/historiales/`
Lista historiales clínicos (paciente ve solo el suyo)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
[
  {
    "id": 1,
    "paciente": {
      "id": 3,
      "usuario": {
        "nombre": "María",
        "apellido": "García",
        "email": "maria@test.com"
      }
    },
    "antecedentes_medicos": "Diabetes tipo 2 controlada",
    "alergias": "Penicilina",
    "medicamentos_actuales": "Metformina 500mg",
    "creado": "2024-01-15T10:00:00-05:00",
    "actualizado": "2025-11-10T14:30:00-05:00"
  }
]
```

### **GET** `/tenant/api/historial/historiales/{id}/`
Detalle completo del historial con episodios

**Response 200:**
```json
{
  "id": 1,
  "paciente": {
    "id": 3,
    "usuario": {
      "nombre": "María",
      "apellido": "García",
      "email": "maria@test.com",
      "fecha_nacimiento": "1990-05-15"
    }
  },
  "antecedentes_medicos": "Diabetes tipo 2 controlada",
  "alergias": "Penicilina",
  "medicamentos_actuales": "Metformina 500mg",
  "episodios": [
    {
      "id": 10,
      "fecha_atencion": "2025-11-10T10:00:00-05:00",
      "odontologo": {
        "id": 5,
        "usuario": {
          "nombre": "Carlos",
          "apellido": "López"
        },
        "especialidad": "Ortodoncia"
      },
      "motivo_consulta": "Restauración Pieza 16",
      "diagnostico": "Caries profunda mesio-oclusal",
      "descripcion_procedimiento": "Restauración con resina Premium 3M A1",
      "observaciones": "Control en 15 días",
      "proxima_cita": "2025-11-25"
    }
  ],
  "documentos": [
    {
      "id": 5,
      "nombre_archivo": "radiografia_panoramica.jpg",
      "tipo_documento": "RADIOGRAFIA",
      "descripcion": "Radiografía panorámica inicial",
      "fecha_subida": "2025-11-10T11:00:00-05:00"
    }
  ],
  "odontogramas": [
    {
      "id": 1,
      "estado_piezas": {
        "16": {
          "estado": "restaurado",
          "material": "resina",
          "fecha": "2025-11-10"
        }
      },
      "fecha_registro": "2025-11-10T10:30:00-05:00"
    }
  ],
  "creado": "2024-01-15T10:00:00-05:00"
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── HistorialClinico.tsx          ← Nuevo
├── components/
│   └── paciente/
│       ├── ResumenHistorial.tsx          ← Nuevo
│       ├── EpisodioCard.tsx              ← Nuevo
│       ├── DocumentoCard.tsx             ← Nuevo
│       └── OdontogramaVisual.tsx         ← Nuevo (simplificado)
├── services/
│   └── historialService.ts               ← Extender
└── types/
    └── historial.types.ts                ← Extender
```

---

## 💻 Código Paso a Paso

### **Paso 1: Extender tipos de Historial**

**Archivo:** `src/types/historial.types.ts` (extender)

```typescript
// ... tipos existentes ...

export interface Episodio {
  id: number;
  fecha_atencion: string;
  odontologo: {
    id: number;
    usuario: {
      nombre: string;
      apellido: string;
    };
    especialidad?: string;
  };
  motivo_consulta: string;
  diagnostico: string;
  descripcion_procedimiento: string;
  observaciones?: string;
  proxima_cita?: string;
}

export interface DocumentoClinico {
  id: number;
  nombre_archivo: string;
  tipo_documento: 'RADIOGRAFIA' | 'FOTO' | 'ESTUDIO' | 'CONSENTIMIENTO' | 'OTRO';
  descripcion?: string;
  fecha_subida: string;
  archivo?: string; // URL
}

export interface EstadoPieza {
  estado: string; // 'sano', 'caries', 'restaurado', 'ausente', etc.
  material?: string;
  fecha?: string;
  observaciones?: string;
}

export interface Odontograma {
  id: number;
  estado_piezas: Record<string, EstadoPieza>; // { "16": {...}, "17": {...} }
  fecha_registro: string;
  observaciones?: string;
}

export interface HistorialClinicoDetalle {
  id: number;
  paciente: {
    id: number;
    usuario: {
      nombre: string;
      apellido: string;
      email: string;
      fecha_nacimiento?: string;
    };
  };
  antecedentes_medicos?: string;
  alergias?: string;
  medicamentos_actuales?: string;
  episodios: Episodio[];
  documentos: DocumentoClinico[];
  odontogramas: Odontograma[];
  creado: string;
  actualizado?: string;
}
```

---

### **Paso 2: Extender servicio de Historial**

**Archivo:** `src/services/historialService.ts` (agregar método)

```typescript
import apiClient from '../config/apiClient';
import type { HistorialClinicoDetalle } from '../types/historial.types';

const historialService = {
  /**
   * Obtener el historial clínico completo del paciente actual
   */
  async getMiHistorial(): Promise<HistorialClinicoDetalle> {
    console.group('📋 [historialService] getMiHistorial');
    
    try {
      // Primero obtener la lista (el paciente solo ve el suyo)
      const listaResponse = await apiClient.get<HistorialClinicoDetalle[]>(
        '/tenant/api/historial/historiales/'
      );
      
      if (listaResponse.data.length === 0) {
        throw new Error('No se encontró historial clínico');
      }
      
      const historialId = listaResponse.data[0].id;
      
      // Luego obtener el detalle completo
      const detalleResponse = await apiClient.get<HistorialClinicoDetalle>(
        `/tenant/api/historial/historiales/${historialId}/`
      );
      
      console.log('✅ Historial obtenido exitosamente');
      console.log('Episodios:', detalleResponse.data.episodios.length);
      console.log('Documentos:', detalleResponse.data.documentos.length);
      console.groupEnd();
      
      return detalleResponse.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo historial:', error);
      console.groupEnd();
      throw error;
    }
  }
};

export default historialService;
```

---

### **Paso 3: Componente EpisodioCard**

**Archivo:** `src/components/paciente/EpisodioCard.tsx` (nuevo)

```typescript
import type { Episodio } from '../../types/historial.types';

interface EpisodioCardProps {
  episodio: Episodio;
}

const EpisodioCard = ({ episodio }: EpisodioCardProps) => {
  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '20px',
      border: '1px solid #e5e7eb',
      marginBottom: '16px'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div>
          <h3 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 4px 0'
          }}>
            📅 {formatearFecha(episodio.fecha_atencion)}
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            {episodio.motivo_consulta}
          </p>
        </div>

        {episodio.odontologo && (
          <div style={{ textAlign: 'right' }}>
            <p style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#374151',
              margin: '0 0 2px 0'
            }}>
              👨‍⚕️ {episodio.odontologo.usuario.nombre} {episodio.odontologo.usuario.apellido}
            </p>
            {episodio.odontologo.especialidad && (
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: 0
              }}>
                {episodio.odontologo.especialidad}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Contenido */}
      <div style={{
        display: 'grid',
        gap: '12px'
      }}>
        {/* Diagnóstico */}
        <div>
          <p style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            margin: '0 0 4px 0',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🔍 Diagnóstico
          </p>
          <p style={{
            fontSize: '14px',
            color: '#111827',
            margin: 0,
            lineHeight: '1.5'
          }}>
            {episodio.diagnostico}
          </p>
        </div>

        {/* Procedimiento */}
        <div>
          <p style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            margin: '0 0 4px 0',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🦷 Procedimiento Realizado
          </p>
          <p style={{
            fontSize: '14px',
            color: '#111827',
            margin: 0,
            lineHeight: '1.5'
          }}>
            {episodio.descripcion_procedimiento}
          </p>
        </div>

        {/* Observaciones */}
        {episodio.observaciones && (
          <div>
            <p style={{
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              margin: '0 0 4px 0',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              💬 Observaciones
            </p>
            <p style={{
              fontSize: '14px',
              color: '#111827',
              margin: 0,
              lineHeight: '1.5'
            }}>
              {episodio.observaciones}
            </p>
          </div>
        )}

        {/* Próxima Cita */}
        {episodio.proxima_cita && (
          <div style={{
            marginTop: '8px',
            padding: '12px',
            backgroundColor: '#dbeafe',
            borderRadius: '6px',
            border: '1px solid #93c5fd'
          }}>
            <p style={{
              fontSize: '13px',
              color: '#1e40af',
              margin: 0
            }}>
              📌 <strong>Próximo control:</strong> {formatearFecha(episodio.proxima_cita)}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EpisodioCard;
```

---

### **Paso 4: Componente DocumentoCard**

**Archivo:** `src/components/paciente/DocumentoCard.tsx` (nuevo)

```typescript
import type { DocumentoClinico } from '../../types/historial.types';

interface DocumentoCardProps {
  documento: DocumentoClinico;
}

const DocumentoCard = ({ documento }: DocumentoCardProps) => {
  const getTipoIcon = (tipo: string): string => {
    const iconos: Record<string, string> = {
      'RADIOGRAFIA': '🦴',
      'FOTO': '📷',
      'ESTUDIO': '📊',
      'CONSENTIMIENTO': '📄',
      'OTRO': '📎'
    };
    return iconos[tipo] || '📄';
  };

  const getTipoColor = (tipo: string): string => {
    const colores: Record<string, string> = {
      'RADIOGRAFIA': '#3b82f6',
      'FOTO': '#10b981',
      'ESTUDIO': '#8b5cf6',
      'CONSENTIMIENTO': '#f59e0b',
      'OTRO': '#6b7280'
    };
    return colores[tipo] || '#6b7280';
  };

  const formatearFecha = (fecha: string): string => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '16px',
      border: '1px solid #e5e7eb',
      display: 'flex',
      gap: '12px',
      alignItems: 'flex-start',
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
      {/* Icono */}
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '8px',
        backgroundColor: `${getTipoColor(documento.tipo_documento)}20`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '24px',
        flexShrink: 0
      }}>
        {getTipoIcon(documento.tipo_documento)}
      </div>

      {/* Contenido */}
      <div style={{ flex: 1 }}>
        <h4 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#111827',
          margin: '0 0 4px 0'
        }}>
          {documento.nombre_archivo}
        </h4>

        <p style={{
          fontSize: '12px',
          color: getTipoColor(documento.tipo_documento),
          fontWeight: '600',
          margin: '0 0 4px 0'
        }}>
          {documento.tipo_documento}
        </p>

        {documento.descripcion && (
          <p style={{
            fontSize: '13px',
            color: '#6b7280',
            margin: '0 0 8px 0',
            lineHeight: '1.4'
          }}>
            {documento.descripcion}
          </p>
        )}

        <p style={{
          fontSize: '12px',
          color: '#9ca3af',
          margin: 0
        }}>
          Subido el {formatearFecha(documento.fecha_subida)}
        </p>
      </div>

      {/* Botón Descargar */}
      <button
        style={{
          padding: '6px 12px',
          backgroundColor: '#f3f4f6',
          color: '#374151',
          border: '1px solid #d1d5db',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: '600',
          cursor: 'pointer',
          flexShrink: 0
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#e5e7eb';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#f3f4f6';
        }}
      >
        ⬇️ Ver
      </button>
    </div>
  );
};

export default DocumentoCard;
```

---

### **Paso 5: Página HistorialClinico**

**Archivo:** `src/pages/paciente/HistorialClinico.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import historialService from '../../services/historialService';
import EpisodioCard from '../../components/paciente/EpisodioCard';
import DocumentoCard from '../../components/paciente/DocumentoCard';
import type { HistorialClinicoDetalle } from '../../types/historial.types';

const HistorialClinico = () => {
  const navigate = useNavigate();

  const [historial, setHistorial] = useState<HistorialClinicoDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [vistaActiva, setVistaActiva] = useState<'episodios' | 'documentos' | 'info'>('episodios');

  useEffect(() => {
    cargarHistorial();
  }, []);

  const cargarHistorial = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await historialService.getMiHistorial();
      setHistorial(data);

    } catch (err: any) {
      console.error('Error cargando historial:', err);
      
      if (err.message === 'No se encontró historial clínico') {
        setError('Aún no tienes un historial clínico registrado');
      } else {
        setError('No se pudo cargar el historial clínico');
      }

    } finally {
      setLoading(false);
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
            ⏳ Cargando historial...
          </p>
        </div>
      </div>
    );
  }

  if (error || !historial) {
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
          <p style={{ fontSize: '48px', margin: '0 0 16px 0' }}>📋</p>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 8px 0'
          }}>
            {error || 'No se encontró historial'}
          </h3>
          <button
            onClick={() => navigate('/paciente/dashboard')}
            style={{
              marginTop: '20px',
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
            Volver al Dashboard
          </button>
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
            📋 Mi Historial Clínico
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '4px 0 0 0'
          }}>
            Registro completo de tus consultas y tratamientos
          </p>
        </div>
      </header>

      {/* Pestañas */}
      <div style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          gap: '8px'
        }}>
          <button
            onClick={() => setVistaActiva('episodios')}
            style={{
              padding: '12px 20px',
              backgroundColor: 'transparent',
              color: vistaActiva === 'episodios' ? '#10b981' : '#6b7280',
              border: 'none',
              borderBottom: `2px solid ${vistaActiva === 'episodios' ? '#10b981' : 'transparent'}`,
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            🦷 Episodios ({historial.episodios.length})
          </button>

          <button
            onClick={() => setVistaActiva('documentos')}
            style={{
              padding: '12px 20px',
              backgroundColor: 'transparent',
              color: vistaActiva === 'documentos' ? '#10b981' : '#6b7280',
              border: 'none',
              borderBottom: `2px solid ${vistaActiva === 'documentos' ? '#10b981' : 'transparent'}`,
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            📄 Documentos ({historial.documentos.length})
          </button>

          <button
            onClick={() => setVistaActiva('info')}
            style={{
              padding: '12px 20px',
              backgroundColor: 'transparent',
              color: vistaActiva === 'info' ? '#10b981' : '#6b7280',
              border: 'none',
              borderBottom: `2px solid ${vistaActiva === 'info' ? '#10b981' : 'transparent'}`,
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            ℹ️ Información General
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Vista: Episodios */}
        {vistaActiva === 'episodios' && (
          <div>
            {historial.episodios.length === 0 ? (
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
                  Sin episodios registrados
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: 0
                }}>
                  Aún no tienes consultas registradas en tu historial
                </p>
              </div>
            ) : (
              <div>
                {historial.episodios
                  .sort((a, b) => new Date(b.fecha_atencion).getTime() - new Date(a.fecha_atencion).getTime())
                  .map((episodio) => (
                    <EpisodioCard key={episodio.id} episodio={episodio} />
                  ))}
              </div>
            )}
          </div>
        )}

        {/* Vista: Documentos */}
        {vistaActiva === 'documentos' && (
          <div>
            {historial.documentos.length === 0 ? (
              <div style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '48px',
                textAlign: 'center',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
              }}>
                <p style={{ fontSize: '48px', margin: '0 0 16px 0' }}>📄</p>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>
                  Sin documentos
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: 0
                }}>
                  No hay documentos clínicos registrados
                </p>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gap: '16px'
              }}>
                {historial.documentos
                  .sort((a, b) => new Date(b.fecha_subida).getTime() - new Date(a.fecha_subida).getTime())
                  .map((documento) => (
                    <DocumentoCard key={documento.id} documento={documento} />
                  ))}
              </div>
            )}
          </div>
        )}

        {/* Vista: Información General */}
        {vistaActiva === 'info' && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 20px 0'
            }}>
              ℹ️ Información General
            </h2>

            <div style={{
              display: 'grid',
              gap: '20px'
            }}>
              {/* Antecedentes Médicos */}
              <div>
                <p style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#6b7280',
                  margin: '0 0 8px 0',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  🏥 Antecedentes Médicos
                </p>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb'
                }}>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    {historial.antecedentes_medicos || 'Sin antecedentes registrados'}
                  </p>
                </div>
              </div>

              {/* Alergias */}
              <div>
                <p style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#6b7280',
                  margin: '0 0 8px 0',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  ⚠️ Alergias
                </p>
                <div style={{
                  padding: '12px',
                  backgroundColor: historial.alergias ? '#fef3c7' : '#f9fafb',
                  borderRadius: '6px',
                  border: `1px solid ${historial.alergias ? '#fde68a' : '#e5e7eb'}`
                }}>
                  <p style={{
                    fontSize: '14px',
                    color: historial.alergias ? '#78350f' : '#111827',
                    margin: 0,
                    lineHeight: '1.5',
                    fontWeight: historial.alergias ? '600' : '400'
                  }}>
                    {historial.alergias || 'Sin alergias registradas'}
                  </p>
                </div>
              </div>

              {/* Medicamentos Actuales */}
              <div>
                <p style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#6b7280',
                  margin: '0 0 8px 0',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  💊 Medicamentos Actuales
                </p>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb'
                }}>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    {historial.medicamentos_actuales || 'Sin medicamentos registrados'}
                  </p>
                </div>
              </div>

              {/* Fecha de Creación */}
              <div style={{
                marginTop: '12px',
                paddingTop: '20px',
                borderTop: '1px solid #e5e7eb'
              }}>
                <p style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  margin: 0
                }}>
                  Historial creado el {new Date(historial.creado).toLocaleDateString('es-ES', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default HistorialClinico;
```

---

### **Paso 6: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import HistorialClinicoPaciente from './pages/paciente/HistorialClinico'; // ← NUEVO

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
        <Route path="/paciente/historial" element={<HistorialClinicoPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Historial con Episodios**
1. Login con `paciente1@test.com` / `paciente123`
2. Navegar a "Historial Clínico"
3. **Esperado**:
   - Lista de episodios ordenados por fecha (más reciente primero)
   - Cada episodio muestra: fecha, odontólogo, motivo, diagnóstico, procedimiento
   - Si hay próxima cita, se muestra resaltada

### **Caso 2: Ver Documentos**
1. En historial, click en pestaña "📄 Documentos"
2. **Esperado**:
   - Lista de documentos con iconos por tipo
   - Información: nombre, tipo, descripción, fecha
   - Botón "Ver" en cada documento

### **Caso 3: Ver Información General**
1. Click en pestaña "ℹ️ Información General"
2. **Esperado**:
   - Antecedentes médicos
   - Alergias (resaltado en amarillo si existen)
   - Medicamentos actuales
   - Fecha de creación del historial

### **Caso 4: Sin Episodios**
1. Paciente sin episodios registrados
2. **Esperado**: Mensaje "Sin episodios registrados"

### **Caso 5: Sin Historial Clínico**
1. Paciente nuevo sin historial
2. **Esperado**: Mensaje "Aún no tienes un historial clínico registrado"

### **Caso 6: Cambiar entre Pestañas**
1. Navegar entre las 3 pestañas
2. **Esperado**: 
   - Pestaña activa resaltada en verde
   - Contenido cambia correctamente
   - Contador de items en cada pestaña

---

## ✅ Checklist de Verificación

- [ ] Página de historial carga correctamente
- [ ] Pestañas funcionan correctamente
- [ ] Vista de episodios muestra todos los datos
- [ ] Episodios ordenados por fecha descendente
- [ ] Vista de documentos muestra cards correctos
- [ ] Iconos de documentos según tipo
- [ ] Vista de información general muestra datos
- [ ] Alergias resaltadas en amarillo
- [ ] Estado vacío para episodios funciona
- [ ] Estado vacío para documentos funciona
- [ ] Error cuando no hay historial funciona
- [ ] Console logs funcionan
- [ ] Responsive en móvil
- [ ] Formato de fechas correcto

---

## 🐛 Errores Comunes

### **Error 1: "No se encontró historial clínico"**
**Síntoma**: Mensaje de error
**Causa**: Paciente no tiene historial creado en el backend
**Solución**: El administrador debe crear el historial primero

### **Error 2: Episodios no se muestran**
**Síntoma**: Lista vacía aunque existen episodios
**Causa**: Backend no incluye episodios en el response
**Solución**: Verificar que el endpoint incluya `episodios` en el serializer

### **Error 3: Documentos no tienen URL**
**Síntoma**: Botón "Ver" no funciona
**Causa**: Campo `archivo` no tiene URL completa
**Solución**: Backend debe devolver URL completa del archivo

---

## 🔄 Siguiente Paso

✅ Ver historial completado → Continuar con **`09_ver_documentos_clinicos.md`** (Descargar documentos)
