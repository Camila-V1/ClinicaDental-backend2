# ⚙️ Configuración Frontend - Vercel

## 📋 Variables de Entorno

### ✅ Configuración Correcta para Producción

```bash
# ============================================================================
# ENTORNO
# ============================================================================
VITE_ENVIRONMENT=production

# ============================================================================
# BACKEND API (Render)
# ============================================================================
# URL completa de la API (incluye /api/v1 si tienes versionado)
VITE_API_URL=https://clinica-dental-backend.onrender.com/api/v1

# URL base del backend (sin path)
VITE_API_BASE_URL=https://clinica-dental-backend.onrender.com

# ============================================================================
# MULTI-TENANT
# ============================================================================
# Dominio base para tenants (sin https://)
VITE_BASE_DOMAIN=onrender.com

# Patrón de subdominio para tenants
VITE_TENANT_DOMAIN_PATTERN={tenant}.onrender.com

# Dominio público (sin tenant específico)
VITE_PUBLIC_DOMAIN=clinica-dental-backend.onrender.com

# ============================================================================
# FRONTEND
# ============================================================================
# Tu dominio de Vercel/Custom domain
VITE_FRONTEND_URL=https://dentaabcxy.store

# Habilitar multi-tenant por subdominio
VITE_USE_SUBDOMAIN=true

# ============================================================================
# CONFIGURACIÓN GENERAL
# ============================================================================
# Debug desactivado en producción
VITE_DEBUG=false

# Timeout para peticiones API (15 segundos)
VITE_API_TIMEOUT=15000

# Nombre de la aplicación
VITE_APP_NAME=Clinica Dental

# Versión
VITE_APP_VERSION=1.0.0

# ============================================================================
# PAGOS (Opcional - si usas Stripe)
# ============================================================================
# VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

---

## 🔧 Pasos para Configurar en Vercel

### 1. **Acceder a Variables de Entorno**

1. Ve a [vercel.com](https://vercel.com)
2. Selecciona tu proyecto
3. Click en **Settings**
4. Click en **Environment Variables**

### 2. **Agregar Variables una por una**

Para cada variable:

| Name | Value | Environment |
|------|-------|-------------|
| `VITE_ENVIRONMENT` | `production` | ✅ Production |
| `VITE_API_URL` | `https://clinica-dental-backend.onrender.com/api/v1` | ✅ Production |
| `VITE_API_BASE_URL` | `https://clinica-dental-backend.onrender.com` | ✅ Production |
| `VITE_BASE_DOMAIN` | `onrender.com` | ✅ Production |
| `VITE_TENANT_DOMAIN_PATTERN` | `{tenant}.onrender.com` | ✅ Production |
| `VITE_PUBLIC_DOMAIN` | `clinica-dental-backend.onrender.com` | ✅ Production |
| `VITE_FRONTEND_URL` | `https://dentaabcxy.store` | ✅ Production |
| `VITE_USE_SUBDOMAIN` | `true` | ✅ Production |
| `VITE_DEBUG` | `false` | ✅ Production |
| `VITE_API_TIMEOUT` | `15000` | ✅ Production |
| `VITE_APP_NAME` | `Clinica Dental` | ✅ Production |
| `VITE_APP_VERSION` | `1.0.0` | ✅ Production |

### 3. **Redeploy**

Después de agregar todas las variables:
1. Ve a **Deployments**
2. Click en el último deployment
3. Click en **⋯** (tres puntos)
4. Click en **Redeploy**
5. Selecciona **Use existing Build Cache** (más rápido)
6. Click en **Redeploy**

---

## ❌ Errores Comunes

### 1. **VITE_API_URL sin /api/v1**

```bash
# ❌ Error: Endpoints no se encuentran
VITE_API_URL=https://clinica-dental-backend.onrender.com

# ✅ Correcto: Incluye el path base de tu API
VITE_API_URL=https://clinica-dental-backend.onrender.com/api/v1
```

**Síntoma:** 404 en todas las peticiones al backend

---

### 2. **VITE_FRONTEND_URL incorrecto**

```bash
# ❌ Error: Dominio temporal de Vercel
VITE_FRONTEND_URL=https://mi-proyecto-abc123.vercel.app

# ✅ Correcto: Tu dominio custom
VITE_FRONTEND_URL=https://dentaabcxy.store
```

**Síntoma:** Errores de CORS, redirects incorrectos

---

### 3. **Olvidar redeploy después de agregar variables**

Las variables solo se aplican en **nuevos deployments**.

**Solución:** Siempre haz **Redeploy** después de cambiar variables.

---

