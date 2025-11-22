# 📦 GUÍA DE INTEGRACIÓN - MÓDULO INVENTARIO

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

El módulo de inventario gestiona **insumos/materiales dentales** y sus **categorías**. 

### ⚠️ CAMBIOS IMPORTANTES

**El backend retorna arrays directos** (sin paginación), excepto el endpoint de bitácora:

```javascript
// ✅ CORRECTO - Formato actual
GET /api/inventario/insumos/
→ [{id: 1, ...}, {id: 2, ...}]

// ❌ INCORRECTO - Ya NO se usa este formato
GET /api/inventario/insumos/
→ {count: 10, results: [...]}
```

---

## 🌐 ENDPOINTS DISPONIBLES

### Base URL
```
https://clinica-dental-backend.onrender.com/api/inventario/
```

### 📊 Categorías de Insumos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/categorias/` | Listar todas las categorías |
| `POST` | `/categorias/` | Crear nueva categoría |
| `GET` | `/categorias/{id}/` | Obtener detalle de categoría |
| `PUT` | `/categorias/{id}/` | Actualizar categoría |
| `PATCH` | `/categorias/{id}/` | Actualizar parcialmente |
| `DELETE` | `/categorias/{id}/` | Eliminar categoría |

**Búsqueda y filtros:**
- `?search=resinas` - Buscar por nombre o descripción
- `?ordering=nombre` - Ordenar por campo
- `?ordering=-creado` - Ordenar descendente

### 📦 Insumos/Materiales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/insumos/` | Listar todos los insumos |
| `POST` | `/insumos/` | Crear nuevo insumo |
| `GET` | `/insumos/{id}/` | Obtener detalle de insumo |
| `PUT` | `/insumos/{id}/` | Actualizar insumo completo |
| `PATCH` | `/insumos/{id}/` | Actualizar parcialmente |
| `DELETE` | `/insumos/{id}/` | Eliminar insumo |
| `GET` | `/insumos/bajo_stock/` | ⚠️ Insumos que requieren reposición |
| `POST` | `/insumos/{id}/ajustar_stock/` | ➕➖ Ajustar stock (entrada/salida) |

**Filtros disponibles:**
- `?categoria=1` - Filtrar por categoría (ID)
- `?activo=true` - Solo insumos activos
- `?search=resina` - Buscar por código, nombre, descripción o proveedor
- `?ordering=nombre` - Ordenar por nombre
- `?ordering=-precio_venta` - Ordenar por precio descendente
- `?ordering=stock_actual` - Ordenar por stock

---

## 📊 ESTRUCTURA DE DATOS

### 1️⃣ Categoría de Insumo

#### Respuesta de `GET /api/inventario/categorias/`

```json
[
  {
    "id": 1,
    "nombre": "Materiales Dentales",
    "descripcion": "Resinas, amalgamas, cementos",
    "activo": true,
    "total_insumos": 5,
    "creado": "2025-11-20T10:00:00Z",
    "actualizado": "2025-11-20T10:00:00Z"
  }
]
```

#### Crear/Actualizar categoría - `POST/PUT /api/inventario/categorias/`

```json
{
  "nombre": "Anestésicos",
  "descripcion": "Anestesia local y tópica",
  "activo": true
}
```

**Campos:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | `string` | ✅ Sí | Nombre único de la categoría |
| `descripcion` | `string` | ❌ No | Descripción opcional |
| `activo` | `boolean` | ❌ No | Estado (default: `true`) |
| `total_insumos` | `number` | 🔒 Read-only | Contador automático |
| `creado` | `datetime` | 🔒 Read-only | Fecha de creación |
| `actualizado` | `datetime` | 🔒 Read-only | Fecha de última actualización |

---

### 2️⃣ Insumo/Material

#### Respuesta de `GET /api/inventario/insumos/` (Listado)

**⚠️ IMPORTANTE:** El listado usa un serializer simplificado para mejor rendimiento.

