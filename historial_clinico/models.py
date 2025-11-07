# historial_clinico/models.py

from django.db import models
from django.conf import settings
import uuid

# Importamos los perfiles de la app 'usuarios'
from usuarios.models import PerfilPaciente, PerfilOdontologo
# Importamos el 'ItemPlanTratamiento' para vincular lo que se HIZO
from tratamientos.models import ItemPlanTratamiento

def subir_documento_paciente(instance, filename):
    """
    Genera una ruta de archivo única para los documentos clínicos,
    organizada por paciente y tenant (schema).
    Ej: tenants/clinica_demo/pacientes/uuid-paciente/documentos/radiografia.pdf
    """
    # Obtenemos el UUID del paciente
    paciente_uuid = instance.historial_clinico.paciente.usuario.id
    extension = filename.split('.')[-1]
    nuevo_nombre = f"{uuid.uuid4()}.{extension}"
    
    return f'tenants/documentos/pacientes/{paciente_uuid}/documentos/{nuevo_nombre}'


class HistorialClinico(models.Model):
    """
    Contenedor principal del historial de un paciente (CU08).
    """
    # Un historial por cada paciente
    paciente = models.OneToOneField(
        PerfilPaciente,
        on_delete=models.CASCADE,
        related_name='historial_clinico',
        primary_key=True
    )
    
    # Campos del prototipo
    antecedentes_medicos = models.TextField(
        blank=True, 
        null=True,
        help_text="Antecedentes médicos generales del paciente"
    )
    alergias = models.TextField(
        blank=True, 
        null=True,
        help_text="Alergias conocidas del paciente"
    )
    medicamentos_actuales = models.TextField(
        blank=True, 
        null=True,
        help_text="Medicamentos que el paciente toma actualmente"
    )
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Historial Clínico"
        verbose_name_plural = "Historiales Clínicos"

    def __str__(self):
        return f"Historial de {self.paciente.usuario.full_name}"


class EpisodioAtencion(models.Model):
    """
    Registro de una visita o evento clínico (CU09).
    Representa el "pasado" o lo que "se hizo".
    """
    historial_clinico = models.ForeignKey(
        HistorialClinico,
        on_delete=models.CASCADE,
        related_name='episodios'
    )
    odontologo = models.ForeignKey(
        PerfilOdontologo,
        on_delete=models.SET_NULL, # Si se borra el odonto, el registro persiste
        null=True, blank=True,
        related_name='episodios_atendidos'
    )
    # Vínculo al plan: ¿Qué ítem del plan se completó en esta visita?
    item_plan_tratamiento = models.ForeignKey(
        ItemPlanTratamiento,
        on_delete=models.SET_NULL, # Si se borra el plan, el registro persiste
        null=True, blank=True,
        related_name='episodios_asociados',
        help_text="Ítem del plan de tratamiento que se completó en esta visita"
    )
    
    # Campos del prototipo
    fecha_atencion = models.DateTimeField(auto_now_add=True)
    motivo_consulta = models.CharField(
        max_length=255,
        help_text="Motivo principal de la consulta"
    )
    diagnostico = models.TextField(
        blank=True, 
        null=True,
        help_text="Diagnóstico realizado en esta consulta"
    )
    descripcion_procedimiento = models.TextField(
        blank=True, 
        null=True, 
        help_text="Detalle de lo que se realizó en esta visita"
    )
    notas_privadas = models.TextField(
        blank=True, 
        null=True, 
        help_text="Notas solo visibles para el personal médico"
    )

    class Meta:
        verbose_name = "Episodio de Atención"
        verbose_name_plural = "Episodios de Atención"
        ordering = ['-fecha_atencion']

    def __str__(self):
        return f"Episodio del {self.fecha_atencion.strftime('%Y-%m-%d')} para {self.historial_clinico.paciente.usuario.full_name}"


class Odontograma(models.Model):
    """
    Una "foto" del estado de la boca en un momento dado (CU10).
    """
    historial_clinico = models.ForeignKey(
        HistorialClinico,
        on_delete=models.CASCADE,
        related_name='odontogramas'
    )
    fecha_snapshot = models.DateTimeField(auto_now_add=True)
    
    # Usamos JSONField para máxima flexibilidad, como en el prototipo
    # Guardará algo como: 
    # { "11": {"estado": "sano"}, "12": {"estado": "caries", "cara": "oclusal"}, ... }
    estado_piezas = models.JSONField(
        default=dict,
        help_text="Estado detallado de cada pieza dental en formato JSON"
    ) 
    
    notas = models.TextField(
        blank=True, 
        null=True,
        help_text="Observaciones adicionales sobre este odontograma"
    )
    
    class Meta:
        verbose_name = "Odontograma"
        verbose_name_plural = "Odontogramas"
        ordering = ['-fecha_snapshot']

    def __str__(self):
        return f"Odontograma de {self.historial_clinico.paciente.usuario.full_name} ({self.fecha_snapshot.strftime('%Y-%m-%d')})"


class DocumentoClinico(models.Model):
    """
    Un archivo adjunto al historial (Radiografía, Foto, PDF, etc.) (CU11)
    """
    historial_clinico = models.ForeignKey(
        HistorialClinico,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    descripcion = models.CharField(
        max_length=255,
        help_text="Descripción del documento"
    )
    
    # Campo para subir el archivo
    archivo = models.FileField(
        upload_to=subir_documento_paciente,
        help_text="Archivo del documento clínico"
    )
    
    tipo_documento = models.CharField(
        max_length=50,
        choices=[
            ('RADIOGRAFIA', 'Radiografía'),
            ('FOTOGRAFIA', 'Fotografía'),
            ('LABORATORIO', 'Examen de Laboratorio'),
            ('CONSENTIMIENTO', 'Consentimiento Informado'),
            ('RECETA', 'Receta Médica'),
            ('INFORME', 'Informe Médico'),
            ('OTRO', 'Otro'),
        ],
        default='OTRO',
        help_text="Tipo de documento clínico"
    )
    
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento Clínico"
        verbose_name_plural = "Documentos Clínicos"
        ordering = ['-creado']

    def __str__(self):
        return f"{self.get_tipo_documento_display()}: {self.descripcion}"
