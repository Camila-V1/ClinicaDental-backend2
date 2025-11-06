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
    
    # --- Campos Principales ---
    email = models.EmailField(unique=True, help_text="Email. Se usará para el login.")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

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
