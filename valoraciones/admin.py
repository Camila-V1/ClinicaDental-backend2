from django.contrib import admin
from .models import Valoracion


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'paciente',
        'odontologo',
        'calificacion',
        'puntualidad',
        'trato',
        'limpieza',
        'created_at',
        'notificacion_enviada'
    ]
    list_filter = [
        'calificacion',
        'notificacion_enviada',
        'created_at',
        'odontologo'
    ]
    search_fields = [
        'paciente__nombre',
        'paciente__apellido',
        'paciente__email',
        'odontologo__nombre',
        'odontologo__apellido',
        'comentario'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'notificacion_enviada',
        'notificacion_enviada_at',
        'calificacion_promedio_aspectos'
    ]
    fieldsets = (
        ('Información General', {
            'fields': ('cita', 'paciente', 'odontologo')
        }),
        ('Calificaciones', {
            'fields': (
                'calificacion',
                'puntualidad',
                'trato',
                'limpieza',
                'calificacion_promedio_aspectos'
            )
        }),
        ('Comentario', {
            'fields': ('comentario',)
        }),
        ('Metadatos', {
            'fields': (
                'created_at',
                'updated_at',
                'notificacion_enviada',
                'notificacion_enviada_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def calificacion_promedio_aspectos(self, obj):
        """Mostrar el promedio de aspectos en el admin"""
        promedio = obj.calificacion_promedio_aspectos
        if promedio:
            return f"{promedio:.2f} ⭐"
        return "N/A"
    calificacion_promedio_aspectos.short_description = "Promedio Aspectos"
