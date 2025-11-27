from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para nuestro modelo Usuario,
    que usa email en lugar de username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tipo_usuario', 'ADMIN')  # Superusuario será ADMIN por defecto

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario Personalizado para cada inquilino (clínica).
    Aquí estarán todos: Admins de clínica, Odontólogos y Pacientes.
    """
    
    # --- Tipos de Usuario (según tu regla) ---
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        ODONTOLOGO = 'ODONTOLOGO', 'Odontólogo'
        PACIENTE = 'PACIENTE', 'Paciente'
    
    # --- Opciones de Sexo ---
    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        OTRO = 'O', 'Otro'
        NO_ESPECIFICAR = 'N', 'Prefiero no especificar'

    # --- Campos Principales ---
    email = models.EmailField(unique=True, help_text="Email. Se usará para el login.")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    # --- Campos Nuevos ---
    ci = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Cédula de Identidad",
        help_text="Número de cédula de identidad o documento de identificación"
    )
    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        null=True,
        blank=True,
        help_text="Sexo del usuario"
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Número de teléfono de contacto"
    )

    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PACIENTE,  # Por defecto, un nuevo usuario es Paciente
    )

    # --- Campos requeridos por Django ---
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Solo Admins y Odontólogos deberían poder entrar al admin
    is_superuser = models.BooleanField(default=False)  # Solo para el superadmin de la clínica
    
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # --- Campo para notificaciones push ---
    fcm_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token de Firebase Cloud Messaging para notificaciones push"
    )

    # --- Configuración del Modelo ---
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'       # Usamos 'email' para el login
    REQUIRED_FIELDS = ['nombre', 'apellido']  # Campos pedidos al crear superusuario

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}"


# --- MODELO ESPECIALIDAD ---

class Especialidad(models.Model):
    """
    Catálogo de especialidades odontológicas.
    Evita errores tipográficos y mantiene consistencia en los datos.
    """
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Nombre de la especialidad odontológica"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        help_text="Descripción detallada de la especialidad"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si la especialidad está activa para ser asignada"
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# --- MODELOS DE PERFIL EXTENDIDO ---

class PerfilOdontologo(models.Model):
    """
    Extiende el modelo Usuario para campos específicos del Odontólogo.
    """
    # Relación uno-a-uno. Cada usuario solo puede tener un perfil de odontólogo.
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='perfil_odontologo'
    )
    
    # Campos específicos del documento
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,  # No permitir eliminar especialidad si tiene odontólogos
        related_name='odontologos',
        null=True,
        blank=True,
        help_text="Especialidad odontológica del profesional"
    )
    cedulaProfesional = models.CharField(max_length=50, blank=True, unique=True, null=True)
    experienciaProfesional = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil Odontólogo'
        verbose_name_plural = 'Perfiles Odontólogos'

    def __str__(self):
        return self.usuario.full_name


class PerfilPaciente(models.Model):
    """
    Extiende el modelo Usuario para campos específicos del Paciente.
    """
    # Relación uno-a-uno. Cada usuario solo puede tener un perfil de paciente.
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='perfil_paciente'
    )
    
    # Campos específicos del documento
    fecha_de_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil Paciente'
        verbose_name_plural = 'Perfiles Pacientes'

    def __str__(self):
        return self.usuario.full_name
