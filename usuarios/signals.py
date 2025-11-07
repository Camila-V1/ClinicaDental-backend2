"""
Señales para crear automáticamente perfiles de usuario según su tipo.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, PerfilOdontologo, PerfilPaciente


@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crear automáticamente el perfil correspondiente cuando se crea un usuario,
    según su tipo_usuario.
    """
    if created:
        # Si es un nuevo usuario, crear su perfil según el tipo
        if instance.tipo_usuario == Usuario.TipoUsuario.ODONTOLOGO:
            PerfilOdontologo.objects.get_or_create(usuario=instance)
        elif instance.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
            PerfilPaciente.objects.get_or_create(usuario=instance)
    else:
        # Si se actualiza un usuario existente y cambió su tipo
        if instance.tipo_usuario == Usuario.TipoUsuario.ODONTOLOGO:
            # Asegurar que tenga perfil de odontólogo
            if not hasattr(instance, 'perfil_odontologo'):
                PerfilOdontologo.objects.get_or_create(usuario=instance)
        elif instance.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
            # Asegurar que tenga perfil de paciente
            if not hasattr(instance, 'perfil_paciente'):
                PerfilPaciente.objects.get_or_create(usuario=instance)
