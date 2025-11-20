# 👨‍⚕️ Gestión de Pacientes

## 🎯 Objetivo
Crear la interfaz para visualizar, buscar y gestionar los pacientes de la clínica. El administrador podrá ver listados, perfiles detallados e historial resumido de cada paciente.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Listar pacientes** con filtros y búsqueda
2. **Ver perfil detallado** con toda la información
3. **Ver historial resumido** (citas, tratamientos, facturas)
4. **Exportar lista** de pacientes a Excel/PDF
5. **Estadísticas del paciente** (gastos, citas, tratamientos)
6. **Navegación rápida** al historial clínico completo

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar pacientes
GET /api/usuarios/pacientes/?activo=true&search=juan
Response: {
  count: 150,
  results: [
    {
      id: 1,
      usuario: {
        id: 10,
        email: "juan.perez@email.com",
        full_name: "Juan Pérez",
        is_active: true,
        date_joined: "2025-01-15T10:00:00Z"
      },
      telefono: "555-1234",
      direccion: "Av. Principal 123",
      fecha_nacimiento: "1985-05-20",
      tipo_sangre: "O+",
      alergias: "Penicilina",
      edad: 39
    }
  ]
}

// 2. Detalle del paciente
GET /api/usuarios/pacientes/{id}/
Response: { /* datos completos */ }

// 3. Historial de citas
GET /api/agenda/citas/?paciente={id}&ordering=-fecha_hora
Response: {
  count: 25,
  results: [/* citas */]
}

// 4. Planes de tratamiento
GET /api/tratamientos/planes-tratamiento/?paciente={id}
Response: {
  count: 5,
  results: [/* planes */]
}

// 5. Facturas del paciente
GET /api/facturacion/facturas/?paciente={id}
Response: {
  count: 10,
  results: [/* facturas */]
}

// 6. Exportar pacientes
GET /api/reportes/reportes/reporte-pacientes/?formato=excel&activo=true
Response: Archivo Excel descargable

// 7. Estadísticas del paciente
GET /api/usuarios/pacientes/{id}/estadisticas/
Response: {
  total_citas: 25,
  citas_completadas: 20,
  citas_canceladas: 5,
  total_gastado: 5000.00,
  saldo_pendiente: 500.00,
  tratamientos_activos: 1,
  tratamientos_completados: 4
}
```

---

## 💻 Implementación Frontend

### 1. Página de Pacientes

```typescript
// src/pages/admin/Pacientes.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Search, Download, Filter } from 'lucide-react';
import { pacientesService } from '@/services/admin/pacientesService';
import PacienteTable from '@/components/admin/pacientes/PacienteTable';
import PacienteDetailModal from '@/components/admin/pacientes/PacienteDetailModal';
import ExportMenu from '@/components/admin/ExportMenu';

