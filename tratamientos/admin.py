from django.contrib import admin
from django.utils import timezone
from .models import (
    CategoriaServicio, Servicio, 
    MaterialServicioFijo, MaterialServicioOpcional,
    PlanDeTratamiento, ItemPlanTratamiento,
    Presupuesto, ItemPresupuesto  # Nuevos modelos del Paso 2.D
)


# ===============================================================================
# PASO 2.B: INLINES PARA LA "RECETA" DE SERVICIOS
# ===============================================================================

class MaterialServicioFijoInline(admin.TabularInline):
    """
    Permite editar Materiales Fijos dentro del admin de Servicio.
    Estos son insumos que SIEMPRE se usan para un servicio específico.
    """
    model = MaterialServicioFijo
    extra = 1  # Muestra 1 slot vacío por defecto
    fields = ('insumo', 'cantidad', 'es_obligatorio', 'notas')
    autocomplete_fields = ['insumo']  # Usa un buscador para los insumos
    verbose_name = "Material Fijo"
    verbose_name_plural = "Materiales Fijos (siempre se usan)"


class MaterialServicioOpcionalInline(admin.TabularInline):
    """
    Permite editar Materiales Opcionales dentro del admin de Servicio.
    Estos son categorías donde se debe ELEGIR un insumo específico.
    """
    model = MaterialServicioOpcional
    extra = 1
    fields = ('categoria_insumo', 'cantidad', 'nombre_personalizado', 'es_obligatorio', 'notas')
    autocomplete_fields = ['categoria_insumo']
    verbose_name = "Material Opcional"
    verbose_name_plural = "Materiales Opcionales (a elegir)"


@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    """
    Administración de categorías de servicios odontológicos.
    """
    list_display = [
        'nombre', 
        'activo', 
        'orden', 
        'cantidad_servicios',
        'creado'
    ]
    list_filter = ['activo', 'creado']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'orden']
    ordering = ['orden', 'nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('activo', 'orden'),
            'classes': ('collapse',)
        }),
    )

    def cantidad_servicios(self, obj):
        """Muestra la cantidad de servicios en esta categoría"""
        return obj.servicios.count()
    cantidad_servicios.short_description = 'Servicios'


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    """
    Administración del catálogo de servicios odontológicos.
    """
    list_display = [
        'codigo_servicio',
        'nombre',
        'categoria',
        'precio_base',
        'duracion_formateada',
        'activo',
        'requiere_cita_previa'
    ]
    list_filter = [
        'categoria',
        'activo',
        'requiere_cita_previa',
        'requiere_autorizacion',
        'creado'
    ]
    search_fields = [
        'codigo_servicio',
        'nombre', 
        'descripcion',
        'categoria__nombre'
    ]
    list_editable = ['activo']
    ordering = ['categoria', 'codigo_servicio']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_servicio', 'nombre', 'categoria', 'descripcion')
        }),
        ('Precio y Tiempo', {
            'fields': ('precio_base', 'tiempo_estimado'),
            'classes': ('wide',)
        }),
        ('Configuración del Servicio', {
            'fields': (
                'requiere_cita_previa', 
                'requiere_autorizacion', 
                'activo'
            ),
            'classes': ('collapse',)
        }),
        ('Notas Internas', {
            'fields': ('notas_internas',),
            'classes': ('collapse',)
        }),
    )
    
    # Filtros laterales mejorados
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('categoria')
    
    # --- PASO 2.B: AÑADIR LAS RECETAS AL ADMIN ---
    inlines = [
        MaterialServicioFijoInline,
        MaterialServicioOpcionalInline
    ]
    
    # Acción personalizada para activar/desactivar servicios
    actions = ['activar_servicios', 'desactivar_servicios']
    
    @admin.action(description='Activar servicios seleccionados')
    def activar_servicios(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} servicios activados correctamente.')
    
    @admin.action(description='Desactivar servicios seleccionados')
    def desactivar_servicios(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} servicios desactivados correctamente.')
    
    # Personalización del formulario
    def save_model(self, request, obj, form, change):
        """Hook para personalizar el guardado"""
        super().save_model(request, obj, form, change)
        
        # Log de auditoría (opcional)
        action = "modificó" if change else "creó"
        self.message_user(
            request, 
            f'Servicio "{obj.nombre}" {action} exitosamente.',
            level='SUCCESS'
        )


# ===============================================================================
# PASO 2.B: ADMIN INDEPENDIENTES PARA MATERIALES (OPCIONAL)
# ===============================================================================

