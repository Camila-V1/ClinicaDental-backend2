# 🔐 FASE 1A1: CONFIGURACIÓN AXIOS - PARTE 1 (Setup Básico)

## 📋 Información del Backend (Verificada)

**Sistema**: Django 5.2.6 + SimpleJWT + django-tenants  
**JWT Access Token**: 15 minutos de duración  
**JWT Refresh Token**: 1 día de duración  
**API Base URL**: `http://localhost:8000`

```javascript
// Endpoints de autenticación (verificados contra backend)
const AUTH_ENDPOINTS = {
  login: '/api/token/',                    // POST: {email, password} → {access, refresh, user}
  register: '/api/usuarios/register/',     // POST: {email, password, first_name, last_name, tipo_usuario}
  refresh: '/api/token/refresh/',          // POST: {refresh} → {access}
  profile: '/api/usuarios/me/'             // GET → user data
};
```

## 🌐 Variables de Entorno (.env.local)

```bash
# URL del backend API
REACT_APP_API_URL=http://localhost:8000

# Para multi-tenant (opcional)
REACT_APP_PUBLIC_API_URL=http://localhost:8000/public
REACT_APP_TENANT_API_URL=http://localhost:8000/api

# Configuración de debugging
REACT_APP_DEBUG=true
```

## ⚙️ Configuración Base de Axios (services/apiConfig.js)

```javascript
import axios from 'axios';

// Crear instancia de API con configuración base
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptor REQUEST: Añadir JWT automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
```

## 🔧 Token Helpers Básicos (utils/tokenHelpers.js)

```javascript
// Limpiar todos los tokens almacenados
export const clearAuthTokens = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  console.log('🧹 Auth tokens cleared');
};

// Verificar si hay tokens válidos almacenados
export const hasValidTokens = () => {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  return !!(accessToken && refreshToken);
};

// Parsear JWT para obtener información (sin verificar firma)
export const parseJWTPayload = (token) => {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    
    return {
      valid: true,
      userId: decoded.user_id,
      exp: decoded.exp,
      iat: decoded.iat,
      expiresIn: decoded.exp - Math.floor(Date.now() / 1000)
    };
  } catch (error) {
    return { valid: false, error: error.message };
  }
};

// Obtener configuración actual de la API
export const getApiConfig = () => ({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  hasAccessToken: !!localStorage.getItem('accessToken'),
  hasRefreshToken: !!localStorage.getItem('refreshToken')
});
```

## ✅ Setup Básico Completado

✅ **Axios instance** configurada  
✅ **Request interceptor** con JWT automático  
✅ **Environment variables** definidas  
✅ **Token helpers** básicos disponibles  

**Continuar con:** `01a1_axios_core_PARTE2.md` (Auto-refresh de tokens)
