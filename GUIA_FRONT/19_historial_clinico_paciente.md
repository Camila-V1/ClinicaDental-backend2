1# Guía 19: Historial Clínico para Pacientes

## Objetivo
Implementar la página de Historial Clínico del paciente que muestra episodios de atención, documentos clínicos, odontograma y alergias/medicamentos.

## Endpoint Backend

### GET /api/historial/historiales/mi_historial/
**Respuesta exitosa (200):**
```json
{
  "id": 77,
  "paciente": 104,
  "paciente_info": {
    "id": 104,
    "nombre": "María",
    "apellido": "García",
    "email": "paciente1@test.com"
  },
  "fecha_apertura": "2025-10-15T00:00:00Z",
  "alergias": "Penicilina",
  "medicamentos_actuales": "Ibuprofeno",
  "antecedentes_medicos": "Hipertensión controlada",
  "observaciones_generales": "Paciente colaborador",
  "odontograma": {
    "id": 77,
    "estado_piezas": {
      "11": {"estado": "sano"},
      "12": {"estado": "sano"},
      "21": {"estado": "caries", "observacion": "Caries en cara oclusal"},
      "22": {"estado": "sano"}
    },
    "observaciones": "Odontograma actualizado 15/10/2025",
    "fecha_ultima_actualizacion": "2025-10-15T10:00:00Z"
  },
  "episodios": [
    {
      "id": 150,
      "fecha_atencion": "2025-10-15T10:00:00Z",
      "odontologo": 103,
      "odontologo_nombre": "Dr. Juan Pérez",
      "motivo_consulta": "Control preventivo",
      "diagnostico": "Caries en pieza 21",
      "tratamiento_realizado": "Limpieza dental y aplicación de flúor",
      "observaciones": "Paciente requiere seguimiento",
      "proxima_cita": null,
      "cita": 125
    }
  ]
}
```

### GET /api/historial/episodios/mis_episodios/
**Descripción:** Lista todos los episodios del paciente (alternativa al nested en mi_historial)
**Respuesta:** Array de episodios

### GET /api/historial/documentos/?historial_clinico=77
**Descripción:** Documentos clínicos del historial
**Respuesta:**
```json
[
  {
    "id": 10,
    "tipo_documento": "RADIOGRAFIA",
    "descripcion": "Radiografía panorámica",
    "archivo": "http://clinica-demo.localhost:8000/media/documentos/panoramica.jpg",
    "creado": "2025-10-15T10:30:00Z",
    "episodio": 150
  }
]
```

## Estructura de Archivos Frontend

```
src/
├── services/
│   └── historialService.ts          # Servicio para endpoints de historial
├── pages/
│   └── paciente/
│       └── HistorialPage.tsx        # Página principal
└── components/
    └── paciente/
        └── historial/
            ├── ResumenHistorial.tsx      # Datos generales del historial
            ├── ListaEpisodios.tsx        # Lista de episodios de atención
            ├── DetalleEpisodio.tsx       # Modal con detalle de un episodio
            ├── VisorOdontograma.tsx      # Visualización del odontograma
            └── DocumentosClinicos.tsx    # Lista de documentos adjuntos
```

## Paso 1: Crear Servicio de Historial

**Archivo:** `src/services/historialService.ts`

```typescript
import apiClient from '../api/apiConfig';

// ============================================
// TIPOS E INTERFACES
// ============================================

export interface OdontogramaDetalle {
  id: number;
  estado_piezas: {
    [pieza: string]: {
      estado: 'sano' | 'caries' | 'obturado' | 'extraido' | 'endodoncia' | 'protesis';
      observacion?: string;
    };
  };
  observaciones: string;
  fecha_ultima_actualizacion: string;
}

export interface EpisodioAtencion {
  id: number;
  fecha_atencion: string;
  odontologo: number;
  odontologo_nombre: string;
  motivo_consulta: string;
  diagnostico: string;
  tratamiento_realizado: string;
  observaciones: string;
  proxima_cita: number | null;
  cita: number | null;
}

export interface HistorialClinico {
  id: number;
  paciente: number;
  paciente_info: {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
  };
  fecha_apertura: string;
  alergias: string;
  medicamentos_actuales: string;
  antecedentes_medicos: string;
  observaciones_generales: string;
  odontograma: OdontogramaDetalle;
  episodios: EpisodioAtencion[];
}

export interface DocumentoClinico {
  id: number;
  tipo_documento: string;
  descripcion: string;
  archivo: string;
  creado: string;
  episodio: number | null;
}

// ============================================
// FUNCIONES DE SERVICIO
// ============================================

/**
 * Obtener el historial clínico completo del paciente autenticado
 */
export const obtenerMiHistorial = async (): Promise<HistorialClinico> => {
  console.log('📋 Obteniendo mi historial clínico...');
  
  const response = await apiClient.get<HistorialClinico>(
    '/api/historial/historiales/mi_historial/'
  );
  
  console.log('✅ Historial obtenido:', response.data);
  return response.data;
};

/**
 * Obtener todos los episodios del paciente
 */
export const obtenerMisEpisodios = async (): Promise<EpisodioAtencion[]> => {
  console.log('📋 Obteniendo mis episodios de atención...');
  
  const response = await apiClient.get<EpisodioAtencion[]>(
    '/api/historial/episodios/mis_episodios/'
  );
  
  console.log(`✅ ${response.data.length} episodios obtenidos`);
  return response.data;
};

/**
 * Obtener documentos clínicos de un historial
 */
export const obtenerDocumentosHistorial = async (
  historialId: number
): Promise<DocumentoClinico[]> => {
  console.log(`📄 Obteniendo documentos del historial ${historialId}...`);
  
  const response = await apiClient.get<DocumentoClinico[]>(
    '/api/historial/documentos/',
    { params: { historial_clinico: historialId } }
  );
  
  console.log(`✅ ${response.data.length} documentos obtenidos`);
  return response.data;
};

/**
 * Descargar un documento clínico
 */
export const descargarDocumento = (archivoUrl: string): void => {
  window.open(archivoUrl, '_blank');
};
```

