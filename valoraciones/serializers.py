from rest_framework import serializers
from .models import Valoracion
from usuarios.serializers import UsuarioSerializer
from agenda.serializers import CitaSerializer


class ValoracionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear valoraciones"""
    
    class Meta:
        model = Valoracion
        fields = [
            'cita',
            'calificacion',
            'comentario',
            'puntualidad',
            'trato',
            'limpieza'
        ]
    
    def validate_cita(self, value):
        """Validar que la cita esté completada y no tenga ya una valoración"""
        if value.estado != 'COMPLETADA':
            raise serializers.ValidationError(
                "Solo se pueden valorar citas completadas"
            )
        
        if hasattr(value, 'valoracion'):
            raise serializers.ValidationError(
                "Esta cita ya tiene una valoración"
            )
        
        return value
    
    def create(self, validated_data):
        # Extraer la cita y el usuario del contexto
        cita = validated_data['cita']
        paciente = self.context['request'].user
        
        # Validar que el usuario sea el paciente de la cita
        if cita.paciente != paciente:
            raise serializers.ValidationError(
                "Solo el paciente de la cita puede valorarla"
            )
        
        # Crear la valoración
        valoracion = Valoracion.objects.create(
            paciente=paciente,
            odontologo=cita.odontologo,
            **validated_data
        )
        
        return valoracion


class ValoracionSerializer(serializers.ModelSerializer):
    """Serializer completo para listar valoraciones"""
    
    paciente = UsuarioSerializer(read_only=True)
    odontologo = UsuarioSerializer(read_only=True)
    cita = CitaSerializer(read_only=True)
    calificacion_promedio_aspectos = serializers.ReadOnlyField()
    
    class Meta:
        model = Valoracion
        fields = [
            'id',
            'cita',
            'paciente',
            'odontologo',
            'calificacion',
            'comentario',
            'puntualidad',
            'trato',
            'limpieza',
            'calificacion_promedio_aspectos',
            'created_at',
            'updated_at',
            'notificacion_enviada',
            'notificacion_enviada_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'notificacion_enviada',
            'notificacion_enviada_at'
        ]


class ValoracionResumenSerializer(serializers.ModelSerializer):
    """Serializer resumido para estadísticas"""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    odontologo_nombre = serializers.CharField(source='odontologo.nombre_completo', read_only=True)
    fecha_cita = serializers.DateTimeField(source='cita.fecha_hora', read_only=True)
    
    class Meta:
        model = Valoracion
        fields = [
            'id',
            'paciente_nombre',
            'odontologo_nombre',
            'calificacion',
            'comentario',
            'fecha_cita',
            'created_at'
        ]


class EstadisticasOdontologoSerializer(serializers.Serializer):
    """Serializer para estadísticas de valoraciones de un odontólogo"""
    
    odontologo_id = serializers.IntegerField()
    odontologo_nombre = serializers.CharField()
    total_valoraciones = serializers.IntegerField()
    calificacion_promedio = serializers.DecimalField(max_digits=3, decimal_places=2)
    puntualidad_promedio = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    trato_promedio = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    limpieza_promedio = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    valoraciones_por_estrella = serializers.DictField()
