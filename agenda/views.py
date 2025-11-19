from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime, time
from .models import Cita
from .serializers import CitaSerializer, CitaListSerializer
from tratamientos.models import ItemPlanTratamiento
from historial_clinico.models import EpisodioAtencion, HistorialClinico
from usuarios.models import PerfilOdontologo


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
        
        # Obtener parámetros del request (opcional)
        marcar_completado = request.data.get('marcar_item_completado', True)
        
        with transaction.atomic():
            # Marcar cita como atendida
            cita.estado = 'ATENDIDA'
            cita.save()
            
            # Si es cita de plan, opcionalmente marcar ítem como completado
            item_completado = None
            if cita.es_cita_plan and marcar_completado and cita.item_plan:
                if cita.item_plan.estado != 'COMPLETADO':
                    cita.item_plan.estado = 'COMPLETADO'
                    from django.utils import timezone
                    cita.item_plan.fecha_realizada = timezone.now()
                    cita.item_plan.save()
                    item_completado = cita.item_plan
        
        # Preparar respuesta
        serializer = self.get_serializer(cita)
        response_data = {
            'message': 'Cita marcada como atendida. Ahora puedes registrar el episodio clínico.',
            'cita': serializer.data
        }
        
        if item_completado:
            servicio_nombre = getattr(item_completado.servicio, 'nombre', 'Servicio') if item_completado.servicio else 'Servicio'
            response_data['item_plan_completado'] = {
                'id': item_completado.id,
                'servicio': servicio_nombre,
                'mensaje': f'Tratamiento "{servicio_nombre}" marcado como completado.'
            }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def disponibilidad(self, request):
        """
        GET /api/agenda/disponibilidad/?fecha=2025-11-20&odontologo_id=X
        
        Retorna los horarios disponibles de un odontólogo en una fecha específica.
        
        Parámetros query:
        - fecha (requerido): Fecha en formato YYYY-MM-DD
        - odontologo_id (requerido): ID del odontólogo
        
        Response:
        {
            "fecha": "2025-11-20",
            "odontologo": {...},
            "horarios_disponibles": ["09:00", "09:30", "10:00", ...],
            "horarios_ocupados": ["11:00", "14:30", ...],
            "horario_atencion": {
                "inicio": "09:00",
                "fin": "18:00"
            }
        }
        """
        # Validar parámetros
        fecha_str = request.query_params.get('fecha')
        odontologo_id = request.query_params.get('odontologo_id')
        
        if not fecha_str:
            return Response(
                {'error': 'El parámetro "fecha" es requerido (formato: YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not odontologo_id:
            return Response(
                {'error': 'El parámetro "odontologo_id" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parsear fecha
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el odontólogo existe
        try:
            odontologo = PerfilOdontologo.objects.select_related('usuario').get(pk=odontologo_id)
        except PerfilOdontologo.DoesNotExist:
            return Response(
                {'error': 'Odontólogo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Configuración de horario de atención (por defecto 9am a 6pm)
        # TODO: En el futuro, esto debería venir de la configuración del odontólogo
        hora_inicio = time(9, 0)  # 9:00 AM
        hora_fin = time(18, 0)    # 6:00 PM
        intervalo_minutos = 30    # Citas cada 30 minutos
        
        # Generar todos los horarios posibles
        horarios_posibles = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_limite = datetime.combine(fecha, hora_fin)
        
        while hora_actual < hora_limite:
            horarios_posibles.append(hora_actual.strftime('%H:%M'))
            hora_actual += timedelta(minutes=intervalo_minutos)
        
        # Obtener citas ocupadas del odontólogo en esa fecha
        fecha_inicio = datetime.combine(fecha, time.min)
        fecha_fin_dia = datetime.combine(fecha, time.max)
        
        citas_ocupadas = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__gte=timezone.make_aware(fecha_inicio),
            fecha_hora__lte=timezone.make_aware(fecha_fin_dia),
            estado__in=['PENDIENTE', 'CONFIRMADA', 'ATENDIDA']  # Excluir canceladas
        ).values_list('fecha_hora', flat=True)
        
        # Convertir citas ocupadas a formato HH:MM
        horarios_ocupados = [
            timezone.localtime(cita).strftime('%H:%M')
            for cita in citas_ocupadas
        ]
        
        # Calcular horarios disponibles
        horarios_disponibles = [
            horario for horario in horarios_posibles
            if horario not in horarios_ocupados
        ]
        
        return Response({
            'fecha': fecha_str,
            'odontologo': {
                'id': odontologo.id,
                'nombre_completo': odontologo.usuario.get_full_name(),
                'especialidad': odontologo.especialidad if hasattr(odontologo, 'especialidad') else None
            },
            'horarios_disponibles': horarios_disponibles,
            'horarios_ocupados': horarios_ocupados,
            'horario_atencion': {
                'inicio': hora_inicio.strftime('%H:%M'),
                'fin': hora_fin.strftime('%H:%M'),
                'intervalo_minutos': intervalo_minutos
            },
            'total_disponibles': len(horarios_disponibles),
            'total_ocupados': len(horarios_ocupados)
        })
    
    @action(detail=False, methods=['get'], url_path='metricas-dia')
    def metricas_dia(self, request):
        """
        GET /api/agenda/citas/metricas-dia/
        
        Retorna métricas del día actual para el dashboard del odontólogo.
        
        Response:
        {
            "fecha": "2025-11-09",
            "citas_hoy": 5,
            "citas_pendientes": 2,
            "citas_confirmadas": 1,
            "citas_atendidas": 2,
            "pacientes_atendidos": 2,
            "proxima_cita": {
                "id": 1,
                "hora": "15:00",
                "paciente": "Juan Pérez",
                "motivo": "Revisión",
                "minutos_restantes": 45
            }
        }
        """
        user = request.user
        hoy = timezone.now().date()
        ahora = timezone.now()
        
        # Verificar que el usuario sea odontólogo
        try:
            odontologo = PerfilOdontologo.objects.get(usuario=user)
        except PerfilOdontologo.DoesNotExist:
            return Response(
                {'error': 'El usuario no tiene un perfil de odontólogo.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener citas del día del odontólogo (usando fecha_hora__date)
        citas_hoy = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__date=hoy
        ).select_related('paciente')
        
        # Métricas básicas
        total_citas = citas_hoy.count()
        citas_pendientes = citas_hoy.filter(estado='PENDIENTE').count()
        citas_confirmadas = citas_hoy.filter(estado='CONFIRMADA').count()
        citas_atendidas = citas_hoy.filter(estado='ATENDIDA').count()
        
        # Pacientes únicos atendidos hoy
        pacientes_atendidos = citas_hoy.filter(
            estado='ATENDIDA'
        ).values('paciente').distinct().count()
        
        # Próxima cita (citas futuras de hoy ordenadas por fecha_hora)
        proxima_cita = None
        citas_futuras = citas_hoy.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA'],
            fecha_hora__gte=ahora
        ).order_by('fecha_hora')
        
        if citas_futuras.exists():
            cita = citas_futuras.first()
            # Calcular minutos restantes
            minutos_restantes = int((cita.fecha_hora - ahora).total_seconds() / 60)
            
            proxima_cita = {
                'id': cita.id,
                'hora': cita.fecha_hora.strftime('%H:%M'),
                'paciente': cita.paciente.usuario.full_name,
                'motivo': cita.motivo,
                'estado': cita.estado,
                'minutos_restantes': minutos_restantes if minutos_restantes > 0 else 0
            }
        
        return Response({
            'fecha': hoy.strftime('%Y-%m-%d'),
            'citas_hoy': total_citas,
            'citas_pendientes': citas_pendientes,
            'citas_confirmadas': citas_confirmadas,
            'citas_atendidas': citas_atendidas,
            'pacientes_atendidos': pacientes_atendidos,
            'proxima_cita': proxima_cita
        })

    @action(detail=False, methods=['get'])
    def horarios_disponibles(self, request):
        """
        GET /api/agenda/citas/horarios_disponibles/
        
        Retorna los horarios disponibles de un odontólogo en una fecha específica.
        
        Query params:
        - odontologo: ID del odontólogo (requerido)
        - fecha: Fecha en formato YYYY-MM-DD (requerido)
        - duracion: Duración de la cita en minutos (opcional, default: 30)
        
        Responde con:
        {
          "fecha": "2025-11-20",
          "odontologo": "Dr. Juan Pérez",
          "horarios": [
            {"hora": "09:00", "disponible": true},
            {"hora": "09:30", "disponible": false},
            {"hora": "10:00", "disponible": true},
            ...
          ]
        }
        """
        odontologo_id = request.query_params.get('odontologo')
        fecha_str = request.query_params.get('fecha')
        duracion = int(request.query_params.get('duracion', 30))
        
        if not odontologo_id:
            return Response(
                {'error': 'Debe especificar el ID del odontólogo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not fecha_str:
            return Response(
                {'error': 'Debe especificar la fecha (formato: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            odontologo = PerfilOdontologo.objects.get(pk=odontologo_id)
        except PerfilOdontologo.DoesNotExist:
            return Response(
                {'error': 'Odontólogo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # No permitir fechas pasadas
        if fecha < timezone.now().date():
            return Response(
                {'error': 'No se pueden agendar citas en fechas pasadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Horario de atención: 8:00 AM a 6:00 PM
        hora_inicio = time(8, 0)
        hora_fin = time(18, 0)
        
        # Obtener citas existentes del odontólogo en esa fecha
        inicio_dia = datetime.combine(fecha, hora_inicio)
        fin_dia = datetime.combine(fecha, hora_fin)
        
        citas_ocupadas = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__date=fecha,
            estado__in=['PENDIENTE', 'CONFIRMADA']  # Solo citas activas
        ).values_list('fecha_hora', flat=True)
        
        # Convertir a set de strings "HH:MM" para comparación rápida
        horas_ocupadas = {
            cita.strftime('%H:%M') for cita in citas_ocupadas
        }
        
        # Generar slots de tiempo cada 30 minutos (o según duración especificada)
        horarios = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_limite = datetime.combine(fecha, hora_fin)
        
        while hora_actual < hora_limite:
            hora_str = hora_actual.strftime('%H:%M')
            disponible = hora_str not in horas_ocupadas
            
            horarios.append({
                'hora': hora_str,
                'disponible': disponible,
                'fecha_hora_completa': hora_actual.isoformat()
            })
            
            # Avanzar según duración
            hora_actual += timedelta(minutes=duracion)
        
        return Response({
            'fecha': fecha_str,
            'odontologo': odontologo.usuario.full_name,
            'odontologo_id': odontologo.pk,
            'horarios': horarios,
            'total_disponibles': sum(1 for h in horarios if h['disponible']),
            'total_ocupados': len(horas_ocupadas)
        })

