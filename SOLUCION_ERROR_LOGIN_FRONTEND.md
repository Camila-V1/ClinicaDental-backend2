# 🔧 SOLUCIÓN ERROR DE LOGIN - FRONTEND

**Fecha:** 15 de Noviembre, 2025  
**Error:** Network Error - CORS + URL incorrecta

---

## 🐛 PROBLEMA IDENTIFICADO

### **Error en Consola:**
```
❌ POST http://clinica-demo.localhost:8000/api/token/ net::ERR_FAILED
❌ No 'Access-Control-Allow-Origin' header is present
```

### **URL Incorrecta:**
```
❌ Intentando: http://clinica-demo.localhost:8000/api/token/
✅ Correcto:   http://clinica-demo.localhost:8000/public/api/token/
```

---

## ✅ SOLUCIÓN: Corregir Configuración del Frontend

### **1. Verificar `apiConfig.ts` o archivo de configuración de Axios**

**Ubicación:** `src/services/apiConfig.ts` o `src/config/api.ts`

**Buscar y corregir:**

```typescript
// ❌ INCORRECTO
const API_BASE_URL = 'http://clinica-demo.localhost:8000';

// Luego en authService:
apiClient.post('/api/token/', data);  // ❌ Falta /public

// ✅ CORRECTO - OPCIÓN 1: Agregar /public en la base URL
const API_BASE_URL = 'http://clinica-demo.localhost:8000/public';

// Luego en authService:
apiClient.post('/api/token/', data);  // ✅ Ahora apunta a /public/api/token/
```

**O OPCIÓN 2: Agregar /public en cada llamada**

```typescript
// Base URL sin /public
const API_BASE_URL = 'http://clinica-demo.localhost:8000';

// En authService.ts - Agregar /public
export const login = async (username: string, password: string) => {
  const response = await apiClient.post('/public/api/token/', {  // ✅ Agregar /public
    username,
    password
  });
  return response.data;
};
```

---

## 📋 ARCHIVO A MODIFICAR EN FRONTEND

### **Opción Recomendada: `apiConfig.ts`**

```typescript
// src/services/apiConfig.ts o src/config/api.ts

import axios from 'axios';

// ✅ CORRECCIÓN: Agregar /public a la base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://clinica-demo.localhost:8000/public';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // ✅ Importante para CORS
});

// Interceptor para agregar token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;
```

### **Luego en `authService.ts`:**

```typescript
// src/services/authService.ts

import apiClient from './apiConfig';

export const authService = {
  login: async (username: string, password: string) => {
    console.log('🔑 authService: Paso 1 - Obteniendo tokens...');
    
    // ✅ Ya no necesita /public porque está en baseURL
    const response = await apiClient.post('/api/token/', {
      username,
      password
    });
    
    return response.data;
  },

  // Para endpoints de tenant (después del login)
  getUserProfile: async () => {
    // ✅ Para tenant, usar URL diferente sin /public
    const tenantClient = axios.create({
      baseURL: 'http://clinica-demo.localhost:8000/tenant',
      withCredentials: true,
    });
    
    const response = await tenantClient.get('/api/usuarios/me/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    return response.data;
  }
};
```

---

## 🎯 ESTRUCTURA DE URLs DEL BACKEND

### **URLs Públicas (sin autenticación):**
```
✅ http://clinica-demo.localhost:8000/public/api/token/          (Login)
✅ http://clinica-demo.localhost:8000/public/api/token/refresh/  (Refresh token)
✅ http://clinica-demo.localhost:8000/public/api/recuperar-password/
```

### **URLs de Tenant (requieren autenticación JWT):**
```
✅ http://clinica-demo.localhost:8000/tenant/api/usuarios/me/
✅ http://clinica-demo.localhost:8000/tenant/api/agenda/citas/
✅ http://clinica-demo.localhost:8000/tenant/api/historial/historiales/
✅ http://clinica-demo.localhost:8000/tenant/api/tratamientos/planes/
✅ http://clinica-demo.localhost:8000/tenant/api/facturacion/facturas/
```

---

## 🔍 ALTERNATIVA: Usar Variables de Entorno

### **Crear `.env` en el frontend:**

```env
# .env
VITE_API_BASE_URL=http://clinica-demo.localhost:8000
VITE_PUBLIC_API_URL=http://clinica-demo.localhost:8000/public
VITE_TENANT_API_URL=http://clinica-demo.localhost:8000/tenant
```

### **Usar en `apiConfig.ts`:**

