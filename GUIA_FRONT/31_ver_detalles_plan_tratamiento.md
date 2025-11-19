# Guía 31: Ver Detalles del Plan de Tratamiento (Paciente)

## 📋 Información General

**Caso de Uso**: CU09 - Gestión de Planes de Tratamiento  
**Actor**: Paciente  
**Objetivo**: Visualizar información completa de su plan de tratamiento, incluyendo progreso, costos, procedimientos y documentos

---

## 🎯 Funcionalidad

El paciente puede:
- ✅ Ver todos los ítems del plan (procedimientos)
- ✅ Ver progreso visual del tratamiento (% completado)
- ✅ Ver costos: total del plan, monto pagado, saldo pendiente
- ✅ Identificar qué tratamientos están completados, en progreso o pendientes
- ✅ Ver fechas de cada procedimiento
- ✅ Ver documentos clínicos adjuntos (radiografías, reportes)
- ✅ Ver observaciones del odontólogo
- ✅ Descargar comprobantes y documentos

---

## 🔌 API Endpoints

### 1. Obtener Detalles del Plan
```
GET /api/tratamientos/planes/{id}/
```

**Headers requeridos**:
```
Authorization: Bearer {access_token}
```

**Parámetros de ruta**:
- `id`: ID del plan de tratamiento

**Respuesta exitosa** (200 OK):
```json
{
  "id": 33,
  "titulo": "Tratamiento Endodoncia + Corona",
  "descripcion": "Plan integral para restauración de pieza 16 con endodoncia realizada",
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
  "estado": "EN_PROGRESO",
  "estado_display": "En progreso",
  "prioridad": "MEDIA",
  "prioridad_display": "Media",
  "fecha_creacion": "2025-11-16T20:28:59.730746Z",
  "fecha_presentacion": null,
  "fecha_aceptacion": null,
  "fecha_inicio": "2025-11-01T20:28:59.730307Z",
  "fecha_finalizacion": null,
  "notas_internas": null,
  "precio_total_plan": "810.00",
  "cantidad_items": 6,
  "porcentaje_completado": 50,
  "puede_ser_editado": true,
  "creado": "2025-11-16T20:28:59.730773Z",
  "actualizado": "2025-11-16T20:28:59.730778Z",
  "items": [
    {
      "id": 99,
      "tratamiento": {
        "id": 1,
        "nombre": "Consulta General",
        "descripcion": "Evaluación inicial del paciente"
      },
      "precio": "50.00",
      "estado": "COMPLETADO",
      "estado_display": "Completado",
      "orden": 1,
      "notas": "Consulta inicial completada - Diagnóstico: caries múltiples y necesidad de endodoncia",
      "creado": "2025-11-16T20:28:59.730822Z",
      "actualizado": "2025-11-16T20:28:59.730825Z"
    },
    {
      "id": 100,
      "tratamiento": {
        "id": 2,
        "nombre": "Limpieza Dental",
        "descripcion": "Profilaxis y limpieza profunda"
      },
      "precio": "80.00",
      "estado": "COMPLETADO",
      "estado_display": "Completado",
      "orden": 2,
      "notas": "Limpieza profunda realizada - Eliminación de sarro y placa bacteriana",
      "creado": "2025-11-16T20:28:59.730844Z",
      "actualizado": "2025-11-16T20:28:59.730846Z"
    },
    {
      "id": 101,
      "tratamiento": {
        "id": 3,
        "nombre": "Restauración Dental",
        "descripcion": "Restauración con resina compuesta"
      },
      "precio": "150.00",
      "estado": "COMPLETADO",
      "estado_display": "Completado",
      "orden": 3,
      "notas": "Restauración pieza 36 - Resina compuesta aplicada exitosamente",
      "creado": "2025-11-16T20:28:59.730865Z",
      "actualizado": "2025-11-16T20:28:59.730867Z"
    },
    {
      "id": 102,
      "tratamiento": {
        "id": 4,
        "nombre": "Endodoncia",
        "descripcion": "Tratamiento de conducto"
      },
      "precio": "300.00",
      "estado": "EN_PROGRESO",
      "estado_display": "En progreso",
      "orden": 4,
      "notas": "Endodoncia pieza 46 - Primera sesión completada, falta obturación final",
      "creado": "2025-11-16T20:28:59.730886Z",
      "actualizado": "2025-11-16T20:28:59.730888Z"
    },
    {
      "id": 103,
      "tratamiento": {
        "id": 3,
        "nombre": "Restauración Dental",
        "descripcion": "Restauración con resina compuesta"
      },
      "precio": "150.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 5,
      "notas": "Restauración pieza 47 - Programada para próxima semana",
      "creado": "2025-11-16T20:28:59.730907Z",
      "actualizado": "2025-11-16T20:28:59.730909Z"
    },
    {
      "id": 104,
      "tratamiento": {
        "id": 2,
        "nombre": "Limpieza Dental",
        "descripcion": "Profilaxis y limpieza profunda"
      },
      "precio": "80.00",
      "estado": "PENDIENTE",
      "estado_display": "Pendiente",
      "orden": 6,
      "notas": "Control y limpieza de mantenimiento - Programado en 3 meses",
      "creado": "2025-11-16T20:28:59.730928Z",
      "actualizado": "2025-11-16T20:28:59.730930Z"
    }
  ]
}
```

