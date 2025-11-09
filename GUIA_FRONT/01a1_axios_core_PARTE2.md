# 🔐 FASE 1A1: CONFIGURACIÓN AXIOS - PARTE 2 (Auto-Refresh)

## 🔄 Interceptor de Response con Auto-Refresh

Este interceptor maneja automáticamente la renovación de tokens cuando el access token expira.

### Archivo: services/apiConfig.js (Continuación)

```javascript
import axios from 'axios';
import api from './apiConfig'; // La instancia base creada en PARTE 1

// Interceptor RESPONSE: Manejo automático de refresh token
api.interceptors.response.use(
  (response) => response, // Si la respuesta es exitosa, simplemente retornarla
  
  async (error) => {
    const originalRequest = error.config;

    // Manejar 401 Unauthorized para refresh automático
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        originalRequest._retry = true; // Marcar para evitar loops infinitos
        
        try {
          // Intentar renovar el access token
          const refreshResponse = await axios.post(
            `${api.defaults.baseURL}/api/token/refresh/`,
            { refresh: refreshToken }
          );
          
          // Guardar nuevo access token
          const newAccessToken = refreshResponse.data.access;
          localStorage.setItem('accessToken', newAccessToken);
          
          // Actualizar header del request original y reintentar
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api.request(originalRequest);
          
        } catch (refreshError) {
          // Si refresh falla, limpiar storage y redirigir a login
          console.warn('Refresh token expired, logging out');
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No hay refresh token, logout directo
        console.warn('No refresh token available, logging out');
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

## 🔍 Cómo Funciona el Auto-Refresh

### Flujo Normal (Token Válido)
```
Usuario → Request → API → Response 200 ✅
```

### Flujo con Token Expirado
```
Usuario → Request 
  ↓ (Access token expirado)
API → Response 401 
  ↓ (Interceptor detecta 401)
Auto-refresh con refresh token
  ↓ (Obtiene nuevo access token)
Reintenta request original → Response 200 ✅
```

### Flujo con Refresh Token Expirado
```
Usuario → Request
  ↓
API → Response 401
  ↓
Auto-refresh FALLA (refresh token inválido)
  ↓
Limpia localStorage
  ↓
Redirige a /login 🚪
```

## 🛡️ Prevención de Loop Infinito

El flag `originalRequest._retry` previene intentos infinitos:

```javascript
if (error.response?.status === 401 && !originalRequest._retry) {
  originalRequest._retry = true; // ← Marca el request
  // ... intento de refresh
}
```

Sin este flag, si el refresh falla, el request se reintentaría infinitamente.

## 📊 Estados Posibles

| Estado | Access Token | Refresh Token | Acción |
|--------|--------------|---------------|--------|
| ✅ Autenticado | Válido | Válido | Request normal |
| 🔄 Refrescando | Expirado | Válido | Auto-refresh → retry |
| 🚪 Logout | Expirado | Expirado | Limpiar → redirect login |
| ❌ No autenticado | Ninguno | Ninguno | Redirect login |

## ⚠️ Consideraciones Importantes

### 1. Uso de axios.post vs api.post para refresh
```javascript
// ✅ CORRECTO: Usar axios.post (sin interceptor)
const refreshResponse = await axios.post(
  `${api.defaults.baseURL}/api/token/refresh/`,
  { refresh: refreshToken }
);

// ❌ INCORRECTO: Usar api.post (con interceptor)
// Esto causaría un loop si el refresh token está expirado
const refreshResponse = await api.post('/api/token/refresh/', ...);
```

### 2. Seguridad del Refresh Token
- El refresh token se envía **solo** en el endpoint de refresh
- Nunca se envía en headers de otros requests
- Se almacena en localStorage (considera httpOnly cookies en producción)

### 3. Manejo de Múltiples Requests Simultáneos
Si varios requests fallan al mismo tiempo (todos con 401), cada uno intentará hacer refresh. Para optimizar, considera implementar un sistema de cola (ver `01a2_axios_advanced.md`).

## ✅ Auto-Refresh Implementado

✅ **Interceptor response** con manejo de 401  
✅ **Auto-refresh** de access token  
✅ **Reintentar requests** fallidos automáticamente  
✅ **Logout automático** cuando refresh falla  
✅ **Prevención de loops** infinitos  

**Continuar con:** `01a1_validators.md` (Validadores y testing)
