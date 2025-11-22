"""
Signals para registrar automáticamente acciones en la bitácora.

NOTA: Los signals de user_logged_in y user_logged_out no funcionan con JWT.
El registro de login se hace directamente en CustomTokenObtainPairView.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reportes.models import BitacoraAccion


# Los signals de login/logout están desactivados porque se usa JWT
# El registro de login se hace en usuarios.jwt_views.CustomTokenObtainPairView

# @receiver(user_logged_in)
# def registrar_login(sender, request, user, **kwargs):
#     """Registra cuando un usuario inicia sesión."""
#     pass

# @receiver(user_logged_out)
# def registrar_logout(sender, request, user, **kwargs):
#     """Registra cuando un usuario cierra sesión."""
#     pass


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
