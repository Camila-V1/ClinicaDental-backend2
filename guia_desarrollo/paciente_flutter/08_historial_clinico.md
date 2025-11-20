# 📋 Historial Clínico

## 🎯 Objetivo
Permitir al paciente ver su historial clínico completo con documentos médicos.

---

## 📡 Modelos

### `lib/models/historial_clinico.dart`

```dart
class HistorialClinico {
  final int id;
  final List<ConsultaMedica> consultas;
  final List<DocumentoMedico> documentos;
  final InformacionMedica? informacionMedica;

  HistorialClinico({
    required this.id,
    required this.consultas,
    required this.documentos,
    this.informacionMedica,
  });

  factory HistorialClinico.fromJson(Map<String, dynamic> json) {
    return HistorialClinico(
      id: json['id'],
      consultas: (json['consultas'] as List?)
          ?.map((e) => ConsultaMedica.fromJson(e))
          .toList() ?? [],
      documentos: (json['documentos'] as List?)
          ?.map((e) => DocumentoMedico.fromJson(e))
          .toList() ?? [],
      informacionMedica: json['informacion_medica'] != null
          ? InformacionMedica.fromJson(json['informacion_medica'])
          : null,
    );
  }
}

class ConsultaMedica {
  final int id;
  final DateTime fecha;
  final String motivo;
  final String diagnostico;
  final String tratamiento;
  final String odontologoNombre;
  final List<String>? piezasDentales;

  ConsultaMedica({
    required this.id,
    required this.fecha,
    required this.motivo,
    required this.diagnostico,
    required this.tratamiento,
    required this.odontologoNombre,
    this.piezasDentales,
  });

  factory ConsultaMedica.fromJson(Map<String, dynamic> json) {
    return ConsultaMedica(
      id: json['id'],
      fecha: DateTime.parse(json['fecha']),
      motivo: json['motivo'] ?? '',
      diagnostico: json['diagnostico'] ?? '',
      tratamiento: json['tratamiento'] ?? '',
      odontologoNombre: json['odontologo']['usuario']['full_name'] ?? '',
      piezasDentales: json['piezas_dentales'] != null
          ? List<String>.from(json['piezas_dentales'])
          : null,
    );
  }
}

class DocumentoMedico {
  final int id;
  final String titulo;
  final String tipo;
  final String? descripcion;
  final String archivo;
  final DateTime fechaSubida;
  final String? subidoPor;

  DocumentoMedico({
    required this.id,
    required this.titulo,
    required this.tipo,
    this.descripcion,
    required this.archivo,
    required this.fechaSubida,
    this.subidoPor,
  });

  factory DocumentoMedico.fromJson(Map<String, dynamic> json) {
    return DocumentoMedico(
      id: json['id'],
      titulo: json['titulo'] ?? '',
      tipo: json['tipo'] ?? '',
      descripcion: json['descripcion'],
      archivo: json['archivo'] ?? '',
      fechaSubida: DateTime.parse(json['fecha_subida']),
      subidoPor: json['subido_por'],
    );
  }

  String get extension {
    return archivo.split('.').last.toLowerCase();
  }

  bool get esPDF => extension == 'pdf';
  bool get esImagen => ['jpg', 'jpeg', 'png', 'gif'].contains(extension);
}

class InformacionMedica {
  final String? tipoSangre;
  final List<String> alergias;
  final List<String> enfermedades;
  final List<String> medicamentos;
  final String? notasAdicionales;

  InformacionMedica({
    this.tipoSangre,
    required this.alergias,
    required this.enfermedades,
    required this.medicamentos,
    this.notasAdicionales,
  });

  factory InformacionMedica.fromJson(Map<String, dynamic> json) {
    return InformacionMedica(
      tipoSangre: json['tipo_sangre'],
      alergias: List<String>.from(json['alergias'] ?? []),
      enfermedades: List<String>.from(json['enfermedades'] ?? []),
      medicamentos: List<String>.from(json['medicamentos'] ?? []),
      notasAdicionales: json['notas_adicionales'],
    );
  }
}
```

---

## 🔌 Servicio

### `lib/services/historial_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/historial_clinico.dart';

class HistorialService {
  final String baseUrl = AppConstants.baseUrlDev;

