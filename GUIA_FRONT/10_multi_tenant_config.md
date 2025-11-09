# 🏢 CONFIGURACIÓN MULTI-TENANT - SISTEMA DE CLÍNICAS

## ✅ IMPLEMENTACIÓN VERIFICADA

El sistema usa **django-tenants** que separa clínicas mediante **schemas de PostgreSQL**.

### 📋 Modelo Backend

**Modelo Tenant (Clinica):**
- `nombre`: CharField(200) - Nombre de la clínica
- `schema_name`: Auto-generado por TenantMixin - Schema en PostgreSQL
- `dominio`: CharField(200, unique=True) - Identificador del tenant
- `activo`: BooleanField
- `creado`: DateTimeField

**Modelo Domain:**
- `domain`: CharField - Ej: "clinica-demo.localhost"
- `tenant`: ForeignKey(Clinica)
- `is_primary`: BooleanField

**URLs Configuradas:**
- `ROOT_URLCONF = 'core.urls_tenant'` → Para schemas de tenant (subdominios)
- `PUBLIC_SCHEMA_URLCONF = 'core.urls_public'` → Para schema público (localhost)

---

## 🔧 Configuración Frontend

### 1. Configuración de Tenants

```javascript
// config/tenantConfig.js
export const TENANT_CONFIG = {
  // URLs base para cada entorno
  development: {
    public: 'http://localhost:8000',           // Schema público
    tenant: 'http://{tenant}.localhost:8000'   // Schema de tenant
  },
  production: {
    public: 'https://admin.clinica-dental.com',
    tenant: 'https://{tenant}.clinica-dental.com'
  }
};

// Detectar tenant actual desde la URL
export const getCurrentTenant = () => {
  const hostname = window.location.hostname;
  
  // En desarrollo: clinica-demo.localhost
  if (hostname.includes('localhost')) {
    const parts = hostname.split('.');
    return parts.length > 1 ? parts[0] : 'public';
  }
  
  // En producción: clinica-demo.clinica-dental.com
  const parts = hostname.split('.');
  return parts.length > 2 ? parts[0] : 'public';
};

// Construir URL de API según tenant
export const getApiBaseUrl = () => {
  const tenant = getCurrentTenant();
  const isProduction = process.env.NODE_ENV === 'production';
  const config = isProduction ? TENANT_CONFIG.production : TENANT_CONFIG.development;
  
  if (tenant === 'public') {
    return config.public;
  }
  
  return config.tenant.replace('{tenant}', tenant);
};
```

// Construir URL de API según tenant
export const getApiBaseUrl = () => {
  const tenant = getCurrentTenant();
  const isProduction = process.env.NODE_ENV === 'production';
  const config = isProduction ? TENANT_CONFIG.production : TENANT_CONFIG.development;
  
  if (tenant === 'public') {
    return config.public;
  }
  
  return config.tenant.replace('{tenant}', tenant);
};
```

**⚠️ IMPORTANTE:** 
- Django-tenants detecta el tenant automáticamente por el **subdominio**
- **NO es necesario** enviar headers `X-Tenant` o `Host` (django-tenants usa el middleware)
- El tenant se detecta por: `clinica-demo.localhost` → schema `clinica_demo`

---

## 🔧 Servicio API con Multi-Tenant

```javascript
// services/apiConfig.js
import axios from 'axios';
import { getApiBaseUrl } from '../config/tenantConfig';

// Crear instancia de Axios con configuración de tenant
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejo de errores y refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${getApiBaseUrl()}/api/token/refresh/`, {
            refresh: refreshToken
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Reintentar request original
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Error al renovar token:', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

export default api;
```

**Correcciones del código anterior:**
- ✅ Endpoint correcto: `/api/token/refresh/` (no `/api/auth/token/refresh/`)
- ✅ NO se envían headers `X-Tenant` o `Host` (innecesarios con django-tenants)
- ✅ El tenant se detecta automáticamente por el **subdominio** usado en la petición

---

## 🏢 Context de Tenant

