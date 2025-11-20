# ✅ PASOS SIGUIENTES - SUBDOMINIOS CONFIGURADOS

## 🎉 ESTADO ACTUAL

### ✅ Completado:

1. **DNS en Namecheap** → Configurado correctamente
   ```
   clinicademo1 → cname.vercel-dns.com ✅
   clinicaabc   → cname.vercel-dns.com ✅
   clinicaxyz   → cname.vercel-dns.com ✅
   ```

2. **Vercel** → Dominios agregados y SSL generándose
   ```
   clinicademo1.dentaabcxy.store ✅
   clinicaabc.dentaabcxy.store   ✅
   clinicaxyz.dentaabcxy.store   ✅
   ```

3. **Backend - Middleware** → Actualizado para leer header `X-Tenant-ID` ✅

4. **Backend - Script** → Creado `crear_tenants_subdominios.py` ✅

5. **Frontend - Documentación** → Código listo en `CODIGO_FRONTEND_SUBDOMINIOS.md` ✅

---

## 📋 LO QUE FALTA HACER

### 🔴 BACKEND (hacer primero)

#### Paso 1: Crear los tenants en la base de datos

```bash
# En tu terminal local o en Render Shell
python crear_tenants_subdominios.py
```

Esto creará:
- `clinica_demo1` (schema para clinicademo1.dentaabcxy.store)
- `clinica_abc` (schema para clinicaabc.dentaabcxy.store)
- `clinica_xyz` (schema para clinicaxyz.dentaabcxy.store)

#### Paso 2: Poblar datos en cada tenant (opcional pero recomendado)

Para cada tenant, necesitas crear usuarios de prueba:

```bash
# Opción A: Manualmente usando Django shell
python manage.py tenant_command shell --schema=clinica_demo1

# Dentro del shell:
from usuarios.models import Usuario
from django.contrib.auth.hashers import make_password

# Crear odontólogo
odontologo = Usuario.objects.create(
    email='odontologo@clinicademo1.com',
    username='odontologo1',
    password=make_password('odontologo123'),
    rol='ODONTOLOGO',
    primer_nombre='Dr. Juan',
    primer_apellido='Pérez',
    activo=True
)

# Crear paciente
paciente = Usuario.objects.create(
    email='paciente@clinicademo1.com',
    username='paciente1',
    password=make_password('paciente123'),
    rol='PACIENTE',
    primer_nombre='María',
    primer_apellido='García',
    activo=True
)
```

O repetir para cada schema:
```bash
python manage.py tenant_command shell --schema=clinica_abc
python manage.py tenant_command shell --schema=clinica_xyz
```

#### Paso 3: Hacer commit y push de los cambios

```bash
git add core/middleware.py crear_tenants_subdominios.py CODIGO_FRONTEND_SUBDOMINIOS.md
git commit -m "feat: soporte multi-tenant con subdominios"
git push
```

#### Paso 4: Redeploy en Render

Render se actualizará automáticamente al detectar el push, o puedes forzar un redeploy manual.

---

### 🟡 FRONTEND (hacer después del backend)

#### Paso 1: Crear archivo de configuración

Crear: `src/config/tenantConfig.ts`

```typescript
export function getTenantFromHostname(): string {
  if (typeof window === 'undefined') return 'clinicademo1';
  
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'clinicademo1';
  }
  
  const parts = hostname.split('.');
  
  if (parts.length >= 3 && parts[0] !== 'www') {
    return parts[0];
  }
  
  return 'clinicademo1';
}

export function getApiConfig() {
  const tenant = getTenantFromHostname();
  
  return {
    tenant: tenant,
    apiUrl: import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com',
  };
}

export function getTenantName(): string {
  const tenant = getTenantFromHostname();
  
  const tenantNames: Record<string, string> = {
    'clinicademo1': 'Clínica Demo 1',
    'clinicaabc': 'Clínica ABC',
    'clinicaxyz': 'Clínica XYZ',
  };
  
  return tenantNames[tenant] || 'Clínica Dental';
}
```

Ver código completo en: `CODIGO_FRONTEND_SUBDOMINIOS.md`

#### Paso 2: Modificar configuración de axios

Agregar en tu `axios.config.ts` (o similar):

