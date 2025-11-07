# facturacion/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Factura, Pago

class PagoInline(admin.TabularInline):
    """Muestra los pagos dentro del admin de la Factura."""
    model = Pago
    extra = 0
    fields = ('fecha_pago', 'monto_pagado', 'metodo_pago', 'estado_pago', 'referencia_transaccion', 'notas')
    readonly_fields = ('fecha_pago',)
    
    def get_queryset(self, request):
        """Optimizar consultas para el inline."""
        return super().get_queryset(request).select_related('paciente__usuario')

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'paciente_info', 'presupuesto_link', 'estado_badge', 
        'monto_total', 'monto_pagado', 'saldo_pendiente', 'fecha_emision'
    )
    list_filter = ('estado', 'fecha_emision', 'fecha_anulacion')
    search_fields = (
        'id', 'paciente__usuario__email', 'paciente__usuario__nombre', 
        'paciente__usuario__apellido', 'paciente__usuario__ci', 'nit_ci', 'razon_social'
    )
    autocomplete_fields = ['paciente', 'presupuesto']
    readonly_fields = ('monto_pagado', 'saldo_pendiente', 'fecha_emision', 'fecha_anulacion')
    list_per_page = 25
    date_hierarchy = 'fecha_emision'
    
    fieldsets = (
        ('Información General', {
            'fields': ('paciente', 'presupuesto', 'estado')
        }),
        ('Datos de Facturación (CU31)', {
            'fields': ('nit_ci', 'razon_social'),
            'classes': ('collapse',)
        }),
        ('Montos', {
            'fields': ('monto_total', 'monto_pagado', 'saldo_pendiente'),
            'classes': ('wide',)
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_anulacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PagoInline]
    
    def paciente_info(self, obj):
        """Muestra información del paciente con enlace."""
        if obj.paciente:
            url = reverse('admin:usuarios_perfilpaciente_change', args=[obj.paciente.pk])
            return format_html(
                '<a href="{}">{}</a><br><small>{}</small>',
                url,
                obj.paciente.usuario.full_name,
                obj.paciente.usuario.email
            )
        return "Sin paciente"
    paciente_info.short_description = "Paciente"
    paciente_info.admin_order_field = "paciente__usuario__apellido"
    
    def presupuesto_link(self, obj):
        """Muestra enlace al presupuesto."""
        if obj.presupuesto:
            url = reverse('admin:tratamientos_presupuesto_change', args=[obj.presupuesto.pk])
            return format_html('<a href="{}">Presupuesto #{}</a>', url, obj.presupuesto.id)
        return "Sin presupuesto"
    presupuesto_link.short_description = "Presupuesto"
    
    def estado_badge(self, obj):
        """Muestra el estado con colores."""
        colors = {
            'PENDIENTE': 'orange',
            'PAGADA': 'green',
            'ANULADA': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado"
    
    actions = ['recalcular_montos_pagados', 'anular_facturas']
    
    def recalcular_montos_pagados(self, request, queryset):
        """Acción para recalcular montos pagados."""
        for factura in queryset:
            factura.recalcular_monto_pagado()
        self.message_user(request, f'{queryset.count()} factura(s) recalculada(s).')
    recalcular_montos_pagados.short_description = "Recalcular montos pagados"
    
    def anular_facturas(self, request, queryset):
        """Acción para anular facturas."""
        from django.utils import timezone
        count = queryset.filter(estado='PENDIENTE').update(
            estado='ANULADA',
            fecha_anulacion=timezone.now()
        )
        self.message_user(request, f'{count} factura(s) anulada(s).')
    anular_facturas.short_description = "Anular facturas seleccionadas"


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'factura_link', 'paciente_info', 'monto_pagado', 
        'metodo_pago', 'estado_pago', 'fecha_pago'
    )
    list_filter = ('metodo_pago', 'estado_pago', 'fecha_pago')
    search_fields = (
        'id', 'factura__id', 'paciente__usuario__email', 'paciente__usuario__nombre',
        'paciente__usuario__apellido', 'referencia_transaccion'
    )
    autocomplete_fields = ['factura', 'paciente']
    readonly_fields = ('fecha_pago',)
    list_per_page = 50
    date_hierarchy = 'fecha_pago'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('factura', 'paciente', 'monto_pagado')
        }),
        ('Detalles del Pago', {
            'fields': ('metodo_pago', 'estado_pago', 'referencia_transaccion'),
            'classes': ('wide',)
        }),
        ('Información Adicional', {
            'fields': ('notas', 'fecha_pago'),
            'classes': ('collapse',)
        }),
    )
    
    # Permitir editar el estado directamente desde la lista
    list_editable = ('estado_pago',)
    
    def factura_link(self, obj):
        """Enlace a la factura."""
        if obj.factura:
            url = reverse('admin:facturacion_factura_change', args=[obj.factura.pk])
            return format_html(
                '<a href="{}">Factura #{}</a><br><small>Bs. {}</small>',
                url,
                obj.factura.id,
                obj.factura.monto_total
            )
        return "Sin factura"
    factura_link.short_description = "Factura"
    factura_link.admin_order_field = "factura__id"
    
    def paciente_info(self, obj):
        """Información del paciente."""
        if obj.paciente:
            return format_html(
                '{}<br><small>{}</small>',
                obj.paciente.usuario.full_name,
                obj.paciente.usuario.email
            )
        return "Sin paciente"
    paciente_info.short_description = "Paciente"
    
    def estado_badge(self, obj):
        """Estado del pago con colores."""
        colors = {
            'PENDIENTE': 'orange',
            'COMPLETADO': 'green',
            'FALLIDO': 'red',
            'CANCELADO': 'gray'
        }
        color = colors.get(obj.estado_pago, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_pago_display()
        )
    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado_pago"
    
    actions = ['marcar_completados', 'marcar_fallidos']
    
    def marcar_completados(self, request, queryset):
        """Marca pagos como completados."""
        count = 0
        for pago in queryset.filter(estado_pago='PENDIENTE'):
            pago.marcar_completado()
            count += 1
        self.message_user(request, f'{count} pago(s) marcado(s) como completado(s).')
    marcar_completados.short_description = "Marcar como completados"
    
    def marcar_fallidos(self, request, queryset):
        """Marca pagos como fallidos."""
        count = queryset.filter(estado_pago='PENDIENTE').update(estado_pago='FALLIDO')
        self.message_user(request, f'{count} pago(s) marcado(s) como fallido(s).')
    marcar_fallidos.short_description = "Marcar como fallidos"
