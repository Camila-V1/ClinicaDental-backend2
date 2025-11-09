# 🔗 GUÍA COMPLETA: CONECTAR FRONTEND AL MULTI-TENANT

## ✅ BACKEND CONFIGURADO Y FUNCIONANDO

### URLs Backend Verificadas:
```
✅ http://localhost:8000/                    → Schema público
✅ http://clinica-demo.localhost:8000/       → Tenant clinica_demo
✅ http://clinica-demo.localhost:8000/api/usuarios/  → Funcionando (Status 200)
```

### Configuración Backend Aplicada:
- ✅ ALLOWED_HOSTS incluye `.localhost`
- ✅ CORS permite subdominios con regex
- ✅ CSRF_TRUSTED_ORIGINS incluye subdominios
- ✅ django-tenants detectando correctamente

---

## 📋 PASOS PARA CONFIGURAR EL FRONTEND

### PASO 1: Archivo hosts de Windows

**Ejecutar PowerShell como Administrador:**
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

**Agregar estas líneas al final:**
```
127.0.0.1 localhost
127.0.0.1 clinica-demo.localhost
```

**Guardar y cerrar.** Reiniciar navegador.

---

### PASO 2: Variables de Entorno (.env.local)

**Ubicación:** `ClinicaDental-frontend2/.env.local`

```bash
# URL base del backend
VITE_API_URL=http://localhost:8000

# Configuración para multi-tenant
VITE_TENANT_MODE=development
VITE_PUBLIC_DOMAIN=localhost:8000
VITE_TENANT_DOMAIN_PATTERN={tenant}.localhost:8000
```

---

### PASO 3: Configuración de Tenant (src/config/tenantConfig.ts)

**Crear archivo:** `src/config/tenantConfig.ts`

```typescript
// src/config/tenantConfig.ts

/**
 * Configuración de URLs para cada entorno
 */
export const TENANT_CONFIG = {
  development: {
    public: 'http://localhost:8000',
    tenant: 'http://{tenant}.localhost:8000'
  },
  production: {
    public: 'https://admin.clinica-dental.com',
    tenant: 'https://{tenant}.clinica-dental.com'
  }
};

/**
 * Detectar el tenant actual desde el hostname del navegador
 * 
 * Ejemplos:
 * - "localhost" → "public"
 * - "clinica-demo.localhost" → "clinica-demo"
 * - "clinica-abc.localhost" → "clinica-abc"
 */
export const getCurrentTenant = (): string => {
  const hostname = window.location.hostname;
  
  console.log('🔍 Detectando tenant desde:', hostname);
  
  // En desarrollo: localhost o *.localhost
  if (hostname.includes('localhost')) {
    const parts = hostname.split('.');
    const tenant = parts.length > 1 ? parts[0] : 'public';
    console.log('✅ Tenant detectado:', tenant);
    return tenant;
  }
  
  // En producción: *.clinica-dental.com
  const parts = hostname.split('.');
  const tenant = parts.length > 2 ? parts[0] : 'public';
  console.log('✅ Tenant detectado:', tenant);
  return tenant;
};

/**
 * Construir URL base del API según el tenant actual
 * 
 * Si estás en: clinica-demo.localhost:5174
 * Retorna: http://clinica-demo.localhost:8000
 */
export const getApiBaseUrl = (): string => {
  const tenant = getCurrentTenant();
  const isDevelopment = import.meta.env.MODE === 'development';
  const config = isDevelopment ? TENANT_CONFIG.development : TENANT_CONFIG.production;
  
  if (tenant === 'public') {
    console.log('📡 API URL (público):', config.public);
    return config.public;
  }
  
  const apiUrl = config.tenant.replace('{tenant}', tenant);
  console.log('📡 API URL (tenant):', apiUrl);
  return apiUrl;
};

/**
 * Verificar si estamos en el schema público
 */
export const isPublicSchema = (): boolean => {
  return getCurrentTenant() === 'public';
};
```

---

### PASO 4: Configuración de Axios (src/config/apiConfig.ts)

**Modificar archivo:** `src/config/apiConfig.ts`

