# 🚀 GUÍA DE DEPLOYMENT EN RENDER

## 📋 Checklist Pre-Deployment

Antes de hacer deploy, verifica que tengas:

- [x] `requirements.txt` con todas las dependencias
- [x] `.env.example` con variables de ejemplo
- [x] `.gitignore` configurado (no subir .env)
- [x] `build.sh` con permisos de ejecución
- [x] `render.yaml` configurado
- [x] `settings.py` usando variables de entorno
- [x] Script de población de datos (`poblar_sistema_completo.py`)

---

## 🎯 Paso a Paso: Deployment en Render

### 1. **Preparar el Repositorio**

```bash
# Asegúrate de que todos los archivos estén en git
git status

# Agregar archivos nuevos
git add .

# Commit
git commit -m "Preparar para deployment en Render"

# Push a GitHub
git push origin main
```

### 2. **Crear Cuenta en Render**

1. Ve a [https://render.com](https://render.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza a Render para acceder a tus repositorios

### 3. **Configurar Base de Datos PostgreSQL**

**⚠️ IMPORTANTE:** Render solo permite 1 base de datos gratuita por cuenta.

#### **Si YA TIENES una BD PostgreSQL en Render:**
1. Ve a tu base de datos existente en el Dashboard
2. Copia la **Internal Database URL** (formato: `postgresql://user:pass@host/dbname`)
3. **Salta al Paso 4** y úsala en la variable `DATABASE_URL`

#### **Si NO TIENES ninguna BD en Render:**
1. Desde el Dashboard de Render, click en **"New +"**
2. Selecciona **"PostgreSQL"**
3. Configura:
   - **Name:** `clinica-dental-db`
   - **Database:** `clinica_dental_prod`
   - **User:** `clinica_user`
   - **Region:** Oregon (o tu preferencia)
   - **Plan:** Free
4. Click en **"Create Database"**
5. **Guarda la Internal Database URL**

#### **Si el error persiste:**
- Verifica cuántas BDs tienes: Dashboard → PostgreSQL
- Elimina BDs que no uses: Settings → Delete Database
- O usa una cuenta diferente de Render

### 4. **Crear Web Service**

1. Desde el Dashboard, click en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio `ClinicaDental-backend2`
5. Configura:
   - **Name:** `clinica-dental-backend`
   - **Region:** Oregon (misma que la BD)
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío)
   - **Runtime:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn core.wsgi:application`

### 5. **Configurar Variables de Entorno**

En la sección **"Environment"**, agrega estas variables:

#### Variables Básicas:
```
PYTHON_VERSION=3.11.9
DEBUG=False
```

#### Secret Key (genera una nueva):
```bash
# Ejecuta esto localmente para generar una clave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
```
SECRET_KEY=tu-clave-generada-aqui
```

#### Hosts y CORS:
```
# ALLOWED_HOSTS: Permite subdominios de onrender.com (multi-tenant)
ALLOWED_HOSTS=.onrender.com

# CORS: Permitir peticiones del frontend
# Nota: Los subdominios ya están permitidos por regex en settings.py
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app

# CSRF: Permitir subdominios (wildcards) para multi-tenant
# Nota: Django 4.0+ soporta wildcards con *
CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://*.vercel.app
```

#### Base de Datos:
```
DATABASE_URL=[copia aquí la Internal Database URL de tu PostgreSQL]
```

Ejemplo de DATABASE_URL:
```
postgresql://clinica_user:password@dpg-xxxxx.oregon-postgres.render.com/clinica_dental_prod
```

#### Variables del Tenant:
```
DEFAULT_TENANT_SCHEMA=clinica_demo
DEFAULT_TENANT_DOMAIN=clinica-demo
```

### 6. **Dar Permisos al build.sh**

Antes de hacer el primer deploy, asegúrate de que `build.sh` tenga permisos de ejecución:

```bash
# En tu máquina local
chmod +x build.sh

# Commit y push
git add build.sh
git commit -m "Add execution permissions to build.sh"
git push origin main
```

### 7. **Deploy**

1. Click en **"Create Web Service"**
2. Render comenzará a:
   - Clonar tu repositorio
   - Instalar dependencias
   - Ejecutar `build.sh`
   - Iniciar el servidor con gunicorn

### 8. **Monitorear el Deploy**

En la consola de logs verás:
```
🚀 INICIANDO BUILD DEL BACKEND - CLÍNICA DENTAL
📦 Instalando dependencias de Python...
📂 Recolectando archivos estáticos...
🔄 Ejecutando migraciones de base de datos...
🌱 Poblando datos iniciales del sistema...
✅ BUILD COMPLETADO EXITOSAMENTE
```

### 9. **Verificar que Funciona**

Tu backend estará disponible en:
```
https://clinica-dental-backend.onrender.com
```

Prueba estos endpoints:
```
GET  https://clinica-dental-backend.onrender.com/api/
POST https://clinica-dental-backend.onrender.com/api/token/
```

Login de prueba:
```json
{
  "email": "admin@clinica-demo.com",
  "password": "admin123"
}
```

---

## 🔧 Configuración Post-Deploy

### ¿Cómo Funciona el Multi-Tenant con Subdominios?

