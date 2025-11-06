# Guía de Verificación del Sistema Multi-Tenant

## ✅ Pasos para Verificar la Configuración

### 1. Configurar el Archivo Hosts (SI NO LO HAS HECHO)

**Abrir PowerShell como Administrador** y ejecutar:
```powershell
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "`n# Django Multi-Tenant`n127.0.0.1   clinica-demo.localhost"
```

O manualmente:
1. Abrir Notepad como Administrador
2. Abrir: `C:\Windows\System32\drivers\etc\hosts`
3. Agregar al final:
```
127.0.0.1   clinica-demo.localhost
```

### 2. Reiniciar el Servidor Django

```bash
python manage.py runserver
```

### 3. Probar el Sitio Público

**URL:** http://localhost:8000/admin/

**⚠️ IMPORTANTE:** El admin público **NO requiere login** porque:
- El modelo `usuarios.Usuario` solo existe en esquemas tenant
- No hay tabla auth_user en el esquema público
- El `PublicAdminSite` sobrescribe `has_permission()` para permitir acceso directo

**🔒 Seguridad en Producción:**
- Implementar HTTP Basic Authentication a nivel de servidor web (nginx/Apache)
- Restricción por IP/VPN
- O gestionar tenants exclusivamente via API desde un tenant administrativo

**Debe mostrar SOLAMENTE:**
- ✅ Tenants
  - Clinicas
  - Domains
- ✅ Authentication and Authorization
  - Groups

**NO debe mostrar:**
- ❌ Usuarios (está SOLO en tenant schemas)
- ❌ Perfil Odontólogo
- ❌ Perfil Paciente
- ❌ Agenda, Historial, etc.

### 4. Probar el Sitio de la Clínica

**URL:** http://clinica-demo.localhost:8000/admin/

**Credenciales:**
- Usuario: `admin@clinica.com`
- Password: `123456`

**Debe mostrar SOLAMENTE:**
- ✅ Usuarios
  - Usuarios
  - Perfil Odontólogo
  - Perfil Paciente
- ✅ Authentication and Authorization
  - Groups
  - Permissions (del tenant)

**NO debe mostrar:**
- ❌ Tenants
- ❌ Clinicas
- ❌ Domains

### 5. Probar los Endpoints de API

#### En la Clínica Demo:

**Registro de Paciente:**
```bash
curl -X POST http://clinica-demo.localhost:8000/api/usuarios/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "paciente@test.com",
    "password": "password123",
    "password2": "password123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "fecha_de_nacimiento": "1990-01-15",
    "direccion": "Calle Principal 123"
  }'
```

**Login:**
```bash
curl -X POST http://clinica-demo.localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinica.com",
    "password": "123456"
  }'
```

## 📊 Resumen de Dominios y Credenciales

| Sitio | URL | Autenticación | Función |
|-------|-----|---------------|---------|
| **Público** | http://localhost:8000/admin/ | ❌ Sin login (acceso directo) | Administrar clínicas y dominios |
| **Clínica Demo** | http://clinica-demo.localhost:8000/admin/ | ✅ admin@clinica.com / 123456 | Administrar la clínica |

**Notas de Seguridad:**
- ⚠️ El admin público NO tiene autenticación porque `usuarios.Usuario` solo existe en tenant schemas
- 🔒 Para producción: Implementar HTTP Basic Auth, restricción por IP, o VPN
- ✅ Los administradores de clínicas acceden via subdominios con autenticación completa

## 🔍 Solución de Problemas

### Error: "Invalid HTTP_HOST header"
- Verificar que el dominio esté en el archivo hosts
- Verificar que `ALLOWED_HOSTS` en settings.py incluya los dominios

### Los modelos aparecen en el admin incorrecto
- ✅ SOLUCIONADO con la implementación de PUBLIC_SCHEMA_URLCONF
- La separación ahora se hace a nivel de URL routing, NO en admin.py
- Cada esquema tiene su propio AdminSite con modelos específicos

### Los checks de connection.schema_name no funcionan
- ✅ PROBLEMA IDENTIFICADO: admin.py se carga UNA VEZ al inicio en esquema público
- ✅ SOLUCIÓN: Separar AdminSite instances (PublicAdminSite vs admin.site)
- NO usar verificaciones condicionales en admin.py

### No puedo acceder a clinica-demo.localhost
- Verificar archivo hosts de Windows
- Intentar con: http://clinica-demo.localhost:8000 (incluir el puerto)
- Limpiar cache del navegador

## 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│          http://localhost:8000                      │
│         (Esquema: public)                           │
│         URLs: core/urls_public.py                   │
│                                                     │
│  PublicAdminSite (custom AdminSite)                 │
│  - Crear nuevas clínicas (tenants)                  │
│  - Gestionar dominios                               │
│  - Modelos: Clinica, Domain, Group                  │
│  - SIN autenticación de usuarios por ahora          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│    http://clinica-demo.localhost:8000               │
│         (Esquema: clinica_demo)                     │
│         URLs: core/urls_tenant.py                   │
│                                                     │
│  admin.site (Django standard AdminSite)             │
│  - Gestionar usuarios (Pacientes, Odontólogos)      │
│  - Gestionar citas, tratamientos, etc.             │
│  - Datos aislados de otras clínicas                 │
│  - Autenticación: usuarios.Usuario                  │
└─────────────────────────────────────────────────────┘
```

### Detalles Técnicos de la Separación

**1. Configuración en settings.py:**
```python
ROOT_URLCONF = 'core.urls_tenant'           # Para tenants
PUBLIC_SCHEMA_URLCONF = 'core.urls_public'  # Para localhost
```

**2. SHARED_APPS (solo en esquema public):**
- django_tenants, tenants
- Django contrib: auth, contenttypes, sessions, messages, staticfiles
- **NO incluye: django.contrib.admin** (evita FK a usuarios.Usuario)
- **NO incluye: usuarios** (exclusivo de tenants)

**3. TENANT_APPS (solo en esquemas tenant):**
- django.contrib.admin (con usuario personalizado)
- usuarios, agenda, historial_clinico, tratamientos, facturacion, inventario, reportes

**4. Patrón AdminSite:**
- `PublicAdminSite` (core/urls_public.py): Registra Clinica, Domain, Group
- `admin.site` (core/urls_tenant.py): Registra modelos de negocio

Este patrón garantiza que los modelos correctos aparezcan en cada admin según el esquema activo.

## ✅ Checklist Final

- [ ] Archivo hosts configurado
- [ ] Servidor Django iniciado
- [ ] Acceso a sitio público verificado
- [ ] Acceso a sitio de clínica verificado
- [ ] Modelos correctos en cada admin
- [ ] API de registro funciona
- [ ] API de login funciona
- [ ] Tokens JWT se generan correctamente
