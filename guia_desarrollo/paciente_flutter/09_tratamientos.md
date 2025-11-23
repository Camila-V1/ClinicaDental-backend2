# 🦷 Tratamientos

## 🎯 Objetivo
Mostrar planes de tratamiento activos y finalizados con progreso detallado.

---

## 📡 Modelos

### `lib/models/tratamiento.dart`

```dart
class PlanTratamiento {
  final int id;
  final String nombre;
  final String descripcion;
  final double costoTotal;
  final double montoAbonado;
  final String estado;
  final DateTime fechaInicio;
  final DateTime? fechaFin;
  final String odontologoNombre;
  final List<ItemTratamiento> items;
  final int progresoPercentage;

  PlanTratamiento({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.costoTotal,
    required this.montoAbonado,
    required this.estado,
    required this.fechaInicio,
    this.fechaFin,
    required this.odontologoNombre,
    required this.items,
    required this.progresoPercentage,
  });

  factory PlanTratamiento.fromJson(Map<String, dynamic> json) {
    return PlanTratamiento(
      id: json['id'],
      nombre: json['nombre'] ?? '',
      descripcion: json['descripcion'] ?? '',
      costoTotal: double.parse(json['costo_total']?.toString() ?? '0'),
      montoAbonado: double.parse(json['monto_abonado']?.toString() ?? '0'),
      estado: json['estado'] ?? '',
      fechaInicio: DateTime.parse(json['fecha_inicio']),
      fechaFin: json['fecha_fin'] != null
          ? DateTime.parse(json['fecha_fin'])
          : null,
      odontologoNombre: json['odontologo']['usuario']['full_name'] ?? '',
      items: (json['items'] as List?)
          ?.map((e) => ItemTratamiento.fromJson(e))
          .toList() ?? [],
      progresoPercentage: json['progreso_percentage'] ?? 0,
    );
  }

  double get saldoPendiente => costoTotal - montoAbonado;
  bool get isActivo => estado == 'ACTIVO';
  bool get isCompletado => estado == 'COMPLETADO';
  bool get isPendiente => estado == 'PENDIENTE';
}

class ItemTratamiento {
  final int id;
  final String servicio;
  final String? piezaDental;
  final double costo;
  final String estado;
  final int sesionesRequeridas;
  final int sesionesCompletadas;
  final DateTime? fechaInicio;
  final DateTime? fechaFin;
  final String? notas;

  ItemTratamiento({
    required this.id,
    required this.servicio,
    this.piezaDental,
    required this.costo,
    required this.estado,
    required this.sesionesRequeridas,
    required this.sesionesCompletadas,
    this.fechaInicio,
    this.fechaFin,
    this.notas,
  });

  factory ItemTratamiento.fromJson(Map<String, dynamic> json) {
    return ItemTratamiento(
      id: json['id'],
      servicio: json['servicio']['nombre'] ?? '',
      piezaDental: json['pieza_dental'],
      costo: double.parse(json['costo']?.toString() ?? '0'),
      estado: json['estado'] ?? '',
      sesionesRequeridas: json['sesiones_requeridas'] ?? 1,
      sesionesCompletadas: json['sesiones_completadas'] ?? 0,
      fechaInicio: json['fecha_inicio'] != null
          ? DateTime.parse(json['fecha_inicio'])
          : null,
      fechaFin: json['fecha_fin'] != null
          ? DateTime.parse(json['fecha_fin'])
          : null,
      notas: json['notas'],
    );
  }

  int get progresoPercentage {
    if (sesionesRequeridas == 0) return 0;
    return ((sesionesCompletadas / sesionesRequeridas) * 100).round();
  }

  bool get isCompletado => estado == 'COMPLETADO';
  bool get isPendiente => estado == 'PENDIENTE';
  bool get isEnProceso => estado == 'EN_PROCESO';
}
```

---

## 🔌 Servicio

> **✅ ACTUALIZADO - 23/11/2025**  
> Ahora usa los **mismos endpoints que el web** (probados y funcionando)

### `lib/services/tratamientos_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/tratamiento.dart';

