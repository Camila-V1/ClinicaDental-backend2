# Guía 20: Mis Citas Completas para Pacientes

## Objetivo
Implementar la página completa de citas del paciente que muestra citas pasadas, próximas, permite cancelar, reagendar y ver detalles.

## Endpoints Backend

### GET /api/agenda/citas/mis_citas/
**Respuesta exitosa (200):**
```json
[
  {
    "id": 127,
    "paciente": 104,
    "paciente_nombre": "María",
    "paciente_email": "paciente1@test.com",
    "odontologo": 103,
    "odontologo_nombre": "Dr. Juan Pérez",
    "fecha_hora": "2025-11-22T09:00:00Z",
    "estado": "CONFIRMADA",
    "motivo_tipo": "CONTROL",
    "motivo_tipo_display": "Control y Revisión",
    "motivo": "Seguimiento de endodoncia",
    "observaciones": "Traer radiografías anteriores",
    "precio_display": "$80.00",
    "es_cita_plan": true,
    "item_plan": 45,
    "item_plan_info": {
      "tratamiento_nombre": "Endodoncia",
      "pieza_dental": "21"
    }
  }
]
```

### PATCH /api/agenda/citas/{id}/cancelar/
**Request:**
```json
{
  "motivo_cancelacion": "No puedo asistir por trabajo"
}
```
**Respuesta exitosa (200):**
```json
{
  "mensaje": "Cita cancelada correctamente",
  "cita": { /* objeto cita actualizado */ }
}
```

### POST /api/agenda/citas/{id}/reagendar/
**Request:**
```json
{
  "nueva_fecha_hora": "2025-11-25T10:00:00"
}
```
**Respuesta exitosa (200):**
```json
{
  "mensaje": "Cita reagendada correctamente",
  "cita": { /* objeto cita actualizado */ }
}
```

## Estructura de Archivos

```
src/
├── services/
│   └── agendaService.ts           # Agregar funciones de cancelar/reagendar
├── pages/
│   └── paciente/
│       └── CitasPage.tsx          # Página principal
└── components/
    └── paciente/
        └── citas/
            ├── FiltroCitas.tsx           # Filtros por estado/fecha
            ├── TarjetaCita.tsx           # Tarjeta individual de cita
            ├── DetalleCita.tsx           # Modal con detalle completo
            ├── FormularioCancelar.tsx    # Modal para cancelar
            └── FormularioReagendar.tsx   # Modal para reagendar
```

## Paso 1: Extender Servicio de Agenda

**Archivo:** `src/services/agendaService.ts` (agregar al final)

```typescript
/**
 * Obtener todas las citas del paciente (pasadas y futuras)
 */
export const obtenerMisCitas = async (): Promise<Cita[]> => {
  console.log('📅 Obteniendo todas mis citas...');
  
  const response = await apiClient.get<Cita[]>('/api/agenda/citas/mis_citas/');
  
  console.log(`✅ ${response.data.length} citas obtenidas`);
  return response.data;
};

/**
 * Cancelar una cita
 */
export const cancelarCita = async (
  citaId: number,
  motivo: string
): Promise<Cita> => {
  console.log(`❌ Cancelando cita ${citaId}...`);
  
  const response = await apiClient.patch<{ mensaje: string; cita: Cita }>(
    `/api/agenda/citas/${citaId}/cancelar/`,
    { motivo_cancelacion: motivo }
  );
  
  console.log('✅ Cita cancelada:', response.data.mensaje);
  return response.data.cita;
};

/**
 * Reagendar una cita
 */
export const reagendarCita = async (
  citaId: number,
  nuevaFecha: string
): Promise<Cita> => {
  console.log(`🔄 Reagendando cita ${citaId}...`);
  
  const response = await apiClient.post<{ mensaje: string; cita: Cita }>(
    `/api/agenda/citas/${citaId}/reagendar/`,
    { nueva_fecha_hora: nuevaFecha }
  );
  
  console.log('✅ Cita reagendada:', response.data.mensaje);
  return response.data.cita;
};
```

## Paso 2: Filtro de Citas

**Archivo:** `src/components/paciente/citas/FiltroCitas.tsx`

