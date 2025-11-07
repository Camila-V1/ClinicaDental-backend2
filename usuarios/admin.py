from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilOdontologo, PerfilPaciente, Especialidad


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del panel de administración para el modelo Usuario personalizado.
    """
    list_display = ('email', 'nombre', 'apellido', 'tipo_usuario', 'tiene_perfil', 'is_active', 'is_staff')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)
    actions = ['crear_perfiles_faltantes']
    
    # Campos que se muestran al editar un usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'tipo_usuario')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos que se muestran al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'tipo_usuario', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def tiene_perfil(self, obj):
        """Verifica si el usuario tiene su perfil correspondiente creado."""
        if obj.tipo_usuario == Usuario.TipoUsuario.ODONTOLOGO:
            return hasattr(obj, 'perfil_odontologo')
        elif obj.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
            return hasattr(obj, 'perfil_paciente')
        return None  # ADMIN no necesita perfil especial
    tiene_perfil.boolean = True
    tiene_perfil.short_description = 'Tiene Perfil'
    
    def crear_perfiles_faltantes(self, request, queryset):
        """Acción para crear perfiles faltantes de usuarios seleccionados."""
        creados = 0
        for usuario in queryset:
            if usuario.tipo_usuario == Usuario.TipoUsuario.ODONTOLOGO:
                if not hasattr(usuario, 'perfil_odontologo'):
                    PerfilOdontologo.objects.create(usuario=usuario)
                    creados += 1
            elif usuario.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
                if not hasattr(usuario, 'perfil_paciente'):
                    PerfilPaciente.objects.create(usuario=usuario)
                    creados += 1
        
        self.message_user(request, f'{creados} perfil(es) creado(s) exitosamente.')
    crear_perfiles_faltantes.short_description = 'Crear perfiles faltantes'


# --- REGISTRO DE ESPECIALIDADES ---

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Especialidades.
    """
    list_display = ('nombre', 'activo', 'total_odontologos', 'creado')
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
    
    def total_odontologos(self, obj):
        """Muestra cuántos odontólogos tienen esta especialidad."""
        return obj.odontologos.count()
    total_odontologos.short_description = 'Total Odontólogos'


# --- REGISTRO DE PERFILES EXTENDIDOS ---

@admin.register(PerfilOdontologo)
class PerfilOdontologoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el perfil de Odontólogo.
    """
    list_display = ('usuario', 'especialidad', 'cedulaProfesional')
    search_fields = ('usuario__email', 'usuario__nombre', 'cedulaProfesional')
    list_filter = ('especialidad',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtrar el campo Usuario para mostrar solo usuarios tipo ODONTOLOGO
        que aún no tienen perfil de odontólogo.
        """
        if db_field.name == "usuario":
            # Mostrar solo usuarios de tipo ODONTOLOGO que no tienen perfil todavía
            kwargs["queryset"] = Usuario.objects.filter(
                tipo_usuario=Usuario.TipoUsuario.ODONTOLOGO
            ).exclude(
                perfil_odontologo__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PerfilPaciente)
class PerfilPacienteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el perfil de Paciente.
    """
    list_display = ('usuario', 'fecha_de_nacimiento', 'direccion')
    search_fields = ('usuario__email', 'usuario__nombre')
    list_filter = ('fecha_de_nacimiento',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtrar el campo Usuario para mostrar solo usuarios tipo PACIENTE
        que aún no tienen perfil de paciente.
        """
        if db_field.name == "usuario":
            # Mostrar solo usuarios de tipo PACIENTE que no tienen perfil todavía
            kwargs["queryset"] = Usuario.objects.filter(
                tipo_usuario=Usuario.TipoUsuario.PACIENTE
            ).exclude(
                perfil_paciente__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

