# 📅 Guía Paso a Paso: Calendario de Citas del Odontólogo

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Backend Disponible](#backend-disponible)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Paso 1: Tipos TypeScript](#paso-1-tipos-typescript)
5. [Paso 2: Servicio de API](#paso-2-servicio-de-api)
6. [Paso 3: Componente de Calendario](#paso-3-componente-de-calendario)
7. [Paso 4: Vista Mensual](#paso-4-vista-mensual)
8. [Paso 5: Vista Semanal](#paso-5-vista-semanal)
9. [Paso 6: Vista Diaria](#paso-6-vista-diaria)
10. [Paso 7: Modal de Detalle de Cita](#paso-7-modal-de-detalle-de-cita)
11. [Paso 8: Integración en Rutas](#paso-8-integración-en-rutas)
12. [Pruebas](#pruebas)

---

## 📖 Descripción General

El **Calendario de Citas** proporciona una vista visual de la agenda del odontólogo en formato:
- 📅 **Vista Mensual**: Todas las citas del mes
- 📅 **Vista Semanal**: Citas por día de la semana
- 📅 **Vista Diaria**: Horario completo del día con citas

**Estado Backend:** ✅ **100% LISTO** - Todos los endpoints disponibles

---

## 🔌 Backend Disponible

### Endpoints ya implementados:

#### 1. Listar Citas por Rango de Fechas
```http
GET /api/agenda/citas/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30
```

**Response:**
```json
[
  {
    "id": 1,
    "paciente": 5,
    "paciente_nombre": "María García",
    "odontologo": 3,
    "odontologo_nombre": "Dr. Juan Pérez",
    "fecha_hora": "2025-11-15T10:00:00Z",
    "estado": "CONFIRMADA",
    "motivo": "Limpieza dental",
    "motivo_tipo": "LIMPIEZA",
    "observaciones": "Primera visita"
  }
]
```

#### 2. Obtener Horarios Disponibles
```http
GET /api/agenda/citas/disponibilidad/?fecha=2025-11-15
```

**Response:**
```json
{
  "fecha": "2025-11-15",
  "horarios_disponibles": [
    "09:00", "09:30", "10:00", "10:30",
    "14:00", "14:30", "15:00"
  ]
}
```

---

## 📦 Instalación de Dependencias

### Instalar react-big-calendar y dependencias

```bash
npm install react-big-calendar date-fns
npm install --save-dev @types/react-big-calendar
```

### Importar estilos CSS en tu archivo principal

**Archivo:** `src/index.tsx` o `src/App.tsx`

```typescript
import 'react-big-calendar/lib/css/react-big-calendar.css';
```

---

## 🔧 Paso 1: Tipos TypeScript

### **Archivo:** `src/types/calendario.types.ts`

```typescript
/**
 * Tipos para el Calendario de Citas
 */

// Estados de cita
export type EstadoCita = 'PENDIENTE' | 'CONFIRMADA' | 'ATENDIDA' | 'CANCELADA';

// Tipos de motivo
export type MotivoTipo = 
  | 'CONSULTA'
  | 'LIMPIEZA'
  | 'EXTRACCION'
  | 'ENDODONCIA'
  | 'CIRUGIA'
  | 'REVISION'
  | 'EMERGENCIA'
  | 'OTRO';

// Evento del calendario (adaptado para react-big-calendar)
export interface EventoCalendario {
  id: number;
  title: string; // Nombre del paciente
  start: Date; // Fecha/hora inicio
  end: Date; // Fecha/hora fin (estimado)
  resource: CitaCalendario; // Datos completos de la cita
}

// Datos de la cita
export interface CitaCalendario {
  id: number;
  paciente: number;
  paciente_nombre: string;
  paciente_email?: string;
  odontologo: number;
  odontologo_nombre: string;
  fecha_hora: string; // ISO string
  estado: EstadoCita;
  motivo: string;
  motivo_tipo?: MotivoTipo;
  observaciones?: string;
  duracion_minutos?: number; // Duración estimada (default: 30)
}

// Filtros del calendario
export interface FiltrosCalendario {
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string; // YYYY-MM-DD
  estado?: EstadoCita;
}

// Vista del calendario
export type VistaCalendario = 'month' | 'week' | 'day' | 'agenda';

// Horarios disponibles
export interface DisponibilidadResponse {
  fecha: string;
  horarios_disponibles: string[];
}

// Configuración de colores por estado
export const COLORES_ESTADO: Record<EstadoCita, string> = {
  PENDIENTE: '#FFA726', // Naranja
  CONFIRMADA: '#66BB6A', // Verde
  ATENDIDA: '#42A5F5', // Azul
  CANCELADA: '#EF5350', // Rojo
};

// Configuración de duración por tipo de motivo (minutos)
export const DURACION_POR_TIPO: Record<MotivoTipo, number> = {
  CONSULTA: 30,
  LIMPIEZA: 45,
  EXTRACCION: 60,
  ENDODONCIA: 90,
  CIRUGIA: 120,
  REVISION: 20,
  EMERGENCIA: 30,
  OTRO: 30,
};
```

---

## 🔧 Paso 2: Servicio de API

### **Archivo:** `src/services/calendarioService.ts`

Agregar estos métodos a tu `agendaService.ts` existente o crear un nuevo servicio:

```typescript
import apiClient from './axios';
import { 
  CitaCalendario, 
  FiltrosCalendario, 
  DisponibilidadResponse 
} from '../types/calendario.types';

/**
 * Servicio para gestión del calendario de citas
 */
const calendarioService = {
  /**
   * Obtiene citas en un rango de fechas para el calendario
   * @param filtros - Fecha inicio y fin
   * @returns Promesa con array de citas
   */
  async getCitasCalendario(filtros: FiltrosCalendario): Promise<CitaCalendario[]> {
    try {
      const params = new URLSearchParams();
      params.append('fecha_inicio', filtros.fecha_inicio);
      params.append('fecha_fin', filtros.fecha_fin);
      
      if (filtros.estado) {
        params.append('estado', filtros.estado);
      }

      const response = await apiClient.get(`/agenda/citas/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener citas del calendario:', error);
      throw error;
    }
  },

  /**
   * Obtiene horarios disponibles para una fecha específica
   * @param fecha - Fecha en formato YYYY-MM-DD
   * @returns Promesa con horarios disponibles
   */
  async getDisponibilidad(fecha: string): Promise<DisponibilidadResponse> {
    try {
      const response = await apiClient.get('/agenda/citas/disponibilidad/', {
        params: { fecha }
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener disponibilidad:', error);
      throw error;
    }
  },

  /**
   * Obtiene detalle de una cita específica
   * @param citaId - ID de la cita
   * @returns Promesa con datos de la cita
   */
  async getDetalleCita(citaId: number): Promise<CitaCalendario> {
    try {
      const response = await apiClient.get(`/agenda/citas/${citaId}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener detalle de cita:', error);
      throw error;
    }
  },

  /**
   * Actualiza el estado de una cita
   * @param citaId - ID de la cita
   * @param estado - Nuevo estado
   * @param observaciones - Observaciones opcionales
   * @returns Promesa con cita actualizada
   */
  async actualizarEstadoCita(
    citaId: number, 
    estado: string,
    observaciones?: string
  ): Promise<CitaCalendario> {
    try {
      const response = await apiClient.patch(`/agenda/citas/${citaId}/`, {
        estado,
        observaciones
      });
      return response.data;
    } catch (error) {
      console.error('Error al actualizar estado de cita:', error);
      throw error;
    }
  }
};

export default calendarioService;
```

---

## 🔧 Paso 3: Componente de Calendario

### **Archivo:** `src/components/Calendario/CalendarioCitas.tsx`

```typescript
import React, { useState, useCallback, useMemo } from 'react';
import { Calendar, dateFnsLocalizer, View } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, addDays } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  Box,
  Paper,
  ToggleButtonGroup,
  ToggleButton,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import ViewWeekIcon from '@mui/icons-material/ViewWeek';
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import ViewDayIcon from '@mui/icons-material/ViewDay';
import ViewAgendaIcon from '@mui/icons-material/ViewAgenda';

import { 
  EventoCalendario, 
  CitaCalendario, 
  VistaCalendario,
  COLORES_ESTADO,
  DURACION_POR_TIPO
} from '../../types/calendario.types';
import calendarioService from '../../services/calendarioService';
import ModalDetalleCita from './ModalDetalleCita';

// Configurar localizer con date-fns en español
const locales = {
  'es': es
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { locale: es }),
  getDay,
  locales
});

// Mensajes en español
const messages = {
  allDay: 'Todo el día',
  previous: 'Anterior',
  next: 'Siguiente',
  today: 'Hoy',
  month: 'Mes',
  week: 'Semana',
  day: 'Día',
  agenda: 'Agenda',
  date: 'Fecha',
  time: 'Hora',
  event: 'Cita',
  noEventsInRange: 'No hay citas en este rango',
  showMore: (total: number) => `+ Ver más (${total})`
};

/**
 * Componente principal del Calendario de Citas
 */
const CalendarioCitas: React.FC = () => {
  // Estado
  const [vista, setVista] = useState<View>('month');
  const [fecha, setFecha] = useState<Date>(new Date());
  const [eventos, setEventos] = useState<EventoCalendario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [citaSeleccionada, setCitaSeleccionada] = useState<CitaCalendario | null>(null);
  const [modalAbierto, setModalAbierto] = useState(false);

  /**
   * Convierte citas del backend a eventos del calendario
   */
  const convertirCitasAEventos = (citas: CitaCalendario[]): EventoCalendario[] => {
    return citas.map(cita => {
      const inicio = new Date(cita.fecha_hora);
      const duracion = cita.duracion_minutos || 
                      DURACION_POR_TIPO[cita.motivo_tipo || 'OTRO'] || 
                      30;
      const fin = addDays(inicio, duracion / (24 * 60)); // Convertir minutos a fracción de día

      return {
        id: cita.id,
        title: cita.paciente_nombre,
        start: inicio,
        end: fin,
        resource: cita
      };
    });
  };

  /**
   * Carga citas del rango visible
   */
  const cargarCitas = useCallback(async (fechaActual: Date, vistaActual: View) => {
    setLoading(true);
    setError(null);

    try {
      // Calcular rango según la vista
      let fechaInicio: Date;
      let fechaFin: Date;

      switch (vistaActual) {
        case 'month':
          // Primer y último día del mes
          fechaInicio = new Date(fechaActual.getFullYear(), fechaActual.getMonth(), 1);
          fechaFin = new Date(fechaActual.getFullYear(), fechaActual.getMonth() + 1, 0);
          break;
        case 'week':
          // Inicio y fin de semana
          fechaInicio = startOfWeek(fechaActual, { locale: es });
          fechaFin = addDays(fechaInicio, 6);
          break;
        case 'day':
          // Solo el día actual
          fechaInicio = fechaActual;
          fechaFin = fechaActual;
          break;
        default:
          fechaInicio = fechaActual;
          fechaFin = addDays(fechaActual, 30);
      }

      // Llamar al servicio
      const citas = await calendarioService.getCitasCalendario({
        fecha_inicio: format(fechaInicio, 'yyyy-MM-dd'),
        fecha_fin: format(fechaFin, 'yyyy-MM-dd')
      });

      // Convertir a eventos
      const eventosNuevos = convertirCitasAEventos(citas);
      setEventos(eventosNuevos);
    } catch (err: any) {
      console.error('Error al cargar citas:', err);
      setError(err.response?.data?.error || 'Error al cargar las citas del calendario');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Efecto: Cargar citas al cambiar fecha o vista
   */
  React.useEffect(() => {
    cargarCitas(fecha, vista);
  }, [fecha, vista, cargarCitas]);

  /**
   * Handler: Cambio de vista
   */
  const handleCambiarVista = (
    event: React.MouseEvent<HTMLElement>,
    nuevaVista: View | null
  ) => {
    if (nuevaVista) {
      setVista(nuevaVista);
    }
  };

  /**
   * Handler: Navegación (anterior/siguiente/hoy)
   */
  const handleNavegar = (nuevaFecha: Date) => {
    setFecha(nuevaFecha);
  };

  /**
   * Handler: Click en evento
   */
  const handleSeleccionarEvento = (evento: EventoCalendario) => {
    setCitaSeleccionada(evento.resource);
    setModalAbierto(true);
  };

  /**
   * Handler: Cerrar modal
   */
  const handleCerrarModal = () => {
    setModalAbierto(false);
    setCitaSeleccionada(null);
  };

  /**
   * Handler: Actualizar cita (desde modal)
   */
  const handleActualizarCita = () => {
    // Recargar citas después de actualizar
    cargarCitas(fecha, vista);
    handleCerrarModal();
  };

  /**
   * Estilos personalizados para eventos según estado
   */
  const eventStyleGetter = (evento: EventoCalendario) => {
    const cita = evento.resource;
    const backgroundColor = COLORES_ESTADO[cita.estado];

    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.9,
        color: 'white',
        border: 'none',
        display: 'block',
        fontSize: '12px',
        padding: '2px 5px'
      }
    };
  };

  /**
   * Renderizado
   */
  return (
    <Box>
      {/* Barra de herramientas */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        {/* Selector de vista */}
        <ToggleButtonGroup
          value={vista}
          exclusive
          onChange={handleCambiarVista}
          size="small"
        >
          <ToggleButton value="month">
            <CalendarViewMonthIcon fontSize="small" sx={{ mr: 1 }} />
            Mes
          </ToggleButton>
          <ToggleButton value="week">
            <ViewWeekIcon fontSize="small" sx={{ mr: 1 }} />
            Semana
          </ToggleButton>
          <ToggleButton value="day">
            <ViewDayIcon fontSize="small" sx={{ mr: 1 }} />
            Día
          </ToggleButton>
          <ToggleButton value="agenda">
            <ViewAgendaIcon fontSize="small" sx={{ mr: 1 }} />
            Agenda
          </ToggleButton>
        </ToggleButtonGroup>

        {/* Leyenda de estados */}
        <Box display="flex" gap={1}>
          <Chip label="Pendiente" size="small" sx={{ bgcolor: COLORES_ESTADO.PENDIENTE, color: 'white' }} />
          <Chip label="Confirmada" size="small" sx={{ bgcolor: COLORES_ESTADO.CONFIRMADA, color: 'white' }} />
          <Chip label="Atendida" size="small" sx={{ bgcolor: COLORES_ESTADO.ATENDIDA, color: 'white' }} />
          <Chip label="Cancelada" size="small" sx={{ bgcolor: COLORES_ESTADO.CANCELADA, color: 'white' }} />
        </Box>
      </Box>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Calendario */}
      <Paper elevation={3} sx={{ p: 2, position: 'relative' }}>
        {loading && (
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            display="flex"
            justifyContent="center"
            alignItems="center"
            bgcolor="rgba(255,255,255,0.7)"
            zIndex={10}
          >
            <CircularProgress />
          </Box>
        )}

        <Calendar
          localizer={localizer}
          events={eventos}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 600 }}
          view={vista}
          onView={setVista}
          date={fecha}
          onNavigate={handleNavegar}
          onSelectEvent={handleSeleccionarEvento}
          eventPropGetter={eventStyleGetter}
          messages={messages}
          culture="es"
          step={30} // Intervalo de 30 minutos
          timeslots={2} // 2 slots por hora
          min={new Date(0, 0, 0, 8, 0, 0)} // Hora inicio: 8:00 AM
          max={new Date(0, 0, 0, 20, 0, 0)} // Hora fin: 8:00 PM
        />
      </Paper>

      {/* Modal de detalle */}
      <ModalDetalleCita
        abierto={modalAbierto}
        cita={citaSeleccionada}
        onCerrar={handleCerrarModal}
        onActualizar={handleActualizarCita}
      />
    </Box>
  );
};

export default CalendarioCitas;
```

---

*Continuará en la siguiente parte...*

## 📚 Archivos Relacionados

- Parte 2: Modal de Detalle de Cita
- Parte 3: Vistas Personalizadas (Mensual, Semanal, Diaria)
- Parte 4: Integración y Pruebas
