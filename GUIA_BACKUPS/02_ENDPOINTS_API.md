# 🔌 ENDPOINTS DE LA API DE BACKUPS

## 📍 Base URL

```
Producción: https://tu-app.onrender.com
Local:      http://clinicademo1.localhost:8000
```

**Todos los endpoints requieren:**
- `Authorization: Bearer <token>`
- `x-tenant-id: <id_del_tenant>` (el frontend ya lo maneja)

---

## 1️⃣ Listar Historial de Backups

### GET `/api/backups/history/`

**Descripción:** Obtiene la lista de todos los backups del tenant actual.

**Permisos:** Usuario autenticado

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-tenant-id: 1
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 3,
    "file_name": "backup-sql-clinica_demo-2025-11-27-143052.sql",
    "file_path": "clinica_demo/backup-sql-clinica_demo-2025-11-27-143052.sql",
    "file_size": 2457600,
    "file_size_mb": 2.34,
    "backup_type": "manual",
    "created_by": {
      "id": 5,
      "email": "admin@clinicademo1.com",
      "nombre": "Administrador"
    },
    "created_at": "2025-11-27T14:30:52.123456Z"
  },
  {
    "id": 2,
    "file_name": "backup-sql-clinica_demo-2025-11-27-100000.sql",
    "file_path": "clinica_demo/backup-sql-clinica_demo-2025-11-27-100000.sql",
    "file_size": 2450000,
    "file_size_mb": 2.33,
    "backup_type": "automatic",
    "created_by": null,
    "created_at": "2025-11-27T10:00:00.000000Z"
  },
  {
    "id": 1,
    "file_name": "backup-sql-clinica_demo-2025-11-26-230000.sql",
    "file_path": "clinica_demo/backup-sql-clinica_demo-2025-11-26-230000.sql",
    "file_size": 2400000,
    "file_size_mb": 2.29,
    "backup_type": "manual",
    "created_by": {
      "id": 5,
      "email": "admin@clinicademo1.com",
      "nombre": "Administrador"
    },
    "created_at": "2025-11-26T23:00:00.000000Z"
  }
]
```

**Respuesta sin backups (200):**
```json
[]
```

**Errores comunes:**
```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden (si el token expiró)
{
  "detail": "Given token not valid for any token type"
}
```

---

## 2️⃣ Crear Backup Manual

### POST `/api/backups/create/`

**Descripción:** Crea un backup manual de la base de datos del tenant actual.

**Permisos:** Solo ADMIN

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-tenant-id: 1
Content-Type: application/json
```

**Query Params (opcional):**
```
?download=true  → Descarga el archivo directamente en lugar de devolver JSON
```

**Sin download (default):**

**Respuesta exitosa (201):**
```json
{
  "message": "Backup creado y subido a Supabase exitosamente",
  "backup_info": {
    "id": 4,
    "file_name": "backup-sql-clinica_demo-2025-11-27-153045.sql",
    "file_path": "clinica_demo/backup-sql-clinica_demo-2025-11-27-153045.sql",
    "file_size": 2460000,
    "file_size_mb": 2.35,
    "backup_type": "manual",
    "created_by": {
      "id": 5,
      "email": "admin@clinicademo1.com",
      "nombre": "Administrador"
    },
    "created_at": "2025-11-27T15:30:45.123456Z"
  }
}
```

**Con ?download=true:**

Devuelve el archivo directamente:
```http
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="backup-sql-clinica_demo-2025-11-27-153045.sql"

[binary data del archivo SQL]
```

**Errores:**
```json
// 403 Forbidden (no es admin)
{
  "error": "Solo los administradores pueden crear backups"
}

// 400 Bad Request
{
  "error": "No se pueden crear backups del schema public"
}

// 500 Internal Server Error
{
  "error": "Error al crear backup: [detalle del error]"
}
```

---

## 3️⃣ Descargar Backup

### GET `/api/backups/history/{id}/download/`

**Descripción:** Descarga un archivo de backup específico.

