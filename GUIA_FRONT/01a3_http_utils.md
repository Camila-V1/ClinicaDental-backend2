# 🔐 FASE 1A2: UTILIDADES HTTP Y HELPERS

## 🔧 Utilidades HTTP Genéricas (services/httpUtils.js)

```javascript
import api from './apiConfig';

// Wrapper genérico para manejo consistente de errores
const handleResponse = (response) => ({
  success: true,
  data: response.data,
  status: response.status
});

const handleError = (error) => ({
  success: false,
  error: error.response?.data?.detail || 
         error.response?.data?.message || 
         error.response?.data || 
         error.message || 
         'Error en la petición',
  status: error.response?.status || 0
});

// Función GET
export const get = async (url, config = {}) => {
  try {
    const response = await api.get(url, config);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

// Función POST
export const post = async (url, data = {}, config = {}) => {
  try {
    const response = await api.post(url, data, config);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

// Función PUT
export const put = async (url, data = {}, config = {}) => {
  try {
    const response = await api.put(url, data, config);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

// Función PATCH
export const patch = async (url, data = {}, config = {}) => {
  try {
    const response = await api.patch(url, data, config);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

// Función DELETE
export const del = async (url, config = {}) => {
  try {
    const response = await api.delete(url, config);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};
```

## 📁 Utilidades para Archivos (services/fileUtils.js)

```javascript
import api from './apiConfig';

// Upload de archivo con progress
export const uploadFile = async (url, file, onProgress = null) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const config = {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress ? (event) => {
        const progress = Math.round((event.loaded * 100) / event.total);
        onProgress(progress);
      } : undefined
    };
    
    const response = await api.post(url, formData, config);
    return { success: true, data: response.data, fileName: file.name };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Error al subir archivo'
    };
  }
};

// Download de archivo
export const downloadFile = async (url, filename) => {
  try {
    const response = await api.get(url, { responseType: 'blob' });
    
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Error al descargar'
    };
  }
};
```

## 🔄 Utilidades Avanzadas (services/advancedUtils.js)

```javascript
import { get } from './httpUtils';

// Paginación helper para listas
export const getPaginated = async (url, page = 1, pageSize = 10) => {
  const result = await get(`${url}?page=${page}&page_size=${pageSize}`);
  
  if (result.success) {
    return {
      ...result,
      pagination: {
        page,
        pageSize,
        total: result.data.count || 0,
        totalPages: Math.ceil((result.data.count || 0) / pageSize),
        hasNext: !!result.data.next,
        hasPrevious: !!result.data.previous
      }
    };
  }
  
  return result;
};

// Cache simple para requests frecuentes
const cache = new Map();
export const getCached = async (url, ttl = 300000) => { // 5min default
  const cached = cache.get(url);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return { ...cached.data, fromCache: true };
  }
  
  const result = await get(url);
  if (result.success) {
    cache.set(url, { data: result, timestamp: Date.now() });
  }
  
  return result;
};

// Búsqueda con debounce
let searchTimeout;
export const searchWithDebounce = async (url, query, delay = 300) => {
  return new Promise((resolve) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      const result = await get(`${url}?search=${encodeURIComponent(query)}`);
      resolve(result);
    }, delay);
  });
};
```

## 🛠️ Utilidades de Validación (utils/validation.js)

```javascript
// Validar respuesta de API
export const isValidResponse = (response) => {
  return response?.success && response?.data;
};

// Sanitizar datos antes de envío
export const sanitizeData = (data) => {
  if (!data || typeof data !== 'object') return data;
  
  const sanitized = {};
  Object.keys(data).forEach(key => {
    const value = data[key];
    if (value !== undefined && value !== null && value !== '') {
      sanitized[key] = value;
    }
  });
  
  return sanitized;
};

// Formatear errores de API para UI
export const formatError = (error) => {
  if (typeof error === 'string') return error;
  if (error?.detail) return error.detail;
  if (error?.message) return error.message;
  
  // Errores de campo de formulario
  if (typeof error === 'object') {
    const fieldErrors = Object.entries(error)
      .map(([field, messages]) => {
        const msg = Array.isArray(messages) ? messages.join(', ') : messages;
        return `${field}: ${msg}`;
      })
      .join('\n');
    
    if (fieldErrors) return fieldErrors;
  }
  
  return 'Error desconocido';
};
```

## ✅ Utilidades HTTP Completadas

✅ **HTTP helpers** genéricos y reutilizables  
✅ **File upload/download** con progress tracking  
✅ **Cache system** simple y efectivo  
✅ **Pagination helpers** para listas  
✅ **Validation utilities** para datos  
✅ **Error formatting** para UX mejorada

**Continuar con:** `01b_auth_service.md` (AuthService y hooks)