"""
Script para actualizar estados de citas y generar datos visuales en el dashboard.

Actualiza algunas citas a estados COMPLETADA y CANCELADA para que el gráfico
de tendencia muestre las 3 líneas (Total, Completadas, Canceladas) correctamente.

Ejecución:
    python actualizar_estados_citas_dashboard.py
"""

import os
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agenda.models import Cita
from django.utils import timezone
from django_tenants.utils import schema_context

def actualizar_estados_citas():
    """
    Actualiza estados de citas existentes para visualización en dashboard.
    
    Estrategia:
    - 40% de citas → COMPLETADA (para mostrar línea verde)
    - 20% de citas → CANCELADA (para mostrar línea roja)
    - 40% quedan PENDIENTE/CONFIRMADA (para comparar)
    """
    
    print("=" * 70)
    print("🔄 ACTUALIZANDO ESTADOS DE CITAS PARA DASHBOARD")
    print("=" * 70)
    
    # Obtener todas las citas
    citas = Cita.objects.all().order_by('fecha_hora')
    total_citas = citas.count()
    
    if total_citas == 0:
        print("❌ No hay citas en la base de datos.")
        return
    
    print(f"\n📊 Total de citas encontradas: {total_citas}")
    print(f"   Distribución objetivo:")
    print(f"   - 40% COMPLETADA (verde): ~{int(total_citas * 0.4)} citas")
    print(f"   - 20% CANCELADA (rojo): ~{int(total_citas * 0.2)} citas")
    print(f"   - 40% PENDIENTE/CONFIRMADA (comparación): ~{int(total_citas * 0.4)} citas")
    
    # Estados actuales antes de actualizar
    print(f"\n📋 Estados ANTES de actualizar:")
    for estado in ['PENDIENTE', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA']:
        count = citas.filter(estado=estado).count()
        print(f"   {estado}: {count}")
    
    # Calcular cuántas citas actualizar
    num_completadas = int(total_citas * 0.4)
    num_canceladas = int(total_citas * 0.2)
    
    # Actualizar citas a COMPLETADA (las primeras 40%)
    citas_para_completar = citas.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )[:num_completadas]
    
    count_completadas = 0
    for cita in citas_para_completar:
        cita.estado = 'COMPLETADA'
        cita.save()
        count_completadas += 1
        print(f"   ✅ Cita #{cita.id} → COMPLETADA (Fecha: {cita.fecha_hora.strftime('%Y-%m-%d %H:%M')})")
    
    # Actualizar citas a CANCELADA (las siguientes 20%)
    citas_para_cancelar = citas.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )[:num_canceladas]
    
    count_canceladas = 0
    for cita in citas_para_cancelar:
        cita.estado = 'CANCELADA'
        cita.save()
        count_canceladas += 1
        print(f"   ❌ Cita #{cita.id} → CANCELADA (Fecha: {cita.fecha_hora.strftime('%Y-%m-%d %H:%M')})")
    
    # Verificar estados después de actualizar
    print(f"\n📋 Estados DESPUÉS de actualizar:")
    for estado in ['PENDIENTE', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA']:
        count = Cita.objects.filter(estado=estado).count()
        print(f"   {estado}: {count}")
    
    print(f"\n" + "=" * 70)
    print(f"✅ ACTUALIZACIÓN COMPLETADA")
    print(f"=" * 70)
    print(f"📈 Ahora ve al Dashboard → Reportes")
    print(f"   El gráfico de Tendencia de Citas mostrará:")
    print(f"   🔵 Línea Azul: Total de citas por día")
    print(f"   🟢 Línea Verde: Citas completadas ({count_completadas} citas)")
    print(f"   🔴 Línea Roja: Citas canceladas ({count_canceladas} citas)")
    print(f"\n💡 También verás cambios en:")
    print(f"   - Ocupación de Odontólogos: Tasa > 0%")
    print(f"   - Estadísticas Generales: Citas completadas > 0")
    print("=" * 70)

def verificar_distribucion():
    """Muestra distribución de citas por fecha y estado."""
    from django.db.models import Count
    from datetime import date, timedelta
    
    print("\n" + "=" * 70)
    print("📊 DISTRIBUCIÓN DE CITAS POR FECHA Y ESTADO")
    print("=" * 70)
    
    # Últimos 15 días
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=14)
    
    print(f"\nPeríodo: {fecha_inicio} a {fecha_fin}")
    print("-" * 70)
    
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        citas_dia = Cita.objects.filter(fecha_hora__date=fecha_actual)
        total = citas_dia.count()
        
        if total > 0:
            completadas = citas_dia.filter(estado='COMPLETADA').count()
            canceladas = citas_dia.filter(estado='CANCELADA').count()
            pendientes = citas_dia.filter(estado__in=['PENDIENTE', 'CONFIRMADA']).count()
            
            print(f"{fecha_actual} | Total: {total:2d} | "
                  f"✅ Completadas: {completadas:2d} | "
                  f"❌ Canceladas: {canceladas:2d} | "
                  f"⏳ Pendientes: {pendientes:2d}")
        
        fecha_actual += timedelta(days=1)
    
    print("-" * 70)

if __name__ == '__main__':
    try:
        # Usar el tenant clinica_demo
        print("🏥 Conectando al tenant: clinica_demo")
        
        with schema_context('clinica_demo'):
            actualizar_estados_citas()
            verificar_distribucion()
        
        print("\n🎉 ¡Listo! Refresca el dashboard para ver los cambios.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
