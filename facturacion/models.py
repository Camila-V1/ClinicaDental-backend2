# facturacion/models.py

from django.db import models
from django.conf import settings
from decimal import Decimal

# Importamos los modelos que necesitamos
from usuarios.models import PerfilPaciente
from tratamientos.models import Presupuesto

class Factura(models.Model):
    """
    Representa la factura oficial generada a partir de un Presupuesto aceptado (CU31).
    """
    class EstadoFactura(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Pago'
        PAGADA = 'PAGADA', 'Pagada'
        ANULADA = 'ANULADA', 'Anulada'

    # Vínculo con el paciente
    paciente = models.ForeignKey(
        PerfilPaciente,
        on_delete=models.SET_NULL, # Si se borra el paciente, la factura persiste
        null=True,
        related_name='facturas'
    )
    # Vínculo con el presupuesto que la originó
    presupuesto = models.OneToOneField(
        Presupuesto,
        on_delete=models.SET_NULL, # Si se borra el presupuesto, la factura persiste
        null=True, blank=True,
        related_name='factura'
    )
    
    # Datos de facturación (del prototipo CU31)
    nit_ci = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="NIT/CI",
        help_text="NIT o CI para la facturación"
    )
    razon_social = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Razón Social",
        help_text="Nombre o razón social para la factura"
    )
    
    # Montos (copiados del presupuesto)
    monto_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Monto total de la factura"
    )
    monto_pagado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Monto pagado hasta el momento"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoFactura.choices,
        default=EstadoFactura.PENDIENTE,
        help_text="Estado actual de la factura"
    )
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision']

    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago."""
        return self.monto_total - self.monto_pagado

    def __str__(self):
        return f"Factura #{self.id} - {self.paciente.usuario.full_name if self.paciente else 'Sin paciente'} (Bs. {self.monto_total})"

    def actualizar_estado_pago(self):
        """
        Actualiza el estado de la factura basado en los pagos.
        """
        if self.monto_pagado >= self.monto_total:
            self.estado = self.EstadoFactura.PAGADA
        else:
            self.estado = self.EstadoFactura.PENDIENTE
        self.save()

    @classmethod
    def crear_desde_presupuesto(cls, presupuesto, nit_ci=None, razon_social=None):
        """
        Método de clase para crear una factura a partir de un presupuesto aceptado.
        """
        if presupuesto.estado != 'ACEPTADO':
            raise ValueError("Solo se pueden facturar presupuestos aceptados")
        
        # Verificar si ya existe una factura para este presupuesto
        if hasattr(presupuesto, 'factura') and presupuesto.factura:
            raise ValueError("Este presupuesto ya tiene una factura asociada")
        
        # Crear la factura
        factura = cls.objects.create(
            paciente=presupuesto.plan_tratamiento.paciente,
            presupuesto=presupuesto,
            monto_total=presupuesto.total,
            nit_ci=nit_ci or presupuesto.plan_tratamiento.paciente.usuario.ci,
            razon_social=razon_social or presupuesto.plan_tratamiento.paciente.usuario.full_name
        )
        
        return factura


class Pago(models.Model):
    """
    Representa un pago (parcial o total) aplicado a una Factura (CU30, CU32, CU33).
    También soporta pagos online directos para citas y tratamientos.
    """
    class TipoPago(models.TextChoices):
        FACTURA = 'FACTURA', 'Pago de Factura'
        CITA = 'CITA', 'Pago de Cita'
        TRATAMIENTO = 'TRATAMIENTO', 'Pago de Tratamiento'
        PLAN = 'PLAN', 'Pago de Plan de Tratamiento'
        OTRO = 'OTRO', 'Otro'
    
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA = 'TARJETA', 'Tarjeta'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia Bancaria'
        QR = 'QR', 'Pago QR'
        CHEQUE = 'CHEQUE', 'Cheque'
        STRIPE = 'STRIPE', 'Stripe (Tarjeta Online)'
        PAYPAL = 'PAYPAL', 'PayPal'
        MERCADOPAGO = 'MERCADOPAGO', 'MercadoPago'
        OTRO = 'OTRO', 'Otro'
        
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PROCESANDO = 'PROCESANDO', 'Procesando'
        COMPLETADO = 'COMPLETADO', 'Completado'
        FALLIDO = 'FALLIDO', 'Fallido'
        CANCELADO = 'CANCELADO', 'Cancelado'
        REEMBOLSADO = 'REEMBOLSADO', 'Reembolsado'

    # Tipo de pago
    tipo_pago = models.CharField(
        max_length=20,
        choices=TipoPago.choices,
        default=TipoPago.FACTURA,
        help_text="Tipo de pago realizado"
    )

    # Relaciones (opcionales según el tipo)
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='pagos',
        null=True,
        blank=True,
        help_text="Factura a la que se aplica este pago"
    )
    cita = models.ForeignKey(
        'agenda.Cita',
        on_delete=models.SET_NULL,
        related_name='pagos',
        null=True,
        blank=True,
        help_text="Cita relacionada con este pago"
    )
    plan_tratamiento = models.ForeignKey(
        'tratamientos.PlanDeTratamiento',
        on_delete=models.SET_NULL,
        related_name='pagos',
        null=True,
        blank=True,
        help_text="Plan de tratamiento relacionado"
    )
    paciente = models.ForeignKey(
        PerfilPaciente,
        on_delete=models.SET_NULL, # Si se borra el paciente, el pago persiste
        null=True,
        related_name='pagos_realizados',
        help_text="Paciente que realiza el pago"
    )
    
    # Datos del pago (del prototipo CU30, CU32)
    monto_pagado = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Monto de este pago específico"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        help_text="Método utilizado para el pago"
    )
    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        help_text="Estado actual del pago"
    )
    
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó el pago"
    )
    
    # Campos para pagos online (Stripe, PayPal, MercadoPago)
    transaccion_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID de la sesión de checkout (Stripe session_id, PayPal order_id, etc.)"
    )
    payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID de la intención de pago (Stripe payment_intent)"
    )
    datos_pago = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos completos de la transacción de la pasarela"
    )
    
    # Campo antiguo para compatibilidad
    referencia_transaccion = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="ID de transacción, Nro. de cheque, etc."
    )
    
    descripcion = models.CharField(
        max_length=500,
        blank=True,
        help_text="Descripción del pago"
    )
    
    notas = models.TextField(
        blank=True, 
        null=True,
        help_text="Notas adicionales sobre el pago"
    )
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']

    def __str__(self):
        if self.tipo_pago == self.TipoPago.FACTURA and self.factura:
            return f"Pago de Bs. {self.monto_pagado} para Factura #{self.factura.id}"
        elif self.tipo_pago == self.TipoPago.CITA and self.cita:
            return f"Pago de Bs. {self.monto_pagado} para Cita #{self.cita.id}"
        elif self.tipo_pago == self.TipoPago.PLAN and self.plan_tratamiento:
            return f"Pago de Bs. {self.monto_pagado} para Plan #{self.plan_tratamiento.id}"
        return f"Pago de Bs. {self.monto_pagado} ({self.get_tipo_pago_display()})"

    def save(self, *args, **kwargs):
        """
        Al guardar un pago, actualiza el total pagado en la factura si aplica.
        """
        super().save(*args, **kwargs)
        
        # Solo recalcular si el pago está completado y tiene factura
        if self.estado_pago == self.EstadoPago.COMPLETADO and self.factura:
            self.factura.recalcular_monto_pagado()
    
    def marcar_completado(self):
        """
        Marca el pago como completado y actualiza la factura o entidad relacionada.
        """
        from django.utils import timezone
        self.estado_pago = self.EstadoPago.COMPLETADO
        self.fecha_completado = timezone.now()
        self.save()
        
        # Marcar cita como pagada si aplica
        if self.tipo_pago == self.TipoPago.CITA and self.cita:
            self.cita.pagada = True
            self.cita.save()

# Agregar método a Factura para recalcular
def recalcular_monto_pagado(self):
    """
    Recalcula el monto pagado basado en pagos completados.
    """
    total_pagado = self.pagos.filter(estado_pago=Pago.EstadoPago.COMPLETADO).aggregate(
        total=models.Sum('monto_pagado')
    )['total'] or Decimal('0.00')
    
    self.monto_pagado = total_pagado
    self.actualizar_estado_pago()

# Añadir el método a la clase Factura
Factura.recalcular_monto_pagado = recalcular_monto_pagado
