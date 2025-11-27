# facturacion/serializers.py

from rest_framework import serializers
from decimal import Decimal
from .models import Factura, Pago

class PagoSerializer(serializers.ModelSerializer):
    """
    Serializer para Pagos (CU30, CU32, CU33)
    """
    paciente_nombre = serializers.CharField(source='paciente.usuario.full_name', read_only=True)
    paciente_email = serializers.EmailField(source='paciente.usuario.email', read_only=True)
    factura_numero = serializers.SerializerMethodField()
    factura_total = serializers.SerializerMethodField()
    cita_info = serializers.SerializerMethodField()
    
    def get_factura_numero(self, obj):
        return obj.factura.id if obj.factura else None
    
    def get_factura_total(self, obj):
        return obj.factura.monto_total if obj.factura else None
    
    def get_cita_info(self, obj):
        if obj.tipo_pago == 'CITA' and obj.cita:
            return {
                'id': obj.cita.id,
                'fecha': obj.cita.fecha_hora.strftime('%Y-%m-%d %H:%M'),
                'motivo': obj.cita.get_motivo_tipo_display() if obj.cita.motivo_tipo else None
            }
        return None
    
    class Meta:
        model = Pago
        fields = (
            'id', 'tipo_pago', 'factura', 'factura_numero', 'factura_total',
            'cita', 'cita_info',
            'paciente', 'paciente_nombre', 'paciente_email', 
            'monto_pagado', 'metodo_pago', 'estado_pago', 
            'fecha_pago', 'referencia_transaccion', 'notas'
        )
        read_only_fields = ('id', 'fecha_pago', 'paciente_nombre', 'paciente_email', 'factura_numero', 'factura_total', 'cita_info')
    
    def validate_monto_pagado(self, value):
        """Validar que el monto sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto pagado debe ser mayor a 0.")
        return value
    
    def validate(self, data):
        """Validaciones cruzadas."""
        factura = data.get('factura')
        monto_pagado = data.get('monto_pagado', 0)
        
        if factura:
            # Verificar que la factura no esté anulada
            if factura.estado == 'ANULADA':
                raise serializers.ValidationError("No se pueden registrar pagos en facturas anuladas.")
            
            # Verificar que el pago no exceda el saldo pendiente
            saldo_pendiente = factura.saldo_pendiente
            if monto_pagado > saldo_pendiente:
                raise serializers.ValidationError(
                    f"El monto pagado (Bs. {monto_pagado}) no puede ser mayor al saldo pendiente (Bs. {saldo_pendiente})."
                )
        
        return data


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear pagos."""
    
    class Meta:
        model = Pago
        fields = (
            'factura', 'monto_pagado', 'metodo_pago', 
            'referencia_transaccion', 'notas'
        )
    
    def validate_monto_pagado(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value


class FacturaSerializer(serializers.ModelSerializer):
    """
    Serializer para Facturas (CU31)
    """
    paciente_nombre = serializers.CharField(source='paciente.usuario.full_name', read_only=True)
    paciente_email = serializers.EmailField(source='paciente.usuario.email', read_only=True)
    paciente_ci = serializers.CharField(source='paciente.usuario.ci', read_only=True)
    paciente_telefono = serializers.CharField(source='paciente.usuario.telefono', read_only=True)
    
    presupuesto_numero = serializers.IntegerField(source='presupuesto.id', read_only=True)
    presupuesto_token = serializers.CharField(source='presupuesto.token_aceptacion', read_only=True)
    
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Anidamos los pagos para ver el detalle en una sola consulta
    pagos = PagoSerializer(many=True, read_only=True)
    
    # Campos calculados
    total_pagos = serializers.SerializerMethodField()
    porcentaje_pagado = serializers.SerializerMethodField()
    
    class Meta:
        model = Factura
        fields = (
            # Información básica
            'id', 'estado', 'fecha_emision', 'fecha_anulacion',
            
            # Información del paciente
            'paciente', 'paciente_nombre', 'paciente_email', 
            'paciente_ci', 'paciente_telefono',
            
            # Información del presupuesto
            'presupuesto', 'presupuesto_numero', 'presupuesto_token',
            
            # Datos de facturación
            'nit_ci', 'razon_social',
            
            # Montos
            'monto_total', 'monto_pagado', 'saldo_pendiente',
            'total_pagos', 'porcentaje_pagado',
            
            # Pagos anidados
            'pagos'
        )
        read_only_fields = (
            'id', 'monto_pagado', 'saldo_pendiente', 'fecha_emision', 'fecha_anulacion',
            'pagos', 'paciente_nombre', 'paciente_email', 'paciente_ci', 'paciente_telefono',
            'presupuesto_numero', 'presupuesto_token', 'total_pagos', 'porcentaje_pagado'
        )
    
    def get_total_pagos(self, obj):
        """Número total de pagos registrados."""
        return obj.pagos.count()
    
    def get_porcentaje_pagado(self, obj):
        """Porcentaje pagado de la factura."""
        if obj.monto_total > 0:
            return round((obj.monto_pagado / obj.monto_total) * 100, 2)
        return 0
    
    def validate_monto_total(self, value):
        """Validar que el monto total sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a 0.")
        return value


class FacturaCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear facturas."""
    
    class Meta:
        model = Factura
        fields = (
            'paciente', 'presupuesto', 'monto_total', 
            'nit_ci', 'razon_social'
        )
    
    def validate_presupuesto(self, value):
        """Validar que el presupuesto esté aceptado."""
        if value and value.estado != 'ACEPTADO':
            raise serializers.ValidationError("Solo se pueden facturar presupuestos aceptados.")
        
        # Verificar que no tenga ya una factura
        if hasattr(value, 'factura') and value.factura:
            raise serializers.ValidationError("Este presupuesto ya tiene una factura asociada.")
        
        return value
    
    def create(self, validated_data):
        """Crear factura con datos del presupuesto."""
        presupuesto = validated_data.get('presupuesto')
        
        # Si no se especifica monto_total, usar el del presupuesto
        if presupuesto and not validated_data.get('monto_total'):
            validated_data['monto_total'] = presupuesto.total
        
        # Si no se especifica paciente, usar el del presupuesto
        if presupuesto and not validated_data.get('paciente'):
            validated_data['paciente'] = presupuesto.plan_tratamiento.paciente
        
        return super().create(validated_data)


class FacturaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de facturas."""
    
    paciente_nombre = serializers.CharField(source='paciente.usuario.full_name', read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_pagos = serializers.SerializerMethodField()
    
    # Campos adicionales para compatibilidad con frontend
    numero = serializers.IntegerField(source='id', read_only=True)
    fecha = serializers.DateTimeField(source='fecha_emision', read_only=True)
    monto = serializers.DecimalField(source='monto_total', max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(source='monto_total', max_digits=10, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(source='saldo_pendiente', max_digits=10, decimal_places=2, read_only=True)
    descripcion = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Factura
        fields = (
            # Campos originales
            'id', 'paciente_nombre', 'estado', 'estado_display', 'monto_total', 
            'monto_pagado', 'saldo_pendiente', 'fecha_emision', 'total_pagos',
            # Campos compatibilidad frontend
            'numero', 'fecha', 'monto', 'total', 'saldo', 'descripcion'
        )
    
    def get_total_pagos(self, obj):
        return obj.pagos.count()
    
    def get_descripcion(self, obj):
        """Generar descripción automática de la factura."""
        if obj.presupuesto:
            return f"Factura por tratamiento - Presupuesto #{obj.presupuesto.id}"
        return f"Factura #{obj.id}"