```typescript
// src/services/apiConfig.ts

import axios from 'axios';

// Cliente para endpoints públicos (login, registro)
export const publicApiClient = axios.create({
  baseURL: import.meta.env.VITE_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Cliente para endpoints de tenant (después de login)
export const tenantApiClient = axios.create({
  baseURL: import.meta.env.VITE_TENANT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Interceptor para agregar token a peticiones de tenant
tenantApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default {
  public: publicApiClient,
  tenant: tenantApiClient,
};
```

### **Usar en servicios:**

```typescript
// src/services/authService.ts

import { publicApiClient, tenantApiClient } from './apiConfig';

export const authService = {
  // Login usa publicApiClient
  login: async (username: string, password: string) => {
    const response = await publicApiClient.post('/api/token/', {
      username,
      password
    });
    return response.data;
  },

  // Perfil usa tenantApiClient
  getUserProfile: async () => {
    const response = await tenantApiClient.get('/api/usuarios/me/');
    return response.data;
  }
};
```

---

## 🧪 PRUEBA RÁPIDA

### **1. Verificar Backend (en una terminal):**
```bash
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO\ClinicaDental-backend2"
python manage.py runserver
```

### **2. Probar endpoint manualmente:**

**Usando PowerShell:**
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "http://clinica-demo.localhost:5173"
}

$body = @{
    username = "juan_perez"
    password = "paciente123"
} | ConvertTo-Json

# ✅ URL CORRECTA con /public
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/public/api/token/" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

**Resultado esperado:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **3. Probar desde el navegador (DevTools):**

```javascript
// Abrir consola del navegador (F12)
fetch('http://clinica-demo.localhost:8000/public/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Origin': 'http://clinica-demo.localhost:5173'
  },
  credentials: 'include',
  body: JSON.stringify({
    username: 'juan_perez',
    password: 'paciente123'
  })
})
.then(res => res.json())
.then(data => console.log('✅ Login exitoso:', data))
.catch(err => console.error('❌ Error:', err));
```

---

## 📊 CHECKLIST DE VERIFICACIÓN

- [ ] **Backend corriendo** en puerto 8000
- [ ] **CORS configurado** en `settings.py` (ya está ✅)
- [ ] **Frontend corriendo** en puerto 5173
- [ ] **URL base incluye `/public`** para endpoints públicos
- [ ] **URL base usa `/tenant`** para endpoints privados
- [ ] **`withCredentials: true`** en configuración de Axios
- [ ] **Token se envía** en header `Authorization: Bearer {token}`

---

## 🐛 TROUBLESHOOTING ADICIONAL

### **Si persiste el error después de corregir URL:**

#### 1. **Limpiar caché del navegador**
```
Ctrl + Shift + Delete → Borrar caché
O usar modo incógnito
```

#### 2. **Reiniciar servidor Django**
```bash
# Ctrl+C para detener
python manage.py runserver
```

#### 3. **Reiniciar servidor Vite**
```bash
# Ctrl+C para detener
npm run dev
```

#### 4. **Verificar que no haya proxy configurado**
En `vite.config.ts`, **NO** debe haber proxy para /api:
```typescript
// ❌ REMOVER si existe
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://clinica-demo.localhost:8000'  // ❌ QUITAR ESTO
    }
  }
});
```

#### 5. **Verificar CORS en Network tab**
Abrir DevTools → Network → Ver request a `/public/api/token/`

**Headers de respuesta debe incluir:**
```
Access-Control-Allow-Origin: http://clinica-demo.localhost:5173
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: authorization, content-type, ...
```

---

## 📝 RESUMEN DE CAMBIOS NECESARIOS

### **En el Frontend:**

1. **Opción Recomendada - Modificar `apiConfig.ts`:**
```typescript
const API_BASE_URL = 'http://clinica-demo.localhost:8000/public';  // ✅ Agregar /public
```

2. **O crear dos clientes separados:**
```typescript
export const publicApiClient = axios.create({
  baseURL: 'http://clinica-demo.localhost:8000/public'
});

export const tenantApiClient = axios.create({
  baseURL: 'http://clinica-demo.localhost:8000/tenant'
});
```

3. **Asegurar `withCredentials: true`**

### **En el Backend (ya está configurado ✅):**
- ✅ CORS_ALLOW_CREDENTIALS = True
- ✅ CORS_ALLOWED_ORIGIN_REGEXES permite subdominios
- ✅ CORS_ALLOW_HEADERS incluye 'authorization'

---

## 🎯 SIGUIENTE PASO

1. **Localizar archivo de configuración** del frontend (probablemente `src/services/apiConfig.ts`)
2. **Agregar `/public`** a la base URL
3. **Reiniciar servidor frontend** (Ctrl+C y `npm run dev`)
4. **Probar login** desde el formulario

---

**🚀 Una vez corregido, el login funcionará correctamente**

**📅 Última actualización:** 15 de Noviembre, 2025
