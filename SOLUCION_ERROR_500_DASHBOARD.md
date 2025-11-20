# 🔧 Solución al Error 500 en Dashboard KPIs

## 📋 Problema Identificado

```
GET /api/reportes/reportes/dashboard-kpis/ 500 (Internal Server Error)
```

### Causa Raíz
El endpoint `dashboard-kpis` intenta contar registros de `PerfilPaciente` pero estos **no existen** en la base de datos porque el script `crear_usuarios_prueba.py` no creó los perfiles correctamente durante el deployment.

---

## ✅ Solución Aplicada

### 1. Correcciones en el Backend

**Commit `0bb9fde`** - Corregir cálculos en reportes/views.py:
- ✅ Cambiar `saldo_pendiente` para iterar sobre facturas en lugar de usar agregación
- ✅ Asegurar que `tasa_ocupacion` retorne `float` en lugar de `int`

**Commit `611e0f5`** - Crear perfiles en crear_usuarios_prueba.py:
- ✅ Agregar creación de `PerfilOdontologo` para odontólogos
- ✅ Agregar creación de `PerfilPaciente` para pacientes
- ✅ Usar `get_or_create` para evitar duplicados

**Commit `e0c5ea2`** - Management command para reparar perfiles:
- ✅ Crear `fix_perfiles.py` management command
- ✅ Agregar `fix_perfiles_produccion.py` script standalone
- ✅ Modificar `build.sh` para ejecutar `fix_perfiles` automáticamente

---

## 🚀 Verificación del Deployment

### Paso 1: Verificar Estado en Render

1. Ir a: https://dashboard.render.com
2. Seleccionar servicio: `clinica-dental-backend`
3. Ver sección "Events" o "Logs"
4. Buscar mensajes:
   ```
   ✅ Datos iniciales creados correctamente
   🔧 REPARANDO PERFILES DE USUARIOS
   ✅ Perfiles de odontólogos creados: X
   ✅ Perfiles de pacientes creados: Y
   🎉 ¡Perfiles reparados!
   ```

### Paso 2: Probar el Endpoint (PowerShell)

```powershell
# 1. Obtener token de autenticación
$headers = @{'X-Tenant-ID' = 'clinica_demo'}
$body = @{'email' = 'admin@clinica-demo.com'; 'password' = 'admin123'} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://clinica-dental-backend.onrender.com/api/token/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -Headers $headers

$token = $response.access

# 2. Probar dashboard-kpis
$authHeaders = @{
    'Authorization' = "Bearer $token"
    'X-Tenant-ID' = 'clinica_demo'
}

Invoke-RestMethod -Uri "https://clinica-dental-backend.onrender.com/api/reportes/reportes/dashboard-kpis/" `
    -Headers $authHeaders
```

**Respuesta Esperada:**
```json
[
  {
    "etiqueta": "Pacientes Activos",
    "valor": 6
  },
  {
    "etiqueta": "Citas Hoy",
    "valor": 0
  },
  {
    "etiqueta": "Ingresos Este Mes",
    "valor": "Bs. 0.00"
  },
  {
    "etiqueta": "Saldo Pendiente",
    "valor": "Bs. 500.00"
  }
]
```

---

## 🔍 Troubleshooting

### Si el error 500 persiste después del deployment:

#### Opción 1: Ejecutar Manualmente el Command

Si tienes acceso a la shell de Render:

```bash
# En el dashboard de Render > Shell
python manage.py fix_perfiles
```

#### Opción 2: Ejecutar el Script Standalone

```bash
# En el dashboard de Render > Shell
python fix_perfiles_produccion.py
```

#### Opción 3: Verificar los Logs de Build

1. Ve a Render Dashboard > Events
2. Busca el último deployment
3. Revisa los logs completos
4. Busca errores en:
   - `python crear_usuarios_prueba.py`
   - `python manage.py fix_perfiles`

#### Opción 4: Verificar la Base de Datos

Si tienes acceso a la shell de Render:

```python
python manage.py shell

# Ejecutar en la shell:
from django_tenants.utils import schema_context
from usuarios.models import PerfilPaciente, PerfilOdontologo
from tenants.models import Clinica

tenant = Clinica.objects.get(schema_name='clinica_demo')

with schema_context('clinica_demo'):
    print(f"PerfilOdontologo: {PerfilOdontologo.objects.count()}")
    print(f"PerfilPaciente: {PerfilPaciente.objects.count()}")
```

**Resultado Esperado:**
```
PerfilOdontologo: 1
PerfilPaciente: 6
```

---

## 📊 Resumen de Commits

| Commit | Descripción | Estado |
|--------|-------------|--------|
| `0bb9fde` | Fix cálculos en dashboard-kpis | ✅ Aplicado |
| `611e0f5` | Crear perfiles en script usuarios | ✅ Aplicado |
| `35b1262` | Corregir endpoint stock bajo en guía | ✅ Aplicado |
| `e0c5ea2` | **Management command fix_perfiles** | 🔄 **Desplegando** |

---

## ⏱️ Timeline Esperado

| Tiempo | Acción | Estado |
|--------|--------|--------|
| **0 min** | Push a GitHub | ✅ Completado |
| **1-3 min** | Render detecta cambios y inicia build | 🔄 En progreso |
| **3-8 min** | Build: instalar deps, migraciones, poblar datos | ⏳ Esperando |
| **8-10 min** | Deploy: iniciar servidor actualizado | ⏳ Esperando |
| **10 min** | ✅ Servidor LIVE con perfiles reparados | 🎯 Objetivo |

---

## 🎯 Próximos Pasos

1. **Esperar 10 minutos** desde el último push (commit `e0c5ea2`)
2. **Verificar en Render** que el deployment completó exitosamente
3. **Probar el endpoint** usando los comandos PowerShell de arriba
4. **Refrescar el frontend** (Ctrl + Shift + R)
5. **Iniciar sesión** con `admin@clinica-demo.com` / `admin123`
6. **Verificar consola del navegador**:
   - ✅ NO debe haber error 500
   - ✅ Dashboard debe mostrar KPIs correctamente

---

## 📝 Notas Adicionales

### ¿Por qué falló la primera vez?

El script `crear_usuarios_prueba.py` creaba usuarios pero **no creaba los perfiles**. El endpoint `dashboard-kpis` necesita:

```python
total_pacientes = PerfilPaciente.objects.filter(
    usuario__is_active=True
).count()
```

Si no hay registros en `PerfilPaciente`, el conteo funciona (retorna 0), pero al iterar sobre facturas relacionadas a pacientes sin perfil, puede causar errores.

### La Solución Definitiva

Ahora el `build.sh` ejecuta **dos scripts**:

1. `crear_usuarios_prueba.py` - Crea usuarios y perfiles
2. `python manage.py fix_perfiles` - Verifica y repara perfiles faltantes

Esto asegura que **todos los usuarios tengan sus perfiles**, incluso si algo falla en el primer script.

---

## ✅ Checklist de Verificación

- [x] Commits aplicados (0bb9fde, 611e0f5, 35b1262, e0c5ea2)
- [ ] Deployment en Render completado exitosamente
- [ ] Endpoint dashboard-kpis responde con 200 OK
- [ ] Frontend carga sin errores 500 en consola
- [ ] Dashboard muestra KPIs correctamente
- [ ] No hay TypeError en tasa_ocupacion.toFixed

---

**Fecha de última actualización:** 2025-11-20  
**Commits relacionados:** `0bb9fde`, `611e0f5`, `35b1262`, `e0c5ea2`  
**Estado:** 🔄 Esperando deployment automático de Render
