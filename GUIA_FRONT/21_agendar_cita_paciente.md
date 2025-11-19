# Guía 21: Agendar Cita (Paciente)

## 📋 Información General

**Caso de Uso**: CU12 - Gestión de Citas  
**Actor**: Paciente  
**Objetivo**: Permitir que el paciente agende una nueva cita con un odontólogo

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver horarios disponibles de odontólogos
- ✅ Seleccionar fecha y hora para la cita
- ✅ Especificar motivo de la consulta
- ✅ Recibir confirmación inmediata

---

## 🔌 API Endpoints

### 1. Obtener Odontólogos Disponibles
```
GET /api/usuarios/odontologos/
```

**Respuesta**:
```json
[
  {
    "id": 103,
    "nombre": "Dr. Juan",
    "apellido": "Pérez",
    "nombre_completo": "Dr. Dr. Juan Pérez",
    "email": "odontologo@clinica-demo.com",
    "telefono": "987654321",
    "especialidad": "Endodoncia",
    "cedula_profesional": "MP12345"
  }
]
```

---

### 2. Obtener Horarios Disponibles
```
GET /api/agenda/citas/horarios_disponibles/
```

**Query params**:
- `odontologo`: ID del odontólogo (requerido)
- `fecha`: Fecha en formato YYYY-MM-DD (requerido)
- `duracion`: Duración en minutos (opcional, default: 30)

**Ejemplo**:
```
GET /api/agenda/citas/horarios_disponibles/?odontologo=103&fecha=2025-12-01
```

**Respuesta**:
```json
{
  "fecha": "2025-12-01",
  "odontologo": "Dr. Juan Pérez",
  "odontologo_id": 103,
  "total_disponibles": 18,
  "total_ocupados": 2,
  "horarios": [
    {
      "hora": "08:00",
      "disponible": true,
      "fecha_hora_completa": "2025-12-01T08:00:00"
    },
    {
      "hora": "08:30",
      "disponible": true,
      "fecha_hora_completa": "2025-12-01T08:30:00"
    },
    {
      "hora": "09:00",
      "disponible": false,
      "fecha_hora_completa": "2025-12-01T09:00:00"
    }
  ]
}
```

---

### 3. Crear Cita
```
POST /api/agenda/citas/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body de la petición**:
```json
{
  "paciente": 104,
  "odontologo": 103,
  "fecha_hora": "2025-12-01T10:00:00Z",
  "motivo_tipo": "CONSULTA",
  "motivo": "Dolor en muela derecha",
  "observaciones": "Dolor intenso desde hace 3 días",
  "item_plan": null
}
```

**⚠️ CRÍTICO - Campo `paciente` requerido**:
```typescript
// El backend REQUIERE el campo paciente (ID del PerfilPaciente)
{
  "paciente": 104,  // ← ID del PerfilPaciente = ID del Usuario
  "odontologo": 103,
  // ... resto de campos
}

// ⚠️ IMPORTANTE: PerfilPaciente usa OneToOneField con primary_key=True
// Esto significa que el ID del PerfilPaciente ES el mismo que el ID del Usuario

// Obtener desde el contexto de autenticación:
const { user } = useAuth();
const pacienteId = user?.id;  // ← Usar directamente el ID del usuario
```

**IMPORTANTE - Tipos de Cita**:

#### A) Cita General (sin plan)
```json
{
  "motivo_tipo": "CONSULTA",  // CONSULTA | URGENCIA | LIMPIEZA | REVISION
  "item_plan": null           // Sin vincular a plan
}
```

#### B) Cita de Tratamiento (vinculada a plan)
```json
{
  "motivo_tipo": "PLAN",      // Tipo especial
  "item_plan": 45,            // ID del item del plan a realizar
  "motivo": "Endodoncia pieza 36"
}
```

**Respuesta exitosa** (201 Created):
```json
{
  "id": 145,
  "paciente": 104,
  "paciente_nombre": "María",
  "paciente_email": "paciente1@test.com",
  "odontologo": 103,
  "odontologo_nombre": "Dr. Juan",
  "fecha_hora": "2025-12-01T10:00:00Z",
  "estado": "PENDIENTE",
  "motivo_tipo": "CONSULTA",
  "motivo_tipo_display": "Consulta General",
  "motivo": "Dolor en muela derecha",
  "observaciones": "Dolor intenso desde hace 3 días",
  "precio_display": "$50.00",
  "es_cita_plan": false,
  "item_plan": null,
  "item_plan_info": null
}
```

**Validaciones del Backend**:
- ❌ Fecha en el pasado → 400 Bad Request
- ❌ Odontólogo no existe → 404 Not Found
- ❌ Horario ocupado → 400 Bad Request ("Ya existe una cita en ese horario")
- ❌ Fuera de horario laboral → 400 Bad Request

---

## 📚 Tipos de Motivo (motivo_tipo)

⚠️ **IMPORTANTE**: Los valores deben coincidir **exactamente** con las choices del backend.

```typescript
export type MotivoTipo = 
  | 'CONSULTA'   // Consulta General - $30.00
  | 'URGENCIA'   // Urgencia/Dolor - $80.00
  | 'LIMPIEZA'   // Limpieza Dental - $60.00
  | 'REVISION'   // Revisión/Control - $20.00
  | 'PLAN';      // Tratamiento de mi Plan - $0.00 (incluido)

