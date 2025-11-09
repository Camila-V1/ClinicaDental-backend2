# 📅 GUÍA: AGENDA DE CITAS - ODONTÓLOGO

## 🎯 Objetivo
Implementar la agenda de citas para que el odontólogo pueda:
- Ver sus citas del día/semana/mes
- Filtrar por fecha y estado
- Ver detalles de cada cita
- Marcar asistencia (completada/cancelada)

---

## 📋 Endpoints Backend Disponibles

### 1. Listar Citas del Odontólogo
```http
GET /api/agenda/citas/
```

**Filtros disponibles (query params):**
- `?fecha_inicio=2025-11-07` - Desde fecha
- `?fecha_fin=2025-11-14` - Hasta fecha
- `?estado=PENDIENTE` - Estados: PENDIENTE, CONFIRMADA, ATENDIDA, CANCELADA
- `?paciente=5` - ID del paciente

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "paciente_nombre": "María",
    "paciente_email": "paciente@clinica-demo.com",
    "odontologo_nombre": "Dr. Juan Pérez",
    "fecha_hora": "2025-11-07T13:00:00Z",
    "estado": "CONFIRMADA",
    "motivo": "Control post-limpieza",
    "observaciones": "Revisar estado de encías"
  }
]
```

### 2. Obtener Detalle de una Cita
```http
GET /api/agenda/citas/{id}/
```

**Response 200 OK:**
```json
{
  "id": 1,
  "paciente": 5,
  "paciente_nombre": "María",
  "paciente_email": "paciente@clinica-demo.com",
  "odontologo": 3,
  "odontologo_nombre": "Dr. Juan Pérez",
  "odontologo_email": "odontologo@clinica-demo.com",
  "odontologo_especialidad": "Odontología General",
  "fecha_hora": "2025-11-07T13:00:00Z",
  "motivo": "Control post-limpieza",
  "observaciones": "Revisar estado de encías",
  "estado": "CONFIRMADA",
  "creado": "2025-11-01T09:00:00Z",
  "actualizado": "2025-11-01T09:00:00Z"
}
```

### 3. Actualizar Estado de Cita
```http
PATCH /api/agenda/citas/{id}/
```

**Request Body:**
```json
{
  "estado": "ATENDIDA",
  "observaciones": "Paciente asistió. Limpieza realizada exitosamente."
}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "paciente": 5,
  "paciente_nombre": "María",
  "paciente_email": "paciente@clinica-demo.com",
  "odontologo": 3,
  "odontologo_nombre": "Dr. Juan Pérez",
  "odontologo_email": "odontologo@clinica-demo.com",
  "odontologo_especialidad": "Odontología General",
  "fecha_hora": "2025-11-07T13:00:00Z",
  "motivo": "Control post-limpieza",
  "observaciones": "Paciente asistió. Limpieza realizada exitosamente.",
  "estado": "ATENDIDA",
  "creado": "2025-11-01T09:00:00Z",
  "actualizado": "2025-11-07T11:30:00Z"
}
```

---

## 🛠️ Implementación Frontend

### PASO 1: Crear servicio de API

**Archivo:** `src/services/agendaService.ts`

```typescript
import api from '../config/apiConfig';

export interface Cita {
  id: number;
  paciente: number; // ID del perfil paciente
  paciente_nombre: string;
  paciente_email: string;
  odontologo: number; // ID del perfil odontólogo
  odontologo_nombre: string;
  odontologo_email?: string;
  odontologo_especialidad?: string;
  fecha_hora: string;
  motivo: string;
  observaciones?: string;
  estado: 'PENDIENTE' | 'CONFIRMADA' | 'ATENDIDA' | 'CANCELADA';
  creado?: string;
  actualizado?: string;
}

export interface FiltrosCitas {
  fecha_inicio?: string; // YYYY-MM-DD
  fecha_fin?: string;
  estado?: string;
  paciente?: number;
}

