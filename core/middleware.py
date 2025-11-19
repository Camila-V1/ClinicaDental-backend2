"""
Middleware personalizado para routing inteligente de tenants
"""
from django.db import connection
from django.conf import settings
import os


class DefaultTenantMiddleware:
    """
    Middleware que fuerza el uso de un tenant por defecto cuando se accede
    al dominio público sin subdominio.
    
    Esto permite que el frontend pueda hacer login directamente a:
    https://clinica-dental-backend.onrender.com/api/v1/token/
    
    Y automáticamente usará el schema del tenant por defecto (clinica_demo).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Tenant por defecto desde variable de entorno o 'clinica_demo'
        self.default_tenant_schema = os.environ.get('DEFAULT_TENANT_SCHEMA', 'clinica_demo')
    
    def __call__(self, request):
        # Solo aplicar para requests a /api/ (no admin ni estáticos)
        if request.path.startswith('/api/'):
            # Obtener el hostname actual
            hostname = request.get_host().split(':')[0]  # Remover puerto si existe
            
            # Lista de dominios públicos (sin tenant)
            public_domains = [
                'localhost',
                '127.0.0.1',
                os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'clinica-dental-backend.onrender.com')
            ]
            
            # Si el hostname es un dominio público (sin subdominio de tenant)
            if hostname in public_domains:
                # Verificar que no estemos ya en el schema público
                if connection.schema_name == 'public':
                    # Forzar el uso del tenant por defecto
                    from tenants.models import Clinica
                    try:
                        default_tenant = Clinica.objects.get(schema_name=self.default_tenant_schema)
                        connection.set_tenant(default_tenant)
                        
                        # Marcar el request como usando tenant por defecto
                        request.using_default_tenant = True
                        
                    except Clinica.DoesNotExist:
                        # Si no existe el tenant por defecto, continuar con public
                        pass
        
        response = self.get_response(request)
        return response
