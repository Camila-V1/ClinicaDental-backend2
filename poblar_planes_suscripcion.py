"""
Script para crear los planes de suscripción iniciales en el sistema.
Ejecutar: python poblar_planes_suscripcion.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import PlanSuscripcion


def crear_planes():
    """Crear los planes de suscripción por defecto."""
    
    planes = [
        {
            'nombre': 'Plan Prueba',
            'tipo': 'PRUEBA',
            'descripcion': 'Plan de prueba gratuito por 7 días. Acceso completo a todas las funcionalidades.',
            'precio': 0.00,
            'duracion_dias': 7,
            'max_usuarios': 5,
            'max_pacientes': 50,
            'activo': True
        },
        {
            'nombre': 'Plan Mensual',
            'tipo': 'MENSUAL',
            'descripcion': 'Plan mensual ideal para clínicas pequeñas. Incluye todas las funcionalidades básicas.',
            'precio': 49.99,
            'duracion_dias': 30,
            'max_usuarios': 10,
            'max_pacientes': 500,
            'activo': True
        },
        {
            'nombre': 'Plan Trimestral',
            'tipo': 'TRIMESTRAL',
            'descripcion': 'Plan trimestral con 10% de descuento. Ideal para clínicas en crecimiento.',
            'precio': 134.97,  # 3 meses con 10% descuento
            'duracion_dias': 90,
            'max_usuarios': 15,
            'max_pacientes': 1000,
            'activo': True
        },
        {
            'nombre': 'Plan Semestral',
            'tipo': 'SEMESTRAL',
            'descripcion': 'Plan semestral con 15% de descuento. Perfecto para clínicas medianas.',
            'precio': 254.95,  # 6 meses con 15% descuento
            'duracion_dias': 180,
            'max_usuarios': 20,
            'max_pacientes': 2000,
            'activo': True
        },
        {
            'nombre': 'Plan Anual',
            'tipo': 'ANUAL',
            'descripcion': 'Plan anual con 20% de descuento. La mejor opción para clínicas establecidas.',
            'precio': 479.90,  # 12 meses con 20% descuento
            'duracion_dias': 365,
            'max_usuarios': 30,
            'max_pacientes': 5000,
            'activo': True
        }
    ]
    
    print("🚀 Creando planes de suscripción...")
    print("-" * 60)
    
    for plan_data in planes:
        plan, created = PlanSuscripcion.objects.get_or_create(
            tipo=plan_data['tipo'],
            defaults=plan_data
        )
        
        if created:
            print(f"✅ Creado: {plan.nombre}")
            print(f"   💰 Precio: ${plan.precio}")
            print(f"   📅 Duración: {plan.duracion_dias} días")
            print(f"   👥 Max usuarios: {plan.max_usuarios}")
            print(f"   🏥 Max pacientes: {plan.max_pacientes}")
        else:
            print(f"ℹ️  Ya existe: {plan.nombre}")
        
        print("-" * 60)
    
    print("\n✨ Proceso completado!")
    print(f"📊 Total de planes activos: {PlanSuscripcion.objects.filter(activo=True).count()}")


if __name__ == '__main__':
    crear_planes()
