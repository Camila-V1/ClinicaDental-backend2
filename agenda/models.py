from django.db import models
from decimal import Decimal
from usuarios.models import PerfilPaciente, PerfilOdontologo


# Catálogo de motivos y precios de citas
MOTIVOS_CITA_CHOICES = [
    ('CONSULTA', 'Consulta General'),
    ('URGENCIA', 'Urgencia/Dolor'),
    ('LIMPIEZA', 'Limpieza Dental'),
    ('REVISION', 'Revisión/Control'),
    ('PLAN', 'Tratamiento de mi Plan'),
]

PRECIOS_CITA = {
    'CONSULTA': Decimal('30.00'),   # Consulta básica accesible
    'URGENCIA': Decimal('80.00'),   # Atención prioritaria
    'LIMPIEZA': Decimal('60.00'),   # Profilaxis
    'REVISION': Decimal('20.00'),   # Control/chequeo
    'PLAN': Decimal('0.00'),        # Ya incluido en plan
}


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
    
    # Tipo de motivo (para determinar precio)
    motivo_tipo = models.CharField(
        max_length=20,
        choices=MOTIVOS_CITA_CHOICES,
        default='CONSULTA',
        verbose_name='Tipo de Motivo',
        help_text='Determina el costo de la cita'
    )
    
    # Descripción adicional del motivo
    motivo = models.TextField(
        verbose_name='Motivo de la consulta',
        help_text='Descripción detallada del motivo'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre la cita'
    )
    
    # Vinculación con plan de tratamiento (si aplica)
    item_plan = models.ForeignKey(
        'tratamientos.ItemPlanTratamiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cita_asociada',
        verbose_name='Ítem del Plan',
        help_text='Si es cita de tratamiento, vincula con el ítem específico del plan'
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
            models.Index(fields=['motivo_tipo']),
        ]
    
    def __str__(self):
        return f"Cita {self.paciente.usuario.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def precio(self):
        """Retorna el precio de la cita según el tipo de motivo"""
        return PRECIOS_CITA.get(self.motivo_tipo, Decimal('0.00'))
    
    @property
    def precio_display(self):
        """Retorna el precio formateado para mostrar"""
        precio = self.precio
        if precio == 0:
            return "Incluido en plan"
        return f"${precio:.2f}"
    
    @property
    def es_cita_plan(self):
        """Verifica si es una cita de tratamiento del plan"""
        return self.motivo_tipo == 'PLAN' and self.item_plan is not None
    
    @property
    def requiere_pago(self):
        """Determina si la cita requiere pago"""
        return self.precio > 0 and not self.es_cita_plan