/**
 * Obtener citas del odontólogo actual
 */
export const obtenerCitas = async (filtros?: FiltrosCitas): Promise<Cita[]> => {
  const params = new URLSearchParams();
  
  if (filtros?.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio);
  if (filtros?.fecha_fin) params.append('fecha_fin', filtros.fecha_fin);
  if (filtros?.estado) params.append('estado', filtros.estado);
  if (filtros?.paciente) params.append('paciente', filtros.paciente.toString());

  const response = await api.get<Cita[]>(`/api/agenda/citas/?${params}`);
  return response.data;
};

/**
 * Obtener detalle de una cita
 */
export const obtenerCita = async (id: number): Promise<Cita> => {
  const response = await api.get<Cita>(`/api/agenda/citas/${id}/`);
  return response.data;
};

/**
 * Actualizar estado de cita
 */
export const actualizarCita = async (
  id: number,
  datos: Partial<Pick<Cita, 'estado' | 'observaciones'>>
): Promise<Cita> => {
  const response = await api.patch<Cita>(`/api/agenda/citas/${id}/`, datos);
  return response.data;
};

/**
 * Marcar cita como atendida
 */
export const atenderCita = async (id: number, observaciones?: string): Promise<Cita> => {
  return actualizarCita(id, { estado: 'ATENDIDA', observaciones });
};

/**
 * Cancelar cita
 */
export const cancelarCita = async (id: number, motivo?: string): Promise<Cita> => {
  return actualizarCita(id, { estado: 'CANCELADA', observaciones: motivo });
};
```

---

### PASO 2: Crear componente de Lista de Citas

**Archivo:** `src/pages/odontologo/AgendaCitas.tsx`

```typescript
import { useState, useEffect } from 'react';
import { obtenerCitas, atenderCita, cancelarCita, type Cita } from '../../services/agendaService';

