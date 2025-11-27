from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.db import connection
from django.utils import timezone
from datetime import datetime
import subprocess
import json
import io
import logging

from .models import BackupRecord, BackupConfiguration
from .serializers import BackupRecordSerializer, BackupConfigurationSerializer
from .supabase_storage import upload_backup_to_supabase, download_backup_from_supabase

logger = logging.getLogger(__name__)


class BackupConfigurationView(APIView):
    """
    Vista para obtener y actualizar la configuración de backups automáticos.
    
    GET /api/backups/config/ - Obtener configuración actual
    PATCH /api/backups/config/ - Actualizar configuración
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener configuración actual (crea una por defecto si no existe)."""
        config, created = BackupConfiguration.objects.get_or_create(
            id=1,  # Solo una configuración por tenant
            defaults={
                'backup_schedule': 'daily',
                'backup_time': '02:00:00',
                'retention_days': 30,
                'is_active': True
            }
        )
        
        serializer = BackupConfigurationSerializer(config)
        return Response(serializer.data)
    
    def patch(self, request):
        """Actualizar configuración (solo ADMIN)."""
        if request.user.tipo_usuario != 'ADMIN':
            return Response(
                {'error': 'Solo los administradores pueden modificar la configuración'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        config, created = BackupConfiguration.objects.get_or_create(id=1)
        
        serializer = BackupConfigurationSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            logger.info(f"✅ Configuración de backups actualizada por {request.user.email}")
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateBackupView(APIView):
    """
    Vista para crear un backup manual del schema actual.
    
    POST /api/backups/create/?download=true
    
    Proceso:
    1. Intenta crear backup con pg_dump (SQL)
    2. Si falla, usa dumpdata (JSON)
    3. Sube el archivo a Supabase Storage
    4. Registra en BackupRecord
    5. Opcionalmente devuelve el archivo para descarga
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Verificar que el usuario sea ADMIN
        if request.user.tipo_usuario != 'ADMIN':
            return Response(
                {'error': 'Solo los administradores pueden crear backups'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        schema_name = connection.schema_name
        
        if schema_name == 'public':
            return Response(
                {'error': 'No se pueden crear backups del schema public'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar dumpdata (JSON) directamente - más compatible con Render
            backup_data_bytes, file_extension = self._create_dumpdata_bytes()
            backup_format = 'json'
            logger.info(f"Backup JSON creado para {schema_name}")
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            file_name = f"backup-{backup_format}-{schema_name}-{timestamp}.{file_extension}"
            file_path_in_bucket = f"{schema_name}/{file_name}"
            
            # Subir a Supabase
            upload_result = upload_backup_to_supabase(backup_data_bytes, file_path_in_bucket)
            
            # Registrar en BD
            backup_record = BackupRecord.objects.create(
                file_name=file_name,
                file_path=upload_result['path'],
                file_size=len(backup_data_bytes),
                backup_type='manual',
                created_by=request.user
            )
            
            logger.info(
                f"✅ Backup manual creado por {request.user.email} (ID: {backup_record.id})"
            )
            
            # Si se solicitó descarga, devolver el archivo
            if request.query_params.get('download', '').lower() == 'true':
                response = HttpResponse(
                    backup_data_bytes,
                    content_type='application/octet-stream'
                )
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
            
            # Devolver info del backup
            serializer = BackupRecordSerializer(backup_record)
            return Response({
                'message': 'Backup creado y subido a Supabase exitosamente',
                'backup_info': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"❌ Error al crear backup: {str(e)}")
            return Response(
                {'error': f'Error al crear backup: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _create_pg_dump_bytes(self, schema_name):
        """Crea backup usando pg_dump."""
        db_settings = settings.DATABASES['default']
        
        # Comando pg_dump
        command = [
            'pg_dump',
            '--dbname', db_settings['NAME'],
            '--host', db_settings['HOST'],
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--schema', schema_name,
            '--format', 'p',  # plain text
            '--inserts',      # usar INSERT statements
            '--no-owner',
            '--no-privileges'
        ]
        
        # Configurar password como variable de entorno
        env = {'PGPASSWORD': db_settings['PASSWORD']}
        
        # Ejecutar comando
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                stderr=stderr
            )
        
        return stdout, 'sql'
    
    def _create_dumpdata_bytes(self):
        """Crea backup usando dumpdata (fallback)."""
        from django.core.management import call_command
        
        # Apps de tenant que queremos respaldar
        tenant_apps = [
            'usuarios',
            'inventario',
            'tratamientos',
            'agenda',
            'historial_clinico',
            'facturacion',
            'reportes'
        ]
        
        output = io.StringIO()
        call_command(
            'dumpdata',
            *tenant_apps,
            indent=2,
            stdout=output
        )
        
        json_data = output.getvalue()
        return json_data.encode('utf-8'), 'json'


class BackupHistoryListView(ListAPIView):
    """
    Vista para listar el historial de backups del schema actual.
    
    GET /api/backups/history/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = BackupRecordSerializer
    
    def get_queryset(self):
        # Solo mostrar backups del schema actual
        return BackupRecord.objects.all().order_by('-created_at')


class DownloadBackupView(APIView):
    """
    Vista para descargar un backup específico desde Supabase.
    
    GET /api/backups/history/{id}/download/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            backup_record = BackupRecord.objects.get(pk=pk)
        except BackupRecord.DoesNotExist:
            return Response(
                {'error': 'Backup no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Descargar desde Supabase
            file_bytes = download_backup_from_supabase(backup_record.file_path)
            
            # Determinar content type
            content_type = (
                'application/sql' if backup_record.file_name.endswith('.sql')
                else 'application/json'
            )
            
            # Devolver archivo
            response = HttpResponse(file_bytes, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{backup_record.file_name}"'
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Error al descargar backup {pk}: {str(e)}")
            return Response(
                {'error': f'Error al descargar backup: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteBackupView(APIView):
    """
    Vista para eliminar un backup (solo ADMIN).
    
    DELETE /api/backups/history/{id}/
    """
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        if request.user.tipo_usuario != 'ADMIN':
            return Response(
                {'error': 'Solo los administradores pueden eliminar backups'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            backup_record = BackupRecord.objects.get(pk=pk)
        except BackupRecord.DoesNotExist:
            return Response(
                {'error': 'Backup no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Eliminar de Supabase
            from .supabase_storage import delete_backup_from_supabase
            delete_backup_from_supabase(backup_record.file_path)
            
            # Eliminar registro de BD
            backup_record.delete()
            
            logger.info(f"✅ Backup {pk} eliminado por {request.user.email}")
            
            return Response(
                {'message': 'Backup eliminado exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            logger.error(f"❌ Error al eliminar backup {pk}: {str(e)}")
            return Response(
                {'error': f'Error al eliminar backup: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RestoreBackupView(APIView):
    """
    Vista para restaurar un backup en el schema actual.
    
    POST /api/backups/history/{id}/restore/
    
    ADVERTENCIA: Esta operación es DESTRUCTIVA y eliminará todos los datos actuales.
    Solo ADMIN puede ejecutarla.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        # Solo ADMIN puede restaurar
        if request.user.tipo_usuario != 'ADMIN':
            return Response(
                {'error': 'Solo los administradores pueden restaurar backups'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        schema_name = connection.schema_name
        
        if schema_name == 'public':
            return Response(
                {'error': 'No se puede restaurar en el schema public'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            backup_record = BackupRecord.objects.get(pk=pk)
        except BackupRecord.DoesNotExist:
            return Response(
                {'error': 'Backup no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar confirmación explícita
        confirm = request.data.get('confirm', False)
        if not confirm:
            return Response(
                {
                    'error': 'Debe confirmar la restauración',
                    'message': 'Esta operación eliminará todos los datos actuales. Envíe "confirm": true para confirmar.',
                    'backup_info': {
                        'file_name': backup_record.file_name,
                        'created_at': backup_record.created_at,
                        'created_by': backup_record.created_by.email if backup_record.created_by else 'Sistema'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Descargar backup desde Supabase
            logger.info(f"📥 Descargando backup {pk} desde Supabase...")
            file_bytes = download_backup_from_supabase(backup_record.file_path)
            
            # Determinar tipo de backup y restaurar
            if backup_record.file_name.endswith('.sql'):
                self._restore_from_sql(file_bytes, schema_name)
            elif backup_record.file_name.endswith('.json'):
                self._restore_from_json(file_bytes)
            else:
                raise ValueError(f"Formato de backup no soportado: {backup_record.file_name}")
            
            logger.info(
                f"✅ Backup {pk} restaurado exitosamente en {schema_name} por {request.user.email}"
            )
            
            return Response({
                'message': 'Backup restaurado exitosamente',
                'backup_info': {
                    'file_name': backup_record.file_name,
                    'created_at': backup_record.created_at,
                    'restored_by': request.user.email,
                    'restored_at': timezone.now()
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"❌ Error al restaurar backup {pk}: {str(e)}")
            return Response(
                {'error': f'Error al restaurar backup: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _restore_from_sql(self, file_bytes, schema_name):
        """Restaura desde un archivo SQL usando psql."""
        db_settings = settings.DATABASES['default']
        
        # Guardar SQL temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.sql', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # Limpiar schema actual (excepto la tabla de backups)
            with connection.cursor() as cursor:
                # Obtener todas las tablas del schema
                cursor.execute(f"""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = '{schema_name}'
                    AND tablename NOT IN ('backups_backuprecord', 'backups_backupconfiguration')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # Eliminar datos de cada tabla
                for table in tables:
                    cursor.execute(f'TRUNCATE TABLE "{schema_name}"."{table}" CASCADE')
            
            # Restaurar usando psql
            command = [
                'psql',
                '--dbname', db_settings['NAME'],
                '--host', db_settings['HOST'],
                '--port', str(db_settings['PORT']),
                '--username', db_settings['USER'],
                '--file', tmp_file_path,
                '--set', f'search_path={schema_name},public'
            ]
            
            env = {'PGPASSWORD': db_settings['PASSWORD']}
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    command,
                    stderr=stderr
                )
        
        finally:
            # Eliminar archivo temporal
            import os
            os.unlink(tmp_file_path)
    
    def _restore_from_json(self, file_bytes):
        """Restaura desde un archivo JSON usando loaddata."""
        from django.core.management import call_command
        
        # Guardar JSON temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # Limpiar datos actuales (excepto backups)
            tenant_apps = [
                'usuarios', 'inventario', 'tratamientos',
                'agenda', 'historial_clinico', 'facturacion', 'reportes'
            ]
            
            from django.apps import apps
            for app_label in tenant_apps:
                try:
                    app_config = apps.get_app_config(app_label)
                    for model in app_config.get_models():
                        if model._meta.db_table not in ['backups_backuprecord', 'backups_backupconfiguration']:
                            model.objects.all().delete()
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo limpiar {app_label}: {str(e)}")
            
            # Cargar datos desde JSON
            call_command('loaddata', tmp_file_path)
        
        finally:
            # Eliminar archivo temporal
            import os
            os.unlink(tmp_file_path)
