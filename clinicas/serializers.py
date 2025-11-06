from rest_framework import serializers
from .models import Clinica


class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = ['id', 'nombre', 'dominio', 'activo', 'creado']
        read_only_fields = ['id', 'creado']
