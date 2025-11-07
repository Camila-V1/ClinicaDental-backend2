from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CategoriaInsumo(models.Model):
    """
    Categorías para agrupar insumos/materiales.
    Ejemplos: Resinas, Anestésicos, Instrumental, Materiales de Impresión, etc.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la categoría (ej: Resinas, Anestésicos)"
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
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría Insumo'
        verbose_name_plural = 'Categorías Insumos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    """
    Materiales e insumos utilizados en los tratamientos dentales.
    Cada insumo tiene precio de costo, precio de venta y stock actual.
    
    Ejemplos:
    - Resina 3M Filtek Z350 A1
    - Resina Genérica Z3
    - Anestesia Lidocaína 2%
    - Guantes de látex (caja)
    """
    categoria = models.ForeignKey(
        CategoriaInsumo,
        on_delete=models.PROTECT,  # No eliminar categoría si tiene insumos
        related_name='insumos',
        help_text="Categoría a la que pertenece el insumo"
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único del insumo (SKU)"
    )
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del insumo/material"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del insumo"
    )
    
    # Precios
    precio_costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Precio de costo del insumo"
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Precio de venta del insumo (al incluirlo en un tratamiento)"
    )
    
    # Control de Stock (CU34, CU35, CU36)
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cantidad actual en stock"
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cantidad mínima antes de alertar"
    )
    unidad_medida = models.CharField(
        max_length=20,
        default='unidad',
        help_text="Unidad de medida (unidad, caja, ml, g, etc.)"
    )
    
    # Información adicional
    proveedor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre del proveedor principal"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si el insumo está activo para ser usado"
    )
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria', 'activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia en porcentaje"""
        if self.precio_costo > 0:
            return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
        return 0

    @property
    def requiere_reposicion(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo

    def ajustar_stock(self, cantidad, motivo=''):
        """
        Ajusta el stock del insumo.
        Cantidad positiva = entrada, cantidad negativa = salida
        """
        self.stock_actual += cantidad
        self.save()
        # Aquí podrías registrar el movimiento en un modelo MovimientoInventario
        return self.stock_actual
