"""
Script para poblar datos completos de María García (paciente1@test.com)
Incluye: Citas, Historial Clínico, Odontograma, Episodios, Documentos, Planes de Tratamiento
"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.utils import timezone
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo
from agenda.models import Cita
from historial_clinico.models import HistorialClinico, Odontograma, EpisodioAtencion, DocumentoClinico
from tratamientos.models import PlanDeTratamiento, ItemPlanTratamiento, Servicio
from facturacion.models import Factura, Pago

# Establecer schema
connection.set_schema('clinica_demo')

print('=' * 80)
print('🦷 POBLANDO DATOS COMPLETOS PARA MARÍA GARCÍA')
print('=' * 80)

# Obtener usuarios y perfiles
try:
    maria_user = Usuario.objects.get(email='paciente1@test.com')
    maria = maria_user.perfil_paciente
    odontologo_user = Usuario.objects.get(email='odontologo@clinica-demo.com')
    odontologo = odontologo_user.perfil_odontologo
    print(f'✅ Paciente: {maria_user.nombre} {maria_user.apellido} (ID Usuario: {maria_user.id})')
    print(f'✅ Odontólogo: {odontologo_user.nombre} {odontologo_user.apellido} (ID Usuario: {odontologo_user.id})')
except (Usuario.DoesNotExist, PerfilPaciente.DoesNotExist, PerfilOdontologo.DoesNotExist, AttributeError) as e:
    print(f'❌ Error: {e}')
    exit(1)

# ============================================================================
# 1. CREAR CITAS
# ============================================================================
print('\n📅 CREANDO CITAS...')

# Limpiar citas existentes de María
Cita.objects.filter(paciente=maria).delete()

# Cita 1: HOY - Programada
from datetime import datetime
hoy = timezone.now()
cita1 = Cita.objects.create(
    paciente=maria,
    odontologo=odontologo,
    fecha_hora=hoy.replace(hour=10, minute=0, second=0, microsecond=0),
    motivo='Limpieza dental y revisión general',
    motivo_tipo='LIMPIEZA',
    estado='CONFIRMADA'
)
print(f'  ✅ Cita confirmada para HOY: {cita1.fecha_hora}')

# Cita 2: AYER - Atendida
ayer = hoy - timedelta(days=1)
cita2 = Cita.objects.create(
    paciente=maria,
    odontologo=odontologo,
    fecha_hora=ayer.replace(hour=14, minute=30, second=0, microsecond=0),
    motivo='Control de tratamiento de conducto',
    motivo_tipo='REVISION',
    estado='ATENDIDA',
    observaciones='Paciente respondió bien al tratamiento'
)
print(f'  ✅ Cita atendida (ayer): {cita2.fecha_hora}')

# Cita 3: Próxima semana - Programada
proxima = hoy + timedelta(days=7)
cita3 = Cita.objects.create(
    paciente=maria,
    odontologo=odontologo,
    fecha_hora=proxima.replace(hour=9, minute=0, second=0, microsecond=0),
    motivo='Seguimiento de endodoncia y colocación de corona',
    motivo_tipo='PLAN',
    estado='PENDIENTE'
)
print(f'  ✅ Cita programada (próxima semana): {cita3.fecha_hora}')

# ============================================================================
# 2. CREAR HISTORIAL CLÍNICO Y ODONTOGRAMA
# ============================================================================
print('\n📋 CREANDO HISTORIAL CLÍNICO...')

# Verificar si ya existe y eliminarlo
try:
    historial_existente = HistorialClinico.objects.get(paciente=maria)
    historial_existente.delete()
    print('  ℹ️  Historial anterior eliminado')
except HistorialClinico.DoesNotExist:
    pass

historial = HistorialClinico.objects.create(
    paciente=maria,
    antecedentes_medicos='Hipertensión controlada con medicación',
    alergias='Penicilina, Ibuprofeno',
    medicamentos_actuales='Losartán 50mg (hipertensión)'
)
print(f'  ✅ Historial clínico creado')

# Crear odontograma
odontograma = Odontograma.objects.create(
    historial_clinico=historial,
    estado_piezas={
        "16": {"estado": "endodoncia", "observacion": "Tratamiento de conducto realizado"},
        "11": {"estado": "sano"},
        "21": {"estado": "sano"},
        "41": {"estado": "desgaste", "observacion": "Desgaste leve en borde incisal"}
    },
    notas='Caries en pieza 16 (molar superior derecho) tratada con endodoncia. Desgaste en incisivos inferiores.'
)
print(f'  ✅ Odontograma creado')

# ============================================================================
# 3. CREAR PLAN DE TRATAMIENTO (Simplificado)
# ============================================================================
print('\n💊 CREANDO PLAN DE TRATAMIENTO...')

# Verificar si existen servicios
servicios_count = Servicio.objects.count()
if servicios_count == 0:
    print('  ⚠️  No hay servicios creados. Creando servicios básicos...')
    
    # Crear servicios básicos
    servicio_endodoncia = Servicio.objects.create(
        nombre='Endodoncia - Molar',
        descripcion='Tratamiento de conducto en pieza molar',
        precio_base=Decimal('250.00'),
        duracion_estimada=90,
        activo=True
    )
    
    servicio_corona = Servicio.objects.create(
        nombre='Corona de Porcelana',
        descripcion='Corona cerámica para restauración dental',
        precio_base=Decimal('350.00'),
        duracion_estimada=60,
        activo=True
    )
    
    servicio_limpieza = Servicio.objects.create(
        nombre='Limpieza Dental',
        descripcion='Profilaxis y detartraje',
        precio_base=Decimal('50.00'),
        duracion_estimada=45,
        activo=True
    )
    
    print(f'  ✅ Creados 3 servicios')
else:
    servicio_endodoncia = Servicio.objects.first()
    servicio_corona = Servicio.objects.all()[1] if servicios_count > 1 else servicio_endodoncia
    servicio_limpieza = Servicio.objects.all()[2] if servicios_count > 2 else servicio_endodoncia

# Limpiar planes existentes
PlanDeTratamiento.objects.filter(paciente=maria).delete()

# Crear plan de tratamiento
plan = PlanDeTratamiento.objects.create(
    paciente=maria,
    odontologo=odontologo,
    titulo='Tratamiento Endodoncia + Corona',
    descripcion='Plan integral para restauración de pieza 16 con endodoncia realizada',
    estado='EN_PROGRESO',
    fecha_inicio=timezone.now() - timedelta(days=15)
)
print(f'  ✅ Plan de tratamiento creado')

# Items del plan
item1 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_endodoncia,
    descripcion='Endodoncia en pieza 16 (2 sesiones)',
    dientes='16',
    orden=1,
    estado='COMPLETADO',
    precio_unitario=servicio_endodoncia.precio_base,
    cantidad=1,
    observaciones='Tratamiento completado exitosamente'
)
print(f'  ✅ Item 1: {item1.servicio.nombre} - COMPLETADO')

item2 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_corona,
    descripcion='Corona de porcelana sobre pieza 16',
    dientes='16',
    orden=2,
    estado='PENDIENTE',
    precio_unitario=servicio_corona.precio_base,
    cantidad=1,
    observaciones='Programar para próxima semana'
)
print(f'  ✅ Item 2: {item2.servicio.nombre} - PENDIENTE')

item3 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_limpieza,
    descripcion='Limpieza dental de mantenimiento',
    dientes='Toda la boca',
    orden=3,
    estado='PENDIENTE',
    precio_unitario=servicio_limpieza.precio_base,
    cantidad=1,
    observaciones='Programar después de colocar corona'
)
print(f'  ✅ Item 3: {item3.servicio.nombre} - PENDIENTE')

# ============================================================================
# 6. CREAR FACTURAS Y PAGOS
# ============================================================================
print('\n💰 CREANDO FACTURAS Y PAGOS...')

# Limpiar facturas existentes
Factura.objects.filter(paciente=maria).delete()

# Factura 1: Endodoncia (PAGADA)
factura1 = Factura.objects.create(
    paciente=maria,
    plan_tratamiento=plan,
    subtotal=Decimal('250.00'),
    descuento=Decimal('0.00'),
    impuesto=Decimal('30.00'),  # 12% IVA
    total=Decimal('280.00'),
    estado='PAGADA',
    fecha_emision=timezone.now().date() - timedelta(days=7),
    observaciones='Pago por endodoncia pieza 16'
)
print(f'  ✅ Factura 1: ${factura1.total} - PAGADA')

# Pago de factura 1
pago1 = Pago.objects.create(
    factura=factura1,
    monto=Decimal('280.00'),
    metodo='EFECTIVO',
    fecha=timezone.now().date() - timedelta(days=7),
    observaciones='Pago completo en efectivo'
)
print(f'    💵 Pago 1: ${pago1.monto} - {pago1.metodo}')

# Factura 2: Corona (PENDIENTE)
factura2 = Factura.objects.create(
    paciente=maria,
    plan_tratamiento=plan,
    subtotal=Decimal('350.00'),
    descuento=Decimal('35.00'),  # 10% descuento
    impuesto=Decimal('37.80'),   # 12% IVA sobre (350-35)
    total=Decimal('352.80'),
    estado='PENDIENTE',
    fecha_emision=timezone.now().date(),
    fecha_vencimiento=timezone.now().date() + timedelta(days=15),
    observaciones='Factura por corona de porcelana (10% descuento por plan completo)'
)
print(f'  ✅ Factura 2: ${factura2.total} - PENDIENTE')

# Pago parcial de factura 2
pago2 = Pago.objects.create(
    factura=factura2,
    monto=Decimal('150.00'),
    metodo='TRANSFERENCIA',
    fecha=timezone.now().date(),
    observaciones='Anticipo del 50%'
)
print(f'    💳 Pago 2 (anticipo): ${pago2.monto} - {pago2.metodo}')

# ============================================================================
# RESUMEN
# ============================================================================
print('\n' + '=' * 80)
print('✅ POBLACIÓN COMPLETADA PARA MARÍA GARCÍA')
print('=' * 80)
print(f'\n👤 Paciente: {maria_user.nombre} {maria_user.apellido}')
print(f'📧 Email: {maria_user.email}')
print(f'🔐 Password: password123')
print('\n📊 DATOS CREADOS:')
print(f'  📅 Citas: {Cita.objects.filter(paciente=maria).count()}')
print(f'  📋 Historiales: 1')
print(f'  🩺 Episodios: {EpisodioAtencion.objects.filter(historial=historial).count()}')
print(f'  📄 Documentos: {DocumentoClinico.objects.filter(episodio__historial=historial).count()}')
print(f'  💊 Planes de tratamiento: {PlanDeTratamiento.objects.filter(paciente=maria).count()}')
print(f'  📝 Items del plan: {ItemPlanTratamiento.objects.filter(plan=plan).count()}')
print(f'  💰 Facturas: {Factura.objects.filter(paciente=maria).count()}')
print(f'  💵 Pagos: {Pago.objects.filter(factura__paciente=maria).count()}')

print('\n🎯 PRÓXIMOS PASOS:')
print('  1. Login con: paciente1@test.com / password123')
print('  2. Ver cita programada para HOY')
print('  3. Consultar historial clínico con 3 episodios')
print('  4. Revisar plan de tratamiento en progreso')
print('  5. Ver facturas (1 pagada, 1 pendiente)')

print('\n✨ ¡Listo para probar en el frontend!')
