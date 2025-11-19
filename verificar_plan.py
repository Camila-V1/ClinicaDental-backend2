import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
connection.set_schema('clinica_demo')

from tratamientos.models import PlanDeTratamiento
from tratamientos.serializers import PlanDeTratamientoListSerializer
from usuarios.models import Usuario

user = Usuario.objects.get(email='paciente1@test.com')
plan = PlanDeTratamiento.objects.filter(paciente=user.perfil_paciente).first()

if plan:
    print(f"✅ Plan encontrado: ID {plan.id}")
    
    # Serializar
    from rest_framework.renderers import JSONRenderer
    serializer = PlanDeTratamientoListSerializer(plan)
    data = serializer.data
    
    print("\n📊 Campos en serializer:")
    for key in data.keys():
        print(f"  - {key}: {data[key]}")
    
    print(f"\n📄 JSON completo:")
    print(json.dumps(dict(data), indent=2, default=str))
else:
    print("❌ No se encontró plan")