export default function AgendaCitas() {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [fechaInicio, setFechaInicio] = useState<string>('');
  const [fechaFin, setFechaFin] = useState<string>('');

  // Cargar citas al montar componente
  useEffect(() => {
    cargarCitas();
  }, [filtroEstado, fechaInicio, fechaFin]);

  const cargarCitas = async () => {
    try {
      setLoading(true);
      const data = await obtenerCitas({
        estado: filtroEstado || undefined,
        fecha_inicio: fechaInicio || undefined,
        fecha_fin: fechaFin || undefined,
      });
      setCitas(data);
    } catch (error) {
      console.error('Error al cargar citas:', error);
      alert('Error al cargar citas');
    } finally {
      setLoading(false);
    }
  };

  const handleAtender = async (id: number) => {
    if (!confirm('¿Marcar esta cita como atendida?')) return;
    
    try {
      await atenderCita(id, 'Atención realizada exitosamente');
      await cargarCitas(); // Recargar lista
      alert('✅ Cita marcada como atendida');
    } catch (error) {
      console.error('Error:', error);
      alert('Error al atender cita');
    }
  };

  const handleCancelar = async (id: number) => {
    const motivo = prompt('Motivo de cancelación:');
    if (!motivo) return;

    try {
      await cancelarCita(id, motivo);
      await cargarCitas();
      alert('✅ Cita cancelada');
    } catch (error) {
      console.error('Error:', error);
      alert('Error al cancelar cita');
    }
  };

  const obtenerColorEstado = (estado: string) => {
    switch (estado) {
      case 'PENDIENTE': return 'bg-yellow-100 text-yellow-800';
      case 'CONFIRMADA': return 'bg-blue-100 text-blue-800';
      case 'ATENDIDA': return 'bg-green-100 text-green-800';
      case 'CANCELADA': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando citas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">📅 Mi Agenda</h1>
        <p className="text-gray-600 mt-1">Gestiona tus citas y consultas</p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Filtro por Estado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="CONFIRMADA">Confirmada</option>
              <option value="ATENDIDA">Atendida</option>
              <option value="CANCELADA">Cancelada</option>
            </select>
          </div>

          {/* Filtro Fecha Inicio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Desde
            </label>
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filtro Fecha Fin */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hasta
            </label>
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Lista de Citas */}
      {citas.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">📭 No hay citas para mostrar</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Paciente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha y Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Motivo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {citas.map((cita) => (
                  <tr key={cita.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {cita.paciente_nombre}
                        </div>
                        <div className="text-sm text-gray-500">
                          {cita.paciente_email}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatearFecha(cita.fecha_hora)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{cita.motivo}</div>
                      {cita.observaciones && (
                        <div className="text-sm text-gray-500 mt-1">
                          {cita.observaciones}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${obtenerColorEstado(cita.estado)}`}>
                        {cita.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {cita.estado === 'CONFIRMADA' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleAtender(cita.id)}
                            className="text-green-600 hover:text-green-900"
                          >
                            ✓ Atender
                          </button>
                          <button
                            onClick={() => handleCancelar(cita.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            ✗ Cancelar
                          </button>
                        </div>
                      )}
                      {cita.estado === 'PENDIENTE' && (
                        <button
                          onClick={() => handleCancelar(cita.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          ✗ Cancelar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### PASO 3: Agregar ruta en el routing

**Archivo:** `src/App.tsx` (o donde tengas las rutas)

```typescript
import AgendaCitas from './pages/odontologo/AgendaCitas';

// Dentro de tus rutas protegidas para ODONTOLOGO:
<Route path="/odontologo/agenda" element={<AgendaCitas />} />
```

---

## 🎨 Estilos con Tailwind CSS

El ejemplo usa Tailwind CSS. Si usas otra librería (Material-UI, Ant Design), adapta las clases.

**Colores de estado:**
- 🟡 PENDIENTE: `bg-yellow-100 text-yellow-800`
- 🔵 CONFIRMADA: `bg-blue-100 text-blue-800`
- 🟢 ATENDIDA: `bg-green-100 text-green-800`
- 🔴 CANCELADA: `bg-red-100 text-red-800`

---

## ✅ Checklist de Implementación

- [ ] Crear `agendaService.ts` con funciones de API
- [ ] Crear componente `AgendaCitas.tsx`
- [ ] Agregar ruta en el router
- [ ] Probar con usuario odontólogo
- [ ] Verificar filtros funcionan
- [ ] Verificar acciones (atender/cancelar)
- [ ] Agregar link en menú lateral/navbar

---

## 🧪 Cómo Probar

1. Login como odontólogo: `odontologo@clinica-demo.com` / `odontologo123`
2. Navegar a `/odontologo/agenda`
3. Verificar que se cargan las 7 citas del Dr. Juan
4. Probar filtros por estado y fecha
5. Marcar una cita como atendida
6. Intentar cancelar una cita

**Citas de prueba disponibles:**
- 2 citas ATENDIDAS (pasadas)
- 3 citas CONFIRMADAS (hoy y futuras)
- 1 cita PENDIENTE
- 1 cita CANCELADA

---

## 📊 Ejemplo de Respuesta Real del API

```json
{
  "id": 3,
  "paciente_nombre": "María",
  "paciente_email": "paciente@clinica-demo.com",
  "odontologo_nombre": "Dr. Juan",
  "fecha_hora": "2025-11-07T13:00:00Z",
  "estado": "CONFIRMADA",
  "motivo": "Control post-limpieza",
  "observaciones": "Revisar estado de encías"
}
```

---

## 🚀 Próximos Pasos

Una vez funcione la Agenda, continuamos con:
1. ✅ Agenda de Citas (actual)
2. 📋 Historial Clínico (ver/editar)
3. 👥 Listado de Pacientes
4. 🦷 Registro de Tratamientos

**¿Está clara esta guía? ¿Necesitas que cree la siguiente (Historial Clínico)?** 🎯
