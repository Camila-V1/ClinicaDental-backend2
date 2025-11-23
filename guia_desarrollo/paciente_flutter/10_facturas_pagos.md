# 💰 Facturas y Pagos

## 🎯 Objetivo
Gestionar visualización de facturas y realizar pagos en línea.

---

## 📡 Modelos

### `lib/models/factura.dart`

```dart
class Factura {
  final int id;
  final String numero;
  final DateTime fecha;
  final double subtotal;
  final double impuestos;
  final double total;
  final String estado;
  final DateTime? fechaVencimiento;
  final List<ItemFactura> items;
  final List<Pago> pagos;
  final int? planTratamientoId;

  Factura({
    required this.id,
    required this.numero,
    required this.fecha,
    required this.subtotal,
    required this.impuestos,
    required this.total,
    required this.estado,
    this.fechaVencimiento,
    required this.items,
    required this.pagos,
    this.planTratamientoId,
  });

  factory Factura.fromJson(Map<String, dynamic> json) {
    return Factura(
      id: json['id'],
      numero: json['numero'] ?? '',
      fecha: DateTime.parse(json['fecha']),
      subtotal: double.parse(json['subtotal']?.toString() ?? '0'),
      impuestos: double.parse(json['impuestos']?.toString() ?? '0'),
      total: double.parse(json['total']?.toString() ?? '0'),
      estado: json['estado'] ?? '',
      fechaVencimiento: json['fecha_vencimiento'] != null
          ? DateTime.parse(json['fecha_vencimiento'])
          : null,
      items: (json['items'] as List?)
          ?.map((e) => ItemFactura.fromJson(e))
          .toList() ?? [],
      pagos: (json['pagos'] as List?)
          ?.map((e) => Pago.fromJson(e))
          .toList() ?? [],
      planTratamientoId: json['plan_tratamiento'],
    );
  }

  double get montoAbonado {
    return pagos.fold(0.0, (sum, pago) => sum + pago.monto);
  }

  double get saldoPendiente => total - montoAbonado;
  bool get isPagada => estado == 'PAGADA';
  bool get isPendiente => estado == 'PENDIENTE';
  bool get isParcial => estado == 'PARCIAL';
  bool get isVencida {
    if (fechaVencimiento == null) return false;
    return DateTime.now().isAfter(fechaVencimiento!) && !isPagada;
  }
}

class ItemFactura {
  final int id;
  final String descripcion;
  final int cantidad;
  final double precioUnitario;
  final double subtotal;

  ItemFactura({
    required this.id,
    required this.descripcion,
    required this.cantidad,
    required this.precioUnitario,
    required this.subtotal,
  });

  factory ItemFactura.fromJson(Map<String, dynamic> json) {
    return ItemFactura(
      id: json['id'],
      descripcion: json['descripcion'] ?? '',
      cantidad: json['cantidad'] ?? 1,
      precioUnitario: double.parse(json['precio_unitario']?.toString() ?? '0'),
      subtotal: double.parse(json['subtotal']?.toString() ?? '0'),
    );
  }
}

class Pago {
  final int id;
  final DateTime fecha;
  final double monto;
  final String metodoPago;
  final String? referencia;
  final String estado;

  Pago({
    required this.id,
    required this.fecha,
    required this.monto,
    required this.metodoPago,
    this.referencia,
    required this.estado,
  });

  factory Pago.fromJson(Map<String, dynamic> json) {
    return Pago(
      id: json['id'],
      fecha: DateTime.parse(json['fecha']),
      monto: double.parse(json['monto']?.toString() ?? '0'),
      metodoPago: json['metodo_pago'] ?? '',
      referencia: json['referencia'],
      estado: json['estado'] ?? '',
    );
  }
}
```

---

## 🔌 Servicios

> **✅ ACTUALIZADO - 23/11/2025**  
> Ahora usa los **mismos endpoints que el web** (probados y funcionando)

### `lib/services/facturas_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/factura.dart';

class FacturasService {
  final String baseUrl = AppConstants.baseUrlDev;

