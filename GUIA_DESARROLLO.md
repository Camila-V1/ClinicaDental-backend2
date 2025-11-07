# 📘 GUÍA DE DESARROLLO - Sistema Multi-Tenant

## 🎯 ¿Dónde agregar nuevas funcionalidades?

Esta guía te indica **exactamente dónde** colocar código nuevo para que funcione correctamente en el sistema multi-tenant.

---

## 📂 ESTRUCTURA DE ADMIN SITES

### 🔵 Admin Público (Gestión de Sistema)
**Ubicación:** `core/urls_public.py`  
**URL:** `http://localhost:8000/admin/`  
**Esquema:** `public`  
**Autenticación:** ❌ No requiere (desarrollo) / ⚠️ HTTP Basic Auth (producción)

**¿Qué va aquí?**
- ✅ Modelos de gestión de tenants: `Clinica`, `Domain`
- ✅ Configuración del sistema multi-tenant
- ❌ **NUNCA** modelos de negocio (Usuarios, Agenda, etc.)

### 🟢 Admin Tenant (Gestión de Clínicas)
**Ubicación:** `<app>/admin.py` (cada app)  
**URL:** `http://clinica-demo.localhost:8000/admin/`  
**Esquema:** `clinica_demo` (u otro tenant)  
**Autenticación:** ✅ Requerida (usuarios.Usuario)

**¿Qué va aquí?**
- ✅ Modelos de negocio: `Usuario`, `Perfil*`, `Agenda`, `Tratamiento`, etc.
- ✅ Toda la lógica operativa de las clínicas
- ❌ **NUNCA** modelos de gestión de tenants

---

## 🆕 AGREGAR NUEVOS MODELOS

### ✅ Para Modelos de NEGOCIO (Clínicas)

**Ejemplo:** Agenda, Tratamientos, Historial Clínico, Facturación, etc.

#### 1️⃣ Crear el modelo
**Archivo:** `<app>/models.py`

```python
# agenda/models.py
from django.db import models
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo

class Cita(models.Model):
    paciente = models.ForeignKey(PerfilPaciente, on_delete=models.CASCADE)
    odontologo = models.ForeignKey(PerfilOdontologo, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ])
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Agenda"
```

#### 2️⃣ Registrar en el admin TENANT
**Archivo:** `<app>/admin.py`

```python
# agenda/admin.py
from django.contrib import admin
from .models import Cita

@admin.register(Cita)  # ✅ USA @admin.register para modelos de NEGOCIO
class CitaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'odontologo', 'fecha', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['paciente__usuario__nombre', 'odontologo__usuario__nombre']
    date_hierarchy = 'fecha'
```

#### 3️⃣ Crear las URLs de API
**Archivo:** `<app>/urls.py`

```python
# agenda/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
]
```

#### 4️⃣ Incluir en las URLs TENANT
**Archivo:** `core/urls_tenant.py` ⚠️ **IMPORTANTE**

```python
# core/urls_tenant.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # ← Admin TENANT (con autenticación)
    
    # API routes para TENANT (clínicas)
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),  # ← AGREGA AQUÍ
    path('api/historial/', include('historial_clinico.urls')),
    path('api/tratamientos/', include('tratamientos.urls')),
    # ... más apps de negocio
]
```

#### 5️⃣ Agregar a TENANT_APPS
**Archivo:** `core/settings.py`

```python
TENANT_APPS = [
    # Django core
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    
    # Third party
    'rest_framework',
    
    # Apps de negocio (TENANT)
    'usuarios',
    'agenda',  # ← AGREGA AQUÍ
    'tratamientos',
    'historial_clinico',
    'facturacion',
    'inventario',
    'reportes',
]
```

#### 6️⃣ Hacer migraciones
```bash
# IMPORTANTE: Migrar en TODOS los tenants
python manage.py makemigrations agenda
python manage.py migrate_schemas --shared  # Si es SHARED_APP
python manage.py migrate_schemas           # Para todos los tenants
```

---

### ❌ Para Modelos de GESTIÓN (Sistema)

**Ejemplo:** Nuevos campos en Clinica o Domain

#### 1️⃣ Modificar el modelo
**Archivo:** `tenants/models.py`

```python
# tenants/models.py
class Clinica(TenantMixin):
    nombre = models.CharField(max_length=100)
    plan = models.CharField(max_length=20)  # ← Nuevo campo
    # ...
```

#### 2️⃣ **NO REGISTRAR** en tenants/admin.py
**Archivo:** `tenants/admin.py`

