# 🔄 Sistema de Backups Automáticos - Clínica Dental

Sistema completo de backups automáticos con almacenamiento en **Supabase Storage** para arquitectura multi-tenant con `django-tenants`.

---

## ✅ **IMPLEMENTACIÓN COMPLETADA**

### **Archivos Creados:**

```
backups/
├── __init__.py
├── apps.py
├── admin.py
├── models.py                    # Modelo BackupRecord
├── serializers.py               # BackupRecordSerializer
├── views.py                     # CreateBackupView, BackupHistoryListView, etc.
├── urls.py                      # Rutas API
├── supabase_storage.py          # Upload/download a Supabase
├── management/
│   └── commands/
│       └── run_scheduled_backups.py  # Comando para backups automáticos
└── migrations/
    └── 0001_initial.py
```

### **Modificaciones:**

- ✅ `tenants/models.py` - Agregados 6 campos de configuración de backups a `Clinica`
- ✅ `core/settings.py` - Agregadas variables `SUPABASE_URL` y `SUPABASE_KEY`
- ✅ `core/urls_tenant.py` - Registradas rutas `api/backups/`
- ✅ `.env` - Credenciales de Supabase configuradas

### **Migraciones Aplicadas:**

- ✅ `backups.0001_initial` - Modelo BackupRecord
- ✅ `tenants.0003_*` - Campos de configuración en Clinica

---

## 📋 **CONFIGURACIÓN DE BACKUPS**

### **Opciones de Programación:**

| Opción | Descripción | Configuración Adicional |
|--------|-------------|------------------------|
| `disabled` | Backups desactivados | - |
| `daily` | Diario a una hora específica | `backup_time` (ej: 02:00 AM) |
| `every_12h` | Cada 12 horas desde hora base | `backup_time` (hora base) |
| `every_6h` | Cada 6 horas desde hora base | `backup_time` (hora base) |
| `weekly` | Semanal en día y hora específica | `backup_weekday` (0-6), `backup_time` |
| `monthly` | Mensual en día y hora específica | `backup_day_of_month` (1-28), `backup_time` |
| `scheduled` | Fecha y hora única | `next_scheduled_backup` (datetime) |

### **Campos del Modelo Clinica:**

```python
backup_schedule = 'daily'           # Tipo de programación
backup_time = '02:00:00'            # Hora específica (HH:MM:SS)
backup_weekday = 6                  # Día de la semana (0=Lun, 6=Dom)
backup_day_of_month = 1             # Día del mes (1-28)
last_backup_at = datetime(...)      # Último backup exitoso
next_scheduled_backup = datetime()  # Solo para 'scheduled'
```

---

## 🚀 **USO DEL SISTEMA**

### **1. Crear Backup Manual**

```http
POST /api/backups/create/
Authorization: Bearer <token_admin>

Response:
{
  "message": "Backup creado y subido a Supabase exitosamente",
  "backup_info": {
    "id": 15,
    "file_name": "backup-sql-clinica_demo-2025-11-26-140530.sql",
    "file_size": 524288,
    "file_size_mb": 0.5,
    "backup_type": "manual",
    "created_by": {
      "id": 2,
      "email": "admin@clinica.com",
      "nombre": "Juan Admin"
    },
    "created_at": "2025-11-26T14:05:30Z"
  }
}
```

**Con descarga directa:**
```http
POST /api/backups/create/?download=true
Authorization: Bearer <token_admin>

Response: Archivo .sql para descarga
```

### **2. Ver Historial de Backups**

```http
GET /api/backups/history/
Authorization: Bearer <token>

Response:
[
  {
    "id": 15,
    "file_name": "backup-sql-clinica_demo-2025-11-26-140530.sql",
    "file_size": 524288,
    "file_size_mb": 0.5,
    "backup_type": "manual",
    "created_by": {
      "id": 2,
      "email": "admin@clinica.com",
      "nombre": "Juan Admin"
    },
    "created_at": "2025-11-26T14:05:30Z"
  },
  {
    "id": 14,
    "file_name": "auto-sql-clinica_demo-2025-11-26-030000.sql",
    "file_size": 498304,
    "file_size_mb": 0.47,
    "backup_type": "automatic",
    "created_by": null,
    "created_at": "2025-11-26T03:00:00Z"
  }
]
```

### **3. Descargar Backup**

```http
GET /api/backups/history/15/download/
Authorization: Bearer <token>

Response: Archivo .sql o .json
```

### **4. Eliminar Backup**

```http
DELETE /api/backups/history/15/
Authorization: Bearer <token_admin>

Response:
{
  "message": "Backup eliminado exitosamente"
}
```

---

## ⏰ **BACKUPS AUTOMÁTICOS**

### **Ejecutar Comando Manualmente:**

```bash
python manage.py run_scheduled_backups
```

**Output:**
```
⏳ Verificando backups programados...
📦 Iniciando backup para: Clínica Dental ABC...
   -> Subido exitosamente a Supabase
✅ 1 backup(s) ejecutado(s) exitosamente.
✅ Verificación de backups finalizada.
```

### **Configurar Cron Job en Render:**

