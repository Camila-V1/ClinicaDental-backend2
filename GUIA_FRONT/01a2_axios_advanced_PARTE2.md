# 🔍 FASE 1A2: AXIOS AVANZADO - PARTE 2 (Debug & Performance)

## 🔧 Logging para Desarrollo (services/apiConfig.advanced.js)

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

export { api };
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

## 📊 Performance Monitoring (utils/debugHelpers.js)

```javascript
import api from '../services/apiConfig';

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

  clear() {
    this.requests = [];
    console.log('🧹 Performance monitor cleared');
  }

  printStats() {
    const stats = this.getStats();
    if (!stats) {
      console.log('📊 No performance data available');
      return;
    }
    
    console.log('📊 Performance Stats:', stats);
    console.table(this.requests.slice(-10)); // Mostrar últimas 10
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
      performanceMonitor.record(
        response.config.url, 
        response.config.method, 
        duration, 
        response.status
      );
      return response;
    },
    (error) => {
      const duration = Date.now() - (error.config?.startTime || 0);
      performanceMonitor.record(
        error.config?.url, 
        error.config?.method, 
        duration, 
        error.response?.status || 0
      );
      return Promise.reject(error);
    }
  );
}
```

## 🛠️ Herramientas de Debugging

```javascript
import { performanceMonitor } from './utils/debugHelpers';
import { quickDiagnostic, testAuth, testRefresh } from './utils/apiTesting';

// Ver estadísticas
performanceMonitor.printStats();

// Diagnóstico completo
const report = await quickDiagnostic();

// Test autenticación
const loginResult = await testAuth({ email: 'test@test.com', password: '123' });
const refreshResult = await testRefresh();
```

## 📋 Variables de Entorno

```bash
# .env.local
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=true  # Activa logging y performance monitoring
```

##  Métricas Monitoreadas

| Métrica | Descripción | Umbral |
|---------|-------------|--------|
| `avgDuration` | Tiempo promedio | < 1000ms |
| `errorRate` | % de errores | < 5% |
| `slowRequests` | Requests > 2s | 0 ideal |

## ✅ Debug & Performance Completado

✅ **Logging** automático en desarrollo  
✅ **Performance monitoring** con métricas  
✅ **Testing utilities** completas  
✅ **Diagnostic tools** para troubleshooting  
✅ **Production-safe** (desactivable)  

**Continuar con:** `01a3_http_utils.md` (Utilidades HTTP genéricas)


✅ **Logging** automático en desarrollo  
✅ **Performance monitoring** con métricas  
✅ **Testing utilities** completas  
✅ **Diagnostic tools** para troubleshooting  
✅ **Production-safe** (desactivable)  

**Continuar con:** `01a3_http_utils.md` (Utilidades HTTP genéricas)
