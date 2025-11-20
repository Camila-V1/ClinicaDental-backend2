# 💰 Facturación y Pagos

## 🎯 Objetivo
Gestionar facturas, pagos y seguimiento financiero de la clínica.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Generar facturas** automáticamente
2. **Registrar pagos** (parciales o totales)
3. **Métodos de pago**: Efectivo, Tarjeta, Transferencia
4. **Estados**: Pendiente, Pagada Parcial, Pagada Total, Vencida
5. **Reportes financieros** (ingresos diarios, semanales, mensuales)
6. **Cuentas por cobrar**
7. **Exportar** facturas a PDF

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar facturas
GET /api/facturacion/facturas/?estado=PENDIENTE&fecha_desde=2025-11-01
Response: {
  count: 15,
  results: [
    {
      id: 1,
      numero_factura: "FAC-2025-001",
      paciente: { id: 5, usuario: { full_name: "María García" } },
      plan_tratamiento: {
        id: 1,
        diagnostico: "Ortodoncia"
      },
      subtotal: 5000.00,
      impuesto: 0.00,
      total: 5000.00,
      monto_pagado: 2000.00,
      saldo_pendiente: 3000.00,
      estado: "PAGADA_PARCIAL",
      fecha_emision: "2025-11-01",
      fecha_vencimiento: "2025-12-01",
      pagos: [
        {
          id: 1,
          monto: 2000.00,
          metodo_pago: "EFECTIVO",
          fecha_pago: "2025-11-01",
          referencia: "PAG-001"
        }
      ]
    }
  ]
}

// 2. Crear factura
POST /api/facturacion/facturas/
Body: {
  paciente: 5,
  plan_tratamiento: 1,
  fecha_vencimiento: "2025-12-01",
  notas: "Pago en cuotas acordado"
}

// 3. Registrar pago
POST /api/facturacion/pagos/
Body: {
  factura: 1,
  monto: 1500.00,
  metodo_pago: "TARJETA",
  referencia: "TXN-123456",
  notas: "Segunda cuota"
}

// 4. Actualizar factura
PATCH /api/facturacion/facturas/{id}/
Body: { fecha_vencimiento: "2025-12-15" }

// 5. Descargar factura PDF
GET /api/facturacion/facturas/{id}/pdf/
Response: Binary PDF file

// 6. Estadísticas financieras
GET /api/facturacion/estadisticas/?periodo=mensual
Response: {
  ingresos_totales: 45000.00,
  facturas_pagadas: 25,
  facturas_pendientes: 10,
  cuentas_por_cobrar: 15000.00,
  ingresos_por_metodo: {
    EFECTIVO: 20000.00,
    TARJETA: 15000.00,
    TRANSFERENCIA: 10000.00
  }
}

// 7. Cuentas por cobrar
GET /api/facturacion/cuentas-por-cobrar/
Response: {
  total_por_cobrar: 25000.00,
  facturas: [
    {
      factura: "FAC-2025-001",
      paciente: "María García",
      saldo: 3000.00,
      dias_vencidos: 5
    }
  ]
}
```

---

## 💻 Implementación Frontend

### 1. Página de Facturas

```typescript
// src/pages/admin/Facturas.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { facturacionService } from '@/services/admin/facturacionService';
import FacturaTable from '@/components/admin/facturacion/FacturaTable';
import FacturaModal from '@/components/admin/facturacion/FacturaModal';
import PagoModal from '@/components/admin/facturacion/PagoModal';
import { toast } from 'react-hot-toast';