El sistema ya está configurado para ejecutarse cada hora en Render. Verifica `render.yaml`:

```yaml
- type: cron
  name: backup-worker
  env: python
  schedule: "0 * * * *"  # Cada hora
  buildCommand: "pip install -r requirements.txt"
  startCommand: "python manage.py run_scheduled_backups"
  envVars:
    - key: DATABASE_URL
      fromDatabase:
        name: psico-db
        property: connectionString
    - key: SUPABASE_URL
      value: https://xqygvoqtikqehvxcihwd.supabase.co
    - key: SUPABASE_KEY
      sync: false
```

---

## 🧪 **CREAR BACKUPS DE PRUEBA**

Para demostración y testing del frontend:

```bash
python crear_backups_prueba.py
```

**Esto creará:**
- 5 backups de ejemplo
- Con diferentes fechas (últimos 6 días)
- Tipos variados (manual/automático)
- Subidos a Supabase Storage
- Registrados en la BD

---

## 📝 **EJEMPLOS DE CONFIGURACIÓN**

### **Backup Diario a las 2:00 AM:**

```python
# Django Admin o Shell
clinica.backup_schedule = 'daily'
clinica.backup_time = '02:00:00'
clinica.save()
```

### **Backup Cada 12 Horas (desde las 3:00 PM):**

```python
clinica.backup_schedule = 'every_12h'
clinica.backup_time = '15:00:00'  # 3:00 PM
clinica.save()
```
Ejecutará a: 3:00 AM, 3:00 PM, 3:00 AM...

### **Backup Semanal (Domingos a las 2:00 AM):**

```python
clinica.backup_schedule = 'weekly'
clinica.backup_weekday = 6  # Domingo
clinica.backup_time = '02:00:00'
clinica.save()
```

### **Backup Mensual (Día 1 a las 2:00 AM):**

```python
clinica.backup_schedule = 'monthly'
clinica.backup_day_of_month = 1
clinica.backup_time = '02:00:00'
clinica.save()
```

### **Backup Programado (Una vez el 30 de Nov a las 10:00 AM):**

```python
from django.utils import timezone
from datetime import datetime

clinica.backup_schedule = 'scheduled'
clinica.next_scheduled_backup = timezone.make_aware(
    datetime(2025, 11, 30, 10, 0, 0)
)
clinica.save()
```

**Nota:** Después de ejecutarse, se auto-desactivará (`backup_schedule = 'disabled'`).

---

## 🔒 **PERMISOS**

- ✅ **Crear backup manual:** Solo `ADMIN`
- ✅ **Ver historial:** Todos los usuarios autenticados
- ✅ **Descargar backup:** Todos los usuarios autenticados
- ✅ **Eliminar backup:** Solo `ADMIN`

---

## ☁️ **ESTRUCTURA EN SUPABASE**

```
Bucket: backups/
├── clinica_demo/
│   ├── backup-sql-clinica_demo-2025-11-26-140530.sql
│   ├── auto-sql-clinica_demo-2025-11-26-030000.sql
│   └── backup-json-clinica_demo-2025-11-25-151045.json
├── clinica_abc/
│   ├── backup-sql-clinica_abc-2025-11-26-093022.sql
│   └── auto-json-clinica_abc-2025-11-26-030030.json
```

**Naming Convention:**
```
[tipo]-[formato]-[schema]-[timestamp].[ext]

Ejemplos:
- backup-sql-clinica_demo-2025-11-26-140530.sql  (manual)
- auto-sql-clinica_demo-2025-11-26-030000.sql    (automático)
```

---

## ✅ **SIGUIENTE PASO: CONFIGURAR EN RENDER**

1. **Ve a Render Dashboard:** https://dashboard.render.com
2. **Selecciona tu servicio** `ClinicaDental-backend2`
3. **Environment → Add Environment Variable:**
   ```
   SUPABASE_URL=https://xqygvoqtikqehvxcihwd.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhxeWd2b3F0aWtxZWh2eGNpaHdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDE2NjAxMCwiZXhwIjoyMDc5NzQyMDEwfQ.SoYIwqR3d1Ys9nGUNTeXohHP-AgR8e916SDb_m9gM0I
   ```
4. **Save Changes** (Render redesplegará automáticamente)
5. **Verificar Cron Job:** Debería aparecer `backup-worker` en tu dashboard

---

## 🎉 **¡SISTEMA LISTO!**

El sistema de backups está **100% implementado y funcional**. Puedes:

1. ✅ Crear backups manuales desde la API
2. ✅ Ver historial completo con metadata
3. ✅ Descargar backups desde Supabase
4. ✅ Configurar backups automáticos flexibles
5. ✅ Ejecutar comando manualmente o con cron
6. ✅ Subir backups de prueba para demostración

**Para probar ahora mismo:**

```bash
# 1. Subir backups de prueba
python crear_backups_prueba.py

# 2. Ver en el navegador o Postman
GET http://localhost:8000/api/backups/history/
Authorization: Bearer <tu_token>
```

---

**Autor:** Sistema ClinicaDental Multi-Tenant  
**Fecha:** 26 de Noviembre, 2025  
**Versión:** 1.0
