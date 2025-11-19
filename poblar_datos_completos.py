"""
Script para poblar TODOS los módulos con datos completos para María García
Ejecutar: python poblar_datos_completos.py
"""

import os
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_tenant_model
from usuarios.models import Usuario
from agenda.models import Cita
from tratamientos.models import (
    Servicio, PlanDeTratamiento, ItemPlanTratamiento,
    Presupuesto, ItemPresupuesto, CategoriaServicio
)
from historial_clinico.models import (
    HistorialClinico, EpisodioAtencion, Odontograma,
    DocumentoClinico
)
from inventario.models import (
    Insumo, CategoriaInsumo
)
from facturacion.models import Factura, Pago

# Obtener el tenant clinica_demo
print("\n🔄 Conectando al tenant clinica_demo...")
Tenant = get_tenant_model()
try:
    tenant = Tenant.objects.get(schema_name='clinica_demo')
    connection.set_tenant(tenant)
    print(f"✅ Conectado al tenant: {tenant.schema_name}\n")
except Tenant.DoesNotExist:
    print("❌ ERROR: Tenant 'clinica_demo' no existe")
    exit(1)

print("\n" + "="*70)
print("🚀 POBLANDO DATOS COMPLETOS PARA MARÍA GARCÍA")
print("="*70 + "\n")

# ============================================================================
# 1. OBTENER USUARIOS Y PERFILES
# ============================================================================
print("📋 1. Obteniendo usuarios...")
try:
    maria = Usuario.objects.get(email='paciente1@test.com')
    paciente_maria = maria.perfil_paciente
    print(f"   ✅ Paciente: {maria.nombre} {maria.apellido}")
except Usuario.DoesNotExist:
    print("   ❌ ERROR: paciente1@test.com no existe")
    exit(1)

try:
    dr_juan = Usuario.objects.get(email='odontologo@clinica-demo.com')
    odontologo_juan = dr_juan.perfil_odontologo
    print(f"   ✅ Odontólogo: {dr_juan.nombre} {dr_juan.apellido}")
except Usuario.DoesNotExist:
    print("   ❌ ERROR: odontologo@clinica-demo.com no existe")
    exit(1)

# ============================================================================
# 2. HISTORIAL CLÍNICO (si no existe)
# ============================================================================
print("\n📋 2. Creando/Verificando Historial Clínico...")
historial, created = HistorialClinico.objects.get_or_create(
    paciente=paciente_maria,
    defaults={
        'alergias': 'Penicilina, Polen',
        'medicamentos_actuales': 'Ibuprofeno 400mg (ocasional), Loratadina 10mg',
        'antecedentes_familiares': 'Diabetes tipo 2 (madre), Hipertensión (padre)',
        'observaciones_generales': 'Paciente colaboradora, buena higiene oral'
    }
)
if created:
    print(f"   ✅ Historial clínico creado (Paciente: {historial.paciente_id})")
else:
    print(f"   ℹ️  Historial clínico ya existía (Paciente: {historial.paciente_id})")

# ============================================================================
# 3. ODONTOGRAMA (si no existe)
# ============================================================================
print("\n📋 3. Creando/Verificando Odontograma...")
odontograma, created = Odontograma.objects.get_or_create(
    historial_clinico=historial,
    defaults={
        'estado_piezas': {
            "11": {"estado": "sano"},
            "12": {"estado": "sano"},
            "13": {"estado": "sano"},
            "14": {"estado": "obturado"},
            "15": {"estado": "sano"},
            "16": {"estado": "endodoncia"},
            "17": {"estado": "sano"},
            "18": {"estado": "ausente"},
            "21": {"estado": "sano"},
            "22": {"estado": "sano"},
            "23": {"estado": "sano"},
            "24": {"estado": "sano"},
            "25": {"estado": "caries"},
            "26": {"estado": "obturado"},
            "27": {"estado": "sano"},
            "28": {"estado": "ausente"},
            "31": {"estado": "sano"},
            "32": {"estado": "sano"},
            "33": {"estado": "sano"},
            "34": {"estado": "obturado"},
            "35": {"estado": "sano"},
            "36": {"estado": "extraccion"},
            "37": {"estado": "sano"},
            "38": {"estado": "ausente"},
            "41": {"estado": "sano"},
            "42": {"estado": "sano"},
            "43": {"estado": "sano"},
            "44": {"estado": "sano"},
            "45": {"estado": "sano"},
            "46": {"estado": "corona"},
            "47": {"estado": "sano"},
            "48": {"estado": "retenido"}
        }
    }
)
if created:
    print(f"   ✅ Odontograma creado (ID: {odontograma.id})")