  // Obtener historial completo
  Future<HistorialClinico> getHistorial({
    required String token,
    required String tenantId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/historial-clinico/mi-historial/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return HistorialClinico.fromJson(data);
      } else {
        throw Exception('Error al cargar historial');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener consulta específica
  Future<ConsultaMedica> getConsulta({
    required String token,
    required String tenantId,
    required int consultaId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/historial-clinico/consultas/$consultaId/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ConsultaMedica.fromJson(data);
      } else {
        throw Exception('Error al cargar consulta');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Descargar documento
  Future<void> descargarDocumento({
    required String token,
    required String tenantId,
    required int documentoId,
  }) async {
    // Implementar descarga de documento
    // Puede usar url_launcher o file_picker
  }
}
```

---

## 📱 Pantalla Principal

### `lib/screens/historial/historial_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/models/historial_clinico.dart';
import 'package:clinica_dental_app/services/historial_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';
import 'package:clinica_dental_app/widgets/historial/consulta_card.dart';
import 'package:clinica_dental_app/widgets/historial/documento_card.dart';
import 'package:clinica_dental_app/widgets/historial/info_medica_card.dart';

class HistorialScreen extends StatefulWidget {
  const HistorialScreen({super.key});

  @override
  State<HistorialScreen> createState() => _HistorialScreenState();
}

class _HistorialScreenState extends State<HistorialScreen>
    with SingleTickerProviderStateMixin {
  final HistorialService _service = HistorialService();
  late TabController _tabController;

  HistorialClinico? _historial;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _cargarHistorial();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _cargarHistorial() async {
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

      final historial = await _service.getHistorial(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
      );

      setState(() {
        _historial = historial;
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
        title: const Text('Historial Clínico'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Consultas', icon: Icon(Icons.medical_services, size: 20)),
            Tab(text: 'Documentos', icon: Icon(Icons.file_copy, size: 20)),
            Tab(text: 'Info Médica', icon: Icon(Icons.info, size: 20)),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : _error != null
              ? _buildError()
              : RefreshIndicator(
                  onRefresh: _cargarHistorial,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildConsultasTab(),
                      _buildDocumentosTab(),
                      _buildInfoMedicaTab(),
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
          const Text('Error al cargar historial'),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _cargarHistorial,
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildConsultasTab() {
    if (_historial?.consultas.isEmpty ?? true) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.medical_services_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No hay consultas registradas'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _historial!.consultas.length,
      itemBuilder: (context, index) {
        final consulta = _historial!.consultas[index];
        return ConsultaCard(
          consulta: consulta,
          onTap: () => _mostrarDetalleConsulta(consulta),
        );
      },
    );
  }

  Widget _buildDocumentosTab() {
    if (_historial?.documentos.isEmpty ?? true) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.file_copy_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No hay documentos disponibles'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _historial!.documentos.length,
      itemBuilder: (context, index) {
        final documento = _historial!.documentos[index];
        return DocumentoCard(
          documento: documento,
          onTap: () => _abrirDocumento(documento),
        );
      },
    );
  }

  Widget _buildInfoMedicaTab() {
    if (_historial?.informacionMedica == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.info_outline, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No hay información médica registrada'),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: InfoMedicaCard(
        informacion: _historial!.informacionMedica!,
      ),
    );
  }

  void _mostrarDetalleConsulta(ConsultaMedica consulta) {
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
        builder: (context, scrollController) => _DetalleConsultaSheet(
          consulta: consulta,
          scrollController: scrollController,
        ),
      ),
    );
  }

  void _abrirDocumento(DocumentoMedico documento) {
    // Implementar apertura de documento
    // Puede usar url_launcher o un visor PDF integrado
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Abriendo ${documento.titulo}...')),
    );
  }
}

// Widget de detalle de consulta
class _DetalleConsultaSheet extends StatelessWidget {
  final ConsultaMedica consulta;
  final ScrollController scrollController;

  const _DetalleConsultaSheet({
    required this.consulta,
    required this.scrollController,
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
            'Detalle de Consulta',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),

          // Información
          _buildInfoRow(
            Icons.calendar_today,
            'Fecha',
            '${consulta.fecha.day}/${consulta.fecha.month}/${consulta.fecha.year}',
          ),
          _buildInfoRow(Icons.person, 'Odontólogo', 'Dr. ${consulta.odontologoNombre}'),
          
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 16),

          _buildSection('Motivo', consulta.motivo),
          _buildSection('Diagnóstico', consulta.diagnostico),
          _buildSection('Tratamiento', consulta.tratamiento),

          if (consulta.piezasDentales != null && consulta.piezasDentales!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'Piezas Dentales',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: consulta.piezasDentales!
                  .map((pieza) => Chip(label: Text(pieza)))
                  .toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Text(value),
        ],
      ),
    );
  }

