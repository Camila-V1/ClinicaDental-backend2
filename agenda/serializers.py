from rest_framework import serializers
from .models import Cita
from django.utils import timezone


class CitaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cita.
    Convierte instancias de Cita a/desde JSON para la API REST.
    """
    
    # Campos de solo lectura con información adicional
    paciente_nombre = serializers.CharField(
        source='paciente.usuario.nombre',
        read_only=True
    )
    paciente_email = serializers.EmailField(
        source='paciente.usuario.email',
        read_only=True
    )
    odontologo_nombre = serializers.CharField(
        source='odontologo.usuario.nombre',
        read_only=True
    )
    odontologo_email = serializers.EmailField(
        source='odontologo.usuario.email',
        read_only=True
    )
    odontologo_especialidad = serializers.CharField(
        source='odontologo.especialidad',
        read_only=True
    )
    
    # Campos relacionados con motivo y precio
    motivo_tipo_display = serializers.CharField(
        source='get_motivo_tipo_display',
        read_only=True
    )
    precio = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    precio_display = serializers.CharField(read_only=True)
    es_cita_plan = serializers.BooleanField(read_only=True)
    requiere_pago = serializers.BooleanField(read_only=True)
    
    # Información del ítem del plan (si aplica)
    item_plan_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Cita
        fields = [
            'id',
            'paciente',
            'paciente_nombre',
            'paciente_email',
            'odontologo',
            'odontologo_nombre',
            'odontologo_email',
            'odontologo_especialidad',
            'fecha_hora',
            'motivo_tipo',
            'motivo_tipo_display',
            'motivo',
            'observaciones',
            'estado',
            'precio',
            'precio_display',
            'es_cita_plan',
            'requiere_pago',
            'item_plan',
            'item_plan_info',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']
    
    def get_item_plan_info(self, obj):
        """
        Retorna información detallada del ítem del plan si existe.
        """
        if not obj.item_plan:
            return None
        
        item = obj.item_plan
        return {
            'id': item.id,
            'servicio_nombre': item.servicio.nombre if item.servicio else None,
            'servicio_descripcion': item.servicio.descripcion if item.servicio else None,
            'descripcion': item.descripcion,
            'precio_unitario': str(item.precio_unitario),
            'cantidad': item.cantidad,
            'subtotal': str(item.subtotal),
            'completado': item.completado,
            'plan_id': item.plan.id,
            'plan_nombre': item.plan.nombre,
            'paciente_nombre': item.plan.paciente.usuario.nombre_completo if hasattr(item.plan.paciente.usuario, 'nombre_completo') else f"{item.plan.paciente.usuario.nombre} {item.plan.paciente.usuario.apellido}"
        }
    
    def validate_fecha_hora(self, value):
        """
        Validar que la fecha de la cita sea futura.
        """
        if value < timezone.now():
            raise serializers.ValidationError(
                "La fecha de la cita debe ser en el futuro."
            )
        return value
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto.
        """
        # Validar que el paciente y odontólogo sean diferentes usuarios
        if 'paciente' in data and 'odontologo' in data:
            if data['paciente'].usuario.id == data['odontologo'].usuario.id:
                raise serializers.ValidationError(
                    "El paciente y el odontólogo no pueden ser la misma persona."
                )
        
        # Validar coherencia entre motivo_tipo y item_plan
        motivo_tipo = data.get('motivo_tipo', getattr(self.instance, 'motivo_tipo', None))
        item_plan = data.get('item_plan', getattr(self.instance, 'item_plan', None))
        
        if motivo_tipo == 'PLAN':
            if not item_plan:
                raise serializers.ValidationError({
                    'item_plan': 'Si el motivo es "Tratamiento de mi Plan", debe seleccionar un ítem del plan.'
                })
            
            # Verificar que el ítem no esté completado
            if item_plan.completado:
                raise serializers.ValidationError({
                    'item_plan': f'El tratamiento "{item_plan.servicio.nombre}" ya ha sido completado.'
                })
            
            # Verificar que el plan esté ACEPTADO
            if item_plan.plan.estado != 'ACEPTADO':
                raise serializers.ValidationError({
                    'item_plan': 'Solo puede agendar tratamientos de planes aceptados.'
                })
        else:
            # Si no es PLAN, no debe tener item_plan
            if item_plan:
                raise serializers.ValidationError({
                    'item_plan': 'Solo las citas de tipo "Tratamiento de mi Plan" pueden vincularse a un ítem del plan.'
                })
        
        return data


class CitaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar citas (sin todos los detalles).
    """
    paciente_nombre = serializers.CharField(
        source='paciente.usuario.nombre',
        read_only=True
    )
    paciente_email = serializers.EmailField(
        source='paciente.usuario.email',
        read_only=True
    )
    odontologo_nombre = serializers.CharField(
        source='odontologo.usuario.nombre',
        read_only=True
    )
    motivo_tipo_display = serializers.CharField(
        source='get_motivo_tipo_display',
        read_only=True
    )
    precio_display = serializers.CharField(read_only=True)
    es_cita_plan = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id',
            'paciente',  # ID del paciente
            'paciente_nombre',
            'paciente_email',
            'odontologo',  # ID del odontólogo
            'odontologo_nombre',
            'fecha_hora',
            'estado',
            'motivo_tipo',
            'motivo_tipo_display',
            'motivo',
            'observaciones',
            'precio_display',
            'es_cita_plan'
        ]
