# 🤖 Chatbot para Flutter - Clínica Dental

Guía completa para implementar un chatbot en la aplicación Flutter de la clínica dental.

## 📋 Tabla de Contenidos

1. [Arquitectura del Chatbot](#arquitectura)
2. [Configuración del Backend](#backend)
3. [Implementación en Flutter](#flutter)
4. [Integración con IA](#ia)
5. [Funcionalidades del Chatbot](#funcionalidades)

---

## 🏗️ Arquitectura del Chatbot

```
┌─────────────────┐
│  Flutter App    │
│  (Usuario)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API REST       │
│  /api/chatbot/  │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│  Base de Datos  │  │  IA Service  │
│  (Mensajes)     │  │  (OpenAI/    │
│                 │  │   Gemini)    │
└─────────────────┘  └──────────────┘
```

---

## 🔧 Configuración del Backend (Django)

### 1. Crear la App `chatbot`

```bash
cd ClinicaDental-backend2
python manage.py startapp chatbot
```

### 2. Modelos (chatbot/models.py)

```python
from django.db import models
from django.conf import settings
from usuarios.models import Usuario

class Conversacion(models.Model):
    """Conversación del chatbot con un usuario."""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='conversaciones')
    titulo = models.CharField(max_length=200, default='Nueva conversación')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
    
    def __str__(self):
        return f"{self.usuario.nombre} - {self.titulo}"


class Mensaje(models.Model):
    """Mensaje individual en una conversación."""
    
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]
    
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Para guardar contexto adicional
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class IntentoChatbot(models.Model):
    """Intenciones predefinidas del chatbot."""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    ejemplos = models.JSONField(default=list)  # Lista de ejemplos de frases
    respuesta_template = models.TextField()
    requiere_autenticacion = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Intento'
        verbose_name_plural = 'Intentos'
    
    def __str__(self):
        return self.nombre
```

### 3. Serializers (chatbot/serializers.py)

```python
from rest_framework import serializers
from .models import Conversacion, Mensaje, IntentoChatbot


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'role', 'content', 'timestamp', 'metadata']
        read_only_fields = ['id', 'timestamp']


class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    
    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'usuario', 'usuario_nombre', 'mensajes', 
                 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConversacionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar conversaciones."""
    
    ultimo_mensaje = serializers.SerializerMethodField()
    total_mensajes = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'ultimo_mensaje', 'total_mensajes', 
                 'created_at', 'updated_at', 'is_active']
    
    def get_ultimo_mensaje(self, obj):
        ultimo = obj.mensajes.last()
        if ultimo:
            return {
                'content': ultimo.content[:100],
                'role': ultimo.role,
                'timestamp': ultimo.timestamp
            }
        return None
    
    def get_total_mensajes(self, obj):
        return obj.mensajes.count()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer para recibir mensajes del usuario."""
    
    mensaje = serializers.CharField(max_length=2000)
    conversacion_id = serializers.IntegerField(required=False, allow_null=True)
    contexto = serializers.JSONField(required=False, default=dict)
```

### 4. Views (chatbot/views.py)

Ver archivo: `01_views_chatbot.py`

### 5. URLs (chatbot/urls.py)

```python
from django.urls import path
from .views import (
    ChatBotView,
    ConversacionListView,
    ConversacionDetailView,
    IntentosDisponiblesView
)

urlpatterns = [
    path('chat/', ChatBotView.as_view(), name='chatbot'),
    path('conversaciones/', ConversacionListView.as_view(), name='conversaciones_list'),
    path('conversaciones/<int:pk>/', ConversacionDetailView.as_view(), name='conversacion_detail'),
    path('intentos/', IntentosDisponiblesView.as_view(), name='intentos_disponibles'),
]
```

### 6. Registrar en core/urls_tenant.py

```python
# Agregar al final
path('api/chatbot/', include('chatbot.urls')),
```

### 7. Agregar a TENANT_APPS en settings.py

```python
TENANT_APPS = [
    # ... otras apps
    'chatbot',
]
```

---

## 📱 Implementación en Flutter

### Estructura de Carpetas

```
lib/
├── features/
│   └── chatbot/
│       ├── models/
│       │   ├── mensaje_model.dart
│       │   ├── conversacion_model.dart
│       │   └── chat_response_model.dart
│       ├── providers/
│       │   └── chatbot_provider.dart
│       ├── services/
│       │   └── chatbot_service.dart
│       ├── screens/
│       │   ├── chat_screen.dart
│       │   └── conversaciones_screen.dart
│       └── widgets/
│           ├── mensaje_bubble.dart
│           ├── chat_input.dart
│           └── typing_indicator.dart
```

### 1. Modelos

Ver archivo: `02_models_flutter.dart`

### 2. Service

Ver archivo: `03_service_flutter.dart`

### 3. Provider

Ver archivo: `04_provider_flutter.dart`

### 4. Screens

Ver archivo: `05_screens_flutter.dart`

### 5. Widgets

Ver archivo: `06_widgets_flutter.dart`

---

## 🧠 Integración con IA

### Opción 1: OpenAI GPT

Ver archivo: `07_openai_integration.py`

### Opción 2: Google Gemini

Ver archivo: `08_gemini_integration.py`

### Opción 3: Chatbot Local (Sin IA externa)

Ver archivo: `09_local_chatbot.py`

---

## 🎯 Funcionalidades del Chatbot

### 1. Consultas Generales
- Horarios de atención
- Ubicación de la clínica
- Servicios disponibles
- Precios de tratamientos

### 2. Gestión de Citas
- Consultar próximas citas
- Solicitar nueva cita
- Cancelar/reprogramar cita
- Ver historial de citas

### 3. Información Médica
- Consultar historial clínico
- Ver tratamientos activos
- Consultar facturas pendientes
- Recordatorios de medicación

### 4. Soporte
- Preguntas frecuentes (FAQ)
- Contacto con recepción
- Emergencias
- Quejas y sugerencias

---

## 🔐 Seguridad

### Backend
```python
# En views.py
class ChatBotView(APIView):
    permission_classes = [IsAuthenticated]  # Requiere JWT
    
    def post(self, request):
        # Validar que el usuario solo acceda a sus datos
        if request.user.tipo_usuario == 'PACIENTE':
            # Restringir acceso a datos del paciente
            pass
```

### Flutter
```dart
// En chatbot_service.dart
Future<ChatResponse> enviarMensaje(String mensaje) async {
  final token = await _authService.getToken();
  
  final response = await http.post(
    Uri.parse('$baseUrl/api/chatbot/chat/'),
    headers: {
      'Authorization': 'Bearer $token',
      'X-Tenant-ID': tenantId,
    },
    body: jsonEncode({'mensaje': mensaje}),
  );
  
  // ...
}
```

---

## 📊 Base de Datos

### Migraciones

```bash
python manage.py makemigrations chatbot
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant
```

### Poblar Intentos Iniciales

Ver archivo: `10_poblar_intentos.py`

---

## 🧪 Testing

### Backend Tests

Ver archivo: `11_tests_backend.py`

### Flutter Tests

Ver archivo: `12_tests_flutter.dart`

---

## 📦 Dependencias

### Backend (requirements.txt)
```txt
openai==1.3.0              # Para GPT
google-generativeai==0.3.0  # Para Gemini
langchain==0.1.0           # Opcional: para IA avanzada
```

### Flutter (pubspec.yaml)
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # HTTP
  http: ^1.1.0
  dio: ^5.4.0
  
  # State Management
  provider: ^6.1.1
  riverpod: ^2.4.9  # Alternativa
  
  # UI
  flutter_chat_ui: ^1.6.10
  bubble: ^1.2.1
  
  # Utilidades
  intl: ^0.18.1
  timeago: ^3.6.0
```

---

## 🚀 Despliegue

### Variables de Entorno (.env)

```env
# IA Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Chatbot Config
CHATBOT_MAX_HISTORY=50
CHATBOT_TIMEOUT=30
CHATBOT_MODEL=gpt-3.5-turbo
```

### Configuración en settings.py

```python
# Chatbot Configuration
CHATBOT_CONFIG = {
    'PROVIDER': env('CHATBOT_PROVIDER', default='local'),  # 'openai', 'gemini', 'local'
    'OPENAI_API_KEY': env('OPENAI_API_KEY', default=''),
    'GEMINI_API_KEY': env('GEMINI_API_KEY', default=''),
    'MODEL': env('CHATBOT_MODEL', default='gpt-3.5-turbo'),
    'MAX_HISTORY': int(env('CHATBOT_MAX_HISTORY', default=50)),
    'TIMEOUT': int(env('CHATBOT_TIMEOUT', default=30)),
    'TEMPERATURE': float(env('CHATBOT_TEMPERATURE', default=0.7)),
}
```

---

## 📱 Capturas de Pantalla Sugeridas

1. **Chat Principal**: Vista de conversación con mensajes
2. **Lista de Conversaciones**: Historial de chats
3. **Typing Indicator**: Indicador de escritura
4. **Sugerencias Rápidas**: Botones de respuesta rápida
5. **Perfil del Bot**: Información del asistente virtual

---

## 🎨 Personalización del UI

### Colores y Estilos

Ver archivo: `13_theme_flutter.dart`

---

## 📚 Referencias

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google Gemini Docs](https://ai.google.dev/docs)
- [Flutter Chat UI Package](https://pub.dev/packages/flutter_chat_ui)
- [Django Channels (WebSockets)](https://channels.readthedocs.io/)

---

## 🔄 Próximas Mejoras

- [ ] WebSockets para mensajes en tiempo real
- [ ] Reconocimiento de voz (Speech-to-Text)
- [ ] Texto a voz (Text-to-Speech)
- [ ] Soporte multiidioma
- [ ] Análisis de sentimientos
- [ ] Chatbot con avatar animado
- [ ] Integración con WhatsApp
- [ ] Notificaciones push para respuestas

---

## 👥 Contribuidores

- Backend: Django REST Framework + PostgreSQL
- Frontend: Flutter + Provider
- IA: OpenAI GPT / Google Gemini

---

## 📞 Soporte

Para dudas o problemas:
- Email: soporte@clinicadental.com
- Docs: `/docs/chatbot/`
