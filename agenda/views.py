from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from .models import Cita
from .serializers import CitaSerializer, CitaListSerializer
from tratamientos.models import ItemPlanTratamiento
from historial_clinico.models import EpisodioAtencion, HistorialClinico


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
        if hasattr(user, 'perfil_paciente'):
            return Cita.objects.filter(
                paciente=user.perfil_paciente
            ).select_related('paciente__usuario', 'odontologo__usuario')
        
        # Si es odontólogo, solo sus citas asignadas
        elif hasattr(user, 'perfil_odontologo'):
            return Cita.objects.filter(
                odontologo=user.perfil_odontologo
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
    
    @action(detail=False, methods=['post'])
    def agendar(self, request):
        """
        POST /api/agenda/citas/agendar/
        
        Agenda una nueva cita con validaciones inteligentes:
        - Si motivo_tipo='PLAN': requiere item_plan, verifica que esté disponible
        - Si motivo_tipo != 'PLAN': requiere pago previo (según lógica de negocio)
        
        Body esperado:
        {
            "odontologo": <id>,
            "fecha_hora": "2025-11-15T10:00:00",
            "motivo_tipo": "CONSULTA" | "URGENCIA" | "LIMPIEZA" | "REVISION" | "PLAN",
            "motivo": "Descripción del motivo",
            "item_plan": <id> (solo si motivo_tipo='PLAN'),
            "observaciones": "Opcional"
        }
        """
        user = request.user
        
        # Solo pacientes pueden agendar sus propias citas
        if not hasattr(user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo pacientes pueden agendar citas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Agregar automáticamente el paciente
        data = request.data.copy()
        data['paciente'] = user.perfil_paciente.pk
        
        # Validar y crear la cita
        serializer = CitaSerializer(data=data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear la cita
        cita = serializer.save()
        
        response_data = {
            'message': 'Cita agendada exitosamente.',
            'cita': CitaSerializer(cita, context={'request': request}).data
        }
        
        # Agregar información de pago si requiere
        if cita.requiere_pago:
            response_data['requiere_pago'] = True
            response_data['monto_a_pagar'] = str(cita.precio)
            response_data['mensaje_pago'] = f'Esta cita requiere un pago de {cita.precio_display}. Proceda con el pago para confirmar la cita.'
        else:
            response_data['requiere_pago'] = False
            if cita.es_cita_plan:
                response_data['mensaje'] = 'Cita de tratamiento agendada. Este servicio está incluido en su plan.'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def atender(self, request, pk=None):
        """
        POST /api/agenda/citas/{id}/atender/
        
        Marca una cita como ATENDIDA y ejecuta lógica adicional:
        - Si es_cita_plan=True: marca el item_plan como completado
        - Crea un episodio en el historial clínico
        - Solo odontólogos o staff pueden usar esta acción
        
        Body opcional:
        {
            "marcar_item_completado": true/false (default: true si es cita de plan),
            "notas_atencion": "Notas de la atención"
        }
        """
        cita = self.get_object()
        user = request.user
        
        # Verificar que sea odontólogo o staff
        if not (hasattr(user, 'perfil_odontologo') or user.is_staff):
            return Response(
                {'error': 'Solo odontólogos pueden marcar citas como atendidas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es odontólogo, verificar que sea SU cita
        if hasattr(user, 'perfil_odontologo'):
            if cita.odontologo.pk != user.perfil_odontologo.pk:
                return Response(
                    {'error': 'No puedes atender citas de otros odontólogos.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if cita.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return Response(
                {'error': 'Solo se pueden atender citas pendientes o confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener parámetros del request
        marcar_completado = request.data.get('marcar_item_completado', True)
        notas_atencion = request.data.get('notas_atencion', '')
        
        with transaction.atomic():
            # Marcar cita como atendida
            cita.estado = 'ATENDIDA'
            cita.save()
            
            # Si es cita de plan, marcar ítem como completado
            item_completado = None
            if cita.es_cita_plan and marcar_completado and cita.item_plan:
                if cita.item_plan.estado != 'COMPLETADO':
                    cita.item_plan.estado = 'COMPLETADO'
                    from django.utils import timezone
                    cita.item_plan.fecha_realizada = timezone.now()
                    cita.item_plan.save()
                    item_completado = cita.item_plan
            
            # Obtener o crear historial clínico del paciente
            historial, created = HistorialClinico.objects.get_or_create(
                paciente=cita.paciente
            )
            
            # Preparar descripción del procedimiento
            descripcion_proc = cita.get_motivo_tipo_display()
            if item_completado:
                servicio_nombre = getattr(item_completado.servicio, 'nombre', 'Servicio') if item_completado.servicio else 'Servicio'
                descripcion_proc += f" - {servicio_nombre}"
            
            # Crear episodio en historial clínico
            episodio = EpisodioAtencion.objects.create(
                historial_clinico=historial,
                odontologo=cita.odontologo,
                motivo_consulta=cita.motivo,
                diagnostico=notas_atencion or f"Atención de cita: {cita.get_motivo_tipo_display()}",
                descripcion_procedimiento=descripcion_proc,
                notas_privadas=f"Cita ID: {cita.id}\n{cita.observaciones or ''}",
                item_plan_tratamiento=cita.item_plan if cita.es_cita_plan else None
            )
        
        serializer = self.get_serializer(cita)
        response_data = {
            'message': 'Cita atendida exitosamente.',
            'cita': serializer.data,
            'episodio_id': episodio.id
        }
        
        if item_completado:
            servicio_nombre = getattr(item_completado.servicio, 'nombre', 'Servicio') if item_completado.servicio else 'Servicio'
            response_data['item_plan_completado'] = {
                'id': item_completado.id,
                'servicio': servicio_nombre,
                'mensaje': f'Tratamiento "{servicio_nombre}" marcado como completado.'
            }
        
        return Response(response_data)