```typescript
import React from 'react';
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export type FiltroEstado = 'TODAS' | 'PENDIENTE' | 'CONFIRMADA' | 'ATENDIDA' | 'CANCELADA';
export type FiltroTiempo = 'TODAS' | 'PROXIMAS' | 'PASADAS';

interface Props {
  filtroEstado: FiltroEstado;
  filtroTiempo: FiltroTiempo;
  onCambiarEstado: (estado: FiltroEstado) => void;
  onCambiarTiempo: (tiempo: FiltroTiempo) => void;
  contadores: {
    todas: number;
    pendientes: number;
    confirmadas: number;
    atendidas: number;
    canceladas: number;
  };
}

export const FiltroCitas: React.FC<Props> = ({
  filtroEstado,
  filtroTiempo,
  onCambiarEstado,
  onCambiarTiempo,
  contadores
}) => {
  const estadosConfig = [
    { valor: 'TODAS' as FiltroEstado, label: 'Todas', icon: Calendar, count: contadores.todas },
    { valor: 'PENDIENTE' as FiltroEstado, label: 'Pendientes', icon: Clock, count: contadores.pendientes, color: 'yellow' },
    { valor: 'CONFIRMADA' as FiltroEstado, label: 'Confirmadas', icon: CheckCircle, count: contadores.confirmadas, color: 'blue' },
    { valor: 'ATENDIDA' as FiltroEstado, label: 'Atendidas', icon: CheckCircle, count: contadores.atendidas, color: 'green' },
    { valor: 'CANCELADA' as FiltroEstado, label: 'Canceladas', icon: XCircle, count: contadores.canceladas, color: 'red' },
  ];

  const tiemposConfig = [
    { valor: 'TODAS' as FiltroTiempo, label: 'Todas' },
    { valor: 'PROXIMAS' as FiltroTiempo, label: 'Próximas' },
    { valor: 'PASADAS' as FiltroTiempo, label: 'Pasadas' },
  ];

  const getColorClasses = (color?: string, activo?: boolean) => {
    if (!activo) return 'text-gray-600 border-gray-300 bg-white';
    
    switch (color) {
      case 'yellow': return 'text-yellow-700 border-yellow-500 bg-yellow-50';
      case 'blue': return 'text-blue-700 border-blue-500 bg-blue-50';
      case 'green': return 'text-green-700 border-green-500 bg-green-50';
      case 'red': return 'text-red-700 border-red-500 bg-red-50';
      default: return 'text-gray-700 border-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Filtro por estado */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Estado de la Cita</h3>
        <div className="flex flex-wrap gap-2">
          {estadosConfig.map((estado) => {
            const Icon = estado.icon;
            const activo = filtroEstado === estado.valor;
            
            return (
              <button
                key={estado.valor}
                onClick={() => onCambiarEstado(estado.valor)}
                className={`
                  flex items-center space-x-2 px-4 py-2 rounded-lg border-2 
                  transition-all duration-200 font-medium
                  ${getColorClasses(estado.color, activo)}
                  ${activo ? 'shadow-md' : 'hover:border-gray-400'}
                `}
              >
                <Icon className="w-4 h-4" />
                <span>{estado.label}</span>
                <span className="text-xs bg-white bg-opacity-50 px-2 py-0.5 rounded-full">
                  {estado.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Filtro por tiempo */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Período</h3>
        <div className="flex space-x-2">
          {tiemposConfig.map((tiempo) => {
            const activo = filtroTiempo === tiempo.valor;
            
            return (
              <button
                key={tiempo.valor}
                onClick={() => onCambiarTiempo(tiempo.valor)}
                className={`
                  px-4 py-2 rounded-lg border-2 transition-all duration-200 font-medium
                  ${activo 
                    ? 'text-blue-700 border-blue-500 bg-blue-50 shadow-md' 
                    : 'text-gray-600 border-gray-300 bg-white hover:border-gray-400'
                  }
                `}
              >
                {tiempo.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
```

## Paso 3: Tarjeta de Cita

**Archivo:** `src/components/paciente/citas/TarjetaCita.tsx`

```typescript
import React from 'react';
import { Cita } from '../../../services/agendaService';
import { Calendar, Clock, User, FileText, DollarSign } from 'lucide-react';

interface Props {
  cita: Cita;
  onClick: () => void;
}

export const TarjetaCita: React.FC<Props> = ({ cita, onClick }) => {
  const formatearFecha = (fecha: string) => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatearHora = (fecha: string) => {
    const date = new Date(fecha);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoBadge = (estado: string) => {
    const configs = {
      PENDIENTE: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pendiente' },
      CONFIRMADA: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Confirmada' },
      ATENDIDA: { bg: 'bg-green-100', text: 'text-green-800', label: 'Atendida' },
      CANCELADA: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelada' },
    };

    const config = configs[estado as keyof typeof configs] || configs.PENDIENTE;
    
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const esPasada = new Date(cita.fecha_hora) < new Date();

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg shadow-md p-6 cursor-pointer 
        transition-all duration-200 hover:shadow-lg hover:scale-[1.02]
        ${esPasada ? 'opacity-75' : ''}
      `}
    >
      {/* Header con fecha y estado */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2 text-gray-600 mb-1">
            <Calendar className="w-4 h-4" />
            <span className="text-sm font-medium capitalize">
              {formatearFecha(cita.fecha_hora)}
            </span>
          </div>
          <div className="flex items-center space-x-2 text-gray-600">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">
              {formatearHora(cita.fecha_hora)}
            </span>
          </div>
        </div>
        {getEstadoBadge(cita.estado)}
      </div>

      {/* Odontólogo */}
      <div className="flex items-center space-x-2 mb-3">
        <User className="w-4 h-4 text-blue-600" />
        <span className="text-gray-900 font-medium">
          {cita.odontologo_nombre}
        </span>
      </div>

      {/* Motivo */}
      <div className="flex items-start space-x-2 mb-3">
        <FileText className="w-4 h-4 text-purple-600 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm text-gray-600">{cita.motivo_tipo_display}</p>
          {cita.motivo && (
            <p className="text-sm text-gray-900 mt-1">{cita.motivo}</p>
          )}
        </div>
      </div>

      {/* Precio */}
      {cita.precio_display && (
        <div className="flex items-center space-x-2 pt-3 border-t border-gray-200">
          <DollarSign className="w-4 h-4 text-green-600" />
          <span className="text-sm font-medium text-gray-900">
            {cita.precio_display}
          </span>
        </div>
      )}

      {/* Indicador de cita vinculada a plan */}
      {cita.es_cita_plan && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
            📋 Vinculada a plan de tratamiento
          </span>
        </div>
      )}
    </div>
  );
};
```

## Paso 4: Página Principal de Citas

**Archivo:** `src/pages/paciente/CitasPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { obtenerMisCitas, Cita } from '../../services/agendaService';
import { FiltroCitas, FiltroEstado, FiltroTiempo } from '../../components/paciente/citas/FiltroCitas';
import { TarjetaCita } from '../../components/paciente/citas/TarjetaCita';
import { Loader2, AlertCircle, Calendar } from 'lucide-react';

