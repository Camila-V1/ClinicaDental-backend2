# 📦 Guía Completa: Sistema de Backups por Clínica

## 📋 Índice
1. [Arquitectura General](#arquitectura-general)
2. [Componentes del Sistema](#componentes-del-sistema)
3. [Flujo de Implementación](#flujo-de-implementación)
4. [Configuración y Uso](#configuración-y-uso)
5. [API Endpoints](#api-endpoints)
6. [Comandos de Gestión](#comandos-de-gestión)
7. [Almacenamiento en Supabase](#almacenamiento-en-supabase)
8. [Backups Automáticos](#backups-automáticos)

---

## 🏗️ Arquitectura General

### Principio de Diseño
El sistema de backups está diseñado para **multi-tenancy** usando `django-tenants`, donde:
- Cada clínica tiene su propio schema PostgreSQL
- Los backups se realizan **por schema** (no de toda la BD)
- Se almacenan en **Supabase Storage** (nube)
- Se registran en modelo `BackupRecord` para historial
- Hay backups **manuales** (admin) y **automáticos** (cron)

### Stack Tecnológico
- **Backend**: Django 5.1.4 + django-tenants
- **Base de datos**: PostgreSQL (Neon)
- **Almacenamiento**: Supabase Storage (bucket `backups`)
- **Formatos**: SQL (pg_dump) o JSON (fallback)
- **Automatización**: Django Management Commands + Cron Jobs

---

## 🧩 Componentes del Sistema

### 1. Modelo `Clinic` (apps/tenants/models.py)

```python
class Clinic(TenantMixin):
    # Campos de configuración de backups
    SCHEDULE_CHOICES = (
        ('disabled', 'Desactivado'),
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('scheduled', 'Programado por Fecha'),
    )
    
    backup_schedule = models.CharField(
        max_length=10,
        choices=SCHEDULE_CHOICES,
        default='disabled',
        help_text="Frecuencia de los backups automáticos."
    )
    
    last_backup_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora del último backup automático."
    )
    
    next_scheduled_backup = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora exacta programada para el próximo backup."
    )
```

**Campos clave:**
- `backup_schedule`: Frecuencia (disabled, daily, weekly, scheduled)
- `last_backup_at`: Timestamp del último backup exitoso
- `next_scheduled_backup`: Fecha programada para backup único

### 2. Modelo `BackupRecord` (apps/backups/models.py)

```python
class BackupRecord(models.Model):
    BACKUP_TYPES = (
        ('manual', 'Manual'),
        ('automatic', 'Automático'),
    )
    
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()  # Ruta en Supabase bucket
    file_size = models.BigIntegerField()
    backup_type = models.CharField(max_length=10, choices=BACKUP_TYPES)
    created_by = models.ForeignKey(User, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Propósito:**
- Historial de todos los backups (manuales y automáticos)
- Metadata de archivos en Supabase
- Permite listar, descargar y restaurar backups

### 3. Vista `CreateBackupView` (apps/backups/views.py)

**Funcionalidad:**
```python
POST /api/backups/create/?download=true
```

**Proceso:**
1. **Intenta pg_dump (SQL)**: 
   - Ejecuta `pg_dump --schema=<schema_name> --format=p --inserts`
   - Genera archivo `.sql` con estructura y datos
   - Usa formato plain text con inserts (no COPY)
   
2. **Fallback a Django dumpdata (JSON)**:
   - Si pg_dump falla (ej: no está instalado o hay error de conexión)
   - Usa `python manage.py dumpdata` para JSON
   - Solo exporta apps de tenant: users, professionals, appointments, chat, clinical_history, payment_system
   
3. **Sube a Supabase Storage**:
   - Path: `<schema_name>/backup-<formato>-<schema>-<timestamp>.<ext>`
   - Bucket: `backups`
   - Content-type: `application/sql` o `application/json`
   
4. **Crea registro en BackupRecord**:
   - Guarda metadata (nombre, tamaño, tipo, usuario)
   - Se guarda en el schema del tenant actual
   
5. **Devuelve archivo o info**:
   - Si `?download=true`: descarga directa del archivo
   - Si no: JSON con info del backup creado

**Código clave:**
```python
def _create_pg_dump_bytes(self, schema_name):
    command = [
        'pg_dump', 
        '--dbname', db_settings['NAME'],
        '--host', '127.0.0.1',
        '--port', str(db_settings['PORT']),
        '--username', db_settings['USER'],
        '--schema', schema_name,
        '--format', 'p',  # plain text
        '--inserts',      # usar INSERT en vez de COPY
        '--no-owner',     # sin comandos de ownership
        '--no-privileges' # sin comandos de privilegios
    ]
    env = {'PGPASSWORD': db_settings['PASSWORD']}
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, stderr=stderr)
    return stdout
```

### 4. Supabase Storage (apps/backups/supabase_storage.py)

**Funciones principales:**

```python
def upload_backup_to_supabase(file_content_bytes, file_path_in_bucket):
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    supabase.storage.from_("backups").upload(
        path=file_path_in_bucket,
        file=file_content_bytes,
        file_options={"content-type": content_type, "upsert": "true"}
    )
    
    public_url = supabase.storage.from_("backups").get_public_url(file_path_in_bucket)
    return {'success': True, 'path': file_path_in_bucket, 'url': public_url}

def download_backup_from_supabase(file_path_in_bucket):
    response_bytes = supabase.storage.from_("backups").download(file_path_in_bucket)
    return response_bytes
```

**Estructura del bucket:**
```
backups/
├── bienestar/
│   ├── backup-sql-bienestar-2025-11-25-140530.sql
│   ├── auto-sql-bienestar-2025-11-25-003012.sql
│   └── backup-json-bienestar-2025-11-24-151045.json
├── mindcare/
│   └── backup-sql-mindcare-2025-11-25-093022.sql
└── public/ (no se usa, excluido)
```

### 5. Comando `run_scheduled_backups` (apps/backups/management/commands/)

**Propósito:** Ejecuta backups automáticos según configuración de cada clínica.

**Lógica de ejecución:**

```python
def handle(self, *args, **options):
    clinics = Clinic.objects.exclude(schema_name='public')
    now = timezone.now()
    
    for clinic in clinics:
        schedule = clinic.backup_schedule
        run_backup = False
        
        # 1. BACKUPS PROGRAMADOS (fecha específica)
        if schedule == 'scheduled':
            if clinic.next_scheduled_backup and clinic.next_scheduled_backup <= now:
                run_backup = True
        
        # 2. BACKUPS DIARIOS
        elif schedule == 'daily':
            if not clinic.last_backup_at or clinic.last_backup_at.date() < now.date():
                run_backup = True
        
        # 3. BACKUPS SEMANALES (Domingos)
        elif schedule == 'weekly':
            if now.weekday() == 6 and (not clinic.last_backup_at or clinic.last_backup_at.date() < now.date()):
                run_backup = True
        
        if run_backup:
            self.perform_backup(clinic)
```

**Función `perform_backup`:**
```python
def perform_backup(self, clinic):
    with schema_context(clinic.schema_name):
        # 1. Crear backup (SQL o JSON)
        backup_data_bytes = view_logic._create_pg_dump_bytes(schema_name)
        
        # 2. Subir a Supabase
        upload_result = upload_backup_to_supabase(backup_data_bytes, file_path)
        
        # 3. Registrar en BD
        BackupRecord.objects.create(
            file_name=file_name,
            file_path=upload_result['path'],
            backup_type='automatic',
            created_by=None
        )
        
        # 4. Actualizar clínica
        clinic.last_backup_at = timezone.now()
        if clinic.backup_schedule == 'scheduled':
            clinic.next_scheduled_backup = None
            clinic.backup_schedule = 'disabled'
        clinic.save()
```

---

## 🔧 Flujo de Implementación

### Paso 1: Instalación de Dependencias

```bash
pip install supabase psycopg2-binary
```

**requirements.txt:**
```
supabase==2.23.0
psycopg2-binary==2.9.10
```

### Paso 2: Configuración de Supabase

**settings.py:**
```python
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
```

**Variables de entorno (.env o Render):**
```
SUPABASE_URL=https://xefqugptdzubukeowcnj.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Paso 3: Crear Bucket en Supabase

1. Ir a **Supabase Dashboard** → Storage
2. Crear bucket llamado `backups`
3. Configurar políticas de acceso (privado o público según necesidad)

### Paso 4: Migraciones de Base de Datos

```bash
# Agregar campos a modelo Clinic
python manage.py makemigrations tenants
python manage.py migrate_schemas --shared
```

**Migración generada (ejemplo):**
```python
# 0004_clinic_backup_schedule_clinic_last_backup_at.py
operations = [
    migrations.AddField(
        model_name='clinic',
        name='backup_schedule',
        field=models.CharField(
            choices=[('disabled', 'Desactivado'), ('daily', 'Diario'), ('weekly', 'Semanal')],
            default='disabled',
            max_length=10
        ),
    ),
    migrations.AddField(
        model_name='clinic',
        name='last_backup_at',
        field=models.DateTimeField(blank=True, null=True),
    ),
]
```

### Paso 5: Crear App `backups`

```bash
python manage.py startapp backups
```

**Estructura:**
```
apps/backups/
├── management/
│   └── commands/
│       └── run_scheduled_backups.py
├── models.py          # BackupRecord
├── views.py           # CreateBackupView, RestoreBackupView
├── serializers.py     # BackupRecordSerializer
├── supabase_storage.py  # Funciones de upload/download
└── urls.py
```

### Paso 6: Registrar URLs

**apps/backups/urls.py:**
```python
from django.urls import path
from .views import CreateBackupView, BackupHistoryListView, DownloadBackupView

urlpatterns = [
    path('create/', CreateBackupView.as_view(), name='create_backup'),
    path('history/', BackupHistoryListView.as_view(), name='backup_history'),
    path('history/<int:pk>/download/', DownloadBackupView.as_view(), name='download_backup'),
    path('restore/', RestoreBackupFromFileView.as_view(), name='restore_backup'),
]
```

**config/urls_tenants.py:**
```python
urlpatterns = [
    # ...
    path('api/backups/', include('apps.backups.urls')),
]
```

### Paso 7: Configurar Permisos

**apps/clinic_admin/permissions.py:**
```python
class IsClinicAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'clinic_admin'
```

**Aplicar en vistas:**
```python
class CreateBackupView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]
```

---

## 🎯 Configuración y Uso

### Configurar Backups Automáticos (Admin)

**Endpoint:**
```
PATCH /api/admin/config/backup/
```

**Request:**
```json
{
  "backup_schedule": "daily"
}
```

**Opciones:**
- `"disabled"`: Sin backups automáticos
- `"daily"`: Backup diario (1 vez al día)
- `"weekly"`: Backup semanal (domingos)
- `"scheduled"`: Backup en fecha específica

**Response:**
```json
{
  "backup_schedule": "daily",
  "last_backup_at": "2025-11-25T03:00:15Z"
}
```

### Crear Backup Manual

**Request:**
```bash
POST /api/backups/create/?download=true
Authorization: Bearer <token_admin>
```

**Response (si download=false):**
```json
{
  "message": "Backup creado y subido a Supabase exitosamente",
  "backup_info": {
    "id": 15,
    "file_name": "backup-sql-bienestar-2025-11-25-140530.sql",
    "file_size": 524288,
    "backup_type": "manual",
    "created_at": "2025-11-25T14:05:30Z",
    "created_by": {
      "id": 2,
      "email": "admin@bienestar.com"
    }
  }
}
```

### Ver Historial de Backups

**Request:**
```bash
GET /api/backups/history/
```

**Response:**
```json
[
  {
    "id": 15,
    "file_name": "backup-sql-bienestar-2025-11-25-140530.sql",
    "file_size": 524288,
    "backup_type": "manual",
    "created_at": "2025-11-25T14:05:30Z",
    "created_by": {"email": "admin@bienestar.com"}
  },
  {
    "id": 14,
    "file_name": "auto-sql-bienestar-2025-11-25-030015.sql",
    "file_size": 498304,
    "backup_type": "automatic",
    "created_at": "2025-11-25T03:00:15Z",
    "created_by": null
  }
]
```

### Descargar Backup

**Request:**
```bash
GET /api/backups/history/15/download/
```

**Response:** Archivo `.sql` o `.json` para descarga directa

---

## 🔄 Comandos de Gestión

### Ejecutar Backups Programados Manualmente

```bash
# En desarrollo local
python manage.py run_scheduled_backups

# En Render Shell
python manage.py run_scheduled_backups
```

**Output esperado:**
```
⏳ Verificando backups programados...
📦 Iniciando backup para: Clínica Bienestar...
   -> Subido exitosamente a Supabase
📦 Iniciando backup para: Clínica Mindcare...
   -> Subido exitosamente a Supabase
✅ Verificación de backups finalizada.
```

### Restaurar Backup (Comando Custom)

**Crear comando:** `apps/backups/management/commands/restore_backup.py`

```python
# Ejemplo básico
def handle(self, *args, **options):
    backup_id = options['backup_id']
    record = BackupRecord.objects.get(id=backup_id)
    
    # Descargar de Supabase
    backup_bytes = download_backup_from_supabase(record.file_path)
    
    # Restaurar con psql o loaddata
    # ...
```

---

## ☁️ Almacenamiento en Supabase

### Estructura del Bucket

```
backups/ (bucket raíz)
├── bienestar/
│   ├── backup-sql-bienestar-2025-11-25-140530.sql     [524 KB] (manual)
│   ├── auto-sql-bienestar-2025-11-25-030015.sql       [498 KB] (auto)
│   └── backup-json-bienestar-2025-11-24-151045.json   [1.2 MB] (fallback)
├── mindcare/
│   ├── backup-sql-mindcare-2025-11-25-093022.sql      [612 KB]
│   └── auto-json-mindcare-2025-11-25-030030.json      [890 KB]
```

### Naming Convention

**Formato:**
```
[tipo]-[formato]-[schema]-[timestamp].[ext]
```

**Ejemplos:**
- `backup-sql-bienestar-2025-11-25-140530.sql` (manual SQL)
- `auto-sql-mindcare-2025-11-25-030015.sql` (automático SQL)
- `backup-json-bienestar-2025-11-24-151045.json` (manual JSON)

### Políticas de Retención

**Configuración recomendada:**
- Backups manuales: Mantener indefinidamente
- Backups diarios: Últimos 30 días
- Backups semanales: Últimos 6 meses

**Implementar con cron adicional:**
```python
# apps/backups/management/commands/cleanup_old_backups.py
def handle(self):
    cutoff_date = timezone.now() - timedelta(days=30)
    old_backups = BackupRecord.objects.filter(
        backup_type='automatic',
        created_at__lt=cutoff_date
    )
    
    for backup in old_backups:
        # Eliminar de Supabase
        supabase.storage.from_("backups").remove([backup.file_path])
        # Eliminar registro
        backup.delete()
```

---

## ⏰ Backups Automáticos

### Configuración en Render (Cron Job)

**render.yaml:**
```yaml
services:
  # ...otros servicios
  
  - type: cron
    name: backup-worker
    env: python
    schedule: "* * * * *"  # Cada minuto (verifica schedules programados)
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python manage.py run_scheduled_backups"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: psico-db
          property: connectionString
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_BUCKET_NAME
        value: backups
```

**Configurar en Render Dashboard:**
1. Ya está configurado en `render.yaml` como `backup-worker`
2. Schedule: `* * * * *` (cada minuto, verifica si hay backups pendientes)
3. Command: `python manage.py run_scheduled_backups`
4. Env vars: Ya configuradas desde `render.yaml`

**Nota importante:** El cron se ejecuta **cada minuto** pero solo hace backup si la configuración de la clínica lo requiere (daily/weekly/scheduled).

### Lógica de Ejecución Detallada

#### 1. Backups Diarios (`daily`)

```python
if schedule == 'daily':
    if not clinic.last_backup_at or clinic.last_backup_at.date() < now.date():
        run_backup = True
```

**Comportamiento:**
- Se ejecuta una vez al día
- Compara fecha de `last_backup_at` con fecha actual
- Si nunca se hizo backup (`None`), ejecuta
- Si el último fue ayer o antes, ejecuta
- Si ya se hizo hoy, **salta**

#### 2. Backups Semanales (`weekly`)

```python
if schedule == 'weekly':
    if now.weekday() == 6 and (not clinic.last_backup_at or clinic.last_backup_at.date() < now.date()):
        run_backup = True
```

**Comportamiento:**
- Solo se ejecuta los **domingos** (weekday == 6)
- Si es domingo y no se hizo hoy, ejecuta
- Resto de días: **salta**

#### 3. Backups Programados (`scheduled`)

```python
if schedule == 'scheduled':
    if clinic.next_scheduled_backup and clinic.next_scheduled_backup <= now:
        run_backup = True
        
        # Después de ejecutar:
        clinic.next_scheduled_backup = None
        clinic.backup_schedule = 'disabled'
```

**Comportamiento:**
- Se ejecuta **una sola vez** en la fecha programada
- Compara `next_scheduled_backup` con hora actual
- Si la fecha ya pasó, ejecuta
- **Importante:** Después de ejecutar, se auto-desactiva
- Limpia `next_scheduled_backup` y pone schedule en `disabled`

### Actualización de Estado Post-Backup

```python
clinic.last_backup_at = timezone.now()

if clinic.backup_schedule == 'scheduled':
    clinic.next_scheduled_backup = None
    clinic.backup_schedule = 'disabled'

clinic.save()
```

---

## 🔒 Seguridad y Mejores Prácticas

### 1. Permisos de API
- Solo `clinic_admin` puede crear backups manuales
- Solo `clinic_admin` puede ver historial de su clínica
- Usuarios normales no tienen acceso

### 2. Aislamiento Multi-Tenant
- Los backups respetan `schema_context`
- Cada clínica solo ve sus propios backups en el historial
- `BackupRecord` se guarda en el schema de cada clínica (no en `public`)
- Los archivos en Supabase se organizan por carpetas de schema

### 3. Variables de Entorno Seguras
```python
# ❌ NUNCA hardcodear
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5..."

# ✅ Usar variables de entorno
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
```

### 4. Logging de Operaciones
```python
logger.info(f"Backup manual creado por {request.user.email} (ID: {record.id})")
logger.error(f"[AutoBackup] Error crítico en {clinic.name}: {e}")
```

### 5. Validación de Tamaño
```python
MAX_BACKUP_SIZE = 100 * 1024 * 1024  # 100 MB

if len(backup_data_bytes) > MAX_BACKUP_SIZE:
    return Response({'error': 'Backup demasiado grande'}, status=400)
```

---

## 🧪 Testing

### Test de Backup Manual

```python
# tests/test_backups.py
def test_create_backup_manual(self):
    response = self.client.post('/api/backups/create/', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    self.assertEqual(response.status_code, 201)
    self.assertIn('backup_info', response.data)
    
    # Verificar registro en BD
    backup = BackupRecord.objects.last()
    self.assertEqual(backup.backup_type, 'manual')
    self.assertEqual(backup.created_by, self.admin_user)
```

### Test de Comando Automático

```python
def test_scheduled_backups_daily(self):
    clinic = Clinic.objects.get(schema_name='bienestar')
    clinic.backup_schedule = 'daily'
    clinic.last_backup_at = timezone.now() - timedelta(days=1)
    clinic.save()
    
    call_command('run_scheduled_backups')
    
    clinic.refresh_from_db()
    self.assertEqual(clinic.last_backup_at.date(), timezone.now().date())
```

---

## 📊 Monitoreo y Métricas

### Queries Útiles

**Backups por clínica (último mes):**
```sql
SELECT 
    c.name AS clinica,
    COUNT(br.id) AS total_backups,
    SUM(br.file_size) / 1024 / 1024 AS total_mb
FROM tenants_clinic c
LEFT JOIN backups_backuprecord br ON br.created_at > NOW() - INTERVAL '30 days'
GROUP BY c.name;
```

**Último backup por clínica:**
```sql
SELECT 
    name, 
    backup_schedule, 
    last_backup_at,
    NOW() - last_backup_at AS time_since_last
FROM tenants_clinic
WHERE schema_name != 'public';
```

---

## ❓ Troubleshooting

### Error: pg_dump no encontrado

**Síntoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'pg_dump'
```

**Solución:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Render: Ya viene instalado, verificar PATH
which pg_dump
```

### Error: Supabase 401 Unauthorized

**Síntoma:**
```
Error al subir a Supabase: 401 Unauthorized
```

**Solución:**
1. Verificar `SUPABASE_KEY` en variables de entorno
2. Usar **service_role key**, no anon key
3. Verificar políticas del bucket en Supabase Dashboard

### Backups no se ejecutan automáticamente

**Debug:**
```bash
# 1. Verificar configuración de clínica
python manage.py shell
>>> from apps.tenants.models import Clinic
>>> Clinic.objects.values('name', 'backup_schedule', 'last_backup_at')

# 2. Ejecutar comando manualmente
python manage.py run_scheduled_backups

# 3. Revisar logs de Render Cron Job
```

---

## 🎯 Resumen de Flujo Completo

### Backup Manual
1. Admin hace `POST /api/backups/create/`
2. Django crea pg_dump del schema
3. Sube archivo a Supabase Storage
4. Crea registro en `BackupRecord`
5. Devuelve info o archivo al admin

### Backup Automático
1. Cron ejecuta `run_scheduled_backups` **cada minuto** (schedule: `* * * * *`)
2. Comando revisa todas las clínicas (excepto `public`)
3. Evalúa si debe hacer backup según configuración:
   - **daily**: Si no se hizo hoy y es un nuevo día
   - **weekly**: Si es domingo y no se hizo hoy
   - **scheduled**: Si `next_scheduled_backup` ya pasó
4. Ejecuta `perform_backup()` para cada clínica elegible
5. Actualiza `last_backup_at` en modelo `Clinic`
6. Si era `scheduled`, limpia `next_scheduled_backup` y desactiva
7. Registra en `BackupRecord` con `backup_type='automatic'` y `created_by=None`

---

## 📚 Archivos Clave del Sistema

| Archivo | Propósito |
|---------|-----------|
| `apps/tenants/models.py` | Modelo Clinic con campos de configuración |
| `apps/backups/models.py` | Modelo BackupRecord para historial |
| `apps/backups/views.py` | Vistas para crear, listar, descargar backups |
| `apps/backups/supabase_storage.py` | Funciones upload/download a Supabase |
| `apps/backups/management/commands/run_scheduled_backups.py` | Comando para backups automáticos |
| `apps/clinic_admin/views.py` | Vista para configurar schedule |
| `render.yaml` | Configuración de Cron Job en Render |

---

## ✅ Checklist de Implementación

- [x] Instalar dependencias (supabase, psycopg2-binary)
- [x] Crear bucket `backups` en Supabase
- [x] Agregar variables de entorno (SUPABASE_URL, SUPABASE_KEY)
- [x] Crear migraciones para `backup_schedule`, `last_backup_at`, `next_scheduled_backup`
- [x] Implementar modelo `BackupRecord`
- [x] Implementar vista `CreateBackupView`
- [x] Implementar funciones de Supabase Storage
- [x] Implementar comando `run_scheduled_backups`
- [x] Configurar Cron Job en Render
- [x] Implementar API de configuración (`BackupConfigView`)
- [x] Agregar permisos de admin
- [x] Crear endpoints para historial y descarga
- [x] Testing de backups manuales y automáticos
- [x] Documentación completa

---

**Autor:** Sistema PsicoAdmin Multi-Tenant  
**Última actualización:** 25 de Noviembre, 2025  
**Versión:** 1.0
