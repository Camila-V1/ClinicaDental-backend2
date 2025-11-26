from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponse
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
from django.contrib.auth import get_user_model
from .payment_handlers import get_payment_handler
import secrets
import string
from datetime import timedelta

User = get_user_model()


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
    ViewSet para gestionar solicitudes de registro con PAGO AUTOMÁTICO.
    
    Flujo:
    1. POST /solicitudes/ - Crear solicitud (público)
    2. POST /solicitudes/{id}/iniciar_pago/ - Iniciar pago (público, con método de pago)
    3. POST /solicitudes/{id}/confirmar_pago/ - Webhook/callback de pasarela (público)
    4. GET /solicitudes/{id}/descargar_credenciales/?token=xxx - Descargar archivo .txt (público con token)
    """
    queryset = SolicitudRegistro.objects.all()
    serializer_class = SolicitudRegistroSerializer
    
    def get_permissions(self):
        """Permitir acciones públicas con token, admin para listar."""
        if self.action in ['create', 'iniciar_pago', 'confirmar_pago', 'verificar_estado', 'descargar_credenciales']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva solicitud de registro (PASO 1)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Generar token de descarga (válido 24h después del pago)
        solicitud.token_descarga = secrets.token_urlsafe(32)
        solicitud.save()
        
        return Response(
            {
                'message': 'Solicitud creada. Procede con el pago.',
                'solicitud_id': solicitud.id,
                'token': solicitud.token_descarga,
                'siguiente_paso': f'/api/tenants/solicitudes/{solicitud.id}/iniciar_pago/',
                'datos': SolicitudRegistroSerializer(solicitud).data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def iniciar_pago(self, request, pk=None):
        """Iniciar proceso de pago (PASO 2)."""
        solicitud = self.get_object()
        
        if solicitud.estado not in ['PENDIENTE_PAGO', 'PAGO_FALLIDO']:
            return Response(
                {'error': 'Esta solicitud ya no está disponible para pago'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        metodo_pago = request.data.get('metodo_pago', 'STRIPE')
        
        if metodo_pago not in dict(SolicitudRegistro.METODO_PAGO_CHOICES):
            return Response(
                {'error': 'Método de pago no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # URLs de retorno
        base_url = request.build_absolute_uri('/').rstrip('/')
        return_url = request.data.get('return_url', f"{base_url}/registro/exito/{solicitud.id}")
        cancel_url = request.data.get('cancel_url', f"{base_url}/registro/cancelado")
        
        try:
            # Obtener handler de pago
            handler = get_payment_handler(metodo_pago)
            
            # Crear pago en la pasarela
            result = handler.create_payment(solicitud, return_url, cancel_url)
            
            if not result.get('success'):
                return Response(
                    {'error': result.get('error', 'Error creando pago')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Actualizar solicitud
            solicitud.metodo_pago = metodo_pago
            solicitud.estado = 'PAGO_PROCESANDO'
            solicitud.transaccion_id = result['payment_id']
            solicitud.datos_pago = result
            solicitud.save()
            
            return Response({
                'message': 'Pago iniciado. Redirige al usuario a payment_url',
                'payment_url': result['payment_url'],
                'payment_id': result['payment_id'],
                'solicitud_id': solicitud.id,
            })
        
        except Exception as e:
            return Response(
                {'error': f'Error iniciando pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post', 'get'], permission_classes=[AllowAny])
    def confirmar_pago(self, request, pk=None):
        """Confirmar pago y crear clínica automáticamente (PASO 3 - Webhook/Callback)."""
        solicitud = self.get_object()
        
        if solicitud.estado not in ['PAGO_PROCESANDO', 'PENDIENTE_PAGO']:
            return Response({
                'message': 'Pago ya procesado',
                'estado': solicitud.estado,
                'solicitud_id': solicitud.id
            })
        
        # Obtener ID de transacción (puede venir en query params o body)
        payment_id = request.GET.get('session_id') or request.GET.get('payment_id') or request.data.get('payment_id') or solicitud.transaccion_id
        
        if not payment_id:
            return Response(
                {'error': 'No se proporcionó payment_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar pago con la pasarela
            handler = get_payment_handler(solicitud.metodo_pago)
            success, payment_data = handler.verify_payment(payment_id, request.data)
            
            if success:
                # PAGO EXITOSO - CREAR CLÍNICA AUTOMÁTICAMENTE
                with transaction.atomic():
                    solicitud.estado = 'PAGO_EXITOSO'
                    solicitud.pago_exitoso = True
                    solicitud.fecha_pago = timezone.now()
                    solicitud.monto_pagado = solicitud.plan_solicitado.precio
                    solicitud.datos_pago.update(payment_data)
                    solicitud.save()
                    
                    # Crear clínica y usuario admin
                    clinica, credenciales = self._crear_clinica_automatica(solicitud)
                    
                    # Actualizar solicitud con credenciales
                    solicitud.estado = 'COMPLETADA'
                    solicitud.clinica_creada = clinica
                    solicitud.usuario_admin_generado = credenciales['email']
                    solicitud.password_admin_generado = credenciales['password']
                    solicitud.procesada = timezone.now()
                    solicitud.token_expira = timezone.now() + timedelta(days=7)  # Token válido 7 días
                    solicitud.save()
                    
                    # Enviar email con link de descarga
                    self._enviar_email_credenciales(solicitud)
                
                return Response({
                    'message': '¡Pago exitoso! Clínica creada automáticamente.',
                    'solicitud_id': solicitud.id,
                    'clinica_id': clinica.id,
                    'clinica_nombre': clinica.nombre,
                    'dominio': clinica.dominio,
                    'download_url': f"/api/tenants/solicitudes/{solicitud.id}/descargar_credenciales/?token={solicitud.token_descarga}",
                    'token': solicitud.token_descarga,
                    'credenciales_nota': 'Descarga el archivo con tus credenciales usando el link proporcionado'
                })
            else:
                # Pago fallido
                solicitud.estado = 'PAGO_FALLIDO'
                solicitud.datos_pago.update(payment_data)
                solicitud.save()
                
                return Response({
                    'error': 'Pago no exitoso',
                    'detalles': payment_data,
                    'solicitud_id': solicitud.id
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        except Exception as e:
            solicitud.estado = 'PAGO_FALLIDO'
            solicitud.motivo_rechazo = str(e)
            solicitud.save()
            
            return Response(
                {'error': f'Error verificando pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def verificar_estado(self, request, pk=None):
        """Verificar estado de la solicitud (público)."""
        solicitud = self.get_object()
        
        data = {
            'solicitud_id': solicitud.id,
            'estado': solicitud.estado,
            'estado_display': solicitud.get_estado_display(),
            'pago_exitoso': solicitud.pago_exitoso,
            'fecha_pago': solicitud.fecha_pago,
        }
        
        if solicitud.estado == 'COMPLETADA':
            data.update({
                'clinica_nombre': solicitud.clinica_creada.nombre if solicitud.clinica_creada else None,
                'dominio': solicitud.clinica_creada.dominio if solicitud.clinica_creada else None,
                'credenciales_disponibles': bool(solicitud.usuario_admin_generado and solicitud.password_admin_generado),
                'token_valido': solicitud.token_expira > timezone.now() if solicitud.token_expira else False,
            })
        
        return Response(data)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def descargar_credenciales(self, request, pk=None):
        """Descargar archivo TXT con credenciales (requiere token)."""
        solicitud = self.get_object()
        token = request.GET.get('token')
        
        # Verificar token
        if not token or token != solicitud.token_descarga:
            return Response(
                {'error': 'Token inválido o faltante'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que esté completada
        if solicitud.estado != 'COMPLETADA':
            return Response(
                {'error': 'La solicitud aún no está completada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar expiración
        if solicitud.token_expira and timezone.now() > solicitud.token_expira:
            return Response(
                {'error': 'El token ha expirado. Contacta con soporte.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que existan credenciales
        if not solicitud.usuario_admin_generado or not solicitud.password_admin_generado:
            return Response(
                {'error': 'Credenciales no disponibles'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generar archivo TXT
        clinica = solicitud.clinica_creada
        contenido = f"""
