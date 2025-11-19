# 🎯 GUÍA DEFINITIVA DE URLs - BACKEND MULTI-TENANT

**Fecha:** 15 de Noviembre, 2025  
**Sistema:** Django Multi-Tenant con django-tenants

---

## 🏗️ ARQUITECTURA DE URLs

El backend tiene **DOS conjuntos de URLs completamente diferentes**:

### 1️⃣ **PUBLIC SCHEMA** (localhost)
- **Dominio:** `http://localhost:8000/`
- **URLconf:** `core/urls_public.py`
- **Propósito:** Administrar tenants (clínicas)

### 2️⃣ **TENANT SCHEMAS** (subdominios)
- **Dominio:** `http://clinica-demo.localhost:8000/`
- **URLconf:** `core/urls_tenant.py`  
- **Propósito:** Operaciones de la clínica (usuarios, citas, etc.)

---

## ✅ URLs CORRECTAS PARA EL FRONTEND

### 🔓 **ENDPOINTS PÚBLICOS (Login, Register)**

**Dominio Tenant:** `http://clinica-demo.localhost:8000/`

```bash
# ✅ LOGIN (JWT Token)
POST http://clinica-demo.localhost:8000/api/token/
Body: { "username": "juan_perez", "password": "paciente123" }

# ✅ REFRESH TOKEN
POST http://clinica-demo.localhost:8000/api/token/refresh/
Body: { "refresh": "eyJ0eXAi..." }

# ✅ REGISTRO (Si existe endpoint)
POST http://clinica-demo.localhost:8000/api/usuarios/register/
Body: { "username": "...", "password": "..." }
```

### 🔒 **ENDPOINTS AUTENTICADOS (Requieren JWT)**

**Dominio Tenant:** `http://clinica-demo.localhost:8000/`

```bash
# ✅ PERFIL DEL USUARIO
GET http://clinica-demo.localhost:8000/api/usuarios/me/
Headers: Authorization: Bearer {access_token}

# ✅ LISTA DE CITAS
GET http://clinica-demo.localhost:8000/api/agenda/citas/
Headers: Authorization: Bearer {access_token}

# ✅ HISTORIAL CLÍNICO
GET http://clinica-demo.localhost:8000/api/historial/historiales/
Headers: Authorization: Bearer {access_token}

# ✅ PLANES DE TRATAMIENTO
GET http://clinica-demo.localhost:8000/api/tratamientos/planes/
Headers: Authorization: Bearer {access_token}

# ✅ FACTURAS
GET http://clinica-demo.localhost:8000/api/facturacion/facturas/
Headers: Authorization: Bearer {access_token}
```

---

## 🚫 URLs QUE **NO EXISTEN**

```bash
# ❌ NO EXISTE /public/api/...
http://clinica-demo.localhost:8000/public/api/token/     ← ERROR

# ❌ NO EXISTE /tenant/api/...
http://clinica-demo.localhost:8000/tenant/api/token/    ← ERROR
```

---

## 📝 CONFIGURACIÓN CORRECTA DEL FRONTEND

### **constants.ts**

```typescript
// src/config/constants.ts

export const API_ENDPOINTS = {
  // ✅ Autenticación (PÚBLICOS - No requieren token)
  LOGIN: '/api/token/',           // ✅ CORRECTO
  REFRESH: '/api/token/refresh/', // ✅ CORRECTO
  REGISTER: '/api/usuarios/register/', // ✅ CORRECTO (si existe)

  // ✅ Usuarios (REQUIEREN JWT)
  USER_PROFILE: '/api/usuarios/me/',
  USER_LIST: '/api/usuarios/',
  ODONTOLOGOS: '/api/usuarios/odontologos/',

  // ✅ Agenda (REQUIEREN JWT)
  CITAS: '/api/agenda/citas/',
  CANCELAR_CITA: (id: number) => `/api/agenda/citas/${id}/cancelar/`,

  // ✅ Historial (REQUIEREN JWT)
  HISTORIAL: '/api/historial/historiales/',
  EPISODIOS: '/api/historial/episodios/',
  DOCUMENTOS: '/api/historial/documentos/',

  // ✅ Tratamientos (REQUIEREN JWT)
  PLANES: '/api/tratamientos/planes/',
  CATALOGO: '/api/tratamientos/catalogo/',

  // ✅ Facturación (REQUIEREN JWT)
  FACTURAS: '/api/facturacion/facturas/',
  PAGOS: '/api/facturacion/pagos/',
};
```

### **apiConfig.ts**

```typescript
// src/config/apiConfig.ts

import axios from 'axios';

// ✅ Base URL: Solo el dominio con subdominio
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://clinica-demo.localhost:8000';

// ✅ Cliente HTTP único
export const apiClient = axios.create({
  baseURL: API_BASE_URL,  // ✅ http://clinica-demo.localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Interceptor para agregar token JWT
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

// Interceptor para manejar refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no es del endpoint de login
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        // ✅ CORRECTO: /api/token/refresh/
        const response = await axios.post(
          `${API_BASE_URL}/api/token/refresh/`,  // ✅ Sin /public
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        // Reintentar request original con nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh falló, logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### **authService.ts**

```typescript
// src/services/authService.ts

import apiClient from '@/config/apiConfig';
import { API_ENDPOINTS } from '@/config/constants';

