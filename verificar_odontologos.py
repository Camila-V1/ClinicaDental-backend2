"""
Verificar el endpoint de odontólogos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario

connection.set_schema('clinica_demo')

print("\n" + "="*70)
print("👨‍⚕️ VERIFICANDO ODONTÓLOGOS EN BD")
print("="*70 + "\n")

odontologos = Usuario.objects.filter(tipo_usuario='ODONTOLOGO', is_active=True)

print(f"📊 Total odontólogos activos: {odontologos.count()}\n")

for odon in odontologos:
    print(f"✅ ID {odon.id}: Dr. {odon.nombre} {odon.apellido}")
    print(f"   📧 Email: {odon.email}")
    print(f"   📞 Teléfono: {odon.telefono}")
    
    if hasattr(odon, 'perfil_odontologo'):
        perfil = odon.perfil_odontologo
        especialidad = perfil.especialidad.nombre if perfil.especialidad else 'No especificada'
        print(f"   🎓 Especialidad: {especialidad}")
        print(f"   📜 Cédula: {perfil.cedulaProfesional or 'No registrada'}")
    else:
        print(f"   ⚠️ Sin perfil de odontólogo")
    print()

print("="*70 + "\n")

# Simular respuesta del endpoint
print("📤 RESPUESTA ESPERADA DEL ENDPOINT:\n")
import json

data = []
for odontologo in odontologos:
    odontologo_data = {
        'id': odontologo.id,
        'email': odontologo.email,
        'nombre': odontologo.nombre,
        'apellido': odontologo.apellido,
        'nombre_completo': f"Dr. {odontologo.nombre} {odontologo.apellido}",
        'telefono': odontologo.telefono,
    }
    
    if hasattr(odontologo, 'perfil_odontologo'):
        perfil = odontologo.perfil_odontologo
        odontologo_data.update({
            'especialidad': perfil.especialidad.nombre if perfil.especialidad else None,
            'cedula_profesional': perfil.cedulaProfesional,
            'experiencia': perfil.experienciaProfesional,
        })
    
    data.append(odontologo_data)

print(json.dumps(data, indent=2, ensure_ascii=False))
print("\n" + "="*70 + "\n")
