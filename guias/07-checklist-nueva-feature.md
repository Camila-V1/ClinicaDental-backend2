# 07 - Checklist: Nueva Funcionalidad

## ✅ Para Modelos de NEGOCIO (lo más común)

### Ejemplo: Agregar módulo de Agenda

```
□ 1. Crear modelo en agenda/models.py
     ├─ Definir campos
     ├─ Agregar Meta class
     └─ Definir __str__()

□ 2. Registrar en agenda/admin.py
     └─ Usar @admin.register(Modelo)  ← IMPORTANTE

□ 3. Crear serializer en agenda/serializers.py
     ├─ Definir campos
     └─ Agregar validaciones

□ 4. Crear views en agenda/views.py
     ├─ ViewSet o APIView
     ├─ permission_classes
     └─ get_queryset() con filtros

□ 5. Crear URLs en agenda/urls.py
     └─ Router o path()

□ 6. ⚠️ Incluir en core/urls_tenant.py
     └─ path('api/agenda/', include('agenda.urls'))

□ 7. Agregar a TENANT_APPS en settings.py
     └─ 'agenda' en la lista

□ 8. Crear migraciones
     └─ python manage.py makemigrations agenda

□ 9. Aplicar migraciones
     └─ python manage.py migrate_schemas

□ 10. Verificar
      ├─ Visitar admin: clinica-demo.localhost:8000/admin/
      ├─ Probar API: /api/agenda/...
      └─ python verificar_sistema.py
```

---

## 🔍 Verificación Rápida

### ¿El modelo aparece donde debe?

```bash
# 1. Verificar que NO esté en admin público
Abrir: http://localhost:8000/admin/
Buscar: ¿Aparece tu modelo? → ❌ NO debe aparecer

# 2. Verificar que SÍ esté en admin tenant
Abrir: http://clinica-demo.localhost:8000/admin/
Buscar: ¿Aparece tu modelo? → ✅ SÍ debe aparecer
```

### ¿La API funciona?

```bash
# Probar con curl o Postman
GET http://clinica-demo.localhost:8000/api/agenda/citas/
Authorization: Bearer <token>

# Debe retornar 200 OK con lista de citas (o [])
```

---

## ⚠️ Errores Comunes

### ❌ Error 1: Modelo en admin incorrecto
**Síntoma:** "Agenda" aparece en localhost:8000/admin/

**Causa:** Registraste en core/urls_public.py por error

**Solución:**
```python
# Eliminar de core/urls_public.py
# Agregar en agenda/admin.py con @admin.register
```

---

### ❌ Error 2: API da 404
**Síntoma:** GET /api/agenda/citas/ → 404 Not Found

**Causa:** No incluiste en core/urls_tenant.py

**Solución:**
```python
# core/urls_tenant.py
urlpatterns = [
    # ...
    path('api/agenda/', include('agenda.urls')),  # ← Agregar
]
```

---

### ❌ Error 3: Migración no funciona
**Síntoma:** "No migrations to apply"

**Causa:** App no está en TENANT_APPS

**Solución:**
```python
# core/settings.py
TENANT_APPS = [
    # ...
    'agenda',  # ← Agregar
]
```

---

## 🧪 Test Manual Completo

```python
# 1. Admin tenant
http://clinica-demo.localhost:8000/admin/
→ Login: admin@clinica.com / 123456
→ ¿Ves tu modelo? ✅

# 2. Admin público
http://localhost:8000/admin/
→ ¿NO ves tu modelo? ✅

# 3. API - List
GET http://clinica-demo.localhost:8000/api/agenda/citas/
Authorization: Bearer <token>
→ Status: 200 ✅

# 4. API - Create
POST http://clinica-demo.localhost:8000/api/agenda/citas/
Authorization: Bearer <token>
Content-Type: application/json
{
  "paciente": 1,
  "odontologo": 1,
  "fecha_hora": "2025-11-10T10:00:00Z",
  "motivo": "Limpieza"
}
→ Status: 201 ✅

# 5. Verificación automática
python verificar_sistema.py
→ 100% ✅
```

---

## 📋 Comandos Útiles

```bash
# Ver apps instaladas en tenant
python manage.py shell_plus
from django.apps import apps
for app in apps.get_app_configs():
    print(app.name)

# Ver modelos registrados en admin
python manage.py shell
from django.contrib import admin
print(admin.site._registry.keys())

# Ver URLs disponibles
python manage.py show_urls  # (requiere django-extensions)

# Verificar migraciones pendientes
python manage.py showmigrations agenda
```

---

## 🎓 Siguiente Lectura

- **Comandos frecuentes:** [08-comandos-frecuentes.md](08-comandos-frecuentes.md)
- **Debugging:** [09-debugging-admin.md](09-debugging-admin.md)
- **Ejemplo completo:** [11-ejemplo-agenda.md](11-ejemplo-agenda.md)
