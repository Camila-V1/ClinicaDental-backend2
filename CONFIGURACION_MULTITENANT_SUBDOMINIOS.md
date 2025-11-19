# 🏥 Configuración Multi-Tenant con Subdominios

## 📋 Resumen

Tu sistema está configurado para soportar **múltiples clínicas** usando **subdominios dinámicos**. Cada clínica registrada obtiene su propio subdominio y datos aislados.

---

## 🌐 Arquitectura de Subdominios

### Desarrollo Local:
```
http://clinica-demo.localhost:8000   → Tenant: clinica_demo
http://otra-clinica.localhost:8000   → Tenant: otra_clinica
http://localhost:8000                → Schema público (registro)
```

### Producción (Render):
```
https://clinica-demo.onrender.com    → Tenant: clinica_demo
https://otra-clinica.onrender.com    → Tenant: otra_clinica
https://clinica-dental-backend.onrender.com → Schema público
```

### Frontend (Vercel/Netlify):
```
https://clinica-demo.vercel.app      → Frontend de clinica_demo
https://otra-clinica.vercel.app      → Frontend de otra_clinica
https://app.vercel.app               → Frontend principal (público)
```

---

## ⚙️ Configuración Aplicada en `settings.py`

### 1. **ALLOWED_HOSTS** (Hosts permitidos)

```python
# En producción
ALLOWED_HOSTS = ['.onrender.com']  # Permite *.onrender.com
```

**Resultado:**
- ✅ `clinica1.onrender.com` → Permitido
- ✅ `clinica2.onrender.com` → Permitido
- ✅ `cualquier-nombre.onrender.com` → Permitido

---

### 2. **CORS_ALLOWED_ORIGIN_REGEXES** (Subdominios permitidos)

```python
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://[\w-]+\.localhost:\d+$",   # *.localhost:puerto
    r"^https://[\w-]+\.onrender\.com$",  # *.onrender.com
    r"^https://[\w-]+\.vercel\.app$",    # *.vercel.app
    r"^https://[\w-]+\.netlify\.app$",   # *.netlify.app
]
```

**Resultado:**
- ✅ Peticiones desde `clinica1.vercel.app` → Permitidas
- ✅ Peticiones desde `clinica2.onrender.com` → Permitidas
- ✅ Cualquier subdominio válido → Permitido

---

### 3. **CSRF_TRUSTED_ORIGINS** (Formularios confiables)

```python
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.vercel.app',
    'https://*.netlify.app',
]
```

**Resultado:**
- ✅ Login desde `clinica1.vercel.app` → Confiable
- ✅ Formularios desde cualquier subdominio → Confiables

---

## 🔐 Variables de Entorno en Render

```bash
# ============================================
# CONFIGURACIÓN MULTI-TENANT
# ============================================

# Permite TODOS los subdominios de onrender.com
ALLOWED_HOSTS=.onrender.com

# CORS: Solo dominios principales (subdominios via regex)
CORS_ALLOWED_ORIGINS=https://clinica-dental-backend.onrender.com

# CSRF: Wildcards para subdominios
CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://*.vercel.app

# Base de datos
DATABASE_URL=postgresql://user:pass@host/db

# Configuración de Django
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui

# Tenant por defecto
DEFAULT_TENANT_SCHEMA=clinica_demo
DEFAULT_TENANT_DOMAIN=clinica-demo
```

---

## 🧪 Cómo Probar Subdominios Localmente

### 1. **Editar archivo hosts** (Windows):

```powershell
# Ejecutar PowerShell como Administrador
notepad C:\Windows\System32\drivers\etc\hosts
```

Agregar:
```
127.0.0.1    clinica-demo.localhost
127.0.0.1    otra-clinica.localhost
```

### 2. **Iniciar servidor Django**:

```bash
python manage.py runserver
```

### 3. **Probar subdominios**:

```bash
# Tenant: clinica-demo
http://clinica-demo.localhost:8000/api/

# Tenant: otra-clinica (si existe)
http://otra-clinica.localhost:8000/api/

# Público
http://localhost:8000/api/
```

---

## 🚀 Flujo de Registro de Nueva Clínica

### Backend Automático (django-tenants):

1. Usuario se registra desde el frontend público
2. Backend crea:
   - ✅ Nuevo registro en `tenants_clinica` (schema_name, domain_url)
   - ✅ Nuevo schema PostgreSQL con todas las tablas
   - ✅ Nuevo registro en `tenants_domain` (domain, tenant)
