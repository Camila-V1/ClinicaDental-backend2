# 📋 ENDPOINTS COMPLETOS - CLÍNICA DENTAL API

## 🌐 URLs Base

- **Backend**: `https://clinica-dental-backend.onrender.com`
- **Frontend**: `https://dentaabcxy.store` o `https://www.dentaabcxy.store`

---

## 🔐 AUTENTICACIÓN (JWT)

### Login
```http
POST /api/token/
Content-Type: application/json

{
  "email": "odontologo@clinica-demo.com",
  "password": "odontologo123"
}
```

**Respuesta:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 👥 USUARIOS (`/api/usuarios/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/register/` | Registro de nuevo paciente |
| GET | `/me/` | Obtener información del usuario actual (requiere token) |
| GET | `/pacientes/` | Listar pacientes (para selects en formularios) |
| GET | `/odontologos/` | Listar odontólogos (para agendar citas) |
| GET | `/health/` | Health check del módulo usuarios |

### Ejemplos:

**Obtener usuario actual:**
```http
GET /api/usuarios/me/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Listar odontólogos:**
```http
GET /api/usuarios/odontologos/
Authorization: Bearer <token>
```

---

## 📅 AGENDA (`/api/agenda/`)

### Endpoints CRUD de Citas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/citas/` | Listar todas las citas |
| POST | `/citas/` | Crear nueva cita |
| GET | `/citas/{id}/` | Detalle de una cita |
| PUT | `/citas/{id}/` | Actualizar cita completa |
| PATCH | `/citas/{id}/` | Actualizar parcialmente |
| DELETE | `/citas/{id}/` | Eliminar cita |

### Endpoints Personalizados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/citas/proximas/` | Citas futuras |
| GET | `/citas/hoy/` | Citas de hoy |
| POST | `/citas/{id}/confirmar/` | Confirmar cita |
| POST | `/citas/{id}/cancelar/` | Cancelar cita |
| POST | `/citas/{id}/atender/` | Marcar como atendida |

---

## 🏥 HISTORIAL CLÍNICO (`/api/historial/`)

### Historiales
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/historiales/` | Listar historiales |
| POST | `/historiales/` | Crear historial |
| GET | `/historiales/{id}/` | Detalle |
| PUT/PATCH | `/historiales/{id}/` | Actualizar |
| DELETE | `/historiales/{id}/` | Eliminar |

### Episodios de Atención
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/episodios/` | Listar episodios |
| POST | `/episodios/` | Crear episodio |
| GET | `/episodios/{id}/` | Detalle |
| PUT/PATCH | `/episodios/{id}/` | Actualizar |

### Odontogramas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/odontogramas/` | Listar odontogramas |
| POST | `/odontogramas/` | Crear odontograma |
| GET | `/odontogramas/{id}/` | Detalle |
| PUT/PATCH | `/odontogramas/{id}/` | Actualizar |

### Documentos Clínicos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/documentos/` | Listar documentos |
| POST | `/documentos/` | Subir documento |
| GET | `/documentos/{id}/` | Detalle |
| DELETE | `/documentos/{id}/` | Eliminar |

---

## 💊 TRATAMIENTOS (`/api/tratamientos/`)

### Categorías de Servicios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/categorias/` | Listar categorías |
| POST | `/categorias/` | Crear categoría |
| GET | `/categorias/{id}/` | Detalle |
| PUT/PATCH | `/categorias/{id}/` | Actualizar |

### Servicios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/servicios/` | Listar servicios |
| POST | `/servicios/` | Crear servicio |
| GET | `/servicios/{id}/` | Detalle |
| PUT/PATCH | `/servicios/{id}/` | Actualizar |

### Planes de Tratamiento
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/planes/` | Listar planes |
| POST | `/planes/` | Crear plan |
| GET | `/planes/{id}/` | Detalle |
| PUT/PATCH | `/planes/{id}/` | Actualizar |
| DELETE | `/planes/{id}/` | Eliminar |

### Items de Plan
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/items/` | Listar items |
| POST | `/items/` | Crear item |
| GET | `/items/{id}/` | Detalle |
| PUT/PATCH | `/items/{id}/` | Actualizar |

### Presupuestos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/presupuestos/` | Listar presupuestos |
| GET | `/presupuestos/{id}/` | Detalle de presupuesto |

---

## 💰 FACTURACIÓN (`/api/facturacion/`)

### Facturas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/facturas/` | Listar facturas |
| POST | `/facturas/` | Crear factura desde presupuesto |
| GET | `/facturas/{id}/` | Detalle |
| PUT/PATCH | `/facturas/{id}/` | Actualizar |
| DELETE | `/facturas/{id}/` | Eliminar |
| POST | `/facturas/{id}/marcar-pagada/` | Marcar como pagada |
| POST | `/facturas/{id}/cancelar/` | Cancelar factura |
| GET | `/facturas/reporte-financiero/` | Reporte financiero |

### Pagos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/pagos/` | Listar pagos |
| POST | `/pagos/` | Registrar pago |
| GET | `/pagos/{id}/` | Detalle |
| PUT/PATCH | `/pagos/{id}/` | Actualizar |
| POST | `/pagos/{id}/anular/` | Anular pago |
| GET | `/pagos/por-factura/?factura_id={id}` | Pagos de una factura |

---

## 📦 INVENTARIO (`/api/inventario/`)

### Categorías de Insumos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/categorias/` | Listar categorías |
| POST | `/categorias/` | Crear categoría |
| GET | `/categorias/{id}/` | Detalle |
| PUT/PATCH | `/categorias/{id}/` | Actualizar |

### Insumos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/insumos/` | Listar insumos |
| POST | `/insumos/` | Crear insumo |
| GET | `/insumos/{id}/` | Detalle |
| PUT/PATCH | `/insumos/{id}/` | Actualizar |
| GET | `/insumos/bajo_stock/` | Insumos con stock bajo |
| POST | `/insumos/{id}/ajustar_stock/` | Ajustar stock |

---

## 📊 REPORTES (`/api/reportes/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard-kpis/` | KPIs del dashboard |
| GET | `/estadisticas-generales/` | Estadísticas completas |
| GET | `/tendencia-citas/?dias=15` | Gráfico de citas por día |
| GET | `/top-procedimientos/?limite=5` | Procedimientos más realizados |
| GET | `/ocupacion-odontologos/?mes=2025-11` | Tasa de ocupación |
| GET | `/reporte-financiero/?periodo=2025-11` | Reporte financiero |

### Ejemplo: Dashboard KPIs
```http
GET /api/reportes/dashboard-kpis/
Authorization: Bearer <token>
```

**Respuesta:**
```json
[
  {"etiqueta": "Pacientes Activos", "valor": 150},
  {"etiqueta": "Citas Hoy", "valor": 8},
  {"etiqueta": "Ingresos Este Mes", "valor": 25000.00},
  {"etiqueta": "Saldo Pendiente", "valor": 5000.00}
]
```

---

## 🔑 CREDENCIALES DE PRUEBA

### Odontólogo
```
Email: odontologo@clinica-demo.com
Password: odontologo123
```

### Pacientes
```
Email: paciente1@test.com hasta paciente5@test.com
Password: paciente123
```

---

## 🛠️ CONFIGURACIÓN TÉCNICA

### Arquitectura Multi-Tenant
- **Middleware**: `DefaultTenantMiddleware` redirige automáticamente requests de `/api/*` al tenant `clinica_demo`
- **Schema**: Usa PostgreSQL con schemas separados (public + clinica_demo)
- **Dominio público**: Acceso sin subdomain → `clinica-dental-backend.onrender.com`

### Headers Requeridos

**Para todos los endpoints autenticados:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### CORS Configurado
- ✅ `https://dentaabcxy.store`
- ✅ `https://www.dentaabcxy.store`
- ✅ `https://*.vercel.app`
- ✅ `https://*.onrender.com`
- ✅ `http://localhost:5173` (desarrollo)

---

## 🚀 FLUJO DE AUTENTICACIÓN

1. **Login**: `POST /api/token/` → Recibe `access` y `refresh` tokens
2. **Obtener usuario**: `GET /api/usuarios/me/` con header `Authorization: Bearer <access>`
3. **Usar API**: Incluir `Authorization: Bearer <access>` en todos los requests
4. **Refresh**: Cuando expire el access token, usar `POST /api/token/refresh/`

---

## ⚙️ PERMISOS POR ROL

### Admin
- Acceso completo a todos los endpoints del tenant

### Odontólogo
- Ve solo datos de sus propios pacientes
- Puede gestionar citas, tratamientos, historial clínico

### Paciente
- Solo ve sus propios datos
- Puede ver citas, facturas, historial

---

## 📝 NOTAS IMPORTANTES

1. **Todos los endpoints requieren autenticación JWT** excepto:
   - `POST /api/token/` (Login)
   - `POST /api/token/refresh/` (Refresh)
   - `POST /api/usuarios/register/` (Registro de paciente)

2. **Rutas simplificadas**: Todos los endpoints usan el prefijo `/api/` sin versionamiento

3. **Tenant automático**: El middleware redirige automáticamente al tenant `clinica_demo`

4. **Formato de respuesta**: Todas las respuestas son JSON

5. **Códigos de estado**:
   - `200 OK` - Éxito
   - `201 Created` - Recurso creado
   - `400 Bad Request` - Error en los datos
   - `401 Unauthorized` - No autenticado
   - `403 Forbidden` - Sin permisos
   - `404 Not Found` - Recurso no encontrado
   - `500 Internal Server Error` - Error del servidor

---

✅ **ESTADO**: Todos los endpoints configurados y funcionando
