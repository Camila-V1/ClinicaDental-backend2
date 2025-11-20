# 👤 Perfil y Configuración

## 🎯 Objetivo
Permitir al paciente gestionar su perfil y configuraciones de la aplicación.

---

## 📱 Pantalla de Perfil

### `lib/screens/perfil/perfil_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';
import 'package:clinica_dental_app/screens/perfil/editar_perfil_screen.dart';
import 'package:clinica_dental_app/screens/perfil/cambiar_password_screen.dart';
import 'package:go_router/go_router.dart';

class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final clinicaProvider = Provider.of<ClinicaProvider>(context);
    final usuario = authProvider.usuario;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: CustomScrollView(
        slivers: [
          // App Bar con perfil
          SliverAppBar(
            expandedHeight: 200,
            floating: false,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
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
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: Colors.white,
                        child: Text(
                          usuario?.fullName.substring(0, 1).toUpperCase() ?? 'U',
                          style: TextStyle(
                            fontSize: 40,
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).primaryColor,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        usuario?.fullName ?? '',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        usuario?.email ?? '',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Contenido
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Información personal
                _buildSection(
                  context,
                  'Información Personal',
                  [
                    _buildInfoTile(
                      context,
                      Icons.person_outline,
                      'Nombre Completo',
                      usuario?.fullName ?? '',
                    ),
                    _buildInfoTile(
                      context,
                      Icons.email_outlined,
                      'Email',
                      usuario?.email ?? '',
                    ),
                    if (usuario?.telefono != null)
                      _buildInfoTile(
                        context,
                        Icons.phone_outlined,
                        'Teléfono',
                        usuario!.telefono!,
                      ),
                    if (usuario?.direccion != null)
                      _buildInfoTile(
                        context,
                        Icons.location_on_outlined,
                        'Dirección',
                        usuario!.direccion!,
                      ),
                  ],
                ),
                const SizedBox(height: 16),

                // Clínica actual
                _buildSection(
                  context,
                  'Clínica',
                  [
                    _buildActionTile(
                      context,
                      Icons.local_hospital_outlined,
                      clinicaProvider.clinicaSeleccionada?.nombre ?? 'Sin clínica',
                      'Cambiar clínica',
                      () => _cambiarClinica(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Cuenta
                _buildSection(
                  context,
                  'Cuenta',
                  [
                    _buildActionTile(
                      context,
                      Icons.edit_outlined,
                      'Editar Perfil',
                      null,
                      () => _editarPerfil(context),
                    ),
                    _buildActionTile(
                      context,
                      Icons.lock_outlined,
                      'Cambiar Contraseña',
                      null,
                      () => _cambiarPassword(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Notificaciones
                _buildSection(
                  context,
                  'Notificaciones',
                  [
                    _buildSwitchTile(
                      context,
                      Icons.notifications_outlined,
                      'Notificaciones Push',
                      true,
                      (value) {
                        // Implementar toggle
                      },
                    ),
                    _buildSwitchTile(
                      context,
                      Icons.email_outlined,
                      'Notificaciones por Email',
                      true,
                      (value) {
                        // Implementar toggle
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Acerca de
                _buildSection(
                  context,
                  'Acerca de',
                  [
                    _buildActionTile(
                      context,
                      Icons.info_outlined,
                      'Versión',
                      '1.0.0',
                      null,
                    ),
                    _buildActionTile(
                      context,
                      Icons.privacy_tip_outlined,
                      'Política de Privacidad',
                      null,
                      () {},
                    ),
                    _buildActionTile(
                      context,
                      Icons.description_outlined,
                      'Términos y Condiciones',
                      null,
                      () {},
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Cerrar sesión
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.logout, color: Colors.red),
                    title: const Text(
                      'Cerrar Sesión',
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    onTap: () => _cerrarSesion(context),
                  ),
                ),
                const SizedBox(height: 32),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection(BuildContext context, String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 8, bottom: 8),
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Card(
          child: Column(children: children),
        ),
      ],
    );
  }

  Widget _buildInfoTile(
    BuildContext context,
    IconData icon,
    String label,
    String value,
  ) {
    return ListTile(
      leading: Icon(icon, color: Theme.of(context).primaryColor),
      title: Text(label, style: Theme.of(context).textTheme.bodySmall),
      subtitle: Text(value, style: const TextStyle(fontSize: 16)),
    );
  }

  Widget _buildActionTile(
    BuildContext context,
    IconData icon,
    String title,
    String? subtitle,
    VoidCallback? onTap,
  ) {
    return ListTile(
      leading: Icon(icon, color: Theme.of(context).primaryColor),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: onTap != null
          ? const Icon(Icons.arrow_forward_ios, size: 16)
          : null,
      onTap: onTap,
    );
  }

  Widget _buildSwitchTile(
    BuildContext context,
    IconData icon,
    String title,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return ListTile(
      leading: Icon(icon, color: Theme.of(context).primaryColor),
      title: Text(title),
      trailing: Switch(
        value: value,
        onChanged: onChanged,
      ),
    );
  }

  void _editarPerfil(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const EditarPerfilScreen(),
      ),
    );
  }

  void _cambiarPassword(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const CambiarPasswordScreen(),
      ),
    );
  }

  void _cambiarClinica(BuildContext context) {
    // Mostrar diálogo de confirmación
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cambiar Clínica'),
        content: const Text(
          '¿Deseas cambiar de clínica? Esto cerrará tu sesión actual.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              final clinicaProvider = Provider.of<ClinicaProvider>(context, listen: false);
              
              authProvider.logout();
              clinicaProvider.limpiarClinica();
              context.go('/selector-clinica');
            },
            child: const Text('Cambiar'),
          ),
        ],
      ),
    );
  }

  void _cerrarSesion(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cerrar Sesión'),
        content: const Text('¿Estás seguro de que deseas cerrar sesión?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              authProvider.logout();
              context.go('/login');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Cerrar Sesión'),
          ),
        ],
      ),
    );
  }
}
```

---

## ✏️ Editar Perfil

### `lib/screens/perfil/editar_perfil_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/services/usuario_service.dart';
import 'package:clinica_dental_app/widgets/common/loading_indicator.dart';

class EditarPerfilScreen extends StatefulWidget {
  const EditarPerfilScreen({super.key});

  @override
  State<EditarPerfilScreen> createState() => _EditarPerfilScreenState();
}

class _EditarPerfilScreenState extends State<EditarPerfilScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _emailController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _direccionController = TextEditingController();
  final _service = UsuarioService();

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final usuario = Provider.of<AuthProvider>(context, listen: false).usuario;
    _nombreController.text = usuario?.fullName ?? '';
    _emailController.text = usuario?.email ?? '';
    _telefonoController.text = usuario?.telefono ?? '';
    _direccionController.text = usuario?.direccion ?? '';
  }

  @override
  void dispose() {
    _nombreController.dispose();
    _emailController.dispose();
    _telefonoController.dispose();
    _direccionController.dispose();
    super.dispose();
  }

  Future<void> _guardarCambios() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    try {
      await _service.actualizarPerfil(
        token: authProvider.accessToken!,
        nombre: _nombreController.text,
        telefono: _telefonoController.text,
        direccion: _direccionController.text,
      );

      if (mounted) {
        // Recargar datos del usuario
        await authProvider.cargarSesion();
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Perfil actualizado exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
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
        title: const Text('Editar Perfil'),
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _nombreController,
                      decoration: const InputDecoration(
                        labelText: 'Nombre Completo',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Ingresa tu nombre';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.email),
                      ),
                      enabled: false,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _telefonoController,
                      decoration: const InputDecoration(
                        labelText: 'Teléfono',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.phone),
                      ),
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _direccionController,
                      decoration: const InputDecoration(
                        labelText: 'Dirección',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_on),
                      ),
                      maxLines: 2,
                    ),
                    const SizedBox(height: 32),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _guardarCambios,
                        child: const Text('Guardar Cambios'),
                      ),
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

