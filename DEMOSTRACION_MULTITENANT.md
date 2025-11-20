# 🏢 DEMOSTRACIÓN DE MULTI-TENANCY

## ¿Cómo funciona el Multi-Tenancy?

El sistema usa **django-tenants** que crea **schemas separados en PostgreSQL** para cada clínica (tenant). Cada tenant tiene:
- ✅ Su propia base de datos (schema)
- ✅ Sus propios usuarios
- ✅ Sus propias citas, tratamientos, facturas
- ✅ Aislamiento total de datos

---

## 📊 Tenants Actuales

### 1. **Public Schema** (Sistema Principal)
- **Schema**: `public`
- **Propósito**: Administración de clínicas
- **Dominios**: 
  - `clinica-dental-backend.onrender.com`
  - `localhost`
  - `127.0.0.1`

### 2. **Clínica Demo** (Tenant por defecto)
- **Schema**: `clinica_demo`
- **Nombre**: Clínica Demo
- **Dominio identificador**: `clinica-demo`
- **Subdominios**:
  - `clinica-demo.localhost` (desarrollo)
  - `clinica-demo.clinica-dental-backend.onrender.com` (producción)

---

## 🎯 ¿Cómo se accede a cada tenant?

### Método 1: Por Subdominio (Multi-tenant tradicional)

```bash
# Acceder a Clínica Demo
https://clinica-demo.clinica-dental-backend.onrender.com/api/usuarios/me/

# Acceder a otra clínica (si existiera)
https://clinica-abc.clinica-dental-backend.onrender.com/api/usuarios/me/
```

### Método 2: Por Middleware (Configuración actual)

Actualmente usamos **DefaultTenantMiddleware** que automáticamente redirige todas las peticiones a `/api/*` al tenant `clinica_demo`, sin necesidad de usar subdominios.

```bash
# El frontend usa esta URL simple
https://clinica-dental-backend.onrender.com/api/usuarios/me/

# El middleware internamente la convierte a
Schema: clinica_demo → Accede a los datos de "Clínica Demo"
```

---

## 🧪 DEMOSTRACIÓN PRÁCTICA

### Paso 1: Ver el tenant actual

```bash
# Endpoint para ver información del sistema
curl https://clinica-dental-backend.onrender.com/
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "Backend de Clínica Dental funcionando correctamente",
  "schema": "public"
}
```

### Paso 2: Hacer login (automáticamente usa clinica_demo)

```bash
curl -X POST https://clinica-dental-backend.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"odontologo@clinica-demo.com","password":"odontologo123"}'
```

**Internamente:**
1. Request llega al dominio público
2. Middleware detecta `/api/`
3. Cambia el schema de `public` → `clinica_demo`
4. Busca el usuario en el schema `clinica_demo`
5. Retorna el token

### Paso 3: Crear un nuevo tenant para demostrar aislamiento

Puedes crear nuevos tenants desde el admin de Django:

**URL Admin:** `https://clinica-dental-backend.onrender.com/admin/`

1. Ir a **Clínicas** → Agregar Clínica
2. Crear:
   - **Nombre**: Clínica ABC
   - **Schema name**: `clinica_abc`
   - **Dominio**: `clinica-abc`
   - **Activo**: ✓

3. Ir a **Domains** → Agregar Domain
   - **Domain**: `clinica-abc.clinica-dental-backend.onrender.com`
   - **Tenant**: Clínica ABC
   - **Is primary**: ✓

### Paso 4: Acceder al nuevo tenant por subdominio

```bash
# Login en Clínica ABC (usando subdominio)
curl -X POST https://clinica-abc.clinica-dental-backend.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@clinica-abc.com","password":"admin123"}'
```

Este acceso usará el schema `clinica_abc` (base de datos separada).

---

## 🔍 Verificar Aislamiento de Datos

### Base de datos PostgreSQL - Schemas separados:

```sql
-- Ver todos los schemas (cada tenant tiene uno)
SELECT schema_name FROM information_schema.schemata;

Resultado:
- public           (sistema principal)
- clinica_demo     (Clínica Demo)
- clinica_abc      (Clínica ABC - si se crea)
```