else:
    print(f"   ℹ️  Odontograma ya existía (ID: {odontograma.id})")

# ============================================================================
# 4. EPISODIOS DE ATENCIÓN
# ============================================================================
print("\n📋 4. Creando Episodios de Atención...")
episodios_data = [
    {
        'fecha': datetime.now() - timedelta(days=90),
        'tipo': 'consulta_general',
        'motivo': 'Control de rutina y limpieza',
        'diagnostico': 'Estado general bueno, caries en pieza 25',
        'tratamiento_realizado': 'Limpieza dental completa, aplicación de flúor',
        'observaciones': 'Recomendar revisión en 3 meses'
    },
    {
        'fecha': datetime.now() - timedelta(days=60),
        'tipo': 'tratamiento',
        'motivo': 'Dolor en pieza 16',
        'diagnostico': 'Pulpitis irreversible en pieza 16',
        'tratamiento_realizado': 'Endodoncia pieza 16 - Primera sesión',
        'observaciones': 'Paciente toleró bien el procedimiento'
    },
    {
        'fecha': datetime.now() - timedelta(days=45),
        'tipo': 'tratamiento',
        'motivo': 'Continuación endodoncia',
        'diagnostico': 'Conductos instrumentados y obturados',
        'tratamiento_realizado': 'Endodoncia pieza 16 - Obturación definitiva',
        'observaciones': 'Recomendar corona en 2 semanas'
    },
    {
        'fecha': datetime.now() - timedelta(days=15),
        'tipo': 'tratamiento',
        'motivo': 'Colocación de corona',
        'diagnostico': 'Pieza 16 apta para corona',
        'tratamiento_realizado': 'Toma de impresiones para corona',
        'observaciones': 'Corona lista en 1 semana'
    },
]

episodios_creados = 0
for ep_data in episodios_data:
    episodio, created = EpisodioAtencion.objects.get_or_create(
        historial_clinico=historial,
        odontologo=odontologo_juan,
        fecha_atencion=ep_data['fecha'],
        defaults={
            'tipo_atencion': ep_data['tipo'],
            'motivo_consulta': ep_data['motivo'],
            'diagnostico': ep_data['diagnostico'],
            'tratamiento_realizado': ep_data['tratamiento_realizado'],
            'observaciones': ep_data['observaciones']
        }
    )
    if created:
        episodios_creados += 1

print(f"   ✅ Episodios creados: {episodios_creados}")
print(f"   ℹ️  Total episodios: {EpisodioAtencion.objects.filter(historial_clinico=historial).count()}")

# ============================================================================
# 5. DOCUMENTOS CLÍNICOS
# ============================================================================
print("\n📋 5. Creando Documentos Clínicos...")

documentos_data = [
    {
        'tipo': 'consentimiento_informado',
        'titulo': 'Consentimiento Informado - Endodoncia',
        'contenido': 'Autorización para tratamiento de conducto pieza 16',
        'fecha': datetime.now() - timedelta(days=60)
    },
    {
        'tipo': 'receta_medica',
        'titulo': 'Receta - Analgésicos post-endodoncia',
        'contenido': 'Ibuprofeno 400mg cada 8 horas por 3 días',
        'fecha': datetime.now() - timedelta(days=45)
    },
    {
        'tipo': 'orden_laboratorio',
        'titulo': 'Orden - Corona Pieza 16',
        'contenido': 'Corona de porcelana sobre metal',
        'fecha': datetime.now() - timedelta(days=15)
    },
]

docs_creados = 0
for doc_data in documentos_data:
    doc, created = DocumentoClinico.objects.get_or_create(
        historial_clinico=historial,
        tipo_documento=doc_data['tipo'],
        titulo=doc_data['titulo'],
        defaults={
            'contenido': doc_data['contenido'],
            'fecha_documento': doc_data['fecha']
        }
    )
    if created:
        docs_creados += 1

