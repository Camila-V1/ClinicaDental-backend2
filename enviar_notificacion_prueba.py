import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from valoraciones.firebase_service import FirebaseNotificationService
from tenants.models import Clinica
from django_tenants.utils import schema_context
import django.utils.timezone
from firebase_admin import messaging

Usuario = get_user_model()

print("\n" + "="*80)
print("🔔 ENVIAR NOTIFICACIÓN DE PRUEBA")
print("="*80)

# Obtener clínica
try:
    clinica = Clinica.objects.get(schema_name="clinica_demo")
    print(f"\n✅ Clínica: {clinica.nombre}")
except Clinica.DoesNotExist:
    print("❌ Clínica no encontrada")
    exit()

# Usar el contexto del schema
with schema_context(clinica.schema_name):
    # Buscar usuario paciente1@test.com
    try:
        usuario = Usuario.objects.get(email="paciente1@test.com")
        print(f"✅ Usuario encontrado: {usuario.nombre} {usuario.apellido}")
        print(f"📧 Email: {usuario.email}")
        print(f"🔑 FCM Token: {usuario.fcm_token[:50] if usuario.fcm_token else 'No disponible'}...")
        
        if not usuario.fcm_token:
            print("\n❌ El usuario no tiene FCM token registrado")
            exit()
        
        # Enviar notificación
        print("\n📤 Enviando notificación de prueba...")
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="🦷 Prueba de Notificación",
                    body="¡Hola María! Esta es una notificación de prueba desde tu clínica dental. El sistema de notificaciones está funcionando correctamente. 🎉"
                ),
                data={
                    'tipo': 'PRUEBA',
                    'usuario_id': str(usuario.id),
                    'timestamp': str(django.utils.timezone.now()),
                    'clinica': clinica.nombre,
                },
                token=usuario.fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                )
            )
            
            response = messaging.send(message)
            resultado = {'success': True, 'message_id': response}
        except Exception as e:
            resultado = {'success': False, 'error': str(e)}
        
        print(f"\n{'='*60}")
        if resultado.get('success'):
            print("✅ NOTIFICACIÓN ENVIADA EXITOSAMENTE")
            print(f"📨 Message ID: {resultado.get('message_id')}")
            print(f"📱 Token: {usuario.fcm_token[:50]}...")
            print(f"📋 Título: 🦷 Prueba de Notificación")
            print(f"📝 Cuerpo: ¡Hola María! Esta es una notificación...")
        else:
            print("❌ ERROR AL ENVIAR NOTIFICACIÓN")
            print(f"Error: {resultado.get('error')}")
        print(f"{'='*60}")
        
        # Enviar otra notificación más específica
        print("\n📤 Enviando notificación de cita recordatorio...")
        
        try:
            message2 = messaging.Message(
                notification=messaging.Notification(
                    title="📅 Recordatorio de Cita",
                    body="Tienes una cita programada para mañana a las 9:30 AM con el Dr. Carlos Rodríguez. ¡No olvides confirmarla!"
                ),
                data={
                    'tipo': 'CITA_RECORDATORIO',
                    'cita_id': '1953',
                    'usuario_id': str(usuario.id),
                    'clinica': clinica.nombre,
                },
                token=usuario.fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                )
            )
            
            response2 = messaging.send(message2)
            resultado2 = {'success': True, 'message_id': response2}
        except Exception as e:
            resultado2 = {'success': False, 'error': str(e)}
        
        print(f"\n{'='*60}")
        if resultado2.get('success'):
            print("✅ NOTIFICACIÓN DE CITA ENVIADA")
            print(f"📨 Message ID: {resultado2.get('message_id')}")
        else:
            print("❌ ERROR AL ENVIAR NOTIFICACIÓN DE CITA")
            print(f"Error: {resultado2.get('error')}")
        print(f"{'='*60}")
        
        # Enviar notificación de valoración
        print("\n📤 Enviando notificación de valoración pendiente...")
        
        try:
            message3 = messaging.Message(
                notification=messaging.Notification(
                    title="⭐ Valora tu Atención",
                    body="¿Cómo estuvo tu última consulta con el Dr. Carlos? Tu opinión es importante para nosotros. ¡Califica tu experiencia!"
                ),
                data={
                    'tipo': 'VALORACION_PENDIENTE',
                    'cita_id': '1945',
                    'usuario_id': str(usuario.id),
                    'clinica': clinica.nombre,
                },
                token=usuario.fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                )
            )
            
            response3 = messaging.send(message3)
            resultado3 = {'success': True, 'message_id': response3}
        except Exception as e:
            resultado3 = {'success': False, 'error': str(e)}
        
        print(f"\n{'='*60}")
        if resultado3.get('success'):
            print("✅ NOTIFICACIÓN DE VALORACIÓN ENVIADA")
            print(f"📨 Message ID: {resultado3.get('message_id')}")
        else:
            print("❌ ERROR AL ENVIAR NOTIFICACIÓN DE VALORACIÓN")
            print(f"Error: {resultado3.get('error')}")
        print(f"{'='*60}")
        
    except Usuario.DoesNotExist:
        print("❌ Usuario no encontrado")

print("\n" + "="*80)
print("🎯 Verifica tu celular - Deberías recibir 3 notificaciones:")
print("   1. 🦷 Prueba de Notificación")
print("   2. 📅 Recordatorio de Cita")
print("   3. ⭐ Valora tu Atención")
print("="*80)