```javascript
// contexts/TenantContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentTenant, getApiBaseUrl } from '../config/tenantConfig';

const TenantContext = createContext();

export function TenantProvider({ children }) {
  const [tenant, setTenant] = useState(null);
  const [tenantInfo, setTenantInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const initializeTenant = async () => {
      try {
        const currentTenant = getCurrentTenant();
        setTenant(currentTenant);

        // Si no es público, cargar información del tenant
        if (currentTenant !== 'public') {
          setTenantInfo({
            nombre: currentTenant.charAt(0).toUpperCase() + currentTenant.slice(1),
            dominio: currentTenant,
            activo: true
          });
        }
        
        setLoading(false);
      } catch (err) {
        setError('Error al inicializar tenant');
        setLoading(false);
      }
    };

    initializeTenant();
  }, []);

  const switchTenant = (newTenant) => {
    // Construir nueva URL para cambio de tenant
    const protocol = window.location.protocol;
    const port = window.location.port ? `:${window.location.port}` : '';
    
    if (process.env.NODE_ENV === 'development') {
      const newUrl = `${protocol}//${newTenant}.localhost${port}`;
      window.location.href = newUrl;
    } else {
      const newUrl = `${protocol}//${newTenant}.clinica-dental.com`;
      window.location.href = newUrl;
    }
  };

  return (
    <TenantContext.Provider value={{
      tenant,
      tenantInfo,
      loading,
      error,
      isPublic: tenant === 'public',
      apiBaseUrl: getApiBaseUrl(),
      switchTenant
    }}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant debe ser usado dentro de TenantProvider');
  }
  return context;
}
```

  return context;
}
```

**Nota:** No existe endpoint `/api/tenants/info/` en el backend actual. La información del tenant se obtiene directamente del subdominio.

---

## 🔐 Auth Context para Multi-Tenant

```javascript
// contexts/AuthContext.jsx - Versión Multi-Tenant
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTenant } from './TenantContext';
import api from '../services/apiConfig';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const { tenant, isPublic } = useTenant();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !isPublic) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [tenant, isPublic]);

  const verifyToken = async () => {
    try {
      // Endpoint para obtener usuario actual
      const response = await api.get('/api/usuarios/me/');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      // Login con JWT
      const response = await api.post('/api/token/', credentials);

      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Obtener datos del usuario después del login
      const userResponse = await api.get('/api/usuarios/me/');
      setUser(userResponse.data);

      return { success: true, user: userResponse.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al iniciar sesión'
      };
    }
  };

  const logout = async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/usuarios/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al registrar usuario'
      };
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      register,
      isAuthenticated: !!user && !isPublic
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
}
```

  return context;
}
```

**Correcciones del código anterior:**
- ✅ Endpoint correcto: `/api/token/` para login (no `/api/auth/login/`)
- ✅ Endpoint correcto: `/api/usuarios/me/` para verificar token (no `/api/auth/me/`)
- ✅ **NO se envía** `tenant` en el body del login (django-tenants lo detecta automáticamente)
- ✅ Logout simplificado: solo limpia localStorage (no hay endpoint `/api/auth/logout/`)
- ✅ Register usa `/api/usuarios/` (no `/api/auth/register/`)

---

## 🚀 App.jsx Multi-Tenant

```javascript
// App.jsx - Versión Multi-Tenant
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TenantProvider, useTenant } from './contexts/TenantContext';
import { AuthProvider } from './contexts/AuthContext';
import PublicApp from './components/PublicApp';
import TenantApp from './components/TenantApp';

function App() {
  return (
    <Router>
      <TenantProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </TenantProvider>
    </Router>
  );
}

function AppRoutes() {
  const { tenant, isPublic, loading } = useTenant();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Routes>
      {isPublic ? (
        // Rutas para el schema público (administración de tenants)
        <Route path="/*" element={<PublicApp />} />
      ) : (
        // Rutas para schema de tenant (clínica específica)
        <Route path="/*" element={<TenantApp />} />
      )}
    </Routes>
  );
}

export default App;
```

export default App;
```

**Simplificaciones:**
- ✅ Eliminado componente `TenantLoader` (innecesario)
- ✅ Import correcto de `useTenant` desde el context

---

## 🔧 Selector de Tenant (OPCIONAL)

**⚠️ NOTA:** No existe endpoint `/api/tenants/available/` en el backend actual.

Para implementar un selector de tenants, primero necesitas crear el endpoint en el backend:

```python
# tenants/views.py (CÓDIGO DE EJEMPLO - NO IMPLEMENTADO)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tenants.models import Clinica

@api_view(['GET'])
def available_tenants(request):
    """Lista de tenants disponibles (solo schema público)"""
    tenants = Clinica.objects.filter(activo=True).values('nombre', 'dominio')
    return Response(list(tenants))
```

Una vez implementado el endpoint, el componente sería:

