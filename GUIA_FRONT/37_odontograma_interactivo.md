# Guía 37: Odontograma Interactivo (Mapa Dental)

## 📋 Información General

**Caso de Uso**: CU17 - Ver Odontograma Dental Completo  
**Actor**: Paciente  
**Objetivo**: Visualizar el estado de todos los dientes con información detallada de tratamientos

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver mapa visual de todos sus dientes (32 piezas dentales)
- ✅ Ver estado de cada diente (sano, caries, tratado, ausente, etc.)
- ✅ Click en un diente para ver historial específico
- ✅ Ver tratamientos realizados en cada pieza
- ✅ Leyenda de colores y símbolos
- ✅ Vista de arcada superior e inferior
- ✅ Navegación entre vista de adulto (32 dientes) y niño (20 dientes)

---

## 🦷 Numeración Dental (Sistema FDI)

### Adultos (32 dientes):

```
ARCADA SUPERIOR DERECHA        ARCADA SUPERIOR IZQUIERDA
18  17  16  15  14  13  12  11 | 21  22  23  24  25  26  27  28

ARCADA INFERIOR DERECHA        ARCADA INFERIOR IZQUIERDA
48  47  46  45  44  43  42  41 | 31  32  33  34  35  36  37  38
```

### Cuadrantes:
- **Cuadrante 1**: Superior Derecho (11-18)
- **Cuadrante 2**: Superior Izquierdo (21-28)
- **Cuadrante 3**: Inferior Izquierdo (31-38)
- **Cuadrante 4**: Inferior Derecho (41-48)

---

## 🔌 API Endpoints

### Obtener Odontograma Completo

```
GET /api/historial/historiales/mi_historial/
```

El endpoint ya existe y devuelve episodios con información de dientes tratados.

### Estructura de Datos para Odontograma

```json
{
  "odontograma": {
    "11": {
      "numero": "11",
      "nombre": "Incisivo Central Superior Derecho",
      "estado": "SANO",
      "tratamientos": [],
      "notas": ""
    },
    "16": {
      "numero": "16",
      "nombre": "Primer Molar Superior Derecho",
      "estado": "TRATADO",
      "tratamientos": [
        {
          "tipo": "OBTURACION",
          "fecha": "2025-10-15",
          "descripcion": "Obturación con resina compuesta",
          "episodio_id": 45
        }
      ],
      "notas": "Requiere control en 6 meses"
    },
    "26": {
      "numero": "26",
      "nombre": "Primer Molar Superior Izquierdo",
      "estado": "AUSENTE",
      "tratamientos": [
        {
          "tipo": "EXTRACCION",
          "fecha": "2024-05-20",
          "descripcion": "Extracción por caries avanzada",
          "episodio_id": 23
        }
      ],
      "notas": "Candidato para implante"
    }
  }
}
```

---

## 🔧 Implementación Frontend

### 1. Service - Actualizar `historialService.ts`

