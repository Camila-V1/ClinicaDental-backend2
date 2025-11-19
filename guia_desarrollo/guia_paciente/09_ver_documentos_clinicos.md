# 09 - Ver y Descargar Documentos Clínicos

## 🎯 Objetivo
Implementar la funcionalidad para que el paciente pueda ver, previsualizar y descargar sus documentos clínicos (radiografías, recetas, informes, etc.) de forma segura.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver historial funcional (Guía 08)

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/historial/documentos/`
Lista documentos clínicos del paciente

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `historial_clinico` (opcional): Filtrar por ID de historial
- `tipo` (opcional): Filtrar por tipo de documento

**Response 200:**
```json
[
  {
    "id": 5,
    "historial_clinico": 1,
    "episodio": 10,
    "nombre_archivo": "radiografia_panoramica_2025-11-10.jpg",
    "tipo_documento": "RADIOGRAFIA",
    "descripcion": "Radiografía panorámica inicial",
    "archivo": "/media/documentos_clinicos/radiografia_panoramica_2025-11-10.jpg",
    "fecha_subida": "2025-11-10T11:00:00-05:00",
    "subido_por": {
      "id": 5,
      "nombre": "Carlos",
      "apellido": "López"
    }
  }
]
```

### **GET** `/tenant/api/historial/documentos/{id}/descargar/`
Descarga un documento específico

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
- Content-Type: application/pdf, image/jpeg, etc.
- Content-Disposition: attachment; filename="radiografia.jpg"
- Binary file data

**Response 404:**
```json
{
  "error": "Este documento no tiene archivo adjunto."
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── Documentos.tsx                ← Nuevo
├── components/
│   └── paciente/
│       ├── DocumentoGaleria.tsx          ← Nuevo
│       ├── DocumentoModal.tsx            ← Nuevo (preview)
│       └── FiltrosDocumentos.tsx         ← Nuevo
└── services/
    └── documentosService.ts              ← Nuevo
```

---

## 💻 Código Paso a Paso

### **Paso 1: Crear servicio de Documentos**

**Archivo:** `src/services/documentosService.ts` (nuevo)

```typescript
import apiClient from '../config/apiClient';
import type { DocumentoClinico } from '../types/historial.types';

const documentosService = {
  /**
   * Obtener todos los documentos del paciente
   */
  async getMisDocumentos(
    historialId?: number,
    tipo?: string
  ): Promise<DocumentoClinico[]> {
    console.group('📄 [documentosService] getMisDocumentos');
    
    const params: Record<string, any> = {};
    if (historialId) params.historial_clinico = historialId;
    if (tipo) params.tipo = tipo;
    
    console.log('Filtros:', params);
    
    try {
      const response = await apiClient.get<DocumentoClinico[]>(
        '/tenant/api/historial/documentos/',
        { params }
      );
      
      console.log('✅ Documentos obtenidos:', response.data.length);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo documentos:', error);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Descargar un documento específico
   */
  async descargarDocumento(documentoId: number): Promise<Blob> {
    console.group('⬇️ [documentosService] descargarDocumento');
    console.log('ID:', documentoId);
    
    try {
      const response = await apiClient.get(
        `/tenant/api/historial/documentos/${documentoId}/descargar/`,
        {
          responseType: 'blob' // Importante para archivos binarios
        }
      );
      
      console.log('✅ Documento descargado');
      console.log('Tipo:', response.headers['content-type']);
      console.log('Tamaño:', response.data.size, 'bytes');
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error descargando documento:', error);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Obtener URL de previsualización (si es imagen)
   */
  getPreviewUrl(documento: DocumentoClinico): string | null {
    if (!documento.archivo) return null;
    
    // Construir URL completa
    const baseUrl = apiClient.defaults.baseURL || '';
    return `${baseUrl}${documento.archivo}`;
  }
};

export default documentosService;
```

---

### **Paso 2: Componente FiltrosDocumentos**

**Archivo:** `src/components/paciente/FiltrosDocumentos.tsx` (nuevo)

```typescript
interface FiltrosDocumentosProps {
  tipoActivo: string | null;
  onChange: (tipo: string | null) => void;
}

const FiltrosDocumentos = ({ tipoActivo, onChange }: FiltrosDocumentosProps) => {
  const tipos = [
    { valor: null, texto: 'Todos', icon: '📁' },
    { valor: 'RADIOGRAFIA', texto: 'Radiografías', icon: '🦴' },
    { valor: 'FOTO', texto: 'Fotografías', icon: '📷' },
    { valor: 'ESTUDIO', texto: 'Estudios', icon: '📊' },
    { valor: 'CONSENTIMIENTO', texto: 'Consentimientos', icon: '📄' },
    { valor: 'OTRO', texto: 'Otros', icon: '📎' }
  ];

  return (
    <div style={{
      display: 'flex',
      gap: '8px',
      flexWrap: 'wrap',
      marginBottom: '20px'
    }}>
      {tipos.map((tipo) => {
        const activo = tipoActivo === tipo.valor;
        
        return (
          <button
            key={tipo.valor || 'todos'}
            onClick={() => onChange(tipo.valor)}
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
              if (!activo) {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
              }
            }}
            onMouseLeave={(e) => {
              if (!activo) {
                e.currentTarget.style.backgroundColor = 'white';
              }
            }}
          >
            <span>{tipo.icon}</span>
            <span>{tipo.texto}</span>
          </button>
        );
      })}
    </div>
  );
};

export default FiltrosDocumentos;
```

---

### **Paso 3: Componente DocumentoModal (preview)**

**Archivo:** `src/components/paciente/DocumentoModal.tsx` (nuevo)

```typescript
import { useState } from 'react';
import type { DocumentoClinico } from '../../types/historial.types';
import documentosService from '../../services/documentosService';

interface DocumentoModalProps {
  documento: DocumentoClinico;
  onCerrar: () => void;
}

const DocumentoModal = ({ documento, onCerrar }: DocumentoModalProps) => {
  const [descargando, setDescargando] = useState(false);

  const esImagen = (): boolean => {
    const extensionesImagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    return extensionesImagen.some(ext => 
      documento.nombre_archivo.toLowerCase().endsWith(ext)
    );
  };

  const handleDescargar = async () => {
    console.group('⬇️ Descargar Documento');
    console.log('ID:', documento.id);
    console.log('Nombre:', documento.nombre_archivo);

    setDescargando(true);

    try {
      const blob = await documentosService.descargarDocumento(documento.id);
      
      // Crear URL temporal del blob
      const url = window.URL.createObjectURL(blob);
      
      // Crear elemento <a> temporal para trigger descarga
      const link = document.createElement('a');
      link.href = url;
      link.download = documento.nombre_archivo;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Liberar URL temporal
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Descarga exitosa');
      console.groupEnd();

    } catch (err: any) {
      console.error('❌ Error en descarga');
      console.groupEnd();
      
      alert('Error al descargar el documento. Intenta nuevamente.');

    } finally {
      setDescargando(false);
    }
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
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}
        onClick={onCerrar}
      >
        {/* Modal */}
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            maxWidth: '900px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{
            padding: '20px 24px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: '16px'
          }}>
            <div style={{ flex: 1 }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#111827',
                margin: '0 0 8px 0'
              }}>
                {documento.nombre_archivo}
              </h3>
              <div style={{
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
                alignItems: 'center'
              }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '4px 8px',
                  backgroundColor: '#dbeafe',
                  color: '#1e40af',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {documento.tipo_documento}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {formatearFecha(documento.fecha_subida)}
                </span>
              </div>
            </div>

            <button
              onClick={onCerrar}
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: '#f3f4f6',
                border: 'none',
                fontSize: '18px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#e5e7eb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
              }}
            >
              ✕
            </button>
          </div>

          {/* Body */}
          <div style={{ padding: '24px' }}>
            {/* Descripción */}
            {documento.descripcion && (
              <div style={{
                padding: '12px',
                backgroundColor: '#f9fafb',
                borderRadius: '6px',
                marginBottom: '20px'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: '#374151',
                  margin: 0,
                  lineHeight: '1.5'
                }}>
                  {documento.descripcion}
                </p>
              </div>
            )}

            {/* Preview de Imagen */}
            {esImagen() && documento.archivo && (
              <div style={{
                marginBottom: '20px',
                textAlign: 'center'
              }}>
                <img
                  src={documentosService.getPreviewUrl(documento) || ''}
                  alt={documento.nombre_archivo}
                  style={{
                    maxWidth: '100%',
                    maxHeight: '500px',
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb'
                  }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}

            {/* Mensaje para no-imágenes */}
            {!esImagen() && (
              <div style={{
                padding: '48px',
                backgroundColor: '#f9fafb',
                borderRadius: '8px',
                textAlign: 'center',
                marginBottom: '20px'
              }}>
                <p style={{
                  fontSize: '48px',
                  margin: '0 0 16px 0'
                }}>
                  📄
                </p>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: 0
                }}>
                  La previsualización no está disponible para este tipo de archivo.
                  <br />
                  Descarga el archivo para verlo.
                </p>
              </div>
            )}

            {/* Botón de Descarga */}
            <button
              onClick={handleDescargar}
              disabled={descargando}
              style={{
                width: '100%',
                padding: '12px 24px',
                backgroundColor: descargando ? '#9ca3af' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: descargando ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!descargando) e.currentTarget.style.backgroundColor = '#059669';
              }}
              onMouseLeave={(e) => {
                if (!descargando) e.currentTarget.style.backgroundColor = '#10b981';
              }}
            >
              {descargando ? '⏳ Descargando...' : '⬇️ Descargar Documento'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default DocumentoModal;
```

---

### **Paso 4: Componente DocumentoGaleria**

**Archivo:** `src/components/paciente/DocumentoGaleria.tsx` (nuevo)

```typescript
import type { DocumentoClinico } from '../../types/historial.types';

interface DocumentoGaleriaProps {
  documentos: DocumentoClinico[];
  onClickDocumento: (documento: DocumentoClinico) => void;
}

const DocumentoGaleria = ({ documentos, onClickDocumento }: DocumentoGaleriaProps) => {
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

  const truncarNombre = (nombre: string, maxLength: number = 30): string => {
    if (nombre.length <= maxLength) return nombre;
    return nombre.substring(0, maxLength - 3) + '...';
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
      gap: '16px'
    }}>
      {documentos.map((documento) => (
        <div
          key={documento.id}
          onClick={() => onClickDocumento(documento)}
          style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid #e5e7eb',
            cursor: 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
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
          {/* Icono grande */}
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '12px',
            backgroundColor: `${getTipoColor(documento.tipo_documento)}20`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            margin: '0 auto'
          }}>
            {getTipoIcon(documento.tipo_documento)}
          </div>

          {/* Información */}
          <div style={{ textAlign: 'center' }}>
            <h4 style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>
              {truncarNombre(documento.nombre_archivo)}
            </h4>

            <p style={{
              fontSize: '12px',
              color: getTipoColor(documento.tipo_documento),
              fontWeight: '600',
              margin: '0 0 8px 0'
            }}>
              {documento.tipo_documento}
            </p>

            <p style={{
              fontSize: '12px',
              color: '#9ca3af',
              margin: 0
            }}>
              {formatearFecha(documento.fecha_subida)}
            </p>
          </div>

          {/* Badge de acción */}
          <div style={{
            padding: '6px 12px',
            backgroundColor: '#f3f4f6',
            borderRadius: '6px',
            textAlign: 'center',
            fontSize: '12px',
            fontWeight: '600',
            color: '#374151'
          }}>
            👁️ Ver documento
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentoGaleria;
```

---

### **Paso 5: Página Documentos**

**Archivo:** `src/pages/paciente/Documentos.tsx` (nuevo)

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import documentosService from '../../services/documentosService';
import historialService from '../../services/historialService';
import FiltrosDocumentos from '../../components/paciente/FiltrosDocumentos';
import DocumentoGaleria from '../../components/paciente/DocumentoGaleria';
import DocumentoModal from '../../components/paciente/DocumentoModal';
import type { DocumentoClinico } from '../../types/historial.types';

const Documentos = () => {
  const navigate = useNavigate();

  const [documentos, setDocumentos] = useState<DocumentoClinico[]>([]);
  const [filtroTipo, setFiltroTipo] = useState<string | null>(null);
  const [documentoSeleccionado, setDocumentoSeleccionado] = useState<DocumentoClinico | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarDocumentos();
  }, []);

  const cargarDocumentos = async () => {
    try {
      setLoading(true);
      setError(null);

      // Obtener historial para tener el ID
      const historial = await historialService.getMiHistorial();
      
      // Obtener documentos
      const docs = await documentosService.getMisDocumentos(historial.id);
      setDocumentos(docs);

    } catch (err: any) {
      console.error('Error cargando documentos:', err);
      setError('No se pudieron cargar los documentos');

    } finally {
      setLoading(false);
    }
  };

  const documentosFiltrados = filtroTipo
    ? documentos.filter(doc => doc.tipo_documento === filtroTipo)
    : documentos;

  const documentosOrdenados = [...documentosFiltrados].sort((a, b) => {
    return new Date(b.fecha_subida).getTime() - new Date(a.fecha_subida).getTime();
  });

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
            ⏳ Cargando documentos...
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
            📄 Mis Documentos Clínicos
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '4px 0 0 0'
          }}>
            {documentos.length} {documentos.length === 1 ? 'documento' : 'documentos'} en total
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
        <FiltrosDocumentos
          tipoActivo={filtroTipo}
          onChange={setFiltroTipo}
        />

        {/* Galería */}
        {documentosOrdenados.length === 0 ? (
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
              No hay documentos
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {filtroTipo
                ? `No tienes documentos de tipo ${filtroTipo}`
                : 'Aún no tienes documentos clínicos registrados'}
            </p>
          </div>
        ) : (
          <DocumentoGaleria
            documentos={documentosOrdenados}
            onClickDocumento={setDocumentoSeleccionado}
          />
        )}
      </main>

      {/* Modal de Documento */}
      {documentoSeleccionado && (
        <DocumentoModal
          documento={documentoSeleccionado}
          onCerrar={() => setDocumentoSeleccionado(null)}
        />
      )}
    </div>
  );
};

export default Documentos;
```

---

### **Paso 6: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import DocumentosPaciente from './pages/paciente/Documentos'; // ← NUEVO

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
        <Route path="/paciente/documentos" element={<DocumentosPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Ver Galería de Documentos**
1. Login con `paciente1@test.com` / `paciente123`
2. Navegar a "Documentos Clínicos"
3. **Esperado**:
   - Grid de cards con documentos
   - Iconos según tipo
   - Nombres truncados si son largos
   - Fechas formateadas

### **Caso 2: Filtrar por Tipo**
1. Click en "🦴 Radiografías"
2. **Esperado**: Solo documentos tipo RADIOGRAFIA
3. Click en "📁 Todos"
4. **Esperado**: Todos los documentos

### **Caso 3: Ver Preview de Imagen**
1. Click en documento de tipo RADIOGRAFIA o FOTO
2. **Esperado**:
   - Modal abre con imagen mostrada
   - Información del documento
   - Botón de descarga

### **Caso 4: Ver Documento No-Imagen**
1. Click en documento PDF o CONSENTIMIENTO
2. **Esperado**:
   - Modal abre sin preview
   - Mensaje "La previsualización no está disponible"
   - Botón de descarga disponible

### **Caso 5: Descargar Documento**
1. Abrir modal de documento
2. Click "⬇️ Descargar Documento"
3. **Esperado**:
   - Botón muestra "⏳ Descargando..."
   - Archivo se descarga con nombre correcto
   - Modal se puede cerrar después

### **Caso 6: Cerrar Modal**
1. Abrir documento
2. Click en "✕" o fuera del modal
3. **Esperado**: Modal se cierra

### **Caso 7: Sin Documentos**
1. Paciente sin documentos
2. **Esperado**: Mensaje "Aún no tienes documentos clínicos registrados"

---

## ✅ Checklist de Verificación

- [ ] Galería carga correctamente
- [ ] Filtros funcionan correctamente
- [ ] Click en documento abre modal
- [ ] Preview de imágenes funciona
- [ ] Mensaje correcto para no-imágenes
- [ ] Botón descargar funciona
- [ ] Descarga con nombre correcto
- [ ] Estado loading durante descarga
- [ ] Modal se puede cerrar
- [ ] Estado vacío funciona
- [ ] Ordenamiento por fecha funciona
- [ ] Responsive en móvil
- [ ] Console logs funcionan
- [ ] Error handling funciona

---

## 🐛 Errores Comunes

### **Error 1: Imagen no carga en preview**
**Síntoma**: Imagen rota en modal
**Causa**: URL del archivo incorrecta o CORS
**Solución**: Verificar que `documento.archivo` tenga URL completa

### **Error 2: Descarga falla**
**Síntoma**: Error al descargar
**Causa**: Endpoint no retorna blob correctamente
**Solución**: Verificar `responseType: 'blob'` en axios

### **Error 3: Nombre de archivo incorrecto**
**Síntoma**: Archivo descarga con nombre genérico
**Causa**: Backend no envía Content-Disposition
**Solución**: Backend debe incluir header `Content-Disposition`

### **Error 4: Modal no cierra**
**Síntoma**: Click fuera no cierra modal
**Causa**: Event propagation no detenido
**Solución**: Verificar `onClick={(e) => e.stopPropagation()}`

---

## 💡 Notas Importantes

### **Tipos de Archivo Soportados**
- **Imágenes**: JPG, PNG, GIF, WebP (preview disponible)
- **PDFs**: Sin preview (solo descarga)
- **Documentos**: DOCX, TXT (solo descarga)

### **Seguridad**
- Backend valida que el documento pertenezca al paciente
- Autenticación requerida para todos los endpoints
- Aislamiento por tenant automático

---

## 🔄 Siguiente Paso

✅ Ver documentos completado → Continuar con **`10_ver_planes_tratamiento.md`** (Inicio de Fase 4 - Planes)
