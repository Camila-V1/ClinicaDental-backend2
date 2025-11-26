# Guía 47: Pagos con Stripe para Citas y Tratamientos

## 📋 Descripción General

Sistema de pagos integrado con Stripe para:
- ✅ **Pago de Citas** - Al agendar o después de la consulta
- ✅ **Pago de Tratamientos** - Al crear o completar un tratamiento
- ✅ **Pago de Planes de Tratamiento** - Pago completo o en cuotas
- ✅ **Historial de Pagos** - Registro completo de transacciones

## 🎯 Flujos de Pago

### **Flujo 1: Pagar Cita**
```
[Agendar Cita] → [Procesar Pago] → [Confirmar] → [Cita Pagada]
```

### **Flujo 2: Pagar Tratamiento**
```
[Crear Tratamiento] → [Calcular Costo] → [Pagar] → [Tratamiento Confirmado]
```

### **Flujo 3: Pagar Plan de Tratamiento**
```
[Plan Creado] → [Seleccionar Items] → [Pago Completo/Cuotas] → [Plan Activo]
```

---

## 📡 Backend - Nuevos Endpoints

### **1. Crear Pago para Cita**

```http
POST /api/facturacion/pagos/crear-pago-cita/
Authorization: Bearer {token}
Content-Type: application/json

{
  "cita_id": 5,
  "monto": 50.00,
  "metodo_pago": "STRIPE",
  "return_url": "http://localhost:5173/citas/pago-exitoso",
  "cancel_url": "http://localhost:5173/citas/pago-cancelado"
}
```

**Respuesta:**
```json
{
  "pago_id": 123,
  "payment_url": "https://checkout.stripe.com/pay/cs_xxx...",
  "session_id": "cs_xxx...",
  "message": "Redirige al usuario a payment_url"
}
```

### **2. Crear Pago para Tratamiento**

```http
POST /api/facturacion/pagos/crear-pago-tratamiento/
Authorization: Bearer {token}
Content-Type: application/json

{
  "tratamiento_id": 10,
  "monto": 150.00,
  "metodo_pago": "STRIPE",
  "return_url": "http://localhost:5173/tratamientos/pago-exitoso",
  "cancel_url": "http://localhost:5173/tratamientos/pago-cancelado"
}
```

### **3. Crear Pago para Plan de Tratamiento**

```http
POST /api/facturacion/pagos/crear-pago-plan/
Authorization: Bearer {token}
Content-Type: application/json

{
  "plan_tratamiento_id": 8,
  "monto": 500.00,
  "metodo_pago": "STRIPE",
  "tipo_pago": "COMPLETO",
  "return_url": "http://localhost:5173/planes/pago-exitoso",
  "cancel_url": "http://localhost:5173/planes/pago-cancelado"
}
```

### **4. Confirmar Pago (Callback/Webhook)**

```http
POST /api/facturacion/pagos/{id}/confirmar/
GET  /api/facturacion/pagos/{id}/confirmar/?session_id=cs_xxx
```

**Respuesta (Pago Exitoso):**
```json
{
  "success": true,
  "pago_id": 123,
  "estado": "COMPLETADO",
  "monto": 50.00,
  "transaccion_id": "cs_xxx...",
  "cita_id": 5,
  "message": "Pago procesado exitosamente"
}
```

### **5. Verificar Estado de Pago**

```http
GET /api/facturacion/pagos/{id}/estado/
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "pago_id": 123,
  "estado": "COMPLETADO",
  "monto": 50.00,
  "fecha_pago": "2025-11-26T10:30:00Z",
  "metodo_pago": "STRIPE",
  "transaccion_id": "cs_xxx...",
  "relacionado": {
    "tipo": "cita",
    "id": 5,
    "descripcion": "Consulta General - Dr. Martínez"
  }
}
```

### **6. Listar Historial de Pagos**

```http
GET /api/facturacion/pagos/?paciente_id=10
GET /api/facturacion/pagos/?estado=COMPLETADO
GET /api/facturacion/pagos/?metodo_pago=STRIPE
Authorization: Bearer {token}
```

---

## 🎨 Frontend - Implementación

### **1. Servicio de Pagos**

