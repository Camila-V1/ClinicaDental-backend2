"""
Módulo para poblar planes de tratamiento con datos realistas
"""

from tratamientos.models import PlanDeTratamiento, ItemPlanTratamiento, Servicio
from usuarios.models import PerfilPaciente, PerfilOdontologo
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random


def poblar_planes_tratamiento(pacientes, odontologos, servicios):
    """
    Crea planes de tratamiento con diferentes estados
    
    Args:
        pacientes: Lista de PerfilPaciente
        odontologos: Lista de PerfilOdontologo
        servicios: Lista de Servicio
    
    Returns:
        tuple: (planes_creados, items_creados)
    """
    planes_creados = []
    items_creados = []
    
    print("\n  🦷 Creando planes de tratamiento...")
    
    if not pacientes or not odontologos or not servicios:
        print("  ⚠️  Faltan datos para crear planes")
        return (planes_creados, items_creados)
    
    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # =========================================================================
    # 1. PLANES COMPLETADOS (este mes)
    # =========================================================================
    print("  → Planes completados este mes...")
    
    servicios_comunes = [s for s in servicios if s.codigo_servicio in 
                         ['ODG-002', 'ODG-003', 'CIR-001', 'EST-001']]
    
    for i in range(5):  # 5 planes completados
        paciente = random.choice(pacientes)
        odontologo = random.choice(odontologos)
        
        # Fecha de creación en este mes (hace 10-25 días)
        dias_atras = random.randint(10, 25)
        fecha_creacion = hoy - timedelta(days=dias_atras)
        
        # Crear el plan
        plan = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            fecha_creacion=fecha_creacion,
            diagnostico=f"Tratamiento dental completado para {paciente.usuario.nombre} {paciente.usuario.apellido}",
            observaciones="Tratamiento finalizado satisfactoriamente",
            estado='COMPLETADO'
        )
        planes_creados.append(plan)
        
        # Agregar 2-4 items completados
        num_items = random.randint(2, 4)
        servicios_seleccionados = random.sample(servicios_comunes, min(num_items, len(servicios_comunes)))
        
        for orden, servicio in enumerate(servicios_seleccionados, 1):
            # Fecha de realización entre creación del plan y hace 2 días
            dias_para_realizar = random.randint(1, min(dias_atras - 2, 15))
            fecha_realizada = fecha_creacion + timedelta(days=dias_para_realizar)
            
            item = ItemPlanTratamiento.objects.create(
                plan=plan,
                servicio=servicio,
                orden=orden,
                estado='COMPLETADO',
                fecha_estimada=fecha_creacion + timedelta(days=random.randint(3, 10)),
                fecha_realizada=fecha_realizada,
                notas=f"{servicio.nombre} realizado exitosamente"
            )
            items_creados.append(item)
        
        # Actualizar costos del plan
        plan.actualizar_costos()
    
    print(f"    ✓ {len([p for p in planes_creados if p.estado == 'COMPLETADO'])} planes completados")
    
    # =========================================================================
    # 2. PLANES EN PROGRESO
    # =========================================================================
    print("  → Planes en progreso...")
    
    for i in range(8):  # 8 planes en progreso
        paciente = random.choice(pacientes)
        odontologo = random.choice(odontologos)
        
        # Fecha de creación hace 5-20 días
        dias_atras = random.randint(5, 20)
        fecha_creacion = hoy - timedelta(days=dias_atras)
        
        plan = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            fecha_creacion=fecha_creacion,
            diagnostico=f"Plan de tratamiento para {paciente.usuario.nombre} {paciente.usuario.apellido}",
            observaciones="Tratamiento en curso",
            estado='EN_PROGRESO'
        )
        planes_creados.append(plan)
        
        # Agregar 3-6 items (algunos completados, otros pendientes)
        num_items = random.randint(3, 6)
        servicios_seleccionados = random.sample(servicios, min(num_items, len(servicios)))
        
        for orden, servicio in enumerate(servicios_seleccionados, 1):
            # 60% completados, 40% pendientes/en progreso
            if random.random() < 0.6:
                estado_item = 'COMPLETADO'
                fecha_realizada = fecha_creacion + timedelta(days=random.randint(1, dias_atras - 1))
                notas = f"{servicio.nombre} completado"
            else:
                estado_item = random.choice(['PENDIENTE', 'EN_PROGRESO'])
                fecha_realizada = None
                notas = f"{servicio.nombre} programado"
            
            item = ItemPlanTratamiento.objects.create(
                plan=plan,
                servicio=servicio,
                orden=orden,
                estado=estado_item,
                fecha_estimada=hoy + timedelta(days=random.randint(1, 30)),
                fecha_realizada=fecha_realizada,
                notas=notas
            )
            items_creados.append(item)
        
        plan.actualizar_costos()
    
    print(f"    ✓ {len([p for p in planes_creados if p.estado == 'EN_PROGRESO'])} planes en progreso")
    
    # =========================================================================
    # 3. PLANES PROPUESTOS/APROBADOS
    # =========================================================================
    print("  → Planes propuestos y aprobados...")
    
    for i in range(6):  # 6 planes propuestos/aprobados
        paciente = random.choice(pacientes)
        odontologo = random.choice(odontologos)
        
        # Fecha de creación hace 1-10 días
        dias_atras = random.randint(1, 10)
        fecha_creacion = hoy - timedelta(days=dias_atras)
        
        estado = random.choice(['PROPUESTO', 'PROPUESTO', 'APROBADO'])  # Más propuestos
        
        plan = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            fecha_creacion=fecha_creacion,
            diagnostico=f"Plan propuesto para {paciente.usuario.nombre} {paciente.usuario.apellido}",
            observaciones="Esperando aprobación del paciente" if estado == 'PROPUESTO' else "Plan aprobado, listo para iniciar",
            estado=estado
        )
        planes_creados.append(plan)
        
        # Agregar 2-5 items todos pendientes
        num_items = random.randint(2, 5)
        servicios_seleccionados = random.sample(servicios, min(num_items, len(servicios)))
        
        for orden, servicio in enumerate(servicios_seleccionados, 1):
            item = ItemPlanTratamiento.objects.create(
                plan=plan,
                servicio=servicio,
                orden=orden,
                estado='PENDIENTE',
                fecha_estimada=hoy + timedelta(days=random.randint(7, 45)),
                notas=f"{servicio.nombre} programado"
            )
            items_creados.append(item)
        
        plan.actualizar_costos()
    
    print(f"    ✓ {len([p for p in planes_creados if p.estado in ['PROPUESTO', 'APROBADO']])} planes propuestos/aprobados")
    
    # =========================================================================
    # 4. ALGUNOS PLANES CANCELADOS
    # =========================================================================
    print("  → Planes cancelados...")
    
    for i in range(2):  # 2 planes cancelados
        paciente = random.choice(pacientes)
        odontologo = random.choice(odontologos)
        
        dias_atras = random.randint(15, 40)
        fecha_creacion = hoy - timedelta(days=dias_atras)
        
        plan = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            fecha_creacion=fecha_creacion,
            diagnostico="Plan cancelado por el paciente",
            observaciones="Paciente decidió no continuar con el tratamiento",
            estado='CANCELADO'
        )
        planes_creados.append(plan)
        
        # Solo 1-2 items, todos cancelados
        num_items = random.randint(1, 2)
        servicios_seleccionados = random.sample(servicios, min(num_items, len(servicios)))
        
        for orden, servicio in enumerate(servicios_seleccionados, 1):
            item = ItemPlanTratamiento.objects.create(
                plan=plan,
                servicio=servicio,
                orden=orden,
                estado='CANCELADO',
                notas="Cancelado junto con el plan"
            )
            items_creados.append(item)
    
    print(f"    ✓ {len([p for p in planes_creados if p.estado == 'CANCELADO'])} planes cancelados")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print(f"\n  ✅ Total planes creados: {len(planes_creados)}")
    print(f"  ✅ Total items creados: {len(items_creados)}")
    
    # Estadísticas por estado
    estados_count = {}
    for plan in planes_creados:
        estados_count[plan.estado] = estados_count.get(plan.estado, 0) + 1
    
    print("     Planes por estado:")
    for estado, count in estados_count.items():
        print(f"       • {estado}: {count}")
    
    # Items completados
    items_completados = len([i for i in items_creados if i.estado == 'COMPLETADO'])
    print(f"     Procedimientos completados: {items_completados}")
    
    return (planes_creados, items_creados)
