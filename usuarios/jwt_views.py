"""
Serializers personalizados para JWT con registro de bitácora.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from reportes.models import BitacoraAccion


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado que registra el login en la bitácora.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Registrar login en bitácora
        request = self.context.get('request')
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
        
        BitacoraAccion.registrar(
            usuario=self.user,
            accion='LOGIN',
            descripcion=f'Inicio de sesión exitoso - {self.user.full_name}',
            detalles={
                'email': self.user.email,
                'tipo_usuario': self.user.tipo_usuario
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return data
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT con registro de bitácora.
    """
    serializer_class = CustomTokenObtainPairSerializer
