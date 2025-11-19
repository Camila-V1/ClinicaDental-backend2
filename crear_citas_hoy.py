"""
Script para crear citas de prueba para HOY
Ejecutar con: python crear_citas_hoy.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agenda.models import Cita
from usuarios.models import PerfilOdontologo, PerfilPaciente
from django.utils import timezone
from datetime import timedelta
from django_tenants.utils import schema_context
from tenants.models import Clinica

print("🚀 Creando citas de prueba para HOY...")
print(f"📅 Fecha actual: {timezone.now().date()}")
print()

# Obtener el tenant
try:
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    print(f"🏢 Tenant encontrado: {tenant.nombre} ({tenant.schema_name})")
    print()
except Clinica.DoesNotExist:
    print("❌ Error: No se encontró el tenant 'clinica_demo'")
    print("   Tenants disponibles:")
    for t in Clinica.objects.all():
        print(f"   - {t.schema_name} ({t.nombre})")
    exit(1)

# Usar el contexto del tenant para todas las operaciones
with schema_context(tenant.schema_name):
    # Obtener el odontólogo y pacientes
    try:
        odonto = PerfilOdontologo.objects.first()
        if not odonto:
            print("❌ Error: No hay odontólogos en el sistema")
            exit(1)
        
        print(f"✅ Odontólogo encontrado: {odonto.usuario.full_name}")
        
        pacientes = list(PerfilPaciente.objects.all()[:3])
        if not pacientes:
            print("❌ Error: No hay pacientes en el sistema")
            exit(1)
        
        print(f"✅ {len(pacientes)} pacientes encontrados")
        print()
        
        # Crear 5 citas para hoy
        ahora = timezone.now()
        citas_creadas = []
        
        # Cita 1: En 2 horas (CONFIRMADA)
        cita1 = Cita.objects.create(
            odontologo=odonto,
            paciente=pacientes[0],
            fecha_hora=ahora + timedelta(hours=2),
            motivo_tipo='CONSULTA',
            motivo='Revisión general - PRÓXIMA',
            estado='CONFIRMADA'
        )
        citas_creadas.append(cita1)
        print(f"✅ Cita 1 creada: {cita1.fecha_hora.strftime('%H:%M')} - {pacientes[0].usuario.full_name} (CONFIRMADA)")
        
        # Cita 2: En 4 horas (PENDIENTE)
        cita2 = Cita.objects.create(
            odontologo=odonto,
            paciente=pacientes[1],
            fecha_hora=ahora + timedelta(hours=4),
            motivo_tipo='LIMPIEZA',
            motivo='Limpieza dental',
            estado='PENDIENTE'
        )
        citas_creadas.append(cita2)
        print(f"✅ Cita 2 creada: {cita2.fecha_hora.strftime('%H:%M')} - {pacientes[1].usuario.full_name} (PENDIENTE)")
        
        # Cita 3: En 6 horas (PENDIENTE)
        cita3 = Cita.objects.create(
            odontologo=odonto,
            paciente=pacientes[2],
            fecha_hora=ahora + timedelta(hours=6),
            motivo_tipo='REVISION',
            motivo='Control post-tratamiento',
            estado='PENDIENTE'
        )
        citas_creadas.append(cita3)
        print(f"✅ Cita 3 creada: {cita3.fecha_hora.strftime('%H:%M')} - {pacientes[2].usuario.full_name} (PENDIENTE)")
        
        # Cita 4: Hace 2 horas (ATENDIDA)
        cita4 = Cita.objects.create(
            odontologo=odonto,
            paciente=pacientes[0],
            fecha_hora=ahora - timedelta(hours=2),
            motivo_tipo='CONSULTA',
            motivo='Consulta de urgencia',
            estado='ATENDIDA'
        )
        citas_creadas.append(cita4)
        print(f"✅ Cita 4 creada: {cita4.fecha_hora.strftime('%H:%M')} - {pacientes[0].usuario.full_name} (ATENDIDA)")
        
        # Cita 5: Hace 4 horas (ATENDIDA)
        cita5 = Cita.objects.create(
            odontologo=odonto,
            paciente=pacientes[1],
            fecha_hora=ahora - timedelta(hours=4),
            motivo_tipo='LIMPIEZA',
            motivo='Profilaxis',
            estado='ATENDIDA'
        )
        citas_creadas.append(cita5)
        print(f"✅ Cita 5 creada: {cita5.fecha_hora.strftime('%H:%M')} - {pacientes[1].usuario.full_name} (ATENDIDA)")
        
        print()
        print("=" * 60)
        print("🎉 ¡CITAS CREADAS EXITOSAMENTE!")
        print("=" * 60)
        print(f"📊 Total citas de hoy: {len(citas_creadas)}")
        print(f"⏰ Pendientes: {sum(1 for c in citas_creadas if c.estado == 'PENDIENTE')}")
        print(f"✅ Confirmadas: {sum(1 for c in citas_creadas if c.estado == 'CONFIRMADA')}")
        print(f"✔️  Atendidas: {sum(1 for c in citas_creadas if c.estado == 'ATENDIDA')}")
        print()
        print("🔄 Ahora recarga tu frontend para ver las métricas actualizadas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
