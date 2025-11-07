# 13 - Cómo Verificar el Sistema

## 🧪 Verificación Automática

### Ejecutar Script de Verificación
```bash
python verificar_sistema.py
```

Este script verifica **9 aspectos** del sistema:

1. ✅ Admin público accesible sin login
2. ✅ Admin público con modelos correctos (Clínicas, Domains)
3. ✅ Admin tenant requiere autenticación
4. ✅ Admin tenant login funcional
5. ✅ Admin tenant con modelos correctos (NO públicos)
6. ✅ API de registro funcional
7. ✅ API de login JWT funcional
8. ✅ API de usuario actual funcional
9. ✅ Aislamiento de datos verificado

### Resultado Esperado
```
🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
El sistema multi-tenant está funcionando correctamente.

Pruebas ejecutadas: 9
Pruebas exitosas: 9
Pruebas fallidas: 0

Porcentaje de éxito: 100.0%
```

---

## 🔍 Verificación Manual

### 1. Verificar Admin Público

**URL:** `http://localhost:8000/admin/`

**✅ Debe cumplir:**
- [ ] Se abre sin pedir login
- [ ] Muestra "Administración del Sistema Multi-Tenant"
- [ ] Tiene sección "TENANTS (ADMINISTRACIÓN DE CLÍNICAS)"
- [ ] Tiene modelo "Clínicas"
- [ ] Tiene modelo "Domains"
- [ ] **NO** tiene "Usuarios"
- [ ] **NO** tiene "Perfiles"
- [ ] **NO** tiene "Agenda"

**❌ Si falla:**
Ver: [09-debugging-admin.md](09-debugging-admin.md)

---

### 2. Verificar Admin Tenant

**URL:** `http://clinica-demo.localhost:8000/admin/`

**✅ Debe cumplir:**
- [ ] Redirige a `/admin/login/`
- [ ] Pide email y password
- [ ] Login con `admin@clinica.com` / `123456` funciona
- [ ] Muestra "Django administration"
- [ ] Tiene sección "USUARIOS"
- [ ] Tiene modelo "Usuarios"
- [ ] Tiene modelo "Perfiles Odontólogos"
- [ ] Tiene modelo "Perfiles Pacientes"
- [ ] **NO** tiene sección "TENANTS"
- [ ] **NO** tiene "Clínicas" ni "Domains"

**❌ Si falla:**
Ver: [09-debugging-admin.md](09-debugging-admin.md)

---

### 3. Verificar API de Registro

**Endpoint:** `POST http://clinica-demo.localhost:8000/api/usuarios/register/`

**Request:**
```json
{
  "email": "test@test.com",
  "password": "password123",
  "password2": "password123",
  "nombre": "Test",
  "apellido": "User",
  "fecha_de_nacimiento": "1990-01-01",
  "direccion": "Calle Test 123"
}
```

**✅ Respuesta esperada (201 Created):**
```json
{
  "message": "Usuario registrado exitosamente",
  "usuario": {
    "id": 2,
    "email": "test@test.com",
    "nombre": "Test",
    "apellido": "User",
    "tipo_usuario": "PACIENTE"
  }
}
```

---

### 4. Verificar API de Login JWT

**Endpoint:** `POST http://clinica-demo.localhost:8000/api/token/`

**Request:**
```json
{
  "email": "admin@clinica.com",
  "password": "123456"
}
```

**✅ Respuesta esperada (200 OK):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 5. Verificar API de Usuario Actual

**Endpoint:** `GET http://clinica-demo.localhost:8000/api/usuarios/me/`

**Headers:**
```
Authorization: Bearer <access_token_del_paso_anterior>
```

**✅ Respuesta esperada (200 OK):**
```json
{
  "id": 1,
  "email": "admin@clinica.com",
  "nombre": "Administrador",
  "apellido": "Demo",
  "tipo_usuario": "ADMIN",
  "is_active": true,
  "is_staff": true
}
```

---

## 🔧 Verificación con Navegador

### Test 1: Hosts Configurado
```bash
# Windows
notepad C:\Windows\System32\drivers\etc\hosts
```

**Debe contener:**
```
127.0.0.1   clinica-demo.localhost
```

**Test:**
Abrir: `http://clinica-demo.localhost:8000/admin/`
- ✅ Debe cargar (redirigir a login)
- ❌ "No se puede acceder" → Hosts no configurado

