"""
URL configuration for the PUBLIC schema (localhost).
This handles administration of tenants/clinics.
"""
from django.contrib.admin import AdminSite
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# Create a custom admin site for the public schema
class PublicAdminSite(AdminSite):
    site_header = "Administración del Sistema Multi-Tenant"
    site_title = "Admin del Sistema"
    index_title = "Gestión de Clínicas"


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