╔══════════════════════════════════════════════════════════════╗
║                   CREDENCIALES DE ACCESO                      ║
║                    CLÍNICA DENTAL SYSTEM                      ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DE LA CLÍNICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nombre:           {clinica.nombre}
  Dominio:          {clinica.dominio}
  Plan:             {clinica.plan.nombre}
  Fecha Creación:   {clinica.creado.strftime('%d/%m/%Y %H:%M')}
  Expira:           {clinica.fecha_expiracion.strftime('%d/%m/%Y') if clinica.fecha_expiracion else 'N/A'}

🔐 CREDENCIALES DE ADMINISTRADOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usuario/Email:    {solicitud.usuario_admin_generado}
  Contraseña:       {solicitud.password_admin_generado}

🌐 URLS DE ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Panel Admin:      {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/admin/
  API:              {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/api/

💳 INFORMACIÓN DEL PAGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Método:           {solicitud.get_metodo_pago_display()}
  Monto:            ${solicitud.monto_pagado}
  Transacción ID:   {solicitud.transaccion_id}
  Fecha:            {solicitud.fecha_pago.strftime('%d/%m/%Y %H:%M')}

⚠️  IMPORTANTE - LEE ESTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. CAMBIA LA CONTRASEÑA inmediatamente después del primer acceso
  2. Este archivo contiene información sensible - guárdalo en un lugar seguro
  3. No compartas estas credenciales con nadie
  4. Puedes descargar este archivo solo hasta: {solicitud.token_expira.strftime('%d/%m/%Y %H:%M') if solicitud.token_expira else 'N/A'}
  5. Si tienes problemas, contacta a soporte: {settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'soporte@clinica.com'}

📞 SOPORTE TÉCNICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Email: {settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'soporte@clinica.com'}
  
¡Bienvenido a Clínica Dental System!

Generado: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
ID Solicitud: {solicitud.id}
""".strip()
        
        # Marcar como descargado
        if not solicitud.credenciales_descargadas:
            solicitud.credenciales_descargadas = True
            solicitud.fecha_descarga_credenciales = timezone.now()
            solicitud.save()
        
        # Retornar archivo TXT
        response = HttpResponse(contenido, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="credenciales_{clinica.dominio}_{timezone.now().strftime("%Y%m%d")}.txt"'
        
        return response
    
    def _crear_clinica_automatica(self, solicitud):
        """Crear clínica, schema, dominio y usuario admin automáticamente."""
        # Generar contraseña segura
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        
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
            estado='ACTIVA',
            activo=True
        )
        
        # Activar el plan
        clinica.activar_plan()
        
        # Crear dominio principal
        Domain.objects.create(
            domain=f"{solicitud.dominio_deseado}.localhost",
            tenant=clinica,
            is_primary=True
        )
        
        # Si está en producción, agregar dominio de producción
        if not settings.DEBUG and hasattr(settings, 'RENDER_EXTERNAL_HOSTNAME'):
            Domain.objects.create(
                domain=f"{solicitud.dominio_deseado}.{settings.RENDER_EXTERNAL_HOSTNAME}",
                tenant=clinica,
                is_primary=False
            )
        
        # Crear usuario administrador en el schema del tenant
        from django.db import connection
        from django_tenants.utils import schema_context
        
        with schema_context(clinica.schema_name):
            admin_user = User.objects.create_user(
                username=solicitud.email.split('@')[0],
                email=solicitud.email,
                password=password,
                first_name=solicitud.nombre_contacto.split()[0] if solicitud.nombre_contacto else 'Admin',
                last_name=' '.join(solicitud.nombre_contacto.split()[1:]) if len(solicitud.nombre_contacto.split()) > 1 else '',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            # Crear perfil de usuario si existe el modelo
            try:
                from usuarios.models import Perfil
                Perfil.objects.create(
                    usuario=admin_user,
                    rol='ADMIN',
                    telefono=solicitud.telefono,
                    direccion=solicitud.direccion,
                    ciudad=solicitud.ciudad,
                    pais=solicitud.pais
                )
            except ImportError:
                pass  # Modelo Perfil no existe
        
        return clinica, {
            'email': solicitud.email,
            'password': password,
            'username': solicitud.email.split('@')[0]
        }
    
    def _enviar_email_credenciales(self, solicitud):
        """Enviar email con link de descarga de credenciales."""
        base_url = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
        download_url = f"https://{base_url}/api/tenants/solicitudes/{solicitud.id}/descargar_credenciales/?token={solicitud.token_descarga}"
        
        asunto = f"¡Tu clínica {solicitud.nombre_clinica} está lista!"
        mensaje = f"""
Hola {solicitud.nombre_contacto},

¡Excelentes noticias! Tu pago ha sido procesado exitosamente y tu clínica "{solicitud.clinica_creada.nombre}" está lista para usar.

📥 DESCARGA TUS CREDENCIALES:
{download_url}

⚠️ IMPORTANTE:
- El link de descarga es válido hasta: {solicitud.token_expira.strftime('%d/%m/%Y %H:%M') if solicitud.token_expira else 'N/A'}
- Descarga el archivo TXT con tus credenciales de acceso
- Cambia la contraseña inmediatamente después del primer acceso
- Guarda el archivo en un lugar seguro

📋 Detalles de tu clínica:
- Nombre: {solicitud.clinica_creada.nombre}
- Dominio: {solicitud.clinica_creada.dominio}
- Plan: {solicitud.plan_solicitado.nombre}
- Válido hasta: {solicitud.clinica_creada.fecha_expiracion.strftime('%d/%m/%Y') if solicitud.clinica_creada.fecha_expiracion else 'N/A'}

Si tienes alguna pregunta, no dudes en contactarnos.

¡Bienvenido a Clínica Dental System!

Saludos,
El equipo de Clínica Dental
"""
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@clinica.com',
            [solicitud.email],
            fail_silently=True
        )
    
    # Métodos antiguos removidos (aprobar/rechazar manual)


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
