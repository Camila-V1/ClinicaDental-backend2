# 🏥 Sistema de Registro Multi-Tenant con Planes de Suscripción

## 📋 Descripción General

Este sistema permite que nuevas clínicas se registren públicamente (sin necesidad de subdominio) y seleccionen un plan de suscripción basado en tiempo. El proceso incluye:

1. **Formulario público** de registro
2. **Selección de plan** (Prueba, Mensual, Trimestral, Semestral, Anual)
3. **Revisión por admin** (aprobar/rechazar)
4. **Creación automática** de tenant (clínica + dominio + schema)
5. **Notificaciones por email**

---

## 🗄️ Modelos Creados

### 1. PlanSuscripcion
Planes de suscripción disponibles para las clínicas.

```python
Campos:
- nombre: Nombre del plan
- tipo: PRUEBA, MENSUAL, TRIMESTRAL, SEMESTRAL, ANUAL
- descripcion: Descripción del plan
- precio: Precio en USD (Decimal)
- duracion_dias: Duración del plan en días
- max_usuarios: Máximo de usuarios permitidos
- max_pacientes: Máximo de pacientes permitidos
- max_almacenamiento_mb: Almacenamiento máximo
- permite_reportes: ¿Permite generar reportes?
- permite_integraciones: ¿Permite integraciones?
- soporte_prioritario: ¿Tiene soporte prioritario?
- activo: Plan activo/inactivo
```

**Planes predefinidos:**
- 🎁 **Plan Prueba**: $0.00 - 7 días (5 usuarios, 50 pacientes)
- 📅 **Plan Mensual**: $49.99 - 30 días (10 usuarios, 500 pacientes)
- 📆 **Plan Trimestral**: $134.97 - 90 días (15 usuarios, 1000 pacientes) - 10% descuento
- 📊 **Plan Semestral**: $254.95 - 180 días (20 usuarios, 2000 pacientes) - 15% descuento
- 🏆 **Plan Anual**: $479.90 - 365 días (30 usuarios, 5000 pacientes) - 20% descuento

### 2. Clinica (Enhanced)
Modelo de tenant mejorado con campos de suscripción.

```python
Nuevos campos agregados:
- email_admin: Email del administrador
- telefono: Teléfono de contacto
- direccion: Dirección física
- ciudad: Ciudad
- pais: País
- plan: FK a PlanSuscripcion
- estado: PENDIENTE, ACTIVA, SUSPENDIDA, CANCELADA
- fecha_inicio: Inicio de suscripción
- fecha_expiracion: Expiración de suscripción
- notas: Notas administrativas
```

**Métodos:**
- `esta_activa` (property): Verifica si está activa y no expirada
- `dias_restantes` (property): Calcula días restantes de suscripción
- `activar_plan(plan)`: Activa el plan y establece fechas
- `renovar_suscripcion()`: Extiende la suscripción por la duración del plan
- `suspender(motivo)`: Suspende la clínica con un motivo

### 3. SolicitudRegistro (NEW)
Solicitudes de registro de nuevas clínicas (vive en schema público).

```python
Campos:
- nombre_clinica: Nombre de la clínica a crear
- dominio_deseado: Subdominio deseado (ej: "miclinica")
- nombre_contacto: Nombre de la persona de contacto
- email: Email de contacto
- telefono: Teléfono
- cargo: Cargo de la persona
- direccion, ciudad, pais: Ubicación
- plan_solicitado: FK a PlanSuscripcion
- estado: PENDIENTE, APROBADA, RECHAZADA, PROCESADA
- motivo_rechazo: Motivo si fue rechazada
- clinica_creada: FK a Clinica (cuando se procesa)
- creada, revisada, procesada: Timestamps
```

**Validaciones:**
- `dominio_deseado`: Solo alfanumérico y guiones, sin guiones al inicio/final
- `email`: No permite solicitudes duplicadas activas
- Verifica unicidad de dominio contra clínicas existentes

---

## 🔌 API Endpoints

