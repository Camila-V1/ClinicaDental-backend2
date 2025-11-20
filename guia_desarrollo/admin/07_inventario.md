# 📦 Inventario

## 🎯 Objetivo
Gestionar el inventario de insumos odontológicos, control de stock y movimientos.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **CRUD de insumos**: Crear, editar, ver, desactivar
2. **Control de stock**: Stock actual, mínimo, máximo
3. **Movimientos**: Entrada, Salida, Ajuste
4. **Alertas** de stock bajo
5. **Historial** de movimientos
6. **Exportar** inventario a Excel

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar insumos
GET /api/inventario/insumos/?stock_bajo=true
Response: {
  count: 50,
  results: [
    {
      id: 1,
      nombre: "Guantes de látex",
      categoria: "Material desechable",
      unidad_medida: "CAJA",
      stock_actual: 5,
      stock_minimo: 10,
      stock_maximo: 50,
      precio_unitario: 25.00,
      activo: true,
      alerta_stock: true
    }
  ]
}

// 2. Crear insumo
POST /api/inventario/insumos/
Body: {
  nombre: "Anestesia Lidocaína",
  categoria: "Medicamentos",
  unidad_medida: "UNIDAD",
  stock_minimo: 20,
  stock_maximo: 100,
  precio_unitario: 15.50
}

// 3. Listar movimientos
GET /api/inventario/movimientos/?tipo=SALIDA&fecha_desde=2025-11-01
Response: {
  count: 150,
  results: [
    {
      id: 1,
      insumo: { id: 1, nombre: "Guantes de látex" },
      tipo_movimiento: "SALIDA",
      cantidad: 2,
      motivo: "Uso en procedimiento",
      usuario: { id: 1, full_name: "Dr. Juan Pérez" },
      fecha_movimiento: "2025-11-20T10:00:00Z"
    }
  ]
}

// 4. Registrar movimiento
POST /api/inventario/movimientos/
Body: {
  insumo: 1,
  tipo_movimiento: "ENTRADA",
  cantidad: 10,
  motivo: "Compra nueva"
}

// 5. Alertas de stock bajo
GET /api/inventario/alertas-stock/
Response: {
  insumos_bajo_stock: [
    {
      id: 1,
      nombre: "Guantes de látex",
      stock_actual: 5,
      stock_minimo: 10,
      diferencia: -5
    }
  ]
}

