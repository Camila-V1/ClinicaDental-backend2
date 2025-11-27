# 🚀 Configuración Inicial del Proyecto Flutter

## 📋 Requisitos Previos

- **Flutter SDK 3.24+** instalado
- **Android Studio** o **VS Code** con extensiones de Flutter
- **Dart SDK** (incluido con Flutter)
- **Git** para control de versiones

---

## 1️⃣ Crear Proyecto Flutter

```bash
# Crear proyecto nuevo
flutter create clinica_dental_admin

# Entrar al directorio
cd clinica_dental_admin

# Verificar instalación
flutter doctor
```

---

## 2️⃣ Configurar `pubspec.yaml`

Reemplaza el contenido con:

```yaml
name: clinica_dental_admin
description: App de administración para Clínica Dental
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # Estado global
  provider: ^6.1.1
  
  # Networking
  http: ^1.1.0
  
  # Persistencia local
  shared_preferences: ^2.2.2
  
  # Gráficos
  fl_chart: ^0.65.0
  
  # Formateo de datos
  intl: ^0.18.1
  
  # Manejo de archivos
  path_provider: ^2.1.1
  permission_handler: ^11.0.1
  
  # UI
  cupertino_icons: ^1.0.6

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  
  # Descomentar si tienes assets
  # assets:
  #   - assets/images/
  #   - assets/icons/
```

---

## 3️⃣ Instalar Dependencias

```bash
flutter pub get
```

**Verificación:**
```bash
flutter pub deps
```

---

## 4️⃣ Configurar Permisos Android

### `android/app/src/main/AndroidManifest.xml`

Agrega dentro de `<manifest>`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- Permisos necesarios -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"/>
    
    <application
        android:label="Clínica Dental Admin"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true">
        
        <!-- ... resto de configuración ... -->
        
    </application>
</manifest>
```

**Nota:** `android:usesCleartextTraffic="true"` permite HTTP (para desarrollo local).

---

## 5️⃣ Configurar Gradle (Android)

### `android/app/build.gradle`

```gradle
android {
    namespace "com.clinica.dental.admin"
    compileSdk 34  // Actualizar si es necesario
    
    defaultConfig {
        applicationId "com.clinica.dental.admin"
        minSdk 21  // Mínimo Android 5.0
        targetSdk 34
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

---

## 6️⃣ Configurar iOS (Opcional)

### `ios/Runner/Info.plist`

Agrega dentro de `<dict>`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso para guardar reportes</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>Necesitamos acceso para guardar reportes</string>
```

---

## 7️⃣ Configurar Variables de Entorno

### `lib/config/env.dart`

```dart
/// Configuración de entorno de la aplicación
class AppConfig {
  // URL del backend
  static const String baseUrl = 'https://clinica-dental-backend.onrender.com';
  
  // Tenant por defecto
  static const String defaultTenant = 'clinica_demo';
  
  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Paginación
  static const int defaultPageSize = 20;
  
  // Desarrollo
  static const bool isDebugMode = true; // Cambiar a false en producción
}
```

---

## 8️⃣ Verificar Configuración

```bash
# Limpiar build anterior
flutter clean

# Instalar dependencias nuevamente
flutter pub get

# Compilar para Android (verificar errores)
flutter build apk --debug

# O ejecutar en emulador/dispositivo
flutter run
```

---

## 9️⃣ Estructura Inicial de Archivos

Después de configurar, tu proyecto debe verse así:

```
clinica_dental_admin/
├── android/
├── ios/
├── lib/
│   ├── config/
│   │   └── env.dart
│   ├── models/
│   ├── providers/
│   ├── screens/
│   ├── services/
│   ├── widgets/
│   └── main.dart
├── test/
├── pubspec.yaml
└── README.md
```

---

## 🔟 Configurar `main.dart` Temporal

### `lib/main.dart`

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Clínica Dental Admin',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.local_hospital, size: 100, color: Colors.teal),
              SizedBox(height: 20),
              Text(
                'Clínica Dental Admin',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 10),
              Text('Configuración completada ✅'),
            ],
          ),
        ),
      ),
    );
  }
}
```

**Ejecutar:**
```bash
flutter run
```

Deberías ver una pantalla con el ícono de hospital y texto de confirmación.

---

## 🐛 Solución de Problemas Comunes

### Error: SDK Version
```bash
flutter upgrade
flutter pub get
```

### Error: Gradle Build Failed
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
```

### Error: Permission Denied (Linux/Mac)
```bash
chmod +x android/gradlew
```

### Error: CocoaPods (iOS)
```bash
cd ios
pod install
cd ..
```

---

## ✅ Checklist de Verificación

- [ ] Flutter SDK instalado y actualizado
- [ ] Proyecto creado exitosamente
- [ ] Dependencias instaladas (`flutter pub get`)
- [ ] Permisos Android configurados
- [ ] Variables de entorno creadas (`env.dart`)
- [ ] `flutter run` ejecuta sin errores
- [ ] Pantalla de prueba visible en emulador/dispositivo

---

## 📚 Recursos Adicionales

- [Flutter Installation Guide](https://docs.flutter.dev/get-started/install)
- [Flutter Doctor](https://docs.flutter.dev/get-started/install/windows#run-flutter-doctor)
- [Android Setup](https://docs.flutter.dev/get-started/install/windows#android-setup)
- [iOS Setup](https://docs.flutter.dev/get-started/install/macos/mobile-ios)

---

## 🎯 Siguiente Paso

Una vez completada la configuración, continúa con:
👉 **[02_ESTRUCTURA_PROYECTO.md](02_ESTRUCTURA_PROYECTO.md)**