  /// ✅ Obtener mis facturas (mismo endpoint que el web)
  Future<List<Factura>> getMisFacturas({
    required String token,
    required String tenantId,
    String? estado,
  }) async {
    try {
      String url = '$baseUrl/api/facturacion/facturas/mis_facturas/';
      
      if (estado != null) {
        url += '?estado=$estado';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,  // ✅ Usar Host en lugar de X-Tenant-ID
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // El endpoint mis_facturas retorna una lista directa
        final List<dynamic> facturas = data is List ? data : (data['results'] ?? []);
        return facturas.map((json) => Factura.fromJson(json)).toList();
      } else if (response.statusCode == 401) {
        throw TokenExpiredException('Token expirado');
      } else {
        throw Exception('Error al cargar facturas: ${response.statusCode}');
      }
    } catch (e) {
      if (e is TokenExpiredException) rethrow;
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// ✅ Obtener estado de cuenta (saldo pendiente total)
  Future<Map<String, dynamic>> getEstadoCuenta({
    required String token,
    required String tenantId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/facturacion/facturas/estado_cuenta/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar estado de cuenta: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  /// ✅ Obtener detalle de factura
  Future<Factura> getFactura({
    required String token,
    required String tenantId,
    required int facturaId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/facturacion/facturas/$facturaId/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Factura.fromJson(data);
      } else if (response.statusCode == 401) {
        throw TokenExpiredException('Token expirado');
      } else {
        throw Exception('Error al cargar factura: ${response.statusCode}');
      }
    } catch (e) {
      if (e is TokenExpiredException) rethrow;
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// ✅ Obtener pagos de una factura
  Future<List<Pago>> getPagosFactura({
    required String token,
    required String tenantId,
    required int facturaId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/facturacion/facturas/$facturaId/pagos/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> pagos = data is List ? data : (data['results'] ?? []);
        return pagos.map((json) => Pago.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar pagos: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Registrar pago
  Future<void> registrarPago({
    required String token,
    required String tenantId,
    required int facturaId,
    required double monto,
    required String metodoPago,
    String? referencia,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/facturacion/pagos/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'factura': facturaId,
          'monto': monto,
          'metodo_pago': metodoPago,
          'referencia': referencia,
        }),
      );

      if (response.statusCode != 201) {
        throw Exception('Error al registrar pago');
      }
    } catch (e) {
      throw Exception('Error al procesar pago: $e');
    }
  }

  // Descargar PDF de factura
  Future<void> descargarPDF({
    required String token,
    required String tenantId,
    required int facturaId,
  }) async {
    // Implementar descarga de PDF
  }
}
```

---

## 📱 Pantalla Principal

### `lib/screens/facturas/facturas_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/models/factura.dart';
import 'package:clinica_dental_app/services/facturas_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';
import 'package:clinica_dental_app/widgets/facturas/factura_card.dart';

class FacturasScreen extends StatefulWidget {
  const FacturasScreen({super.key});

  @override
  State<FacturasScreen> createState() => _FacturasScreenState();
}

class _FacturasScreenState extends State<FacturasScreen>
    with SingleTickerProviderStateMixin {
  final FacturasService _service = FacturasService();
  late TabController _tabController;

  List<Factura> _facturasPendientes = [];
  List<Factura> _facturasPagadas = [];
  bool _isLoading = true;
  String? _error;
  double _totalPendiente = 0.0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _cargarFacturas();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _cargarFacturas() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    if (authProvider.accessToken == null ||
        clinicaProvider.clinicaSeleccionada == null) {
      return;
    }

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final facturas = await _service.getMisFacturas(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
      );

      setState(() {
        _facturasPendientes = facturas
            .where((f) => !f.isPagada)
            .toList()
          ..sort((a, b) => b.fecha.compareTo(a.fecha));
        
        _facturasPagadas = facturas
            .where((f) => f.isPagada)
            .toList()
          ..sort((a, b) => b.fecha.compareTo(a.fecha));

        _totalPendiente = _facturasPendientes.fold(
          0.0,
          (sum, f) => sum + f.saldoPendiente,
        );
        
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverAppBar(
              expandedHeight: 160,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('Mis Facturas'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Theme.of(context).primaryColor,
                        Theme.of(context).primaryColor.withOpacity(0.7),
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Saldo Pendiente',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 14,
                            ),
                          ),
                          Text(
                            '\$${_totalPendiente.toStringAsFixed(2)}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              bottom: TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: 'Pendientes'),
                  Tab(text: 'Pagadas'),
                ],
              ),
            ),
          ];
        },
        body: _isLoading
            ? const Center(child: LoadingIndicator())
            : _error != null
                ? _buildError()
                : RefreshIndicator(
                    onRefresh: _cargarFacturas,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        _buildFacturasList(_facturasPendientes, esPendiente: true),
                        _buildFacturasList(_facturasPagadas, esPendiente: false),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          const Text('Error al cargar facturas'),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _cargarFacturas,
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildFacturasList(List<Factura> facturas, {required bool esPendiente}) {
    if (facturas.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.receipt_long_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              esPendiente
                  ? 'No tienes facturas pendientes'
                  : 'No hay facturas pagadas',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: facturas.length,
      itemBuilder: (context, index) {
        final factura = facturas[index];
        return FacturaCard(
          factura: factura,
          onTap: () => _mostrarDetalleFactura(factura),
          onPagar: esPendiente
              ? () => _mostrarFormularioPago(factura)
              : null,
        );
      },
    );
  }

  void _mostrarDetalleFactura(Factura factura) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DetalleFacturaScreen(factura: factura),
      ),
    );
  }

  void _mostrarFormularioPago(Factura factura) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => FormularioPagoSheet(
        factura: factura,
        onPagoExitoso: () {
          _cargarFacturas();
        },
      ),
    );
  }
}
```

---

## 💳 Formulario de Pago

### `lib/widgets/facturas/formulario_pago_sheet.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/models/factura.dart';
import 'package:clinica_dental_app/services/facturas_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';