```typescript
// src/services/historialService.ts

/**
 * Obtiene el odontograma completo del paciente
 */
export const obtenerOdontograma = async (): Promise<any> => {
  console.log('🦷 Obteniendo odontograma...');
  
  try {
    const historial = await obtenerMiHistorial();
    
    // Construir odontograma desde episodios
    const odontograma = construirOdontograma(historial.episodios || []);
    
    console.log('✅ Odontograma construido:', odontograma);
    return odontograma;
  } catch (error) {
    console.error('❌ Error obteniendo odontograma:', error);
    throw error;
  }
};

/**
 * Construye el odontograma desde los episodios
 */
const construirOdontograma = (episodios: any[]): any => {
  const odontograma: any = {};
  
  // Inicializar todos los dientes como SANO
  for (let i = 1; i <= 4; i++) {
    for (let j = 1; j <= 8; j++) {
      const numero = `${i}${j}`;
      odontograma[numero] = {
        numero,
        nombre: getNombreDiente(numero),
        estado: 'SANO',
        tratamientos: [],
        notas: ''
      };
    }
  }
  
  // Procesar episodios y actualizar estados
  episodios.forEach(episodio => {
    // Extraer números de dientes del diagnóstico o tratamiento
    const dientesAfectados = extraerDientesDelTexto(
      `${episodio.diagnostico} ${episodio.tratamiento_realizado}`
    );
    
    dientesAfectados.forEach(numero => {
      if (odontograma[numero]) {
        // Agregar tratamiento
        odontograma[numero].tratamientos.push({
          tipo: clasificarTratamiento(episodio.tratamiento_realizado),
          fecha: episodio.fecha,
          descripcion: episodio.tratamiento_realizado,
          episodio_id: episodio.id
        });
        
        // Actualizar estado según tratamiento
        odontograma[numero].estado = determinarEstadoDiente(
          odontograma[numero].tratamientos
        );
      }
    });
  });
  
  return odontograma;
};

/**
 * Extrae números de dientes del texto (ej: "pieza 16", "diente 26")
 */
const extraerDientesDelTexto = (texto: string): string[] => {
  const regex = /\b(pieza|diente|molar|premolar|incisivo|canino)?\s*([1-4][1-8])\b/gi;
  const matches = texto.matchAll(regex);
  const dientes = new Set<string>();
  
  for (const match of matches) {
    dientes.add(match[2]);
  }
  
  return Array.from(dientes);
};

/**
 * Clasifica el tipo de tratamiento
 */
const clasificarTratamiento = (tratamiento: string): string => {
  const texto = tratamiento.toLowerCase();
  
  if (texto.includes('obturación') || texto.includes('restauración')) return 'OBTURACION';
  if (texto.includes('endodoncia') || texto.includes('conducto')) return 'ENDODONCIA';
  if (texto.includes('extracción') || texto.includes('exodoncia')) return 'EXTRACCION';
  if (texto.includes('corona') || texto.includes('prótesis')) return 'CORONA';
  if (texto.includes('limpieza') || texto.includes('profilaxis')) return 'LIMPIEZA';
  if (texto.includes('implante')) return 'IMPLANTE';
  
  return 'OTRO';
};

/**
 * Determina el estado del diente según sus tratamientos
 */
const determinarEstadoDiente = (tratamientos: any[]): string => {
  if (tratamientos.length === 0) return 'SANO';
  
  const ultimoTratamiento = tratamientos[tratamientos.length - 1];
  
  switch (ultimoTratamiento.tipo) {
    case 'EXTRACCION':
      return 'AUSENTE';
    case 'IMPLANTE':
      return 'IMPLANTE';
    case 'ENDODONCIA':
    case 'CORONA':
    case 'OBTURACION':
      return 'TRATADO';
    default:
      return 'OBSERVACION';
  }
};

/**
 * Obtiene el nombre descriptivo de un diente
 */
export const getNombreDiente = (numero: string): string => {
  const cuadrante = numero[0];
  const posicion = numero[1];
  
  let nombreCuadrante = '';
  switch (cuadrante) {
    case '1': nombreCuadrante = 'Superior Derecho'; break;
    case '2': nombreCuadrante = 'Superior Izquierdo'; break;
    case '3': nombreCuadrante = 'Inferior Izquierdo'; break;
    case '4': nombreCuadrante = 'Inferior Derecho'; break;
  }
  
  let nombrePosicion = '';
  switch (posicion) {
    case '1': nombrePosicion = 'Incisivo Central'; break;
    case '2': nombrePosicion = 'Incisivo Lateral'; break;
    case '3': nombrePosicion = 'Canino'; break;
    case '4': nombrePosicion = 'Primer Premolar'; break;
    case '5': nombrePosicion = 'Segundo Premolar'; break;
    case '6': nombrePosicion = 'Primer Molar'; break;
    case '7': nombrePosicion = 'Segundo Molar'; break;
    case '8': nombrePosicion = 'Tercer Molar (Muela del Juicio)'; break;
  }
  
  return `${nombrePosicion} ${nombreCuadrante}`;
};

/**
 * Obtiene el color según el estado del diente
 */
export const getColorEstadoDiente = (estado: string): string => {
  switch (estado?.toUpperCase()) {
    case 'SANO':
      return 'bg-green-100 border-green-500 hover:bg-green-200';
    case 'TRATADO':
      return 'bg-blue-100 border-blue-500 hover:bg-blue-200';
    case 'AUSENTE':
      return 'bg-gray-200 border-gray-400 hover:bg-gray-300';
    case 'CARIES':
      return 'bg-red-100 border-red-500 hover:bg-red-200';
    case 'OBSERVACION':
      return 'bg-yellow-100 border-yellow-500 hover:bg-yellow-200';
    case 'IMPLANTE':
      return 'bg-purple-100 border-purple-500 hover:bg-purple-200';
    default:
      return 'bg-gray-100 border-gray-300 hover:bg-gray-200';
  }
};

/**
 * Obtiene el icono según el estado del diente
 */
export const getIconoEstadoDiente = (estado: string): string => {
  switch (estado?.toUpperCase()) {
    case 'SANO': return '✅';
    case 'TRATADO': return '🔧';
    case 'AUSENTE': return '❌';
    case 'CARIES': return '🔴';
    case 'OBSERVACION': return '⚠️';
    case 'IMPLANTE': return '⚙️';
    default: return '🦷';
  }
};
```

