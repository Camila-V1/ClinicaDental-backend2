# 02 - ¿Dónde Va Cada Cosa?

## 🎯 Regla de Oro

```
┌────────────────────────────────────────────────┐
│  "Si lo usa LA CLÍNICA → urls_tenant.py"      │
│  "Si gestiona CLÍNICAS → urls_public.py"      │
└────────────────────────────────────────────────┘
```

---

## ✅ Va en TENANT (99% de los casos)

### Características
- Es funcionalidad de **negocio**
- Lo usan los usuarios de la clínica (odontólogos, pacientes, admin de clínica)
- Requiere autenticación JWT
- Trabaja con datos específicos de UNA clínica

### Ejemplos:
- ✅ Agenda de citas
- ✅ Tratamientos
- ✅ Historial clínico
- ✅ Facturación
- ✅ Inventario de la clínica
- ✅ Reportes de la clínica
- ✅ Usuarios (odontólogos, pacientes)
- ✅ Perfiles

### Ubicación del código:
```
<app>/models.py          → Modelo de negocio
<app>/admin.py           → @admin.register(Modelo)
<app>/serializers.py     → Serializers REST
<app>/views.py           → ViewSets / APIViews
<app>/urls.py            → URLs de la app
core/urls_tenant.py      → path('api/<app>/', include('<app>.urls'))
core/settings.py         → TENANT_APPS = [..., '<app>']
```

---

## ❌ Va en PUBLIC (1% de los casos)

### Características
- Es funcionalidad de **gestión del sistema**
- Lo usa el administrador del sistema (no de la clínica)
- Gestiona las clínicas en sí (crear, editar, desactivar)
- Trabaja con el esquema `public`

### Ejemplos:
- ❌ Crear/editar Clínica
- ❌ Asignar dominio a clínica
- ❌ Ver estadísticas globales (todas las clínicas)
- ❌ Configuración del sistema multi-tenant

### Ubicación del código:
```
tenants/models.py        → Clinica, Domain
tenants/admin.py         → Clases admin SIN @register
core/urls_public.py      → public_admin.register(...) + APIs
core/settings.py         → SHARED_APPS = ['tenants', ...]
```

---

## 🧠 Cómo Decidir

Hazte estas preguntas:

### Pregunta 1: ¿Quién lo usará?
```
┌─────────────────────────────────────────┐
│ Odontólogo / Paciente / Admin Clínica  │ → TENANT
├─────────────────────────────────────────┤
│ Administrador del Sistema               │ → PUBLIC
└─────────────────────────────────────────┘
```

### Pregunta 2: ¿Qué esquema usa?
```
┌─────────────────────────────────────────┐
│ Esquema clinica_demo / clinica_abc      │ → TENANT
├─────────────────────────────────────────┤
│ Esquema public                          │ → PUBLIC
└─────────────────────────────────────────┘
```

### Pregunta 3: ¿Requiere JWT?
```
┌─────────────────────────────────────────┐
│ SÍ (usuario de la clínica)              │ → TENANT
├─────────────────────────────────────────┤
│ NO (o HTTP Basic Auth)                  │ → PUBLIC
└─────────────────────────────────────────┘
```

### Pregunta 4: ¿FK a qué modelos?
```
┌─────────────────────────────────────────┐
│ FK a Usuario, Perfil*, etc.             │ → TENANT
├─────────────────────────────────────────┤
│ FK a Clinica, Domain                    │ → PUBLIC
└─────────────────────────────────────────┘
```

---

## 📋 Tabla de Decisión Rápida

| Funcionalidad | Tenant? | Public? | ¿Por qué? |
|---------------|---------|---------|-----------|
| **Agenda de citas** | ✅ | ❌ | Negocio de la clínica |
| **Tratamientos** | ✅ | ❌ | Negocio de la clínica |
| **Usuarios (odontos/pacientes)** | ✅ | ❌ | Usuarios de la clínica |
| **Historial clínico** | ✅ | ❌ | Datos del paciente |
| **Facturación** | ✅ | ❌ | Operación de la clínica |
| **Inventario** | ✅ | ❌ | Recursos de la clínica |
| **Reportes de clínica** | ✅ | ❌ | Análisis de la clínica |
| **Crear/editar Clínica** | ❌ | ✅ | Gestión del sistema |
| **Asignar dominio** | ❌ | ✅ | Configuración tenant |
| **Estadísticas globales** | ❌ | ✅ | Todas las clínicas |

---

## 🔍 Casos Especiales

### Caso: "Quiero ver lista de todas las clínicas"

**Desde el punto de vista del sistema:**
```python
# core/urls_public.py
path('api/tenants/clinicas/', ClinicaListView.as_view())
# Retorna TODAS las clínicas del sistema
```

**Desde el punto de vista de un admin de clínica:**
```python
# core/urls_tenant.py
path('api/mi-clinica/', MiClinicaView.as_view())
# Retorna SOLO los datos de SU clínica (conexión automática)
```

### Caso: "Configuración de la clínica"

Si es **configuración operativa** (horarios, logo, etc.):
- ✅ TENANT → Modelo `ConfiguracionClinica` en app `clinicas` (TENANT_APPS)

Si es **configuración del sistema tenant** (schema, plan, límites):
- ❌ PUBLIC → Modelo `Clinica` en app `tenants` (SHARED_APPS)

---

## ⚠️ Errores Comunes

### ❌ ERROR 1: Registrar modelos tenant en public admin
```python
# tenants/admin.py - ¡INCORRECTO!
@admin.register(Usuario)  # ← Usuario no existe en esquema público
class UsuarioAdmin(admin.ModelAdmin):
    pass
```

### ✅ CORRECTO:
```python
# usuarios/admin.py - ¡CORRECTO!
@admin.register(Usuario)  # ← Se registra en admin.site (tenant)
class UsuarioAdmin(admin.ModelAdmin):
    pass
```

---

### ❌ ERROR 2: APIs de clínica en URLs públicas
```python
# core/urls_public.py - ¡INCORRECTO!
path('api/agenda/', include('agenda.urls'))  # ← Agenda es de clínicas
```

### ✅ CORRECTO:
```python
# core/urls_tenant.py - ¡CORRECTO!
path('api/agenda/', include('agenda.urls'))  # ← Aquí va
```

---

### ❌ ERROR 3: Modelos públicos en TENANT_APPS
```python
# core/settings.py - ¡INCORRECTO!
TENANT_APPS = [
    'tenants',  # ← Clinica/Domain deben estar en SHARED_APPS
    'usuarios',
]
```

### ✅ CORRECTO:
```python
# core/settings.py - ¡CORRECTO!
SHARED_APPS = ['tenants']  # ← Clinica/Domain aquí
TENANT_APPS = ['usuarios', 'agenda', ...]  # ← Negocio aquí
```

---

## 🎓 Próximo Paso

- Para crear modelo de negocio: **[03-crear-modelo-negocio.md](03-crear-modelo-negocio.md)**
- Para crear modelo de gestión: **[04-crear-modelo-gestion.md](04-crear-modelo-gestion.md)**
