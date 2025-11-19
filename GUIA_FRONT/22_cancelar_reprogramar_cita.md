# Guía 22: Cancelar y Reprogramar Citas

## 📋 Información General

**Caso de Uso**: CU12 - Gestión de Citas  
**Actor**: Paciente  
**Objetivo**: Permitir cancelar o reprogramar citas existentes

---

## 🎯 Funcionalidades

### 1. Cancelar Cita
- ✅ Solo citas con estado `PENDIENTE` o `CONFIRMADA`
- ✅ Hasta 12 horas antes de la fecha programada
- ✅ Cambia estado a `CANCELADA`

### 2. Reprogramar Cita
- ✅ Cambiar fecha/hora de una cita existente
- ✅ Mantiene el mismo odontólogo y motivo
- ✅ Validaciones de disponibilidad

---

## 🔌 API Endpoints

### Cancelar Cita

```
DELETE /api/agenda/citas/{id}/cancelar/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Respuesta exitosa** (200 OK):
```json
{
  "detail": "Cita cancelada exitosamente",
  "cita": {
    "id": 145,
    "estado": "CANCELADA",
    "fecha_hora": "2025-12-01T10:00:00Z",
    "paciente_nombre": "María",
    "odontologo_nombre": "Dr. Juan"
  }
}
```

**Errores comunes**:
```json
// Cita ya realizada
{
  "detail": "No se puede cancelar una cita completada"
}

// Menos de 12 horas
{
  "detail": "No se puede cancelar con menos de 12 horas de anticipación"
}

// No es tu cita
{
  "detail": "No tienes permiso para cancelar esta cita"
}
```

---

### Reprogramar Cita

```
PATCH /api/agenda/citas/{id}/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body de la petición**:
```json
{
  "fecha_hora": "2025-12-05T15:00:00Z"
}
```

**Respuesta exitosa** (200 OK):
```json
{
  "id": 145,
  "paciente": 104,
  "paciente_nombre": "María",
  "odontologo": 103,
  "odontologo_nombre": "Dr. Juan",
  "fecha_hora": "2025-12-05T15:00:00Z",
  "estado": "PENDIENTE",
  "motivo_tipo": "CONSULTA",
  "motivo": "Dolor en muela derecha",
  "observaciones": "",
  "precio_display": "$50.00"
}
```

---

## 🔧 Implementación Frontend

### 1. Service - `agendaService.ts`

```typescript
// src/services/agendaService.ts

/**
 * Cancela una cita existente
 */
export const cancelarCita = async (citaId: number): Promise<any> => {
  console.log(`🚫 Cancelando cita ID: ${citaId}`);
  
  const response = await apiClient.delete(`/api/agenda/citas/${citaId}/cancelar/`);
  
  console.log('✅ Cita cancelada:', response.data);
  return response.data;
};

/**
 * Reprograma una cita existente
 */
export const reprogramarCita = async (
  citaId: number,
  nuevaFechaHora: string
): Promise<Cita> => {
  console.log(`🔄 Reprogramando cita ID: ${citaId}`, { nuevaFechaHora });
  
  const response = await apiClient.patch<Cita>(
    `/api/agenda/citas/${citaId}/`,
    { fecha_hora: nuevaFechaHora }
  );
  
  console.log('✅ Cita reprogramada:', response.data);
  return response.data;
};

/**
 * Verifica si una cita puede ser cancelada
 */
export const puedeCancelar = (cita: Cita): { puede: boolean; razon?: string } => {
  const ahora = new Date();
  const fechaCita = new Date(cita.fecha_hora);
  const horasHasta = (fechaCita.getTime() - ahora.getTime()) / (1000 * 60 * 60);
  
  // Ya pasó
  if (horasHasta < 0) {
    return { puede: false, razon: 'La cita ya pasó' };
  }
  
  // Menos de 12 horas
  if (horasHasta < 12) {
    return { puede: false, razon: 'Debe cancelar con al menos 12 horas de anticipación' };
  }
  
  // Estado no permite cancelación
  if (cita.estado === 'COMPLETADA') {
    return { puede: false, razon: 'La cita ya fue completada' };
  }
  
  if (cita.estado === 'CANCELADA') {
    return { puede: false, razon: 'La cita ya está cancelada' };
  }
  
  return { puede: true };
};
```

---

### 2. Componente - `MisCitas.tsx` (con acciones)

