"""
Comando para crear backups automáticos del tenant clinica_demo.

Uso:
    python manage.py crear_backup_automatico

Este comando se puede programar en Render como Cron Job.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import datetime
import io
import logging

from tenants.models import Clinica
from backups.models import BackupRecord
from backups.supabase_storage import upload_backup_to_supabase

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Crea un backup automático del tenant clinica_demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='clinica_demo',
            help='Schema del tenant a respaldar (default: clinica_demo)'
        )

    def handle(self, *args, **options):
        tenant_schema = options['tenant']
        
        try:
            # Obtener el tenant
            tenant = Clinica.objects.get(schema_name=tenant_schema)
            
            # Cambiar al schema del tenant
            connection.set_tenant(tenant)
            
            self.stdout.write(f"📦 Creando backup automático para {tenant_schema}...")
            
            # Crear backup usando dumpdata
            backup_data_bytes = self._create_dumpdata_bytes()
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            file_name = f"backup-auto-json-{tenant_schema}-{timestamp}.json"
            file_path_in_bucket = f"{tenant_schema}/{file_name}"
            
            # Subir a Supabase
            self.stdout.write(f"☁️  Subiendo a Supabase...")
            upload_result = upload_backup_to_supabase(backup_data_bytes, file_path_in_bucket)
            
            # Registrar en BD
            backup_record = BackupRecord.objects.create(
                file_name=file_name,
                file_path=upload_result['path'],
                file_size=len(backup_data_bytes),
                backup_type='automatico',
                created_by=None  # Backup automático, sin usuario
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Backup automático creado exitosamente\n"
                    f"   ID: {backup_record.id}\n"
                    f"   Archivo: {file_name}\n"
                    f"   Tamaño: {len(backup_data_bytes) / 1024:.2f} KB\n"
                    f"   Fecha: {backup_record.created_at}"
                )
            )
            
            logger.info(f"✅ Backup automático creado: {file_name} ({backup_record.id})")
            
        except Clinica.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Tenant '{tenant_schema}' no encontrado")
            )
            logger.error(f"Tenant {tenant_schema} no encontrado")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error al crear backup: {str(e)}")
            )
            logger.error(f"Error al crear backup automático: {str(e)}")
            raise

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
            'reportes',
            'backups'
        ]
        
        output = io.StringIO()
        call_command(
            'dumpdata',
            *tenant_apps,
            indent=2,
            stdout=output
        )
        
        json_data = output.getvalue()
        return json_data.encode('utf-8')
