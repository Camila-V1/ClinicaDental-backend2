# 📊 Guía Completa: Reportes Dinámicos y Bitácora de Auditoría

## 🎯 Resumen Ejecutivo

Este documento describe las **nuevas funcionalidades implementadas** para el módulo de reportes y auditoría del sistema de gestión de clínica dental.

### ✨ Características Nuevas

1. **13 Reportes Dinámicos** con filtros personalizables
2. **Exportación a PDF y Excel** para todos los reportes
3. **Sistema de Bitácora/Auditoría** completo con rastreo de acciones
4. **Filtros combinables** para análisis avanzados

---

## 📊 REPORTES DINÁMICOS (CU37)

### 1. Dashboard KPIs
**Endpoint:** `GET /api/reportes/reportes/dashboard-kpis/`

**Descripción:** Muestra las 4 métricas principales del dashboard.

**Respuesta:**
```json
[
  {"etiqueta": "Pacientes Activos", "valor": 150},
  {"etiqueta": "Citas Hoy", "valor": 8},
  {"etiqueta": "Ingresos Este Mes", "valor": "$25,000.00"},
  {"etiqueta": "Saldo Pendiente", "valor": "$5,000.00"}
]
```

**Exportación:**
```bash
GET /api/reportes/reportes/dashboard-kpis/?formato=pdf
GET /api/reportes/reportes/dashboard-kpis/?formato=excel
```

---

### 2. Estadísticas Generales
**Endpoint:** `GET /api/reportes/reportes/estadisticas-generales/`

**Descripción:** Métricas completas del sistema.

**Respuesta:**
```json
{
  "total_pacientes_activos": 150,
  "total_odontologos": 5,
  "citas_mes_actual": 120,
  "tratamientos_completados": 45,
  "ingresos_mes_actual": 25000.00,
  "promedio_factura": 555.55,
  "tasa_ocupacion": 85.50
}
```

---

### 3. Tendencia de Citas
**Endpoint:** `GET /api/reportes/reportes/tendencia-citas/`

**Parámetros:**
- `dias` (opcional): Número de días a analizar (default: 15)

**Ejemplos:**
```bash
GET /api/reportes/reportes/tendencia-citas/?dias=7
GET /api/reportes/reportes/tendencia-citas/?dias=30&formato=pdf
```

**Respuesta:**
```json
[
  {"fecha": "2025-11-01", "cantidad": 5},
  {"fecha": "2025-11-02", "cantidad": 8},
  {"fecha": "2025-11-03", "cantidad": 3}
]
```

---

### 4. Top Procedimientos
**Endpoint:** `GET /api/reportes/reportes/top-procedimientos/`

**Parámetros:**
- `limite` (opcional): Número de procedimientos a mostrar (default: 5)

**Ejemplos:**
```bash
GET /api/reportes/reportes/top-procedimientos/?limite=10
GET /api/reportes/reportes/top-procedimientos/?limite=20&formato=excel
```

---

### 5. Ocupación de Odontólogos
**Endpoint:** `GET /api/reportes/reportes/ocupacion-odontologos/`

**Parámetros:**
- `mes` (opcional): Mes en formato YYYY-MM (default: mes actual)

**Ejemplos:**
```bash
GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-11
GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-10&formato=pdf
```

---

### 6. Reporte Financiero
**Endpoint:** `GET /api/reportes/reportes/reporte-financiero/`

**Parámetros:**
- `periodo` (opcional): YYYY-MM (mensual) o YYYY (anual)

**Ejemplos:**
```bash
# Mes específico
GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11

# Año completo
GET /api/reportes/reportes/reporte-financiero/?periodo=2025

# Exportar a Excel
GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11&formato=excel
```

**Respuesta:**
```json
{
  "periodo": "2025-11",
  "total_facturado": 30000.00,
  "total_pagado": 25000.00,
  "saldo_pendiente": 5000.00,
  "numero_facturas": 45
}
```

---

### 7. Reporte de Pacientes (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-pacientes/`

**Parámetros:**
- `activo`: true/false - Filtrar por estado
- `desde`: YYYY-MM-DD - Fecha de registro desde
- `hasta`: YYYY-MM-DD - Fecha de registro hasta
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Pacientes activos
GET /api/reportes/reportes/reporte-pacientes/?activo=true

# Pacientes registrados en noviembre
GET /api/reportes/reportes/reporte-pacientes/?desde=2025-11-01&hasta=2025-11-30

# Exportar todos los pacientes a Excel
GET /api/reportes/reportes/reporte-pacientes/?formato=excel
```

**Respuesta:**
```json
[
  {
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "555-1234",
    "fecha_nacimiento": "15/03/1985",
    "fecha_registro": "01/01/2025",
    "activo": "Sí",
    "total_citas": 12,
    "total_gastado": "$3,500.00"
  }
]
```

---

### 8. Reporte de Tratamientos (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-tratamientos/`

