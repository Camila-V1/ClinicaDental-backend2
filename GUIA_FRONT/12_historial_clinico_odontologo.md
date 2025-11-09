# 📋 GUÍA: HISTORIAL CLÍNICO - ODONTÓLOGO

## 🎯 Objetivo
Implementar el módulo de historial clínico para que el odontólogo pueda:
- Ver listado de todos los pacientes con historial
- Acceder al historial completo de cada paciente
- Visualizar antecedentes médicos, alergias y medicamentos
- Revisar episodios de atención previos
- Consultar odontogramas
- Agregar nuevos episodios de atención

---

## 📋 Endpoints Backend Disponibles

### 1. Listar Historiales Clínicos
```http
GET /api/historial/historiales/
```

**Response 200 OK:**
```json
[
  {
    "paciente": 20,
    "paciente_nombre": "María García",
    "paciente_email": "paciente@clinica-demo.com",
    "alergias": "Alergia a la penicilina",
    "medicamentos_actuales": "Enalapril 10mg (1 vez al día)",
    "actualizado": "2025-11-07T23:23:24.634291Z",
    "total_episodios": 3,
    "ultimo_episodio": "2025-11-02T23:23:24.643076Z"
  }
]
```

### 2. Obtener Detalle del Historial
```http
GET /api/historial/historiales/{paciente_id}/
```

**Response 200 OK:**
```json
{
  "paciente": 20,
  "paciente_nombre": "María García",
  "paciente_email": "paciente@clinica-demo.com",
  "paciente_ci": "1234567",
  "paciente_telefono": "555123456",
  "paciente_fecha_nacimiento": "1985-03-15",
  "paciente_direccion": "Av. Principal 123",
  
  "antecedentes_medicos": "Hipertensión controlada con medicación",
  "alergias": "Alergia a la penicilina",
  "medicamentos_actuales": "Enalapril 10mg (1 vez al día)",
  
  "creado": "2025-11-07T23:23:24.634291Z",
  "actualizado": "2025-11-07T23:23:24.634291Z",
  
  "total_episodios": 3,
  "total_odontogramas": 1,
  "total_documentos": 0,
  "ultimo_episodio": "2025-11-02T23:23:24.643076Z",
  
  "episodios": [
    {
      "id": 2,
      "odontologo": 20,
      "odontologo_nombre": "Dr. Juan Pérez",
      "odontologo_especialidad": null,
      "item_plan_tratamiento": null,
      "item_plan_descripcion": null,
      "fecha_atencion": "2025-11-02T23:23:24.643076Z",
      "motivo_consulta": "Control post-tratamiento",
      "diagnostico": "Evolución favorable de obturación pieza 46",
      "descripcion_procedimiento": "Control de obturación realizada hace 1 mes...",
      "notas_privadas": "Todo bien. Próximo control en 6 meses."
    }
  ],
  
  "odontogramas": [
    {
      "id": 1,
      "fecha_snapshot": "2025-11-07T23:23:24.658027Z",
      "estado_piezas": {
        "11": {"estado": "sano"},
        "46": {"estado": "obturado", "cara": "oclusal", "material": "resina"}
      },
      "notas": "Ausencia de terceros molares"
    }
  ],
  
  "documentos": []
}
```

### 3. Listar Todos los Episodios
```http
GET /api/historial/episodios/
```

**Response 200 OK:**
```json
[
  {
    "id": 2,
    "odontologo": 20,
    "odontologo_nombre": "Dr. Juan Pérez",
    "odontologo_especialidad": null,
    "item_plan_tratamiento": null,
    "item_plan_descripcion": null,
    "fecha_atencion": "2025-11-02T23:23:24.643076Z",
    "motivo_consulta": "Control post-tratamiento",
    "diagnostico": "Evolución favorable",
    "descripcion_procedimiento": "Control realizado exitosamente",
    "notas_privadas": "Paciente en buen estado"
  }
]
```

### 4. Crear Nuevo Episodio
```http
POST /api/historial/episodios/
```