```tsx
// src/pages/paciente/MisCitas.tsx

import React, { useState, useEffect } from 'react';
import { 
  obtenerMisCitas, 
  cancelarCita, 
  reprogramarCita,
  puedeCancelar,
  Cita 
} from '../../services/agendaService';
import ModalCancelarCita from '../../components/ModalCancelarCita';
import ModalReprogramarCita from '../../components/ModalReprogramarCita';

export default function MisCitas() {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modales
  const [citaSeleccionada, setCitaSeleccionada] = useState<Cita | null>(null);
  const [modalCancelar, setModalCancelar] = useState(false);
  const [modalReprogramar, setModalReprogramar] = useState(false);

  useEffect(() => {
    cargarCitas();
  }, []);

  const cargarCitas = async () => {
    try {
      setCargando(true);
      const data = await obtenerMisCitas();
      setCitas(data);
      setError(null);
    } catch (err) {
      console.error('❌ Error cargando citas:', err);
      setError('Error al cargar las citas');
    } finally {
      setCargando(false);
    }
  };

  const handleCancelar = (cita: Cita) => {
    const validacion = puedeCancelar(cita);
    
    if (!validacion.puede) {
      alert(`❌ ${validacion.razon}`);
      return;
    }
    
    setCitaSeleccionada(cita);
    setModalCancelar(true);
  };

  const confirmarCancelacion = async () => {
    if (!citaSeleccionada) return;
    
    try {
      await cancelarCita(citaSeleccionada.id);
      
      // Actualizar lista local
      setCitas(citas.map(c => 
        c.id === citaSeleccionada.id 
          ? { ...c, estado: 'CANCELADA' }
          : c
      ));
      
      setModalCancelar(false);
      setCitaSeleccionada(null);
      
      alert('✅ Cita cancelada exitosamente');
    } catch (err: any) {
      console.error('❌ Error cancelando cita:', err);
      alert(err.response?.data?.detail || 'Error al cancelar la cita');
    }
  };

  const handleReprogramar = (cita: Cita) => {
    const validacion = puedeCancelar(cita); // Mismas validaciones
    
    if (!validacion.puede) {
      alert(`❌ ${validacion.razon}`);
      return;
    }
    
    setCitaSeleccionada(cita);
    setModalReprogramar(true);
  };

  const confirmarReprogramacion = async (nuevaFecha: string) => {
    if (!citaSeleccionada) return;
    
    try {
      const citaActualizada = await reprogramarCita(citaSeleccionada.id, nuevaFecha);
      
      // Actualizar lista local
      setCitas(citas.map(c => 
        c.id === citaSeleccionada.id ? citaActualizada : c
      ));
      
      setModalReprogramar(false);
      setCitaSeleccionada(null);
      
      alert('✅ Cita reprogramada exitosamente');
    } catch (err: any) {
      console.error('❌ Error reprogramando cita:', err);
      alert(err.response?.data?.detail || 'Error al reprogramar la cita');
    }
  };

  const formatearFecha = (fechaStr: string) => {
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoBadge = (estado: string) => {
    const estilos = {
      PENDIENTE: 'bg-yellow-100 text-yellow-800',
      CONFIRMADA: 'bg-blue-100 text-blue-800',
      COMPLETADA: 'bg-green-100 text-green-800',
      CANCELADA: 'bg-red-100 text-red-800'
    };
    
    return estilos[estado as keyof typeof estilos] || 'bg-gray-100 text-gray-800';
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">⏳ Cargando citas...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">📅 Mis Citas</h1>
          <p className="text-gray-600 mt-1">
            {citas.length} cita{citas.length !== 1 ? 's' : ''} registrada{citas.length !== 1 ? 's' : ''}
          </p>
        </div>
        
        <button
          onClick={() => window.location.href = '/paciente/citas/agendar'}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          ➕ Nueva Cita
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Lista de citas */}
      <div className="space-y-4">
        {citas.map(cita => {
          const validacion = puedeCancelar(cita);
          
          return (
            <div
              key={cita.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                
                {/* Info principal */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getEstadoBadge(cita.estado)}`}>
                      {cita.estado}
                    </span>
                    <span className="text-sm text-gray-500">
                      #{cita.id}
                    </span>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    👨‍⚕️ {cita.odontologo_nombre}
                  </h3>
                  
                  <div className="space-y-1 text-gray-600">
                    <p className="flex items-center gap-2">
                      <span>🗓️</span>
                      <span className="font-medium">{formatearFecha(cita.fecha_hora)}</span>
                    </p>
                    
                    <p className="flex items-center gap-2">
                      <span>📋</span>
                      <span>{cita.motivo_tipo_display}</span>
                    </p>
                    
                    <p className="flex items-center gap-2">
                      <span>💬</span>
                      <span className="italic">{cita.motivo}</span>
                    </p>
                    
                    {cita.observaciones && (
                      <p className="text-sm text-gray-500 mt-2">
                        Obs: {cita.observaciones}
                      </p>
                    )}
                  </div>
                </div>

                {/* Acciones */}
                <div className="flex flex-col gap-2 ml-4">
                  {validacion.puede && (
                    <>
                      <button
                        onClick={() => handleReprogramar(cita)}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
                      >
                        🔄 Reprogramar
                      </button>
                      
                      <button
                        onClick={() => handleCancelar(cita)}
                        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
                      >
                        ❌ Cancelar
                      </button>
                    </>
                  )}
                  
                  {!validacion.puede && (
                    <span className="text-xs text-gray-500 text-center">
                      {validacion.razon}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Sin citas */}
      {citas.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📅</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No tienes citas agendadas
          </h3>
          <p className="text-gray-500 mb-6">
            Agenda tu primera cita para comenzar tu tratamiento
          </p>
          <button
            onClick={() => window.location.href = '/paciente/citas/agendar'}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            ➕ Agendar Cita
          </button>
        </div>
      )}

      {/* Modal Cancelar */}
      {modalCancelar && citaSeleccionada && (
        <ModalCancelarCita
          cita={citaSeleccionada}
          onConfirmar={confirmarCancelacion}
          onCancelar={() => {
            setModalCancelar(false);
            setCitaSeleccionada(null);
          }}
        />
      )}

      {/* Modal Reprogramar */}
      {modalReprogramar && citaSeleccionada && (
        <ModalReprogramarCita
          cita={citaSeleccionada}
          onConfirmar={confirmarReprogramacion}
          onCancelar={() => {
            setModalReprogramar(false);
            setCitaSeleccionada(null);
          }}
        />
      )}
    </div>
  );
}
```

---

### 3. Modal Cancelar - `ModalCancelarCita.tsx`

```tsx
// src/components/ModalCancelarCita.tsx

