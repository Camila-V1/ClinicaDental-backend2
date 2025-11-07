# 09 - Debugging: Admin Incorrecto

## 🚨 Problema: Modelo en Admin Equivocado

---

## Síntoma 1: Modelo de Clínica en Admin Público

### ❌ Error
Abres `http://localhost:8000/admin/` y ves:
```
Admin Público
├── TENANTS
│   ├── Clínicas
│   └── Domains
└── USUARIOS  ← ❌ ¡NO DEBE ESTAR AQUÍ!
    └── Usuarios
```

### 🔍 Causa
Registraste el modelo en `PublicAdminSite` por error.

### ✅ Solución

**1. Buscar dónde está registrado:**
```python
# Buscar en core/urls_public.py
public_admin.register(Usuario, UsuarioAdmin)  # ← Encontrado
```

**2. ELIMINAR de urls_public.py:**
```python
# core/urls_public.py
# ❌ ELIMINAR ESTAS LÍNEAS
# from usuarios.models import Usuario
# from usuarios.admin import UsuarioAdmin
# public_admin.register(Usuario, UsuarioAdmin)
```

**3. MOVER a usuarios/admin.py:**
```python
# usuarios/admin.py
from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)  # ← Usar decorador
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'nombre', 'apellido']
```

**4. Reiniciar servidor:**
```bash
# Ctrl+C en terminal
python manage.py runserver
```

**5. Verificar:**
- `localhost:8000/admin/` → NO debe tener Usuarios
- `clinica-demo.localhost:8000/admin/` → SÍ debe tener Usuarios

---

## Síntoma 2: Clinica/Domain en Admin Tenant

### ❌ Error
Abres `http://clinica-demo.localhost:8000/admin/` y ves:
```
Admin Tenant
├── USUARIOS
│   └── Usuarios
└── TENANTS  ← ❌ ¡NO DEBE ESTAR AQUÍ!
    ├── Clínicas
    └── Domains
```

### 🔍 Causa
Usaste `@admin.register` en `tenants/admin.py`.

### ✅ Solución

**1. Abrir tenants/admin.py:**
```python
# tenants/admin.py
from django.contrib import admin
from .models import Clinica, Domain

@admin.register(Clinica)  # ← ❌ PROBLEMA AQUÍ
class ClinicaAdmin(admin.ModelAdmin):
    pass
```

**2. QUITAR decorador @admin.register:**
```python
# tenants/admin.py
from django.contrib import admin
from .models import Clinica, Domain

# ✅ SIN decorador (no se registra automáticamente)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'schema_name', 'activo']
```

**3. Asegurar que ESTÉ en core/urls_public.py:**
```python
# core/urls_public.py
from tenants.models import Clinica, Domain

class SimpleClinicaAdmin(ModelAdmin):
    list_display = ['nombre', 'schema_name', 'activo']

public_admin.register(Clinica, SimpleClinicaAdmin)
public_admin.register(Domain, SimpleDomainAdmin)
```

**4. Reiniciar servidor y verificar.**

---

## Síntoma 3: Modelo No Aparece en Ningún Admin

### ❌ Error
Creaste un modelo pero no aparece ni en admin público ni tenant.

### 🔍 Causas Posibles

#### Causa A: No está registrado
```python
# agenda/admin.py
from .models import Cita

# ❌ Clase definida pero NO registrada
class CitaAdmin(admin.ModelAdmin):
    pass
```

**Solución:**
```python
# agenda/admin.py
from django.contrib import admin
from .models import Cita

@admin.register(Cita)  # ← ✅ Agregar decorador
class CitaAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'paciente']
```

---

#### Causa B: App no está en INSTALLED_APPS
```python
# core/settings.py
TENANT_APPS = [
    'usuarios',
    # 'agenda',  ← ❌ Comentado o falta
]
```

**Solución:**
```python
# core/settings.py
TENANT_APPS = [
    'usuarios',
    'agenda',  # ← ✅ Descomentar o agregar
]
```

---

