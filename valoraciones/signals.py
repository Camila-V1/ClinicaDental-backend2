"""
Signals para enviar notificaciones cuando una cita se completa
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from agenda.models import Cita
from .models import Valoracion
from .firebase_service import FirebaseNotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Cita)
def enviar_notificacion_valoracion_cita_completada(sender, instance, created, **kwargs):
    """
    Señal que detecta cuando una cita cambia a estado COMPLETADA
    y envía notificación push al paciente para que valore la atención
    """
    
    # Solo procesar si la cita acaba de cambiar a COMPLETADA
    if instance.estado == 'COMPLETADA':
        
        # Verificar que no se haya enviado notificación antes
        # y que no exista ya una valoración
        if not hasattr(instance, 'valoracion'):
            
            # Obtener el token FCM del paciente
            paciente = instance.paciente
            
            # Verificar que el paciente tenga token FCM registrado
            if hasattr(paciente, 'fcm_token') and paciente.fcm_token:
                
                logger.info(
                    f"📲 Enviando notificación de valoración a {paciente.email} "
                    f"por cita con {instance.odontologo.full_name}"
                )
                
                # Enviar notificación
                exito = FirebaseNotificationService.enviar_notificacion_valoracion(
                    device_token=paciente.fcm_token,
                    cita_id=instance.id,
                    odontologo_nombre=instance.odontologo.full_name
                )
                
                if exito:
                    logger.info(f"✅ Notificación enviada exitosamente a {paciente.email}")
                else:
                    logger.error(f"❌ Fallo al enviar notificación a {paciente.email}")
                    
            else:
                logger.warning(
                    f"⚠️ Paciente {paciente.email} no tiene token FCM registrado. "
                    "No se puede enviar notificación push."
                )
