# 🏥 Selector de Clínica

## 🎯 Objetivo
Crear la pantalla inicial donde el usuario selecciona la clínica dental a la que pertenece.

---

## 📋 Requisitos

- Mostrar lista de clínicas disponibles
- Diseño atractivo con cards
- Guardar clínica seleccionada
- Navegar a login/registro después de seleccionar

---

## 📡 Modelo de Clínica

### `lib/models/clinica.dart`

```dart
class Clinica {
  final String id;
  final String nombre;
  final String? logo;
  final String? direccion;
  final String? telefono;
  final String? descripcion;

  Clinica({
    required this.id,
    required this.nombre,
    this.logo,
    this.direccion,
    this.telefono,
    this.descripcion,
  });

  factory Clinica.fromJson(Map<String, dynamic> json) {
    return Clinica(
      id: json['schema_name'] ?? json['id'].toString(),
      nombre: json['nombre'] ?? '',
      logo: json['logo'],
      direccion: json['direccion'],
      telefono: json['telefono'],
      descripcion: json['descripcion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'logo': logo,
      'direccion': direccion,
      'telefono': telefono,
      'descripcion': descripcion,
    };
  }
}
```

---

## 🔌 Servicio de Clínicas

### `lib/services/clinica_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';
import 'package:clinica_dental_app/models/clinica.dart';

class ClinicaService {
  // ✅ IMPORTANTE: Usar URL de producción (Render), NO localhost
  final String baseUrl = 'https://clinica-dental-backend.onrender.com';

  // Obtener lista de clínicas disponibles
  Future<List<Clinica>> getClinicas() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/tenants/clinicas/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Clinica.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar clínicas');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Lista de clínicas de ejemplo (si no hay endpoint)
  Future<List<Clinica>> getClinicasDemo() async {
    // Simular delay de red
    await Future.delayed(const Duration(seconds: 1));

    return [
      Clinica(
        id: 'clinica_demo',
        nombre: 'Clínica Dental Dr. Pérez',
        logo: 'https://via.placeholder.com/150',
        direccion: 'Av. Principal #123, La Paz',
        telefono: '+591 1234567',
        descripcion: 'Clínica dental especializada en ortodoncia',
      ),
      Clinica(
        id: 'clinica_sonrisa',
        nombre: 'Sonrisa Perfecta',
        logo: 'https://via.placeholder.com/150',
        direccion: 'Calle Central #456, Santa Cruz',
        telefono: '+591 7654321',
        descripcion: 'Tu salud dental es nuestra prioridad',
      ),
      Clinica(
        id: 'clinica_dental_plus',
        nombre: 'Dental Plus',
        logo: 'https://via.placeholder.com/150',
        direccion: 'Zona Sur #789, Cochabamba',
        telefono: '+591 5551234',
        descripcion: 'Tecnología de punta en odontología',
      ),
    ];
  }
}
```

---

## 🗄️ Provider de Clínica

### `lib/providers/clinica_provider.dart`

```dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clinica_dental_app/models/clinica.dart';
import 'package:clinica_dental_app/config/constants.dart';

class ClinicaProvider with ChangeNotifier {
  Clinica? _clinicaSeleccionada;
  
  Clinica? get clinicaSeleccionada => _clinicaSeleccionada;
  
  bool get tieneClinicaSeleccionada => _clinicaSeleccionada != null;

  // Seleccionar clínica
  Future<void> seleccionarClinica(Clinica clinica) async {
    _clinicaSeleccionada = clinica;
    
    // Guardar en SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyTenantId, clinica.id);
    await prefs.setString(AppConstants.keyTenantName, clinica.nombre);
    
    notifyListeners();
  }

  // Cargar clínica guardada
  Future<void> cargarClinicaGuardada() async {
    final prefs = await SharedPreferences.getInstance();
    final tenantId = prefs.getString(AppConstants.keyTenantId);
    final tenantName = prefs.getString(AppConstants.keyTenantName);
    
    if (tenantId != null && tenantName != null) {
      _clinicaSeleccionada = Clinica(
        id: tenantId,
        nombre: tenantName,
      );
      notifyListeners();
    }
  }

  // Limpiar clínica seleccionada
  Future<void> limpiarClinica() async {
    _clinicaSeleccionada = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.keyTenantId);
    await prefs.remove(AppConstants.keyTenantName);
    
    notifyListeners();
  }
}
```

---

## 📱 Pantalla de Selector de Clínica

### `lib/screens/selector_clinica_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:clinica_dental_app/models/clinica.dart';
import 'package:clinica_dental_app/services/clinica_service.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';

class SelectorClinicaScreen extends StatefulWidget {
  const SelectorClinicaScreen({super.key});

  @override
  State<SelectorClinicaScreen> createState() => _SelectorClinicaScreenState();
}

