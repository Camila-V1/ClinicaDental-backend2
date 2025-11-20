# 📅 Agenda y Gestión de Citas

## 🎯 Objetivo
Crear un calendario interactivo para gestionar las citas de todos los odontólogos de la clínica, con vistas por día, semana y mes.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Calendario visual** con citas de todos los odontólogos
2. **Vistas**: Día, Semana, Mes
3. **Filtrar por odontólogo** o ver todos
4. **Crear/Editar/Cancelar** citas
5. **Verificar disponibilidad** de horarios
6. **Código de colores** por estado (pendiente, confirmada, completada)
7. **Notificaciones** de citas próximas

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar citas (con filtros)
GET /api/agenda/citas/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30&odontologo=1
Response: {
  count: 45,
  results: [
    {
      id: 1,
      paciente: { id: 5, usuario: { full_name: "María García" } },
      odontologo: { id: 1, usuario: { full_name: "Dr. Juan Pérez" } },
      fecha_hora: "2025-11-20T10:00:00Z",
      duracion_minutos: 30,
      motivo: "Limpieza dental",
      estado: "CONFIRMADA",
      notas: "Primera cita"
    }
  ]
}

// 2. Crear cita
POST /api/agenda/citas/
Body: {
  paciente: 5,
  odontologo: 1,
  fecha_hora: "2025-11-21T14:00:00",
  duracion_minutos: 60,
  motivo: "Endodoncia",
  estado: "PENDIENTE"
}

// 3. Actualizar cita
PATCH /api/agenda/citas/{id}/
Body: { estado: "CONFIRMADA" }

// 4. Cancelar cita
PATCH /api/agenda/citas/{id}/
Body: { estado: "CANCELADA", notas: "Paciente no disponible" }

// 5. Verificar disponibilidad
GET /api/agenda/disponibilidad/?odontologo=1&fecha=2025-11-21
Response: {
  bloques_disponibles: [
    { hora_inicio: "09:00", hora_fin: "09:30" },
    { hora_inicio: "09:30", hora_fin: "10:00" },
    // ...
  ]
}

// 6. Horarios del odontólogo
GET /api/agenda/horarios/?odontologo=1
Response: {
  count: 5,
  results: [
    {
      dia_semana: 1,  // Lunes
      hora_inicio: "09:00:00",
      hora_fin: "13:00:00",
      activo: true
    }
  ]
}
```

---

## 💻 Implementación Frontend

### 1. Página de Agenda

```typescript
// src/pages/admin/Agenda.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import esLocale from '@fullcalendar/core/locales/es';
import { agendaService } from '@/services/admin/agendaService';
import CitaModal from '@/components/admin/agenda/CitaModal';
import { toast } from 'react-hot-toast';

export default function Agenda() {
  const queryClient = useQueryClient();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedOdontologo, setSelectedOdontologo] = useState('');
  const [citaModal, setCitaModal] = useState<{
    isOpen: boolean;
    cita?: any;
    dateInfo?: any;
  }>({ isOpen: false });

  // Fetch citas
  const { data: citas, isLoading } = useQuery({
    queryKey: ['citas', selectedDate, selectedOdontologo],
    queryFn: () => agendaService.getCitas({
      fecha_inicio: new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1),
      fecha_fin: new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0),
      odontologo: selectedOdontologo || undefined,
    }),
  });

  // Fetch odontólogos
  const { data: odontologos } = useQuery({
    queryKey: ['odontologos-activos'],
    queryFn: () => agendaService.getOdontologos(),
  });

  // Crear/Actualizar cita
  const citaMutation = useMutation({
    mutationFn: (data: any) =>
      citaModal.cita
        ? agendaService.updateCita(citaModal.cita.id, data)
        : agendaService.createCita(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['citas'] });
      setCitaModal({ isOpen: false });
      toast.success(citaModal.cita ? 'Cita actualizada' : 'Cita creada');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al guardar cita');
    },
  });

  // Convertir citas a eventos de FullCalendar
  const events = citas?.results.map((cita: any) => ({
    id: cita.id,
    title: `${cita.paciente.usuario.full_name} - ${cita.motivo}`,
    start: cita.fecha_hora,
    end: new Date(new Date(cita.fecha_hora).getTime() + cita.duracion_minutos * 60000),
    backgroundColor: getColorByEstado(cita.estado),
    borderColor: getColorByEstado(cita.estado),
    extendedProps: { ...cita },
  })) || [];

  const handleDateClick = (info: any) => {
    setCitaModal({
      isOpen: true,
      dateInfo: info,
    });
  };

  const handleEventClick = (info: any) => {
    setCitaModal({
      isOpen: true,
      cita: info.event.extendedProps,
    });
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agenda de Citas</h1>
          <p className="text-gray-600">Gestiona las citas de todos los odontólogos</p>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filtrar por odontólogo:</label>
          <select
            value={selectedOdontologo}
            onChange={(e) => setSelectedOdontologo(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los odontólogos</option>
            {odontologos?.results.map((odon: any) => (
              <option key={odon.id} value={odon.id}>
                Dr. {odon.usuario.full_name}
              </option>
            ))}
          </select>
          
          {/* Leyenda de colores */}
          <div className="ml-auto flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span>Pendiente</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span>Confirmada</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span>Completada</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span>Cancelada</span>
            </div>
          </div>
        </div>
      </div>

      {/* Calendario */}
      <div className="bg-white rounded-lg shadow p-6">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
          }}
          locale={esLocale}
          events={events}
          dateClick={handleDateClick}
          eventClick={handleEventClick}
          slotMinTime="08:00:00"
          slotMaxTime="20:00:00"
          allDaySlot={false}
          height="auto"
          businessHours={{
            daysOfWeek: [1, 2, 3, 4, 5],
            startTime: '09:00',
            endTime: '18:00',
          }}
        />
      </div>

      {/* Modal de Cita */}
      <CitaModal
        isOpen={citaModal.isOpen}
        onClose={() => setCitaModal({ isOpen: false })}
        cita={citaModal.cita}
        dateInfo={citaModal.dateInfo}
        onSubmit={(data) => citaMutation.mutate(data)}
        isLoading={citaMutation.isPending}
      />
    </div>
  );
}

