from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from .models import PlanSuscripcion, SolicitudRegistro, Clinica, Domain
from .serializers import (
    PlanSuscripcionSerializer,
    SolicitudRegistroSerializer,
    ClinicaPublicSerializer,
    ClinicaAdminSerializer
)
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


class PlanSuscripcionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet público para ver planes de suscripción disponibles.
    Solo lectura, cualquiera puede verlos.
    """
    queryset = PlanSuscripcion.objects.filter(activo=True)
    serializer_class = PlanSuscripcionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Ordenar planes por precio."""
        return self.queryset.order_by('precio')


class SolicitudRegistroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar solicitudes de registro de clínicas.
    
    - POST (crear): Público - cualquiera puede solicitar
    - GET (listar/detalle): Solo admin
    - PATCH/PUT: Solo admin para aprobar/rechazar
    """
    queryset = SolicitudRegistro.objects.all()
    serializer_class = SolicitudRegistroSerializer
    
    def get_permissions(self):
        """Permitir POST público, el resto requiere admin."""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva solicitud de registro."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Enviar email de confirmación al solicitante
        try:
            self._enviar_email_confirmacion(solicitud)
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        # Enviar notificación a administradores
        try:
            self._notificar_admin_nueva_solicitud(solicitud)
        except Exception as e:
            print(f"Error enviando notificación admin: {e}")
        
        return Response(
            {
                'message': 'Solicitud enviada exitosamente. Te contactaremos pronto.',
                'solicitud': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def aprobar(self, request, pk=None):
        """Aprobar una solicitud y crear la clínica."""
        solicitud = self.get_object()
        
        if solicitud.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden aprobar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Crear la clínica
                clinica = self._crear_clinica_desde_solicitud(solicitud)
                
                # Actualizar solicitud
                solicitud.estado = 'PROCESADA'
                solicitud.clinica_creada = clinica
                solicitud.revisada = timezone.now()
                solicitud.procesada = timezone.now()
                solicitud.save()
                
                # Enviar email con credenciales
                self._enviar_email_clinica_creada(solicitud, clinica)
            
            return Response({
                'message': 'Solicitud aprobada y clínica creada exitosamente',
                'clinica': ClinicaPublicSerializer(clinica).data
            })
        
        except Exception as e:
            return Response(
                {'error': f'Error al crear clínica: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def rechazar(self, request, pk=None):
        """Rechazar una solicitud."""
        solicitud = self.get_object()
        
        if solicitud.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden rechazar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get('motivo', '')
        if not motivo:
            return Response(
                {'error': 'Debe proporcionar un motivo de rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = 'RECHAZADA'
        solicitud.motivo_rechazo = motivo
        solicitud.revisada = timezone.now()
        solicitud.save()
        
        # Enviar email informando rechazo
        self._enviar_email_rechazo(solicitud)
        
        return Response({
            'message': 'Solicitud rechazada',
            'solicitud': SolicitudRegistroSerializer(solicitud).data
        })
    
    def _crear_clinica_desde_solicitud(self, solicitud):
        """Crear clínica y dominio desde una solicitud aprobada."""
        # Crear schema_name único
        schema_name = f"tenant_{solicitud.dominio_deseado.replace('-', '_')}"
        
        # Crear la clínica (tenant)
        clinica = Clinica.objects.create(
            schema_name=schema_name,
            nombre=solicitud.nombre_clinica,
            dominio=solicitud.dominio_deseado,
            email_admin=solicitud.email,
            telefono=solicitud.telefono,
            direccion=solicitud.direccion,
            ciudad=solicitud.ciudad,
            pais=solicitud.pais,
            plan=solicitud.plan_solicitado,
            estado='PENDIENTE',
            activo=False  # Se activará cuando procesen el pago
        )
        
        # Crear el dominio principal
        Domain.objects.create(
            domain=f"{solicitud.dominio_deseado}.localhost",  # En dev
            tenant=clinica,
            is_primary=True
        )
        
        # Si estás en producción, agregar también el dominio de producción
        if not settings.DEBUG:
            Domain.objects.create(
                domain=f"{solicitud.dominio_deseado}.{settings.RENDER_EXTERNAL_HOSTNAME}",
                tenant=clinica,
                is_primary=False
            )
        
        return clinica
    
    def _enviar_email_confirmacion(self, solicitud):
        """Enviar email de confirmación al solicitante."""
        asunto = "Solicitud de registro recibida - Clínica Dental"
        mensaje = f"""
        Hola {solicitud.nombre_contacto},
        
        Hemos recibido tu solicitud para crear la clínica "{solicitud.nombre_clinica}".
        
        Detalles de la solicitud:
        - Dominio: {solicitud.dominio_deseado}
        - Plan: {solicitud.plan_solicitado.nombre}
        - Email: {solicitud.email}
        
        Nuestro equipo revisará tu solicitud y te contactaremos pronto.
        
        Gracias por tu interés.
        
        Saludos,
        El equipo de Clínica Dental
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [solicitud.email],
            fail_silently=True
        )
    
    def _notificar_admin_nueva_solicitud(self, solicitud):
        """Notificar a los admins sobre nueva solicitud."""
        asunto = f"Nueva solicitud de registro: {solicitud.nombre_clinica}"
        mensaje = f"""
        Nueva solicitud de registro recibida:
        
        Clínica: {solicitud.nombre_clinica}
        Dominio: {solicitud.dominio_deseado}
        Contacto: {solicitud.nombre_contacto}
        Email: {solicitud.email}
        Teléfono: {solicitud.telefono}
        Plan: {solicitud.plan_solicitado.nombre}
        
        Revisa la solicitud en el panel de administración.
        """
        
        # Enviar a los admins configurados
        admin_emails = [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') else []
        if admin_emails:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True
            )
    
    def _enviar_email_clinica_creada(self, solicitud, clinica):
        """Enviar email cuando la clínica es creada."""
        asunto = "¡Tu clínica ha sido aprobada!"
        mensaje = f"""
        Hola {solicitud.nombre_contacto},
        
        ¡Buenas noticias! Tu solicitud ha sido aprobada y tu clínica "{clinica.nombre}" ha sido creada.
        
        Detalles de acceso:
        - URL: {solicitud.dominio_deseado}.{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}
        - Email: {solicitud.email}
        
        El siguiente paso es activar tu plan "{clinica.plan.nombre}" por ${clinica.plan.precio}.
        
        Te contactaremos para coordinar el pago y activación.
        
        ¡Bienvenido a bordo!
        
        Saludos,
        El equipo de Clínica Dental
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [solicitud.email],
            fail_silently=True
        )
    
    def _enviar_email_rechazo(self, solicitud):
        """Enviar email cuando la solicitud es rechazada."""
        asunto = "Actualización sobre tu solicitud"
        mensaje = f"""
        Hola {solicitud.nombre_contacto},
        
        Lamentamos informarte que tu solicitud para crear "{solicitud.nombre_clinica}" no ha sido aprobada.
        
        Motivo: {solicitud.motivo_rechazo}
        
        Si tienes preguntas o deseas discutir esto, por favor contáctanos.
        
        Saludos,
        El equipo de Clínica Dental
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [solicitud.email],
            fail_silently=True
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def info_registro(request):
    """
    Endpoint público que retorna información sobre el proceso de registro.
    """
    planes = PlanSuscripcion.objects.filter(activo=True).order_by('precio')
    
    return Response({
        'mensaje': 'Bienvenido al sistema de registro de clínicas',
        'pasos': [
            '1. Selecciona un plan de suscripción',
            '2. Completa el formulario de registro',
            '3. Espera la aprobación de tu solicitud',
            '4. Realiza el pago del plan seleccionado',
            '5. Accede a tu clínica con las credenciales proporcionadas'
        ],
        'planes_disponibles': PlanSuscripcionSerializer(planes, many=True).data,
        'contacto': {
            'email': settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'contacto@clinica.com',
            'mensaje': 'Para más información, contáctanos'
        }
    })


def index(request):
    """Vista pública del dominio raíz."""
    data = list(Clinica.objects.values('id', 'nombre', 'dominio', 'activo'))
    return JsonResponse({'clinicas': data})
