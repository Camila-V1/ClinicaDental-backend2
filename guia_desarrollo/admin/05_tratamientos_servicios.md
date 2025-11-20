# 🦷 Tratamientos y Servicios

## 🎯 Objetivo
Gestionar el catálogo de servicios odontológicos y los planes de tratamiento de los pacientes.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Catálogo de servicios**: CRUD completo
2. **Planes de tratamiento**: Crear, ver, actualizar progreso
3. **Presupuestos**: Generar y aprobar
4. **Historial de procedimientos** realizados
5. **Estadísticas** de servicios más demandados
6. **Seguimiento de progreso** del tratamiento

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar servicios
GET /api/tratamientos/servicios/
Response: {
  count: 25,
  results: [
    {
      id: 1,
      nombre: "Limpieza Dental",
      descripcion: "Profilaxis completa",
      precio: 150.00,
      duracion_estimada: 30,
      activo: true
    }
  ]
}

// 2. Crear servicio
POST /api/tratamientos/servicios/
Body: {
  nombre: "Endodoncia",
  descripcion: "Tratamiento de conducto",
  precio: 800.00,
  duracion_estimada: 90
}

// 3. Listar planes de tratamiento
GET /api/tratamientos/planes-tratamiento/?paciente=5
Response: {
  count: 2,
  results: [
    {
      id: 1,
      paciente: { id: 5, usuario: { full_name: "María García" } },
      odontologo: { id: 1, usuario: { full_name: "Dr. Juan Pérez" } },
      diagnostico: "Caries múltiples",
      fecha_inicio: "2025-11-01",
      fecha_fin_estimada: "2025-12-15",
      estado: "EN_PROGRESO",
      progreso: 40,
      items: [
        {
          id: 1,
          servicio: { id: 1, nombre: "Limpieza Dental", precio: 150.00 },
          diente: "18",
          estado: "COMPLETADO",
          precio_acordado: 150.00
        },
        {
          id: 2,
          servicio: { id: 2, nombre: "Resina", precio: 250.00 },
          diente: "16",
          estado: "PENDIENTE",
          precio_acordado: 250.00
        }
      ]
    }
  ]
}

// 4. Crear plan de tratamiento
POST /api/tratamientos/planes-tratamiento/
Body: {
  paciente: 5,
  odontologo: 1,
  diagnostico: "Tratamiento ortodóntico",
  observaciones: "Paciente requiere brackets",
  items: [
    { servicio: 10, diente: "11", precio_acordado: 3500.00 }
  ]
}

// 5. Actualizar item del plan
PATCH /api/tratamientos/items-plan/{id}/
Body: { estado: "COMPLETADO" }

// 6. Estadísticas de servicios
GET /api/tratamientos/estadisticas/servicios/
Response: {
  top_servicios: [
    { servicio: "Limpieza Dental", cantidad: 145, ingresos: 21750.00 },
    { servicio: "Resina", cantidad: 89, ingresos: 22250.00 }
  ]
}

// 7. Generar presupuesto PDF
GET /api/tratamientos/planes-tratamiento/{id}/presupuesto/?formato=pdf
Response: Binary PDF file
```

---

## 💻 Implementación Frontend

### 1. Página de Servicios

```typescript
// src/pages/admin/Servicios.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tratamientosService } from '@/services/admin/tratamientosService';
import ServicioTable from '@/components/admin/tratamientos/ServicioTable';
import ServicioModal from '@/components/admin/tratamientos/ServicioModal';
import { toast } from 'react-hot-toast';

