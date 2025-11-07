# facturacion/views.py
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Factura, Pago
from .serializers import (
    FacturaSerializer, FacturaCreateSerializer, FacturaListSerializer,
    PagoSerializer, PagoCreateSerializer
)
from usuarios.models import PerfilPaciente


class FacturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de facturas (CU30-CU33)
    - Admins: Ven todas las facturas del tenant
    - Doctores: Ven facturas de sus pacientes  
    - Pacientes: Solo ven sus propias facturas
    """
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'create':
            return FacturaCreateSerializer
        elif self.action == 'list':
            return FacturaListSerializer
        return FacturaSerializer
    
    def get_queryset(self):
        """Filtrar facturas según tipo de usuario"""
        user = self.request.user
        queryset = Factura.objects.all().select_related('presupuesto', 'paciente')
        
        # Admin ve todas las facturas
        if user.is_staff:
            return queryset
        
        # Doctor ve facturas de sus pacientes
        if hasattr(user, 'perfilprofesional'):
            # Obtener pacientes del doctor
            pacientes_ids = PerfilPaciente.objects.filter(
                historialclinico__episodioatencion__doctor=user.perfilprofesional
            ).values_list('id', flat=True).distinct()
            return queryset.filter(paciente_id__in=pacientes_ids)
        
        # Paciente solo ve sus facturas
        if hasattr(user, 'perfilpaciente'):
            return queryset.filter(paciente=user.perfilpaciente)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Crear factura desde presupuesto aceptado"""
        presupuesto = serializer.validated_data['presupuesto']
        
        # Verificar que el presupuesto esté aceptado
        if presupuesto.estado != 'aceptado':
            raise serializers.ValidationError(
                "Solo se pueden facturar presupuestos aceptados"
            )
        
        # Verificar que no exista factura para este presupuesto
        if Factura.objects.filter(presupuesto=presupuesto).exists():
            raise serializers.ValidationError(
                "Ya existe una factura para este presupuesto"
            )
        
        serializer.save(
            paciente=presupuesto.plan_tratamiento.paciente,
            monto_total=presupuesto.total_presupuestado
        )
    
    @action(detail=True, methods=['post'])
    def marcar_pagada(self, request, pk=None):
        """Marcar factura como completamente pagada"""
        factura = self.get_object()
        
        if factura.estado == 'pagada':
            return Response(
                {'error': 'La factura ya está pagada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el monto pagado cubra el total
        if factura.monto_pagado >= factura.monto_total:
            factura.estado = 'pagada'
            factura.fecha_pagada = timezone.now()
            factura.save()
            
            return Response({
                'message': 'Factura marcada como pagada',
                'factura': self.get_serializer(factura).data
            })
        else:
            return Response(
                {'error': f'Faltan ${factura.saldo_pendiente:.2f} por pagar'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar factura (solo admin)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo los administradores pueden cancelar facturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        factura = self.get_object()
        
        if factura.estado == 'cancelada':
            return Response(
                {'error': 'La factura ya está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if factura.monto_pagado > 0:
            return Response(
                {'error': 'No se puede cancelar una factura con pagos realizados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        factura.estado = 'cancelada'
        factura.save()
        
        return Response({
            'message': 'Factura cancelada exitosamente',
            'factura': self.get_serializer(factura).data
        })
    
    @action(detail=False, methods=['get'])
    def reporte_financiero(self, request):
        """Generar reporte financiero (solo admin/doctor)"""
        if not (request.user.is_staff or hasattr(request.user, 'perfilprofesional')):
            return Response(
                {'error': 'Sin permisos para ver reportes financieros'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtros opcionales
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = self.get_queryset()
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_emision__date__gte=fecha_inicio)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_emision__date__lte=fecha_fin)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calcular estadísticas
        total_facturas = queryset.count()
        facturas_pendientes = queryset.filter(estado='pendiente').count()
        facturas_pagadas = queryset.filter(estado='pagada').count()
        facturas_canceladas = queryset.filter(estado='cancelada').count()
        
        monto_total_facturado = queryset.aggregate(
            total=Sum('monto_total')
        )['total'] or 0
        
        monto_total_pagado = queryset.aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        monto_pendiente = monto_total_facturado - monto_total_pagado
        
        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                'fecha_fin': fecha_fin.isoformat() if fecha_fin else None
            },
            'resumen': {
                'total_facturas': total_facturas,
                'facturas_pendientes': facturas_pendientes,
                'facturas_pagadas': facturas_pagadas,
                'facturas_canceladas': facturas_canceladas,
                'monto_total_facturado': float(monto_total_facturado),
                'monto_total_pagado': float(monto_total_pagado),
                'monto_pendiente': float(monto_pendiente),
                'porcentaje_cobrado': round(
                    (monto_total_pagado / monto_total_facturado * 100) if monto_total_facturado > 0 else 0,
                    2
                )
            }
        })


class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos
    - Admins: Ven todos los pagos del tenant
    - Doctores: Ven pagos de facturas de sus pacientes
    - Pacientes: Solo ven sus propios pagos
    """
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'create':
            return PagoCreateSerializer
        return PagoSerializer
    
    def get_queryset(self):
        """Filtrar pagos según tipo de usuario"""
        user = self.request.user
        queryset = Pago.objects.all().select_related('factura', 'factura__paciente')
        
        # Admin ve todos los pagos
        if user.is_staff:
            return queryset
        
        # Doctor ve pagos de facturas de sus pacientes
        if hasattr(user, 'perfilprofesional'):
            # Obtener pacientes del doctor
            pacientes_ids = PerfilPaciente.objects.filter(
                historialclinico__episodioatencion__doctor=user.perfilprofesional
            ).values_list('id', flat=True).distinct()
            return queryset.filter(factura__paciente_id__in=pacientes_ids)
        
        # Paciente solo ve sus pagos
        if hasattr(user, 'perfilpaciente'):
            return queryset.filter(factura__paciente=user.perfilpaciente)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Registrar nuevo pago"""
        factura = serializer.validated_data['factura']
        
        # Verificar que la factura no esté cancelada
        if factura.estado == 'cancelada':
            raise serializers.ValidationError(
                "No se pueden registrar pagos en facturas canceladas"
            )
        
        # Verificar que no se exceda el monto total
        monto = serializer.validated_data['monto_pagado']
        nuevo_monto_pagado = factura.monto_pagado + monto
        
        if nuevo_monto_pagado > factura.total:
            raise serializers.ValidationError(
                f"El pago excede el saldo pendiente. "
                f"Máximo permitido: ${factura.saldo_pendiente:.2f}"
            )
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular pago (solo admin)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo los administradores pueden anular pagos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pago = self.get_object()
        
        if pago.estado_pago == 'CANCELADO':
            return Response(
                {'error': 'El pago ya está anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Anular pago
        pago.estado_pago = 'CANCELADO'
        pago.save()
        
        return Response({
            'message': 'Pago anulado exitosamente',
            'pago': self.get_serializer(pago).data
        })
    
    @action(detail=False, methods=['get'])
    def por_factura(self, request):
        """Obtener pagos de una factura específica"""
        factura_id = request.query_params.get('factura_id')
        
        if not factura_id:
            return Response(
                {'error': 'El parámetro factura_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar que el usuario tenga acceso a esta factura
            factura = Factura.objects.get(id=factura_id)
            factura_queryset = FacturaViewSet().get_queryset()
            
            if not factura_queryset.filter(id=factura_id).exists():
                return Response(
                    {'error': 'No tiene permisos para ver esta factura'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            pagos = self.get_queryset().filter(
                factura_id=factura_id
            ).exclude(estado_pago='CANCELADO').order_by('-fecha_pago')
            
            return Response({
                'factura': {
                    'id': factura.id,
                    'numero': factura.numero,
                    'total': float(factura.monto_total),
                    'monto_pagado': float(factura.monto_pagado),
                    'saldo_pendiente': float(factura.saldo_pendiente)
                },
                'pagos': self.get_serializer(pagos, many=True).data,
                'total_pagos': pagos.count(),
                'suma_pagos': float(sum(p.monto_pagado for p in pagos))
            })
            
        except Factura.DoesNotExist:
            return Response(
                {'error': 'Factura no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