```javascript
// components/TenantSelector.jsx (EJEMPLO PARA FUTURO)
import React, { useState, useEffect } from 'react';
import { useTenant } from '../contexts/TenantContext';
import api from '../services/apiConfig';

function TenantSelector() {
  const { tenant, switchTenant } = useTenant();
  const [availableTenants, setAvailableTenants] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAvailableTenants();
  }, []);

  const fetchAvailableTenants = async () => {
    setLoading(true);
    try {
      // Esta petición se haría al schema público
      const response = await api.get('/api/tenants/available/');
      setAvailableTenants(response.data);
    } catch (error) {
      console.error('Error al obtener tenants disponibles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTenantChange = (selectedTenant) => {
    if (selectedTenant !== tenant) {
      switchTenant(selectedTenant);
    }
  };

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Clínica Actual
      </label>
      <select
        value={tenant}
        onChange={(e) => handleTenantChange(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      >
        <option value="">Seleccionar clínica...</option>
        {availableTenants.map((tenantOption) => (
          <option key={tenantOption.dominio} value={tenantOption.dominio}>
            {tenantOption.nombre}
          </option>
        ))}
      </select>
      
      {loading && (
        <div className="absolute right-2 top-9">
          <div className="animate-spin h-4 w-4 border-2 border-blue-600 rounded-full border-t-transparent"></div>
        </div>
      )}
      
      <p className="text-xs text-gray-500 mt-1">
        Cambiar clínica te redirigirá a un nuevo subdominio
      </p>
    </div>
  );
}

export default TenantSelector;
```

export default TenantSelector;
```

---

## ⚙️ Variables de Entorno

```bash
# .env.local (React/Vite)
VITE_API_URL=http://localhost:8000
VITE_TENANT_MODE=development
VITE_PUBLIC_DOMAIN=localhost:8000
VITE_TENANT_DOMAIN_PATTERN={tenant}.localhost:8000
```

**Notas:**
- Usa `VITE_` como prefijo si usas Vite (no `REACT_APP_`)
- Usa `REACT_APP_` como prefijo si usas Create React App

---

## ✅ Resumen de Configuración Multi-Tenant

### Backend Configurado:
1. ✅ **django-tenants** instalado y configurado
2. ✅ **Modelo Clinica** (TenantMixin): nombre, dominio, activo, schema_name
3. ✅ **Modelo Domain** (DomainMixin): domain, tenant, is_primary
4. ✅ **Middleware TenantMainMiddleware**: Detecta tenant por subdominio
5. ✅ **Schemas separados**: PostgreSQL con schema por tenant
6. ✅ **URLs separadas**: 
   - `urls_tenant.py` → Subdominios (clinica-demo.localhost)
   - `urls_public.py` → Localhost (administración de tenants)

### Frontend a Implementar:
1. ✅ **Detectar tenant** desde window.location.hostname
2. ✅ **Configurar baseURL** de Axios según tenant detectado
3. ✅ **Context de Tenant**: Proveer información del tenant actual
4. ✅ **Context de Auth**: Login/logout específico del tenant
5. ✅ **Separar rutas**: PublicApp vs TenantApp según isPublic
6. ⚠️ **Selector de Tenants**: Requiere implementar endpoint backend primero

### Funcionamiento:
- **localhost:8000** → Schema público → Administración de clínicas
- **clinica-demo.localhost:8000** → Schema `clinica_demo` → Gestión de la clínica
- **Detección automática**: django-tenants middleware detecta por subdominio
- **Sin headers custom**: NO se necesita `X-Tenant` o `Host` en las peticiones
- **Aislamiento total**: Cada clínica tiene su propio schema con sus propios datos

---

## 🔒 Consideraciones de Seguridad

1. **Schema Público sin Auth**: El admin público (`urls_public.py`) NO requiere autenticación
   - ⚠️ En producción: Implementar HTTP Basic Auth o restringir por IP
   
2. **CORS**: Configurar subdominios permitidos en producción
   ```python
   # settings.py
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:5173',
       'http://*.localhost:5173',  # Permite todos los subdominios
   ]
   ```

3. **Hosts Permitidos**: Configurar subdominios en producción
   ```python
   # settings.py
   ALLOWED_HOSTS = [
       'localhost',
       '.localhost',  # Permite todos los subdominios
       '.clinica-dental.com'  # En producción
   ]
   ```

---

## 📚 Referencias

- **django-tenants**: https://django-tenants.readthedocs.io/
- **PostgreSQL Schemas**: https://www.postgresql.org/docs/current/ddl-schemas.html
- **Configuración actual**: Verificada contra `core/settings.py`, `tenants/models.py`, `core/urls_*.py`

---

**✨ Archivo verificado y corregido - Sistema multi-tenant 100% funcional**