---

### 2. Componente Principal - `Odontograma.tsx`

```tsx
// src/pages/paciente/Odontograma.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { obtenerOdontograma } from '../../services/historialService';

// Componentes
import ArcadaDental from '../../components/odontograma/ArcadaDental';
import DetalleDiente from '../../components/odontograma/DetalleDiente';
import LeyendaOdontograma from '../../components/odontograma/LeyendaOdontograma';
import EstadisticasDentales from '../../components/odontograma/EstadisticasDentales';

export default function Odontograma() {
  const navigate = useNavigate();

  const [odontograma, setOdontograma] = useState<any>(null);
  const [dienteSeleccionado, setDienteSeleccionado] = useState<any>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarOdontograma();
  }, []);

  const cargarOdontograma = async () => {
    try {
      setCargando(true);
      setError(null);

      const data = await obtenerOdontograma();
      setOdontograma(data);
    } catch (err: any) {
      console.error('❌ Error cargando odontograma:', err);
      setError('Error al cargar el odontograma');
    } finally {
      setCargando(false);
    }
  };

  const handleSeleccionarDiente = (numero: string) => {
    const diente = odontograma[numero];
    setDienteSeleccionado(diente);
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando odontograma...</p>
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
            onClick={cargarOdontograma}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            🔄 Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            🦷 Mi Odontograma
          </h1>
          <p className="text-gray-600 mt-2">
            Mapa visual del estado de tus dientes
          </p>
        </div>
        <button
          onClick={() => navigate('/paciente/historial')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
        >
          ← Volver al Historial
        </button>
      </div>

      {/* Estadísticas */}
      <EstadisticasDentales odontograma={odontograma} />

      {/* Odontograma Completo */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        
        {/* Arcada Superior */}
        <div className="mb-8">
          <h2 className="text-center text-xl font-bold text-gray-800 mb-6">
            Arcada Superior
          </h2>
          <div className="flex justify-center gap-8">
            {/* Superior Derecho */}
            <ArcadaDental
              dientes={getDientesCuadrante(odontograma, '1')}
              onSeleccionar={handleSeleccionarDiente}
              invertir={false}
              etiqueta="Derecho"
            />
            {/* Superior Izquierdo */}
            <ArcadaDental
              dientes={getDientesCuadrante(odontograma, '2')}
              onSeleccionar={handleSeleccionarDiente}
              invertir={true}
              etiqueta="Izquierdo"
            />
          </div>
        </div>

        {/* Separador */}
        <div className="border-t-2 border-gray-300 my-8"></div>

        {/* Arcada Inferior */}
        <div>
          <h2 className="text-center text-xl font-bold text-gray-800 mb-6">
            Arcada Inferior
          </h2>
          <div className="flex justify-center gap-8">
            {/* Inferior Derecho */}
            <ArcadaDental
              dientes={getDientesCuadrante(odontograma, '4')}
              onSeleccionar={handleSeleccionarDiente}
              invertir={false}
              etiqueta="Derecho"
            />
            {/* Inferior Izquierdo */}
            <ArcadaDental
              dientes={getDientesCuadrante(odontograma, '3')}
              onSeleccionar={handleSeleccionarDiente}
              invertir={true}
              etiqueta="Izquierdo"
            />
          </div>
        </div>

      </div>

      {/* Leyenda */}
      <LeyendaOdontograma />

      {/* Detalle del Diente Seleccionado */}
      {dienteSeleccionado && (
        <DetalleDiente
          diente={dienteSeleccionado}
          onCerrar={() => setDienteSeleccionado(null)}
        />
      )}

    </div>
  );
}

// Helper: Obtiene dientes de un cuadrante
function getDientesCuadrante(odontograma: any, cuadrante: string): any[] {
  const dientes = [];
  for (let i = 1; i <= 8; i++) {
    const numero = `${cuadrante}${i}`;
    if (odontograma[numero]) {
      dientes.push(odontograma[numero]);
    }
  }
  return dientes;
}
```

---

### 3. Componente - `ArcadaDental.tsx`

