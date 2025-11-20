"""
Admin configuration for Tenants app.

IMPORTANT: Clinica and Domain models should ONLY be registered in the PUBLIC admin.
They should NOT appear in tenant admin sites.

This file is intentionally left minimal to avoid registering these models
in the standard admin.site (which is used by tenant schemas).

The registration happens in core/urls_public.py using PublicAdminSite.
"""

from django.contrib import admin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from .models import Clinica, Domain, PlanSuscripcion, SolicitudRegistro

# DO NOT REGISTER THESE MODELS HERE!
# They are registered in core/urls_public.py for the public schema only.

# If you need admin classes for the public admin, define them here
# but DON'T use @admin.register decorator


class ClinicaAdmin(admin.ModelAdmin):
    """Admin for Clinica model - Used ONLY in PublicAdminSite"""
    list_display = (
        'nombre', 'dominio', 'plan', 'estado', 'esta_activa', 
        'dias_restantes', 'fecha_inicio', 'fecha_expiracion', 'creado'
    )
    list_filter = ('estado', 'plan', 'activo', 'ciudad', 'pais')
    search_fields = ('nombre', 'dominio', 'email_admin', 'ciudad')
    readonly_fields = ('schema_name', 'creado', 'actualizado', 'esta_activa', 'dias_restantes')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('schema_name', 'nombre', 'dominio', 'activo')
        }),
        ('Suscripción', {
            'fields': ('plan', 'estado', 'fecha_inicio', 'fecha_expiracion')
        }),
        ('Contacto', {
            'fields': ('email_admin', 'telefono', 'direccion', 'ciudad', 'pais')
        }),
        ('Estado', {
            'fields': ('esta_activa', 'dias_restantes', 'notas')
        }),
        ('Fechas', {
            'fields': ('creado', 'actualizado')
        })
    )
    
    actions = ['activar_plan_action', 'renovar_suscripcion_action', 'suspender_action']
    
    def activar_plan_action(self, request, queryset):
        """Activar plan para las clínicas seleccionadas."""
        for clinica in queryset:
            if clinica.plan and clinica.estado == 'PENDIENTE':
                clinica.activar_plan(clinica.plan)
                self.message_user(
                    request,
                    f"Plan activado para {clinica.nombre}",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    f"No se puede activar {clinica.nombre} - verificar estado y plan",
                    messages.WARNING
                )
    
    activar_plan_action.short_description = "Activar plan de suscripción"
    
    def renovar_suscripcion_action(self, request, queryset):
        """Renovar suscripción para las clínicas seleccionadas."""
        for clinica in queryset:
            try:
                clinica.renovar_suscripcion()
                self.message_user(
                    request,
                    f"Suscripción renovada para {clinica.nombre}",
                    messages.SUCCESS
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error renovando {clinica.nombre}: {str(e)}",
                    messages.ERROR
                )
    
    renovar_suscripcion_action.short_description = "Renovar suscripción"
    
    def suspender_action(self, request, queryset):
        """Suspender clínicas seleccionadas."""
        for clinica in queryset:
            clinica.suspender("Suspendido desde el panel de administración")
            self.message_user(
                request,
                f"Clínica {clinica.nombre} suspendida",
                messages.SUCCESS
            )
    
    suspender_action.short_description = "Suspender clínicas"


class DomainAdmin(admin.ModelAdmin):
    """Admin for Domain model - Used ONLY in PublicAdminSite"""
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__nombre')


class PlanSuscripcionAdmin(admin.ModelAdmin):
    """Admin for PlanSuscripcion model - Used ONLY in PublicAdminSite"""
    list_display = (
        'nombre', 'get_tipo_display', 'precio', 'duracion_dias',
        'max_usuarios', 'max_pacientes', 'activo'
    )
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'descripcion')
    
    fieldsets = (
        ('Información del Plan', {
            'fields': ('nombre', 'tipo', 'descripcion', 'activo')
        }),
        ('Precio y Duración', {
            'fields': ('precio', 'duracion_dias')
        }),
        ('Límites', {
            'fields': ('max_usuarios', 'max_pacientes', 'max_almacenamiento_mb')
        }),
        ('Características', {
            'fields': ('permite_reportes', 'permite_integraciones', 'soporte_prioritario')
        })
    )
    
    def get_tipo_display(self, obj):
        return obj.get_tipo_display()
    
    get_tipo_display.short_description = 'Tipo de Plan'


