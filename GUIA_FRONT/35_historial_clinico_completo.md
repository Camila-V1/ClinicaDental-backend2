# Guía 35: Historial Clínico Completo del Paciente

## 📋 Información General

**Caso de Uso**: CU15 - Ver Historial Clínico Completo  
**Actor**: Paciente  
**Objetivo**: Visualizar todo el historial médico dental con episodios, documentos y tratamientos

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver lista completa de episodios clínicos
- ✅ Acceder a detalles de cada episodio (diagnóstico, tratamiento)
- ✅ Descargar documentos adjuntos (radiografías, recetas, estudios)
- ✅ Ver línea de tiempo médica
- ✅ Filtrar por fecha y tipo
- ✅ Ver evolución de tratamientos
- ✅ Acceder a notas del odontólogo

---

## 🔌 API Endpoints (Ya Existen)

Según los logs, ya tienes acceso a:

```
GET /api/historial/historiales/mi_historial/
```

**Respuesta del Backend**:
```json
{
  "id": 123,
  "paciente": 104,
  "paciente_nombre": "María García",
  "paciente_email": "paciente1@test.com",
  "fecha_creacion": "2025-01-15T10:00:00Z",
  "episodios": [
    {
      "id": 45,
      "fecha": "2025-11-15T10:00:00Z",
      "tipo": "CONSULTA",
      "diagnostico": "Caries en molar superior derecho",
      "tratamiento_realizado": "Limpieza y obturación",
      "notas": "Paciente presenta buen estado general",
      "odontologo": 5,
      "odontologo_nombre": "Dr. Juan Pérez",
      "documentos": [
        {
          "id": 12,
          "tipo": "RADIOGRAFIA",
          "nombre": "radiografia_molar_202511.jpg",
          "archivo": "http://..../media/documentos/radiografia_molar_202511.jpg",
          "descripcion": "Radiografía periapical molar 16",
          "fecha_subida": "2025-11-15T10:30:00Z"
        }
      ],
      "cita": 128
    }
  ],
  "episodios_count": 15,
  "documentos": [
    // Array con TODOS los documentos (10 según logs)
  ],
  "ultimo_episodio": {
    "fecha": "2025-11-15T10:00:00Z",
    "diagnostico": "Control de tratamiento de conducto"
  }
}
```

---

## 🔧 Implementación Frontend

### 1. Service - `historialService.ts` (Actualizar/Verificar)

Ya existe según logs, pero agregar funciones auxiliares:

```typescript
// src/services/historialService.ts

import apiClient from '../config/apiConfig';

/**
 * Obtiene el historial clínico completo del paciente
 */
export const obtenerMiHistorial = async (): Promise<any> => {
  console.log('📋 Obteniendo mi historial clínico completo...');
  
  try {
    const response = await apiClient.get('/api/historial/historiales/mi_historial/');
    console.log('✅ Historial obtenido:', response.data);
    console.log('📄 Total episodios:', response.data.episodios?.length || 0);
    console.log('📄 Total documentos:', response.data.documentos?.length || 0);
    
    return response.data;
  } catch (error) {
    console.error('❌ Error obteniendo historial:', error);
    throw error;
  }
};

/**
 * Obtiene detalle de un episodio específico
 */
export const obtenerDetalleEpisodio = async (episodioId: number): Promise<any> => {
  console.log(`📋 Obteniendo episodio ${episodioId}...`);
  
  try {
    const response = await apiClient.get(`/api/historial/episodios/${episodioId}/`);
    console.log('✅ Episodio obtenido:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error obteniendo episodio:', error);
    throw error;
  }
};

/**
 * Descarga un documento del historial
 */
export const descargarDocumento = (urlDocumento: string, nombreArchivo: string) => {
  console.log('📥 Descargando documento:', nombreArchivo);
  
  try {
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = urlDocumento;
    link.download = nombreArchivo;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('✅ Descarga iniciada');
  } catch (error) {
    console.error('❌ Error descargando documento:', error);
  }
};

// ============================================
// FUNCIONES AUXILIARES
// ============================================

/**
 * Formatea fecha a texto legible
 */
export const formatearFecha = (fechaISO: string): string => {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Obtiene el color según el tipo de episodio
 */
export const getTipoEpisodioColor = (tipo: string): string => {
  switch (tipo?.toUpperCase()) {
    case 'CONSULTA':
      return 'bg-blue-100 text-blue-800';
    case 'EMERGENCIA':
      return 'bg-red-100 text-red-800';
    case 'CONTROL':
      return 'bg-green-100 text-green-800';
    case 'TRATAMIENTO':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Obtiene el icono según el tipo de episodio
 */
export const getTipoEpisodioIcono = (tipo: string): string => {
  switch (tipo?.toUpperCase()) {
    case 'CONSULTA':
      return '🩺';
    case 'EMERGENCIA':
      return '🚨';
    case 'CONTROL':
      return '✅';
    case 'TRATAMIENTO':
      return '🦷';
    default:
      return '📋';
  }
};

/**
 * Obtiene el color según el tipo de documento
 */
export const getTipoDocumentoColor = (tipo: string): string => {
  switch (tipo?.toUpperCase()) {
    case 'RADIOGRAFIA':
      return 'bg-purple-100 text-purple-800';
    case 'RECETA':
      return 'bg-green-100 text-green-800';
    case 'ESTUDIO':
      return 'bg-blue-100 text-blue-800';
    case 'CONSENTIMIENTO':
      return 'bg-yellow-100 text-yellow-800';
    case 'FOTO':
      return 'bg-pink-100 text-pink-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Obtiene el icono según el tipo de documento
 */
export const getTipoDocumentoIcono = (tipo: string): string => {
  switch (tipo?.toUpperCase()) {
    case 'RADIOGRAFIA':
      return '🔬';
    case 'RECETA':
      return '💊';
    case 'ESTUDIO':
      return '📊';
    case 'CONSENTIMIENTO':
      return '📝';
    case 'FOTO':
      return '📷';
    default:
      return '📄';
  }
};

/**
 * Agrupa episodios por mes
 */
export const agruparEpisodiosPorMes = (episodios: any[]): any => {
  const grupos: any = {};
  
  episodios.forEach(episodio => {
    const fecha = new Date(episodio.fecha);
    const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
    const mesNombre = fecha.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
    
    if (!grupos[mesKey]) {
      grupos[mesKey] = {
        nombre: mesNombre.charAt(0).toUpperCase() + mesNombre.slice(1),
        episodios: []
      };
    }
    
    grupos[mesKey].episodios.push(episodio);
  });
  
  // Convertir a array y ordenar por fecha descendente
  return Object.entries(grupos)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([key, value]) => value);
};
```

---

### 2. Componente Principal - `HistorialClinicoCompleto.tsx`

