# 📅 FASE 3: AGENDA Y CITAS - CALENDARIO INTERACTIVO

## 📋 Endpoints de Agenda

### Sistema de citas y calendario médico

```javascript
// Endpoints agenda
const APPOINTMENT_ENDPOINTS = {
  // Citas
  appointments: '/api/agenda/citas/',
  appointmentDetail: '/api/agenda/citas/{id}/',
  
  // Estados de citas
  confirmAppointment: '/api/agenda/citas/{id}/confirmar/',
  cancelAppointment: '/api/agenda/citas/{id}/cancelar/',
  attendAppointment: '/api/agenda/citas/{id}/atender/',
  
  // Filtros especiales
  upcomingAppointments: '/api/agenda/citas/proximas/',
  todayAppointments: '/api/agenda/citas/hoy/'
};
```

## 🔧 1. Servicio de Agenda

```javascript
// services/appointmentService.js
import api from './apiConfig';

class AppointmentService {
  // Citas
  async getAppointments(date = '', doctor = '', status = '', page = 1) {
    try {
      const params = { 
        date: date || undefined,
        doctor: doctor || undefined,
        estado: status || undefined,
        page
      };
      const response = await api.get('/api/agenda/citas/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener citas' };
    }
  }

  async getAppointmentDetail(appointmentId) {
    try {
      const response = await api.get(`/api/agenda/citas/${appointmentId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener cita' };
    }
  }

  async createAppointment(appointmentData) {
    try {
      const response = await api.post('/api/agenda/citas/', appointmentData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear cita' 
      };
    }
  }

  async updateAppointment(appointmentId, appointmentData) {
    try {
      const response = await api.put(`/api/agenda/citas/${appointmentId}/`, appointmentData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar cita' 
      };
    }
  }

  async deleteAppointment(appointmentId) {
    try {
      await api.delete(`/api/agenda/citas/${appointmentId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar cita' };
    }
  }

  // Estados de citas
  async confirmAppointment(appointmentId) {
    try {
      const response = await api.post(`/api/agenda/citas/${appointmentId}/confirmar/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al confirmar cita' 
      };
    }
  }

  async cancelAppointment(appointmentId) {
    try {
      const response = await api.post(`/api/agenda/citas/${appointmentId}/cancelar/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al cancelar cita' 
      };
    }
  }

  async attendAppointment(appointmentId) {
    try {
      const response = await api.post(`/api/agenda/citas/${appointmentId}/atender/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al atender cita' 
      };
    }
  }

  // Filtros especiales
  async getUpcomingAppointments() {
    try {
      const response = await api.get('/api/agenda/citas/proximas/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener citas próximas' };
    }
  }

  async getTodayAppointments() {
    try {
      const response = await api.get('/api/agenda/citas/hoy/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener citas de hoy' };
    }
  }
}

export default new AppointmentService();
```

## 📅 2. Hook de Agenda

```javascript
// hooks/useAppointments.js
import { useState, useEffect } from 'react';
import appointmentService from '../services/appointmentService';

