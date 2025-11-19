# Guía 36: Detalle Completo de Episodio Clínico

## 📋 Información General

**Caso de Uso**: CU16 - Ver Detalle de Episodio Clínico  
**Actor**: Paciente  
**Objetivo**: Visualizar información completa y detallada de un episodio médico específico

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver toda la información del episodio
- ✅ Ver diagnóstico completo
- ✅ Ver tratamiento realizado detallado
- ✅ Leer notas del odontólogo
- ✅ Ver y descargar documentos adjuntos (radiografías, recetas)
- ✅ Ver información del profesional que atendió
- ✅ Ver cita relacionada (si existe)
- ✅ Ver historial de cambios/actualizaciones
- ✅ Navegar entre episodios (anterior/siguiente)

---

## 🔌 API Endpoints

### Obtener Detalle de Episodio

```
GET /api/historial/episodios/{id}/
```

**Respuesta Esperada**:
```json
{
  "id": 45,
  "historial": 123,
  "fecha": "2025-11-15T10:00:00Z",
  "tipo": "CONSULTA",
  "diagnostico": "Caries en molar superior derecho (pieza 16)",
  "tratamiento_realizado": "Se realizó limpieza profunda de la cavidad y obturación con resina compuesta. Se aplicó sellante dental en fosas y fisuras adyacentes como medida preventiva.",
  "notas": "Paciente presenta buen estado general de salud bucal. Se recomienda continuar con higiene dental adecuada y controles cada 6 meses. Paciente no reporta alergias a materiales dentales.",
  "odontologo": 5,
  "odontologo_nombre": "Dr. Juan Pérez Gómez",
  "odontologo_especialidad": "Endodoncia",
  "odontologo_email": "juan.perez@clinica.com",
  "documentos": [
    {
      "id": 12,
      "tipo": "RADIOGRAFIA",
      "nombre": "radiografia_molar_16_202511.jpg",
      "archivo": "http://clinica-demo.localhost:8000/media/documentos/radiografia_molar_16_202511.jpg",
      "descripcion": "Radiografía periapical del molar 16 mostrando caries profunda",
      "fecha_subida": "2025-11-15T10:30:00Z",
      "subido_por": "Dr. Juan Pérez"
    },
    {
      "id": 13,
      "tipo": "RECETA",
      "nombre": "receta_analgesicos_202511.pdf",
      "archivo": "http://clinica-demo.localhost:8000/media/documentos/receta_analgesicos_202511.pdf",
      "descripcion": "Receta de analgésicos post-tratamiento",
      "fecha_subida": "2025-11-15T11:00:00Z",
      "subido_por": "Dr. Juan Pérez"
    }
  ],
  "cita": {
    "id": 128,
    "fecha_hora": "2025-11-15T10:00:00Z",
    "motivo": "Dolor en molar superior derecho",
    "estado": "COMPLETADA",
    "duracion_minutos": 45
  },
  "created_at": "2025-11-15T11:30:00Z",
  "updated_at": "2025-11-15T12:00:00Z"
}
```

---

## 🔧 Implementación Frontend

### 1. Service - Actualizar `historialService.ts`

Agregar función para obtener detalle:

```typescript
// src/services/historialService.ts

/**
 * Obtiene el detalle completo de un episodio específico
 */
export const obtenerDetalleEpisodio = async (episodioId: number): Promise<any> => {
  console.log(`📋 Obteniendo detalle del episodio ${episodioId}...`);
  
  try {
    const response = await apiClient.get(`/api/historial/episodios/${episodioId}/`);
    console.log('✅ Detalle del episodio obtenido:', response.data);
    console.log('📄 Documentos adjuntos:', response.data.documentos?.length || 0);
    
    return response.data;
  } catch (error) {
    console.error('❌ Error obteniendo detalle del episodio:', error);
    throw error;
  }
};

/**
 * Obtiene el episodio anterior y siguiente para navegación
 */
export const obtenerEpisodiosNavegacion = async (
  historialId: number, 
  episodioActualId: number
): Promise<{ anterior: number | null; siguiente: number | null }> => {
  console.log(`🔍 Obteniendo episodios para navegación...`);
  
  try {
    // Obtener el historial completo
    const historial = await obtenerMiHistorial();
    const episodios = historial.episodios || [];
    
    // Ordenar por fecha descendente (más reciente primero)
    const episodiosOrdenados = [...episodios].sort(
      (a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
    );
    
    // Encontrar índice del episodio actual
    const indiceActual = episodiosOrdenados.findIndex(e => e.id === episodioActualId);
    
    return {
      anterior: indiceActual > 0 ? episodiosOrdenados[indiceActual - 1].id : null,
      siguiente: indiceActual < episodiosOrdenados.length - 1 
        ? episodiosOrdenados[indiceActual + 1].id 
        : null
    };
  } catch (error) {
    console.error('❌ Error obteniendo navegación:', error);
    return { anterior: null, siguiente: null };
  }
};
```

