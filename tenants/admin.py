"""
Admin configuration for Tenants app.

IMPORTANT: Clinica and Domain models should ONLY be registered in the PUBLIC admin.
They should NOT appear in tenant admin sites.

This file is intentionally left minimal to avoid registering these models
in the standard admin.site (which is used by tenant schemas).

The registration happens in core/urls_public.py using PublicAdminSite.
"""

from django.contrib import admin
from .models import Clinica, Domain

# DO NOT REGISTER THESE MODELS HERE!
# They are registered in core/urls_public.py for the public schema only.

# If you need admin classes for the public admin, define them here
# but DON'T use @admin.register decorator

class ClinicaAdmin(admin.ModelAdmin):
    """Admin for Clinica model - Used ONLY in PublicAdminSite"""
    list_display = ('nombre', 'dominio', 'activo', 'creado')
    list_filter = ('activo',)
    search_fields = ('nombre', 'dominio')


class DomainAdmin(admin.ModelAdmin):
    """Admin for Domain model - Used ONLY in PublicAdminSite"""
    list_display = ('domain', 'tenant')
