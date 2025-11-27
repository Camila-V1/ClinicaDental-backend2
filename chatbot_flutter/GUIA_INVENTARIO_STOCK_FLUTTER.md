# 📦 Guía: Gestión de Inventario y Stock en Flutter

## 📋 Resumen

El sistema de inventario permite gestionar insumos odontológicos con control de stock, alertas de stock bajo y ajustes de inventario.

---

## 🎯 Endpoints Disponibles

### 1. **Listar Insumos**
```
GET /api/inventario/insumos/
```

**Parámetros opcionales**:
- `categoria`: Filtrar por ID de categoría
- `activo`: `true` o `false`
- `search`: Buscar por código, nombre, descripción o proveedor

**Response**:
```json
[
  {
    "id": 1,
    "codigo": "RES-A2-001",
    "nombre": "Resina Compuesta A2",
    "descripcion": "Resina fotopolimerizable color A2",
    "categoria": {
      "id": 1,
      "nombre": "Materiales Dentales"
    },
    "precio_costo": "45.00",
    "precio_venta": "75.00",
    "stock_actual": "50.00",
    "stock_minimo": "10.00",
    "unidad_medida": "unidad",
    "proveedor": "Dental Corp",
    "activo": true,
    "requiere_reposicion": false
  }
]
```

---

### 2. **Insumos con Stock Bajo** ⚠️
```
GET /api/inventario/insumos/bajo_stock/
```

Devuelve solo los insumos donde `stock_actual <= stock_minimo`

**Response**:
```json
[
  {
    "id": 5,
    "codigo": "CEM-ION-001",
    "nombre": "Cemento de Ionómero",
    "stock_actual": "5.00",
    "stock_minimo": "12.00",
    "unidad_medida": "unidad",
    "requiere_reposicion": true
  }
]
```

---

### 3. **Ajustar Stock**
```
POST /api/inventario/insumos/{id}/ajustar_stock/
```

**Request Body**:
```json
{
  "cantidad": 10,        // Positivo = entrada, Negativo = salida
  "motivo": "Compra"     // Opcional
}
```

**Response**:
```json
{
  "mensaje": "Stock ajustado exitosamente",
  "insumo": "Resina Compuesta A2",
  "stock_anterior": 50.00,
  "ajuste": 10.0,
  "stock_actual": 60.00,
  "motivo": "Compra"
}
```

---

### 4. **Categorías de Insumos**
```
GET /api/inventario/categorias/
```

**Response**:
```json
[
  {
    "id": 1,
    "nombre": "Materiales Dentales",
    "descripcion": "Resinas, cementos, amalgamas",
    "activo": true
  }
]
```

---

## 📱 Implementación en Flutter

### 1. **Modelo de Insumo**

