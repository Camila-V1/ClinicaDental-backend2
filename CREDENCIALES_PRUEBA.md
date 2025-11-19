# 🔐 CREDENCIALES DE PRUEBA - SISTEMA CLÍNICA DENTAL

**Fecha:** 15 de Noviembre, 2025  
**Sistema:** Multi-Tenant con JWT Authentication  
**Backend:** Django 5.2.6 + DRF

---

## 🏥 TENANTS DE PRUEBA

### **Tenant 1: Clínica Demo (Principal)**
```
Subdomain: clinica-demo
Schema: clinica_demo
URL Completa: http://clinica-demo.localhost:8000/
```

### **Tenant 2: Clínica 1 (Alternativo)**
```
Subdomain: clinica1
Schema: clinica1
URL Completa: http://clinica1.localhost:8000/
```

---

## 👥 USUARIOS POR ROL

### 👨‍💼 **1. ADMINISTRADOR**

```json
{
  "username": "admin_clinica",
  "password": "admin123",
  "email": "admin@clinica1.com",
  "tipo_usuario": "administrador"
}
```

**Permisos:**
- ✅ Acceso total al sistema
- ✅ Gestión de usuarios
- ✅ Configuración del sistema
- ✅ Ver todos los reportes
- ✅ CRUD completo en todos los módulos

**Endpoints de prueba:**
```bash
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "admin_clinica",
  "password": "admin123"
}
```

---

### 👨‍⚕️ **2. ODONTÓLOGO (Clínica Demo)**

```json
{
  "email": "odontologo@clinica-demo.com",
  "password": "password123",
  "tipo_usuario": "ODONTOLOGO",
  "tenant": "clinica-demo"
}
```

**Permisos:**
- ✅ Ver/editar historiales clínicos de sus pacientes
- ✅ Gestionar citas asignadas
- ✅ Crear/editar planes de tratamiento
- ✅ Registrar episodios de atención
- ✅ Ver facturas de sus pacientes
- ❌ NO puede ver pacientes de otros odontólogos

**Endpoints de prueba:**
```bash
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "odontologo1",
  "password": "odonto123"
}

# Ver sus citas
GET http://clinica1.localhost:8000/tenant/api/agenda/citas/
Authorization: Bearer {token}
```

---

### 👩‍💼 **3. RECEPCIONISTA**

```json
{
  "username": "recepcionista1",
  "password": "recep123",
  "email": "recepcion@clinica1.com",
  "tipo_usuario": "recepcionista",
  "nombres": "Ana",
  "apellidos": "López"
}
```

**Permisos:**
- ✅ Gestionar citas (agendar, cancelar, reprogramar)
- ✅ Registrar pagos y facturas
- ✅ Ver información básica de pacientes
- ✅ Gestionar inventario
- ❌ NO puede editar historiales clínicos
- ❌ NO puede crear planes de tratamiento

**Endpoints de prueba:**
```bash
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "recepcionista1",
  "password": "recep123"
}

# Agendar cita
POST http://clinica1.localhost:8000/tenant/api/agenda/citas/
Authorization: Bearer {token}

# Registrar pago
POST http://clinica1.localhost:8000/tenant/api/facturacion/pagos/
Authorization: Bearer {token}
```

---

### 🦷 **4. PACIENTE**

#### **Paciente 1 (Clínica Demo)**

**✅ IMPORTANTE: El login usa EMAIL como usuario**

```json
{
  "email": "paciente1@test.com",     ← ✅ USAR EMAIL PARA LOGIN
  "password": "password123",
  "tipo_usuario": "PACIENTE",
  "tenant": "clinica-demo"
}
```

**Datos del Perfil:**
- Fecha de nacimiento: 1990-05-15
- Teléfono: 0998765432
- Alergias: "Penicilina, Ibuprofeno"
- Enfermedades previas: "Hipertensión controlada"

**Datos de Prueba:**
- ✅ 3 citas registradas (1 pendiente, 1 atendida, 1 cancelada)
- ✅ 1 historial clínico con 2 episodios
- ✅ 1 plan de tratamiento activo (Ortodoncia)
- ✅ 2 facturas (1 pendiente, 1 pagada)

