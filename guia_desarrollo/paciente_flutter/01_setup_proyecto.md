# 🏗️ Setup del Proyecto Flutter

## 🎯 Objetivo
Crear y configurar el proyecto Flutter para la app móvil del paciente.

---

## 📋 Requisitos Previos

- Flutter SDK 3.16.0 o superior
- Dart 3.2.0 o superior
- Android Studio / VS Code con extensiones Flutter
- Xcode (para iOS, solo macOS)
- Git

---

## 🚀 Crear Proyecto

### 1. Crear proyecto Flutter

```bash
# Navegar a la carpeta donde quieres crear el proyecto
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO"

# Crear proyecto
flutter create clinica_dental_app

# Entrar al proyecto
cd clinica_dental_app

# Verificar que funciona
flutter doctor
```

### 2. Configurar `pubspec.yaml`

```yaml
name: clinica_dental_app
description: App móvil para pacientes de clínicas dentales
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # HTTP & API
  http: ^1.1.0
  dio: ^5.4.0
  
  # State Management
  provider: ^6.1.1
  
  # Storage
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0
  
  # UI & Navigation
  go_router: ^12.1.1
  cupertino_icons: ^1.0.6
  
  # Forms & Validation
  intl: ^0.18.1
  
  # Date & Time
  table_calendar: ^3.0.9
  
  # Notifications
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.6
  flutter_local_notifications: ^16.3.0
  
  # UI Enhancements
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  pull_to_refresh: ^2.0.0
  
  # Utils
  url_launcher: ^6.2.2
  share_plus: ^7.2.1
  fluttertoast: ^8.2.4

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
    - assets/animations/
  
  fonts:
    - family: Poppins
      fonts:
        - asset: assets/fonts/Poppins-Regular.ttf
        - asset: assets/fonts/Poppins-Medium.ttf
          weight: 500
        - asset: assets/fonts/Poppins-SemiBold.ttf
          weight: 600
        - asset: assets/fonts/Poppins-Bold.ttf
          weight: 700
```

### 3. Instalar dependencias

```bash
flutter pub get
```

---

## 📁 Crear Estructura de Carpetas

```bash
# Crear estructura de carpetas
mkdir lib/config
mkdir lib/core
mkdir lib/core/api
mkdir lib/core/storage
mkdir lib/core/utils
mkdir lib/models
mkdir lib/providers
mkdir lib/services
mkdir lib/screens
mkdir lib/screens/citas
mkdir lib/screens/tratamientos
mkdir lib/screens/historial
mkdir lib/screens/facturas
mkdir lib/screens/perfil
mkdir lib/widgets
mkdir lib/widgets/common
mkdir lib/widgets/citas
mkdir lib/widgets/tratamientos
mkdir lib/widgets/facturas
mkdir assets
mkdir assets/images
mkdir assets/icons
mkdir assets/fonts
```

---

## 🎨 Configurar Tema

### `lib/config/theme.dart`

```dart
import 'package:flutter/material.dart';

class AppTheme {
  // Colores principales
  static const Color primaryColor = Color(0xFF3B82F6); // Blue 500
  static const Color secondaryColor = Color(0xFF10B981); // Green 500
  static const Color accentColor = Color(0xFF8B5CF6); // Purple 500
  static const Color backgroundColor = Color(0xFFF9FAFB); // Gray 50
  static const Color surfaceColor = Color(0xFFFFFFFF);
  static const Color errorColor = Color(0xFFEF4444); // Red 500
  static const Color warningColor = Color(0xFFF59E0B); // Yellow 500
  
  // Colores de texto
  static const Color textPrimary = Color(0xFF111827); // Gray 900
  static const Color textSecondary = Color(0xFF6B7280); // Gray 500
  static const Color textDisabled = Color(0xFF9CA3AF); // Gray 400

  // Tema claro
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    primaryColor: primaryColor,
    scaffoldBackgroundColor: backgroundColor,
    colorScheme: const ColorScheme.light(
      primary: primaryColor,
      secondary: secondaryColor,
      error: errorColor,
      background: backgroundColor,
      surface: surfaceColor,
    ),
    
    // AppBar
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: surfaceColor,
      foregroundColor: textPrimary,
      iconTheme: IconThemeData(color: textPrimary),
      titleTextStyle: TextStyle(
        color: textPrimary,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        fontFamily: 'Poppins',
      ),
    ),
    
    // Botones
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        elevation: 0,
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          fontFamily: 'Poppins',
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primaryColor,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        side: const BorderSide(color: primaryColor, width: 2),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          fontFamily: 'Poppins',
        ),
      ),
    ),
    
    // Inputs
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surfaceColor,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: errorColor),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      hintStyle: const TextStyle(color: textDisabled),
    ),
    
    // Cards
    cardTheme: CardTheme(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE5E7EB), width: 1),
      ),
      color: surfaceColor,
    ),
    
    // Tipografía
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: textPrimary,
        fontFamily: 'Poppins',
      ),
      headlineMedium: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: textPrimary,
        fontFamily: 'Poppins',
      ),
      headlineSmall: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: textPrimary,
        fontFamily: 'Poppins',
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        color: textPrimary,
        fontFamily: 'Poppins',
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        color: textSecondary,
        fontFamily: 'Poppins',
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        color: textSecondary,
        fontFamily: 'Poppins',
      ),
    ),
    
    fontFamily: 'Poppins',
  );
}
```

