# Guía de Instalación del Chatbot

## 🚀 Instalación Rápida

### 1. Configurar Backend (Django)

```bash
# Navegar al proyecto
cd ClinicaDental-backend2

# Crear la app chatbot
python manage.py startapp chatbot

# Copiar archivos
# - Copiar models.py, views.py, serializers.py, urls.py desde chatbot_flutter/
# - Copiar ia_service.py desde 07_openai_integration.py

# Instalar dependencias
pip install openai==1.3.0
pip install google-generativeai==0.3.0  # Si usas Gemini

# Agregar a settings.py
TENANT_APPS = [
    # ... otras apps
    'chatbot',
]

# Agregar configuración de chatbot en settings.py
CHATBOT_CONFIG = {
    'PROVIDER': 'openai',  # 'openai', 'gemini', 'local'
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
    'MODEL': 'gpt-3.5-turbo',
    'MAX_HISTORY': 50,
    'TEMPERATURE': 0.7,
}

# Agregar URL en core/urls_tenant.py
path('api/chatbot/', include('chatbot.urls')),

# Crear migraciones
python manage.py makemigrations chatbot
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# Poblar intentos iniciales (opcional)
python manage.py shell
>>> from chatbot.models import IntentoChatbot
>>> IntentoChatbot.objects.create(
...     nombre="consultar_horarios",
...     descripcion="Consultar horarios de atención",
...     ejemplos=["¿Cuáles son los horarios?", "¿A qué hora abren?"],
...     respuesta_template="Nuestros horarios son: Lunes a Viernes 8AM-8PM...",
...     is_active=True
... )
```

### 2. Configurar Flutter

```bash
# Crear carpetas
lib/features/chatbot/
├── models/
├── services/
├── providers/
├── screens/
└── widgets/

# Agregar dependencias en pubspec.yaml
dependencies:
  http: ^1.1.0
  provider: ^6.1.1
  timeago: ^3.6.0
  intl: ^0.18.1

# Instalar
flutter pub get

# Copiar archivos desde chatbot_flutter/
# - 02_models_flutter.dart → models/
# - 03_service_flutter.dart → services/
# - 04_provider_flutter.dart → providers/
# - 05_screens_flutter.dart → screens/
# - 06_widgets_flutter.dart → widgets/

# Registrar provider en main.dart
import 'package:provider/provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => ChatbotProvider(
            ChatbotService(
              baseUrl: 'https://tu-backend.onrender.com',
              tenantId: 'clinica_demo',
              getToken: () async {
                // Obtener token de AuthService
                return await AuthService().getToken();
              },
            ),
          ),
        ),
      ],
      child: MyApp(),
    ),
  );
}
```

### 3. Variables de Entorno

```env
# .env (Backend)
OPENAI_API_KEY=sk-proj-xxx
GEMINI_API_KEY=xxx
CHATBOT_PROVIDER=openai
CHATBOT_MODEL=gpt-3.5-turbo
```

### 4. Agregar Ruta en Flutter

```dart
// En tu archivo de rutas
import 'package:flutter/material.dart';
import 'features/chatbot/screens/chat_screen.dart';

// Agregar ruta
MaterialPageRoute(
  builder: (_) => ChatScreen(),
)

// O en tu bottom navigation
BottomNavigationBarItem(
  icon: Icon(Icons.chat),
  label: 'Chatbot',
),
```

---

## 🔒 Configurar API Key de OpenAI

### Opción 1: OpenAI GPT (Recomendado)

1. Crear cuenta en https://platform.openai.com
2. Ir a API Keys: https://platform.openai.com/api-keys
3. Crear nueva key
4. Copiar y guardar en `.env`:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxx
```

5. Configurar límites de uso (recomendado $5-10/mes)

### Opción 2: Google Gemini (Gratis)

1. Ir a https://makersuite.google.com/app/apikey
2. Crear API key
3. Guardar en `.env`:

```env
GEMINI_API_KEY=xxxxxxxxxxxxx
CHATBOT_PROVIDER=gemini
```

### Opción 3: Chatbot Local (Sin IA externa)

```python
# En settings.py
CHATBOT_CONFIG = {
    'PROVIDER': 'local',  # No requiere API keys
}
```

---

## 📊 Poblar Base de Datos

```python
# scripts_poblacion/poblar_chatbot.py

from chatbot.models import IntentoChatbot

