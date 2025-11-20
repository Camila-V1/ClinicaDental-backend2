from django.db import models

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class BitacoraAccion(models.Model):
    """
    Modelo para registrar todas las acciones importantes del sistema (CU39).
    
    Registra: Usuario, Acción, Modelo afectado, Fecha/Hora, Detalles, IP
    """
    
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
        ('VER', 'Ver'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('EXPORTAR', 'Exportar datos'),
        ('IMPRIMIR', 'Imprimir'),
        ('OTRO', 'Otro'),
    ]
    
    # Usuario que realizó la acción
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_bitacora'
    )
    
    # Tipo de acción realizada
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        default='OTRO'
    )
    
    # Modelo afectado (usando ContentType para genericidad)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de modelo'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID del objeto'
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Descripción de la acción
    descripcion = models.TextField(
        help_text='Descripción detallada de la acción realizada'
    )
    
    # Datos adicionales (JSON con información relevante)
    detalles = models.JSONField(
        null=True,
        blank=True,
        help_text='Información adicional en formato JSON'
    )
    
    # Fecha y hora de la acción
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    # Dirección IP desde donde se realizó la acción
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    
    # User agent del navegador
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='Navegador/Dispositivo'
    )
    
    class Meta:
        db_table = 'reportes_bitacora_accion'
        verbose_name = 'Registro de Bitácora'
        verbose_name_plural = 'Registros de Bitácora'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['accion', '-fecha_hora']),
        ]
    
    def __str__(self):
        usuario_nombre = self.usuario.full_name if self.usuario else 'Sistema'
        fecha = self.fecha_hora.strftime('%d/%m/%Y %H:%M')
        return f"{usuario_nombre} - {self.get_accion_display()} - {fecha}"
    
    @classmethod
    def registrar(cls, usuario, accion, descripcion, content_object=None, detalles=None, ip_address=None, user_agent=None):
        """
        Método auxiliar para crear registros de bitácora fácilmente
        
        Ejemplo:
            BitacoraAccion.registrar(
                usuario=request.user,
                accion='CREAR',
                descripcion='Creó nuevo paciente Juan Pérez',
                content_object=paciente,
                detalles={'email': 'juan@example.com'},
                ip_address=get_client_ip(request)
            )
        """
        bitacora = cls(
            usuario=usuario,
            accion=accion,
            descripcion=descripcion,
            detalles=detalles,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if content_object:
            bitacora.content_object = content_object
        
        bitacora.save()
        return bitacora

