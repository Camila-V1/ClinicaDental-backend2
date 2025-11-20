# 🔑 CREDENCIALES DE ACCESO - SISTEMA CLÍNICA DENTAL

**Fecha de Actualización:** 20 de Noviembre, 2025  
**Tenant:** Clínica Dental Demo  
**Dominio Local:** clinica-demo.localhost:8000  
**Dominio Producción:** clinicademo1.dentaabcxy.store

---

## 📋 CREDENCIALES DE PRUEBA

### 👨‍💼 ADMINISTRADOR
```
Email:    admin@clinica-demo.com
Password: admin123
Tipo:     ADMIN
Permisos: Acceso total al sistema
```

**Puede acceder a:**
- ✅ Dashboard completo con KPIs
- ✅ Gestión de usuarios (crear, editar, eliminar)
- ✅ Gestión de citas (todas las citas)
- ✅ Planes de tratamiento (todos los planes)
- ✅ Facturas y pagos (todas)
- ✅ Inventario completo
- ✅ Reportes y estadísticas
- ✅ Configuración del sistema

---

### 🦷 ODONTÓLOGO
```
Email:    odontologo@clinica-demo.com
Password: odontologo123
Tipo:     ODONTOLOGO
Permisos: Gestión clínica de pacientes asignados
```

**Puede acceder a:**
- ✅ Sus citas programadas
- ✅ Historiales clínicos de sus pacientes
- ✅ Crear/editar episodios de atención
- ✅ Gestionar documentos clínicos
- ✅ Crear planes de tratamiento
- ✅ Ver odontogramas
- ⛔ NO puede gestionar usuarios
- ⛔ NO puede ver reportes financieros globales

---

### 🧑‍⚕️ PACIENTE
```
Email:    paciente@clinica-demo.com
Password: paciente123
Tipo:     PACIENTE
Permisos: Solo visualización de datos propios
```

**Puede acceder a:**
- ✅ Su perfil médico
- ✅ Sus citas (agendar, reprogramar, cancelar)
- ✅ Su historial clínico (solo lectura)
- ✅ Sus documentos clínicos
- ✅ Sus planes de tratamiento
- ✅ Sus facturas y pagos
- ⛔ NO puede ver datos de otros pacientes
- ⛔ NO puede acceder a reportes
- ⛔ NO puede gestionar inventario

---

## 🔐 EJEMPLOS DE USO (PowerShell)

### 1️⃣ Login como Administrador

```powershell
# Obtener token
$body = '{"email": "admin@clinica-demo.com", "password": "admin123"}'
$response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
$token = $response.access

# Guardar headers para peticiones subsecuentes
$headers = @{"Authorization" = "Bearer $token"}

# Probar endpoint
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/usuarios/me/" -Headers $headers
```

**Respuesta esperada:**
```json
{
  "id": 7,
  "email": "admin@clinica-demo.com",
  "nombre": "Administrador",
  "apellido": "Principal",
  "full_name": "Administrador Principal",
  "tipo_usuario": "ADMIN",
  "is_active": true
}
```

---

### 2️⃣ Login como Odontólogo

```powershell
# Obtener token
$body = '{"email": "odontologo@clinica-demo.com", "password": "odontologo123"}'
$response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
$token = $response.access
$headers = @{"Authorization" = "Bearer $token"}

# Ver perfil
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/usuarios/me/" -Headers $headers

# Ver lista de pacientes
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/usuarios/pacientes/" -Headers $headers

# Ver citas del odontólogo
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/agenda/citas/" -Headers $headers
```

---

### 3️⃣ Login como Paciente

```powershell
# Obtener token
$body = '{"email": "paciente@clinica-demo.com", "password": "paciente123"}'
$response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
$token = $response.access
$headers = @{"Authorization" = "Bearer $token"}

# Ver perfil propio
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/usuarios/me/" -Headers $headers

# Ver mis citas
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/agenda/citas/" -Headers $headers

# Ver mi historial clínico
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/historial/historiales/" -Headers $headers
```

---

## 🌐 ENDPOINTS PRINCIPALES

### Autenticación
```
POST /api/token/                    # Obtener access + refresh token
POST /api/token/refresh/            # Refrescar access token
```

### Usuarios
```
GET  /api/usuarios/me/              # Datos del usuario actual
GET  /api/usuarios/pacientes/       # Listar pacientes (Admin/Odontologo)
GET  /api/usuarios/odontologos/     # Listar odontólogos
POST /api/usuarios/register/        # Registro de nuevo paciente
```