```json
[
  {
    "id": 531,
    "codigo": "RES-A2-001",
    "nombre": "Resina Compuesta A2",
    "categoria_nombre": "Materiales Dentales",
    "precio_venta": "75.00",
    "stock_actual": "25.00",
    "unidad_medida": "unidad",
    "requiere_reposicion": false,
    "activo": true
  },
  {
    "id": 534,
    "codigo": "AML-001",
    "nombre": "Amalgama Dental",
    "categoria_nombre": "Materiales Dentales",
    "precio_venta": "95.00",
    "stock_actual": "5.00",
    "unidad_medida": "unidad",
    "requiere_reposicion": true,
    "activo": true
  }
]
```

#### Respuesta de `GET /api/inventario/insumos/{id}/` (Detalle)

**⚠️ El detalle incluye TODOS los campos:**

```json
{
  "id": 531,
  "categoria": 1,
  "categoria_nombre": "Materiales Dentales",
  "codigo": "RES-A2-001",
  "nombre": "Resina Compuesta A2",
  "descripcion": "Resina fotopolimerizable de alta calidad, tono A2",
  "precio_costo": "45.00",
  "precio_venta": "75.00",
  "margen_ganancia": "66.67",
  "stock_actual": "25.00",
  "stock_minimo": "10.00",
  "requiere_reposicion": false,
  "unidad_medida": "unidad",
  "proveedor": "Dental Supply Co.",
  "activo": true,
  "creado": "2025-11-20T10:00:00Z",
  "actualizado": "2025-11-22T15:30:00Z"
}
```

#### Crear/Actualizar insumo - `POST/PUT /api/inventario/insumos/`

```json
{
  "categoria": 1,
  "codigo": "RES-A3-001",
  "nombre": "Resina Compuesta A3",
  "descripcion": "Resina fotopolimerizable tono A3",
  "precio_costo": "45.00",
  "precio_venta": "75.00",
  "stock_actual": "30.00",
  "stock_minimo": "10.00",
  "unidad_medida": "unidad",
  "proveedor": "Dental Supply Co.",
  "activo": true
}
```

**Campos del Insumo:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | `number` | 🔒 Read-only | ID único del insumo |
| `categoria` | `number` | ✅ Sí | ID de la categoría |
| `categoria_nombre` | `string` | 🔒 Read-only | Nombre de la categoría (automático) |
| `codigo` | `string` | ✅ Sí | Código único (SKU) - Max 50 chars |
| `nombre` | `string` | ✅ Sí | Nombre del insumo - Max 200 chars |
| `descripcion` | `string` | ❌ No | Descripción detallada |
| `precio_costo` | `decimal` | ✅ Sí | Precio de costo (≥ 0.00) |
| `precio_venta` | `decimal` | ✅ Sí | Precio de venta (≥ precio_costo) |
| `margen_ganancia` | `decimal` | 🔒 Read-only | `((venta - costo) / costo) * 100` |
| `stock_actual` | `decimal` | ❌ No | Cantidad en stock (default: 0.00) |
| `stock_minimo` | `decimal` | ❌ No | Stock mínimo antes de alerta (default: 0.00) |
| `requiere_reposicion` | `boolean` | 🔒 Read-only | `true` si `stock_actual ≤ stock_minimo` |
| `unidad_medida` | `string` | ❌ No | unidad/caja/ml/g (default: "unidad") |
| `proveedor` | `string` | ❌ No | Nombre del proveedor - Max 200 chars |
| `activo` | `boolean` | ❌ No | Estado activo/inactivo (default: `true`) |
| `creado` | `datetime` | 🔒 Read-only | Fecha de creación |
| `actualizado` | `datetime` | 🔒 Read-only | Fecha de última actualización |

---

### 3️⃣ Insumos con Stock Bajo

#### `GET /api/inventario/insumos/bajo_stock/`

Retorna SOLO los insumos donde `stock_actual ≤ stock_minimo`:

