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
        source='paciente.usuario.get_full_name',
        read_only=True
    )
    paciente_email = serializers.EmailField(
        source='paciente.usuario.email',
        read_only=True
    )
    odontologo_nombre = serializers.CharField(
        source='odontologo.usuario.get_full_name',
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
            'motivo',
            'observaciones',
            'estado',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']
    
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
        
        return data


class CitaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar citas (sin todos los detalles).
    """
    paciente_nombre = serializers.CharField(
        source='paciente.usuario.get_full_name',
        read_only=True
    )
    odontologo_nombre = serializers.CharField(
        source='odontologo.usuario.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Cita
        fields = [
            'id',
            'paciente_nombre',
            'odontologo_nombre',
            'fecha_hora',
            'estado',
            'motivo'
        ]
