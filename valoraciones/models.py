from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from usuarios.models import Usuario
from agenda.models import Cita


class Valoracion(models.Model):
    """
    Modelo para almacenar las valoraciones/reseñas de los pacientes
    sobre la atención recibida por los odontólogos
    """
    
    cita = models.OneToOneField(
        Cita,
        on_delete=models.CASCADE,
        related_name='valoracion',
        help_text='Cita que está siendo valorada'
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='valoraciones_realizadas',
        help_text='Paciente que realiza la valoración'
    )
    odontologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='valoraciones_recibidas',
        help_text='Odontólogo que recibe la valoración'
    )
    
    # Calificación (1-5 estrellas)
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Calificación de 1 a 5 estrellas'
    )
    
    # Comentario opcional
    comentario = models.TextField(
        blank=True,
        null=True,
        help_text='Comentario adicional del paciente'
    )
    
    # Aspectos específicos (opcionales)
    puntualidad = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='Calificación de puntualidad (1-5)'
    )
    trato = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='Calificación del trato recibido (1-5)'
    )
    limpieza = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='Calificación de limpieza e higiene (1-5)'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Indica si el paciente recibió la notificación
    notificacion_enviada = models.BooleanField(default=False)
    notificacion_enviada_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'valoraciones'
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['odontologo', '-created_at']),
            models.Index(fields=['paciente', '-created_at']),
            models.Index(fields=['calificacion']),
        ]
    
    def __str__(self):
        return f"Valoración de {self.paciente.nombre} a {self.odontologo.nombre} - {self.calificacion}⭐"
    
    @property
    def calificacion_promedio_aspectos(self):
        """Calcula el promedio de los aspectos específicos si están presentes"""
        aspectos = [self.puntualidad, self.trato, self.limpieza]
        aspectos_validos = [a for a in aspectos if a is not None]
        if aspectos_validos:
            return sum(aspectos_validos) / len(aspectos_validos)
        return None
