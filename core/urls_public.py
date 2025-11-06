"""
URL configuration for the PUBLIC schema (localhost).
This handles administration of tenants/clinics.

IMPORTANT: PublicAdminSite does NOT require authentication because
usuarios.Usuario only exists in tenant schemas, not in public schema.
"""
from django.contrib.admin import AdminSite
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


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
    
    # JWT authentication endpoints (public)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