```json
[
  {
    "id": 534,
    "codigo": "AML-001",
    "nombre": "Amalgama Dental",
    "categoria_nombre": "Materiales Dentales",
    "precio_venta": "95.00",
    "stock_actual": "5.00",
    "unidad_medida": "unidad",
    "requiere_reposicion": true,
    "activo": true
  }
]
```

**⚠️ NOTA:** Si no hay insumos con stock bajo, retorna array vacío `[]`.

---

### 4️⃣ Ajustar Stock

#### `POST /api/inventario/insumos/{id}/ajustar_stock/`

**Body:**
```json
{
  "cantidad": 10,
  "motivo": "Compra a proveedor"
}
```

**Respuesta exitosa:**
```json
{
  "mensaje": "Stock ajustado exitosamente",
  "insumo": "Resina Compuesta A2",
  "stock_anterior": 25.00,
  "ajuste": 10.0,
  "stock_actual": 35.00,
  "motivo": "Compra a proveedor"
}
```

**Parámetros:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `cantidad` | `number` | ✅ Sí | Positivo = entrada, Negativo = salida |
| `motivo` | `string` | ❌ No | Razón del ajuste (ej: "Compra", "Uso en tratamiento") |

**Ejemplos:**
- `{"cantidad": 10}` → Entrada de 10 unidades
- `{"cantidad": -5, "motivo": "Uso en tratamiento"}` → Salida de 5 unidades

---

## 🔧 GUÍA DE IMPLEMENTACIÓN FRONTEND

### Paso 1: Servicio de API

```javascript
// src/services/inventarioService.js
import api from './axiosConfig';

const inventarioService = {
  // ========== CATEGORÍAS ==========
  
  getCategorias: async (params = {}) => {
    const response = await api.get('/api/inventario/categorias/', { params });
    return response.data; // Array directo
  },

  getCategoriaById: async (id) => {
    const response = await api.get(`/api/inventario/categorias/${id}/`);
    return response.data;
  },

  createCategoria: async (data) => {
    const response = await api.post('/api/inventario/categorias/', data);
    return response.data;
  },

  updateCategoria: async (id, data) => {
    const response = await api.put(`/api/inventario/categorias/${id}/`, data);
    return response.data;
  },

  deleteCategoria: async (id) => {
    await api.delete(`/api/inventario/categorias/${id}/`);
  },

  // ========== INSUMOS ==========

  getInsumos: async (params = {}) => {
    const response = await api.get('/api/inventario/insumos/', { params });
    return response.data; // Array directo
  },

  getInsumoById: async (id) => {
    const response = await api.get(`/api/inventario/insumos/${id}/`);
    return response.data;
  },

  createInsumo: async (data) => {
    const response = await api.post('/api/inventario/insumos/', data);
    return response.data;
  },

  updateInsumo: async (id, data) => {
    const response = await api.put(`/api/inventario/insumos/${id}/`, data);
    return response.data;
  },

  deleteInsumo: async (id) => {
    await api.delete(`/api/inventario/insumos/${id}/`);
  },

  // ========== FUNCIONES ESPECIALES ==========

  getInsumosBajoStock: async () => {
    const response = await api.get('/api/inventario/insumos/bajo_stock/');
    return response.data; // Array directo
  },

  ajustarStock: async (id, cantidad, motivo = '') => {
    const response = await api.post(
      `/api/inventario/insumos/${id}/ajustar_stock/`,
      { cantidad, motivo }
    );
    return response.data;
  }
};

export default inventarioService;
```

---

### Paso 2: Componente de Tabla de Insumos