#### Causa C: Migraciones no aplicadas
```bash
# Verificar
python manage.py showmigrations agenda

# Si no hay migraciones:
python manage.py makemigrations agenda
python manage.py migrate_schemas
```

---

## Síntoma 4: Cambios en Admin No Se Reflejan

### ❌ Error
Modificaste `admin.py` pero no ves cambios en el navegador.

### ✅ Solución

**1. Reiniciar servidor Django:**
```bash
# Ctrl+C en terminal
python manage.py runserver
```

**2. Refrescar navegador con caché limpio:**
- Chrome/Edge: `Ctrl + Shift + R`
- Firefox: `Ctrl + F5`

**3. Verificar que editaste el archivo correcto:**
```bash
# Ver última modificación
Get-ChildItem agenda\admin.py | Select-Object FullName, LastWriteTime
```

---

## 🔧 Herramientas de Debugging

### Ver Modelos Registrados

```bash
python manage.py shell
```
```python
from django.contrib import admin
from core.urls_public import public_admin

# Modelos en admin.site (tenant)
print("=== ADMIN TENANT (admin.site) ===")
for model, model_admin in admin.site._registry.items():
    app = model._meta.app_label
    name = model.__name__
    print(f"{app}.{name}")

print("\n=== ADMIN PÚBLICO (public_admin) ===")
for model, model_admin in public_admin._registry.items():
    app = model._meta.app_label
    name = model.__name__
    print(f"{app}.{name}")
```

### Ver Apps Instaladas

```bash
python manage.py shell
```
```python
from django.apps import apps

print("=== TENANT_APPS ===")
from django.conf import settings
for app in settings.TENANT_APPS:
    print(f"  - {app}")

print("\n=== SHARED_APPS ===")
for app in settings.SHARED_APPS:
    print(f"  - {app}")
```

---

## 📋 Checklist de Debugging

```
□ 1. ¿El modelo está en admin.py?
     → Buscar en <app>/admin.py

□ 2. ¿Tiene @admin.register?
     → Debe tenerlo para modelos tenant
     → NO debe tenerlo para modelos públicos

□ 3. ¿La app está en TENANT_APPS o SHARED_APPS?
     → settings.py → TENANT_APPS o SHARED_APPS

□ 4. ¿Las migraciones están aplicadas?
     → python manage.py showmigrations <app>

□ 5. ¿Reiniciaste el servidor?
     → Ctrl+C → python manage.py runserver

□ 6. ¿Limpiaste caché del navegador?
     → Ctrl+Shift+R

□ 7. ¿Estás en el admin correcto?
     → localhost:8000/admin/ (público)
     → clinica-demo.localhost:8000/admin/ (tenant)
```

---

## 🎓 Regla Mnemotécnica

```
┌─────────────────────────────────────────────────┐
│  @admin.register(Modelo)                        │
│  → admin.site (tenant)                          │
│  → clinica-demo.localhost:8000/admin/           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  public_admin.register(Modelo, Admin)           │
│  → PublicAdminSite (público)                    │
│  → localhost:8000/admin/                        │
└─────────────────────────────────────────────────┘
```

---

## 🆘 Último Recurso

Si nada funciona, ejecuta diagnóstico completo:

```bash
python manage.py shell
```
```python
# Script de diagnóstico
from django.contrib import admin
from core.urls_public import public_admin
from django.conf import settings
from django.apps import apps

print("="*50)
print("DIAGNÓSTICO COMPLETO")
print("="*50)

print("\n1. TENANT_APPS:")
for app in settings.TENANT_APPS:
    print(f"   ✓ {app}")

print("\n2. Modelos en admin.site:")
for model in admin.site._registry:
    print(f"   ✓ {model._meta.app_label}.{model.__name__}")

print("\n3. Modelos en public_admin:")
for model in public_admin._registry:
    print(f"   ✓ {model._meta.app_label}.{model.__name__}")

print("\n4. Apps instaladas:")
for app in apps.get_app_configs():
    print(f"   ✓ {app.name}")
```

Copia la salida y compárala con lo esperado. 🔍
