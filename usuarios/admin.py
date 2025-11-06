from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilOdontologo, PerfilPaciente


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del panel de administración para el modelo Usuario personalizado.
    """
    list_display = ('email', 'nombre', 'apellido', 'tipo_usuario', 'is_active', 'is_staff')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)
    
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


# --- REGISTRO DE PERFILES EXTENDIDOS ---

@admin.register(PerfilOdontologo)
class PerfilOdontologoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el perfil de Odontólogo.
    """
    list_display = ('usuario', 'especialidad', 'cedulaProfesional')
    search_fields = ('usuario__email', 'usuario__nombre', 'cedulaProfesional')
    list_filter = ('especialidad',)


@admin.register(PerfilPaciente)
class PerfilPacienteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el perfil de Paciente.
    """
    list_display = ('usuario', 'fecha_de_nacimiento', 'direccion')
    search_fields = ('usuario__email', 'usuario__nombre')
    list_filter = ('fecha_de_nacimiento',)