```typescript
import { getTenantFromHostname } from './config/tenantConfig';

// En el interceptor de request:
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // ⭐ AGREGAR ESTO:
    const tenantId = getTenantFromHostname();
    config.headers['X-Tenant-ID'] = tenantId;
    
    console.log('📡 Request a:', config.url);
    console.log('🏢 Tenant ID:', tenantId);
    
    return config;
  },
  (error) => Promise.reject(error)
);
```

#### Paso 3: Commit y push

```bash
git add src/config/tenantConfig.ts src/config/axios.ts
git commit -m "feat: detección automática de tenant desde subdominio"
git push
```

Vercel hará redeploy automáticamente.

---

## 🧪 CÓMO PROBAR

### 1. Esperar SSL (5-15 minutos)

Verifica que los certificados SSL estén listos en Vercel:
```
✅ clinicademo1.dentaabcxy.store - Valid Configuration
✅ clinicaabc.dentaabcxy.store - Valid Configuration
✅ clinicaxyz.dentaabcxy.store - Valid Configuration
```

### 2. Probar cada subdominio

#### Clínica Demo 1:
```
URL: https://clinicademo1.dentaabcxy.store
Credenciales: odontologo@clinicademo1.com / odontologo123
```

#### Clínica ABC:
```
URL: https://clinicaabc.dentaabcxy.store
Credenciales: odontologo@clinicaabc.com / odontologo123
```

#### Clínica XYZ:
```
URL: https://clinicaxyz.dentaabcxy.store
Credenciales: odontologo@clinicaxyz.com / odontologo123
```

### 3. Verificar aislamiento de datos

1. Crear un paciente en Clínica Demo 1
2. Ir a Clínica ABC
3. Verificar que NO aparezca el paciente de Clínica Demo 1

✅ Si no aparece → Aislamiento funcionando correctamente

---

## 🎯 CHECKLIST COMPLETO

### Backend:
- [ ] Ejecutar `python crear_tenants_subdominios.py`
- [ ] Poblar datos en `clinica_demo1` (usuarios de prueba)
- [ ] Poblar datos en `clinica_abc` (usuarios de prueba)
- [ ] Poblar datos en `clinica_xyz` (usuarios de prueba)
- [ ] Commit y push cambios
- [ ] Verificar redeploy en Render

### Frontend:
- [ ] Crear `src/config/tenantConfig.ts`
- [ ] Modificar axios para enviar header `X-Tenant-ID`
- [ ] Commit y push cambios
- [ ] Verificar redeploy en Vercel

### Testing:
- [ ] Esperar generación SSL en Vercel (5-15 min)
- [ ] Acceder a `clinicademo1.dentaabcxy.store`
- [ ] Acceder a `clinicaabc.dentaabcxy.store`
- [ ] Acceder a `clinicaxyz.dentaabcxy.store`
- [ ] Verificar header `X-Tenant-ID` en DevTools Network
- [ ] Probar login en cada subdominio
- [ ] Crear datos en una clínica y verificar que no aparezcan en otra

---

## ⏱️ TIEMPO ESTIMADO

- **Backend:** 30 minutos
  - Crear tenants: 5 min
  - Poblar datos: 15 min
  - Deploy: 10 min

- **Frontend:** 20 minutos
  - Código: 10 min
  - Deploy: 10 min

- **Testing:** 15 minutos

**Total: ~1 hora**

---

## 📞 DEBUGGING

Si algo no funciona:

1. **Ver logs del backend en Render:**
   ```
   Render Dashboard → ClinicaDental-backend → Logs
   ```

2. **Ver headers en frontend:**
   ```javascript
   // DevTools → Console
   console.log('Tenant:', getTenantFromHostname());
   
   // DevTools → Network → Seleccionar request → Headers
   // Buscar: X-Tenant-ID
   ```

3. **Verificar tenant en backend:**
   ```python
   # En Render Shell
   python manage.py shell
   
   from tenants.models import Clinica
   print(Clinica.objects.all())
   ```

---

## 🚀 SIGUIENTE PASO INMEDIATO

**Ejecuta esto ahora:**

```bash
python crear_tenants_subdominios.py
```

Esto creará los 3 tenants en tu base de datos y ejecutará las migraciones necesarias. 🎯
