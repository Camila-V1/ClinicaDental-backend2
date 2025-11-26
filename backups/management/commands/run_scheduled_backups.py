"""
Comando para ejecutar backups programados automáticamente.

Uso:
    python manage.py run_scheduled_backups

Este comando debe ejecutarse periódicamente (ej: cada 1 hora con cron).
Revisa todas las clínicas y ejecuta backups según su configuración:

- daily: Una vez al día a la hora especificada
- every_12h/every_6h: Cada X horas desde la hora base
- weekly: Un día específico de la semana a una hora
- monthly: Un día específico del mes a una hora
- scheduled: Fecha y hora exacta (una sola vez)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from django_tenants.utils import schema_context
from datetime import datetime, timedelta
import logging
import subprocess
import io

from tenants.models import Clinica
from backups.models import BackupRecord
from backups.supabase_storage import upload_backup_to_supabase

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ejecuta backups automáticos programados para todas las clínicas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⏳ Verificando backups programados...'))
        
        # Obtener todas las clínicas (excepto public)
        clinicas = Clinica.objects.exclude(schema_name='public').filter(activo=True)
        
        now = timezone.now()
        backups_ejecutados = 0
        
        for clinica in clinicas:
            try:
                if self._should_run_backup(clinica, now):
                    self.stdout.write(
                        self.style.SUCCESS(f'📦 Iniciando backup para: {clinica.nombre}...')
                    )
                    self._perform_backup(clinica)
                    backups_ejecutados += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error en backup de {clinica.nombre}: {str(e)}')
                )
                logger.error(f"[AutoBackup] Error crítico en {clinica.nombre}: {e}", exc_info=True)
        
        if backups_ejecutados > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {backups_ejecutados} backup(s) ejecutado(s) exitosamente.')
            )
        else:
            self.stdout.write('ℹ️  No hay backups programados en este momento.')
        
        self.stdout.write(self.style.SUCCESS('✅ Verificación de backups finalizada.'))

    def _should_run_backup(self, clinica, now):
        """Determina si debe ejecutarse un backup según la configuración de la clínica."""
        schedule = clinica.backup_schedule
        
        if schedule == 'disabled':
            return False
        
        # PROGRAMADO POR FECHA ESPECÍFICA
        if schedule == 'scheduled':
            if clinica.next_scheduled_backup and clinica.next_scheduled_backup <= now:
                return True
            return False
        
        # DIARIO: Una vez al día a la hora especificada
        if schedule == 'daily':
            return self._should_run_daily(clinica, now)
        
        # CADA X HORAS
        if schedule in ['every_12h', 'every_6h']:
            return self._should_run_interval(clinica, now)
        
        # SEMANAL: Día específico de la semana
        if schedule == 'weekly':
            return self._should_run_weekly(clinica, now)
        
        # MENSUAL: Día específico del mes
        if schedule == 'monthly':
            return self._should_run_monthly(clinica, now)
        
        return False

    def _should_run_daily(self, clinica, now):
        """Backup diario a una hora específica."""
        if not clinica.backup_time:
            # Si no hay hora configurada, usar 2:00 AM por defecto
            target_time = datetime.strptime('02:00', '%H:%M').time()
        else:
            target_time = clinica.backup_time
        
        # Verificar si ya se ejecutó hoy
        if clinica.last_backup_at:
            if clinica.last_backup_at.date() == now.date():
                return False  # Ya se ejecutó hoy
        
        # Verificar si es la hora correcta (con margen de 1 hora)
        current_time = now.time()
        target_hour = target_time.hour
        current_hour = current_time.hour
        
        # Ejecutar si la hora actual es >= hora objetivo y no se ha ejecutado hoy
        if current_hour >= target_hour:
            return True
        
        return False

    def _should_run_interval(self, clinica, now):
        """Backup cada X horas desde una hora base."""
        interval_hours = 12 if clinica.backup_schedule == 'every_12h' else 6
        
        if not clinica.backup_time:
            # Hora base por defecto
            base_hour = 2  # 2:00 AM
        else:
            base_hour = clinica.backup_time.hour
        
        # Si no hay último backup, ejecutar si la hora actual coincide con un múltiplo
        if not clinica.last_backup_at:
            current_hour = now.hour
            # Verificar si la hora actual es un múltiplo desde la hora base
            if (current_hour - base_hour) % interval_hours == 0:
                return True
            return False
        
        # Si ya hay un backup, verificar si pasaron X horas
        time_since_last = now - clinica.last_backup_at
        if time_since_last >= timedelta(hours=interval_hours):
            return True
        
        return False

    def _should_run_weekly(self, clinica, now):
        """Backup semanal en un día específico."""
        if clinica.backup_weekday is None:
            target_weekday = 6  # Domingo por defecto
        else:
            target_weekday = clinica.backup_weekday
        
        if not clinica.backup_time:
            target_time = datetime.strptime('02:00', '%H:%M').time()
        else:
            target_time = clinica.backup_time
        
        # Verificar si es el día correcto
        if now.weekday() != target_weekday:
            return False
        
        # Verificar si ya se ejecutó hoy
        if clinica.last_backup_at and clinica.last_backup_at.date() == now.date():
            return False
        
        # Verificar si es la hora correcta
        if now.time().hour >= target_time.hour:
            return True
        
        return False

    def _should_run_monthly(self, clinica, now):
        """Backup mensual en un día específico del mes."""
        if not clinica.backup_day_of_month:
            target_day = 1  # Día 1 por defecto
        else:
            target_day = clinica.backup_day_of_month
        
        if not clinica.backup_time:
            target_time = datetime.strptime('02:00', '%H:%M').time()
        else:
            target_time = clinica.backup_time
        
        # Verificar si es el día correcto del mes
        if now.day != target_day:
            return False
        
        # Verificar si ya se ejecutó este mes
        if clinica.last_backup_at:
            if (clinica.last_backup_at.year == now.year and
                clinica.last_backup_at.month == now.month):
                return False
        
        # Verificar si es la hora correcta
        if now.time().hour >= target_time.hour:
            return True
        
        return False

    def _perform_backup(self, clinica):
        """Ejecuta el backup para una clínica específica."""
        schema_name = clinica.schema_name
        
        with schema_context(schema_name):
            try:
                # Intentar pg_dump primero
                try:
                    backup_data_bytes, file_extension = self._create_pg_dump_bytes(schema_name)
                    backup_format = 'sql'
                except Exception:
                    # Fallback a dumpdata
                    backup_data_bytes, file_extension = self._create_dumpdata_bytes()
                    backup_format = 'json'
                
                # Generar nombre de archivo
                timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
                file_name = f"auto-{backup_format}-{schema_name}-{timestamp}.{file_extension}"
                file_path_in_bucket = f"{schema_name}/{file_name}"
                
                # Subir a Supabase
                upload_result = upload_backup_to_supabase(backup_data_bytes, file_path_in_bucket)
                
                # Registrar en BD
                BackupRecord.objects.create(
                    file_name=file_name,
                    file_path=upload_result['path'],
                    file_size=len(backup_data_bytes),
                    backup_type='automatic',
                    created_by=None
                )
                
                # Actualizar clínica
                clinica.last_backup_at = timezone.now()
                
                # Si era programado por fecha, desactivar
                if clinica.backup_schedule == 'scheduled':
                    clinica.next_scheduled_backup = None
                    clinica.backup_schedule = 'disabled'
                
                clinica.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'   -> Subido exitosamente a Supabase')
                )
                logger.info(f"✅ Backup automático creado para {clinica.nombre}")
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   -> Error: {str(e)}')
                )
                raise

    def _create_pg_dump_bytes(self, schema_name):
        """Crea backup usando pg_dump."""
        from django.conf import settings
        
        db_settings = settings.DATABASES['default']
        
        command = [
            'pg_dump',
            '--dbname', db_settings['NAME'],
            '--host', db_settings['HOST'],
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--schema', schema_name,
            '--format', 'p',
            '--inserts',
            '--no-owner',
            '--no-privileges'
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
        
        return stdout, 'sql'

    def _create_dumpdata_bytes(self):
        """Crea backup usando dumpdata (fallback)."""
        from django.core.management import call_command
        
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
        call_command('dumpdata', *tenant_apps, indent=2, stdout=output)
        
        json_data = output.getvalue()
        return json_data.encode('utf-8'), 'json'
