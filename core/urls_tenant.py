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
from rest_framework_simplejwt.views import TokenRefreshView
from usuarios.jwt_views import CustomTokenObtainPairView

urlpatterns = [
    # Admin panel for TENANT (clinic staff)
    # Shows: Usuarios, Agenda, Tratamientos, Facturacion, etc.
    path('admin/', admin.site.urls),
    
    # JWT authentication endpoints (for tenant users)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes for tenant operations
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),
    path('api/historial/', include('historial_clinico.urls')),
    path('api/tratamientos/', include('tratamientos.urls')),
    path('api/facturacion/', include('facturacion.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/reportes/', include('reportes.urls')),
    path('api/backups/', include('backups.urls')),  # Sistema de backups
    path('api/chatbot/', include('chatbot.urls')),  # Chatbot asistente
    path('api/', include('valoraciones.urls')),  # Sistema de valoraciones
]
