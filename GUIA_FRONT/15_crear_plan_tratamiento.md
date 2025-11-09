# 🦷 GUÍA 15: CREAR PLAN DE TRATAMIENTO

## 🎯 Objetivo

Implementar el módulo completo de **Planes de Tratamiento** para que el odontólogo pueda:
1. Crear un plan de tratamiento para un paciente
2. Agregar servicios (ítems) al plan con precios dinámicos
3. Visualizar el precio total calculado automáticamente
4. Gestionar estados del plan (PROPUESTO → PRESENTADO → ACEPTADO → EN_PROGRESO → COMPLETADO)

Este es el **corazón del sistema de presupuestos** con precios dinámicos basados en materiales seleccionados.

---

## 📋 Endpoints Backend Disponibles

### 1. Listar/Crear Planes
```http
GET  /api/tratamientos/planes/
POST /api/tratamientos/planes/
```

### 2. Detalle/Actualizar Plan
```http
GET    /api/tratamientos/planes/{id}/
PUT    /api/tratamientos/planes/{id}/
PATCH  /api/tratamientos/planes/{id}/
DELETE /api/tratamientos/planes/{id}/
```

### 3. Listar Servicios Disponibles
```http
GET /api/tratamientos/servicios/
```

### 4. Crear/Listar Ítems del Plan
```http
GET  /api/tratamientos/items/
POST /api/tratamientos/items/
PUT  /api/tratamientos/items/{id}/
```

---

## 📊 Estructura de Datos

### PlanDeTratamiento (Request para POST)
```typescript
interface CrearPlanDTO {
  paciente: number;              // ID del PerfilPaciente
  odontologo: number;            // ID del PerfilOdontologo
  titulo: string;                // Ej: "Rehabilitación Dental Completa"
  descripcion?: string;          // Descripción detallada
  estado?: string;               // "PROPUESTO" | "PRESENTADO" | "ACEPTADO" | "EN_PROGRESO" | "COMPLETADO"
  prioridad?: string;            // "BAJA" | "MEDIA" | "ALTA" | "URGENTE"
  notas_internas?: string;       // Notas privadas para el equipo
}
```

### PlanDeTratamiento (Response)
```typescript
interface PlanDeTratamiento {
  id: number;
  titulo: string;
  descripcion: string;
  
  // Relaciones
  paciente: number;
  paciente_info: {
    id: number;
    nombre_completo: string;
    email: string;
  };
  odontologo: number;
  odontologo_info: {
    id: number;
    nombre_completo: string;
    especialidad: string | null;
  };
  
  // Estado
  estado: string;              // "PROPUESTO", "ACEPTADO", etc.
  estado_display: string;      // "Propuesto", "Aceptado", etc.
  prioridad: string;
  prioridad_display: string;
  
  // Fechas
  fecha_creacion: string;
  fecha_presentacion: string | null;
  fecha_aceptacion: string | null;
  fecha_inicio: string | null;
  fecha_finalizacion: string | null;
  
  // Ítems y cálculos
  items: ItemPlanTratamiento[];  // Array de ítems anidados
  precio_total_plan: string;     // Decimal calculado automáticamente
  cantidad_items: number;
  porcentaje_completado: number; // 0-100
  puede_ser_editado: boolean;
  
  // Metadatos
  notas_internas: string;
  creado: string;
  actualizado: string;
}
```

### ItemPlanTratamiento (Request para POST)
```typescript
interface CrearItemPlanDTO {
  plan: number;                        // ID del plan
  servicio: number;                    // ID del servicio
  insumo_seleccionado?: number | null; // ID del insumo opcional
  orden?: number;                      // Orden de ejecución (default: 1)
  notas?: string;                      // Notas específicas
  fecha_estimada?: string;             // Fecha estimada (YYYY-MM-DD)
}
```

