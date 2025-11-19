"""
Script para agregar datos visibles en el dashboard de María García
"""
import os
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import get_tenant_model
from django.db import connection
from usuarios.models import Usuario
from facturacion.models import Factura, Pago
from historial_clinico.models import HistorialClinico, EpisodioAtencion, DocumentoClinico
from django.utils import timezone

# Conectar al tenant
print("\n🔄 Conectando al tenant clinica_demo...")
Tenant = get_tenant_model()
tenant = Tenant.objects.get(schema_name='clinica_demo')
connection.set_tenant(tenant)
print(f"✅ Conectado al tenant: {tenant.schema_name}\n")

# Obtener usuarios
maria = Usuario.objects.get(email='paciente1@test.com')
paciente_maria = maria.perfil_paciente
dr_juan = Usuario.objects.get(email='odontologo@clinica-demo.com')
odontologo_juan = dr_juan.perfil_odontologo

print("="*70)
print("💰 AGREGANDO FACTURAS")
print("="*70)

# Factura 1: Limpieza (Pagada completamente)
factura1, created = Factura.objects.get_or_create(
    paciente=paciente_maria,
    monto_total=Decimal('60.00'),
    estado='PAGADA',
    defaults={
        'fecha_emision': timezone.now() - timedelta(days=90),
        'monto_pagado': Decimal('60.00'),
        'nit_ci': maria.ci,
        'razon_social': f'{maria.nombre} {maria.apellido}'
    }
)

if created:
    # Actualizar fecha_emision manualmente porque auto_now_add no permite override
    factura1.fecha_emision = timezone.now() - timedelta(days=90)
    factura1.save()
    
    pago1 = Pago.objects.create(
        factura=factura1,
        paciente=paciente_maria,
        monto_pagado=Decimal('60.00'),
        metodo_pago='EFECTIVO',
        estado_pago='COMPLETADO',
        notas='Pago completo al momento del servicio - Limpieza dental'
    )
    pago1.fecha_pago = timezone.now() - timedelta(days=90)
    pago1.save()
    print("✅ Factura 1 creada: Limpieza dental - PAGADA ($60)")

# Factura 2: Endodoncia (Pago parcial - DEUDA)
factura2, created = Factura.objects.get_or_create(
    paciente=paciente_maria,
    monto_total=Decimal('250.00'),
    estado='PENDIENTE',
    monto_pagado=Decimal('150.00'),
    defaults={
        'nit_ci': maria.ci,
        'razon_social': f'{maria.nombre} {maria.apellido}'
    }
)

if created:
    factura2.fecha_emision = timezone.now() - timedelta(days=60)
    factura2.save()
    
    pago2 = Pago.objects.create(
        factura=factura2,
        paciente=paciente_maria,
        monto_pagado=Decimal('150.00'),
        metodo_pago='TARJETA',
        estado_pago='COMPLETADO',
        notas='Pago inicial del 60% - Endodoncia pieza 16'
    )
    pago2.fecha_pago = timezone.now() - timedelta(days=60)
    pago2.save()
    print("✅ Factura 2 creada: Endodoncia - PENDIENTE ($150 de $250) - DEUDA: $100")

# Factura 3: Corona (Pendiente - DEUDA COMPLETA)
factura3, created = Factura.objects.get_or_create(
    paciente=paciente_maria,
    monto_total=Decimal('350.00'),
    estado='PENDIENTE',
    monto_pagado=Decimal('0.00'),
    defaults={
        'nit_ci': maria.ci,
        'razon_social': f'{maria.nombre} {maria.apellido}'
    }
)

if created:
    factura3.fecha_emision = timezone.now() - timedelta(days=15)
    factura3.save()
    print("✅ Factura 3 creada: Corona - PENDIENTE ($350) - DEUDA: $350")

print("\n="*70)
print("📋 AGREGANDO EPISODIOS DE ATENCIÓN")
print("="*70)

historial = HistorialClinico.objects.get(paciente=paciente_maria)

episodios_data = [
    {
        'fecha': timezone.now() - timedelta(days=90),
        'motivo': 'Control de rutina y limpieza dental',
        'diagnostico': 'Estado general bueno. Caries en pieza 25 detectada.',
        'procedimiento': 'Limpieza dental completa, aplicación de flúor, evaluación general.'
    },
    {
        'fecha': timezone.now() - timedelta(days=60),
        'motivo': 'Dolor en pieza 16',
        'diagnostico': 'Pulpitis irreversible en pieza 16',
        'procedimiento': 'Endodoncia pieza 16 - Primera fase: apertura cameral y limpieza de conductos'
    },
    {
        'fecha': timezone.now() - timedelta(days=45),
        'motivo': 'Continuación de endodoncia',
        'diagnostico': 'Conductos instrumentados correctamente',
        'procedimiento': 'Endodoncia pieza 16 - Obturación definitiva de conductos'
    },
    {
        'fecha': timezone.now() - timedelta(days=15),
        'motivo': 'Preparación para corona',
        'diagnostico': 'Pieza 16 apta para rehabilitación protésica',
        'procedimiento': 'Toma de impresiones para corona. Corona en fabricación.'
    },
]

episodios_creados = 0
for ep_data in episodios_data:
    episodio, created = EpisodioAtencion.objects.get_or_create(
        historial_clinico=historial,
        odontologo=odontologo_juan,
        fecha_atencion=ep_data['fecha'],
        motivo_consulta=ep_data['motivo'],
        defaults={
            'diagnostico': ep_data['diagnostico'],
            'descripcion_procedimiento': ep_data['procedimiento']
        }
    )
    if created:
        episodios_creados += 1

print(f"✅ Episodios creados: {episodios_creados}")

print("\n="*70)
print("✅ RESUMEN DE DATOS AGREGADOS")
print("="*70)

total_facturas = Factura.objects.filter(paciente=paciente_maria).count()
facturas = Factura.objects.filter(paciente=paciente_maria)
saldo_pendiente = sum([f.monto_total - f.monto_pagado for f in facturas])

print(f"""
💰 FACTURACIÓN:
   • Total facturas: {total_facturas}
   • Facturas pagadas: {Factura.objects.filter(paciente=paciente_maria, estado='PAGADA').count()}
   • Facturas pendientes: {Factura.objects.filter(paciente=paciente_maria, estado='PENDIENTE').count()}
   • SALDO PENDIENTE: ${saldo_pendiente:.2f}

📋 HISTORIAL CLÍNICO:
   • Episodios de atención: {EpisodioAtencion.objects.filter(historial_clinico=historial).count()}

🎯 ESTADO: Dashboard ahora mostrará:
   ✅ Saldo pendiente: ${saldo_pendiente:.2f}
   ✅ {total_facturas} facturas registradas
   ✅ {EpisodioAtencion.objects.filter(historial_clinico=historial).count()} episodios de atención
""")

print("="*70)
print("🎉 ¡Datos agregados exitosamente!")
print("="*70)
print("\n💡 Recarga el navegador (F5) para ver los cambios\n")
