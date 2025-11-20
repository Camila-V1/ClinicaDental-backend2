# 🎨 CÓDIGO PARA EL FRONTEND - DETECCIÓN DE SUBDOMINIOS

## 📁 Archivos a crear/modificar en el frontend

---

## 1️⃣ Crear: `src/config/tenantConfig.ts` (o `.js`)

```typescript
/**
 * Configuración para Multi-Tenancy basado en subdominios
 * Detecta automáticamente el tenant desde la URL
 */

/**
 * Extrae el tenant ID desde el hostname actual
 * 
 * Ejemplos:
 * - clinicademo1.dentaabcxy.store → 'clinicademo1'
 * - clinicaabc.dentaabcxy.store → 'clinicaabc'
 * - www.dentaabcxy.store → 'clinicademo1' (default)
 * - dentaabcxy.store → 'clinicademo1' (default)
 * - localhost:5173 → 'clinicademo1' (default)
 */
export function getTenantFromHostname(): string {
  // SSR/Node environment fallback
  if (typeof window === 'undefined') {
    return 'clinicademo1';
  }
  
  const hostname = window.location.hostname;
  
  // Desarrollo local
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Puedes cambiar esto para probar diferentes tenants localmente
    return 'clinicademo1';
  }
  
  // Producción: extraer subdominio
  const parts = hostname.split('.');
  
  // Si tiene subdominio (más de 2 partes) y no es 'www'
  if (parts.length >= 3 && parts[0] !== 'www') {
    return parts[0]; // Retorna el subdominio
  }
  
  // Default para dominio principal o www
  return 'clinicademo1';
}

/**
 * Obtiene la configuración de API para el tenant actual
 */
export function getApiConfig() {
  const tenant = getTenantFromHostname();
  
  return {
    tenant: tenant,
    apiUrl: import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com',
  };
}

/**
 * Obtiene el nombre legible del tenant actual
 */
export function getTenantName(): string {
  const tenant = getTenantFromHostname();
  
  const tenantNames: Record<string, string> = {
    'clinicademo1': 'Clínica Demo 1',
    'clinicaabc': 'Clínica ABC',
    'clinicaxyz': 'Clínica XYZ',
  };
  
  return tenantNames[tenant] || 'Clínica Dental';
}
```

---

## 2️⃣ Modificar: `src/config/axios.ts` (o donde configures axios)

```typescript
import axios from 'axios';
import { getTenantFromHostname } from './tenantConfig';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// ✅ Interceptor para agregar token Y tenant ID
axiosInstance.interceptors.request.use(
  (config) => {
    // 1. Agregar token de autenticación
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 2. ⭐ NUEVO: Agregar tenant ID desde el subdominio
    const tenantId = getTenantFromHostname();
    config.headers['X-Tenant-ID'] = tenantId;
    
    // Log para debugging (puedes remover en producción)
    console.log('📡 Request a:', config.url);
    console.log('🏢 Tenant ID:', tenantId);
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de respuestas (si lo tienes)
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    // ... tu lógica de refresh token, etc.
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## 3️⃣ Opcional: Modificar `src/App.tsx` para mostrar tenant actual

```typescript
import { useEffect } from 'react';
import { getTenantFromHostname, getTenantName } from './config/tenantConfig';

function App() {
  useEffect(() => {
    const tenant = getTenantFromHostname();
    const tenantName = getTenantName();
    
    console.log('🏥 Tenant actual:', tenant);
    console.log('🏥 Nombre clínica:', tenantName);
    
    // Opcional: Cambiar el título de la página
    document.title = `${tenantName} - Sistema de Gestión`;
  }, []);

  return (
    <div className="App">
      {/* Tu aplicación */}
    </div>
  );
}

export default App;
```

---

## 4️⃣ Opcional: Componente para mostrar nombre de clínica en header

```typescript
// src/components/TenantHeader.tsx
import { getTenantName } from '../config/tenantConfig';

export function TenantHeader() {
  const tenantName = getTenantName();
  
  return (
    <div className="tenant-header">
      <h1>{tenantName}</h1>
      <p className="text-sm text-gray-500">Sistema de Gestión Clínica</p>
    </div>
  );
}
```

---

## 5️⃣ Variables de Entorno (`.env`)

```bash
# Backend API URL (sin cambios)
VITE_API_URL=https://clinica-dental-backend.onrender.com
```

**No necesitas cambiar nada más**, el tenant se detecta automáticamente del subdominio.

---

## 🧪 CÓMO PROBAR LOCALMENTE

### Opción 1: Editar archivo hosts (simulación de subdominios)

**Windows: `C:\Windows\System32\drivers\etc\hosts`**

```
127.0.0.1  clinicademo1.localhost
127.0.0.1  clinicaabc.localhost
127.0.0.1  clinicaxyz.localhost
```

Luego accede a:
- `http://clinicademo1.localhost:5173`
- `http://clinicaabc.localhost:5173`

### Opción 2: Cambiar manualmente en `tenantConfig.ts`

```typescript
export function getTenantFromHostname(): string {
  if (typeof window === 'undefined') return 'clinicaabc'; // ⬅️ Cambiar aquí
  
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'clinicaabc'; // ⬅️ Y aquí para probar diferentes tenants
  }
  
  // ... resto del código
}
```

### Opción 3: Query parameter temporal (para testing)

```typescript
export function getTenantFromHostname(): string {
  if (typeof window === 'undefined') return 'clinicademo1';
  
  // ⭐ Para testing: permite ?tenant=clinicaabc
  const urlParams = new URLSearchParams(window.location.search);
  const tenantParam = urlParams.get('tenant');
  if (tenantParam) {
    return tenantParam;
  }
  
  const hostname = window.location.hostname;
  // ... resto del código
}
```

Entonces puedes probar:
- `http://localhost:5173/?tenant=clinicademo1`
- `http://localhost:5173/?tenant=clinicaabc`

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Archivos a crear:
- [ ] `src/config/tenantConfig.ts` con función `getTenantFromHostname()`

### Archivos a modificar:
- [ ] `src/config/axios.ts` (agregar header `X-Tenant-ID`)
- [ ] `src/App.tsx` (opcional: mostrar tenant actual en console)

### Probar:
- [ ] Abrir DevTools → Console → Ver "🏢 Tenant ID: ..."
- [ ] Abrir DevTools → Network → Ver header `X-Tenant-ID` en requests
- [ ] Acceder a diferentes subdominios y verificar que cambia el tenant

---

## 🎯 RESUMEN

**Cambios mínimos necesarios:**

1. ✅ Crear `tenantConfig.ts` (1 archivo nuevo)
2. ✅ Agregar 3 líneas en axios config (1 archivo modificado)

**Total de código nuevo:** ~50 líneas

**Tiempo estimado:** 15-20 minutos

---

## 🐛 DEBUGGING

Si tienes problemas, verifica en DevTools:

```javascript
// En la consola del navegador:
console.log('Hostname:', window.location.hostname);
console.log('Tenant detectado:', getTenantFromHostname());
```

En Network tab, verifica que las peticiones incluyan:
```
Headers:
  X-Tenant-ID: clinicaabc
  Authorization: Bearer <token>
```