---

### Test 2: Servidor Corriendo
```bash
python manage.py runserver
```

**Verificar:**
```
Starting development server at http://127.0.0.1:8000/
```

**Test:**
Abrir: `http://localhost:8000/admin/`
- ✅ Debe cargar admin público
- ❌ Error → Servidor no está corriendo

---

## 📊 Verificación de Base de Datos

### Ver Esquemas
```bash
python manage.py shell
```
```python
from django.db import connection

# Ver esquema actual
print(connection.schema_name)

# Listar todos los esquemas
from tenants.models import Clinica
for clinica in Clinica.objects.all():
    print(f"Schema: {clinica.schema_name}")
```

### Ver Tablas en Esquema
```bash
python manage.py dbshell
```
```sql
-- Ver esquema actual
SELECT current_schema();

-- Listar schemas
SELECT schema_name FROM information_schema.schemata;

-- Ver tablas en public
\dt public.*

-- Ver tablas en clinica_demo
\dt clinica_demo.*
```

---

## 🎯 Checklist Post-Desarrollo

Después de agregar una nueva funcionalidad, verifica:

```
□ 1. Servidor inicia sin errores
     → python manage.py runserver

□ 2. Admin público NO tiene tu nuevo modelo
     → http://localhost:8000/admin/

□ 3. Admin tenant SÍ tiene tu nuevo modelo
     → http://clinica-demo.localhost:8000/admin/

□ 4. Puedes crear instancias desde admin tenant
     → Probar "Add" en tu modelo

□ 5. API retorna 200/201 (no 404)
     → GET/POST http://clinica-demo.localhost:8000/api/<tu-app>/

□ 6. API requiere JWT (si debe requerirlo)
     → Request sin token → 401 Unauthorized

□ 7. Verificación automática pasa
     → python verificar_sistema.py → 100%
```

---

## 🐛 Problemas Comunes

### Problema: verify_sistema.py falla

**Error:** `Connection refused`

**Solución:**
```bash
# 1. Verificar que el servidor esté corriendo
python manage.py runserver

# 2. En otra terminal, ejecutar
python verificar_sistema.py
```

---

### Problema: Admin tenant muestra modelos públicos

**Error:** Ves "Clínicas" y "Domains" en admin tenant

**Solución:**
1. Abrir `tenants/admin.py`
2. Verificar que **NO** tenga `@admin.register(Clinica)`
3. Reiniciar servidor
4. Ver: [09-debugging-admin.md](09-debugging-admin.md)

---

### Problema: API da 404

**Error:** `GET /api/agenda/citas/ → 404`

**Solución:**
```python
# 1. Verificar en core/urls_tenant.py
urlpatterns = [
    # ...
    path('api/agenda/', include('agenda.urls')),  # ← Debe estar aquí
]

# 2. Reiniciar servidor
# 3. Verificar que uses URL tenant (no público):
# ✅ http://clinica-demo.localhost:8000/api/agenda/citas/
# ❌ http://localhost:8000/api/agenda/citas/
```

---

## 📝 Log de Verificación

Guarda un registro de tus verificaciones:

```
Fecha: 2025-11-06
Funcionalidad: Módulo Agenda
Desarrollador: Tu Nombre

□ Admin público: ✅ No muestra Agenda
□ Admin tenant: ✅ Muestra Agenda con 3 citas
□ API List: ✅ GET /api/agenda/citas/ → 200 OK
□ API Create: ✅ POST /api/agenda/citas/ → 201 Created
□ API con JWT: ✅ Sin token → 401 Unauthorized
□ Verificación auto: ✅ 100% (9/9 tests)

Estado: ✅ APROBADO
```

---

## 🎓 Herramientas Recomendadas

### Para Testing de APIs
- **Thunder Client** (extensión VS Code)
- **Postman**
- **Insomnia**

### Para Base de Datos
- **pgAdmin** (PostgreSQL GUI)
- **DBeaver** (universal DB tool)

### Para Debugging
- **Django Debug Toolbar**
  ```bash
  pip install django-debug-toolbar
  ```

---

**💡 Tip Final:** Ejecuta `python verificar_sistema.py` antes y después de cada feature nueva. Es tu red de seguridad. 🛡️
