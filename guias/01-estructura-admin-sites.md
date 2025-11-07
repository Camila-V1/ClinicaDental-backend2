# 01 - Estructura de Admin Sites

## 🎯 Dos Admin Sites Separados

El sistema tiene **DOS** admin sites completamente independientes:

---

## 🔵 Admin Público (Gestión de Sistema)

### Información General
- **URL:** `http://localhost:8000/admin/`
- **Archivo:** `core/urls_public.py`
- **AdminSite:** `PublicAdminSite` (custom)
- **Esquema DB:** `public`
- **Autenticación:** ❌ No requiere (desarrollo) / ⚠️ HTTP Basic Auth (producción)

### ¿Qué contiene?
```
Admin Público
├── TENANTS (Administración de Clínicas)
│   ├── Clínicas
│   └── Domains
└── (NO tiene nada más)
```

### Características
- Sin autenticación de usuarios (no existe tabla `usuarios_usuario` en esquema público)
- Template personalizado: `templates/admin_public/index.html`
- Métodos sobrescritos: `has_permission()`, `login()`, `each_context()`, etc.
- Solo modelos de `SHARED_APPS`

### Código de Registro
```python
# En core/urls_public.py
public_admin = PublicAdminSite(name='public_admin')

public_admin.register(Clinica, SimpleClinicaAdmin)
public_admin.register(Domain, SimpleDomainAdmin)
```

---

## 🟢 Admin Tenant (Gestión de Clínicas)

### Información General
- **URL:** `http://clinica-demo.localhost:8000/admin/`
- **Archivo:** Múltiples `<app>/admin.py`
- **AdminSite:** `admin.site` (Django estándar)
- **Esquema DB:** `clinica_demo` (u otro tenant)
- **Autenticación:** ✅ Requerida (usuarios.Usuario + JWT)

### ¿Qué contiene?
```
Admin Tenant
├── AUTHENTICATION AND AUTHORIZATION
│   └── Groups
├── USUARIOS
│   ├── Perfiles Odontólogos
│   ├── Perfiles Pacientes
│   └── Usuarios
├── AGENDA (cuando lo implementes)
│   └── Citas
├── TRATAMIENTOS (cuando lo implementes)
│   └── Tratamientos
└── ... más apps de negocio
```

### Características
- Requiere login con `usuarios.Usuario`
- Template estándar de Django admin
- Todos los modelos de `TENANT_APPS`
- Aislamiento automático por schema

### Código de Registro
```python
# En usuarios/admin.py
from django.contrib import admin

@admin.register(Usuario)  # ← Usa el admin.site estándar
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'nombre', 'apellido']
```

---

## ⚠️ Regla Fundamental

```
┌──────────────────────────────────────────────────────┐
│  SI USAS @admin.register                             │
│  → Se registra en admin.site ESTÁNDAR (tenant)       │
│  → Aparecerá en clinica-demo.localhost:8000/admin/  │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  SI USAS public_admin.register(...)                  │
│  → Se registra en PublicAdminSite (público)          │
│  → Aparecerá en localhost:8000/admin/               │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Comparación Rápida

| Aspecto | Admin Público | Admin Tenant |
|---------|---------------|--------------|
| **URL** | localhost:8000/admin/ | clinica-demo.localhost:8000/admin/ |
| **Login** | ❌ No requiere | ✅ Requerido |
| **Esquema** | public | clinica_demo |
| **Modelos** | Clinica, Domain | Usuario, Perfil*, Agenda, etc. |
| **Registro** | `public_admin.register()` | `@admin.register` |
| **Archivo** | `core/urls_public.py` | `<app>/admin.py` |
| **Template** | Custom (admin_public/index.html) | Standard (admin/index.html) |
| **Usuario** | N/A | usuarios.Usuario |

---

## 🔍 ¿Cómo saber en cuál estoy?

### Por URL:
- `localhost:8000/admin/` → Admin Público
- `*.localhost:8000/admin/` → Admin Tenant

### Por contenido:
- ¿Tiene "Clínicas" y "Domains"? → Admin Público
- ¿Tiene "Usuarios" y "Perfiles"? → Admin Tenant

### Por login:
- ¿Entra sin login? → Admin Público
- ¿Pide email/password? → Admin Tenant

---

## 💡 Ejemplo Visual

```
Browser: http://localhost:8000/admin/
┌─────────────────────────────────────────┐
│ Administración del Sistema Multi-Tenant │
├─────────────────────────────────────────┤
│ TENANTS (ADMINISTRACIÓN DE CLÍNICAS)    │
│   • Clínicas                            │
│   • Domains                             │
└─────────────────────────────────────────┘
       ↑
       Esto es el Admin PÚBLICO


Browser: http://clinica-demo.localhost:8000/admin/
┌─────────────────────────────────────────┐
│ [Login requerido]                       │
│ Email: admin@clinica.com                │
│ Password: ******                        │
└─────────────────────────────────────────┘
       ↓ Después del login
┌─────────────────────────────────────────┐
│ Django administration                   │
├─────────────────────────────────────────┤
│ AUTHENTICATION AND AUTHORIZATION        │
│   • Groups                              │
│ USUARIOS                                │
│   • Perfiles Odontólogos                │
│   • Perfiles Pacientes                  │
│   • Usuarios                            │
└─────────────────────────────────────────┘
       ↑
       Esto es el Admin TENANT
```

---

## 🎓 Próximo Paso

Lee: **[02-donde-va-cada-cosa.md](02-donde-va-cada-cosa.md)** para saber dónde colocar tu código nuevo.
