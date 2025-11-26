# Guía 46: Sistema de Registro Automático de Clínicas con Pago

## 📋 Descripción General

Sistema completo de auto-registro de clínicas con pago automático. El flujo incluye:
1. Usuario llena formulario → Crea solicitud
2. Usuario paga (Stripe/PayPal/MercadoPago) → Se verifica pago
3. **Pago exitoso → Se crea clínica automáticamente**
4. **Se genera usuario admin con contraseña aleatoria**
5. **Usuario descarga archivo TXT con credenciales**

## 🔄 Flujo Completo

```
[Formulario] → [Pagar] → [Verificar Pago] → [Crear Clínica] → [Descargar Credenciales TXT]
```

## 📡 Endpoints del Backend

### 1. Crear Solicitud de Registro (Público)
```http
POST /api/tenants/solicitudes/
Content-Type: application/json

{
  "nombre_clinica": "Clínica Dental Santa María",
  "dominio_deseado": "santa-maria",
  "nombre_contacto": "Dr. Juan Pérez",
  "email": "juan@santamaria.com",
  "telefono": "+1234567890",
  "cargo": "Director",
  "direccion": "Av. Principal 123",
  "ciudad": "Lima",
  "pais": "Perú",
  "plan_solicitado": 2,
  "mensaje": "Necesito 5 usuarios"
}
```

**Respuesta:**
```json
{
  "message": "Solicitud creada. Procede con el pago.",
  "solicitud_id": 1,
  "token": "abc123xyz...",
  "siguiente_paso": "/api/tenants/solicitudes/1/iniciar_pago/",
  "datos": { ... }
}
```

### 2. Iniciar Proceso de Pago (Público)
```http
POST /api/tenants/solicitudes/1/iniciar_pago/
Content-Type: application/json

{
  "metodo_pago": "STRIPE",
  "return_url": "https://mifrontend.com/registro/exito",
  "cancel_url": "https://mifrontend.com/registro/cancelado"
}
```

**Respuesta:**
```json
{
  "message": "Pago iniciado. Redirige al usuario a payment_url",
  "payment_url": "https://checkout.stripe.com/pay/cs_xxx...",
  "payment_id": "cs_xxx...",
  "solicitud_id": 1
}
```

### 3. Confirmar Pago (Webhook de Pasarela)
```http
POST /api/tenants/solicitudes/1/confirmar_pago/
GET  /api/tenants/solicitudes/1/confirmar_pago/?session_id=cs_xxx

# Este endpoint es llamado por la pasarela de pago o cuando el usuario regresa
```

**Respuesta (Pago Exitoso):**
```json
{
  "message": "¡Pago exitoso! Clínica creada automáticamente.",
  "solicitud_id": 1,
  "clinica_id": 5,
  "clinica_nombre": "Clínica Dental Santa María",
  "dominio": "santa-maria",
  "download_url": "/api/tenants/solicitudes/1/descargar_credenciales/?token=abc123...",
  "token": "abc123xyz...",
  "credenciales_nota": "Descarga el archivo con tus credenciales usando el link proporcionado"
}
```

### 4. Verificar Estado (Público)
```http
GET /api/tenants/solicitudes/1/verificar_estado/
```

**Respuesta:**
```json
{
  "solicitud_id": 1,
  "estado": "COMPLETADA",
  "estado_display": "Completada (Clínica Creada)",
  "pago_exitoso": true,
  "fecha_pago": "2025-11-26T10:30:00Z",
  "clinica_nombre": "Clínica Dental Santa María",
  "dominio": "santa-maria",
  "credenciales_disponibles": true,
  "token_valido": true
}
```

### 5. Descargar Credenciales TXT (Público con Token)
```http
GET /api/tenants/solicitudes/1/descargar_credenciales/?token=abc123xyz...
```

**Respuesta:** Archivo `credenciales_santa-maria_20251126.txt`

```txt
╔══════════════════════════════════════════════════════════════╗
║                   CREDENCIALES DE ACCESO                      ║
║                    CLÍNICA DENTAL SYSTEM                      ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DE LA CLÍNICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nombre:           Clínica Dental Santa María
  Dominio:          santa-maria
  Plan:             Plan Profesional
  Fecha Creación:   26/11/2025 10:30
  Expira:           26/12/2025

🔐 CREDENCIALES DE ADMINISTRADOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usuario/Email:    juan@santamaria.com
  Contraseña:       Xy9@mK2#pL4$qR7!

🌐 URLS DE ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Panel Admin:      https://clinica-dental-backend.onrender.com/admin/
  API:              https://clinica-dental-backend.onrender.com/api/

💳 INFORMACIÓN DEL PAGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Método:           Stripe
  Monto:            $99.00
  Transacción ID:   cs_xxx...
  Fecha:            26/11/2025 10:30

⚠️  IMPORTANTE - LEE ESTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. CAMBIA LA CONTRASEÑA inmediatamente después del primer acceso
  2. Este archivo contiene información sensible - guárdalo en un lugar seguro
  3. No compartas estas credenciales con nadie
  4. Puedes descargar este archivo solo hasta: 03/12/2025 10:30
  
¡Bienvenido a Clínica Dental System!
```