**Parámetros:**
- `estado`: PROPUESTO/EN_PROGRESO/COMPLETADO/CANCELADO
- `desde`: YYYY-MM-DD
- `hasta`: YYYY-MM-DD
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Tratamientos en progreso
GET /api/reportes/reportes/reporte-tratamientos/?estado=EN_PROGRESO

# Tratamientos completados en noviembre
GET /api/reportes/reportes/reporte-tratamientos/?estado=COMPLETADO&desde=2025-11-01&hasta=2025-11-30

# Exportar a PDF
GET /api/reportes/reportes/reporte-tratamientos/?formato=pdf
```

---

### 9. Reporte de Inventario (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-inventario/`

**Parámetros:**
- `stock_bajo`: true - Solo insumos con stock bajo
- `categoria`: ID de categoría
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Insumos con stock bajo
GET /api/reportes/reportes/reporte-inventario/?stock_bajo=true

# Por categoría específica
GET /api/reportes/reportes/reporte-inventario/?categoria=1

# Exportar todo el inventario a Excel
GET /api/reportes/reportes/reporte-inventario/?formato=excel
```

**Respuesta:**
```json
[
  {
    "codigo": "RES-001",
    "nombre": "Resina 3M Filtek Z350",
    "categoria": "Resinas",
    "stock_actual": 5,
    "stock_minimo": 10,
    "estado_stock": "BAJO",
    "unidad_medida": "unidad",
    "precio_costo": "$45.00",
    "precio_venta": "$60.00",
    "valor_total": "$225.00",
    "proveedor": "3M Company"
  }
]
```

---

### 10. Citas por Odontólogo (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-citas-odontologo/`

**Parámetros:**
- `mes`: YYYY-MM (default: mes actual)
- `estado`: CONFIRMADA/COMPLETADA/CANCELADA
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Todas las citas de noviembre
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11

# Solo citas completadas
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11&estado=COMPLETADA

# Exportar a PDF
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11&formato=pdf
```

---

### 11. Ingresos Diarios (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-ingresos-diarios/`

**Parámetros:**
- `desde`: YYYY-MM-DD (default: hace 30 días)
- `hasta`: YYYY-MM-DD (default: hoy)
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Ingresos del mes
GET /api/reportes/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30

# Exportar a Excel
GET /api/reportes/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30&formato=excel
```

**Respuesta:**
```json
[
  {
    "fecha": "01/11/2025",
    "ingresos": "$1,250.00",
    "num_pagos": 5
  },
  {
    "fecha": "02/11/2025",
    "ingresos": "$850.00",
    "num_pagos": 3
  }
]
```

---

### 12. Servicios Populares (NUEVO)
**Endpoint:** `GET /api/reportes/reportes/reporte-servicios-populares/`

**Parámetros:**
- `limite`: Número de servicios (default: 10)
- `formato`: json/pdf/excel

**Ejemplos:**
```bash
# Top 20 servicios
GET /api/reportes/reportes/reporte-servicios-populares/?limite=20

# Exportar top 10 a PDF
GET /api/reportes/reportes/reporte-servicios-populares/?limite=10&formato=pdf
```

---

## 📄 EXPORTACIÓN PDF Y EXCEL (CU38)

### Características

- **Formatos profesionales** con logo y estilos corporativos
- **Nombres automáticos** con fecha y hora
- **Compatible con todos los reportes**

### Uso

Simplemente añade `?formato=pdf` o `?formato=excel` a cualquier endpoint de reportes.

**Ejemplos:**
```bash
# PDF
GET /api/reportes/reportes/dashboard-kpis/?formato=pdf

# Excel
GET /api/reportes/reportes/reporte-pacientes/?activo=true&formato=excel