---

## 🔧 Configurar Constantes

### `lib/config/constants.dart`

```dart
class AppConstants {
  // API
  static const String baseUrl = 'http://tu-servidor.com';
  static const String baseUrlDev = 'http://10.0.2.2:8000'; // Android Emulator
  static const String baseUrlDevIOS = 'http://localhost:8000'; // iOS Simulator
  
  // Storage Keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyTenantId = 'tenant_id';
  static const String keyTenantName = 'tenant_name';
  static const String keyUserId = 'user_id';
  static const String keyUserEmail = 'user_email';
  static const String keyUserName = 'user_name';
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Pagination
  static const int defaultPageSize = 20;
  
  // Formato de fechas
  static const String dateFormat = 'dd/MM/yyyy';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'dd/MM/yyyy HH:mm';
}
```

---

## 🚦 Configurar Rutas

### `lib/config/routes.dart`

```dart
import 'package:go_router/go_router.dart';
import 'package:clinica_dental_app/screens/splash_screen.dart';
import 'package:clinica_dental_app/screens/selector_clinica_screen.dart';
import 'package:clinica_dental_app/screens/login_screen.dart';
import 'package:clinica_dental_app/screens/registro_screen.dart';
import 'package:clinica_dental_app/screens/home_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/selector-clinica',
        builder: (context, state) => const SelectorClinicaScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/registro',
        builder: (context, state) => const RegistroScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      // Más rutas...
    ],
  );
}
```

---

## 📱 Configurar `main.dart`

### `lib/main.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clinica_dental_app/config/theme.dart';
import 'package:clinica_dental_app/config/routes.dart';
import 'package:clinica_dental_app/providers/auth_provider.dart';
import 'package:clinica_dental_app/providers/clinica_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar Firebase (opcional, para notificaciones)
  // await Firebase.initializeApp();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ClinicaProvider()),
        // Más providers...
      ],
      child: MaterialApp.router(
        title: 'Clínica Dental',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        routerConfig: AppRouter.router,
      ),
    );
  }
}
```

---

## ⚙️ Configuración de Android

### `android/app/build.gradle`

```gradle
android {
    namespace "com.tuempresa.clinica_dental_app"
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.tuempresa.clinica_dental_app"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.debug
        }
    }
}
```

### `android/app/src/main/AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permisos -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    
    <application
        android:label="Clínica Dental"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true"> <!-- Para desarrollo -->
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
              />
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

## 🍎 Configuración de iOS

### `ios/Runner/Info.plist`

```xml
<key>CFBundleName</key>
<string>Clínica Dental</string>
<key>CFBundleDisplayName</key>
<string>Clínica Dental</string>

<!-- Permisos -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para tomar fotos de documentos</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a la galería para subir imágenes</string>
```

---

## ✅ Verificar Instalación

```bash
# Verificar que todo está bien
flutter doctor -v

# Ejecutar en emulador/dispositivo Android
flutter run

# Ejecutar en emulador/dispositivo iOS
flutter run -d ios

# Build para producción
flutter build apk --release
flutter build ios --release
```

---

## 🎯 Próximo Paso

Ahora que el proyecto está configurado, continuamos con:
- **[03_selector_clinica.md](03_selector_clinica.md)** - Crear la pantalla de selección de clínica