export const MOTIVOS_CITA = [
  { value: 'CONSULTA', label: 'Consulta General', precio: '$30.00', requierePlan: false },
  { value: 'URGENCIA', label: 'Urgencia/Dolor', precio: '$80.00', requierePlan: false },
  { value: 'LIMPIEZA', label: 'Limpieza Dental', precio: '$60.00', requierePlan: false },
  { value: 'REVISION', label: 'Revisión/Control', precio: '$20.00', requierePlan: false },
  { value: 'PLAN', label: 'Tratamiento Programado (Plan)', precio: 'Incluido', requierePlan: true }
];
```

---

## 🔧 Implementación Frontend

### 1. Service - `agendaService.ts`

```typescript
// src/services/agendaService.ts

import apiClient from './apiConfig';

export interface CrearCitaData {
  paciente: number;  // ID del PerfilPaciente (requerido)
  odontologo: number;
  fecha_hora: string; // ISO 8601: "2025-12-01T10:00:00Z"
  motivo_tipo: 'CONSULTA' | 'URGENCIA' | 'LIMPIEZA' | 'REVISION' | 'PLAN';
  motivo: string;
  observaciones?: string;
  item_plan?: number | null; // Solo si motivo_tipo === 'PLAN'
}

export interface Cita {
  id: number;
  paciente: number;
  paciente_nombre: string;
  paciente_email: string;
  odontologo: number;
  odontologo_nombre: string;
  fecha_hora: string;
  estado: 'PENDIENTE' | 'CONFIRMADA' | 'COMPLETADA' | 'CANCELADA';
  motivo_tipo: string;
  motivo_tipo_display: string;
  motivo: string;
  observaciones: string;
  precio_display: string;
  es_cita_plan: boolean;
  item_plan: number | null;
  item_plan_info: any;
}

/**
 * Crea una nueva cita
 */
export const crearCita = async (data: CrearCitaData): Promise<Cita> => {
  console.log('📅 Creando nueva cita...', data);
  
  const response = await apiClient.post<Cita>('/api/agenda/citas/', data);
  
  console.log('✅ Cita creada:', response.data);
  return response.data;
};

/**
 * Obtiene horarios disponibles de un odontólogo en una fecha
 */
export const obtenerHorariosDisponibles = async (
  odontologoId: number,
  fecha: string // "YYYY-MM-DD"
): Promise<HorariosDisponibles> => {
  console.log('🕐 Obteniendo horarios disponibles...', { odontologoId, fecha });
  
  const response = await apiClient.get('/api/agenda/citas/horarios_disponibles/', {
    params: {
      odontologo: odontologoId,
      fecha: fecha
    }
  });
  
  console.log('✅ Horarios obtenidos:', response.data.total_disponibles, 'disponibles');
  return response.data;
};

export interface HorariosDisponibles {
  fecha: string;
  odontologo: string;
  odontologo_id: number;
  total_disponibles: number;
  total_ocupados: number;
  horarios: Horario[];
}

export interface Horario {
  hora: string;
  disponible: boolean;
  fecha_hora_completa: string;
}


/**
 * Obtiene lista de odontólogos disponibles
 */
export const obtenerOdontologos = async () => {
  console.log('👨‍⚕️ Obteniendo lista de odontólogos...');
  
  const response = await apiClient.get('/api/usuarios/odontologos/');
  
  console.log('✅ Odontólogos obtenidos:', response.data.length);
  return response.data;
};

/**
 * Obtiene planes activos del paciente (para citas de tratamiento)
 */