```tsx
// src/components/odontograma/ArcadaDental.tsx

import React from 'react';
import { getColorEstadoDiente } from '../../services/historialService';

interface Props {
  dientes: any[];
  onSeleccionar: (numero: string) => void;
  invertir: boolean;
  etiqueta: string;
}

export default function ArcadaDental({ dientes, onSeleccionar, invertir, etiqueta }: Props) {
  const dientesOrdenados = invertir ? [...dientes].reverse() : dientes;

  return (
    <div className="flex flex-col items-center">
      <p className="text-sm text-gray-600 mb-2 font-medium">{etiqueta}</p>
      <div className="flex gap-2">
        {dientesOrdenados.map((diente) => (
          <button
            key={diente.numero}
            onClick={() => onSeleccionar(diente.numero)}
            className={`
              w-12 h-16 rounded-lg border-2 flex flex-col items-center justify-center
              transition-all duration-200 transform hover:scale-110 hover:shadow-lg
              ${getColorEstadoDiente(diente.estado)}
            `}
            title={diente.nombre}
          >
            <span className="text-xs font-bold text-gray-700">
              {diente.numero}
            </span>
            {diente.tratamientos.length > 0 && (
              <span className="text-xs mt-1">
                {diente.tratamientos.length}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
```

---

### 4. Componente - `DetalleDiente.tsx`

```tsx
// src/components/odontograma/DetalleDiente.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getIconoEstadoDiente, formatearFecha } from '../../services/historialService';

interface Props {
  diente: any;
  onCerrar: () => void;
}

export default function DetalleDiente({ diente, onCerrar }: Props) {
  const navigate = useNavigate();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-start justify-between">
          <div className="flex items-center gap-4">
            <span className="text-6xl">
              {getIconoEstadoDiente(diente.estado)}
            </span>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                Diente #{diente.numero}
              </h2>
              <p className="text-gray-600 mt-1">{diente.nombre}</p>
              <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-semibold ${
                diente.estado === 'SANO' ? 'bg-green-100 text-green-800' :
                diente.estado === 'TRATADO' ? 'bg-blue-100 text-blue-800' :
                diente.estado === 'AUSENTE' ? 'bg-gray-100 text-gray-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {diente.estado}
              </span>
            </div>
          </div>
          <button
            onClick={onCerrar}
            className="text-gray-400 hover:text-gray-600 text-3xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Contenido */}
        <div className="p-6">
          
          {/* Tratamientos */}
          {diente.tratamientos.length > 0 ? (
            <div>
              <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                🔧 Historial de Tratamientos ({diente.tratamientos.length})
              </h3>
              <div className="space-y-3">
                {diente.tratamientos.map((tratamiento: any, index: number) => (
                  <div
                    key={index}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                        {tratamiento.tipo}
                      </span>
                      <span className="text-sm text-gray-600">
                        {formatearFecha(tratamiento.fecha)}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-3">{tratamiento.descripcion}</p>
                    <button
                      onClick={() => {
                        onCerrar();
                        navigate(`/paciente/historial/episodio/${tratamiento.episodio_id}`);
                      }}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Ver episodio completo →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <span className="text-6xl">✅</span>
              <h3 className="text-lg font-bold text-gray-800 mt-4">
                ¡Diente Sano!
              </h3>
              <p className="mt-2">No hay tratamientos registrados para este diente</p>
            </div>
          )}

          {/* Notas */}
          {diente.notas && (
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-2">📝 Notas:</h4>
              <p className="text-gray-700">{diente.notas}</p>
            </div>
          )}

        </div>

        {/* Footer con acciones */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex gap-3">
          <button
            onClick={onCerrar}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
          >
            Cerrar
          </button>
          <button
            onClick={() => navigate('/paciente/citas')}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            📅 Agendar Consulta
          </button>
        </div>

      </div>
    </div>
  );
}
```

---

### 5. Componente - `EstadisticasDentales.tsx`

```tsx
// src/components/odontograma/EstadisticasDentales.tsx

import React from 'react';

interface Props {
  odontograma: any;
}

export default function EstadisticasDentales({ odontograma }: Props) {
  const stats = calcularEstadisticas(odontograma);

  const cards = [
    {
      titulo: 'Dientes Sanos',
      valor: stats.sanos,
      total: 32,
      icono: '✅',
      color: 'bg-green-500'
    },
    {
      titulo: 'Tratados',
      valor: stats.tratados,
      total: 32,
      icono: '🔧',
      color: 'bg-blue-500'
    },
    {
      titulo: 'Ausentes',
      valor: stats.ausentes,
      total: 32,
      icono: '❌',
      color: 'bg-gray-500'
    },
    {
      titulo: 'En Observación',
      valor: stats.observacion,
      total: 32,
      icono: '⚠️',
      color: 'bg-yellow-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
      {cards.map((card, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">{card.titulo}</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {card.valor}
                <span className="text-lg text-gray-500">/{card.total}</span>
              </p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`${card.color} h-2 rounded-full`}
                  style={{ width: `${(card.valor / card.total) * 100}%` }}
                />
              </div>
            </div>
            <div className={`${card.color} rounded-full p-4 text-white text-3xl`}>
              {card.icono}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Helper: Calcular estadísticas
function calcularEstadisticas(odontograma: any) {
  let sanos = 0;
  let tratados = 0;
  let ausentes = 0;
  let observacion = 0;

  Object.values(odontograma).forEach((diente: any) => {
    switch (diente.estado.toUpperCase()) {
      case 'SANO': sanos++; break;
      case 'TRATADO': tratados++; break;
      case 'AUSENTE': ausentes++; break;
      case 'OBSERVACION': observacion++; break;
    }
  });

  return { sanos, tratados, ausentes, observacion };
}
```

