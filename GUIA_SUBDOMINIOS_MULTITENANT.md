# 🌐 CONFIGURACIÓN DE SUBDOMINIOS POR CLÍNICA

## 🎯 Objetivo

Permitir que cada clínica tenga su propio subdominio en el frontend:
- `https://clinicademo1.dentaabcxy.store` → Clínica Demo 1
- `https://clinicaabc.dentaabcxy.store` → Clínica ABC
- `https://clinicaxyz.dentaabcxy.store` → Clínica XYZ

---

## 📋 CAMBIOS NECESARIOS

### 1. DNS - Configuración en Namecheap

Necesitas agregar un registro **wildcard** (comodín) para permitir subdominios dinámicos:

**En Namecheap → Advanced DNS:**

```
Type        Host    Value                   TTL
CNAME       *       cname.vercel-dns.com    Automatic
```

Esto permite que **cualquier subdominio** (`*.dentaabcxy.store`) apunte a Vercel.

---

### 2. Frontend - Vercel Configuration

#### 2.1 Agregar Dominios en Vercel

En el dashboard de Vercel → Settings → Domains:

1. Agregar dominio principal (ya existe):
   - `dentaabcxy.store` ✅
   - `www.dentaabcxy.store` ✅

2. Agregar subdominios para cada clínica:
   - `clinicademo1.dentaabcxy.store`
   - `clinicaabc.dentaabcxy.store`
   - `clinicaxyz.dentaabcxy.store`
   - ...o usar wildcard: `*.dentaabcxy.store`

**Vercel permite usar wildcards en planes Pro.**

#### 2.2 Configuración del Frontend

**Archivo: `tenantConfig.ts` o `config.ts`**

```typescript
// Detectar el tenant desde el subdominio
export function getTenantFromHostname(): string {
  if (typeof window === 'undefined') return 'clinicademo1'; // SSR default
  
  const hostname = window.location.hostname;
  
  // Ejemplos:
  // clinicademo1.dentaabcxy.store → clinicademo1
  // clinicaabc.dentaabcxy.store → clinicaabc
  // www.dentaabcxy.store → clinicademo1 (default)
  // dentaabcxy.store → clinicademo1 (default)
  
  const parts = hostname.split('.');
  
  // Si es subdominio (tiene más de 2 partes y no es www)
  if (parts.length >= 3 && parts[0] !== 'www') {
    return parts[0]; // Retorna el subdominio
  }
  
  // Default para dominio principal o www
  return 'clinicademo1';
}

// Configuración de la API por tenant
export function getApiConfig() {
  const tenant = getTenantFromHostname();
  
  return {
    tenant: tenant,
    apiUrl: 'https://clinica-dental-backend.onrender.com',
    // No necesitas cambiar la URL del backend, el middleware lo maneja
  };
}
```

**Uso en componentes:**

```typescript
import { getTenantFromHostname, getApiConfig } from './config/tenantConfig';

function App() {
  const tenant = getTenantFromHostname();
  const config = getApiConfig();
  
  console.log('🏢 Tenant actual:', tenant);
  console.log('🌐 API URL:', config.apiUrl);
  
  // Usar el tenant en peticiones si es necesario
  // ...
}
```

---

### 3. Backend - Modificar Middleware

Necesitas actualizar el middleware para detectar el tenant desde el subdominio del **frontend** en lugar de usar siempre `clinica_demo`.

**Archivo: `core/middleware.py`**