class SolicitudRegistroAdmin(admin.ModelAdmin):
    """Admin for SolicitudRegistro model - Used ONLY in PublicAdminSite"""
    list_display = (
        'nombre_clinica', 'dominio_deseado', 'nombre_contacto',
        'email', 'plan_solicitado', 'estado', 'creada', 'procesada'
    )
    list_filter = ('estado', 'plan_solicitado', 'pais', 'creada')
    search_fields = ('nombre_clinica', 'dominio_deseado', 'email', 'nombre_contacto')
    readonly_fields = ('creada', 'revisada', 'procesada', 'clinica_creada')
    
    fieldsets = (
        ('Información de la Clínica', {
            'fields': ('nombre_clinica', 'dominio_deseado', 'plan_solicitado')
        }),
        ('Datos de Contacto', {
            'fields': ('nombre_contacto', 'email', 'telefono', 'cargo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais')
        }),
        ('Estado de la Solicitud', {
            'fields': ('estado', 'motivo_rechazo', 'clinica_creada')
        }),
        ('Fechas', {
            'fields': ('creada', 'revisada', 'procesada')
        })
    )
    
    actions = ['aprobar_solicitud', 'rechazar_solicitud']
    
    def aprobar_solicitud(self, request, queryset):
        """Aprobar solicitudes seleccionadas y crear las clínicas."""
        for solicitud in queryset:
            if solicitud.estado != 'PENDIENTE':
                self.message_user(
                    request,
                    f"Solicitud {solicitud.nombre_clinica} no está pendiente",
                    messages.WARNING
                )
                continue
            
            try:
                with transaction.atomic():
                    # Crear schema_name único
                    schema_name = f"tenant_{solicitud.dominio_deseado.replace('-', '_')}"
                    
                    # Crear la clínica (tenant)
                    clinica = Clinica.objects.create(
                        schema_name=schema_name,
                        nombre=solicitud.nombre_clinica,
                        dominio=solicitud.dominio_deseado,
                        email_admin=solicitud.email,
                        telefono=solicitud.telefono,
                        direccion=solicitud.direccion,
                        ciudad=solicitud.ciudad,
                        pais=solicitud.pais,
                        plan=solicitud.plan_solicitado,
                        estado='PENDIENTE',
                        activo=False
                    )
                    
                    # Crear el dominio
                    Domain.objects.create(
                        domain=f"{solicitud.dominio_deseado}.localhost",
                        tenant=clinica,
                        is_primary=True
                    )
                    
                    # Si estás en producción
                    if not settings.DEBUG and hasattr(settings, 'RENDER_EXTERNAL_HOSTNAME'):
                        Domain.objects.create(
                            domain=f"{solicitud.dominio_deseado}.{settings.RENDER_EXTERNAL_HOSTNAME}",
                            tenant=clinica,
                            is_primary=False
                        )
                    
                    # Actualizar solicitud
                    solicitud.estado = 'PROCESADA'
                    solicitud.clinica_creada = clinica
                    solicitud.revisada = timezone.now()
                    solicitud.procesada = timezone.now()
                    solicitud.save()
                    
                    self.message_user(
                        request,
                        f"Solicitud aprobada: Clínica '{clinica.nombre}' creada exitosamente",
                        messages.SUCCESS
                    )
                    
            except Exception as e:
                self.message_user(
                    request,
                    f"Error procesando {solicitud.nombre_clinica}: {str(e)}",
                    messages.ERROR
                )
    
    aprobar_solicitud.short_description = "Aprobar solicitudes y crear clínicas"
    
    def rechazar_solicitud(self, request, queryset):
        """Rechazar solicitudes seleccionadas."""
        # Esta acción necesita un formulario personalizado para el motivo
        # Por ahora, usamos un motivo genérico
        motivo = "Solicitud rechazada desde el panel de administración"
        
        for solicitud in queryset:
            if solicitud.estado != 'PENDIENTE':
                self.message_user(
                    request,
                    f"Solicitud {solicitud.nombre_clinica} no está pendiente",
                    messages.WARNING
                )
                continue
            
            solicitud.estado = 'RECHAZADA'
            solicitud.motivo_rechazo = motivo
            solicitud.revisada = timezone.now()
            solicitud.save()
            
            self.message_user(
                request,
                f"Solicitud rechazada: {solicitud.nombre_clinica}",
                messages.SUCCESS
            )
    
    rechazar_solicitud.short_description = "Rechazar solicitudes"
