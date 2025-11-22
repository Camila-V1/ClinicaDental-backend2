"""
Signals para registrar automáticamente acciones en la bitácora.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reportes.models import BitacoraAccion


@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    """Registra cuando un usuario inicia sesión."""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    BitacoraAccion.registrar(
        usuario=user,
        accion='LOGIN',
        descripcion=f'Inicio de sesión exitoso - {user.full_name}',
        detalles={
            'email': user.email,
            'tipo_usuario': user.tipo_usuario
        },
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    """Registra cuando un usuario cierra sesión."""
    if user:
        ip_address = get_client_ip(request)
        
        BitacoraAccion.registrar(
            usuario=user,
            accion='LOGOUT',
            descripcion=f'Cierre de sesión - {user.full_name}',
            detalles={'email': user.email},
            ip_address=ip_address
        )


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