```python
"""
Middleware personalizado para routing inteligente de tenants
"""
from django.db import connection
from django.conf import settings
import os


class DefaultTenantMiddleware:
    """
    Middleware que detecta el tenant basado en headers del request.
    
    Flujo:
    1. Frontend detecta subdominio (ej: clinicaabc.dentaabcxy.store)
    2. Frontend envía header: X-Tenant-ID: clinicaabc
    3. Backend busca el tenant con dominio 'clinicaabc'
    4. Backend cambia al schema correspondiente
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Tenant por defecto si no se especifica
        self.default_tenant_schema = os.environ.get('DEFAULT_TENANT_SCHEMA', 'clinica_demo')
    
    def __call__(self, request):
        # Solo aplicar para requests a /api/
        if request.path.startswith('/api/'):
            # Obtener el hostname actual
            hostname = request.get_host().split(':')[0]
            
            # Lista de dominios públicos (sin tenant específico)
            public_domains = [
                'localhost',
                '127.0.0.1',
                os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'clinica-dental-backend.onrender.com')
            ]
            
            # Si es un dominio público, verificar schema
            if hostname in public_domains:
                # Verificar que no estemos ya en el schema público
                if connection.schema_name == 'public':
                    # Intentar obtener tenant desde header personalizado
                    tenant_id = request.headers.get('X-Tenant-ID', '').lower()
                    
                    if not tenant_id:
                        # Si no hay header, usar el por defecto
                        tenant_id = self.default_tenant_schema
                    
                    # Buscar el tenant
                    from tenants.models import Clinica
                    try:
                        # Buscar por dominio o schema_name
                        tenant = Clinica.objects.filter(
                            models.Q(dominio=tenant_id) | 
                            models.Q(schema_name=tenant_id)
                        ).first()
                        
                        if tenant:
                            connection.set_tenant(tenant)
                            request.using_tenant = tenant_id
                        else:
                            # Si no existe, usar el por defecto
                            default_tenant = Clinica.objects.get(schema_name=self.default_tenant_schema)
                            connection.set_tenant(default_tenant)
                            request.using_default_tenant = True
                            
                    except Clinica.DoesNotExist:
                        # Si no existe el tenant por defecto, continuar con public
                        pass
        
        response = self.get_response(request)
        return response
```

---

### 4. Backend - Configurar CORS para Wildcards

**Archivo: `core/settings.py`**

Ya está configurado, pero verifica que incluya:

```python
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://[\w-]+\.dentaabcxy\.store$",  # ✅ Permite subdominios
    r"^https://dentaabcxy\.store$",           # ✅ Dominio principal
    # ... otros
]
```

---

### 5. Frontend - Configurar Axios para enviar Tenant ID

**Archivo: `axios.config.js`**

```javascript
import axios from 'axios';
import { getTenantFromHostname } from './config/tenantConfig';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// Interceptor para agregar token Y tenant ID
axiosInstance.interceptors.request.use(
  (config) => {
    // Agregar token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Agregar tenant ID desde el subdominio
    const tenantId = getTenantFromHostname();
    config.headers['X-Tenant-ID'] = tenantId;
    
    console.log('📡 Request a:', config.url);
    console.log('🏢 Tenant ID:', tenantId);
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ... resto del código
```

---

### 6. Backend - Crear Tenants Adicionales

Necesitas crear los tenants en el backend para cada subdominio.

**Script: `crear_tenant.py`**

```python
"""
Script para crear un nuevo tenant
Uso: python crear_tenant.py clinicaabc "Clínica ABC"
"""
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain
from django.core.management import call_command

def crear_tenant(dominio, nombre):
    """Crear un nuevo tenant con su schema y dominio"""
    
    schema_name = dominio.replace('-', '_')
    
    # 1. Crear el tenant
    print(f"📝 Creando tenant: {nombre}")
    tenant = Clinica.objects.create(
        schema_name=schema_name,
        nombre=nombre,
        dominio=dominio,
        activo=True
    )
    print(f"✅ Tenant creado: {tenant.schema_name}")
    
    # 2. Crear dominios
    dominios = [
        f"{dominio}.dentaabcxy.store",  # Frontend
        f"{dominio}.localhost",         # Desarrollo
    ]
    
    for domain_name in dominios:
        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=(domain_name == f"{dominio}.dentaabcxy.store")
        )
        print(f"✅ Dominio creado: {domain_name}")
    
    # 3. Ejecutar migraciones para el nuevo schema
    print(f"🔄 Ejecutando migraciones para {schema_name}...")
    call_command('migrate_schemas', schema=schema_name)
    print(f"✅ Migraciones completadas")
    
    print(f"\n🎉 Tenant '{nombre}' creado exitosamente!")
    print(f"   📍 URL: https://{dominio}.dentaabcxy.store")
    print(f"   🗄️  Schema: {schema_name}")
    
    return tenant

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python crear_tenant.py <dominio> <nombre>")
        print("Ejemplo: python crear_tenant.py clinicaabc \"Clínica ABC\"")
        sys.exit(1)
    
    dominio = sys.argv[1]
    nombre = sys.argv[2]
    
    crear_tenant(dominio, nombre)
```

