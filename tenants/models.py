from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone
from datetime import timedelta


class PlanSuscripcion(models.Model):
    """Planes de suscripción disponibles para las clínicas."""
    
    TIPO_CHOICES = [
        ('PRUEBA', 'Prueba (7 días gratis)'),
        ('MENSUAL', 'Mensual'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio en USD")
    duracion_dias = models.IntegerField(help_text="Duración del plan en días")
    max_usuarios = models.IntegerField(default=10, help_text="Máximo de usuarios permitidos")
    max_pacientes = models.IntegerField(default=500, help_text="Máximo de pacientes permitidos")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plan de Suscripción"
        verbose_name_plural = "Planes de Suscripción"
        ordering = ['precio']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}/{self.get_tipo_display()}"


class Clinica(TenantMixin):
    """Modelo que representa un Tenant (Clínica).

    Usamos TenantMixin que añade los campos necesarios para django-tenants
    y gestion del schema.
    """
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('ACTIVA', 'Activa'),
        ('SUSPENDIDA', 'Suspendida por Pago'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    BACKUP_SCHEDULE_CHOICES = [
        ('disabled', 'Desactivado'),
        ('daily', 'Diario'),
        ('every_12h', 'Cada 12 horas'),
        ('every_6h', 'Cada 6 horas'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('scheduled', 'Programado (Fecha específica)'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=200)
    dominio = models.CharField(max_length=200, unique=True, help_text="Dominio/identificador del tenant")
    
    # Información de contacto
    email_admin = models.EmailField(blank=True, default='', help_text="Email del administrador de la clínica")
    telefono = models.CharField(max_length=20, blank=True, default='')
    direccion = models.TextField(blank=True, default='')
    ciudad = models.CharField(max_length=100, blank=True, default='')
    pais = models.CharField(max_length=100, blank=True, default='')
    
    # Plan y suscripción
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='clinicas'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    
    # Control
    activo = models.BooleanField(default=False, help_text="Activo en el sistema")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    # Notas administrativas
    notas = models.TextField(blank=True, help_text="Notas internas del administrador")
    
    # ============================================================================
    # CONFIGURACIÓN DE BACKUPS AUTOMÁTICOS
    # ============================================================================
    backup_schedule = models.CharField(
        max_length=20,
        choices=BACKUP_SCHEDULE_CHOICES,
        default='disabled',
        help_text="Frecuencia de los backups automáticos"
    )
    
    backup_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Hora específica para backups (ej: 02:00 AM para diarios/semanales/mensuales)"
    )
    
    backup_weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text="Día de la semana para backups semanales (0=Lunes, 6=Domingo)"
    )
    
    backup_day_of_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Día del mes para backups mensuales (1-28)"
    )
    
    last_backup_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora del último backup automático exitoso"
    )
    
    next_scheduled_backup = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora exacta programada para el próximo backup (solo para 'scheduled')"
    )

    # Si se crea esta instancia desde el admin, auto_create_schema=True
    auto_create_schema = True

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"

    def __str__(self):
        return f"{self.nombre} ({self.dominio})"
    
    @property
    def esta_activa(self):
        """Verifica si la clínica está activa y no ha expirado."""
        if not self.activo or self.estado != 'ACTIVA':
            return False
        if self.fecha_expiracion and timezone.now() > self.fecha_expiracion:
            return False
        return True
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes de suscripción."""
        if not self.fecha_expiracion:
            return None
        delta = self.fecha_expiracion - timezone.now()
        return max(0, delta.days)
    
    def activar_plan(self, plan=None):
        """Activa la clínica con el plan especificado."""
        if plan:
            self.plan = plan
        
        if not self.plan:
            raise ValueError("La clínica debe tener un plan asignado")
        
        self.estado = 'ACTIVA'
        self.activo = True
        self.fecha_inicio = timezone.now()
        self.fecha_expiracion = timezone.now() + timedelta(days=self.plan.duracion_dias)
        self.save()
    
    def renovar_suscripcion(self):
        """Renueva la suscripción por el período del plan actual."""
        if not self.plan:
            raise ValueError("La clínica debe tener un plan asignado")
        
        if self.fecha_expiracion and self.fecha_expiracion > timezone.now():
            # Si aún no ha expirado, extender desde la fecha de expiración
            self.fecha_expiracion = self.fecha_expiracion + timedelta(days=self.plan.duracion_dias)
        else:
            # Si ya expiró, renovar desde ahora
            self.fecha_expiracion = timezone.now() + timedelta(days=self.plan.duracion_dias)
        
        self.estado = 'ACTIVA'
        self.activo = True
        self.save()
    
    def suspender(self, motivo=''):
        """Suspende la clínica."""
        self.estado = 'SUSPENDIDA'
        self.activo = False
        if motivo:
            self.notas = f"{timezone.now()}: Suspendida - {motivo}\n{self.notas}"
        self.save()


class Domain(DomainMixin):
    """Modelo Domain para mapear subdominios a tenants.

    Extiende DomainMixin proporcionado por django-tenants.
    """
    pass


class SolicitudRegistro(models.Model):
    """Solicitudes de registro de nuevas clínicas.
    
    Este modelo vive en el esquema público y permite que potenciales
    clientes soliciten crear una nueva clínica.
    """
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('PROCESADA', 'Procesada (Clínica Creada)'),
    ]
    
    # Información de la clínica
    nombre_clinica = models.CharField(max_length=200)
    dominio_deseado = models.CharField(
        max_length=200,
        unique=True,
        help_text="Subdominio deseado (ej: 'miclinica' para miclinica.ejemplo.com)"
    )
    
    # Información del solicitante
    nombre_contacto = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    cargo = models.CharField(max_length=100, blank=True)
    
    # Información adicional
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    
    # Plan seleccionado
    plan_solicitado = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        related_name='solicitudes'
    )
    
    # Información adicional de la solicitud
    mensaje = models.TextField(
        blank=True,
        help_text="Mensaje o comentarios adicionales del solicitante"
    )
    
    # Estado de la solicitud
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    motivo_rechazo = models.TextField(blank=True)
    
    # Relación con la clínica creada (si fue aprobada)
    clinica_creada = models.ForeignKey(
        Clinica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitud_origen'
    )
    
    # Timestamps
    creada = models.DateTimeField(auto_now_add=True)
    revisada = models.DateTimeField(null=True, blank=True)
    procesada = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Solicitud de Registro"
        verbose_name_plural = "Solicitudes de Registro"
        ordering = ['-creada']
    
    def __str__(self):
        return f"{self.nombre_clinica} - {self.get_estado_display()}"
