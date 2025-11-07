from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Cita
from .serializers import CitaSerializer, CitaListSerializer


class CitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar citas.
    
    Proporciona operaciones CRUD completas para citas, con filtrado automático
    basado en el rol del usuario autenticado:
    - Pacientes: solo ven sus propias citas
    - Odontólogos: solo ven sus citas asignadas
    - Staff/Admin: ven todas las citas
    
    Endpoints disponibles:
    - GET /api/agenda/citas/ - Lista todas las citas (filtradas por rol)
    - POST /api/agenda/citas/ - Crear nueva cita
    - GET /api/agenda/citas/{id}/ - Detalle de una cita
    - PUT/PATCH /api/agenda/citas/{id}/ - Actualizar cita
    - DELETE /api/agenda/citas/{id}/ - Eliminar cita
    - GET /api/agenda/citas/proximas/ - Citas futuras (custom action)
    - GET /api/agenda/citas/hoy/ - Citas de hoy (custom action)
    - POST /api/agenda/citas/{id}/confirmar/ - Confirmar cita
    - POST /api/agenda/citas/{id}/cancelar/ - Cancelar cita
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'list':
            return CitaListSerializer
        return CitaSerializer
    
    def get_queryset(self):
        """
        Retorna el queryset de citas filtrado según el tipo de usuario.
        El aislamiento por tenant es automático gracias a django-tenants.
        """
        user = self.request.user
        
        # Si es paciente, solo sus citas
        if hasattr(user, 'perfilpaciente'):
            return Cita.objects.filter(
                paciente=user.perfilpaciente
            ).select_related('paciente__usuario', 'odontologo__usuario')
        
        # Si es odontólogo, solo sus citas asignadas
        elif hasattr(user, 'perfilodontologo'):
            return Cita.objects.filter(
                odontologo=user.perfilodontologo
            ).select_related('paciente__usuario', 'odontologo__usuario')
        
        # Si es staff/admin, todas las citas
        elif user.is_staff:
            return Cita.objects.all().select_related(
                'paciente__usuario',
                'odontologo__usuario'
            )
        
        # Otros casos (no debería llegar aquí)
        return Cita.objects.none()
    
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """
        GET /api/agenda/citas/proximas/
        
        Retorna las citas futuras del usuario, ordenadas por fecha.
        Solo incluye citas con estado PENDIENTE o CONFIRMADA.
        """
        ahora = timezone.now()
        queryset = self.get_queryset().filter(
            fecha_hora__gte=ahora,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).order_by('fecha_hora')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hoy(self, request):
        """
        GET /api/agenda/citas/hoy/
        
        Retorna las citas de hoy del usuario.
        """
        hoy_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = hoy_inicio + timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            fecha_hora__gte=hoy_inicio,
            fecha_hora__lt=hoy_fin
        ).order_by('fecha_hora')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'fecha': hoy_inicio.date(),
            'total': queryset.count(),
            'citas': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """
        POST /api/agenda/citas/{id}/confirmar/
        
        Confirma una cita que está en estado PENDIENTE.
        """
        cita = self.get_object()
        
        if cita.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden confirmar citas pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cita.estado = 'CONFIRMADA'
        cita.save()
        
        serializer = self.get_serializer(cita)
        return Response({
            'message': 'Cita confirmada exitosamente.',
            'cita': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        POST /api/agenda/citas/{id}/cancelar/
        
        Cancela una cita (cualquier estado excepto ya CANCELADA).
        """
        cita = self.get_object()
        
        if cita.estado == 'CANCELADA':
            return Response(
                {'error': 'La cita ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cita.estado == 'ATENDIDA':
            return Response(
                {'error': 'No se puede cancelar una cita ya atendida.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cita.estado = 'CANCELADA'
        cita.save()
        
        serializer = self.get_serializer(cita)
        return Response({
            'message': 'Cita cancelada exitosamente.',
            'cita': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def atender(self, request, pk=None):
        """
        POST /api/agenda/citas/{id}/atender/
        
        Marca una cita como ATENDIDA.
        Solo odontólogos o staff pueden usar esta acción.
        """
        cita = self.get_object()
        user = request.user
        
        # Verificar que sea odontólogo o staff
        if not (hasattr(user, 'perfilodontologo') or user.is_staff):
            return Response(
                {'error': 'Solo odontólogos pueden marcar citas como atendidas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es odontólogo, verificar que sea SU cita
        if hasattr(user, 'perfilodontologo'):
            if cita.odontologo.id != user.perfilodontologo.id:
                return Response(
                    {'error': 'No puedes atender citas de otros odontólogos.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if cita.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return Response(
                {'error': 'Solo se pueden atender citas pendientes o confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cita.estado = 'ATENDIDA'
        cita.save()
        
        serializer = self.get_serializer(cita)
        return Response({
            'message': 'Cita marcada como atendida.',
            'cita': serializer.data
        })
