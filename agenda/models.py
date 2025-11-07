from django.db import models
from usuarios.models import PerfilPaciente, PerfilOdontologo


class Cita(models.Model):
    """
    Modelo para representar una cita médica en la agenda.
    Relaciona un paciente con un odontólogo en una fecha/hora específica.
    """
    
    # Relaciones
    paciente = models.ForeignKey(
        PerfilPaciente,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Paciente'
    )
    odontologo = models.ForeignKey(
        PerfilOdontologo,
        on_delete=models.CASCADE,
        related_name='citas_atendidas',
        verbose_name='Odontólogo'
    )
    
    # Datos de la cita
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    motivo = models.TextField(verbose_name='Motivo de la consulta')
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre la cita'
    )
    
    # Estado de la cita
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado'
    )
    
    # Timestamps automáticos
    creado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    actualizado = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Agenda'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"Cita {self.paciente.usuario.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
