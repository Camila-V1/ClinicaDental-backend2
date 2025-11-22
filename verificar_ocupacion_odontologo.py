"""
Script para verificar la ocupación del odontólogo después de actualizar estados.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from agenda.models import Cita
from usuarios.models import PerfilOdontologo
from django.utils import timezone

def verificar_ocupacion():
    print("=" * 70)
    print("👨‍⚕️ VERIFICACIÓN DE OCUPACIÓN DE ODONTÓLOGOS")
    print("=" * 70)
    
    with schema_context('clinica_demo'):
        # Obtener odontólogos
        odontologos = PerfilOdontologo.objects.filter(
            usuario__is_active=True
        ).select_related('usuario')
        
        print(f"\n📋 Odontólogos encontrados: {odontologos.count()}")
        
        for odontologo in odontologos:
            print(f"\n👨‍⚕️ {odontologo.usuario.full_name}")
            print(f"   Usuario ID: {odontologo.usuario.id}")
            
            # Citas del mes actual
            hoy = timezone.now().date()
            anio, mes = hoy.year, hoy.month
            
            citas_mes = Cita.objects.filter(
                odontologo=odontologo,
                fecha_hora__year=anio,
                fecha_hora__month=mes
            )
            
            total = citas_mes.count()
            completadas = citas_mes.filter(estado='COMPLETADA').count()
            canceladas = citas_mes.filter(estado='CANCELADA').count()
            pendientes = citas_mes.filter(estado__in=['PENDIENTE', 'CONFIRMADA']).count()
            
            horas_ocupadas = completadas * 2
            pacientes_atendidos = citas_mes.filter(
                estado='COMPLETADA'
            ).values('paciente').distinct().count()
            
            if total > 0:
                tasa_ocupacion = round((completadas / total * 100), 2)
            else:
                tasa_ocupacion = 0.0
            
            print(f"\n   📊 Citas del mes ({anio}-{mes:02d}):")
            print(f"      Total: {total}")
            print(f"      ✅ Completadas: {completadas}")
            print(f"      ❌ Canceladas: {canceladas}")
            print(f"      ⏳ Pendientes: {pendientes}")
            print(f"\n   📈 Métricas:")
            print(f"      Horas Ocupadas: {horas_ocupadas}h")
            print(f"      Tasa de Ocupación: {tasa_ocupacion}%")
            print(f"      Pacientes Atendidos: {pacientes_atendidos}")
            
            # Detalles de citas completadas
            if completadas > 0:
                print(f"\n   ✅ Citas Completadas:")
                citas_completadas = citas_mes.filter(estado='COMPLETADA').order_by('fecha_hora')
                for cita in citas_completadas:
                    print(f"      - ID: {cita.id} | Fecha: {cita.fecha_hora.strftime('%Y-%m-%d %H:%M')} | Paciente: {cita.paciente.usuario.full_name}")
        
        print("\n" + "=" * 70)
        print("✅ Verificación completada")
        print("=" * 70)
        print("\n💡 Si el dashboard aún muestra 0%, intenta:")
        print("   1. Hacer F5 (refrescar página)")
        print("   2. Ctrl + Shift + R (refrescar sin cache)")
        print("   3. Cerrar y abrir el navegador")
        print("=" * 70)

if __name__ == '__main__':
    verificar_ocupacion()
