# reportes/serializers.py

from rest_framework import serializers
from .models import BitacoraAccion

class ReporteSimpleSerializer(serializers.Serializer):
    """
    Serializer genérico para reportes simples de tipo 'etiqueta-valor'.
    
    Usado para KPIs, rankings y datos categóricos.
    
    Ejemplo de salida:
    [
        {"etiqueta": "Endodoncia", "valor": 10}, 
        {"etiqueta": "Restauración", "valor": 5},
        {"etiqueta": "Limpieza", "valor": 15}
    ]
    """
    etiqueta = serializers.CharField(
        help_text="Nombre o descripción del elemento reportado"
    )
    valor = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Valor numérico asociado (cantidad, monto, porcentaje, etc.)"
    )


class ReporteTendenciaSerializer(serializers.Serializer):
    """
    Serializer para reportes de tendencias temporales (gráficos de líneas).
    
    Usado para mostrar evolución de datos a lo largo del tiempo.
    
    Ejemplo de salida:
    [
        {"fecha": "2025-11-01", "cantidad": 5}, 
        {"fecha": "2025-11-02", "cantidad": 8},
        {"fecha": "2025-11-03", "cantidad": 3}
    ]
    """
    fecha = serializers.DateField(
        help_text="Fecha del punto de datos"
    )
    cantidad = serializers.IntegerField(
        help_text="Cantidad registrada en esa fecha"
    )


class ReporteFinancieroSerializer(serializers.Serializer):
    """
    Serializer para reportes financieros con información monetaria detallada.
    
    Ejemplo de salida:
    {
        "periodo": "2025-11",
        "total_facturado": 15000.00,
        "total_pagado": 12000.00,
        "saldo_pendiente": 3000.00,
        "numero_facturas": 25
    }
    """
    periodo = serializers.CharField(
        help_text="Período del reporte (ej: '2025-11', '2025-Q1')"
    )
    total_facturado = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monto total facturado en el período"
    )
    total_pagado = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monto total pagado en el período"  
    )
    saldo_pendiente = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Saldo pendiente de pago"
    )
    numero_facturas = serializers.IntegerField(
        help_text="Cantidad de facturas generadas"
    )


class ReporteEstadisticasGeneralesSerializer(serializers.Serializer):
    """
    Serializer para estadísticas generales del sistema.
    
    Usado en dashboards y resúmenes ejecutivos.
    """
    total_pacientes_activos = serializers.IntegerField()
    total_odontologos = serializers.IntegerField()
    citas_mes_actual = serializers.IntegerField()
    tratamientos_completados = serializers.IntegerField()
    ingresos_mes_actual = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_factura = serializers.DecimalField(max_digits=10, decimal_places=2)
    tasa_ocupacion = serializers.DecimalField(max_digits=5, decimal_places=2)  # Porcentaje


class BitacoraSerializer(serializers.ModelSerializer):
    """
    Serializer para registros de bitácora/auditoría (CU39).
    
    Muestra quién hizo qué, cuándo y desde dónde.
    """
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    modelo = serializers.SerializerMethodField()
    
    class Meta:
        model = BitacoraAccion
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'accion',
            'accion_display',
            'modelo',
            'object_id',
            'descripcion',
            'detalles',
            'fecha_hora',
            'ip_address',
            'user_agent'
        ]
        read_only_fields = ['id', 'fecha_hora']
    
    def get_modelo(self, obj):
        """Devuelve el nombre del modelo afectado"""
        if obj.content_type:
            return obj.content_type.model
        return None
