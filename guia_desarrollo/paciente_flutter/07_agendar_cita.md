# 📅 Agendar Cita

## 🎯 Objetivo
Permitir al paciente agendar nuevas citas seleccionando fecha, hora, odontólogo y motivo.

---

## 📡 Modelos Adicionales

### `lib/models/horario.dart`

```dart
class HorarioDisponible {
  final String hora;
  final bool disponible;
  final int? citaId;

  HorarioDisponible({
    required this.hora,
    required this.disponible,
    this.citaId,
  });

  factory HorarioDisponible.fromJson(Map<String, dynamic> json) {
    return HorarioDisponible(
      hora: json['hora'],
      disponible: json['disponible'] ?? false,
      citaId: json['cita_id'],
    );
  }
}

class OdontologoDisponible {
  final int id;
  final String nombre;
  final String? especialidad;
  final String? foto;
  final List<String> diasDisponibles;

  OdontologoDisponible({
    required this.id,
    required this.nombre,
    this.especialidad,
    this.foto,
    required this.diasDisponibles,
  });

  factory OdontologoDisponible.fromJson(Map<String, dynamic> json) {
    return OdontologoDisponible(
      id: json['id'],
      nombre: json['nombre_completo'] ?? '${json['nombre']} ${json['apellido']}',  // ✅ FIX: nombre_completo directo
      especialidad: json['especialidad'],
      foto: null,  // ✅ Endpoint /api/usuarios/odontologos/ no retorna foto
      diasDisponibles: [],  // ✅ Endpoint no retorna dias_disponibles
    );
  }
}
```

---

## 🔌 Servicio de Agendamiento

### `lib/services/agendamiento_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/horario.dart';

class AgendamientoService {
  final String baseUrl = AppConstants.baseUrlDev;

