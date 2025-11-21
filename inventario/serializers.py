"""
Serializers para la API de Inventario.
"""
from rest_framework import serializers
from .models import CategoriaInsumo, Insumo


class CategoriaInsumoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CategoriaInsumo.
    """
    total_insumos = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoriaInsumo
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activo',
            'total_insumos',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']
    
    def get_total_insumos(self, obj):
        """Retorna el total de insumos en esta categoría."""
        return obj.insumos.filter(activo=True).count()


class InsumoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Insumo.
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    # Convertir decimales a float para compatibilidad con frontend
    margen_ganancia = serializers.FloatField(read_only=True)
    precio_costo = serializers.FloatField()
    precio_venta = serializers.FloatField()
    
    requiere_reposicion = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Insumo
        fields = [
            'id',
            'categoria',
            'categoria_nombre',
            'codigo',
            'nombre',
            'descripcion',
            'precio_costo',
            'precio_venta',
            'margen_ganancia',
            'stock_actual',
            'stock_minimo',
            'requiere_reposicion',
            'unidad_medida',
            'proveedor',
            'activo',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']
    
    def validate_precio_venta(self, value):
        """Validar que el precio de venta no sea menor al precio de costo."""
        precio_costo = self.initial_data.get('precio_costo')
        if precio_costo and value < float(precio_costo):
            raise serializers.ValidationError(
                "El precio de venta no puede ser menor al precio de costo."
            )
        return value
    
    def validate_codigo(self, value):
        """Validar que el código sea único."""
        if self.instance:
            # Si estamos editando, excluir el registro actual
            if Insumo.objects.exclude(pk=self.instance.pk).filter(codigo=value).exists():
                raise serializers.ValidationError("Ya existe un insumo con este código.")
        else:
            # Si estamos creando, verificar que no exista
            if Insumo.objects.filter(codigo=value).exists():
                raise serializers.ValidationError("Ya existe un insumo con este código.")
        return value


class InsumoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar insumos (más ligero).
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    requiere_reposicion = serializers.BooleanField(read_only=True)
    
    # Convertir decimales a float para compatibilidad con frontend
    precio_costo = serializers.FloatField(read_only=True)
    precio_venta = serializers.FloatField(read_only=True)
    stock_actual = serializers.IntegerField(read_only=True)
    stock_minimo = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Insumo
        fields = [
            'id',
            'codigo',
            'nombre',
            'categoria_nombre',
            'precio_costo',
            'precio_venta',
            'stock_actual',
            'stock_minimo',
            'unidad_medida',
            'requiere_reposicion',
            'activo'
        ]