export const obtenerPlanesActivos = async () => {
  console.log('📋 Obteniendo planes activos del paciente...');
  
  const response = await apiClient.get('/api/tratamientos/planes/activos/');
  
  console.log('✅ Planes activos:', response.data.length);
  return response.data;
};
```

---

### 2. Componente - `AgendarCita.tsx`

```tsx
// src/pages/paciente/AgendarCita.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { crearCita, obtenerOdontologos, CrearCitaData } from '../../services/agendaService';
import { useAuth } from '../../context/AuthContext';  // ← Importar para obtener usuario

const MOTIVOS_CITA = [
  { value: 'CONSULTA', label: 'Consulta General ($30.00)' },
  { value: 'URGENCIA', label: 'Urgencia/Dolor ($80.00)' },
  { value: 'LIMPIEZA', label: 'Limpieza Dental ($60.00)' },
  { value: 'REVISION', label: 'Revisión/Control ($20.00)' }
];

export default function AgendarCita() {
  const navigate = useNavigate();
  const { user } = useAuth();  // ← Obtener usuario autenticado
  
  // Estado del formulario
  const [formData, setFormData] = useState<CrearCitaData>({
    paciente: user?.id || 0,  // ← ID del usuario = ID del PerfilPaciente
    odontologo: 0,
    fecha_hora: '',
    motivo_tipo: 'CONSULTA',
    motivo: '',
    observaciones: ''
  });
  
  // Estados de UI
  const [odontologos, setOdontologos] = useState<any[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  // Cargar odontólogos al montar
  useEffect(() => {
    cargarOdontologos();
  }, []);

  const cargarOdontologos = async () => {
    try {
      const data = await obtenerOdontologos();
      setOdontologos(data);
      
      // Seleccionar primer odontólogo por defecto
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, odontologo: data[0].id }));
      }
    } catch (err: any) {
      console.error('❌ Error cargando odontólogos:', err);
      setError('Error al cargar lista de odontólogos');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('📝 [AgendarCita] Submit formulario');
    
    // Validaciones básicas
    if (!formData.paciente) {
      setError('Error: No se pudo obtener el perfil del paciente');
      return;
    }
    
    if (!formData.odontologo) {
      setError('Debe seleccionar un odontólogo');
      return;
    }
    
    if (!formData.fecha_hora) {
      setError('Debe seleccionar fecha y hora');
      return;
    }
    
    if (!formData.motivo.trim()) {
      setError('Debe especificar el motivo de la consulta');
      return;
    }
    
    setCargando(true);
    setError(null);
    
    try {
      // ⚠️ IMPORTANTE: Ajustar zona horaria para evitar error 400
      // El backend espera hora local, pero toISOString() convierte a UTC
      const fechaLocal = new Date(formData.fecha_hora);
      const offsetMinutos = fechaLocal.getTimezoneOffset();
      const fechaAjustada = new Date(fechaLocal.getTime() - (offsetMinutos * 60000));
      const fechaISO = fechaAjustada.toISOString();
      
      const citaData: CrearCitaData = {
        ...formData,
        fecha_hora: fechaISO
      };
      
      console.log('📤 Enviando datos:', citaData);
      console.log('🕐 Fecha original:', formData.fecha_hora);
      console.log('🌍 Fecha ISO ajustada:', fechaISO);
      console.log('📝 Motivo validado:', formData.motivo);
      console.log('📋 Observaciones:', formData.observaciones || '(vacío)');
      
      const citaCreada = await crearCita(citaData);
      
      console.log('✅ Cita creada exitosamente:', citaCreada);
      setExito(true);
      
      // Redirigir después de 2 segundos
      setTimeout(() => {
        navigate('/paciente/citas');
      }, 2000);
      
    } catch (err: any) {
      console.error('❌ Error al crear cita:', err);
      
      if (err.response?.data) {
        // Errores específicos del backend
        const errorData = err.response.data;
        
        console.log('📋 Error completo del backend:', errorData);
        console.log('📋 Status code:', err.response?.status);
        
        if (typeof errorData === 'object' && errorData.detail) {
          setError(errorData.detail);
        } else if (errorData.motivo) {
          setError(`Motivo inválido: ${errorData.motivo[0]}`);
        } else if (errorData.motivo_tipo) {
          setError(`Tipo de motivo inválido: ${errorData.motivo_tipo[0]}`);
        } else if (errorData.fecha_hora) {
          setError(`Fecha inválida: ${errorData.fecha_hora[0]}`);
        } else if (errorData.odontologo) {
          setError(`Odontólogo: ${errorData.odontologo[0]}`);
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors[0]);
        } else {
          // Mostrar todos los errores si no coincide con ningún patrón
          const errores = Object.entries(errorData)
            .map(([campo, mensajes]) => `${campo}: ${Array.isArray(mensajes) ? mensajes.join(', ') : mensajes}`)
            .join(' | ');
          setError(`Error al agendar: ${errores}`);
        }
      } else {
        setError('Error de conexión. Intente nuevamente.');
      }
    } finally {
      setCargando(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'odontologo' ? parseInt(value) : value
    }));
  };

  // Calcular fecha mínima (mañana)
  const minFecha = new Date();
  minFecha.setDate(minFecha.getDate() + 1);
  const minFechaStr = minFecha.toISOString().slice(0, 16);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            📅 Agendar Nueva Cita
          </h1>
          <p className="text-gray-600 mt-2">
            Complete el formulario para solicitar una cita
          </p>
        </div>

        {/* Alerta de éxito */}
        {exito && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <span className="text-2xl mr-3">✅</span>
              <div>
                <p className="text-green-800 font-semibold">
                  ¡Cita agendada exitosamente!
                </p>
                <p className="text-green-600 text-sm mt-1">
                  Redirigiendo a tus citas...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Alerta de error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <span className="text-2xl mr-3">❌</span>
              <div>
                <p className="text-red-800 font-semibold">Error</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Formulario */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            
            {/* Odontólogo */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                👨‍⚕️ Odontólogo *
              </label>
              <select
                name="odontologo"
                value={formData.odontologo}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Seleccione un odontólogo</option>
                {odontologos.map(odon => (
                  <option key={odon.id} value={odon.id}>
                    Dr. {odon.nombre} {odon.apellido}
                    {odon.especialidad && ` - ${odon.especialidad}`}
                  </option>
                ))}
              </select>
            </div>

            {/* Fecha y hora */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🗓️ Fecha y Hora *
              </label>
              <input
                type="datetime-local"
                name="fecha_hora"
                value={formData.fecha_hora}
                onChange={handleChange}
                min={minFechaStr}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                ⏰ Horario de atención: Lunes a Viernes 8:00 AM - 6:00 PM
              </p>
            </div>

            {/* Tipo de motivo */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                📋 Tipo de Consulta *
              </label>
              <select
                name="motivo_tipo"
                value={formData.motivo_tipo}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                {MOTIVOS_CITA.map(motivo => (
                  <option key={motivo.value} value={motivo.value}>
                    {motivo.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Motivo */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                📝 Motivo de la Consulta *
              </label>
              <input
                type="text"
                name="motivo"
                value={formData.motivo}
                onChange={handleChange}
                placeholder="Ej: Dolor en muela, Limpieza dental, Control de ortodoncia"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                maxLength={200}
              />
            </div>

            {/* Observaciones */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                💬 Observaciones (opcional)
              </label>
              <textarea
                name="observaciones"
                value={formData.observaciones}
                onChange={handleChange}
                placeholder="Información adicional que considere importante"
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Botones */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={cargando || exito}
                className={`
                  flex-1 py-3 px-6 rounded-lg font-semibold text-white
                  ${cargando || exito 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                  }
                  transition-colors
                `}
              >
                {cargando ? '⏳ Agendando...' : '✅ Agendar Cita'}
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/paciente/citas')}
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        {/* Información adicional */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-800 mb-2">ℹ️ Información importante</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Las citas deben agendarse con al menos 24 horas de anticipación</li>
            <li>• Recibirá una confirmación por correo electrónico</li>
            <li>• Puede cancelar o reprogramar hasta 12 horas antes</li>
            <li>• En caso de emergencia, contacte directamente a la clínica</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
```

---

## 📝 Notas Importantes

### 1. ⚠️ Zona Horaria - ERROR 400 COMÚN

**Problema**: El input `datetime-local` devuelve fecha en hora local (ej: `2025-11-18T12:30`), pero `toISOString()` convierte a UTC sumando/restando horas según tu zona horaria.

**Ejemplo del error**:
```typescript
// ❌ INCORRECTO:
const fecha = new Date('2025-11-18T12:30'); // 12:30 PM hora local
const fechaISO = fecha.toISOString();       // "2025-11-18T20:30:00.000Z" (UTC+8)
// Backend rechaza: 20:30 está fuera del horario 8:00-18:00
```

**Solución implementada**:
```typescript
// ✅ CORRECTO:
const fechaLocal = new Date(formData.fecha_hora);
const offsetMinutos = fechaLocal.getTimezoneOffset();
const fechaAjustada = new Date(fechaLocal.getTime() - (offsetMinutos * 60000));
const fechaISO = fechaAjustada.toISOString();
// Resultado: "2025-11-18T12:30:00.000Z" (mantiene hora original)
```

**Por qué funciona**:
- `getTimezoneOffset()` devuelve la diferencia en minutos entre UTC y tu zona horaria
- Restamos ese offset para "cancelar" la conversión automática de `toISOString()`
- El backend recibe la hora exacta que seleccionó el usuario

### 2. ⚠️ ERROR CRÍTICO: Campo "motivo" truncado o cortado

**Problema detectado (error 400)**:  
El campo `motivo` llega al backend **truncado** a solo 9 caracteres.

**Logs del error**:
```
📤 Datos enviados:
  - Motivo: de la Co              ❌ Solo 9 caracteres (texto cortado)
  - Observaciones: de la Co       ❌ También cortado
  
Usuario escribió: "Motivo de la Consulta"  (21 caracteres)
Backend recibe:   "de la Co"               (9 caracteres)
```

**Posibles causas**:

**A) Bug en handleChange** - El input está cortando el texto:
```tsx
// ❌ INCORRECTO (posible bug):
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, value } = e.target;
  setFormData(prev => ({
    ...prev,
    [name]: value.substring(0, 9)  // ← Cortando a 9 caracteres
  }));
};

// ✅ CORRECTO:
const handleChange = (
  e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
) => {
  const { name, value } = e.target;
  setFormData(prev => ({
    ...prev,
    [name]: name === 'odontologo' ? parseInt(value) : value  // ← Sin truncar
  }));
};
```

**B) maxLength incorrecto** - El input tiene límite muy bajo:
```tsx
// ❌ INCORRECTO:
<input
  name="motivo"
  value={formData.motivo}
  onChange={handleChange}
  maxLength={9}              // ← Límite de 9 caracteres
/>

// ✅ CORRECTO:
<input
  name="motivo"
  value={formData.motivo}
  onChange={handleChange}
  maxLength={200}            // ← Límite razonable
  minLength={10}             // ← Mínimo recomendado
  required
/>
```

**C) name incorrecto** - El input tiene un name que no coincide:
```tsx
// ❌ INCORRECTO:
<input 
  name="motivoCita"           // ← Diferente del estado
  value={formData.motivo}
/>
// Resultado: formData.motivo queda vacío o con valor inicial

// ✅ CORRECTO:
<input 
  name="motivo"               // ← Coincide con formData.motivo
  value={formData.motivo}
/>
```

**Debugging recomendado**:
```tsx
const handleChange = (e: React.ChangeEvent<HTMLInputElement | ...>) => {
  const { name, value } = e.target;
  
  // Logging para detectar el problema
  console.log('🔍 [handleChange] Campo:', name);
  console.log('🔍 [handleChange] Valor completo:', value);
  console.log('🔍 [handleChange] Longitud:', value.length);
  
  setFormData(prev => {
    const newData = {
      ...prev,
      [name]: name === 'odontologo' ? parseInt(value) : value
    };
    
    console.log('✅ [handleChange] Estado actualizado:', newData);
    return newData;
  });
};
```

**Validación adicional en handleSubmit**:
```tsx
// Validar longitud mínima
if (formData.motivo.trim().length < 10) {
  setError('El motivo debe tener al menos 10 caracteres');
  console.error('❌ Motivo muy corto:', formData.motivo, `(${formData.motivo.length} caracteres)`);
  return;
}

// Validar que no esté truncado (sin espacios finales abruptos)
const motivoTrimmed = formData.motivo.trim();
if (motivoTrimmed !== formData.motivo && motivoTrimmed.length < 15) {
  console.warn('⚠️ Posible texto truncado detectado');
}
```

### 3. ⚠️ ERROR: Campo "motivo" con texto incorrecto (caso alternativo)

**Problema más común (error 400)**:  
El campo `motivo` llega al backend con el **texto del label HTML** en lugar del valor del input.

**Logs del error**:
```
📤 Datos enviados:
  - Motivo: 📝 Motivo de la Consulta *        ❌ LABEL, no el input
  - Observaciones: 📝 Motivo de la Consulta * ❌ LABEL, no el textarea
```

**Causa raíz**: El atributo `name` del input no coincide con la propiedad del estado:

```tsx
// ❌ INCORRECTO (causa el error):
<label>📝 Motivo de la Consulta *</label>
<input 
  type="text"
  name="motivoCita"           // ← name diferente del estado
  value={formData.motivo}     // ← estado usa "motivo"
  onChange={handleChange}
/>
// Resultado: handleChange no actualiza formData.motivo
// El estado queda con valor inicial '' (vacío)
// Al enviar, se envía '' que el backend rechaza

// ✅ CORRECTO:
<label className="block text-sm font-medium text-gray-700 mb-2">
  📝 Motivo de la Consulta *
</label>
<input 
  type="text"
  name="motivo"               // ← name DEBE coincidir con formData.motivo
  value={formData.motivo}
  onChange={handleChange}
  placeholder="Ej: Dolor en muela, Limpieza dental, Control de ortodoncia"
  required
/>
```

**Validación implementada** (en handleSubmit):
```typescript
// Validar que no sea placeholder
if (formData.motivo.includes('📝') || formData.motivo.includes('*')) {
  setError('Por favor, ingrese un motivo válido');
  return;
}
```

**Debugging en consola**:
```typescript
console.log('📝 Motivo validado:', formData.motivo);
console.log('📋 Observaciones:', formData.observaciones || '(vacío)');
```

### 3. Validaciones del Backend

El backend valida:
- ✅ Fecha no sea pasada
- ✅ Horario dentro de rango: **8:00 AM - 6:00 PM** (18:00)
- ✅ No conflictos con otras citas en el mismo horario
- ✅ Odontólogo exista y esté activo

**Errores comunes**:
```
❌ 400 "paciente: This field is required" → Falta agregar campo paciente al payload
❌ 400 "No se pueden agendar citas en fechas pasadas"
❌ 400 "Horario fuera del rango permitido" → Hora no está entre 8:00-18:00
❌ 400 "Ya existe una cita en ese horario" → Conflicto con otra cita
❌ 400 "Invalid choice: CONTROL" → Usar REVISION en lugar de CONTROL
❌ 400 "Invalid choice: EMERGENCIA" → Usar URGENCIA en lugar de EMERGENCIA
❌ 400 "Invalid choice: TRATAMIENTO" → No existe, usar CONSULTA, LIMPIEZA o PLAN
❌ 404 "Odontólogo no encontrado" → ID inválido
❌ 404 "Paciente no encontrado" → ID de paciente inválido
```

**⚠️ CRÍTICO - Valores correctos de motivo_tipo**:
```typescript
// ❌ INCORRECTOS (causan 400 "Invalid choice"):
'CONTROL'      → ✅ Usar 'REVISION'
'EMERGENCIA'   → ✅ Usar 'URGENCIA'
'TRATAMIENTO'  → ✅ Usar 'CONSULTA', 'LIMPIEZA' o 'PLAN'

// ✅ CORRECTOS (backend los acepta):
'CONSULTA'   // $30.00
'URGENCIA'   // $80.00
'LIMPIEZA'   // $60.00
'REVISION'   // $20.00
'PLAN'       // $0.00 (incluido en plan)
```

### 3. Estados de Cita

- `PENDIENTE`: Recién creada, esperando confirmación
- `CONFIRMADA`: Confirmada por la clínica
- `COMPLETADA`: Cita realizada
- `CANCELADA`: Cancelada por paciente o clínica

### 4. Tipos de Cita

**A) Cita General** (sin plan):
```json
{
  "motivo_tipo": "CONSULTA",  // O URGENCIA, LIMPIEZA, REVISION
  "item_plan": null
}
```

**B) Cita de Tratamiento** (vinculada a plan):
```json
{
  "motivo_tipo": "PLAN",
  "item_plan": 45  // ID del item del plan
}
```

---

## 🧪 Testing

```typescript
// Datos de prueba
const citaTest: CrearCitaData = {
  odontologo: 103,
  fecha_hora: "2025-12-01T10:00:00Z",
  motivo_tipo: "CONSULTA",
  motivo: "Dolor en muela derecha",
  observaciones: "Dolor intenso desde hace 3 días"
};
```

---

**Siguiente**: [Guía 22 - Cancelar/Reprogramar Cita](./22_cancelar_reprogramar_cita.md)