export default function Facturas() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    estado: '',
    fecha_desde: '',
    fecha_hasta: '',
  });
  const [facturaModal, setFacturaModal] = useState<{
    isOpen: boolean;
    factura?: any;
  }>({ isOpen: false });
  const [pagoModal, setPagoModal] = useState<{
    isOpen: boolean;
    factura?: any;
  }>({ isOpen: false });

  // Fetch facturas
  const { data, isLoading } = useQuery({
    queryKey: ['facturas', filters],
    queryFn: () => facturacionService.getFacturas(filters),
  });

  // Fetch estadísticas
  const { data: estadisticas } = useQuery({
    queryKey: ['estadisticas-facturacion'],
    queryFn: () => facturacionService.getEstadisticas({ periodo: 'mensual' }),
  });

  // Crear factura
  const facturaMutation = useMutation({
    mutationFn: facturacionService.createFactura,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
      setFacturaModal({ isOpen: false });
      toast.success('Factura creada');
    },
  });

  // Registrar pago
  const pagoMutation = useMutation({
    mutationFn: facturacionService.createPago,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-facturacion'] });
      setPagoModal({ isOpen: false });
      toast.success('Pago registrado');
    },
  });

  // Descargar factura PDF
  const handleDownloadFactura = async (facturaId: number) => {
    try {
      const blob = await facturacionService.downloadFacturaPDF(facturaId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `factura_${facturaId}.pdf`;
      a.click();
      toast.success('Factura descargada');
    } catch (error) {
      toast.error('Error al descargar factura');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturación y Pagos</h1>
          <p className="text-gray-600">Gestiona facturas y registra pagos</p>
        </div>
        <button
          onClick={() => setFacturaModal({ isOpen: true })}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Nueva Factura
        </button>
      </div>

      {/* KPIs */}
      {estadisticas && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Ingresos del Mes</p>
            <p className="text-2xl font-bold text-green-600">
              ${estadisticas.ingresos_totales.toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Facturas Pagadas</p>
            <p className="text-2xl font-bold text-blue-600">
              {estadisticas.facturas_pagadas}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Facturas Pendientes</p>
            <p className="text-2xl font-bold text-yellow-600">
              {estadisticas.facturas_pendientes}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Por Cobrar</p>
            <p className="text-2xl font-bold text-red-600">
              ${estadisticas.cuentas_por_cobrar.toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-3 gap-4">
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
              <option value="PENDIENTE">Pendiente</option>
              <option value="PAGADA_PARCIAL">Pagada Parcial</option>
              <option value="PAGADA">Pagada Total</option>
              <option value="VENCIDA">Vencida</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Desde
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
              Hasta
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
      <FacturaTable
        facturas={data?.results || []}
        isLoading={isLoading}
        onRegistrarPago={(factura) => setPagoModal({ isOpen: true, factura })}
        onDownload={handleDownloadFactura}
      />

      {/* Modales */}
      <FacturaModal
        isOpen={facturaModal.isOpen}
        onClose={() => setFacturaModal({ isOpen: false })}
        onSubmit={(data) => facturaMutation.mutate(data)}
        isLoading={facturaMutation.isPending}
      />

      <PagoModal
        isOpen={pagoModal.isOpen}
        onClose={() => setPagoModal({ isOpen: false })}
        factura={pagoModal.factura}
        onSubmit={(data) => pagoMutation.mutate(data)}
        isLoading={pagoMutation.isPending}
      />
    </div>
  );
}
```

---

### 2. Tabla de Facturas

```typescript
// src/components/admin/facturacion/FacturaTable.tsx
import React from 'react';
import { Download, DollarSign, Eye } from 'lucide-react';

interface FacturaTableProps {
  facturas: any[];
  isLoading: boolean;
  onRegistrarPago: (factura: any) => void;
  onDownload: (id: number) => void;
}

export default function FacturaTable({
  facturas,
  isLoading,
  onRegistrarPago,
  onDownload,
}: FacturaTableProps) {
  if (isLoading) {
    return <div className="text-center py-8">Cargando facturas...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Número
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Paciente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Fecha Emisión
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Total
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Pagado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Saldo
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
          {facturas.map((factura) => (
            <tr key={factura.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-gray-900">
                  {factura.numero_factura}
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {factura.paciente.usuario.full_name}
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {new Date(factura.fecha_emision).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                ${factura.total.toFixed(2)}
              </td>
              <td className="px-6 py-4 text-sm text-green-600">
                ${factura.monto_pagado.toFixed(2)}
              </td>
              <td className="px-6 py-4 text-sm text-red-600 font-semibold">
                ${factura.saldo_pendiente.toFixed(2)}
              </td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 text-xs rounded-full ${getEstadoColor(factura.estado)}`}>
                  {factura.estado.replace('_', ' ')}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  {factura.saldo_pendiente > 0 && (
                    <button
                      onClick={() => onRegistrarPago(factura)}
                      className="text-green-600 hover:text-green-800"
                      title="Registrar pago"
                    >
                      <DollarSign className="w-5 h-5" />
                    </button>
                  )}
                  <button
                    onClick={() => onDownload(factura.id)}
                    className="text-blue-600 hover:text-blue-800"
                    title="Descargar PDF"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function getEstadoColor(estado: string) {
  const colors = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800',
    PAGADA_PARCIAL: 'bg-blue-100 text-blue-800',
    PAGADA: 'bg-green-100 text-green-800',
    VENCIDA: 'bg-red-100 text-red-800',
  };
  return colors[estado] || 'bg-gray-100 text-gray-800';
}
```

---

### 3. Modal de Pago

```typescript
// src/components/admin/facturacion/PagoModal.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Modal from '@/components/ui/Modal';

const pagoSchema = z.object({
  factura: z.number(),
  monto: z.number().min(0.01, 'El monto debe ser mayor a 0'),
  metodo_pago: z.enum(['EFECTIVO', 'TARJETA', 'TRANSFERENCIA']),
  referencia: z.string().optional(),
  notas: z.string().optional(),
});

type PagoFormData = z.infer<typeof pagoSchema>;

interface PagoModalProps {
  isOpen: boolean;
  onClose: () => void;
  factura?: any;
  onSubmit: (data: PagoFormData) => void;
  isLoading: boolean;
}

export default function PagoModal({
  isOpen,
  onClose,
  factura,
  onSubmit,
  isLoading,
}: PagoModalProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<PagoFormData>({
    resolver: zodResolver(pagoSchema),
    defaultValues: {
      factura: factura?.id,
      monto: factura?.saldo_pendiente || 0,
      metodo_pago: 'EFECTIVO',
    },
  });

  const monto = watch('monto');

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Registrar Pago"
    >
      {factura && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Factura:</span> {factura.numero_factura}
          </p>
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Paciente:</span> {factura.paciente.usuario.full_name}
          </p>
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Saldo pendiente:</span>{' '}
            <span className="text-red-600 font-bold">
              ${factura.saldo_pendiente.toFixed(2)}
            </span>
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <input type="hidden" {...register('factura', { valueAsNumber: true })} />

        {/* Monto */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Monto a Pagar *
          </label>
          <input
            type="number"
            step="0.01"
            {...register('monto', { valueAsNumber: true })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="0.00"
          />
          {errors.monto && (
            <p className="text-red-500 text-sm mt-1">{errors.monto.message}</p>
          )}
          {monto > factura?.saldo_pendiente && (
            <p className="text-yellow-600 text-sm mt-1">
              ⚠️ El monto es mayor al saldo pendiente
            </p>
          )}
        </div>

        {/* Método de Pago */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Método de Pago *
          </label>
          <select
            {...register('metodo_pago')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="EFECTIVO">Efectivo</option>
            <option value="TARJETA">Tarjeta</option>
            <option value="TRANSFERENCIA">Transferencia</option>
          </select>
        </div>

        {/* Referencia */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Referencia / No. Transacción
          </label>
          <input
            {...register('referencia')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ej: TXN-123456"
          />
        </div>

        {/* Notas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notas (opcional)
          </label>
          <textarea
            {...register('notas')}
            rows={2}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Observaciones del pago..."
          />
        </div>

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
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {isLoading ? 'Registrando...' : 'Registrar Pago'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
```

---

### 4. Servicio de Facturación

```typescript
// src/services/admin/facturacionService.ts
import api from '@/lib/axios';

export const facturacionService = {
  // Facturas
  async getFacturas(filters: any = {}) {
    const params = new URLSearchParams();
    if (filters.estado) params.append('estado', filters.estado);
    if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
    if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
    
    const { data } = await api.get(`/facturacion/facturas/?${params.toString()}`);
    return data;
  },

  async createFactura(facturaData: any) {
    const { data } = await api.post('/facturacion/facturas/', facturaData);
    return data;
  },

  async downloadFacturaPDF(facturaId: number) {
    const { data } = await api.get(`/facturacion/facturas/${facturaId}/pdf/`, {
      responseType: 'blob',
    });
    return data;
  },

  // Pagos
  async createPago(pagoData: any) {
    const { data } = await api.post('/facturacion/pagos/', pagoData);
    return data;
  },

  // Estadísticas
  async getEstadisticas(params: any = {}) {
    const { data } = await api.get('/facturacion/estadisticas/', { params });
    return data;
  },

  async getCuentasPorCobrar() {
    const { data } = await api.get('/facturacion/cuentas-por-cobrar/');
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Crear página Facturas.tsx
- [ ] Crear FacturaTable
- [ ] Crear FacturaModal y PagoModal
- [ ] Crear facturacionService
- [ ] KPIs financieros
- [ ] Descarga de facturas PDF
- [ ] Registro de pagos múltiples
- [ ] Vista de cuentas por cobrar
- [ ] Alertas de facturas vencidas

---

**Siguiente:** `07_inventario.md`