### Agenda
```
GET    /api/agenda/citas/           # Listar citas (filtrado por rol)
POST   /api/agenda/citas/           # Crear nueva cita
PATCH  /api/agenda/citas/{id}/      # Reprogramar cita
POST   /api/agenda/citas/{id}/cancelar/          # Cancelar cita
POST   /api/agenda/citas/{id}/marcar_asistencia/ # Marcar asistencia
```

### Historial Clínico
```
GET  /api/historial/historiales/    # Historiales (filtrado por rol)
GET  /api/historial/episodios/      # Episodios de atención
POST /api/historial/episodios/      # Crear episodio
GET  /api/historial/documentos/     # Documentos clínicos
POST /api/historial/documentos/     # Subir documento
```

### Tratamientos
```
GET  /api/tratamientos/catalogo/    # Catálogo de tratamientos
GET  /api/tratamientos/planes/      # Planes de tratamiento
POST /api/tratamientos/planes/      # Crear plan
```

### Facturación
```
GET  /api/facturacion/facturas/     # Listar facturas
POST /api/facturacion/facturas/     # Generar factura
POST /api/facturacion/pagos/        # Registrar pago
```

### Reportes
```
GET  /api/reportes/reportes/dashboard-kpis/           # KPIs principales
GET  /api/reportes/reportes/estadisticas-generales/   # Estadísticas
GET  /api/reportes/reportes/reporte-pacientes/        # Reporte de pacientes
GET  /api/reportes/reportes/reporte-financiero/       # Reporte financiero
```

---

## ✅ VERIFICACIÓN DE CREDENCIALES

### Test Rápido (PowerShell)

```powershell
# Script de verificación completa
Write-Host "🔍 Verificando credenciales...`n" -ForegroundColor Yellow

# Admin
Write-Host "👨‍💼 Probando ADMINISTRADOR..." -ForegroundColor Cyan
$body = '{"email": "admin@clinica-demo.com", "password": "admin123"}'
try {
    $response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ ADMIN: Login exitoso" -ForegroundColor Green
} catch {
    Write-Host "❌ ADMIN: Login fallido" -ForegroundColor Red
}

# Odontólogo
Write-Host "`n🦷 Probando ODONTÓLOGO..." -ForegroundColor Cyan
$body = '{"email": "odontologo@clinica-demo.com", "password": "odontologo123"}'
try {
    $response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ ODONTOLOGO: Login exitoso" -ForegroundColor Green
} catch {
    Write-Host "❌ ODONTOLOGO: Login fallido" -ForegroundColor Red
}

# Paciente
Write-Host "`n🧑‍⚕️ Probando PACIENTE..." -ForegroundColor Cyan
$body = '{"email": "paciente@clinica-demo.com", "password": "paciente123"}'
try {
    $response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ PACIENTE: Login exitoso" -ForegroundColor Green
} catch {
    Write-Host "❌ PACIENTE: Login fallido" -ForegroundColor Red
}

Write-Host "`n✅ Verificación completada`n" -ForegroundColor Yellow
```

---

## 🚀 PRUEBAS EN PRODUCCIÓN

**URL Base:** https://clinicademo1.dentaabcxy.store

### ⚠️ IMPORTANTE
Las credenciales funcionarán en producción **SOLO SI**:
1. ✅ El deployment en Render se completó exitosamente
2. ✅ Se ejecutó el script `poblar_sistema_completo.py` en producción
3. ✅ El dominio `clinicademo1.dentaabcxy.store` está correctamente configurado

### Comando de prueba en producción:
```powershell
$body = '{"email": "admin@clinica-demo.com", "password": "admin123"}'
Invoke-RestMethod -Uri "https://clinicademo1.dentaabcxy.store/api/token/" -Method POST -ContentType "application/json" -Body $body
```

---

## 📝 NOTAS ADICIONALES

### Seguridad
- 🔒 Tokens JWT con expiración automática
- 🔒 Refresh tokens para renovación
- 🔒 Permisos por rol (IsAdministrador, IsOdontologo, IsPaciente)
- 🔒 Filtrado automático por tenant

### Tokens
- **Access Token:** Válido por 60 minutos
- **Refresh Token:** Válido por 30 días
- **Formato:** Bearer {token}

### Troubleshooting
- Si el login falla: Verificar que el servidor esté corriendo
- Si el token expira: Usar el refresh token
- Si no hay permisos: Verificar el tipo_usuario del token

---

**Generado automáticamente el:** 20/11/2025  
**Script:** `crear_usuarios_prueba.py`
