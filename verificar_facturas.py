import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from facturacion.models import Factura
from usuarios.models import PerfilPaciente

with schema_context('clinica_demo'):
    # Buscar el paciente
    paciente = PerfilPaciente.objects.get(usuario__email='paciente1@test.com')
    print(f"✅ Paciente encontrado: {paciente.usuario.nombre} {paciente.usuario.apellido} (Usuario ID: {paciente.usuario_id})")
    
    # Buscar TODAS las facturas sin filtrar por estado
    todas_facturas = Factura.objects.filter(paciente=paciente)
    print(f"\n📊 Total facturas encontradas: {todas_facturas.count()}")
    
    if todas_facturas.count() == 0:
        print("❌ No hay facturas para este paciente")
    else:
        print("\n💰 Detalles de cada factura:")
        for f in todas_facturas:
            saldo = f.monto_total - f.monto_pagado
            print(f"  • Factura {f.id}:")
            print(f"    - Monto total: ${f.monto_total}")
            print(f"    - Monto pagado: ${f.monto_pagado}")
            print(f"    - Saldo pendiente: ${saldo}")
            print(f"    - Estado: '{f.estado}' (tipo: {type(f.estado).__name__})")
            print(f"    - Fecha emisión: {f.fecha_emision}")
            print()
        
        # Probar filtros
        print("\n🔍 Probando filtros:")
        pendientes_upper = todas_facturas.filter(estado='PENDIENTE')
        pendientes_lower = todas_facturas.filter(estado='pendiente')
        pagadas_upper = todas_facturas.filter(estado='PAGADA')
        pagadas_lower = todas_facturas.filter(estado='pagada')
        
        print(f"  • filter(estado='PENDIENTE'): {pendientes_upper.count()} facturas")
        print(f"  • filter(estado='pendiente'): {pendientes_lower.count()} facturas")
        print(f"  • filter(estado='PAGADA'): {pagadas_upper.count()} facturas")
        print(f"  • filter(estado='pagada'): {pagadas_lower.count()} facturas")
        
        # Calcular totales
        from django.db.models import Sum
        totales = todas_facturas.aggregate(
            monto_total=Sum('monto_total'),
            monto_pagado=Sum('monto_pagado')
        )
        saldo_total = (totales['monto_total'] or 0) - (totales['monto_pagado'] or 0)
        
        print(f"\n💵 TOTALES:")
        print(f"  • Suma monto_total: ${totales['monto_total']}")
        print(f"  • Suma monto_pagado: ${totales['monto_pagado']}")
        print(f"  • SALDO PENDIENTE: ${saldo_total}")