## Paso 2: Componente Resumen del Historial

**Archivo:** `src/components/paciente/historial/ResumenHistorial.tsx`

```typescript
import React from 'react';
import { HistorialClinico } from '../../../services/historialService';
import { AlertCircle, Pill, FileText, Calendar } from 'lucide-react';

interface Props {
  historial: HistorialClinico;
}

export const ResumenHistorial: React.FC<Props> = ({ historial }) => {
  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Información General
      </h2>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Fecha de apertura */}
        <div className="flex items-start space-x-3">
          <Calendar className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
          <div>
            <p className="text-sm text-gray-600">Fecha de Apertura</p>
            <p className="font-medium text-gray-900">
              {formatearFecha(historial.fecha_apertura)}
            </p>
          </div>
        </div>

        {/* Alergias */}
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-gray-600">Alergias</p>
            <p className="font-medium text-gray-900">
              {historial.alergias || 'Ninguna registrada'}
            </p>
          </div>
        </div>

        {/* Medicamentos actuales */}
        <div className="flex items-start space-x-3">
          <Pill className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-gray-600">Medicamentos Actuales</p>
            <p className="font-medium text-gray-900">
              {historial.medicamentos_actuales || 'Ninguno'}
            </p>
          </div>
        </div>

        {/* Antecedentes médicos */}
        <div className="flex items-start space-x-3">
          <FileText className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-gray-600">Antecedentes Médicos</p>
            <p className="font-medium text-gray-900">
              {historial.antecedentes_medicos || 'Ninguno'}
            </p>
          </div>
        </div>
      </div>

      {/* Observaciones generales */}
      {historial.observaciones_generales && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm font-medium text-blue-900 mb-2">
            Observaciones Generales
          </p>
          <p className="text-sm text-blue-800">
            {historial.observaciones_generales}
          </p>
        </div>
      )}
    </div>
  );
};
```

## Paso 3: Lista de Episodios

**Archivo:** `src/components/paciente/historial/ListaEpisodios.tsx`

```typescript
import React, { useState } from 'react';
import { EpisodioAtencion } from '../../../services/historialService';
import { Calendar, User, FileText, ChevronRight } from 'lucide-react';
import { DetalleEpisodio } from './DetalleEpisodio';

interface Props {
  episodios: EpisodioAtencion[];
}

export const ListaEpisodios: React.FC<Props> = ({ episodios }) => {
  const [episodioSeleccionado, setEpisodioSeleccionado] = useState<EpisodioAtencion | null>(null);

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (episodios.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-600 text-lg">No hay episodios de atención registrados</p>
        <p className="text-gray-400 text-sm mt-2">
          Los episodios aparecerán aquí después de cada consulta
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800">
            Episodios de Atención
          </h2>
          <p className="text-gray-600 mt-1">
            {episodios.length} {episodios.length === 1 ? 'episodio' : 'episodios'} registrados
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {episodios.map((episodio) => (
            <div
              key={episodio.id}
              onClick={() => setEpisodioSeleccionado(episodio)}
              className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {/* Fecha y odontólogo */}
                  <div className="flex items-center space-x-4 mb-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="w-4 h-4 mr-2" />
                      {formatearFecha(episodio.fecha_atencion)}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <User className="w-4 h-4 mr-2" />
                      {episodio.odontologo_nombre}
                    </div>
                  </div>

                  {/* Motivo de consulta */}
                  <p className="font-medium text-gray-900 mb-2">
                    {episodio.motivo_consulta}
                  </p>

                  {/* Diagnóstico (preview) */}
                  <p className="text-sm text-gray-600 line-clamp-2">
                    <span className="font-medium">Diagnóstico:</span> {episodio.diagnostico}
                  </p>
                </div>

                <ChevronRight className="w-5 h-5 text-gray-400 ml-4 flex-shrink-0" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de detalle */}
      {episodioSeleccionado && (
        <DetalleEpisodio
          episodio={episodioSeleccionado}
          onClose={() => setEpisodioSeleccionado(null)}
        />
      )}
    </>
  );
};
```