  Widget _buildSection(String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(content),
        ],
      ),
    );
  }
}
```

---

## 🎨 Widgets

### `lib/widgets/historial/consulta_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/models/historial_clinico.dart';

class ConsultaCard extends StatelessWidget {
  final ConsultaMedica consulta;
  final VoidCallback onTap;

  const ConsultaCard({
    super.key,
    required this.consulta,
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
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.medical_services,
                  color: Theme.of(context).primaryColor,
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      consulta.motivo,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Dr. ${consulta.odontologoNombre}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      DateFormat('dd/MM/yyyy').format(consulta.fecha),
                      style: Theme.of(context).textTheme.bodySmall,
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
}
```

### `lib/widgets/historial/documento_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/models/historial_clinico.dart';

class DocumentoCard extends StatelessWidget {
  final DocumentoMedico documento;
  final VoidCallback onTap;

  const DocumentoCard({
    super.key,
    required this.documento,
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
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getTipoColor(documento.tipo).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _getTipoIcon(documento.tipo),
                  color: _getTipoColor(documento.tipo),
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      documento.titulo,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      documento.tipo,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      DateFormat('dd/MM/yyyy').format(documento.fechaSubida),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.download,
                color: Theme.of(context).primaryColor,
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getTipoIcon(String tipo) {
    switch (tipo.toLowerCase()) {
      case 'radiografia':
      case 'radiografía':
        return Icons.photo_camera;
      case 'receta':
        return Icons.receipt;
      case 'consentimiento':
        return Icons.description;
      default:
        return Icons.file_copy;
    }
  }

  Color _getTipoColor(String tipo) {
    switch (tipo.toLowerCase()) {
      case 'radiografia':
      case 'radiografía':
        return Colors.purple;
      case 'receta':
        return Colors.green;
      case 'consentimiento':
        return Colors.orange;
      default:
        return Colors.blue;
    }
  }
}
```

### `lib/widgets/historial/info_medica_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:clinica_dental_app/models/historial_clinico.dart';

class InfoMedicaCard extends StatelessWidget {
  final InformacionMedica informacion;

  const InfoMedicaCard({
    super.key,
    required this.informacion,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (informacion.tipoSangre != null)
          _buildInfoCard(
            context,
            'Tipo de Sangre',
            informacion.tipoSangre!,
            Icons.bloodtype,
            Colors.red,
          ),
        
        if (informacion.alergias.isNotEmpty)
          _buildListCard(
            context,
            'Alergias',
            informacion.alergias,
            Icons.warning,
            Colors.orange,
          ),
        
        if (informacion.enfermedades.isNotEmpty)
          _buildListCard(
            context,
            'Enfermedades',
            informacion.enfermedades,
            Icons.local_hospital,
            Colors.purple,
          ),
        
        if (informacion.medicamentos.isNotEmpty)
          _buildListCard(
            context,
            'Medicamentos',
            informacion.medicamentos,
            Icons.medication,
            Colors.blue,
          ),
        
        if (informacion.notasAdicionales != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.note, color: Colors.grey.shade700),
                      const SizedBox(width: 8),
                      Text(
                        'Notas Adicionales',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(informacion.notasAdicionales!),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildInfoCard(
    BuildContext context,
    String titulo,
    String valor,
    IconData icon,
    Color color,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titulo,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                Text(
                  valor,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListCard(
    BuildContext context,
    String titulo,
    List<String> items,
    IconData icon,
    Color color,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color),
                const SizedBox(width: 8),
                Text(
                  titulo,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Text(item)),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelos completos
- [ ] Crear `HistorialService`
- [ ] Crear `HistorialScreen` con 3 tabs
- [ ] Widget `ConsultaCard`
- [ ] Widget `DocumentoCard`
- [ ] Widget `InfoMedicaCard`
- [ ] Detalle de consulta en bottom sheet
- [ ] Implementar descarga de documentos

---

**Siguiente:** [09_tratamientos.md](09_tratamientos.md)
