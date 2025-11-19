"""
URL Configuration for TENANT Schemas (Clinics)

This URLconf is used by django-tenants for all tenant schemas (clinic subdomains).
Examples: clinica-demo.localhost, clinica-abc.localhost

IMPORTANT: This file uses the STANDARD admin.site.urls, which will show only
tenant-specific models (usuarios, agenda, tratamientos, etc.)

The public schema (localhost) uses core.urls_public instead.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin panel for TENANT (clinic staff)
    # Shows: Usuarios, Agenda, Tratamientos, Facturacion, etc.
    path('admin/', admin.site.urls),
    
    # JWT authentication endpoints (for tenant users) - API v1
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes for tenant operations - API v1
    path('api/v1/usuarios/', include('usuarios.urls')),
    path('api/v1/agenda/', include('agenda.urls')),
    path('api/v1/historial/', include('historial_clinico.urls')),
    path('api/v1/tratamientos/', include('tratamientos.urls')),
    path('api/v1/facturacion/', include('facturacion.urls')),
    path('api/v1/inventario/', include('inventario.urls')),
    path('api/v1/reportes/', include('reportes.urls')),
]
