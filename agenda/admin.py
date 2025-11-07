from django.contrib import admin
from .models import Cita
from usuarios.models import PerfilPaciente, PerfilOdontologo


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Cita.
    """
    list_display = [
        'fecha_hora',
        'get_paciente_nombre',
        'get_odontologo_nombre',
        'estado',
        'motivo_corto'
    ]
    list_filter = ['estado', 'fecha_hora', 'odontologo']
    search_fields = [
        'paciente__usuario__nombre',
        'paciente__usuario__apellido',
        'odontologo__usuario__nombre',
        'odontologo__usuario__apellido',
        'motivo'
    ]
    date_hierarchy = 'fecha_hora'
    ordering = ['-fecha_hora']
    
    fieldsets = (
        ('Información de la Cita', {
            'fields': ('paciente', 'odontologo', 'fecha_hora', 'motivo')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        }),
        ('Metadatos', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado', 'actualizado')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtrar los campos de ForeignKey para mostrar solo perfiles válidos.
        """
        if db_field.name == "paciente":
            # Mostrar solo perfiles de paciente que existen
            kwargs["queryset"] = PerfilPaciente.objects.select_related('usuario').all()
        if db_field.name == "odontologo":
            # Mostrar solo perfiles de odontólogo que existen
            kwargs["queryset"] = PerfilOdontologo.objects.select_related('usuario').all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_paciente_nombre(self, obj):
        """Retorna el nombre completo del paciente"""
        return f"{obj.paciente.usuario.nombre} {obj.paciente.usuario.apellido}"
    get_paciente_nombre.short_description = 'Paciente'
    get_paciente_nombre.admin_order_field = 'paciente__usuario__nombre'
    
    def get_odontologo_nombre(self, obj):
        """Retorna el nombre completo del odontólogo"""
        return f"{obj.odontologo.usuario.nombre} {obj.odontologo.usuario.apellido}"
    get_odontologo_nombre.short_description = 'Odontólogo'
    get_odontologo_nombre.admin_order_field = 'odontologo__usuario__nombre'
    
    def motivo_corto(self, obj):
        """Retorna los primeros 50 caracteres del motivo"""
        if len(obj.motivo) > 50:
            return f"{obj.motivo[:50]}..."
        return obj.motivo
    motivo_corto.short_description = 'Motivo'
