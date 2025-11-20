# 📜 Bitácora de Auditoría

## 🎯 Objetivo
Visualizar el registro completo de acciones realizadas en el sistema para auditoría y trazabilidad.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Listado de acciones** con filtros avanzados
2. **Tipos de acción**: CREAR, EDITAR, ELIMINAR, LOGIN, LOGOUT, EXPORTAR, IMPORTAR, ACCESO, ERROR
3. **Detalles JSON** de cada acción
4. **Filtrar por**: Usuario, tipo de acción, modelo afectado, fechas
5. **Búsqueda** por IP, user agent, detalles
6. **Estadísticas** de actividad
7. **Exportar** bitácora a Excel

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar acciones
GET /api/reportes/bitacora/?tipo_accion=CREAR&fecha_desde=2025-11-01&usuario=5
Response: {
  count: 500,
  results: [
    {
      id: 1,
      usuario: {
        id: 5,
        full_name: "Dr. Juan Pérez",
        email: "juan@clinica.com"
      },
      tipo_accion: "CREAR",
      modelo: "Paciente",
      objeto_id: 10,
      detalles: {
        nombre: "María García",
        email: "maria@example.com"
      },
      ip_address: "192.168.1.100",
      user_agent: "Mozilla/5.0...",
      fecha: "2025-11-20T14:30:00Z"
    }
  ]
}

// 2. Detalle de acción
GET /api/reportes/bitacora/{id}/
Response: {
  id: 1,
  usuario: { ... },
  tipo_accion: "EDITAR",
  modelo: "Cita",
  objeto_id: 25,
  detalles: {
    campo_modificado: "estado",
    valor_anterior: "PENDIENTE",
    valor_nuevo: "CONFIRMADA"
  },
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  fecha: "2025-11-20T14:30:00Z"
}

// 3. Estadísticas de bitácora
GET /api/reportes/bitacora/estadisticas/?periodo=mensual
Response: {
  total_acciones: 1500,
  acciones_por_tipo: {
    CREAR: 450,
    EDITAR: 600,
    ELIMINAR: 50,
    LOGIN: 300,
    LOGOUT: 100
  },
  usuarios_mas_activos: [
    { usuario: "Dr. Juan Pérez", acciones: 450 },
    { usuario: "Dra. Ana López", acciones: 380 }
  ],
  modelos_mas_modificados: [
    { modelo: "Cita", acciones: 600 },
    { modelo: "Paciente", acciones: 300 }
  ]
}