```dart
// lib/models/insumo_model.dart

class Insumo {
  final int id;
  final String codigo;
  final String nombre;
  final String? descripcion;
  final CategoriaInsumo categoria;
  final double precioCosto;
  final double precioVenta;
  final double stockActual;
  final double stockMinimo;
  final String unidadMedida;
  final String? proveedor;
  final bool activo;
  final bool requiereReposicion;

  Insumo({
    required this.id,
    required this.codigo,
    required this.nombre,
    this.descripcion,
    required this.categoria,
    required this.precioCosto,
    required this.precioVenta,
    required this.stockActual,
    required this.stockMinimo,
    required this.unidadMedida,
    this.proveedor,
    required this.activo,
    required this.requiereReposicion,
  });

  factory Insumo.fromJson(Map<String, dynamic> json) {
    return Insumo(
      id: json['id'],
      codigo: json['codigo'],
      nombre: json['nombre'],
      descripcion: json['descripcion'],
      categoria: CategoriaInsumo.fromJson(json['categoria']),
      precioCosto: double.parse(json['precio_costo'].toString()),
      precioVenta: double.parse(json['precio_venta'].toString()),
      stockActual: double.parse(json['stock_actual'].toString()),
      stockMinimo: double.parse(json['stock_minimo'].toString()),
      unidadMedida: json['unidad_medida'],
      proveedor: json['proveedor'],
      activo: json['activo'],
      requiereReposicion: json['requiere_reposicion'] ?? false,
    );
  }

  // Calculado: porcentaje de stock
  double get porcentajeStock {
    if (stockMinimo == 0) return 100;
    return (stockActual / stockMinimo) * 100;
  }

  // Calculado: margen de ganancia
  double get margenGanancia {
    if (precioCosto == 0) return 0;
    return ((precioVenta - precioCosto) / precioCosto) * 100;
  }

  // Color de alerta según stock
  Color get colorAlerta {
    if (stockActual <= 0) return Colors.red;
    if (requiereReposicion) return Colors.orange;
    if (porcentajeStock < 150) return Colors.yellow;
    return Colors.green;
  }

  // Icono de alerta
  IconData get iconoAlerta {
    if (stockActual <= 0) return Icons.error;
    if (requiereReposicion) return Icons.warning;
    return Icons.check_circle;
  }
}

class CategoriaInsumo {
  final int id;
  final String nombre;
  final String? descripcion;
  final bool activo;

  CategoriaInsumo({
    required this.id,
    required this.nombre,
    this.descripcion,
    required this.activo,
  });

  factory CategoriaInsumo.fromJson(Map<String, dynamic> json) {
    return CategoriaInsumo(
      id: json['id'],
      nombre: json['nombre'],
      descripcion: json['descripcion'],
      activo: json['activo'],
    );
  }
}
```

---

### 2. **Servicio de Inventario**

```dart
// lib/services/inventario_service.dart

import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/insumo_model.dart';
import 'auth_service.dart';

class InventarioService {
  final String baseUrl;
  final String tenantId;
  final AuthService authService;

  InventarioService({
    required this.baseUrl,
    required this.tenantId,
    required this.authService,
  });

  Future<Map<String, String>> _getHeaders() async {
    final token = await authService.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
      'X-Tenant-ID': tenantId,
    };
  }

  // Listar todos los insumos
  Future<List<Insumo>> getInsumos({
    int? categoriaId,
    bool? activo,
    String? search,
  }) async {
    final headers = await _getHeaders();
    
    // Construir query params
    String url = '$baseUrl/api/inventario/insumos/';
    List<String> params = [];
    
    if (categoriaId != null) params.add('categoria=$categoriaId');
    if (activo != null) params.add('activo=$activo');
    if (search != null && search.isNotEmpty) params.add('search=$search');
    
    if (params.isNotEmpty) {
      url += '?${params.join('&')}';
    }

    final response = await http.get(
      Uri.parse(url),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Insumo.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener insumos: ${response.statusCode}');
    }
  }

  // Listar insumos con stock bajo
  Future<List<Insumo>> getInsumosBajoStock() async {
    final headers = await _getHeaders();
    
    final response = await http.get(
      Uri.parse('$baseUrl/api/inventario/insumos/bajo_stock/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Insumo.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener stock bajo: ${response.statusCode}');
    }
  }

  // Obtener detalle de un insumo
  Future<Insumo> getInsumo(int id) async {
    final headers = await _getHeaders();
    
    final response = await http.get(
      Uri.parse('$baseUrl/api/inventario/insumos/$id/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return Insumo.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al obtener insumo: ${response.statusCode}');
    }
  }

  // Ajustar stock
  Future<Map<String, dynamic>> ajustarStock(
    int insumoId,
    double cantidad,
    String motivo,
  ) async {
    final headers = await _getHeaders();
    
    final response = await http.post(
      Uri.parse('$baseUrl/api/inventario/insumos/$insumoId/ajustar_stock/'),
      headers: headers,
      body: jsonEncode({
        'cantidad': cantidad,
        'motivo': motivo,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al ajustar stock: ${response.body}');
    }
  }

  // Listar categorías
  Future<List<CategoriaInsumo>> getCategorias() async {
    final headers = await _getHeaders();
    
    final response = await http.get(
      Uri.parse('$baseUrl/api/inventario/categorias/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => CategoriaInsumo.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener categorías: ${response.statusCode}');
    }
  }
}
```