### 6. Listar Planes Disponibles (Público)
```http
GET /api/tenants/planes/
```

## 🎨 Implementación Frontend

### **1. Servicio de API**

```typescript
// src/services/registroService.ts
import axiosCore from './axios-core';

interface DatosRegistro {
  nombre_clinica: string;
  dominio_deseado: string;
  nombre_contacto: string;
  email: string;
  telefono: string;
  cargo?: string;
  direccion?: string;
  ciudad?: string;
  pais?: string;
  plan_solicitado: number;
  mensaje?: string;
}

interface RespuestaCreacion {
  solicitud_id: number;
  token: string;
  siguiente_paso: string;
  message: string;
  datos: any;
}

interface RespuestaIniciarPago {
  payment_url: string;
  payment_id: string;
  solicitud_id: number;
  message: string;
}

interface RespuestaConfirmarPago {
  solicitud_id: number;
  clinica_id: number;
  clinica_nombre: string;
  dominio: string;
  download_url: string;
  token: string;
  message: string;
}

export const registroService = {
  // Listar planes disponibles
  obtenerPlanes: async () => {
    const response = await axiosCore.get('/tenants/planes/');
    return response.data;
  },

  // Crear solicitud de registro
  crearSolicitud: async (datos: DatosRegistro): Promise<RespuestaCreacion> => {
    const response = await axiosCore.post('/tenants/solicitudes/', datos);
    return response.data;
  },

  // Iniciar proceso de pago
  iniciarPago: async (
    solicitudId: number,
    metodoPago: 'STRIPE' | 'PAYPAL' | 'MERCADOPAGO',
    returnUrl: string,
    cancelUrl: string
  ): Promise<RespuestaIniciarPago> => {
    const response = await axiosCore.post(
      `/tenants/solicitudes/${solicitudId}/iniciar_pago/`,
      {
        metodo_pago: metodoPago,
        return_url: returnUrl,
        cancel_url: cancelUrl,
      }
    );
    return response.data;
  },

  // Confirmar pago (callback)
  confirmarPago: async (solicitudId: number, paymentId?: string): Promise<RespuestaConfirmarPago> => {
    const params = paymentId ? `?payment_id=${paymentId}` : '';
    const response = await axiosCore.post(
      `/tenants/solicitudes/${solicitudId}/confirmar_pago/${params}`
    );
    return response.data;
  },

  // Verificar estado
  verificarEstado: async (solicitudId: number) => {
    const response = await axiosCore.get(
      `/tenants/solicitudes/${solicitudId}/verificar_estado/`
    );
    return response.data;
  },

  // Descargar credenciales (retorna blob para descarga directa)
  descargarCredenciales: async (solicitudId: number, token: string) => {
    const response = await axiosCore.get(
      `/tenants/solicitudes/${solicitudId}/descargar_credenciales/?token=${token}`,
      { responseType: 'blob' }
    );
    return response.data;
  },
};
```

### **2. Componente: Formulario de Registro**

