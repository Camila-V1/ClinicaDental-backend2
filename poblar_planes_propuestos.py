"""
Script para poblar planes de tratamiento propuestos para María (paciente1@test.com)
"""

import os
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from usuarios.models import PerfilPaciente, PerfilOdontologo
from tratamientos.models import Servicio, PlanDeTratamiento, ItemPlanTratamiento

def poblar_planes_propuestos():
    print("=" * 80)
    print("🦷 POBLANDO PLANES PROPUESTOS PARA MARÍA")
    print("=" * 80)
    
    # Obtener tenant actual
    try:
        tenant_name = connection.tenant.schema_name if hasattr(connection, 'tenant') else 'clinica_demo'
    except:
        tenant_name = 'clinica_demo'
    print(f"📍 Tenant: {tenant_name}")
    
    # Buscar paciente María
    try:
        paciente = PerfilPaciente.objects.get(usuario__email='paciente1@test.com')
        print(f"✅ Paciente encontrado: {paciente.usuario.nombre} {paciente.usuario.apellido} (ID: {paciente.pk})")
    except PerfilPaciente.DoesNotExist:
        print("❌ No se encontró el paciente María")
        return
    
    # Buscar odontólogo
    try:
        odontologo = PerfilOdontologo.objects.first()
        print(f"✅ Odontólogo encontrado: Dr. {odontologo.usuario.nombre} {odontologo.usuario.apellido} (ID: {odontologo.pk})")
    except:
        print("❌ No se encontró odontólogo")
        return
    
    # Buscar tratamientos del catálogo
    try:
        consulta = Servicio.objects.get(nombre='Consulta General')
        limpieza = Servicio.objects.get(nombre='Limpieza Dental')
        restauracion = Servicio.objects.get(nombre='Restauración Dental')
        endodoncia = Servicio.objects.get(nombre='Endodoncia')
        print(f"✅ Tratamientos del catálogo encontrados")
    except Exception as e:
        print(f"❌ Error buscando tratamientos: {e}")
        return
    
    print("\n" + "=" * 80)
    print("📋 CREANDO PLANES PROPUESTOS")
    print("=" * 80)
    
    # PLAN 1: Ortodoncia Completa (ALTA PRIORIDAD)
    print("\n1️⃣ Creando Plan: Ortodoncia Completa...")
    plan1 = PlanDeTratamiento.objects.create(
        paciente=paciente,
        odontologo=odontologo,
        titulo="Ortodoncia Completa con Brackets Metálicos",
        descripcion="Plan de tratamiento ortodóncico completo con brackets metálicos de alta calidad. Duración estimada: 18 meses. Incluye consultas mensuales de ajuste y seguimiento post-tratamiento.",
        estado='PROPUESTO',
        prioridad='ALTA',
        fecha_presentacion=datetime.now(),
    )
    
    # Items del plan de ortodoncia
    items_ortodoncia = [
        {"nombre": "Consulta de Ortodoncia", "descripcion": "Evaluación ortodóncica inicial", "precio": "150.00", "orden": 1, "notas": "Evaluación completa con radiografías panorámicas y cefalométricas"},
        {"nombre": "Limpieza Dental Profunda", "descripcion": "Profilaxis completa", "precio": "100.00", "orden": 2, "notas": "Limpieza profunda requerida antes de colocar brackets"},
        {"nombre": "Colocación de Brackets", "descripcion": "Instalación de brackets metálicos", "precio": "1200.00", "orden": 3, "notas": "Brackets metálicos de alta calidad en ambas arcadas, incluye primer arco"},
        {"nombre": "Controles Mensuales (x12)", "descripcion": "Ajustes mensuales", "precio": "1200.00", "orden": 4, "notas": "12 controles mensuales con cambio de arcos y ajustes necesarios"},
        {"nombre": "Controles Mensuales (x6)", "descripcion": "Ajustes finales", "precio": "600.00", "orden": 5, "notas": "6 controles adicionales para ajustes finales"},
        {"nombre": "Retiro de Brackets", "descripcion": "Remoción de aparatología", "precio": "200.00", "orden": 6, "notas": "Retiro cuidadoso de brackets y limpieza dental completa"},
        {"nombre": "Retenedores", "descripcion": "Fabricación de retenedores", "precio": "450.00", "orden": 7, "notas": "Retenedores superior e inferior removibles, uso permanente nocturno"},
        {"nombre": "Controles Post-Ortodoncia (x6)", "descripcion": "Seguimiento", "precio": "120.00", "orden": 8, "notas": "6 controles bimensuales para verificar estabilidad"},
        {"nombre": "Radiografía Final", "descripcion": "Control radiográfico", "precio": "80.00", "orden": 9, "notas": "Radiografía panorámica para verificar resultados finales"},
    ]
    
    total_ortodoncia = Decimal('0.00')
    for item_data in items_ortodoncia:
        # Crear tratamiento en catálogo si no existe
        tratamiento, _ = Servicio.objects.get_or_create(
            nombre=item_data["nombre"],
            defaults={
                'descripcion': item_data["descripcion"],
                'precio_base': Decimal(item_data["precio"]),
                'duracion_estimada_minutos': 60,
                'codigo': item_data["nombre"][:10].upper()
            }
        )
        
        ItemPlanTratamiento.objects.create(
            plan=plan1,
            tratamiento=tratamiento,
            precio=Decimal(item_data["precio"]),
            estado='PENDIENTE',
            orden=item_data["orden"],
            notas=item_data["notas"]
        )
        total_ortodoncia += Decimal(item_data["precio"])
    
    print(f"   ✅ Plan creado (ID: {plan1.id}) - Total: ${total_ortodoncia}")
    print(f"   📊 {len(items_ortodoncia)} items agregados")
    
    # PLAN 2: Implante Dental (MEDIA PRIORIDAD)
    print("\n2️⃣ Creando Plan: Implante Dental Pieza 26...")
    plan2 = PlanDeTratamiento.objects.create(
        paciente=paciente,
        odontologo=odontologo,
        titulo="Implante Dental Pieza 26",
        descripcion="Colocación de implante dental de titanio en pieza 26 (primer molar superior derecho) con corona de porcelana. Incluye cirugía de implante, período de osteointegración y colocación de corona definitiva.",
        estado='PROPUESTO',
        prioridad='MEDIA',
        fecha_presentacion=datetime.now() - timedelta(days=1),
    )
    
    items_implante = [
        {"nombre": "Consulta de Implantología", "descripcion": "Evaluación inicial", "precio": "100.00", "orden": 1, "notas": "Evaluación completa con radiografías 3D y planificación digital"},
        {"nombre": "Cirugía de Implante", "descripcion": "Colocación de implante", "precio": "800.00", "orden": 2, "notas": "Implante de titanio de alta calidad con técnica mínimamente invasiva"},
        {"nombre": "Control Post-Quirúrgico", "descripcion": "Revisión post-cirugía", "precio": "50.00", "orden": 3, "notas": "Control a los 7 días, retiro de puntos y evaluación de cicatrización"},
        {"nombre": "Corona de Porcelana", "descripcion": "Corona definitiva", "precio": "700.00", "orden": 4, "notas": "Corona de porcelana-cerámica de alta estética sobre implante"},
        {"nombre": "Control Final", "descripcion": "Verificación", "precio": "50.00", "orden": 5, "notas": "Control final con radiografía para verificar ajuste y oclusión"},
    ]
    
    total_implante = Decimal('0.00')
    for item_data in items_implante:
        tratamiento, _ = Servicio.objects.get_or_create(
            nombre=item_data["nombre"],
            defaults={
                'descripcion': item_data["descripcion"],
                'precio_base': Decimal(item_data["precio"]),
                'duracion_estimada_minutos': 90,
                'codigo': item_data["nombre"][:10].upper()
            }
        )
        
        ItemPlanTratamiento.objects.create(
            plan=plan2,
            tratamiento=tratamiento,
            precio=Decimal(item_data["precio"]),
            estado='PENDIENTE',
            orden=item_data["orden"],
            notas=item_data["notas"]
        )
        total_implante += Decimal(item_data["precio"])
    
    print(f"   ✅ Plan creado (ID: {plan2.id}) - Total: ${total_implante}")
    print(f"   📊 {len(items_implante)} items agregados")
    
    # PLAN 3: Blanqueamiento Dental (BAJA PRIORIDAD)
    print("\n3️⃣ Creando Plan: Blanqueamiento Dental Profesional...")
    plan3 = PlanDeTratamiento.objects.create(
        paciente=paciente,
        odontologo=odontologo,
        titulo="Blanqueamiento Dental Profesional",
        descripcion="Tratamiento de blanqueamiento dental profesional con técnica combinada (en consultorio + domiciliaria). Incluye limpieza previa, aplicación de gel blanqueador en consultorio y kit para uso en casa.",
        estado='PROPUESTO',
        prioridad='BAJA',
        fecha_presentacion=datetime.now() - timedelta(days=2),
    )
    
    items_blanqueamiento = [
        {"nombre": "Limpieza Dental", "descripcion": "Profilaxis previa", "precio": "80.00", "orden": 1, "notas": "Limpieza profesional necesaria antes del blanqueamiento"},
        {"nombre": "Blanqueamiento en Consultorio", "descripcion": "Sesión profesional", "precio": "300.00", "orden": 2, "notas": "Aplicación de gel blanqueador de alta concentración con luz LED"},
        {"nombre": "Kit de Blanqueamiento Domiciliario", "descripcion": "Para uso en casa", "precio": "150.00", "orden": 3, "notas": "Cubetas personalizadas y gel blanqueador para 2 semanas de uso nocturno"},
        {"nombre": "Control y Retoque", "descripcion": "Seguimiento", "precio": "50.00", "orden": 4, "notas": "Control a las 2 semanas con retoque si es necesario"},
    ]
    
    total_blanqueamiento = Decimal('0.00')
    for item_data in items_blanqueamiento:
        tratamiento, _ = Servicio.objects.get_or_create(
            nombre=item_data["nombre"],
            defaults={
                'descripcion': item_data["descripcion"],
                'precio_base': Decimal(item_data["precio"]),
                'duracion_estimada_minutos': 60,
                'codigo': item_data["nombre"][:10].upper()
            }
        )
        
        ItemPlanTratamiento.objects.create(
            plan=plan3,
            tratamiento=tratamiento,
            precio=Decimal(item_data["precio"]),
            estado='PENDIENTE',
            orden=item_data["orden"],
            notas=item_data["notas"]
        )
        total_blanqueamiento += Decimal(item_data["precio"])
    
    print(f"   ✅ Plan creado (ID: {plan3.id}) - Total: ${total_blanqueamiento}")
    print(f"   📊 {len(items_blanqueamiento)} items agregados")
    
    # PLAN 4: Tratamiento de Caries Múltiples (ALTA PRIORIDAD)
    print("\n4️⃣ Creando Plan: Tratamiento de Caries Múltiples...")
    plan4 = PlanDeTratamiento.objects.create(
        paciente=paciente,
        odontologo=odontologo,
        titulo="Tratamiento de Caries Múltiples",
        descripcion="Plan integral para tratamiento de 5 caries detectadas en piezas 14, 15, 24, 36 y 37. Incluye restauraciones con resina compuesta de alta calidad y estética.",
        estado='PROPUESTO',
        prioridad='ALTA',
        fecha_presentacion=datetime.now() - timedelta(hours=12),
    )
    
    items_caries = [
        {"nombre": "Consulta General", "descripcion": "Diagnóstico inicial", "precio": "50.00", "orden": 1, "notas": "Evaluación completa con radiografías de detalle"},
        {"nombre": "Restauración Dental", "descripcion": "Pieza 14", "precio": "150.00", "orden": 2, "notas": "Restauración con resina compuesta fotopolimerizable"},
        {"nombre": "Restauración Dental", "descripcion": "Pieza 15", "precio": "150.00", "orden": 3, "notas": "Restauración con resina compuesta fotopolimerizable"},
        {"nombre": "Restauración Dental", "descripcion": "Pieza 24", "precio": "150.00", "orden": 4, "notas": "Restauración con resina compuesta fotopolimerizable"},
        {"nombre": "Restauración Dental", "descripcion": "Pieza 36", "precio": "150.00", "orden": 5, "notas": "Restauración con resina compuesta fotopolimerizable"},
        {"nombre": "Restauración Dental", "descripcion": "Pieza 37", "precio": "150.00", "orden": 6, "notas": "Restauración con resina compuesta fotopolimerizable"},
        {"nombre": "Control Post-Tratamiento", "descripcion": "Verificación", "precio": "30.00", "orden": 7, "notas": "Control a los 15 días para verificar adaptación y oclusión"},
    ]
    
    total_caries = Decimal('0.00')
    for item_data in items_caries:
        tratamiento, _ = Servicio.objects.get_or_create(
            nombre=item_data["nombre"],
            defaults={
                'descripcion': item_data["descripcion"],
                'precio_base': Decimal(item_data["precio"]),
                'duracion_estimada_minutos': 45,
                'codigo': item_data["nombre"][:10].upper()
            }
        )
        
        ItemPlanTratamiento.objects.create(
            plan=plan4,
            tratamiento=tratamiento,
            precio=Decimal(item_data["precio"]),
            estado='PENDIENTE',
            orden=item_data["orden"],
            notas=item_data["notas"]
        )
        total_caries += Decimal(item_data["precio"])
    
    print(f"   ✅ Plan creado (ID: {plan4.id}) - Total: ${total_caries}")
    print(f"   📊 {len(items_caries)} items agregados")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("✅ RESUMEN DE PLANES CREADOS")
    print("=" * 80)
    
    planes_propuestos = PlanDeTratamiento.objects.filter(
        paciente=paciente,
        estado='PROPUESTO'
    )
    
    print(f"\n📋 Total de planes propuestos para {paciente.usuario.nombre}: {planes_propuestos.count()}")
    print("\nDetalle:")
    for plan in planes_propuestos:
        items_count = plan.items.count()
        precio_total = sum(item.precio for item in plan.items.all())
        print(f"  • {plan.titulo}")
        print(f"    - ID: {plan.id}")
        print(f"    - Prioridad: {plan.get_prioridad_display()}")
        print(f"    - Items: {items_count}")
        print(f"    - Precio Total: ${precio_total}")
        print(f"    - Fecha Presentación: {plan.fecha_presentacion.strftime('%d/%m/%Y %H:%M')}")
        print()
    
    print("=" * 80)
    print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("\n💡 Ahora puedes:")
    print("   1. Acceder al frontend como paciente1@test.com")
    print("   2. Ir a 'Solicitudes de Tratamiento'")
    print("   3. Ver los 4 planes propuestos pendientes de aprobación")
    print()

if __name__ == '__main__':
    poblar_planes_propuestos()
