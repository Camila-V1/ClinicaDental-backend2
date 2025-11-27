# 📋 GUÍA DE IMPLEMENTACIÓN - SISTEMA DE BACKUPS

## 🎯 RESUMEN EJECUTIVO

**Estado:** ✅ Implementado en Backend (Pendiente verificación en Producción)  
**Tipo:** Tenant-Specific (cada clínica gestiona sus propios backups)  
**Almacenamiento:** Supabase Storage (bucket: `backups`)  
**Autenticación:** JWT requerido  
**Permisos:** Solo usuarios autenticados de cada tenant

---

## 📁 ESTRUCTURA DEL MÓDULO

```
backups/
├── __init__.py                    # ✅ Módulo Python válido
├── models.py                      # ✅ BackupRecord model
├── serializers.py                 # ✅ BackupRecordSerializer
├── views.py                       # ✅ 4 vistas principales
├── urls.py                        # ✅ URL patterns configurados
├── apps.py                        # ✅ BackupsConfig
├── supabase_storage.py            # ✅ Integración con Supabase
├── admin.py                       # ✅ Registro en Django Admin
└── migrations/
    ├── __init__.py
    └── 0001_initial.py            # ✅ Migración inicial aplicada
```

---

## 🔗 ENDPOINTS DISPONIBLES

### Base URL
```
https://clinica-dental-backend.onrender.com/api/backups/
```

### 1️⃣ Listar Historial de Backups
```http
GET /api/backups/history/
Authorization: Bearer {token}
X-Tenant-ID: clinica_demo
```

**Respuesta Esperada (200 OK):**
```json
[
  {
    "id": 1,
    "file_name": "backup_clinica_demo_2025-11-27_12-30-45.sql",
    "file_path": "backups/clinica_demo/backup_2025-11-27.sql",
    "file_size": 2548736,
    "file_size_mb": 2.43,
    "backup_type": "manual",
    "created_by": {
      "id": 1004,
      "email": "admin@clinicademo1.com",
      "nombre": "Admin",
      "apellido": "Sistema"
    },
    "created_at": "2025-11-27T12:30:45.123456Z"
  }
]
```

**Respuesta si no hay backups (200 OK):**
```json
[]
```

---

### 2️⃣ Crear Backup Manual
```http
POST /api/backups/create/
Authorization: Bearer {token}
X-Tenant-ID: clinica_demo
Content-Type: application/json

{
  "backup_type": "manual"
}
```

**Respuesta (201 CREATED):**
```json
{
  "success": true,
  "message": "Backup creado exitosamente",
  "backup": {
    "id": 2,
    "file_name": "backup_clinica_demo_2025-11-27_14-15-30.sql",
    "file_size_mb": 2.56,
    "created_at": "2025-11-27T14:15:30.123456Z"
  }
}
```

---

### 3️⃣ Descargar Backup
```http
GET /api/backups/history/{id}/download/
Authorization: Bearer {token}
X-Tenant-ID: clinica_demo
```

**Respuesta:**
- **200 OK:** Archivo SQL descargado (application/octet-stream)
- **404 Not Found:** Backup no encontrado
- **500 Error:** Archivo no encontrado en Supabase

---

### 4️⃣ Eliminar Backup
```http
DELETE /api/backups/history/{id}/
Authorization: Bearer {token}
X-Tenant-ID: clinica_demo
```

**Respuesta (204 NO CONTENT):**
Sin contenido (eliminación exitosa)

---

## 🔧 CONFIGURACIÓN BACKEND

### 1. Registro en INSTALLED_APPS
**Archivo:** `core/settings.py`
```python
TENANT_APPS = [
    # ... otras apps
    'backups',  # ✅ Sistema de backups automáticos
]
```

### 2. URLs Configuradas
**Archivo:** `core/urls_tenant.py`
```python
urlpatterns = [
    # ... otras rutas
    path('api/backups/', include('backups.urls')),  # ✅ Sistema de backups
]
```

### 3. Modelo BackupRecord
**Archivo:** `backups/models.py`
```python
class BackupRecord(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    file_size = models.BigIntegerField()
    backup_type = models.CharField(max_length=10, choices=BACKUP_TYPES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 4. Variables de Entorno Requeridas
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=backups
```

---

## 🐛 TROUBLESHOOTING

### Problema: 404 Not Found en `/api/backups/history/`

**Posibles Causas:**
1. ❌ Migraciones no aplicadas en producción
2. ❌ Módulo `backups` no importable
3. ❌ Error de sintaxis en algún archivo
4. ❌ Conflicto de nombres en URLs

**Solución en Render Shell:**
```bash
# 1. Verificar migraciones
python manage.py showmigrations backups

# 2. Aplicar migraciones si no están
python manage.py migrate backups

# 3. Verificar importación del módulo
python manage.py shell
>>> from backups.models import BackupRecord
>>> from backups.views import BackupHistoryListView
>>> exit()

# 4. Verificar URLs
python manage.py show_urls | grep backups
```

---

### Problema: CORS Error en Exportación

**Error:**
```
Request header field x-tenant is not allowed by Access-Control-Allow-Headers
```

**Solución Aplicada:**
```python
# core/settings.py
CORS_ALLOW_HEADERS = [
    # ... otros headers
    'x-tenant-id',
    'x-tenant',  # ✅ Agregado para exportación de reportes
]
```

---

## 📱 IMPLEMENTACIÓN FRONTEND

### Servicio de Backups
**Archivo:** `src/services/backupsService.js`

