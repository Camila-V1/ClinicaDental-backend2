# 🔍 FASE 1A1: VALIDADORES Y TESTING

## 🔍 Validadores de Configuración (utils/configValidator.js)

```javascript
import api from '../services/apiConfig';

// Verificar que las variables de entorno estén configuradas
export const validateEnvVars = () => {
  const requiredVars = ['REACT_APP_API_URL'];
  const missing = requiredVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    console.error('❌ Missing environment variables:', missing);
    return { valid: false, missing };
  }
  
  console.log('✅ Environment variables configured correctly');
  return { valid: true, missing: [] };
};

// Test básico de conectividad con el backend
export const testApiConnection = async () => {
  try {
    // Intentar hacer una petición simple al backend
    const response = await api.get('/api/usuarios/health/', {
      validateStatus: (status) => status >= 200 && status < 500
    });
    
    return { 
      connected: true, 
      status: response.status,
      message: 'Backend is reachable'
    };
  } catch (error) {
    return { 
      connected: false, 
      status: error.response?.status || 0,
      message: error.message || 'Backend unreachable'
    };
  }
};

// Verificar estructura de respuesta JWT
export const validateJWTResponse = (responseData) => {
  const hasAccess = responseData && typeof responseData.access === 'string';
  const hasRefresh = responseData && typeof responseData.refresh === 'string';
  const hasUser = responseData && typeof responseData.user === 'object';
  
  return {
    valid: hasAccess && hasRefresh && hasUser,
    details: {
      hasAccessToken: hasAccess,
      hasRefreshToken: hasRefresh,
      hasUserData: hasUser,
      userType: responseData.user?.tipo_usuario || 'unknown'
    }
  };
};

// Validar formato de token JWT
export const validateTokenFormat = (token) => {
  if (!token || typeof token !== 'string') {
    return { valid: false, error: 'Token must be a string' };
  }
  
  const parts = token.split('.');
  if (parts.length !== 3) {
    return { valid: false, error: 'JWT must have 3 parts' };
  }
  
  try {
    // Intentar decodificar el payload
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    return {
      valid: true,
      isExpired: payload.exp < now,
      expiresIn: payload.exp - now,
      userId: payload.user_id
    };
  } catch (error) {
    return { valid: false, error: 'Invalid JWT format' };
  }
};
```

## 🧪 Testing Utilities (utils/apiTesting.js)

```javascript
import { validateEnvVars, testApiConnection, validateJWTResponse } from './configValidator';
import { getApiConfig, hasValidTokens } from './tokenHelpers';

// Ejecutar todos los tests de configuración
export const runConfigurationTests = async () => {
  console.log('🔧 Running configuration tests...');
  
  const results = {
    environment: validateEnvVars(),
    connectivity: await testApiConnection(),
    tokens: hasValidTokens(),
    config: getApiConfig()
  };
  
  console.log('📊 Configuration test results:', results);
  return results;
};

// Test de autenticación con credenciales
export const testAuthFlow = async (credentials) => {
  try {
    const response = await fetch('/api/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    const validation = validateJWTResponse(data);
    
    return {
      success: true,
      validation,
      tokens: {
        access: data.access?.substring(0, 20) + '...',
        refresh: data.refresh?.substring(0, 20) + '...'
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      status: error.status || 'unknown'
    };
  }
};

// Diagnóstico completo del sistema
export const runFullDiagnostic = async () => {
  const diagnostic = {
    timestamp: new Date().toISOString(),
    tests: await runConfigurationTests()
  };
  
  // Agregar información del navegador
  diagnostic.browser = {
    userAgent: navigator.userAgent,
    language: navigator.language,
    localStorage: typeof Storage !== 'undefined'
  };
  
  console.log('🩺 Full system diagnostic:', diagnostic);
  return diagnostic;
};
```

## 🔄 Status Checker (utils/statusChecker.js)

```javascript
import api from '../services/apiConfig';
import { parseJWTPayload } from './tokenHelpers';

// Verificar estado de autenticación
export const checkAuthStatus = () => {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!accessToken || !refreshToken) {
    return { authenticated: false, reason: 'No tokens found' };
  }
  
  const tokenInfo = parseJWTPayload(accessToken);
  if (!tokenInfo.valid) {
    return { authenticated: false, reason: 'Invalid token format' };
  }
  
  if (tokenInfo.expiresIn <= 0) {
    return { 
      authenticated: false, 
      reason: 'Access token expired',
      needsRefresh: true 
    };
  }
  
  return {
    authenticated: true,
    expiresIn: tokenInfo.expiresIn,
    userId: tokenInfo.userId
  };
};

// Verificar salud del API
export const checkApiHealth = async () => {
  try {
    const response = await api.get('/api/usuarios/health/', { timeout: 5000 });
    return {
      healthy: true,
      status: response.status,
      responseTime: response.headers['x-response-time'] || 'unknown'
    };
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
      status: error.response?.status || 0
    };
  }
};
```

## ✅ Validación Completa

✅ **Environment validation** implementada  
✅ **API connectivity testing** configurado  
✅ **JWT response validation** incluida  
✅ **Auth flow testing** disponible  
✅ **System diagnostic** completo  
✅ **Status checking** implementado

**Continuar con:** `01a2_axios_advanced.md` (Multi-tenant y debugging avanzado)