```typescript
// src/services/pagosService.ts
import axiosAdvanced from './axios-advanced';

interface DatosPagoCita {
  cita_id: number;
  monto: number;
  metodo_pago: 'STRIPE' | 'PAYPAL' | 'MERCADOPAGO';
  return_url: string;
  cancel_url: string;
}

interface DatosPagoTratamiento {
  tratamiento_id: number;
  monto: number;
  metodo_pago: 'STRIPE' | 'PAYPAL' | 'MERCADOPAGO';
  return_url: string;
  cancel_url: string;
}

interface DatosPagoPlan {
  plan_tratamiento_id: number;
  monto: number;
  metodo_pago: 'STRIPE' | 'PAYPAL' | 'MERCADOPAGO';
  tipo_pago: 'COMPLETO' | 'CUOTA';
  return_url: string;
  cancel_url: string;
}

interface RespuestaCrearPago {
  pago_id: number;
  payment_url: string;
  session_id: string;
  message: string;
}

export const pagosService = {
  // Crear pago para cita
  crearPagoCita: async (datos: DatosPagoCita): Promise<RespuestaCrearPago> => {
    const response = await axiosAdvanced.post('/facturacion/pagos/crear-pago-cita/', datos);
    return response.data;
  },

  // Crear pago para tratamiento
  crearPagoTratamiento: async (datos: DatosPagoTratamiento): Promise<RespuestaCrearPago> => {
    const response = await axiosAdvanced.post('/facturacion/pagos/crear-pago-tratamiento/', datos);
    return response.data;
  },

  // Crear pago para plan de tratamiento
  crearPagoPlan: async (datos: DatosPagoPlan): Promise<RespuestaCrearPago> => {
    const response = await axiosAdvanced.post('/facturacion/pagos/crear-pago-plan/', datos);
    return response.data;
  },

  // Confirmar pago
  confirmarPago: async (pagoId: number, sessionId?: string) => {
    const params = sessionId ? `?session_id=${sessionId}` : '';
    const response = await axiosAdvanced.post(`/facturacion/pagos/${pagoId}/confirmar/${params}`);
    return response.data;
  },

  // Verificar estado
  verificarEstado: async (pagoId: number) => {
    const response = await axiosAdvanced.get(`/facturacion/pagos/${pagoId}/estado/`);
    return response.data;
  },

  // Listar historial
  listarPagos: async (filtros?: {
    paciente_id?: number;
    estado?: string;
    metodo_pago?: string;
  }) => {
    const response = await axiosAdvanced.get('/facturacion/pagos/', { params: filtros });
    return response.data;
  },
};
```

---

### **2. Hook Personalizado para Pagos**

```typescript
// src/hooks/usePago.ts
import { useState } from 'react';
import { pagosService } from '../services/pagosService';
import { useNavigate } from 'react-router-dom';

interface UsePagoOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
}

export const usePago = (options?: UsePagoOptions) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const procesarPagoCita = async (citaId: number, monto: number) => {
    setLoading(true);
    setError(null);

    try {
      const returnUrl = `${window.location.origin}/citas/pago-confirmacion`;
      const cancelUrl = `${window.location.origin}/citas`;

      const resultado = await pagosService.crearPagoCita({
        cita_id: citaId,
        monto,
        metodo_pago: 'STRIPE',
        return_url: returnUrl,
        cancel_url: cancelUrl,
      });

      // Guardar pagoId en localStorage para recuperar después
      localStorage.setItem('pending_payment_id', resultado.pago_id.toString());
      localStorage.setItem('pending_payment_type', 'cita');

      // Redirigir a Stripe Checkout
      window.location.href = resultado.payment_url;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Error procesando pago';
      setError(errorMsg);
      options?.onError?.(err);
    } finally {
      setLoading(false);
    }
  };

  const procesarPagoTratamiento = async (tratamientoId: number, monto: number) => {
    setLoading(true);
    setError(null);

    try {
      const returnUrl = `${window.location.origin}/tratamientos/pago-confirmacion`;
      const cancelUrl = `${window.location.origin}/tratamientos`;

      const resultado = await pagosService.crearPagoTratamiento({
        tratamiento_id: tratamientoId,
        monto,
        metodo_pago: 'STRIPE',
        return_url: returnUrl,
        cancel_url: cancelUrl,
      });

      localStorage.setItem('pending_payment_id', resultado.pago_id.toString());
      localStorage.setItem('pending_payment_type', 'tratamiento');

      window.location.href = resultado.payment_url;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Error procesando pago';
      setError(errorMsg);
      options?.onError?.(err);
    } finally {
      setLoading(false);
    }
  };

  const procesarPagoPlan = async (planId: number, monto: number, tipoPago: 'COMPLETO' | 'CUOTA' = 'COMPLETO') => {
    setLoading(true);
    setError(null);

    try {
      const returnUrl = `${window.location.origin}/planes-tratamiento/pago-confirmacion`;
      const cancelUrl = `${window.location.origin}/planes-tratamiento`;

      const resultado = await pagosService.crearPagoPlan({
        plan_tratamiento_id: planId,
        monto,
        metodo_pago: 'STRIPE',
        tipo_pago: tipoPago,
        return_url: returnUrl,
        cancel_url: cancelUrl,
      });

      localStorage.setItem('pending_payment_id', resultado.pago_id.toString());
      localStorage.setItem('pending_payment_type', 'plan');

      window.location.href = resultado.payment_url;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Error procesando pago';
      setError(errorMsg);
      options?.onError?.(err);
    } finally {
      setLoading(false);
    }
  };

  return {
    procesarPagoCita,
    procesarPagoTratamiento,
    procesarPagoPlan,
    loading,
    error,
  };
};
```

