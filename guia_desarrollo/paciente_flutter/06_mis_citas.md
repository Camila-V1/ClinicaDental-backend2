# 📅 Mis Citas

> **✅ GUÍA ACTUALIZADA** - 22/11/2025  
> Esta guía ha sido corregida para reflejar los endpoints reales del backend.  
> Cambios principales:
> - Endpoint: `/api/agenda/citas/` o `/api/agenda/citas/proximas/` (no `/api/agenda/mis-citas/`)
> - Estado: `ATENDIDA` (no `COMPLETADA`)
> - El backend filtra automáticamente por usuario autenticado

## 🎯 Objetivo
Permitir al paciente ver sus citas programadas, pasadas y cancelar/reagendar.

---

## 📡 Modelo de Cita

### `lib/models/cita.dart`

```dart
class CitaDetallada {
  final int id;
  final DateTime fechaHora;
  final int duracionMinutos;
  final String motivo;
  final String estado;
  final String? notas;
  final Odontologo odontologo;
  final bool puedeModificar;

  CitaDetallada({
    required this.id,
    required this.fechaHora,
    required this.duracionMinutos,
    required this.motivo,
    required this.estado,
    this.notas,
    required this.odontologo,
    this.puedeModificar = false,
  });

  factory CitaDetallada.fromJson(Map<String, dynamic> json) {
    return CitaDetallada(
      id: json['id'],
      fechaHora: DateTime.parse(json['fecha_hora']),
      duracionMinutos: json['duracion_minutos'] ?? 30,
      motivo: json['motivo'] ?? '',
      estado: json['estado'] ?? '',
      notas: json['notas'],
      odontologo: Odontologo.fromJson(json['odontologo']),
      puedeModificar: json['puede_modificar'] ?? false,
    );
  }

  bool get isPendiente => estado == 'PENDIENTE';
  bool get isConfirmada => estado == 'CONFIRMADA';
  bool get isAtendida => estado == 'ATENDIDA';      // ✅ Cambio: Backend usa 'ATENDIDA', no 'COMPLETADA'
  bool get isCancelada => estado == 'CANCELADA';
  bool get isPasada => fechaHora.isBefore(DateTime.now());
}

class Odontologo {
  final int id;
  final String nombre;
  final String? especialidad;
  final String? foto;

  Odontologo({
    required this.id,
    required this.nombre,
    this.especialidad,
    this.foto,
  });

  factory Odontologo.fromJson(Map<String, dynamic> json) {
    return Odontologo(
      id: json['id'],
      nombre: json['usuario']['full_name'] ?? '',
      especialidad: json['especialidad'],
      foto: json['usuario']['foto'],
    );
  }
}
```

---

## 🔌 Servicio de Citas

### `lib/services/citas_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/cita.dart';

class CitaService {
  // ✅ IMPORTANTE: Usar URL de producción (Render), NO localhost
  final String baseUrl = 'https://clinica-dental-backend.onrender.com';