@admin.register(MaterialServicioFijo)
class MaterialServicioFijoAdmin(admin.ModelAdmin):
    """Admin para gestionar materiales fijos independientemente"""
    list_display = ['servicio', 'insumo', 'cantidad', 'costo_material_formateado', 'es_obligatorio']
    list_filter = ['es_obligatorio', 'servicio__categoria', 'insumo__categoria']
    search_fields = ['servicio__nombre', 'insumo__nombre']
    autocomplete_fields = ['servicio', 'insumo']
    readonly_fields = ['costo_adicional', 'costo_material_formateado']


@admin.register(MaterialServicioOpcional)
class MaterialServicioOpcionalAdmin(admin.ModelAdmin):
    """Admin para gestionar materiales opcionales independientemente"""
    list_display = ['servicio', 'categoria_insumo', 'cantidad', 'nombre_personalizado', 'es_obligatorio']
    list_filter = ['es_obligatorio', 'servicio__categoria', 'categoria_insumo']
    search_fields = ['servicio__nombre', 'categoria_insumo__nombre', 'nombre_personalizado']
    autocomplete_fields = ['servicio', 'categoria_insumo']


# ===============================================================================
# PASO 2.C: ADMIN PARA PLANES DE TRATAMIENTO
# ===============================================================================

class ItemPlanTratamientoInline(admin.TabularInline):
    """
    Inline para gestionar ítems dentro de un plan de tratamiento.
    ¡Aquí es donde se materializa tu idea del precio dinámico!
    """
    model = ItemPlanTratamiento
    extra = 1
    fields = (
        'orden', 'servicio', 'insumo_seleccionado', 'estado', 
        'precio_total_formateado', 'fecha_estimada', 'notas'
    )
    readonly_fields = ['precio_total_formateado']
    autocomplete_fields = ['servicio', 'insumo_seleccionado']
    ordering = ['orden']
    verbose_name = "Ítem del Plan"
    verbose_name_plural = "Ítems del Plan (Servicios y Materiales)"

    def precio_total_formateado(self, obj):
        """Muestra el precio total calculado"""
        if obj.pk:
            return obj.precio_total_formateado
        return "Se calculará al guardar"
    precio_total_formateado.short_description = 'Precio Total'


@admin.register(PlanDeTratamiento)
class PlanDeTratamientoAdmin(admin.ModelAdmin):
    """
    Admin para gestionar planes de tratamiento.
    Incluye vista de ítems inline para crear/editar el plan completo.
    """
    list_display = [
        'titulo', 
        'paciente_info',
        'odontologo_info',
        'estado',
        'prioridad',
        'cantidad_items',
        'precio_total_formateado',
        'porcentaje_completado',
        'fecha_creacion'
    ]
    list_filter = [
        'estado',
        'prioridad',
        'odontologo',
        'fecha_creacion',
        'fecha_aceptacion'
    ]
    search_fields = [
        'titulo',
        'paciente__usuario__nombre',
        'paciente__usuario__apellido',
        'paciente__usuario__email',
        'odontologo__usuario__nombre',
        'odontologo__usuario__apellido'
    ]
    autocomplete_fields = ['paciente', 'odontologo']
    readonly_fields = [
        'precio_total_formateado',
        'cantidad_items',
        'porcentaje_completado',
        'fecha_creacion',
        'fecha_presentacion',
        'fecha_aceptacion',
        'fecha_finalizacion'
    ]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('titulo', 'descripcion', 'paciente', 'odontologo')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad'),
            'classes': ('wide',)
        }),
        ('Fechas Importantes', {
            'fields': (
                'fecha_creacion', 'fecha_presentacion', 
                'fecha_aceptacion', 'fecha_finalizacion'
            ),
            'classes': ('collapse',)
        }),
        ('Resumen del Plan', {
            'fields': (
                'cantidad_items', 'porcentaje_completado', 'precio_total_formateado'
            ),
            'classes': ('wide',)
        }),
        ('Notas', {
            'fields': ('notas_internas',),
            'classes': ('collapse',)
        }),
    )
    
    # ¡AQUÍ ES DONDE SE INTEGRAN LOS ÍTEMS!
    inlines = [ItemPlanTratamientoInline]
    
    # Acciones personalizadas
    actions = ['marcar_como_presentado', 'marcar_como_aceptado']
    
    def paciente_info(self, obj):
        """Información del paciente"""
        return f"{obj.paciente.usuario.nombre} {obj.paciente.usuario.apellido}"
    paciente_info.short_description = 'Paciente'
    
    def odontologo_info(self, obj):
        """Información del odontólogo"""
        return f"Dr. {obj.odontologo.usuario.nombre} {obj.odontologo.usuario.apellido}"
    odontologo_info.short_description = 'Odontólogo'
    
    def precio_total_formateado(self, obj):
        """Precio total del plan formateado"""
        return f"${obj.precio_total_plan:.2f}"
    precio_total_formateado.short_description = 'Precio Total'
    
    @admin.action(description='Marcar como presentado al paciente')
    def marcar_como_presentado(self, request, queryset):
        updated = 0
        for plan in queryset:
            if plan.estado == 'PROPUESTO':
                plan.marcar_como_presentado()
                updated += 1
        self.message_user(request, f'{updated} planes marcados como presentados.')
    
    @admin.action(description='Marcar como aceptado por el paciente')
    def marcar_como_aceptado(self, request, queryset):
        updated = 0
        for plan in queryset:
            if plan.estado in ['PROPUESTO', 'PRESENTADO']:
                plan.marcar_como_aceptado()
                updated += 1
        self.message_user(request, f'{updated} planes marcados como aceptados.')