  // Obtener odontólogos disponibles
  Future<List<OdontologoDisponible>> getOdontologosDisponibles({
    required String token,
    required String tenantId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/agenda/odontologos-disponibles/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => OdontologoDisponible.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar odontólogos');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener horarios disponibles
  Future<List<HorarioDisponible>> getHorariosDisponibles({
    required String token,
    required String tenantId,
    required int odontologoId,
    required DateTime fecha,
  }) async {
    try {
      final fechaStr = '${fecha.year}-${fecha.month.toString().padLeft(2, '0')}-${fecha.day.toString().padLeft(2, '0')}';
      
      final response = await http.get(
        Uri.parse('$baseUrl/api/agenda/horarios-disponibles/?odontologo_id=$odontologoId&fecha=$fechaStr'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => HorarioDisponible.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar horarios');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Agendar cita
  Future<void> agendarCita({
    required String token,
    required String tenantId,
    required int pacienteId,      // ✅ REQUERIDO: ID del paciente autenticado
    required int odontologoId,
    required DateTime fechaHora,
    required String motivoTipo,  // ✅ VALORES VÁLIDOS: 'CONSULTA', 'URGENCIA', 'LIMPIEZA', 'REVISION', 'PLAN'
    required String motivo,
    String? observaciones,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/agenda/citas/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'paciente': pacienteId,       // ✅ Campo requerido por el backend
          'odontologo': odontologoId,
          'fecha_hora': fechaHora.toIso8601String(),
          'motivo_tipo': motivoTipo,    // Solo acepta: CONSULTA, URGENCIA, LIMPIEZA, REVISION, PLAN
          'motivo': motivo,
          'observaciones': observaciones ?? '',
        }),
      );

      if (response.statusCode != 201) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Error al agendar cita');
      }
    } catch (e) {
      throw Exception('Error al agendar: $e');
    }
  }
}
```

---

## 📱 Pantalla de Agendar Cita

### `lib/screens/citas/agendar_cita_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:clinica_dental_app/models/horario.dart';
import 'package:clinica_dental_app/services/agendamiento_service.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';
import 'package:go_router/go_router.dart';

class AgendarCitaScreen extends StatefulWidget {
  const AgendarCitaScreen({super.key});

  @override
  State<AgendarCitaScreen> createState() => _AgendarCitaScreenState();
}

class _AgendarCitaScreenState extends State<AgendarCitaScreen> {
  final AgendamientoService _service = AgendamientoService();
  final _formKey = GlobalKey<FormState>();
  final _motivoController = TextEditingController();

  int _step = 0;
  List<OdontologoDisponible> _odontologos = [];
  OdontologoDisponible? _odontologoSeleccionado;
  DateTime _fechaSeleccionada = DateTime.now();
  DateTime _focusedDay = DateTime.now();
  List<HorarioDisponible> _horarios = [];
  HorarioDisponible? _horarioSeleccionado;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _cargarOdontologos();
  }

  @override
  void dispose() {
    _motivoController.dispose();
    super.dispose();
  }

  Future<void> _cargarOdontologos() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    setState(() => _isLoading = true);

    try {
      final odontologos = await _service.getOdontologosDisponibles(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
      );

      setState(() {
        _odontologos = odontologos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _cargarHorarios() async {
    if (_odontologoSeleccionado == null) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    setState(() => _isLoading = true);

    try {
      final horarios = await _service.getHorariosDisponibles(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
        odontologoId: _odontologoSeleccionado!.id,
        fecha: _fechaSeleccionada,
      );

      setState(() {
        _horarios = horarios;
        _horarioSeleccionado = null;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _confirmarCita() async {
    if (!_formKey.currentState!.validate()) return;
    if (_odontologoSeleccionado == null || _horarioSeleccionado == null) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);

    setState(() => _isLoading = true);

    try {
      // Construir fecha y hora
      final horaPartes = _horarioSeleccionado!.hora.split(':');
      final fechaHora = DateTime(
        _fechaSeleccionada.year,
        _fechaSeleccionada.month,
        _fechaSeleccionada.day,
        int.parse(horaPartes[0]),
        int.parse(horaPartes[1]),
      );

      // ✅ Obtener pacienteId del usuario autenticado
      final perfilUsuario = authProvider.usuario;
      final pacienteId = perfilUsuario?.id;
      
      if (pacienteId == null) {
        throw Exception('No se pudo obtener el ID del paciente');
      }

      await _service.agendarCita(
        token: authProvider.accessToken!,
        tenantId: clinicaProvider.clinicaSeleccionada!.id,
        pacienteId: pacienteId,
        odontologoId: _odontologoSeleccionado!.id,
        fechaHora: fechaHora,
        motivoTipo: 'CONSULTA',  // ✅ Valores válidos: CONSULTA, URGENCIA, LIMPIEZA, REVISION, PLAN
        motivo: _motivoController.text,
        observaciones: '',
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cita agendada exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
        context.pop();
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agendar Cita'),
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : Stepper(
              currentStep: _step,
              onStepContinue: () {
                if (_step == 0 && _odontologoSeleccionado == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Selecciona un odontólogo')),
                  );
                  return;
                }
                if (_step == 1 && _horarioSeleccionado == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Selecciona un horario')),
                  );
                  return;
                }
                if (_step < 2) {
                  setState(() => _step++);
                  if (_step == 1) _cargarHorarios();
                } else {
                  _confirmarCita();
                }
              },
              onStepCancel: () {
                if (_step > 0) {
                  setState(() => _step--);
                }
              },
              steps: [
                Step(
                  title: const Text('Seleccionar Odontólogo'),
                  content: _buildOdontologosStep(),
                  isActive: _step >= 0,
                  state: _step > 0 ? StepState.complete : StepState.indexed,
                ),
                Step(
                  title: const Text('Seleccionar Fecha y Hora'),
                  content: _buildFechaHoraStep(),
                  isActive: _step >= 1,
                  state: _step > 1 ? StepState.complete : StepState.indexed,
                ),
                Step(
                  title: const Text('Confirmar Detalles'),
                  content: _buildConfirmacionStep(),
                  isActive: _step >= 2,
                ),
              ],
            ),
    );
  }

  Widget _buildOdontologosStep() {
    if (_odontologos.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No hay odontólogos disponibles'),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _odontologos.length,
      itemBuilder: (context, index) {
        final odontologo = _odontologos[index];
        final isSelected = _odontologoSeleccionado?.id == odontologo.id;

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          color: isSelected
              ? Theme.of(context).primaryColor.withOpacity(0.1)
              : null,
          child: ListTile(
            leading: CircleAvatar(
              backgroundImage: odontologo.foto != null
                  ? NetworkImage(odontologo.foto!)
                  : null,
              child: odontologo.foto == null
                  ? const Icon(Icons.person)
                  : null,
            ),
            title: Text('Dr. ${odontologo.nombre}'),
            subtitle: odontologo.especialidad != null
                ? Text(odontologo.especialidad!)
                : null,
            trailing: isSelected
                ? Icon(Icons.check_circle, color: Theme.of(context).primaryColor)
                : null,
            onTap: () {
              setState(() {
                _odontologoSeleccionado = odontologo;
                _horarioSeleccionado = null;
              });
            },
          ),
        );
      },
    );
  }

  Widget _buildFechaHoraStep() {
    return Column(
      children: [
        // Calendario
        Card(
          child: TableCalendar(
            firstDay: DateTime.now(),
            lastDay: DateTime.now().add(const Duration(days: 90)),
            focusedDay: _focusedDay,
            selectedDayPredicate: (day) => isSameDay(_fechaSeleccionada, day),
            onDaySelected: (selectedDay, focusedDay) {
              setState(() {
                _fechaSeleccionada = selectedDay;
                _focusedDay = focusedDay;
              });
              _cargarHorarios();
            },
            calendarFormat: CalendarFormat.month,
            availableCalendarFormats: const {
              CalendarFormat.month: 'Mes',
            },
            headerStyle: const HeaderStyle(
              formatButtonVisible: false,
              titleCentered: true,
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Horarios
        if (_horarios.isEmpty)
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text('No hay horarios disponibles para esta fecha'),
          )
        else
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _horarios.map((horario) {
              final isSelected = _horarioSeleccionado?.hora == horario.hora;
              final isDisponible = horario.disponible;

              return ChoiceChip(
                label: Text(horario.hora),
                selected: isSelected,
                onSelected: isDisponible
                    ? (selected) {
                        setState(() {
                          _horarioSeleccionado = selected ? horario : null;
                        });
                      }
                    : null,
                selectedColor: Theme.of(context).primaryColor,
                labelStyle: TextStyle(
                  color: isSelected ? Colors.white : null,
                ),
                disabledColor: Colors.grey.shade200,
              );
            }).toList(),
          ),
      ],
    );
  }

  Widget _buildConfirmacionStep() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Resumen
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Resumen de la Cita',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  _buildResumenRow(
                    Icons.person,
                    'Odontólogo',
                    'Dr. ${_odontologoSeleccionado?.nombre ?? ''}',
                  ),
                  _buildResumenRow(
                    Icons.calendar_today,
                    'Fecha',
                    '${_fechaSeleccionada.day}/${_fechaSeleccionada.month}/${_fechaSeleccionada.year}',
                  ),
                  _buildResumenRow(
                    Icons.access_time,
                    'Hora',
                    _horarioSeleccionado?.hora ?? '',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Motivo
          TextFormField(
            controller: _motivoController,
            decoration: const InputDecoration(
              labelText: 'Motivo de la cita',
              hintText: 'Ej: Revisión general, dolor de muela, etc.',
              border: OutlineInputBorder(),
            ),
            maxLines: 3,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Por favor ingresa el motivo';
              }
              return null;
            },
          ),
        ],
      ),
    );
  }

  Widget _buildResumenRow(IconData icon, String label, String value) {
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
}
```

---

## ✅ Checklist

- [ ] Crear modelos `HorarioDisponible` y `OdontologoDisponible`
- [ ] Crear `AgendamientoService`
- [ ] Crear `AgendarCitaScreen` con Stepper
- [ ] Step 1: Selección de odontólogo
- [ ] Step 2: Calendario y horarios (table_calendar)
- [ ] Step 3: Motivo y confirmación
- [ ] Validación de formulario
- [ ] Integrar con backend

---

**Siguiente:** [08_historial_clinico.md](08_historial_clinico.md)