```typescript
// src/config/apiConfig.ts
import axios, { AxiosError } from 'axios';
import { getApiBaseUrl } from './tenantConfig';

/**
 * Instancia de Axios con baseURL dinámica según tenant
 */
const api = axios.create({
  baseURL: getApiBaseUrl(), // ← CLAVE: Se ajusta automáticamente
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor REQUEST: Agregar token JWT
 */
api.interceptors.request.use(
  (config) => {
    // Log para debugging
    console.log('📤 Request:', config.method?.toUpperCase(), config.url);
    console.log('📡 Base URL:', config.baseURL);
    
    // Agregar token si existe
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔐 Token agregado');
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Error en request:', error);
    return Promise.reject(error);
  }
);

/**
 * Interceptor RESPONSE: Manejar refresh token
 */
api.interceptors.response.use(
  (response) => {
    console.log('✅ Response:', response.status, response.config.url);
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    console.error('❌ Error en response:', error.response?.status, error.config?.url);

    // Si es 401 y no es retry, intentar refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          console.log('🔄 Intentando refresh token...');
          
          // Importante: usar baseURL actual
          const response = await axios.post(
            `${getApiBaseUrl()}/api/token/refresh/`,
            { refresh: refreshToken }
          );

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          console.log('✅ Token renovado exitosamente');

          // Reintentar request original con nuevo token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('❌ Error al renovar token:', refreshError);
        
        // Limpiar storage y redirigir
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

### PASO 5: Context de Tenant (src/context/TenantContext.tsx)

**Crear archivo:** `src/context/TenantContext.tsx`

```typescript
// src/context/TenantContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getCurrentTenant, getApiBaseUrl, isPublicSchema } from '../config/tenantConfig';

interface TenantContextType {
  tenant: string;
  tenantInfo: {
    nombre: string;
    dominio: string;
  } | null;
  isPublic: boolean;
  apiBaseUrl: string;
  loading: boolean;
  error: string;
  switchTenant: (newTenant: string) => void;
}

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenant, setTenant] = useState<string>('');
  const [tenantInfo, setTenantInfo] = useState<{ nombre: string; dominio: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const initializeTenant = async () => {
      try {
        console.log('🏢 Inicializando tenant...');
        
        const currentTenant = getCurrentTenant();
        setTenant(currentTenant);

        // Si no es público, crear info del tenant
        if (currentTenant !== 'public') {
          setTenantInfo({
            nombre: currentTenant.charAt(0).toUpperCase() + currentTenant.slice(1).replace('-', ' '),
            dominio: currentTenant,
          });
          console.log('✅ Tenant inicializado:', currentTenant);
        } else {
          console.log('🌐 Schema público detectado');
        }

        setLoading(false);
      } catch (err) {
        console.error('❌ Error al inicializar tenant:', err);
        setError('Error al inicializar tenant');
        setLoading(false);
      }
    };

    initializeTenant();
  }, []);

  const switchTenant = (newTenant: string) => {
    console.log('🔀 Cambiando a tenant:', newTenant);
    
    const protocol = window.location.protocol;
    const port = window.location.port ? `:${window.location.port}` : '';

    let newUrl: string;
    
    if (import.meta.env.MODE === 'development') {
      if (newTenant === 'public') {
        newUrl = `${protocol}//localhost${port}`;
      } else {
        newUrl = `${protocol}//${newTenant}.localhost${port}`;
      }
    } else {
      if (newTenant === 'public') {
        newUrl = `${protocol}//admin.clinica-dental.com`;
      } else {
        newUrl = `${protocol}//${newTenant}.clinica-dental.com`;
      }
    }

    console.log('➡️ Redirigiendo a:', newUrl);
    window.location.href = newUrl;
  };

  return (
    <TenantContext.Provider
      value={{
        tenant,
        tenantInfo,
        isPublic: isPublicSchema(),
        apiBaseUrl: getApiBaseUrl(),
        loading,
        error,
        switchTenant,
      }}
    >
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant debe usarse dentro de TenantProvider');
  }
  return context;
}
```

---

### PASO 6: Modificar App.tsx

**Modificar archivo:** `src/App.tsx`

```typescript
// src/App.tsx
import { BrowserRouter } from 'react-router-dom';
import { TenantProvider } from './context/TenantContext';
import { AuthProvider } from './context/AuthContext';
// ... otros imports

