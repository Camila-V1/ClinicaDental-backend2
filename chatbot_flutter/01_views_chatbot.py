# chatbot/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from .models import Conversacion, Mensaje, IntentoChatbot
from .serializers import (
    ConversacionSerializer, 
    ConversacionListSerializer,
    MensajeSerializer,
    ChatRequestSerializer
)
from .ia_service import ChatbotService

logger = logging.getLogger(__name__)


class ChatBotView(APIView):
    """
    Vista principal del chatbot.
    
    POST /api/chatbot/chat/
    {
        "mensaje": "¿Cuáles son los horarios de atención?",
        "conversacion_id": 1,  // Opcional
        "contexto": {}  // Opcional
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        mensaje_texto = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        contexto = serializer.validated_data.get('contexto', {})
        
        try:
            # Obtener o crear conversación
            if conversacion_id:
                conversacion = Conversacion.objects.get(
                    id=conversacion_id, 
                    usuario=request.user
                )
            else:
                # Crear nueva conversación
                conversacion = Conversacion.objects.create(
                    usuario=request.user,
                    titulo=mensaje_texto[:50] + '...' if len(mensaje_texto) > 50 else mensaje_texto
                )
            
            # Guardar mensaje del usuario
            mensaje_usuario = Mensaje.objects.create(
                conversacion=conversacion,
                role='user',
                content=mensaje_texto,
                metadata=contexto
            )
            
            # Obtener historial de la conversación
            historial = conversacion.mensajes.order_by('timestamp')[:50]
            historial_formateado = [
                {'role': msg.role, 'content': msg.content}
                for msg in historial
            ]
            
            # Generar respuesta del chatbot
            chatbot_service = ChatbotService()
            respuesta_bot = chatbot_service.generar_respuesta(
                mensaje_usuario=mensaje_texto,
                historial=historial_formateado,
                usuario=request.user,
                contexto=contexto
            )
            
            # Guardar respuesta del bot
            mensaje_bot = Mensaje.objects.create(
                conversacion=conversacion,
                role='assistant',
                content=respuesta_bot['mensaje'],
                metadata=respuesta_bot.get('metadata', {})
            )
            
            # Actualizar timestamp de la conversación
            conversacion.updated_at = timezone.now()
            conversacion.save()
            
            logger.info(
                f"✅ Mensaje procesado en conversación {conversacion.id} "
                f"para usuario {request.user.email}"
            )
            
            return Response({
                'conversacion_id': conversacion.id,
                'mensaje_usuario': MensajeSerializer(mensaje_usuario).data,
                'mensaje_bot': MensajeSerializer(mensaje_bot).data,
                'metadata': respuesta_bot.get('metadata', {})
            }, status=status.HTTP_200_OK)
        
        except Conversacion.DoesNotExist:
            return Response(
                {'error': 'Conversación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"❌ Error en chatbot: {str(e)}")
            return Response(
                {'error': f'Error al procesar mensaje: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversacionListView(ListAPIView):
    """
    Lista todas las conversaciones del usuario autenticado.
    
    GET /api/chatbot/conversaciones/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConversacionListSerializer
    
    def get_queryset(self):
        return Conversacion.objects.filter(
            usuario=self.request.user,
            is_active=True
        ).order_by('-updated_at')


class ConversacionDetailView(RetrieveAPIView):
    """
    Obtiene el detalle completo de una conversación con todos sus mensajes.
    
    GET /api/chatbot/conversaciones/{id}/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConversacionSerializer
    
    def get_queryset(self):
        return Conversacion.objects.filter(usuario=self.request.user)


class IntentosDisponiblesView(APIView):
    """
    Lista los intentos/capacidades disponibles del chatbot.
    
    GET /api/chatbot/intentos/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        intentos = IntentoChatbot.objects.filter(is_active=True)
        
        # Filtrar según tipo de usuario
        if request.user.tipo_usuario == 'PACIENTE':
            # Solo intentos que no requieren autenticación especial
            pass
        elif request.user.tipo_usuario == 'ODONTOLOGO':
            # Intentos adicionales para odontólogos
            pass
        
        data = [
            {
                'nombre': intento.nombre,
                'descripcion': intento.descripcion,
                'ejemplos': intento.ejemplos[:3]  # Primeros 3 ejemplos
            }
            for intento in intentos
        ]
        
        return Response(data, status=status.HTTP_200_OK)
