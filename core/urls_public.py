"""
URL configuration for the PUBLIC schema (localhost).
This handles administration of tenants/clinics.

IMPORTANT: PublicAdminSite does NOT require authentication because
usuarios.Usuario only exists in tenant schemas, not in public schema.
"""
from django.contrib.admin import AdminSite
from django.urls import path, include
from django.shortcuts import redirect


# Create a custom admin site for the public schema WITHOUT authentication
class PublicAdminSite(AdminSite):
    site_header = "Administración del Sistema Multi-Tenant"
    site_title = "Admin del Sistema"
    index_title = "Gestión de Clínicas"
    
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
            'available_apps': self.get_app_list(request),
            'is_popup': False,
            'is_nav_sidebar_enabled': True,
            'log_entries': [],  # Empty to avoid querying django_admin_log
        }
    
    def index(self, request, extra_context=None):
        """
        Override index to avoid loading admin logs (django_admin_log table doesn't exist in public schema).
        """
        from django.template.response import TemplateResponse
        
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

# Register public models (tenants)
from tenants.models import Clinica, Domain
from tenants.admin import ClinicaAdmin, DomainAdmin

public_admin.register(Clinica, ClinicaAdmin)
public_admin.register(Domain, DomainAdmin)

# Also register Django's built-in Group model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

public_admin.register(Group, GroupAdmin)


urlpatterns = [
    # Public admin for managing tenants
    path('admin/', public_admin.urls),
    
    # API for tenant management (public)
    path('api/tenants/', include('tenants.urls')),
]