---

### **3. Componente: Botón de Pago para Citas**

```tsx
// src/components/pagos/BotonPagarCita.tsx
import React from 'react';
import { usePago } from '../../hooks/usePago';

interface Props {
  citaId: number;
  monto: number;
  disabled?: boolean;
}

export const BotonPagarCita: React.FC<Props> = ({ citaId, monto, disabled }) => {
  const { procesarPagoCita, loading, error } = usePago({
    onError: (err) => {
      console.error('Error al procesar pago:', err);
    },
  });

  const handlePagar = () => {
    if (confirm(`¿Confirmar pago de $${monto.toFixed(2)}?`)) {
      procesarPagoCita(citaId, monto);
    }
  };

  return (
    <div>
      <button
        onClick={handlePagar}
        disabled={disabled || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Procesando...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
              <path fillRule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clipRule="evenodd" />
            </svg>
            Pagar ${monto.toFixed(2)}
          </>
        )}
      </button>
      {error && (
        <p className="text-red-500 text-sm mt-2">{error}</p>
      )}
    </div>
  );
};
```

---

### **4. Componente: Modal de Pago para Tratamientos**

```tsx
// src/components/pagos/ModalPagarTratamiento.tsx
import React, { useState } from 'react';
import { usePago } from '../../hooks/usePago';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  tratamiento: {
    id: number;
    nombre: string;
    costo: number;
  };
}

export const ModalPagarTratamiento: React.FC<Props> = ({ isOpen, onClose, tratamiento }) => {
  const { procesarPagoTratamiento, loading, error } = usePago();
  const [montoPagar, setMontoPagar] = useState(tratamiento.costo);

  if (!isOpen) return null;

  const handleConfirmarPago = () => {
    procesarPagoTratamiento(tratamiento.id, montoPagar);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Procesar Pago</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-50 p-4 rounded">
            <p className="text-sm text-gray-600">Tratamiento</p>
            <p className="font-semibold text-lg">{tratamiento.nombre}</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Monto a Pagar</label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                max={tratamiento.costo}
                value={montoPagar}
                onChange={(e) => setMontoPagar(parseFloat(e.target.value))}
                className="w-full border rounded px-8 py-2"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Costo total: ${tratamiento.costo.toFixed(2)}
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-sm text-blue-800">
              💳 Serás redirigido a Stripe para completar el pago de forma segura.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={loading}
              className="flex-1 border border-gray-300 rounded px-4 py-2 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirmarPago}
              disabled={loading || montoPagar <= 0}
              className="flex-1 bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Procesando...' : `Pagar $${montoPagar.toFixed(2)}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

### **5. Página de Confirmación de Pago**

