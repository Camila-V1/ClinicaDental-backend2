from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from .models import Valoracion
from .serializers import (
    ValoracionSerializer,
    ValoracionCreateSerializer,
    ValoracionResumenSerializer,
    EstadisticasOdontologoSerializer
)
from agenda.models import Cita
import logging

logger = logging.getLogger(__name__)


class ValoracionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar valoraciones de pacientes
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ValoracionCreateSerializer
        elif self.action == 'resumen':
            return ValoracionResumenSerializer
        return ValoracionSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Si es paciente, ver solo sus valoraciones
        if user.tipo_usuario == 'PACIENTE':
            return Valoracion.objects.filter(paciente=user)
        
        # Si es odontólogo, ver valoraciones recibidas
        elif user.tipo_usuario == 'ODONTOLOGO':
            return Valoracion.objects.filter(odontologo=user)
        
        # Si es admin, ver todas
        elif user.tipo_usuario == 'ADMIN':
            return Valoracion.objects.all()
        
        return Valoracion.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva valoración"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info(
            f"✅ Valoración creada por {request.user.email} "
            f"con calificación {serializer.data.get('calificacion')}⭐"
        )
        
        return Response(
            ValoracionSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def mis_valoraciones(self, request):
        """Obtener las valoraciones realizadas por el paciente actual"""
        if request.user.tipo_usuario != 'PACIENTE':
            return Response(
                {'error': 'Solo los pacientes pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        valoraciones = Valoracion.objects.filter(paciente=request.user)
        serializer = ValoracionResumenSerializer(valoraciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_estadisticas(self, request):
        """Obtener estadísticas de valoraciones del odontólogo actual"""
        if request.user.tipo_usuario != 'ODONTOLOGO':
            return Response(
                {'error': 'Solo los odontólogos pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        valoraciones = Valoracion.objects.filter(odontologo=request.user)
        
        if not valoraciones.exists():
            return Response({
                'odontologo_id': request.user.id,
                'odontologo_nombre': request.user.nombre_completo,
                'total_valoraciones': 0,
                'calificacion_promedio': 0,
                'mensaje': 'Aún no tienes valoraciones'
            })
        
        # Calcular estadísticas
        stats = valoraciones.aggregate(
            total=Count('id'),
            promedio=Avg('calificacion'),
            puntualidad_avg=Avg('puntualidad'),
            trato_avg=Avg('trato'),
            limpieza_avg=Avg('limpieza')
        )
        
        # Contar valoraciones por estrella
        valoraciones_por_estrella = {
            '5': valoraciones.filter(calificacion=5).count(),
            '4': valoraciones.filter(calificacion=4).count(),
            '3': valoraciones.filter(calificacion=3).count(),
            '2': valoraciones.filter(calificacion=2).count(),
            '1': valoraciones.filter(calificacion=1).count(),
        }
        
        data = {
            'odontologo_id': request.user.id,
            'odontologo_nombre': request.user.nombre_completo,
            'total_valoraciones': stats['total'],
            'calificacion_promedio': round(stats['promedio'], 2) if stats['promedio'] else 0,
            'puntualidad_promedio': round(stats['puntualidad_avg'], 2) if stats['puntualidad_avg'] else None,
            'trato_promedio': round(stats['trato_avg'], 2) if stats['trato_avg'] else None,
            'limpieza_promedio': round(stats['limpieza_avg'], 2) if stats['limpieza_avg'] else None,
            'valoraciones_por_estrella': valoraciones_por_estrella
        }
        
        serializer = EstadisticasOdontologoSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def citas_pendientes_valoracion(self, request):
        """Obtener citas completadas que aún no han sido valoradas"""
        if request.user.tipo_usuario != 'PACIENTE':
            return Response(
                {'error': 'Solo los pacientes pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el perfil del paciente
        from usuarios.models import PerfilPaciente
        try:
            perfil_paciente = PerfilPaciente.objects.get(usuario=request.user)
        except PerfilPaciente.DoesNotExist:
            return Response({
                'count': 0,
                'citas': [],
                'mensaje': 'No se encontró perfil de paciente'
            })
        
        # Buscar citas completadas sin valoración
        citas_pendientes = Cita.objects.filter(
            paciente=perfil_paciente,
            estado='COMPLETADA'
        ).exclude(
            id__in=Valoracion.objects.filter(
                paciente=request.user
            ).values_list('cita_id', flat=True)
        ).select_related('odontologo')
        
        from agenda.serializers import CitaSerializer
        serializer = CitaSerializer(citas_pendientes, many=True)
        
        return Response({
            'count': citas_pendientes.count(),
            'citas': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def ranking_odontologos(self, request):
        """Obtener ranking de odontólogos por calificación"""
        if request.user.tipo_usuario != 'ADMIN':
            return Response(
                {'error': 'Solo los administradores pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from usuarios.models import Usuario
        from django.db.models import Avg, Count
        
        odontologos = Usuario.objects.filter(
            tipo_usuario='ODONTOLOGO'
        ).annotate(
            total_valoraciones=Count('valoraciones_recibidas'),
            calificacion_promedio=Avg('valoraciones_recibidas__calificacion')
        ).filter(
            total_valoraciones__gt=0
        ).order_by('-calificacion_promedio')
        
        resultado = []
        for odontologo in odontologos:
            resultado.append({
                'odontologo_id': odontologo.id,
                'odontologo_nombre': odontologo.nombre_completo,
                'total_valoraciones': odontologo.total_valoraciones,
                'calificacion_promedio': round(odontologo.calificacion_promedio, 2)
            })
        
        return Response(resultado)
    
    @action(detail=False, methods=['post'], url_path='enviar-notificacion-prueba')
    def enviar_notificacion_prueba(self, request):
        """
        Endpoint para enviar notificación de prueba al usuario actual
        """
        try:
            usuario = request.user
            
            if not usuario.fcm_token:
                return Response({
                    'error': 'Usuario no tiene token FCM registrado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Importar el servicio de Firebase
            from firebase_admin import messaging
            
            # Crear mensaje
            message = messaging.Message(
                notification=messaging.Notification(
                    title=request.data.get('titulo', '🦷 Prueba de Notificación'),
                    body=request.data.get('mensaje', '¡Hola! Esta es una notificación de prueba.')
                ),
                data=request.data.get('data', {
                    'tipo': 'PRUEBA',
                    'usuario_id': str(usuario.id)
                }),
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
            
            # Enviar notificación
            response = messaging.send(message)
            
            logger.info(f"✅ Notificación de prueba enviada a {usuario.email}. Message ID: {response}")
            
            return Response({
                'success': True,
                'message': 'Notificación enviada exitosamente',
                'message_id': response,
                'usuario': usuario.email,
                'fcm_token': usuario.fcm_token[:50] + '...'
            })
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación de prueba: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
