"""
Script para poblar el plan de tratamiento de María García con items reales
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario
from tratamientos.models import PlanDeTratamiento, ItemPlanTratamiento, Servicio

connection.set_schema('clinica_demo')

print("\n" + "="*70)
print("💊 POBLANDO PLAN DE TRATAMIENTO CON ITEMS")
print("="*70 + "\n")

# Buscar el plan de María García
user = Usuario.objects.get(email='paciente1@test.com')
plan = PlanDeTratamiento.objects.get(paciente=user.perfil_paciente)

print(f"✅ Plan encontrado: {plan.titulo}")
print(f"   Estado actual: {plan.estado}")
print(f"   Items actuales: {plan.items.count()}")

# Limpiar items anteriores
plan.items.all().delete()
print(f"\n🗑️  Items anteriores eliminados")

# Buscar servicios existentes
print(f"\n📋 Buscando servicios existentes...")
servicios_existentes = list(Servicio.objects.filter(activo=True)[:6])

if len(servicios_existentes) < 3:
    print("❌ No hay suficientes servicios en la BD. Ejecuta poblar_sistema_completo.py primero")
    exit(1)

servicios = servicios_existentes
for servicio in servicios:
    print(f"  ♻️  {servicio.codigo_servicio}: {servicio.nombre} - ${servicio.precio_base}")

# Crear items del plan con diferentes estados
items_plan = [
    {
        'servicio': servicios[0],
        'estado': 'COMPLETADO',
        'notas': 'Consulta inicial completada - Diagnóstico: caries múltiples y necesidad de endodoncia'
    },
    {
        'servicio': servicios[1] if len(servicios) > 1 else servicios[0],
        'estado': 'COMPLETADO',
        'notas': 'Limpieza profunda realizada - Eliminación de sarro y placa bacteriana'
    },
    {
        'servicio': servicios[2] if len(servicios) > 2 else servicios[0],
        'estado': 'COMPLETADO',
        'notas': 'Restauración pieza 36 - Resina compuesta aplicada exitosamente'
    },
    {
        'servicio': servicios[5] if len(servicios) > 5 else servicios[0],
        'estado': 'EN_PROGRESO',
        'notas': 'Endodoncia pieza 46 - Primera sesión completada, falta obturación final'
    },
    {
        'servicio': servicios[2] if len(servicios) > 2 else servicios[0],
        'estado': 'PENDIENTE',
        'notas': 'Restauración pieza 47 - Programada para próxima semana'
    },
    {
        'servicio': servicios[1] if len(servicios) > 1 else servicios[0],
        'estado': 'PENDIENTE',
        'notas': 'Control y limpieza de mantenimiento - Programado en 3 meses'
    }
]

print(f"\n💊 Creando {len(items_plan)} items del plan...")
for i, item_data in enumerate(items_plan, 1):
    item = ItemPlanTratamiento.objects.create(
        plan=plan,
        servicio=item_data['servicio'],
        estado=item_data['estado'],
        notas=item_data['notas'],
        orden=i
    )
    
    icon = {
        'COMPLETADO': '✅',
        'EN_PROGRESO': '🔄',
        'PENDIENTE': '⏳'
    }[item.estado]
    
    print(f"  {icon} {item.estado:12} - {item.servicio.nombre:30} ${item.precio_total}")
    print(f"     └─ {item.notas[:60]}...")

# Verificar resultado
plan.refresh_from_db()

print(f"\n{'='*70}")
print(f"✅ PLAN ACTUALIZADO")
print(f"{'='*70}")
print(f"  Total items: {plan.cantidad_items}")
print(f"  Precio total: ${plan.precio_total_plan}")
print(f"  Porcentaje completado: {plan.porcentaje_completado}%")
print(f"  Estado: {plan.estado}")

# Desglose por estado
completados = plan.items.filter(estado='COMPLETADO').count()
en_progreso = plan.items.filter(estado='EN_PROGRESO').count()
pendientes = plan.items.filter(estado='PENDIENTE').count()

print(f"\n📊 Desglose:")
print(f"  ✅ Completados: {completados}")
print(f"  🔄 En progreso: {en_progreso}")
print(f"  ⏳ Pendientes: {pendientes}")

print(f"\n{'='*70}\n")