function App() {
  return (
    <BrowserRouter>
      <TenantProvider>  {/* ← AGREGAR: Primero TenantProvider */}
        <AuthProvider>   {/* ← MANTENER: Luego AuthProvider */}
          {/* Tus rutas aquí */}
        </AuthProvider>
      </TenantProvider>
    </BrowserRouter>
  );
}

export default App;
```

**⚠️ ORDEN IMPORTANTE:**
1. `BrowserRouter` (más externo)
2. `TenantProvider` (detecta tenant)
3. `AuthProvider` (usa info del tenant)
4. Resto de la app

---

### PASO 7: Modificar AuthContext (si es necesario)

**Actualizar:** `src/context/AuthContext.tsx`

```typescript
// src/context/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useTenant } from './TenantContext'; // ← IMPORTAR
import api from '../config/apiConfig';

// ... interfaces ...

export function AuthProvider({ children }: { children: ReactNode }) {
  const { tenant, isPublic } = useTenant(); // ← USAR TENANT
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    // Solo verificar token si NO es schema público
    if (token && !isPublic) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [tenant, isPublic]); // ← DEPENDER DEL TENANT

  const verifyToken = async () => {
    try {
      console.log('🔐 Verificando token...');
      const response = await api.get('/api/usuarios/me/');
      setUser(response.data);
      console.log('✅ Usuario autenticado:', response.data.email);
    } catch (error) {
      console.error('❌ Token inválido');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials: { email: string; password: string }) => {
    try {
      console.log('🔑 Intentando login en tenant:', tenant);
      console.log('📧 Email:', credentials.email);
      
      // PASO 1: Obtener tokens JWT
      const tokenResponse = await api.post('/api/token/', credentials);
      
      console.log('✅ Tokens recibidos');
      
      const { access, refresh } = tokenResponse.data;
      
      // Guardar tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // PASO 2: Obtener datos del usuario
      const userResponse = await api.get('/api/usuarios/me/');
      
      console.log('✅ Datos de usuario recibidos:', userResponse.data.email);
      
      setUser(userResponse.data);
      localStorage.setItem('user', JSON.stringify(userResponse.data));

      return { 
        success: true, 
        user: userResponse.data 
      };
    } catch (error: any) {
      console.error('❌ Error en login:', error.response?.data);
      
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al iniciar sesión',
      };
    }
  };

  const logout = () => {
    console.log('👋 Cerrando sesión');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user && !isPublic,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}
```

---

## 🧪 PROBAR LA CONFIGURACIÓN

### 1. Verificar Detección de Tenant

Abrir consola del navegador (F12) y acceder a:

```
http://localhost:5174/
→ Debería ver logs:
  🔍 Detectando tenant desde: localhost
  ✅ Tenant detectado: public
  📡 API URL (público): http://localhost:8000

http://clinica-demo.localhost:5174/
→ Debería ver logs:
  🔍 Detectando tenant desde: clinica-demo.localhost
  ✅ Tenant detectado: clinica-demo
  📡 API URL (tenant): http://clinica-demo.localhost:8000
```

### 2. Probar Login

**En la consola del navegador:**

```javascript
// Acceder a: http://clinica-demo.localhost:5174/login

// Ver valores actuales
console.log('Tenant:', window.location.hostname);
console.log('API URL:', /* verificar en Network tab */);

// Intentar login con credenciales de clinica-demo
// Ver en Network tab que las peticiones van a:
// POST http://clinica-demo.localhost:8000/api/token/
// GET  http://clinica-demo.localhost:8000/api/usuarios/me/
```

### 3. Verificar Network Tab

**En Chrome DevTools > Network:**

1. Hacer login
2. Verificar peticiones:
   ```
   POST http://clinica-demo.localhost:8000/api/token/
   Status: 200
   Response: { "access": "...", "refresh": "..." }

   GET http://clinica-demo.localhost:8000/api/usuarios/me/
   Status: 200
   Response: { "id": 1, "email": "...", "tipo_usuario": "..." }
   ```

3. Si ves errores CORS:
   - Verificar que backend está corriendo
   - Verificar ALLOWED_HOSTS en backend
   - Verificar CORS_ALLOWED_ORIGIN_REGEXES

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema 1: "ERR_NAME_NOT_RESOLVED"

**Causa:** Archivo hosts no configurado

**Solución:**
```powershell
# Como Administrador
notepad C:\Windows\System32\drivers\etc\hosts

