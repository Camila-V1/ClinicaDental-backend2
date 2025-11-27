"""
Módulo para poblar agenda con citas de ejemplo
"""

from agenda.models import Cita
from datetime import datetime, timedelta
from django.utils import timezone
import random


def poblar_agenda(odontologos, pacientes, servicios):
    """
    Crea citas de ejemplo
    
    Args:
        odontologos: Lista de PerfilOdontologo
        pacientes: Lista de PerfilPaciente
        servicios: Lista de Servicio
    
    Returns:
        list: Lista de citas creadas
    """
    citas_creadas = []
    
    print("\n  📅 Creando citas...")
    
    # Validar que tenemos datos
    if not odontologos or not pacientes:
        print("  ⚠️  No hay odontólogos o pacientes para crear citas")
        return citas_creadas
    
    # =========================================================================
    # CITAS PASADAS (últimos 30 días) - ATENDIDAS
    # =========================================================================
    print("  → Citas pasadas (atendidas)...")
    
    base_date = timezone.now()
    
    for i in range(15):
        dias_atras = random.randint(1, 30)
        fecha = base_date - timedelta(days=dias_atras)
        
        # Ajustar a horario laboral (8 AM - 6 PM)
        hora = random.choice([8, 9, 10, 11, 14, 15, 16, 17])
        fecha = fecha.replace(hour=hora, minute=random.choice([0, 30]), second=0, microsecond=0)
        
        # Evitar domingos
        if fecha.weekday() == 6:
            fecha = fecha - timedelta(days=1)
        
        odontologo = random.choice(odontologos)
        paciente = random.choice(pacientes)
        
        # Motivos comunes
        motivo_tipo = random.choice(['CONSULTA', 'LIMPIEZA', 'REVISION'])
        motivos_texto = {
            'CONSULTA': 'Dolor en muela superior derecha',
            'LIMPIEZA': 'Limpieza dental programada',
            'REVISION': 'Control post-tratamiento'
        }
        
        cita, created = Cita.objects.get_or_create(
            odontologo=odontologo,
            paciente=paciente,
            fecha_hora=fecha,
            defaults={
                'motivo_tipo': motivo_tipo,
                'motivo': motivos_texto[motivo_tipo],
                'estado': 'ATENDIDA',
                'observaciones': 'Cita atendida satisfactoriamente',
                'pagada': True
            }
        )
        
        if created:
            citas_creadas.append(cita)
    
    print(f"    ✓ {len([c for c in citas_creadas if c.estado == 'ATENDIDA'])} citas atendidas")
    
    # =========================================================================
    # CITAS DE HOY
    # =========================================================================
    print("  → Citas de hoy...")
    
    hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Cita en la mañana (ya atendida)
    cita_manana = Cita.objects.create(
        odontologo=odontologos[0],
        paciente=pacientes[0],
        fecha_hora=hoy.replace(hour=9, minute=0),
        motivo_tipo='LIMPIEZA',
        motivo='Limpieza dental programada',
        estado='ATENDIDA',
        observaciones='Limpieza realizada, paciente sin complicaciones',
        pagada=True
    )
    citas_creadas.append(cita_manana)
    
    # Cita confirmada para más tarde
    if timezone.now().hour < 15:
        odonts_list = list(odontologos)
        pacs_list = list(pacientes)
        cita_tarde = Cita.objects.create(
            odontologo=odonts_list[-1] if len(odonts_list) > 1 else odonts_list[0],
            paciente=pacs_list[-1] if len(pacs_list) > 1 else pacs_list[0],
            fecha_hora=hoy.replace(hour=15, minute=30),
            motivo_tipo='CONSULTA',
            motivo='Consulta odontológica general',
            estado='CONFIRMADA',
            observaciones='Paciente confirmó asistencia',
            pagada=False
        )
        citas_creadas.append(cita_tarde)
    
    print(f"    ✓ {len([c for c in citas_creadas if c.fecha_hora.date() == hoy.date()])} citas hoy")
    
    # =========================================================================
    # CITAS FUTURAS (próximos 30 días)
    # =========================================================================
    print("  → Citas futuras (programadas)...")
    
    for i in range(20):
        dias_adelante = random.randint(1, 30)
        fecha = base_date + timedelta(days=dias_adelante)
        
        # Ajustar a horario laboral
        hora = random.choice([8, 9, 10, 11, 14, 15, 16, 17])
        fecha = fecha.replace(hour=hora, minute=random.choice([0, 30]), second=0, microsecond=0)
        
        # Evitar domingos
        if fecha.weekday() == 6:
            fecha = fecha + timedelta(days=1)
        
        odontologo = random.choice(odontologos)
        paciente = random.choice(pacientes)
        
        # Motivos variados
        motivo_tipo = random.choice(['CONSULTA', 'LIMPIEZA', 'REVISION', 'URGENCIA'])
        motivos_dict = {
            'CONSULTA': 'Consulta de control',
            'LIMPIEZA': 'Limpieza dental',
            'REVISION': 'Revisión general',
            'URGENCIA': 'Dolor dental agudo'
        }
        
        # Estados variados para citas futuras
        estado = random.choices(
            ['PENDIENTE', 'CONFIRMADA'],
            weights=[30, 70]
        )[0]
        
        cita, created = Cita.objects.get_or_create(
            odontologo=odontologo,
            paciente=paciente,
            fecha_hora=fecha,
            defaults={
                'motivo_tipo': motivo_tipo,
                'motivo': motivos_dict[motivo_tipo],
                'estado': estado,
                'pagada': False
            }
        )
        
        if created:
            citas_creadas.append(cita)
    
    print(f"    ✓ {len([c for c in citas_creadas if c.estado in ['PENDIENTE', 'CONFIRMADA']])} citas futuras")
    
    # =========================================================================
    # ALGUNAS CITAS CANCELADAS
    # =========================================================================
    print("  → Citas canceladas...")
    
    for i in range(3):
        dias_adelante = random.randint(5, 15)
        fecha = base_date + timedelta(days=dias_adelante)
        fecha = fecha.replace(hour=random.choice([10, 14, 16]), minute=0, second=0, microsecond=0)
        
        if fecha.weekday() == 6:
            fecha = fecha + timedelta(days=1)
        
        cita = Cita.objects.create(
            odontologo=random.choice(odontologos),
            paciente=random.choice(pacientes),
            fecha_hora=fecha,
            motivo_tipo='CONSULTA',
            motivo='Cita cancelada por el paciente',
            estado='CANCELADA',
            observaciones='Paciente canceló por motivos personales',
            pagada=False
        )
        citas_creadas.append(cita)
    
    print(f"    ✓ {len([c for c in citas_creadas if c.estado == 'CANCELADA'])} citas canceladas")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print(f"\n  ✅ Total de citas creadas: {len(citas_creadas)}")
    
    # Estadísticas por estado
    estados_count = {}
    for cita in citas_creadas:
        estados_count[cita.estado] = estados_count.get(cita.estado, 0) + 1
    
    print("     Estados:")
    for estado, count in estados_count.items():
        print(f"       • {estado}: {count}")
    
    return citas_creadas


def obtener_citas_hoy():
    """Retorna citas del día actual"""
    hoy = timezone.now().date()
    return Cita.objects.filter(
        fecha_hora__date=hoy
    ).order_by('fecha_hora')


def obtener_citas_semana():
    """Retorna citas de la semana actual"""
    hoy = timezone.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    return Cita.objects.filter(
        fecha_hora__date__range=[inicio_semana.date(), fin_semana.date()]
    ).order_by('fecha_hora')


def obtener_citas_por_odontologo(odontologo):
    """Retorna citas de un odontólogo específico"""
    return Cita.objects.filter(odontologo=odontologo).order_by('-fecha_hora')


def obtener_citas_por_paciente(paciente):
    """Retorna historial de citas de un paciente"""
    return Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')