## 🔒 Cambiar Contraseña

### `lib/screens/perfil/cambiar_password_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/services/auth_service.dart';

class CambiarPasswordScreen extends StatefulWidget {
  const CambiarPasswordScreen({super.key});

  @override
  State<CambiarPasswordScreen> createState() => _CambiarPasswordScreenState();
}

class _CambiarPasswordScreenState extends State<CambiarPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _actualController = TextEditingController();
  final _nuevaController = TextEditingController();
  final _confirmarController = TextEditingController();
  final _service = AuthService();

  bool _isLoading = false;
  bool _obscureActual = true;
  bool _obscureNueva = true;
  bool _obscureConfirmar = true;

  @override
  void dispose() {
    _actualController.dispose();
    _nuevaController.dispose();
    _confirmarController.dispose();
    super.dispose();
  }

  Future<void> _cambiarPassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    try {
      await _service.cambiarPassword(
        token: authProvider.accessToken!,
        passwordActual: _actualController.text,
        passwordNueva: _nuevaController.text,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Contraseña actualizada exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
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
        title: const Text('Cambiar Contraseña'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _actualController,
                decoration: InputDecoration(
                  labelText: 'Contraseña Actual',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureActual ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _obscureActual = !_obscureActual);
                    },
                  ),
                ),
                obscureText: _obscureActual,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Ingresa tu contraseña actual';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nuevaController,
                decoration: InputDecoration(
                  labelText: 'Nueva Contraseña',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.lock),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureNueva ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _obscureNueva = !_obscureNueva);
                    },
                  ),
                ),
                obscureText: _obscureNueva,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Ingresa una nueva contraseña';
                  }
                  if (value.length < 6) {
                    return 'Mínimo 6 caracteres';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _confirmarController,
                decoration: InputDecoration(
                  labelText: 'Confirmar Nueva Contraseña',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.lock),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureConfirmar ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _obscureConfirmar = !_obscureConfirmar);
                    },
                  ),
                ),
                obscureText: _obscureConfirmar,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Confirma la nueva contraseña';
                  }
                  if (value != _nuevaController.text) {
                    return 'Las contraseñas no coinciden';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _cambiarPassword,
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Cambiar Contraseña'),
                ),
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

## 🔌 Servicio de Usuario

### `lib/services/usuario_service.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:clinica_dental_app/config/constants.dart';

class UsuarioService {
  final String baseUrl = AppConstants.baseUrlDev;

  Future<void> actualizarPerfil({
    required String token,
    required String nombre,
    String? telefono,
    String? direccion,
  }) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/api/usuarios/perfil/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'full_name': nombre,
          'telefono': telefono,
          'direccion': direccion,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Error al actualizar perfil');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}
```

---

## ✅ Checklist

- [ ] Crear `PerfilScreen`
- [ ] Crear `EditarPerfilScreen`
- [ ] Crear `CambiarPasswordScreen`
- [ ] Crear `UsuarioService`
- [ ] Secciones de información
- [ ] Cambio de clínica
- [ ] Configuración de notificaciones
- [ ] Cerrar sesión con confirmación

---

**Siguiente:** [12_api_service.md](12_api_service.md)
