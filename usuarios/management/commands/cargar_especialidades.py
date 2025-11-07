"""
Comando para cargar especialidades odontológicas iniciales.
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from tenants.models import Clinica
from usuarios.models import Especialidad


class Command(BaseCommand):
    help = 'Carga especialidades odontológicas iniciales en el catálogo de cada clínica'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Nombre del esquema específico (opcional, si no se especifica se aplica a todos)'
        )

    def handle(self, *args, **options):
        especialidades = [
            {
                'nombre': 'Odontología General',
                'descripcion': 'Práctica general de odontología, tratamientos preventivos y curativos básicos.'
            },
            {
                'nombre': 'Ortodoncia',
                'descripcion': 'Corrección de la posición de los dientes y los huesos maxilares para mejorar la mordida.'
            },
            {
                'nombre': 'Endodoncia',
                'descripcion': 'Tratamiento de conductos radiculares, pulpa dental y tejidos periapicales.'
            },
            {
                'nombre': 'Periodoncia',
                'descripcion': 'Tratamiento de las enfermedades de las encías y estructuras de soporte de los dientes.'
            },
            {
                'nombre': 'Prostodoncia',
                'descripcion': 'Rehabilitación oral mediante prótesis dentales, coronas, puentes e implantes.'
            },
            {
                'nombre': 'Cirugía Oral y Maxilofacial',
                'descripcion': 'Cirugías de boca, mandíbula, cara y cuello, incluyendo extracciones complejas.'
            },
            {
                'nombre': 'Odontopediatría',
                'descripcion': 'Cuidado dental especializado para bebés, niños y adolescentes.'
            },
            {
                'nombre': 'Implantología',
                'descripcion': 'Colocación y mantenimiento de implantes dentales para reemplazo de dientes.'
            },
            {
                'nombre': 'Estética Dental',
                'descripcion': 'Tratamientos cosméticos para mejorar la apariencia de los dientes y sonrisa.'
            },
            {
                'nombre': 'Radiología Oral',
                'descripcion': 'Diagnóstico mediante radiografías y estudios de imagen dental.'
            },
        ]

        schema_name = options.get('schema')
        
        if schema_name:
            # Cargar en un esquema específico
            self._cargar_en_schema(schema_name, especialidades)
        else:
            # Cargar en todos los tenants
            clinicas = Clinica.objects.exclude(schema_name='public')
            for clinica in clinicas:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(f'\n📋 Procesando clínica: {clinica.nombre}')
                )
                self._cargar_en_schema(clinica.schema_name, especialidades)

        self.stdout.write(
            self.style.SUCCESS('\n✅ Proceso completado exitosamente')
        )

    def _cargar_en_schema(self, schema_name, especialidades):
        """Carga las especialidades en un esquema específico."""
        with schema_context(schema_name):
            creadas = 0
            actualizadas = 0

            for esp_data in especialidades:
                especialidad, created = Especialidad.objects.get_or_create(
                    nombre=esp_data['nombre'],
                    defaults={'descripcion': esp_data['descripcion']}
                )
                
                if created:
                    creadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Creada: {especialidad.nombre}')
                    )
                else:
                    # Actualizar descripción si ya existe
                    especialidad.descripcion = esp_data['descripcion']
                    especialidad.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ↻ Actualizada: {especialidad.nombre}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'  📊 Resultado: {creadas} creadas, {actualizadas} actualizadas'
                )
            )