print(f"   ✅ Documentos creados: {docs_creados}")

# ============================================================================
# 6. SERVICIOS CATÁLOGO
# ============================================================================
print("\n📋 6. Verificando Catálogo de Servicios...")

# Primero crear categorías
categorias_servicio = [
    {'codigo': 'ENDO', 'nombre': 'Endodoncia'},
    {'codigo': 'PROT', 'nombre': 'Prótesis'},
    {'codigo': 'OPER', 'nombre': 'Operatoria'},
    {'codigo': 'PREV', 'nombre': 'Prevención'},
    {'codigo': 'CIRU', 'nombre': 'Cirugía'},
]

for cat_data in categorias_servicio:
    CategoriaServicio.objects.get_or_create(
        codigo=cat_data['codigo'],
        defaults={'nombre': cat_data['nombre']}
    )

servicios_catalogo = [
    {'codigo': 'ENDO-001', 'nombre': 'Endodoncia Unirradicular', 'precio': 250.00, 'categoria_cod': 'ENDO'},
    {'codigo': 'ENDO-002', 'nombre': 'Endodoncia Birradicular', 'precio': 350.00, 'categoria_cod': 'ENDO'},
    {'codigo': 'CORONA-002', 'nombre': 'Corona Metal-Porcelana', 'precio': 350.00, 'categoria_cod': 'PROT'},
    {'codigo': 'OBTU-002', 'nombre': 'Obturación Compuesta', 'precio': 120.00, 'categoria_cod': 'OPER'},
    {'codigo': 'LIMPIEZA-001', 'nombre': 'Limpieza Dental', 'precio': 60.00, 'categoria_cod': 'PREV'},
]

servs_creados = 0
for serv_data in servicios_catalogo:
    categoria = CategoriaServicio.objects.get(codigo=serv_data['categoria_cod'])
    serv, created = Servicio.objects.get_or_create(
        codigo=serv_data['codigo'],
        defaults={
            'nombre': serv_data['nombre'],
            'precio_base': Decimal(str(serv_data['precio'])),
            'categoria': categoria,
            'descripcion': f"Servicio de {serv_data['nombre']}",
            'duracion_estimada_minutos': 60,
            'activo': True
        }
    )
    if created:
        servs_creados += 1

print(f"   ✅ Servicios creados: {servs_creados}")
print(f"   ℹ️  Total catálogo: {Servicio.objects.filter(activo=True).count()}")

# ============================================================================
# 7. PLAN DE TRATAMIENTO
# ============================================================================
print("\n📋 7. Creando Plan de Tratamiento...")

plan, created = PlanDeTratamiento.objects.get_or_create(
    paciente=paciente_maria,
    odontologo=odontologo_juan,
    titulo='Tratamiento Integral - Endodoncia y Rehabilitación',
    defaults={
        'descripcion': 'Plan completo: endodoncia pieza 16, corona, obturación pieza 25',
        'estado': 'EN_PROGRESO',
        'fecha_inicio': date.today() - timedelta(days=60),
        'observaciones': 'Paciente con buena respuesta al tratamiento'
    }
)

if created:
    print(f"   ✅ Plan creado (ID: {plan.id})")
    
    # Items del plan
    items_plan = [
        {
            'servicio_codigo': 'ENDO-001',
            'pieza': '16',
            'descripcion': 'Endodoncia pieza 16',
            'estado': 'completado',
            'prioridad': 1,
            'orden': 1
        },
        {
            'servicio_codigo': 'CORONA-002',
            'pieza': '16',
            'descripcion': 'Corona metal-porcelana pieza 16',
            'estado': 'en_progreso',
            'prioridad': 1,
            'orden': 2
        },
        {
            'servicio_codigo': 'OBTU-002',
            'pieza': '25',
            'descripcion': 'Obturación compuesta pieza 25',
            'estado': 'pendiente',
            'prioridad': 2,
            'orden': 3
        },
    ]
    
    items_creados = 0
    for item_data in items_plan:
        servicio = Servicio.objects.get(codigo=item_data['servicio_codigo'])
        item, created_item = ItemPlanTratamiento.objects.get_or_create(
            plan=plan,
            servicio=servicio,
            defaults={
                'pieza_dental': item_data['pieza'],
                'descripcion_personalizada': item_data['descripcion'],
                'estado': item_data['estado'],
                'prioridad': item_data['prioridad'],
                'orden_ejecucion': item_data['orden'],
                'precio_servicio': servicio.precio_base
            }
        )
        if created_item:
            items_creados += 1
    
    print(f"   ✅ Items del plan creados: {items_creados}")
