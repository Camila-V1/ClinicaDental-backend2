"""
URL configuration for the PUBLIC schema (localhost).
This handles administration of tenants/clinics.

IMPORTANT: PublicAdminSite does NOT require authentication because
usuarios.Usuario only exists in tenant schemas, not in public schema.
"""
from django.contrib.admin import AdminSite
from django.urls import path, include
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def health_check(request):
    """Endpoint de salud para verificar que el backend está funcionando"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Backend de Clínica Dental funcionando correctamente',
        'schema': 'public',
        'endpoints': {
            'admin': '/admin/',
            'api_tenants': '/api/tenants/',
        }
    })


def api_root(request):
    """Root API endpoint para el schema público"""
    return JsonResponse({
        'message': 'API de Clínica Dental - Schema Público',
        'version': '1.0',
        'endpoints': {
            'health': '/',
            'admin': '/admin/',
            'tenants': '/api/tenants/',
        },
        'note': 'Para acceder a las APIs de clínicas específicas, usa el subdominio correspondiente'
    })


# Create a custom admin site for the public schema WITHOUT authentication
class PublicAdminSite(AdminSite):
    site_header = "Administración del Sistema Multi-Tenant"
    site_title = "Admin del Sistema"
    index_title = "Gestión de Clínicas"
    index_template = 'admin_public/index.html'  # Custom template
    
    # Disable login requirement for public admin
    # WARNING: In production, implement HTTP Basic Auth or restrict network access
    def has_permission(self, request):
        """
        Allow access without authentication.
        
        SECURITY NOTE: This admin only manages Clinics and Domains.
        For production, consider:
        - HTTP Basic Authentication at web server level
        - VPN/IP restriction
        - Separate management interface with proper auth
        """
        return True
    
    def login(self, request, extra_context=None):
        """
        Redirect to admin index since we don't use authentication.
        """
        return redirect('admin:index')
    
    def each_context(self, request):
        """
        Override to avoid accessing user-related context that might query usuarios_usuario.
        """
        from django.urls import reverse
        from django.utils.text import capfirst
        from django.utils.translation import gettext_lazy as _
        
        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': reverse('admin:index', current_app=self.name) if self.site_url == '/' else self.site_url,
            'has_permission': True,  # Always true for public admin
            'available_apps': [],  # Will be populated by index()
            'is_popup': False,
            'is_nav_sidebar_enabled': True,
            'log_entries': [],  # Empty to avoid querying django_admin_log
        }
    
    def get_app_list(self, request, app_label=None):
        """
        Override to safely get app list without querying django_admin_log.
        """
        from django.contrib.admin import site as default_site
        from django.urls import reverse, NoReverseMatch
        from django.utils.text import capfirst
        
        app_dict = {}
        
        # Only iterate over models registered in THIS admin site
        for model, model_admin in self._registry.items():
            app_label_local = model._meta.app_label
            
            has_module_perms = True  # No permission check for public admin
            
            if has_module_perms:
                perms = {
                    'add': True,
                    'change': True,
                    'delete': True,
                    'view': True,
                }
                
                # Check whether user has any perm for this module.
                if True in perms.values():
                    info = (app_label_local, model._meta.model_name)
                    model_dict = {
                        'model': model,
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                        'admin_url': None,
                        'add_url': None,
                    }
                    
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                    except NoReverseMatch:
                        pass
                    
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    
                    if app_label_local in app_dict:
                        app_dict[app_label_local]['models'].append(model_dict)
                    else:
                        app_dict[app_label_local] = {
                            'name': model._meta.app_config.verbose_name if hasattr(model._meta, 'app_config') else app_label_local.title(),
                            'app_label': app_label_local,
                            'app_url': None,
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }
        
        if app_label:
            return app_dict.get(app_label)
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Override index to avoid loading admin logs (django_admin_log table doesn't exist in public schema).
        """
        from django.template.response import TemplateResponse
        from django.utils.text import capfirst
        
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            # Don't include 'recent_actions' to avoid querying django_admin_log
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        
        return TemplateResponse(request, self.index_template or 'admin/index.html', context)


# Instantiate the public admin site
public_admin = PublicAdminSite(name='public_admin')

# Register public models (tenants) with basic ModelAdmin (not custom admins)
from tenants.models import Clinica, Domain
from django.contrib.admin import ModelAdmin

# Use basic ModelAdmin to avoid any permission checks
class SimpleClinicaAdmin(ModelAdmin):
    list_display = ['nombre', 'schema_name', 'activo']
    search_fields = ['nombre', 'schema_name']

class SimpleDomainAdmin(ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    search_fields = ['domain']

public_admin.register(Clinica, SimpleClinicaAdmin)
public_admin.register(Domain, SimpleDomainAdmin)


urlpatterns = [
    # Health check
    path('', health_check, name='health'),
    path('api/', api_root, name='api_root'),
    
    # JWT authentication endpoints (redirect to tenant)
    # Note: These will work if accessing via tenant subdomain
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Public admin for managing tenants
    path('admin/', public_admin.urls),
    
    # API for tenant management (public)
    path('api/tenants/', include('tenants.urls')),
]