@admin.register(ItemPlanTratamiento)
class ItemPlanTratamientoAdmin(admin.ModelAdmin):
    """
    Admin independiente para ítems de plan (vista detallada).
    Útil para gestionar ítems específicos y ver el desglose de precios.
    """
    list_display = [
        'plan_titulo',
        'servicio',
        'insumo_seleccionado',
        'precio_servicio_snapshot',
        'precio_materiales_fijos_snapshot',
        'precio_insumo_seleccionado_snapshot',
        'precio_total_formateado',
        'estado',
        'orden'
    ]
    list_filter = [
        'estado',
        'servicio__categoria',
        'plan__estado',
        'plan__odontologo'
    ]
    search_fields = [
        'plan__titulo',
        'servicio__nombre',
        'insumo_seleccionado__nombre',
        'plan__paciente__usuario__nombre',
        'plan__paciente__usuario__apellido'
    ]
    autocomplete_fields = ['plan', 'servicio', 'insumo_seleccionado']
    readonly_fields = [
        'precio_total_formateado',
        'precio_servicio_snapshot',
        'precio_materiales_fijos_snapshot', 
        'precio_insumo_seleccionado_snapshot'
    ]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('plan', 'servicio', 'insumo_seleccionado', 'orden')
        }),
        ('Desglose de Precios (Automático)', {
            'fields': (
                'precio_servicio_snapshot',
                'precio_materiales_fijos_snapshot',
                'precio_insumo_seleccionado_snapshot',
                'precio_total_formateado'
            ),
            'classes': ('wide',),
            'description': 'Estos precios se calculan automáticamente al guardar'
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_estimada', 'fecha_realizada')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    def plan_titulo(self, obj):
        """Título del plan"""
        return obj.plan.titulo
    plan_titulo.short_description = 'Plan'


# ===============================================================================
# PASO 2.D: ADMIN PARA PRESUPUESTOS (CU20, CU21)
# ===============================================================================

class ItemPresupuestoInline(admin.TabularInline):
    """
    Muestra los ítems "congelados" dentro del Presupuesto.
    ¡ESTOS SON DE SOLO LECTURA! Una vez creados, no se pueden cambiar.
    """
    model = ItemPresupuesto
    extra = 0  # No se pueden añadir nuevos desde aquí
    readonly_fields = [
        'orden', 'nombre_servicio', 'nombre_insumo_seleccionado',
        'precio_servicio', 'precio_materiales_fijos', 
        'precio_insumo_seleccionado', 'precio_total_item',
        'precio_total_formateado', 'creado'
    ]
    fields = [
        'orden', 'nombre_servicio', 'nombre_insumo_seleccionado',
        'precio_servicio', 'precio_materiales_fijos', 
        'precio_insumo_seleccionado', 'precio_total_formateado'
    ]
    can_delete = False  # No se pueden borrar
    
    def has_add_permission(self, request, obj=None):
        return False  # No se pueden añadir ítems manualmente

    def precio_total_formateado(self, obj):
        """Precio total formateado"""
        return f"${obj.precio_total_item:,.2f}"
    precio_total_formateado.short_description = 'Total'


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    """
    Administrador de Presupuestos - El corazón del CU20 y CU21.
    
    Aquí se "congelan" los planes en ofertas formales que el paciente puede aceptar.
    """
    list_display = (
        '__str__', 'plan_paciente', 'estado_coloreado', 
        'total_formateado', 'fecha_presentacion', 'fecha_vencimiento_estado',
        'puede_ser_aceptado_display'
    )
    list_filter = (
        'estado', 
        'fecha_presentacion', 
        'fecha_vencimiento',
        'plan_tratamiento__prioridad'
    )
    search_fields = (
        'plan_tratamiento__titulo', 
        'plan_tratamiento__paciente__usuario__nombre',
        'plan_tratamiento__paciente__usuario__apellido',
        'plan_tratamiento__paciente__usuario__email'
    )
    readonly_fields = (
        'token_aceptacion', 'creado', 'actualizado',
        'subtotal_servicios', 'subtotal_materiales_fijos',
        'subtotal_materiales_opcionales', 'descuento_total', 
        'total_presupuestado', 'total_formateado',
        'link_aceptacion', 'esta_vencido_display', 'puede_ser_aceptado_display'
    )
    
    fieldsets = (
        ('Información General', {
            'fields': ('plan_tratamiento', 'version', 'estado')
        }),
        ('Fechas Importantes', {
            'fields': (
                'fecha_presentacion', 
                'fecha_vencimiento', 
                'fecha_aceptacion',
                'esta_vencido_display',
                'puede_ser_aceptado_display'
            )
        }),
        ('Desglose de Costos (Snapshot Congelado)', {
            'fields': (
                'subtotal_servicios', 
                'subtotal_materiales_fijos',
                'subtotal_materiales_opcionales', 
                'descuento_total', 
                'total_formateado'
            ),
            'classes': ('wide',),
            'description': 'Estos precios están congelados y no cambiarán aunque se modifique el inventario'
        }),
        ('Token de Aceptación (CU21)', {
            'fields': ('token_aceptacion', 'link_aceptacion'),
            'classes': ('collapse',),
            'description': 'El paciente puede aceptar el presupuesto usando este enlace único'
        }),
        ('Metadata', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    # Añadimos los ítems "congelados" para verlos
    inlines = [ItemPresupuestoInline]
    
    actions = ['presentar_presupuestos', 'marcar_como_vencidos']

    def plan_paciente(self, obj):
        """Información del paciente"""
        paciente = obj.plan_tratamiento.paciente
        return f"{paciente.usuario.nombre} {paciente.usuario.apellido}"
    plan_paciente.short_description = 'Paciente'

    def estado_coloreado(self, obj):
        """Estado con colores"""
        colores = {
            'BORRADOR': '#6c757d',      # Gris
            'PRESENTADO': '#007bff',    # Azul
            'ACEPTADO': '#28a745',      # Verde
            'RECHAZADO': '#dc3545',     # Rojo
            'VENCIDO': '#fd7e14',       # Naranja
        }
        color = colores.get(obj.estado, '#6c757d')
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_estado_display()}</span>'
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.allow_tags = True

    def total_formateado(self, obj):
        """Total formateado"""
        return f"${obj.total_presupuestado:,.2f}"
    total_formateado.short_description = 'Total'
    total_formateado.admin_order_field = 'total_presupuestado'

    def fecha_vencimiento_estado(self, obj):
        """Fecha de vencimiento con indicador de estado"""
        if not obj.fecha_vencimiento:
            return "Sin fecha límite"
        
        estado = "🟢" if not obj.esta_vencido else "🔴"
        return f"{estado} {obj.fecha_vencimiento}"
    fecha_vencimiento_estado.short_description = 'Vence'

    def esta_vencido_display(self, obj):
        """Indica si está vencido"""
        return "🔴 Sí" if obj.esta_vencido else "🟢 No"
    esta_vencido_display.short_description = '¿Vencido?'

    def puede_ser_aceptado_display(self, obj):
        """Indica si puede ser aceptado"""
        return "✅ Sí" if obj.puede_ser_aceptado else "❌ No"
    puede_ser_aceptado_display.short_description = '¿Puede aceptarse?'

    def link_aceptacion(self, obj):
        """Link para que el paciente acepte el presupuesto"""
        if obj.estado == 'PRESENTADO' and obj.puede_ser_aceptado:
            url = f"/api/tratamientos/presupuestos/{obj.id}/aceptar/{obj.token_aceptacion}/"
            return f'<a href="{url}" target="_blank">🔗 Link de aceptación</a>'
        return "No disponible"
    link_aceptacion.short_description = 'Link Aceptación (CU21)'
    link_aceptacion.allow_tags = True

    # --- Acciones personalizadas ---
    def presentar_presupuestos(self, request, queryset):
        """Presenta presupuestos seleccionados"""
        count = 0
        for presupuesto in queryset.filter(estado='BORRADOR'):
            try:
                presupuesto.presentar()
                count += 1
            except Exception as e:
                self.message_user(request, f"Error presentando {presupuesto}: {e}", level='ERROR')
        
        if count > 0:
            self.message_user(request, f"Se presentaron {count} presupuestos correctamente")
    presentar_presupuestos.short_description = "📧 Presentar presupuestos seleccionados"

    def marcar_como_vencidos(self, request, queryset):
        """Marca presupuestos vencidos"""
        count = queryset.filter(
            estado='PRESENTADO'
        ).filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).update(estado='VENCIDO')
        
        if count > 0:
            self.message_user(request, f"Se marcaron {count} presupuestos como vencidos")
    marcar_como_vencidos.short_description = "⏰ Marcar vencidos"
