from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# --- IMPORTACIONES ADICIONALES PARA PASO 2.B ---
# Importamos los modelos del Paso 1 (Inventario) para crear las "recetas"
from inventario.models import Insumo, CategoriaInsumo


class CategoriaServicio(models.Model):
    """
    Categorías para agrupar servicios odontológicos.
    Ejemplos: Odontología General, Ortodoncia, Endodoncia, Cirugía, Estética
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la categoría (ej: Odontología General, Ortodoncia)"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de la categoría"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si la categoría está activa"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización en listas"
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría de Servicio'
        verbose_name_plural = 'Categorías de Servicios'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    """
    Catálogo de servicios odontológicos que ofrece la clínica.
    
    Este modelo define los procedimientos básicos con sus honorarios base,
    pero NO incluye el costo de materiales (eso se calcula dinámicamente
    en base a los insumos seleccionados).
    
    Ejemplos:
    - Consulta de Diagnóstico
    - Limpieza Dental
    - Restauración Simple  
    - Endodoncia
    - Extracción Simple
    - Corona de Porcelana
    """
    categoria = models.ForeignKey(
        CategoriaServicio,
        on_delete=models.PROTECT,  # No eliminar categoría si tiene servicios
        related_name='servicios',
        help_text="Categoría a la que pertenece el servicio"
    )
    codigo_servicio = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código único del servicio (ej: CONS-001, REST-001)"
    )
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del servicio odontológico"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del procedimiento"
    )
    
    # Precio base (honorarios del profesional por tiempo/conocimiento)
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Honorarios base del servicio (sin materiales)"
    )
    
    # Información operacional
    tiempo_estimado = models.PositiveIntegerField(
        default=30,
        help_text="Tiempo estimado del procedimiento en minutos"
    )
    requiere_cita_previa = models.BooleanField(
        default=True,
        help_text="Si el servicio requiere cita programada"
    )
    requiere_autorizacion = models.BooleanField(
        default=False,
        help_text="Si requiere autorización especial (ej: cirugías)"
    )
    
    # Metadatos
    activo = models.BooleanField(
        default=True,
        help_text="Si el servicio está disponible para ser ofrecido"
    )
    notas_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas para uso interno del personal"
    )
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Catálogo de Servicios'
        ordering = ['categoria', 'nombre']
        indexes = [
            models.Index(fields=['codigo_servicio']),
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.codigo_servicio} - {self.nombre}"

    @property
    def duracion_formateada(self):
        """Retorna el tiempo estimado en formato legible"""
        if self.tiempo_estimado < 60:
            return f"{self.tiempo_estimado} min"
        else:
            horas = self.tiempo_estimado // 60
            minutos = self.tiempo_estimado % 60
            if minutos == 0:
                return f"{horas}h"
            else:
                return f"{horas}h {minutos}min"

    @property
    def categoria_nombre(self):
        """Helper para mostrar nombre de categoría"""
        return self.categoria.nombre if self.categoria else "Sin categoría"

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # El código debe ser uppercase y sin espacios
        if self.codigo_servicio:
            self.codigo_servicio = self.codigo_servicio.upper().replace(' ', '')
        
        # Tiempo mínimo de 5 minutos
        if self.tiempo_estimado < 5:
            raise ValidationError({'tiempo_estimado': 'El tiempo mínimo es de 5 minutos'})

    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)


# ===============================================================================
# PASO 2.B: MODELOS DE "RECETA" (Materiales por Servicio)
# ===============================================================================

class MaterialServicioFijo(models.Model):
    """
    Define un INSUMO específico que SIEMPRE se usa para un servicio.
    
    Ejemplos:
    - "Endodoncia" SIEMPRE usa 1x "Kit de Endodoncia"
    - "Consulta" SIEMPRE usa 1x "Ficha Médica"
    - "Limpieza" SIEMPRE usa 1x "Kit Limpieza Básica"
    
    Este material tiene precio fijo y se suma automáticamente al costo.
    """
    servicio = models.ForeignKey(
        Servicio, 
        on_delete=models.CASCADE, 
        related_name='materiales_fijos',
        help_text="Servicio que requiere este material"
    )
    insumo = models.ForeignKey(
        Insumo, 
        on_delete=models.PROTECT,  # Evita borrar un insumo si está en una receta
        related_name='servicios_fijos',
        help_text="Insumo específico que se usa"
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.0,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cantidad del insumo requerida"
    )
    es_obligatorio = models.BooleanField(
        default=True,
        help_text="Si este material es obligatorio para el servicio"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas sobre el uso de este material"
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Material Fijo de Servicio"
        verbose_name_plural = "Materiales Fijos de Servicio"
        # Evita duplicados: no se puede añadir el mismo insumo dos veces al mismo servicio
        unique_together = ('servicio', 'insumo')
        indexes = [
            models.Index(fields=['servicio', 'es_obligatorio']),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.insumo.nombre} para {self.servicio.nombre}"

    @property
    def costo_adicional(self):
        """
        Retorna el costo adicional que añade este material al servicio.
        Usa el precio de VENTA del insumo multiplicado por la cantidad.
        """
        return self.insumo.precio_venta * self.cantidad

    @property
    def costo_material_formateado(self):
        """Helper para mostrar el costo formateado"""
        return f"${self.costo_adicional:.2f}"

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        if self.cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a 0'})


class MaterialServicioOpcional(models.Model):
    """
    Define una CATEGORÍA de insumos de la cual se DEBE ELEGIR UNO.
    
    Ejemplos:
    - "Restauración" requiere 1x de la categoría "Resinas" 
      (el doctor elegirá: Resina 3M A1, Resina Genérica, etc.)
    - "Anestesia" requiere 1x de la categoría "Anestésicos"
      (el doctor elegirá: Lidocaína 2%, Articaína, etc.)
    
    El precio final dependerá del insumo específico elegido.
    """
    servicio = models.ForeignKey(
        Servicio, 
        on_delete=models.CASCADE, 
        related_name='materiales_opcionales',
        help_text="Servicio que requiere elegir un material"
    )
    categoria_insumo = models.ForeignKey(
        CategoriaInsumo, 
        on_delete=models.PROTECT, 
        related_name='servicios_opcionales',
        help_text="Categoría de insumos entre los que se puede elegir"
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.0,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cantidad requerida del insumo elegido"
    )
    es_obligatorio = models.BooleanField(
        default=True,
        help_text="Si es obligatorio elegir un material de esta categoría"
    )
    nombre_personalizado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nombre descriptivo para mostrar al usuario (ej: 'Tipo de Resina')"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Instrucciones o notas sobre la selección"
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Material Opcional de Servicio"
        verbose_name_plural = "Materiales Opcionales de Servicio"
        unique_together = ('servicio', 'categoria_insumo')
        indexes = [
            models.Index(fields=['servicio', 'es_obligatorio']),
        ]

    def __str__(self):
        nombre = self.nombre_personalizado or f"Elegir {self.categoria_insumo.nombre}"
        return f"{self.cantidad} x {nombre} para {self.servicio.nombre}"

    @property
    def opciones_disponibles(self):
        """Retorna los insumos disponibles de esta categoría"""
        return self.categoria_insumo.insumos.filter(activo=True)

    @property
    def rango_precios(self):
        """Retorna el rango de precios de los insumos disponibles"""
        opciones = self.opciones_disponibles
        if opciones.exists():
            precios = [insumo.precio_venta * self.cantidad for insumo in opciones]
            return {
                'minimo': min(precios),
                'maximo': max(precios),
                'promedio': sum(precios) / len(precios)
            }
        return {'minimo': 0, 'maximo': 0, 'promedio': 0}

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        if self.cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a 0'})


# ===============================================================================
# PASO 2.C: MODELOS DE PLAN DE TRATAMIENTO (CU19)
# ===============================================================================

class PlanDeTratamiento(models.Model):
    """
    Plan de tratamiento propuesto para un paciente.
    
    Este modelo representa el "plan maestro" que un odontólogo crea para un paciente,
    conteniendo una lista de servicios necesarios. Aquí es donde se materializa
    tu idea del precio dinámico: cada ítem del plan tendrá precios específicos
    basados en los materiales elegidos.
    
    Estados del plan:
    - PROPUESTO: El doctor creó el plan pero el paciente no lo ha visto
    - PRESENTADO: El plan fue mostrado al paciente
    - ACEPTADO: El paciente aceptó el plan y presupuesto
    - EN_PROGRESO: Se están ejecutando los tratamientos
    - COMPLETADO: Todos los tratamientos fueron realizados
    - CANCELADO: El plan fue cancelado
    """
    
    # Relaciones principales
    paciente = models.ForeignKey(
        'usuarios.PerfilPaciente',
        on_delete=models.CASCADE,
        related_name='planes_tratamiento',
        help_text="Paciente para quien se crea el plan"
    )
    odontologo = models.ForeignKey(
        'usuarios.PerfilOdontologo',
        on_delete=models.PROTECT,  # No eliminar odontólogo si tiene planes
        related_name='planes_creados',
        help_text="Odontólogo que crea el plan"
    )
    
    # Información del plan
    titulo = models.CharField(
        max_length=200,
        help_text="Título descriptivo del plan (ej: 'Rehabilitación Dental Completa')"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del plan de tratamiento"
    )
    
    # Estados del plan
    class EstadoPlan(models.TextChoices):
        PROPUESTO = 'PROPUESTO', 'Propuesto'
        PRESENTADO = 'PRESENTADO', 'Presentado al paciente'
        ACEPTADO = 'ACEPTADO', 'Aceptado por el paciente'
        EN_PROGRESO = 'EN_PROGRESO', 'En progreso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoPlan.choices,
        default=EstadoPlan.PROPUESTO,
        help_text="Estado actual del plan"
    )
    
    # Fechas importantes
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_presentacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha en que se presentó el plan al paciente"
    )
    fecha_aceptacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha en que el paciente aceptó el plan"
    )
    fecha_inicio = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha de inicio de los tratamientos"
    )
    fecha_finalizacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha de finalización de todos los tratamientos"
    )
    
    # Información adicional
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('BAJA', 'Baja'),
            ('MEDIA', 'Media'),
            ('ALTA', 'Alta'),
            ('URGENTE', 'Urgente')
        ],
        default='MEDIA',
        help_text="Prioridad del plan de tratamiento"
    )
    notas_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas internas para el equipo médico"
    )
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan de Tratamiento'
        verbose_name_plural = 'Planes de Tratamiento'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['paciente', 'estado']),
            models.Index(fields=['odontologo', 'fecha_creacion']),
            models.Index(fields=['estado', 'prioridad']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente.usuario.nombre} {self.paciente.usuario.apellido}"
    
    @property
    def precio_total_plan(self):
        """
        Calcula el precio total del plan sumando todos sus ítems.
        Este es el precio final que verá el paciente.
        """
        return sum(item.precio_total for item in self.items.all())
    
    @property
    def cantidad_items(self):
        """Retorna la cantidad de ítems en el plan"""
        return self.items.count()
    
    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de ítems completados"""
        total_items = self.cantidad_items
        if total_items == 0:
            return 0
        items_completados = self.items.filter(estado='COMPLETADO').count()
        return int((items_completados / total_items) * 100)
    
    def puede_ser_editado(self):
        """Determina si el plan puede ser editado"""
        return self.estado in ['PROPUESTO', 'PRESENTADO']
    
    def marcar_como_presentado(self):
        """Marca el plan como presentado al paciente"""
        if self.estado == self.EstadoPlan.PROPUESTO:
            self.estado = self.EstadoPlan.PRESENTADO
            from django.utils import timezone
            self.fecha_presentacion = timezone.now()
            self.save()
    
    def marcar_como_aceptado(self):
        """Marca el plan como aceptado por el paciente"""
        if self.estado in [self.EstadoPlan.PROPUESTO, self.EstadoPlan.PRESENTADO]:
            self.estado = self.EstadoPlan.ACEPTADO
            from django.utils import timezone
            self.fecha_aceptacion = timezone.now()
            self.save()
    
    def actualizar_progreso(self):
        """
        Actualiza automáticamente el estado del plan basado en el progreso de sus ítems.
        
        Este método implementa la lógica del MODELO HÍBRIDO:
        - Se llama automáticamente desde los signals cuando se crea un episodio vinculado
        - Actualiza el estado del plan según el progreso de los ítems
        
        Transiciones de estado:
        - ACEPTADO → EN_PROGRESO: Cuando se completa el primer ítem
        - EN_PROGRESO → COMPLETADO: Cuando se completan todos los ítems
        
        También actualiza las fechas de inicio y finalización.
        """
        from django.utils import timezone
        
        # Obtener estadísticas de los ítems
        total_items = self.items.count()
        
        if total_items == 0:
            return  # Plan sin ítems, no hacer nada
        
        items_completados = self.items.filter(estado='COMPLETADO').count()
        items_en_progreso = self.items.filter(estado='EN_PROGRESO').count()
        
        # ============================================================================
        # TRANSICIÓN: ACEPTADO → EN_PROGRESO
        # ============================================================================
        
        if self.estado == self.EstadoPlan.ACEPTADO:
            # Si hay al menos un ítem EN_PROGRESO o COMPLETADO
            if items_en_progreso > 0 or items_completados > 0:
                self.estado = self.EstadoPlan.EN_PROGRESO
                self.fecha_inicio = timezone.now()
                self.save(update_fields=['estado', 'fecha_inicio'])
                print(f"   🚀 Plan iniciado: ACEPTADO → EN_PROGRESO")
        
        # ============================================================================
        # TRANSICIÓN: EN_PROGRESO → COMPLETADO
        # ============================================================================
        
        elif self.estado == self.EstadoPlan.EN_PROGRESO:
            # Si TODOS los ítems están completados
            if items_completados == total_items:
                self.estado = self.EstadoPlan.COMPLETADO
                self.fecha_finalizacion = timezone.now()
                self.save(update_fields=['estado', 'fecha_finalizacion'])
                print(f"   🎉 Plan completado: EN_PROGRESO → COMPLETADO")
        
        # ============================================================================
        # ACTUALIZACIÓN DE METADATOS
        # ============================================================================
        
        # Actualizar fecha_inicio si no existe y hay progreso
        if not self.fecha_inicio and (items_en_progreso > 0 or items_completados > 0):
            self.fecha_inicio = timezone.now()
            self.save(update_fields=['fecha_inicio'])
        
        return {
            'total_items': total_items,
            'items_completados': items_completados,
            'items_en_progreso': items_en_progreso,
            'porcentaje': self.porcentaje_completado,
            'estado': self.estado
        }


