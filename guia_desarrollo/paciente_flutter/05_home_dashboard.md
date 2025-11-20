# 🏠 Home Dashboard

## 🎯 Objetivo
Crear el dashboard principal con navegación por tabs y resumen de información del paciente.

---

## 📱 Estructura del Home

El Home tendrá navegación por tabs en la parte inferior:
- **Tab 1**: Dashboard (resumen)
- **Tab 2**: Mis Citas
- **Tab 3**: Tratamientos
- **Tab 4**: Perfil

---

## 📡 Servicio del Dashboard

### `lib/services/dashboard_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';

class DashboardData {
  final int proximasCitas;
  final int tratamientosActivos;
  final double saldoPendiente;
  final Cita? proximaCita;

  DashboardData({
    required this.proximasCitas;
    required this.tratamientosActivos,
    required this.saldoPendiente,
    this.proximaCita,
  });

  factory DashboardData.fromJson(Map<String, dynamic> json) {
    return DashboardData(
      proximasCitas: json['proximas_citas'] ?? 0,
      tratamientosActivos: json['tratamientos_activos'] ?? 0,
      saldoPendiente: double.parse(json['saldo_pendiente']?.toString() ?? '0'),
      proximaCita: json['proxima_cita'] != null 
          ? Cita.fromJson(json['proxima_cita'])
          : null,
    );
  }
}

class Cita {
  final int id;
  final String fechaHora;
  final String motivo;
  final String odontologoNombre;
  final String estado;

  Cita({
    required this.id,
    required this.fechaHora,
    required this.motivo,
    required this.odontologoNombre,
    required this.estado,
  });

  factory Cita.fromJson(Map<String, dynamic> json) {
    return Cita(
      id: json['id'],
      fechaHora: json['fecha_hora'],
      motivo: json['motivo'] ?? '',
      odontologoNombre: json['odontologo']['usuario']['full_name'] ?? '',
      estado: json['estado'] ?? '',
    );
  }
}

class DashboardService {
  final String baseUrl = AppConstants.baseUrlDev;

  Future<DashboardData> getDashboard(String token, String tenantId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/pacientes/dashboard/'),
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return DashboardData.fromJson(data);
      } else {
        throw Exception('Error al cargar dashboard');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}
```

---

## 📱 Pantalla Principal con Tabs

### `lib/screens/home_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/screens/dashboard_tab.dart';
import 'package:clinica_dental_app/screens/citas/mis_citas_screen.dart';
import 'package:clinica_dental_app/screens/tratamientos/tratamientos_screen.dart';
import 'package:clinica_dental_app/screens/perfil/perfil_screen.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    DashboardTab(),
    MisCitasScreen(),
    TratamientosScreen(),
    PerfilScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: Theme.of(context).primaryColor,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today_outlined),
            activeIcon: Icon(Icons.calendar_today),
            label: 'Citas',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.medical_services_outlined),
            activeIcon: Icon(Icons.medical_services),
            label: 'Tratamientos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
      floatingActionButton: _selectedIndex == 1
          ? FloatingActionButton.extended(
              onPressed: () {
                // Navegar a agendar cita
                context.push('/agendar-cita');
              },
              icon: const Icon(Icons.add),
              label: const Text('Agendar'),
            )
          : null,
    );
  }
}
```

---

## 📊 Tab de Dashboard

### `lib/screens/dashboard_tab.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/services/dashboard_service.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';

