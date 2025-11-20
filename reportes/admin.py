from django.contrib import admin
from .models import BitacoraAccion


@admin.register(BitacoraAccion)
class BitacoraAccionAdmin(admin.ModelAdmin):
    """
    Administración de la bitácora de acciones.
    """
    list_display = [
        'id',
        'fecha_hora',
        'usuario',
        'accion',
        'descripcion_corta',
        'modelo',
        'ip_address'
    ]
    list_filter = [
        'accion',
        'fecha_hora',
        'content_type'
    ]
    search_fields = [
        'descripcion',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__email',
        'ip_address'
    ]
    readonly_fields = [
        'id',
        'usuario',
        'accion',
        'content_type',
        'object_id',
        'descripcion',
        'detalles',
        'fecha_hora',
        'ip_address',
        'user_agent'
    ]
    date_hierarchy = 'fecha_hora'
    ordering = ['-fecha_hora']
    
    def descripcion_corta(self, obj):
        """Muestra descripción truncada"""
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def modelo(self, obj):
        """Muestra el nombre del modelo"""
        return obj.content_type.model if obj.content_type else 'N/A'
    modelo.short_description = 'Modelo'
    
    def has_add_permission(self, request):
        """No permitir crear registros manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros (auditoría)"""
        return False

