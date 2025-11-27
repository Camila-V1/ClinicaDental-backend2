# 🔄 CAMBIOS EN FLUTTER PARA BACKEND ACTUAL

> **Fecha:** 27/11/2025  
> **Objetivo:** Actualizar la app Flutter para usar las nuevas funcionalidades del backend

---

## 📋 RESUMEN DE NUEVAS FUNCIONALIDADES BACKEND

El backend actual tiene implementadas estas funcionalidades que Flutter NO está usando:

### ✅ 1. Sistema de Valoraciones con Notificaciones Push
- App Django: `valoraciones`
- Notificaciones automáticas con Firebase cuando se completa una cita
- 6 endpoints REST para gestionar valoraciones
- Campo `fcm_token` en modelo Usuario

### ✅ 2. Pagos con Stripe para Facturas
- Integración completa con Stripe Checkout
- Endpoints para crear Payment Intent
- Confirmación de pagos
- Webhook configurado

### ✅ 3. Pagos con Stripe para Citas
- Pago directo de citas sin factura
- Endpoints específicos en `facturacion/views_pagos.py`

### ✅ 4. Pagos con Stripe para Planes de Tratamiento
- Pago completo o parcial de planes
- Tracking de pagos por plan

---

## 🚀 QUÉ HAY QUE AGREGAR EN FLUTTER

---

## 1️⃣ SISTEMA DE VALORACIONES

### Backend Endpoints Disponibles:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/usuarios/registrar-fcm-token/` | POST | Registrar token FCM del dispositivo |
| `/api/valoraciones/` | POST | Crear nueva valoración |
| `/api/valoraciones/` | GET | Listar valoraciones (admin) |
| `/api/valoraciones/{id}/` | GET | Detalle de valoración |
| `/api/valoraciones/mis_valoraciones/` | GET | Valoraciones del paciente |
| `/api/valoraciones/citas_pendientes_valoracion/` | GET | Citas sin valorar |
| `/api/valoraciones/mis_estadisticas/` | GET | Estadísticas del odontólogo |
| `/api/valoraciones/ranking_odontologos/` | GET | Ranking de odontólogos (admin) |

### 1.1 Dependencias Necesarias

Agregar en `pubspec.yaml`:

```yaml
dependencies:
  # Firebase para notificaciones push
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.6
  flutter_local_notifications: ^16.3.0
  
  # Rating UI
  flutter_rating_bar: ^4.0.1
```

### 1.2 Configuración Firebase Android

**Archivo:** `android/app/google-services.json`

> ⚠️ **IMPORTANTE:** Solicitar el archivo `google-services.json` al administrador del backend.  
> El proyecto Firebase ID es: `psicoadmin-94485`

### 1.3 Modelo Dart para Valoracion

**Archivo:** `lib/models/valoracion.dart`

```dart
class Valoracion {
  final int? id;
  final int cita;
  final int calificacion;  // 1-5
  final String? comentario;
  final int? puntualidad;  // 1-5 opcional
  final int? trato;        // 1-5 opcional
  final int? limpieza;     // 1-5 opcional
  final DateTime? createdAt;
  final bool? notificacionEnviada;

  Valoracion({
    this.id,
    required this.cita,
    required this.calificacion,
    this.comentario,
    this.puntualidad,
    this.trato,
    this.limpieza,
    this.createdAt,
    this.notificacionEnviada,
  });

  factory Valoracion.fromJson(Map<String, dynamic> json) {
    return Valoracion(
      id: json['id'],
      cita: json['cita'],
      calificacion: json['calificacion'],
      comentario: json['comentario'],
      puntualidad: json['puntualidad'],
      trato: json['trato'],
      limpieza: json['limpieza'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      notificacionEnviada: json['notificacion_enviada'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'cita': cita,
      'calificacion': calificacion,
      'comentario': comentario,
      'puntualidad': puntualidad,
      'trato': trato,
      'limpieza': limpieza,
    };
  }
}
```

### 1.4 Servicio API para Valoraciones

**Archivo:** `lib/services/valoraciones_service.dart`

```dart
import 'package:dio/dio.dart';
import '../models/valoracion.dart';
import 'api_client.dart';

class ValoracionesService {
  final ApiClient _apiClient = ApiClient();

  // Registrar token FCM
  Future<void> registrarFCMToken(String fcmToken) async {
    try {
      await _apiClient.post('/api/usuarios/registrar-fcm-token/', data: {
        'fcm_token': fcmToken,
      });
    } catch (e) {
      print('Error registrando token FCM: $e');
      rethrow;
    }
  }

  // Crear valoración
  Future<Valoracion> crearValoracion(Valoracion valoracion) async {
    try {
      final response = await _apiClient.post(
        '/api/valoraciones/',
        data: valoracion.toJson(),
      );
      return Valoracion.fromJson(response.data);
    } catch (e) {
      print('Error creando valoración: $e');
      rethrow;
    }
  }

  // Obtener mis valoraciones
  Future<List<Valoracion>> obtenerMisValoraciones() async {
    try {
      final response = await _apiClient.get(
        '/api/valoraciones/mis_valoraciones/',
      );
      return (response.data as List)
          .map((json) => Valoracion.fromJson(json))
          .toList();
    } catch (e) {
      print('Error obteniendo valoraciones: $e');
      rethrow;
    }
  }

  // Obtener citas pendientes de valoración
  Future<Map<String, dynamic>> obtenerCitasPendientesValoracion() async {
    try {
      final response = await _apiClient.get(
        '/api/valoraciones/citas_pendientes_valoracion/',
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      print('Error obteniendo citas pendientes: $e');
      rethrow;
    }
  }
}
```