```javascript
import api from './api';

export const backupsService = {
  // Listar historial
  getHistorial: async () => {
    const response = await api.get('/api/backups/history/');
    return response.data;
  },

  // Crear backup
  createBackup: async () => {
    const response = await api.post('/api/backups/create/', {
      backup_type: 'manual'
    });
    return response.data;
  },

  // Descargar backup
  downloadBackup: async (id) => {
    const response = await api.get(`/api/backups/history/${id}/download/`, {
      responseType: 'blob'
    });
    
    // Crear link de descarga
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `backup_${id}.sql`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  // Eliminar backup
  deleteBackup: async (id) => {
    await api.delete(`/api/backups/history/${id}/`);
  }
};
```

---

### Componente React de Ejemplo
```jsx
import { useState, useEffect } from 'react';
import { backupsService } from '../services/backupsService';

function BackupsPage() {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBackups();
  }, []);

  const loadBackups = async () => {
    try {
      const data = await backupsService.getHistorial();
      setBackups(data);
    } catch (error) {
      console.error('Error al cargar backups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      await backupsService.createBackup();
      await loadBackups(); // Recargar lista
      alert('Backup creado exitosamente');
    } catch (error) {
      alert('Error al crear backup');
    }
  };

  const handleDownload = async (id) => {
    try {
      await backupsService.downloadBackup(id);
    } catch (error) {
      alert('Error al descargar backup');
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <h1>Gestión de Backups</h1>
      <button onClick={handleCreateBackup}>Crear Backup</button>
      
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tamaño</th>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {backups.map(backup => (
            <tr key={backup.id}>
              <td>{backup.file_name}</td>
              <td>{backup.file_size_mb} MB</td>
              <td>{backup.backup_type}</td>
              <td>{new Date(backup.created_at).toLocaleString()}</td>
              <td>
                <button onClick={() => handleDownload(backup.id)}>
                  Descargar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend
- [x] Modelo `BackupRecord` creado
- [x] Migraciones generadas (`0001_initial.py`)
- [x] Migraciones aplicadas en local ✅
- [ ] **Migraciones aplicadas en Render** ⚠️ PENDIENTE VERIFICAR
- [x] Vistas implementadas (4 endpoints)
- [x] Serializer configurado
- [x] URLs registradas en `urls_tenant.py`
- [x] Módulo en `TENANT_APPS`
- [x] `__init__.py` presente
- [x] Integración con Supabase Storage

### Configuración
- [x] CORS configurado con `x-tenant` header
- [ ] Variables de entorno en Render ⚠️ VERIFICAR
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SUPABASE_BUCKET`

### Frontend
- [ ] Servicio de backups implementado
- [ ] Componente de gestión creado
- [ ] Manejo de errores implementado
- [ ] UI/UX diseñada

---

## 🚀 PRÓXIMOS PASOS

### 1. Verificar en Render (PRIORIDAD ALTA)
```bash
# Acceder a Render Shell
python manage.py showmigrations backups
python manage.py migrate backups

# Probar importación
python manage.py shell
>>> from backups.models import BackupRecord
>>> BackupRecord.objects.count()
```

### 2. Probar Endpoint Manualmente
```bash
# Con curl
curl -X GET \
  https://clinica-dental-backend.onrender.com/api/backups/history/ \
  -H "Authorization: Bearer {token}" \
  -H "X-Tenant-ID: clinica_demo"
```

### 3. Crear Backups de Prueba
```python
# En Django shell
from backups.models import BackupRecord
from usuarios.models import Usuario

admin = Usuario.objects.get(email='admin@clinicademo1.com')

backup = BackupRecord.objects.create(
    file_name='backup_test_2025-11-27.sql',
    file_path='backups/clinica_demo/test.sql',
    file_size=1024000,
    backup_type='manual',
    created_by=admin
)
```

### 4. Implementar en Frontend
- Crear página de gestión de backups
- Integrar servicio con API
- Agregar al menú de navegación
- Implementar permisos (solo admin)

---

## 📊 DATOS DE EJEMPLO

```json
[
  {
    "id": 1,
    "file_name": "backup_clinica_demo_2025-11-27_09-00-00.sql",
    "file_path": "backups/clinica_demo/auto/backup_2025-11-27_09-00-00.sql",
    "file_size": 2548736,
    "file_size_mb": 2.43,
    "backup_type": "automatic",
    "created_by": null,
    "created_at": "2025-11-27T09:00:00Z"
  },
  {
    "id": 2,
    "file_name": "backup_clinica_demo_2025-11-27_14-30-15.sql",
    "file_path": "backups/clinica_demo/manual/backup_2025-11-27_14-30-15.sql",
    "file_size": 2601984,
    "file_size_mb": 2.48,
    "backup_type": "manual",
    "created_by": {
      "id": 1004,
      "email": "admin@clinicademo1.com",
      "nombre": "Admin",
      "apellido": "Sistema"
    },
    "created_at": "2025-11-27T14:30:15Z"
  }
]
```

---

## 🔍 DEBUGGING

### Ver logs en Render
```bash
# Buscar errores relacionados con backups
grep -i "backup" logs.txt
grep -i "404" logs.txt | grep "backups"
```

### Verificar importación en Python
```python
import sys
sys.path.insert(0, '/path/to/project')

# Probar imports
from backups import models
from backups import views
from backups import serializers
from backups.models import BackupRecord

print("✅ Todos los imports funcionan")
```

### Test de URL patterns
```python
from django.urls import reverse

# Debe funcionar
url = reverse('backups:backup_history')
print(url)  # /api/backups/history/
```

---

## 📞 CONTACTO Y SOPORTE

Si los problemas persisten:
1. Verificar logs de Render
2. Confirmar que migraciones están aplicadas
3. Revisar variables de entorno de Supabase
4. Probar endpoints con Postman/Thunder Client

**Última actualización:** 27/11/2025  
**Versión:** 1.0