```tsx
// src/pages/PagoConfirmacion.tsx
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { pagosService } from '../services/pagosService';

export const PagoConfirmacion: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [estado, setEstado] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    confirmarPago();
  }, []);

  const confirmarPago = async () => {
    const sessionId = searchParams.get('session_id');
    const pagoId = localStorage.getItem('pending_payment_id');
    const tipoPago = localStorage.getItem('pending_payment_type');

    if (!pagoId) {
      setError('No se encontró información del pago');
      setLoading(false);
      return;
    }

    try {
      // Confirmar el pago
      await pagosService.confirmarPago(Number(pagoId), sessionId || undefined);

      // Verificar estado
      const estadoPago = await pagosService.verificarEstado(Number(pagoId));
      setEstado(estadoPago);

      // Limpiar localStorage
      localStorage.removeItem('pending_payment_id');
      localStorage.removeItem('pending_payment_type');
    } catch (error: any) {
      setError(error.response?.data?.error || 'Error verificando pago');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando pago...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-20 p-6">
        <div className="bg-red-50 border border-red-200 rounded p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2">Error</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-20 p-6">
      <div className="bg-green-50 border border-green-200 rounded p-6 mb-6">
        <div className="flex items-center mb-4">
          <svg className="w-12 h-12 text-green-600 mr-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <div>
            <h2 className="text-2xl font-bold text-green-700">¡Pago Exitoso!</h2>
            <p className="text-green-600">Tu pago ha sido procesado correctamente</p>
          </div>
        </div>

        <div className="space-y-2 mt-4 text-gray-700">
          <p><strong>Monto:</strong> ${estado?.monto.toFixed(2)}</p>
          <p><strong>Método:</strong> {estado?.metodo_pago}</p>
          <p><strong>ID Transacción:</strong> {estado?.transaccion_id}</p>
          <p><strong>Fecha:</strong> {new Date(estado?.fecha_pago).toLocaleString()}</p>
          
          {estado?.relacionado && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <p><strong>Relacionado con:</strong></p>
              <p className="text-sm">{estado.relacionado.tipo}: {estado.relacionado.descripcion}</p>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={() => navigate('/citas')}
        className="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700"
      >
        Volver a Citas
      </button>
    </div>
  );
};
```

---

### **6. Integración en Lista de Citas**

```tsx
// src/components/citas/CitaCard.tsx (ejemplo de uso)
import React from 'react';
import { BotonPagarCita } from '../pagos/BotonPagarCita';

interface Props {
  cita: {
    id: number;
    fecha: string;
    odontologo_nombre: string;
    estado: string;
    costo: number;
    pagada: boolean;
  };
}

export const CitaCard: React.FC<Props> = ({ cita }) => {
  return (
    <div className="border rounded p-4 hover:shadow-lg transition">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-lg">
            {new Date(cita.fecha).toLocaleDateString()}
          </h3>
          <p className="text-gray-600">Dr. {cita.odontologo_nombre}</p>
        </div>
        <span className={`px-3 py-1 rounded text-sm ${
          cita.pagada ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
        }`}>
          {cita.pagada ? 'Pagada' : 'Pendiente de Pago'}
        </span>
      </div>

      <div className="flex justify-between items-center">
        <p className="text-xl font-bold text-blue-600">${cita.costo.toFixed(2)}</p>
        
        {!cita.pagada && cita.estado === 'CONFIRMADA' && (
          <BotonPagarCita 
            citaId={cita.id} 
            monto={cita.costo}
          />
        )}
      </div>
    </div>
  );
};
```

---

## 🔧 Configuración Adicional en Settings

```python
# core/settings.py

# Stripe Configuration (ya está)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')

# URL base para callbacks
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')
```

---

## 📝 Estados de Pago

| Estado | Descripción |
|--------|-------------|
| `PENDIENTE` | Pago iniciado, esperando confirmación |
| `PROCESANDO` | Usuario en checkout de Stripe |
| `COMPLETADO` | Pago exitoso y verificado |
| `FALLIDO` | Pago rechazado o error |
| `CANCELADO` | Usuario canceló el pago |
| `REEMBOLSADO` | Pago reembolsado |

---

## ✅ Características

- ✅ Pago seguro con Stripe Checkout
- ✅ Soporte para citas, tratamientos y planes
- ✅ Confirmación automática de pagos
- ✅ Historial completo de transacciones
- ✅ Múltiples métodos de pago (preparado para PayPal/MercadoPago)
- ✅ Manejo de errores y estados
- ✅ UI/UX optimizada con feedback visual
- ✅ Webhooks para confirmación automática

---

## 🎯 Próximos Pasos

1. Implementar backend de pagos en Django
2. Crear componentes frontend siguiendo esta guía
3. Probar con tarjeta de prueba: `4242 4242 4242 4242`
4. Configurar webhooks en producción
5. Agregar opciones de pago en cuotas
6. Implementar sistema de reembolsos