### Endpoints Públicos (sin autenticación)

#### 1. Listar Planes Disponibles
```http
GET /api/planes/

Response:
[
  {
    "id": 1,
    "nombre": "Plan Mensual",
    "tipo": "MENSUAL",
    "tipo_display": "Mensual",
    "descripcion": "...",
    "precio": "49.99",
    "duracion_dias": 30,
    "max_usuarios": 10,
    "max_pacientes": 500
  },
  ...
]
```

#### 2. Información del Proceso de Registro
```http
GET /api/registro/info/

Response:
{
  "mensaje": "Bienvenido al sistema de registro de clínicas",
  "pasos": [
    "1. Selecciona un plan de suscripción",
    "2. Completa el formulario de registro",
    ...
  ],
  "planes_disponibles": [...],
  "contacto": {
    "email": "contacto@clinica.com",
    "mensaje": "Para más información, contáctanos"
  }
}
```

#### 3. Crear Solicitud de Registro
```http
POST /api/solicitudes/

Request:
{
  "nombre_clinica": "Mi Clínica Dental",
  "dominio_deseado": "miclinica",
  "nombre_contacto": "Juan Pérez",
  "email": "juan@email.com",
  "telefono": "+1234567890",
  "cargo": "Director",
  "direccion": "Calle 123",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "plan_solicitado": 2  // ID del plan
}

Response:
{
  "message": "Solicitud enviada exitosamente. Te contactaremos pronto.",
  "solicitud": {
    "id": 1,
    "nombre_clinica": "Mi Clínica Dental",
    "dominio_deseado": "miclinica",
    "estado": "PENDIENTE",
    "plan_info": {
      "nombre": "Plan Mensual",
      "precio": "49.99"
    },
    ...
  }
}
```

### Endpoints de Admin (requieren autenticación de admin)

#### 4. Listar Solicitudes
```http
GET /api/solicitudes/
Authorization: Bearer <admin_token>
```

#### 5. Aprobar Solicitud
```http
POST /api/solicitudes/{id}/aprobar/
Authorization: Bearer <admin_token>

Response:
{
  "message": "Solicitud aprobada y clínica creada exitosamente",
  "clinica": {
    "nombre": "Mi Clínica Dental",
    "dominio": "miclinica",
    "schema_name": "tenant_miclinica",
    ...
  }
}
```

#### 6. Rechazar Solicitud
```http
POST /api/solicitudes/{id}/rechazar/
Authorization: Bearer <admin_token>

Request:
{
  "motivo": "Información incompleta"
}

Response:
{
  "message": "Solicitud rechazada",
  "solicitud": {...}
}
```

---

## 🎯 Workflow Completo

### Paso 1: Usuario Solicita Registro
```
Usuario → Formulario Web/App → POST /api/solicitudes/
```

El sistema:
1. Valida dominio (alfanumérico, no duplicado)
2. Valida email (no solicitudes duplicadas)
3. Crea SolicitudRegistro con estado PENDIENTE
4. Envía email de confirmación al solicitante
5. Notifica a los administradores

### Paso 2: Admin Revisa Solicitud
```
Admin → Panel Admin (/admin/) → Revisa SolicitudRegistro
```

Opciones:
- **Aprobar**: Crea automáticamente Clinica + Domain + Schema
- **Rechazar**: Marca como rechazada y especifica motivo

### Paso 3: Creación Automática de Tenant (si se aprueba)

Cuando el admin aprueba:

```python
# Se crea automáticamente:
1. Clinica (Tenant)
   - schema_name: "tenant_miclinica"
   - nombre: "Mi Clínica Dental"
   - dominio: "miclinica"
   - plan: Plan seleccionado
   - estado: "PENDIENTE" (cambiar a ACTIVA cuando paguen)
   - email_admin, telefono, etc.

2. Domain(s)
   - Desarrollo: "miclinica.localhost"
   - Producción: "miclinica.tudominio.com"

3. Schema PostgreSQL
   - Se crea automáticamente por django-tenants
   - Se ejecutan migraciones del tenant
```