def poblar_intentos():
    """Poblar intentos iniciales del chatbot."""
    
    intentos = [
        {
            'nombre': 'consultar_horarios',
            'descripcion': 'Consultar horarios de atención de la clínica',
            'ejemplos': [
                '¿Cuáles son los horarios?',
                '¿A qué hora abren?',
                '¿Están abiertos el domingo?',
                'Horario de atención'
            ],
            'respuesta_template': """🕐 Nuestros horarios de atención son:

📅 Lunes a Viernes: 8:00 AM - 8:00 PM
📅 Sábados: 9:00 AM - 2:00 PM
📅 Domingos: Cerrado

¿Te gustaría agendar una cita?""",
            'requiere_autenticacion': False
        },
        {
            'nombre': 'consultar_precios',
            'descripcion': 'Consultar precios de tratamientos',
            'ejemplos': [
                '¿Cuánto cuesta?',
                'Precios',
                '¿Cuál es el precio de una limpieza?',
                'Valores de tratamientos'
            ],
            'respuesta_template': """💰 Estos son algunos de nuestros precios:

• Limpieza dental: $30-50
• Obturación: $40-80
• Extracción: $50-100
• Ortodoncia: desde $800
• Implantes: desde $1200

Los precios pueden variar según complejidad. ¿Sobre qué tratamiento te gustaría más información?""",
            'requiere_autenticacion': False
        },
        {
            'nombre': 'agendar_cita',
            'descripcion': 'Información para agendar citas',
            'ejemplos': [
                'Quiero agendar una cita',
                'Reservar hora',
                'Necesito una consulta',
                'Pedir cita'
            ],
            'respuesta_template': """📅 ¡Excelente! Para agendar tu cita puedes:

1️⃣ Usar la sección "Mis Citas" en la app
2️⃣ Llamarnos al: (123) 456-7890
3️⃣ Visitar nuestra clínica

¿Prefieres que te ayude con algo más?""",
            'requiere_autenticacion': True
        },
        {
            'nombre': 'consultar_citas',
            'descripcion': 'Ver próximas citas del paciente',
            'ejemplos': [
                'Mis citas',
                'Próximas citas',
                '¿Cuándo es mi cita?',
                'Ver mis reservas'
            ],
            'respuesta_template': """📋 Para ver tus citas:

Ve a la sección "Mis Citas" en el menú principal.

Allí podrás ver:
• Próximas citas
• Historial de citas
• Cancelar o reprogramar

¿Necesitas ayuda con algo más?""",
            'requiere_autenticacion': True
        },
        {
            'nombre': 'ubicacion',
            'descripcion': 'Ubicación de la clínica',
            'ejemplos': [
                '¿Dónde están ubicados?',
                'Dirección',
                '¿Cómo llego?',
                'Ubicación de la clínica'
            ],
            'respuesta_template': """📍 Estamos ubicados en:

🏥 Calle Principal #123
Edificio Medical Center, Piso 2
Ciudad, País

🚗 Estacionamiento disponible
🚇 Metro: Estación Central (línea azul)

¿Necesitas indicaciones más específicas?""",
            'requiere_autenticacion': False
        },
        {
            'nombre': 'emergencias',
            'descripcion': 'Información para emergencias dentales',
            'ejemplos': [
                'Tengo una emergencia',
                'Dolor de muelas urgente',
                'Necesito atención urgente',
                'Emergencia dental'
            ],
            'respuesta_template': """🚨 EMERGENCIA DENTAL

Para atención de emergencias:

📞 Llama inmediatamente al: (123) 456-7890
📱 WhatsApp: +1-234-567-890

Si es fuera de horario:
🏥 Hospital Central: (123) 999-9999

Síntomas graves (ir a urgencias):
• Sangrado incontrolable
• Inflamación severa
• Fractura de mandíbula
• Trauma facial

¿Puedo ayudarte con algo más?""",
            'requiere_autenticacion': False
        },
    ]
    
    for intento_data in intentos:
        IntentoChatbot.objects.get_or_create(
            nombre=intento_data['nombre'],
            defaults=intento_data
        )
    
    print(f"✅ {len(intentos)} intentos creados")

if __name__ == '__main__':
    poblar_intentos()
```

Ejecutar:

```bash
python manage.py shell < scripts_poblacion/poblar_chatbot.py
```

---

## ✅ Verificar Instalación

### Backend:

```bash
# Iniciar servidor
python manage.py runserver

# Probar endpoints
curl -H "Authorization: Bearer TOKEN" \
     -H "X-Tenant-ID: clinica_demo" \
     http://localhost:8000/api/chatbot/intentos/
```

### Flutter:

```bash
# Ejecutar app
flutter run

# O generar APK
flutter build apk
```

---

## 🧪 Probar el Chatbot

1. **Abrir la app Flutter**
2. **Login** con un usuario (admin@clinicademo1.com / admin123)
3. **Ir a la sección de Chatbot**
4. **Enviar mensaje**: "Hola"
5. **Verificar respuesta** del bot

Mensajes de prueba:
- "¿Cuáles son los horarios?"
- "Quiero agendar una cita"
- "¿Cuánto cuesta una limpieza?"
- "Ver mis próximas citas"

---

## 🐛 Solución de Problemas

### Error: "Token not valid"
- Verificar que el token JWT esté vigente
- Revisar configuración de `X-Tenant-ID`

### Error: "OPENAI_API_KEY not set"
- Verificar `.env` tiene la key correcta
- Reiniciar servidor Django

### Error: "Conversation not found"
- Verificar que el usuario tenga acceso a esa conversación
- Revisar permisos en el backend

### Bot no responde
- Verificar logs de Django: `python manage.py runserver`
- Revisar que el servicio de IA esté configurado
- Probar con modo `local` primero

---

## 📚 Próximos Pasos

1. Personalizar respuestas del bot
2. Agregar más intentos predefinidos
3. Implementar WebSockets para tiempo real
4. Agregar reconocimiento de voz
5. Integrar con WhatsApp

---

¡Listo! El chatbot debería estar funcionando. 🎉