**Request Body:**
```json
{
  "historial_clinico": 20,
  "motivo_consulta": "Dolor en molar superior",
  "diagnostico": "Caries profunda pieza 16",
  "descripcion_procedimiento": "Se realizó limpieza de caries y obturación con resina",
  "notas_privadas": "Paciente cooperador"
}
```

**Response 201 CREATED:**
```json
{
  "id": 8,
  "odontologo": 20,
  "odontologo_nombre": "Dr. Juan Pérez",
  "odontologo_especialidad": null,
  "item_plan_tratamiento": null,
  "item_plan_descripcion": null,
  "fecha_atencion": "2025-11-07T23:45:12.123456Z",
  "motivo_consulta": "Dolor en molar superior",
  "diagnostico": "Caries profunda pieza 16",
  "descripcion_procedimiento": "Se realizó limpieza de caries y obturación con resina",
  "notas_privadas": "Paciente cooperador"
}
```

### 5. Listar Odontogramas
```http
GET /api/historial/odontogramas/
```

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "fecha_snapshot": "2025-11-07T23:23:24.658027Z",
    "estado_piezas": {
      "11": {"estado": "sano"},
      "12": {"estado": "sano"},
      "46": {"estado": "obturado", "cara": "oclusal", "material": "resina"}
    },
    "notas": "Buen estado general de higiene oral"
  }
]
```

---

## 🛠️ Implementación Frontend

### PASO 1: Crear servicio de API

**Archivo:** `src/services/historialService.ts`

```typescript
import api from '../config/apiConfig';

export interface HistorialResumen {
  paciente: number;
  paciente_nombre: string;
  paciente_email: string;
  alergias?: string;
  medicamentos_actuales?: string;
  actualizado: string;
  total_episodios: number;
  ultimo_episodio?: string;
}

export interface EpisodioAtencion {
  id: number;
  odontologo: number;
  odontologo_nombre: string;
  odontologo_especialidad?: string;
  item_plan_tratamiento?: number;
  item_plan_descripcion?: string;
  fecha_atencion: string;
  motivo_consulta: string;
  diagnostico?: string;
  descripcion_procedimiento?: string;
  notas_privadas?: string;
}

export interface Odontograma {
  id: number;
  fecha_snapshot: string;
  estado_piezas: Record<string, any>;
  notas?: string;
}

export interface HistorialCompleto {
  paciente: number;
  paciente_nombre: string;
  paciente_email: string;
  paciente_ci?: string;
  paciente_telefono?: string;
  paciente_fecha_nacimiento?: string;
  paciente_direccion?: string;
  
  antecedentes_medicos?: string;
  alergias?: string;
  medicamentos_actuales?: string;
  
  creado: string;
  actualizado: string;
  
  total_episodios: number;
  total_odontogramas: number;
  total_documentos: number;
  ultimo_episodio?: string;
  
  episodios: EpisodioAtencion[];
  odontogramas: Odontograma[];
  documentos: any[];
}

export interface CrearEpisodioDTO {
  historial_clinico: number;
  motivo_consulta: string;
  diagnostico?: string;
  descripcion_procedimiento?: string;
  notas_privadas?: string;
}

/**
 * Obtener lista de historiales clínicos
 */
export const obtenerHistoriales = async (): Promise<HistorialResumen[]> => {
  const response = await api.get<HistorialResumen[]>('/api/historial/historiales/');
  return response.data;
};

/**
 * Obtener historial completo de un paciente
 */
export const obtenerHistorialCompleto = async (pacienteId: number): Promise<HistorialCompleto> => {
  const response = await api.get<HistorialCompleto>(`/api/historial/historiales/${pacienteId}/`);
  return response.data;
};

/**
 * Obtener todos los episodios
 */
export const obtenerEpisodios = async (): Promise<EpisodioAtencion[]> => {
  const response = await api.get<EpisodioAtencion[]>('/api/historial/episodios/');
  return response.data;
};

/**
 * Crear nuevo episodio de atención
 */