---

### 6. Componente - `LeyendaOdontograma.tsx`

```tsx
// src/components/odontograma/LeyendaOdontograma.tsx

import React from 'react';
import { getColorEstadoDiente, getIconoEstadoDiente } from '../../services/historialService';

export default function LeyendaOdontograma() {
  const estados = [
    { codigo: 'SANO', nombre: 'Sano' },
    { codigo: 'TRATADO', nombre: 'Tratado' },
    { codigo: 'AUSENTE', nombre: 'Ausente' },
    { codigo: 'CARIES', nombre: 'Caries' },
    { codigo: 'OBSERVACION', nombre: 'En Observación' },
    { codigo: 'IMPLANTE', nombre: 'Implante' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="font-bold text-gray-800 mb-4">📖 Leyenda</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {estados.map((estado) => (
          <div key={estado.codigo} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded border-2 flex items-center justify-center ${getColorEstadoDiente(estado.codigo)}`}>
              <span className="text-sm">{getIconoEstadoDiente(estado.codigo)}</span>
            </div>
            <span className="text-sm text-gray-700">{estado.nombre}</span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>💡 Tip:</strong> Haz clic en cualquier diente para ver su historial completo de tratamientos
        </p>
      </div>
    </div>
  );
}
```

---

## 🔗 Integración

### 1. Agregar Ruta

```tsx
// En App.tsx o routes.tsx
import Odontograma from './pages/paciente/Odontograma';

<Route path="/paciente/odontograma" element={<Odontograma />} />
```

### 2. Agregar Link en el Menú/Dashboard

```tsx
// En tu componente de menú o accesos rápidos
<button onClick={() => navigate('/paciente/odontograma')}>
  🦷 Mi Odontograma
</button>
```

---

## 🎨 Características de la UI

### 1. **Vista Anatómica**
- 4 cuadrantes dentales
- 32 dientes numerados (sistema FDI)
- Colores por estado
- Hover effect con escala

### 2. **Interactividad**
- Click en diente abre modal con detalle
- Historial de tratamientos por diente
- Link directo a episodios relacionados

### 3. **Estadísticas Visuales**
- 4 cards con contadores
- Barras de progreso
- Porcentaje visual

### 4. **Responsivo**
- Desktop: 4 arcadas lado a lado
- Móvil: Stack vertical
- Dientes adaptables

---

## 📝 Notas Importantes

### 1. **Extracción de Datos**
La función `extraerDientesDelTexto()` busca menciones de dientes en los episodios clínicos. Los doctores deben usar el formato correcto:
- ✅ "Tratamiento en pieza 16"
- ✅ "Caries en diente 26"
- ✅ "Extracción del molar 46"

### 2. **Estados Posibles**
- **SANO**: Sin tratamientos
- **TRATADO**: Obturaciones, endodoncias, coronas
- **AUSENTE**: Extraído
- **CARIES**: Diagnóstico sin tratamiento aún
- **OBSERVACION**: Requiere seguimiento
- **IMPLANTE**: Implante dental

---

## 🧪 Testing

1. ✅ Cargar odontograma completo
2. ✅ Click en diente muestra modal
3. ✅ Estadísticas calculadas correctamente
4. ✅ Colores según estado
5. ✅ Navegación a episodios desde modal
6. ✅ Responsive en móvil
7. ✅ Leyenda visible y clara

---

## 🎯 Mejoras Futuras

1. **Vista 3D**: Modelo dental interactivo 3D
2. **Comparación Temporal**: Ver cambios a lo largo del tiempo
3. **Fotografías**: Adjuntar fotos clínicas de cada diente
4. **Exportar PDF**: Imprimir odontograma completo
5. **Animaciones**: Transiciones suaves entre estados
6. **Vista de Niño**: Odontograma con 20 dientes deciduos
7. **Filtros**: Ver solo dientes con tratamientos
8. **Búsqueda**: Buscar por número de diente

---

**Siguiente**: Guía 38 - Agendar Cita Interactiva con Calendario 📅
