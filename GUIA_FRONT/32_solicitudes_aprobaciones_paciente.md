# Guía 32: Solicitudes y Aprobaciones de Planes (Paciente)

## 📋 Información General

**Caso de Uso**: CU09 - Gestión de Planes de Tratamiento  
**Actor**: Paciente  
**Objetivo**: Ver solicitudes de planes de tratamiento propuestos por el odontólogo y aprobarlos o rechazarlos

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver lista de planes propuestos por su odontólogo
- ✅ Ver detalles de cada propuesta (procedimientos, costos, descripción)
- ✅ Aprobar un plan propuesto
- ✅ Rechazar un plan propuesto con motivo
- ✅ Ver historial de decisiones (aprobados/rechazados)
- ✅ Recibir notificaciones de nuevas propuestas

---

## 🔌 API Endpoints

### 1. Listar Solicitudes Pendientes
```
GET /api/tratamientos/planes/propuestos/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Query params opcionales**:
```
?estado=PROPUESTO          → Solo propuestas pendientes
?estado=APROBADO           → Solo planes aprobados
?estado=RECHAZADO          → Solo planes rechazados (por el paciente)
```

**Respuesta exitosa** (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 35,
      "titulo": "Ortodoncia Completa",
      "descripcion": "Plan de tratamiento ortodóncico completo con brackets metálicos, estimado 18 meses",
      "paciente": 104,
      "paciente_info": {
        "id": 104,
        "nombre": "María",
        "apellido": "García",
        "email": "paciente1@test.com"
      },
      "odontologo": 103,
      "odontologo_info": {
        "id": 103,
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "odontologo@clinica-demo.com"
      },
      "estado": "PROPUESTO",
      "estado_display": "Propuesto",
      "prioridad": "ALTA",
      "prioridad_display": "Alta",
      "fecha_creacion": "2025-11-16T21:00:00Z",
      "fecha_presentacion": "2025-11-16T21:00:00Z",
      "fecha_aceptacion": null,
      "precio_total_plan": "3500.00",
      "cantidad_items": 8,
      "porcentaje_completado": 0,
      "puede_ser_editado": true,
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 36,
      "titulo": "Implante Dental Pieza 26",
      "descripcion": "Colocación de implante dental en pieza 26 con corona de porcelana",
      "paciente": 104,
      "paciente_info": {
        "id": 104,
        "nombre": "María",
        "apellido": "García",
        "email": "paciente1@test.com"
      },
      "odontologo": 103,
      "odontologo_info": {
        "id": 103,
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "odontologo@clinica-demo.com"
      },
      "estado": "PROPUESTO",
      "estado_display": "Propuesto",
      "prioridad": "MEDIA",
      "prioridad_display": "Media",
      "fecha_creacion": "2025-11-15T15:30:00Z",
      "fecha_presentacion": "2025-11-15T15:30:00Z",
      "fecha_aceptacion": null,
      "precio_total_plan": "1800.00",
      "cantidad_items": 4,
      "porcentaje_completado": 0,
      "puede_ser_editado": true,
      "creado": "2025-11-15T15:30:00Z",
      "actualizado": "2025-11-15T15:30:00Z"
    }
  ]
}
```

---

