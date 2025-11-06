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

urlpatterns = [
    # Admin panel for TENANT (clinic staff)
    # Shows: Usuarios, Agenda, Tratamientos, Facturacion, etc.
    path('admin/', admin.site.urls),
    
    # API routes for tenant operations
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),
    path('api/historial/', include('historial_clinico.urls')),
    path('api/tratamientos/', include('tratamientos.urls')),
    path('api/facturacion/', include('facturacion.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/reportes/', include('reportes.urls')),
]
