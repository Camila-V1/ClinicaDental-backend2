from rest_framework import serializers
from .models import BackupRecord


class CreatedBySerializer(serializers.Serializer):
    """Serializer simple para mostrar info del usuario que creó el backup."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nombre = serializers.CharField()


class BackupRecordSerializer(serializers.ModelSerializer):
    """Serializer para listar registros de backups."""
    
    created_by = serializers.SerializerMethodField()
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = BackupRecord
        fields = [
            'id',
            'file_name',
            'file_path',
            'file_size',
            'file_size_mb',
            'backup_type',
            'created_by',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_created_by(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'email': obj.created_by.email,
                'nombre': obj.created_by.nombre
            }
        return None
