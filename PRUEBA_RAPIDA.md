# 🚀 Prueba Rápida del Sistema Multi-Tenant

## ✅ Verificación de Separación de Admin Sites

### 1️⃣ Admin Público (localhost)

**URL:** http://localhost:8000/admin/

**Comportamiento Esperado:**
- ✅ Acceso DIRECTO sin login
- ✅ Título: "Administración del Sistema Multi-Tenant"
- ✅ Modelos visibles:
  - Tenants → Clinicas
  - Tenants → Domains
  - Authentication and Authorization → Groups

**❌ NO debe mostrar:**
- Usuarios
- Perfiles (Odontólogo, Paciente)
- Agenda, Tratamientos, etc.

---

### 2️⃣ Admin de Clínica (tenant)

**IMPORTANTE:** Primero configura el archivo hosts:

#### Windows (PowerShell como Administrador):
```powershell
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "`n127.0.0.1   clinica-demo.localhost"
```

**URL:** http://clinica-demo.localhost:8000/admin/

**Credenciales:**
- Email: `admin@clinica.com`
- Password: `123456`

**Comportamiento Esperado:**
- ✅ Pantalla de LOGIN (requiere autenticación)
- ✅ Título: "Django administration" (admin estándar)
- ✅ Modelos visibles:
  - Usuarios → Usuarios
  - Usuarios → Perfil odontólogo
  - Usuarios → Perfil paciente
  - Authentication and Authorization → Groups

**❌ NO debe mostrar:**
- Tenants
- Clinicas
- Domains

---

## 🧪 Pruebas de API

### Registro de Paciente (en tenant)

```bash
curl -X POST http://clinica-demo.localhost:8000/api/usuarios/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "paciente.test@email.com",
    "password": "password123",
    "password2": "password123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "fecha_de_nacimiento": "1990-01-15",
    "direccion": "Calle Principal 123"
  }'
```

**Respuesta esperada:** `201 Created` con datos del usuario

### Login JWT (en tenant)

```bash
curl -X POST http://clinica-demo.localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinica.com",
    "password": "123456"
  }'
```

**Respuesta esperada:** Tokens de acceso y refresh

### Usuario Actual (con JWT)

```bash
# Primero obtén el token del endpoint anterior, luego:
curl http://clinica-demo.localhost:8000/api/usuarios/me/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Respuesta esperada:** Datos del usuario autenticado

---

## 📋 Checklist de Verificación

- [ ] ✅ Servidor iniciado: `python manage.py runserver`
- [ ] ✅ Admin público accesible sin login (localhost:8000/admin/)
- [ ] ✅ Admin público muestra SOLO Clinicas, Domains, Groups
- [ ] ✅ Archivo hosts configurado con clinica-demo.localhost
- [ ] ✅ Admin tenant requiere login (clinica-demo.localhost:8000/admin/)
- [ ] ✅ Admin tenant muestra SOLO Usuarios, Perfiles, etc.
- [ ] ✅ API de registro funciona (POST /api/usuarios/register/)
- [ ] ✅ API de login funciona (POST /api/token/)
- [ ] ✅ API de usuario actual funciona (GET /api/usuarios/me/)

---

## 🐛 Troubleshooting

### Error: "no existe la relación usuarios_usuario"
✅ **SOLUCIONADO** - El admin público ya NO intenta autenticar con Usuario.

### Error: "Invalid HTTP_HOST header: 'clinica-demo.localhost'"
- Verificar archivo hosts de Windows
- Agregar `ALLOWED_HOSTS = ['*']` en settings.py (solo desarrollo)

### Admin muestra modelos incorrectos
✅ **SOLUCIONADO** - Separación completa con PUBLIC_SCHEMA_URLCONF

### No puedo acceder a clinica-demo.localhost
1. Verificar archivo hosts: `C:\Windows\System32\drivers\etc\hosts`
2. Debe contener: `127.0.0.1   clinica-demo.localhost`
3. Reiniciar navegador después de modificar hosts
4. Incluir el puerto: `http://clinica-demo.localhost:8000`

---

## ✅ Estado del Sistema

**Última actualización:** Noviembre 6, 2025

- ✅ Separación de admin sites: FUNCIONAL
- ✅ Admin público sin autenticación: IMPLEMENTADO
- ✅ Admin tenant con autenticación: FUNCIONAL
- ✅ API de registro: FUNCIONAL
- ✅ JWT authentication: FUNCIONAL
- ✅ Aislamiento de datos por tenant: VERIFICADO

**Próximo paso:** Implementar lógica de negocio (Agenda, Tratamientos, Historial Clínico)