**Errores posibles**:
```
❌ 404 "Not found" → Plan no existe
❌ 403 "Forbidden" → El plan no pertenece al paciente autenticado
❌ 401 "Unauthorized" → Token inválido o expirado
```

---

### 2. Descargar Documento
```
GET /api/historial/documentos/{id}/descargar/
```

**Respuesta**: Archivo descargable (PDF, JPG, PNG, etc.)

---

## 🔧 Implementación Frontend

### 1. Service - `planesService.ts`

Agregar función para obtener detalle del plan:

```typescript
// src/services/planesService.ts

/**
 * Obtiene los detalles completos de un plan de tratamiento
 */
export const obtenerDetallePlan = async (planId: number): Promise<PlanDetalle> => {
  console.log('📋 Obteniendo detalles del plan:', planId);
  
  const response = await apiClient.get<PlanDetalle>(`/api/tratamientos/planes/${planId}/`);
  
  console.log('✅ Detalles del plan obtenidos:', response.data);
  return response.data;
};

/**
 * Descarga un documento clínico
 */
export const descargarDocumento = async (documentoId: number): Promise<void> => {
  console.log('📥 Descargando documento:', documentoId);
  
  const response = await apiClient.get(`/api/historial/documentos/${documentoId}/descargar/`, {
    responseType: 'blob'
  });
  
  // Crear URL temporal para descargar
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `documento_${documentoId}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
  
  console.log('✅ Documento descargado');
};

export interface PlanDetalle {
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
  estado: 'PROPUESTO' | 'APROBADO' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  estado_display: string;
  prioridad: string;
  prioridad_display: string;
  fecha_creacion: string;
  fecha_presentacion: string | null;
  fecha_aceptacion: string | null;
  fecha_inicio: string | null;
  fecha_finalizacion: string | null;
  notas_internas: string | null;
  precio_total_plan: string;
  cantidad_items: number;
  porcentaje_completado: number;
  puede_ser_editado: boolean;
  creado: string;
  actualizado: string;
  items: ItemPlanDetalle[];
}

export interface ItemPlanDetalle {
  id: number;
  tratamiento: {
    id: number;
    nombre: string;
    descripcion: string;
  };
  precio: string;
  estado: 'PENDIENTE' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  estado_display: string;
  orden: number;
  notas: string | null;
  creado: string;
  actualizado: string;
}

// Nota: El backend actual NO devuelve documentos ni facturas en el detalle del plan
// Estas interfaces se mantendrán para futuras implementaciones
```

---

### 2. Componente - `DetallePlan.tsx`

```tsx
// src/pages/paciente/DetallePlan.tsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { obtenerDetallePlan, descargarDocumento, PlanDetalle } from '../../services/planesService';