3. Backend retorna credenciales de acceso
4. Usuario accede a: `https://nueva-clinica.onrender.com`

### Código de Ejemplo:

```python
from tenants.models import Clinica, Domain

# Crear nueva clínica
nueva_clinica = Clinica.objects.create(
    schema_name='clinica_nueva',
    nombre='Clínica Nueva',
    dominio='clinica-nueva',  # Identificador único
    activo=True
)

# Crear el dominio asociado
Domain.objects.create(
    domain='clinica-nueva.onrender.com',  # O clinica-nueva.localhost en dev
    tenant=nueva_clinica,
    is_primary=True
)

# django-tenants automáticamente:
# 1. Crea el schema "clinica_nueva"
# 2. Ejecuta todas las migraciones en ese schema
# 3. Mapea el dominio "clinica-nueva.onrender.com" al schema
```

---

## 📡 Ejemplo de Peticiones CORS

### ✅ Petición Permitida:

```javascript
// Desde: https://clinica-demo.vercel.app
fetch('https://clinica-demo.onrender.com/api/citas/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json'
  }
})
// ✅ Permitido por CORS_ALLOWED_ORIGIN_REGEXES
```

### ✅ Login Permitido:

```javascript
// Desde: https://clinica-nueva.vercel.app
fetch('https://clinica-nueva.onrender.com/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'admin@clinica.com',
    password: 'password123'
  })
})
// ✅ Permitido por CSRF_TRUSTED_ORIGINS
```

---

## 🔍 Verificación de Configuración

### Comando para verificar settings:

```bash
python manage.py shell
```

```python
from django.conf import settings

# Ver ALLOWED_HOSTS
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)

# Ver CORS
print("CORS_ALLOWED_ORIGINS:", settings.CORS_ALLOWED_ORIGINS)
print("CORS_ALLOWED_ORIGIN_REGEXES:", settings.CORS_ALLOWED_ORIGIN_REGEXES)

# Ver CSRF
print("CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
```

### Verificar tenant:

```python
from tenants.models import Clinica, Domain

# Listar todas las clínicas
for clinica in Clinica.objects.all():
    print(f"Schema: {clinica.schema_name}")
    print(f"Nombre: {clinica.nombre}")
    print(f"Dominio: {clinica.dominio}")
    print(f"Activo: {clinica.activo}")
    
    # Ver dominios asociados
    for domain in clinica.domains.all():
        print(f"  → {domain.domain} (Primary: {domain.is_primary})")
    print("---")
```

---

## 🎯 Resumen de Ventajas

| Característica | Beneficio |
|---------------|-----------|
| **Subdominios Dinámicos** | Cada clínica tiene su URL única |
| **Datos Aislados** | Schema PostgreSQL separado por clínica |
| **CORS Automático** | Subdominios permitidos via regex |
| **CSRF Protegido** | Wildcards para subdominios confiables |
| **Escalable** | Agregar clínicas sin reconfigurar |
| **Seguro** | Usuarios no pueden acceder a datos de otras clínicas |

---

## 🛡️ Seguridad

### ¿Es seguro permitir *.onrender.com?

**Sí**, porque:
1. django-tenants **aísla los datos** por schema
2. Cada subdominio accede solo a **su propio schema**
3. La autenticación JWT es **por tenant**
4. Un usuario de clinica1.onrender.com **NO puede** acceder a datos de clinica2.onrender.com

### Flujo de Seguridad:

```
1. Usuario accede: https://clinica1.onrender.com/api/pacientes/
2. django-tenants detecta: domain="clinica1.onrender.com"
3. Busca en DB: Clinica con domain_url="clinica1"
4. Obtiene: schema_name="clinica_1"
5. Ejecuta query: SET search_path TO clinica_1
6. Devuelve: Solo pacientes del schema clinica_1
```

**Imposible** acceder a datos de otro tenant sin credenciales válidas de ese tenant.

---

## 📞 Soporte

Si tienes problemas con subdominios:

1. Verifica que el tenant existe: `python manage.py tenant_command shell`
2. Verifica el dominio en DB: `SELECT * FROM tenants_domain;`
3. Verifica CORS en browser DevTools (Network → Headers)
4. Revisa logs de Render para errores de middleware

---

**¡Tu sistema multi-tenant está listo para producción! 🎉**
