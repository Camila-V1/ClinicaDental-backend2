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

**Credenciales:**
- Usuario: `superadmin@sistema.com`
- Password: `superadmin123`

**Debe mostrar SOLAMENTE:**
- ✅ Tenants
  - Clinicas
  - Domains
- ✅ Authentication and Authorization
  - Groups
  - Permissions (solo del esquema público)

**NO debe mostrar:**
- ❌ Usuarios
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

| Sitio | URL | Usuario | Password | Función |
|-------|-----|---------|----------|---------|
| **Público** | http://localhost:8000/admin/ | superadmin@sistema.com | superadmin123 | Administrar clínicas |
| **Clínica Demo** | http://clinica-demo.localhost:8000/admin/ | admin@clinica.com | 123456 | Administrar la clínica |

## 🔍 Solución de Problemas

### Error: "Invalid HTTP_HOST header"
- Verificar que el dominio esté en el archivo hosts
- Verificar que `ALLOWED_HOSTS` en settings.py incluya los dominios

### Los modelos aparecen en el admin incorrecto
- Verificar que todos los archivos admin.py tengan la verificación de `connection.schema_name`
- Reiniciar el servidor después de cambiar los archivos admin.py

### No puedo acceder a clinica-demo.localhost
- Verificar archivo hosts de Windows
- Intentar con: http://clinica-demo.localhost:8000 (incluir el puerto)
- Limpiar cache del navegador

## 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│          http://localhost:8000                      │
│         (Esquema: public)                           │
│                                                     │
│  Super Admin del Sistema                            │
│  - Crear nuevas clínicas (tenants)                  │
│  - Gestionar dominios                               │
│  - Administración global                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│    http://clinica-demo.localhost:8000               │
│         (Esquema: clinica_demo)                     │
│                                                     │
│  Admin de la Clínica                                │
│  - Gestionar usuarios (Pacientes, Odontólogos)      │
│  - Gestionar citas, tratamientos, etc.             │
│  - Datos aislados de otras clínicas                 │
└─────────────────────────────────────────────────────┘
```

## ✅ Checklist Final

- [ ] Archivo hosts configurado
- [ ] Servidor Django iniciado
- [ ] Acceso a sitio público verificado
- [ ] Acceso a sitio de clínica verificado
- [ ] Modelos correctos en cada admin
- [ ] API de registro funciona
- [ ] API de login funciona
- [ ] Tokens JWT se generan correctamente
