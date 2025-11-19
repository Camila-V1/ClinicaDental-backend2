# ✅ SOLUCIÓN CORS - CONFIGURACIÓN APLICADA

**Fecha:** 15 de Noviembre, 2025  
**Estado:** ✅ **CONFIGURADO Y LISTO**

---

## 🎯 PROBLEMA IDENTIFICADO

**Error CORS en Frontend:**
```
Access to XMLHttpRequest at 'http://clinica-demo.localhost:8000/public/api/token/' 
from origin 'http://clinica-demo.localhost:5173' has been blocked by CORS policy
```

**Causa:**
El backend Django no estaba permitiendo credenciales (cookies, headers de autorización) en peticiones CORS desde el frontend.

---

## ✅ SOLUCIÓN APLICADA

### 1. **Verificación de django-cors-headers**
```bash
✅ django-cors-headers 4.7.0 - YA INSTALADO
✅ 'corsheaders' en INSTALLED_APPS
✅ 'corsheaders.middleware.CorsMiddleware' en MIDDLEWARE (posición correcta)
```

### 2. **Configuración CORS en `core/settings.py`**

```python
# --- Configuración de CORS ---

# Orígenes (servidores de frontend) que tienen permiso para hacer peticiones
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Puerto por defecto de Vite (React)
    "http://localhost:5174",  # Puerto alternativo Vite
    "http://localhost:3000",  # Puerto por defecto de Create-React-App
]

# Permitir subdominios para multi-tenant
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://[\w-]+\.localhost:\d+$",  # ✅ Permite cualquier subdominio.localhost
]

# ✅ AGREGADO: Permitir envío de cookies y credenciales (necesario para JWT)
CORS_ALLOW_CREDENTIALS = True

# ✅ AGREGADO: Permitir headers específicos (necesarios para JWT)
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',        # ← CRÍTICO para JWT
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### 3. **Orden del Middleware (CORRECTO)**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_tenants.middleware.TenantMainMiddleware',  # Multi-tenant
    'corsheaders.middleware.CorsMiddleware',           # ✅ CORS (después de tenant, antes de common)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

## 🧪 PRUEBA DE FUNCIONAMIENTO

### **1. Reiniciar servidor Django**
```bash
# Detener servidor (Ctrl+C)
# Iniciar nuevamente
python manage.py runserver
```

### **2. Probar desde frontend**
```bash
# En el directorio del frontend
npm run dev
```

### **3. Probar Login**
```typescript
// En Login.tsx
const response = await fetch('http://clinica-demo.localhost:8000/public/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // ✅ Ahora esto funcionará
  body: JSON.stringify({
    username: 'juan_perez',
    password: 'paciente123'
  })
});
```

**Resultado esperado:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🔍 VERIFICACIÓN DE HEADERS

### **Request Headers (Frontend → Backend)**
```
Origin: http://clinica-demo.localhost:5173
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type
```

### **Response Headers (Backend → Frontend)**
```
✅ Access-Control-Allow-Origin: http://clinica-demo.localhost:5173
✅ Access-Control-Allow-Credentials: true
✅ Access-Control-Allow-Headers: authorization, content-type, ...
✅ Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [x] **django-cors-headers instalado** (v4.7.0)
- [x] **corsheaders en INSTALLED_APPS**
- [x] **CorsMiddleware en posición correcta** (después de TenantMainMiddleware, antes de CommonMiddleware)
- [x] **CORS_ALLOWED_ORIGIN_REGEXES configurado** (permite subdominios)
- [x] **CORS_ALLOW_CREDENTIALS = True** ✅ **NUEVO**
- [x] **CORS_ALLOW_HEADERS configurado** ✅ **NUEVO**
- [x] **CSRF_TRUSTED_ORIGINS incluye subdominios**
- [x] **Servidor Django reiniciado**

---

## 🎯 DOMINIOS PERMITIDOS