// 4. Exportar bitácora
GET /api/reportes/bitacora/exportar/?formato=excel&fecha_desde=2025-11-01
Response: Binary Excel file
```

---

## 💻 Implementación Frontend

### 1. Página de Bitácora

```typescript
// src/pages/admin/Bitacora.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { bitacoraService } from '@/services/admin/bitacoraService';
import BitacoraTable from '@/components/admin/bitacora/BitacoraTable';
import BitacoraDetailModal from '@/components/admin/bitacora/BitacoraDetailModal';
import { Download } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function Bitacora() {
  const [filters, setFilters] = useState({
    tipo_accion: '',
    modelo: '',
    usuario: '',
    fecha_desde: '',
    fecha_hasta: '',
    search: '',
  });
  const [detailModal, setDetailModal] = useState<{
    isOpen: boolean;
    accion?: any;
  }>({ isOpen: false });
  const [page, setPage] = useState(1);

  // Fetch acciones
  const { data, isLoading } = useQuery({
    queryKey: ['bitacora', filters, page],
    queryFn: () => bitacoraService.getAcciones({ ...filters, page }),
  });

  // Fetch estadísticas
  const { data: estadisticas } = useQuery({
    queryKey: ['bitacora-estadisticas'],
    queryFn: () => bitacoraService.getEstadisticas({ periodo: 'mensual' }),
  });

  // Exportar bitácora
  const handleExport = async () => {
    try {
      const blob = await bitacoraService.exportarBitacora({
        ...filters,
        formato: 'excel',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bitacora_${new Date().toISOString().split('T')[0]}.xlsx`;
      a.click();
      toast.success('Bitácora exportada');
    } catch (error) {
      toast.error('Error al exportar');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bitácora de Auditoría</h1>
          <p className="text-gray-600">Registro completo de acciones del sistema</p>
        </div>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          <Download className="w-5 h-5" />
          Exportar Excel
        </button>
      </div>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Total Acciones</p>
            <p className="text-2xl font-bold text-gray-900">{estadisticas.total_acciones}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Creaciones</p>
            <p className="text-2xl font-bold text-green-600">
              {estadisticas.acciones_por_tipo.CREAR}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Ediciones</p>
            <p className="text-2xl font-bold text-blue-600">
              {estadisticas.acciones_por_tipo.EDITAR}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Eliminaciones</p>
            <p className="text-2xl font-bold text-red-600">
              {estadisticas.acciones_por_tipo.ELIMINAR}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Inicios de Sesión</p>
            <p className="text-2xl font-bold text-purple-600">
              {estadisticas.acciones_por_tipo.LOGIN}
            </p>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Acción
            </label>
            <select
              value={filters.tipo_accion}
              onChange={(e) => setFilters({ ...filters, tipo_accion: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas</option>
              <option value="CREAR">Crear</option>
              <option value="EDITAR">Editar</option>
              <option value="ELIMINAR">Eliminar</option>
              <option value="LOGIN">Login</option>
              <option value="LOGOUT">Logout</option>
              <option value="EXPORTAR">Exportar</option>
              <option value="ACCESO">Acceso</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Modelo
            </label>
            <select
              value={filters.modelo}
              onChange={(e) => setFilters({ ...filters, modelo: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="Paciente">Paciente</option>
              <option value="Cita">Cita</option>
              <option value="PlanTratamiento">Plan de Tratamiento</option>
              <option value="Factura">Factura</option>
              <option value="Insumo">Insumo</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder="IP, detalles..."
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Desde
            </label>
            <input
              type="date"
              value={filters.fecha_desde}
              onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Hasta
            </label>
            <input
              type="date"
              value={filters.fecha_hasta}
              onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Tabla */}
      <BitacoraTable
        acciones={data?.results || []}
        isLoading={isLoading}
        onViewDetail={(accion) => setDetailModal({ isOpen: true, accion })}
      />

      {/* Paginación */}
      {data && data.count > 20 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border rounded-lg disabled:opacity-50"
          >
            Anterior
          </button>
          <span className="px-4 py-2">
            Página {page} de {Math.ceil(data.count / 20)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(data.count / 20)}
            className="px-4 py-2 border rounded-lg disabled:opacity-50"
          >
            Siguiente
          </button>
        </div>
      )}

      {/* Modal de detalle */}
      <BitacoraDetailModal
        isOpen={detailModal.isOpen}
        onClose={() => setDetailModal({ isOpen: false })}
        accion={detailModal.accion}
      />
    </div>
  );
}
```

---

### 2. Tabla de Bitácora

```typescript
// src/components/admin/bitacora/BitacoraTable.tsx
import React from 'react';
import { Eye } from 'lucide-react';

interface BitacoraTableProps {
  acciones: any[];
  isLoading: boolean;
  onViewDetail: (accion: any) => void;
}

export default function BitacoraTable({
  acciones,
  isLoading,
  onViewDetail,
}: BitacoraTableProps) {
  if (isLoading) {
    return <div className="text-center py-8">Cargando bitácora...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fecha/Hora
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Usuario
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acción
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Modelo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                ID Objeto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                IP Address
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {acciones.map((accion) => (
              <tr key={accion.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {new Date(accion.fecha).toLocaleDateString('es-ES')}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(accion.fecha).toLocaleTimeString('es-ES')}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {accion.usuario?.full_name || 'Sistema'}
                  </div>
                  <div className="text-xs text-gray-500">{accion.usuario?.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${getTipoAccionColor(accion.tipo_accion)}`}>
                    {accion.tipo_accion}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {accion.modelo || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {accion.objeto_id || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                  {accion.ip_address}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => onViewDetail(accion)}
                    className="text-blue-600 hover:text-blue-800"
                    title="Ver detalles"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getTipoAccionColor(tipo: string) {
  const colors = {
    CREAR: 'bg-green-100 text-green-800',
    EDITAR: 'bg-blue-100 text-blue-800',
    ELIMINAR: 'bg-red-100 text-red-800',
    LOGIN: 'bg-purple-100 text-purple-800',
    LOGOUT: 'bg-gray-100 text-gray-800',
    EXPORTAR: 'bg-yellow-100 text-yellow-800',
    ACCESO: 'bg-indigo-100 text-indigo-800',
    ERROR: 'bg-red-100 text-red-800',
  };
  return colors[tipo] || 'bg-gray-100 text-gray-800';
}
```

---

### 3. Modal de Detalle

```typescript
// src/components/admin/bitacora/BitacoraDetailModal.tsx
import React from 'react';
import Modal from '@/components/ui/Modal';

interface BitacoraDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  accion?: any;
}

export default function BitacoraDetailModal({
  isOpen,
  onClose,
  accion,
}: BitacoraDetailModalProps) {
  if (!accion) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Detalles de la Acción">
      <div className="space-y-4">
        {/* Información básica */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Usuario</label>
            <p className="mt-1 text-sm text-gray-900">
              {accion.usuario?.full_name || 'Sistema'}
            </p>
            <p className="text-xs text-gray-500">{accion.usuario?.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Fecha/Hora</label>
            <p className="mt-1 text-sm text-gray-900">
              {new Date(accion.fecha).toLocaleString('es-ES')}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Tipo de Acción</label>
            <p className="mt-1 text-sm text-gray-900">{accion.tipo_accion}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Modelo</label>
            <p className="mt-1 text-sm text-gray-900">{accion.modelo || '-'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">ID Objeto</label>
            <p className="mt-1 text-sm text-gray-900">{accion.objeto_id || '-'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">IP Address</label>
            <p className="mt-1 text-sm font-mono text-gray-900">{accion.ip_address}</p>
          </div>
        </div>

        {/* User Agent */}
        <div>
          <label className="block text-sm font-medium text-gray-700">User Agent</label>
          <p className="mt-1 text-xs text-gray-600 break-all">{accion.user_agent}</p>
        </div>

        {/* Detalles JSON */}
        {accion.detalles && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Detalles de la Acción
            </label>
            <pre className="p-3 bg-gray-50 border rounded-lg text-xs overflow-auto max-h-96">
              {JSON.stringify(accion.detalles, null, 2)}
            </pre>
          </div>
        )}

        {/* Botón cerrar */}
        <div className="flex justify-end pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
}
```

---

### 4. Servicio de Bitácora

```typescript
// src/services/admin/bitacoraService.ts
import api from '@/lib/axios';

export const bitacoraService = {
  // Listar acciones
  async getAcciones(params: any = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.tipo_accion) queryParams.append('tipo_accion', params.tipo_accion);
    if (params.modelo) queryParams.append('modelo', params.modelo);
    if (params.usuario) queryParams.append('usuario', params.usuario);
    if (params.fecha_desde) queryParams.append('fecha_desde', params.fecha_desde);
    if (params.fecha_hasta) queryParams.append('fecha_hasta', params.fecha_hasta);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page.toString());

    const { data } = await api.get(`/reportes/bitacora/?${queryParams.toString()}`);
    return data;
  },

  // Detalle de acción
  async getAccionDetail(id: number) {
    const { data } = await api.get(`/reportes/bitacora/${id}/`);
    return data;
  },

  // Estadísticas
  async getEstadisticas(params: any = {}) {
    const { data } = await api.get('/reportes/bitacora/estadisticas/', { params });
    return data;
  },

  // Exportar
  async exportarBitacora(params: any = {}) {
    const { data } = await api.get('/reportes/bitacora/exportar/', {
      params,
      responseType: 'blob',
    });
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Crear página Bitacora.tsx
- [ ] Crear BitacoraTable
- [ ] Crear BitacoraDetailModal
- [ ] Crear bitacoraService
- [ ] Filtros avanzados (tipo, modelo, usuario, fecha)
- [ ] Búsqueda por IP y detalles
- [ ] Estadísticas de actividad
- [ ] Paginación
- [ ] Exportación a Excel
- [ ] Vista de detalles JSON

---

**Siguiente:** `10_configuracion_clinica.md`