export const CitasPage: React.FC = () => {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [citasFiltradas, setCitasFiltradas] = useState<Cita[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<FiltroEstado>('TODAS');
  const [filtroTiempo, setFiltroTiempo] = useState<FiltroTiempo>('TODAS');
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarCitas();
  }, []);

  useEffect(() => {
    aplicarFiltros();
  }, [citas, filtroEstado, filtroTiempo]);

  const cargarCitas = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await obtenerMisCitas();
      setCitas(data);
    } catch (err: any) {
      console.error('❌ Error al cargar citas:', err);
      setError('Error al cargar las citas');
    } finally {
      setCargando(false);
    }
  };

  const aplicarFiltros = () => {
    let resultado = [...citas];
    const ahora = new Date();

    // Filtrar por estado
    if (filtroEstado !== 'TODAS') {
      resultado = resultado.filter(c => c.estado === filtroEstado);
    }

    // Filtrar por tiempo
    if (filtroTiempo === 'PROXIMAS') {
      resultado = resultado.filter(c => new Date(c.fecha_hora) >= ahora);
    } else if (filtroTiempo === 'PASADAS') {
      resultado = resultado.filter(c => new Date(c.fecha_hora) < ahora);
    }

    // Ordenar por fecha (próximas primero, luego pasadas)
    resultado.sort((a, b) => {
      const fechaA = new Date(a.fecha_hora).getTime();
      const fechaB = new Date(b.fecha_hora).getTime();
      return fechaB - fechaA; // Más recientes primero
    });

    setCitasFiltradas(resultado);
  };

  const calcularContadores = () => {
    return {
      todas: citas.length,
      pendientes: citas.filter(c => c.estado === 'PENDIENTE').length,
      confirmadas: citas.filter(c => c.estado === 'CONFIRMADA').length,
      atendidas: citas.filter(c => c.estado === 'ATENDIDA').length,
      canceladas: citas.filter(c => c.estado === 'CANCELADA').length,
    };
  };

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Cargando citas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <AlertCircle className="w-6 h-6 text-red-600 mb-2" />
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Mis Citas</h1>

      <div className="space-y-6">
        {/* Filtros */}
        <FiltroCitas
          filtroEstado={filtroEstado}
          filtroTiempo={filtroTiempo}
          onCambiarEstado={setFiltroEstado}
          onCambiarTiempo={setFiltroTiempo}
          contadores={calcularContadores()}
        />

        {/* Lista de citas */}
        {citasFiltradas.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">
              No hay citas con los filtros seleccionados
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {citasFiltradas.map((cita) => (
              <TarjetaCita
                key={cita.id}
                cita={cita}
                onClick={() => console.log('Abrir detalle:', cita.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

## Paso 5: Registrar Ruta

**Archivo:** `src/App.tsx`

```typescript
import { CitasPage } from './pages/paciente/CitasPage';

// Dentro de las rutas protegidas de paciente:
<Route path="/paciente/citas" element={<CitasPage />} />
```

## Verificación

1. **Login:** paciente1@test.com / password123
2. **Navegar a:** http://clinica-demo.localhost:5173/paciente/citas
3. **Verificar:**
   - ✅ Se muestran las 3 citas con sus detalles
   - ✅ Los filtros funcionan correctamente
   - ✅ Los badges de estado tienen los colores correctos
   - ✅ Las citas se ordenan cronológicamente

## Próximos Pasos

En la siguiente guía agregaremos:
- Modal de detalle completo
- Funcionalidad de cancelar cita
- Funcionalidad de reagendar cita
- Confirmación de asistencia