```jsx
// src/components/Inventario/TablaInsumos.jsx
import React from 'react';

const TablaInsumos = ({ insumos, isLoading, onEdit, onDelete }) => {
  if (isLoading) {
    return <div>Cargando inventario...</div>;
  }

  if (!insumos || insumos.length === 0) {
    return <div>No hay insumos registrados</div>;
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Código</th>
          <th>Nombre</th>
          <th>Categoría</th>
          <th>Precio Venta</th>
          <th>Stock Actual</th>
          <th>Unidad</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {insumos.map((insumo) => (
          <tr 
            key={insumo.id}
            className={insumo.requiere_reposicion ? 'table-warning' : ''}
          >
            <td>{insumo.codigo}</td>
            <td>
              {insumo.nombre}
              {insumo.requiere_reposicion && (
                <span className="badge bg-danger ms-2">
                  ⚠️ Stock Bajo
                </span>
              )}
            </td>
            <td>{insumo.categoria_nombre}</td>
            <td>Bs. {parseFloat(insumo.precio_venta).toFixed(2)}</td>
            <td>
              <strong>{parseFloat(insumo.stock_actual).toFixed(2)}</strong>
            </td>
            <td>{insumo.unidad_medida}</td>
            <td>
              <span className={`badge ${insumo.activo ? 'bg-success' : 'bg-secondary'}`}>
                {insumo.activo ? 'Activo' : 'Inactivo'}
              </span>
            </td>
            <td>
              <button onClick={() => onEdit(insumo)}>Editar</button>
              <button onClick={() => onDelete(insumo.id)}>Eliminar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TablaInsumos;
```

---

### Paso 3: Página Principal de Inventario

```jsx
// src/pages/Inventario.jsx
import React, { useState, useEffect } from 'react';
import inventarioService from '../services/inventarioService';
import TablaInsumos from '../components/Inventario/TablaInsumos';

const Inventario = () => {
  const [insumos, setInsumos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filtros, setFiltros] = useState({
    search: '',
    categoria: '',
    activo: 'true'
  });

  // Cargar datos iniciales
  useEffect(() => {
    cargarDatos();
  }, [filtros]);

  const cargarDatos = async () => {
    setIsLoading(true);
    try {
      // ✅ Backend retorna arrays directos
      const [insumosData, categoriasData] = await Promise.all([
        inventarioService.getInsumos(filtros),
        inventarioService.getCategorias()
      ]);

      setInsumos(insumosData);
      setCategorias(categoriasData);
    } catch (error) {
      console.error('Error al cargar inventario:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (insumo) => {
    // Abrir modal de edición
    console.log('Editar insumo:', insumo);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Eliminar este insumo?')) {
      try {
        await inventarioService.deleteInsumo(id);
        cargarDatos(); // Recargar lista
      } catch (error) {
        console.error('Error al eliminar:', error);
      }
    }
  };

  return (
    <div className="inventario-page">
      <h1>Inventario de Insumos</h1>

      {/* Filtros */}
      <div className="filtros">
        <input
          type="text"
          placeholder="Buscar por código o nombre..."
          value={filtros.search}
          onChange={(e) => setFiltros({ ...filtros, search: e.target.value })}
        />
        
        <select
          value={filtros.categoria}
          onChange={(e) => setFiltros({ ...filtros, categoria: e.target.value })}
        >
          <option value="">Todas las categorías</option>
          {categorias.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nombre}
            </option>
          ))}
        </select>

        <select
          value={filtros.activo}
          onChange={(e) => setFiltros({ ...filtros, activo: e.target.value })}
        >
          <option value="">Todos</option>
          <option value="true">Solo activos</option>
          <option value="false">Solo inactivos</option>
        </select>
      </div>

      {/* Tabla */}
      <TablaInsumos
        insumos={insumos}
        isLoading={isLoading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default Inventario;
```

---

### Paso 4: Componente de Ajuste de Stock

