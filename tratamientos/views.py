from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    CategoriaServicio, Servicio, PlanDeTratamiento, ItemPlanTratamiento,
    Presupuesto, ItemPresupuesto  # Nuevos modelos del Paso 2.D
)
from .serializers import (
    CategoriaServicioSerializer,
    ServicioSerializer,
    ServicioListSerializer,
    ServicioCatalogoSerializer,
    PlanDeTratamientoSerializer,
    PlanDeTratamientoListSerializer,
    ItemPlanTratamientoSerializer,
    ItemPlanTratamientoSimpleSerializer,
    # Nuevos serializers del Paso 2.D
    PresupuestoSerializer,
    PresupuestoListSerializer,
    PresupuestoCreacionSerializer,
    ItemPresupuestoSerializer
)


def index(request):
    return JsonResponse({"status": "ok", "app": "tratamientos"})


class CategoriaServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de servicios odontológicos.
    
    Endpoints disponibles:
    - GET /api/tratamientos/categorias/ - Lista categorías
    - POST /api/tratamientos/categorias/ - Crear categoría
    - GET /api/tratamientos/categorias/{id}/ - Detalle categoría
    - PUT/PATCH /api/tratamientos/categorias/{id}/ - Actualizar
    - DELETE /api/tratamientos/categorias/{id}/ - Eliminar
    """
    queryset = CategoriaServicio.objects.all()
    serializer_class = CategoriaServicioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['orden', 'nombre', 'creado']
    ordering = ['orden', 'nombre']

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        GET /api/tratamientos/categorias/activas/
        
        Retorna solo las categorías activas, ordenadas por orden.
        """
        categorias = self.queryset.filter(activo=True).order_by('orden', 'nombre')
        serializer = self.get_serializer(categorias, many=True)
        return Response(serializer.data)


class ServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el catálogo de servicios odontológicos.
    
    Proporciona operaciones CRUD completas para servicios, con filtrado 
    y endpoints especializados para diferentes casos de uso.
    
    Endpoints disponibles:
    - GET /api/tratamientos/servicios/ - Lista servicios (con filtros)
    - POST /api/tratamientos/servicios/ - Crear servicio
    - GET /api/tratamientos/servicios/{id}/ - Detalle servicio
    - PUT/PATCH /api/tratamientos/servicios/{id}/ - Actualizar
    - DELETE /api/tratamientos/servicios/{id}/ - Eliminar
    - GET /api/tratamientos/servicios/catalogo/ - Catálogo público (CU22)
    - GET /api/tratamientos/servicios/por_categoria/ - Agrupados por categoría
    """
    queryset = Servicio.objects.select_related('categoria')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'categoria': ['exact'],
        'activo': ['exact'],
        'requiere_cita_previa': ['exact'],
        'requiere_autorizacion': ['exact'],
        'precio_base': ['gte', 'lte'],
        'tiempo_estimado': ['gte', 'lte']
    }
    search_fields = ['codigo_servicio', 'nombre', 'descripcion', 'categoria__nombre']
    ordering_fields = ['nombre', 'precio_base', 'tiempo_estimado', 'creado']
    ordering = ['categoria', 'codigo_servicio']

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        # Siempre usar el serializer completo para que incluya opciones_disponibles
        # Esto es necesario para el modal de agregar ítems al plan
        if self.action == 'catalogo':
            return ServicioCatalogoSerializer
        return ServicioSerializer

    def get_queryset(self):
        """
        Personalizar queryset según necesidades.
        El aislamiento por tenant es automático gracias a django-tenants.
        """
        queryset = super().get_queryset()
        
        # Para staff/admin: todos los servicios
        # Para otros usuarios: solo servicios activos
        if not self.request.user.is_staff:
            queryset = queryset.filter(activo=True)
        
        return queryset

    @action(detail=False, methods=['get'])
    def catalogo(self, request):
        """
        GET /api/tratamientos/servicios/catalogo/
        
        Endpoint público del catálogo de servicios (CU22).
        Retorna solo servicios activos con información esencial.
        """
        servicios = self.get_queryset().filter(activo=True)
        
        # Aplicar filtros de query params si existen
        categoria_id = request.query_params.get('categoria')
        if categoria_id:
            servicios = servicios.filter(categoria_id=categoria_id)
        
        # Filtro por precio máximo
        precio_max = request.query_params.get('precio_max')
        if precio_max:
            try:
                servicios = servicios.filter(precio_base__lte=float(precio_max))
            except ValueError:
                pass
        
        # Ordenar por categoría y nombre
        servicios = servicios.order_by('categoria__orden', 'categoria__nombre', 'nombre')
        
        # Paginación si hay muchos resultados
        page = self.paginate_queryset(servicios)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(servicios, many=True)
        return Response({
            'total': servicios.count(),
            'servicios': serializer.data
        })

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """
        GET /api/tratamientos/servicios/por_categoria/
        
        Retorna servicios agrupados por categoría.
        Útil para mostrar en interfaces organizadas.
        """
        from django.db.models import Prefetch
        
        # Obtener categorías con sus servicios
        categorias = CategoriaServicio.objects.filter(
            activo=True
        ).prefetch_related(
            Prefetch(
                'servicios',
                queryset=self.get_queryset().filter(activo=True),
                to_attr='servicios_activos'
            )
        ).order_by('orden', 'nombre')
        
        resultado = []
        for categoria in categorias:
            if categoria.servicios_activos:  # Solo incluir si tiene servicios
                categoria_data = CategoriaServicioSerializer(categoria).data
                categoria_data['servicios'] = ServicioCatalogoSerializer(
                    categoria.servicios_activos, many=True
                ).data
                resultado.append(categoria_data)
        
        return Response({
            'categorias': resultado,
            'total_categorias': len(resultado)
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        GET /api/tratamientos/servicios/estadisticas/
        
        Retorna estadísticas del catálogo de servicios.
        Solo para staff/admin.
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Acceso denegado'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.db.models import Count, Avg, Min, Max
        
        stats = {
            'total_servicios': Servicio.objects.count(),
            'servicios_activos': Servicio.objects.filter(activo=True).count(),
            'servicios_inactivos': Servicio.objects.filter(activo=False).count(),
            'total_categorias': CategoriaServicio.objects.count(),
            'categorias_activas': CategoriaServicio.objects.filter(activo=True).count(),
            'precio_promedio': Servicio.objects.filter(activo=True).aggregate(
                Avg('precio_base')
            )['precio_base__avg'] or 0,
            'precio_minimo': Servicio.objects.filter(activo=True).aggregate(
                Min('precio_base')
            )['precio_base__min'] or 0,
            'precio_maximo': Servicio.objects.filter(activo=True).aggregate(
                Max('precio_base')
            )['precio_base__max'] or 0,
            'tiempo_promedio': Servicio.objects.filter(activo=True).aggregate(
                Avg('tiempo_estimado')
            )['tiempo_estimado__avg'] or 0,
        }
        
        # Servicios por categoría
        stats['por_categoria'] = list(
            CategoriaServicio.objects.annotate(
                cantidad_servicios=Count('servicios')
            ).values('nombre', 'cantidad_servicios').order_by('-cantidad_servicios')
        )
        
        return Response(stats)


# ===============================================================================
# PASO 2.C: VIEWSETS PARA PLANES DE TRATAMIENTO - ¡AQUÍ SE MATERIALIZA EL PRECIO DINÁMICO!
# ===============================================================================

class PlanDeTratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para planes de tratamiento con precio dinámico.
    
    ¡Este es donde tu visión cobra vida! Aquí los doctores:
    1. Crean planes personalizados para cada paciente
    2. Seleccionan servicios específicos
    3. Eligen materiales opcionales (¡precio dinámico!)
    4. El sistema calcula y congela precios automáticamente
    
    Endpoints:
    - GET /api/tratamientos/planes/ - Lista planes
    - POST /api/tratamientos/planes/ - Crear plan
    - GET /api/tratamientos/planes/{id}/ - Detalle plan
    - PUT/PATCH /api/tratamientos/planes/{id}/ - Actualizar
    - DELETE /api/tratamientos/planes/{id}/ - Eliminar
    - POST /api/tratamientos/planes/{id}/presentar/ - Presentar plan al paciente
    - POST /api/tratamientos/planes/{id}/aceptar/ - Paciente acepta plan
    - POST /api/tratamientos/planes/{id}/iniciar/ - Iniciar tratamiento
    - POST /api/tratamientos/planes/{id}/finalizar/ - Finalizar tratamiento
    - GET /api/tratamientos/planes/mis_planes/ - Planes del doctor actual
    - GET /api/tratamientos/planes/por_paciente/ - Planes de un paciente específico
    """
    queryset = PlanDeTratamiento.objects.select_related(
        'paciente__usuario', 
        'odontologo__usuario',
        'odontologo__especialidad'
    ).prefetch_related('items__servicio', 'items__insumo_seleccionado')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'estado': ['exact'],
        'prioridad': ['exact'],
        'paciente': ['exact'],
        'odontologo': ['exact'],
        'fecha_creacion': ['gte', 'lte'],
        'fecha_presentacion': ['gte', 'lte']
    }
    search_fields = [
        'titulo', 
        'descripcion', 
        'paciente__usuario__nombre',
        'paciente__usuario__apellido',
        'odontologo__usuario__nombre',
        'odontologo__usuario__apellido'
    ]
    ordering_fields = ['fecha_creacion', 'precio_total_plan', 'estado']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        """Serializer apropiado según la acción"""
        if self.action == 'list' or self.action == 'mis_planes':
            return PlanDeTratamientoListSerializer
        return PlanDeTratamientoSerializer

    def get_queryset(self):
        """
        Filtrar planes según el rol del usuario.
        Los médicos solo ven sus planes o los de su clínica.
        """
        queryset = super().get_queryset()
        
        # Si es paciente, solo ve sus propios planes
        if hasattr(self.request.user, 'perfil_paciente'):
            queryset = queryset.filter(paciente=self.request.user.perfil_paciente)
        
        # Si es odontólogo, solo ve planes donde participa o de su clínica
        elif hasattr(self.request.user, 'perfil_odontologo'):
            # Por ahora, ve todos los planes de la clínica (tenant)
            # En el futuro podrías filtrar solo por planes propios
            pass
        
        # Normalizar filtro de estado: ACTIVO -> EN_PROGRESO
        estado_param = self.request.query_params.get('estado')
        if estado_param == 'ACTIVO':
            queryset = queryset.filter(estado='en_progreso')
        
        return queryset

    def perform_create(self, serializer):
        """
        Al crear un plan, establecer el odontólogo automáticamente si aplica.
        """
        # Si el usuario es odontólogo, lo asignamos automáticamente
        if hasattr(self.request.user, 'perfil_odontologo'):
            serializer.save(odontologo=self.request.user.perfil_odontologo)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def presentar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/presentar/
        
        Presenta el plan al paciente para su aprobación.
        Solo el odontólogo propietario puede presentar el plan.
        """
        plan = self.get_object()
        
        # Verificar permisos
        if hasattr(request.user, 'perfil_odontologo'):
            if plan.odontologo != request.user.perfil_odontologo:
                return Response(
                    {'error': 'No tienes permisos para presentar este plan'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el odontólogo puede presentar el plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado del plan
        if plan.estado != 'borrador':
            return Response(
                {'error': f'No se puede presentar un plan en estado {plan.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que tenga al menos un ítem
        if not plan.items.exists():
            return Response(
                {'error': 'El plan debe tener al menos un tratamiento antes de presentarlo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar estado y registrar fecha
        plan.presentar()
        
        return Response({
            'message': 'Plan presentado al paciente exitosamente',
            'plan_id': plan.id,
            'estado': plan.get_estado_display(),
            'fecha_presentacion': plan.fecha_presentacion,
            'precio_total': str(plan.precio_total_plan)
        })

    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/aceptar/
        
        El paciente acepta el plan de tratamiento.
        SOLO el paciente propietario puede aceptar.
        """
        plan = self.get_object()
        
        # Verificar permisos - SOLO el paciente puede aceptar
        if not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo un paciente puede aceptar el plan de tratamiento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.paciente != request.user.perfil_paciente:
            return Response(
                {'error': 'No tienes permisos para aceptar este plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado del plan
        if plan.estado != 'presentado':
            return Response(
                {'error': f'No se puede aceptar un plan en estado {plan.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aceptar plan
        plan.aceptar()
        
        return Response({
            'message': 'Plan de tratamiento aceptado exitosamente',
            'plan_id': plan.id,
            'estado': plan.get_estado_display(),
            'fecha_aceptacion': plan.fecha_aceptacion,
            'precio_total_final': str(plan.precio_total_plan)
        })

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/aprobar/
        
        El paciente aprueba el plan de tratamiento propuesto.
        Alias de 'aceptar' para compatibilidad con frontend.
        """
        plan = self.get_object()
        
        # Verificar permisos - SOLO el paciente puede aprobar
        if not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo un paciente puede aprobar el plan de tratamiento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.paciente != request.user.perfil_paciente:
            return Response(
                {'error': 'No tiene permiso para aprobar este plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado del plan (debe ser PROPUESTO)
        if plan.estado not in ['propuesto', 'presentado']:
            return Response(
                {'error': f'El plan no está en estado PROPUESTO'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener comentarios opcionales
        comentarios = request.data.get('comentarios', '')
        
        # Cambiar estado a APROBADO
        plan.estado = 'aprobado'
        plan.fecha_aceptacion = timezone.now()
        if comentarios:
            plan.notas_internas = (plan.notas_internas or '') + f'\n\nComentarios del paciente: {comentarios}'
        plan.save()
        
        return Response({
            'id': plan.id,
            'titulo': plan.titulo,
            'estado': plan.estado,
            'estado_display': plan.get_estado_display(),
            'fecha_aceptacion': plan.fecha_aceptacion,
            'mensaje': 'Plan de tratamiento aprobado exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/rechazar/
        
        El paciente rechaza el plan de tratamiento propuesto.
        Requiere motivo obligatorio.
        """
        plan = self.get_object()
        
        # Verificar permisos - SOLO el paciente puede rechazar
        if not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo un paciente puede rechazar el plan de tratamiento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.paciente != request.user.perfil_paciente:
            return Response(
                {'error': 'No tiene permiso para rechazar este plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado del plan
        if plan.estado not in ['propuesto', 'presentado']:
            return Response(
                {'error': 'El plan no está en estado PROPUESTO'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar motivo (requerido)
        motivo = request.data.get('motivo', '').strip()
        if not motivo:
            return Response(
                {'error': 'El campo \'motivo\' es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener comentarios adicionales
        comentarios = request.data.get('comentarios', '')
        
        # Cambiar estado a RECHAZADO
        plan.estado = 'rechazado'
        plan.notas_internas = (plan.notas_internas or '') + f'\n\nMOTIVO DE RECHAZO: {motivo}'
        if comentarios:
            plan.notas_internas += f'\nComentarios adicionales: {comentarios}'
        plan.save()
        
        return Response({
            'id': plan.id,
            'titulo': plan.titulo,
            'estado': plan.estado,
            'estado_display': plan.get_estado_display(),
            'motivo_rechazo': motivo,
            'mensaje': 'Plan de tratamiento rechazado'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/iniciar/
        
        Inicia la ejecución del plan de tratamiento.
        Solo el odontólogo puede iniciar.
        """
        plan = self.get_object()
        
        # Verificar permisos (solo odontólogo o staff)
        if hasattr(request.user, 'perfil_odontologo'):
            if plan.odontologo != request.user.perfil_odontologo:
                return Response(
                    {'error': 'No tienes permisos para iniciar este plan'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el odontólogo puede iniciar el tratamiento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado
        if plan.estado != 'aceptado':
            return Response(
                {'error': f'No se puede iniciar un plan en estado {plan.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Iniciar plan
        plan.iniciar()
        
        return Response({
            'message': 'Tratamiento iniciado exitosamente',
            'plan_id': plan.id,
            'estado': plan.get_estado_display(),
            'fecha_inicio': plan.fecha_inicio
        })

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/finalizar/
        
        Finaliza el plan de tratamiento.
        Solo cuando todos los ítems estén completados.
        """
        plan = self.get_object()
        
        # Verificar permisos
        if hasattr(request.user, 'perfil_odontologo'):
            if plan.odontologo != request.user.perfil_odontologo:
                return Response(
                    {'error': 'No tienes permisos para finalizar este plan'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el odontólogo puede finalizar el tratamiento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado
        if plan.estado != 'en_progreso':
            return Response(
                {'error': f'No se puede finalizar un plan en estado {plan.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que todos los ítems estén completados
        items_pendientes = plan.items.exclude(estado='completado').count()
        if items_pendientes > 0:
            return Response(
                {'error': f'Aún hay {items_pendientes} tratamientos pendientes de completar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Finalizar plan
        plan.finalizar()
        
        return Response({
            'message': 'Plan de tratamiento finalizado exitosamente',
            'plan_id': plan.id,
            'estado': plan.get_estado_display(),
            'fecha_finalizacion': plan.fecha_finalizacion,
            'duracion_total': (plan.fecha_finalizacion - plan.fecha_inicio).days if plan.fecha_inicio else None
        })

    @action(detail=False, methods=['get'])
    def propuestos(self, request):
        """
        GET /api/tratamientos/planes/propuestos/
        
        Lista planes propuestos (solicitudes) para el paciente actual.
        Permite filtrar por estado.
        """
        if not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo pacientes pueden ver solicitudes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtrar planes del paciente
        queryset = self.get_queryset().filter(paciente=request.user.perfil_paciente)
        
        # Filtrar por estado si se especifica
        estado_param = request.query_params.get('estado', 'PROPUESTO')
        if estado_param:
            queryset = queryset.filter(estado=estado_param.lower())
        
        # Aplicar paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mis_planes(self, request):
        """
        GET /api/tratamientos/planes/mis_planes/
        
        Planes del odontólogo actual o del paciente actual.
        """
        queryset = self.get_queryset()
        
        if hasattr(request.user, 'perfil_odontologo'):
            queryset = queryset.filter(odontologo=request.user.perfil_odontologo)
        elif hasattr(request.user, 'perfil_paciente'):
            queryset = queryset.filter(paciente=request.user.perfil_paciente)
        else:
            return Response(
                {'error': 'Usuario sin perfil de odontólogo o paciente'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Aplicar filtros adicionales
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        GET /api/tratamientos/planes/activos/
        
        Retorna planes activos (ACEPTADO, EN_PROGRESO) del usuario actual.
        Usado por el frontend para seleccionar planes al agendar citas.
        """
        queryset = self.get_queryset()
        
        # Solo pacientes pueden usar este endpoint
        if not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo pacientes pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtrar por estados activos
        queryset = queryset.filter(
            paciente=request.user.perfil_paciente,
            estado__in=['ACEPTADO', 'EN_PROGRESO']
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """
        GET /api/tratamientos/planes/por_paciente/?paciente_id=123
        
        Obtiene todos los planes de un paciente específico.
        Solo odontólogos y staff pueden ver planes de otros pacientes.
        """
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Debe especificar paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar permisos
        if hasattr(request.user, 'perfil_paciente'):
            if str(request.user.perfil_paciente.id) != str(paciente_id):
                return Response(
                    {'error': 'No tienes permisos para ver planes de otros pacientes'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        queryset = self.get_queryset().filter(paciente_id=paciente_id)
        
        # Filtros adicionales
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'paciente_id': paciente_id,
            'total_planes': queryset.count(),
            'planes': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='generar-presupuesto')
    def generar_presupuesto(self, request, pk=None):
        """
        POST /api/tratamientos/planes/{id}/generar-presupuesto/
        
        ¡CU20! Crea un nuevo Presupuesto (snapshot) a partir de este Plan de Tratamiento.
        
        Este endpoint "congela" el plan actual con todos sus precios dinámicos
        calculados y crea una oferta formal que el paciente puede aceptar.
        """
        plan = self.get_object()
        
        # Verificar permisos (solo odontólogo o staff pueden generar presupuestos)
        if hasattr(request.user, 'perfil_odontologo'):
            if plan.odontologo != request.user.perfil_odontologo:
                return Response(
                    {'error': 'No tienes permisos para generar presupuestos de este plan'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el odontólogo puede generar presupuestos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que el plan esté en estado apropiado
        if plan.estado not in ['borrador', 'presentado']:
            return Response(
                {'error': 'Solo se pueden generar presupuestos de planes en Borrador o Presentado'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if plan.items.count() == 0:
            return Response(
                {'error': 'No se puede generar un presupuesto de un plan sin tratamientos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar el serializer de creación para validar datos adicionales
        serializer = PresupuestoCreacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular la siguiente versión
        version_actual = plan.presupuestos.count() + 1
        
        # Calcular fecha de vencimiento
        fecha_vencimiento = serializer.validated_data.get('fecha_vencimiento')
        if not fecha_vencimiento:
            fecha_vencimiento = timezone.now().date() + timedelta(days=30)  # 30 días por defecto
        
        # Crear el Presupuesto
        presupuesto = Presupuesto.objects.create(
            plan_tratamiento=plan,
            version=version_actual,
            estado=Presupuesto.EstadoPresupuesto.PRESENTADO,
            fecha_presentacion=timezone.now(),
            fecha_vencimiento=fecha_vencimiento
        )
        
        # ¡AQUÍ OCURRE LA MAGIA! Calcular y "congelar" los totales
        presupuesto.calcular_totales_desde_plan()
        
        # "Congelar" cada ítem del plan en el presupuesto
        for item_plan in plan.items.all():
            ItemPresupuesto.objects.create(
                presupuesto=presupuesto,
                item_plan_original=item_plan,
                orden=item_plan.orden,
                nombre_servicio=item_plan.servicio.nombre,
                nombre_insumo_seleccionado=item_plan.insumo_seleccionado.nombre if item_plan.insumo_seleccionado else "Sin material específico",
                precio_servicio=item_plan.precio_servicio_snapshot,
                precio_materiales_fijos=item_plan.precio_materiales_fijos_snapshot,
                precio_insumo_seleccionado=item_plan.precio_insumo_seleccionado_snapshot,
                precio_total_item=item_plan.precio_total
            )
            
        # Actualizar el estado del plan
        plan.estado = PlanDeTratamiento.EstadoPlan.PRESENTADO
        plan.save()
        
        # Retornar el presupuesto creado
        result_serializer = PresupuestoSerializer(presupuesto)
        return Response({
            'message': f'Presupuesto V{presupuesto.version} generado exitosamente',
            'presupuesto': result_serializer.data,
            'total_congelado': f"${presupuesto.total_presupuestado:,.2f}",
            'url_aceptacion': f"/api/tratamientos/presupuestos/{presupuesto.id}/aceptar/{presupuesto.token_aceptacion}/"
        }, status=status.HTTP_201_CREATED)


class ItemPlanTratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ítems de planes de tratamiento.
    
    ¡Aquí es donde ocurre la MAGIA del precio dinámico!
    Cada ítem representa un tratamiento específico con:
    - Servicio base seleccionado
    - Material opcional elegido (si aplica)
    - Precio calculado y congelado automáticamente
    
    Endpoints:
    - GET /api/tratamientos/items/ - Lista ítems
    - POST /api/tratamientos/items/ - Crear ítem (¡calcula precio dinámico!)
    - GET /api/tratamientos/items/{id}/ - Detalle ítem
    - PUT/PATCH /api/tratamientos/items/{id}/ - Actualizar ítem
    - DELETE /api/tratamientos/items/{id}/ - Eliminar ítem
    - POST /api/tratamientos/items/{id}/completar/ - Marcar como completado
    - POST /api/tratamientos/items/{id}/reagendar/ - Reagendar tratamiento
    """
    queryset = ItemPlanTratamiento.objects.select_related(
        'plan__paciente__usuario',
        'plan__odontologo__usuario', 
        'servicio__categoria',
        'insumo_seleccionado__categoria'
    )
    serializer_class = ItemPlanTratamientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'plan': ['exact'],
        'servicio': ['exact'],
        'estado': ['exact'],
        'fecha_estimada': ['gte', 'lte'],
        'fecha_realizada': ['gte', 'lte']
    }
    search_fields = [
        'servicio__nombre',
        'insumo_seleccionado__nombre',
        'notas'
    ]
    ordering_fields = ['orden', 'fecha_estimada', 'precio_total']
    ordering = ['plan', 'orden']

    def get_queryset(self):
        """
        Filtrar ítems según permisos del usuario.
        """
        queryset = super().get_queryset()
        
        # Si es paciente, solo ve ítems de sus planes
        if hasattr(self.request.user, 'perfil_paciente'):
            queryset = queryset.filter(plan__paciente=self.request.user.perfil_paciente)
        
        # Si es odontólogo, solo ve ítems de sus planes
        elif hasattr(self.request.user, 'perfil_odontologo'):
            queryset = queryset.filter(plan__odontologo=self.request.user.perfil_odontologo)
        
        return queryset

    def perform_create(self, serializer):
        """
        ¡AQUÍ OCURRE LA MAGIA DEL PRECIO DINÁMICO!
        
        Al crear un ítem, el sistema automáticamente:
        1. Captura el precio actual del servicio
        2. Captura precios de materiales fijos
        3. Captura precio del insumo seleccionado
        4. Congela estos precios en snapshots
        5. Calcula el precio total
        
        ¡Así el precio queda congelado aunque los costos cambien después!
        """
        serializer.save()
        
        # El método save() del modelo ya maneja toda la lógica de snapshots
        # Ver ItemPlanTratamiento.save() en models.py

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """
        POST /api/tratamientos/items/{id}/completar/
        
        Marca un ítem como completado.
        Solo el odontólogo puede completar tratamientos.
        """
        item = self.get_object()
        
        # Verificar permisos
        if hasattr(request.user, 'perfil_odontologo'):
            if item.plan.odontologo != request.user.perfil_odontologo:
                return Response(
                    {'error': 'No tienes permisos para completar este tratamiento'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el odontólogo puede completar tratamientos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar estado del plan
        if item.plan.estado not in ['aceptado', 'en_progreso']:
            return Response(
                {'error': 'No se pueden completar tratamientos de un plan no aceptado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar estado del ítem
        if item.estado == 'completado':
            return Response(
                {'error': 'Este tratamiento ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Completar ítem
        from django.utils import timezone
        item.estado = 'completado'
        item.fecha_realizada = timezone.now()
        item.save()
        
        # Si el plan estaba aceptado, cambiarlo a en_progreso
        if item.plan.estado == 'aceptado':
            item.plan.iniciar()
        
        return Response({
            'message': 'Tratamiento completado exitosamente',
            'item_id': item.id,
            'estado': item.get_estado_display(),
            'fecha_realizada': item.fecha_realizada,
            'precio_final': str(item.precio_total)
        })

    @action(detail=True, methods=['post'])
    def reagendar(self, request, pk=None):
        """
        POST /api/tratamientos/items/{id}/reagendar/
        Body: {"nueva_fecha": "2024-01-15", "motivo": "Reagendado por el paciente"}
        
        Reagenda un tratamiento pendiente.
        """
        item = self.get_object()
        
        # Verificar que se puede reagendar
        if item.estado == 'completado':
            return Response(
                {'error': 'No se puede reagendar un tratamiento completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener nueva fecha del body
        nueva_fecha = request.data.get('nueva_fecha')
        motivo = request.data.get('motivo', 'Reagendado')
        
        if not nueva_fecha:
            return Response(
                {'error': 'Debe especificar la nueva_fecha'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            fecha_obj = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar fecha
        fecha_anterior = item.fecha_estimada
        item.fecha_estimada = fecha_obj
        item.notas = f"{item.notas}\n\nReagendado: {motivo} (anterior: {fecha_anterior})" if item.notas else f"Reagendado: {motivo}"
        item.save()
        
        return Response({
            'message': 'Tratamiento reagendado exitosamente',
            'item_id': item.id,
            'fecha_anterior': fecha_anterior,
            'fecha_nueva': fecha_obj,
            'motivo': motivo
        })


# ===============================================================================
# PASO 2.D: VIEWSETS PARA PRESUPUESTOS (CU20, CU21)
# ===============================================================================

class PresupuestoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para manejar Presupuestos - El corazón del CU20 y CU21.
    
    ¡AQUÍ SE MANEJA LA ACEPTACIÓN DE PRESUPUESTOS!
    
    Los presupuestos son "snapshots" inmutables de los planes de tratamiento
    que permiten al paciente aceptar una oferta formal con precios congelados.
    
    Endpoints:
    - GET /api/tratamientos/presupuestos/ - Lista presupuestos
    - GET /api/tratamientos/presupuestos/{id}/ - Detalle presupuesto
    - POST /api/tratamientos/presupuestos/{id}/aceptar/{token}/ - ¡CU21! Aceptar presupuesto
    """
    queryset = Presupuesto.objects.select_related(
        'plan_tratamiento__paciente__usuario',
        'plan_tratamiento__odontologo__usuario'
    ).prefetch_related('items')
    permission_classes = [permissions.IsAuthenticated]  # Protegido por defecto
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'estado': ['exact'],
        'plan_tratamiento__paciente': ['exact'],
        'plan_tratamiento__odontologo': ['exact'],
        'fecha_presentacion': ['gte', 'lte'],
        'fecha_vencimiento': ['gte', 'lte'],
    }
    search_fields = [
        'plan_tratamiento__titulo',
        'plan_tratamiento__paciente__usuario__nombre',
        'plan_tratamiento__paciente__usuario__apellido',
        'plan_tratamiento__odontologo__usuario__nombre'
    ]
    ordering_fields = ['fecha_presentacion', 'total_presupuestado', 'version']
    ordering = ['-fecha_presentacion']

    def get_serializer_class(self):
        """Serializer apropiado según la acción"""
        if self.action == 'list':
            return PresupuestoListSerializer
        return PresupuestoSerializer

    def get_queryset(self):
        """
        Filtrar presupuestos según el rol del usuario.
        Los pacientes solo ven sus propios presupuestos.
        Los odontólogos ven presupuestos de sus planes.
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Si es paciente, solo ve sus presupuestos
        if hasattr(user, 'perfil_paciente'):
            return queryset.filter(plan_tratamiento__paciente=user.perfil_paciente)
        
        # Si es odontólogo, solo ve presupuestos de sus planes
        elif hasattr(user, 'perfil_odontologo'):
            return queryset.filter(plan_tratamiento__odontologo=user.perfil_odontologo)
        
        # Staff ve todos (de su tenant)
        elif user.is_staff:
            return queryset
        
        # Default: no ve nada
        return queryset.none()

    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[permissions.AllowAny],  # ¡Público! Usa el token para autenticación
        url_path='aceptar/(?P<token>[^/.]+)'
    )
    def aceptar_presupuesto(self, request, pk=None, token=None):
        """
        POST /api/tratamientos/presupuestos/{id}/aceptar/{token}/
        
        ¡CU21! Permite a un paciente aceptar un presupuesto usando el token único.
        
        Este es el endpoint público que el paciente puede usar desde un email
        sin necesidad de iniciar sesión. El token garantiza la seguridad.
        """
        # Buscar presupuesto por ID y token
        presupuesto = get_object_or_404(
            Presupuesto, 
            id=pk, 
            token_aceptacion=token
        )
        
        # Verificar que puede ser aceptado
        if presupuesto.estado == Presupuesto.EstadoPresupuesto.ACEPTADO:
            return Response({
                'message': 'Este presupuesto ya fue aceptado anteriormente',
                'fecha_aceptacion': presupuesto.fecha_aceptacion,
                'total': f"${presupuesto.total_presupuestado:,.2f}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if presupuesto.estado == Presupuesto.EstadoPresupuesto.RECHAZADO:
            return Response({
                'error': 'Este presupuesto fue rechazado y no puede ser aceptado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if presupuesto.estado == Presupuesto.EstadoPresupuesto.VENCIDO or presupuesto.esta_vencido:
            return Response({
                'error': 'Este presupuesto ha vencido y ya no puede ser aceptado',
                'fecha_vencimiento': presupuesto.fecha_vencimiento
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not presupuesto.puede_ser_aceptado:
            return Response({
                'error': f'Este presupuesto no puede ser aceptado (Estado: {presupuesto.get_estado_display()})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ¡ACEPTAR EL PRESUPUESTO! 🎉
        try:
            presupuesto.aceptar()  # Esto actualiza automáticamente el plan
            
            # Información del plan y paciente para la respuesta
            plan = presupuesto.plan_tratamiento
            paciente = plan.paciente
            
            return Response({
                'success': True,
                'message': f'¡Presupuesto aceptado exitosamente!',
                'presupuesto': {
                    'id': presupuesto.id,
                    'version': presupuesto.version,
                    'total': f"${presupuesto.total_presupuestado:,.2f}",
                    'fecha_aceptacion': presupuesto.fecha_aceptacion
                },
                'plan': {
                    'titulo': plan.titulo,
                    'estado': plan.get_estado_display(),
                    'total_items': plan.items.count()
                },
                'paciente': {
                    'nombre': f"{paciente.usuario.nombre} {paciente.usuario.apellido}",
                    'email': paciente.usuario.email
                },
                'proximos_pasos': 'El odontólogo será notificado y se programarán las citas correspondientes'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al aceptar el presupuesto: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """
        POST /api/tratamientos/presupuestos/{id}/rechazar/
        
        Permite rechazar un presupuesto (requiere autenticación).
        """
        presupuesto = self.get_object()
        
        # Verificar permisos
        if hasattr(request.user, 'perfil_paciente'):
            if presupuesto.plan_tratamiento.paciente != request.user.perfil_paciente:
                return Response(
                    {'error': 'No tienes permisos para rechazar este presupuesto'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Solo el paciente puede rechazar el presupuesto'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not presupuesto.puede_ser_aceptado:
            return Response(
                {'error': 'Este presupuesto no está en estado de ser rechazado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rechazar presupuesto
        motivo = request.data.get('motivo', 'Rechazado por el paciente')
        presupuesto.rechazar(motivo)
        
        return Response({
            'message': 'Presupuesto rechazado exitosamente',
            'motivo': motivo
        })

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """
        GET /api/tratamientos/presupuestos/vencidos/
        
        Lista presupuestos que han vencido (solo para staff).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo el personal puede ver presupuestos vencidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(
            estado=Presupuesto.EstadoPresupuesto.PRESENTADO,
            fecha_vencimiento__lt=timezone.now().date()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_vencidos': queryset.count(),
            'presupuestos_vencidos': serializer.data
        })