---

### 3. **Provider de Inventario**

```dart
// lib/providers/inventario_provider.dart

import 'package:flutter/foundation.dart';
import '../models/insumo_model.dart';
import '../services/inventario_service.dart';

class InventarioProvider with ChangeNotifier {
  final InventarioService _service;

  List<Insumo> _insumos = [];
  List<Insumo> _insumosBajoStock = [];
  List<CategoriaInsumo> _categorias = [];
  bool _isLoading = false;
  String? _error;

  InventarioProvider(this._service);

  // Getters
  List<Insumo> get insumos => _insumos;
  List<Insumo> get insumosBajoStock => _insumosBajoStock;
  List<CategoriaInsumo> get categorias => _categorias;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Estadísticas calculadas
  int get totalInsumos => _insumos.length;
  int get insumosConStockBajo => _insumosBajoStock.length;
  double get valorTotalInventario => _insumos.fold(
    0, 
    (sum, insumo) => sum + (insumo.stockActual * insumo.precioCosto)
  );

  // Cargar insumos
  Future<void> cargarInsumos({
    int? categoriaId,
    bool? activo,
    String? search,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _insumos = await _service.getInsumos(
        categoriaId: categoriaId,
        activo: activo,
        search: search,
      );
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Cargar insumos con stock bajo
  Future<void> cargarStockBajo() async {
    try {
      _insumosBajoStock = await _service.getInsumosBajoStock();
      notifyListeners();
    } catch (e) {
      print('Error al cargar stock bajo: $e');
    }
  }

  // Cargar categorías
  Future<void> cargarCategorias() async {
    try {
      _categorias = await _service.getCategorias();
      notifyListeners();
    } catch (e) {
      print('Error al cargar categorías: $e');
    }
  }

  // Ajustar stock
  Future<bool> ajustarStock(int insumoId, double cantidad, String motivo) async {
    try {
      await _service.ajustarStock(insumoId, cantidad, motivo);
      
      // Recargar los datos
      await cargarInsumos();
      await cargarStockBajo();
      
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
}
```

---

### 4. **Pantalla de Inventario**