### 1.5 Inicializar Firebase en main.dart

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar Firebase
  await Firebase.initializeApp();
  
  // Solicitar permisos de notificaciones
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  await messaging.requestPermission();
  
  runApp(MyApp());
}
```

---

## 2️⃣ PAGOS CON STRIPE

### Backend Endpoints Disponibles:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/facturacion/pagos/crear-pago-cita/` | POST | Crear pago para cita |
| `/api/facturacion/pagos/crear-pago-plan/` | POST | Crear pago para plan tratamiento |
| `/api/facturacion/pagos/{id}/confirmar/` | POST/GET | Confirmar pago completado |
| `/api/facturacion/pagos/{id}/estado/` | GET | Verificar estado de pago |

### 2.1 Dependencias Necesarias

```yaml
dependencies:
  flutter_stripe: ^10.1.0
  url_launcher: ^6.2.2
```

### 2.2 Configuración Stripe

**En el backend** ya está configurado con Stripe.

**En Flutter** agregar en `main.dart`:

```dart
import 'package:flutter_stripe/flutter_stripe.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Configurar Stripe (solicitar la clave pública al administrador)
  Stripe.publishableKey = 'SOLICITAR_AL_ADMINISTRADOR';
  
  runApp(MyApp());
}
```

> ⚠️ **NOTA:** Solicitar la `STRIPE_PUBLIC_KEY` al administrador del backend (está en el archivo `.env`)

### 2.3 Modelo Pago

**Archivo:** `lib/models/pago.dart`

```dart
class Pago {
  final int? id;
  final int? factura;
  final int? cita;
  final int? planTratamiento;
  final double montoPagado;
  final String metodoPago;  // STRIPE, EFECTIVO, etc.
  final String estadoPago;  // COMPLETADO, PROCESANDO, FALLIDO
  final String? transaccionId;
  final DateTime? fechaPago;

  Pago({
    this.id,
    this.factura,
    this.cita,
    this.planTratamiento,
    required this.montoPagado,
    required this.metodoPago,
    required this.estadoPago,
    this.transaccionId,
    this.fechaPago,
  });

  factory Pago.fromJson(Map<String, dynamic> json) {
    return Pago(
      id: json['id'],
      factura: json['factura'],
      cita: json['cita'],
      planTratamiento: json['plan_tratamiento'],
      montoPagado: double.parse(json['monto_pagado'].toString()),
      metodoPago: json['metodo_pago'],
      estadoPago: json['estado_pago'],
      transaccionId: json['transaccion_id'],
      fechaPago: json['fecha_pago'] != null 
          ? DateTime.parse(json['fecha_pago']) 
          : null,
    );
  }
}
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Valoraciones
- [ ] Agregar dependencias Firebase en `pubspec.yaml`
- [ ] Solicitar y copiar `google-services.json` a `android/app/`
- [ ] Configurar `android/build.gradle` y `android/app/build.gradle`
- [ ] Crear modelo `Valoracion`
- [ ] Crear servicio `ValoracionesService`
- [ ] Inicializar Firebase en `main.dart`
- [ ] Agregar badge en citas completadas
- [ ] Probar notificaciones push

### Pagos Stripe
- [ ] Agregar dependencia `flutter_stripe` en `pubspec.yaml`
- [ ] Solicitar `STRIPE_PUBLIC_KEY` al administrador
- [ ] Configurar `Stripe.publishableKey` en `main.dart`
- [ ] Crear modelo `Pago`
- [ ] Crear servicio `PagosService`
- [ ] Agregar botón "Pagar" en facturas pendientes
- [ ] Implementar deep linking para confirmación
- [ ] Probar pago completo

---

## 🚀 PRIORIDAD DE IMPLEMENTACIÓN

1. **ALTA:** Valoraciones (mejora experiencia del paciente)
2. **ALTA:** Pagos Stripe (genera ingresos)
3. **MEDIA:** Actualización UI de facturas
4. **MEDIA:** Actualización UI de citas con badge

---

## 🔗 RECURSOS

- Firebase Flutter: https://firebase.google.com/docs/flutter/setup
- Flutter Stripe: https://pub.dev/packages/flutter_stripe
- Backend Guías: Ver `GUIA_SISTEMA_VALORACIONES.md`
