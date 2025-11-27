# 📊 Dashboard Screen - Pantalla Principal de Reportes

## 📱 Vista General

Dashboard con estadísticas en tiempo real para administradores, incluyendo:
- KPIs principales
- Gráfico de tendencia de citas
- Top procedimientos
- Ocupación de odontólogos
- Exportación de reportes

---

## 🎯 Archivo: `lib/screens/admin/dashboard_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/reportes_service.dart';
import '../../widgets/kpi_card.dart';
import '../../widgets/tendencia_chart.dart';
import '../../widgets/top_procedimientos_chart.dart';
import '../../widgets/ocupacion_table.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ReportesService _reportesService = ReportesService();
  
  bool _isLoading = true;
  String? _error;
  
  // Datos del dashboard
  Map<String, dynamic> _kpis = {};
  List<Map<String, dynamic>> _tendenciaCitas = [];
  List<Map<String, dynamic>> _topProcedimientos = [];
  List<Map<String, dynamic>> _ocupacionOdontologos = [];
  Map<String, dynamic> _estadisticasGenerales = {};

  @override
  void initState() {
    super.initState();
    _cargarDatosDashboard();
  }

  Future<void> _cargarDatosDashboard() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Cargar todos los datos en paralelo
      final results = await Future.wait([
        _reportesService.obtenerDashboardKPIs(),
        _reportesService.obtenerTendenciaCitas(dias: 15),
        _reportesService.obtenerTopProcedimientos(limite: 5),
        _reportesService.obtenerOcupacionOdontologos(),
        _reportesService.obtenerEstadisticasGenerales(),
      ]);

      setState(() {
        _kpis = results[0] as Map<String, dynamic>;
        _tendenciaCitas = results[1] as List<Map<String, dynamic>>;
        _topProcedimientos = results[2] as List<Map<String, dynamic>>;
        _ocupacionOdontologos = results[3] as List<Map<String, dynamic>>;
        _estadisticasGenerales = results[4] as Map<String, dynamic>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _exportarReporte(String tipo, String formato) async {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Descargando $formato...')),
      );

      bool exito = await _reportesService.exportarReporte(
        tipoReporte: tipo,
        formato: formato,
      );

      if (exito && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Reporte $formato descargado exitosamente'),
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

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final usuario = authProvider.usuario;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard Estadísticas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarDatosDashboard,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await authProvider.logout();
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/login');
              }
            },
          ),
        ],
      ),
      body: _isLoading
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
                        onPressed: _cargarDatosDashboard,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _cargarDatosDashboard,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Saludo al usuario
                        Text(
                          '¡Hola, ${usuario?.nombre ?? "Admin"}!',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Resumen de estadísticas',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.grey[600],
                              ),
                        ),
                        const SizedBox(height: 24),

                        // KPIs principales
                        _buildKPIsGrid(),
                        const SizedBox(height: 32),

                        // Estadísticas Generales (con exportación)
                        _buildEstadisticasGenerales(),
                        const SizedBox(height: 32),

                        // Gráfico de Tendencia de Citas
                        _buildTendenciaCitas(),
                        const SizedBox(height: 32),

                        // Top Procedimientos
                        _buildTopProcedimientos(),
                        const SizedBox(height: 32),

                        // Ocupación de Odontólogos
                        _buildOcupacionOdontologos(),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildKPIsGrid() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        KpiCard(
          titulo: 'Pacientes Activos',
          valor: _kpis['total_pacientes']?.toString() ?? '0',
          icono: Icons.people,
          color: Colors.blue,
        ),
        KpiCard(
          titulo: 'Citas Hoy',
          valor: _kpis['citas_hoy']?.toString() ?? '0',
          icono: Icons.calendar_today,
          color: Colors.green,
        ),
        KpiCard(
          titulo: 'Ingresos Mes',
          valor: '\$${_kpis['ingresos_mes']?.toStringAsFixed(2) ?? '0.00'}',
          icono: Icons.attach_money,
          color: Colors.orange,
        ),
        KpiCard(
          titulo: 'Saldo Pendiente',
          valor: '\$${_kpis['facturas_pendientes']?.toString() ?? '0'}',
          icono: Icons.warning,
          color: Colors.red,
        ),
      ],
    );
  }

  Widget _buildEstadisticasGenerales() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '📊 Estadísticas Generales',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.picture_as_pdf, color: Colors.red),
                      onPressed: () => _exportarReporte('estadisticas-generales', 'pdf'),
                      tooltip: 'Descargar PDF',
                    ),
                    IconButton(
                      icon: const Icon(Icons.grid_on, color: Colors.green),
                      onPressed: () => _exportarReporte('estadisticas-generales', 'excel'),
                      tooltip: 'Descargar Excel',
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildStatRow('Pacientes Activos', _estadisticasGenerales['total_pacientes_activos']),
            _buildStatRow('Citas del Mes', _estadisticasGenerales['citas_mes_actual']),
            _buildStatRow('Tasa Ocupación', '${_estadisticasGenerales['tasa_ocupacion']}%'),
            _buildStatRow('Planes Activos', _estadisticasGenerales['planes_activos']),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16)),
          Text(
            value?.toString() ?? '0',
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildTendenciaCitas() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '📈 Tendencia de Citas',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.picture_as_pdf, color: Colors.red),
                      onPressed: () => _exportarReporte('tendencia-citas', 'pdf'),
                      tooltip: 'Descargar PDF',
                    ),
                    IconButton(
                      icon: const Icon(Icons.grid_on, color: Colors.green),
                      onPressed: () => _exportarReporte('tendencia-citas', 'excel'),
                      tooltip: 'Descargar Excel',
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 250,
              child: TendenciaChart(data: _tendenciaCitas),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopProcedimientos() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '🏆 Top Procedimientos',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.picture_as_pdf, color: Colors.red),
                      onPressed: () => _exportarReporte('top-procedimientos', 'pdf'),
                      tooltip: 'Descargar PDF',
                    ),
                    IconButton(
                      icon: const Icon(Icons.grid_on, color: Colors.green),
                      onPressed: () => _exportarReporte('top-procedimientos', 'excel'),
                      tooltip: 'Descargar Excel',
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 300,
              child: TopProcedimientosChart(data: _topProcedimientos),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOcupacionOdontologos() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '👨‍⚕️ Ocupación de Odontólogos',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            OcupacionTable(data: _ocupacionOdontologos),
          ],
        ),
      ),
    );
  }
}
```

---

## 🎨 Características

### 1. Carga de Datos en Paralelo
- `Future.wait()` para cargar todos los endpoints simultáneamente
- Mejora el tiempo de carga inicial

### 2. Pull-to-Refresh
- `RefreshIndicator` para recargar datos con gesto
- Actualización manual con botón de refresh

### 3. Exportación de Reportes
- Botones PDF/Excel en cada sección
- Feedback visual con SnackBar
- Manejo de errores

### 4. Estados de UI
- Loading: CircularProgressIndicator
- Error: Mensaje con botón de reintentar
- Datos: Vista completa del dashboard

---

## 📝 Notas de Implementación

1. **Importar widgets personalizados** (se crearán en guías posteriores):
   - `KpiCard` - Tarjetas de métricas
   - `TendenciaChart` - Gráfico de líneas
   - `TopProcedimientosChart` - Gráfico de barras
   - `OcupacionTable` - Tabla de ocupación

2. **Provider de Autenticación**:
   - Acceso a datos del usuario logueado
   - Función de logout

3. **Servicio de Reportes**:
   - Métodos para consumir endpoints del backend
   - Exportación de archivos

---

## 🎯 Siguiente Paso

Continúa con los widgets de KPI y gráficos:
👉 **[07_KPI_CARDS.md](07_KPI_CARDS.md)**
