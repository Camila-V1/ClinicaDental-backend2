# 40. Facturación Admin - Crear Facturas desde Presupuestos y Registrar Pagos

## 🎯 Objetivo
Implementar la gestión completa de facturación para administradores: crear facturas desde presupuestos aceptados, registrar pagos y gestionar estado de facturas.

> **⚠️ IMPORTANTE:** Las facturas se crean DESDE PRESUPUESTOS YA ACEPTADOS, no con items directos.

---

## 📁 Estructura de Archivos

```
src/
├── services/
│   └── facturacionAdminService.ts (CREAR)
└── pages/
    └── admin/
        ├── FacturacionAdmin.tsx (ACTUALIZAR)
        ├── PresupuestosParaFacturar.tsx (CREAR)
        └── DetalleFacturaAdmin.tsx (CREAR)
```

---

## 1️⃣ Servicio de Facturación Admin

**Archivo:** `src/services/facturacionAdminService.ts`

```typescript
import { httpRequest } from './core/httpCore';

export interface CrearFacturaDTO {
  presupuesto: number;  // ID del presupuesto ACEPTADO
}

export interface RegistrarPagoDTO {
  factura: number;
  monto_pagado: number;
  metodo_pago: 'EFECTIVO' | 'TARJETA' | 'TRANSFERENCIA' | 'CHEQUE';
  referencia_transaccion?: string;
  notas?: string;
}

export const facturacionAdminService = {
  // Crear factura desde presupuesto aceptado
  crearFacturaDesdePresupuesto: (presupuestoId: number) =>
    httpRequest<any>({
      method: 'POST',
      url: '/facturacion/facturas/',
      data: { presupuesto: presupuestoId }
    }),

  // Registrar pago (crea un nuevo pago)
  registrarPago: (data: RegistrarPagoDTO) =>
    httpRequest<any>({
      method: 'POST',
      url: '/facturacion/pagos/',
      data
    }),

  // Cancelar factura (solo admin)
  cancelarFactura: (facturaId: number) =>
    httpRequest<any>({
      method: 'POST',
      url: `/facturacion/facturas/${facturaId}/cancelar/`
    }),

  // Anular pago (solo admin)
  anularPago: (pagoId: number) =>
    httpRequest<any>({
      method: 'POST',
      url: `/facturacion/pagos/${pagoId}/anular/`
    }),

  // Obtener pagos de una factura
  getPagosPorFactura: (facturaId: number) =>
    httpRequest<any>({
      method: 'GET',
      url: `/facturacion/pagos/por-factura/`,
      params: { factura_id: facturaId }
    })
};
```

---

## 2️⃣ Página Presupuestos para Facturar

**Archivo:** `src/pages/admin/PresupuestosParaFacturar.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { facturacionAdminService } from '../../services/facturacionAdminService';
import { presupuestosService } from '../../services/presupuestosService';
import toast from 'react-hot-toast';

export default function PresupuestosParaFacturar() {
  const navigate = useNavigate();
  const [presupuestos, setPresupuestos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarPresupuestos();
  }, []);

  const cargarPresupuestos = async () => {
    try {
      // Obtener presupuestos en estado ACEPTADO que no tienen factura
      const data = await presupuestosService.getPresupuestos({ 
        estado: 'aceptado' 
      });
      
      // Filtrar los que ya tienen factura asociada
      const sinFactura = data.results?.filter(p => !p.factura_id) || [];
      setPresupuestos(sinFactura);
    } catch (error) {
      toast.error('Error al cargar presupuestos');
    } finally {
      setLoading(false);
    }
  };

  const crearFactura = async (presupuestoId: number, nombrePaciente: string) => {
    if (!confirm(`¿Crear factura para ${nombrePaciente}?`)) return;
    
    try {
      await facturacionAdminService.crearFacturaDesdePresupuesto(presupuestoId);
      toast.success('Factura creada exitosamente');
      cargarPresupuestos(); // Recargar lista
    } catch (error: any) {
      const mensaje = error.response?.data?.error || 'Error al crear factura';
      toast.error(mensaje);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Presupuestos para Facturar</h1>
        <button
          onClick={() => navigate('/admin/facturacion')}
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
        >
          Ver Facturas
        </button>
      </div>

      {presupuestos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No hay presupuestos aceptados pendientes de facturar
        </div>
      ) : (
        <div className="grid gap-4">
          {presupuestos.map(presupuesto => (
            <div key={presupuesto.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2">
                    {presupuesto.plan_tratamiento.paciente.usuario.nombre} {presupuesto.plan_tratamiento.paciente.usuario.apellido}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Plan de Tratamiento</p>
                      <p className="font-medium">#{presupuesto.plan_tratamiento.id}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Odontólogo</p>
                      <p className="font-medium">
                        {presupuesto.plan_tratamiento.odontologo.usuario.nombre}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Fecha Presupuesto</p>
                      <p className="font-medium">
                        {new Date(presupuesto.fecha_creacion).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Total Presupuestado</p>
                      <p className="font-bold text-lg text-blue-600">
                        Bs. {presupuesto.total_presupuestado}
                      </p>
                    </div>
                  </div>

                  {/* Items del presupuesto */}
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Servicios incluidos:</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {presupuesto.items?.map((item: any, idx: number) => (
                        <li key={idx}>
                          • {item.servicio_nombre} - Bs. {item.precio_unitario}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="ml-4">
                  <button
                    onClick={() => crearFactura(
                      presupuesto.id, 
                      `${presupuesto.plan_tratamiento.paciente.usuario.nombre} ${presupuesto.plan_tratamiento.paciente.usuario.apellido}`
                    )}
                    className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
                  >
                    📄 Crear Factura
                  </button>
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

## 3️⃣ Modal Registrar Pago

**Componente:** `ModalRegistrarPago.tsx`

```typescript
import { useState } from 'react';
import { facturacionAdminService } from '../../services/facturacionAdminService';
import toast from 'react-hot-toast';

