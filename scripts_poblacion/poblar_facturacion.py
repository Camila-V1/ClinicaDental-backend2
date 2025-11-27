"""
Módulo para poblar facturación y pagos
NOTA: El sistema real requiere Presupuestos aprobados para generar facturas.
Este módulo crea pagos directos a citas como workaround para demostración.
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random


def poblar_facturacion(pacientes, citas_atendidas):
    """
    Crea facturas y pagos para citas atendidas
    
    Args:
        pacientes: Lista de PerfilPaciente
        citas_atendidas: Lista de Cita atendidas
    
    Returns:
        tuple: (facturas_creadas, pagos_creados)
    """
    from facturacion.models import Factura, Pago
    
    print("\n=== POBLANDO FACTURACIÓN Y PAGOS ===")
    
    facturas_creadas = []
    pagos_creados = []
    
    # Métodos de pago disponibles
    metodos_pago = ['EFECTIVO', 'TARJETA', 'TRANSFERENCIA', 'QR']
    
    # =========================================================================
    # CREAR FACTURAS Y PAGOS PARA CITAS ATENDIDAS
    # =========================================================================
    print("\n1. Creando facturas y pagos para citas atendidas...")
    
    for cita in citas_atendidas[:15]:  # Primeras 15 citas atendidas
        # Obtener precio de la cita según su tipo
        monto = cita.precio
        
        # Solo crear factura y pago si tiene costo
        if monto > 0:
            # Crear factura
            factura = Factura.objects.create(
                paciente=cita.paciente,
                nit_ci=cita.paciente.usuario.ci or '0',
                razon_social=f"{cita.paciente.usuario.nombre} {cita.paciente.usuario.apellido}",
                monto_total=monto,
                monto_pagado=monto,
                estado='PAGADA',
                fecha_emision=cita.fecha_hora.date()
            )
            
            facturas_creadas.append(factura)
            
            # Crear pago vinculado a la factura
            metodo = random.choice(metodos_pago)
            
            pago = Pago.objects.create(
                tipo_pago='CITA',
                cita=cita,
                factura=factura,
                paciente=cita.paciente,
                monto_pagado=monto,
                metodo_pago=metodo,
                estado_pago='COMPLETADO',
                fecha_pago=cita.fecha_hora,
                fecha_completado=cita.fecha_hora,
                descripcion=f'Pago de cita - {cita.get_motivo_tipo_display()}',
                referencia_transaccion=f'REF-{cita.id}-{random.randint(1000, 9999)}'
            )
            
            pagos_creados.append(pago)
    
    print(f"   ✓ {len(facturas_creadas)} facturas creadas")
    print(f"   ✓ {len(pagos_creados)} pagos completados creados")
    
    # =========================================================================
    # ALGUNAS FACTURAS PENDIENTES
    # =========================================================================
    print("\n2. Creando algunas facturas pendientes...")
    
    # Tomar algunas citas futuras y crear facturas pendientes
    from agenda.models import Cita
    citas_futuras = Cita.objects.filter(
        estado='CONFIRMADA'
    )[:5]
    
    for cita in citas_futuras:
        monto = cita.precio
        
        if monto > 0:
            # Crear factura pendiente
            factura = Factura.objects.create(
                paciente=cita.paciente,
                nit_ci=cita.paciente.usuario.ci or '0',
                razon_social=f"{cita.paciente.usuario.nombre} {cita.paciente.usuario.apellido}",
                monto_total=monto,
                monto_pagado=Decimal('0.00'),
                estado='PENDIENTE',
                fecha_emision=timezone.now().date()
            )
            
            facturas_creadas.append(factura)
            
            # Crear pago pendiente vinculado
            metodo = random.choice(metodos_pago)
            
            pago = Pago.objects.create(
                tipo_pago='CITA',
                cita=cita,
                factura=factura,
                paciente=cita.paciente,
                monto_pagado=monto,
                metodo_pago=metodo,
                estado_pago='PENDIENTE',
                descripcion=f'Pago pendiente - {cita.get_motivo_tipo_display()}',
                referencia_transaccion=f'PEND-{cita.id}-{random.randint(1000, 9999)}'
            )
            
            pagos_creados.append(pago)
    
    print(f"   ✓ {len([p for p in pagos_creados if p.estado_pago == 'PENDIENTE'])} pagos pendientes")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    total_facturas = Factura.objects.count()
    total_pagos = Pago.objects.count()
    
    # Calcular estadísticas de facturas
    facturas_pagadas = Factura.objects.filter(estado='PAGADA').count()
    facturas_pendientes = Factura.objects.filter(estado='PENDIENTE').count()
    
    # Calcular estadísticas de pagos
    pagos_completados = Pago.objects.filter(estado_pago='COMPLETADO').count()
    pagos_pendientes = Pago.objects.filter(estado_pago='PENDIENTE').count()
    
    total_cobrado = sum(
        p.monto_pagado for p in Pago.objects.filter(estado_pago='COMPLETADO')
    )
    total_por_cobrar = sum(
        p.monto_pagado for p in Pago.objects.filter(estado_pago='PENDIENTE')
    )
    
    print("\n=== RESUMEN FACTURACIÓN ===")
    print(f"Facturas totales: {total_facturas}")
    print(f"  - Pagadas: {facturas_pagadas}")
    print(f"  - Pendientes: {facturas_pendientes}")
    print(f"\nPagos totales: {total_pagos}")
    print(f"  - Completados: {pagos_completados}")
    print(f"  - Pendientes: {pagos_pendientes}")
    print(f"\nTotal cobrado: Bs. {total_cobrado:,.2f}")
    print(f"Total por cobrar: Bs. {total_por_cobrar:,.2f}")
    
    # Distribución de métodos de pago
    print("\nMétodos de pago utilizados:")
    for metodo in metodos_pago:
        count = Pago.objects.filter(
            metodo_pago=metodo,
            estado_pago='COMPLETADO'
        ).count()
        total_metodo = sum(
            p.monto_pagado for p in Pago.objects.filter(
                metodo_pago=metodo,
                estado_pago='COMPLETADO'
            )
        )
        if count > 0:
            print(f"  - {metodo}: {count} pagos (Bs. {total_metodo:,.2f})")
    
    return (facturas_creadas, pagos_creados)


# Funciones auxiliares
def obtener_pagos_paciente(paciente):
    """Obtiene todos los pagos de un paciente"""
    from facturacion.models import Pago
    return Pago.objects.filter(paciente=paciente).order_by('-fecha_pago')


def obtener_pagos_periodo(fecha_inicio, fecha_fin):
    """Obtiene pagos en un período específico"""
    from facturacion.models import Pago
    return Pago.objects.filter(
        fecha_pago__gte=fecha_inicio,
        fecha_pago__lte=fecha_fin,
        estado_pago='COMPLETADO'
    ).order_by('fecha_pago')


def calcular_ingresos_mes(mes, anio):
    """Calcula ingresos totales de un mes"""
    from facturacion.models import Pago
    from datetime import date
    
    # Primer y último día del mes
    primer_dia = date(anio, mes, 1)
    if mes == 12:
        ultimo_dia = date(anio + 1, 1, 1)
    else:
        ultimo_dia = date(anio, mes + 1, 1)
    
    pagos = Pago.objects.filter(
        fecha_pago__gte=primer_dia,
        fecha_pago__lt=ultimo_dia,
        estado_pago='COMPLETADO'
    )
    
    return sum(p.monto_pagado for p in pagos)


def obtener_pagos_pendientes():
    """Obtiene todos los pagos pendientes"""
    from facturacion.models import Pago
    return Pago.objects.filter(estado_pago='PENDIENTE').order_by('fecha_pago')
