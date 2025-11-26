from django.contrib import admin
from .models import BackupRecord


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'backup_type', 'file_size_mb', 'created_by', 'created_at']
    list_filter = ['backup_type', 'created_at']
    search_fields = ['file_name', 'file_path']
    readonly_fields = ['file_name', 'file_path', 'file_size', 'backup_type', 'created_by', 'created_at']
    
    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = "Tamaño"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