**Permisos:** Usuario autenticado

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-tenant-id: 1
```

**Ejemplo:**
```http
GET /api/backups/history/3/download/
```

**Respuesta exitosa (200):**
```http
Content-Type: application/sql
Content-Disposition: attachment; filename="backup-sql-clinica_demo-2025-11-27-143052.sql"

[binary data del archivo SQL]
```

**Errores:**
```json
// 404 Not Found
{
  "error": "Backup no encontrado"
}

// 500 Internal Server Error
{
  "error": "Error al descargar backup: [detalle del error]"
}
```

---

## 4️⃣ Eliminar Backup

### DELETE `/api/backups/history/{id}/`

**Descripción:** Elimina un backup (archivo + registro en BD).

**Permisos:** Solo ADMIN

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-tenant-id: 1
```

**Ejemplo:**
```http
DELETE /api/backups/history/3/
```

**Respuesta exitosa (204):**
```json
{
  "message": "Backup eliminado exitosamente"
}
```

**Errores:**
```json
// 403 Forbidden (no es admin)
{
  "error": "Solo los administradores pueden eliminar backups"
}

// 404 Not Found
{
  "error": "Backup no encontrado"
}

// 500 Internal Server Error
{
  "error": "Error al eliminar backup: [detalle del error]"
}
```

---

## 📊 Ejemplo Completo: Flujo de Uso

### 1. Listar backups existentes
```bash
curl -X GET "https://tu-app.onrender.com/api/backups/history/" \
  -H "Authorization: Bearer <token>" \
  -H "x-tenant-id: 1"
```

### 2. Crear nuevo backup
```bash
curl -X POST "https://tu-app.onrender.com/api/backups/create/" \
  -H "Authorization: Bearer <token>" \
  -H "x-tenant-id: 1" \
  -H "Content-Type: application/json"
```

### 3. Descargar backup específico
```bash
curl -X GET "https://tu-app.onrender.com/api/backups/history/3/download/" \
  -H "Authorization: Bearer <token>" \
  -H "x-tenant-id: 1" \
  --output backup.sql
```

### 4. Eliminar backup antiguo
```bash
curl -X DELETE "https://tu-app.onrender.com/api/backups/history/1/" \
  -H "Authorization: Bearer <token>" \
  -H "x-tenant-id: 1"
```

---

## ⚡ Códigos de Estado HTTP

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Lista obtenida o descarga exitosa |
| 201 | Created | Backup creado exitosamente |
| 204 | No Content | Backup eliminado exitosamente |
| 400 | Bad Request | Parámetros inválidos |
| 401 | Unauthorized | Token no proporcionado o inválido |
| 403 | Forbidden | Sin permisos (no es ADMIN) |
| 404 | Not Found | Backup no existe |
| 500 | Internal Server Error | Error del servidor |

---

## 🧪 Testing con curl

### Obtener token primero:
```bash
TOKEN=$(curl -X POST "https://tu-app.onrender.com/api/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinicademo1.com",
    "password": "admin123"
  }' | jq -r '.access')

TENANT_ID=1
```

### Listar backups:
```bash
curl -X GET "https://tu-app.onrender.com/api/backups/history/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-tenant-id: $TENANT_ID" \
  | jq
```

### Crear backup:
```bash
curl -X POST "https://tu-app.onrender.com/api/backups/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-tenant-id: $TENANT_ID" \
  | jq
```

---

## 📝 Notas Importantes

1. **Multi-tenant:** Cada clínica solo ve sus propios backups
2. **Permisos:** Solo ADMINs pueden crear/eliminar backups
3. **Tamaño:** Los archivos pueden ser grandes (2-10 MB típicamente)
4. **Formato:** SQL (preferido) o JSON (fallback)
5. **Storage:** Los archivos se almacenan en Supabase, no en el servidor

---

**Siguiente:** [06_SERVICIOS_AXIOS.md](06_SERVICIOS_AXIOS.md) - Implementación en el frontend
