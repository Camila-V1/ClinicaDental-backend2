"""
Middleware personalizado para routing inteligente de tenants
"""
from django.db import connection, models
from django.conf import settings
import os


class DefaultTenantMiddleware:
    """
    Middleware que detecta el tenant basado en el header X-Tenant-ID.
    
    Flujo:
    1. Frontend detecta subdominio (ej: clinicaabc.dentaabcxy.store)
    2. Frontend extrae tenant ID (clinicaabc) y envía header: X-Tenant-ID: clinicaabc
    3. Backend busca el tenant con dominio 'clinicaabc'
    4. Backend cambia al schema correspondiente
    
    Fallback: Si no hay header X-Tenant-ID, usa el tenant por defecto (clinica_demo).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Tenant por defecto si no se especifica
        self.default_tenant_schema = os.environ.get('DEFAULT_TENANT_SCHEMA', 'clinica_demo')
    
    def __call__(self, request):
        # Obtener el hostname actual
        hostname = request.get_host().split(':')[0]
        
        # Lista de dominios públicos (sin tenant específico)
        public_domains = [
            'localhost',
            '127.0.0.1',
            os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'clinica-dental-backend.onrender.com'),
            'api.dentaabcxy.store',  # Dominio custom API
        ]
        
        # Si es un dominio público Y estamos en schema public, cambiar al tenant
        if hostname in public_domains and connection.schema_name == 'public':
            # Intentar obtener tenant desde header personalizado
            tenant_id = request.headers.get('X-Tenant-ID', '').lower()
            
            # Si viene 'clinicademo1', usar 'clinica_demo' (mismo schema)
            if tenant_id == 'clinicademo1':
                tenant_id = 'clinica_demo'
            
            if not tenant_id:
                # Si no hay header, usar el por defecto
                tenant_id = self.default_tenant_schema
            
            # Buscar el tenant
            from tenants.models import Clinica
            try:
                tenant = Clinica.objects.filter(
                    models.Q(dominio=tenant_id) | 
                    models.Q(schema_name=tenant_id)
                ).first()
                
                if tenant:
                    connection.set_tenant(tenant)
                    request.using_tenant = tenant_id
                else:
                    # Si no existe, usar el por defecto
                    default_tenant = Clinica.objects.filter(schema_name=self.default_tenant_schema).first()
                    if default_tenant:
                        connection.set_tenant(default_tenant)
                        request.using_default_tenant = True
                    
            except Exception as e:
                # Log error pero continuar
                import logging
                logging.error(f"Error en DefaultTenantMiddleware: {e}")
        
        response = self.get_response(request)
        return response
