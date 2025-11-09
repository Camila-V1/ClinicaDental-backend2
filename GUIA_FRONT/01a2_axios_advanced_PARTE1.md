# 🏢 FASE 1A2: AXIOS AVANZADO - PARTE 1 (Multi-Tenant)

## 🔧 Configuración Avanzada - Switch de Base URL

```javascript
import api from './apiConfig';

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

## 🏢 Multi-Tenant Support (services/tenantManager.js)

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

## 🔄 Uso en App Principal (App.js o index.js)

```javascript
import React, { useEffect } from 'react';
import { configureTenantApi, getCurrentTenant } from './services/tenantManager';

function App() {
  useEffect(() => {
    // Configurar API según el tenant al iniciar la app
    const tenantConfig = configureTenantApi();
    
    console.log('🏢 Tenant Configuration:', tenantConfig);
    console.log('📍 Current Tenant:', getCurrentTenant());
    
    // Guardar info del tenant en contexto si es necesario
    if (tenantConfig.configured) {
      sessionStorage.setItem('currentTenant', tenantConfig.tenant);
    }
  }, []);
  
  return (
    <div className="App">
      {/* Tu aplicación */}
    </div>
  );
}

export default App;
```

## 🧪 Testing del Sistema Multi-Tenant

```javascript
import { configureTenantApi, detectTenant, getCurrentTenant } from './services/tenantManager';

// Test de detección de tenant
export const testTenantDetection = () => {
  const detected = detectTenant();
  console.log('🔍 Tenant Detection:', detected);
  
  return {
    hostname: window.location.hostname,
    detected,
    expected: {
      localhost: { tenant: null, isMultiTenant: false },
      'clinica-demo.localhost': { tenant: 'clinica-demo', isMultiTenant: true }
    }
  };
};

// Test de configuración completa
export const testTenantConfiguration = () => {
  const config = configureTenantApi();
  const current = getCurrentTenant();
  
  console.log('⚙️ Tenant Config Test:', { config, current });
  
  return {
    success: config.configured !== undefined,
    config,
    current,
    apiUrl: current.apiUrl
  };
};
```

## 📋 Escenarios de Uso Multi-Tenant

### Escenario 1: Localhost (Sin Tenant)
```
URL: http://localhost:3000
Tenant: null
API URL: http://localhost:8000
Esquema BD: public
```

### Escenario 2: Clínica Demo (Desarrollo)
```
URL: http://clinica-demo.localhost:3000
Tenant: clinica-demo
API URL: http://clinica-demo.localhost:8000
Esquema BD: clinica_demo
```

### Escenario 3: Clínica ABC (Producción)
```
URL: https://clinica-abc.tudominio.com
Tenant: clinica-abc
API URL: https://clinica-abc.tudominio.com
Esquema BD: clinica_abc
```

## ⚠️ Consideraciones Importantes

### 1. Autenticación por Tenant
Cada tenant tiene su propia autenticación JWT independiente:
```javascript
// Los tokens se almacenan separados por tenant
const storageKey = `accessToken_${currentTenant}`;
localStorage.setItem(storageKey, token);
```

### 2. CORS en Backend
Asegúrate que el backend Django tenga CORS configurado para los subdominios:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://clinica-demo.localhost:3000",
    "http://clinica-test.localhost:3000",
]
```

### 3. Hosts File (Desarrollo Windows)
Para desarrollo local, configurar `C:\Windows\System32\drivers\etc\hosts`:
```
127.0.0.1 localhost
127.0.0.1 clinica-demo.localhost
127.0.0.1 clinica-test.localhost
```

## ✅ Multi-Tenant Configurado

✅ **Detección automática** de tenant desde URL  
✅ **Switch dinámico** de base URL  
✅ **Testing utilities** para verificación  
✅ **Integración** en App principal  
✅ **Soporte** para desarrollo y producción  

**Continuar con:** `01a2_axios_advanced_PARTE2.md` (Debugging y Performance)
