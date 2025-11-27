"""
Serializers personalizados para JWT con registro de bitácora.
"""

import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from reportes.models import BitacoraAccion
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado que registra el login en la bitácora.
    """
    
    def validate(self, attrs):
        email = attrs.get('email', 'N/A')
        password = attrs.get('password', 'N/A')
        
        logger.info("="*70)
        logger.info("🔐 [JWT LOGIN] Intento de autenticación")
        logger.info(f"   📧 Email recibido: {email}")
        logger.info(f"   🔑 Password recibido: {'*' * len(password)} ({len(password)} caracteres)")
        
        request = self.context.get('request')
        if request:
            logger.info(f"   🌐 Host: {request.META.get('HTTP_HOST', 'N/A')}")
            logger.info(f"   📍 IP: {self.get_client_ip(request)}")
            logger.info(f"   🖥️  User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:100]}")
        
        # Intentar autenticación manual para logging
        try:
            from django_tenants.utils import get_tenant_model
            from django.db import connection
            
            logger.info(f"   🏢 Schema actual: {connection.schema_name}")
            logger.info(f"   🔍 Buscando usuario con email: {email}")
            
            # Llamar al validate del padre (hace authenticate internamente)
            data = super().validate(attrs)
            
            logger.info("   ✅ Autenticación EXITOSA")
            logger.info(f"   👤 Usuario autenticado: {self.user.email}")
            logger.info(f"   🆔 Usuario ID: {self.user.id}")
            logger.info(f"   👔 Tipo: {self.user.tipo_usuario}")
            logger.info("="*70)
            
        except Exception as e:
            logger.error("   ❌ Autenticación FALLIDA")
            logger.error(f"   ⚠️  Error: {str(e)}")
            logger.error(f"   📝 Tipo de error: {type(e).__name__}")
            logger.error("="*70)
            raise
        
        # Registrar login en bitácora
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