```python
# tenants/admin.py
# ⚠️ NO USES @admin.register AQUÍ

class ClinicaAdmin(admin.ModelAdmin):
    """Para uso SOLO en PublicAdminSite"""
    list_display = ['nombre', 'schema_name', 'plan', 'activo']  # ← Agrega campo
```

#### 3️⃣ Registrar en PublicAdminSite
**Archivo:** `core/urls_public.py`

```python
# core/urls_public.py

class SimpleClinicaAdmin(ModelAdmin):
    list_display = ['nombre', 'schema_name', 'plan', 'activo']  # ← Agrega campo
    search_fields = ['nombre', 'schema_name']

public_admin.register(Clinica, SimpleClinicaAdmin)
```

#### 4️⃣ Agregar a SHARED_APPS
**Archivo:** `core/settings.py`

```python
SHARED_APPS = [
    'django_tenants',
    'tenants',  # ← Ya está aquí
    # NO agregar apps de negocio
]
```

---

## 🔗 AGREGAR NUEVAS APIs

### ✅ APIs para CLÍNICAS (lo más común)

**Ubicación:** `<app>/views.py` → `<app>/urls.py` → `core/urls_tenant.py`

**Ejemplo:** Endpoint para listar citas de un paciente

```python
# agenda/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cita
from .serializers import CitaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    permission_classes = [permissions.IsAuthenticated]  # ← Requiere JWT
    
    def get_queryset(self):
        # Solo citas del tenant actual (aislamiento automático)
        return Cita.objects.all()
    
    @action(detail=False, methods=['get'])
    def mis_citas(self, request):
        """GET /api/agenda/citas/mis_citas/"""
        # Filtrar citas del usuario actual
        if hasattr(request.user, 'perfilpaciente'):
            citas = Cita.objects.filter(paciente=request.user.perfilpaciente)
        elif hasattr(request.user, 'perfilodontologo'):
            citas = Cita.objects.filter(odontologo=request.user.perfilodontologo)
        else:
            citas = Cita.objects.none()
        
        serializer = self.get_serializer(citas, many=True)
        return Response(serializer.data)
```

**Incluir en URLs:**

```python
# agenda/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# core/urls_tenant.py ← IMPORTANTE: Agregar aquí
urlpatterns = [
    # ...
    path('api/agenda/', include('agenda.urls')),  # ← Nueva ruta
]
```

**URL resultante:**
- `POST http://clinica-demo.localhost:8000/api/agenda/citas/` (crear)
- `GET http://clinica-demo.localhost:8000/api/agenda/citas/` (listar)
- `GET http://clinica-demo.localhost:8000/api/agenda/citas/mis_citas/` (acción custom)

---

### ❌ APIs para GESTIÓN (menos común)

**Ubicación:** `tenants/views.py` → `tenants/urls.py` → `core/urls_public.py`

**Ejemplo:** Crear nueva clínica (sistema)

```python
# tenants/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Clinica, Domain
from .serializers import ClinicaSerializer

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer
    permission_classes = []  # ⚠️ Implementar autenticación apropiada
```

```python
# core/urls_public.py ← Agregar aquí
urlpatterns = [
    path('admin/', public_admin.urls),
    path('api/tenants/', include('tenants.urls')),  # ← APIs de gestión
]
```

**URL resultante:**
- `POST http://localhost:8000/api/tenants/clinicas/` (crear clínica)

---

## 🚦 REGLAS DE ORO

### ✅ SIEMPRE usa `core/urls_tenant.py` si:
- Es lógica de negocio (Agenda, Tratamientos, Facturación, etc.)
- Requiere autenticación con JWT
- Trabaja con datos específicos de una clínica
- Usa modelos de TENANT_APPS

### ❌ NUNCA uses `core/urls_public.py` para:
- Funcionalidades de clínicas
- APIs que requieren JWT de usuarios
- Modelos de negocio

### ✅ USA `core/urls_public.py` SOLO si:
- Es gestión de tenants (crear/editar Clinica o Domain)
- Es administración del sistema multi-tenant
- Usa modelos de SHARED_APPS

---

## 📋 CHECKLIST PARA NUEVA FUNCIONALIDAD

### Para features de CLÍNICAS (99% de los casos):

```
□ 1. Crear modelo en <app>/models.py
□ 2. Registrar con @admin.register en <app>/admin.py
□ 3. Crear serializer en <app>/serializers.py
□ 4. Crear views en <app>/views.py
□ 5. Crear urls en <app>/urls.py
□ 6. Incluir en core/urls_tenant.py (path('api/<app>/', ...))
□ 7. Agregar app a TENANT_APPS en settings.py
□ 8. Ejecutar: python manage.py makemigrations
□ 9. Ejecutar: python manage.py migrate_schemas
□ 10. Probar en http://clinica-demo.localhost:8000/api/<app>/
```