```dart
// lib/screens/inventario_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/inventario_provider.dart';
import '../models/insumo_model.dart';

class InventarioScreen extends StatefulWidget {
  @override
  _InventarioScreenState createState() => _InventarioScreenState();
}

class _InventarioScreenState extends State<InventarioScreen> {
  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    final provider = context.read<InventarioProvider>();
    await provider.cargarInsumos();
    await provider.cargarStockBajo();
    await provider.cargarCategorias();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<InventarioProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Text('Inventario'),
        actions: [
          // Indicador de alertas de stock bajo
          if (provider.insumosConStockBajo > 0)
            IconButton(
              icon: Badge(
                label: Text('${provider.insumosConStockBajo}'),
                child: Icon(Icons.warning, color: Colors.orange),
              ),
              onPressed: () => _mostrarStockBajo(context),
            ),
          IconButton(
            icon: Icon(Icons.search),
            onPressed: () => _mostrarBusqueda(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _cargarDatos,
        child: Column(
          children: [
            // Estadísticas en cards
            _buildEstadisticas(provider),
            
            // Lista de insumos
            Expanded(
              child: provider.isLoading
                  ? Center(child: CircularProgressIndicator())
                  : provider.insumos.isEmpty
                      ? Center(child: Text('No hay insumos'))
                      : ListView.builder(
                          itemCount: provider.insumos.length,
                          itemBuilder: (context, index) {
                            final insumo = provider.insumos[index];
                            return _buildInsumoCard(context, insumo);
                          },
                        ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Agregar nuevo insumo
        },
        child: Icon(Icons.add),
      ),
    );
  }

  Widget _buildEstadisticas(InventarioProvider provider) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: _StatCard(
              icon: Icons.inventory,
              title: 'Total Insumos',
              value: '${provider.totalInsumos}',
              color: Colors.blue,
            ),
          ),
          SizedBox(width: 16),
          Expanded(
            child: _StatCard(
              icon: Icons.warning,
              title: 'Stock Bajo',
              value: '${provider.insumosConStockBajo}',
              color: Colors.orange,
            ),
          ),
          SizedBox(width: 16),
          Expanded(
            child: _StatCard(
              icon: Icons.attach_money,
              title: 'Valor Total',
              value: 'Bs ${provider.valorTotalInventario.toStringAsFixed(0)}',
              color: Colors.green,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsumoCard(BuildContext context, Insumo insumo) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: insumo.colorAlerta.withOpacity(0.2),
          child: Icon(
            insumo.iconoAlerta,
            color: insumo.colorAlerta,
          ),
        ),
        title: Text(
          insumo.nombre,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 4),
            Text('Código: ${insumo.codigo}'),
            SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.inventory_2, size: 16, color: Colors.grey),
                SizedBox(width: 4),
                Text(
                  'Stock: ${insumo.stockActual} ${insumo.unidadMedida}',
                  style: TextStyle(
                    color: insumo.requiereReposicion ? Colors.red : Colors.black,
                    fontWeight: insumo.requiereReposicion ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
                SizedBox(width: 16),
                Text(
                  'Mínimo: ${insumo.stockMinimo}',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
            SizedBox(height: 4),
            LinearProgressIndicator(
              value: (insumo.stockActual / insumo.stockMinimo).clamp(0.0, 1.0),
              backgroundColor: Colors.grey[300],
              color: insumo.colorAlerta,
            ),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              'Bs ${insumo.precioVenta}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            Text(
              'Costo: Bs ${insumo.precioCosto}',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        onTap: () => _mostrarDetalleInsumo(context, insumo),
      ),
    );
  }

  void _mostrarDetalleInsumo(BuildContext context, Insumo insumo) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(insumo.nombre),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _InfoRow('Código', insumo.codigo),
            _InfoRow('Categoría', insumo.categoria.nombre),
            _InfoRow('Stock Actual', '${insumo.stockActual} ${insumo.unidadMedida}'),
            _InfoRow('Stock Mínimo', '${insumo.stockMinimo} ${insumo.unidadMedida}'),
            _InfoRow('Precio Costo', 'Bs ${insumo.precioCosto}'),
            _InfoRow('Precio Venta', 'Bs ${insumo.precioVenta}'),
            _InfoRow('Margen', '${insumo.margenGanancia.toStringAsFixed(1)}%'),
            if (insumo.proveedor != null)
              _InfoRow('Proveedor', insumo.proveedor!),
            if (insumo.descripcion != null)
              Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text(
                  insumo.descripcion!,
                  style: TextStyle(color: Colors.grey),
                ),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cerrar'),
          ),
          ElevatedButton.icon(
            icon: Icon(Icons.add_circle),
            label: Text('Ajustar Stock'),
            onPressed: () {
              Navigator.pop(context);
              _mostrarDialogoAjuste(context, insumo);
            },
          ),
        ],
      ),
    );
  }

  void _mostrarDialogoAjuste(BuildContext context, Insumo insumo) {
    final cantidadController = TextEditingController();
    final motivoController = TextEditingController();
    bool esEntrada = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text('Ajustar Stock'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${insumo.nombre}\nStock actual: ${insumo.stockActual} ${insumo.unidadMedida}',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 16),
              SegmentedButton<bool>(
                segments: [
                  ButtonSegment(
                    value: true,
                    label: Text('Entrada'),
                    icon: Icon(Icons.add, color: Colors.green),
                  ),
                  ButtonSegment(
                    value: false,
                    label: Text('Salida'),
                    icon: Icon(Icons.remove, color: Colors.red),
                  ),
                ],
                selected: {esEntrada},
                onSelectionChanged: (Set<bool> newSelection) {
                  setState(() {
                    esEntrada = newSelection.first;
                  });
                },
              ),
              SizedBox(height: 16),
              TextField(
                controller: cantidadController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Cantidad',
                  border: OutlineInputBorder(),
                  suffixText: insumo.unidadMedida,
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: motivoController,
                decoration: InputDecoration(
                  labelText: 'Motivo (opcional)',
                  border: OutlineInputBorder(),
                  hintText: esEntrada ? 'Compra, Donación...' : 'Uso, Vencido...',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () async {
                final cantidad = double.tryParse(cantidadController.text);
                if (cantidad == null || cantidad <= 0) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Cantidad inválida')),
                  );
                  return;
                }

                final cantidadFinal = esEntrada ? cantidad : -cantidad;
                final provider = context.read<InventarioProvider>();

                Navigator.pop(context);

                final success = await provider.ajustarStock(
                  insumo.id,
                  cantidadFinal,
                  motivoController.text.isEmpty ? (esEntrada ? 'Entrada' : 'Salida') : motivoController.text,
                );

                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Stock ajustado exitosamente'),
                      backgroundColor: Colors.green,
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Error al ajustar stock'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: esEntrada ? Colors.green : Colors.red,
              ),
              child: Text('Confirmar'),
            ),
          ],
        ),
      ),
    );
  }

  void _mostrarStockBajo(BuildContext context) {
    final provider = context.read<InventarioProvider>();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.warning, color: Colors.orange),
            SizedBox(width: 8),
            Text('Alertas de Stock Bajo'),
          ],
        ),
        content: Container(
          width: double.maxFinite,
          child: provider.insumosBajoStock.isEmpty
              ? Text('✅ No hay insumos con stock bajo')
              : ListView.builder(
                  shrinkWrap: true,
                  itemCount: provider.insumosBajoStock.length,
                  itemBuilder: (context, index) {
                    final insumo = provider.insumosBajoStock[index];
                    return ListTile(
                      leading: Icon(Icons.error, color: Colors.red),
                      title: Text(insumo.nombre),
                      subtitle: Text(
                        'Stock: ${insumo.stockActual} / Mínimo: ${insumo.stockMinimo}',
                      ),
                      trailing: Text(
                        '${insumo.unidadMedida}',
                        style: TextStyle(color: Colors.grey),
                      ),
                    );
                  },
                ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cerrar'),
          ),
        ],
      ),
    );
  }

  void _mostrarBusqueda(BuildContext context) {
    // TODO: Implementar búsqueda
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '$label:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(value),
        ],
      ),
    );
  }
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear modelo `Insumo` con propiedades calculadas
- [ ] Crear `InventarioService` con todos los endpoints
- [ ] Crear `InventarioProvider` para gestión de estado
- [ ] Implementar pantalla de inventario con lista y filtros
- [ ] Agregar indicador de alertas de stock bajo
- [ ] Implementar diálogo de ajuste de stock
- [ ] Agregar estadísticas visuales (cards, progress bars)
- [ ] Probar con diferentes escenarios

---

## 🎯 Características Clave

✅ **Alertas visuales**: Colores e iconos según nivel de stock
✅ **Stock bajo**: Badge en AppBar con contador
✅ **Ajuste de stock**: Entrada/Salida con motivo
✅ **Estadísticas**: Total insumos, stock bajo, valor total
✅ **Progress bar**: Indicador visual del nivel de stock
✅ **Filtros**: Por categoría, activo, búsqueda

¡Listo para implementar! 📦✨