```jsx
// src/components/Inventario/AjustarStock.jsx
import React, { useState } from 'react';
import inventarioService from '../../services/inventarioService';

const AjustarStock = ({ insumo, onSuccess, onCancel }) => {
  const [cantidad, setCantidad] = useState('');
  const [motivo, setMotivo] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!cantidad || cantidad === '0') {
      alert('Ingrese una cantidad válida');
      return;
    }

    setIsLoading(true);
    try {
      const resultado = await inventarioService.ajustarStock(
        insumo.id,
        parseFloat(cantidad),
        motivo
      );

      alert(`✅ ${resultado.mensaje}\nNuevo stock: ${resultado.stock_actual}`);
      onSuccess();
    } catch (error) {
      console.error('Error al ajustar stock:', error);
      alert('❌ Error al ajustar el stock');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal">
      <h2>Ajustar Stock: {insumo.nombre}</h2>
      <p>Stock actual: <strong>{insumo.stock_actual} {insumo.unidad_medida}</strong></p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Cantidad (+ entrada / - salida):</label>
          <input
            type="number"
            step="0.01"
            value={cantidad}
            onChange={(e) => setCantidad(e.target.value)}
            placeholder="Ej: 10 o -5"
            required
          />
          <small>
            Ingrese número positivo para entrada o negativo para salida
          </small>
        </div>

        <div className="form-group">
          <label>Motivo (opcional):</label>
          <input
            type="text"
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            placeholder="Ej: Compra, Uso en tratamiento"
            maxLength={200}
          />
        </div>

        <div className="form-actions">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Ajustando...' : 'Ajustar Stock'}
          </button>
          <button type="button" onClick={onCancel}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default AjustarStock;
```

---

### Paso 5: Widget de Alertas de Stock Bajo

```jsx
// src/components/Dashboard/StockBajoWidget.jsx
import React, { useState, useEffect } from 'react';
import inventarioService from '../../services/inventarioService';

const StockBajoWidget = () => {
  const [insumosBajoStock, setInsumosBajoStock] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    cargarStockBajo();
  }, []);

  const cargarStockBajo = async () => {
    try {
      const data = await inventarioService.getInsumosBajoStock();
      setInsumosBajoStock(data);
    } catch (error) {
      console.error('Error al cargar stock bajo:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div>Cargando...</div>;
  }

  return (
    <div className="widget stock-bajo-widget">
      <h3>⚠️ Insumos con Stock Bajo</h3>
      
      {insumosBajoStock.length === 0 ? (
        <p className="text-success">✅ Todos los insumos tienen stock suficiente</p>
      ) : (
        <ul className="list-group">
          {insumosBajoStock.map((insumo) => (
            <li key={insumo.id} className="list-group-item list-group-item-warning">
              <strong>{insumo.nombre}</strong><br />
              <small>
                Stock: {insumo.stock_actual} {insumo.unidad_medida} 
                (Código: {insumo.codigo})
              </small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default StockBajoWidget;
```

---

## 🔍 EJEMPLOS DE INTEGRACIÓN

### Ejemplo 1: Crear Nuevo Insumo

```jsx
const CrearInsumo = () => {
  const [formData, setFormData] = useState({
    categoria: '',
    codigo: '',
    nombre: '',
    descripcion: '',
    precio_costo: '',
    precio_venta: '',
    stock_actual: '0',
    stock_minimo: '5',
    unidad_medida: 'unidad',
    proveedor: '',
    activo: true
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const nuevoInsumo = await inventarioService.createInsumo(formData);
      alert(`✅ Insumo creado: ${nuevoInsumo.nombre}`);
      // Limpiar formulario o redirigir
    } catch (error) {
      if (error.response?.data) {
        // Mostrar errores de validación
        Object.entries(error.response.data).forEach(([campo, mensajes]) => {
          alert(`${campo}: ${mensajes.join(', ')}`);
        });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Campos del formulario */}
    </form>
  );
};
```

---

### Ejemplo 2: Búsqueda en Tiempo Real

```jsx
const BuscarInsumos = () => {
  const [busqueda, setBusqueda] = useState('');
  const [resultados, setResultados] = useState([]);

  useEffect(() => {
    const buscar = async () => {
      if (busqueda.length >= 3) {
        const data = await inventarioService.getInsumos({ 
          search: busqueda 
        });
        setResultados(data);
      } else {
        setResultados([]);
      }
    };

    const timer = setTimeout(buscar, 300); // Debounce
    return () => clearTimeout(timer);
  }, [busqueda]);

  return (
    <div>
      <input
        type="text"
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar insumo..."
      />
      
      <ul>
        {resultados.map((insumo) => (
          <li key={insumo.id}>
            {insumo.codigo} - {insumo.nombre} 
            (Stock: {insumo.stock_actual})
          </li>
        ))}
      </ul>
    </div>
  );
};
```