```tsx
// src/pages/RegistroClinica.tsx
import React, { useState, useEffect } from 'react';
import { registroService } from '../services/registroService';
import { useNavigate } from 'react-router-dom';

export const RegistroClinica: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: Form, 2: Pago, 3: Descarga
  const [planes, setPlanes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre_clinica: '',
    dominio_deseado: '',
    nombre_contacto: '',
    email: '',
    telefono: '',
    cargo: '',
    direccion: '',
    ciudad: '',
    pais: '',
    plan_solicitado: 0,
    mensaje: '',
  });
  const [solicitudId, setSolicitudId] = useState<number | null>(null);
  const [token, setToken] = useState<string>('');

  useEffect(() => {
    cargarPlanes();
  }, []);

  const cargarPlanes = async () => {
    try {
      const data = await registroService.obtenerPlanes();
      setPlanes(data);
    } catch (error) {
      console.error('Error cargando planes:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const respuesta = await registroService.crearSolicitud(formData);
      setSolicitudId(respuesta.solicitud_id);
      setToken(respuesta.token);
      setStep(2);
    } catch (error: any) {
      alert(error.response?.data?.message || 'Error creando solicitud');
    } finally {
      setLoading(false);
    }
  };

  const handlePagar = async (metodoPago: 'STRIPE' | 'PAYPAL' | 'MERCADOPAGO') => {
    if (!solicitudId) return;

    setLoading(true);
    try {
      const returnUrl = `${window.location.origin}/registro/confirmacion/${solicitudId}`;
      const cancelUrl = `${window.location.origin}/registro/cancelado`;

      const respuesta = await registroService.iniciarPago(
        solicitudId,
        metodoPago,
        returnUrl,
        cancelUrl
      );

      // Redirigir a la pasarela de pago
      window.location.href = respuesta.payment_url;
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error iniciando pago');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Registro de Nueva Clínica</h1>

      {/* PASO 1: Formulario */}
      {step === 1 && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 font-semibold">Nombre de la Clínica *</label>
              <input
                type="text"
                required
                className="w-full border rounded px-3 py-2"
                value={formData.nombre_clinica}
                onChange={(e) => setFormData({ ...formData, nombre_clinica: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 font-semibold">Dominio Deseado *</label>
              <div className="flex items-center">
                <input
                  type="text"
                  required
                  pattern="[a-z0-9-]+"
                  className="w-full border rounded px-3 py-2"
                  placeholder="mi-clinica"
                  value={formData.dominio_deseado}
                  onChange={(e) => setFormData({ ...formData, dominio_deseado: e.target.value.toLowerCase() })}
                />
                <span className="ml-2 text-gray-600">.clinica.com</span>
              </div>
            </div>

            <div>
              <label className="block mb-2 font-semibold">Nombre de Contacto *</label>
              <input
                type="text"
                required
                className="w-full border rounded px-3 py-2"
                value={formData.nombre_contacto}
                onChange={(e) => setFormData({ ...formData, nombre_contacto: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 font-semibold">Email *</label>
              <input
                type="email"
                required
                className="w-full border rounded px-3 py-2"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 font-semibold">Teléfono *</label>
              <input
                type="tel"
                required
                className="w-full border rounded px-3 py-2"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 font-semibold">Cargo</label>
              <input
                type="text"
                className="w-full border rounded px-3 py-2"
                value={formData.cargo}
                onChange={(e) => setFormData({ ...formData, cargo: e.target.value })}
              />
            </div>

            <div className="col-span-2">
              <label className="block mb-2 font-semibold">Plan *</label>
              <div className="grid grid-cols-3 gap-4">
                {planes.map((plan: any) => (
                  <div
                    key={plan.id}
                    onClick={() => setFormData({ ...formData, plan_solicitado: plan.id })}
                    className={`border rounded p-4 cursor-pointer transition ${
                      formData.plan_solicitado === plan.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    <h3 className="font-bold text-lg">{plan.nombre}</h3>
                    <p className="text-2xl font-bold text-blue-600">${plan.precio}</p>
                    <p className="text-sm text-gray-600">{plan.tipo_display}</p>
                    <p className="text-sm mt-2">{plan.descripcion}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !formData.plan_solicitado}
            className="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Procesando...' : 'Continuar al Pago'}
          </button>
        </form>
      )}

      {/* PASO 2: Seleccionar Método de Pago */}
      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Selecciona Método de Pago</h2>
          <p className="text-gray-600">
            Solicitud creada exitosamente. Elige tu método de pago preferido:
          </p>

          <div className="grid grid-cols-3 gap-4 mt-6">
            <button
              onClick={() => handlePagar('STRIPE')}
              disabled={loading}
              className="border-2 border-gray-300 rounded p-6 hover:border-blue-500 hover:bg-blue-50 transition"
            >
              <img src="/stripe-logo.png" alt="Stripe" className="h-12 mx-auto mb-2" />
              <p className="font-semibold">Tarjeta de Crédito</p>
              <p className="text-sm text-gray-600">Stripe</p>
            </button>

            <button
              onClick={() => handlePagar('PAYPAL')}
              disabled={loading}
              className="border-2 border-gray-300 rounded p-6 hover:border-blue-500 hover:bg-blue-50 transition"
            >
              <img src="/paypal-logo.png" alt="PayPal" className="h-12 mx-auto mb-2" />
              <p className="font-semibold">PayPal</p>
              <p className="text-sm text-gray-600">Cuenta PayPal</p>
            </button>

            <button
              onClick={() => handlePagar('MERCADOPAGO')}
              disabled={loading}
              className="border-2 border-gray-300 rounded p-6 hover:border-blue-500 hover:bg-blue-50 transition"
            >
              <img src="/mp-logo.png" alt="MercadoPago" className="h-12 mx-auto mb-2" />
              <p className="font-semibold">MercadoPago</p>
              <p className="text-sm text-gray-600">América Latina</p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

