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
    
    Usado para mostrar evolución de datos a lo largo del tiempo con desglose por estado.
    
    Ejemplo de salida:
    [
        {"fecha": "2025-11-01", "cantidad": 5, "completadas": 3, "canceladas": 1}, 
        {"fecha": "2025-11-02", "cantidad": 8, "completadas": 6, "canceladas": 0},
        {"fecha": "2025-11-03", "cantidad": 3, "completadas": 2, "canceladas": 1}
    ]
    """
    fecha = serializers.DateField(
        help_text="Fecha del punto de datos"
    )
    cantidad = serializers.IntegerField(
        help_text="Cantidad total registrada en esa fecha"
    )
    completadas = serializers.IntegerField(
        required=False,
        help_text="Cantidad de citas completadas en esa fecha"
    )
    canceladas = serializers.IntegerField(
        required=False,
        help_text="Cantidad de citas canceladas en esa fecha"
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
    Serializer para estadísticas generales completas del sistema.
    
    Usado en dashboards y resúmenes ejecutivos.
    
    Incluye métricas agrupadas por categoría:
    - Pacientes: activos, nuevos del mes
    - Citas: total, completadas, pendientes, canceladas
    - Tratamientos: completados, planes activos, procedimientos
    - Financiero: ingresos, pendiente, facturas vencidas
    """
    # Pacientes
    total_pacientes_activos = serializers.IntegerField(
        help_text="Total de pacientes activos en el sistema"
    )
    pacientes_nuevos_mes = serializers.IntegerField(
        help_text="Pacientes registrados en el mes actual"
    )
    
    # Odontólogos
    total_odontologos = serializers.IntegerField(
        help_text="Total de odontólogos activos"
    )
    
    # Citas
    citas_mes_actual = serializers.IntegerField(
        help_text="Total de citas del mes (sin canceladas)"
    )
    citas_completadas = serializers.IntegerField(
        help_text="Citas completadas en el mes"
    )
    citas_pendientes = serializers.IntegerField(
        help_text="Citas pendientes o confirmadas"
    )
    citas_canceladas = serializers.IntegerField(
        help_text="Citas canceladas en el mes"
    )
    
    # Tratamientos
    tratamientos_completados = serializers.IntegerField(
        help_text="Planes de tratamiento completados"
    )
    planes_activos = serializers.IntegerField(
        help_text="Planes en progreso, propuestos o aprobados"
    )
    total_procedimientos = serializers.IntegerField(
        help_text="Total de procedimientos realizados"
    )
    
    # Financiero
    ingresos_mes_actual = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Ingresos del mes actual (pagos completados)"
    )
    monto_pendiente = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monto pendiente de cobro"
    )
    facturas_vencidas = serializers.IntegerField(
        help_text="Cantidad de facturas vencidas sin pagar"
    )
    promedio_factura = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Promedio de monto por factura"
    )
    
    # Ocupación
    tasa_ocupacion = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Porcentaje de ocupación de agenda"
    )


class BitacoraSerializer(serializers.ModelSerializer):
    """
    Serializer para registros de bitácora/auditoría (CU39).
    
    Muestra quién hizo qué, cuándo y desde dónde.
    """
    usuario = serializers.SerializerMethodField()
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    modelo = serializers.SerializerMethodField()
    
    class Meta:
        model = BitacoraAccion
        fields = [
            'id',
            'usuario',
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
    
    def get_usuario(self, obj):
        """Devuelve información completa del usuario"""
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.full_name,
                'email': obj.usuario.email,
                'tipo_usuario': obj.usuario.tipo_usuario
            }
        return {
            'id': None,
            'nombre_completo': 'Sistema',
            'email': 'sistema@clinica-demo.com',
            'tipo_usuario': 'SISTEMA'
        }
    
    def get_modelo(self, obj):
        """Devuelve el nombre del modelo afectado"""
        if obj.content_type:
            return obj.content_type.model
        return None