### 2. Obtener Detalle de Plan Propuesto
```
GET /api/tratamientos/planes/{id}/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Respuesta exitosa** (200 OK):
```json
{
  "id": 35,
  "titulo": "Ortodoncia Completa",
  "descripcion": "Plan de tratamiento ortodóncico completo con brackets metálicos, estimado 18 meses",
  "paciente": 104,
  "paciente_info": {
    "id": 104,
    "nombre": "María",
    "apellido": "García",
    "email": "paciente1@test.com"
  },
  "odontologo": 103,
  "odontologo_info": {
    "id": 103,
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "odontologo@clinica-demo.com"
  },
  "estado": "PROPUESTO",
  "estado_display": "Propuesto",
  "prioridad": "ALTA",
  "prioridad_display": "Alta",
  "fecha_creacion": "2025-11-16T21:00:00Z",
  "fecha_presentacion": "2025-11-16T21:00:00Z",
  "fecha_aceptacion": null,
  "fecha_inicio": null,
  "fecha_finalizacion": null,
  "notas_internas": "Paciente requiere tratamiento urgente para corrección de mordida",
  "precio_total_plan": "3500.00",
  "cantidad_items": 8,
  "porcentaje_completado": 0,
  "puede_ser_editado": true,
  "creado": "2025-11-16T21:00:00Z",
  "actualizado": "2025-11-16T21:00:00Z",
  "items": [
    {
      "id": 110,
      "tratamiento": {
        "id": 8,
        "nombre": "Consulta de Ortodoncia",
        "descripcion": "Evaluación ortodóncica inicial"
      },
      "precio": "150.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 1,
      "notas": "Evaluación completa con radiografías panorámicas",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 111,
      "tratamiento": {
        "id": 9,
        "nombre": "Limpieza Dental Profunda",
        "descripcion": "Profilaxis completa antes de ortodoncia"
      },
      "precio": "100.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 2,
      "notas": "Limpieza profunda requerida antes de colocar brackets",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 112,
      "tratamiento": {
        "id": 10,
        "nombre": "Colocación de Brackets",
        "descripcion": "Instalación de brackets metálicos"
      },
      "precio": "1200.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 3,
      "notas": "Brackets metálicos de alta calidad, incluye primer arco",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 113,
      "tratamiento": {
        "id": 11,
        "nombre": "Control Mensual (x12)",
        "descripcion": "Controles mensuales de ortodoncia"
      },
      "precio": "1200.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 4,
      "notas": "12 controles mensuales incluidos, ajuste de arcos",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 114,
      "tratamiento": {
        "id": 12,
        "nombre": "Retiro de Brackets",
        "descripcion": "Remoción de aparatología"
      },
      "precio": "200.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 5,
      "notas": "Retiro cuidadoso de brackets y limpieza final",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 115,
      "tratamiento": {
        "id": 13,
        "nombre": "Retenedores",
        "descripcion": "Fabricación de retenedores"
      },
      "precio": "450.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 6,
      "notas": "Retenedores superior e inferior, uso permanente",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 116,
      "tratamiento": {
        "id": 14,
        "nombre": "Control Post-Ortodoncia (x6)",
        "descripcion": "Controles posteriores al tratamiento"
      },
      "precio": "120.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 7,
      "notas": "6 controles bimensuales post-tratamiento",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    },
    {
      "id": 117,
      "tratamiento": {
        "id": 15,
        "nombre": "Radiografía de Control Final",
        "descripcion": "Radiografía panorámica final"
      },
      "precio": "80.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 8,
      "notas": "Radiografía para verificar resultados finales",
      "creado": "2025-11-16T21:00:00Z",
      "actualizado": "2025-11-16T21:00:00Z"
    }
  ]
}
```

---

### 3. Aprobar Plan
```
POST /api/tratamientos/planes/{id}/aprobar/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body** (opcional):
```json
{
  "comentarios": "Acepto el plan de tratamiento propuesto. Quisiera iniciar lo antes posible."
}
```

**Respuesta exitosa** (200 OK):
```json
{
  "id": 35,
  "titulo": "Ortodoncia Completa",
  "estado": "APROBADO",
  "estado_display": "Aprobado",
  "fecha_aceptacion": "2025-11-16T22:15:30Z",
  "mensaje": "Plan de tratamiento aprobado exitosamente"
}
```

**Errores posibles**:
```
❌ 400 "El plan no está en estado PROPUESTO"
❌ 403 "No tiene permiso para aprobar este plan"
❌ 404 "Plan no encontrado"
```

---

