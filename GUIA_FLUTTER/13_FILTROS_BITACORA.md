# 🔍 Widget de Filtros Avanzados para Bitácora

## 🎯 Archivo: `lib/widgets/filtros_bitacora.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class FiltrosBitacora extends StatefulWidget {
  final Map<String, dynamic> filtrosActuales;
  final Function(Map<String, dynamic>) onAplicar;

  const FiltrosBitacora({
    super.key,
    required this.filtrosActuales,
    required this.onAplicar,
  });

  @override
  State<FiltrosBitacora> createState() => _FiltrosBitacoraState();
}

class _FiltrosBitacoraState extends State<FiltrosBitacora> {
  late Map<String, dynamic> _filtros;

  // Controladores de texto
  final TextEditingController _ipController = TextEditingController();
  final TextEditingController _modeloController = TextEditingController();

  // Valores seleccionados
  String? _accionSeleccionada;
  DateTime? _fechaDesde;
  DateTime? _fechaHasta;

  // Opciones de acciones
  final List<String> _acciones = [
    'CREAR',
    'EDITAR',
    'ELIMINAR',
    'VER',
    'LOGIN',
    'LOGOUT',
    'EXPORTAR',
    'IMPRIMIR',
  ];

  @override
  void initState() {
    super.initState();
    _filtros = Map.from(widget.filtrosActuales);

    // Inicializar valores desde filtros actuales
    _accionSeleccionada = _filtros['accion'];
    _ipController.text = _filtros['ip'] ?? '';
    _modeloController.text = _filtros['modelo'] ?? '';

    if (_filtros['desde'] != null) {
      try {
        _fechaDesde = DateTime.parse(_filtros['desde']);
      } catch (e) {
        _fechaDesde = null;
      }
    }

    if (_filtros['hasta'] != null) {
      try {
        _fechaHasta = DateTime.parse(_filtros['hasta']);
      } catch (e) {
        _fechaHasta = null;
      }
    }
  }

  @override
  void dispose() {
    _ipController.dispose();
    _modeloController.dispose();
    super.dispose();
  }

  void _aplicarFiltros() {
    final Map<String, dynamic> nuevosFiltros = {};

    // Acción
    if (_accionSeleccionada != null && _accionSeleccionada!.isNotEmpty) {
      nuevosFiltros['accion'] = _accionSeleccionada;
    }

    // Fecha desde
    if (_fechaDesde != null) {
      nuevosFiltros['desde'] = DateFormat('yyyy-MM-dd').format(_fechaDesde!);
    }

    // Fecha hasta
    if (_fechaHasta != null) {
      nuevosFiltros['hasta'] = DateFormat('yyyy-MM-dd').format(_fechaHasta!);
    }

    // IP
    if (_ipController.text.isNotEmpty) {
      nuevosFiltros['ip'] = _ipController.text;
    }

    // Modelo
    if (_modeloController.text.isNotEmpty) {
      nuevosFiltros['modelo'] = _modeloController.text.toLowerCase();
    }

    widget.onAplicar(nuevosFiltros);
    Navigator.pop(context);
  }

  void _limpiarFiltros() {
    setState(() {
      _accionSeleccionada = null;
      _fechaDesde = null;
      _fechaHasta = null;
      _ipController.clear();
      _modeloController.clear();
    });
  }