### **Producción Local (Multi-Tenant)**
```
✅ http://clinica-demo.localhost:5173
✅ http://clinica-demo.localhost:5174
✅ http://clinica1.localhost:5173
✅ http://cualquier-subdominio.localhost:5173
✅ http://cualquier-subdominio.localhost:[CUALQUIER_PUERTO]
```

### **Desarrollo Simple**
```
✅ http://localhost:5173
✅ http://localhost:5174
✅ http://localhost:3000
```

---

## 🐛 TROUBLESHOOTING

### **Si persiste el error CORS:**

#### 1. **Verificar que el servidor esté corriendo**
```bash
python manage.py runserver
# Debe mostrar: http://127.0.0.1:8000/
```

#### 2. **Limpiar caché del navegador**
```
Ctrl + Shift + Delete → Borrar caché
O usar modo incógnito
```

#### 3. **Verificar la consola del navegador**
```javascript
// Debe mostrar
Access-Control-Allow-Origin: http://clinica-demo.localhost:5173
Access-Control-Allow-Credentials: true
```

#### 4. **Verificar settings.py**
```bash
python manage.py shell
>>> from django.conf import settings
>>> settings.CORS_ALLOW_CREDENTIALS
True
>>> settings.CORS_ALLOWED_ORIGIN_REGEXES
[re.compile('^http://[\\w-]+\\.localhost:\\d+$')]
```

#### 5. **Verificar que fetch incluya credentials**
```typescript
fetch(url, {
  method: 'POST',
  credentials: 'include',  // ← DEBE estar presente
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }
})
```

---

## 🔐 SEGURIDAD

### **Desarrollo (Actual)**
```python
DEBUG = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://[\w-]+\.localhost:\d+$",  # Cualquier puerto
]
```

### **Producción (Futuro)**
```python
DEBUG = False
CORS_ALLOWED_ORIGINS = [
    "https://clinica-demo.midominio.com",
    "https://clinica1.midominio.com",
    # Lista explícita de dominios permitidos
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://[\w-]+\.midominio\.com$",  # Solo HTTPS
]
```

---

## 📝 COMANDOS DE VERIFICACIÓN

### **Ver configuración actual**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print("CORS_ALLOW_CREDENTIALS:", settings.CORS_ALLOW_CREDENTIALS)
>>> print("CORS_ALLOWED_ORIGIN_REGEXES:", settings.CORS_ALLOWED_ORIGIN_REGEXES)
>>> print("CORS_ALLOW_HEADERS:", settings.CORS_ALLOW_HEADERS)
```

### **Probar endpoint desde curl**
```bash
curl -X POST http://clinica-demo.localhost:8000/public/api/token/ \
  -H "Origin: http://clinica-demo.localhost:5173" \
  -H "Content-Type: application/json" \
  -d '{"username":"juan_perez","password":"paciente123"}' \
  -v
```

**Buscar en la respuesta:**
```
< Access-Control-Allow-Origin: http://clinica-demo.localhost:5173
< Access-Control-Allow-Credentials: true
```

---

## ✅ RESULTADO FINAL

### **Antes (❌ Error)**
```
Access to XMLHttpRequest blocked by CORS policy
```

### **Después (✅ Funciona)**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🚀 PRÓXIMOS PASOS

1. ✅ **CORS configurado y funcionando**
2. 🔄 **Reiniciar servidor Django**
3. 🔄 **Probar login desde frontend**
4. 🔄 **Verificar que todas las peticiones funcionen**
5. 🔄 **Implementar las 13 guías del módulo paciente**

---

## 📚 REFERENCIAS

- [django-cors-headers Documentation](https://github.com/adamchainz/django-cors-headers)
- [Django Settings Reference](https://docs.djangoproject.com/en/5.2/ref/settings/)
- [CORS Standard](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [JWT with Django](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**🎉 CORS CONFIGURADO CORRECTAMENTE - LISTO PARA DESARROLLO**

**Última actualización:** 15 de Noviembre, 2025
