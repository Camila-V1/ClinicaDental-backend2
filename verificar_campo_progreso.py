"""
Verificar que el campo progreso se envíe correctamente
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario
from tratamientos.models import PlanDeTratamiento
from tratamientos.serializers import PlanDeTratamientoListSerializer

connection.set_schema('clinica_demo')

user = Usuario.objects.get(email='paciente1@test.com')
planes = PlanDeTratamiento.objects.filter(paciente=user.perfil_paciente)
serializer = PlanDeTratamientoListSerializer(planes, many=True)

if serializer.data:
    plan = serializer.data[0]
    
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN CAMPOS PROGRESO")
    print("="*70)
    
    print(f"\n📊 Campos de progreso:")
    print(f"  - porcentaje_completado: {plan.get('porcentaje_completado')} (tipo: {type(plan.get('porcentaje_completado')).__name__})")
    print(f"  - progreso: {plan.get('progreso')} (tipo: {type(plan.get('progreso')).__name__})")
    
    print(f"\n📊 Campos de items:")
    print(f"  - cantidad_items: {plan.get('cantidad_items')} (tipo: {type(plan.get('cantidad_items')).__name__})")
    print(f"  - num_items: {plan.get('num_items')} (tipo: {type(plan.get('num_items')).__name__})")
    print(f"  - total_items: {plan.get('total_items')} (tipo: {type(plan.get('total_items')).__name__})")
    print(f"  - items_completados: {plan.get('items_completados')} (tipo: {type(plan.get('items_completados')).__name__})")
    
    print(f"\n📊 Otros campos:")
    print(f"  - observaciones: '{plan.get('observaciones')}' (tipo: {type(plan.get('observaciones')).__name__})")
    print(f"  - notas_internas: '{plan.get('notas_internas')}' (tipo: {type(plan.get('notas_internas')).__name__ if 'notas_internas' in plan else 'N/A'})")
    
    print(f"\n🧪 Verificación booleana:")
    print(f"  - bool(50) = {bool(50)}")
    print(f"  - bool(0) = {bool(0)}")
    print(f"  - bool('') = {bool('')}")
    print(f"  - progreso == 50: {plan.get('progreso') == 50}")
    print(f"  - progreso is not None: {plan.get('progreso') is not None}")
    
    print(f"\n📄 JSON Serializado (como lo recibe el frontend):")
    json_str = json.dumps(plan, indent=2, default=str)
    # Solo mostrar campos relevantes
    import re
    relevant = ['porcentaje_completado', 'progreso', 'cantidad_items', 'items_completados', 'observaciones']
    for campo in relevant:
        match = re.search(rf'"{campo}":\s*([^,\n]+)', json_str)
        if match:
            print(f"  {campo}: {match.group(1)}")
    
    print("\n" + "="*70 + "\n")