export function useAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAppointments = async (date = '', doctor = '', status = '') => {
    setLoading(true);
    setError('');
    
    const result = await appointmentService.getAppointments(date, doctor, status);
    
    if (result.success) {
      setAppointments(result.data.results || result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const createAppointment = async (appointmentData) => {
    const result = await appointmentService.createAppointment(appointmentData);
    if (result.success) {
      await fetchAppointments(); // Refrescar lista
    }
    return result;
  };

  const updateAppointmentStatus = async (appointmentId, action) => {
    let result;
    
    switch (action) {
      case 'confirm':
        result = await appointmentService.confirmAppointment(appointmentId);
        break;
      case 'cancel':
        result = await appointmentService.cancelAppointment(appointmentId);
        break;
      case 'attend':
        result = await appointmentService.attendAppointment(appointmentId);
        break;
      default:
        return { success: false, error: 'Acción no válida' };
    }

    if (result.success) {
      await fetchAppointments(); // Refrescar lista
    }
    return result;
  };

  return {
    appointments,
    loading,
    error,
    fetchAppointments,
    createAppointment,
    updateAppointmentStatus,
    refetch: () => fetchAppointments()
  };
}

export function useAvailability() {
  // NOTA: Funcionalidad no implementada en el backend actual
  // La gestión de disponibilidad debe agregarse en agenda/views.py
  
  return {
    availability: [],
    loading: false,
    error: 'Funcionalidad de disponibilidad no implementada en backend',
    fetchAvailability: () => Promise.resolve()
  };
}

export function useDailySchedule() {
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchDailySchedule = async (date) => {
    setLoading(true);
    setError('');
    
    const result = await appointmentService.getTodayAppointments();
    
    if (result.success) {
      setSchedule(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return {
    schedule,
    loading,
    error,
    fetchDailySchedule
  };
}
```

## 📅 3. Calendario de Citas

```javascript
// components/AppointmentCalendar.jsx
import React, { useState, useEffect } from 'react';
import { useAppointments } from '../hooks/useAppointments';
import { useAuth } from '../contexts/AuthContext';

function AppointmentCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [view, setView] = useState('month'); // 'month', 'week', 'day'
  
  const { appointments, loading, error, fetchAppointments, updateAppointmentStatus } = useAppointments();
  const { user } = useAuth();

  // Funciones de utilidad para fechas
  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  const getMonthDays = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Días del mes anterior
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const day = new Date(year, month, -i);
      days.push({ date: day, isCurrentMonth: false });
    }
    
    // Días del mes actual
    for (let day = 1; day <= daysInMonth; day++) {
      const dayDate = new Date(year, month, day);
      days.push({ date: dayDate, isCurrentMonth: true });
    }
    
    // Completar la última semana
    const remainingDays = 42 - days.length; // 6 semanas × 7 días
    for (let day = 1; day <= remainingDays; day++) {
      const dayDate = new Date(year, month + 1, day);
      days.push({ date: dayDate, isCurrentMonth: false });
    }
    
    return days;
  };

  const getAppointmentsForDate = (date) => {
    const dateStr = formatDate(date);
    return appointments.filter(apt => 
      apt.fecha === dateStr
    );
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDIENTE': 'bg-blue-500',
      'CONFIRMADA': 'bg-green-500',
      'ATENDIDA': 'bg-purple-500',
      'CANCELADA': 'bg-red-500'
    };
    return colors[status] || 'bg-gray-400';
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const handleAppointmentClick = (appointment) => {
    // Aquí puedes abrir un modal o navegar a los detalles
    console.log('Cita seleccionada:', appointment);
  };

  const handleQuickAction = async (appointmentId, action) => {
    const result = await updateAppointmentStatus(appointmentId, action);
    if (result.success) {
      alert('Acción realizada correctamente');
    } else {
      alert('Error: ' + result.error);
    }
  };

  useEffect(() => {
    // Cargar citas del mes actual
    const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    
    fetchAppointments(); // Cargar todas las citas o filtrar por rango de fechas
  }, [currentDate]);

  const monthDays = getMonthDays(currentDate);
  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  if (loading) {
    return <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Calendario de Citas</h1>
        <div className="flex space-x-2">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Nueva Cita
          </button>
          <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
            Ver Agenda del Día
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Controles del calendario */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigateMonth(-1)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            ← Anterior
          </button>
          <h2 className="text-xl font-semibold">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <button
            onClick={() => navigateMonth(1)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            Siguiente →
          </button>
        </div>
        
        <div className="flex space-x-2">
          <button 
            onClick={() => setCurrentDate(new Date())}
            className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Hoy
          </button>
        </div>
      </div>

      {/* Calendario */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Días de la semana */}
        <div className="grid grid-cols-7 bg-gray-50">
          {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(day => (
            <div key={day} className="p-4 text-center text-sm font-medium text-gray-700">
              {day}
            </div>
          ))}
        </div>

        {/* Días del mes */}
        <div className="grid grid-cols-7">
          {monthDays.map((day, index) => {
            const dayAppointments = getAppointmentsForDate(day.date);
            const isToday = formatDate(day.date) === formatDate(new Date());
            const isSelected = formatDate(day.date) === formatDate(selectedDate);
            
            return (
              <div
                key={index}
                onClick={() => setSelectedDate(day.date)}
                className={`min-h-[120px] p-2 border-b border-r border-gray-200 cursor-pointer hover:bg-gray-50 ${
                  !day.isCurrentMonth ? 'bg-gray-50 text-gray-400' : ''
                } ${isToday ? 'bg-blue-50' : ''} ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className={`text-sm font-medium mb-1 ${isToday ? 'text-blue-600' : ''}`}>
                  {day.date.getDate()}
                </div>
                
                {/* Citas del día */}
                <div className="space-y-1">
                  {dayAppointments.slice(0, 3).map((appointment) => (
                    <div
                      key={appointment.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAppointmentClick(appointment);
                      }}
                      className={`text-xs p-1 rounded text-white cursor-pointer hover:opacity-80 ${getStatusColor(appointment.estado)}`}
                      title={`${appointment.hora} - ${appointment.paciente_nombre}`}
                    >
                      <div className="truncate">
                        {appointment.hora} {appointment.paciente_nombre}
                      </div>
                    </div>
                  ))}
                  
                  {dayAppointments.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{dayAppointments.length - 3} más
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Panel lateral con detalles del día seleccionado */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">
          Citas para {selectedDate.toLocaleDateString('es-ES', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </h3>
        
        {getAppointmentsForDate(selectedDate).length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            No hay citas programadas para este día
          </div>
        ) : (
          <div className="space-y-3">
            {getAppointmentsForDate(selectedDate).map((appointment) => (
              <div key={appointment.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{appointment.hora}</span>
                      <span className={`px-2 py-1 text-xs rounded-full text-white ${getStatusColor(appointment.estado)}`}>
                        {appointment.estado}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      <strong>Paciente:</strong> {appointment.paciente_nombre}
                    </div>
                    <div className="text-sm text-gray-600">
                      <strong>Tratamiento:</strong> {appointment.tratamiento || 'Consulta general'}
                    </div>
                    {appointment.observaciones && (
                      <div className="text-sm text-gray-600">
                        <strong>Observaciones:</strong> {appointment.observaciones}
                      </div>
                    )}
                  </div>
                  
                  {appointment.estado === 'PENDIENTE' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleQuickAction(appointment.id, 'confirm')}
                        className="text-green-600 hover:text-green-800 text-sm"
                      >
                        Confirmar
                      </button>
                      <button
                        onClick={() => handleQuickAction(appointment.id, 'cancel')}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Cancelar
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AppointmentCalendar;
```

## 📋 4. Lista de Citas Diarias

```javascript
// components/DailyAppointments.jsx
import React, { useState, useEffect } from 'react';
import { useDailySchedule } from '../hooks/useAppointments';
import appointmentService from '../services/appointmentService';

function DailyAppointments() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const { schedule, loading, error, fetchDailySchedule } = useDailySchedule();

  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  const handleStatusChange = async (appointmentId, newStatus, data = {}) => {
    let result;
    
    switch (newStatus) {
      case 'CONFIRMADA':
        result = await appointmentService.confirmAppointment(appointmentId);
        break;
      case 'CANCELADA':
        const motivo = prompt('Motivo de la cancelación:');
        if (motivo) {
          result = await appointmentService.cancelAppointment(appointmentId, motivo);
        }
        break;
      default:
        return;
    }

    if (result && result.success) {
      fetchDailySchedule(formatDate(selectedDate));
      alert('Estado actualizado correctamente');
    } else {
      alert('Error al actualizar el estado: ' + (result?.error || 'Error desconocido'));
    }
  };

  const getTimeSlots = () => {
    const slots = [];
    for (let hour = 8; hour < 20; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`);
      slots.push(`${hour.toString().padStart(2, '0')}:30`);
    }
    return slots;
  };

  const getAppointmentForTime = (time) => {
    if (!schedule || !schedule.citas) return null;
    return schedule.citas.find(apt => apt.hora === time);
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDIENTE': 'bg-blue-100 border-blue-300 text-blue-800',
      'CONFIRMADA': 'bg-green-100 border-green-300 text-green-800',
      'ATENDIDA': 'bg-purple-100 border-purple-300 text-purple-800',
      'CANCELADA': 'bg-red-100 border-red-300 text-red-800'
    };
    return colors[status] || 'bg-gray-100 border-gray-300 text-gray-800';
  };

  useEffect(() => {
    fetchDailySchedule(formatDate(selectedDate));
  }, [selectedDate]);

  const timeSlots = getTimeSlots();

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Agenda del Día</h1>
        
        <div className="flex items-center space-x-4">
          <input
            type="date"
            value={formatDate(selectedDate)}
            onChange={(e) => setSelectedDate(new Date(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Nueva Cita
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agenda de horarios */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold">
                  {selectedDate.toLocaleDateString('es-ES', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </h2>
              </div>
              
              <div className="divide-y divide-gray-100">
                {timeSlots.map((time) => {
                  const appointment = getAppointmentForTime(time);
                  
                  return (
                    <div key={time} className="flex items-center p-4 hover:bg-gray-50">
                      <div className="w-20 text-sm font-medium text-gray-500">
                        {time}
                      </div>
                      
                      <div className="flex-1">
                        {appointment ? (
                          <div className={`border rounded-lg p-3 ${getStatusColor(appointment.estado)}`}>
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="font-medium">
                                  {appointment.paciente_nombre}
                                </div>
                                <div className="text-sm opacity-75">
                                  {appointment.tratamiento || 'Consulta general'}
                                </div>
                                {appointment.doctor_nombre && (
                                  <div className="text-sm opacity-75">
                                    Dr. {appointment.doctor_nombre}
                                  </div>
                                )}
                              </div>
                              
                              <div className="flex space-x-1 ml-4">
                                {appointment.estado === 'PENDIENTE' && (
                                  <>
                                    <button
                                      onClick={() => handleStatusChange(appointment.id, 'CONFIRMADA')}
                                      className="text-green-600 hover:text-green-800 text-xs px-2 py-1 bg-white rounded border"
                                      title="Confirmar cita"
                                    >
                                      ✓
                                    </button>
                                    <button
                                      onClick={() => handleStatusChange(appointment.id, 'CANCELADA')}
                                      className="text-red-600 hover:text-red-800 text-xs px-2 py-1 bg-white rounded border"
                                      title="Cancelar cita"
                                    >
                                      ✗
                                    </button>
                                  </>
                                )}
                                
                                {appointment.estado === 'CONFIRMADA' && (
                                  <button
                                    onClick={() => handleStatusChange(appointment.id, 'ATENDIDA')}
                                    className="text-purple-600 hover:text-purple-800 text-xs px-2 py-1 bg-white rounded border"
                                    title="Marcar como atendida"
                                  >
                                    Atender
                                  </button>
                                )}
                                
                                <button
                                  className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 bg-white rounded border"
                                  title="Ver detalles"
                                >
                                  👁
                                </button>
                              </div>
                            </div>
                            
                            {appointment.observaciones && (
                              <div className="text-sm mt-2 opacity-75">
                                <strong>Obs:</strong> {appointment.observaciones}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-gray-400 text-sm italic">
                            Horario disponible
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Panel de estadísticas */}
          <div className="space-y-6">
            {/* Resumen del día */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Resumen del Día</h3>
              
              {schedule && (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total de citas:</span>
                    <span className="font-medium">{schedule.total_citas || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confirmadas:</span>
                    <span className="font-medium text-green-600">
                      {schedule.citas_confirmadas || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pendientes:</span>
                    <span className="font-medium text-yellow-600">
                      {schedule.citas_pendientes || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Canceladas:</span>
                    <span className="font-medium text-red-600">
                      {schedule.citas_canceladas || 0}
                    </span>
                  </div>
                  
                  <hr className="my-3" />
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tiempo ocupado:</span>
                    <span className="font-medium">
                      {schedule.tiempo_ocupado || '0h'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tiempo libre:</span>
                    <span className="font-medium">
                      {schedule.tiempo_libre || '0h'}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Acciones rápidas */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Acciones Rápidas</h3>
              
              <div className="space-y-2">
                <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                  Nueva Cita
                </button>
                <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700">
                  Buscar Paciente
                </button>
                <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700">
                  Ver Disponibilidad
                </button>
                <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700">
                  Reportes del Día
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DailyAppointments;
```

## ✅ Próximos Pasos

1. Implementar formularios de creación/edición de citas
2. Agregar sistema de notificaciones
3. Continuar con **06_historial_clinico.md**

---
**Endpoints implementados**: ✅ CRUD Citas ✅ Estados de citas ✅ Disponibilidad ✅ Calendario ✅ Agenda diaria