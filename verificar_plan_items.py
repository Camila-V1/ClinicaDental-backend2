"""
Verificar que el plan con items se serialice correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario
from tratamientos.models import PlanDeTratamiento
from tratamientos.serializers import PlanDeTratamientoListSerializer

connection.set_schema('clinica_demo')

user = Usuario.objects.get(email='paciente1@test.com')
planes = PlanDeTratamiento.objects.filter(paciente=user.perfil_paciente, estado='EN_PROGRESO')
serializer = PlanDeTratamientoListSerializer(planes, many=True)

if serializer.data:
    plan_data = serializer.data[0]
    
    print("\n" + "="*70)
    print("✅ DATOS DEL PLAN PARA FRONTEND")
    print("="*70)
    
    print(f"\n📋 Información General:")
    print(f"  - ID: {plan_data['id']}")
    print(f"  - Título/Nombre: {plan_data.get('titulo')} / {plan_data.get('nombre')}")
    print(f"  - Estado: {plan_data['estado']}")
    print(f"  - Paciente: {plan_data['paciente_nombre']}")
    
    print(f"\n💰 Precios:")
    print(f"  - precio_total_plan: {plan_data.get('precio_total_plan')}")
    print(f"  - total: {plan_data.get('total')}")
    print(f"  - monto_total: {plan_data.get('monto_total')}")
    print(f"  - costo_total: {plan_data.get('costo_total')}")
    
    print(f"\n📊 Progreso:")
    print(f"  - porcentaje_completado: {plan_data.get('porcentaje_completado')}%")
    print(f"  - progreso: {plan_data.get('progreso')}%")
    print(f"  - cantidad_items: {plan_data.get('cantidad_items')}")
    print(f"  - num_items: {plan_data.get('num_items')}")
    print(f"  - total_items: {plan_data.get('total_items')}")
    print(f"  - items_completados: {plan_data.get('items_completados')}")
    
    print(f"\n🗂️ Items del plan ({len(plan_data.get('items_simples', []))}):")
    for i, item in enumerate(plan_data.get('items_simples', [])[:3], 1):
        print(f"  {i}. {item.get('servicio_nombre')} - {item.get('estado')}")
        print(f"     Precio: ${item.get('precio_total')}")
        print(f"     Notas: {item.get('notas', 'N/A')[:50]}...")
    
    print(f"\n📝 Otros campos:")
    print(f"  - observaciones: '{plan_data.get('observaciones')}'")
    print(f"  - paciente_id: {plan_data.get('paciente_id')}")
    print(f"  - odontologo_nombre: {plan_data.get('odontologo_nombre')}")
    print(f"  - prioridad: {plan_data.get('prioridad')}")
    
    print("\n" + "="*70 + "\n")
else:
    print("❌ No se encontró plan")