else:
    print(f"   ℹ️  Plan ya existía (ID: {plan.id})")

# ============================================================================
# 8. PRESUPUESTO
# ============================================================================
print("\n📋 8. Creando Presupuesto...")

presupuesto, created = Presupuesto.objects.get_or_create(
    paciente=paciente_maria,
    odontologo=odontologo_juan,
    titulo='Presupuesto - Tratamiento Integral',
    defaults={
        'descripcion': 'Presupuesto para endodoncia, corona y obturación',
        'estado': 'aceptado',
        'fecha_validez': date.today() + timedelta(days=30),
        'observaciones': 'Presupuesto aceptado por paciente',
        'monto_total': Decimal('850.00'),
        'descuento': Decimal('50.00'),
        'monto_final': Decimal('800.00')
    }
)

if created:
    print(f"   ✅ Presupuesto creado (ID: {presupuesto.id})")
    
    # Items del presupuesto
    items_presupuesto = [
        {'codigo': 'ENDO-001', 'pieza': '16', 'cantidad': 1},
        {'codigo': 'CORONA-002', 'pieza': '16', 'cantidad': 1},
        {'codigo': 'OBTU-002', 'pieza': '25', 'cantidad': 1},
    ]
    
    for item_data in items_presupuesto:
        servicio = Servicio.objects.get(codigo=item_data['codigo'])
        ItemPresupuesto.objects.get_or_create(
            presupuesto=presupuesto,
            servicio=servicio,
            defaults={
                'pieza_dental': item_data['pieza'],
                'cantidad': item_data['cantidad'],
                'precio_unitario': servicio.precio_base,
                'subtotal': servicio.precio_base * item_data['cantidad']
            }
        )
    
    print(f"   ✅ Items de presupuesto creados")
else:
    print(f"   ℹ️  Presupuesto ya existía (ID: {presupuesto.id})")

# ============================================================================
# 9. CITAS
# ============================================================================
print("\n📋 9. Creando Citas...")

citas_data = [
    {
        'fecha': datetime.now() - timedelta(days=90, hours=-9),  # Pasada
        'estado': 'ATENDIDA',
        'motivo_tipo': 'consulta_general',
        'motivo': 'Control y limpieza dental',
        'observaciones': 'Limpieza realizada satisfactoriamente'
    },
    {
        'fecha': datetime.now() - timedelta(days=60, hours=-10),  # Pasada
        'estado': 'ATENDIDA',
        'motivo_tipo': 'tratamiento',
        'motivo': 'Endodoncia pieza 16 - Primera sesión',
        'observaciones': 'Primera fase completada'
    },
    {
        'fecha': datetime.now() - timedelta(days=45, hours=-9),  # Pasada
        'estado': 'ATENDIDA',
        'motivo_tipo': 'tratamiento',
        'motivo': 'Endodoncia pieza 16 - Obturación',
        'observaciones': 'Endodoncia completada'
    },
    {
        'fecha': datetime.now() - timedelta(days=15, hours=-10),  # Pasada
        'estado': 'ATENDIDA',
        'motivo_tipo': 'tratamiento',
        'motivo': 'Toma de impresiones para corona',
        'observaciones': 'Impresiones tomadas'
    },
    {
        'fecha': datetime.now() + timedelta(days=7, hours=9),  # Próxima
        'estado': 'CONFIRMADA',
        'motivo_tipo': 'tratamiento',
        'motivo': 'Colocación de corona pieza 16',
        'observaciones': 'Corona lista para instalación'
    },
    {
        'fecha': datetime.now() + timedelta(days=30, hours=14),  # Futura
        'estado': 'PENDIENTE',
        'motivo_tipo': 'tratamiento',
        'motivo': 'Obturación pieza 25',
        'observaciones': 'Tratamiento de caries'
    },
]

