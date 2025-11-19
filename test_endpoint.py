import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from facturacion.models import Factura
from usuarios.models import Usuario, PerfilPaciente
from django.db.models import Sum

with schema_context('clinica_demo'):
    # Simular lo que hace el endpoint estado_cuenta
    user = Usuario.objects.get(email='paciente1@test.com')
    
    print(f"👤 Usuario: {user.nombre} {user.apellido}")
    print(f"📧 Email: {user.email}")
    print(f"🏷️ Tipo: {user.tipo_usuario}")
    print(f"🔗 Tiene perfil_paciente? {hasattr(user, 'perfil_paciente')}")
    
    if hasattr(user, 'perfil_paciente'):
        paciente = user.perfil_paciente
        print(f"✅ Perfil paciente encontrado (usuario_id: {paciente.usuario_id})")
        
        # Simular el queryset del ViewSet
        queryset = Factura.objects.filter(paciente=paciente)
        
        print(f"\n📊 SIMULANDO ENDPOINT estado_cuenta:")
        print(f"  • Queryset base: {queryset.count()} facturas")
        
        # Calcular totales (exactamente como en el endpoint)
        total_facturas = queryset.count()
        facturas_pendientes = queryset.filter(estado='PENDIENTE').count()
        facturas_pagadas = queryset.filter(estado='PAGADA').count()
        
        monto_total = queryset.aggregate(total=Sum('monto_total'))['total'] or 0
        monto_pagado = queryset.aggregate(total=Sum('monto_pagado'))['total'] or 0
        saldo_pendiente = monto_total - monto_pagado
        
        print(f"  • total_facturas: {total_facturas}")
        print(f"  • facturas_pendientes: {facturas_pendientes}")
        print(f"  • facturas_pagadas: {facturas_pagadas}")
        print(f"  • monto_total: ${monto_total}")
        print(f"  • monto_pagado: ${monto_pagado}")
        print(f"  • saldo_pendiente: ${saldo_pendiente}")
        
        print(f"\n💰 RESULTADO ESPERADO:")
        print(f"  {{")
        print(f"    'saldo_pendiente': '${saldo_pendiente:,.2f}',")
        print(f"    'total_facturas': {total_facturas},")
        print(f"    'facturas_pendientes': {facturas_pendientes},")
        print(f"    'facturas_pagadas': {facturas_pagadas},")
        print(f"    'monto_total': {float(monto_total)},")
        print(f"    'monto_pagado': {float(monto_pagado)}")
        print(f"  }}")