export const crearEpisodio = async (datos: CrearEpisodioDTO): Promise<EpisodioAtencion> => {
  const response = await api.post<EpisodioAtencion>('/api/historial/episodios/', datos);
  return response.data;
};

/**
 * Obtener mis episodios (del odontólogo logueado)
 */
export const obtenerMisEpisodios = async (): Promise<EpisodioAtencion[]> => {
  const response = await api.get<EpisodioAtencion[]>('/api/historial/episodios/mis_episodios/');
  return response.data;
};

/**
 * Obtener todos los odontogramas
 */
export const obtenerOdontogramas = async (): Promise<Odontograma[]> => {
  const response = await api.get<Odontograma[]>('/api/historial/odontogramas/');
  return response.data;
};
```

---

### PASO 2: Crear componente de Lista de Historiales

**Archivo:** `src/pages/odontologo/HistorialesList.tsx`

```typescript
import { useState, useEffect } from 'react';
import { obtenerHistoriales, type HistorialResumen } from '../../services/historialService';
import { useNavigate } from 'react-router-dom';

export default function HistorialesList() {
  const [historiales, setHistoriales] = useState<HistorialResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    cargarHistoriales();
  }, []);

  const cargarHistoriales = async () => {
    try {
      setLoading(true);
      const data = await obtenerHistoriales();
      setHistoriales(data);
    } catch (error) {
      console.error('Error al cargar historiales:', error);
      alert('Error al cargar historiales');
    } finally {
      setLoading(false);
    }
  };

  const historialesFiltrados = historiales.filter(h =>
    h.paciente_nombre.toLowerCase().includes(filtro.toLowerCase()) ||
    h.paciente_email.toLowerCase().includes(filtro.toLowerCase())
  );

  const formatearFecha = (fecha: string) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">📋 Historiales Clínicos</h1>
        <p className="text-gray-600 mt-1">Gestiona los historiales de tus pacientes</p>
      </div>

      {/* Búsqueda */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
      </div>

      {/* Lista de Historiales */}
      {historialesFiltrados.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">📭 No se encontraron historiales</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {historialesFiltrados.map((historial) => (
            <div
              key={historial.paciente}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/odontologo/historiales/${historial.paciente}`)}
            >
              <div className="p-6">
                {/* Nombre del Paciente */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {historial.paciente_nombre}
                    </h3>
                    <p className="text-sm text-gray-500">{historial.paciente_email}</p>
                  </div>
                </div>

                {/* Información Relevante */}
                <div className="space-y-2 mb-4">
                  {historial.alergias && (
                    <div className="flex items-center text-sm">
                      <span className="text-red-600 font-medium mr-2">⚠️ Alergias:</span>
                      <span className="text-gray-700">{historial.alergias}</span>
                    </div>
                  )}
                  
                  {historial.medicamentos_actuales && (
                    <div className="flex items-center text-sm">
                      <span className="text-blue-600 font-medium mr-2">💊 Medicamentos:</span>
                      <span className="text-gray-700 truncate">{historial.medicamentos_actuales}</span>
                    </div>
                  )}
                </div>

                {/* Estadísticas */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {historial.total_episodios}
                    </div>
                    <div className="text-xs text-gray-500">Episodios</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-sm text-gray-600">
                      Última atención
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatearFecha(historial.ultimo_episodio || '')}
                    </div>
                  </div>
                </div>

                {/* Botón Ver Detalle */}
                <button
                  className="mt-4 w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/odontologo/historiales/${historial.paciente}`);
                  }}
                >
                  Ver Historial Completo →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### PASO 3: Crear componente de Detalle del Historial

