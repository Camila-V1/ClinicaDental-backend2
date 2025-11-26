from rest_framework import serializers
from .models import PlanSuscripcion, SolicitudRegistro, Clinica
import re


class PlanSuscripcionSerializer(serializers.ModelSerializer):
    """Serializer para planes de suscripción."""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = PlanSuscripcion
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'descripcion',
            'precio', 'duracion_dias', 'max_usuarios', 'max_pacientes',
            'activo'
        ]
        read_only_fields = ['id']


class SolicitudRegistroSerializer(serializers.ModelSerializer):
    """Serializer para solicitudes de registro de nuevas clínicas."""
    
    plan_info = PlanSuscripcionSerializer(source='plan_solicitado', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = SolicitudRegistro
        fields = [
            'id', 'nombre_clinica', 'dominio_deseado',
            'nombre_contacto', 'email', 'telefono', 'cargo',
            'direccion', 'ciudad', 'pais',
            'plan_solicitado', 'plan_info',
            'mensaje', 'estado', 'estado_display',
            'motivo_rechazo', 'creada'
        ]
        read_only_fields = ['id', 'estado', 'motivo_rechazo', 'creada']
    
    def validate_dominio_deseado(self, value):
        """Validar que el dominio sea válido y no exista."""
        # Solo permitir letras, números y guiones
        if not re.match(r'^[a-z0-9-]+$', value.lower()):
            raise serializers.ValidationError(
                "El dominio solo puede contener letras minúsculas, números y guiones."
            )
        
        # No permitir que empiece o termine con guión
        if value.startswith('-') or value.endswith('-'):
            raise serializers.ValidationError(
                "El dominio no puede empezar ni terminar con guión."
            )
        
        # Verificar que no exista una clínica con ese dominio
        if Clinica.objects.filter(dominio=value.lower()).exists():
            raise serializers.ValidationError(
                "Este dominio ya está en uso. Por favor, elige otro."
            )
        
        return value.lower()
    
    def validate_email(self, value):
        """Validar que el email no esté ya registrado."""
        if SolicitudRegistro.objects.filter(
            email=value,
            estado__in=['PENDIENTE_PAGO', 'PAGO_PROCESANDO', 'PAGO_EXITOSO', 'COMPLETADA']
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una solicitud activa con este email."
            )
        return value.lower()


class ClinicaPublicSerializer(serializers.ModelSerializer):
    """Serializer público de clínica (información limitada)."""
    
    plan_info = PlanSuscripcionSerializer(source='plan', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Clinica
        fields = [
            'id', 'nombre', 'dominio', 'email_admin',
            'telefono', 'ciudad', 'pais',
            'plan_info', 'estado', 'estado_display',
            'fecha_expiracion', 'dias_restantes', 'esta_activa'
        ]
        read_only_fields = fields


class ClinicaAdminSerializer(serializers.ModelSerializer):
    """Serializer completo de clínica (para administradores)."""
    
    plan_info = PlanSuscripcionSerializer(source='plan', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Clinica
        fields = '__all__'
        read_only_fields = ['schema_name', 'creado', 'actualizado']
