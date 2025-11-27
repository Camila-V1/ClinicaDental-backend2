# 🔍 Bitácora Screen - Pantalla de Auditoría

## 📱 Vista General

Pantalla para visualizar el historial de acciones del sistema con:
- Lista paginada de acciones
- Filtros avanzados (usuario, acción, fecha, modelo)
- Búsqueda en descripción
- Exportación a PDF/Excel
- Estadísticas de actividad

---

## 🎯 Archivo: `lib/screens/admin/bitacora_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/bitacora_service.dart';
import '../../widgets/filtros_bitacora.dart';

class BitacoraScreen extends StatefulWidget {
  const BitacoraScreen({super.key});

  @override
  State<BitacoraScreen> createState() => _BitacoraScreenState();
}

class _BitacoraScreenState extends State<BitacoraScreen> {
  final BitacoraService _bitacoraService = BitacoraService();
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();

  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _error;

  List<Map<String, dynamic>> _registros = [];
  int _paginaActual = 1;
  bool _tieneMasPaginas = true;

  // Filtros activos
  Map<String, dynamic> _filtrosActivos = {};

  @override
  void initState() {
    super.initState();
    _cargarRegistros();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent * 0.8) {
      if (!_isLoadingMore && _tieneMasPaginas) {
        _cargarMasRegistros();
      }
    }
  }

  Future<void> _cargarRegistros({bool limpiar = true}) async {
    if (limpiar) {
      setState(() {
        _isLoading = true;
        _error = null;
        _paginaActual = 1;
        _registros.clear();
      });
    }

    try {
      final resultado = await _bitacoraService.obtenerBitacora(
        pagina: _paginaActual,
        filtros: _filtrosActivos,
      );

      setState(() {
        _registros.addAll(resultado['results'] as List<Map<String, dynamic>>);
        _tieneMasPaginas = resultado['next'] != null;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  Future<void> _cargarMasRegistros() async {
    setState(() {
      _isLoadingMore = true;
      _paginaActual++;
    });
    await _cargarRegistros(limpiar: false);
  }

  void _aplicarFiltros(Map<String, dynamic> filtros) {
    setState(() {
      _filtrosActivos = filtros;
    });
    _cargarRegistros();
  }

  void _limpiarFiltros() {
    setState(() {
      _filtrosActivos.clear();
      _searchController.clear();
    });
    _cargarRegistros();
  }

  Future<void> _exportarBitacora(String formato) async {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Descargando bitácora en $formato...')),
      );

      final exito = await _bitacoraService.exportarBitacora(
        formato: formato,
        filtros: _filtrosActivos,
      );

      if (exito && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Bitácora descargada exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _mostrarEstadisticas() async {
    try {
      final stats = await _bitacoraService.obtenerEstadisticas(dias: 7);
      
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => _buildEstadisticasDialog(stats),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar estadísticas: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bitácora del Sistema'),
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: _mostrarEstadisticas,
            tooltip: 'Ver estadísticas',
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf, color: Colors.red),
            onPressed: () => _exportarBitacora('pdf'),
            tooltip: 'Exportar PDF',
          ),
          IconButton(
            icon: const Icon(Icons.grid_on, color: Colors.green),
            onPressed: () => _exportarBitacora('excel'),
            tooltip: 'Exportar Excel',
          ),
        ],
      ),
      body: Column(
        children: [
          // Barra de búsqueda
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Buscar en descripción...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _filtrosActivos.remove('descripcion');
                          _cargarRegistros();
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onSubmitted: (value) {
                if (value.isNotEmpty) {
                  _filtrosActivos['descripcion'] = value;
                  _cargarRegistros();
                }
              },
            ),
          ),

          // Filtros activos
          if (_filtrosActivos.isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ..._filtrosActivos.entries.map((entry) {
                    return Chip(
                      label: Text('${entry.key}: ${entry.value}'),
                      onDeleted: () {
                        setState(() {
                          _filtrosActivos.remove(entry.key);
                        });
                        _cargarRegistros();
                      },
                    );
                  }).toList(),
                  ActionChip(
                    label: const Text('Limpiar filtros'),
                    onPressed: _limpiarFiltros,
                    avatar: const Icon(Icons.clear_all, size: 18),
                  ),
                ],
              ),
            ),

          // Botón de filtros
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ElevatedButton.icon(
              onPressed: () => _mostrarFiltros(),
              icon: const Icon(Icons.filter_list),
              label: Text('Filtros (${_filtrosActivos.length})'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Lista de registros
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.error_outline, size: 60, color: Colors.red),
                            const SizedBox(height: 16),
                            Text('Error: $_error'),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _cargarRegistros,
                              child: const Text('Reintentar'),
                            ),
                          ],
                        ),
                      )
                    : _registros.isEmpty
                        ? const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.inbox, size: 80, color: Colors.grey),
                                SizedBox(height: 16),
                                Text('No hay registros para mostrar'),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () => _cargarRegistros(),
                            child: ListView.separated(
                              controller: _scrollController,
                              padding: const EdgeInsets.all(16),
                              itemCount: _registros.length + (_isLoadingMore ? 1 : 0),
                              separatorBuilder: (context, index) => const SizedBox(height: 12),
                              itemBuilder: (context, index) {
                                if (index == _registros.length) {
                                  return const Center(
                                    child: Padding(
                                      padding: EdgeInsets.all(16),
                                      child: CircularProgressIndicator(),
                                    ),
                                  );
                                }
                                
                                return _buildRegistroCard(_registros[index]);
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildRegistroCard(Map<String, dynamic> registro) {
    final accion = registro['accion'] as String;
    final descripcion = registro['descripcion'] as String;
    final usuario = registro['usuario_nombre'] as String?;
    final fechaHora = DateTime.parse(registro['fecha_hora']);
    final ip = registro['ip_address'] as String?;

    final iconoAccion = _getIconoAccion(accion);
    final colorAccion = _getColorAccion(accion);

    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: colorAccion.withOpacity(0.2),
          child: Icon(iconoAccion, color: colorAccion),
        ),
        title: Text(
          descripcion,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('👤 ${usuario ?? 'Usuario desconocido'}'),
            Text('🕐 ${DateFormat('dd/MM/yyyy HH:mm').format(fechaHora)}'),
            if (ip != null) Text('📍 IP: $ip'),
          ],
        ),
        trailing: Chip(
          label: Text(
            accion,
            style: TextStyle(color: colorAccion, fontSize: 12),
          ),
          backgroundColor: colorAccion.withOpacity(0.1),
        ),
        isThreeLine: true,
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
      default:
        return Icons.info;
    }
  }

  Color _getColorAccion(String accion) {
    switch (accion) {
      case 'CREAR':
        return Colors.green;
      case 'EDITAR':
        return Colors.blue;
      case 'ELIMINAR':
        return Colors.red;
      case 'VER':
        return Colors.grey;
      case 'LOGIN':
        return Colors.teal;
      case 'LOGOUT':
        return Colors.orange;
      case 'EXPORTAR':
        return Colors.purple;
      default:
        return Colors.blueGrey;
    }
  }

  void _mostrarFiltros() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => FiltrosBitacora(
        filtrosActuales: Map.from(_filtrosActivos),
        onAplicar: _aplicarFiltros,
      ),
    );
  }

  Widget _buildEstadisticasDialog(Map<String, dynamic> stats) {
    return AlertDialog(
      title: const Text('📊 Estadísticas de Actividad'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Período: ${stats['periodo']}'),
            const SizedBox(height: 16),
            Text(
              'Total de acciones: ${stats['total_acciones']}',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(height: 32),
            const Text('Acciones por tipo:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...((stats['acciones_por_tipo'] as List).map((item) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(item['accion']),
                    Chip(label: Text('${item['total']}')),
                  ],
                ),
              );
            }).toList()),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cerrar'),
        ),
      ],
    );
  }
}
```

---

## 🔑 Características

### 1. Paginación Infinita
- Carga automática al hacer scroll
- `_scrollController` detecta cuando llega al 80% del scroll

### 2. Búsqueda
- Búsqueda en descripción de acciones
- Actualización en tiempo real

### 3. Filtros Visuales
- Chips mostrando filtros activos
- Botón para limpiar todos los filtros

### 4. Exportación
- Botones en AppBar para PDF y Excel
- Aplica los filtros activos a la exportación

### 5. Estadísticas
- Modal con resumen de actividad
- Acciones por tipo en últimos 7 días

---

## 🎨 UI por Tipo de Acción

| Acción | Ícono | Color |
|--------|-------|-------|
| CREAR | add_circle | Verde |
| EDITAR | edit | Azul |
| ELIMINAR | delete | Rojo |
| VER | visibility | Gris |
| LOGIN | login | Teal |
| LOGOUT | logout | Naranja |
| EXPORTAR | download | Morado |

---

## 🎯 Siguiente Paso

Implementar servicio de bitácora:
👉 **[12_BITACORA_SERVICE.md](12_BITACORA_SERVICE.md)**