**Archivo:** `src/pages/odontologo/HistorialDetalle.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { obtenerHistorialCompleto, type HistorialCompleto } from '../../services/historialService';

export default function HistorialDetalle() {
  const { pacienteId } = useParams<{ pacienteId: string }>();
  const [historial, setHistorial] = useState<HistorialCompleto | null>(null);
  const [loading, setLoading] = useState(true);
  const [tabActiva, setTabActiva] = useState<'general' | 'episodios' | 'odontogramas'>('general');
  const navigate = useNavigate();

  useEffect(() => {
    if (pacienteId) {
      cargarHistorial(parseInt(pacienteId));
    }
  }, [pacienteId]);

  const cargarHistorial = async (id: number) => {
    try {
      setLoading(true);
      const data = await obtenerHistorialCompleto(id);
      setHistorial(data);
    } catch (error) {
      console.error('Error al cargar historial:', error);
      alert('Error al cargar historial');
    } finally {
      setLoading(false);
    }
  };

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!historial) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">No se encontró el historial</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/odontologo/historiales')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Volver a la lista
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900">
          {historial.paciente_nombre}
        </h1>
        <p className="text-gray-600">{historial.paciente_email}</p>
      </div>

      {/* Datos del Paciente */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">👤 Datos del Paciente</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <span className="text-sm text-gray-500">CI:</span>
            <p className="font-medium">{historial.paciente_ci || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-gray-500">Teléfono:</span>
            <p className="font-medium">{historial.paciente_telefono || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-gray-500">Fecha de Nacimiento:</span>
            <p className="font-medium">{historial.paciente_fecha_nacimiento || 'N/A'}</p>
          </div>
          <div className="md:col-span-3">
            <span className="text-sm text-gray-500">Dirección:</span>
            <p className="font-medium">{historial.paciente_direccion || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Alertas Médicas */}
      {(historial.alergias || historial.medicamentos_actuales || historial.antecedentes_medicos) && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-r-lg">
          <h3 className="font-semibold text-yellow-800 mb-2">⚠️ Información Médica Importante</h3>
          
          {historial.alergias && (
            <div className="mb-2">
              <span className="font-medium text-red-700">Alergias:</span>
              <p className="text-gray-700">{historial.alergias}</p>
            </div>
          )}
          
          {historial.medicamentos_actuales && (
            <div className="mb-2">
              <span className="font-medium text-blue-700">Medicamentos Actuales:</span>
              <p className="text-gray-700">{historial.medicamentos_actuales}</p>
            </div>
          )}
          
          {historial.antecedentes_medicos && (
            <div>
              <span className="font-medium text-purple-700">Antecedentes Médicos:</span>
              <p className="text-gray-700">{historial.antecedentes_medicos}</p>
            </div>
          )}
        </div>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl font-bold text-blue-600">{historial.total_episodios}</div>
          <div className="text-sm text-gray-600 mt-1">Episodios de Atención</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl font-bold text-green-600">{historial.total_odontogramas}</div>
          <div className="text-sm text-gray-600 mt-1">Odontogramas</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl font-bold text-purple-600">{historial.total_documentos}</div>
          <div className="text-sm text-gray-600 mt-1">Documentos</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex">
            <button
              onClick={() => setTabActiva('general')}
              className={`py-4 px-6 font-medium ${
                tabActiva === 'general'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              📊 General
            </button>
            <button
              onClick={() => setTabActiva('episodios')}
              className={`py-4 px-6 font-medium ${
                tabActiva === 'episodios'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🩺 Episodios ({historial.episodios.length})
            </button>
            <button
              onClick={() => setTabActiva('odontogramas')}
              className={`py-4 px-6 font-medium ${
                tabActiva === 'odontogramas'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🦷 Odontogramas ({historial.odontogramas.length})
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Tab General */}
          {tabActiva === 'general' && (
            <div className="space-y-4">
              <p className="text-gray-600">
                Última actualización: {formatearFecha(historial.actualizado)}
              </p>
              {historial.ultimo_episodio && (
                <p className="text-gray-600">
                  Última atención: {formatearFecha(historial.ultimo_episodio)}
                </p>
              )}
            </div>
          )}

          {/* Tab Episodios */}
          {tabActiva === 'episodios' && (
            <div className="space-y-4">
              {historial.episodios.length === 0 ? (
                <p className="text-gray-500">No hay episodios registrados</p>
              ) : (
                historial.episodios.map((episodio) => (
                  <div key={episodio.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">{episodio.motivo_consulta}</h4>
                        <p className="text-sm text-gray-500">
                          {formatearFecha(episodio.fecha_atencion)}
                        </p>
                      </div>
                      <span className="text-sm text-blue-600">{episodio.odontologo_nombre}</span>
                    </div>
                    
                    {episodio.diagnostico && (
                      <div className="mt-2">
                        <span className="text-sm font-medium text-gray-700">Diagnóstico:</span>
                        <p className="text-sm text-gray-600">{episodio.diagnostico}</p>
                      </div>
                    )}
                    
                    {episodio.descripcion_procedimiento && (
                      <div className="mt-2">
                        <span className="text-sm font-medium text-gray-700">Procedimiento:</span>
                        <p className="text-sm text-gray-600">{episodio.descripcion_procedimiento}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab Odontogramas */}
          {tabActiva === 'odontogramas' && (
            <div className="space-y-4">
              {historial.odontogramas.length === 0 ? (
                <p className="text-gray-500">No hay odontogramas registrados</p>
              ) : (
                historial.odontogramas.map((odontograma) => (
                  <div key={odontograma.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          Odontograma {formatearFecha(odontograma.fecha_snapshot)}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {Object.keys(odontograma.estado_piezas).length} piezas registradas
                        </p>
                      </div>
                    </div>
                    
                    {odontograma.notas && (
                      <div className="mt-2">
                        <span className="text-sm font-medium text-gray-700">Notas:</span>
                        <p className="text-sm text-gray-600">{odontograma.notas}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### PASO 4: Agregar rutas

**Archivo:** `src/App.tsx` (o donde tengas las rutas)

```typescript
import HistorialesList from './pages/odontologo/HistorialesList';
import HistorialDetalle from './pages/odontologo/HistorialDetalle';

// Dentro de tus rutas protegidas para ODONTOLOGO:
<Route path="/odontologo/historiales" element={<HistorialesList />} />
<Route path="/odontologo/historiales/:pacienteId" element={<HistorialDetalle />} />
```

---

## ✅ Checklist de Implementación

- [ ] Crear `historialService.ts` con funciones de API
- [ ] Crear componente `HistorialesList.tsx`
- [ ] Crear componente `HistorialDetalle.tsx`
- [ ] Agregar rutas en el router
- [ ] Probar con usuario odontólogo
- [ ] Verificar filtros funcionan
- [ ] Agregar link en menú lateral/navbar

---

## 🧪 Cómo Probar

1. Login como odontólogo: `odontologo@clinica-demo.com` / `odontologo123`
2. Navegar a `/odontologo/historiales`
3. Verificar que se cargan 4 historiales
4. Buscar por nombre o email
5. Hacer clic en "Ver Historial Completo"
6. Revisar tabs: General, Episodios, Odontogramas
7. Verificar alertas médicas (alergias, medicamentos)

**Datos de prueba disponibles:**
- 4 historiales clínicos
- 7 episodios de atención
- 3 odontogramas
- 0 documentos

---

## 🚀 Próximos Pasos

1. ✅ Agenda de Citas
2. ✅ Historial Clínico (actual)
3. 🔄 Agregar nuevo episodio desde la agenda
4. 👥 Listado de Pacientes
5. 🦷 Registro de Tratamientos

---

## 📝 Notas Importantes

- ⚠️ **Alergias**: Siempre mostrar en color rojo y destacado
- 💊 **Medicamentos**: Mostrar en la vista de lista para acceso rápido
- 🔒 **Notas Privadas**: Solo visibles para el personal médico (no para pacientes)
- 📊 **Estadísticas**: Total de episodios, odontogramas y documentos
- 🦷 **Odontograma**: JSONField flexible para guardar estado de cada pieza dental

---

**¿Está lista esta guía? El API está completamente probado y funcionando correctamente!** ✅ 🎯
