import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from tratamientos.models import PlanDeTratamiento

with schema_context('clinica_demo'):
    # Actualizar estados de MAYÚSCULAS a minúsculas
    actualizaciones = {
        'PROPUESTO': 'propuesto',
        'PRESENTADO': 'presentado',
        'ACEPTADO': 'aceptado',
        'APROBADO': 'aprobado',
        'RECHAZADO': 'rechazado',
        'EN_PROGRESO': 'en_progreso',
        'COMPLETADO': 'completado',
        'CANCELADO': 'cancelado',
    }
    
    total = 0
    for viejo, nuevo in actualizaciones.items():
        count = PlanDeTratamiento.objects.filter(estado=viejo).update(estado=nuevo)
        if count > 0:
            print(f'✅ Actualizados {count} planes de "{viejo}" → "{nuevo}"')
            total += count
    
    print(f'\n🎉 Total actualizado: {total} planes')
    
    # Mostrar resumen
    print('\n📊 Resumen de estados:')
    for estado in ['propuesto', 'presentado', 'aceptado', 'aprobado', 'rechazado', 'en_progreso', 'completado', 'cancelado']:
        count = PlanDeTratamiento.objects.filter(estado=estado).count()
        if count > 0:
            print(f'   - {estado}: {count} planes')
