"""
Poblar especialidades odontológicas y asignar al odontólogo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from tratamientos.models import Especialidad
from usuarios.models import Usuario

connection.set_schema('clinica_demo')

print("\n" + "="*70)
print("🦷 POBLANDO ESPECIALIDADES ODONTOLÓGICAS")
print("="*70 + "\n")

# Crear especialidades comunes en odontología
especialidades_data = [
    {
        'nombre': 'Odontología General',
        'descripcion': 'Atención dental integral y preventiva'
    },
    {
        'nombre': 'Ortodoncia',
        'descripcion': 'Corrección de malposiciones dentales y maxilares'
    },
    {
        'nombre': 'Endodoncia',
        'descripcion': 'Tratamiento de conductos radiculares'
    },
    {
        'nombre': 'Periodoncia',
        'descripcion': 'Tratamiento de enfermedades de las encías'
    },
    {
        'nombre': 'Cirugía Oral',
        'descripcion': 'Procedimientos quirúrgicos en boca y maxilares'
    },
    {
        'nombre': 'Odontopediatría',
        'descripcion': 'Odontología especializada en niños'
    },
    {
        'nombre': 'Implantología',
        'descripcion': 'Colocación de implantes dentales'
    },
    {
        'nombre': 'Estética Dental',
        'descripcion': 'Tratamientos de embellecimiento dental'
    }
]

especialidades_creadas = []

for esp_data in especialidades_data:
    especialidad, created = Especialidad.objects.get_or_create(
        nombre=esp_data['nombre'],
        defaults={'descripcion': esp_data['descripcion']}
    )
    
    if created:
        print(f"✅ Creada: {especialidad.nombre}")
        especialidades_creadas.append(especialidad)
    else:
        print(f"ℹ️  Ya existe: {especialidad.nombre}")

print(f"\n📊 Total especialidades creadas: {len(especialidades_creadas)}")
print(f"📊 Total especialidades en BD: {Especialidad.objects.count()}")

# Asignar especialidad "Odontología General" al odontólogo
print("\n" + "="*70)
print("👨‍⚕️ ASIGNANDO ESPECIALIDAD AL ODONTÓLOGO")
print("="*70 + "\n")

try:
    usuario = Usuario.objects.get(email='odontologo@clinica-demo.com')
    
    if hasattr(usuario, 'perfil_odontologo'):
        perfil = usuario.perfil_odontologo
        
        # Obtener la especialidad "Odontología General"
        especialidad_general = Especialidad.objects.get(nombre='Odontología General')
        
        perfil.especialidad = especialidad_general
        perfil.save()
        
        print(f"✅ Especialidad asignada a: {usuario.nombre} {usuario.apellido}")
        print(f"   📋 Especialidad: {especialidad_general.nombre}")
        print(f"   📧 Email: {usuario.email}")
    else:
        print("❌ El usuario no tiene perfil de odontólogo")

except Usuario.DoesNotExist:
    print("❌ Usuario odontólogo no encontrado")
except Especialidad.DoesNotExist:
    print("❌ Especialidad 'Odontología General' no encontrada")

print("\n" + "="*70)
print("✅ PROCESO COMPLETADO")
print("="*70 + "\n")
