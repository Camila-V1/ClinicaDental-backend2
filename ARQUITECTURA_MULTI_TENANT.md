# 🏗️ ARQUITECTURA MULTI-TENANT - CLÍNICA DENTAL

**Sistema Django Multi-Tenant con PostgreSQL Schemas**  
**Versión:** 1.0  
**Última actualización:** Noviembre 2025

---

## 📋 TABLA DE CONTENIDOS

1. [¿Qué es Multi-Tenant?](#qué-es-multi-tenant)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Schema PUBLIC vs TENANT](#schema-public-vs-tenant)
4. [Flujo de Requests](#flujo-de-requests)
5. [Modelos y Apps](#modelos-y-apps)
6. [Configuración de URLs](#configuración-de-urls)
7. [Middleware Inteligente](#middleware-inteligente)
8. [Gestión de Tenants](#gestión-de-tenants)
9. [Ejemplos Prácticos](#ejemplos-prácticos)
10. [Troubleshooting](#troubleshooting)

---

## 🤔 ¿Qué es Multi-Tenant?

**Multi-Tenant** es una arquitectura donde **múltiples clientes (tenants)** comparten la **misma infraestructura de aplicación**, pero **sus datos están completamente aislados**.

### En nuestro caso:
- **Cada clínica es un TENANT independiente**
- **Cada clínica tiene su propia base de datos lógica** (schema de PostgreSQL)
- **Datos 100% aislados**: La Clínica A no puede ver datos de la Clínica B
- **Código compartido**: Todas las clínicas usan el mismo código Django

### Ventajas:
✅ **Escalabilidad**: Agregar nueva clínica = crear nuevo schema (segundos)  
✅ **Aislamiento**: Datos separados por schema (seguridad)  
✅ **Mantenimiento**: Un solo código para todas las clínicas  
✅ **Costos**: Un solo servidor para múltiples clientes  
✅ **Backups**: Backups independientes por clínica  

---

## 🏛️ ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  SCHEMA: public                           │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  Tablas:                                                  │ │
│  │  • tenants_clinica         (Registro de clínicas)        │ │
│  │  • tenants_domain          (Dominios de clínicas)        │ │
│  │  • tenants_plansuscripcion (Planes disponibles)          │ │
│  │  • tenants_solicitudregistro (Solicitudes de registro)   │ │
│  │  • django_migrations       (Control de migraciones)      │ │
│  │                                                           │ │
│  │  NO CONTIENE:                                             │ │
│  │  ❌ usuarios_usuario                                      │ │
│  │  ❌ agenda_cita                                           │ │
│  │  ❌ historial_clinico                                     │ │
│  │  ❌ Ningún dato de clínicas                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             SCHEMA: clinica_demo                          │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  Tablas:                                                  │ │
│  │  • usuarios_usuario                                       │ │
│  │  • usuarios_perfilodontologo                              │ │
│  │  • usuarios_perfilpaciente                                │ │
│  │  • agenda_cita                                            │ │
│  │  • historial_clinico_historialclinico                     │ │
│  │  • historial_clinico_episodioatencion                     │ │
│  │  • tratamientos_servicio                                  │ │
│  │  • inventario_insumo                                      │ │
│  │  • facturacion_pago                                       │ │
│  │  • ... (todas las tablas de negocio)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             SCHEMA: clinica_abc                           │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  Tablas:                                                  │ │
│  │  • usuarios_usuario                                       │ │
│  │  • agenda_cita                                            │ │
│  │  • historial_clinico_historialclinico                     │ │
│  │  • ... (mismas tablas que clinica_demo)                   │ │
│  │                                                           │ │
│  │  ⚠️ DATOS COMPLETAMENTE INDEPENDIENTES                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             SCHEMA: clinica_xyz                           │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  Tablas:                                                  │ │
│  │  • usuarios_usuario                                       │ │
│  │  • agenda_cita                                            │ │
│  │  • ... (mismas tablas)                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                         ... más clínicas ...                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔀 SCHEMA PUBLIC vs TENANT

### 📂 SCHEMA PUBLIC (Administración del Sistema)

**Propósito:** Gestionar las clínicas (tenants) del sistema.

**Contiene:**
- ✅ Registro de clínicas (`tenants_clinica`)
- ✅ Dominios de clínicas (`tenants_domain`)
- ✅ Planes de suscripción (`tenants_plansuscripcion`)
- ✅ Solicitudes de registro (`tenants_solicitudregistro`)
- ✅ Control de migraciones (`django_migrations`)

**NO contiene:**
- ❌ Usuarios de clínicas
- ❌ Pacientes, citas, historiales
- ❌ Ningún dato de negocio

**Acceso:**
- **URL:** `http://localhost:8000/admin/` (desarrollo)
- **URL:** `https://clinica-dental-backend.onrender.com/admin/` (producción)
- **Admin:** `PublicAdminSite` (sin autenticación en desarrollo)
- **Función:** Crear/editar/eliminar clínicas

**Apps en PUBLIC:**
```python
SHARED_APPS = [
    'django_tenants',
    'tenants',                 # ← Gestión de clínicas
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]
```

---

### 🏥 SCHEMAS TENANT (Clínicas Individuales)

**Propósito:** Almacenar los datos de cada clínica de forma aislada.

**Contiene:**
- ✅ Usuarios de la clínica (`usuarios_usuario`)
- ✅ Perfiles (odontólogos, pacientes)
- ✅ Citas (`agenda_cita`)
- ✅ Historiales clínicos
- ✅ Episodios de atención
- ✅ Servicios/Tratamientos
- ✅ Inventario (insumos)
- ✅ Facturación y pagos
- ✅ Reportes
- ✅ Backups

**Acceso:**
- **URL Subdominio:** `http://clinicademo1.localhost:8000/admin/`
- **URL Producción:** `https://clinicademo1.dentaabcxy.store/admin/`
- **Admin:** `admin.site.urls` (Django admin estándar)
- **Autenticación:** Requiere login con usuario de la clínica
- **Función:** Gestionar datos de la clínica específica

**Apps en TENANT:**
```python
TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'usuarios',              # ← DEBE estar en TENANT_APPS
    'agenda',
    'historial_clinico',
    'tratamientos',
    'facturacion',
    'inventario',
    'reportes',
    'backups',
    'rest_framework',
]
```

---

## 📊 COMPARACIÓN PUBLIC vs TENANT

| Característica | SCHEMA PUBLIC | SCHEMA TENANT |
|----------------|---------------|---------------|
| **Propósito** | Gestionar clínicas | Datos de clínica específica |
| **URL Admin** | `/admin/` en dominio público | `/admin/` en subdominio |
| **Modelos** | Clinica, Domain, PlanSuscripcion | Usuario, Cita, HistorialClinico |
| **Autenticación** | Sin autenticación (desarrollo) | Requiere login con Usuario |
| **Usuario Admin** | No existe tabla usuarios_usuario | Existe tabla usuarios_usuario |
| **Ejemplo URL** | `localhost:8000/admin/` | `clinicademo1.localhost:8000/admin/` |
| **Producción** | `clinica-dental-backend.onrender.com/admin/` | `clinicademo1.dentaabcxy.store/admin/` |
| **Apps** | SHARED_APPS | TENANT_APPS |
| **Migraciones** | `migrate_schemas --shared` | `migrate_schemas` |

---

## 🚀 FLUJO DE REQUESTS

### 1️⃣ Request al Schema PUBLIC

```
┌─────────────┐
│   Cliente   │
│  (Browser)  │
└──────┬──────┘
       │
       │ GET http://localhost:8000/admin/
       │
       ▼
┌──────────────────────────────────────────────┐
│  TenantMainMiddleware (django-tenants)       │
├──────────────────────────────────────────────┤
│  1. Detecta hostname: localhost              │
│  2. Busca en tenants_domain: localhost       │
│  3. Encuentra: Clinica (schema: public)      │
│  4. connection.set_tenant(public)            │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         core.urls_public.py                  │
├──────────────────────────────────────────────┤
│  path('admin/', public_admin.urls)           │
│                                              │
│  PublicAdminSite:                            │
│  • Muestra: Clinica, Domain, Plan            │
│  • No requiere autenticación (dev)           │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         SCHEMA: public                       │
├──────────────────────────────────────────────┤
│  SELECT * FROM tenants_clinica;              │
│  SELECT * FROM tenants_domain;               │
└──────────────────────────────────────────────┘
```

---

### 2️⃣ Request al Schema TENANT (Subdominio)

```
┌─────────────┐
│   Cliente   │
│  (Browser)  │
└──────┬──────┘
       │
       │ GET http://clinicademo1.localhost:8000/admin/
       │
       ▼
┌──────────────────────────────────────────────┐
│  TenantMainMiddleware (django-tenants)       │
├──────────────────────────────────────────────┤
│  1. Detecta hostname: clinicademo1.localhost │
│  2. Busca en tenants_domain: clinicademo1    │
│  3. Encuentra: Clinica (schema: clinica_demo)│
│  4. connection.set_tenant(clinica_demo)      │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         core.urls_tenant.py                  │
├──────────────────────────────────────────────┤
│  path('admin/', admin.site.urls)             │
│                                              │
│  admin.site (Django admin estándar):         │
│  • Muestra: Usuario, Cita, Historial        │
│  • Requiere autenticación                    │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         SCHEMA: clinica_demo                 │
├──────────────────────────────────────────────┤
│  SELECT * FROM usuarios_usuario;             │
│  SELECT * FROM agenda_cita;                  │
│  SELECT * FROM historial_clinico;            │
└──────────────────────────────────────────────┘
```

---

### 3️⃣ Request API desde Frontend (Producción)

```
┌─────────────────────────┐
│   Frontend Vercel       │
│  dentaabcxy.store       │
└──────────┬──────────────┘
           │
           │ POST https://clinica-dental-backend.onrender.com/api/token/
           │ Headers: {
           │   "X-Tenant-ID": "clinicademo1"
           │ }
           │ Body: { email, password }
           │
           ▼
┌──────────────────────────────────────────────┐
│  TenantMainMiddleware                        │
├──────────────────────────────────────────────┤
│  1. Hostname: clinica-dental-backend.onrender│
│  2. Es dominio público → schema: public      │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  DefaultTenantMiddleware (CUSTOM)            │
├──────────────────────────────────────────────┤
│  1. Request path: /api/token/                │
│  2. Schema actual: public                    │
│  3. Lee header: X-Tenant-ID = "clinicademo1" │
│  4. Busca Clinica con dominio "clinicademo1" │
│  5. connection.set_tenant(clinica_demo)      │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│         core.urls_public.py                  │
├──────────────────────────────────────────────┤
│  path('api/token/', CustomTokenObtainPairView│
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│         SCHEMA: clinica_demo                 │
├──────────────────────────────────────────────┤
│  SELECT * FROM usuarios_usuario              │
│  WHERE email = 'admin@clinicademo1.com';     │
│                                              │
│  ✅ Retorna JWT token                        │
└──────────────────────────────────────────────┘
```

---

## 🗂️ MODELOS Y APPS

### Apps en SHARED_APPS (Schema PUBLIC)

#### 1. **tenants** (Gestión de Clínicas)

**Modelos:**

```python
# tenants/models.py

class PlanSuscripcion(models.Model):
    """Planes disponibles (PRUEBA, MENSUAL, ANUAL)"""
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20)  # PRUEBA, MENSUAL, etc.
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.IntegerField()
    max_usuarios = models.IntegerField(default=10)
    max_pacientes = models.IntegerField(default=500)
    activo = models.BooleanField(default=True)

class Clinica(TenantMixin):
    """Representa una clínica (tenant)"""
    # Campos obligatorios de TenantMixin:
    schema_name = models.CharField(max_length=63)  # ej: 'clinica_demo'
    
    # Campos personalizados:
    nombre = models.CharField(max_length=200)      # ej: 'Clínica Demo'
    dominio = models.CharField(max_length=200)     # ej: 'clinicademo1'
    email_admin = models.EmailField()
    telefono = models.CharField(max_length=20)
    plan = models.ForeignKey(PlanSuscripcion)
    estado = models.CharField()  # ACTIVA, SUSPENDIDA, CANCELADA
    fecha_expiracion = models.DateTimeField()
    backup_schedule = models.CharField()  # Frecuencia de backups

class Domain(DomainMixin):
    """Mapea dominios/subdominios a clínicas"""
    # Campos obligatorios de DomainMixin:
    domain = models.CharField(max_length=253)      # ej: 'clinicademo1.localhost'
    tenant = models.ForeignKey(Clinica)
    is_primary = models.BooleanField(default=True)

class SolicitudRegistro(models.Model):
    """Solicitudes de nuevas clínicas"""
    nombre_clinica = models.CharField(max_length=200)
    dominio_deseado = models.CharField(max_length=200)
    nombre_contacto = models.CharField(max_length=200)
    email = models.EmailField()
    plan_solicitado = models.ForeignKey(PlanSuscripcion)
    estado = models.CharField()  # PENDIENTE_PAGO, COMPLETADA, etc.
```

**Ubicación:** Schema `public` únicamente  
**Acceso Admin:** `http://localhost:8000/admin/` (PublicAdminSite)

---

### Apps en TENANT_APPS (Schemas de Clínicas)

#### 1. **usuarios** (Usuarios de la Clínica)

```python
# usuarios/models.py

class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario de una clínica específica"""
    # Tipos de usuario
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        ODONTOLOGO = 'ODONTOLOGO', 'Odontólogo'
        PACIENTE = 'PACIENTE', 'Paciente'
    
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True, null=True, blank=True)
    sexo = models.CharField(max_length=1, null=True, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    activo = models.BooleanField(default=True)
    # ⚠️ Perfil se crea según tipo_usuario

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

class PerfilOdontologo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT)
    cedulaProfesional = models.CharField(max_length=50)
    experienciaProfesional = models.TextField(blank=True)

class PerfilPaciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    fecha_de_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.TextField(blank=True)
    telefono_de_contacto = models.CharField(max_length=20, blank=True)
```

#### 2. **tratamientos** (Servicios Dentales)

```python
class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100)

class Servicio(models.Model):
    """Servicios dentales (antes Tratamiento)"""
    categoria = models.ForeignKey(CategoriaServicio)
    codigo_servicio = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    precio_base = models.DecimalField()
    tiempo_estimado = models.IntegerField()  # minutos
```

#### 3. **agenda** (Citas)

```python
class Cita(models.Model):
    odontologo = models.ForeignKey(PerfilOdontologo)
    paciente = models.ForeignKey(PerfilPaciente)
    fecha_hora = models.DateTimeField()
    motivo_tipo = models.CharField()  # CONSULTA, URGENCIA, etc.
    motivo = models.TextField()
    estado = models.CharField()  # PENDIENTE, CONFIRMADA, ATENDIDA, CANCELADA
    pagada = models.BooleanField(default=False)
```

#### 4. **historial_clinico** (Historiales Médicos)

```python
class HistorialClinico(models.Model):
    paciente = models.OneToOneField(PerfilPaciente)
    grupo_sanguineo = models.CharField(max_length=5)
    alergias = models.TextField()

class EpisodioAtencion(models.Model):
    historial = models.ForeignKey(HistorialClinico)
    odontologo = models.ForeignKey(PerfilOdontologo)
    fecha = models.DateTimeField()
    diagnostico = models.TextField()
    tratamiento_realizado = models.TextField()

class Odontograma(models.Model):
    historial = models.ForeignKey(HistorialClinico)
    fecha = models.DateTimeField()
    estado_piezas = models.JSONField()  # {"11": {"estado": "sano"}, ...}
```

#### 5. **inventario** (Insumos)

```python
class CategoriaInsumo(models.Model):
    nombre = models.CharField(max_length=100)

class Insumo(models.Model):
    categoria = models.ForeignKey(CategoriaInsumo)
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    precio_costo = models.DecimalField()
    precio_venta = models.DecimalField()
    stock_actual = models.IntegerField()
```

#### 6. **facturacion** (Pagos y Facturas)

```python
class Pago(models.Model):
    tipo_pago = models.CharField()  # CITA, FACTURA, PLAN
    cita = models.ForeignKey(Cita, null=True)
    paciente = models.ForeignKey(PerfilPaciente)
    monto_pagado = models.DecimalField()
    metodo_pago = models.CharField()  # EFECTIVO, TARJETA, etc.
    estado_pago = models.CharField()  # COMPLETADO, PENDIENTE
```

**Ubicación:** Cada schema de clínica (`clinica_demo`, `clinica_abc`, etc.)  
**Acceso Admin:** `http://clinicademo1.localhost:8000/admin/`

---

## 🔗 CONFIGURACIÓN DE URLs

### 1. `core/settings.py` (Configuración)

```python
# django-tenants configuration
TENANT_MODEL = "tenants.Clinica"
TENANT_DOMAIN_MODEL = "tenants.Domain"

# URLconfs
ROOT_URLCONF = 'core.urls_tenant'           # ← Para schemas TENANT
PUBLIC_SCHEMA_URLCONF = 'core.urls_public'  # ← Para schema PUBLIC

# Nota: ROOT_URLCONF se usa para los schemas de clínicas (tenant)
# PUBLIC_SCHEMA_URLCONF se usa para el schema público (localhost)
```

### 2. `core/urls_public.py` (Schema PUBLIC)

```python
from django.urls import path, include
from core.urls_public import public_admin  # Instancia del PublicAdminSite

urlpatterns = [
    path('', health_check),              # Health check
    path('admin/', public_admin.urls),   # Admin de clínicas
    path('api/tenants/', include('tenants.urls')),  # API tenants
    
    # APIs redirigidas por DefaultTenantMiddleware:
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),
    # ... resto de APIs
]
```

### 3. `core/urls_tenant.py` (Schemas TENANT)

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),     # Admin de clínica
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),
    path('api/historial/', include('historial_clinico.urls')),
    # ... todas las APIs de clínica
]
```

---

## ⚙️ MIDDLEWARE INTELIGENTE

### `core/middleware.py` - DefaultTenantMiddleware

**Problema:**  
Cuando el frontend (Vercel) llama a `https://clinica-dental-backend.onrender.com/api/token/`, django-tenants detecta el dominio público y carga el schema `public`, pero `usuarios_usuario` **no existe en public**.

**Solución:**  
Middleware personalizado que detecta el header `X-Tenant-ID` y cambia al schema correcto.

```python
class DefaultTenantMiddleware:
    def __call__(self, request):
        # Solo para requests a /api/
        if request.path.startswith('/api/'):
            hostname = request.get_host().split(':')[0]
            
            # Si es dominio público
            public_domains = ['localhost', 'clinica-dental-backend.onrender.com']
            
            if hostname in public_domains:
                if connection.schema_name == 'public':
                    # Leer header X-Tenant-ID
                    tenant_id = request.headers.get('X-Tenant-ID', '').lower()
                    
                    if not tenant_id:
                        tenant_id = 'clinica_demo'  # Default
                    
                    # Buscar tenant
                    tenant = Clinica.objects.filter(
                        Q(dominio=tenant_id) | Q(schema_name=tenant_id)
                    ).first()
                    
                    if tenant:
                        connection.set_tenant(tenant)  # ← Cambiar schema
        
        return self.get_response(request)
```

**Flujo:**

1. Frontend detecta subdominio: `clinicademo1.dentaabcxy.store`
2. Frontend extrae tenant ID: `clinicademo1`
3. Frontend envía header: `X-Tenant-ID: clinicademo1`
4. Backend busca clínica con dominio `clinicademo1`
5. Backend cambia al schema `clinica_demo`
6. Request procede en el schema correcto

---

## 🔧 GESTIÓN DE TENANTS

### Crear Nueva Clínica (Manual)

#### Opción 1: Desde Django Admin

```
1. Acceder a: http://localhost:8000/admin/
2. Clic en "Clínicas" → "Agregar Clínica"
3. Llenar datos:
   - Schema name: clinica_nueva
   - Nombre: Clínica Nueva
   - Dominio: clinicanuevas
4. Guardar (auto_create_schema=True crea el schema)
5. Crear Domain:
   - Domain: clinicanuevas.localhost
   - Tenant: Clínica Nueva
   - Is primary: ✓
```

#### Opción 2: Desde Python Shell

```python
from tenants.models import Clinica, Domain, PlanSuscripcion

# Crear plan (si no existe)
plan = PlanSuscripcion.objects.create(
    nombre="Plan Básico",
    tipo="MENSUAL",
    precio=29.99,
    duracion_dias=30,
    max_usuarios=10,
    max_pacientes=500
)

# Crear clínica
clinica = Clinica.objects.create(
    schema_name='clinica_nueva',
    nombre='Clínica Nueva',
    dominio='clinicanuevas',
    email_admin='admin@clinicanuevas.com',
    plan=plan,
    estado='ACTIVA',
    activo=True
)

# Crear dominio
Domain.objects.create(
    domain='clinicanuevas.localhost',
    tenant=clinica,
    is_primary=True
)

print(f"✅ Clínica creada: {clinica.nombre}")
print(f"   Schema: {clinica.schema_name}")
print(f"   URL: http://clinicanuevas.localhost:8000/")
```

#### Opción 3: Script Automatizado

```python
# scripts_poblacion/crear_tenant.py
def crear_o_verificar_tenant(schema_name, nombre, dominio_principal):
    clinica, created = Clinica.objects.get_or_create(
        schema_name=schema_name,
        defaults={
            'nombre': nombre,
            'dominio': dominio_principal.split('.')[0],
            'estado': 'ACTIVA',
            'activo': True,
        }
    )
    
    if created:
        # Crear dominio
        Domain.objects.create(
            domain=dominio_principal,
            tenant=clinica,
            is_primary=True
        )
        
        # Activar plan
        plan = PlanSuscripcion.objects.get(tipo='PRUEBA')
        clinica.activar_plan(plan)
    
    return clinica
```

---

### Migraciones

#### Migrar Schema PUBLIC

```powershell
# Migraciones para tablas compartidas (tenants_clinica, etc.)
python manage.py migrate_schemas --shared
```

#### Migrar Todos los Schemas TENANT

```powershell
# Migraciones para todas las clínicas
python manage.py migrate_schemas
```

#### Migrar Schema TENANT Específico

```powershell
# Migrar solo clinica_demo
python manage.py migrate_schemas --schema=clinica_demo
```

---

### Poblar Datos de Demo

```powershell
# Poblar clínica demo con datos de prueba
python scripts_poblacion/poblar_todo.py
```

Este script:
1. Crea/verifica tenant `clinica_demo`
2. Puebla usuarios (admin, odontólogos, pacientes)
3. Puebla servicios, insumos, citas, historiales, pagos

---

## 💡 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Login desde Frontend

**Frontend (dentaabcxy.store):**

```javascript
// Detectar subdominio
const hostname = window.location.hostname;  // "clinicademo1.dentaabcxy.store"
const tenantId = hostname.split('.')[0];    // "clinicademo1"

// Request de login
const response = await fetch('https://clinica-dental-backend.onrender.com/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': tenantId,  // ← Header crucial
  },
  body: JSON.stringify({
    email: 'admin@clinicademo1.com',
    password: 'admin123'
  })
});

const data = await response.json();
// { access: "eyJ...", refresh: "eyJ...", usuario: {...} }
```

**Backend (Django):**

```python
# 1. TenantMainMiddleware detecta hostname público
# 2. DefaultTenantMiddleware lee X-Tenant-ID: "clinicademo1"
# 3. Busca Clinica con dominio="clinicademo1"
# 4. connection.set_tenant(clinica_demo)
# 5. CustomTokenObtainPairView ejecuta en schema clinica_demo
# 6. SELECT * FROM usuarios_usuario WHERE email = ...
# 7. ✅ Usuario encontrado, retorna JWT
```

---

### Ejemplo 2: Crear Cita desde App Móvil

**App Móvil:**

```javascript
// Usuario ya logueado, tiene token JWT y tenantId guardados
const tenantId = await AsyncStorage.getItem('tenantId');  // "clinicademo1"
const token = await AsyncStorage.getItem('accessToken');

const response = await fetch('https://clinica-dental-backend.onrender.com/api/agenda/citas/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenantId,  // ← Especifica la clínica
  },
  body: JSON.stringify({
    odontologo: 2,
    paciente: 5,
    fecha_hora: '2024-12-01T10:00:00',
    motivo_tipo: 'CONSULTA',
    motivo: 'Revisión general'
  })
});
```

**Backend:**

```python
# DefaultTenantMiddleware cambia a schema clinica_demo
# CitaViewSet ejecuta en clinica_demo
# INSERT INTO agenda_cita (odontologo_id, paciente_id, ...)
# ✅ Cita creada en schema correcto
```

---

### Ejemplo 3: Acceso Directo por Subdominio

**Desarrollo Local:**

```
http://clinicademo1.localhost:8000/admin/
```

1. TenantMainMiddleware detecta hostname: `clinicademo1.localhost`
2. Busca en `tenants_domain` donde `domain = 'clinicademo1.localhost'`
3. Encuentra `Clinica` con `schema_name = 'clinica_demo'`
4. `connection.set_tenant(clinica_demo)`
5. Carga `urls_tenant.py`
6. Muestra admin de clínica (Usuario, Cita, etc.)

**Producción:**

```
https://clinicademo1.dentaabcxy.store/admin/
```

Mismo flujo, pero con dominio de producción.

---

## 🐛 TROUBLESHOOTING

### Problema 1: "relation usuarios_usuario does not exist"

**Causa:** Request en schema `public` pero intentando acceder a tabla tenant.

**Solución:**
1. Verificar que frontend envía header `X-Tenant-ID`
2. Verificar middleware `DefaultTenantMiddleware` en `settings.MIDDLEWARE`
3. Verificar que el tenant existe:
   ```python
   from tenants.models import Clinica
   Clinica.objects.filter(dominio='clinicademo1')
   ```

---

### Problema 2: Admin no muestra modelos tenant

**Causa:** Accediendo a admin público en lugar de admin tenant.

**URLs:**
- ❌ `http://localhost:8000/admin/` → Schema public (solo Clinica, Domain)
- ✅ `http://clinicademo1.localhost:8000/admin/` → Schema clinica_demo (Usuario, Cita, etc.)

---

### Problema 3: Migraciones no se aplican

**Solución:**

```powershell
# Migrar public
python manage.py migrate_schemas --shared

# Migrar todos los tenants
python manage.py migrate_schemas

# Verificar schema específico
python manage.py dbshell
\dt  # Listar tablas
SET search_path TO clinica_demo;
\dt  # Verificar tablas del tenant
```

---

### Problema 4: Cannot create tenant without domain

**Causa:** Creaste `Clinica` pero no `Domain`.

**Solución:**

```python
from tenants.models import Clinica, Domain

clinica = Clinica.objects.get(schema_name='clinica_demo')

Domain.objects.create(
    domain='clinicademo1.localhost',  # Desarrollo
    tenant=clinica,
    is_primary=True
)

# Producción: Agregar dominio adicional
Domain.objects.create(
    domain='clinicademo1.dentaabcxy.store',
    tenant=clinica,
    is_primary=False
)
```

---

### Problema 5: CORS Error desde Frontend

**Causa:** Frontend no configurado en CORS o falta header.

**Solución:**

```python
# core/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'https://dentaabcxy.store',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.dentaabcxy\.store$",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-tenant-id',  # ← Importante
]
```

---

## 📚 RECURSOS ADICIONALES

### Documentación:
- **django-tenants:** https://django-tenants.readthedocs.io/
- **PostgreSQL Schemas:** https://www.postgresql.org/docs/current/ddl-schemas.html
- **Django Rest Framework:** https://www.django-rest-framework.org/

### Archivos Importantes:
- `core/settings.py` - Configuración SHARED_APPS y TENANT_APPS
- `core/urls_public.py` - URLs para schema public
- `core/urls_tenant.py` - URLs para schemas tenant
- `core/middleware.py` - Middleware personalizado
- `tenants/models.py` - Modelos de gestión de clínicas
- `tenants/admin.py` - Admin personalizado para clínicas

### Scripts Útiles:
- `scripts_poblacion/crear_tenant.py` - Crear clínicas programáticamente
- `scripts_poblacion/poblar_todo.py` - Poblar datos de demo
- `scripts_poblacion/poblar_usuarios.py` - Crear usuarios de prueba

---

## 🎓 CONCEPTOS CLAVE

1. **Schema = Base de Datos Lógica**
   - Cada schema tiene sus propias tablas
   - Aislamiento total de datos
   - Mismo servidor PostgreSQL

2. **Public Schema = Gestión de Clínicas**
   - Solo administración del sistema
   - Sin datos de negocio
   - Admin sin autenticación (desarrollo)

3. **Tenant Schema = Datos de Clínica**
   - Usuarios, citas, historiales
   - Autenticación requerida
   - Datos aislados por clínica

4. **django-tenants = Router Automático**
   - Detecta hostname
   - Carga schema correcto
   - Carga URLconf correcto

5. **Middleware Personalizado = Tenant por Header**
   - Para apps móviles y SPAs
   - Header `X-Tenant-ID`
   - Fallback a tenant por defecto

---

## ✅ CHECKLIST DE VERIFICACIÓN

Usa este checklist para verificar que tu sistema multi-tenant está correctamente configurado:

### Schema PUBLIC:
- [ ] Migración `migrate_schemas --shared` ejecutada
- [ ] Tabla `tenants_clinica` existe
- [ ] Tabla `tenants_domain` existe
- [ ] Admin accesible en `localhost:8000/admin/`
- [ ] Modelos Clinica, Domain, Plan visibles en admin

### Schema TENANT:
- [ ] Clínica creada en admin o por script
- [ ] Domain creado y vinculado a clínica
- [ ] Migración `migrate_schemas` ejecutada
- [ ] Admin accesible en `clinicademo1.localhost:8000/admin/`
- [ ] Modelos Usuario, Cita, Historial visibles

### APIs:
- [ ] Token endpoint funciona con header `X-Tenant-ID`
- [ ] CORS configurado correctamente
- [ ] Middleware `DefaultTenantMiddleware` activo
- [ ] Frontend puede hacer login
- [ ] Frontend puede crear/leer datos

### Producción:
- [ ] Variable `RENDER_EXTERNAL_HOSTNAME` configurada
- [ ] Dominios custom agregados en Domain
- [ ] SSL configurado (HTTPS)
- [ ] CORS permite dominios de producción
- [ ] Backups automáticos configurados

---

**¿Preguntas?** Consulta la documentación de django-tenants o revisa los logs para más detalles.