function getColorByEstado(estado: string) {
  const colors = {
    PENDIENTE: '#eab308',     // yellow-500
    CONFIRMADA: '#3b82f6',    // blue-500
    COMPLETADA: '#10b981',    // green-500
    CANCELADA: '#ef4444',     // red-500
  };
  return colors[estado] || '#6b7280';
}
```

---

### 2. Modal de Cita

```typescript
// src/components/admin/agenda/CitaModal.tsx
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Modal from '@/components/ui/Modal';
import { agendaService } from '@/services/admin/agendaService';

const citaSchema = z.object({
  paciente: z.number().min(1, 'Selecciona un paciente'),
  odontologo: z.number().min(1, 'Selecciona un odontólogo'),
  fecha_hora: z.string(),
  duracion_minutos: z.number().min(15).max(240),
  motivo: z.string().min(3, 'El motivo es requerido'),
  estado: z.enum(['PENDIENTE', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA']),
  notas: z.string().optional(),
});

type CitaFormData = z.infer<typeof citaSchema>;

interface CitaModalProps {
  isOpen: boolean;
  onClose: () => void;
  cita?: any;
  dateInfo?: any;
  onSubmit: (data: CitaFormData) => void;
  isLoading: boolean;
}

export default function CitaModal({
  isOpen,
  onClose,
  cita,
  dateInfo,
  onSubmit,
  isLoading,
}: CitaModalProps) {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<CitaFormData>({
    resolver: zodResolver(citaSchema),
    defaultValues: cita || {
      duracion_minutos: 30,
      estado: 'PENDIENTE',
      fecha_hora: dateInfo?.dateStr || new Date().toISOString().slice(0, 16),
    },
  });

  // Fetch pacientes
  const { data: pacientes } = useQuery({
    queryKey: ['pacientes-activos'],
    queryFn: () => agendaService.getPacientes(),
    enabled: isOpen,
  });

  // Fetch odontólogos
  const { data: odontologos } = useQuery({
    queryKey: ['odontologos-activos'],
    queryFn: () => agendaService.getOdontologos(),
    enabled: isOpen,
  });

  const odontologoSeleccionado = watch('odontologo');
  const fechaHora = watch('fecha_hora');

  // Fetch disponibilidad
  const { data: disponibilidad } = useQuery({
    queryKey: ['disponibilidad', odontologoSeleccionado, fechaHora],
    queryFn: () => agendaService.getDisponibilidad(odontologoSeleccionado, fechaHora),
    enabled: !!odontologoSeleccionado && !!fechaHora,
  });

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={cita ? 'Editar Cita' : 'Nueva Cita'}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Paciente */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Paciente *
          </label>
          <select
            {...register('paciente', { valueAsNumber: true })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Selecciona un paciente</option>
            {pacientes?.results.map((pac: any) => (
              <option key={pac.id} value={pac.id}>
                {pac.usuario.full_name}
              </option>
            ))}
          </select>
          {errors.paciente && (
            <p className="text-red-500 text-sm mt-1">{errors.paciente.message}</p>
          )}
        </div>

        {/* Odontólogo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Odontólogo *
          </label>
          <select
            {...register('odontologo', { valueAsNumber: true })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Selecciona un odontólogo</option>
            {odontologos?.results.map((odon: any) => (
              <option key={odon.id} value={odon.id}>
                Dr. {odon.usuario.full_name} {odon.especialidad && `- ${odon.especialidad}`}
              </option>
            ))}
          </select>
          {errors.odontologo && (
            <p className="text-red-500 text-sm mt-1">{errors.odontologo.message}</p>
          )}
        </div>

        {/* Fecha y Hora */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha y Hora *
            </label>
            <input
              type="datetime-local"
              {...register('fecha_hora')}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            {errors.fecha_hora && (
              <p className="text-red-500 text-sm mt-1">{errors.fecha_hora.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duración (minutos) *
            </label>
            <select
              {...register('duracion_minutos', { valueAsNumber: true })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={15}>15 min</option>
              <option value={30}>30 min</option>
              <option value={45}>45 min</option>
              <option value={60}>1 hora</option>
              <option value={90}>1.5 horas</option>
              <option value={120}>2 horas</option>
            </select>
          </div>
        </div>

        {/* Motivo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Motivo de la Cita *
          </label>
          <input
            {...register('motivo')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ej: Limpieza dental, Endodoncia"
          />
          {errors.motivo && (
            <p className="text-red-500 text-sm mt-1">{errors.motivo.message}</p>
          )}
        </div>

        {/* Estado */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estado
          </label>
          <select
            {...register('estado')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="PENDIENTE">Pendiente</option>
            <option value="CONFIRMADA">Confirmada</option>
            <option value="COMPLETADA">Completada</option>
            <option value="CANCELADA">Cancelada</option>
          </select>
        </div>

        {/* Notas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notas (opcional)
          </label>
          <textarea
            {...register('notas')}
            rows={3}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Observaciones adicionales..."
          />
        </div>

        {/* Alerta de disponibilidad */}
        {disponibilidad && !disponibilidad.disponible && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ El odontólogo tiene otra cita en este horario
            </p>
          </div>
        )}

        {/* Botones */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Guardando...' : cita ? 'Actualizar' : 'Crear Cita'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
```

---

### 3. Servicio de Agenda

```typescript
// src/services/admin/agendaService.ts
import api from '@/lib/axios';

export const agendaService = {
  // Listar citas
  async getCitas(filters: any = {}) {
    const params = new URLSearchParams();
    
    if (filters.fecha_inicio) params.append('fecha_inicio', filters.fecha_inicio.toISOString().split('T')[0]);
    if (filters.fecha_fin) params.append('fecha_fin', filters.fecha_fin.toISOString().split('T')[0]);
    if (filters.odontologo) params.append('odontologo', filters.odontologo);
    
    const { data } = await api.get(`/agenda/citas/?${params.toString()}`);
    return data;
  },

  // Crear cita
  async createCita(citaData: any) {
    const { data } = await api.post('/agenda/citas/', citaData);
    return data;
  },

  // Actualizar cita
  async updateCita(id: number, citaData: any) {
    const { data } = await api.patch(`/agenda/citas/${id}/`, citaData);
    return data;
  },

  // Verificar disponibilidad
  async getDisponibilidad(odontologoId: number, fecha: string) {
    const { data } = await api.get('/agenda/disponibilidad/', {
      params: { odontologo: odontologoId, fecha }
    });
    return data;
  },

  // Obtener odontólogos
  async getOdontologos() {
    const { data } = await api.get('/usuarios/usuarios/', {
      params: { tipo_usuario: 'ODONTOLOGO', is_active: true }
    });
    return data;
  },

  // Obtener pacientes
  async getPacientes() {
    const { data } = await api.get('/usuarios/pacientes/', {
      params: { activo: true }
    });
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Instalar FullCalendar
- [ ] Crear página Agenda.tsx
- [ ] Crear CitaModal
- [ ] Crear agendaService
- [ ] Implementar vistas día/semana/mes
- [ ] Código de colores por estado
- [ ] Verificación de disponibilidad
- [ ] Filtro por odontólogo
- [ ] Drag & drop (opcional)

---

**Siguiente:** `05_tratamientos_servicios.md`
