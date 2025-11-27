"""
Módulo para poblar historial clínico con episodios y odontogramas
"""
from django.utils import timezone
from datetime import timedelta
import random


def poblar_historial(odontologos, pacientes, citas_atendidas):
    """
    Crea historiales clínicos, episodios y odontogramas
    
    Args:
        odontologos: Lista de PerfilOdontologo
        pacientes: Lista de PerfilPaciente
        citas_atendidas: Lista de Cita con estado ATENDIDA
    
    Returns:
        tuple: (historiales, episodios, odontogramas)
    """
    from historial_clinico.models import HistorialClinico, EpisodioAtencion, Odontograma
    
    print("\n=== POBLANDO HISTORIAL CLÍNICO ===")
    
    historiales_creados = []
    episodios_creados = []
    odontogramas_creados = []
    
    # =========================================================================
    # 1. CREAR HISTORIALES CLÍNICOS PARA CADA PACIENTE
    # =========================================================================
    print("\n1. Creando historiales clínicos base...")
    
    for paciente in pacientes:
        # Crear o obtener historial clínico (OneToOne)
        historial, created = HistorialClinico.objects.get_or_create(
            paciente=paciente,
            defaults={
                'antecedentes_medicos': random.choice([
                    'Sin antecedentes médicos relevantes',
                    'Hipertensión controlada con medicación',
                    'Diabetes tipo 2, tratamiento con metformina',
                    'Asma leve, uso esporádico de inhalador'
                ]),
                'alergias': random.choice([
                    'Sin alergias conocidas',
                    'Alergia a penicilina',
                    'Alergia a ibuprofeno',
                    'Sin alergias medicamentosas'
                ]),
                'medicamentos_actuales': random.choice([
                    'Ninguno',
                    'Losartán 50mg (1 vez al día)',
                    'Metformina 850mg (2 veces al día)',
                    'Ninguno actualmente'
                ])
            }
        )
        
        if created:
            historiales_creados.append(historial)
            print(f"   ✓ Historial creado para: {paciente.usuario.full_name}")
    
    print(f"   ✓ {len(historiales_creados)} historiales clínicos creados")
    
    # =========================================================================
    # 2. CREAR EPISODIOS DE ATENCIÓN VINCULADOS A CITAS
    # =========================================================================
    print("\n2. Creando episodios de atención...")
    
    diagnosticos_comunes = [
        'Caries dental en pieza {diente}',
        'Gingivitis leve generalizada',
        'Placa bacteriana moderada',
        'Periodontitis crónica leve en sector {sector}',
        'Sensibilidad dental',
        'Inflamación gingival localizada',
        'Cálculo dental supragingival',
        'Higiene oral regular'
    ]
    
    procedimientos_comunes = [
        'Limpieza dental completa con ultrasonido y pasta profiláctica',
        'Obturación con resina compuesta en pieza {diente}',
        'Profilaxis y aplicación de flúor',
        'Tratamiento de conducto en pieza {diente}',
        'Extracción simple de pieza {diente}',
        'Curetaje dental en cuadrante {cuadrante}',
        'Consulta de diagnóstico y plan de tratamiento'
    ]
    
    # Crear episodios para las primeras 12 citas atendidas
    for cita in citas_atendidas[:12]:
        historial = HistorialClinico.objects.filter(paciente=cita.paciente).first()
        
        if historial:
            diente = random.randint(11, 48)
            sector = random.choice(['superior', 'inferior', 'anterior', 'posterior'])
            cuadrante = random.choice(['1', '2', '3', '4'])
            
            episodio = EpisodioAtencion.objects.create(
                historial_clinico=historial,
                odontologo=cita.odontologo,
                motivo_consulta=cita.motivo,
                diagnostico=random.choice(diagnosticos_comunes).format(
                    diente=diente, sector=sector
                ),
                descripcion_procedimiento=random.choice(procedimientos_comunes).format(
                    diente=diente, cuadrante=cuadrante
                ),
                notas_privadas=f'Paciente tolera bien el procedimiento. Próximo control en 6 meses.'
            )
            episodios_creados.append(episodio)
    
    print(f"   ✓ {len(episodios_creados)} episodios de atención creados")
    
    # =========================================================================
    # 3. CREAR ODONTOGRAMAS
    # =========================================================================
    print("\n3. Creando odontogramas...")
    
    # Estados dentales posibles
    estados_diente = ['sano', 'caries', 'obturado', 'endodoncia', 'corona', 'ausente', 'fracturado']
    
    # Crear odontogramas para cada historial
    for historial in HistorialClinico.objects.all():
        # Crear 1-2 odontogramas por paciente
        num_odontogramas = random.choice([1, 2])
        
        for _ in range(num_odontogramas):
            # Generar estado de las piezas dentales (32 dientes)
            estado_piezas = {}
            
            # Dientes superiores (11-18, 21-28)
            for i in range(11, 19):
                estado = random.choices(
                    estados_diente,
                    weights=[70, 10, 10, 3, 2, 3, 2]
                )[0]
                
                estado_piezas[str(i)] = {
                    'estado': estado,
                    'notas': f'Pieza {i} - {estado}'
                }
            
            for i in range(21, 29):
                estado = random.choices(
                    estados_diente,
                    weights=[70, 10, 10, 3, 2, 3, 2]
                )[0]
                
                estado_piezas[str(i)] = {
                    'estado': estado,
                    'notas': f'Pieza {i} - {estado}'
                }
            
            # Dientes inferiores (31-38, 41-48)
            for i in range(31, 39):
                estado = random.choices(
                    estados_diente,
                    weights=[70, 10, 10, 3, 2, 3, 2]
                )[0]
                
                estado_piezas[str(i)] = {
                    'estado': estado,
                    'notas': f'Pieza {i} - {estado}'
                }
            
            for i in range(41, 49):
                estado = random.choices(
                    estados_diente,
                    weights=[70, 10, 10, 3, 2, 3, 2]
                )[0]
                
                estado_piezas[str(i)] = {
                    'estado': estado,
                    'notas': f'Pieza {i} - {estado}'
                }
            
            # Crear odontograma
            odontograma = Odontograma.objects.create(
                historial_clinico=historial,
                estado_piezas=estado_piezas,
                notas='Odontograma completo. Estado general de salud bucal evaluado.'
            )
            odontogramas_creados.append(odontograma)
    
    print(f"   ✓ {len(odontogramas_creados)} odontogramas creados")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print("\n=== RESUMEN HISTORIAL CLÍNICO ===")
    print(f"Historiales clínicos: {HistorialClinico.objects.count()}")
    print(f"Episodios de atención: {len(episodios_creados)}")
    print(f"Odontogramas: {len(odontogramas_creados)}")
    
    return (
        list(HistorialClinico.objects.all()),
        episodios_creados,
        odontogramas_creados
    )


# Funciones auxiliares
def obtener_historial_paciente(paciente):
    """Obtiene el historial clínico de un paciente"""
    from historial_clinico.models import HistorialClinico
    return HistorialClinico.objects.filter(paciente=paciente).first()


def obtener_episodios_paciente(paciente):
    """Obtiene todos los episodios de un paciente"""
    from historial_clinico.models import HistorialClinico
    historial = HistorialClinico.objects.filter(paciente=paciente).first()
    if historial:
        return historial.episodios.all().order_by('-fecha_atencion')
    return []


def obtener_ultimo_odontograma(paciente):
    """Obtiene el odontograma más reciente de un paciente"""
    from historial_clinico.models import HistorialClinico
    historial = HistorialClinico.objects.filter(paciente=paciente).first()
    if historial:
        return historial.odontogramas.order_by('-fecha_snapshot').first()
    return None
