"""
Servicio para enviar notificaciones push usando Firebase Cloud Messaging (FCM)
"""
import json
import logging
from pathlib import Path
from django.conf import settings
from firebase_admin import credentials, messaging, initialize_app

logger = logging.getLogger(__name__)

# Inicializar Firebase Admin SDK
try:
    # Buscar el archivo de credenciales
    firebase_cred_path = Path(settings.BASE_DIR) / 'psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json'
    
    if firebase_cred_path.exists():
        cred = credentials.Certificate(str(firebase_cred_path))
        initialize_app(cred)
        logger.info("✅ Firebase Admin SDK inicializado correctamente")
    else:
        logger.warning(f"⚠️ Archivo de credenciales Firebase no encontrado: {firebase_cred_path}")
except Exception as e:
    logger.error(f"❌ Error al inicializar Firebase Admin SDK: {e}")


class FirebaseNotificationService:
    """Servicio para enviar notificaciones push vía Firebase"""
    
    @staticmethod
    def enviar_notificacion_valoracion(device_token: str, cita_id: int, odontologo_nombre: str):
        """
        Envía notificación push al paciente para que valore la atención recibida
        
        Args:
            device_token: Token FCM del dispositivo del paciente
            cita_id: ID de la cita completada
            odontologo_nombre: Nombre del odontólogo que atendió
        
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Crear el mensaje de notificación
            message = messaging.Message(
                notification=messaging.Notification(
                    title='¿Cómo fue tu atención? 🦷',
                    body=f'Valora la atención del Dr. {odontologo_nombre}. ¡Tu opinión es importante!'
                ),
                data={
                    'tipo': 'solicitud_valoracion',
                    'cita_id': str(cita_id),
                    'odontologo': odontologo_nombre,
                    'click_action': 'VALORAR_CITA'
                },
                token=device_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default',
                        click_action='VALORAR_CITA'
                    )
                )
            )
            
            # Enviar el mensaje
            response = messaging.send(message)
            logger.info(f"✅ Notificación enviada exitosamente. Response ID: {response}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al enviar notificación push: {e}")
            return False
    
    @staticmethod
    def enviar_notificacion_masiva(device_tokens: list, titulo: str, mensaje: str, data: dict = None):
        """
        Envía notificación push a múltiples dispositivos
        
        Args:
            device_tokens: Lista de tokens FCM
            titulo: Título de la notificación
            mensaje: Cuerpo de la notificación
            data: Datos adicionales (opcional)
        
        Returns:
            dict: Resultado con éxitos y fallos
        """
        try:
            # Crear el mensaje multicast
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=titulo,
                    body=mensaje
                ),
                data=data or {},
                tokens=device_tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                )
            )
            
            # Enviar el mensaje
            response = messaging.send_multicast(message)
            
            logger.info(
                f"✅ Notificación masiva enviada. "
                f"Éxitos: {response.success_count}, Fallos: {response.failure_count}"
            )
            
            return {
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'responses': response.responses
            }
            
        except Exception as e:
            logger.error(f"❌ Error al enviar notificación masiva: {e}")
            return {
                'success_count': 0,
                'failure_count': len(device_tokens),
                'error': str(e)
            }
    
    @staticmethod
    def verificar_token(device_token: str):
        """
        Verifica si un token FCM es válido
        
        Args:
            device_token: Token FCM a verificar
        
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            # Intentar enviar un mensaje de prueba (dry run)
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Test',
                    body='Test'
                ),
                token=device_token
            )
            
            messaging.send(message, dry_run=True)
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Token FCM inválido: {e}")
            return False
