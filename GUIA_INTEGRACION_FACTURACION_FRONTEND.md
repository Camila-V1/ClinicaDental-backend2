# 💰 GUÍA DE INTEGRACIÓN - MÓDULO FACTURACIÓN

**Fecha:** 22 de Noviembre 2025  
**Backend:** Django REST Framework 3.14.0  
**Versión:** 1.0

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Estructura de Datos](#estructura-de-datos)
4. [Guía de Implementación Frontend](#guía-de-implementación-frontend)
5. [Ejemplos de Integración](#ejemplos-de-integración)
6. [Manejo de Errores](#manejo-de-errores)

---

## 🎯 RESUMEN EJECUTIVO

El módulo de facturación gestiona **facturas** y **pagos** de tratamientos dentales.

### ⚠️ CAMBIOS IMPORTANTES

**El backend retorna arrays directos** (sin paginación):

```javascript
// ✅ CORRECTO - Formato actual
GET /api/facturacion/facturas/
→ [{id: 1, ...}, {id: 2, ...}]

// ❌ INCORRECTO - Ya NO se usa
GET /api/facturacion/facturas/
→ {count: 3, results: [...]}
```

### 🔐 Permisos por Rol

| Rol | Permisos |
|-----|----------|
| **Admin** | Ver todas las facturas/pagos, cancelar, anular |
| **Odontólogo** | Ver facturas/pagos de sus pacientes |
| **Paciente** | Solo ver sus propias facturas/pagos |

---

## 🌐 ENDPOINTS DISPONIBLES

### Base URL
```
https://clinica-dental-backend.onrender.com/api/facturacion/
```

### 🧾 Facturas

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| `GET` | `/facturas/` | Listar facturas | Según rol |
| `POST` | `/facturas/` | Crear factura desde presupuesto | Admin/Doctor |
| `GET` | `/facturas/{id}/` | Detalle de factura | Según rol |
| `PUT` | `/facturas/{id}/` | Actualizar factura | Admin |
| `DELETE` | `/facturas/{id}/` | Eliminar factura | Admin |
| `POST` | `/facturas/{id}/marcar_pagada/` | Marcar como pagada | Admin |
| `POST` | `/facturas/{id}/cancelar/` | Cancelar factura | Solo Admin |
| `GET` | `/facturas/estado_cuenta/` | Estado de cuenta del paciente | Solo Paciente |
| `GET` | `/facturas/mis_facturas/` | Facturas del paciente autenticado | Solo Paciente |
| `GET` | `/facturas/reporte_financiero/` | Reporte financiero | Admin/Doctor |

**Filtros:**
- `?search=nombre` - Buscar por nombre de paciente
- `?estado=PENDIENTE` - Filtrar por estado (PENDIENTE/PAGADA/ANULADA)
- `?fecha_desde=2025-01-01` - Filtrar desde fecha
- `?fecha_hasta=2025-12-31` - Filtrar hasta fecha

---

### 💳 Pagos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| `GET` | `/pagos/` | Listar pagos | Según rol |
| `POST` | `/pagos/` | Registrar nuevo pago | Admin/Doctor |
| `GET` | `/pagos/{id}/` | Detalle de pago | Según rol |
| `POST` | `/pagos/{id}/anular/` | Anular pago | Solo Admin |
| `GET` | `/pagos/por_factura/?factura_id=X` | Pagos de una factura | Según rol |

---

## 📊 ESTRUCTURA DE DATOS

### 1️⃣ Factura (Listado)

#### Respuesta de `GET /api/facturacion/facturas/`

```json
[
  {
    "id": 162,
    "paciente_nombre": "Laura Rodríguez",
    "estado": "PENDIENTE",
    "estado_display": "Pendiente de Pago",
    "monto_total": "225.00",
    "monto_pagado": "0.00",
    "saldo_pendiente": "225.00",
    "fecha_emision": "2025-11-22T10:30:00Z",
    "total_pagos": 0,
    
    "numero": 162,
    "fecha": "2025-11-22T10:30:00Z",
    "monto": "225.00",
    "total": "225.00",
    "saldo": "225.00",
    "descripcion": "Factura por tratamiento - Presupuesto #45"
  }
]
```

**Campos del Listado:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `number` | ID único de la factura |
| `numero` | `number` | Alias de `id` (compatibilidad) |
| `paciente_nombre` | `string` | Nombre completo del paciente |
| `estado` | `string` | PENDIENTE / PAGADA / ANULADA |
| `estado_display` | `string` | Texto legible del estado |
| `monto_total` | `decimal` | Monto total de la factura |
| `monto` | `decimal` | Alias de `monto_total` |
| `total` | `decimal` | Alias de `monto_total` |
| `monto_pagado` | `decimal` | Total pagado hasta ahora |
| `saldo_pendiente` | `decimal` | Monto faltante por pagar |
| `saldo` | `decimal` | Alias de `saldo_pendiente` |
| `fecha_emision` | `datetime` | Fecha de emisión de factura |
| `fecha` | `datetime` | Alias de `fecha_emision` |
| `total_pagos` | `number` | Cantidad de pagos registrados |
| `descripcion` | `string` | Descripción automática |

---

### 2️⃣ Factura (Detalle)

#### Respuesta de `GET /api/facturacion/facturas/{id}/`

```json
{
  "id": 162,
  "estado": "PENDIENTE",
  "fecha_emision": "2025-11-22T10:30:00Z",
  "fecha_anulacion": null,
  
  "paciente": 356,
  "paciente_nombre": "Laura Rodríguez",
  "paciente_email": "laura.rodriguez@test.com",
  "paciente_ci": "7654321",
  "paciente_telefono": "71234567",
  
  "presupuesto": 45,
  "presupuesto_numero": 45,
  "presupuesto_token": "ABC123XYZ",
  
  "nit_ci": "7654321",
  "razon_social": "Laura Rodríguez",
  
  "monto_total": "225.00",
  "monto_pagado": "0.00",
  "saldo_pendiente": "225.00",
  "total_pagos": 0,
  "porcentaje_pagado": 0.0,
  
  "pagos": []
}
```

**Campos Adicionales del Detalle:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `paciente` | `number` | ID del perfil paciente |
| `paciente_email` | `string` | Email del paciente |
| `paciente_ci` | `string` | CI del paciente |
| `paciente_telefono` | `string` | Teléfono del paciente |
| `presupuesto` | `number` | ID del presupuesto asociado |
| `presupuesto_numero` | `number` | Número de presupuesto |
| `presupuesto_token` | `string` | Token de aceptación |
| `nit_ci` | `string` | NIT/CI para facturación |
| `razon_social` | `string` | Nombre/Razón social |
| `porcentaje_pagado` | `decimal` | % pagado del total |
| `pagos` | `array` | Lista de pagos registrados |
| `fecha_anulacion` | `datetime` | Fecha de anulación (null si activa) |

---

### 3️⃣ Crear Factura

#### `POST /api/facturacion/facturas/`

```json
{
  "paciente": 356,
  "presupuesto": 45,
  "monto_total": "225.00",
  "nit_ci": "7654321",
  "razon_social": "Laura Rodríguez"
}
```

**Validaciones:**
- ✅ Presupuesto debe estar en estado `ACEPTADO`
- ✅ Presupuesto no debe tener factura previa
- ⚠️ Si no se especifica `monto_total`, usa el total del presupuesto
- ⚠️ Si no se especifica `paciente`, usa el paciente del presupuesto

**Respuesta:**
```json
{
  "id": 163,
  "estado": "PENDIENTE",
  "paciente_nombre": "Laura Rodríguez",
  "monto_total": "225.00",
  "monto_pagado": "0.00",
  "saldo_pendiente": "225.00",
  "fecha_emision": "2025-11-22T15:45:00Z"
}
```

---

### 4️⃣ Pago

#### Respuesta de `GET /api/facturacion/pagos/`

```json
[
  {
    "id": 89,
    "factura": 161,
    "factura_numero": 161,
    "factura_total": "80.00",
    "paciente": 355,
    "paciente_nombre": "Carlos López",
    "paciente_email": "carlos.lopez@test.com",
    "monto_pagado": "50.00",
    "metodo_pago": "EFECTIVO",
    "estado_pago": "COMPLETADO",
    "fecha_pago": "2025-11-22T11:00:00Z",
    "referencia_transaccion": "PAGO-001",
    "notas": "Pago parcial en efectivo"
  }
]
```

**Campos del Pago:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `number` | ID único del pago |
| `factura` | `number` | ID de la factura |
| `factura_numero` | `number` | Número de factura |
| `factura_total` | `decimal` | Total de la factura |
| `paciente` | `number` | ID del perfil paciente |
| `paciente_nombre` | `string` | Nombre del paciente |
| `paciente_email` | `string` | Email del paciente |
| `monto_pagado` | `decimal` | Monto de este pago |
| `metodo_pago` | `string` | EFECTIVO / TARJETA / TRANSFERENCIA / QR |
| `estado_pago` | `string` | COMPLETADO / PENDIENTE / CANCELADO |
| `fecha_pago` | `datetime` | Fecha del pago |
| `referencia_transaccion` | `string` | Referencia o comprobante |
| `notas` | `string` | Notas adicionales |

---

### 5️⃣ Registrar Pago

#### `POST /api/facturacion/pagos/`

```json
{
  "factura": 162,
  "monto_pagado": "100.00",
  "metodo_pago": "TARJETA",
  "referencia_transaccion": "TRX-20251122-001",
  "notas": "Pago con tarjeta de débito"
}
```

**Validaciones:**
- ✅ Monto debe ser > 0
- ✅ Factura no debe estar ANULADA
- ✅ Monto no debe exceder saldo pendiente
- ⚠️ Al pagar completo, factura cambia a estado PAGADA automáticamente

**Respuesta:**
```json
{
  "id": 90,
  "factura": 162,
  "monto_pagado": "100.00",
  "metodo_pago": "TARJETA",
  "estado_pago": "COMPLETADO",
  "fecha_pago": "2025-11-22T16:00:00Z"
}
```

---

### 6️⃣ Estado de Cuenta (Solo Pacientes)

#### `GET /api/facturacion/facturas/estado_cuenta/`

```json
{
  "saldo_pendiente": 225.0,
  "monto_total": 355.0,
  "monto_pagado": 130.0,
  
  "saldo_pendiente_formatted": "$225.00",
  "monto_total_formatted": "$355.00",
  "monto_pagado_formatted": "$130.00",
  
  "total_facturado": 355.0,
  "total_pagado": 130.0,
  "total_pendiente": 225.0,
  
  "total_facturas": 3,
  "facturas_pendientes": 1,
  "facturas_pagadas": 2,
  
  "facturas": [
    {
      "id": 162,
      "paciente_nombre": "Laura Rodríguez",
      "estado": "PENDIENTE",
      "monto_total": "225.00",
      "saldo_pendiente": "225.00",
      "fecha_emision": "2025-11-22T10:30:00Z"
    }
  ]
}
```

**Uso:** Mostrar resumen financiero en perfil del paciente.

---

### 7️⃣ Reporte Financiero (Admin/Doctor)

#### `GET /api/facturacion/facturas/reporte_financiero/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30`

```json
{
  "periodo": {
    "fecha_inicio": "2025-11-01",
    "fecha_fin": "2025-11-30"
  },
  "resumen": {
    "total_facturas": 3,
    "facturas_pendientes": 1,
    "facturas_pagadas": 2,
    "facturas_canceladas": 0,
    "monto_total_facturado": 355.0,
    "monto_total_pagado": 130.0,
    "monto_pendiente": 225.0,
    "porcentaje_cobrado": 36.62
  }
}
```

---

## 🔧 GUÍA DE IMPLEMENTACIÓN FRONTEND

### Paso 1: Servicio de API

```javascript
// src/services/facturacionService.js
import api from './axiosConfig';

const facturacionService = {
  // ========== FACTURAS ==========
  
  getFacturas: async (params = {}) => {
    const response = await api.get('/api/facturacion/facturas/', { params });
    return response.data; // Array directo
  },

  getFacturaById: async (id) => {
    const response = await api.get(`/api/facturacion/facturas/${id}/`);
    return response.data;
  },

  createFactura: async (data) => {
    const response = await api.post('/api/facturacion/facturas/', data);
    return response.data;
  },

  marcarPagada: async (id) => {
    const response = await api.post(`/api/facturacion/facturas/${id}/marcar_pagada/`);
    return response.data;
  },

  cancelarFactura: async (id) => {
    const response = await api.post(`/api/facturacion/facturas/${id}/cancelar/`);
    return response.data;
  },

  // ========== PAGOS ==========

  getPagos: async (params = {}) => {
    const response = await api.get('/api/facturacion/pagos/', { params });
    return response.data; // Array directo
  },

  getPagoById: async (id) => {
    const response = await api.get(`/api/facturacion/pagos/${id}/`);
    return response.data;
  },

  registrarPago: async (data) => {
    const response = await api.post('/api/facturacion/pagos/', data);
    return response.data;
  },

  anularPago: async (id) => {
    const response = await api.post(`/api/facturacion/pagos/${id}/anular/`);
    return response.data;
  },

  getPagosPorFactura: async (facturaId) => {
    const response = await api.get('/api/facturacion/pagos/por_factura/', {
      params: { factura_id: facturaId }
    });
    return response.data;
  },

  // ========== REPORTES ==========

  getEstadoCuenta: async () => {
    // Solo para pacientes
    const response = await api.get('/api/facturacion/facturas/estado_cuenta/');
    return response.data;
  },

  getMisFacturas: async (params = {}) => {
    // Solo para pacientes
    const response = await api.get('/api/facturacion/facturas/mis_facturas/', { params });
    return response.data;
  },

  getReporteFinanciero: async (fechaInicio, fechaFin) => {
    // Solo para admin/doctor
    const response = await api.get('/api/facturacion/facturas/reporte_financiero/', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
    });
    return response.data;
  }
};

export default facturacionService;
```

---

### Paso 2: Componente Tabla de Facturas

```jsx
// src/components/Facturacion/TablaFacturas.jsx
import React from 'react';

const TablaFacturas = ({ facturas, isLoading, onDetalle, onPagar }) => {
  if (isLoading) {
    return <div>Cargando facturas...</div>;
  }

  if (!facturas || facturas.length === 0) {
    return <div>No hay facturas registradas</div>;
  }

  const getEstadoBadge = (estado) => {
    const badges = {
      'PENDIENTE': 'badge bg-warning',
      'PAGADA': 'badge bg-success',
      'ANULADA': 'badge bg-danger'
    };
    return badges[estado] || 'badge bg-secondary';
  };

  return (
    <table className="table table-hover">
      <thead>
        <tr>
          <th>N° Factura</th>
          <th>Paciente</th>
          <th>Fecha</th>
          <th>Monto Total</th>
          <th>Pagado</th>
          <th>Saldo</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {facturas.map((factura) => (
          <tr key={factura.id}>
            <td><strong>#{factura.numero || factura.id}</strong></td>
            <td>{factura.paciente_nombre}</td>
            <td>
              {new Date(factura.fecha_emision).toLocaleDateString('es-BO')}
            </td>
            <td>Bs. {parseFloat(factura.monto_total).toFixed(2)}</td>
            <td>Bs. {parseFloat(factura.monto_pagado).toFixed(2)}</td>
            <td>
              <strong className={factura.saldo_pendiente > 0 ? 'text-danger' : 'text-success'}>
                Bs. {parseFloat(factura.saldo_pendiente).toFixed(2)}
              </strong>
            </td>
            <td>
              <span className={getEstadoBadge(factura.estado)}>
                {factura.estado_display}
              </span>
            </td>
            <td>
              <button 
                className="btn btn-sm btn-info"
                onClick={() => onDetalle(factura)}
              >
                Ver Detalle
              </button>
              {factura.estado === 'PENDIENTE' && factura.saldo_pendiente > 0 && (
                <button 
                  className="btn btn-sm btn-primary ms-1"
                  onClick={() => onPagar(factura)}
                >
                  Pagar
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TablaFacturas;
```

---

### Paso 3: Modal de Registro de Pago

```jsx
// src/components/Facturacion/RegistrarPago.jsx
import React, { useState } from 'react';
import facturacionService from '../../services/facturacionService';

const RegistrarPago = ({ factura, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    monto_pagado: '',
    metodo_pago: 'EFECTIVO',
    referencia_transaccion: '',
    notas: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const monto = parseFloat(formData.monto_pagado);
    const saldoPendiente = parseFloat(factura.saldo_pendiente);

    if (monto <= 0) {
      alert('El monto debe ser mayor a 0');
      return;
    }

    if (monto > saldoPendiente) {
      alert(`El monto no puede exceder el saldo pendiente (Bs. ${saldoPendiente.toFixed(2)})`);
      return;
    }

    setIsLoading(true);
    try {
      await facturacionService.registrarPago({
        factura: factura.id,
        ...formData
      });

      alert('✅ Pago registrado exitosamente');
      onSuccess();
    } catch (error) {
      console.error('Error al registrar pago:', error);
      alert('❌ Error al registrar el pago');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal">
      <h2>Registrar Pago - Factura #{factura.numero || factura.id}</h2>
      <p><strong>Paciente:</strong> {factura.paciente_nombre}</p>
      <p><strong>Saldo Pendiente:</strong> Bs. {parseFloat(factura.saldo_pendiente).toFixed(2)}</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Monto a Pagar *</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            max={factura.saldo_pendiente}
            value={formData.monto_pagado}
            onChange={(e) => setFormData({ ...formData, monto_pagado: e.target.value })}
            placeholder="0.00"
            required
          />
        </div>

        <div className="form-group">
          <label>Método de Pago *</label>
          <select
            value={formData.metodo_pago}
            onChange={(e) => setFormData({ ...formData, metodo_pago: e.target.value })}
            required
          >
            <option value="EFECTIVO">Efectivo</option>
            <option value="TARJETA">Tarjeta</option>
            <option value="TRANSFERENCIA">Transferencia</option>
            <option value="QR">QR</option>
          </select>
        </div>

        <div className="form-group">
          <label>Referencia/Comprobante</label>
          <input
            type="text"
            value={formData.referencia_transaccion}
            onChange={(e) => setFormData({ ...formData, referencia_transaccion: e.target.value })}
            placeholder="Ej: TRX-20251122-001"
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label>Notas</label>
          <textarea
            value={formData.notas}
            onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
            placeholder="Notas adicionales..."
            rows={3}
          />
        </div>

        <div className="form-actions">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Registrando...' : 'Registrar Pago'}
          </button>
          <button type="button" onClick={onCancel}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegistrarPago;
```

---

### Paso 4: Widget de Estado de Cuenta (Pacientes)

```jsx
// src/components/Paciente/EstadoCuentaWidget.jsx
import React, { useState, useEffect } from 'react';
import facturacionService from '../../services/facturacionService';

const EstadoCuentaWidget = () => {
  const [estadoCuenta, setEstadoCuenta] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    cargarEstadoCuenta();
  }, []);

  const cargarEstadoCuenta = async () => {
    try {
      const data = await facturacionService.getEstadoCuenta();
      setEstadoCuenta(data);
    } catch (error) {
      console.error('Error al cargar estado de cuenta:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div>Cargando estado de cuenta...</div>;
  }

  if (!estadoCuenta) {
    return <div>Error al cargar datos</div>;
  }

  return (
    <div className="widget estado-cuenta-widget">
      <h3>💰 Mi Estado de Cuenta</h3>
      
      <div className="resumen-financiero">
        <div className="stat">
          <span className="label">Total Facturado:</span>
          <span className="value">Bs. {estadoCuenta.total_facturado.toFixed(2)}</span>
        </div>
        
        <div className="stat">
          <span className="label">Total Pagado:</span>
          <span className="value text-success">
            Bs. {estadoCuenta.total_pagado.toFixed(2)}
          </span>
        </div>
        
        <div className="stat">
          <span className="label">Saldo Pendiente:</span>
          <span className={`value ${estadoCuenta.saldo_pendiente > 0 ? 'text-danger' : 'text-success'}`}>
            Bs. {estadoCuenta.saldo_pendiente.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="contadores">
        <p>📄 Total Facturas: <strong>{estadoCuenta.total_facturas}</strong></p>
        <p>⏳ Pendientes: <strong>{estadoCuenta.facturas_pendientes}</strong></p>
        <p>✅ Pagadas: <strong>{estadoCuenta.facturas_pagadas}</strong></p>
      </div>

      {estadoCuenta.facturas.length > 0 && (
        <div className="facturas-pendientes">
          <h4>Facturas Pendientes</h4>
          <ul>
            {estadoCuenta.facturas.map((factura) => (
              <li key={factura.id}>
                <strong>#{factura.id}</strong> - 
                Bs. {parseFloat(factura.saldo_pendiente).toFixed(2)} 
                ({new Date(factura.fecha_emision).toLocaleDateString()})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default EstadoCuentaWidget;
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Frontend Mínimo Viable

- [ ] Servicio de API (`facturacionService.js`)
- [ ] Tabla de facturas con datos reales
- [ ] Indicador visual de estado (Pendiente/Pagada/Anulada)
- [ ] Modal de registro de pago
- [ ] Validación de montos (no exceder saldo pendiente)
- [ ] Vista de detalle de factura con lista de pagos
- [ ] Widget de estado de cuenta (pacientes)
- [ ] Filtros por estado y fecha

### Funcionalidades Avanzadas

- [ ] Historial de pagos por factura
- [ ] Exportar facturas a PDF
- [ ] Reportes financieros (admin/doctor)
- [ ] Notificaciones de facturas pendientes
- [ ] Gráficos de ingresos por mes
- [ ] Recordatorios de pago
- [ ] Impresión de recibos

---

## ⚠️ MANEJO DE ERRORES

```javascript
try {
  await facturacionService.registrarPago(data);
} catch (error) {
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        // Validación fallida
        if (data.error) {
          alert(data.error); // "El pago excede el saldo pendiente..."
        }
        break;

      case 403:
        // Sin permisos
        alert('No tiene permisos para registrar pagos');
        break;

      case 404:
        // Factura no encontrada
        alert('Factura no encontrada');
        break;

      default:
        alert('Error al procesar la solicitud');
    }
  }
}
```

---

**✅ Documento actualizado:** 22 de Noviembre 2025  
**🔧 Versión Backend:** Django 5.2.6 + DRF 3.14.0  
**🚀 Deployment:** Render (https://clinica-dental-backend.onrender.com)
