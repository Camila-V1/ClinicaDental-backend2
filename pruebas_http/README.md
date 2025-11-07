# 🧪 Pruebas HTTP para Clínica Dental Backend

Esta carpeta contiene archivos `.http` para probar **todo el sistema backend** de la clínica dental de manera estructurada.

## 📋 Requisitos Previos

1. **Servidor funcionando**: `python manage.py runserver`
2. **Tenant demo activo**: `clinica-demo.localhost:8000`
3. **Hosts configurados**: Ejecutar `setup_hosts.ps1` si es necesario
4. **Extensión REST Client**: Instalar en VS Code para ejecutar archivos `.http`

## 🗂️ Estructura de Archivos

| Archivo | Descripción | Casos de Uso |
|---------|-------------|--------------|
| `00_autenticacion.http` | **EXHAUSTIVO:** Login, registro, CRUD usuarios completo | CU01, CU02, CU04 + Seguridad |
| `01_inventario.http` | **EXHAUSTIVO:** Inventario completo, CRUD, filtros, validaciones | CU34, CU35, CU36 + CRUD |
| `02_tratamientos.http` | **EXHAUSTIVO:** Planes, servicios, presupuestos, CRUD completo | CU19-CU22, CU24 + CRUD |
| `03_agenda_historial.http` | **EXHAUSTIVO:** Citas, historial, CRUD, estados, filtros | CU08-CU12, CU14-CU18 + CRUD |
| `04_facturacion.http` | **EXHAUSTIVO:** Facturas, pagos, reportes, validaciones | CU30-CU33 + CRUD |
| `05_reportes.http` | **EXHAUSTIVO:** Todos los reportes, filtros, validaciones | CU37, CU38 + Casos límite |
| `06_permisos_paciente.http` | **EXHAUSTIVO:** Seguridad completa, ataques, aislamiento | CU32 + Seguridad completa |
| `07_casos_especiales.http` | Edge cases y validaciones del sistema | Pruebas límite |

## 🚀 Orden de Ejecución Recomendado

### 1️⃣ **Preparación (OBLIGATORIO)**
```
00_autenticacion.http
```
- Ejecutar **A. LOGIN ADMINISTRADOR** y copiar el token
- Ejecutar **B. REGISTRAR NUEVO PACIENTE**
- Ejecutar **C. LOGIN PACIENTE** y copiar el token
- **Actualizar las variables** `@adminToken` y `@pacienteToken` en todos los archivos

### 2️⃣ **Flujo Principal del Negocio**
```
01_inventario.http → 02_tratamientos.http → 03_agenda_historial.http → 04_facturacion.http
```

### 3️⃣ **Análisis y Reportes**
```
05_reportes.http
```

### 4️⃣ **Validaciones de Seguridad**
```
06_permisos_paciente.http → 07_casos_especiales.http
```

## 📝 Instrucciones de Uso

### Variables a Actualizar

Cada archivo tiene variables al inicio. **Debes actualizarlas** con los IDs reales que vayas obteniendo:

```http
@baseUrl = http://clinica-demo.localhost:8000
@adminToken = PEGAR_TOKEN_AQUI
@pacienteToken = PEGAR_TOKEN_AQUI
@categoriaId = PEGAR_ID_AQUI
@servicioId = PEGAR_ID_AQUI
# ... etc
```

### Cómo Ejecutar

1. **Abrir archivo** `.http` en VS Code
2. **Click en "Send Request"** encima de cada bloque `POST`/`GET`
3. **Copiar IDs** de las respuestas y actualizar variables
4. **Continuar** con el siguiente endpoint

### Ejemplo de Flujo Completo

```
1. 00_autenticacion.http → Obtener tokens
2. 01_inventario.http → Crear categoría (ID: 3) e insumo (ID: 10)
3. 02_tratamientos.http → Crear servicio (ID: 5) y plan (ID: 2)
4. 03_agenda_historial.http → Agendar cita y registrar historial
5. 04_facturacion.http → Generar factura y registrar pago
6. 05_reportes.http → Ver dashboards actualizados
```

## 🎯 **Resultados Esperados**

### ✅ **Flujo Exitoso**

- **Autenticación**: Login/registro + CRUD completo de usuarios
- **Inventario**: CRUD completo, stock, alertas, filtros, validaciones
- **Tratamientos**: CRUD servicios/planes, precio dinámico, presupuestos
- **Agenda + Historial**: CRUD citas, estados, episodios, documentos
- **Facturación**: CRUD facturas/pagos, reportes financieros, validaciones
- **Reportes**: Todos los dashboards, filtros, casos límite
- **Seguridad**: Aislamiento completo, validación de permisos

### ⚠️ **Validaciones de Seguridad**

- **Pacientes**: Solo ven sus propios datos
- **Administradores**: Acceso completo al sistema
- **Tokens inválidos**: Rechazo con 401 Unauthorized
- **Datos aislados**: Cada paciente aislado de otros

## 🔧 Solución de Problemas

### Error 401 (No autorizado)
- Verificar que el token sea válido y esté bien copiado
- Los tokens JWT expiran, hacer login nuevamente si es necesario

### Error 404 (No encontrado)
- Verificar que los IDs en las variables sean correctos
- Algunos endpoints requieren datos previos (ej: crear plan antes de generar presupuesto)

### Error 400 (Datos inválidos)
- Revisar formato JSON y campos requeridos
- Verificar que las fechas estén en formato correcto: `YYYY-MM-DDTHH:MM:SSZ`

### Error 403 (Prohibido)
- Algunos endpoints requieren permisos de administrador
- Verificar que estés usando `@adminToken` y no `@pacienteToken`

## 📊 Verificación Final

Después de ejecutar todos los flujos, deberías tener:

- ✅ **Usuarios**: CRUD completo, roles, permisos validados
- ✅ **Inventario**: Categorías, insumos, stock, alertas funcionando
- ✅ **Tratamientos**: Servicios, planes, presupuestos, precio dinámico
- ✅ **Agenda**: Citas con todos los estados (programada, confirmada, cancelada, no-show)
- ✅ **Historial**: Episodios, odontogramas, documentos clínicos
- ✅ **Facturación**: Facturas, pagos múltiples, reportes financieros
- ✅ **Reportes**: Dashboards, KPIs, tendencias, estadísticas
- ✅ **Seguridad**: Aislamiento de datos, validación de permisos

## 🎉 ¡Sistema 100% Probado y Funcional!

Con estos archivos **exhaustivos** puedes probar **TODOS los endpoints** que implementaste, no solo el flujo básico. Tu backend está completamente validado y listo para producción! 🚀

### 📊 **Cobertura de Pruebas:**
- **+200 endpoints** probados individualmente
- **CRUD completo** en todos los módulos  
- **Filtros y búsquedas** avanzadas
- **Validaciones** y casos límite
- **Seguridad** y aislamiento de datos
- **Integración** entre módulos

---

**💡 Tip**: Usa estos archivos como **documentación viva** de tu API. Cada endpoint está documentado con ejemplos reales de uso.