export default function Pacientes() {
  const [selectedPaciente, setSelectedPaciente] = useState(null);
  const [filters, setFilters] = useState({
    activo: 'true',
    search: '',
    edad_min: '',
    edad_max: '',
  });

  // Fetch pacientes
  const { data, isLoading } = useQuery({
    queryKey: ['pacientes', filters],
    queryFn: () => pacientesService.getPacientes(filters),
  });

  const handleViewDetail = (paciente: any) => {
    setSelectedPaciente(paciente);
  };

  const handleExport = async (formato: 'pdf' | 'excel') => {
    const url = await pacientesService.exportPacientes(filters, formato);
    window.open(url, '_blank');
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pacientes</h1>
          <p className="text-gray-600">
            Total: {data?.count || 0} pacientes registrados
          </p>
        </div>
        <div className="flex gap-3">
          <ExportMenu onExport={handleExport} />
          <a
            href="/recepcionista/pacientes/nuevo"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Nuevo Paciente
          </a>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div className="md:col-span-2 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre, email o teléfono..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Estado */}
          <select
            value={filters.activo}
            onChange={(e) => setFilters({ ...filters, activo: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </select>

          {/* Limpiar */}
          <button
            onClick={() => setFilters({ activo: 'true', search: '', edad_min: '', edad_max: '' })}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Limpiar
          </button>
        </div>

        {/* Filtros avanzados */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Edad mínima</label>
            <input
              type="number"
              value={filters.edad_min}
              onChange={(e) => setFilters({ ...filters, edad_min: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="18"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Edad máxima</label>
            <input
              type="number"
              value={filters.edad_max}
              onChange={(e) => setFilters({ ...filters, edad_max: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="65"
            />
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-lg shadow">
        <PacienteTable
          pacientes={data?.results || []}
          isLoading={isLoading}
          onViewDetail={handleViewDetail}
        />
      </div>

      {/* Modal de Detalle */}
      {selectedPaciente && (
        <PacienteDetailModal
          paciente={selectedPaciente}
          onClose={() => setSelectedPaciente(null)}
        />
      )}
    </div>
  );
}
```

---

### 2. Tabla de Pacientes

```typescript
// src/components/admin/pacientes/PacienteTable.tsx
import React from 'react';
import { Eye, Phone, Mail, Calendar } from 'lucide-react';
import { formatDate, calculateAge } from '@/lib/utils';

interface Paciente {
  id: number;
  usuario: {
    full_name: string;
    email: string;
    is_active: boolean;
  };
  telefono: string;
  fecha_nacimiento: string;
  tipo_sangre: string;
}

interface PacienteTableProps {
  pacientes: Paciente[];
  isLoading: boolean;
  onViewDetail: (paciente: Paciente) => void;
}

export default function PacienteTable({ pacientes, isLoading, onViewDetail }: PacienteTableProps) {
  if (isLoading) {
    return <TableSkeleton />;
  }

  if (pacientes.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No se encontraron pacientes</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Paciente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Contacto
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Edad
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Tipo Sangre
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Estado
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {pacientes.map((paciente) => (
            <tr key={paciente.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                    <span className="text-white font-medium">
                      {paciente.usuario.full_name.charAt(0)}
                    </span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">
                      {paciente.usuario.full_name}
                    </p>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="space-y-1">
                  <div className="flex items-center text-sm text-gray-600">
                    <Mail className="w-4 h-4 mr-2" />
                    {paciente.usuario.email}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Phone className="w-4 h-4 mr-2" />
                    {paciente.telefono || 'No registrado'}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {calculateAge(paciente.fecha_nacimiento)} años
              </td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                  {paciente.tipo_sangre || 'N/A'}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  paciente.usuario.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {paciente.usuario.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-6 py-4 text-right">
                <button
                  onClick={() => onViewDetail(paciente)}
                  className="inline-flex items-center gap-1 px-3 py-1 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  <Eye className="w-4 h-4" />
                  Ver Detalle
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="p-6 space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="h-20 bg-gray-100 rounded animate-pulse" />
      ))}
    </div>
  );
}
```

---

### 3. Modal de Detalle del Paciente

```typescript
// src/components/admin/pacientes/PacienteDetailModal.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, Calendar, DollarSign, FileText, Activity } from 'lucide-react';
import { pacientesService } from '@/services/admin/pacientesService';
import Modal from '@/components/ui/Modal';
import { formatDate, formatCurrency } from '@/lib/utils';

interface PacienteDetailModalProps {
  paciente: any;
  onClose: () => void;
}

export default function PacienteDetailModal({ paciente, onClose }: PacienteDetailModalProps) {
  // Fetch estadísticas
  const { data: estadisticas } = useQuery({
    queryKey: ['paciente-estadisticas', paciente.id],
    queryFn: () => pacientesService.getEstadisticas(paciente.id),
  });

  // Fetch últimas citas
  const { data: citas } = useQuery({
    queryKey: ['paciente-citas', paciente.id],
    queryFn: () => pacientesService.getCitas(paciente.id, 5),
  });

  // Fetch facturas pendientes
  const { data: facturas } = useQuery({
    queryKey: ['paciente-facturas', paciente.id],
    queryFn: () => pacientesService.getFacturas(paciente.id, 5),
  });

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={paciente.usuario.full_name}
      size="xl"
    >
      <div className="space-y-6">
        {/* Información Personal */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Información Personal</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Email:</span>
              <p className="font-medium">{paciente.usuario.email}</p>
            </div>
            <div>
              <span className="text-gray-600">Teléfono:</span>
              <p className="font-medium">{paciente.telefono || 'No registrado'}</p>
            </div>
            <div>
              <span className="text-gray-600">Fecha Nacimiento:</span>
              <p className="font-medium">{formatDate(paciente.fecha_nacimiento)}</p>
            </div>
            <div>
              <span className="text-gray-600">Tipo Sangre:</span>
              <p className="font-medium">{paciente.tipo_sangre || 'No registrado'}</p>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">Dirección:</span>
              <p className="font-medium">{paciente.direccion || 'No registrado'}</p>
            </div>
            {paciente.alergias && (
              <div className="col-span-2">
                <span className="text-gray-600">Alergias:</span>
                <p className="font-medium text-red-600">{paciente.alergias}</p>
              </div>
            )}
          </div>
        </div>

        {/* Estadísticas */}
        {estadisticas && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Estadísticas</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <Calendar className="w-8 h-8 text-blue-600 mb-2" />
                <p className="text-2xl font-bold text-blue-600">
                  {estadisticas.total_citas}
                </p>
                <p className="text-sm text-gray-600">Citas Totales</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <Activity className="w-8 h-8 text-green-600 mb-2" />
                <p className="text-2xl font-bold text-green-600">
                  {estadisticas.tratamientos_activos}
                </p>
                <p className="text-sm text-gray-600">Tratamientos Activos</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <DollarSign className="w-8 h-8 text-purple-600 mb-2" />
                <p className="text-2xl font-bold text-purple-600">
                  {formatCurrency(estadisticas.total_gastado)}
                </p>
                <p className="text-sm text-gray-600">Total Gastado</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <FileText className="w-8 h-8 text-orange-600 mb-2" />
                <p className="text-2xl font-bold text-orange-600">
                  {formatCurrency(estadisticas.saldo_pendiente)}
                </p>
                <p className="text-sm text-gray-600">Saldo Pendiente</p>
              </div>
            </div>
          </div>
        )}

        {/* Últimas Citas */}
        {citas && citas.results.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Últimas Citas</h3>
            <div className="space-y-2">
              {citas.results.map((cita: any) => (
                <div key={cita.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{cita.motivo}</p>
                    <p className="text-sm text-gray-600">
                      {formatDate(cita.fecha_hora)} - Dr. {cita.odontologo.usuario.full_name}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    cita.estado === 'COMPLETADA' ? 'bg-green-100 text-green-800' :
                    cita.estado === 'CONFIRMADA' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {cita.estado}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Facturas Pendientes */}
        {facturas && facturas.results.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Facturas Recientes</h3>
            <div className="space-y-2">
              {facturas.results.map((factura: any) => (
                <div key={factura.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Factura #{factura.numero_factura}</p>
                    <p className="text-sm text-gray-600">{formatDate(factura.fecha_emision)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatCurrency(factura.monto_total)}</p>
                    <span className={`text-xs ${
                      factura.estado === 'PAGADA' ? 'text-green-600' : 'text-orange-600'
                    }`}>
                      {factura.estado}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Botón Historial Completo */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cerrar
          </button>
          <a
            href={`/odontologo/historial-clinico/${paciente.id}`}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Ver Historial Completo
          </a>
        </div>
      </div>
    </Modal>
  );
}
```

---

### 4. Servicio de Pacientes

```typescript
// src/services/admin/pacientesService.ts
import api from '@/lib/axios';

export const pacientesService = {
  // Listar pacientes
  async getPacientes(filters: any = {}) {
    const params = new URLSearchParams();
    
    if (filters.activo) params.append('activo', filters.activo);
    if (filters.search) params.append('search', filters.search);
    if (filters.edad_min) params.append('edad_min', filters.edad_min);
    if (filters.edad_max) params.append('edad_max', filters.edad_max);
    
    const { data } = await api.get(`/usuarios/pacientes/?${params.toString()}`);
    return data;
  },

  // Obtener estadísticas
  async getEstadisticas(pacienteId: number) {
    const { data } = await api.get(`/usuarios/pacientes/${pacienteId}/estadisticas/`);
    return data;
  },

  // Obtener citas
  async getCitas(pacienteId: number, limit: number = 5) {
    const { data } = await api.get(`/agenda/citas/`, {
      params: {
        paciente: pacienteId,
        ordering: '-fecha_hora',
        page_size: limit
      }
    });
    return data;
  },

  // Obtener facturas
  async getFacturas(pacienteId: number, limit: number = 5) {
    const { data } = await api.get(`/facturacion/facturas/`, {
      params: {
        paciente: pacienteId,
        ordering: '-fecha_emision',
        page_size: limit
      }
    });
    return data;
  },

  // Exportar pacientes
  async exportPacientes(filters: any, formato: 'pdf' | 'excel') {
    const params = new URLSearchParams();
    
    if (filters.activo) params.append('activo', filters.activo);
    params.append('formato', formato);
    
    const { data } = await api.get(
      `/reportes/reportes/reporte-pacientes/?${params.toString()}`,
      { responseType: 'blob' }
    );
    
    return URL.createObjectURL(data);
  },
};
```

---

## ✅ Checklist de Implementación

- [ ] Crear página Pacientes.tsx
- [ ] Crear componente PacienteTable
- [ ] Crear componente PacienteDetailModal
- [ ] Crear pacientesService
- [ ] Implementar filtros avanzados
- [ ] Implementar búsqueda
- [ ] Implementar paginación
- [ ] Vista de estadísticas
- [ ] Exportación PDF/Excel
- [ ] Link a historial clínico
- [ ] Vista responsive

---

**Siguiente:** `04_agenda_citas.md`
