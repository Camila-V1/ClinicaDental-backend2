# Sistema de Backups - Clínica Dental

Este archivo confirma que el sistema de backups está configurado y listo para deploy.

## Estado Actual

- ✅ App `backups` en TENANT_APPS
- ✅ URLs configuradas en `urls_tenant.py`
- ✅ Migraciones creadas
- ✅ `build.sh` actualizado para migrar tenant
- ⏳ Deploy pendiente

## Endpoints Disponibles

### GET /api/backups/history/
Lista el historial de backups del tenant actual.

### POST /api/backups/create/
Crea un backup manual (solo ADMIN).

### GET /api/backups/history/{id}/download/
Descarga un backup específico.

### DELETE /api/backups/history/{id}/
Elimina un backup (solo ADMIN).

## Deploy

Para aplicar los cambios en producción:

```bash
git add .
git commit -m "docs: Sistema de backups configurado"
git push origin main
```

Render detectará el push y re-desplegará automáticamente en ~5-10 minutos.