### ItemPlanTratamiento (Response)
```typescript
interface ItemPlanTratamiento {
  id: number;
  plan: number;
  
  // Servicio
  servicio: number;
  servicio_nombre: string;
  servicio_info: {
    id: number;
    nombre: string;
    codigo_servicio: string;
    precio_base: string;
    categoria_nombre: string;
    duracion_formateada: string;
    materiales_fijos: MaterialFijo[];
    materiales_opcionales: MaterialOpcional[];
  };
  
  // Insumo seleccionado (si aplica)
  insumo_seleccionado: number | null;
  insumo_nombre: string | null;
  insumo_seleccionado_info: Insumo | null;
  
  // Snapshots de precios (congelados al crear)
  precio_servicio_snapshot: string;
  precio_materiales_fijos_snapshot: string;
  precio_insumo_seleccionado_snapshot: string;
  
  // Precio total calculado
  precio_total: string;
  precio_total_formateado: string;  // Ej: "$350.00"
  
  // Estado
  estado: string;               // "PENDIENTE" | "EN_PROGRESO" | "COMPLETADO" | "CANCELADO"
  estado_display: string;
  orden: number;
  notas: string;
  fecha_estimada: string | null;
  fecha_realizada: string | null;
  
  creado: string;
  actualizado: string;
}
```

### Servicio (Response)
```typescript
interface Servicio {
  id: number;
  codigo_servicio: string;      // Ej: "ENDO-001"
  nombre: string;
  descripcion: string;
  categoria: number;
  categoria_nombre: string;
  precio_base: string;
  tiempo_estimado: number;      // Minutos
  duracion_formateada: string;  // Ej: "1h 30min"
  requiere_cita_previa: boolean;
  requiere_autorizacion: boolean;
  activo: boolean;
  
  // Materiales (recetas)
  materiales_fijos: MaterialServicioFijo[];
  materiales_opcionales: MaterialServicioOpcional[];
  costo_materiales_fijos: string;
  tiene_materiales_opcionales: boolean;
}
```

---

## 🛠️ Implementación Frontend

### PASO 1: Crear Servicio de Planes

**Archivo:** `src/services/planesService.ts`

```typescript
import api from './axios';

// ============================================================================
// TIPOS
// ============================================================================

export interface CrearPlanDTO {
  paciente: number;
  odontologo: number;
  titulo: string;
  descripcion?: string;
  estado?: 'PROPUESTO' | 'PRESENTADO' | 'ACEPTADO' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  prioridad?: 'BAJA' | 'MEDIA' | 'ALTA' | 'URGENTE';
  notas_internas?: string;
}

export interface PacienteInfo {
  id: number;
  nombre_completo: string;
  email: string;
}

export interface OdontologoInfo {
  id: number;
  nombre_completo: string;
  especialidad: string | null;
}

export interface ItemPlanTratamiento {
  id: number;
  plan: number;
  servicio: number;
  servicio_nombre: string;
  insumo_seleccionado: number | null;
  insumo_nombre: string | null;
  precio_servicio_snapshot: string;
  precio_materiales_fijos_snapshot: string;
  precio_insumo_seleccionado_snapshot: string;
  precio_total: string;
  precio_total_formateado: string;
  estado: string;
  estado_display: string;
  orden: number;
  notas: string;
  fecha_estimada: string | null;
  fecha_realizada: string | null;
  creado: string;
}

export interface PlanDeTratamiento {
  id: number;
  titulo: string;
  descripcion: string;
  paciente: number;
  paciente_info: PacienteInfo;
  odontologo: number;
  odontologo_info: OdontologoInfo;
  estado: string;
  estado_display: string;
  prioridad: string;
  prioridad_display: string;
  fecha_creacion: string;
  fecha_presentacion: string | null;
  fecha_aceptacion: string | null;
  fecha_inicio: string | null;
  fecha_finalizacion: string | null;
  items: ItemPlanTratamiento[];
  precio_total_plan: string;
  cantidad_items: number;
  porcentaje_completado: number;
  puede_ser_editado: boolean;
  notas_internas: string;
  creado: string;
  actualizado: string;
}

export interface CrearItemPlanDTO {
  plan: number;
  servicio: number;
  insumo_seleccionado?: number | null;
  orden?: number;
  notas?: string;
  fecha_estimada?: string;
}

// ============================================================================
// API CALLS
// ============================================================================

/**
 * Listar planes de tratamiento
 */
export const obtenerPlanes = async (filtros?: {
  paciente?: number;
  odontologo?: number;
  estado?: string;
}): Promise<PlanDeTratamiento[]> => {
  const params = new URLSearchParams();
  if (filtros?.paciente) params.append('paciente', filtros.paciente.toString());
  if (filtros?.odontologo) params.append('odontologo', filtros.odontologo.toString());
  if (filtros?.estado) params.append('estado', filtros.estado);
  
  const response = await api.get<PlanDeTratamiento[]>(
    `/api/tratamientos/planes/${params.toString() ? '?' + params.toString() : ''}`
  );
  return response.data;
};

/**
 * Obtener detalle de un plan
 */
export const obtenerPlan = async (id: number): Promise<PlanDeTratamiento> => {
  const response = await api.get<PlanDeTratamiento>(`/api/tratamientos/planes/${id}/`);
  return response.data;
};

/**
 * Crear un nuevo plan de tratamiento
 */
export const crearPlan = async (datos: CrearPlanDTO): Promise<PlanDeTratamiento> => {
  const response = await api.post<PlanDeTratamiento>('/api/tratamientos/planes/', datos);
  return response.data;
};

/**
 * Actualizar un plan existente
 */
export const actualizarPlan = async (
  id: number,
  datos: Partial<CrearPlanDTO>
): Promise<PlanDeTratamiento> => {
  const response = await api.patch<PlanDeTratamiento>(`/api/tratamientos/planes/${id}/`, datos);
  return response.data;
};

/**
 * Eliminar un plan
 */
export const eliminarPlan = async (id: number): Promise<void> => {
  await api.delete(`/api/tratamientos/planes/${id}/`);
};

/**
 * Crear un ítem (servicio) en el plan
 */
export const crearItemPlan = async (datos: CrearItemPlanDTO): Promise<ItemPlanTratamiento> => {
  const response = await api.post<ItemPlanTratamiento>('/api/tratamientos/items/', datos);
  return response.data;
};

/**
 * Actualizar un ítem del plan
 */
export const actualizarItemPlan = async (
  id: number,
  datos: Partial<CrearItemPlanDTO>
): Promise<ItemPlanTratamiento> => {
  const response = await api.patch<ItemPlanTratamiento>(`/api/tratamientos/items/${id}/`, datos);
  return response.data;
};

/**
 * Eliminar un ítem del plan
 */
export const eliminarItemPlan = async (id: number): Promise<void> => {
  await api.delete(`/api/tratamientos/items/${id}/`);
};

/**
 * Marcar un ítem como completado
 */
export const completarItemPlan = async (id: number): Promise<ItemPlanTratamiento> => {
  const response = await api.patch<ItemPlanTratamiento>(`/api/tratamientos/items/${id}/`, {
    estado: 'COMPLETADO',
    fecha_realizada: new Date().toISOString()
  });
  return response.data;
};
```

