"""
Verificar endpoint de horarios disponibles
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.test import RequestFactory
from agenda.views import CitaViewSet
from usuarios.models import Usuario

connection.set_schema('clinica_demo')

# Simular request
factory = RequestFactory()

# Obtener usuario paciente
paciente_user = Usuario.objects.get(email='paciente1@test.com')

# Crear request simulado usando DRF Request
from rest_framework.request import Request

django_request = factory.get('/api/agenda/citas/horarios_disponibles/', {
    'odontologo': '103',
    'fecha': '2025-11-20'
})
django_request.user = paciente_user

# Wrap en DRF Request
request = Request(django_request)

# Llamar al viewset
viewset = CitaViewSet()
viewset.request = request
viewset.format_kwarg = None

response = viewset.horarios_disponibles(request)

print("\n" + "="*70)
print("🕐 HORARIOS DISPONIBLES - 20 Nov 2025")
print("="*70 + "\n")

data = response.data

print(f"📅 Fecha: {data['fecha']}")
print(f"👨‍⚕️ Odontólogo: {data['odontologo']}")
print(f"✅ Horarios disponibles: {data['total_disponibles']}")
print(f"❌ Horarios ocupados: {data['total_ocupados']}")
print(f"\n📋 Primeros 10 horarios:\n")

for horario in data['horarios'][:10]:
    icono = "✅" if horario['disponible'] else "❌"
    estado = "DISPONIBLE" if horario['disponible'] else "OCUPADO"
    print(f"  {icono} {horario['hora']} - {estado}")

print("\n" + "="*70)
print(f"\n💡 Endpoint: GET /api/agenda/citas/horarios_disponibles/")
print(f"   ?odontologo=103&fecha=2025-11-20")
print("\n" + "="*70 + "\n")
