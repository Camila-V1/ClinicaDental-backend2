from django.urls import path
from .views import (
    BackupConfigurationView,
    CreateBackupView,
    BackupHistoryListView,
    DownloadBackupView,
    DeleteBackupView,
    RestoreBackupView
)

urlpatterns = [
    path('config/', BackupConfigurationView.as_view(), name='backup_config'),
    path('create/', CreateBackupView.as_view(), name='create_backup'),
    path('history/', BackupHistoryListView.as_view(), name='backup_history'),
    path('history/<int:pk>/download/', DownloadBackupView.as_view(), name='download_backup'),
    path('history/<int:pk>/restore/', RestoreBackupView.as_view(), name='restore_backup'),
    path('history/<int:pk>/', DeleteBackupView.as_view(), name='delete_backup'),
]
