from django.db import models
from django.conf import settings


class BackupConfiguration(models.Model):
    """Configuración de backups automáticos (una instancia por tenant)."""
    
    SCHEDULE_CHOICES = (
        ('daily', 'Diario'),
        ('every_12h', 'Cada 12 horas'),
        ('every_6h', 'Cada 6 horas'),
        ('weekly', 'Semanal'),
    )
    
    backup_schedule = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHOICES,
        default='daily',
        help_text="Frecuencia de backups automáticos"
    )
    backup_time = models.TimeField(
        default='02:00:00',
        help_text="Hora para ejecutar backups (formato 24h)"
    )
    retention_days = models.IntegerField(
        default=30,
        help_text="Días para mantener backups antes de eliminarlos"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Si los backups automáticos están activados"
    )
    last_backup_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha del último backup automático"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backup_configs_actualizadas'
    )
    
    class Meta:
        verbose_name = "Configuración de Backup"
        verbose_name_plural = "Configuraciones de Backup"
    
    def __str__(self):
        return f"Config Backup - {self.get_backup_schedule_display()}"


class BackupRecord(models.Model):
    """Registro de backups realizados (se guarda en cada schema de tenant)."""
    
    BACKUP_TYPES = (
        ('manual', 'Manual'),
        ('automatic', 'Automático'),
    )
    
    file_name = models.CharField(max_length=255, help_text="Nombre del archivo de backup")
    file_path = models.TextField(help_text="Ruta del archivo en Supabase Storage")
    file_size = models.BigIntegerField(help_text="Tamaño del archivo en bytes")
    backup_type = models.CharField(max_length=10, choices=BACKUP_TYPES, default='manual')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_creados',
        help_text="Usuario que creó el backup (null si es automático)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Registro de Backup"
        verbose_name_plural = "Registros de Backups"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.get_backup_type_display()}"
    
    @property
    def file_size_mb(self):
        """Retorna el tamaño en MB."""
        return round(self.file_size / (1024 * 1024), 2)