class DashboardTab extends StatefulWidget {
  const DashboardTab({super.key});

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  final DashboardService _dashboardService = DashboardService();
  DashboardData? _dashboardData;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarDashboard();
  }

  Future<void> _cargarDashboard() async {
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

      final data = await _dashboardService.getDashboard(
        authProvider.accessToken!,
        clinicaProvider.clinicaSeleccionada!.id,
      );

      setState(() {
        _dashboardData = data;
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
    final authProvider = Provider.of<AuthProvider>(context);
    final clinicaProvider = Provider.of<ClinicaProvider>(context);

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _cargarDashboard,
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverAppBar(
                floating: true,
                backgroundColor: Colors.transparent,
                elevation: 0,
                title: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '¡Hola, ${authProvider.usuario?.fullName.split(' ').first ?? ''}!',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    if (clinicaProvider.clinicaSeleccionada != null)
                      Text(
                        clinicaProvider.clinicaSeleccionada!.nombre,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                  ],
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.notifications_outlined),
                    onPressed: () {
                      // Ver notificaciones
                    },
                  ),
                ],
              ),

              // Contenido
              if (_isLoading)
                const SliverFillRemaining(
                  child: Center(child: LoadingIndicator()),
                )
              else if (_error != null)
                SliverFillRemaining(
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text('Error al cargar datos'),
                        const SizedBox(height: 8),
                        ElevatedButton(
                          onPressed: _cargarDashboard,
                          child: const Text('Reintentar'),
                        ),
                      ],
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding: const EdgeInsets.all(16),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      // KPIs
                      _buildKPICards(),
                      const SizedBox(height: 24),

                      // Próxima cita
                      if (_dashboardData?.proximaCita != null) ...[
                        _buildProximaCita(),
                        const SizedBox(height: 24),
                      ],

                      // Accesos rápidos
                      _buildAccesosRapidos(),
                      const SizedBox(height: 24),

                      // Recordatorios
                      _buildRecordatorios(),
                    ]),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildKPICards() {
    return Row(
      children: [
        Expanded(
          child: _KPICard(
            icon: Icons.calendar_today,
            title: 'Próximas Citas',
            value: _dashboardData?.proximasCitas.toString() ?? '0',
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _KPICard(
            icon: Icons.medical_services,
            title: 'Tratamientos',
            value: _dashboardData?.tratamientosActivos.toString() ?? '0',
            color: Colors.purple,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _KPICard(
            icon: Icons.attach_money,
            title: 'Saldo',
            value: '\$${_dashboardData?.saldoPendiente.toStringAsFixed(0) ?? '0'}',
            color: Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildProximaCita() {
    final cita = _dashboardData!.proximaCita!;
    final fecha = DateTime.parse(cita.fechaHora);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.event, color: Theme.of(context).primaryColor),
                const SizedBox(width: 8),
                Text(
                  'Próxima Cita',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontSize: 18),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      Text(
                        DateFormat('dd').format(fecha),
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        DateFormat('MMM').format(fecha).toUpperCase(),
                        style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(context).primaryColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
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
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Dr. ${cita.odontologoNombre}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      Text(
                        DateFormat('HH:mm').format(fecha),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 16,
                  color: Theme.of(context).primaryColor,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccesosRapidos() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Accesos Rápidos',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontSize: 18),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _AccesoRapidoCard(
                icon: Icons.calendar_today,
                title: 'Agendar Cita',
                onTap: () {},
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _AccesoRapidoCard(
                icon: Icons.receipt_long,
                title: 'Ver Facturas',
                onTap: () {},
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _AccesoRapidoCard(
                icon: Icons.history,
                title: 'Historial Clínico',
                onTap: () {},
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _AccesoRapidoCard(
                icon: Icons.help_outline,
                title: 'Ayuda',
                onTap: () {},
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRecordatorios() {
    return Card(
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Icon(Icons.info_outline, color: Colors.blue.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Recordatorio',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.blue.shade900,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'No olvides confirmar tu cita 24 horas antes',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.blue.shade800,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Widget de KPI Card
class _KPICard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const _KPICard({
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

// Widget de Acceso Rápido
class _AccesoRapidoCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _AccesoRapidoCard({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(icon, color: Theme.of(context).primaryColor, size: 32),
              const SizedBox(height: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
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

## ✅ Checklist

- [ ] Crear `DashboardService`
- [ ] Crear modelo `DashboardData` y `Cita`
- [ ] Crear `HomeScreen` con navegación por tabs
- [ ] Crear `DashboardTab`
- [ ] Implementar KPI cards
- [ ] Mostrar próxima cita
- [ ] Accesos rápidos
- [ ] Pull to refresh
- [ ] Manejo de errores

---

**Siguiente:** [06_mis_citas.md](06_mis_citas.md)
