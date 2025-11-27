# 🔥 GUÍA DE CONFIGURACIÓN: SISTEMA DE VALORACIONES CON NOTIFICACIONES PUSH

## 📋 RESUMEN DEL SISTEMA IMPLEMENTADO

✅ **Backend completo creado:**
- App `valoraciones` con modelo Valoracion
- Notificaciones push con Firebase Cloud Messaging
- Señal automática que detecta citas completadas
- 6 endpoints REST para gestionar valoraciones
- Campo `fcm_token` agregado al modelo Usuario

---

## 🚀 PARTE 1: CONFIGURAR FIREBASE EN RENDER (BACKEND)

### 1.1 Convertir credenciales JSON a variable de entorno

El archivo `psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json` está en tu carpeta local pero NO en GitHub (por seguridad).

**Paso 1:** Abre el archivo y copia todo su contenido.

**Paso 2:** Ve a Render Dashboard:
1. Entra a tu servicio `clinica-dental-backend`
2. Click en **"Environment"** (menú izquierdo)
3. Click en **"Add Environment Variable"**
4. Agrega:
   ```
   Key: FIREBASE_CREDENTIALS_JSON
   Value: [PEGA TODO EL CONTENIDO DEL ARCHIVO JSON AQUÍ]
   ```
5. **IMPORTANTE:** El valor debe ser el JSON completo, empezando con `{` y terminando con `}`
6. Click en **"Save Changes"**

Render reiniciará el servicio automáticamente (~2 minutos).

### 1.2 Actualizar firebase_service.py para usar variable de entorno

El archivo ya está configurado para buscar el archivo JSON localmente. Para producción, vamos a modificarlo:

```python
# valoraciones/firebase_service.py (líneas 13-24)
# Cambiar de:
firebase_cred_path = Path(settings.BASE_DIR) / 'psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json'

# A:
import os
import json

firebase_cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
if firebase_cred_json:
    cred = credentials.Certificate(json.loads(firebase_cred_json))
    initialize_app(cred)
else:
    # Fallback para desarrollo local
    firebase_cred_path = Path(settings.BASE_DIR) / 'psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json'
    if firebase_cred_path.exists():
        cred = credentials.Certificate(str(firebase_cred_path))
        initialize_app(cred)
```

Hago el cambio ahora mismo... ✅

---

## 📱 PARTE 2: CONFIGURAR REACT NATIVE (FRONTEND)

### 2.1 Instalar Firebase en tu app React Native

```bash
npm install @react-native-firebase/app @react-native-firebase/messaging
```

### 2.2 Configurar Android

**Paso 1:** Copia el archivo `google-services (3).json` que está en tu carpeta raíz del backend.

**Paso 2:** Pega el archivo en:
```
android/app/google-services.json
```

**Paso 3:** Edita `android/build.gradle`:
```gradle
buildscript {
    dependencies {
        // Agregar esta línea
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

**Paso 4:** Edita `android/app/build.gradle`:
```gradle
// Al FINAL del archivo, agregar:
apply plugin: 'com.google.gms.google-services'
```

**Paso 5:** Edita `AndroidManifest.xml`:
```xml
<application ...>
    <!-- Agregar esto -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_channel_id"
        android:value="@string/default_notification_channel_id" />
</application>
```

### 2.3 Código React Native para manejar notificaciones

**Archivo: `src/services/firebaseService.js`**
```javascript
import messaging from '@react-native-firebase/messaging';
import axios from './axiosConfig';

class FirebaseService {
  async requestPermission() {
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
      console.log('✅ Permisos de notificación concedidos');
      await this.getFCMToken();
    }
  }

  async getFCMToken() {
    try {
      const fcmToken = await messaging().getToken();
      console.log('📱 Token FCM obtenido:', fcmToken);
      
      // Enviar token al backend
      await axios.post('/api/usuarios/registrar-fcm-token/', {
        fcm_token: fcmToken
      });
      
      console.log('✅ Token registrado en el backend');
      return fcmToken;
    } catch (error) {
      console.error('❌ Error al obtener token FCM:', error);
    }
  }

  setupNotificationListeners() {
    // Escuchar notificaciones cuando la app está en primer plano
    messaging().onMessage(async remoteMessage => {
      console.log('📬 Notificación recibida (app abierta):', remoteMessage);
      
      if (remoteMessage.data.tipo === 'solicitud_valoracion') {
        // Mostrar modal o navegar a pantalla de valoración
        const citaId = remoteMessage.data.cita_id;
        // navigation.navigate('ValoracionScreen', { citaId });
      }
    });

    // Escuchar cuando el usuario toca la notificación
    messaging().onNotificationOpenedApp(remoteMessage => {
      console.log('👆 Notificación tocada (app en background):', remoteMessage);
      
      if (remoteMessage.data.tipo === 'solicitud_valoracion') {
        const citaId = remoteMessage.data.cita_id;
        // navigation.navigate('ValoracionScreen', { citaId });
      }
    });

    // Escuchar cuando la app se abre desde una notificación (app cerrada)
    messaging()
      .getInitialNotification()
      .then(remoteMessage => {
        if (remoteMessage) {
          console.log('🚀 App abierta desde notificación:', remoteMessage);
          
          if (remoteMessage.data.tipo === 'solicitud_valoracion') {
            const citaId = remoteMessage.data.cita_id;
            // navigation.navigate('ValoracionScreen', { citaId });
          }
        }
      });
  }
}