## Paso 4: Detalle de Episodio (Modal)

**Archivo:** `src/components/paciente/historial/DetalleEpisodio.tsx`

```typescript
import React from 'react';
import { EpisodioAtencion } from '../../../services/historialService';
import { X, Calendar, User, FileText, Stethoscope, Pill } from 'lucide-react';

interface Props {
  episodio: EpisodioAtencion;
  onClose: () => void;
}

export const DetalleEpisodio: React.FC<Props> = ({ episodio, onClose }) => {
  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            Detalle del Episodio
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Contenido */}
        <div className="p-6 space-y-6">
          {/* Información básica */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Fecha de Atención</p>
                <p className="font-medium text-gray-900">
                  {formatearFecha(episodio.fecha_atencion)}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <User className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Odontólogo</p>
                <p className="font-medium text-gray-900">
                  {episodio.odontologo_nombre}
                </p>
              </div>
            </div>
          </div>

          {/* Motivo de consulta */}
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <FileText className="w-5 h-5 text-blue-600 mt-1" />
              <div className="flex-1">
                <p className="font-medium text-blue-900 mb-1">Motivo de Consulta</p>
                <p className="text-blue-800">{episodio.motivo_consulta}</p>
              </div>
            </div>
          </div>

          {/* Diagnóstico */}
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Stethoscope className="w-5 h-5 text-purple-600 mt-1" />
              <div className="flex-1">
                <p className="font-medium text-purple-900 mb-1">Diagnóstico</p>
                <p className="text-purple-800">{episodio.diagnostico}</p>
              </div>
            </div>
          </div>

          {/* Tratamiento realizado */}
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Pill className="w-5 h-5 text-green-600 mt-1" />
              <div className="flex-1">
                <p className="font-medium text-green-900 mb-1">Tratamiento Realizado</p>
                <p className="text-green-800">{episodio.tratamiento_realizado}</p>
              </div>
            </div>
          </div>

          {/* Observaciones */}
          {episodio.observaciones && (
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium text-gray-900 mb-2">Observaciones</p>
              <p className="text-gray-700">{episodio.observaciones}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};
```

## Paso 5: Página Principal de Historial

**Archivo:** `src/pages/paciente/HistorialPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { ResumenHistorial } from '../../components/paciente/historial/ResumenHistorial';
import { ListaEpisodios } from '../../components/paciente/historial/ListaEpisodios';
import { 
  HistorialClinico, 
  obtenerMiHistorial 
} from '../../services/historialService';
import { Loader2, AlertCircle } from 'lucide-react';

export const HistorialPage: React.FC = () => {
  const [historial, setHistorial] = useState<HistorialClinico | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarHistorial();
  }, []);

  const cargarHistorial = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await obtenerMiHistorial();
      setHistorial(data);
    } catch (err: any) {
      console.error('❌ Error al cargar historial:', err);
      setError(err.response?.data?.detail || 'Error al cargar el historial clínico');
    } finally {
      setCargando(false);
    }
  };

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Cargando historial clínico...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-red-900 font-medium mb-1">Error al cargar historial</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={cargarHistorial}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Intentar nuevamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!historial) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">No se encontró historial clínico</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Mi Historial Clínico
      </h1>

      <div className="space-y-6">
        {/* Resumen general */}
        <ResumenHistorial historial={historial} />

        {/* Lista de episodios */}
        <ListaEpisodios episodios={historial.episodios} />
      </div>
    </div>
  );
};
```

## Paso 6: Registrar Ruta

**Archivo:** `src/App.tsx`

```typescript
import { HistorialPage } from './pages/paciente/HistorialPage';

// Dentro de las rutas protegidas de paciente:
<Route path="/paciente/historial" element={<HistorialPage />} />
```

## Verificación

1. **Login como paciente:** paciente1@test.com / password123
2. **Navegar a:** http://clinica-demo.localhost:5173/paciente/historial
3. **Verificar:**
   - ✅ Se muestra la información general (alergias, medicamentos)
   - ✅ Se listan los 8 episodios de atención
   - ✅ Al hacer clic en un episodio se abre el modal con detalles
   - ✅ No hay errores en consola

## Próximos Pasos

Una vez verificado el historial, puedes agregar:
- Visor de odontograma interactivo
- Galería de documentos clínicos
- Filtros por fecha/odontólogo
- Impresión del historial en PDF