### Paso 4: Notificación al Usuario

El usuario recibe email con:
- URL de acceso: `miclinica.tudominio.com`
- Email de acceso
- Instrucciones para pago y activación

---

## 🎨 Panel de Administración

### Modelos Registrados en Public Admin

#### 1. Planes de Suscripción
- **Lista**: nombre, tipo, precio, duración, límites, activo
- **Filtros**: tipo, activo
- **Búsqueda**: nombre, descripción
- **Edición**: Todos los campos del plan

#### 2. Solicitudes de Registro
- **Lista**: nombre_clinica, dominio, contacto, email, plan, estado, fechas
- **Filtros**: estado, plan, país, fecha de creación
- **Búsqueda**: nombre_clinica, dominio, email, contacto
- **Acciones**:
  - ✅ **Aprobar solicitudes**: Crea clínica automáticamente
  - ❌ **Rechazar solicitudes**: Marca como rechazada
- **Campos readonly**: creada, revisada, procesada, clinica_creada

#### 3. Clínicas
- **Lista**: nombre, dominio, plan, estado, activa, días restantes, fechas
- **Filtros**: estado, plan, activo, ciudad, país
- **Búsqueda**: nombre, dominio, email_admin, ciudad
- **Acciones**:
  - 🚀 **Activar plan**: Activa el plan de suscripción
  - 🔄 **Renovar suscripción**: Extiende por la duración del plan
  - ⏸️ **Suspender**: Suspende la clínica
- **Properties visualizadas**: esta_activa, dias_restantes

#### 4. Dominios
- **Lista**: domain, tenant, is_primary
- **Filtros**: is_primary
- **Búsqueda**: domain, tenant__nombre

---

## 📧 Sistema de Emails

### Email 1: Confirmación de Solicitud
**Trigger**: Usuario crea solicitud  
**Destinatario**: Solicitante  
**Contenido**:
```
Hola {nombre_contacto},

Hemos recibido tu solicitud para crear la clínica "{nombre_clinica}".

Detalles:
- Dominio: {dominio_deseado}
- Plan: {plan.nombre}
- Email: {email}

Nuestro equipo revisará tu solicitud pronto.
```

### Email 2: Notificación a Admins
**Trigger**: Usuario crea solicitud  
**Destinatario**: Administradores  
**Contenido**:
```
Nueva solicitud de registro:

Clínica: {nombre_clinica}
Dominio: {dominio_deseado}
Contacto: {nombre_contacto}
Email: {email}
Plan: {plan.nombre}

Revisa en: {url_admin}
```

### Email 3: Solicitud Aprobada
**Trigger**: Admin aprueba solicitud  
**Destinatario**: Solicitante  
**Contenido**:
```
¡Buenas noticias! Tu solicitud ha sido aprobada.

Clínica: {nombre_clinica}
URL: {dominio}.{host}
Email: {email}

Próximo paso: Activar plan "{plan.nombre}" por ${plan.precio}
```

### Email 4: Solicitud Rechazada
**Trigger**: Admin rechaza solicitud  
**Destinatario**: Solicitante  
**Contenido**:
```
Tu solicitud para "{nombre_clinica}" no ha sido aprobada.

Motivo: {motivo_rechazo}

Contáctanos para más información.
```

---

## 🔐 Seguridad y Validaciones

### Validaciones de Dominio
```python
- Regex: ^[a-z0-9-]+$
- No guiones al inicio/final
- Unicidad contra:
  - Clinica.dominio (existentes)
  - SolicitudRegistro.dominio_deseado (pendientes)
```

### Validaciones de Email
```python
- Formato válido de email
- No solicitudes activas duplicadas del mismo email
```

### Permisos de API
```python
- Planes: AllowAny (público)
- Solicitudes POST: AllowAny (público)
- Solicitudes GET/LIST: IsAdminUser
- Aprobar/Rechazar: IsAdminUser
```