class FormularioPagoSheet extends StatefulWidget {
  final Factura factura;
  final VoidCallback onPagoExitoso;

  const FormularioPagoSheet({
    super.key,
    required this.factura,
    required this.onPagoExitoso,
  });

  @override
  State<FormularioPagoSheet> createState() => _FormularioPagoSheetState();
}

class _FormularioPagoSheetState extends State<FormularioPagoSheet> {
  final _formKey = GlobalKey<FormState>();
  final _montoController = TextEditingController();
  final _referenciaController = TextEditingController();
  final FacturasService _service = FacturasService();
  
  String _metodoPago = 'EFECTIVO';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _montoController.text = widget.factura.saldoPendiente.toStringAsFixed(2);
  }

  @override
  void dispose() {
    _montoController.dispose();
    _referenciaController.dispose();
    super.dispose();
  }

  Future<void> _procesarPago() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    setState(() => _isLoading = true);

    try {
      await _service.registrarPago(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
        facturaId: widget.factura.id,
        monto: double.parse(_montoController.text),
        metodoPago: _metodoPago,
        referencia: _referenciaController.text.isEmpty
            ? null
            : _referenciaController.text,
      );

      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Pago registrado exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
        widget.onPagoExitoso();
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Título
              Text(
                'Registrar Pago',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                'Factura: ${widget.factura.numero}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 24),

              // Saldo pendiente
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Saldo Pendiente:',
                      style: TextStyle(fontWeight: FontWeight.w500),
                    ),
                    Text(
                      '\$${widget.factura.saldoPendiente.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Monto
              TextFormField(
                controller: _montoController,
                decoration: const InputDecoration(
                  labelText: 'Monto a Pagar',
                  prefixText: '\$ ',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Ingresa el monto';
                  }
                  final monto = double.tryParse(value);
                  if (monto == null || monto <= 0) {
                    return 'Monto inválido';
                  }
                  if (monto > widget.factura.saldoPendiente) {
                    return 'Monto excede el saldo pendiente';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Método de pago
              DropdownButtonFormField<String>(
                value: _metodoPago,
                decoration: const InputDecoration(
                  labelText: 'Método de Pago',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'EFECTIVO', child: Text('Efectivo')),
                  DropdownMenuItem(value: 'TARJETA', child: Text('Tarjeta')),
                  DropdownMenuItem(value: 'TRANSFERENCIA', child: Text('Transferencia')),
                ],
                onChanged: (value) {
                  setState(() => _metodoPago = value!);
                },
              ),
              const SizedBox(height: 16),

              // Referencia
              TextFormField(
                controller: _referenciaController,
                decoration: const InputDecoration(
                  labelText: 'Referencia (Opcional)',
                  hintText: 'Número de transacción, recibo, etc.',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),

              // Botones
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _isLoading ? null : () => Navigator.pop(context),
                      child: const Text('Cancelar'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _procesarPago,
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Pagar'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## 🎨 Widgets

### `lib/widgets/facturas/factura_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/models/factura.dart';

class FacturaCard extends StatelessWidget {
  final Factura factura;
  final VoidCallback onTap;
  final VoidCallback? onPagar;

  const FacturaCard({
    super.key,
    required this.factura,
    required this.onTap,
    this.onPagar,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    factura.numero,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: _getEstadoColor().withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      factura.estado,
                      style: TextStyle(
                        color: _getEstadoColor(),
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 14, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    DateFormat('dd/MM/yyyy').format(factura.fecha),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (factura.isVencida) ...[
                    const SizedBox(width: 12),
                    Icon(Icons.warning, size: 14, color: Colors.red.shade700),
                    const SizedBox(width: 4),
                    Text(
                      'Vencida',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.red.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ],
              ),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Total',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Text(
                        '\$${factura.total.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  if (!factura.isPagada) ...[
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'Saldo',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        Text(
                          '\$${factura.saldoPendiente.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.orange,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
              if (onPagar != null) ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: onPagar,
                    child: const Text('Pagar'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Color _getEstadoColor() {
    if (factura.isPagada) return Colors.green;
    if (factura.isVencida) return Colors.red;
    if (factura.isParcial) return Colors.blue;
    return Colors.orange;
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelos `Factura`, `ItemFactura` y `Pago`
- [ ] Crear `FacturasService`
- [ ] Crear `FacturasScreen` con tabs
- [ ] Widget `FacturaCard`
- [ ] Formulario de pago
- [ ] Validación de montos
- [ ] Indicador de saldo total
- [ ] Detectar facturas vencidas

---

**Siguiente:** [11_perfil_configuracion.md](11_perfil_configuracion.md)