// 6. Exportar inventario
GET /api/reportes/reporte-inventario/?formato=excel
Response: Binary Excel file
```

---

## 💻 Implementación Frontend

### 1. Página de Inventario

```typescript
// src/pages/admin/Inventario.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventarioService } from '@/services/admin/inventarioService';
import InsumoTable from '@/components/admin/inventario/InsumoTable';
import InsumoModal from '@/components/admin/inventario/InsumoModal';
import MovimientoModal from '@/components/admin/inventario/MovimientoModal';
import { AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function Inventario() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    search: '',
    stock_bajo: false,
  });
  const [insumoModal, setInsumoModal] = useState<{
    isOpen: boolean;
    insumo?: any;
  }>({ isOpen: false });
  const [movimientoModal, setMovimientoModal] = useState<{
    isOpen: boolean;
    insumo?: any;
  }>({ isOpen: false });

  // Fetch insumos
  const { data, isLoading } = useQuery({
    queryKey: ['insumos', filters],
    queryFn: () => inventarioService.getInsumos(filters),
  });

  // Fetch alertas
  const { data: alertas } = useQuery({
    queryKey: ['alertas-stock'],
    queryFn: inventarioService.getAlertasStock,
  });

  // Crear/Actualizar insumo
  const insumoMutation = useMutation({
    mutationFn: (data: any) =>
      insumoModal.insumo
        ? inventarioService.updateInsumo(insumoModal.insumo.id, data)
        : inventarioService.createInsumo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insumos'] });
      setInsumoModal({ isOpen: false });
      toast.success(insumoModal.insumo ? 'Insumo actualizado' : 'Insumo creado');
    },
  });

  // Registrar movimiento
  const movimientoMutation = useMutation({
    mutationFn: inventarioService.createMovimiento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insumos'] });
      queryClient.invalidateQueries({ queryKey: ['alertas-stock'] });
      setMovimientoModal({ isOpen: false });
      toast.success('Movimiento registrado');
    },
  });

  // Exportar inventario
  const handleExport = async () => {
    try {
      const blob = await inventarioService.exportarInventario();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `inventario_${new Date().toISOString().split('T')[0]}.xlsx`;
      a.click();
      toast.success('Inventario exportado');
    } catch (error) {
      toast.error('Error al exportar');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inventario</h1>
          <p className="text-gray-600">Gestiona los insumos odontológicos</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExport}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            📊 Exportar Excel
          </button>
          <button
            onClick={() => setInsumoModal({ isOpen: true })}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + Nuevo Insumo
          </button>
        </div>
      </div>

      {/* Alertas */}
      {alertas && alertas.insumos_bajo_stock.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <h3 className="font-semibold text-yellow-800">
              {alertas.insumos_bajo_stock.length} insumos con stock bajo
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {alertas.insumos_bajo_stock.slice(0, 5).map((insumo: any) => (
              <span key={insumo.id} className="text-sm text-yellow-700">
                {insumo.nombre} (quedan {insumo.stock_actual})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            placeholder="Buscar insumos..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.stock_bajo}
              onChange={(e) => setFilters({ ...filters, stock_bajo: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Solo stock bajo</span>
          </label>
        </div>
      </div>

      {/* Tabla */}
      <InsumoTable
        insumos={data?.results || []}
        isLoading={isLoading}
        onEdit={(insumo) => setInsumoModal({ isOpen: true, insumo })}
        onRegistrarMovimiento={(insumo) => setMovimientoModal({ isOpen: true, insumo })}
      />

      {/* Modales */}
      <InsumoModal
        isOpen={insumoModal.isOpen}
        onClose={() => setInsumoModal({ isOpen: false })}
        insumo={insumoModal.insumo}
        onSubmit={(data) => insumoMutation.mutate(data)}
        isLoading={insumoMutation.isPending}
      />

      <MovimientoModal
        isOpen={movimientoModal.isOpen}
        onClose={() => setMovimientoModal({ isOpen: false })}
        insumo={movimientoModal.insumo}
        onSubmit={(data) => movimientoMutation.mutate(data)}
        isLoading={movimientoMutation.isPending}
      />
    </div>
  );
}
```

---

### 2. Tabla de Insumos

```typescript
// src/components/admin/inventario/InsumoTable.tsx
import React from 'react';
import { Edit2, Package, AlertCircle } from 'lucide-react';

interface InsumoTableProps {
  insumos: any[];
  isLoading: boolean;
  onEdit: (insumo: any) => void;
  onRegistrarMovimiento: (insumo: any) => void;
}

export default function InsumoTable({
  insumos,
  isLoading,
  onEdit,
  onRegistrarMovimiento,
}: InsumoTableProps) {
  if (isLoading) {
    return <div className="text-center py-8">Cargando insumos...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Nombre
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Categoría
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Stock Actual
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Stock Mín/Máx
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Unidad
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Precio Unit.
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {insumos.map((insumo) => {
            const stockBajo = insumo.stock_actual <= insumo.stock_minimo;

            return (
              <tr key={insumo.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    {stockBajo && <AlertCircle className="w-4 h-4 text-yellow-500" />}
                    <span className="text-sm font-medium text-gray-900">
                      {insumo.nombre}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {insumo.categoria}
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`text-sm font-semibold ${
                      stockBajo ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {insumo.stock_actual}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {insumo.stock_minimo} / {insumo.stock_maximo}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {insumo.unidad_medida}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  ${insumo.precio_unitario.toFixed(2)}
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      insumo.activo
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {insumo.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onEdit(insumo)}
                      className="text-blue-600 hover:text-blue-800"
                      title="Editar"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => onRegistrarMovimiento(insumo)}
                      className="text-green-600 hover:text-green-800"
                      title="Registrar movimiento"
                    >
                      <Package className="w-5 h-5" />
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
```

---

### 3. Modal de Movimiento

```typescript
// src/components/admin/inventario/MovimientoModal.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Modal from '@/components/ui/Modal';

const movimientoSchema = z.object({
  insumo: z.number(),
  tipo_movimiento: z.enum(['ENTRADA', 'SALIDA', 'AJUSTE']),
  cantidad: z.number().min(1, 'La cantidad debe ser mayor a 0'),
  motivo: z.string().min(3, 'El motivo es requerido'),
});

type MovimientoFormData = z.infer<typeof movimientoSchema>;

interface MovimientoModalProps {
  isOpen: boolean;
  onClose: () => void;
  insumo?: any;
  onSubmit: (data: MovimientoFormData) => void;
  isLoading: boolean;
}

export default function MovimientoModal({
  isOpen,
  onClose,
  insumo,
  onSubmit,
  isLoading,
}: MovimientoModalProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<MovimientoFormData>({
    resolver: zodResolver(movimientoSchema),
    defaultValues: {
      insumo: insumo?.id,
      tipo_movimiento: 'ENTRADA',
      cantidad: 1,
    },
  });

  const tipoMovimiento = watch('tipo_movimiento');
  const cantidad = watch('cantidad');

  const nuevoStock = insumo
    ? tipoMovimiento === 'ENTRADA'
      ? insumo.stock_actual + cantidad
      : tipoMovimiento === 'SALIDA'
      ? insumo.stock_actual - cantidad
      : cantidad
    : 0;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Registrar Movimiento"
    >
      {insumo && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Insumo:</span> {insumo.nombre}
          </p>
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Stock actual:</span>{' '}
            <span className="font-bold">{insumo.stock_actual} {insumo.unidad_medida}</span>
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <input type="hidden" {...register('insumo', { valueAsNumber: true })} />

        {/* Tipo de Movimiento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Movimiento *
          </label>
          <select
            {...register('tipo_movimiento')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="ENTRADA">Entrada (Agregar stock)</option>
            <option value="SALIDA">Salida (Reducir stock)</option>
            <option value="AJUSTE">Ajuste (Establecer stock)</option>
          </select>
        </div>

        {/* Cantidad */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {tipoMovimiento === 'AJUSTE' ? 'Nuevo Stock *' : 'Cantidad *'}
          </label>
          <input
            type="number"
            {...register('cantidad', { valueAsNumber: true })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            min="1"
          />
          {errors.cantidad && (
            <p className="text-red-500 text-sm mt-1">{errors.cantidad.message}</p>
          )}
          {tipoMovimiento !== 'AJUSTE' && (
            <p className="text-sm text-gray-600 mt-1">
              Stock resultante: <span className="font-semibold">{nuevoStock}</span>
            </p>
          )}
        </div>

        {/* Motivo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Motivo *
          </label>
          <textarea
            {...register('motivo')}
            rows={3}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ej: Compra nueva, Uso en procedimiento, Corrección de inventario..."
          />
          {errors.motivo && (
            <p className="text-red-500 text-sm mt-1">{errors.motivo.message}</p>
          )}
        </div>

        {/* Alerta si stock resultante es negativo */}
        {tipoMovimiento === 'SALIDA' && nuevoStock < 0 && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">
              ⚠️ El stock resultante sería negativo
            </p>
          </div>
        )}

        {/* Botones */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading || (tipoMovimiento === 'SALIDA' && nuevoStock < 0)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Registrando...' : 'Registrar Movimiento'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
```

---

### 4. Servicio de Inventario

```typescript
// src/services/admin/inventarioService.ts
import api from '@/lib/axios';

export const inventarioService = {
  // Insumos
  async getInsumos(filters: any = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    if (filters.stock_bajo) params.append('stock_bajo', 'true');
    
    const { data } = await api.get(`/inventario/insumos/?${params.toString()}`);
    return data;
  },

  async createInsumo(insumoData: any) {
    const { data } = await api.post('/inventario/insumos/', insumoData);
    return data;
  },

  async updateInsumo(id: number, insumoData: any) {
    const { data } = await api.patch(`/inventario/insumos/${id}/`, insumoData);
    return data;
  },

  // Movimientos
  async createMovimiento(movimientoData: any) {
    const { data } = await api.post('/inventario/movimientos/', movimientoData);
    return data;
  },

  // Alertas
  async getAlertasStock() {
    const { data } = await api.get('/inventario/alertas-stock/');
    return data;
  },

  // Exportar
  async exportarInventario() {
    const { data } = await api.get('/reportes/reporte-inventario/?formato=excel', {
      responseType: 'blob',
    });
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Crear página Inventario.tsx
- [ ] Crear InsumoTable
- [ ] Crear InsumoModal y MovimientoModal
- [ ] Crear inventarioService
- [ ] Alertas de stock bajo
- [ ] Exportación a Excel
- [ ] Historial de movimientos
- [ ] Validación de stock negativo

---

**Siguiente:** `08_reportes_estadisticas.md`