**Endpoints de prueba:**
```bash
# Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# Ver perfil
GET http://clinica1.localhost:8000/tenant/api/usuarios/me/
Authorization: Bearer {token}

# Ver mis citas
GET http://clinica1.localhost:8000/tenant/api/agenda/citas/
Authorization: Bearer {token}

# Ver historial
GET http://clinica1.localhost:8000/tenant/api/historial/historiales/
Authorization: Bearer {token}

# Ver planes
GET http://clinica1.localhost:8000/tenant/api/tratamientos/planes/
Authorization: Bearer {token}

# Ver facturas
GET http://clinica1.localhost:8000/tenant/api/facturacion/facturas/
Authorization: Bearer {token}
```

---

#### **Paciente 2 (Clínica Demo)**

```json
{
  "email": "paciente2@test.com",
  "password": "password123",
  "tipo_usuario": "PACIENTE",
  "tenant": "clinica-demo"
}
```

**Datos del Perfil:**
- Fecha de nacimiento: 1985-08-22
- Teléfono: 0991234567
- Alergias: "Ninguna"
- Enfermedades previas: "Ninguna"

**Datos de Prueba:**
- ✅ 2 citas (1 programada, 1 atendida)
- ✅ 1 historial clínico con 1 episodio
- ✅ 1 plan de tratamiento (Blanqueamiento)
- ✅ 1 factura pagada

---

#### **Paciente 3 (Clínica Demo)**

```json
{
  "email": "paciente3@test.com",
  "password": "password123",
  "tipo_usuario": "PACIENTE",
  "tenant": "clinica-demo"
}
```

**Datos del Perfil:**
- Fecha de nacimiento: 1978-03-10
- Teléfono: 0987654321
- Alergias: "Látex"
- Enfermedades previas: "Diabetes tipo 2"

**Datos de Prueba:**
- ✅ 1 cita pendiente
- ✅ Sin historial clínico aún (paciente nuevo)
- ✅ Sin planes de tratamiento
- ✅ Sin facturas

---

## 🔑 TOKENS JWT

### Estructura del Token

```json
{
  "token_type": "Bearer",
  "exp": 1700000000,
  "iat": 1699996400,
  "jti": "unique-token-id",
  "user_id": 1,
  "username": "juan_perez",
  "tipo_usuario": "paciente"
}
```

### Tiempo de Expiración
- **Access Token:** 60 minutos
- **Refresh Token:** 24 horas

### Cómo Usar el Token

```bash
# En headers de peticiones
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# Renovar token
POST http://clinica1.localhost:8000/public/api/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🧪 ESCENARIOS DE PRUEBA

### **Escenario 1: Login y Dashboard Paciente**
```bash
# 1. Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# 2. Ver perfil
GET http://clinica1.localhost:8000/tenant/api/usuarios/me/
Authorization: Bearer {access_token}

# 3. Dashboard - Ver próximas citas
GET http://clinica1.localhost:8000/tenant/api/agenda/citas/?estado=PROGRAMADA
Authorization: Bearer {access_token}
```

---

### **Escenario 2: Solicitar y Cancelar Cita**
```bash
# 1. Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# 2. Listar odontólogos disponibles
GET http://clinica1.localhost:8000/tenant/api/usuarios/odontologos/
Authorization: Bearer {access_token}

# 3. Solicitar cita
POST http://clinica1.localhost:8000/tenant/api/agenda/citas/
Authorization: Bearer {access_token}
{
  "odontologo": 2,
  "fecha": "2025-11-20",
  "hora": "10:00:00",
  "motivo": "Limpieza dental"
}

# 4. Cancelar cita (usar ID de cita creada)
POST http://clinica1.localhost:8000/tenant/api/agenda/citas/{id}/cancelar/
Authorization: Bearer {access_token}
{
  "motivo_cancelacion": "No puedo asistir"
}
```

---

### **Escenario 3: Ver Historial y Documentos**
```bash
# 1. Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# 2. Ver historial clínico
GET http://clinica1.localhost:8000/tenant/api/historial/historiales/
Authorization: Bearer {access_token}

# 3. Ver documentos clínicos
GET http://clinica1.localhost:8000/tenant/api/historial/documentos/
Authorization: Bearer {access_token}

# 4. Descargar documento (usar ID del documento)
GET http://clinica1.localhost:8000/tenant/api/historial/documentos/{id}/descargar/
Authorization: Bearer {access_token}
```

---

### **Escenario 4: Ver Plan de Tratamiento**
```bash
# 1. Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# 2. Listar planes
GET http://clinica1.localhost:8000/tenant/api/tratamientos/planes/
Authorization: Bearer {access_token}

