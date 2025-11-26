"""
Módulo para interactuar con Supabase Storage.
Maneja la subida y descarga de backups a/desde Supabase.
"""

from supabase import create_client, Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

BUCKET_NAME = 'backups'


def get_supabase_client() -> Client:
    """Crea y retorna un cliente de Supabase."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL y SUPABASE_KEY deben estar configurados en settings"
        )
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_backup_to_supabase(file_content_bytes: bytes, file_path_in_bucket: str) -> dict:
    """
    Sube un archivo de backup a Supabase Storage.
    
    Args:
        file_content_bytes: Contenido del backup en bytes
        file_path_in_bucket: Ruta dentro del bucket (ej: 'clinica1/backup-sql-2025-11-26.sql')
    
    Returns:
        dict con 'success', 'path' y 'url'
    """
    try:
        supabase = get_supabase_client()
        
        # Determinar content-type según extensión
        content_type = 'application/sql' if file_path_in_bucket.endswith('.sql') else 'application/json'
        
        # Subir archivo
        supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path_in_bucket,
            file=file_content_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"  # Sobrescribir si ya existe
            }
        )
        
        # Obtener URL pública (aunque el bucket sea privado, necesitamos la ruta)
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path_in_bucket)
        
        logger.info(f"✅ Backup subido exitosamente a Supabase: {file_path_in_bucket}")
        
        return {
            'success': True,
            'path': file_path_in_bucket,
            'url': public_url
        }
    
    except Exception as e:
        logger.error(f"❌ Error al subir backup a Supabase: {str(e)}")
        raise Exception(f"Error al subir a Supabase: {str(e)}")


def download_backup_from_supabase(file_path_in_bucket: str) -> bytes:
    """
    Descarga un archivo de backup desde Supabase Storage.
    
    Args:
        file_path_in_bucket: Ruta del archivo en el bucket
    
    Returns:
        bytes: Contenido del archivo
    """
    try:
        supabase = get_supabase_client()
        
        # Descargar archivo
        response_bytes = supabase.storage.from_(BUCKET_NAME).download(file_path_in_bucket)
        
        logger.info(f"✅ Backup descargado exitosamente: {file_path_in_bucket}")
        
        return response_bytes
    
    except Exception as e:
        logger.error(f"❌ Error al descargar backup: {str(e)}")
        raise Exception(f"Error al descargar desde Supabase: {str(e)}")


def delete_backup_from_supabase(file_path_in_bucket: str) -> dict:
    """
    Elimina un archivo de backup de Supabase Storage.
    
    Args:
        file_path_in_bucket: Ruta del archivo en el bucket
    
    Returns:
        dict con 'success'
    """
    try:
        supabase = get_supabase_client()
        
        # Eliminar archivo
        supabase.storage.from_(BUCKET_NAME).remove([file_path_in_bucket])
        
        logger.info(f"✅ Backup eliminado exitosamente: {file_path_in_bucket}")
        
        return {'success': True}
    
    except Exception as e:
        logger.error(f"❌ Error al eliminar backup: {str(e)}")
        raise Exception(f"Error al eliminar de Supabase: {str(e)}")