### Admin Panel
```python
- Sin autenticación en desarrollo (PublicAdminSite)
- En producción: Usar HTTP Basic Auth o VPN
```

---

## 🚀 Uso desde Frontend

### Ejemplo: Flutter/React - Formulario de Registro

```dart
// 1. Obtener planes disponibles
final planes = await http.get('${baseUrl}/api/planes/');

// 2. Mostrar formulario con selección de plan

// 3. Enviar solicitud
final response = await http.post(
  '${baseUrl}/api/solicitudes/',
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'nombre_clinica': 'Mi Clínica',
    'dominio_deseado': 'miclinica',
    'nombre_contacto': 'Juan Pérez',
    'email': 'juan@email.com',
    'telefono': '+1234567890',
    'cargo': 'Director',
    'ciudad': 'Bogotá',
    'pais': 'Colombia',
    'plan_solicitado': selectedPlanId,
  }),
);

// 4. Mostrar confirmación
if (response.statusCode == 201) {
  // Solicitud enviada exitosamente
  showDialog('¡Solicitud enviada! Te contactaremos pronto.');
}
```

---

## 📝 Configuración Requerida

### settings.py
```python
# Email configuration (para notificaciones)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password'
DEFAULT_FROM_EMAIL = 'noreply@tudominio.com'

ADMINS = [
    ('Admin Name', 'admin@email.com'),
]

# Para dominios de producción
RENDER_EXTERNAL_HOSTNAME = 'tudominio.com'  # Sin www
```

### urls_public.py
```python
# Ya incluido:
path('api/tenants/', include('tenants.urls')),
```

---

## 🧪 Testing

### Probar Endpoint de Planes
```bash
curl http://localhost:8000/api/planes/
```

### Probar Registro de Solicitud
```bash
curl -X POST http://localhost:8000/api/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_clinica": "Test Clínica",
    "dominio_deseado": "testclinica",
    "nombre_contacto": "Juan Test",
    "email": "test@example.com",
    "telefono": "123456789",
    "cargo": "Director",
    "ciudad": "Test City",
    "pais": "Test Country",
    "plan_solicitado": 2
  }'
```

### Verificar Solicitud en Admin
1. Ir a: http://localhost:8000/admin/
2. Click en "Solicitudes de Registro"
3. Ver la solicitud pendiente
4. Usar acción "Aprobar solicitudes"
5. Verificar que se creó la clínica en "Clínicas"

---

## 📊 Migración Ejecutada

```bash
python manage.py makemigrations tenants
python manage.py migrate tenants

# Resultado:
# + Create model PlanSuscripcion
# + Add field actualizado to clinica
# + Add field ciudad to clinica
# + Add field email_admin to clinica
# + Add field estado to clinica
# + Add field plan to clinica
# + Create model SolicitudRegistro
```

---

## ✅ Checklist de Implementación

- [x] Modelos creados (PlanSuscripcion, Clinica enhanced, SolicitudRegistro)
- [x] Serializers con validaciones
- [x] Views y ViewSets con permisos
- [x] URLs configuradas
- [x] Admin panel con acciones personalizadas
- [x] Migración creada y aplicada
- [x] Planes de suscripción poblados
- [x] Sistema de emails implementado
- [x] Validaciones de dominio y email
- [x] Workflow de aprobación/rechazo
- [x] Creación automática de tenant

---

## 🎉 Resultado Final

Ahora tienes un sistema completo de registro multi-tenant que permite:

1. ✨ **Usuarios** pueden registrarse públicamente sin subdominios
2. 💰 **Seleccionar planes** con precios y límites claros
3. 📧 **Recibir confirmaciones** automáticas por email
4. 👨‍💼 **Admins** pueden aprobar/rechazar desde panel
5. 🏥 **Clínicas** se crean automáticamente con su schema
6. 🔒 **Control de suscripciones** con fechas y estados
7. 📱 **Compatible** con apps móviles y web

¡Sistema listo para producción! 🚀