export default function Servicios() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [servicioModal, setServicioModal] = useState<{
    isOpen: boolean;
    servicio?: any;
  }>({ isOpen: false });

  // Fetch servicios
  const { data, isLoading } = useQuery({
    queryKey: ['servicios', search],
    queryFn: () => tratamientosService.getServicios({ search }),
  });

  // Crear/Actualizar servicio
  const servicioMutation = useMutation({
    mutationFn: (data: any) =>
      servicioModal.servicio
        ? tratamientosService.updateServicio(servicioModal.servicio.id, data)
        : tratamientosService.createServicio(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servicios'] });
      setServicioModal({ isOpen: false });
      toast.success(servicioModal.servicio ? 'Servicio actualizado' : 'Servicio creado');
    },
  });

  // Eliminar servicio
  const deleteMutation = useMutation({
    mutationFn: tratamientosService.deleteServicio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servicios'] });
      toast.success('Servicio desactivado');
    },
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Catálogo de Servicios</h1>
          <p className="text-gray-600">Gestiona los servicios odontológicos</p>
        </div>
        <button
          onClick={() => setServicioModal({ isOpen: true })}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Nuevo Servicio
        </button>
      </div>

      {/* Buscador */}
      <div className="bg-white rounded-lg shadow p-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar servicios..."
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Tabla */}
      <ServicioTable
        servicios={data?.results || []}
        isLoading={isLoading}
        onEdit={(servicio) => setServicioModal({ isOpen: true, servicio })}
        onDelete={(id) => {
          if (confirm('¿Desactivar este servicio?')) {
            deleteMutation.mutate(id);
          }
        }}
      />

      {/* Modal */}
      <ServicioModal
        isOpen={servicioModal.isOpen}
        onClose={() => setServicioModal({ isOpen: false })}
        servicio={servicioModal.servicio}
        onSubmit={(data) => servicioMutation.mutate(data)}
        isLoading={servicioMutation.isPending}
      />
    </div>
  );
}
```

---

### 2. Página de Planes de Tratamiento

```typescript
// src/pages/admin/PlanesTratamiento.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tratamientosService } from '@/services/admin/tratamientosService';
import PlanTable from '@/components/admin/tratamientos/PlanTable';
import PlanModal from '@/components/admin/tratamientos/PlanModal';
import { toast } from 'react-hot-toast';