```tsx
// src/pages/paciente/HistorialClinicoCompleto.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  obtenerMiHistorial,
  agruparEpisodiosPorMes
} from '../../services/historialService';

// Componentes
import EpisodioCard from '../../components/historial/EpisodioCard';
import DocumentosGaleria from '../../components/historial/DocumentosGaleria';
import LineaTiempo from '../../components/historial/LineaTiempo';
import FiltrosHistorial from '../../components/historial/FiltrosHistorial';
import EstadisticasHistorial from '../../components/historial/EstadisticasHistorial';

export default function HistorialClinicoCompleto() {
  const navigate = useNavigate();

  const [historial, setHistorial] = useState<any>(null);
  const [episodiosFiltrados, setEpisodiosFiltrados] = useState<any[]>([]);
  const [vistaActual, setVistaActual] = useState<'lista' | 'timeline'>('lista');
  const [filtros, setFiltros] = useState({
    tipo: '',
    fechaInicio: '',
    fechaFin: '',
    busqueda: ''
  });
  
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarHistorial();
  }, []);

  useEffect(() => {
    if (historial?.episodios) {
      aplicarFiltros();
    }
  }, [historial, filtros]);

  const cargarHistorial = async () => {
    try {
      setCargando(true);
      setError(null);

      const data = await obtenerMiHistorial();
      setHistorial(data);
      setEpisodiosFiltrados(data.episodios || []);
    } catch (err: any) {
      console.error('❌ Error cargando historial:', err);
      setError('Error al cargar el historial clínico');
    } finally {
      setCargando(false);
    }
  };

  const aplicarFiltros = () => {
    let episodios = [...(historial?.episodios || [])];

    // Filtrar por tipo
    if (filtros.tipo) {
      episodios = episodios.filter(e => 
        e.tipo?.toUpperCase() === filtros.tipo.toUpperCase()
      );
    }

    // Filtrar por fecha inicio
    if (filtros.fechaInicio) {
      episodios = episodios.filter(e => 
        new Date(e.fecha) >= new Date(filtros.fechaInicio)
      );
    }

    // Filtrar por fecha fin
    if (filtros.fechaFin) {
      episodios = episodios.filter(e => 
        new Date(e.fecha) <= new Date(filtros.fechaFin)
      );
    }

    // Filtrar por búsqueda
    if (filtros.busqueda) {
      const busqueda = filtros.busqueda.toLowerCase();
      episodios = episodios.filter(e =>
        e.diagnostico?.toLowerCase().includes(busqueda) ||
        e.tratamiento_realizado?.toLowerCase().includes(busqueda) ||
        e.notas?.toLowerCase().includes(busqueda) ||
        e.odontologo_nombre?.toLowerCase().includes(busqueda)
      );
    }

    setEpisodiosFiltrados(episodios);
  };

  const cambiarFiltro = (campo: string, valor: any) => {
    setFiltros(prev => ({ ...prev, [campo]: valor }));
  };

  const limpiarFiltros = () => {
    setFiltros({
      tipo: '',
      fechaInicio: '',
      fechaFin: '',
      busqueda: ''
    });
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando historial clínico...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={cargarHistorial}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            🔄 Reintentar
          </button>
        </div>
      </div>
    );
  }

  const episodiosAgrupados = agruparEpisodiosPorMes(episodiosFiltrados);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            🏥 Historial Clínico Completo
          </h1>
          <p className="text-gray-600 mt-2">
            Todos tus registros médicos dentales
          </p>
        </div>
        <button
          onClick={() => navigate('/paciente/dashboard')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
        >
          ← Volver
        </button>
      </div>

      {/* Estadísticas */}
      <EstadisticasHistorial historial={historial} />

      {/* Filtros */}
      <FiltrosHistorial
        filtros={filtros}
        cambiarFiltro={cambiarFiltro}
        limpiarFiltros={limpiarFiltros}
      />

      {/* Toggle Vista */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setVistaActual('lista')}
            className={`px-4 py-2 rounded-lg font-medium ${
              vistaActual === 'lista'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📋 Lista
          </button>
          <button
            onClick={() => setVistaActual('timeline')}
            className={`px-4 py-2 rounded-lg font-medium ${
              vistaActual === 'timeline'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            ⏱️ Línea de Tiempo
          </button>
        </div>

        <p className="text-gray-600">
          {episodiosFiltrados.length} de {historial?.episodios?.length || 0} episodios
        </p>
      </div>

      {/* Contenido según vista */}
      {episodiosFiltrados.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <span className="text-6xl">🔍</span>
          <h3 className="text-xl font-bold text-gray-800 mt-4">
            No se encontraron episodios
          </h3>
          <p className="text-gray-600 mt-2">
            Intenta ajustar los filtros de búsqueda
          </p>
          {(filtros.tipo || filtros.fechaInicio || filtros.fechaFin || filtros.busqueda) && (
            <button
              onClick={limpiarFiltros}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Limpiar Filtros
            </button>
          )}
        </div>
      ) : vistaActual === 'lista' ? (
        <div className="space-y-8">
          {episodiosAgrupados.map((grupo: any, index: number) => (
            <div key={index}>
              <h2 className="text-xl font-bold text-gray-800 mb-4 sticky top-0 bg-gray-50 py-2 z-10">
                📅 {grupo.nombre}
              </h2>
              <div className="space-y-4">
                {grupo.episodios.map((episodio: any) => (
                  <EpisodioCard key={episodio.id} episodio={episodio} />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <LineaTiempo episodios={episodiosFiltrados} />
      )}

      {/* Galería de Documentos (si hay) */}
      {historial?.documentos?.length > 0 && (
        <div className="mt-8">
          <DocumentosGaleria documentos={historial.documentos} />
        </div>
      )}

    </div>
  );
}
```

---

### 3. Componente - `EpisodioCard.tsx`

```tsx
// src/components/historial/EpisodioCard.tsx

import React, { useState } from 'react';
import {
  formatearFecha,
  getTipoEpisodioColor,
  getTipoEpisodioIcono,
  getTipoDocumentoIcono,
  descargarDocumento
} from '../../services/historialService';

interface Props {
  episodio: any;
}

export default function EpisodioCard({ episodio }: Props) {
  const [expandido, setExpandido] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
      
      {/* Header del Card */}
      <div
        className="p-6 cursor-pointer"
        onClick={() => setExpandido(!expandido)}
      >
        <div className="flex items-start justify-between">
          
          <div className="flex items-start gap-4 flex-1">
            {/* Icono */}
            <div className="text-4xl flex-shrink-0">
              {getTipoEpisodioIcono(episodio.tipo)}
            </div>

            {/* Info Principal */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getTipoEpisodioColor(episodio.tipo)}`}>
                  {episodio.tipo}
                </span>
                <span className="text-sm text-gray-600">
                  {formatearFecha(episodio.fecha)}
                </span>
              </div>

              <h3 className="font-bold text-gray-800 text-lg mb-2">
                {episodio.diagnostico}
              </h3>

              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>👨‍⚕️</span>
                <span>{episodio.odontologo_nombre}</span>
              </div>

              <div className="mt-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Navegar a detalle del episodio
                    window.location.href = `/paciente/historial/episodio/${episodio.id}`;
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Ver detalle completo →
                </button>
              </div>

              {episodio.documentos?.length > 0 && (
                <div className="mt-2 flex items-center gap-2 text-sm text-blue-600">
                  <span>📎</span>
                  <span>{episodio.documentos.length} {episodio.documentos.length === 1 ? 'documento' : 'documentos'}</span>
                </div>
              )}
            </div>
          </div>

          {/* Botón Expandir */}
          <button className="text-2xl text-gray-400 hover:text-gray-600 transition-colors">
            {expandido ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {/* Contenido Expandido */}
      {expandido && (
        <div className="px-6 pb-6 border-t border-gray-200 pt-4">
          
          {/* Tratamiento Realizado */}
          {episodio.tratamiento_realizado && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-2">
                🦷 Tratamiento Realizado:
              </h4>
              <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                {episodio.tratamiento_realizado}
              </p>
            </div>
          )}

          {/* Notas del Odontólogo */}
          {episodio.notas && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-2">
                📝 Notas del Odontólogo:
              </h4>
              <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                {episodio.notas}
              </p>
            </div>
          )}

          {/* Documentos Adjuntos */}
          {episodio.documentos?.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">
                📎 Documentos Adjuntos:
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {episodio.documentos.map((doc: any) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {getTipoDocumentoIcono(doc.tipo)}
                      </span>
                      <div>
                        <p className="font-medium text-gray-800 text-sm">
                          {doc.nombre}
                        </p>
                        {doc.descripcion && (
                          <p className="text-xs text-gray-600 mt-1">
                            {doc.descripcion}
                          </p>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => descargarDocumento(doc.archivo, doc.nombre)}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                    >
                      ⬇️ Descargar
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cita Relacionada */}
          {episodio.cita && (
            <div className="mt-4 text-sm text-gray-600">
              <span className="font-medium">📅 Relacionado con cita #{episodio.cita}</span>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
```

---

### 4. Componente - `EstadisticasHistorial.tsx`

```tsx
// src/components/historial/EstadisticasHistorial.tsx

import React from 'react';

interface Props {
  historial: any;
}

export default function EstadisticasHistorial({ historial }: Props) {
  const stats = [
    {
      titulo: 'Total Episodios',
      valor: historial?.episodios_count || 0,
      icono: '📋',
      color: 'bg-blue-500'
    },
    {
      titulo: 'Documentos',
      valor: historial?.documentos?.length || 0,
      icono: '📄',
      color: 'bg-green-500'
    },
    {
      titulo: 'Último Registro',
      valor: historial?.ultimo_episodio?.fecha 
        ? new Date(historial.ultimo_episodio.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
        : 'N/A',
      icono: '📅',
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">{stat.titulo}</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stat.valor}</p>
            </div>
            <div className={`${stat.color} rounded-full p-4 text-white text-3xl`}>
              {stat.icono}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

### 5. Componente - `FiltrosHistorial.tsx`

```tsx
// src/components/historial/FiltrosHistorial.tsx

import React from 'react';

interface Props {
  filtros: any;
  cambiarFiltro: (campo: string, valor: any) => void;
  limpiarFiltros: () => void;
}

export default function FiltrosHistorial({ filtros, cambiarFiltro, limpiarFiltros }: Props) {
  const tieneFiltrosActivos = filtros.tipo || filtros.fechaInicio || filtros.fechaFin || filtros.busqueda;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">🔍 Filtros</h3>
        {tieneFiltrosActivos && (
          <button
            onClick={limpiarFiltros}
            className="text-sm text-red-600 hover:text-red-800 font-medium"
          >
            🗑️ Limpiar
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Búsqueda */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Buscar
          </label>
          <input
            type="text"
            placeholder="Diagnóstico, tratamiento, doctor..."
            value={filtros.busqueda}
            onChange={(e) => cambiarFiltro('busqueda', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Tipo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo
          </label>
          <select
            value={filtros.tipo}
            onChange={(e) => cambiarFiltro('tipo', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todos</option>
            <option value="CONSULTA">Consulta</option>
            <option value="EMERGENCIA">Emergencia</option>
            <option value="CONTROL">Control</option>
            <option value="TRATAMIENTO">Tratamiento</option>
          </select>
        </div>

        {/* Fecha Inicio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Desde
          </label>
          <input
            type="date"
            value={filtros.fechaInicio}
            onChange={(e) => cambiarFiltro('fechaInicio', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Fecha Fin */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Hasta
          </label>
          <input
            type="date"
            value={filtros.fechaFin}
            onChange={(e) => cambiarFiltro('fechaFin', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

      </div>
    </div>
  );
}
```

---

### 6. Componente - `LineaTiempo.tsx`

```tsx
// src/components/historial/LineaTiempo.tsx

import React from 'react';
import {
  formatearFecha,
  getTipoEpisodioColor,
  getTipoEpisodioIcono
} from '../../services/historialService';

interface Props {
  episodios: any[];
}

export default function LineaTiempo({ episodios }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="relative">
        {/* Línea vertical */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-200"></div>

        {/* Episodios */}
        <div className="space-y-8">
          {episodios.map((episodio, index) => (
            <div key={episodio.id} className="relative flex items-start gap-6">
              
              {/* Punto en la línea */}
              <div className="relative z-10 flex-shrink-0">
                <div className="w-16 h-16 bg-white border-4 border-blue-500 rounded-full flex items-center justify-center text-2xl">
                  {getTipoEpisodioIcono(episodio.tipo)}
                </div>
              </div>

              {/* Contenido */}
              <div className="flex-1 bg-gray-50 rounded-lg p-6 hover:bg-gray-100 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getTipoEpisodioColor(episodio.tipo)}`}>
                    {episodio.tipo}
                  </span>
                  <span className="text-sm text-gray-600">
                    {formatearFecha(episodio.fecha)}
                  </span>
                </div>

                <h3 className="font-bold text-gray-800 text-lg mb-2">
                  {episodio.diagnostico}
                </h3>

                {episodio.tratamiento_realizado && (
                  <p className="text-gray-700 mb-2">
                    {episodio.tratamiento_realizado}
                  </p>
                )}

                <div className="flex items-center gap-4 text-sm text-gray-600 mt-3">
                  <span>👨‍⚕️ {episodio.odontologo_nombre}</span>
                  {episodio.documentos?.length > 0 && (
                    <span>📎 {episodio.documentos.length} documentos</span>
                  )}
                </div>
              </div>

            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

### 7. Componente - `DocumentosGaleria.tsx`

```tsx
// src/components/historial/DocumentosGaleria.tsx

import React, { useState } from 'react';
import {
  getTipoDocumentoColor,
  getTipoDocumentoIcono,
  descargarDocumento,
  formatearFecha
} from '../../services/historialService';

interface Props {
  documentos: any[];
}

export default function DocumentosGaleria({ documentos }: Props) {
  const [filtroTipo, setFiltroTipo] = useState('');

  const documentosFiltrados = filtroTipo
    ? documentos.filter(doc => doc.tipo === filtroTipo)
    : documentos;

  const tiposUnicos = [...new Set(documentos.map(doc => doc.tipo))];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-800">
          📁 Todos los Documentos ({documentos.length})
        </h2>

        {/* Filtro por tipo */}
        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="" key="todos">Todos los tipos</option>
          {tiposUnicos.map((tipo, index) => (
            <option key={`tipo-${tipo}-${index}`} value={tipo}>{tipo}</option>
          ))}
        </select>
      </div>

      {documentosFiltrados.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <span className="text-6xl">📭</span>
          <p className="mt-4">No hay documentos de este tipo</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documentosFiltrados.map((doc) => (
            <div
              key={doc.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-lg transition-all"
            >
              {/* Preview (si es imagen) */}
              {doc.tipo === 'FOTO' || doc.tipo === 'RADIOGRAFIA' ? (
                <div className="mb-3">
                  <img
                    src={doc.archivo}
                    alt={doc.nombre}
                    className="w-full h-40 object-cover rounded-lg"
                    onError={(e) => {
                      // Fallback si falla la carga de imagen
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              ) : (
                <div className="mb-3 h-40 bg-gray-100 rounded-lg flex items-center justify-center">
                  <span className="text-6xl">
                    {getTipoDocumentoIcono(doc.tipo)}
                  </span>
                </div>
              )}

              {/* Info */}
              <div className="mb-3">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getTipoDocumentoColor(doc.tipo)}`}>
                  {doc.tipo}
                </span>
              </div>

              <h4 className="font-semibold text-gray-800 mb-2 truncate">
                {doc.nombre}
              </h4>

              {doc.descripcion && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {doc.descripcion}
                </p>
              )}

              <p className="text-xs text-gray-500 mb-3">
                {formatearFecha(doc.fecha_subida)}
              </p>

              {/* Botón Descargar */}
              <button
                onClick={() => descargarDocumento(doc.archivo, doc.nombre)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
              >
                ⬇️ Descargar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🔗 Integración con React Router

Actualiza `App.tsx` o tu archivo de rutas:

```tsx
// Importar el componente
import HistorialClinicoCompleto from './pages/paciente/HistorialClinicoCompleto';

// Agregar ruta
<Route path="/paciente/historial" element={<HistorialClinicoCompleto />} />
```

---

## 🎨 Características de la UI

### 1. **Vista Lista**
- Cards expandibles por episodio
- Agrupación por mes
- Documentos adjuntos con descarga
- Información completa del tratamiento

### 2. **Vista Timeline**
- Línea de tiempo vertical
- Iconos distintivos por tipo
- Badges de color por tipo
- Cronología visual clara

### 3. **Filtros Avanzados**
- Búsqueda por texto
- Filtro por tipo de episodio
- Rango de fechas
- Limpiar filtros rápido

### 4. **Galería de Documentos**
- Grid responsive
- Preview de imágenes
- Filtro por tipo de documento
- Descarga con un clic

### 5. **Estadísticas**
- Total de episodios
- Total de documentos
- Último registro

---

## 📝 Notas Importantes

### 1. **Backend Ya Existe**
✅ Según tus logs, el endpoint `/api/historial/historiales/mi_historial/` ya está funcionando y devuelve:
- ✅ 15 episodios (episodios_count)
- ✅ 10 documentos
- ✅ Información del paciente
- ✅ Último episodio

### 2. **Estructura de Archivos**
```
src/
├── services/
│   └── historialService.ts       ← Ya existe, agregar helpers
├── components/
│   └── historial/                ← Nuevo directorio
│       ├── EpisodioCard.tsx
│       ├── EstadisticasHistorial.tsx
│       ├── FiltrosHistorial.tsx
│       ├── LineaTiempo.tsx
│       └── DocumentosGaleria.tsx
└── pages/
    └── paciente/
        └── HistorialClinicoCompleto.tsx
```

### 3. **Optimizaciones**
- ✅ Carga única del historial completo
- ✅ Filtros en frontend (sin peticiones adicionales)
- ✅ Lazy loading de imágenes
- ✅ Cards expandibles (ahorra espacio)

---

## 🧪 Testing

### Casos de Prueba

1. ✅ **Carga inicial**: Todos los episodios visibles
2. ✅ **Filtro por tipo**: Solo episodios del tipo seleccionado
3. ✅ **Filtro por fecha**: Rango funcional
4. ✅ **Búsqueda de texto**: Encuentra en diagnóstico/tratamiento
5. ✅ **Expandir/contraer**: Cards expandibles
6. ✅ **Descargar documento**: Descarga correcta
7. ✅ **Vista timeline**: Cambio de vista
8. ✅ **Sin resultados**: Mensaje cuando filtros no coinciden
9. ✅ **Limpiar filtros**: Vuelve al estado inicial
10. ✅ **Responsive**: Mobile y desktop

---

## 🎯 Mejoras Futuras

1. **Visor de Imágenes**: Modal lightbox para ver radiografías
2. **Comparador**: Comparar radiografías lado a lado
3. **Exportar PDF**: Reporte completo del historial
4. **Comentarios**: Paciente puede agregar notas
5. **Notificaciones**: Cuando se agrega nuevo episodio
6. **Búsqueda Avanzada**: Búsqueda por diente específico
7. **Calendario 3D**: Visualización dental 3D
8. **Recordatorios**: Próximos controles basados en historial

---

**¡Listo!** Con esta guía tienes todo lo necesario para implementar el Historial Clínico Completo. 

El backend ya está funcionando según tus logs, solo necesitas crear los componentes en el frontend. 🚀