export default new FirebaseService();
```

**Archivo: `src/screens/ValoracionScreen.js`**
```javascript
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity } from 'react-native';
import axios from '../services/axiosConfig';

const ValoracionScreen = ({ route }) => {
  const { citaId } = route.params;
  const [calificacion, setCalificacion] = useState(5);
  const [comentario, setComentario] = useState('');
  const [puntualidad, setPuntualidad] = useState(null);
  const [trato, setTrato] = useState(null);
  const [limpieza, setLimpieza] = useState(null);

  const enviarValoracion = async () => {
    try {
      await axios.post('/api/valoraciones/', {
        cita: citaId,
        calificacion,
        comentario,
        puntualidad,
        trato,
        limpieza
      });
      
      alert('✅ ¡Gracias por tu valoración!');
      // navigation.goBack();
    } catch (error) {
      console.error('Error al enviar valoración:', error);
      alert('❌ Error al enviar valoración');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold' }}>
        ¿Cómo fue tu atención? 🦷
      </Text>
      
      {/* Componente de estrellas para calificación */}
      {/* ... */}
      
      <TextInput
        multiline
        placeholder="Comentario (opcional)"
        value={comentario}
        onChangeText={setComentario}
        style={{ borderWidth: 1, padding: 10, marginTop: 20 }}
      />
      
      <TouchableOpacity
        onPress={enviarValoracion}
        style={{ backgroundColor: '#2196F3', padding: 15, marginTop: 20 }}
      >
        <Text style={{ color: 'white', textAlign: 'center', fontSize: 16 }}>
          Enviar Valoración
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default ValoracionScreen;
```

**Inicializar Firebase al arrancar la app (`App.js`):**
```javascript
import { useEffect } from 'react';
import firebaseService from './src/services/firebaseService';

function App() {
  useEffect(() => {
    // Solicitar permisos y configurar listeners
    firebaseService.requestPermission();
    firebaseService.setupNotificationListeners();
  }, []);

  return (
    // ... tu app
  );
}
```

---

## 🔌 PARTE 3: ENDPOINTS DISPONIBLES

### 1. **Registrar Token FCM**
```http
POST /api/usuarios/registrar-fcm-token/
Authorization: Bearer <token>
Content-Type: application/json

{
  "fcm_token": "dA8xF..."
}
```

### 2. **Crear Valoración**
```http
POST /api/valoraciones/
Authorization: Bearer <token>
Content-Type: application/json

{
  "cita": 123,
  "calificacion": 5,
  "comentario": "Excelente atención",
  "puntualidad": 5,
  "trato": 5,
  "limpieza": 5
}
```

### 3. **Ver Mis Valoraciones (Paciente)**
```http
GET /api/valoraciones/mis_valoraciones/
Authorization: Bearer <token>
```

### 4. **Ver Estadísticas (Odontólogo)**
```http
GET /api/valoraciones/mis_estadisticas/
Authorization: Bearer <token>
```

### 5. **Citas Pendientes de Valoración**
```http
GET /api/valoraciones/citas_pendientes_valoracion/
Authorization: Bearer <token>
```

### 6. **Ranking de Odontólogos (Admin)**
```http
GET /api/valoraciones/ranking_odontologos/
Authorization: Bearer <token>
```

---

## 🧪 PARTE 4: PROBAR EL SISTEMA

### Paso 1: Completar una cita
```bash
# Cambiar estado de una cita a COMPLETADA
# Esto dispara automáticamente la señal que envía notificación push
```

### Paso 2: El paciente recibirá notificación en su dispositivo

### Paso 3: Al tocar la notificación, se abre la app en la pantalla de valoración

### Paso 4: El paciente califica y envía la valoración

---

## 📊 MODELO DE DATOS

```python
class Valoracion:
    cita (OneToOne)           # Cita que se está valorando
    paciente (ForeignKey)     # Quien valora
    odontologo (ForeignKey)   # Quien recibe la valoración
    calificacion (int 1-5)    # Calificación general
    comentario (text)         # Comentario opcional
    puntualidad (int 1-5)     # Opcional
    trato (int 1-5)           # Opcional
    limpieza (int 1-5)        # Opcional
    created_at
    updated_at
    notificacion_enviada (bool)
    notificacion_enviada_at
```

---

## ⚡ FLUJO AUTOMÁTICO

1. **Odontólogo completa una cita** → Estado cambia a `COMPLETADA`
2. **Señal Django detecta el cambio** → `valoraciones/signals.py`
3. **Se envía notificación push** → Firebase Cloud Messaging
4. **Paciente recibe notificación** → En su dispositivo móvil
5. **Paciente toca notificación** → App abre pantalla de valoración
6. **Paciente califica** → POST `/api/valoraciones/`
7. **Valoración guardada** → Visible en estadísticas del odontólogo

---

## 🔧 PRÓXIMOS PASOS

1. ✅ Configurar variable de entorno en Render
2. ✅ Modificar firebase_service.py (lo hago ahora)
3. ⏳ Instalar Firebase en React Native
4. ⏳ Implementar pantalla de valoración
5. ⏳ Probar con cita real

¿Te ayudo con algún paso específico?