export default function PlanesTratamiento() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    paciente: '',
    estado: '',
  });
  const [planModal, setPlanModal] = useState<{
    isOpen: boolean;
    plan?: any;
  }>({ isOpen: false });

  // Fetch planes
  const { data, isLoading } = useQuery({
    queryKey: ['planes-tratamiento', filters],
    queryFn: () => tratamientosService.getPlanes(filters),
  });

  // Crear plan
  const planMutation = useMutation({
    mutationFn: tratamientosService.createPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planes-tratamiento'] });
      setPlanModal({ isOpen: false });
      toast.success('Plan de tratamiento creado');
    },
  });

  // Actualizar item
  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, data }: any) =>
      tratamientosService.updateItemPlan(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planes-tratamiento'] });
      toast.success('Item actualizado');
    },
  });

  // Descargar presupuesto
  const handleDownloadPresupuesto = async (planId: number) => {
    try {
      const blob = await tratamientosService.downloadPresupuesto(planId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presupuesto_plan_${planId}.pdf`;
      a.click();
      toast.success('Presupuesto descargado');
    } catch (error) {
      toast.error('Error al descargar presupuesto');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Planes de Tratamiento</h1>
          <p className="text-gray-600">Gestiona los tratamientos de los pacientes</p>
        </div>
        <button
          onClick={() => setPlanModal({ isOpen: true })}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Nuevo Plan
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={filters.estado}
              onChange={(e) => setFilters({ ...filters, estado: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="PROPUESTO">Propuesto</option>
              <option value="APROBADO">Aprobado</option>
              <option value="EN_PROGRESO">En Progreso</option>
              <option value="COMPLETADO">Completado</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla */}
      <PlanTable
        planes={data?.results || []}
        isLoading={isLoading}
        onViewDetails={(plan) => setPlanModal({ isOpen: true, plan })}
        onUpdateItem={(itemId, estado) =>
          updateItemMutation.mutate({ itemId, data: { estado } })
        }
        onDownloadPresupuesto={handleDownloadPresupuesto}
      />

      {/* Modal */}
      <PlanModal
        isOpen={planModal.isOpen}
        onClose={() => setPlanModal({ isOpen: false })}
        plan={planModal.plan}
        onSubmit={(data) => planMutation.mutate(data)}
        isLoading={planMutation.isPending}
      />
    </div>
  );
}
```

---

### 3. Tabla de Planes

```typescript
// src/components/admin/tratamientos/PlanTable.tsx
import React from 'react';
import { FileText, Download, Eye } from 'lucide-react';

interface PlanTableProps {
  planes: any[];
  isLoading: boolean;
  onViewDetails: (plan: any) => void;
  onUpdateItem: (itemId: number, estado: string) => void;
  onDownloadPresupuesto: (planId: number) => void;
}

export default function PlanTable({
  planes,
  isLoading,
  onViewDetails,
  onUpdateItem,
  onDownloadPresupuesto,
}: PlanTableProps) {
  if (isLoading) {
    return <div className="text-center py-8">Cargando planes...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Paciente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Odontólogo
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Diagnóstico
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Progreso
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Total
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {planes.map((plan) => {
            const total = plan.items.reduce(
              (sum: number, item: any) => sum + parseFloat(item.precio_acordado),
              0
            );

            return (
              <tr key={plan.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">
                    {plan.paciente.usuario.full_name}
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  Dr. {plan.odontologo.usuario.full_name}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-xs truncate">
                    {plan.diagnostico}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${plan.progreso}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600">{plan.progreso}%</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${getEstadoColor(plan.estado)}`}>
                    {plan.estado.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                  ${total.toFixed(2)}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onViewDetails(plan)}
                      className="text-blue-600 hover:text-blue-800"
                      title="Ver detalles"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => onDownloadPresupuesto(plan.id)}
                      className="text-green-600 hover:text-green-800"
                      title="Descargar presupuesto"
                    >
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function getEstadoColor(estado: string) {
  const colors = {
    PROPUESTO: 'bg-yellow-100 text-yellow-800',
    APROBADO: 'bg-blue-100 text-blue-800',
    EN_PROGRESO: 'bg-purple-100 text-purple-800',
    COMPLETADO: 'bg-green-100 text-green-800',
    CANCELADO: 'bg-red-100 text-red-800',
  };
  return colors[estado] || 'bg-gray-100 text-gray-800';
}
```

---

### 4. Servicio de Tratamientos

```typescript
// src/services/admin/tratamientosService.ts
import api from '@/lib/axios';

export const tratamientosService = {
  // Servicios
  async getServicios(filters: any = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    
    const { data } = await api.get(`/tratamientos/servicios/?${params.toString()}`);
    return data;
  },

  async createServicio(servicioData: any) {
    const { data } = await api.post('/tratamientos/servicios/', servicioData);
    return data;
  },

  async updateServicio(id: number, servicioData: any) {
    const { data } = await api.patch(`/tratamientos/servicios/${id}/`, servicioData);
    return data;
  },

  async deleteServicio(id: number) {
    const { data } = await api.patch(`/tratamientos/servicios/${id}/`, { activo: false });
    return data;
  },

  // Planes de tratamiento
  async getPlanes(filters: any = {}) {
    const params = new URLSearchParams();
    if (filters.paciente) params.append('paciente', filters.paciente);
    if (filters.estado) params.append('estado', filters.estado);
    
    const { data } = await api.get(`/tratamientos/planes-tratamiento/?${params.toString()}`);
    return data;
  },

  async createPlan(planData: any) {
    const { data } = await api.post('/tratamientos/planes-tratamiento/', planData);
    return data;
  },

  async updateItemPlan(itemId: number, itemData: any) {
    const { data } = await api.patch(`/tratamientos/items-plan/${itemId}/`, itemData);
    return data;
  },

  async downloadPresupuesto(planId: number) {
    const { data } = await api.get(
      `/tratamientos/planes-tratamiento/${planId}/presupuesto/?formato=pdf`,
      { responseType: 'blob' }
    );
    return data;
  },

  // Estadísticas
  async getEstadisticasServicios() {
    const { data } = await api.get('/tratamientos/estadisticas/servicios/');
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Crear página Servicios.tsx
- [ ] Crear ServicioTable y ServicioModal
- [ ] Crear página PlanesTratamiento.tsx
- [ ] Crear PlanTable y PlanModal
- [ ] Crear tratamientosService
- [ ] Implementar descarga de presupuestos PDF
- [ ] Barra de progreso del tratamiento
- [ ] Actualización de items completados
- [ ] Vista de detalles expandida

---

**Siguiente:** `06_facturacion_pagos.md`