  // Obtener mis citas
  // ✅ Backend filtra automáticamente por usuario autenticado
  Future<List<CitaDetallada>> getMisCitas({
    required String token,
    required String tenantId,
    String? estado,
    bool soloProximas = false,
  }) async {
    try {
      // ✅ Endpoints disponibles:
      // - /api/agenda/citas/ (lista general, ya filtra por usuario)
      // - /api/agenda/citas/proximas/ (solo futuras PENDIENTE/CONFIRMADA)
      // - /api/agenda/citas/hoy/ (solo de hoy)
      String url;
      if (soloProximas) {
        url = '$baseUrl/api/agenda/citas/proximas/';  // ✅ Custom action
      } else {
        url = '$baseUrl/api/agenda/citas/';  // ✅ Lista general
        if (estado != null) {
          url += '?estado=$estado';  // ✅ Filtro por estado
        }
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Host': '$tenantId.localhost',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // ✅ Backend puede retornar array directo o paginado
        final List<dynamic> citas = data is List ? data : (data['results'] ?? []);
        return citas.map((json) => CitaDetallada.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar citas');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener detalle de cita
  Future<CitaDetallada> getCita({
    required String token,
    required String tenantId,
    required int citaId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/agenda/citas/$citaId/'),
        headers: {
          'Content-Type': 'application/json',
          'Host': '$tenantId.localhost',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return CitaDetallada.fromJson(data);
      } else {
        throw Exception('Error al cargar cita');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Cancelar cita
  Future<void> cancelarCita({
    required String token,
    required String tenantId,
    required int citaId,
    String? motivo,
  }) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/api/agenda/citas/$citaId/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'estado': 'CANCELADA',
          'notas': motivo ?? 'Cancelada por el paciente',
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Error al cancelar cita');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Confirmar cita
  Future<void> confirmarCita({
    required String token,
    required String tenantId,
    required int citaId,
  }) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/api/agenda/citas/$citaId/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
        body: json.encode({'estado': 'CONFIRMADA'}),
      );

      if (response.statusCode != 200) {
        throw Exception('Error al confirmar cita');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}
```

---

## 📱 Pantalla de Mis Citas

### `lib/screens/citas/mis_citas_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/models/cita.dart';
import 'package:clinica_dental_app/services/citas_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/citas/cita_card.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';

class MisCitasScreen extends StatefulWidget {
  const MisCitasScreen({super.key});

  @override
  State<MisCitasScreen> createState() => _MisCitasScreenState();
}

class _MisCitasScreenState extends State<MisCitasScreen> with SingleTickerProviderStateMixin {
  final CitasService _citasService = CitasService();
  late TabController _tabController;
  
  List<CitaDetallada> _citasProximas = [];
  List<CitaDetallada> _citasPasadas = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _cargarCitas();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _cargarCitas() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    if (authProvider.accessToken == null || clinicaProvider.clinicaSeleccionada == null) {
      return;
    }

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final todasCitas = await _citasService.getMisCitas(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
      );

      final ahora = DateTime.now();
      
      setState(() {
        _citasProximas = todasCitas
            .where((cita) => cita.fechaHora.isAfter(ahora) && !cita.isCancelada)
            .toList()
          ..sort((a, b) => a.fechaHora.compareTo(b.fechaHora));
        
        _citasPasadas = todasCitas
            .where((cita) => cita.fechaHora.isBefore(ahora) || cita.isCancelada)
            .toList()
          ..sort((a, b) => b.fechaHora.compareTo(a.fechaHora));
        
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _cancelarCita(CitaDetallada cita) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancelar Cita'),
        content: const Text('¿Estás seguro de que deseas cancelar esta cita?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('No'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Sí, cancelar'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    try {
      await _citasService.cancelarCita(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
        citaId: cita.id,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cita cancelada exitosamente')),
        );
        _cargarCitas();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al cancelar: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      appBar: AppBar(
        title: const Text('Mis Citas'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Próximas'),
            Tab(text: 'Historial'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : _error != null
              ? _buildError()
              : RefreshIndicator(
                  onRefresh: _cargarCitas,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildCitasList(_citasProximas, esProximas: true),
                      _buildCitasList(_citasPasadas, esProximas: false),
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
          const Text('Error al cargar citas'),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _cargarCitas,
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildCitasList(List<CitaDetallada> citas, {required bool esProximas}) {
    if (citas.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.calendar_today_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              esProximas ? 'No tienes citas próximas' : 'No hay citas pasadas',
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
      itemCount: citas.length,
      itemBuilder: (context, index) {
        final cita = citas[index];
        return CitaCard(
          cita: cita,
          onTap: () => _mostrarDetalleCita(cita),
          onCancelar: cita.puedeModificar && esProximas
              ? () => _cancelarCita(cita)
              : null,
        );
      },
    );
  }

  void _mostrarDetalleCita(CitaDetallada cita) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => _DetalleCitaSheet(
          cita: cita,
          scrollController: scrollController,
          onCancelar: cita.puedeModificar ? () => _cancelarCita(cita) : null,
        ),
      ),
    );
  }
}

// Widget de detalle de cita
class _DetalleCitaSheet extends StatelessWidget {
  final CitaDetallada cita;
  final ScrollController scrollController;
  final VoidCallback? onCancelar;

  const _DetalleCitaSheet({
    required this.cita,
    required this.scrollController,
    this.onCancelar,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      controller: scrollController,
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
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
            'Detalle de la Cita',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),

          // Información
          _buildInfoRow(Icons.medical_services, 'Motivo', cita.motivo),
          _buildInfoRow(Icons.person, 'Odontólogo', 'Dr. ${cita.odontologo.nombre}'),
          if (cita.odontologo.especialidad != null)
            _buildInfoRow(Icons.verified, 'Especialidad', cita.odontologo.especialidad!),
          _buildInfoRow(
            Icons.calendar_today,
            'Fecha',
            '${cita.fechaHora.day}/${cita.fechaHora.month}/${cita.fechaHora.year}',
          ),
          _buildInfoRow(
            Icons.access_time,
            'Hora',
            '${cita.fechaHora.hour.toString().padLeft(2, '0')}:${cita.fechaHora.minute.toString().padLeft(2, '0')}',
          ),
          _buildInfoRow(Icons.timer, 'Duración', '${cita.duracionMinutos} minutos'),
          _buildInfoRow(Icons.flag, 'Estado', cita.estado),

          if (cita.notas != null) ...[
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            Text(
              'Notas',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(cita.notas!),
          ],

          // Botones
          if (onCancelar != null) ...[
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  onCancelar!();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                ),
                child: const Text('Cancelar Cita'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## 🎨 Widget CitaCard

### `lib/widgets/citas/cita_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/models/cita.dart';

class CitaCard extends StatelessWidget {
  final CitaDetallada cita;
  final VoidCallback onTap;
  final VoidCallback? onCancelar;

  const CitaCard({
    super.key,
    required this.cita,
    required this.onTap,
    this.onCancelar,
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
          child: Row(
            children: [
              // Fecha
              Container(
                width: 60,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _getEstadoColor(cita.estado).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Text(
                      DateFormat('dd').format(cita.fechaHora),
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: _getEstadoColor(cita.estado),
                      ),
                    ),
                    Text(
                      DateFormat('MMM').format(cita.fechaHora).toUpperCase(),
                      style: TextStyle(
                        fontSize: 12,
                        color: _getEstadoColor(cita.estado),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),

              // Información
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      cita.motivo,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Dr. ${cita.odontologo.nombre}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Icon(Icons.access_time, size: 14, color: Colors.grey.shade600),
                        const SizedBox(width: 4),
                        Text(
                          DateFormat('HH:mm').format(cita.fechaHora),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(width: 12),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: _getEstadoColor(cita.estado).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            _getEstadoTexto(cita.estado),
                            style: TextStyle(
                              fontSize: 11,
                              color: _getEstadoColor(cita.estado),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: Colors.grey.shade400,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getEstadoColor(String estado) {
    switch (estado) {
      case 'CONFIRMADA':
        return Colors.green;
      case 'PENDIENTE':
        return Colors.orange;
      case 'COMPLETADA':
        return Colors.blue;
      case 'CANCELADA':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getEstadoTexto(String estado) {
    switch (estado) {
      case 'CONFIRMADA':
        return 'Confirmada';
      case 'PENDIENTE':
        return 'Pendiente';
      case 'COMPLETADA':
        return 'Completada';
      case 'CANCELADA':
        return 'Cancelada';
      default:
        return estado;
    }
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelo `CitaDetallada` y `Odontologo`
- [ ] Crear `CitasService`
- [ ] Crear `MisCitasScreen`
- [ ] Implementar tabs (Próximas/Historial)
- [ ] Crear widget `CitaCard`
- [ ] Detalle de cita en bottom sheet
- [ ] Funcionalidad de cancelar cita
- [ ] Pull to refresh
- [ ] Estados vacíos

---

**Siguiente:** [07_agendar_cita.md](07_agendar_cita.md)
