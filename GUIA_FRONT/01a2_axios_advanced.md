# 🔐 FASE 1A2: CONFIGURACIÓN AVANZADA AXIOS

> ⚠️ **NOTA**: Este documento ha sido dividido para mejor manejo:
> - **PARTE 1**: `01a2_axios_advanced_PARTE1.md` - Multi-tenant (202 líneas) ✅
> - **PARTE 2**: `01a2_axios_advanced_PARTE2.md` - Debug & Performance (203 líneas) ✅

## � Resumen de Funcionalidades

Este archivo original se mantiene como referencia rápida. Para implementación detallada, consulta las partes 1 y 2.

### PARTE 1 - Multi-Tenant
- Detección automática de tenant desde URL
- Switch dinámico de base URL
- Soporte para subdominios en desarrollo y producción
- Testing de configuración multi-tenant

### PARTE 2 - Debug & Performance  
- Logging automático en desarrollo
- Performance monitoring con métricas
- Testing utilities (connectivity, auth, refresh)
- Herramientas de diagnóstico

```javascript
import api from './apiConfig';

// Configurar logging para desarrollo
if (process.env.REACT_APP_DEBUG === 'true') {
  // Log requests
  api.interceptors.request.use(
    (config) => {
      console.log(`🔄 ${config.method?.toUpperCase()} ${config.url}`, config.data || '');
      return config;
    }
  );

  // Log responses
  api.interceptors.response.use(
    (response) => {
      console.log(`✅ ${response.status} ${response.config.url}`, response.data);
      return response;
    },
    (error) => {
      console.log(`❌ ${error.response?.status || 'ERR'} ${error.config?.url}`, 
                  error.response?.data || error.message);
      return Promise.reject(error);
    }
  );
}

// Función para cambiar base URL dinámicamente (multi-tenant)
export const switchApiTenant = (tenantUrl) => {
  if (!tenantUrl) {
    console.warn('⚠️ No tenant URL provided');
    return false;
  }
  
  api.defaults.baseURL = tenantUrl;
  console.log(`🏢 API switched to tenant: ${tenantUrl}`);
  return true;
};

// Restaurar configuración por defecto
export const resetApiConfig = () => {
  api.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  console.log('🔄 API config reset to default');
};

// Obtener información de configuración actual
export const getCurrentApiConfig = () => ({
  baseURL: api.defaults.baseURL,
  timeout: api.defaults.timeout,
  headers: api.defaults.headers,
  isAuthenticated: !!localStorage.getItem('accessToken'),
  currentTenant: api.defaults.baseURL !== (process.env.REACT_APP_API_URL || 'http://localhost:8000')
});

export { api };
```

## 🏢 Multi-tenant Support (services/tenantManager.js)

```javascript
import { switchApiTenant, resetApiConfig } from './apiConfig.advanced';

// Detectar tenant desde URL o subdomain
export const detectTenant = () => {
  const hostname = window.location.hostname;
  
  // Para desarrollo local: clinica-demo.localhost, clinica-test.localhost
  if (hostname.includes('.localhost')) {
    const tenant = hostname.split('.')[0];
    return { tenant, isMultiTenant: true };
  }
  
  // Para producción: demo.clinica.com, test.clinica.com
  if (hostname.includes('.')) {
    const parts = hostname.split('.');
    if (parts.length >= 3) {
      const tenant = parts[0];
      return { tenant, isMultiTenant: true };
    }
  }
  
  return { tenant: null, isMultiTenant: false };
};

// Configurar API para tenant específico
export const configureTenantApi = () => {
  const { tenant, isMultiTenant } = detectTenant();
  
  if (isMultiTenant && tenant) {
    // Construir URL del tenant
    const protocol = window.location.protocol;
    const tenantUrl = `${protocol}//${window.location.host}`;
    
    switchApiTenant(tenantUrl);
    
    return { 
      configured: true, 
      tenant, 
      apiUrl: tenantUrl 
    };
  } else {
    // Usar configuración por defecto (público)
    resetApiConfig();
    
    return { 
      configured: false, 
      tenant: 'public', 
      apiUrl: process.env.REACT_APP_API_URL 
    };
  }
};