export default function DetallePlan() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [plan, setPlan] = useState<PlanDetalle | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [descargando, setDescargando] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      cargarDetallePlan(parseInt(id));
    }
  }, [id]);

  const cargarDetallePlan = async (planId: number) => {
    try {
      setCargando(true);
      const data = await obtenerDetallePlan(planId);
      setPlan(data);
    } catch (err: any) {
      console.error('❌ Error cargando plan:', err);
      if (err.response?.status === 404) {
        setError('Plan de tratamiento no encontrado');
      } else if (err.response?.status === 403) {
        setError('No tiene permiso para ver este plan');
      } else {
        setError('Error al cargar los detalles del plan');
      }
    } finally {
      setCargando(false);
    }
  };

  const handleDescargarDocumento = async (documentoId: number) => {
    try {
      setDescargando(documentoId);
      await descargarDocumento(documentoId);
    } catch (err) {
      console.error('❌ Error descargando documento:', err);
      alert('Error al descargar el documento');
    } finally {
      setDescargando(null);
    }
  };

  const getEstadoBadgeColor = (estado: string) => {
    switch (estado) {
      case 'COMPLETADO':
        return 'bg-green-100 text-green-800';
      case 'EN_PROGRESO':
        return 'bg-blue-100 text-blue-800';
      case 'PENDIENTE':
        return 'bg-yellow-100 text-yellow-800';
      case 'CANCELADO':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando detalles del plan...</p>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/paciente/planes')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Volver a Planes
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/paciente/planes')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center"
          >
            ← Volver a Planes
          </button>
          <h1 className="text-3xl font-bold text-gray-800">
            {plan.titulo}
          </h1>
          <p className="text-gray-600 mt-1">
            Odontólogo: Dr. {plan.odontologo_info.nombre} {plan.odontologo_info.apellido}
          </p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getEstadoBadgeColor(plan.estado)}`}>
          {plan.estado_display}
        </span>
      </div>

      {/* Resumen General */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Progreso</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {plan.porcentaje_completado}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {plan.items.filter(i => i.estado === 'COMPLETADO').length} de {plan.cantidad_items} procedimientos
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Costo Total</div>
          <div className="text-2xl font-bold text-gray-800 mt-1">
            ${plan.precio_total_plan}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Plan completo
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Items</div>
          <div className="text-2xl font-bold text-indigo-600 mt-1">
            {plan.cantidad_items}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Procedimientos
          </div>
        </div>
      </div>

      {/* Barra de Progreso Visual */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Progreso del Tratamiento
        </h2>
        <div className="relative">
          <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
            <div
              style={{ width: `${plan.porcentaje_completado}%` }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-500"
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>Inicio</span>
            <span className="font-semibold">{plan.porcentaje_completado}% Completado</span>
            <span>Finalización</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 mt-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {plan.items.filter(i => i.estado === 'COMPLETADO').length}
            </div>
            <div className="text-xs text-gray-600">Completados</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">
              {plan.items.filter(i => i.estado === 'EN_PROGRESO').length}
            </div>
            <div className="text-xs text-gray-600">En Progreso</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">
              {plan.items.filter(i => i.estado === 'PENDIENTE').length}
            </div>
            <div className="text-xs text-gray-600">Pendientes</div>
          </div>
        </div>
      </div>

      {/* Descripción y Notas */}
      {(plan.descripcion || plan.notas_internas) && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          {plan.descripcion && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Descripción del Plan</h3>
              <p className="text-gray-600">{plan.descripcion}</p>
            </div>
          )}
          {plan.notas_internas && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Notas Internas</h3>
              <p className="text-gray-600">{plan.notas_internas}</p>
            </div>
          )}
        </div>
      )}

      {/* Lista de Procedimientos */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">
            Procedimientos del Plan ({plan.cantidad_items})
          </h2>
        </div>
        <div className="divide-y divide-gray-200">
          {plan.items.map((item) => (
            <div key={item.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start flex-1">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-sm font-semibold text-blue-600">{item.orden}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {item.tratamiento.nombre}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {item.tratamiento.descripcion}
                    </p>
                    {item.notas && (
                      <p className="text-sm text-gray-600 mt-2 italic bg-gray-50 p-2 rounded">
                        💬 {item.notas}
                      </p>
                    )}
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold mb-2 ${getEstadoBadgeColor(item.estado)}`}>
                    {item.estado_display}
                  </div>
                  <div className="text-lg font-bold text-gray-800">
                    ${item.precio}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Nota: Documentos y Facturas se manejan en módulos separados */}

      {/* Fechas del Tratamiento */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
        <h3 className="font-semibold text-blue-800 mb-2">📅 Cronología del Tratamiento</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-blue-700">Fecha de Creación:</span>
            <div className="font-semibold text-blue-900">
              {new Date(plan.fecha_creacion).toLocaleDateString('es-ES')}
            </div>
          </div>
          {plan.fecha_inicio && (
            <div>
              <span className="text-blue-700">Fecha de Inicio:</span>
              <div className="font-semibold text-blue-900">
                {new Date(plan.fecha_inicio).toLocaleDateString('es-ES')}
              </div>
            </div>
          )}
          {plan.fecha_finalizacion && (
            <div>
              <span className="text-blue-700">Fecha de Finalización:</span>
              <div className="font-semibold text-blue-900">
                {new Date(plan.fecha_finalizacion).toLocaleDateString('es-ES')}
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
```

---

## 🎨 Características de la UI

### 1. Cards de Resumen
- **4 métricas principales**: Progreso, Costo Total, Pagado, Saldo Pendiente
- **Colores distintivos**: Azul (progreso), Verde (pagado), Naranja (pendiente)
- **Información clara**: Valores grandes, descripciones pequeñas

### 2. Barra de Progreso
- **Progreso visual**: Barra animada con porcentaje
- **Contador de estados**: Completados, En progreso, Pendientes
- **Transiciones suaves**: Animación al cargar

### 3. Lista de Procedimientos
- **Orden numerado**: Badge con número de secuencia
- **Estados coloreados**: Verde (completado), Azul (en progreso), Amarillo (pendiente)
- **Información detallada**: Nombre, descripción, pieza dental, fecha, observaciones
- **Precio destacado**: En negrita a la derecha

### 4. Documentos Clínicos
- **Grid responsive**: 1 columna (móvil), 2 columnas (desktop)
- **Botón de descarga**: Con indicador de carga
- **Metadata visible**: Tipo, subido por, fecha

### 5. Facturas Relacionadas
- **Lista compacta**: Con número, fecha, monto, estado
- **Navegación directa**: Botón para ver detalle de factura
- **Estados claros**: Verde (pagada), Naranja (pendiente)

---

## 📝 Notas Importantes

### 1. Permisos y Seguridad

El backend valida que el plan pertenezca al paciente autenticado:

```python
# En el ViewSet del backend
def get_queryset(self):
    user = self.request.user
    if user.tipo_usuario == 'PACIENTE':
        return Plan.objects.filter(paciente=user.perfil_paciente)
    return Plan.objects.none()
```

Si el paciente intenta acceder a un plan que no es suyo:
```
❌ 403 Forbidden
```

### 2. Descarga de Documentos

La descarga se maneja con `responseType: 'blob'`:

```typescript
const response = await apiClient.get(`/api/.../descargar/`, {
  responseType: 'blob'  // ← Importante para archivos binarios
});

// Crear enlace temporal de descarga
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', 'documento.pdf');
link.click();
window.URL.revokeObjectURL(url);  // ← Limpiar memoria
```

### 3. Estados de los Items

| Estado | Color | Descripción |
|--------|-------|-------------|
| `COMPLETADO` | Verde | Procedimiento finalizado |
| `EN_PROGRESO` | Azul | Procedimiento iniciado pero no terminado |
| `PENDIENTE` | Amarillo | Aún no iniciado |
| `CANCELADO` | Rojo | Procedimiento cancelado |

### 4. Cálculo del Progreso

El backend calcula automáticamente:

```python
porcentaje_completado = (items_completados / total_items) * 100
```

### 5. Navegación

Rutas sugeridas:
```
/paciente/planes              → Lista de planes
/paciente/planes/:id          → Detalle del plan (esta guía)
/paciente/facturas/:id        → Detalle de factura
```

---

## 🧪 Testing

### Datos de Prueba

```typescript
// Plan de ejemplo
const planTest = {
  id: 33,
  nombre: "Tratamiento Endodoncia + Corona",
  estado: "EN_PROGRESO",
  porcentaje_completado: 50.0,
  total_items: 6,
  items_completados: 3,
  costo_total_display: "$810.00",
  monto_pagado_display: "$450.00",
  saldo_pendiente_display: "$360.00"
};
```

### Casos de Prueba

1. ✅ **Plan en progreso**: Mostrar barra parcialmente llena
2. ✅ **Plan completado**: Barra al 100%, todos los items verdes
3. ✅ **Plan pendiente**: Sin fechas de realización, todos amarillos
4. ✅ **Con documentos**: Mostrar sección de documentos
5. ✅ **Sin documentos**: Ocultar sección
6. ✅ **Con facturas**: Mostrar lista de facturas
7. ✅ **Descarga de documento**: Probar descarga de PDF/imagen
8. ✅ **Plan no autorizado**: Verificar error 403
9. ✅ **Plan inexistente**: Verificar error 404

---

**Siguiente**: [Guía 32 - Solicitudes y Aprobaciones](./32_solicitudes_aprobaciones.md)