# 3. Ver detalle de plan (usar ID del plan)
GET http://clinica1.localhost:8000/tenant/api/tratamientos/planes/{id}/
Authorization: Bearer {access_token}
```

---

### **Escenario 5: Ver Facturas y Pagos**
```bash
# 1. Login
POST http://clinica1.localhost:8000/public/api/token/
{
  "username": "juan_perez",
  "password": "paciente123"
}

# 2. Listar facturas
GET http://clinica1.localhost:8000/tenant/api/facturacion/facturas/
Authorization: Bearer {access_token}

# 3. Ver detalle de factura (usar ID de factura)
GET http://clinica1.localhost:8000/tenant/api/facturacion/facturas/{id}/
Authorization: Bearer {access_token}

# 4. Ver pagos de una factura
GET http://clinica1.localhost:8000/tenant/api/facturacion/pagos/?factura={id}
Authorization: Bearer {access_token}
```

---

## 🔒 SEGURIDAD Y PERMISOS

### Validación Automática por Tenant
Todos los endpoints verifican que:
- ✅ Usuario pertenece al tenant correcto
- ✅ Token JWT es válido y no expirado
- ✅ Usuario tiene permisos para la acción
- ✅ Solo ve sus propios datos (pacientes)

### Filtrado Automático
```python
# Pacientes solo ven sus datos
GET /tenant/api/agenda/citas/
→ Retorna solo citas del paciente autenticado

# Odontólogos solo ven sus pacientes
GET /tenant/api/historial/historiales/
→ Retorna solo historiales de pacientes asignados

# Administradores ven todo
GET /tenant/api/usuarios/
→ Retorna todos los usuarios del tenant
```

---

## 🐛 TROUBLESHOOTING

### Error: "Authentication credentials were not provided"
```bash
# Solución: Agregar token en header
Authorization: Bearer {access_token}
```

### Error: "Token is invalid or expired"
```bash
# Solución: Renovar token
POST http://clinica1.localhost:8000/public/api/token/refresh/
{
  "refresh": "{refresh_token}"
}
```

### Error: "You do not have permission to perform this action"
```bash
# Solución: Verificar que:
# 1. Usuario tiene el rol correcto
# 2. Está accediendo a sus propios recursos
# 3. Endpoint permite ese tipo de usuario
```

### Error: "Not found"
```bash
# Solución: Verificar que:
# 1. URL incluye subdomain correcto (clinica1.localhost:8000)
# 2. ID del recurso existe y pertenece al usuario
# 3. Usuario tiene permiso para ver ese recurso
```

---

## 📝 COMANDOS ÚTILES

### Crear Usuarios de Prueba
```bash
# Ejecutar script de población
python manage.py shell < poblar_sistema_completo.py

# O crear manualmente
python manage.py create_tenant_superuser --schema=clinica1
```

### Ver Usuarios Existentes
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all()
```

### Resetear Contraseña
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='juan_perez')
>>> user.set_password('paciente123')
>>> user.save()
```

---

## 🚀 INICIO RÁPIDO

### 1. Levantar el servidor
```bash
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO\ClinicaDental-backend2"
python manage.py runserver
```

### 2. Probar login en navegador
```
http://clinica1.localhost:8000/public/api/token/
```

### 3. Usar VSCode REST Client
Abrir archivo: `pruebas_http/00_autenticacion.http`

---

## 📊 RESUMEN DE CREDENCIALES

| Rol | Username | Password | Email |
|-----|----------|----------|-------|
| Administrador | admin_clinica | admin123 | admin@clinica1.com |
| Odontólogo | odontologo1 | odonto123 | odontologo@clinica1.com |
| Recepcionista | recepcionista1 | recep123 | recepcion@clinica1.com |
| Paciente 1 | juan_perez | paciente123 | juan.perez@email.com |
| Paciente 2 | maria_gonzalez | paciente123 | maria.gonzalez@email.com |
| Paciente 3 | pedro_rodriguez | paciente123 | pedro.rodriguez@email.com |

---

**🔐 IMPORTANTE:** Estas credenciales son SOLO para desarrollo y pruebas. En producción usar contraseñas seguras y encriptadas.

**📅 Última actualización:** 15 de Noviembre, 2025