## 🧪 Verificar Configuración

### En el navegador (DevTools → Console):

```javascript
// Verificar que las variables se cargaron
console.log('API URL:', import.meta.env.VITE_API_URL)
console.log('Frontend URL:', import.meta.env.VITE_FRONTEND_URL)
console.log('Base Domain:', import.meta.env.VITE_BASE_DOMAIN)
console.log('Environment:', import.meta.env.VITE_ENVIRONMENT)
```

**Resultado esperado:**
```
API URL: https://clinica-dental-backend.onrender.com/api/v1
Frontend URL: https://dentaabcxy.store
Base Domain: onrender.com
Environment: production
```

---

## 🌐 Configuración de Dominio Custom (dentaabcxy.store)

Si ya configuraste `dentaabcxy.store` en Vercel:

### 1. **Verificar DNS**

En tu proveedor de dominio (Namecheap, GoDaddy, etc.):

```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
```

O si usas A records:
```
Type: A
Name: @
Value: 76.76.21.21
```

### 2. **Actualizar Backend (Render)**

Actualiza las variables de entorno en Render para incluir tu dominio:

```bash
CORS_ALLOWED_ORIGINS=https://dentaabcxy.store,https://clinica-dental-backend.onrender.com

CSRF_TRUSTED_ORIGINS=https://dentaabcxy.store,https://*.onrender.com
```

---

## 🔄 Flujo de Peticiones

### Desarrollo Local:
```
Frontend (localhost:5173)
    ↓
Backend (localhost:8000/api/v1)
```

### Producción:
```
Frontend (dentaabcxy.store)
    ↓
Backend (clinica-dental-backend.onrender.com/api/v1)
```

### Multi-Tenant:
```
Frontend Clinica 1 (clinica1.dentaabcxy.store)
    ↓
Backend Tenant 1 (clinica1.onrender.com/api/v1)

Frontend Clinica 2 (clinica2.dentaabcxy.store)
    ↓
Backend Tenant 2 (clinica2.onrender.com/api/v1)
```

---

## 📊 Ejemplo de Código Frontend

### axiosCore.ts:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '15000');

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar tenant automáticamente
axiosInstance.interceptors.request.use((config) => {
  const tenant = getTenantFromURL(); // Función que extrae tenant del subdominio
  if (tenant) {
    config.headers['X-Tenant'] = tenant;
  }
  return config;
});
```

### getTenantFromURL.ts:

```typescript
export function getTenantFromURL(): string | null {
  const hostname = window.location.hostname;
  const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'localhost';
  
  // Desarrollo: clinica-demo.localhost
  // Producción: clinica-demo.onrender.com
  const parts = hostname.split('.');
  
  if (parts.length >= 2) {
    const tenant = parts[0];
    // Excluir 'www' y el dominio principal
    if (tenant !== 'www' && !hostname.includes('vercel.app')) {
      return tenant;
    }
  }
  
  return null;
}
```

---

## ✅ Checklist Final

Antes de considerar la configuración completa:

- [ ] Variables agregadas en Vercel
- [ ] Redeploy realizado en Vercel
- [ ] Dominio custom configurado (dentaabcxy.store)
- [ ] Backend actualizado con CORS para tu dominio
- [ ] Verificado en DevTools que las variables se cargan
- [ ] Petición de prueba al backend exitosa
- [ ] Login funciona correctamente
- [ ] Multi-tenant funciona con subdominios

---

## 🚨 Si Algo No Funciona

### 1. **Check CORS Errors**

En DevTools → Network → Headers:

```
Request URL: https://clinica-dental-backend.onrender.com/api/v1/token/
Request Method: POST
Status Code: 403 Forbidden

Access-Control-Allow-Origin: null  ← ERROR
```

**Solución:** Actualiza `CORS_ALLOWED_ORIGINS` en Render.

---

### 2. **Check 404 Errors**

```
GET https://clinica-dental-backend.onrender.com/token/
Status Code: 404 Not Found
```

**Problema:** Falta `/api/v1/` en la URL

**Solución:** Verifica que `VITE_API_URL` incluya `/api/v1`

---

### 3. **Variables no se aplican**

**Problema:** Cambios de variables no se reflejan

**Solución:** 
1. Vercel → Settings → Environment Variables
2. Verifica que estén en **Production** ✅
3. **Redeploy** obligatorio

---

## 📞 Soporte

- **Vercel Docs:** https://vercel.com/docs/concepts/projects/environment-variables
- **Vite Docs:** https://vitejs.dev/guide/env-and-mode.html

---

**¡Tu frontend está listo para producción! 🚀**
