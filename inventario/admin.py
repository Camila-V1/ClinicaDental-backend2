from django.contrib import admin
from django.db import connection
from .models import CategoriaInsumo, Insumo


@admin.register(CategoriaInsumo)
class CategoriaInsumoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Categorías de Insumos.
    """
    list_display = ('nombre', 'total_insumos', 'activo', 'creado')
    list_filter = ('activo', 'creado')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Metadatos', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado', 'actualizado')
    
    def total_insumos(self, obj):
        """Muestra cuántos insumos tiene esta categoría."""
        return obj.insumos.count()
    total_insumos.short_description = 'Total Insumos'
    
    def get_queryset(self, request):
        """Solo mostrar en admin de tenants, no en public."""
        qs = super().get_queryset(request)
        if connection.schema_name == 'public':
            return qs.none()
        return qs


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Insumos.
    """
    list_display = (
        'codigo',
        'nombre',
        'categoria',
        'precio_venta',
        'stock_actual',
        'stock_status',
        'activo'
    )
    list_filter = ('categoria', 'activo', 'creado')
    search_fields = ('codigo', 'nombre', 'descripcion', 'proveedor')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('categoria', 'codigo', 'nombre', 'descripcion', 'activo')
        }),
        ('Precios', {
            'fields': ('precio_costo', 'precio_venta')
        }),
        ('Control de Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'unidad_medida')
        }),
        ('Proveedor', {
            'fields': ('proveedor',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado', 'actualizado')
    
    def stock_status(self, obj):
        """Muestra el estado del stock con un indicador visual."""
        if obj.requiere_reposicion:
            return '⚠️ Bajo'
        return '✅ OK'
    stock_status.short_description = 'Estado Stock'
    
    def get_queryset(self, request):
        """Solo mostrar en admin de tenants, no en public."""
        qs = super().get_queryset(request)
        if connection.schema_name == 'public':
            return qs.none()
        return qs.select_related('categoria')