---

### Ejemplo 3: Filtros Múltiples

```jsx
const FiltrarInsumos = () => {
  const [filtros, setFiltros] = useState({
    categoria: '',
    activo: 'true',
    search: '',
    ordering: 'nombre'
  });

  const aplicarFiltros = async () => {
    const params = {};
    
    if (filtros.categoria) params.categoria = filtros.categoria;
    if (filtros.activo) params.activo = filtros.activo;
    if (filtros.search) params.search = filtros.search;
    if (filtros.ordering) params.ordering = filtros.ordering;

    const insumos = await inventarioService.getInsumos(params);
    // Procesar resultados
  };

  return (
    <div>
      {/* Controles de filtro */}
      <button onClick={aplicarFiltros}>Aplicar Filtros</button>
    </div>
  );
};
```

---

## ⚠️ MANEJO DE ERRORES

### Errores Comunes

```javascript
try {
  await inventarioService.createInsumo(data);
} catch (error) {
  if (error.response) {
    // Error del servidor (4xx, 5xx)
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        // Validación fallida
        console.error('Errores de validación:', data);
        // data puede ser: { codigo: ["Ya existe un insumo con este código."] }
        break;

      case 401:
        // No autenticado
        console.error('Token expirado o inválido');
        // Redirigir a login
        break;

      case 403:
        // Sin permisos
        console.error('No tiene permisos para esta acción');
        break;

      case 404:
        // No encontrado
        console.error('Insumo no encontrado');
        break;

      case 500:
        // Error del servidor
        console.error('Error interno del servidor');
        break;

      default:
        console.error('Error desconocido:', status);
    }
  } else if (error.request) {
    // La petición fue enviada pero no hubo respuesta
    console.error('Sin respuesta del servidor');
  } else {
    // Error al configurar la petición
    console.error('Error de configuración:', error.message);
  }
}
```

---

### Validaciones del Backend

El backend valida:

1. **Código único:** No puede haber dos insumos con el mismo código
2. **Precio de venta ≥ precio de costo:** El precio de venta debe ser igual o mayor al costo
3. **Categoría válida:** La categoría debe existir y estar activa
4. **Valores numéricos positivos:** Precios y stock deben ser ≥ 0
5. **Stock suficiente:** Al ajustar stock negativo, no puede quedar negativo

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Frontend Mínimo Viable

- [ ] Servicio de API (`inventarioService.js`)
- [ ] Tabla de insumos con datos reales
- [ ] Filtro por categoría
- [ ] Búsqueda por nombre/código
- [ ] Indicador visual de stock bajo (`requiere_reposicion`)
- [ ] Formulario crear insumo
- [ ] Formulario editar insumo
- [ ] Botón eliminar con confirmación
- [ ] Widget de stock bajo en dashboard

### Funcionalidades Avanzadas

- [ ] Ajustar stock (entrada/salida)
- [ ] Historial de movimientos (si implementas modelo MovimientoInventario)
- [ ] Exportar a Excel/PDF
- [ ] Filtros avanzados (ordenamiento, múltiples criterías)
- [ ] Gráficos de stock vs tiempo
- [ ] Alertas automáticas de stock bajo
- [ ] Gestión de proveedores

---

## 🆘 SOPORTE

Si encuentras algún problema o necesitas ayuda adicional:

1. **Verificar autenticación:** Todos los endpoints requieren JWT token válido
2. **Verificar estructura de datos:** Los nombres de campos DEBEN coincidir exactamente
3. **Revisar logs del navegador:** Buscar errores 400/500 en la consola
4. **Verificar formato de respuesta:** Backend retorna arrays directos (sin paginación)

---

**✅ Documento actualizado:** 22 de Noviembre 2025  
**🔧 Versión Backend:** Django 5.2.6 + DRF 3.14.0  
**🚀 Deployment:** Render (https://clinica-dental-backend.onrender.com)