class _SelectorClinicaScreenState extends State<SelectorClinicaScreen> {
  final ClinicaService _clinicaService = ClinicaService();
  List<Clinica> _clinicas = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarClinicas();
  }

  Future<void> _cargarClinicas() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Usar getClinicasDemo() si no tienes endpoint real
      final clinicas = await _clinicaService.getClinicasDemo();

      setState(() {
        _clinicas = clinicas;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _seleccionarClinica(Clinica clinica) async {
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);
    await clinicaProvider.seleccionarClinica(clinica);
    
    if (mounted) {
      context.go('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  // Logo o ícono
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Icon(
                      Icons.local_hospital_rounded,
                      size: 48,
                      color: Theme.of(context).primaryColor,
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Título
                  Text(
                    '¡Bienvenido!',
                    style: Theme.of(context).textTheme.headlineLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  
                  // Subtítulo
                  Text(
                    'Selecciona tu clínica dental',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).textTheme.bodyMedium?.color,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            // Lista de clínicas
            Expanded(
              child: _buildBody(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: LoadingIndicator());
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                'Error al cargar clínicas',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _cargarClinicas,
                icon: const Icon(Icons.refresh),
                label: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
    }

    if (_clinicas.isEmpty) {
      return Center(
        child: Text(
          'No hay clínicas disponibles',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      itemCount: _clinicas.length,
      itemBuilder: (context, index) {
        final clinica = _clinicas[index];
        return _ClinicaCard(
          clinica: clinica,
          onTap: () => _seleccionarClinica(clinica),
        );
      },
    );
  }
}

// Widget de Card de Clínica
class _ClinicaCard extends StatelessWidget {
  final Clinica clinica;
  final VoidCallback onTap;

  const _ClinicaCard({
    required this.clinica,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              // Logo
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  image: clinica.logo != null
                      ? DecorationImage(
                          image: NetworkImage(clinica.logo!),
                          fit: BoxFit.cover,
                        )
                      : null,
                ),
                child: clinica.logo == null
                    ? Icon(
                        Icons.local_hospital,
                        color: Theme.of(context).primaryColor,
                        size: 32,
                      )
                    : null,
              ),
              const SizedBox(width: 16),
              
              // Información
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Nombre
                    Text(
                      clinica.nombre,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontSize: 16,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    
                    if (clinica.direccion != null) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on_outlined,
                            size: 14,
                            color: Theme.of(context).textTheme.bodyMedium?.color,
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              clinica.direccion!,
                              style: Theme.of(context).textTheme.bodyMedium,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                    
                    if (clinica.telefono != null) ...[
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Icon(
                            Icons.phone_outlined,
                            size: 14,
                            color: Theme.of(context).textTheme.bodyMedium?.color,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            clinica.telefono!,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              
              // Icono de flecha
              Icon(
                Icons.arrow_forward_ios,
                size: 20,
                color: Theme.of(context).primaryColor,
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

## 🎨 Widget de Loading Indicator

### `lib/widgets/common/loading_indicator.dart`

```dart
import 'package:flutter/material.dart';

class LoadingIndicator extends StatelessWidget {
  final double size;
  final Color? color;

  const LoadingIndicator({
    super.key,
    this.size = 40,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(
        strokeWidth: 3,
        valueColor: AlwaysStoppedAnimation<Color>(
          color ?? Theme.of(context).primaryColor,
        ),
      ),
    );
  }
}
```

---

## 🔄 Splash Screen

### `lib/screens/splash_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    // Cargar clínica guardada
    final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);
    await clinicaProvider.cargarClinicaGuardada();

    // Cargar sesión guardada
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.cargarSesion();

    // Esperar 2 segundos
    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;

    // Navegar según el estado
    if (authProvider.isAuthenticated && clinicaProvider.tieneClinicaSeleccionada) {
      context.go('/home');
    } else if (clinicaProvider.tieneClinicaSeleccionada) {
      context.go('/login');
    } else {
      context.go('/selector-clinica');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).primaryColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo o ícono
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(30),
              ),
              child: Icon(
                Icons.local_hospital_rounded,
                size: 80,
                color: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(height: 32),
            
            // Título
            const Text(
              'Clínica Dental',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            
            const Text(
              'Tu salud dental es nuestra prioridad',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 48),
            
            // Loading
            const SizedBox(
              width: 40,
              height: 40,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## ✅ Checklist

- [ ] Crear modelo `Clinica`
- [ ] Crear servicio `ClinicaService`
- [ ] Crear provider `ClinicaProvider`
- [ ] Crear `SelectorClinicaScreen`
- [ ] Crear `SplashScreen`
- [ ] Crear widget `LoadingIndicator`
- [ ] Probar selección de clínica
- [ ] Verificar guardado en SharedPreferences

---

**Siguiente:** [04_login_registro.md](04_login_registro.md) - Login y Registro