citas_creadas = 0
for cita_data in citas_data:
    cita, created = Cita.objects.get_or_create(
        paciente=paciente_maria,
        odontologo=odontologo_juan,
        fecha_hora=cita_data['fecha'],
        defaults={
            'estado': cita_data['estado'],
            'motivo_tipo': cita_data['motivo_tipo'],
            'motivo': cita_data['motivo'],
            'observaciones': cita_data['observaciones']
        }
    )
    if created:
        citas_creadas += 1

print(f"   ✅ Citas creadas: {citas_creadas}")
print(f"   ℹ️  Total citas: {Cita.objects.filter(paciente=paciente_maria).count()}")

# ============================================================================
# 10. INVENTARIO - CATEGORÍAS E INSUMOS
# ============================================================================
print("\n📋 10. Creando Inventario...")

categorias_data = [
    {'codigo': 'INST', 'nombre': 'Instrumental', 'descripcion': 'Instrumental odontológico'},
    {'codigo': 'ENDO', 'nombre': 'Materiales Endodoncia', 'descripcion': 'Materiales para tratamientos de conducto'},
    {'codigo': 'OBTU', 'nombre': 'Materiales Obturación', 'descripcion': 'Resinas y materiales de relleno'},
    {'codigo': 'ANES', 'nombre': 'Anestésicos', 'descripcion': 'Anestésicos locales'},
    {'codigo': 'DESI', 'nombre': 'Desinfectantes', 'descripcion': 'Productos de desinfección'},
]

cats_creadas = 0
for cat_data in categorias_data:
    cat, created = CategoriaInsumo.objects.get_or_create(
        codigo=cat_data['codigo'],
        nombre=cat_data['nombre'],
        defaults={'descripcion': cat_data['descripcion']}
    )
    if created:
        cats_creadas += 1

print(f"   ✅ Categorías creadas: {cats_creadas}")

# Insumos
insumos_data = [
    {
        'codigo': 'INSU-001',
        'nombre': 'Limas Endodónticas Set',
        'categoria_cod': 'ENDO',
        'stock': 25,
        'stock_minimo': 10,
        'precio': 15.00
    },
    {
        'codigo': 'INSU-002',
        'nombre': 'Gutapercha Puntas',
        'categoria_cod': 'ENDO',
        'stock': 100,
        'stock_minimo': 30,
        'precio': 0.50
    },
    {
        'codigo': 'INSU-003',
        'nombre': 'Resina Compuesta A2',
        'categoria_cod': 'OBTU',
        'stock': 15,
        'stock_minimo': 5,
        'precio': 35.00
    },
    {
        'codigo': 'INSU-004',
        'nombre': 'Lidocaína 2% con Epinefrina',
        'categoria_cod': 'ANES',
        'stock': 50,
        'stock_minimo': 20,
        'precio': 2.00
    },
    {
        'codigo': 'INSU-005',
        'nombre': 'Alcohol 70%',
        'categoria_cod': 'DESI',
        'stock': 30,
        'stock_minimo': 10,
        'precio': 5.00
    },
]

insumos_creados = 0
for insu_data in insumos_data:
    categoria = CategoriaInsumo.objects.get(codigo=insu_data['categoria_cod'])
    insu, created = Insumo.objects.get_or_create(
        codigo=insu_data['codigo'],
        defaults={
            'nombre': insu_data['nombre'],
            'categoria': categoria,
            'stock_actual': insu_data['stock'],
            'stock_minimo': insu_data['stock_minimo'],
            'precio_unitario': Decimal(str(insu_data['precio'])),
            'unidad_medida': 'unidad'
        }
    )
    if created:
        insumos_creados += 1

print(f"   ✅ Insumos creados: {insumos_creados}")

# ============================================================================
# 11. FACTURAS Y PAGOS
# ============================================================================
print("\n📋 11. Creando Facturas y Pagos...")

# Factura 1: Limpieza (Pagada)
factura1, created1 = Factura.objects.get_or_create(
    paciente=paciente_maria,
    fecha_emision=date.today() - timedelta(days=90),
    defaults={
        'numero_factura': f'F-{date.today().year}-001',
        'concepto': 'Limpieza dental',
        'monto_total': Decimal('60.00'),
        'monto_pagado': Decimal('60.00'),
        'estado': 'pagada',
        'fecha_vencimiento': date.today() - timedelta(days=60)
    }
)