export const authService = {
  // ✅ Login
  login: async (username: string, password: string) => {
    console.log('🔑 authService: Iniciando login...');
    
    // ✅ CORRECTO: /api/token/ (sin /public)
    const response = await apiClient.post(API_ENDPOINTS.LOGIN, {
      username,
      password
    });

    // Guardar tokens
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    console.log('✅ Login exitoso, tokens guardados');
    return response.data;
  },

  // ✅ Obtener perfil (requiere JWT)
  getUserProfile: async () => {
    // ✅ CORRECTO: /api/usuarios/me/ (sin /tenant)
    const response = await apiClient.get(API_ENDPOINTS.USER_PROFILE);
    return response.data;
  },

  // ✅ Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    console.log('✅ Logout: Tokens eliminados');
  }
};
```

---

## 🧪 PRUEBAS CON CURL/POWERSHELL

### **1. Login (Obtener tokens)**

```powershell
# PowerShell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    username = "juan_perez"
    password = "paciente123"
} | ConvertTo-Json

# ✅ URL CORRECTA
Invoke-RestMethod `
    -Uri "http://clinica-demo.localhost:8000/api/token/" `
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

### **2. Obtener perfil (con token)**

```powershell
# Reemplazar {TOKEN} con el access token del paso 1
$headers = @{
    "Authorization" = "Bearer {TOKEN}"
}

# ✅ URL CORRECTA
Invoke-RestMethod `
    -Uri "http://clinica-demo.localhost:8000/api/usuarios/me/" `
    -Method GET `
    -Headers $headers
```

---

## 📊 RESUMEN DE CAMBIOS NECESARIOS

### ❌ **ANTES (Incorrecto)**

```typescript
// constants.ts
LOGIN: '/public/api/token/',  // ❌ NO EXISTE

// apiConfig.ts
const API_BASE_URL = 'http://clinica-demo.localhost:8000/public'; // ❌ NO EXISTE

// Refresh token
`${API_BASE_URL}/public/api/token/refresh/`  // ❌ NO EXISTE
```

### ✅ **AHORA (Correcto)**

```typescript
// constants.ts
LOGIN: '/api/token/',  // ✅ CORRECTO

// apiConfig.ts
const API_BASE_URL = 'http://clinica-demo.localhost:8000';  // ✅ CORRECTO

// Refresh token
`${API_BASE_URL}/api/token/refresh/`  // ✅ CORRECTO
```

---

## 🎯 ESTRUCTURA COMPLETA DE URLs DEL BACKEND

### **Para Tenant: `clinica-demo.localhost:8000`**

```
📁 core/urls_tenant.py
│
├─ 🔓 PÚBLICOS (No requieren JWT)
│  ├─ /api/token/                     → Login (POST)
│  └─ /api/token/refresh/            → Refresh token (POST)
│
├─ 🔒 USUARIOS (Requieren JWT)
│  ├─ /api/usuarios/                 → Lista de usuarios
│  ├─ /api/usuarios/me/              → Perfil actual
│  └─ /api/usuarios/odontologos/     → Lista de odontólogos
│
├─ 🔒 AGENDA (Requieren JWT)
│  ├─ /api/agenda/citas/             → CRUD de citas
│  └─ /api/agenda/citas/{id}/cancelar/ → Cancelar cita
│
├─ 🔒 HISTORIAL (Requieren JWT)
│  ├─ /api/historial/historiales/    → Historiales clínicos
│  ├─ /api/historial/episodios/      → Episodios de atención
│  └─ /api/historial/documentos/     → Documentos clínicos
│
├─ 🔒 TRATAMIENTOS (Requieren JWT)
│  ├─ /api/tratamientos/planes/      → Planes de tratamiento
│  └─ /api/tratamientos/catalogo/    → Catálogo de tratamientos
│
└─ 🔒 FACTURACIÓN (Requieren JWT)
   ├─ /api/facturacion/facturas/     → Facturas
   └─ /api/facturacion/pagos/        → Pagos
```

### **Para Public: `localhost:8000`** (No usado por el frontend)

```
📁 core/urls_public.py
│
├─ /admin/                           → Admin de tenants
└─ /api/tenants/                     → Gestión de clínicas (interno)
```

---

## 🔍 VERIFICACIÓN FINAL

### **Checklist de configuración del frontend:**

- [ ] `API_BASE_URL = 'http://clinica-demo.localhost:8000'` (sin /public)
- [ ] `LOGIN: '/api/token/'` (sin /public)
- [ ] `REFRESH: '/api/token/refresh/'` (sin /public)
- [ ] `USER_PROFILE: '/api/usuarios/me/'` (sin /tenant)
- [ ] `CITAS: '/api/agenda/citas/'` (sin /tenant)
- [ ] `withCredentials: true` en axios
- [ ] Interceptor agrega `Authorization: Bearer {token}`

---

## 🎉 CONCLUSIÓN

**NO existen las rutas `/public/api/...` ni `/tenant/api/...`**

**Todas las rutas del tenant son simplemente `/api/...`**

```
✅ Correcto: http://clinica-demo.localhost:8000/api/token/
✅ Correcto: http://clinica-demo.localhost:8000/api/usuarios/me/
✅ Correcto: http://clinica-demo.localhost:8000/api/agenda/citas/

❌ Incorrecto: http://clinica-demo.localhost:8000/public/api/token/
❌ Incorrecto: http://clinica-demo.localhost:8000/tenant/api/usuarios/me/
```

---

**📅 Última actualización:** 15 de Noviembre, 2025  
**🔧 Estado:** Documentación definitiva de URLs