# PDF con filtros
GET /api/reportes/reportes/reporte-tratamientos/?estado=EN_PROGRESO&desde=2025-11-01&formato=pdf
```

### Archivos Generados

**PDF:**
- Nombre: `{Titulo_Reporte}_YYYYMMDD_HHMMSS.pdf`
- Ejemplo: `Reporte_de_Pacientes_20251120_143000.pdf`
- Contenido: Encabezado con logo, tablas formateadas, métricas destacadas

**Excel:**
- Nombre: `{Titulo_Reporte}_YYYYMMDD_HHMMSS.xlsx`
- Ejemplo: `KPIs_del_Dashboard_20251120_143000.xlsx`
- Contenido: Hoja con formato, colores, bordes, columnas autoajustadas

---

## 🔍 BITÁCORA DE AUDITORÍA (CU39)

### Características

- **Rastreo automático** de acciones importantes
- **Trazabilidad completa** (quién, qué, cuándo, dónde)
- **Filtros avanzados** para búsquedas precisas
- **Estadísticas de actividad** del sistema

### Endpoints

#### 1. Listar Bitácora
**Endpoint:** `GET /api/reportes/bitacora/`

**Respuesta:**
```json
{
  "count": 1250,
  "next": "http://...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": 2,
      "usuario_nombre": "Dr. Juan Pérez",
      "accion": "CREAR",
      "accion_display": "Crear",
      "modelo": "perfilpaciente",
      "object_id": 45,
      "descripcion": "Creó nuevo paciente María García",
      "detalles": {"email": "maria@example.com"},
      "fecha_hora": "2025-11-20T14:30:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

---

#### 2. Filtrar Bitácora

**Parámetros disponibles:**
- `usuario`: ID del usuario
- `accion`: CREAR/EDITAR/ELIMINAR/VER/LOGIN/LOGOUT/EXPORTAR/IMPRIMIR/OTRO
- `desde`: Fecha desde (YYYY-MM-DD)
- `hasta`: Fecha hasta (YYYY-MM-DD)
- `modelo`: Nombre del modelo (ej: paciente, cita, factura)
- `ip`: Dirección IP
- `descripcion`: Búsqueda en texto de descripción

**Ejemplos:**
```bash
# Acciones de un usuario específico
GET /api/reportes/bitacora/?usuario=2

# Solo creaciones
GET /api/reportes/bitacora/?accion=CREAR

# Rango de fechas
GET /api/reportes/bitacora/?desde=2025-11-01&hasta=2025-11-30

# Acciones sobre un modelo específico
GET /api/reportes/bitacora/?modelo=factura

# Combinando filtros
GET /api/reportes/bitacora/?usuario=2&accion=EDITAR&desde=2025-11-01

# Búsqueda por texto
GET /api/reportes/bitacora/?descripcion=paciente
```

---

#### 3. Estadísticas de Bitácora
**Endpoint:** `GET /api/reportes/bitacora/estadisticas/`

**Parámetros:**
- `dias`: Número de días a analizar (default: 7)

**Ejemplo:**
```bash
GET /api/reportes/bitacora/estadisticas/?dias=30
```

**Respuesta:**
```json
{
  "periodo": "Últimos 30 días",
  "total_acciones": 1250,
  "acciones_por_tipo": [
    {"accion": "VER", "total": 450},
    {"accion": "EDITAR", "total": 320},
    {"accion": "CREAR", "total": 280}
  ],
  "usuarios_mas_activos": [
    {"usuario__first_name": "Juan", "usuario__last_name": "Pérez", "total": 350},
    {"usuario__first_name": "Ana", "usuario__last_name": "López", "total": 280}
  ],
  "actividad_diaria": [
    {"fecha_hora__date": "2025-11-01", "total": 45},
    {"fecha_hora__date": "2025-11-02", "total": 52}
  ]
}
```

---

#### 4. Exportar Bitácora
**Endpoint:** `GET /api/reportes/bitacora/exportar/`

**Parámetros:**
- `formato`: pdf/excel
- `desde`: YYYY-MM-DD
- `hasta`: YYYY-MM-DD
- Todos los filtros de bitácora

**Ejemplos:**
```bash
# Exportar todo a Excel
GET /api/reportes/bitacora/exportar/?formato=excel

# Exportar rango específico a PDF
GET /api/reportes/bitacora/exportar/?formato=pdf&desde=2025-11-01&hasta=2025-11-30

# Exportar solo acciones de un usuario
GET /api/reportes/bitacora/exportar/?formato=excel&usuario=2
```

---

### Registrar Acciones en Código

Para registrar acciones manualmente en tu código:

```python
from reportes.models import BitacoraAccion

# Ejemplo 1: Crear paciente
BitacoraAccion.registrar(
    usuario=request.user,
    accion='CREAR',
    descripcion=f'Creó nuevo paciente {paciente.usuario.full_name}',
    content_object=paciente,
    detalles={'email': paciente.usuario.email},
    ip_address=request.META.get('REMOTE_ADDR')
)

# Ejemplo 2: Editar tratamiento
BitacoraAccion.registrar(
    usuario=request.user,
    accion='EDITAR',
    descripcion=f'Modificó plan de tratamiento #{plan.id}',
    content_object=plan,
    detalles={'campo_modificado': 'estado', 'nuevo_valor': 'COMPLETADO'}
)

# Ejemplo 3: Eliminar cita
BitacoraAccion.registrar(
    usuario=request.user,
    accion='ELIMINAR',
    descripcion=f'Canceló cita del {cita.fecha_hora}',
    detalles={'paciente': cita.paciente.usuario.full_name, 'motivo': 'Paciente no disponible'}
)

# Ejemplo 4: Login
BitacoraAccion.registrar(
    usuario=user,
    accion='LOGIN',
    descripcion=f'Inicio de sesión exitoso',
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT')
)

# Ejemplo 5: Exportar reporte
BitacoraAccion.registrar(
    usuario=request.user,
    accion='EXPORTAR',
    descripcion=f'Exportó reporte de pacientes a PDF',
    detalles={'formato': 'pdf', 'filtros': {'activo': True}}
)
```

---

## 🔐 Permisos y Seguridad

### Autenticación
Todos los endpoints requieren **autenticación JWT**.

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Permisos
- **Reportes:** Todos los usuarios autenticados pueden ver reportes
- **Bitácora:** Solo administradores pueden ver la bitácora completa
- **Exportación:** Disponible para todos los usuarios autenticados

---

## 📝 Ejemplos de Uso Completos

### Caso 1: Análisis Financiero Mensual

```bash
# 1. Ver KPIs del dashboard
GET /api/reportes/reportes/dashboard-kpis/

# 2. Reporte financiero detallado de noviembre
GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11

# 3. Ingresos día a día de noviembre
GET /api/reportes/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30

# 4. Exportar todo a Excel
GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11&formato=excel
GET /api/reportes/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30&formato=excel
```

### Caso 2: Evaluación de Odontólogos

```bash
# 1. Ver ocupación por odontólogo
GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-11

# 2. Citas por odontólogo con detalle
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11

# 3. Exportar a PDF para reunión
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11&formato=pdf
```

### Caso 3: Control de Inventario

```bash
# 1. Ver insumos con stock bajo
GET /api/reportes/reportes/reporte-inventario/?stock_bajo=true

# 2. Exportar para hacer pedido
GET /api/reportes/reportes/reporte-inventario/?stock_bajo=true&formato=excel

# 3. Ver todo el inventario valorizado
GET /api/reportes/reportes/reporte-inventario/?formato=excel
```

### Caso 4: Auditoría de Seguridad

```bash
# 1. Ver todos los logins del último mes
GET /api/reportes/bitacora/?accion=LOGIN&desde=2025-10-20&hasta=2025-11-20

# 2. Ver acciones de un usuario sospechoso
GET /api/reportes/bitacora/?usuario=5&desde=2025-11-01

# 3. Exportar evidencia
GET /api/reportes/bitacora/exportar/?formato=pdf&usuario=5&desde=2025-11-01
```

---

## 🎨 Personalización

### Modificar Diseño de PDFs

Edita `reportes/utils.py` en la clase `PDFReportGenerator`:

```python
def _setup_custom_styles(self):
    # Cambiar colores
    self.styles['CustomTitle'].textColor = colors.HexColor('#tu_color')
    
    # Cambiar fuente
    self.styles['CustomTitle'].fontName = 'Times-Roman'
    
    # Cambiar tamaño
    self.styles['CustomTitle'].fontSize = 20
```

### Modificar Diseño de Excel

Edita `reportes/utils.py` en la clase `ExcelReportGenerator`:

```python
def _setup_styles(self):
    # Cambiar color de encabezados
    self.header_fill = PatternFill(
        start_color='tu_color_hex', 
        end_color='tu_color_hex', 
        fill_type='solid'
    )
```

---

## 🐛 Troubleshooting

### Error: "ImportError: cannot import name 'Material'"
**Solución:** El modelo correcto es `Insumo`, no `Material`. Ya está corregido en la última versión.

### Error: "No se puede exportar a PDF"
**Solución:** Verificar que reportlab esté instalado:
```bash
pip install reportlab
```

### Error: "No se puede exportar a Excel"
**Solución:** Verificar que openpyxl esté instalado:
```bash
pip install openpyxl
```

### Bitácora no registra acciones
**Solución:** Asegúrate de llamar a `BitacoraAccion.registrar()` en tus views después de cada acción importante.

---

## 📚 Recursos Adicionales

- **Documentación de ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Documentación de OpenPyXL:** https://openpyxl.readthedocs.io/
- **Django Aggregation:** https://docs.djangoproject.com/en/5.0/topics/db/aggregation/

---

## ✅ Checklist de Implementación

- [x] 13 reportes dinámicos implementados
- [x] Exportación PDF funcionando
- [x] Exportación Excel funcionando
- [x] Modelo de Bitácora creado y migrado
- [x] ViewSet de Bitácora con filtros
- [x] Estadísticas de bitácora
- [x] Exportación de bitácora
- [x] Documentación completa
- [x] Todas las migraciones aplicadas
- [x] Admin de bitácora configurado

---

**Fecha de última actualización:** 20 de Noviembre de 2025  
**Versión:** 1.0  
**Autor:** Sistema de Gestión de Clínica Dental