if created1:
    # Pago completo
    Pago.objects.create(
        factura=factura1,
        monto=Decimal('60.00'),
        metodo_pago='efectivo',
        fecha_pago=date.today() - timedelta(days=90),
        observaciones='Pago al momento del servicio'
    )
    print(f"   ✅ Factura 1 creada y pagada (ID: {factura1.id})")

# Factura 2: Endodoncia (Pagada parcialmente)
factura2, created2 = Factura.objects.get_or_create(
    paciente=paciente_maria,
    fecha_emision=date.today() - timedelta(days=60),
    defaults={
        'numero_factura': f'F-{date.today().year}-002',
        'concepto': 'Endodoncia pieza 16',
        'monto_total': Decimal('250.00'),
        'monto_pagado': Decimal('150.00'),
        'estado': 'parcial',
        'fecha_vencimiento': date.today() + timedelta(days=30)
    }
)

if created2:
    # Pago inicial
    Pago.objects.create(
        factura=factura2,
        monto=Decimal('150.00'),
        metodo_pago='tarjeta',
        fecha_pago=date.today() - timedelta(days=60),
        observaciones='Pago inicial 60%'
    )
    print(f"   ✅ Factura 2 creada con pago parcial (ID: {factura2.id})")

# Factura 3: Corona (Pendiente)
factura3, created3 = Factura.objects.get_or_create(
    paciente=paciente_maria,
    fecha_emision=date.today() - timedelta(days=15),
    defaults={
        'numero_factura': f'F-{date.today().year}-003',
        'concepto': 'Corona metal-porcelana pieza 16',
        'monto_total': Decimal('350.00'),
        'monto_pagado': Decimal('0.00'),
        'estado': 'pendiente',
        'fecha_vencimiento': date.today() + timedelta(days=30)
    }
)

if created3:
    print(f"   ✅ Factura 3 creada (pendiente de pago) (ID: {factura3.id})")

total_facturas = Factura.objects.filter(paciente=paciente_maria).count()
total_pagos = Pago.objects.filter(factura__paciente=paciente_maria).count()
print(f"   ℹ️  Total facturas: {total_facturas}")
print(f"   ℹ️  Total pagos: {total_pagos}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*70)
print("✅ POBLADO COMPLETO FINALIZADO")
print("="*70)

print(f"""
📊 RESUMEN DE DATOS CREADOS PARA {maria.nombre} {maria.apellido}:

📋 HISTORIAL CLÍNICO:
   • Historial: {HistorialClinico.objects.filter(paciente=paciente_maria).count()}
   • Episodios: {EpisodioAtencion.objects.filter(historial_clinico=historial).count()}
   • Odontograma: {Odontograma.objects.filter(historial_clinico=historial).count()}
   • Documentos: {DocumentoClinico.objects.filter(historial_clinico=historial).count()}

🦷 TRATAMIENTOS:
   • Planes: {PlanDeTratamiento.objects.filter(paciente=paciente_maria).count()}
   • Items de plan: {ItemPlanTratamiento.objects.filter(plan__paciente=paciente_maria).count()}
   • Presupuestos: {Presupuesto.objects.filter(paciente=paciente_maria).count()}

📅 AGENDA:
   • Total citas: {Cita.objects.filter(paciente=paciente_maria).count()}
   • Atendidas: {Cita.objects.filter(paciente=paciente_maria, estado='ATENDIDA').count()}
   • Próximas: {Cita.objects.filter(paciente=paciente_maria, estado__in=['PENDIENTE', 'CONFIRMADA']).count()}

💰 FACTURACIÓN:
   • Facturas: {Factura.objects.filter(paciente=paciente_maria).count()}
   • Pagos: {Pago.objects.filter(factura__paciente=paciente_maria).count()}
   • Saldo pendiente: ${Decimal('450.00'):.2f}

📦 INVENTARIO (Sistema):
   • Categorías: {CategoriaInsumo.objects.count()}
   • Insumos: {Insumo.objects.count()}

🔑 CREDENCIALES:
   • Email: {maria.email}
   • Password: password123
""")

print("="*70)
print("🎉 ¡Dashboard listo para pruebas completas!")
print("="*70 + "\n")
