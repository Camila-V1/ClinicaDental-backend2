"""
Script para crear y subir backups de prueba a Supabase.

Uso:
    python crear_backups_prueba.py

Este script crea 5 backups de ejemplo con diferentes fechas y tipos,
y los sube a Supabase Storage para demostración.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.db import connection
from django_tenants.utils import schema_context
from datetime import timedelta
from tenants.models import Clinica
from backups.models import BackupRecord
from backups.supabase_storage import upload_backup_to_supabase

def crear_backups_prueba():
    """Crea y sube backups de prueba a Supabase."""
    
    # Obtener la primera clínica activa
    try:
        clinica = Clinica.objects.exclude(schema_name='public').first()
        if not clinica:
            print("❌ No hay clínicas disponibles")
            return
    except Exception as e:
        print(f"❌ Error al obtener clínica: {e}")
        return
    
    schema_name = clinica.schema_name
    print(f"📦 Creando backups de prueba para: {clinica.nombre} (schema: {schema_name})")
    
    # Definir backups de ejemplo
    backups_ejemplo = [
        {
            'nombre': f'backup-sql-{schema_name}-2025-11-20-030000.sql',
            'tipo': 'automatic',
            'dias_atras': 6,
            'contenido': b'''-- Backup Semanal Automático
-- Fecha: 2025-11-20 03:00:00
-- Schema: ''' + schema_name.encode() + b'''

-- Backup de demostración
INSERT INTO usuarios_usuario (id, email, nombre) VALUES (999, 'demo@backup.com', 'Usuario Demo');
'''
        },
        {
            'nombre': f'backup-sql-{schema_name}-2025-11-23-030000.sql',
            'tipo': 'automatic',
            'dias_atras': 3,
            'contenido': b'''-- Backup Diario Automático
-- Fecha: 2025-11-23 03:00:00

-- Backup de demostración
INSERT INTO agenda_cita (id, fecha, hora) VALUES (999, '2025-11-23', '10:00');
'''
        },
        {
            'nombre': f'backup-sql-{schema_name}-2025-11-25-140530.sql',
            'tipo': 'manual',
            'dias_atras': 1,
            'contenido': b'''-- Backup Manual por Administrador
-- Fecha: 2025-11-25 14:05:30

-- Backup de demostración
INSERT INTO tratamientos_presupuesto (id, estado) VALUES (999, 'PENDIENTE');
'''
        },
        {
            'nombre': f'backup-sql-{schema_name}-2025-11-26-030000.sql',
            'tipo': 'automatic',
            'dias_atras': 0,
            'horas_atras': 12,
            'contenido': b'''-- Backup Automático Cada 12 Horas
-- Fecha: 2025-11-26 03:00:00

-- Backup de demostración
INSERT INTO inventario_insumo (id, nombre, stock) VALUES (999, 'Material Demo', 100);
'''
        },
        {
            'nombre': f'backup-json-{schema_name}-2025-11-26-093000.json',
            'tipo': 'automatic',
            'dias_atras': 0,
            'contenido': b'''[
  {
    "model": "usuarios.usuario",
    "pk": 999,
    "fields": {
      "email": "backup@demo.com",
      "nombre": "Backup de Prueba"
    }
  }
]'''
        },
    ]
    
    with schema_context(schema_name):
        backups_creados = 0
        
        for backup_data in backups_ejemplo:
            try:
                # Calcular fecha de creación
                fecha_creacion = timezone.now() - timedelta(days=backup_data.get('dias_atras', 0))
                if 'horas_atras' in backup_data:
                    fecha_creacion -= timedelta(hours=backup_data['horas_atras'])
                
                # Subir a Supabase
                file_path = f"{schema_name}/{backup_data['nombre']}"
                result = upload_backup_to_supabase(
                    backup_data['contenido'],
                    file_path
                )
                
                # Crear registro en la BD
                backup_record = BackupRecord.objects.create(
                    file_name=backup_data['nombre'],
                    file_path=result['path'],
                    file_size=len(backup_data['contenido']),
                    backup_type=backup_data['tipo'],
                    created_by=None,  # None para todos, incluso manuales de ejemplo
                    created_at=fecha_creacion
                )
                
                # Forzar la fecha de creación (auto_now_add lo pone automático)
                BackupRecord.objects.filter(id=backup_record.id).update(created_at=fecha_creacion)
                
                print(f"✅ Subido: {backup_data['nombre']} ({backup_data['tipo']})")
                backups_creados += 1
                
            except Exception as e:
                print(f"❌ Error al subir {backup_data['nombre']}: {e}")
        
        print(f"\n🎉 {backups_creados}/{len(backups_ejemplo)} backups de prueba creados exitosamente")
        print(f"\n📋 Puedes verlos en:")
        print(f"   GET http://localhost:8000/api/backups/history/")
        print(f"\n☁️  También están en Supabase Storage:")
        print(f"   Bucket: backups/{schema_name}/")


if __name__ == '__main__':
    crear_backups_prueba()
