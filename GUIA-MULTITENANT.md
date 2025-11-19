# 🏢 Guía del Sistema Multi-Tenant

## 📋 Índice
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Tipos de Usuarios](#tipos-de-usuarios)
3. [Crear y Gestionar Tenants](#crear-y-gestionar-tenants)
4. [Acceso y Autenticación](#acceso-y-autenticación)
5. [Gestión de Usuarios por Tenant](#gestión-de-usuarios-por-tenant)
6. [Comandos Útiles](#comandos-útiles)

---

## 🏗️ Arquitectura del Sistema

### ¿Qué es Multi-Tenant?

Un sistema **multi-tenant** permite que múltiples clientes (tenants/clínicas) compartan la misma aplicación pero con **datos completamente aislados**.

```
Base de Datos Compartida
├── Tenant: BIENESTAR
│   ├── Usuarios de BIENESTAR
│   ├── Pacientes de BIENESTAR
│   └── Profesionales de BIENESTAR
│
├── Tenant: ARMONIA
│   ├── Usuarios de ARMONIA
│   ├── Pacientes de ARMONIA
│   └── Profesionales de ARMONIA
│
└── Superadmin Global (ve TODOS los tenants)
```

### Componentes Clave

1. **Tenant Model** (`core/models.py`): Representa cada clínica
2. **TenantMiddleware** (`core/middleware.py`): Detecta el tenant actual por subdominio
3. **TenantModel** (clase base): Todos los modelos heredan de esta para auto-filtrado
4. **Thread-Local Storage**: Guarda el tenant actual en memoria por petición

---

## 👥 Tipos de Usuarios

### 1. Superadmin Global del Sistema

**Características:**
- `is_superuser = True`
- `is_staff = True`
- **NO** pertenece a ningún tenant
- Accede sin subdominio

**Acceso:**
- URL: `http://localhost:8080/admin/`
- Ve: Lista de TODOS los tenants/clínicas
- NO ve: Usuarios, Pacientes, Profesionales individuales
- Función: Crear y gestionar clínicas

**Crear:**
```bash
python manage.py create_system_admin \
  --email superadmin@sistema.com \
  --password super123 \
  --first-name Sistema \
  --last-name Administrador
```

---

### 2. Admin de Tenant (Admin de Clínica)

**Características:**
- `is_superuser = False`
- `is_staff = True`
- **Pertenece** a un tenant específico
- Rol: `ADMIN` en `TenantMembership`

**Acceso:**
- URL: `http://<subdominio>.localhost:8080/admin/`
- Ejemplo: `http://bienestar.localhost:8080/admin/`
- Ve: Solo usuarios, pacientes y profesionales de SU clínica
- NO ve: Otros tenants ni superadmin

**Permisos:**
- Gestionar usuarios de su clínica
- Crear/editar pacientes
- Crear/editar profesionales
- Ver estadísticas de su clínica

---

### 3. Profesional

**Características:**
- `is_staff = False`
- Tiene perfil `Profesional` con especialidad y licencia
- Rol: `PROFESIONAL` en `TenantMembership`

**Acceso:**
- URL API: `http://<subdominio>.localhost:8080/api/`
- NO accede al admin Django
- Usa aplicación frontend/móvil

**Función:**
- Ver sus citas
- Gestionar su agenda
- Atender pacientes

---

### 4. Paciente

**Características:**
- `is_staff = False`
- Tiene perfil `Paciente` con datos clínicos
- Rol: `PACIENTE` en `TenantMembership`

**Acceso:**
- URL API: `http://<subdominio>.localhost:8080/api/`
- NO accede al admin Django
- Usa aplicación frontend/móvil

**Función:**
- Agendar citas
- Ver historial
- Comunicarse con profesionales

---

## 🏥 Crear y Gestionar Tenants

### Paso 1: Crear un Tenant (Clínica)

```bash
python manage.py setup_tenant \
  --name "Centro BIENESTAR" \
  --subdomain bienestar \
  --email admin@bienestar.com \
  --password admin123 \
  --first-name Admin \
  --last-name Bienestar
```

**Resultado:**
- ✅ Crea el tenant "Centro BIENESTAR"
- ✅ Crea usuario admin (`admin@bienestar.com`)
- ✅ Asigna rol `ADMIN` al usuario
- ✅ Da permisos completos sobre usuarios/pacientes/profesionales
- ✅ URL de acceso: `http://bienestar.localhost:8080/admin/`

### Paso 2: Ver Tenants Creados (Solo Superadmin)

1. Acceder a: `http://localhost:8080/admin/`
2. Login con: `superadmin@sistema.com` / `super123`
3. Ver sección: **Core → Centros Psicológicos**

### Paso 3: Activar/Desactivar Tenants

Desde el admin del superadmin:
- Seleccionar tenants
- Acciones → "Activar tenants seleccionados" o "Desactivar"
- Tenants desactivados NO pueden acceder al sistema

---

## 🔐 Acceso y Autenticación

### Estructura de URLs

| Usuario | URL | Email | Password |
|---------|-----|-------|----------|
| Superadmin Global | `localhost:8080/admin/` | `superadmin@sistema.com` | `super123` |
| Admin BIENESTAR | `bienestar.localhost:8080/admin/` | `admin@bienestar.com` | `admin123` |
| Admin ARMONIA | `armonia.localhost:8080/admin/` | `admin@armonia.com` | `admin123` |

### Detección de Tenant

El sistema detecta el tenant por **subdominio**:

```
http://bienestar.localhost:8080/admin/
        ^^^^^^^^
        Este es el subdominio que identifica al tenant
```

**Middleware (`core/middleware.py`):**
1. Lee el `Host` del request: `bienestar.localhost:8080`
2. Extrae el subdominio: `bienestar`
3. Busca en BD: `Tenant.objects.get(subdomain='bienestar')`
4. Establece tenant en thread-local: `set_current_tenant(tenant)`
5. Todos los queries se filtran automáticamente por este tenant

### Rutas Excluidas del Middleware

Estas rutas NO requieren tenant:
- `/admin/` - Admin Django (acceso global y por tenant)
- `/api/` - API REST (tokens JWT)
- `/static/` - Archivos CSS/JS
- `/media/` - Archivos subidos
- `/favicon.ico`

---

## 👤 Gestión de Usuarios por Tenant

### Agregar Usuario a un Tenant

```bash
python manage.py add_user_to_tenant \
  --email profesional@bienestar.com \
  --password prof123 \
  --tenant bienestar \
  --role PROFESIONAL \
  --first-name Juan \
  --last-name Pérez \
  --especialidad "Psicología Clínica" \
  --licencia PSI-12345
```

**Parámetros:**
- `--email`: Email único del usuario
- `--password`: Contraseña
- `--tenant`: Subdominio del tenant (ej: `bienestar`)
- `--role`: `ADMIN`, `PROFESIONAL` o `PACIENTE`
- `--first-name`, `--last-name`: Nombre completo
- `--especialidad`: Solo para `PROFESIONAL`
- `--licencia`: Solo para `PROFESIONAL`

### Crear Paciente

```bash
python manage.py add_user_to_tenant \
  --email paciente@bienestar.com \
  --password pac123 \
  --tenant bienestar \
  --role PACIENTE \
  --first-name María \
  --last-name González
```

**Nota**: El perfil de paciente se crea automáticamente. Los datos clínicos se completan desde el admin.

### Ver Usuarios de un Tenant (Admin)

1. Acceder a: `http://bienestar.localhost:8080/admin/`
2. Login con admin del tenant
3. Ir a: **Users → Usuarios**
4. Solo verás usuarios de tu clínica

---

## 🛠️ Comandos Útiles

### Gestión de Tenants

```bash
# Crear superadmin global del sistema
python manage.py create_system_admin \
  --email superadmin@sistema.com \
  --password super123 \
  --first-name Sistema \
  --last-name Admin

# Crear nuevo tenant con admin
python manage.py setup_tenant \
  --name "Mi Clínica" \
  --subdomain miclinica \
  --email admin@miclinica.com \
  --password admin123

# Listar todos los tenants (Django shell)
python manage.py shell -c "from core.models import Tenant; [print(f'{t.subdomain}: {t.nombre}') for t in Tenant.objects.all()]"
```

### Gestión de Usuarios

```bash
# Agregar profesional a tenant
python manage.py add_user_to_tenant \
  --email prof@tenant.com \
  --password pass123 \
  --tenant mitenent \
  --role PROFESIONAL \
  --first-name Nombre \
  --last-name Apellido \
  --especialidad "Especialidad" \
  --licencia "LIC-123"

# Agregar paciente a tenant
python manage.py add_user_to_tenant \
  --email pac@tenant.com \
  --password pass123 \
  --tenant mitenent \
  --role PACIENTE \
  --first-name Nombre \
  --last-name Apellido

# Listar usuarios de un tenant (Django shell)
python manage.py shell -c "from users.models import TenantMembership; from core.models import Tenant; t = Tenant.objects.get(subdomain='bienestar'); [print(f'{m.user.email} - {m.role}') for m in TenantMembership.objects.filter(tenant=t)]"

# Arreglar permisos de admins de tenant
python manage.py fix_admin_permissions
```

### Desarrollo y Testing

```bash
# Iniciar servidor
python manage.py runserver 8080

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Acceder a shell de Django
python manage.py shell

# Ver todos los usuarios
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); [print(f'{u.email} - Staff: {u.is_staff} - Super: {u.is_superuser}') for u in User.objects.all()]"
```

---

## 📊 Diagrama de Flujo de Acceso

```
┌─────────────────────────────────────────────┐
│  Usuario accede a una URL                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │ TenantMiddleware      │
      │ Analiza el subdominio │
      └───────┬───────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌─────────┐        ┌──────────────┐
│ SIN     │        │ CON          │
│ Subdom  │        │ Subdominio   │
└────┬────┘        └──────┬───────┘
     │                    │
     │                    ▼
     │         ┌──────────────────┐
     │         │ Buscar Tenant en │
     │         │ base de datos    │
     │         └──────┬───────────┘
     │                │
     │                ▼
     │         ┌──────────────────┐
     │         │ set_current_     │
     │         │ tenant(tenant)   │
     │         └──────┬───────────┘
     │                │
     ▼                ▼
┌─────────────────────────────┐
│  Verificar permisos:        │
│  - Superadmin → Ve tenants  │
│  - Admin tenant → Ve su     │
│    clínica únicamente       │
└─────────────────────────────┘
```

---

## 🔒 Aislamiento de Datos

### Automático por TenantModel

Todos los modelos que heredan de `TenantModel` se filtran automáticamente:

```python
# En core/models.py
class TenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    objects = TenantAwareManager()  # Manager personalizado
    
    class Meta:
        abstract = True
```

**Ejemplo:**
```python
# Usuario en BIENESTAR hace:
Paciente.objects.all()
# Retorna: Solo pacientes de BIENESTAR

# Usuario en ARMONIA hace:
Paciente.objects.all()
# Retorna: Solo pacientes de ARMONIA

# Superadmin global (sin tenant) hace:
Paciente.all_objects.all()  # Usa all_objects en vez de objects
# Retorna: TODOS los pacientes de TODOS los tenants
```

### Ventajas del Aislamiento

✅ **Seguridad**: Imposible acceder a datos de otro tenant  
✅ **Simplicidad**: No necesitas filtrar manualmente en cada query  
✅ **Escalabilidad**: Agregar nuevos tenants es instantáneo  
✅ **Mantenimiento**: Una sola base de datos para todo el sistema  

---

## 🚀 Siguientes Pasos

1. **Crear tu primer tenant**: Usa `setup_tenant`
2. **Acceder al admin del tenant**: `http://<subdominio>.localhost:8080/admin/`
3. **Agregar profesionales y pacientes**: Usa `add_user_to_tenant`
4. **Desarrollar API REST**: Implementar endpoints para frontend
5. **Implementar Fase 2**: Sistema de agendamiento de citas

---

## 📞 Resumen de Credenciales Actuales

| Rol | Email | Password | URL |
|-----|-------|----------|-----|
| Superadmin Global | `superadmin@sistema.com` | `super123` | `localhost:8080/admin/` |
| Admin BIENESTAR | `admin@bienestar.com` | `admin123` | `bienestar.localhost:8080/admin/` |
| Admin ARMONIA | `admin@armonia.com` | `admin123` | `armonia.localhost:8080/admin/` |

---

## ⚠️ Consideraciones Importantes

1. **Subdominios en localhost**: Funciona con `bienestar.localhost:8080`, no necesitas configurar `/etc/hosts`
2. **Producción**: Cambia `ALLOWED_HOSTS` y configura DNS real
3. **Seguridad**: Cambia `SECRET_KEY` y passwords en producción
4. **CORS**: Configurar orígenes permitidos en producción
5. **JWT Tokens**: Duración de 1 hora (access) y 7 días (refresh)

---

**Última actualización**: Noviembre 15, 2025
