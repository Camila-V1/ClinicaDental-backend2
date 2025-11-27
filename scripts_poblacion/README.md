# 📚 GUÍA DE USO - SCRIPTS DE POBLACIÓN MODULAR

## 📋 Descripción General

Sistema modular completo para poblar la base de datos de la Clínica Dental con datos realistas y coherentes.

## 🗂️ Estructura de Archivos

```
scripts_poblacion/
├── __init__.py                    # Inicialización del paquete
├── poblar_todo.py                 # ⭐ Script principal (ejecutar este)
├── crear_tenant.py                # Módulo 1: Crear tenant y dominios
├── poblar_usuarios.py             # Módulo 2: Usuarios con credenciales exactas
├── poblar_tratamientos.py         # Módulo 3: 20 tratamientos dentales
├── poblar_inventario.py           # Módulo 4: 35+ productos con stock
├── poblar_agenda.py               # Módulo 5: 40+ citas (pasadas/futuras)
├── poblar_historial.py            # Módulo 6: Episodios clínicos y odontogramas
└── poblar_facturacion.py          # Módulo 7: Facturas y pagos
```

## 🚀 Uso Básico

### Ejecutar Script Completo

```bash
python scripts_poblacion/poblar_todo.py
```

Este comando ejecuta TODOS los módulos en orden:
1. ✅ Crear/verificar tenant
2. ✅ Crear usuarios (7 usuarios)
3. ✅ Crear tratamientos (20 tratamientos)
4. ✅ Crear inventario (35+ productos)
5. ✅ Crear citas (40+ citas)
6. ✅ Crear historial clínico (episodios y odontogramas)
7. ✅ Crear facturación (facturas y pagos)

## 🔐 Credenciales Creadas

| Rol | Email | Password |
|-----|-------|----------|
| **Admin** | admin@clinicademo1.com | admin123 |
| **Odontólogo** | odontologo@clinica-demo.com | odontologo123 |
| **Odontólogo 2** | dra.lopez@clinica-demo.com | odontologo123 |
| **Recepcionista** | recepcionista@clinica-demo.com | recep123 |
| **Paciente 1** | paciente1@test.com | paciente123 |
| **Paciente 2** | paciente2@test.com | paciente123 |
| **Paciente 3** | paciente3@test.com | paciente123 |

## 🧹 Limpiar Base de Datos

Si necesitas **borrar todo y empezar de cero**:

1. Editar `poblar_todo.py` línea ~73:
```python
# Descomentar esta línea:
limpiar_tenant_existente(SCHEMA_NAME)
```

2. Ejecutar:
```bash
python scripts_poblacion/poblar_todo.py
```

⚠️ **CUIDADO**: Esto elimina el tenant completo incluyendo todos los datos.

## 📊 Datos Generados

### Usuarios (7 total)
- 1 Administrador
- 2 Odontólogos
- 1 Recepcionista
- 3 Pacientes

### Tratamientos (20 total)
- 7 Categorías: Odontología General, Endodoncia, Periodoncia, etc.
- Códigos: ODG-001, ENDO-001, etc.
- Precios: Bs. 150 - Bs. 2500

### Inventario (35+ productos)
- 8 Categorías: Instrumental, Materiales, Anestésicos, etc.
- Stock management completo
- Productos bajo stock marcados

### Agenda (40+ citas)
- 15 completadas (últimos 30 días)
- 3 hoy (completada, en curso, confirmada)
- 20 futuras (próximos 30 días)
- 3 canceladas

### Historial Clínico
- Episodios vinculados a citas completadas
- Odontogramas completos (32 dientes)
- Estados: SANO, CARIES, OBTURADO, etc.

### Facturación
- 20+ facturas vinculadas a citas
- 5 facturas directas
- 3 con planes de pago
- Estados: PAGADA, PENDIENTE, PARCIAL
- Métodos: EFECTIVO, TARJETA, TRANSFERENCIA, QR

## 🔧 Uso Modular (Avanzado)

Si solo quieres ejecutar **módulos específicos**:

### Ejemplo 1: Solo Usuarios
```python
from django_tenants.utils import schema_context
from scripts_poblacion import poblar_usuarios

with schema_context('clinica_demo'):
    usuarios = poblar_usuarios.poblar_usuarios()
    print(f"Creados {len(usuarios)} usuarios")
```

### Ejemplo 2: Solo Inventario
```python
from django_tenants.utils import schema_context
from scripts_poblacion import poblar_inventario

with schema_context('clinica_demo'):
    categorias, productos = poblar_inventario.poblar_inventario()
    print(f"Productos: {len(productos)}")
```

### Ejemplo 3: Solo Agenda
```python
from django_tenants.utils import schema_context
from scripts_poblacion import poblar_usuarios, poblar_tratamientos, poblar_agenda

with schema_context('clinica_demo'):
    odontologos = poblar_usuarios.obtener_odontologos()
    pacientes = poblar_usuarios.obtener_pacientes()
    tratamientos = poblar_tratamientos.obtener_tratamientos_por_categoria('Odontología General')
    
    citas = poblar_agenda.poblar_agenda(odontologos, pacientes, tratamientos)
    print(f"Citas: {len(citas)}")
```

## 🛠️ Funciones Auxiliares

Cada módulo incluye funciones helper para reutilizar:

### poblar_usuarios.py
- `obtener_odontologos()` - Lista de odontólogos
- `obtener_pacientes()` - Lista de pacientes
- `obtener_admin()` - Usuario admin

### poblar_tratamientos.py
- `obtener_tratamientos_por_categoria(nombre_cat)` - Filtrar por categoría
- `obtener_tratamiento_por_codigo(codigo)` - Buscar por código

### poblar_inventario.py
- `obtener_productos_bajo_stock()` - Productos con stock mínimo
- `obtener_consumibles()` - Solo consumibles

### poblar_agenda.py
- `obtener_citas_hoy()` - Citas de hoy
- `obtener_citas_semana()` - Citas de la semana
- `obtener_citas_por_odontologo(odontologo)` - Por odontólogo

### poblar_historial.py
- `obtener_episodios_paciente(paciente)` - Historial del paciente
- `obtener_ultimo_odontograma(paciente)` - Odontograma más reciente
- `obtener_dientes_con_problemas(paciente)` - Dientes afectados

### poblar_facturacion.py
- `obtener_facturas_pendientes()` - Facturas sin pagar
- `obtener_facturas_paciente(paciente)` - Por paciente
- `calcular_ingresos_mes(mes, anio)` - Ingresos mensuales
- `obtener_deudores()` - Pacientes con deuda

## 📝 Configuración

Editar constantes en `poblar_todo.py`:

```python
DOMINIO_PRINCIPAL = 'clinicademo1.dentaabcxy.store'
SCHEMA_NAME = 'clinica_demo'
NOMBRE_CLINICA = 'Clínica Demo'
```

## 🚢 Integración con Render

Para usar en producción, actualizar `build.sh`:

```bash
echo "Poblando base de datos con datos de demo..."
python scripts_poblacion/poblar_todo.py
```

## 🐛 Troubleshooting

### Error: "Tenant already exists"
- Normal si el tenant ya existe
- El script verifica y usa el existente
- Para limpiar, usar `limpiar_tenant_existente()`

### Error: "No module named scripts_poblacion"
- Ejecutar desde la raíz del proyecto
- Verificar que existe `scripts_poblacion/__init__.py`

### Error: "relation does not exist"
- Ejecutar migraciones primero:
```bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

## 🎯 Características Principales

✅ **Idempotente**: Puede ejecutarse múltiples veces sin duplicar
✅ **Modular**: Cada módulo es independiente y reutilizable
✅ **Realista**: Datos coherentes con relaciones correctas
✅ **Completo**: Cubre todos los módulos del sistema
✅ **Documentado**: Código comentado y helpers incluidos
✅ **Configurable**: Fácil ajustar cantidades y datos

## 📞 Soporte

Si tienes problemas:
1. Verificar logs en consola
2. Revisar que migraciones estén aplicadas
3. Confirmar que tenant existe en BD
4. Verificar credenciales de conexión

---

**¡Sistema listo para poblar! 🎉**