class ItemPlanTratamiento(models.Model):
    """
    Ítem individual dentro de un plan de tratamiento.
    
    ¡AQUÍ ES DONDE SE MATERIALIZA TU IDEA DEL PRECIO DINÁMICO!
    
    Cada ítem representa un servicio específico (ej: "Restauración Simple")
    con materiales específicos elegidos por el doctor (ej: "Resina 3M A1").
    
    El precio final se calcula automáticamente como:
    precio_total = precio_servicio_snapshot + precio_materiales_fijos + precio_insumo_seleccionado
    
    Los precios se "congelen" (snapshot) al momento de crear el ítem para que
    no cambien si después actualizas los precios en el inventario.
    """
    
    # Relaciones principales
    plan = models.ForeignKey(
        PlanDeTratamiento,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Plan de tratamiento al que pertenece este ítem"
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,  # No eliminar servicio si está en un plan
        related_name='items_plan',
        help_text="Servicio a realizar"
    )
    
    # PASO 2.C: AQUÍ ESTÁ TU IDEA - SELECCIÓN DE MATERIAL ESPECÍFICO
    insumo_seleccionado = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='planes_donde_usado',
        help_text="Insumo específico elegido para materiales opcionales"
    )
    
    # SNAPSHOTS DE PRECIOS (para que no cambien después)
    precio_servicio_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio base del servicio al momento de crear el ítem"
    )
    precio_materiales_fijos_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Costo de materiales fijos al momento de crear el ítem"
    )
    precio_insumo_seleccionado_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Precio del insumo seleccionado al momento de crear el ítem"
    )
    
    # Estado del ítem
    class EstadoItem(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En progreso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoItem.choices,
        default=EstadoItem.PENDIENTE,
        help_text="Estado de este ítem específico"
    )
    
    # Información adicional
    orden = models.PositiveIntegerField(
        default=1,
        help_text="Orden de ejecución de este ítem en el plan"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas específicas para este ítem"
    )
    fecha_estimada = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha estimada para realizar este tratamiento"
    )
    fecha_realizada = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se realizó el tratamiento"
    )
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ítem Plan Tratamiento'
        verbose_name_plural = 'Ítems Plan Tratamiento'
        ordering = ['plan', 'orden']
        indexes = [
            models.Index(fields=['plan', 'orden']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        insumo_info = f" ({self.insumo_seleccionado.nombre})" if self.insumo_seleccionado else ""
        return f"{self.servicio.nombre}{insumo_info} - {self.plan.titulo}"
    
    @property
    def precio_total(self):
        """
        ¡EL CORAZÓN DE TU IDEA!
        
        Calcula el precio total dinámico de este ítem:
        - Honorarios del servicio (del snapshot)
        - Costo de materiales fijos (del snapshot)  
        - Precio del material opcional elegido (del snapshot)
        
        Ejemplo:
        - Restauración Simple: $80 (honorarios)
        - Materiales fijos (lidocaína): $18
        - Material elegido (Resina 3M): $75
        - TOTAL: $173
        """
        return (
            self.precio_servicio_snapshot + 
            self.precio_materiales_fijos_snapshot + 
            self.precio_insumo_seleccionado_snapshot
        )
    
    @property
    def precio_total_formateado(self):
        """Retorna el precio total formateado para mostrar"""
        return f"${self.precio_total:.2f}"
    
    def actualizar_snapshots(self):
        """
        Actualiza los precios snapshot basándose en los precios actuales.
        Se llama automáticamente al crear/editar el ítem.
        """
        # Snapshot del precio base del servicio
        self.precio_servicio_snapshot = self.servicio.precio_base
        
        # Snapshot del costo de materiales fijos
        materiales_fijos_total = sum(
            material.costo_adicional 
            for material in self.servicio.materiales_fijos.all()
        )
        self.precio_materiales_fijos_snapshot = materiales_fijos_total
        
        # Snapshot del precio del insumo seleccionado
        if self.insumo_seleccionado:
            self.precio_insumo_seleccionado_snapshot = self.insumo_seleccionado.precio_venta
        else:
            self.precio_insumo_seleccionado_snapshot = Decimal('0.00')
    
    def marcar_como_completado(self):
        """Marca este ítem como completado"""
        self.estado = self.EstadoItem.COMPLETADO
        from django.utils import timezone
        self.fecha_realizada = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save para actualizar snapshots automáticamente"""
        # Actualizar snapshots de precios si es la primera vez o si cambiaron los materiales
        if not self.pk or 'actualizar_precios' in kwargs:
            if 'actualizar_precios' in kwargs:
                kwargs.pop('actualizar_precios')
            self.actualizar_snapshots()
        
        super().save(*args, **kwargs)


# ===============================================================================
# PASO 2.D: PRESUPUESTO Y ACEPTACIÓN (CU20, CU21)
# ===============================================================================

class Presupuesto(models.Model):
    """
    Representa una oferta formal (Presupuesto) basada en un Plan de Tratamiento.
    
    ¡ESTO ES LO QUE EL PACIENTE ACEPTA! (CU20, CU21)
    
    Es un "snapshot" inmutable del plan que congela todos los precios
    y permite al paciente aceptar la propuesta mediante un token único.
    """
    class EstadoPresupuesto(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PRESENTADO = 'PRESENTADO', 'Presentado'
        ACEPTADO = 'ACEPTADO', 'Aceptado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'
        VENCIDO = 'VENCIDO', 'Vencido'

    # Vinculado al plan que lo originó
    plan_tratamiento = models.ForeignKey(
        PlanDeTratamiento,
        on_delete=models.CASCADE,
        related_name='presupuestos',
        help_text="Plan de tratamiento del cual se genera este presupuesto"
    )
    
    # Datos del presupuesto
    version = models.PositiveIntegerField(
        default=1, 
        help_text="Versión del presupuesto para este plan (permite múltiples versiones)"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoPresupuesto.choices,
        default=EstadoPresupuesto.BORRADOR,
        help_text="Estado actual del presupuesto"
    )
    
    # Snapshots de totales (Copia de los totales en el momento de la creación)
    subtotal_servicios = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total de todos los servicios base"
    )
    subtotal_materiales_fijos = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total de materiales fijos incluidos"
    )
    subtotal_materiales_opcionales = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total de materiales opcionales seleccionados"
    )
    descuento_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Descuentos aplicados (si los hay)"
    )
    total_presupuestado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Precio total final del presupuesto"
    )

    # Fechas importantes
    fecha_presentacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Cuándo se presentó el presupuesto al paciente"
    )
    fecha_vencimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha límite para aceptar el presupuesto"
    )
    fecha_aceptacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Cuándo el paciente aceptó el presupuesto"
    )
    
    # Token para aceptación digital (CU21)
    token_aceptacion = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        help_text="Token único para que el paciente pueda aceptar sin login"
    )
    
    # Metadatos
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ['-fecha_presentacion', '-version']
        # Un plan solo puede tener una versión activa a la vez
        unique_together = ('plan_tratamiento', 'version')
        indexes = [
            models.Index(fields=['plan_tratamiento', 'estado']),
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['token_aceptacion']),
        ]

    def __str__(self):
        return f"Presupuesto V{self.version} para {self.plan_tratamiento.titulo}"

    @property
    def esta_vencido(self):
        """Verifica si el presupuesto está vencido"""
        if not self.fecha_vencimiento:
            return False
        from django.utils import timezone
        return timezone.now().date() > self.fecha_vencimiento

    @property 
    def puede_ser_aceptado(self):
        """Verifica si el presupuesto puede ser aceptado"""
        return (
            self.estado == self.EstadoPresupuesto.PRESENTADO and 
            not self.esta_vencido
        )

    def calcular_totales_desde_plan(self):
        """
        Copia los precios calculados del Plan de Tratamiento.
        ¡Esto "congela" el precio para siempre!
        """
        # Calcular subtotales desde los ítems del plan
        items = self.plan_tratamiento.items.all()
        
        self.subtotal_servicios = sum(item.precio_servicio_snapshot for item in items)
        self.subtotal_materiales_fijos = sum(item.precio_materiales_fijos_snapshot for item in items)
        self.subtotal_materiales_opcionales = sum(item.precio_insumo_seleccionado_snapshot for item in items)
        
        # Por ahora no hay descuentos, pero se puede agregar lógica aquí
        self.descuento_total = Decimal('0.00')
        
        # Calcular total
        self.total_presupuestado = (
            self.subtotal_servicios + 
            self.subtotal_materiales_fijos + 
            self.subtotal_materiales_opcionales - 
            self.descuento_total
        )
        
        self.save()

    def presentar(self):
        """Presenta el presupuesto al paciente"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.estado = self.EstadoPresupuesto.PRESENTADO
        self.fecha_presentacion = timezone.now()
        
        # Vence en 30 días por defecto
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = timezone.now().date() + timedelta(days=30)
        
        self.save()

    def aceptar(self):
        """El paciente acepta el presupuesto"""
        if not self.puede_ser_aceptado:
            raise ValueError("Este presupuesto no puede ser aceptado")
        
        from django.utils import timezone
        
        self.estado = self.EstadoPresupuesto.ACEPTADO
        self.fecha_aceptacion = timezone.now()
        self.save()
        
        # Actualizar el plan de tratamiento
        self.plan_tratamiento.estado = PlanDeTratamiento.EstadoPlan.ACEPTADO
        self.plan_tratamiento.fecha_aceptacion = self.fecha_aceptacion
        self.plan_tratamiento.save()

    def rechazar(self, motivo=None):
        """Rechaza el presupuesto"""
        self.estado = self.EstadoPresupuesto.RECHAZADO
        self.save()


class ItemPresupuesto(models.Model):
    """
    Un "Snapshot" o "foto" de un ItemPlanTratamiento en el momento
    en que se genera el presupuesto. 
    
    ¡ESTO ES INMUTABLE! Una vez creado, no se puede cambiar.
    Garantiza que el paciente vea exactamente lo que va a pagar.
    """
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Presupuesto al que pertenece este ítem"
    )
    
    # Referencia al ítem original (puede ser null si se borra el plan)
    item_plan_original = models.ForeignKey(
        ItemPlanTratamiento,
        on_delete=models.SET_NULL, # Si borran el ítem del plan, el presupuesto no cambia
        null=True, 
        blank=True,
        related_name='snapshots_presupuesto',
        help_text="Ítem original del plan (referencia)"
    )
    
    # --- Snapshots de datos (copiados del ítem original) ---
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden del ítem en el presupuesto"
    )
    nombre_servicio = models.CharField(
        max_length=200,
        help_text="Nombre del servicio (snapshot)"
    )
    nombre_insumo_seleccionado = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Nombre del material seleccionado (snapshot)"
    )
    
    # --- Snapshots de precios (congelados para siempre) ---
    precio_servicio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio del servicio base (congelado)"
    )
    precio_materiales_fijos = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio de materiales fijos (congelado)"
    )
    precio_insumo_seleccionado = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio del material opcional (congelado)"
    )
    precio_total_item = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio total del ítem (congelado)"
    )

    # Metadatos
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ítem de Presupuesto"
        verbose_name_plural = "Ítems de Presupuesto"
        ordering = ['orden']
        indexes = [
            models.Index(fields=['presupuesto', 'orden']),
        ]

    def __str__(self):
        insumo_info = f" + {self.nombre_insumo_seleccionado}" if self.nombre_insumo_seleccionado else ""
        return f"{self.nombre_servicio}{insumo_info} (${self.precio_total_item})"

    @property
    def precio_total_formateado(self):
        """Precio total formateado para mostrar"""
        return f"${self.precio_total_item:,.2f}"
