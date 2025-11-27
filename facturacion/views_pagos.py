"""
Views para pagos con Stripe de citas y tratamientos.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from .models import Pago, Factura
from .serializers import PagoSerializer
from agenda.models import Cita
from tratamientos.models import PlanDeTratamiento
from usuarios.models import PerfilPaciente
from tenants.payment_handlers import get_payment_handler


class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos con Stripe.
    """
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Si es paciente, solo sus pagos
        if hasattr(user, 'perfil_paciente'):
            return Pago.objects.filter(paciente=user.perfil_paciente)
        
        # Admin y odontólogos ven todos
        return Pago.objects.all()
    
    @action(detail=False, methods=['post'], url_path='crear-pago-cita')
    def crear_pago_cita(self, request):
        """
        Crear pago para una cita.
        
        POST /api/facturacion/pagos/crear-pago-cita/
        {
            "cita_id": 5,
            "monto": 50.00,
            "metodo_pago": "STRIPE",
            "return_url": "http://localhost:5173/citas/pago-exitoso",
            "cancel_url": "http://localhost:5173/citas/pago-cancelado"
        }
        """
        cita_id = request.data.get('cita_id')
        monto = Decimal(str(request.data.get('monto', 0)))
        metodo_pago = request.data.get('metodo_pago', 'STRIPE')
        return_url = request.data.get('return_url')
        cancel_url = request.data.get('cancel_url')
        
        if not cita_id or monto <= 0:
            return Response(
                {'error': 'Datos inválidos. Proporciona cita_id y monto válidos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        if hasattr(user, 'perfil_paciente'):
            if cita.paciente.id != user.perfil_paciente.id:
                return Response(
                    {'error': 'No tienes permiso para pagar esta cita'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            with transaction.atomic():
                # Crear registro de pago
                pago = Pago.objects.create(
                    cita=cita,
                    paciente=cita.paciente,
                    tipo_pago=Pago.TipoPago.CITA,
                    monto_pagado=monto,
                    metodo_pago=metodo_pago,
                    estado_pago=Pago.EstadoPago.PROCESANDO,
                )
                
                # Crear pago en Stripe
                handler = get_payment_handler(metodo_pago)
                
                # Crear objeto temporal para payment handler
                class PagoTemp:
                    def __init__(self, pago_obj, cita_obj):
                        self.id = pago_obj.id
                        self.monto_pagado = pago_obj.monto_pagado
                        self.descripcion = f"Pago de Cita #{cita_obj.id} - {cita_obj.odontologo.usuario.full_name}"
                
                pago_temp = PagoTemp(pago, cita)
                result = handler.create_payment(pago_temp, return_url, cancel_url)
                
                if not result.get('success'):
                    pago.delete()
                    return Response(
                        {'error': result.get('error', 'Error creando pago')},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Actualizar pago con datos de Stripe
                pago.transaccion_id = result['payment_id']
                pago.datos_pago = result
                pago.save()
                
                return Response({
                    'pago_id': pago.id,
                    'payment_url': result['payment_url'],
                    'session_id': result['payment_id'],
                    'message': 'Redirige al usuario a payment_url'
                })
        
        except Exception as e:
            return Response(
                {'error': f'Error procesando pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='crear-pago-tratamiento')
    def crear_pago_tratamiento(self, request):
        """
        Crear pago para un tratamiento individual.
        """
        # Implementación similar a crear_pago_cita
        return Response({'message': 'Implementar lógica de pago de tratamiento'})
    
    @action(detail=False, methods=['post'], url_path='crear-pago-plan')
    def crear_pago_plan(self, request):
        """
        Crear pago para plan de tratamiento.
        
        POST /api/facturacion/pagos/crear-pago-plan/
        {
            "plan_tratamiento_id": 8,
            "monto": 500.00,
            "metodo_pago": "STRIPE",
            "tipo_pago": "COMPLETO",
            "return_url": "...",
            "cancel_url": "..."
        }
        """
        plan_id = request.data.get('plan_tratamiento_id')
        monto = Decimal(str(request.data.get('monto', 0)))
        metodo_pago = request.data.get('metodo_pago', 'STRIPE')
        tipo_pago_plan = request.data.get('tipo_pago', 'COMPLETO')
        return_url = request.data.get('return_url')
        cancel_url = request.data.get('cancel_url')
        
        if not plan_id or monto <= 0:
            return Response(
                {'error': 'Datos inválidos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plan = PlanDeTratamiento.objects.get(id=plan_id)
        except PlanDeTratamiento.DoesNotExist:
            return Response(
                {'error': 'Plan de tratamiento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        if hasattr(user, 'perfil_paciente'):
            if plan.paciente.id != user.perfil_paciente.id:
                return Response(
                    {'error': 'No tienes permiso para pagar este plan'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            with transaction.atomic():
                # Crear registro de pago
                pago = Pago.objects.create(
                    plan_tratamiento=plan,
                    paciente=plan.paciente,
                    tipo_pago=Pago.TipoPago.PLAN,
                    monto_pagado=monto,
                    metodo_pago=metodo_pago,
                    estado_pago=Pago.EstadoPago.PROCESANDO,
                    notas=f"Tipo de pago: {tipo_pago_plan}"
                )
                
                # Crear pago en Stripe
                handler = get_payment_handler(metodo_pago)
                
                class PagoTemp:
                    def __init__(self, pago_obj, plan_obj):
                        self.id = pago_obj.id
                        self.monto_pagado = pago_obj.monto_pagado
                        self.descripcion = f"Plan de Tratamiento #{plan_obj.id} - {plan_obj.descripcion[:50]}"
                
                pago_temp = PagoTemp(pago, plan)
                result = handler.create_payment(pago_temp, return_url, cancel_url)
                
                if not result.get('success'):
                    pago.delete()
                    return Response(
                        {'error': result.get('error')},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Actualizar pago
                pago.transaccion_id = result['payment_id']
                pago.datos_pago = result
                pago.save()
                
                return Response({
                    'pago_id': pago.id,
                    'payment_url': result['payment_url'],
                    'session_id': result['payment_id'],
                    'message': 'Redirige al usuario a payment_url'
                })
        
        except Exception as e:
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post', 'get'], url_path='confirmar')
    def confirmar_pago(self, request, pk=None):
        """
        Confirmar pago después del checkout de Stripe.
        
        POST /api/facturacion/pagos/{id}/confirmar/
        GET  /api/facturacion/pagos/{id}/confirmar/?session_id=cs_xxx
        """
        pago = self.get_object()
        
        if pago.estado_pago not in [Pago.EstadoPago.PROCESANDO, Pago.EstadoPago.PENDIENTE]:
            return Response({
                'message': 'Pago ya procesado',
                'estado': pago.estado_pago,
                'pago_id': pago.id
            })
        
        # Obtener session_id
        session_id = request.GET.get('session_id') or request.data.get('session_id') or pago.transaccion_id
        
        if not session_id:
            return Response(
                {'error': 'No se proporcionó session_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar pago con Stripe
            handler = get_payment_handler(pago.metodo_pago)
            success, payment_data = handler.verify_payment(session_id)
            
            if success:
                with transaction.atomic():
                    pago.estado_pago = Pago.EstadoPago.COMPLETADO
                    pago.fecha_completado = timezone.now()
                    pago.payment_intent_id = payment_data.get('payment_intent')
                    pago.datos_pago.update(payment_data)
                    pago.save()
                    
                    # Marcar cita como pagada si aplica
                    if pago.cita:
                        pago.cita.pagada = True
                        pago.cita.save()
                
                return Response({
                    'success': True,
                    'pago_id': pago.id,
                    'estado': pago.estado_pago,
                    'monto': float(pago.monto_pagado),
                    'transaccion_id': pago.transaccion_id,
                    'message': 'Pago procesado exitosamente'
                })
            else:
                pago.estado_pago = Pago.EstadoPago.FALLIDO
                pago.datos_pago.update(payment_data)
                pago.save()
                
                return Response({
                    'success': False,
                    'error': 'Pago no exitoso',
                    'detalles': payment_data
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        except Exception as e:
            pago.estado_pago = Pago.EstadoPago.FALLIDO
            pago.notas = f"Error: {str(e)}"
            pago.save()
            
            return Response(
                {'error': f'Error verificando pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='estado')
    def verificar_estado(self, request, pk=None):
        """
        Verificar estado de un pago.
        
        GET /api/facturacion/pagos/{id}/estado/
        """
        pago = self.get_object()
        
        data = {
            'pago_id': pago.id,
            'estado': pago.estado_pago,
            'monto': float(pago.monto_pagado),
            'fecha_pago': pago.fecha_pago,
            'metodo_pago': pago.metodo_pago,
            'transaccion_id': pago.transaccion_id,
        }
        
        if pago.cita:
            data['relacionado'] = {
                'tipo': 'cita',
                'id': pago.cita.id,
                'descripcion': pago.descripcion
            }
        elif pago.plan_tratamiento:
            data['relacionado'] = {
                'tipo': 'plan',
                'id': pago.plan_tratamiento.id,
                'descripcion': pago.descripcion
            }
        
        return Response(data)