---

### PASO 2: Crear Componente de Lista de Planes

**Archivo:** `src/pages/odontologo/PlanesList.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { obtenerPlanes, type PlanDeTratamiento } from '../../services/planesService';

export default function PlanesList() {
  const navigate = useNavigate();
  const [planes, setPlanes] = useState<PlanDeTratamiento[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('TODOS');

  useEffect(() => {
    cargarPlanes();
  }, []);

  const cargarPlanes = async () => {
    try {
      setLoading(true);
      const data = await obtenerPlanes();
      setPlanes(data);
    } catch (error) {
      console.error('Error al cargar planes:', error);
      alert('Error al cargar planes de tratamiento');
    } finally {
      setLoading(false);
    }
  };

  const planesFiltrados = planes.filter(plan => {
    if (filtroEstado === 'TODOS') return true;
    return plan.estado === filtroEstado;
  });

  const obtenerColorEstado = (estado: string) => {
    switch (estado) {
      case 'PROPUESTO': return 'bg-gray-100 text-gray-800';
      case 'PRESENTADO': return 'bg-blue-100 text-blue-800';
      case 'ACEPTADO': return 'bg-green-100 text-green-800';
      case 'EN_PROGRESO': return 'bg-yellow-100 text-yellow-800';
      case 'COMPLETADO': return 'bg-purple-100 text-purple-800';
      case 'CANCELADO': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const obtenerColorPrioridad = (prioridad: string) => {
    switch (prioridad) {
      case 'URGENTE': return 'text-red-600 font-bold';
      case 'ALTA': return 'text-orange-600 font-semibold';
      case 'MEDIA': return 'text-yellow-600';
      case 'BAJA': return 'text-gray-600';
      default: return 'text-gray-600';
    }
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
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📋 Planes de Tratamiento</h1>
          <p className="text-gray-600 mt-1">Gestiona los planes de tratamiento de tus pacientes</p>
        </div>
        <button
          onClick={() => navigate('/odontologo/planes/nuevo')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 font-medium"
        >
          ➕ Nuevo Plan
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex gap-2 flex-wrap">
        {['TODOS', 'PROPUESTO', 'ACEPTADO', 'EN_PROGRESO', 'COMPLETADO'].map(estado => (
          <button
            key={estado}
            onClick={() => setFiltroEstado(estado)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filtroEstado === estado
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            {estado === 'TODOS' ? 'Todos' : estado.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Lista de Planes */}
      {planesFiltrados.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 text-lg">📭 No hay planes con este filtro</p>
          <button
            onClick={() => navigate('/odontologo/planes/nuevo')}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Crear primer plan de tratamiento
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {planesFiltrados.map((plan) => (
            <div
              key={plan.id}
              onClick={() => navigate(`/odontologo/planes/${plan.id}`)}
              className="bg-white rounded-lg shadow hover:shadow-xl transition-shadow cursor-pointer border border-gray-200"
            >
              {/* Header Card */}
              <div className="p-5 border-b border-gray-200">
                <div className="flex justify-between items-start mb-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${obtenerColorEstado(plan.estado)}`}>
                    {plan.estado_display}
                  </span>
                  <span className={`text-xs ${obtenerColorPrioridad(plan.prioridad)}`}>
                    🔥 {plan.prioridad_display}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                  {plan.titulo}
                </h3>
                <p className="text-sm text-gray-600">
                  👤 {plan.paciente_info.nombre_completo}
                </p>
              </div>

              {/* Body Card */}
              <div className="p-5">
                {/* Progreso */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Progreso</span>
                    <span className="font-semibold text-gray-900">{plan.porcentaje_completado}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${plan.porcentaje_completado}%` }}
                    ></div>
                  </div>
                </div>

                {/* Ítems y Precio */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Procedimientos</p>
                    <p className="text-lg font-bold text-gray-900">{plan.cantidad_items}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Precio Total</p>
                    <p className="text-lg font-bold text-green-600">${parseFloat(plan.precio_total_plan).toFixed(2)}</p>
                  </div>
                </div>

                {/* Fecha */}
                <div className="text-xs text-gray-500">
                  📅 Creado: {new Date(plan.fecha_creacion).toLocaleDateString('es-ES')}
                </div>
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

### PASO 3: Crear Componente de Formulario de Nuevo Plan

**Archivo:** `src/pages/odontologo/PlanNuevo.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { crearPlan, type CrearPlanDTO } from '../../services/planesService';
import { obtenerUsuarios, type Usuario } from '../../services/usuariosService';
import { useAuth } from '../../context/AuthContext';

export default function PlanNuevo() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [loading, setLoading] = useState(false);
  const [pacientes, setPacientes] = useState<Usuario[]>([]);
  const [buscandoPacientes, setBuscandoPacientes] = useState(true);

  const [formData, setFormData] = useState<CrearPlanDTO>({
    paciente: 0,
    odontologo: usuario?.id || 0,
    titulo: '',
    descripcion: '',
    estado: 'PROPUESTO',
    prioridad: 'MEDIA',
    notas_internas: ''
  });

  useEffect(() => {
    cargarPacientes();
  }, []);

  const cargarPacientes = async () => {
    try {
      setBuscandoPacientes(true);
      const data = await obtenerUsuarios({ tipo_usuario: 'PACIENTE' });
      setPacientes(data);
    } catch (error) {
      console.error('Error al cargar pacientes:', error);
      alert('Error al cargar lista de pacientes');
    } finally {
      setBuscandoPacientes(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.titulo.trim()) {
      alert('El título es obligatorio');
      return;
    }

    if (!formData.paciente) {
      alert('Debes seleccionar un paciente');
      return;
    }

    try {
      setLoading(true);
      const planCreado = await crearPlan(formData);
      alert('✅ Plan de tratamiento creado exitosamente');
      
      // Redirigir al detalle del plan para agregar ítems
      navigate(`/odontologo/planes/${planCreado.id}`);
    } catch (error: any) {
      console.error('Error al crear plan:', error);
      alert('❌ Error al crear plan: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/odontologo/planes')}
          className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
        >
          ← Volver a Planes
        </button>
        <h1 className="text-3xl font-bold text-gray-900">📋 Nuevo Plan de Tratamiento</h1>
        <p className="text-gray-600 mt-1">Crea un plan personalizado para tu paciente</p>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
        {/* Paciente */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Paciente <span className="text-red-500">*</span>
          </label>
          {buscandoPacientes ? (
            <div className="text-gray-500">Cargando pacientes...</div>
          ) : (
            <select
              value={formData.paciente}
              onChange={(e) => setFormData({ ...formData, paciente: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            >
              <option value={0}>Selecciona un paciente</option>
              {pacientes.map(paciente => (
                <option key={paciente.id} value={paciente.id}>
                  {paciente.full_name} - CI: {paciente.ci}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Título */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Título del Plan <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.titulo}
            onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Ej: Rehabilitación Dental Completa"
            required
          />
        </div>

        {/* Descripción */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción
          </label>
          <textarea
            value={formData.descripcion}
            onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Describe el plan de tratamiento general..."
          />
        </div>

        {/* Prioridad */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Prioridad
          </label>
          <select
            value={formData.prioridad}
            onChange={(e) => setFormData({ ...formData, prioridad: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="BAJA">Baja</option>
            <option value="MEDIA">Media</option>
            <option value="ALTA">Alta</option>
            <option value="URGENTE">Urgente</option>
          </select>
        </div>

        {/* Notas Internas */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notas Internas (Solo para el equipo médico)
          </label>
          <textarea
            value={formData.notas_internas}
            onChange={(e) => setFormData({ ...formData, notas_internas: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Notas privadas sobre el plan..."
          />
        </div>

        {/* Botones */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate('/odontologo/planes')}
            disabled={loading}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Creando...
              </>
            ) : (
              '✅ Crear Plan'
            )}
          </button>
        </div>

        {/* Info */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            ℹ️ <strong>Nota:</strong> Después de crear el plan, podrás agregar los servicios (procedimientos) que incluirá el tratamiento.
          </p>
        </div>
      </form>
    </div>
  );
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear `src/services/planesService.ts` con tipos y funciones API
- [ ] Crear `src/pages/odontologo/PlanesList.tsx` (lista de planes)
- [ ] Crear `src/pages/odontologo/PlanNuevo.tsx` (formulario de creación)
- [ ] Agregar rutas en el router:
  ```tsx
  <Route path="/odontologo/planes" element={<PlanesList />} />
  <Route path="/odontologo/planes/nuevo" element={<PlanNuevo />} />
  ```
- [ ] Agregar link en menú de navegación del odontólogo
- [ ] Probar flujo completo de creación

---

## 🧪 Cómo Probar

1. Login como odontólogo: `odontologo@clinica-demo.com` / `odontologo123`

2. Ir a `/odontologo/planes`

3. Click en "➕ Nuevo Plan"

4. Llenar formulario:
   ```
   Paciente: María García
   Título: Rehabilitación Dental Completa
   Descripción: Plan integral que incluye endodoncia, corona y limpieza
   Prioridad: Alta
   ```

5. Click en "✅ Crear Plan"

6. Verificar redirección al detalle del plan

7. En el listado, verificar que aparece el nuevo plan con:
   - Estado: PROPUESTO
   - Progreso: 0%
   - 0 procedimientos
   - Precio: $0.00

---

## 🚀 Próximos Pasos

Después de crear el plan, necesitarás:

1. **Guía 16:** Agregar ítems (servicios) al plan con precios dinámicos
2. **Guía 17:** Vista de detalle del plan con gestión completa
3. **Guía 18:** Vincular episodios desde la agenda

---

## 📝 Notas Importantes

### ⚠️ Validaciones
- ✅ Título obligatorio
- ✅ Paciente obligatorio
- ✅ Odontólogo se auto-asigna del usuario autenticado
- ✅ Estado inicial siempre es PROPUESTO

### 🔒 Seguridad
- ✅ Token JWT requerido
- ✅ Verificación de rol ODONTOLOGO
- ✅ Solo el odontólogo creador puede editar (hasta que se presente)

### 🎨 UX/UI
- ✅ Diseño responsive (mobile-first)
- ✅ Loading states
- ✅ Validaciones en tiempo real
- ✅ Feedback visual de éxito/error
- ✅ Cards visuales con progreso y precios
