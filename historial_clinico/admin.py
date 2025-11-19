# historial_clinico/admin.py

from django.contrib import admin
from .models import HistorialClinico, EpisodioAtencion, Odontograma, DocumentoClinico

# --- Inlines para el Historial Clínico ---
# Esto nos permite ver y añadir episodios, odontogramas y documentos
# directamente desde la página del Historial del paciente.

class EpisodioAtencionInline(admin.TabularInline):
    model = EpisodioAtencion
    extra = 0 # No mostrar formularios vacíos por defecto
    fields = ('fecha_atencion', 'odontologo', 'motivo_consulta', 'diagnostico', 'descripcion_procedimiento')
    readonly_fields = ('fecha_atencion',)
    autocomplete_fields = ['odontologo', 'item_plan_tratamiento']
    verbose_name = "Episodio de Atención"
    verbose_name_plural = "Episodios de Atención"

class OdontogramaInline(admin.TabularInline):
    model = Odontograma
    extra = 0
    fields = ('fecha_snapshot', 'notas', 'estado_piezas')
    readonly_fields = ('fecha_snapshot',)
    
class DocumentoClinicoInline(admin.TabularInline):
    model = DocumentoClinico
    extra = 0
    fields = ('creado', 'descripcion', 'tipo_documento', 'archivo')
    readonly_fields = ('creado',)

# --- Admin Principal para HistorialClinico ---

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'alergias_preview', 'medicamentos_preview', 'total_episodios', 'actualizado')
    list_filter = ('actualizado', 'creado')
    search_fields = ('paciente__usuario__email', 'paciente__usuario__nombre', 'paciente__usuario__apellido', 'paciente__usuario__ci')
    autocomplete_fields = ['paciente']
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('paciente',)
        }),
        ('Antecedentes Médicos (CU08)', {
            'fields': ('antecedentes_medicos', 'alergias', 'medicamentos_actuales'),
            'classes': ('wide',)
        }),
        ('Metadatos', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado', 'actualizado')
    
    # Aquí adjuntamos los inlines
    inlines = [
        EpisodioAtencionInline,
        OdontogramaInline,
        DocumentoClinicoInline,
    ]
    
    def alergias_preview(self, obj):
        """Vista previa de alergias en la lista."""
        if obj.alergias:
            return obj.alergias[:50] + "..." if len(obj.alergias) > 50 else obj.alergias
        return "Sin alergias registradas"
    alergias_preview.short_description = "Alergias"
    
    def medicamentos_preview(self, obj):
        """Vista previa de medicamentos en la lista."""
        if obj.medicamentos_actuales:
            return obj.medicamentos_actuales[:50] + "..." if len(obj.medicamentos_actuales) > 50 else obj.medicamentos_actuales
        return "Sin medicamentos registrados"
    medicamentos_preview.short_description = "Medicamentos"
    
    def total_episodios(self, obj):
        """Muestra el total de episodios de atención."""
        return obj.episodios.count()
    total_episodios.short_description = "Total Episodios"

# --- Registramos los otros modelos para que se puedan gestionar individualmente ---
# (Aunque es más práctico hacerlo desde el HistorialClinico)

@admin.register(EpisodioAtencion)
class EpisodioAtencionAdmin(admin.ModelAdmin):
    list_display = ('historial_clinico', 'fecha_atencion', 'odontologo', 'motivo_consulta', 'tiene_diagnostico')
    list_filter = ('fecha_atencion', 'odontologo', 'item_plan_tratamiento__servicio')
    search_fields = (
        'historial_clinico__paciente__usuario__email', 
        'historial_clinico__paciente__usuario__nombre',
        'historial_clinico__paciente__usuario__apellido',
        'motivo_consulta', 
        'diagnostico'
    )
    autocomplete_fields = ['historial_clinico', 'odontologo', 'item_plan_tratamiento']
    date_hierarchy = 'fecha_atencion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('historial_clinico', 'odontologo', 'item_plan_tratamiento', 'fecha_atencion')
        }),
        ('Detalles de la Consulta', {
            'fields': ('motivo_consulta', 'diagnostico', 'descripcion_procedimiento')
        }),
        ('Notas Internas', {
            'fields': ('notas_privadas',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_atencion',)
    
    def tiene_diagnostico(self, obj):
        """Indica si el episodio tiene diagnóstico."""
        return bool(obj.diagnostico)
    tiene_diagnostico.boolean = True
    tiene_diagnostico.short_description = "Tiene Diagnóstico"

@admin.register(Odontograma)
class OdontogramaAdmin(admin.ModelAdmin):
    list_display = ('historial_clinico', 'fecha_snapshot', 'piezas_registradas')
    list_filter = ('fecha_snapshot',)
    search_fields = (
        'historial_clinico__paciente__usuario__email',
        'historial_clinico__paciente__usuario__nombre',
        'historial_clinico__paciente__usuario__apellido'
    )
    autocomplete_fields = ['historial_clinico']
    date_hierarchy = 'fecha_snapshot'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('historial_clinico', 'fecha_snapshot')
        }),
        ('Estado de Piezas Dentales', {
            'fields': ('estado_piezas',),
            'classes': ('wide',)
        }),
        ('Observaciones', {
            'fields': ('notas',)
        }),
    )
    
    readonly_fields = ('fecha_snapshot',)
    
    def piezas_registradas(self, obj):
        """Muestra el número de piezas registradas."""
        if obj.estado_piezas and isinstance(obj.estado_piezas, dict):
            return len(obj.estado_piezas)
        return 0
    piezas_registradas.short_description = "Piezas Registradas"

@admin.register(DocumentoClinico)
class DocumentoClinicoAdmin(admin.ModelAdmin):
    list_display = ('historial_clinico', 'episodio', 'descripcion', 'tipo_documento', 'tiene_archivo', 'creado')
    list_filter = ('tipo_documento', 'creado')
    search_fields = (
        'historial_clinico__paciente__usuario__email', 
        'historial_clinico__paciente__usuario__nombre',
        'historial_clinico__paciente__usuario__apellido',
        'descripcion'
    )
    autocomplete_fields = ['historial_clinico', 'episodio']
    date_hierarchy = 'creado'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('historial_clinico', 'episodio', 'descripcion', 'tipo_documento')
        }),
        ('Archivo', {
            'fields': ('archivo',)
        }),
        ('Metadatos', {
            'fields': ('creado',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado',)
    
    def tiene_archivo(self, obj):
        """Indica si el documento tiene archivo adjunto."""
        return bool(obj.archivo)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = "Archivo Adjunto"
