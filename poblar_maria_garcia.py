"""
Script para poblar datos completos de María García (maria.garcia@email.com)
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
    maria_user = Usuario.objects.get(email='maria.garcia@email.com')
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
# 3. CREAR EPISODIOS DE ATENCIÓN (CONSULTAS)
# ============================================================================
print('\n📝 CREANDO EPISODIOS DE ATENCIÓN...')

# Episodio 1: Primera consulta (hace 20 días)
episodio1 = EpisodioAtencion.objects.create(
    historial_clinico=historial,
    odontologo=odontologo,
    motivo_consulta='Dolor intenso en molar superior derecho',
    diagnostico='Caries profunda en pieza 16 con afectación pulpar',
    descripcion_procedimiento='Apertura cameral y preparación para endodoncia. Primera sesión de endodoncia - Conductos limpios.',
    notas_privadas='Paciente presenta dolor moderado. Se prescribe analgésico. Pieza dental: 16'
)
# Actualizar fecha manualmente (auto_now_add impide modificación)
episodio1.fecha_atencion = timezone.now() - timedelta(days=20)
episodio1.save()
print(f'  ✅ Episodio 1: {episodio1.motivo_consulta}')

# Episodio 2: Segunda sesión endodoncia (hace 10 días)
episodio2 = EpisodioAtencion.objects.create(
    historial_clinico=historial,
    odontologo=odontologo,
    motivo_consulta='Control y finalización de endodoncia',
    diagnostico='Endodoncia en proceso - pieza 16',
    descripcion_procedimiento='Obturación de conductos radiculares con gutapercha. Endodoncia completada. Sellado temporal.',
    notas_privadas='Tratamiento exitoso. Programar colocación de corona. Pieza dental: 16'
)
episodio2.fecha_atencion = timezone.now() - timedelta(days=10)
episodio2.save()
print(f'  ✅ Episodio 2: {episodio2.motivo_consulta}')

# Episodio 3: Limpieza dental (hace 5 días)
episodio3 = EpisodioAtencion.objects.create(
    historial_clinico=historial,
    odontologo=odontologo,
    motivo_consulta='Limpieza dental y revisión general',
    diagnostico='Leve acumulación de sarro. Encías sanas.',
    descripcion_procedimiento='Profilaxis completa con ultrasonido y pulido. Limpieza dental profesional completada.',
    notas_privadas='Higiene bucal adecuada. Continuar con cuidado en casa.'
)
episodio3.fecha_atencion = timezone.now() - timedelta(days=5)
episodio3.save()
print(f'  ✅ Episodio 3: {episodio3.motivo_consulta}')

print(f'  📊 Total episodios creados: {EpisodioAtencion.objects.filter(historial_clinico=historial).count()}')

# ============================================================================
# 4. CREAR DOCUMENTOS CLÍNICOS
# ============================================================================
print('\n📄 CREANDO DOCUMENTOS CLÍNICOS...')

# Crear archivo dummy para evitar error de FileField
from django.core.files.base import ContentFile

# Documento 1: Radiografía del episodio 1
doc1 = DocumentoClinico.objects.create(
    historial_clinico=historial,
    episodio=episodio1,
    descripcion='Radiografía periapical de pieza 16 - Diagnóstico inicial',
    tipo_documento='RADIOGRAFIA',
    archivo=ContentFile(b'', name='radiografia_pieza16_inicial.jpg')
)
print(f'  ✅ Documento 1: {doc1.descripcion}')

# Documento 2: Radiografía del episodio 2
doc2 = DocumentoClinico.objects.create(
    historial_clinico=historial,
    episodio=episodio2,
    descripcion='Radiografía post-endodoncia pieza 16',
    tipo_documento='RADIOGRAFIA',
    archivo=ContentFile(b'', name='radiografia_pieza16_post.jpg')
)
print(f'  ✅ Documento 2: {doc2.descripcion}')

# Documento 3: Consentimiento informado
doc3 = DocumentoClinico.objects.create(
    historial_clinico=historial,
    episodio=episodio1,
    descripcion='Consentimiento informado para tratamiento de endodoncia',
    tipo_documento='CONSENTIMIENTO',
    archivo=ContentFile(b'', name='consentimiento_endodoncia.pdf')
)
print(f'  ✅ Documento 3: {doc3.descripcion}')

# Documento 4: Receta médica
doc4 = DocumentoClinico.objects.create(
    historial_clinico=historial,
    episodio=episodio1,
    descripcion='Receta: Ibuprofeno 400mg y Amoxicilina 500mg',
    tipo_documento='RECETA',
    archivo=ContentFile(b'', name='receta_antibioticos.pdf')
)
print(f'  ✅ Documento 4: {doc4.descripcion}')

print(f'  📊 Total documentos creados: {DocumentoClinico.objects.filter(historial_clinico=historial).count()}')

# ============================================================================
# 5. CREAR PLAN DE TRATAMIENTO (Simplificado)
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
    orden=1,
    estado='COMPLETADO',
    precio_servicio_snapshot=servicio_endodoncia.precio_base,
    precio_materiales_fijos_snapshot=Decimal('0.00'),
    precio_insumo_seleccionado_snapshot=Decimal('0.00'),
    notas='Endodoncia en pieza 16 (2 sesiones) - Tratamiento completado exitosamente',
    fecha_realizada=timezone.now() - timedelta(days=10)
)
print(f'  ✅ Item 1: {item1.servicio.nombre} - COMPLETADO')

item2 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_corona,
    orden=2,
    estado='PENDIENTE',
    precio_servicio_snapshot=servicio_corona.precio_base,
    precio_materiales_fijos_snapshot=Decimal('0.00'),
    precio_insumo_seleccionado_snapshot=Decimal('0.00'),
    notas='Corona de porcelana sobre pieza 16 - Programar para próxima semana',
    fecha_estimada=(timezone.now() + timedelta(days=7)).date()
)
print(f'  ✅ Item 2: {item2.servicio.nombre} - PENDIENTE')

item3 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_limpieza,
    orden=3,
    estado='PENDIENTE',
    precio_servicio_snapshot=servicio_limpieza.precio_base,
    precio_materiales_fijos_snapshot=Decimal('0.00'),
    precio_insumo_seleccionado_snapshot=Decimal('0.00'),
    notas='Limpieza dental de mantenimiento en toda la boca - Programar después de colocar corona',
    fecha_estimada=(timezone.now() + timedelta(days=14)).date()
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
    presupuesto=None,
    monto_total=Decimal('280.00'),
    monto_pagado=Decimal('280.00'),
    estado='PAGADA',
    nit_ci='12345678',
    razon_social='María García López'
)
print(f'  ✅ Factura 1: ${factura1.monto_total} - PAGADA')

# Pago de factura 1
pago1 = Pago.objects.create(
    factura=factura1,
    paciente=maria,
    monto_pagado=Decimal('280.00'),
    metodo_pago='EFECTIVO',
    estado_pago='COMPLETADO',
    notas='Pago completo en efectivo'
)
print(f'    💵 Pago 1: ${pago1.monto_pagado} - {pago1.metodo_pago}')

# Factura 2: Corona (PENDIENTE con pago parcial)
factura2 = Factura.objects.create(
    paciente=maria,
    presupuesto=None,
    monto_total=Decimal('352.80'),
    monto_pagado=Decimal('150.00'),
    estado='PENDIENTE',
    nit_ci='12345678',
    razon_social='María García López'
)
print(f'  ✅ Factura 2: ${factura2.monto_total} - PENDIENTE (Pagado: ${factura2.monto_pagado})')

# Pago parcial de factura 2
pago2 = Pago.objects.create(
    factura=factura2,
    paciente=maria,
    monto_pagado=Decimal('150.00'),
    metodo_pago='TRANSFERENCIA',
    estado_pago='COMPLETADO',
    notas='Anticipo del 50%'
)
print(f'    💳 Pago 2 (anticipo): ${pago2.monto_pagado} - {pago2.metodo_pago}')

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
print(f'  🩺 Episodios: {EpisodioAtencion.objects.filter(historial_clinico=historial).count()}')
print(f'  📄 Documentos: {DocumentoClinico.objects.filter(historial_clinico=historial).count()}')
print(f'  💊 Planes de tratamiento: {PlanDeTratamiento.objects.filter(paciente=maria).count()}')
print(f'  📝 Items del plan: {ItemPlanTratamiento.objects.filter(plan=plan).count()}')
print(f'  💰 Facturas: {Factura.objects.filter(paciente=maria).count()}')
print(f'  💵 Pagos: {Pago.objects.filter(factura__paciente=maria).count()}')

print('\n🎯 PRÓXIMOS PASOS:')
print('  1. Login con: maria.garcia@email.com / password123')
print('  2. Ver cita programada para HOY')
print('  3. Consultar historial clínico con 3 episodios y 4 documentos')
print('  4. Revisar plan de tratamiento en progreso')
print('  5. Ver facturas (1 pagada, 1 pendiente)')

print('\n✨ ¡Listo para probar en el frontend!')