# Agregar:
127.0.0.1 clinica-demo.localhost
```

Reiniciar navegador.

### Problema 2: "CORS Error"

**Causa:** Backend no permite el origen

**Solución:** Verificar en `core/settings.py`:
```python
ALLOWED_HOSTS = ['.localhost']  # ← Debe tener el punto

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://[\w-]+\.localhost:\d+$",  # ← Debe estar presente
]
```

Reiniciar Django.

### Problema 3: "404 Not Found"

**Causa:** URL incorrecta o endpoint no existe

**Solución:**
- Verificar que `getApiBaseUrl()` retorna URL correcta
- Verificar que endpoints son: `/api/token/`, `/api/usuarios/me/`
- Ver logs en consola del frontend

### Problema 4: "401 Unauthorized" en /me/

**Causa:** Token no se está enviando

**Solución:** Verificar interceptor de Axios:
```typescript
// En apiConfig.ts debe existir:
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Problema 5: Login exitoso pero no redirige

**Causa:** Verificar manejo de respuesta en componente Login

**Solución:**
```typescript
const handleLogin = async (credentials) => {
  const result = await login(credentials);
  
  if (result.success) {
    console.log('✅ Login exitoso, redirigiendo...');
    navigate('/dashboard'); // ← Asegurarse de redirigir
  } else {
    console.error('❌ Error:', result.error);
    setError(result.error);
  }
};
```

---

## 📊 FLUJO COMPLETO DE LOGIN

```
┌─────────────────────────────────────────────────────┐
│ USUARIO: http://clinica-demo.localhost:5174/login  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ FRONTEND: TenantContext                             │
│ - getCurrentTenant() → "clinica-demo"              │
│ - getApiBaseUrl() → http://clinica-demo.localhost:8000 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ FRONTEND: AuthContext.login()                       │
│                                                      │
│ PASO 1: POST /api/token/                           │
│         Body: { email, password }                   │
│         → Backend retorna: { access, refresh }      │
│                                                      │
│ PASO 2: GET /api/usuarios/me/                      │
│         Header: Authorization: Bearer {access}      │
│         → Backend retorna: { user data }            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ BACKEND: Django (clinica-demo.localhost:8000)      │
│                                                      │
│ django-tenants middleware:                          │
│ - Lee hostname: "clinica-demo.localhost"           │
│ - Busca Domain en DB                                │
│ - Encuentra Tenant: clinica_demo                    │
│ - Usa schema: clinica_demo                          │
│                                                      │
│ ViewSet usuarios:                                    │
│ - Valida credenciales en schema clinica_demo       │
│ - Retorna token JWT                                 │
│ - Retorna datos del usuario                         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ FRONTEND: AuthContext                               │
│ - Guarda tokens en localStorage                     │
│ - Guarda user en state                              │
│ - Marca isAuthenticated = true                      │
│ - Redirige a /dashboard                             │
└─────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST FINAL

Antes de probar, verificar:

- [ ] Archivo hosts configurado con `clinica-demo.localhost`
- [ ] `.env.local` con variables correctas
- [ ] `tenantConfig.ts` creado con funciones de detección
- [ ] `apiConfig.ts` usa `getApiBaseUrl()`
- [ ] `TenantContext.tsx` creado y exportado
- [ ] `App.tsx` envuelve con `TenantProvider`
- [ ] `AuthContext.tsx` usa `useTenant()` y hace 2 peticiones en login
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo (npm run dev)
- [ ] Navegador reiniciado (para leer hosts)

---

## 🎯 COMANDOS PARA PROBAR

```powershell
# Terminal 1: Backend
cd "c:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO\ClinicaDental-backend2"
python manage.py runserver

# Terminal 2: Frontend
cd "c:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO\ClinicaDental-frontend2"
npm run dev

# Navegador:
# http://localhost:5174/ (schema público)
# http://clinica-demo.localhost:5174/ (tenant clinica-demo)
```

---

**✨ Con esta guía el frontend debería conectarse correctamente al sistema multi-tenant del backend**