### 4. Rechazar Plan
```
POST /api/tratamientos/planes/{id}/rechazar/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body** (requerido):
```json
{
  "motivo": "Prefiero un tratamiento con brackets cerámicos en lugar de metálicos",
  "comentarios": "Por favor, elabore una nueva propuesta con materiales estéticos"
}
```

**Respuesta exitosa** (200 OK):
```json
{
  "id": 35,
  "titulo": "Ortodoncia Completa",
  "estado": "RECHAZADO",
  "estado_display": "Rechazado",
  "motivo_rechazo": "Prefiero un tratamiento con brackets cerámicos en lugar de metálicos",
  "mensaje": "Plan de tratamiento rechazado"
}
```

**Errores posibles**:
```
❌ 400 "El campo 'motivo' es requerido"
❌ 400 "El plan no está en estado PROPUESTO"
❌ 403 "No tiene permiso para rechazar este plan"
❌ 404 "Plan no encontrado"
```

---

## 🔧 Implementación Frontend

### 1. Service - `planesService.ts`

```typescript
// src/services/planesService.ts

/**
 * Obtiene planes propuestos (solicitudes pendientes)
 */
export const obtenerPlanesPropuestos = async (estado?: string): Promise<PlanResumen[]> => {
  console.log('📋 Obteniendo planes propuestos');
  
  const params: any = {};
  if (estado) {
    params.estado = estado;
  } else {
    params.estado = 'PROPUESTO'; // Por defecto solo pendientes
  }
  
  const response = await apiClient.get<PaginatedResponse<PlanResumen>>(
    '/api/tratamientos/planes/propuestos/',
    { params }
  );
  
  console.log('✅ Planes propuestos obtenidos:', response.data.results.length);
  return response.data.results;
};

/**
 * Aprueba un plan de tratamiento propuesto
 */
export const aprobarPlan = async (
  planId: number,
  comentarios?: string
): Promise<PlanRespuestaAprobacion> => {
  console.log('✅ Aprobando plan:', planId);
  
  const body: any = {};
  if (comentarios) {
    body.comentarios = comentarios;
  }
  
  const response = await apiClient.post<PlanRespuestaAprobacion>(
    `/api/tratamientos/planes/${planId}/aprobar/`,
    body
  );
  
  console.log('✅ Plan aprobado exitosamente');
  return response.data;
};

/**
 * Rechaza un plan de tratamiento propuesto
 */
export const rechazarPlan = async (
  planId: number,
  motivo: string,
  comentarios?: string
): Promise<PlanRespuestaRechazo> => {
  console.log('❌ Rechazando plan:', planId);
  
  const body: any = {
    motivo: motivo
  };
  
  if (comentarios) {
    body.comentarios = comentarios;
  }
  
  const response = await apiClient.post<PlanRespuestaRechazo>(
    `/api/tratamientos/planes/${planId}/rechazar/`,
    body
  );
  
  console.log('✅ Plan rechazado');
  return response.data;
};

// Interfaces
export interface PlanResumen {
  id: number;
  titulo: string;
  descripcion: string;
  paciente: number;
  paciente_info: {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
  };
  odontologo: number;
  odontologo_info: {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
  };
  estado: 'PROPUESTO' | 'APROBADO' | 'RECHAZADO' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  estado_display: string;
  prioridad: string;
  prioridad_display: string;
  fecha_creacion: string;
  fecha_presentacion: string | null;
  fecha_aceptacion: string | null;
  precio_total_plan: string;
  cantidad_items: number;
  porcentaje_completado: number;
  puede_ser_editado: boolean;
  creado: string;
  actualizado: string;
}

export interface PlanRespuestaAprobacion {
  id: number;
  titulo: string;
  estado: string;
  estado_display: string;
  fecha_aceptacion: string;
  mensaje: string;
}

export interface PlanRespuestaRechazo {
  id: number;
  titulo: string;
  estado: string;
  estado_display: string;
  motivo_rechazo: string;
  mensaje: string;
}
```

---

### 2. Componente - `SolicitudesPlanes.tsx`

```tsx
// src/pages/paciente/SolicitudesPlanes.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  obtenerPlanesPropuestos, 
  aprobarPlan, 
  rechazarPlan 
} from '../../services/planesService';