interface Props {
  facturaId: number;
  saldoPendiente: number;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ModalRegistrarPago({ facturaId, saldoPendiente, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState({
    monto_pagado: saldoPendiente,
    metodo_pago: 'EFECTIVO' as 'EFECTIVO' | 'TARJETA' | 'TRANSFERENCIA' | 'CHEQUE',
    referencia_transaccion: '',
    notas: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.monto_pagado > saldoPendiente) {
      toast.error('El monto no puede ser mayor al saldo pendiente');
      return;
    }
    
    try {
      await facturacionAdminService.registrarPago({
        factura: facturaId,
        ...formData
      });
      toast.success('Pago registrado exitosamente');
      onSuccess();
      onClose();
    } catch (error: any) {
      const mensaje = error.response?.data?.error || 'Error al registrar pago';
      toast.error(mensaje);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <h2 className="text-xl font-bold mb-4">Registrar Pago</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Monto *</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max={saldoPendiente}
              required
              value={formData.monto_pagado}
              onChange={(e) => setFormData({ ...formData, monto_pagado: parseFloat(e.target.value) })}
              className="w-full border rounded px-3 py-2"
            />
            <span className="text-sm text-gray-500">Saldo pendiente: Bs. {saldoPendiente.toFixed(2)}</span>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Método de Pago *</label>
            <select
              required
              value={formData.metodo_pago}
              onChange={(e) => setFormData({ ...formData, metodo_pago: e.target.value as any })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="EFECTIVO">Efectivo</option>
              <option value="TARJETA">Tarjeta</option>
              <option value="TRANSFERENCIA">Transferencia</option>
              <option value="CHEQUE">Cheque</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Referencia de Transacción</label>
            <input
              type="text"
              value={formData.referencia_transaccion}
              onChange={(e) => setFormData({ ...formData, referencia_transaccion: e.target.value })}
              className="w-full border rounded px-3 py-2"
              placeholder="Número de transacción, cheque, etc."
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Notas</label>
            <textarea
              value={formData.notas}
              onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
              className="w-full border rounded px-3 py-2"
              rows={2}
              placeholder="Observaciones o detalles adicionales"
            />
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Registrar
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## 4️⃣ Integración en Lista de Facturas

Agregar botones en `FacturacionAdmin.tsx`:

```typescript
import { useState } from 'react';
import ModalRegistrarPago from '../../components/facturacion/ModalRegistrarPago';

// Dentro del componente
const [facturaSeleccionada, setFacturaSeleccionada] = useState(null);
const [mostrarModalPago, setMostrarModalPago] = useState(false);

// En la tabla de facturas
{factura.estado === 'PENDIENTE' ? (
  <button
    onClick={() => {
      setFacturaSeleccionada(factura);
      setMostrarModalPago(true);
    }}
    className="text-green-600 hover:text-green-700"
  >
    💰 Registrar Pago
  </button>
) : null}

{factura.estado === 'PENDIENTE' && (
  <button
    onClick={() => cancelarFactura(factura.id)}
    className="text-red-600 hover:text-red-700"
  >
    ❌ Cancelar Factura
  </button>
)}

// Función para cancelar factura
const cancelarFactura = async (facturaId: number) => {
  if (!confirm('¿Está seguro de cancelar esta factura?')) return;
  
  try {
    await facturacionAdminService.cancelarFactura(facturaId);
    toast.success('Factura cancelada');
    cargarFacturas();
  } catch (error) {
    toast.error('Error al cancelar factura');
  }
};

// Renderizar modal
{mostrarModalPago && facturaSeleccionada && (
  <ModalRegistrarPago
    facturaId={facturaSeleccionada.id}
    saldoPendiente={facturaSeleccionada.saldo_pendiente}
    onClose={() => setMostrarModalPago(false)}
    onSuccess={cargarFacturas}
  />
)}
```

---

## 5️⃣ Vista de Pagos de una Factura

**Componente:** `DetallePagosFactura.tsx`

```typescript
import { useState, useEffect } from 'react';
import { facturacionAdminService } from '../../services/facturacionAdminService';
import toast from 'react-hot-toast';

interface Props {
  facturaId: number;
}

export default function DetallePagosFactura({ facturaId }: Props) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    cargarPagos();
  }, [facturaId]);

  const cargarPagos = async () => {
    try {
      const response = await facturacionAdminService.getPagosPorFactura(facturaId);
      setData(response);
    } catch (error) {
      toast.error('Error al cargar pagos');
    }
  };

  const anularPago = async (pagoId: number) => {
    if (!confirm('¿Anular este pago?')) return;
    
    try {
      await facturacionAdminService.anularPago(pagoId);
      toast.success('Pago anulado');
      cargarPagos();
    } catch (error) {
      toast.error('Error al anular pago');
    }
  };

  if (!data) return <div>Cargando...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">Pagos Registrados</h3>
      
      {/* Resumen */}
      <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded">
        <div>
          <p className="text-sm text-gray-600">Total Factura</p>
          <p className="text-lg font-bold">Bs. {data.factura.total}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Total Pagado</p>
          <p className="text-lg font-bold text-green-600">Bs. {data.factura.monto_pagado}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Saldo Pendiente</p>
          <p className="text-lg font-bold text-red-600">Bs. {data.factura.saldo_pendiente}</p>
        </div>
      </div>

      {/* Lista de pagos */}
      <table className="min-w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left">Fecha</th>
            <th className="px-4 py-2 text-left">Método</th>
            <th className="px-4 py-2 text-left">Monto</th>
            <th className="px-4 py-2 text-left">Referencia</th>
            <th className="px-4 py-2 text-left">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {data.pagos.map((pago: any) => (
            <tr key={pago.id} className="border-t">
              <td className="px-4 py-2">{new Date(pago.fecha_pago).toLocaleDateString()}</td>
              <td className="px-4 py-2">{pago.metodo_pago}</td>
              <td className="px-4 py-2 font-bold">Bs. {pago.monto_pagado}</td>
              <td className="px-4 py-2 text-sm">{pago.referencia_transaccion || '-'}</td>
              <td className="px-4 py-2">
                <button
                  onClick={() => anularPago(pago.id)}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  Anular
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## ✅ Checklist

- [ ] Crear `facturacionAdminService.ts`
- [ ] Crear página `PresupuestosParaFacturar.tsx`
- [ ] Crear componente `ModalRegistrarPago.tsx`
- [ ] Crear componente `DetallePagosFactura.tsx`
- [ ] Agregar rutas en `App.tsx`
- [ ] Probar crear factura desde presupuesto
- [ ] Probar registrar pago
- [ ] Probar cancelar factura
- [ ] Probar anular pago
- [ ] Validar permisos (solo ADMIN)

**Endpoints utilizados:**
- `POST /api/facturacion/facturas/` + body `{presupuesto: id}`
- `POST /api/facturacion/pagos/` + body `{factura, monto_pagado, metodo_pago, ...}`
- `POST /api/facturacion/facturas/{id}/cancelar/`
- `POST /api/facturacion/pagos/{id}/anular/`
- `GET /api/facturacion/pagos/por-factura/?factura_id={id}`

**Flujo completo:**
1. Odontólogo crea presupuesto → estado `PROPUESTO`
2. Paciente acepta presupuesto → estado `ACEPTADO`
3. Admin crea factura desde presupuesto → estado `PENDIENTE`
4. Admin registra pago(s) → actualiza `monto_pagado`
5. Cuando `monto_pagado >= monto_total` → estado `PAGADA`
