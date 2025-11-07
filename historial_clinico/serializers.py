# historial_clinico/serializers.py

from rest_framework import serializers
from .models import HistorialClinico, EpisodioAtencion, Odontograma, DocumentoClinico

class DocumentoClinicoSerializer(serializers.ModelSerializer):
    """Serializer para documentos clínicos."""
    
    class Meta:
        model = DocumentoClinico
        fields = ('id', 'descripcion', 'archivo', 'tipo_documento', 'creado')
        read_only_fields = ('id', 'creado')


class OdontogramaSerializer(serializers.ModelSerializer):
    """Serializer para odontogramas."""
    
    class Meta:
        model = Odontograma
        fields = ('id', 'fecha_snapshot', 'estado_piezas', 'notas')
        read_only_fields = ('id', 'fecha_snapshot')


class EpisodioAtencionSerializer(serializers.ModelSerializer):
    """Serializer para episodios de atención."""
    
    odontologo_nombre = serializers.CharField(source='odontologo.usuario.full_name', read_only=True)
    odontologo_especialidad = serializers.CharField(source='odontologo.especialidad.nombre', read_only=True)
    item_plan_descripcion = serializers.CharField(source='item_plan_tratamiento.servicio.nombre', read_only=True)
    
    class Meta:
        model = EpisodioAtencion
        fields = (
            'id', 'odontologo', 'odontologo_nombre', 'odontologo_especialidad',
            'item_plan_tratamiento', 'item_plan_descripcion',
            'fecha_atencion', 'motivo_consulta', 'diagnostico', 
            'descripcion_procedimiento', 'notas_privadas'
        )
        read_only_fields = ('id', 'fecha_atencion')


class HistorialClinicoSerializer(serializers.ModelSerializer):
    """
    Serializer completo que anida los episodios, odontogramas y documentos.
    """
    paciente_nombre = serializers.CharField(source='paciente.usuario.full_name', read_only=True)
    paciente_email = serializers.EmailField(source='paciente.usuario.email', read_only=True)
    paciente_ci = serializers.CharField(source='paciente.usuario.ci', read_only=True)
    paciente_telefono = serializers.CharField(source='paciente.usuario.telefono', read_only=True)
    paciente_fecha_nacimiento = serializers.DateField(source='paciente.fecha_de_nacimiento', read_only=True)
    paciente_direccion = serializers.CharField(source='paciente.direccion', read_only=True)
    
    # Anidamos los inlines para que la API devuelva todo junto
    episodios = EpisodioAtencionSerializer(many=True, read_only=True)
    odontogramas = OdontogramaSerializer(many=True, read_only=True)
    documentos = DocumentoClinicoSerializer(many=True, read_only=True)
    
    # Campos calculados
    total_episodios = serializers.SerializerMethodField()
    total_odontogramas = serializers.SerializerMethodField()
    total_documentos = serializers.SerializerMethodField()
    ultimo_episodio = serializers.SerializerMethodField()

    class Meta:
        model = HistorialClinico
        fields = (
            # Datos del paciente
            'paciente', 'paciente_nombre', 'paciente_email', 'paciente_ci', 
            'paciente_telefono', 'paciente_fecha_nacimiento', 'paciente_direccion',
            
            # Antecedentes médicos
            'antecedentes_medicos', 'alergias', 'medicamentos_actuales',
            
            # Metadatos
            'creado', 'actualizado',
            
            # Datos anidados
            'episodios', 'odontogramas', 'documentos',
            
            # Campos calculados
            'total_episodios', 'total_odontogramas', 'total_documentos', 'ultimo_episodio'
        )
        read_only_fields = ('creado', 'actualizado')
    
    def get_total_episodios(self, obj):
        """Número total de episodios de atención."""
        return obj.episodios.count()
    
    def get_total_odontogramas(self, obj):
        """Número total de odontogramas."""
        return obj.odontogramas.count()
    
    def get_total_documentos(self, obj):
        """Número total de documentos."""
        return obj.documentos.count()
    
    def get_ultimo_episodio(self, obj):
        """Fecha del último episodio de atención."""
        ultimo = obj.episodios.first()  # Ya están ordenados por -fecha_atencion
        return ultimo.fecha_atencion if ultimo else None


# --- Serializers de solo lectura para listas ---

class HistorialClinicoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de historiales."""
    
    paciente_nombre = serializers.CharField(source='paciente.usuario.full_name', read_only=True)
    paciente_email = serializers.EmailField(source='paciente.usuario.email', read_only=True)
    total_episodios = serializers.SerializerMethodField()
    ultimo_episodio = serializers.SerializerMethodField()
    
    class Meta:
        model = HistorialClinico
        fields = (
            'paciente', 'paciente_nombre', 'paciente_email',
            'alergias', 'medicamentos_actuales', 'actualizado',
            'total_episodios', 'ultimo_episodio'
        )
    
    def get_total_episodios(self, obj):
        return obj.episodios.count()
    
    def get_ultimo_episodio(self, obj):
        ultimo = obj.episodios.first()
        return ultimo.fecha_atencion if ultimo else None


class EpisodioAtencionCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear episodios."""
    
    class Meta:
        model = EpisodioAtencion
        fields = (
            'historial_clinico', 'odontologo', 'item_plan_tratamiento',
            'motivo_consulta', 'diagnostico', 'descripcion_procedimiento', 'notas_privadas'
        )
    
    def validate(self, data):
        """Validaciones personalizadas."""
        # Si se especifica un item_plan_tratamiento, debe pertenecer al mismo paciente
        if data.get('item_plan_tratamiento'):
            item_plan = data['item_plan_tratamiento']
            historial_paciente = data['historial_clinico'].paciente
            plan_paciente = item_plan.plan_tratamiento.paciente
            
            if historial_paciente != plan_paciente:
                raise serializers.ValidationError(
                    "El ítem del plan de tratamiento debe pertenecer al mismo paciente del historial."
                )
        
        return data