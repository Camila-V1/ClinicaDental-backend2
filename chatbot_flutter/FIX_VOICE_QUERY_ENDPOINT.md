# 🔧 Fix: Endpoint de Comandos de Voz - Error 404

## 🐛 Problema Detectado

El frontend está haciendo peticiones a:
```
❌ POST https://clinica-dental-backend.onrender.com/reportes/voice-query/
```

Pero el endpoint correcto es:
```
✅ POST https://clinica-dental-backend.onrender.com/api/reportes/voice-query/
```

**Falta el prefijo `/api/`**

---

## 📋 Error en Consola

```javascript
POST https://clinica-dental-backend.onrender.com/reportes/voice-query/ 404 (Not Found)

🚀 [API REQUEST] ==================
  Method: POST
  BaseURL: https://clinica-dental-backend.onrender.com
  URL: /reportes/voice-query/  ❌ INCORRECTO
  Full URL: https://clinica-dental-backend.onrender.com/reportes/voice-query/
  Data: {texto: 'Ingresos del mes actual'}
====================================
```

---

## ✅ Solución

### Opción 1: Corregir el Service (RECOMENDADO)

Busca el archivo del servicio de reportes con comandos de voz (probablemente `reportes_service.js` o `voice_service.js`) y cambia:

```javascript
// ❌ ANTES (Incorrecto)
const processVoiceCommand = async (texto) => {
  const response = await api.post('/reportes/voice-query/', { texto });
  return response.data;
};

// ✅ DESPUÉS (Correcto)
const processVoiceCommand = async (texto) => {
  const response = await api.post('/api/reportes/voice-query/', { texto });
  return response.data;
};
```

### Opción 2: Si usas axios configurado

Si tienes axios configurado con `baseURL`, asegúrate de que la ruta sea correcta:

```javascript
// En tu servicio
import api from './axios_core';

// ✅ La ruta DEBE incluir /api/
export const processVoiceCommand = async (texto) => {
  try {
    const response = await api.post('/api/reportes/voice-query/', { 
      texto 
    });
    return response.data;
  } catch (error) {
    console.error('Error en comando de voz:', error);
    throw error;
  }
};
```

---

## 🧪 Verificación Backend

El endpoint **SÍ EXISTE** en el backend y está correctamente configurado:

### 1. Archivo: `reportes/urls.py`
```python
from .voice_views import VoiceReportQueryView

urlpatterns = [
    path('', include(router.urls)),
    path('voice-query/', VoiceReportQueryView.as_view(), name='voice-query'),
]
```

### 2. Archivo: `core/urls_tenant.py` y `core/urls_public.py`
```python
urlpatterns = [
    ...
    path('api/reportes/', include('reportes.urls')),  # ✅ Prefijo /api/
    ...
]
```

### 3. URL Final Completa
```
✅ POST /api/reportes/voice-query/
```

---

## 📝 Formato del Request

### Request Body:
```json
{
  "texto": "Ingresos del mes actual"
}
```

### Headers:
```javascript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer YOUR_TOKEN",
  "X-Tenant-ID": "clinica_demo"
}
```

### Response Exitosa (200 OK):
```json
{
  "interpretacion": {
    "texto_original": "Ingresos del mes actual",
    "tipo_reporte": "ingresos",
    "fecha_inicio": "2025-11-01",
    "fecha_fin": "2025-11-30",
    "filtros": {},
    "interpretacion": "Reporte de ingresos desde el 01/11/2025 hasta el 30/11/2025"
  },
  "datos": [
    {
      "id": 1,
      "fecha": "27/11/2025 10:30",
      "monto": 150.00,
      "metodo_pago": "Efectivo",
      "factura": "FAC-000001",
      "paciente": "Juan Pérez"
    }
  ],
  "resumen": {
    "total": 1,
    "tipo": "ingresos",
    "periodo": "01/11/2025 - 30/11/2025",
    "total_ingresos": 510.00,
    "promedio": 510.00
  }
}
```

---

## 🔍 Comandos de Voz Soportados

El backend ya tiene implementado el procesamiento NLP para estos comandos:

### Reportes de Citas:
- ✅ "citas del mes"
- ✅ "citas de hoy"
- ✅ "citas del 1 al 5 de septiembre"
- ✅ "agenda de la semana"

### Reportes de Ingresos:
- ✅ "ingresos del mes"
- ✅ "ingresos del mes actual"
- ✅ "cuánto ganamos en noviembre"

### Reportes de Facturas:
- ✅ "facturas pendientes"
- ✅ "facturas del mes"
- ✅ "facturas completadas de septiembre"

### Reportes de Tratamientos:
- ✅ "tratamientos en progreso"
- ✅ "tratamientos del mes"

### Reportes de Pacientes:
- ✅ "pacientes nuevos del mes"
- ✅ "pacientes registrados en octubre"

---

## 🧪 Prueba con CURL

Para verificar que el endpoint funciona en el backend:

```bash
curl -X POST https://clinica-dental-backend.onrender.com/api/reportes/voice-query/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-ID: clinica_demo" \
  -d '{"texto": "Ingresos del mes actual"}'
```

---

## 📁 Archivos a Modificar en el Frontend

Busca y corrige en estos archivos:

1. **`src/services/reportes_service.js`** o similar
2. **`src/services/voice_service.js`** (si existe)
3. **Cualquier componente que llame directamente al endpoint**

### Busca este patrón:
```javascript
// ❌ Patrones incorrectos a buscar y corregir
api.post('/reportes/voice-query/', ...)
axios.post('https://...com/reportes/voice-query/', ...)
fetch('.../reportes/voice-query/', ...)
```

### Reemplaza por:
```javascript
// ✅ Patrón correcto
api.post('/api/reportes/voice-query/', ...)
axios.post('https://...com/api/reportes/voice-query/', ...)
fetch('.../api/reportes/voice-query/', ...)
```

---

## ✅ Checklist de Verificación

- [ ] Localizar archivo del servicio de voz en el frontend
- [ ] Cambiar `/reportes/voice-query/` → `/api/reportes/voice-query/`
- [ ] Recompilar el frontend (npm run build o similar)
- [ ] Probar con un comando simple: "citas de hoy"
- [ ] Verificar en DevTools que la URL ahora incluye `/api/`
- [ ] Comprobar que la respuesta es 200 OK con datos

---

## 🎯 Resumen

**Problema**: Falta `/api/` en la URL del frontend
**Solución**: Agregar `/api/` antes de `/reportes/voice-query/`
**Endpoint correcto**: `POST /api/reportes/voice-query/`

Una vez corregido, los comandos de voz funcionarán correctamente. 🎤✅