class TratamientosService {
  final String baseUrl = AppConstants.baseUrlDev;

  /// ✅ Obtener mis planes de tratamiento (mismo endpoint que el web)
  Future<List<PlanTratamiento>> getMisTratamientos({
    required String token,
    required String tenantId,
    String? estado,
  }) async {
    try {
      String url = '$baseUrl/api/tratamientos/planes/';
      
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
        final List<dynamic> planes = data['results'] ?? data;
        return planes.map((json) => PlanTratamiento.fromJson(json)).toList();
      } else if (response.statusCode == 401) {
        throw TokenExpiredException('Token expirado');
      } else {
        throw Exception('Error al cargar tratamientos: ${response.statusCode}');
      }
    } catch (e) {
      if (e is TokenExpiredException) rethrow;
      throw Exception('Error de conexión: $e');
    }
  }

  /// ✅ Obtener detalle de plan con items
  Future<PlanTratamiento> getPlanDetalle({
    required String token,
    required String tenantId,
    required int planId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/tratamientos/planes/$planId/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return PlanTratamiento.fromJson(data);
      } else if (response.statusCode == 401) {
        throw TokenExpiredException('Token expirado');
      } else {
        throw Exception('Error al cargar plan: ${response.statusCode}');
      }
    } catch (e) {
      if (e is TokenExpiredException) rethrow;
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// ✅ Obtener items de un plan
  Future<List<ItemTratamiento>> getPlanItems({
    required String token,
    required String tenantId,
    required int planId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/tratamientos/planes/$planId/items/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> items = data['results'] ?? data;
        return items.map((json) => ItemTratamiento.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar items: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}

class TokenExpiredException implements Exception {
  final String message;
  TokenExpiredException(this.message);
  
  @override
  String toString() => message;
}
```

---

## 📱 Pantalla Principal

### `lib/screens/tratamientos/tratamientos_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/models/tratamiento.dart';
import 'package:clinica_dental_app/services/tratamientos_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';
import 'package:clinica_dental_app/widgets/tratamientos/plan_card.dart';

class TratamientosScreen extends StatefulWidget {
  const TratamientosScreen({super.key});

  @override
  State<TratamientosScreen> createState() => _TratamientosScreenState();
}

class _TratamientosScreenState extends State<TratamientosScreen>
    with SingleTickerProviderStateMixin {
  final TratamientosService _service = TratamientosService();
  late TabController _tabController;

  List<PlanTratamiento> _planesActivos = [];
  List<PlanTratamiento> _planesFinalizados = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _cargarTratamientos();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _cargarTratamientos() async {
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

      final planes = await _service.getMisTratamientos(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
      );

      setState(() {
        _planesActivos = planes
            .where((p) => p.isActivo || p.isPendiente)
            .toList();
        _planesFinalizados = planes
            .where((p) => p.isCompletado)
            .toList();
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
      appBar: AppBar(
        title: const Text('Mis Tratamientos'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Activos'),
            Tab(text: 'Finalizados'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : _error != null
              ? _buildError()
              : RefreshIndicator(
                  onRefresh: _cargarTratamientos,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildPlanesList(_planesActivos, esActivo: true),
                      _buildPlanesList(_planesFinalizados, esActivo: false),
                    ],
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
          const Text('Error al cargar tratamientos'),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _cargarTratamientos,
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildPlanesList(List<PlanTratamiento> planes, {required bool esActivo}) {
    if (planes.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.medical_services_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              esActivo
                  ? 'No tienes tratamientos activos'
                  : 'No hay tratamientos finalizados',
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
      itemCount: planes.length,
      itemBuilder: (context, index) {
        final plan = planes[index];
        return PlanCard(
          plan: plan,
          onTap: () => _mostrarDetallePlan(plan),
        );
      },
    );
  }

  void _mostrarDetallePlan(PlanTratamiento plan) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DetallePlanScreen(plan: plan),
      ),
    );
  }
}
```

---

## 📋 Detalle del Plan

### `lib/screens/tratamientos/detalle_plan_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/models/tratamiento.dart';
import 'package:clinica_dental_app/widgets/tratamientos/item_tratamiento_card.dart';

class DetallePlanScreen extends StatelessWidget {
  final PlanTratamiento plan;

  const DetallePlanScreen({super.key, required this.plan});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalle del Tratamiento'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header con info general
            _buildHeader(context),

            // Progreso
            _buildProgresoSection(context),

            // Costos
            _buildCostosSection(context),

            // Items del tratamiento
            _buildItemsSection(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).primaryColor,
            Theme.of(context).primaryColor.withOpacity(0.7),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.3),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              plan.estado,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            plan.nombre,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            plan.descripcion,
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              const Icon(Icons.person, color: Colors.white, size: 16),
              const SizedBox(width: 8),
              Text(
                'Dr. ${plan.odontologoNombre}',
                style: const TextStyle(color: Colors.white),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.calendar_today, color: Colors.white, size: 16),
              const SizedBox(width: 8),
              Text(
                'Inicio: ${DateFormat('dd/MM/yyyy').format(plan.fechaInicio)}',
                style: const TextStyle(color: Colors.white),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProgresoSection(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Progreso del Tratamiento',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              Text(
                '${plan.progresoPercentage}%',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: plan.progresoPercentage / 100,
              minHeight: 12,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(
                Theme.of(context).primaryColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCostosSection(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Costo Total:'),
              Text(
                '\$${plan.costoTotal.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Monto Abonado:'),
              Text(
                '\$${plan.montoAbonado.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Saldo Pendiente:'),
              Text(
                '\$${plan.saldoPendiente.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildItemsSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Procedimientos (${plan.items.length})',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          ...plan.items.map((item) => ItemTratamientoCard(item: item)),
        ],
      ),
    );
  }
}
```

---

## 🎨 Widgets

### `lib/widgets/tratamientos/plan_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:clinica_dental_app/models/tratamiento.dart';

class PlanCard extends StatelessWidget {
  final PlanTratamiento plan;
  final VoidCallback onTap;

  const PlanCard({
    super.key,
    required this.plan,
    required this.onTap,
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
                  Expanded(
                    child: Text(
                      plan.nombre,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
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
                      plan.estado,
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
              Text(
                plan.descripcion,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.person, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    'Dr. ${plan.odontologoNombre}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: plan.progresoPercentage / 100,
                  minHeight: 8,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Theme.of(context).primaryColor,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Progreso: ${plan.progresoPercentage}%',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  Text(
                    '\$${plan.costoTotal.toStringAsFixed(0)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
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

  Color _getEstadoColor() {
    if (plan.isActivo) return Colors.green;
    if (plan.isCompletado) return Colors.blue;
    return Colors.orange;
  }
}
```

### `lib/widgets/tratamientos/item_tratamiento_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:clinica_dental_app/models/tratamiento.dart';

class ItemTratamientoCard extends StatelessWidget {
  final ItemTratamiento item;

  const ItemTratamientoCard({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    item.servicio,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                if (item.piezaDental != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Pieza ${item.piezaDental}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Sesiones',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Text(
                        '${item.sesionesCompletadas}/${item.sesionesRequeridas}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Estado',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Text(
                        item.estado,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _getEstadoColor(),
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      'Costo',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    Text(
                      '\$${item.costo.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: item.progresoPercentage / 100,
                minHeight: 6,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation<Color>(_getEstadoColor()),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getEstadoColor() {
    if (item.isCompletado) return Colors.green;
    if (item.isEnProceso) return Colors.blue;
    return Colors.orange;
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelos `PlanTratamiento` e `ItemTratamiento`
- [ ] Crear `TratamientosService`
- [ ] Crear `TratamientosScreen` con tabs
- [ ] Crear `DetallePlanScreen`
- [ ] Widget `PlanCard`
- [ ] Widget `ItemTratamientoCard`
- [ ] Indicadores de progreso
- [ ] Información de costos

---

**Siguiente:** [10_facturas_pagos.md](10_facturas_pagos.md)