export default function SolicitudesPlanes() {
  const navigate = useNavigate();
  
  const [solicitudes, setSolicitudes] = useState<any[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal de confirmación
  const [modalAprobar, setModalAprobar] = useState<number | null>(null);
  const [modalRechazar, setModalRechazar] = useState<number | null>(null);
  const [comentarios, setComentarios] = useState('');
  const [motivo, setMotivo] = useState('');
  const [procesando, setProcesando] = useState(false);

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  const cargarSolicitudes = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await obtenerPlanesPropuestos('propuesto');
      setSolicitudes(data);
    } catch (err: any) {
      console.error('❌ Error cargando solicitudes:', err);
      setError('Error al cargar las solicitudes de tratamiento');
    } finally {
      setCargando(false);
    }
  };

  const handleAprobar = async (planId: number) => {
    try {
      setProcesando(true);
      await aprobarPlan(planId, comentarios);
      
      // Mostrar mensaje de éxito
      alert('✅ Plan de tratamiento aprobado exitosamente');
      
      // Cerrar modal y limpiar
      setModalAprobar(null);
      setComentarios('');
      
      // Recargar lista
      await cargarSolicitudes();
    } catch (err: any) {
      console.error('❌ Error aprobando plan:', err);
      alert(err.response?.data?.detail || 'Error al aprobar el plan');
    } finally {
      setProcesando(false);
    }
  };

  const handleRechazar = async (planId: number) => {
    if (!motivo.trim()) {
      alert('⚠️ Debe indicar el motivo del rechazo');
      return;
    }

    try {
      setProcesando(true);
      await rechazarPlan(planId, motivo, comentarios);
      
      // Mostrar mensaje de éxito
      alert('✅ Plan de tratamiento rechazado. El odontólogo será notificado.');
      
      // Cerrar modal y limpiar
      setModalRechazar(null);
      setMotivo('');
      setComentarios('');
      
      // Recargar lista
      await cargarSolicitudes();
    } catch (err: any) {
      console.error('❌ Error rechazando plan:', err);
      alert(err.response?.data?.detail || 'Error al rechazar el plan');
    } finally {
      setProcesando(false);
    }
  };

  const getPrioridadColor = (prioridad: string) => {
    switch (prioridad) {
      case 'ALTA':
        return 'text-red-600';
      case 'MEDIA':
        return 'text-yellow-600';
      case 'BAJA':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando solicitudes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          Solicitudes de Tratamiento
        </h1>
        <p className="text-gray-600 mt-2">
          Revisa y responde a las propuestas de tratamiento enviadas por tu odontólogo
        </p>
      </div>

      {/* Contador */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <span className="text-2xl mr-3">📋</span>
          <div>
            <h3 className="font-semibold text-blue-800">
              {solicitudes.length} {solicitudes.length === 1 ? 'solicitud pendiente' : 'solicitudes pendientes'}
            </h3>
            <p className="text-sm text-blue-600">
              Por favor, revisa y responde a cada propuesta
            </p>
          </div>
        </div>
      </div>

      {/* Lista de Solicitudes */}
      {solicitudes.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <span className="text-6xl">✅</span>
          <h3 className="text-xl font-semibold text-gray-800 mt-4">
            No hay solicitudes pendientes
          </h3>
          <p className="text-gray-600 mt-2">
            Todas tus propuestas de tratamiento han sido respondidas
          </p>
          <button
            onClick={() => navigate('/paciente/planes')}
            className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Ver Mis Planes
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {solicitudes.map((solicitud) => (
            <div key={solicitud.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                
                {/* Header de la solicitud */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-bold text-gray-800">
                        {solicitud.titulo}
                      </h2>
                      <span className={`text-sm font-semibold ${getPrioridadColor(solicitud.prioridad)}`}>
                        ⚠️ {solicitud.prioridad_display}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Propuesto por: Dr. {solicitud.odontologo_info.nombre} {solicitud.odontologo_info.apellido}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Fecha: {new Date(solicitud.fecha_presentacion || solicitud.fecha_creacion).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-800">
                      ${solicitud.precio_total_plan}
                    </div>
                    <div className="text-xs text-gray-500">
                      {solicitud.cantidad_items} procedimientos
                    </div>
                  </div>
                </div>

                {/* Descripción */}
                {solicitud.descripcion && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 text-sm">
                      {solicitud.descripcion}
                    </p>
                  </div>
                )}

                {/* Acciones */}
                <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => navigate(`/paciente/planes/${solicitud.id}`)}
                    className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    👁️ Ver Detalles Completos
                  </button>
                  <button
                    onClick={() => setModalAprobar(solicitud.id)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    ✅ Aprobar
                  </button>
                  <button
                    onClick={() => setModalRechazar(solicitud.id)}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                  >
                    ❌ Rechazar
                  </button>
                </div>

              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Aprobar */}
      {modalAprobar && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              ✅ Aprobar Plan de Tratamiento
            </h3>
            <p className="text-gray-600 mb-4">
              ¿Está seguro que desea aprobar este plan de tratamiento?
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Al aprobar, el odontólogo podrá comenzar a programar y ejecutar los procedimientos.
            </p>

            {/* Comentarios opcionales */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comentarios (opcional)
              </label>
              <textarea
                value={comentarios}
                onChange={(e) => setComentarios(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Ej: Me gustaría iniciar lo antes posible..."
              />
            </div>

            {/* Botones */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setModalAprobar(null);
                  setComentarios('');
                }}
                disabled={procesando}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleAprobar(modalAprobar)}
                disabled={procesando}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {procesando ? 'Procesando...' : 'Confirmar Aprobación'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Rechazar */}
      {modalRechazar && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              ❌ Rechazar Plan de Tratamiento
            </h3>
            <p className="text-gray-600 mb-4">
              Por favor, indique el motivo del rechazo para que el odontólogo pueda elaborar una nueva propuesta.
            </p>

            {/* Motivo (requerido) */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motivo del rechazo <span className="text-red-500">*</span>
              </label>
              <textarea
                value={motivo}
                onChange={(e) => setMotivo(e.target.value)}
                rows={3}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Ej: Prefiero tratamiento con materiales estéticos..."
              />
            </div>

            {/* Comentarios adicionales */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comentarios adicionales (opcional)
              </label>
              <textarea
                value={comentarios}
                onChange={(e) => setComentarios(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Información adicional..."
              />
            </div>

            {/* Botones */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setModalRechazar(null);
                  setMotivo('');
                  setComentarios('');
                }}
                disabled={procesando}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleRechazar(modalRechazar)}
                disabled={procesando || !motivo.trim()}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {procesando ? 'Procesando...' : 'Confirmar Rechazo'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
```

---

## 🎨 Características de la UI

### 1. Lista de Solicitudes
- **Card por solicitud**: Fondo blanco con hover effect
- **Información destacada**: Título, odontólogo, fecha, precio
- **Indicador de prioridad**: Color según urgencia (rojo, amarillo, verde)
- **Descripción visible**: Background gris claro para destacar

### 2. Botones de Acción
- **Ver Detalles**: Gris, navega a vista completa del plan
- **Aprobar**: Verde, abre modal de confirmación
- **Rechazar**: Rojo, abre modal con formulario de motivo

### 3. Modal de Aprobación
- **Confirmación clara**: Mensaje explicativo
- **Comentarios opcionales**: Textarea para notas del paciente
- **Botones distintivos**: Cancelar (gris), Confirmar (verde)
- **Estado de carga**: Botón deshabilitado durante procesamiento

### 4. Modal de Rechazo
- **Motivo requerido**: Campo obligatorio con asterisco
- **Comentarios adicionales**: Campo opcional
- **Validación**: Botón deshabilitado si falta motivo
- **Feedback claro**: Mensaje de que el odontólogo será notificado

### 5. Estado Vacío
- **Mensaje positivo**: Ícono grande de check
- **Navegación sugerida**: Botón para ver planes activos
- **Diseño centrado**: Card grande con padding generoso

---

## 📝 Notas Importantes

### 1. Estados del Plan

```typescript
PROPUESTO   → Pendiente de aprobación del paciente
APROBADO    → Paciente aceptó, puede iniciar tratamiento
RECHAZADO   → Paciente rechazó, odontólogo debe revisar
EN_PROGRESO → Tratamiento en curso
COMPLETADO  → Todos los procedimientos finalizados
CANCELADO   → Cancelado por cualquiera de las partes
```

### 2. Validaciones Backend

El backend valida:
- ✅ Plan pertenece al paciente autenticado
- ✅ Plan está en estado `PROPUESTO`
- ✅ Motivo de rechazo es obligatorio
- ✅ Solo puede aprobar/rechazar una vez

### 3. Flujo de Aprobación

```
1. Odontólogo crea plan → estado PROPUESTO
2. Paciente ve solicitud en esta vista
3. Paciente revisa detalles completos
4. Paciente aprueba → estado APROBADO, fecha_aceptacion guardada
5. Odontólogo notificado → puede iniciar tratamiento
```

### 4. Flujo de Rechazo

```
1. Paciente rechaza con motivo
2. Estado cambia a RECHAZADO
3. Motivo guardado en el plan
4. Odontólogo notificado → puede crear nueva propuesta
5. Plan rechazado no aparece más en solicitudes pendientes
```

### 5. Notificaciones

Después de aprobar/rechazar:
```typescript
// Mostrar mensaje de éxito
alert('✅ Plan aprobado exitosamente');

// Recargar lista para actualizar vista
await cargarSolicitudes();
```

---

## 🔗 Integración con Otras Vistas

### Navegación Sugerida

```typescript
// Desde Dashboard
/paciente/dashboard → Ver "X solicitudes pendientes" → /paciente/solicitudes

// Desde Solicitudes
/paciente/solicitudes → Ver Detalles → /paciente/planes/:id

// Después de aprobar
/paciente/solicitudes → Ver Mis Planes → /paciente/planes

// Ver plan aprobado
/paciente/planes → Clic en plan → /paciente/planes/:id
```

### Badge de Notificación

Agregar contador en menú:
```tsx
<Link to="/paciente/solicitudes" className="nav-link">
  Solicitudes
  {solicitudesPendientes > 0 && (
    <span className="ml-2 px-2 py-1 bg-red-500 text-white text-xs rounded-full">
      {solicitudesPendientes}
    </span>
  )}
</Link>
```

---

## 🧪 Testing

### Casos de Prueba

1. ✅ **Lista vacía**: Sin solicitudes pendientes
2. ✅ **Una solicitud**: Mostrar correctamente
3. ✅ **Múltiples solicitudes**: Ordenadas por fecha
4. ✅ **Aprobar plan**: Modal, confirmación, recarga
5. ✅ **Rechazar sin motivo**: Botón deshabilitado
6. ✅ **Rechazar con motivo**: Éxito, recarga
7. ✅ **Navegación a detalle**: Ruta correcta
8. ✅ **Error de conexión**: Mensaje de error
9. ✅ **Plan ya aprobado**: Error 400
10. ✅ **Prioridades**: Colores correctos (alta=rojo, media=amarillo, baja=verde)

### Datos de Prueba

```typescript
const solicitudTest: PlanResumen = {
  id: 35,
  titulo: "Ortodoncia Completa",
  descripcion: "Plan ortodóncico con brackets metálicos",
  estado: "PROPUESTO",
  prioridad: "ALTA",
  precio_total_plan: "3500.00",
  cantidad_items: 8,
  fecha_presentacion: "2025-11-16T21:00:00Z",
  odontologo_info: {
    nombre: "Juan",
    apellido: "Pérez"
  }
};
```

---

## 🎯 Mejoras Futuras

1. **Notificaciones Push**: Alertar al paciente de nuevas propuestas
2. **Comparar Planes**: Si hay múltiples propuestas para el mismo problema
3. **Chat Integrado**: Preguntas directas al odontólogo antes de decidir
4. **Historial Completo**: Ver planes rechazados anteriormente
5. **Recordatorios**: Si no responde en X días
6. **Firma Digital**: Aceptación con firma electrónica

---

**Siguiente**: [Guía 33 - Detalles de Factura y Pagos](./33_detalle_factura_pagos.md)
