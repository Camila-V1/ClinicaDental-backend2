# 08 - Comandos Frecuentes

## 🚀 Desarrollo Diario

### Iniciar Servidor
```bash
python manage.py runserver
```
- Admin público: `http://localhost:8000/admin/`
- Admin tenant: `http://clinica-demo.localhost:8000/admin/`

---

## 🗄️ Base de Datos

### Crear Migraciones
```bash
# Para una app específica
python manage.py makemigrations agenda

# Para todas las apps
python manage.py makemigrations
```

### Aplicar Migraciones

```bash
# Solo esquema público (SHARED_APPS)
python manage.py migrate_schemas --shared

# Todos los tenants (TENANT_APPS)
python manage.py migrate_schemas

# Un tenant específico
python manage.py migrate_schemas --schema=clinica_demo
```

### Ver Estado de Migraciones
```bash
# Ver todas
python manage.py showmigrations

# Ver de una app
python manage.py showmigrations agenda
```

---

## 👤 Usuarios y Tenants

### Crear Superusuario (en tenant)
```bash
# Para tenant específico
python manage.py shell
```
```python
from django_tenants.utils import schema_context
from usuarios.models import Usuario

with schema_context('clinica_demo'):
    Usuario.objects.create_superuser(
        email='admin@clinica.com',
        password='123456',
        nombre='Admin',
        apellido='Demo'
    )
```

### Crear Nueva Clínica (Tenant)
```bash
python manage.py shell
```
```python
from tenants.models import Clinica, Domain

# Crear tenant
clinica = Clinica(
    schema_name='clinica_nueva',
    nombre='Clínica Nueva',
    dominio='clinica-nueva.localhost',
    activo=True
)
clinica.save()

# Crear dominio
domain = Domain()
domain.domain = 'clinica-nueva.localhost'
domain.tenant = clinica
domain.is_primary = True
domain.save()
```

---

## 🧪 Testing y Verificación

### Ejecutar Verificación Completa
```bash
python verificar_sistema.py
```

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test

# App específica
python manage.py test agenda

# Test específico
python manage.py test agenda.tests.TestCitaModel
```

---

## 🔍 Debugging

### Django Shell
```bash
python manage.py shell
```

### Shell con modelos cargados
```bash
# Requiere django-extensions
pip install django-extensions

python manage.py shell_plus
```

### Ver URLs registradas
```bash
# Requiere django-extensions
python manage.py show_urls
```

### Ver información del tenant actual
```bash
python manage.py shell
```
```python
from django.db import connection
print(f"Schema actual: {connection.schema_name}")
```

### Inspeccionar Admin Site
```bash
python manage.py shell
```
```python
from django.contrib import admin

# Ver modelos registrados en admin.site estándar
print("Modelos en admin.site:")
for model in admin.site._registry.keys():
    print(f"  - {model._meta.app_label}.{model.__name__}")

# Ver modelos en public_admin
from core.urls_public import public_admin
print("\nModelos en public_admin:")
for model in public_admin._registry.keys():
    print(f"  - {model._meta.app_label}.{model.__name__}")
```

---

## 📦 Dependencias

### Instalar Nuevas Dependencias
```bash
pip install nombre-paquete
pip freeze > requirements.txt
```

### Actualizar Dependencias
```bash
pip install --upgrade nombre-paquete
pip freeze > requirements.txt
```

---

## 🔄 Git

### Workflow Normal
```bash
# Ver cambios
git status

# Agregar archivos
git add .

# Commit
git commit -m "Mensaje descriptivo"

# Push
git push origin main
```

### Ver Logs
```bash
# Últimos commits
git log --oneline -10

# Cambios en un archivo
git log -p archivo.py
```

---

## 🧹 Limpieza

### Limpiar Cache de Python
```bash
# Windows PowerShell
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Resetear Migraciones (⚠️ Desarrollo solamente)
```bash
# 1. Borrar archivos de migraciones (excepto __init__.py)
# 2. Borrar la base de datos
# 3. Crear todo de nuevo
python manage.py makemigrations
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

---

## 🔐 Variables de Entorno

### Ver Variable
```bash
# PowerShell
echo $env:DJANGO_SECRET_KEY

# Linux/Mac
echo $DJANGO_SECRET_KEY
```

### Establecer Variable (Sesión actual)
```bash
# PowerShell
$env:DJANGO_SECRET_KEY = "tu-clave-secreta"

# Linux/Mac
export DJANGO_SECRET_KEY="tu-clave-secreta"
```

---

## 📊 Estadísticas del Proyecto

### Contar Líneas de Código
```bash
# PowerShell
(Get-ChildItem -Recurse -Include *.py | Select-String .).Count

# Linux/Mac
find . -name "*.py" | xargs wc -l
```

### Ver Tamaño de Apps
```bash
# PowerShell
Get-ChildItem -Directory | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1KB
    [PSCustomObject]@{
        Folder = $_.Name
        SizeKB = [math]::Round($size, 2)
    }
} | Sort-Object SizeKB -Descending
```

---

## 🎓 Comandos por Tarea

### Agregar Nueva Funcionalidad
```bash
# 1. Crear app
python manage.py startapp nombre_app

# 2. Editar models.py, admin.py, etc.

# 3. Agregar a TENANT_APPS en settings.py

# 4. Crear migraciones
python manage.py makemigrations nombre_app

# 5. Aplicar migraciones
python manage.py migrate_schemas

# 6. Verificar
python verificar_sistema.py
```

### Actualizar Modelo Existente
```bash
# 1. Editar models.py

# 2. Crear migración
python manage.py makemigrations nombre_app

# 3. Revisar migración generada
cat nombre_app/migrations/000X_auto_YYYYMMDD_HHMM.py

# 4. Aplicar
python manage.py migrate_schemas

# 5. Verificar en admin
# Abrir admin tenant y ver cambios
```

---

## 🆘 Comandos de Emergencia

### Servidor no arranca
```bash
# Ver errores detallados
python manage.py check

# Ver problemas de migraciones
python manage.py showmigrations

# Ver configuración actual
python manage.py diffsettings
```

### Base de datos corrupta
```bash
# Backup primero!
# Luego resetear (SOLO desarrollo)
python manage.py flush --database=default
python manage.py migrate_schemas
```

---

**💡 Tip:** Crea aliases en PowerShell para comandos frecuentes:

```powershell
# En tu $PROFILE de PowerShell
function Run-Django { python manage.py runserver }
Set-Alias pyr Run-Django

function Django-Migrate { python manage.py migrate_schemas }
Set-Alias pym Django-Migrate

function Django-Shell { python manage.py shell }
Set-Alias pys Django-Shell
```

Ahora puedes usar: `pyr`, `pym`, `pys` 🚀