  Future<void> _seleccionarFecha(BuildContext context, bool esDesde) async {
    final DateTime? fechaSeleccionada = await showDatePicker(
      context: context,
      initialDate: esDesde
          ? (_fechaDesde ?? DateTime.now())
          : (_fechaHasta ?? DateTime.now()),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      locale: const Locale('es', 'ES'),
      helpText: esDesde ? 'Seleccionar fecha desde' : 'Seleccionar fecha hasta',
    );

    if (fechaSeleccionada != null) {
      setState(() {
        if (esDesde) {
          _fechaDesde = fechaSeleccionada;
        } else {
          _fechaHasta = fechaSeleccionada;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        left: 16,
        right: 16,
        top: 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Título
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Filtros Avanzados',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Filtro: Tipo de Acción
            _buildSeccionTitulo('Tipo de Acción'),
            DropdownButtonFormField<String>(
              value: _accionSeleccionada,
              decoration: const InputDecoration(
                labelText: 'Seleccionar acción',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.category),
              ),
              items: [
                const DropdownMenuItem(value: null, child: Text('Todas')),
                ..._acciones.map((accion) {
                  return DropdownMenuItem(
                    value: accion,
                    child: Row(
                      children: [
                        Icon(_getIconoAccion(accion), size: 20),
                        const SizedBox(width: 8),
                        Text(accion),
                      ],
                    ),
                  );
                }).toList(),
              ],
              onChanged: (value) {
                setState(() {
                  _accionSeleccionada = value;
                });
              },
            ),
            const SizedBox(height: 24),

            // Filtro: Rango de Fechas
            _buildSeccionTitulo('Rango de Fechas'),
            Row(
              children: [
                Expanded(
                  child: _buildCampoFecha(
                    context,
                    'Desde',
                    _fechaDesde,
                    () => _seleccionarFecha(context, true),
                    () {
                      setState(() {
                        _fechaDesde = null;
                      });
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildCampoFecha(
                    context,
                    'Hasta',
                    _fechaHasta,
                    () => _seleccionarFecha(context, false),
                    () {
                      setState(() {
                        _fechaHasta = null;
                      });
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Filtro: Modelo
            _buildSeccionTitulo('Modelo de Datos'),
            TextField(
              controller: _modeloController,
              decoration: const InputDecoration(
                labelText: 'Nombre del modelo',
                hintText: 'Ej: cita, paciente, factura',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.storage),
              ),
            ),
            const SizedBox(height: 24),

            // Filtro: Dirección IP
            _buildSeccionTitulo('Dirección IP'),
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'IP del cliente',
                hintText: 'Ej: 192.168.1.1',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.wifi),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 32),

            // Botones de acción
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _limpiarFiltros,
                    child: const Text('Limpiar'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _aplicarFiltros,
                    child: const Text('Aplicar Filtros'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSeccionTitulo(String titulo) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        titulo,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }

  Widget _buildCampoFecha(
    BuildContext context,
    String label,
    DateTime? fecha,
    VoidCallback onTap,
    VoidCallback onClear,
  ) {
    return InkWell(
      onTap: onTap,
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
          prefixIcon: const Icon(Icons.calendar_today),
          suffixIcon: fecha != null
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 20),
                  onPressed: onClear,
                )
              : null,
        ),
        child: Text(
          fecha != null
              ? DateFormat('dd/MM/yyyy').format(fecha)
              : 'Seleccionar',
          style: TextStyle(
            color: fecha != null ? Colors.black : Colors.grey,
          ),
        ),
      ),
    );
  }

  IconData _getIconoAccion(String accion) {
    switch (accion) {
      case 'CREAR':
        return Icons.add_circle;
      case 'EDITAR':
        return Icons.edit;
      case 'ELIMINAR':
        return Icons.delete;
      case 'VER':
        return Icons.visibility;
      case 'LOGIN':
        return Icons.login;
      case 'LOGOUT':
        return Icons.logout;
      case 'EXPORTAR':
        return Icons.download;
      case 'IMPRIMIR':
        return Icons.print;
      default:
        return Icons.info;
    }
  }
}
```

---

## 🔑 Características

### 1. Filtros Disponibles
- **Acción**: Dropdown con iconos (CREAR, EDITAR, ELIMINAR, etc.)
- **Rango de fechas**: Date pickers para desde/hasta
- **Modelo**: Campo de texto para nombre del modelo
- **IP**: Campo de texto para dirección IP

### 2. Validación
- Fechas no pueden ser futuras
- Modelo se convierte automáticamente a minúsculas
- Campos vacíos no se incluyen en los filtros

### 3. UX
- Modal Bottom Sheet responsivo
- Botones de limpiar/aplicar
- Iconos visuales para cada acción
- Date pickers nativos
- Botón X para cerrar fechas seleccionadas

---

## 🎨 Uso en BitacoraScreen

```dart
void _mostrarFiltros() {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,  // Permite scroll cuando hay teclado
    builder: (context) => FiltrosBitacora(
      filtrosActuales: Map.from(_filtrosActivos),
      onAplicar: (filtros) {
        setState(() {
          _filtrosActivos = filtros;
        });
        _cargarRegistros();
      },
    ),
  );
}
```

---

## 📝 Formato de Filtros Aplicados

```dart
{
  'accion': 'CREAR',              // Tipo de acción
  'desde': '2025-11-01',          // Fecha desde (ISO)
  'hasta': '2025-11-30',          // Fecha hasta (ISO)
  'modelo': 'cita',               // Modelo en minúsculas
  'ip': '192.168.1.1',            // Dirección IP
}
```

---

## 🎯 Resumen de Implementación Completa

Has completado la guía para crear una **app Flutter de administración** con:

✅ **Dashboard de Reportes**
- KPIs principales
- Gráficos de tendencia y top procedimientos
- Exportación a PDF/Excel
- Actualización en tiempo real

✅ **Bitácora de Auditoría**
- Lista paginada de acciones
- Filtros avanzados con modal
- Búsqueda en descripción
- Estadísticas de actividad
- Exportación filtrada

✅ **Servicios API**
- `ReportesService` para endpoints de reportes
- `BitacoraService` para endpoints de auditoría
- Manejo de autenticación JWT
- Multi-tenant automático
- Exportación y descarga de archivos

---

## 📦 Archivos Creados

```
GUIA_FLUTTER/
├── 00_README.md                    # Índice general
├── 01_CONFIGURACION_PROYECTO.md    # Setup inicial
├── 06_DASHBOARD_SCREEN.md          # Pantalla principal
├── 09_REPORTES_SERVICE.md          # Servicio de reportes
├── 11_BITACORA_SCREEN.md           # Pantalla de bitácora
├── 12_BITACORA_SERVICE.md          # Servicio de bitácora
└── 13_FILTROS_BITACORA.md          # Widget de filtros
```

---

## 🚀 Siguiente Paso

Ya tienes toda la documentación necesaria para implementar las funcionalidades de **admin**. Puedes:

1. Seguir las guías en orden
2. Implementar los widgets faltantes (KPI cards, gráficos)
3. Configurar el routing y navegación
4. Probar la integración con el backend

**¡Listo para desarrollar tu app Flutter de administración!** 🎉

