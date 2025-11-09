# usuarios/serializers.py

from rest_framework import serializers
from .models import Usuario, PerfilPaciente, PerfilOdontologo


class PerfilPacienteSerializer(serializers.ModelSerializer):
    """Serializer para el perfil extendido de Paciente."""
    class Meta:
        model = PerfilPaciente
        fields = ['fecha_de_nacimiento', 'direccion']


class PerfilOdontologoSerializer(serializers.ModelSerializer):
    """Serializer para el perfil extendido de Odontólogo."""
    class Meta:
        model = PerfilOdontologo
        fields = ['especialidad', 'cedulaProfesional', 'experienciaProfesional']


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para LEER la información de un usuario.
    Incluye perfiles anidados según el tipo de usuario.
    """
    # Incluimos los perfiles de forma anidada (solo lectura)
    perfil_paciente = PerfilPacienteSerializer(read_only=True)
    perfil_odontologo = PerfilOdontologoSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre', 'apellido', 'ci', 'sexo', 'telefono', 
            'tipo_usuario', 'is_active', 'date_joined',
            'perfil_paciente', 'perfil_odontologo'
        ]
        read_only_fields = ['id', 'date_joined']


class PacienteListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar pacientes.
    Usado en selects y dropdowns del frontend.
    """
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 'email', 'telefono', 'ci']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR (registrar) un nuevo usuario PACIENTE (CU01).
    El registro público solo permite crear pacientes.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar contraseña')
    
    # Campos del perfil de paciente
    fecha_de_nacimiento = serializers.DateField(required=True, write_only=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'email', 'password', 'password2', 'nombre', 'apellido', 
            'ci', 'sexo', 'telefono',
            'fecha_de_nacimiento', 'direccion'
        ]

    def validate(self, attrs):
        """Validar que las contraseñas coincidan."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return attrs

    def create(self, validated_data):
        """Crear el Usuario y su PerfilPaciente asociado."""
        # Removemos password2 ya que no es parte del modelo
        validated_data.pop('password2')
        
        # Extraemos los datos del perfil
        fecha_nacimiento = validated_data.pop('fecha_de_nacimiento')
        direccion = validated_data.pop('direccion', '')

        # Creamos el Usuario (tipo PACIENTE por defecto)
        usuario = Usuario.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            ci=validated_data.get('ci'),
            sexo=validated_data.get('sexo'),
            telefono=validated_data.get('telefono'),
            password=validated_data['password'],
            tipo_usuario='PACIENTE'  # El registro público es solo para pacientes
        )

        # Creamos el PerfilPaciente asociado
        PerfilPaciente.objects.create(
            usuario=usuario,
            fecha_de_nacimiento=fecha_nacimiento,
            direccion=direccion
        )
        
        return usuario