Tu backend ahora soporta **subdominios dinámicos** para cada clínica registrada:

```
https://clinica1.onrender.com  → Tenant: clinica1
https://clinica2.onrender.com  → Tenant: clinica2
https://tu-app.onrender.com    → Tenant público (registro)
```

**Configuración aplicada:**
- ✅ `ALLOWED_HOSTS=.onrender.com` permite `*.onrender.com`
- ✅ `CORS_ALLOWED_ORIGIN_REGEXES` permite subdominios de Render, Vercel, Netlify
- ✅ `CSRF_TRUSTED_ORIGINS` usa wildcards `https://*.onrender.com`

### Conectar Frontend

Actualiza tu frontend para apuntar a Render:

```typescript
// axiosCore.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com';
```

En tu archivo `.env` del frontend:
```
VITE_API_URL=https://clinica-dental-backend.onrender.com
```

### Configurar Dominio Personalizado (Opcional)

1. En Render, ve a tu servicio
2. Click en **"Settings"** → **"Custom Domain"**
3. Agrega tu dominio: `api.tuclinica.com`
4. Configura el DNS según las instrucciones de Render

---

## 📊 Credenciales Creadas Automáticamente

El script `poblar_sistema_completo.py` crea:

### Admin:
```
Email: admin@clinica-demo.com
Password: admin123
```

### Odontólogo:
```
Email: odontologo@clinica-demo.com
Password: password123
```

### Pacientes (5):
```
Email: paciente1@test.com a paciente5@test.com
Password: password123
```

### Datos Incluidos:
- ✅ Tenant: clinica-demo
- ✅ 5 pacientes con perfiles completos
- ✅ 1 odontólogo con especialidad
- ✅ 10+ servicios odontológicos
- ✅ 20+ insumos en inventario
- ✅ Citas programadas
- ✅ Episodios de atención
- ✅ Odontogramas
- ✅ Planes de tratamiento
- ✅ Facturas y pagos

---

## 🐛 Troubleshooting

### Error: "relation 'facturacion_pago' does not exist"
**Problema:** Las migraciones del tenant no se ejecutaron, solo las compartidas.
**Solución:** El `build.sh` ahora crea automáticamente el tenant y ejecuta sus migraciones. Si ya hiciste deploy:
```bash
# En Render Shell
python manage.py shell
>>> from tenants.models import Clinica
>>> Clinica.objects.create(schema_name='clinica_demo', name='Clínica Demo', domain_url='clinica-demo', telefono='000-0000', direccion='Dirección de prueba', activo=True)
>>> exit()
python manage.py migrate_schemas --schema=clinica_demo
python poblar_sistema_completo.py
```

### Error: "relation does not exist"
**Solución:** Las migraciones no se ejecutaron correctamente.
```bash
# En Render Shell
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --schema=clinica_demo
```

### Error: "No module named 'decouple'"
**Solución:** Asegúrate de que `python-decouple` esté en `requirements.txt`

### Error: "SECRET_KEY must not be empty"
**Solución:** Verifica que la variable `SECRET_KEY` esté configurada en Render.

### El sitio carga lento la primera vez
**Solución:** Normal en el plan Free de Render. El servicio se "duerme" después de 15 minutos de inactividad.

### Error de CORS
**Solución:** Verifica que `CORS_ALLOWED_ORIGINS` incluya la URL de tu frontend.

---

## 📝 Comandos Útiles en Render Shell

Para acceder a la shell de Render:
1. Ve a tu servicio en Render
2. Click en **"Shell"** en el menú superior

Comandos útiles:
```bash
# Ver usuarios
python manage.py tenant_command shell --schema=clinica_demo

# Crear superusuario manualmente
python manage.py tenant_command createsuperuser --schema=clinica_demo

# Ver logs
python manage.py check --deploy

# Ejecutar migraciones
python manage.py migrate_schemas --shared
```

---

## 🔄 Actualizaciones Continuas

Cada vez que hagas `git push` a la rama `main`, Render automáticamente:
1. Detectará los cambios
2. Ejecutará `build.sh`
3. Reiniciará el servicio
4. **NOTA:** Los datos no se borrarán, solo se ejecutarán migraciones nuevas

---

## 💰 Costos

### Plan Free:
- ✅ 750 horas/mes (suficiente para un proyecto)
- ✅ Se "duerme" después de 15 minutos sin actividad
- ✅ Tarda ~30 segundos en "despertar"
- ✅ PostgreSQL 1GB gratis

### Upgrade a Starter ($7/mes):
- ✅ Sin límite de horas
- ✅ Sin hibernación
- ✅ Más recursos (RAM/CPU)
- ✅ PostgreSQL 10GB

---

## 🎉 ¡Listo!

Tu backend está en producción en:
```
https://clinica-dental-backend.onrender.com
```

Panel Admin:
```
https://clinica-dental-backend.onrender.com/admin/
```

API:
```
https://clinica-dental-backend.onrender.com/api/
```

---

## 📞 Soporte

- **Documentación Render:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **Django Tenants:** https://django-tenants.readthedocs.io/

---

**¡Tu sistema de clínica dental está en producción! 🦷✨**