**Ejecutar:**

```bash
# En Render Shell o localmente
python crear_tenant.py clinicaabc "Clínica ABC"
python crear_tenant.py clinicaxyz "Clínica XYZ"
```

---

## 🚀 FLUJO COMPLETO

### 1. Usuario accede a subdominio

```
Usuario → https://clinicaabc.dentaabcxy.store/paciente/dashboard
```

### 2. Frontend detecta tenant

```javascript
const tenant = getTenantFromHostname();
// tenant = 'clinicaabc'
```

### 3. Frontend hace petición con header

```javascript
GET /api/usuarios/me/
Headers:
  Authorization: Bearer <token>
  X-Tenant-ID: clinicaabc
```

### 4. Backend recibe y procesa

```python
# Middleware detecta header X-Tenant-ID
tenant_id = request.headers.get('X-Tenant-ID')  # 'clinicaabc'

# Busca el tenant
tenant = Clinica.objects.get(dominio='clinicaabc')

# Cambia al schema correspondiente
connection.set_tenant(tenant)  # Schema: clinica_abc

# Ejecuta la consulta en ese schema
usuario = Usuario.objects.get(...)  # Busca en clinica_abc.usuarios_usuario
```

### 5. Respuesta

```
Usuario de Clínica ABC → Solo ve datos de su clínica
Usuario de Clínica XYZ → Solo ve datos de su clínica
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### DNS (Namecheap)
- [ ] Agregar registro CNAME wildcard: `*` → `cname.vercel-dns.com`

### Frontend (Vercel)
- [ ] Agregar dominios en Vercel:
  - [ ] `clinicademo1.dentaabcxy.store`
  - [ ] `clinicaabc.dentaabcxy.store`
  - [ ] O configurar wildcard `*.dentaabcxy.store`
- [ ] Crear `tenantConfig.ts` con función `getTenantFromHostname()`
- [ ] Modificar axios config para enviar header `X-Tenant-ID`
- [ ] Probar detección de subdominio en navegador

### Backend (Render)
- [ ] Modificar `core/middleware.py` para leer header `X-Tenant-ID`
- [ ] Importar `Q` de Django models en middleware
- [ ] Verificar CORS permite `*.dentaabcxy.store`
- [ ] Crear script `crear_tenant.py`
- [ ] Crear tenants adicionales:
  - [ ] `clinicademo1` (renombrar actual)
  - [ ] `clinicaabc`
  - [ ] `clinicaxyz`
- [ ] Ejecutar migraciones para cada tenant
- [ ] Poblar datos iniciales para cada tenant

### Pruebas
- [ ] Acceder a `https://clinicademo1.dentaabcxy.store` → Debe mostrar datos de clinicademo1
- [ ] Acceder a `https://clinicaabc.dentaabcxy.store` → Debe mostrar datos de clinicaabc
- [ ] Verificar que los datos estén aislados (diferentes usuarios en cada clínica)
- [ ] Probar login en cada subdominio

---

## ⚠️ CONSIDERACIONES

### Ventajas
✅ Cada clínica tiene su URL única  
✅ Branding personalizado por clínica  
✅ Mejor organización multi-tenant  
✅ Fácil de entender para usuarios  

### Desventajas
⚠️ Requiere plan Pro de Vercel para wildcards (o agregar dominios manualmente)  
⚠️ Necesitas crear cada tenant manualmente en el backend  
⚠️ Cambio en configuración del middleware  

### Alternativa Más Simple
Si no quieres usar subdominios, puedes:
1. Mantener un solo dominio: `dentaabcxy.store`
2. Seleccionar clínica después del login
3. Guardar tenant en localStorage
4. Enviar header `X-Tenant-ID` basado en selección del usuario

---

## 🎯 RESUMEN

**¿Es complicado?** No, pero requiere:
1. Configurar DNS wildcard (5 min)
2. Agregar dominios en Vercel (5 min)
3. Modificar frontend para detectar subdominio (30 min)
4. Modificar backend middleware (20 min)
5. Crear tenants adicionales (10 min por tenant)

**Total: ~1-2 horas de trabajo** para tener multi-tenancy con subdominios funcionando completamente. 🚀
