# 🚀 CONFIGURACIÓN CORRECTA DE RENDER

## ❌ PROBLEMA ACTUAL

El **Build Command** del CRON JOB está mal configurado en el dashboard de Render.

Esto causa el error:
```
ModuleNotFoundError: No module named 'django'
```

---

## ✅ SOLUCIÓN

### 1️⃣ Configuración del CRON JOB en Dashboard de Render

Ingresa a: https://dashboard.render.com/cron/backup-automatico-cron/settings

**Build Command** debe ser:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Command** (este sí ejecuta el backup):
```bash
python manage.py run_scheduled_backups
```

**Schedule**: `0 * * * *` (cada hora)

---

### 2️⃣ Configuración del WEB SERVICE

El web service (backend principal) debe tener:

**Build Command**:
```bash
bash build.sh
```

**Start Command**:
```bash
gunicorn core.wsgi:application
```

---

## 📝 PASOS PARA CORREGIR

1. Ve a: https://dashboard.render.com/
2. Selecciona el servicio: **backup-automatico-cron**
3. Ve a **Settings** → **Build & Deploy**
4. Cambia:
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Command**: `python manage.py run_scheduled_backups`
5. Click en **Save Changes**
6. El servicio se reconstruirá automáticamente

---

## 🔍 VERIFICACIÓN

Después de corregir, el build debería mostrar:

```bash
==> Running build command 'pip install --upgrade pip && pip install -r requirements.txt'...
==> Collecting Django==5.2.6
==> Installing collected packages: Django...
==> Successfully installed Django-5.2.6

==> Running command 'python manage.py run_scheduled_backups'...
[2025-11-27 09:30:00] INFO: Verificando backups programados...
✅ No hay backups programados en este momento
```

---

## 📋 RESUMEN DE COMANDOS CORRECTOS

| Servicio | Build Command | Start/Command |
|----------|---------------|---------------|
| **Web Service** | `bash build.sh` | `gunicorn core.wsgi:application` |
| **Cron Job** | `pip install --upgrade pip && pip install -r requirements.txt` | `python manage.py run_scheduled_backups` |

---

**Última actualización:** 27/11/2025