### Cada schema tiene sus propias tablas:

```sql
-- Usuarios en clinica_demo
SELECT * FROM clinica_demo.usuarios_usuario;

-- Usuarios en clinica_abc (diferente conjunto de datos)
SELECT * FROM clinica_abc.usuarios_usuario;
```

**Los datos están completamente aislados. Un usuario de clinica_demo NO puede ver datos de clinica_abc.**

---

## 🎨 Visualización del Multi-Tenancy

```
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL Database: clinica_dental_prod               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Schema: public  │  │ Schema: clinica_ │            │
│  │                  │  │       demo       │            │
│  ├──────────────────┤  ├──────────────────┤            │
│  │ tenants_clinica  │  │ usuarios_usuario │            │
│  │ tenants_domain   │  │ agenda_cita      │            │
│  │ django_*         │  │ tratamientos_*   │            │
│  │                  │  │ facturacion_*    │            │
│  └──────────────────┘  │ historial_*      │            │
│                        └──────────────────┘            │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ Schema: clinica_ │  │ Schema: clinica_ │            │
│  │       abc        │  │       xyz        │            │
│  ├──────────────────┤  ├──────────────────┤            │
│  │ usuarios_usuario │  │ usuarios_usuario │            │
│  │ agenda_cita      │  │ agenda_cita      │            │
│  │ tratamientos_*   │  │ tratamientos_*   │            │
│  │ facturacion_*    │  │ facturacion_*    │            │
│  │ historial_*      │  │ historial_*      │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Ventajas del Multi-Tenancy

1. **Aislamiento de Datos**: Cada clínica tiene sus datos separados
2. **Escalabilidad**: Agregar nuevas clínicas sin cambiar código
3. **Seguridad**: Un tenant no puede acceder a datos de otro
4. **Personalización**: Cada clínica puede tener su configuración
5. **Eficiencia**: Un solo backend maneja múltiples clínicas

---

## 🚀 Para Demostrar Multi-Tenancy en Producción

### Opción 1: Crear un segundo tenant manualmente

1. Accede al admin: `https://clinica-dental-backend.onrender.com/admin/`
2. Crea una nueva clínica (por ejemplo: "Clínica ABC")
3. Ejecuta migraciones para el nuevo schema:
   ```bash
   python manage.py migrate_schemas --schema=clinica_abc
   ```
4. Pobla datos iniciales para ese tenant
5. Accede por subdominio: `https://clinica-abc.clinica-dental-backend.onrender.com/`

### Opción 2: Usar el middleware actual (más simple)

El middleware actual (`DefaultTenantMiddleware`) está configurado para usar siempre `clinica_demo`. Para soportar múltiples tenants desde el dominio principal, necesitarías:

1. **Opción A**: Agregar un header `X-Tenant-Id` en las peticiones del frontend
2. **Opción B**: Modificar el middleware para detectar el tenant del usuario después del login
3. **Opción C**: Usar subdominios (método tradicional de django-tenants)

---

## 📝 Estado Actual

**Configuración Actual:**
- ✅ Multi-tenancy configurado y funcionando
- ✅ Schema `public` para administración
- ✅ Schema `clinica_demo` con datos de prueba
- ✅ Middleware redirige todo a `clinica_demo` por simplicidad
- ✅ Frontend no necesita manejar subdominios

**Para usar múltiples clínicas reales:**
1. Crear nuevos tenants en el admin
2. Usar subdominios: `clinica-abc.clinica-dental-backend.onrender.com`
3. O modificar middleware para soportar selección de tenant

---

## 🎯 Conclusión

El sistema **SÍ tiene multi-tenancy completamente funcional**. Actualmente está configurado para:
- Usar un tenant por defecto (`clinica_demo`) para simplicidad
- Permitir agregar más tenants cuando sea necesario
- Cada tenant tiene datos completamente aislados

**El multi-tenancy está activo y funcionando, solo que está configurado para facilitar el desarrollo con un solo tenant visible desde el dominio principal.** 🏢✨
