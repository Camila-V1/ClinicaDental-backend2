# 42. Ajuste de Stock en Inventario

## 🎯 Objetivo
Implementar la funcionalidad de ajuste de stock de insumos con registro de motivo.

> **⚠️ NOTA:** El backend actualmente NO registra un historial de movimientos. Solo permite ajustar el stock actual con un motivo. El historial de movimientos será implementado en una versión futura.

---

## 📁 Actualizar Servicio Existente

**Archivo:** `src/services/inventarioService.ts` (ACTUALIZAR)

Agregar este método al servicio existente:

```typescript
export const inventarioService = {
  // ... métodos existentes ...

  // Ajustar stock
  ajustarStock: (insumoId: number, data: {
    cantidad: number;
    motivo: string;
    observaciones?: string;
  }) =>
    httpRequest<any>({
      method: 'POST',
      url: `/inventario/insumos/${insumoId}/ajustar_stock/`,
      data
    })
};
```

---

## 1️⃣ Modal Ajustar Stock

**Archivo:** `src/components/inventario/ModalAjustarStock.tsx` (CREAR)

```typescript
import { useState } from 'react';
import { inventarioService } from '../../services/inventarioService';
import toast from 'react-hot-toast';

interface Props {
  insumo: {
    id: number;
    nombre: string;
    stock_actual: number;
  };
  onClose: () => void;
  onSuccess: () => void;
}

export default function ModalAjustarStock({ insumo, onClose, onSuccess }: Props) {
  const [tipo, setTipo] = useState<'ENTRADA' | 'SALIDA'>('ENTRADA');
  const [formData, setFormData] = useState({
    cantidad: 0,
    motivo: '',
    observaciones: ''
  });

  const MOTIVOS = {
    ENTRADA: [
      'Compra a proveedor',
      'Devolución de paciente',
      'Corrección de inventario',
      'Donación',
      'Otro'
    ],
    SALIDA: [
      'Uso en tratamiento',
      'Producto vencido',
      'Producto dañado',
      'Donación',
      'Corrección de inventario',
      'Otro'
    ]
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.cantidad <= 0) {
      toast.error('La cantidad debe ser mayor a 0');
      return;
    }

    try {
      // Convertir a negativo si es salida
      const cantidad = tipo === 'SALIDA' ? -formData.cantidad : formData.cantidad;
      
      await inventarioService.ajustarStock(insumo.id, {
        cantidad,
        motivo: formData.motivo,
        observaciones: formData.observaciones
      });
      
      toast.success('Stock ajustado correctamente');
      onSuccess();
      onClose();
    } catch (error: any) {
      const mensaje = error.response?.data?.error || 'Error al ajustar stock';
      toast.error(mensaje);
    }
  };

  const stockNuevo = tipo === 'ENTRADA' 
    ? insumo.stock_actual + formData.cantidad
    : insumo.stock_actual - formData.cantidad;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <h2 className="text-xl font-bold mb-4">Ajustar Stock: {insumo.nombre}</h2>
        
        <div className="mb-4 p-3 bg-gray-100 rounded">
          <p className="text-sm text-gray-600">Stock actual</p>
          <p className="text-2xl font-bold">{insumo.stock_actual}</p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Tipo de movimiento */}
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              onClick={() => setTipo('ENTRADA')}
              className={`flex-1 py-2 rounded ${
                tipo === 'ENTRADA'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              ➕ Entrada
            </button>
            <button
              type="button"
              onClick={() => setTipo('SALIDA')}
              className={`flex-1 py-2 rounded ${
                tipo === 'SALIDA'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              ➖ Salida
            </button>
          </div>

          {/* Cantidad */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Cantidad *</label>
            <input
              type="number"
              min="1"
              step="0.01"
              required
              value={formData.cantidad}
              onChange={(e) => setFormData({ ...formData, cantidad: parseFloat(e.target.value) || 0 })}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          {/* Motivo */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Motivo *</label>
            <select
              required
              value={formData.motivo}
              onChange={(e) => setFormData({ ...formData, motivo: e.target.value })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Seleccione un motivo</option>
              {MOTIVOS[tipo].map(motivo => (
                <option key={motivo} value={motivo}>{motivo}</option>
              ))}
            </select>
          </div>

          {/* Observaciones */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Observaciones</label>
            <textarea
              value={formData.observaciones}
              onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
              className="w-full border rounded px-3 py-2"
              rows={2}
              placeholder="Detalles adicionales (opcional)"
            />
          </div>

          {/* Preview */}
          <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
            <p className="text-sm text-gray-600">Stock nuevo</p>
            <p className="text-2xl font-bold text-blue-600">
              {stockNuevo >= 0 ? stockNuevo.toFixed(2) : 'ERROR: Stock negativo'}
            </p>
          </div>

          {stockNuevo < 0 && (
            <div className="mb-4 p-3 bg-red-50 rounded border border-red-200">
              <p className="text-sm text-red-600">
                ⚠️ La cantidad de salida excede el stock disponible
              </p>
            </div>
          )}

          {/* Botones */}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={stockNuevo < 0}
              className={`flex-1 text-white px-4 py-2 rounded ${
                tipo === 'ENTRADA' 
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              Confirmar
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

## 2️⃣ Integrar en Página de Inventario

Actualizar `src/pages/admin/Inventario.tsx`:

```typescript
import { useState } from 'react';
import ModalAjustarStock from '../../components/inventario/ModalAjustarStock';

// Dentro del componente
const [insumoSeleccionado, setInsumoSeleccionado] = useState(null);

// Agregar botón en cada fila de la tabla de insumos
<button
  onClick={() => setInsumoSeleccionado(insumo)}
  className="text-blue-600 hover:text-blue-700"
  title="Ajustar stock"
>
  📦 Ajustar Stock
</button>

// Renderizar modal al final del componente
{insumoSeleccionado && (
  <ModalAjustarStock
    insumo={insumoSeleccionado}
    onClose={() => setInsumoSeleccionado(null)}
    onSuccess={() => {
      cargarInsumos(); // Recargar lista de insumos
      setInsumoSeleccionado(null);
    }}
  />
)}
```

---

## 3️⃣ Mejora: Indicador de Stock Bajo

Agregar indicador visual en la lista de insumos:

```typescript
// En la tabla de insumos
<td className="px-6 py-4">
  <div className="flex items-center gap-2">
    <span className="font-medium">{insumo.stock_actual}</span>
    {insumo.stock_actual <= insumo.stock_minimo && (
      <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
        ⚠️ Bajo
      </span>
    )}
  </div>
</td>
```

---

## ✅ Checklist

- [ ] Actualizar `inventarioService.ts` con método `ajustarStock`
- [ ] Crear componente `ModalAjustarStock.tsx`
- [ ] Integrar modal en `Inventario.tsx`
- [ ] Agregar indicador visual de stock bajo
- [ ] Probar ajuste de stock (entrada)
- [ ] Probar ajuste de stock (salida)
- [ ] Validar que no permita stock negativo
- [ ] Verificar que el motivo sea obligatorio

**Endpoint utilizado:**
- `POST /api/inventario/insumos/{id}/ajustar_stock/`

**Respuesta del backend:**
```json
{
  "mensaje": "Stock ajustado exitosamente",
  "insumo": "INS001 - Resina Z350",
  "stock_anterior": 50,
  "ajuste": -10,
  "stock_actual": 40,
  "motivo": "Uso en tratamiento"
}
```

---

## 📝 Nota sobre Historial de Movimientos

> **⚠️ IMPORTANTE:** El backend actualmente NO implementa un modelo `MovimientoInventario` para registrar el historial de cambios. Los ajustes de stock se registran en la bitácora del sistema pero no hay una tabla dedicada para consultar movimientos históricos.
>
> **Funcionalidad futura:** En una versión posterior se implementará:
> - Modelo `MovimientoInventario` en el backend
> - Endpoint `GET /api/inventario/movimientos/` para consultar historial
> - Página `MovimientosInventario.tsx` para visualizar trazabilidad
>
> Por ahora, solo puedes:
> - ✅ Ajustar stock con motivo
> - ✅ Ver stock actual
> - ✅ Ver alertas de stock bajo
> - ❌ Ver historial de movimientos (no disponible)
