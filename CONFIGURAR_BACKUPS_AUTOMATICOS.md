# 🔄 Configurar Backups Automáticos en Render

## 📋 Resumen

Este sistema permite crear backups automáticos del tenant `clinica_demo` usando un **Cron Job** en Render.

---

## 🛠️ Configuración en Render Dashboard

### Paso 1: Crear un Cron Job

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Selecciona tu servicio: `clinica-dental-backend`
3. En el menú lateral, haz clic en **"Cron Jobs"**
4. Clic en **"New Cron Job"**

### Paso 2: Configurar el Cron Job

**Nombre:** `Backup Automático Diario`

**Comando:**
```bash
python manage.py crear_backup_automatico --tenant=clinica_demo
```

**Schedule (Cron Expression):**

Elige una de estas opciones:

#### Opción 1: Backup Diario a las 3:00 AM (UTC)
```
0 3 * * *
```

#### Opción 2: Backup cada 12 horas (3 AM y 3 PM UTC)
```
0 3,15 * * *
```

#### Opción 3: Backup cada 6 horas
```
0 */6 * * *
```

#### Opción 4: Backup semanal (Domingos a las 3 AM)
```
0 3 * * 0
```

**Región:** Selecciona la misma región de tu servicio (Oregon)

**Environment:** Production (hereda las variables de entorno de tu servicio)

### Paso 3: Guardar

Haz clic en **"Create Cron Job"**

---

## 🧪 Probar Manualmente

### Desde tu terminal local:

```bash
# Probar localmente (requiere configuración de Supabase)
python manage.py crear_backup_automatico

# Probar con otro tenant
python manage.py crear_backup_automatico --tenant=clinica_demo
```

### Desde Render Shell:

1. Ve a tu servicio en Render
2. Clic en **"Shell"** en el menú
3. Ejecuta:
```bash
python manage.py crear_backup_automatico
```

---

## 📊 Verificar Backups Creados

### Desde el Frontend:

1. Inicia sesión como ADMIN
2. Ve a **Configuración > Backups**
3. Verás la lista de backups con:
   - ✅ Fecha y hora
   - ✅ Tipo: "Automático" o "Manual"
   - ✅ Tamaño del archivo
   - ✅ Botón de descarga

### Desde la API:

```bash
# Obtener historial de backups
curl -X GET "https://clinica-dental-backend.onrender.com/api/backups/history/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-ID: clinica_demo"
```

---

## 🔍 Logs y Monitoreo

### Ver logs del Cron Job en Render:

1. Ve a tu servicio en Render
2. Clic en **"Cron Jobs"**
3. Clic en el nombre del job
4. Verás los logs de cada ejecución

### Logs que deberías ver:

```
📦 Creando backup automático para clinica_demo...
☁️  Subiendo a Supabase...
✅ Backup automático creado exitosamente
   ID: 123
   Archivo: backup-auto-json-clinica_demo-2025-11-27-120000.json
   Tamaño: 245.67 KB
   Fecha: 2025-11-27 12:00:00
```

---

## 📝 Tipos de Backup

El sistema diferencia entre:

### Backup Manual
- Creado por un usuario ADMIN desde el frontend
- Campo `backup_type = 'manual'`
- Campo `created_by` = usuario que lo creó

### Backup Automático
- Creado por el Cron Job
- Campo `backup_type = 'automatico'`
- Campo `created_by` = NULL

---

## 🗑️ Limpieza Automática (Opcional)

Para evitar acumulación de backups antiguos, puedes crear otro comando:

```bash
# Eliminar backups mayores a 30 días
python manage.py limpiar_backups_antiguos --dias=30
```

---

## ⚠️ Troubleshooting

### El Cron Job no se ejecuta:

1. Verifica que el schedule (cron expression) sea válido
2. Revisa los logs del Cron Job en Render
3. Asegúrate de que las variables de entorno de Supabase estén configuradas

### Error "Tenant no encontrado":

- Verifica que el tenant `clinica_demo` exista en la tabla `tenants_clinica`
- Usa el schema correcto: `--tenant=clinica_demo`

### Error al subir a Supabase:

- Verifica las credenciales en variables de entorno:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SUPABASE_BUCKET_NAME`

---

## 📚 Referencias

- Render Cron Jobs: https://render.com/docs/cronjobs
- Cron Expression Guide: https://crontab.guru/
- Django Management Commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/

---

## ✅ Estado Actual

- ✅ Comando de backup automático creado
- ✅ Endpoint de historial funcionando (200 OK)
- ✅ Frontend muestra backups correctamente
- ⏳ Pendiente: Configurar Cron Job en Render (requiere acceso al dashboard)

---

**Última actualización:** 27 de noviembre de 2025
