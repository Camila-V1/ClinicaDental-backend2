from rest_framework import serializers
from .models import BackupRecord, BackupConfiguration


class CreatedBySerializer(serializers.Serializer):
    """Serializer simple para mostrar info del usuario que creó el backup."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nombre = serializers.CharField()


class BackupConfigurationSerializer(serializers.ModelSerializer):
    """Serializer para configuración de backups automáticos."""
    
    updated_by = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupConfiguration
        fields = [
            'id',
            'backup_schedule',
            'backup_time',
            'retention_days',
            'is_active',
            'last_backup_at',
            'updated_at',
            'updated_by'
        ]
        read_only_fields = ['id', 'last_backup_at', 'updated_at', 'updated_by']
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            return {
                'id': obj.updated_by.id,
                'email': obj.updated_by.email,
                'nombre': obj.updated_by.nombre
            }
        return None


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