// Obtener configuración de tenant actual
export const getCurrentTenant = () => {
  const { tenant, isMultiTenant } = detectTenant();
  return {
    name: tenant || 'public',
    isMultiTenant,
    apiUrl: api.defaults.baseURL
  };
};
```

## 🧪 Testing Utilities (utils/apiTesting.js)

```javascript
import api from '../services/apiConfig';

// Test básico de conectividad
export const testConnection = async () => {
  try {
    const response = await api.get('/api/usuarios/health/', {
      validateStatus: () => true
    });
    return { success: true, status: response.status };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// Test de autenticación
export const testAuth = async (credentials) => {
  try {
    const response = await api.post('/api/token/', credentials);
    return {
      success: true,
      hasTokens: !!(response.data.access && response.data.refresh),
      userType: response.data.user?.tipo_usuario
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
};

// Test de refresh token
export const testRefresh = async () => {
  const refresh = localStorage.getItem('refreshToken');
  if (!refresh) return { success: false, error: 'No refresh token' };
  
  try {
    const response = await api.post('/api/token/refresh/', { refresh });
    return { success: true, hasNewToken: !!response.data.access };
  } catch (error) {
    return { success: false, error: error.response?.data?.detail };
  }
};

// Diagnóstico rápido del sistema
export const quickDiagnostic = async () => {
  const report = {
    apiUrl: api.defaults.baseURL,
    hasTokens: !!localStorage.getItem('accessToken'),
    connectivity: await testConnection(),
    timestamp: new Date().toISOString()
  };
  
  console.log('🔍 Quick Diagnostic:', report);
  return report;
};
```

## 📊 Performance & Debugging (utils/debugHelpers.js)

```javascript
// Simple performance monitor para desarrollo
class SimplePerformanceMonitor {
  constructor() {
    this.enabled = process.env.REACT_APP_DEBUG === 'true';
    this.requests = [];
  }

  record(url, method, duration, status) {
    if (!this.enabled) return;
    
    this.requests.push({ url, method, duration, status });
    
    // Mantener solo últimas 50 métricas
    if (this.requests.length > 50) {
      this.requests = this.requests.slice(-50);
    }
    
    // Log requests lentos
    if (duration > 2000) {
      console.warn(`🐌 Slow request: ${method} ${url} took ${duration}ms`);
    }
  }

  getStats() {
    if (!this.requests.length) return null;
    
    const avg = this.requests.reduce((sum, r) => sum + r.duration, 0) / this.requests.length;
    const errors = this.requests.filter(r => r.status >= 400).length;
    
    return {
      total: this.requests.length,
      avgDuration: Math.round(avg),
      errorRate: Math.round((errors / this.requests.length) * 100),
      slowRequests: this.requests.filter(r => r.duration > 2000).length
    };
  }
}

export const performanceMonitor = new SimplePerformanceMonitor();

// Añadir interceptor de performance solo en debug
if (process.env.REACT_APP_DEBUG === 'true') {
  api.interceptors.request.use((config) => {
    config.startTime = Date.now();
    return config;
  });

  api.interceptors.response.use(
    (response) => {
      const duration = Date.now() - (response.config.startTime || 0);
      performanceMonitor.record(response.config.url, response.config.method, duration, response.status);
      return response;
    },
    (error) => {
      const duration = Date.now() - (error.config?.startTime || 0);
      performanceMonitor.record(error.config?.url, error.config?.method, duration, error.response?.status || 0);
      return Promise.reject(error);
    }
  );
}
```

## ✅ Configuración Avanzada Completada

✅ **Debug logging** para desarrollo  
✅ **Multi-tenant switching** automático  
✅ **Testing utilities** completas  
✅ **Performance monitoring** incluido  
✅ **Diagnostic tools** para troubleshooting

**Continuar con:** `01a3_http_utils.md` (Utilidades HTTP genéricas)