import React from 'react';
import { Cita } from '../services/agendaService';

interface Props {
  cita: Cita;
  onConfirmar: () => void;
  onCancelar: () => void;
}

export default function ModalCancelarCita({ cita, onConfirmar, onCancelar }: Props) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        
        <div className="text-center mb-4">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            ¿Cancelar cita?
          </h2>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Odontólogo:</strong> {cita.odontologo_nombre}
          </p>
          <p className="text-sm text-gray-600 mb-2">
            <strong>Fecha:</strong> {new Date(cita.fecha_hora).toLocaleString('es-ES')}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Motivo:</strong> {cita.motivo}
          </p>
        </div>

        <p className="text-gray-700 mb-6 text-center">
          Esta acción no se puede deshacer. Podrás agendar una nueva cita cuando lo necesites.
        </p>

        <div className="flex gap-3">
          <button
            onClick={onCancelar}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            No, mantener
          </button>
          
          <button
            onClick={onConfirmar}
            className="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold"
          >
            Sí, cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### 4. Modal Reprogramar - `ModalReprogramarCita.tsx`

```tsx
// src/components/ModalReprogramarCita.tsx

import React, { useState } from 'react';
import { Cita } from '../services/agendaService';

interface Props {
  cita: Cita;
  onConfirmar: (nuevaFecha: string) => void;
  onCancelar: () => void;
}

export default function ModalReprogramarCita({ cita, onConfirmar, onCancelar }: Props) {
  const [nuevaFecha, setNuevaFecha] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nuevaFecha) {
      alert('Debe seleccionar una nueva fecha');
      return;
    }
    
    // Convertir a ISO UTC
    const fechaISO = new Date(nuevaFecha).toISOString();
    onConfirmar(fechaISO);
  };

  // Fecha mínima: mañana
  const minFecha = new Date();
  minFecha.setDate(minFecha.getDate() + 1);
  const minFechaStr = minFecha.toISOString().slice(0, 16);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          🔄 Reprogramar Cita
        </h2>

        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Fecha actual:</strong> {new Date(cita.fecha_hora).toLocaleString('es-ES')}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Odontólogo:</strong> {cita.odontologo_nombre}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nueva fecha y hora
            </label>
            <input
              type="datetime-local"
              value={nuevaFecha}
              onChange={(e) => setNuevaFecha(e.target.value)}
              min={minFechaStr}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onCancelar}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            
            <button
              type="submit"
              className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## 📝 Reglas de Negocio

1. **Cancelación**:
   - ✅ Solo estados: `PENDIENTE`, `CONFIRMADA`
   - ✅ Mínimo 12 horas de anticipación
   - ✅ Solo el paciente dueño de la cita

2. **Reprogramación**:
   - ✅ Mismas validaciones que cancelación
   - ✅ Nueva fecha debe estar disponible
   - ✅ Mantiene odontólogo y motivo original

3. **Restricciones**:
   - ❌ No se puede modificar citas `COMPLETADAS`
   - ❌ No se puede cancelar con menos de 12 horas
   - ❌ No se puede reprogramar a fechas pasadas

---

**Siguiente**: [Guía 23 - Subir Documentos](./23_subir_documentos.md)