### **3. Componente: Confirmación y Descarga**

```tsx
// src/pages/RegistroConfirmacion.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { registroService } from '../services/registroService';

export const RegistroConfirmacion: React.FC = () => {
  const { solicitudId } = useParams<{ solicitudId: string }>();
  const [searchParams] = useSearchParams();
  const [estado, setEstado] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    verificarPago();
  }, []);

  const verificarPago = async () => {
    const paymentId = searchParams.get('session_id') || searchParams.get('payment_id');
    
    try {
      // Confirmar pago
      const confirmacion = await registroService.confirmarPago(
        Number(solicitudId),
        paymentId || undefined
      );

      // Verificar estado
      const estadoActual = await registroService.verificarEstado(Number(solicitudId));
      setEstado(estadoActual);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Error verificando pago');
    } finally {
      setLoading(false);
    }
  };

  const handleDescargar = async () => {
    if (!estado?.token) return;

    try {
      const blob = await registroService.descargarCredenciales(
        Number(solicitudId),
        estado.token
      );

      // Crear link de descarga
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `credenciales_${estado.dominio}_${new Date().toISOString().split('T')[0]}.txt`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error descargando credenciales');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando pago y creando tu clínica...</p>
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
            <p className="text-green-600">Tu clínica ha sido creada automáticamente</p>
          </div>
        </div>

        <div className="space-y-2 mt-4">
          <p><strong>Clínica:</strong> {estado?.clinica_nombre}</p>
          <p><strong>Dominio:</strong> {estado?.dominio}</p>
          <p><strong>Fecha de pago:</strong> {new Date(estado?.fecha_pago).toLocaleString()}</p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded p-6">
        <h3 className="text-xl font-bold mb-4">📥 Descarga tus Credenciales</h3>
        <p className="mb-4 text-gray-700">
          Hemos generado automáticamente un usuario administrador con una contraseña segura.
          Descarga el archivo TXT con tus credenciales de acceso.
        </p>
        
        <button
          onClick={handleDescargar}
          className="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700 flex items-center justify-center"
        >
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          Descargar Credenciales (TXT)
        </button>

        <p className="mt-4 text-sm text-gray-600">
          ⚠️ <strong>Importante:</strong> Guarda este archivo en un lugar seguro y cambia la contraseña
          después del primer inicio de sesión.
        </p>
      </div>

      <div className="mt-6 text-center">
        <p className="text-gray-600">
          Recibirás un email con el link de descarga. El link es válido por 7 días.
        </p>
      </div>
    </div>
  );
};
```

### **4. Rutas**

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { RegistroClinica } from './pages/RegistroClinica';
import { RegistroConfirmacion } from './pages/RegistroConfirmacion';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/registro" element={<RegistroClinica />} />
        <Route path="/registro/confirmacion/:solicitudId" element={<RegistroConfirmacion />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## 🔒 Configuración de Pasarelas (Backend)

Agregar en `settings.py`:

```python
# Stripe
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')

# PayPal
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', default='')
PAYPAL_SECRET = env('PAYPAL_SECRET', default='')
PAYPAL_MODE = env('PAYPAL_MODE', default='sandbox')  # 'sandbox' o 'live'

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN = env('MERCADOPAGO_ACCESS_TOKEN', default='')
```

## 📝 Estados de Solicitud

| Estado | Descripción |
|--------|-------------|
| `PENDIENTE_PAGO` | Solicitud creada, esperando pago |
| `PAGO_PROCESANDO` | Usuario redirigido a pasarela de pago |
| `PAGO_EXITOSO` | Pago verificado, creando clínica |
| `COMPLETADA` | Clínica creada, credenciales disponibles |
| `PAGO_FALLIDO` | Pago rechazado o fallido |
| `CANCELADA` | Solicitud cancelada por usuario |

## ✅ Características Implementadas

- ✅ Creación automática de clínica tras pago
- ✅ Generación automática de usuario admin
- ✅ Contraseña aleatoria segura (16 caracteres)
- ✅ Descarga de credenciales en TXT
- ✅ Token de descarga con expiración (7 días)
- ✅ Soporte para Stripe, PayPal, MercadoPago
- ✅ Email con link de descarga
- ✅ Verificación automática de pago
- ✅ Creación de schema + dominio
- ✅ Activación automática del plan

## 🎯 Próximos Pasos

1. Configurar credenciales de pasarelas en Render
2. Probar flujo completo en desarrollo
3. Configurar webhooks de pasarelas para confirmación automática
4. Personalizar emails con plantillas HTML
5. Agregar página de landing para mostrar planes