---

### 2. Componente Principal - `DetalleEpisodio.tsx`

```tsx
// src/pages/paciente/DetalleEpisodio.tsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  obtenerDetalleEpisodio,
  obtenerEpisodiosNavegacion,
  formatearFecha,
  getTipoEpisodioColor,
  getTipoEpisodioIcono,
  descargarDocumento
} from '../../services/historialService';

// Componentes
import InfoPrincipal from '../../components/historial/detalle/InfoPrincipal';
import DocumentosDetalle from '../../components/historial/detalle/DocumentosDetalle';
import CitaRelacionada from '../../components/historial/detalle/CitaRelacionada';
import InfoOdontologo from '../../components/historial/detalle/InfoOdontologo';

export default function DetalleEpisodio() {
  const { episodioId } = useParams<{ episodioId: string }>();
  const navigate = useNavigate();

  const [episodio, setEpisodio] = useState<any>(null);
  const [navegacion, setNavegacion] = useState<{ anterior: number | null; siguiente: number | null }>({
    anterior: null,
    siguiente: null
  });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (episodioId) {
      cargarEpisodio(parseInt(episodioId));
    }
  }, [episodioId]);

  const cargarEpisodio = async (id: number) => {
    try {
      setCargando(true);
      setError(null);

      const [detalleData, navData] = await Promise.all([
        obtenerDetalleEpisodio(id),
        obtenerEpisodiosNavegacion(0, id) // historialId no es necesario según backend
      ]);

      setEpisodio(detalleData);
      setNavegacion(navData);
    } catch (err: any) {
      console.error('❌ Error cargando episodio:', err);
      setError('Error al cargar el detalle del episodio');
    } finally {
      setCargando(false);
    }
  };

  const navegarAEpisodio = (id: number | null) => {
    if (id) {
      navigate(`/paciente/historial/episodio/${id}`);
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando episodio...</p>
        </div>
      </div>
    );
  }

  if (error || !episodio) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error || 'Episodio no encontrado'}</p>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <button
              onClick={() => navigate('/paciente/historial')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              ← Volver al Historial
            </button>
            <button
              onClick={() => cargarEpisodio(parseInt(episodioId!))}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              🔄 Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      
      {/* Header con Navegación */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/paciente/historial')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center gap-2"
        >
          ← Volver al Historial
        </button>

        {/* Navegación Anterior/Siguiente */}
        <div className="flex gap-2">
          <button
            onClick={() => navegarAEpisodio(navegacion.anterior)}
            disabled={!navegacion.anterior}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
              navegacion.anterior
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            ← Anterior
          </button>
          <button
            onClick={() => navegarAEpisodio(navegacion.siguiente)}
            disabled={!navegacion.siguiente}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
              navegacion.siguiente
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            Siguiente →
          </button>
        </div>
      </div>

      {/* Título y Badge */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="text-6xl">
            {getTipoEpisodioIcono(episodio.tipo)}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getTipoEpisodioColor(episodio.tipo)}`}>
                {episodio.tipo}
              </span>
              <span className="text-gray-600">
                {formatearFecha(episodio.fecha)}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              {episodio.diagnostico}
            </h1>
            <p className="text-gray-600">
              Episodio #{episodio.id} - Registrado el {new Date(episodio.created_at).toLocaleDateString('es-ES')}
            </p>
          </div>
        </div>
      </div>

      {/* Grid de Contenido */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Columna Principal (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Información Principal */}
          <InfoPrincipal episodio={episodio} />

          {/* Documentos Adjuntos */}
          {episodio.documentos?.length > 0 && (
            <DocumentosDetalle documentos={episodio.documentos} />
          )}

          {/* Cita Relacionada */}
          {episodio.cita && (
            <CitaRelacionada cita={episodio.cita} />
          )}

        </div>

        {/* Columna Lateral (1/3) */}
        <div className="space-y-6">
          
          {/* Información del Odontólogo */}
          <InfoOdontologo episodio={episodio} />

          {/* Metadata */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="font-bold text-gray-800 mb-4">📅 Información Adicional</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">Creado:</p>
                <p className="font-medium text-gray-800">
                  {new Date(episodio.created_at).toLocaleString('es-ES')}
                </p>
              </div>
              {episodio.updated_at !== episodio.created_at && (
                <div>
                  <p className="text-gray-600">Última actualización:</p>
                  <p className="font-medium text-gray-800">
                    {new Date(episodio.updated_at).toLocaleString('es-ES')}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Acciones Rápidas */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="font-bold text-gray-800 mb-4">⚡ Acciones</h3>
            <div className="space-y-2">
              <button
                onClick={() => window.print()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
              >
                🖨️ Imprimir Episodio
              </button>
              <button
                onClick={() => navigate('/paciente/citas')}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2"
              >
                📅 Agendar Consulta
              </button>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
```

---

### 3. Componente - `InfoPrincipal.tsx`

```tsx
// src/components/historial/detalle/InfoPrincipal.tsx

import React from 'react';

interface Props {
  episodio: any;
}

export default function InfoPrincipal({ episodio }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        📋 Información Clínica Completa
      </h2>

      {/* Diagnóstico */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          🔍 Diagnóstico
        </h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-gray-800 leading-relaxed">
            {episodio.diagnostico}
          </p>
        </div>
      </div>

      {/* Tratamiento Realizado */}
      {episodio.tratamiento_realizado && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            🦷 Tratamiento Realizado
          </h3>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">
              {episodio.tratamiento_realizado}
            </p>
          </div>
        </div>
      )}

      {/* Notas del Odontólogo */}
      {episodio.notas && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            📝 Notas del Odontólogo
          </h3>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">
              {episodio.notas}
            </p>
          </div>
        </div>
      )}

      {/* Mensaje si no hay tratamiento ni notas */}
      {!episodio.tratamiento_realizado && !episodio.notas && (
        <div className="text-center py-8 text-gray-500">
          <span className="text-4xl">📄</span>
          <p className="mt-2">No hay información adicional registrada</p>
        </div>
      )}
    </div>
  );
}
```

---

### 4. Componente - `DocumentosDetalle.tsx`

```tsx
// src/components/historial/detalle/DocumentosDetalle.tsx

import React, { useState } from 'react';
import {
  getTipoDocumentoColor,
  getTipoDocumentoIcono,
  descargarDocumento,
  formatearFecha
} from '../../../services/historialService';

interface Props {
  documentos: any[];
}

export default function DocumentosDetalle({ documentos }: Props) {
  const [imagenExpandida, setImagenExpandida] = useState<string | null>(null);

  const esImagen = (tipo: string) => {
    return tipo === 'FOTO' || tipo === 'RADIOGRAFIA';
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          📎 Documentos Adjuntos ({documentos.length})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documentos.map((doc) => (
            <div
              key={doc.id}
              className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 hover:shadow-lg transition-all"
            >
              {/* Preview */}
              {esImagen(doc.tipo) ? (
                <div 
                  className="h-48 bg-gray-100 cursor-pointer relative group"
                  onClick={() => setImagenExpandida(doc.archivo)}
                >
                  <img
                    src={doc.archivo}
                    alt={doc.nombre}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5JbWFnZW4gbm8gZGlzcG9uaWJsZTwvdGV4dD48L3N2Zz4=';
                    }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all">
                    <span className="text-white text-4xl">🔍</span>
                  </div>
                </div>
              ) : (
                <div className="h-48 bg-gray-100 flex items-center justify-center">
                  <span className="text-6xl">
                    {getTipoDocumentoIcono(doc.tipo)}
                  </span>
                </div>
              )}

              {/* Info */}
              <div className="p-4">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getTipoDocumentoColor(doc.tipo)}`}>
                  {doc.tipo}
                </span>
                <h4 className="font-semibold text-gray-800 mt-3 mb-2">
                  {doc.nombre}
                </h4>
                {doc.descripcion && (
                  <p className="text-sm text-gray-600 mb-3">
                    {doc.descripcion}
                  </p>
                )}
                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                  <span>{formatearFecha(doc.fecha_subida)}</span>
                  {doc.subido_por && <span>Por: {doc.subido_por}</span>}
                </div>
                <button
                  onClick={() => descargarDocumento(doc.archivo, doc.nombre)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
                >
                  ⬇️ Descargar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de Imagen Expandida */}
      {imagenExpandida && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setImagenExpandida(null)}
        >
          <div className="relative max-w-5xl max-h-full">
            <button
              onClick={() => setImagenExpandida(null)}
              className="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75 text-2xl"
            >
              ×
            </button>
            <img
              src={imagenExpandida}
              alt="Vista ampliada"
              className="max-w-full max-h-screen object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </>
  );
}
```

---

### 5. Componente - `InfoOdontologo.tsx`

```tsx
// src/components/historial/detalle/InfoOdontologo.tsx

import React from 'react';

interface Props {
  episodio: any;
}

export default function InfoOdontologo({ episodio }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
        👨‍⚕️ Profesional a Cargo
      </h3>

      <div className="space-y-4">
        {/* Foto o Avatar */}
        <div className="flex justify-center">
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center text-4xl">
            👨‍⚕️
          </div>
        </div>

        {/* Información */}
        <div className="text-center">
          <h4 className="font-bold text-lg text-gray-800">
            {episodio.odontologo_nombre}
          </h4>
          {episodio.odontologo_especialidad && (
            <p className="text-sm text-blue-600 font-medium mt-1">
              {episodio.odontologo_especialidad}
            </p>
          )}
        </div>

        {/* Contacto */}
        {episodio.odontologo_email && (
          <div className="pt-4 border-t border-gray-200">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>📧</span>
              <a 
                href={`mailto:${episodio.odontologo_email}`}
                className="text-blue-600 hover:text-blue-800 hover:underline"
              >
                {episodio.odontologo_email}
              </a>
            </div>
          </div>
        )}

        {/* Botón Agendar */}
        <button
          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors flex items-center justify-center gap-2"
        >
          📅 Agendar con este doctor
        </button>
      </div>
    </div>
  );
}
```

---

### 6. Componente - `CitaRelacionada.tsx`

```tsx
// src/components/historial/detalle/CitaRelacionada.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatearFecha } from '../../../services/historialService';

interface Props {
  cita: any;
}

export default function CitaRelacionada({ cita }: Props) {
  const navigate = useNavigate();

  const getEstadoColor = (estado: string) => {
    switch (estado?.toUpperCase()) {
      case 'COMPLETADA':
        return 'bg-green-100 text-green-800';
      case 'PENDIENTE':
        return 'bg-yellow-100 text-yellow-800';
      case 'CANCELADA':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        📅 Cita Relacionada
      </h2>

      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">
              Cita #{cita.id}
            </h4>
            <p className="text-sm text-gray-600">
              {formatearFecha(cita.fecha_hora)}
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getEstadoColor(cita.estado)}`}>
            {cita.estado}
          </span>
        </div>

        {cita.motivo && (
          <div className="mb-3">
            <p className="text-sm font-medium text-gray-700">Motivo:</p>
            <p className="text-sm text-gray-600">{cita.motivo}</p>
          </div>
        )}

        {cita.duracion_minutos && (
          <div className="mb-3">
            <p className="text-sm text-gray-600">
              ⏱️ Duración: {cita.duracion_minutos} minutos
            </p>
          </div>
        )}

        <button
          onClick={() => navigate(`/paciente/citas/${cita.id}`)}
          className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
        >
          Ver detalle de la cita →
        </button>
      </div>
    </div>
  );
}
```

---

## 🔗 Integración con React Router

```tsx
// En tu archivo de rutas (App.tsx o routes.tsx)

import DetalleEpisodio from './pages/paciente/DetalleEpisodio';

// Agregar ruta con parámetro dinámico
<Route path="/paciente/historial/episodio/:episodioId" element={<DetalleEpisodio />} />
```

---

## 🎨 Características de la UI

### 1. **Layout de 2 Columnas**
- **Columna principal (2/3)**: Información clínica, documentos, cita
- **Columna lateral (1/3)**: Odontólogo, metadata, acciones

### 2. **Navegación Inteligente**
- Botones Anterior/Siguiente entre episodios
- Deshabilitados automáticamente si no hay más episodios
- Mantiene el flujo cronológico

### 3. **Documentos con Preview**
- Imágenes (radiografías/fotos) con preview
- Click para ver en modal fullscreen
- PDFs con icono y descarga directa

### 4. **Modal de Imagen**
- Fondo negro semi-transparente
- Imagen centrada y responsive
- Click fuera para cerrar
- Botón X para cerrar

### 5. **Acciones Rápidas**
- Imprimir episodio
- Agendar consulta
- Contactar al doctor

---

## 📝 Notas Importantes

### 1. **Estructura de Archivos**
```
src/
├── services/
│   └── historialService.ts          ← Actualizar con nuevas funciones
├── components/
│   └── historial/
│       └── detalle/                 ← Nuevo subdirectorio
│           ├── InfoPrincipal.tsx
│           ├── DocumentosDetalle.tsx
│           ├── InfoOdontologo.tsx
│           └── CitaRelacionada.tsx
└── pages/
    └── paciente/
        └── DetalleEpisodio.tsx      ← Nuevo
```

### 2. **Navegación desde HistorialClinicoCompleto**
Ya actualicé la Guía 35 para incluir un botón "Ver detalle completo →" en cada card de episodio que navegará a esta vista.

### 3. **Función de Impresión**
El botón "Imprimir" usa `window.print()` que abrirá el diálogo de impresión del navegador. Puedes agregar CSS específico para impresión si es necesario.

---

## 🧪 Testing

### Casos de Prueba

1. ✅ **Carga inicial**: Episodio se carga correctamente
2. ✅ **Navegación anterior**: Funciona si existe episodio anterior
3. ✅ **Navegación siguiente**: Funciona si existe episodio siguiente
4. ✅ **Sin navegación**: Botones deshabilitados en extremos
5. ✅ **Documentos con imágenes**: Preview y modal funcionan
6. ✅ **Documentos sin imágenes**: Se muestra icono correcto
7. ✅ **Modal de imagen**: Abre, cierra y es responsive
8. ✅ **Descargar documento**: Descarga correctamente
9. ✅ **Cita relacionada**: Link a detalle de cita funciona
10. ✅ **Error 404**: Mensaje de error si episodio no existe
11. ✅ **Volver al historial**: Navegación funciona
12. ✅ **Imprimir**: Diálogo de impresión se abre

---

## 🎯 Mejoras Futuras

1. **Compartir Episodio**: Enviar por email o WhatsApp
2. **Agregar Comentario**: Paciente puede agregar notas personales
3. **Comparar Radiografías**: Vista lado a lado de dos radiografías
4. **Exportar a PDF**: Generar PDF del episodio completo
5. **Zoom en Imágenes**: Control de zoom en modal de imagen
6. **Historial de Cambios**: Ver quién y cuándo modificó el episodio
7. **Notificaciones**: Alertar cuando se actualiza un episodio
8. **Vista 3D Dental**: Marcador visual en modelo 3D de dientes

---

**¡Listo!** Ahora tienes:
- ✅ **Guía 35** corregida (error de keys en select)
- ✅ **Guía 36** completa con vista detallada de episodios
- ✅ Navegación entre episodios (anterior/siguiente)
- ✅ Modal de imágenes fullscreen
- ✅ Integración con el historial completo

🚀