---

## 🧪 VERIFICAR SEPARACIÓN CORRECTA

Después de agregar nueva funcionalidad, ejecuta:

```bash
python verificar_sistema.py
```

**Debe mostrar:**
- ✅ Admin público: NO tiene tu nuevo modelo
- ✅ Admin tenant: SÍ tiene tu nuevo modelo
- ✅ API accesible solo en tenant URLs

---

## 📚 EJEMPLOS RÁPIDOS

### Ejemplo 1: Agregar módulo de Tratamientos

```python
# 1. tratamientos/models.py
class Tratamiento(models.Model):
    paciente = models.ForeignKey(PerfilPaciente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

# 2. tratamientos/admin.py
@admin.register(Tratamiento)  # ✅ Correcto
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo', 'costo']

# 3. tratamientos/urls.py
from rest_framework.routers import DefaultRouter
from .views import TratamientoViewSet

router = DefaultRouter()
router.register(r'', TratamientoViewSet)
urlpatterns = router.urls

# 4. core/urls_tenant.py ← IMPORTANTE
urlpatterns = [
    # ...
    path('api/tratamientos/', include('tratamientos.urls')),  # ← Aquí
]
```

### Ejemplo 2: Agregar campo a Clinica (gestión)

```python
# 1. tenants/models.py
class Clinica(TenantMixin):
    # ... campos existentes
    max_usuarios = models.IntegerField(default=10)  # ← Nuevo

# 2. core/urls_public.py ← IMPORTANTE
class SimpleClinicaAdmin(ModelAdmin):
    list_display = ['nombre', 'schema_name', 'max_usuarios', 'activo']  # ← Aquí

public_admin.register(Clinica, SimpleClinicaAdmin)
```

---

## 🔍 DEBUGGING

### ¿Tu modelo aparece en el admin incorrecto?

**Síntoma:** Clinicas/Domains en admin tenant  
**Causa:** Usaste `@admin.register` en `tenants/admin.py`  
**Solución:** Remover decorador, registrar en `core/urls_public.py`

**Síntoma:** Usuarios/Agenda en admin público  
**Causa:** Registraste en PublicAdminSite  
**Solución:** Usar `@admin.register` en `<app>/admin.py` (admin estándar)

### ¿Tu API no funciona?

**Síntoma:** 404 en `http://clinica-demo.localhost:8000/api/agenda/`  
**Causa:** No incluiste en `core/urls_tenant.py`  
**Solución:** Agregar `path('api/agenda/', include('agenda.urls'))`

**Síntoma:** 404 en `http://localhost:8000/api/tenants/`  
**Causa:** No incluiste en `core/urls_public.py`  
**Solución:** Agregar `path('api/tenants/', include('tenants.urls'))`

---

## 📞 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────────┐
│  🔵 ADMIN PÚBLICO (localhost:8000/admin/)                       │
│  core/urls_public.py → PublicAdminSite                          │
├─────────────────────────────────────────────────────────────────┤
│  Modelos:                                                       │
│    ✅ tenants.Clinica (gestión)                                │
│    ✅ tenants.Domain (gestión)                                 │
│    ❌ NUNCA modelos de negocio                                 │
├─────────────────────────────────────────────────────────────────┤
│  APIs:                                                          │
│    ✅ /api/tenants/ (crear clínicas, etc.)                     │
│    ❌ NUNCA APIs de operaciones de clínicas                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  🟢 ADMIN TENANT (clinica-demo.localhost:8000/admin/)           │
│  <app>/admin.py → admin.site (estándar)                         │
├─────────────────────────────────────────────────────────────────┤
│  Modelos:                                                       │
│    ✅ usuarios.Usuario                                          │
│    ✅ usuarios.Perfil*                                          │
│    ✅ agenda.Cita                                               │
│    ✅ tratamientos.Tratamiento                                  │
│    ✅ TODOS los modelos de negocio                             │
│    ❌ NUNCA tenants.Clinica ni tenants.Domain                  │
├─────────────────────────────────────────────────────────────────┤
│  APIs (core/urls_tenant.py):                                    │
│    ✅ /api/usuarios/                                            │
│    ✅ /api/agenda/                                              │
│    ✅ /api/tratamientos/                                        │
│    ✅ TODAS las APIs de operaciones                            │
│    ❌ NUNCA /api/tenants/                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎓 REGLA MNEMOTÉCNICA

**"Si lo usa la clínica → urls_tenant.py"**  
**"Si gestiona clínicas → urls_public.py"**

---

**Última actualización:** Noviembre 6, 2025  
**Versión del sistema:** 100% funcional (9/9 tests)
