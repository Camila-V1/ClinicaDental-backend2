#!/usr/bin/env python
"""
🏥 POBLADOR UNIVERSAL DEL SISTEMA
================================
Script completo para restablecer y poblar la base de datos con todos los módulos.

CREDENCIALES:
- Odontólogo (tenant): odontologo@clinica-demo.com / odontologo123

USO:
    python poblar_sistema_completo.py
"""
import os
import django
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth.hashers import make_password
from usuarios.models import Usuario, PerfilOdontologo, PerfilPaciente, Especialidad
from agenda.models import Cita
from inventario.models import CategoriaInsumo, Insumo
from tratamientos.models import Servicio, PlanDeTratamiento, ItemPlanTratamiento, CategoriaServicio, MaterialServicioFijo, MaterialServicioOpcional
from historial_clinico.models import HistorialClinico, Odontograma, EpisodioAtencion
from facturacion.models import Factura, Pago

print('=' * 80)
print('🏥 POBLADOR UNIVERSAL DEL SISTEMA - CLÍNICA DENTAL')
print('=' * 80)
print()


# ============================================================================
# PASO 1: LIMPIAR Y PREPARAR TENANT
# ============================================================================
def limpiar_tenant():
    print('🧹 PASO 1: LIMPIANDO TENANT clinica-demo')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    # Orden inverso de dependencias
    modelos_a_limpiar = [
        ('Pagos', Pago),
        ('Facturas', Factura),
        ('Episodios Atención', EpisodioAtencion),
        ('Items Plan Tratamiento', ItemPlanTratamiento),
        ('Planes de Tratamiento', PlanDeTratamiento),
        ('Citas', Cita),
        ('Materiales Fijos Servicio', MaterialServicioFijo),
        ('Materiales Opcionales Servicio', MaterialServicioOpcional),
        ('Servicios', Servicio),
        ('Categorías Servicio', CategoriaServicio),
        ('Insumos', Insumo),
        ('Categorías Insumo', CategoriaInsumo),
        ('Odontogramas', Odontograma),
        ('Historiales Clínicos', HistorialClinico),
        ('Perfiles Paciente', PerfilPaciente),
        ('Perfiles Odontólogo', PerfilOdontologo),
        ('Usuarios', Usuario),
        ('Especialidades', Especialidad),
    ]
    
    for nombre, modelo in modelos_a_limpiar:
        count = modelo.objects.count()
        if count > 0:
            modelo.objects.all().delete()
            print(f'  ✅ Eliminados {count} {nombre}')
    
    print()


# ============================================================================
# PASO 2: CREAR USUARIOS DEL TENANT
# ============================================================================
def crear_usuarios():
    print('👥 PASO 2: CREANDO USUARIOS DEL TENANT')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    # Crear especialidad primero
    especialidad_general = Especialidad.objects.create(
        nombre='Odontología General',
        descripcion='Atención odontológica general y preventiva',
        activo=True
    )
    print(f'  ✅ Especialidad creada: {especialidad_general.nombre}')
    
    # Solo el odontólogo
    odontologo_user = Usuario.objects.create_user(
        email='odontologo@clinica-demo.com',
        password='odontologo123',
        nombre='Dr. Juan',
        apellido='Pérez',
        tipo_usuario='ODONTOLOGO',
        telefono='987654321',
        ci='1234567',
        sexo='M'
    )
    print(f'  ✅ Odontólogo: {odontologo_user.email}')
    
    # Crear perfil de odontólogo CON especialidad
    perfil_odontologo, created = PerfilOdontologo.objects.get_or_create(
        usuario=odontologo_user,
        defaults={
            'cedulaProfesional': 'COL-12345',
            'experienciaProfesional': '10 años de experiencia en odontología general',
            'especialidad': especialidad_general
        }
    )
    if created:
        print(f'  ✅ Perfil odontólogo creado con especialidad: {especialidad_general.nombre}')
    else:
        print(f'  ⚠️  Perfil odontólogo ya existía')
    
    # Crear 5 pacientes de prueba
    pacientes_data = [
        {
            'email': 'paciente1@test.com',
            'nombre': 'María',
            'apellido': 'García',
            'telefono': '555123456',
            'ci': '7654321',
            'sexo': 'F',
            'tipo_sangre': 'O+',
            'alergias': 'Penicilina',
            'antecedentes': 'Hipertensión controlada'
        },
        {
            'email': 'paciente2@test.com',
            'nombre': 'Carlos',
            'apellido': 'López',
            'telefono': '555789012',
            'ci': '8765432',
            'sexo': 'M',
            'tipo_sangre': 'A+',
            'alergias': 'Ninguna',
            'antecedentes': 'Ninguno'
        },
        {
            'email': 'paciente3@test.com',
            'nombre': 'Laura',
            'apellido': 'Rodríguez',
            'telefono': '555345678',
            'ci': '9876543',
            'sexo': 'F',
            'tipo_sangre': 'B+',
            'alergias': 'Látex',
            'antecedentes': 'Asma leve'
        },
        {
            'email': 'paciente4@test.com',
            'nombre': 'Pedro',
            'apellido': 'Martínez',
            'telefono': '555456789',
            'ci': '6543210',
            'sexo': 'M',
            'tipo_sangre': 'AB+',
            'alergias': 'Ninguna',
            'antecedentes': 'Diabetes tipo 2'
        },
        {
            'email': 'paciente5@test.com',
            'nombre': 'Ana',
            'apellido': 'Torres',
            'telefono': '555567890',
            'ci': '5432109',
            'sexo': 'F',
            'tipo_sangre': 'O-',
            'alergias': 'Anestesia local (lidocaína)',
            'antecedentes': 'Ninguno'
        }
    ]
    
    pacientes_creados = []
    for datos in pacientes_data:
        paciente_user = Usuario.objects.create_user(
            email=datos['email'],
            password='paciente123',
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            tipo_usuario='PACIENTE',
            telefono=datos['telefono'],
            ci=datos['ci'],
            sexo=datos['sexo']
        )
        
        perfil_paciente, created = PerfilPaciente.objects.get_or_create(
            usuario=paciente_user,
            defaults={
                'tipo_sangre': datos.get('tipo_sangre'),
                'alergias': datos.get('alergias'),
                'enfermedades_cronicas': datos.get('antecedentes'),
                'contacto_emergencia': f'Emergencia {datos["nombre"]}',
                'telefono_emergencia': '555000000'
            }
        )
        
        # Crear historial clínico
        historial, created = HistorialClinico.objects.get_or_create(paciente=perfil_paciente)
        
        # Crear odontograma
        odontograma, created = Odontograma.objects.get_or_create(historial_clinico=historial)
        
        pacientes_creados.append(perfil_paciente)  # Devolver perfil en lugar de usuario
        print(f'  ✅ Paciente: {paciente_user.email} (con historial y odontograma)')
    
    print()
    return odontologo_user, perfil_odontologo, pacientes_creados


# ============================================================================
# PASO 3: CREAR CATÁLOGO DE INVENTARIO
# ============================================================================
def crear_inventario():
    print('📦 PASO 3: CREANDO CATÁLOGO DE INVENTARIO')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    # Categorías de Insumos
    categorias = {
        'Materiales Dentales': CategoriaInsumo.objects.create(
            nombre='Materiales Dentales',
            descripcion='Resinas, cementos, amalgamas'
        ),
        'Instrumental': CategoriaInsumo.objects.create(
            nombre='Instrumental',
            descripcion='Instrumental odontológico'
        ),
        'Insumos Descartables': CategoriaInsumo.objects.create(
            nombre='Insumos Descartables',
            descripcion='Guantes, cubrebocas, jeringas'
        ),
        'Anestésicos': CategoriaInsumo.objects.create(
            nombre='Anestésicos',
            descripcion='Anestésicos locales'
        )
    }
    print(f'  ✅ {len(categorias)} categorías creadas')
    
    # Insumos para inventario
    insumos_data = [
        # Materiales Dentales
        {
            'categoria': categorias['Materiales Dentales'],
            'nombre': 'Resina Compuesta A2',
            'descripcion': 'Resina fotopolimerizable color A2',
            'codigo': 'RES-A2-001',
            'stock_minimo': Decimal('10'),
            'stock_actual': Decimal('50'),
            'precio_costo': Decimal('45.00'),
            'precio_venta': Decimal('75.00'),
            'unidad_medida': 'unidad'
        },
        {
            'categoria': categorias['Materiales Dentales'],
            'nombre': 'Resina Compuesta A3',
            'descripcion': 'Resina fotopolimerizable color A3',
            'codigo': 'RES-A3-001',
            'stock_minimo': Decimal('10'),
            'stock_actual': Decimal('45'),
            'precio_costo': Decimal('45.00'),
            'precio_venta': Decimal('75.00'),
            'unidad_medida': 'unidad'
        },
        {
            'categoria': categorias['Materiales Dentales'],
            'nombre': 'Cemento Temporal',
            'descripcion': 'Cemento para restauraciones temporales',
            'codigo': 'CEM-TMP-001',
            'stock_minimo': Decimal('8'),
            'stock_actual': Decimal('30'),
            'precio_costo': Decimal('25.00'),
            'precio_venta': Decimal('40.00'),
            'unidad_medida': 'unidad'
        },
        {
            'categoria': categorias['Materiales Dentales'],
            'nombre': 'Amalgama Dental',
            'descripcion': 'Amalgama de plata para restauraciones',
            'codigo': 'AML-001',
            'stock_minimo': Decimal('5'),
            'stock_actual': Decimal('20'),
            'precio_costo': Decimal('60.00'),
            'precio_venta': Decimal('95.00'),
            'unidad_medida': 'unidad'
        },
        # Instrumental
        {
            'categoria': categorias['Instrumental'],
            'nombre': 'Espejo Dental',
            'descripcion': 'Espejo intraoral con mango',
            'codigo': 'INS-ESP-001',
            'stock_minimo': Decimal('20'),
            'stock_actual': Decimal('80'),
            'precio_costo': Decimal('5.00'),
            'precio_venta': Decimal('12.00'),
            'unidad_medida': 'unidad'
        },
        {
            'categoria': categorias['Instrumental'],
            'nombre': 'Pinza Dental',
            'descripcion': 'Pinza de acero inoxidable',
            'codigo': 'INS-PIN-001',
            'stock_minimo': Decimal('15'),
            'stock_actual': Decimal('60'),
            'precio_costo': Decimal('8.00'),
            'precio_venta': Decimal('15.00'),
            'unidad_medida': 'unidad'
        },
        # Descartables
        {
            'categoria': categorias['Insumos Descartables'],
            'nombre': 'Guantes Látex M',
            'descripcion': 'Caja de guantes látex talla M',
            'codigo': 'GLV-LAT-M',
            'stock_minimo': Decimal('50'),
            'stock_actual': Decimal('200'),
            'precio_costo': Decimal('8.00'),
            'precio_venta': Decimal('15.00'),
            'unidad_medida': 'caja'
        },
        {
            'categoria': categorias['Insumos Descartables'],
            'nombre': 'Cubrebocas Descartable',
            'descripcion': 'Caja de cubrebocas tricapa',
            'codigo': 'CBR-001',
            'stock_minimo': Decimal('40'),
            'stock_actual': Decimal('150'),
            'precio_costo': Decimal('10.00'),
            'precio_venta': Decimal('18.00'),
            'unidad_medida': 'caja'
        },
        {
            'categoria': categorias['Insumos Descartables'],
            'nombre': 'Jeringa Descartable 5ml',
            'descripcion': 'Jeringa descartable con aguja',
            'codigo': 'JER-5ML-001',
            'stock_minimo': Decimal('100'),
            'stock_actual': Decimal('500'),
            'precio_costo': Decimal('0.50'),
            'precio_venta': Decimal('1.50'),
            'unidad_medida': 'unidad'
        },
        # Anestésicos
        {
            'categoria': categorias['Anestésicos'],
            'nombre': 'Lidocaína 2%',
            'descripcion': 'Anestésico local con epinefrina',
            'codigo': 'ANE-LID-001',
            'stock_minimo': Decimal('30'),
            'stock_actual': Decimal('120'),
            'precio_costo': Decimal('3.00'),
            'precio_venta': Decimal('8.00'),
            'unidad_medida': 'unidad'
        }
    ]
    
    insumos_creados = []
    for datos in insumos_data:
        insumo = Insumo.objects.create(**datos)
        insumos_creados.append(insumo)
    
    print(f'  ✅ {len(insumos_creados)} insumos creados')
    print()
    return insumos_creados


# ============================================================================
# PASO 4: CREAR CATÁLOGO DE SERVICIOS
# ============================================================================
def crear_servicios(insumos_inventario):
    print('🦷 PASO 4: CREANDO CATÁLOGO DE SERVICIOS')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    # Importar modelos necesarios
    from tratamientos.models import CategoriaServicio
    
    # Crear categorías de servicios
    cat_general = CategoriaServicio.objects.create(
        nombre='Odontología General',
        descripcion='Servicios generales de odontología',
        orden=1
    )
    
    cat_ortodoncia = CategoriaServicio.objects.create(
        nombre='Ortodoncia',
        descripcion='Servicios de ortodoncia',
        orden=2
    )
    
    cat_endodoncia = CategoriaServicio.objects.create(
        nombre='Endodoncia',
        descripcion='Tratamientos de conducto',
        orden=3
    )
    
    cat_cirugia = CategoriaServicio.objects.create(
        nombre='Cirugía',
        descripcion='Procedimientos quirúrgicos',
        orden=4
    )
    
    cat_rehabilitacion = CategoriaServicio.objects.create(
        nombre='Rehabilitación',
        descripcion='Coronas, puentes e implantes',
        orden=5
    )
    
    cat_estetica = CategoriaServicio.objects.create(
        nombre='Estética Dental',
        descripcion='Blanqueamiento y estética',
        orden=6
    )
    
    print(f'  ✅ 6 categorías de servicios creadas')
    
    # Crear servicios
    servicios_data = [
        {
            'categoria': cat_general,
            'codigo_servicio': 'CONS-001',
            'nombre': 'Consulta General',
            'descripcion': 'Revisión general y diagnóstico',
            'precio_base': Decimal('50.00'),
            'tiempo_estimado': 30
        },
        {
            'categoria': cat_general,
            'codigo_servicio': 'LIMP-001',
            'nombre': 'Limpieza Dental',
            'descripcion': 'Profilaxis y limpieza dental completa',
            'precio_base': Decimal('80.00'),
            'tiempo_estimado': 45
        },
        {
            'categoria': cat_general,
            'codigo_servicio': 'REST-001',
            'nombre': 'Restauración Dental',
            'descripcion': 'Obturación con resina o amalgama',
            'precio_base': Decimal('150.00'),
            'tiempo_estimado': 60
        },
        {
            'categoria': cat_endodoncia,
            'codigo_servicio': 'ENDO-001',
            'nombre': 'Endodoncia',
            'descripcion': 'Tratamiento de conducto',
            'precio_base': Decimal('300.00'),
            'tiempo_estimado': 90
        },
        {
            'categoria': cat_cirugia,
            'codigo_servicio': 'EXTR-001',
            'nombre': 'Extracción Simple',
            'descripcion': 'Extracción de pieza dental simple',
            'precio_base': Decimal('100.00'),
            'tiempo_estimado': 30
        },
        {
            'categoria': cat_ortodoncia,
            'codigo_servicio': 'ORTO-001',
            'nombre': 'Instalación Ortodoncia',
            'descripcion': 'Instalación de brackets y arco',
            'precio_base': Decimal('200.00'),
            'tiempo_estimado': 120
        },
        {
            'categoria': cat_ortodoncia,
            'codigo_servicio': 'ORTO-002',
            'nombre': 'Control Ortodoncia',
            'descripcion': 'Control y ajuste mensual',
            'precio_base': Decimal('40.00'),
            'tiempo_estimado': 30
        },
        {
            'categoria': cat_rehabilitacion,
            'codigo_servicio': 'CORO-001',
            'nombre': 'Corona Dental',
            'descripcion': 'Colocación de corona',
            'precio_base': Decimal('400.00'),
            'tiempo_estimado': 90
        },
        {
            'categoria': cat_rehabilitacion,
            'codigo_servicio': 'IMPL-001',
            'nombre': 'Implante Dental',
            'descripcion': 'Colocación de implante',
            'precio_base': Decimal('800.00'),
            'tiempo_estimado': 120
        },
        {
            'categoria': cat_estetica,
            'codigo_servicio': 'BLAN-001',
            'nombre': 'Blanqueamiento Dental',
            'descripcion': 'Blanqueamiento profesional',
            'precio_base': Decimal('250.00'),
            'tiempo_estimado': 60
        }
    ]
    
    servicios_creados = {}
    for datos in servicios_data:
        servicio = Servicio.objects.create(**datos)
        servicios_creados[datos['codigo_servicio']] = servicio
    
    print(f'  ✅ {len(servicios_creados)} servicios creados')
    print()
    return servicios_creados


# ============================================================================
# PASO 5: CREAR CITAS (con nuevos campos motivo_tipo e item_plan)
# ============================================================================
def crear_citas(odontologo, pacientes, planes=None):
    print('📅 PASO 5: CREANDO CITAS')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    hoy = timezone.now().date()
    
    citas_data = [
        # Citas completadas (pasadas) - diferentes tipos
        {
            'paciente': pacientes[0],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy - timedelta(days=15), time(9, 0))),
            'motivo_tipo': 'CONSULTA',
            'motivo': 'Primera consulta - Dolor en muela inferior derecha',
            'observaciones': 'Primera consulta del paciente. Evaluación completa.',
            'estado': 'ATENDIDA'
        },
        {
            'paciente': pacientes[1],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy - timedelta(days=10), time(10, 0))),
            'motivo_tipo': 'LIMPIEZA',
            'motivo': 'Limpieza dental de rutina semestral',
            'observaciones': 'Limpieza profunda realizada exitosamente.',
            'estado': 'ATENDIDA'
        },
        {
            'paciente': pacientes[2],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy - timedelta(days=5), time(14, 0))),
            'motivo_tipo': 'URGENCIA',
            'motivo': 'Dolor agudo en molar - Urgencia',
            'observaciones': 'Atención de urgencia. Obturación temporal realizada.',
            'estado': 'ATENDIDA'
        },
        # Cita de hoy
        {
            'paciente': pacientes[3],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy, time(11, 0))),
            'motivo_tipo': 'REVISION',
            'motivo': 'Control post-tratamiento de endodoncia',
            'observaciones': 'Control de progreso general.',
            'estado': 'CONFIRMADA'
        },
        # Citas futuras - diferentes tipos
        {
            'paciente': pacientes[4],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=2), time(9, 0))),
            'motivo_tipo': 'CONSULTA',
            'motivo': 'Consulta para valoración de implante',
            'observaciones': '',
            'estado': 'PENDIENTE'
        },
        {
            'paciente': pacientes[0],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=7), time(15, 0))),
            'motivo_tipo': 'REVISION',
            'motivo': 'Control post consulta inicial',
            'observaciones': '',
            'estado': 'PENDIENTE'
        },
        {
            'paciente': pacientes[2],
            'odontologo': odontologo,
            'fecha_hora': timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=10), time(16, 0))),
            'motivo_tipo': 'LIMPIEZA',
            'motivo': 'Limpieza dental programada',
            'observaciones': '',
            'estado': 'PENDIENTE'
        }
    ]
    
    citas_creadas = []
    for datos in citas_data:
        cita = Cita.objects.create(**datos)
        citas_creadas.append(cita)
    
    # Resumen por tipo
    tipos_count = {}
    for cita in citas_creadas:
        tipo = cita.get_motivo_tipo_display()
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    print(f'  ✅ {len(citas_creadas)} citas creadas')
    print(f'      - Atendidas: {sum(1 for c in citas_creadas if c.estado == "ATENDIDA")}')
    print(f'      - Confirmadas: {sum(1 for c in citas_creadas if c.estado == "CONFIRMADA")}')
    print(f'      - Pendientes: {sum(1 for c in citas_creadas if c.estado == "PENDIENTE")}')
    print(f'      Por tipo:')
    for tipo, count in tipos_count.items():
        print(f'        • {tipo}: {count}')
    print()
    return citas_creadas


# ============================================================================
# PASO 6: CREAR EPISODIOS DE ATENCIÓN
# ============================================================================
def crear_episodios(citas_atendidas, odontologo):
    print('📋 PASO 6: CREANDO EPISODIOS DE ATENCIÓN')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    episodios_data = [
        {
            'cita': citas_atendidas[0],
            'motivo_consulta': 'Dolor leve en molar superior derecho',
            'diagnostico': 'Caries incipiente en pieza 16. Paciente refiere sensibilidad al frío.',
            'descripcion_procedimiento': 'Se realizó valoración completa. Se programó restauración dental para próxima cita.',
            'notas_privadas': 'PA: 120/80, FC: 72. Recomendado: Ibuprofeno 400mg cada 8h si hay dolor.'
        },
        {
            'cita': citas_atendidas[1],
            'motivo_consulta': 'Limpieza dental programada',
            'diagnostico': 'Buena higiene oral, presencia de sarro en zona posterior.',
            'descripcion_procedimiento': 'Profilaxis completa realizada con éxito. Se eliminó sarro acumulado. Se dieron instrucciones de técnica de cepillado mejorada.',
            'notas_privadas': 'PA: 118/75, FC: 68. Indicado: Enjuague bucal con clorhexidina 0.12% por 7 días.'
        },
        {
            'cita': citas_atendidas[2],
            'motivo_consulta': 'Restauración programada',
            'diagnostico': 'Caries profunda en pieza 36 sin compromiso pulpar.',
            'descripcion_procedimiento': 'Restauración con resina compuesta en pieza 36. Se usó anestesia local. Paciente toleró bien el procedimiento.',
            'notas_privadas': 'PA: 122/78, FC: 75. Medicado: Paracetamol 500mg si hay molestia post-procedimiento.'
        }
    ]
    
    episodios_creados = []
    for datos in episodios_data:
        # Obtener historial del paciente
        historial = HistorialClinico.objects.get(paciente=datos['cita'].paciente)
        
        episodio = EpisodioAtencion.objects.create(
            historial_clinico=historial,
            odontologo=odontologo,
            motivo_consulta=datos['motivo_consulta'],
            diagnostico=datos['diagnostico'],
            descripcion_procedimiento=datos['descripcion_procedimiento'],
            notas_privadas=datos['notas_privadas']
        )
        episodios_creados.append(episodio)
    
    print(f'  ✅ {len(episodios_creados)} episodios de atención creados')
    print()
    return episodios_creados


# ============================================================================
# PASO 7: CREAR PLANES DE TRATAMIENTO
# ============================================================================
def crear_planes(pacientes, servicios, odontologo):
    print('📝 PASO 7: CREANDO PLANES DE TRATAMIENTO')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    # Plan 1: Ortodoncia para paciente 1 (ACEPTADO)
    plan1 = PlanDeTratamiento.objects.create(
        paciente=pacientes[1],
        odontologo=odontologo,
        titulo='Plan de Ortodoncia Completa',
        descripcion='Tratamiento de ortodoncia con brackets metálicos, duración estimada 18 meses. Paciente adulto joven, cooperador.',
        estado='ACEPTADO'
    )
    
    # Ítems del plan 1
    ItemPlanTratamiento.objects.create(
        plan=plan1,
        servicio=servicios['CONS-001'],
        orden=1,
        notas='Valoración inicial de ortodoncia',
        fecha_estimada=timezone.now().date() - timedelta(days=30),
        estado='COMPLETADO',
        precio_servicio_snapshot=servicios['CONS-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('10.00'),
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    ItemPlanTratamiento.objects.create(
        plan=plan1,
        servicio=servicios['ORTO-001'],
        orden=2,
        notas='Instalación de brackets metálicos',
        fecha_estimada=timezone.now().date() + timedelta(days=7),
        estado='PENDIENTE',
        precio_servicio_snapshot=servicios['ORTO-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('130.00'),  # Incluye brackets
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    # 6 controles mensuales
    for i in range(6):
        ItemPlanTratamiento.objects.create(
            plan=plan1,
            servicio=servicios['ORTO-002'],
            orden=3 + i,
            notas=f'Control mensual #{i+1}',
            fecha_estimada=timezone.now().date() + timedelta(days=30 * (i+1)),
            estado='PENDIENTE',
            precio_servicio_snapshot=servicios['ORTO-002'].precio_base,
            precio_materiales_fijos_snapshot=Decimal('5.00'),
            precio_insumo_seleccionado_snapshot=Decimal('0.00')
        )
    
    plan1.actualizar_progreso()
    print(f'  ✅ Plan 1: Ortodoncia (ACEPTADO) - {plan1.items.count()} ítems')
    
    # Plan 2: Rehabilitación para paciente 3 (PROPUESTO)
    plan2 = PlanDeTratamiento.objects.create(
        paciente=pacientes[2],
        odontologo=odontologo,
        titulo='Plan de Rehabilitación Oral',
        descripcion='Tratamiento integral: endodoncia + corona. Paciente requiere recuperar función masticatoria.',
        estado='PROPUESTO'
    )
    
    ItemPlanTratamiento.objects.create(
        plan=plan2,
        servicio=servicios['ENDO-001'],
        orden=1,
        notas='Endodoncia en pieza 26',
        fecha_estimada=timezone.now().date() + timedelta(days=14),
        estado='PENDIENTE',
        precio_servicio_snapshot=servicios['ENDO-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('80.00'),
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    ItemPlanTratamiento.objects.create(
        plan=plan2,
        servicio=servicios['CORO-001'],
        orden=2,
        notas='Corona de porcelana en pieza 26',
        fecha_estimada=timezone.now().date() + timedelta(days=28),
        estado='PENDIENTE',
        precio_servicio_snapshot=servicios['CORO-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('400.00'),  # Incluye corona
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    plan2.actualizar_progreso()
    print(f'  ✅ Plan 2: Rehabilitación (PROPUESTO) - {plan2.items.count()} ítems')
    
    # Plan 3: Implante para paciente 4 (PRESENTADO)
    plan3 = PlanDeTratamiento.objects.create(
        paciente=pacientes[3],
        odontologo=odontologo,
        titulo='Plan de Implante Dental',
        descripcion='Colocación de implante en pieza ausente. Paciente con buena salud oral general.',
        estado='PRESENTADO'
    )
    
    ItemPlanTratamiento.objects.create(
        plan=plan3,
        servicio=servicios['IMPL-001'],
        orden=1,
        notas='Colocación de implante en zona de pieza 46',
        fecha_estimada=timezone.now().date() + timedelta(days=21),
        estado='PENDIENTE',
        precio_servicio_snapshot=servicios['IMPL-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('700.00'),  # Incluye implante
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    ItemPlanTratamiento.objects.create(
        plan=plan3,
        servicio=servicios['CORO-001'],
        orden=2,
        notas='Corona sobre implante (después de 3 meses)',
        fecha_estimada=timezone.now().date() + timedelta(days=111),
        estado='PENDIENTE',
        precio_servicio_snapshot=servicios['CORO-001'].precio_base,
        precio_materiales_fijos_snapshot=Decimal('400.00'),
        precio_insumo_seleccionado_snapshot=Decimal('0.00')
    )
    
    plan3.actualizar_progreso()
    print(f'  ✅ Plan 3: Implante (PRESENTADO) - {plan3.items.count()} ítems')
    
    print()
    return [plan1, plan2, plan3]


# ============================================================================
# PASO 7B: CREAR CITAS VINCULADAS A PLANES
# ============================================================================
def crear_citas_plan(odontologo, pacientes, planes):
    print('📅 PASO 7B: CREANDO CITAS VINCULADAS A PLANES DE TRATAMIENTO')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    hoy = timezone.now().date()
    citas_plan = []
    
    # Plan 1 (Ortodoncia) - paciente 1 - tiene item COMPLETADO y varios PENDIENTES
    plan_orto = planes[0]
    items_orto = list(plan_orto.items.filter(estado='PENDIENTE').order_by('orden'))
    
    if len(items_orto) >= 2:
        # Cita para instalación de brackets (próxima semana)
        cita_instalacion = Cita.objects.create(
            paciente=pacientes[1],
            odontologo=odontologo,
            fecha_hora=timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=7), time(14, 0))),
            motivo_tipo='PLAN',
            motivo='Instalación de brackets según plan de ortodoncia',
            item_plan=items_orto[0],  # Instalación
            observaciones='Cita vinculada al plan de ortodoncia',
            estado='CONFIRMADA'
        )
        citas_plan.append(cita_instalacion)
        print(f'  ✅ Cita PLAN: Instalación de brackets (paciente {pacientes[1].usuario.nombre})')
        
        # Cita para primer control (mes siguiente)
        cita_control1 = Cita.objects.create(
            paciente=pacientes[1],
            odontologo=odontologo,
            fecha_hora=timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=35), time(10, 0))),
            motivo_tipo='PLAN',
            motivo='Primer control mensual de ortodoncia',
            item_plan=items_orto[1],  # Primer control
            observaciones='Primer ajuste mensual programado',
            estado='PENDIENTE'
        )
        citas_plan.append(cita_control1)
        print(f'  ✅ Cita PLAN: Primer control ortodoncia (paciente {pacientes[1].usuario.nombre})')
    
    # Plan 2 (Rehabilitación) - paciente 2 - todos PENDIENTES
    plan_rehab = planes[1]
    items_rehab = list(plan_rehab.items.filter(estado='PENDIENTE').order_by('orden'))
    
    if len(items_rehab) >= 1:
        # Cita para endodoncia (dentro de 2 semanas)
        cita_endo = Cita.objects.create(
            paciente=pacientes[2],
            odontologo=odontologo,
            fecha_hora=timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=14), time(9, 30))),
            motivo_tipo='PLAN',
            motivo='Endodoncia en pieza 26 según plan de tratamiento',
            item_plan=items_rehab[0],  # Endodoncia
            observaciones='Primera sesión de endodoncia',
            estado='PENDIENTE'
        )
        citas_plan.append(cita_endo)
        print(f'  ✅ Cita PLAN: Endodoncia (paciente {pacientes[2].usuario.nombre})')
    
    # Plan 3 (Implante) - paciente 3 - todos PENDIENTES  
    plan_impl = planes[2]
    items_impl = list(plan_impl.items.filter(estado='PENDIENTE').order_by('orden'))
    
    if len(items_impl) >= 1:
        # Cita para colocación de implante (3 semanas)
        cita_impl = Cita.objects.create(
            paciente=pacientes[3],
            odontologo=odontologo,
            fecha_hora=timezone.make_aware(timezone.datetime.combine(hoy + timedelta(days=21), time(11, 0))),
            motivo_tipo='PLAN',
            motivo='Colocación de implante dental según plan',
            item_plan=items_impl[0],  # Implante
            observaciones='Cirugía de implante programada',
            estado='PENDIENTE'
        )
        citas_plan.append(cita_impl)
        print(f'  ✅ Cita PLAN: Colocación implante (paciente {pacientes[3].usuario.nombre})')
    
    print(f'\n  ✅ Total citas tipo PLAN creadas: {len(citas_plan)}')
    print(f'      - CONFIRMADA: {sum(1 for c in citas_plan if c.estado == "CONFIRMADA")}')
    print(f'      - PENDIENTE: {sum(1 for c in citas_plan if c.estado == "PENDIENTE")}')
    print()
    return citas_plan


# ============================================================================
# PASO 8: CREAR FACTURAS Y PAGOS
# ============================================================================
def crear_facturas_pagos(citas_completadas):
    print('💰 PASO 8: CREANDO FACTURAS Y PAGOS')
    print('-' * 80)
    
    connection.set_schema('clinica_demo')
    
    facturas_creadas = []
    pagos_creados = []
    
    # Factura 1: Consulta general
    paciente1_perfil = citas_completadas[0].paciente
    factura1 = Factura.objects.create(
        paciente=paciente1_perfil,
        nit_ci='1234567',
        razon_social=paciente1_perfil.usuario.full_name,
        monto_total=Decimal('50.00'),
        monto_pagado=Decimal('50.00'),
        estado='PAGADA'
    )
    
    Pago.objects.create(
        factura=factura1,
        paciente=paciente1_perfil,
        monto_pagado=Decimal('50.00'),
        metodo_pago='EFECTIVO',
        estado_pago='COMPLETADO',
        referencia_transaccion='PAGO-001'
    )
    
    facturas_creadas.append(factura1)
    print(f'  ✅ Factura 1: Bs. {factura1.monto_total} (PAGADA)')
    
    # Factura 2: Limpieza dental
    paciente2_perfil = citas_completadas[1].paciente
    factura2 = Factura.objects.create(
        paciente=paciente2_perfil,
        nit_ci='7654321',
        razon_social=paciente2_perfil.usuario.full_name,
        monto_total=Decimal('80.00'),
        monto_pagado=Decimal('80.00'),
        estado='PAGADA'
    )
    
    Pago.objects.create(
        factura=factura2,
        paciente=paciente2_perfil,
        monto_pagado=Decimal('80.00'),
        metodo_pago='TARJETA',
        estado_pago='COMPLETADO',
        referencia_transaccion='PAGO-002'
    )
    
    facturas_creadas.append(factura2)
    print(f'  ✅ Factura 2: Bs. {factura2.monto_total} (PAGADA)')
    
    # Factura 3: Restauración dental (pago parcial)
    paciente3_perfil = citas_completadas[2].paciente
    factura3 = Factura.objects.create(
        paciente=paciente3_perfil,
        nit_ci='9876543',
        razon_social=paciente3_perfil.usuario.full_name,
        monto_total=Decimal('225.00'),
        monto_pagado=Decimal('150.00'),
        estado='PENDIENTE'
    )
    
    # Pago parcial
    Pago.objects.create(
        factura=factura3,
        paciente=paciente3_perfil,
        monto_pagado=Decimal('150.00'),
        metodo_pago='EFECTIVO',
        estado_pago='COMPLETADO',
        referencia_transaccion='PAGO-003'
    )
    
    facturas_creadas.append(factura3)
    print(f'  ✅ Factura 3: Bs. {factura3.monto_total} (PENDIENTE - Pagado Bs. 150)')
    
    print()
    return facturas_creadas


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    try:
        print('📋 INICIANDO POBLADO DEL SISTEMA')
        print('Tenant: clinica-demo')
        print()
        
        # Paso 1: Limpiar tenant
        limpiar_tenant()
        
        # Paso 2: Usuarios
        odontologo, perfil_odontologo, pacientes = crear_usuarios()
        
        # Paso 3: Inventario
        insumos_inventario = crear_inventario()
        
        # Paso 4: Servicios
        servicios = crear_servicios(insumos_inventario)
        
        # Paso 5: Citas (antes de planes para poder vincular después)
        citas = crear_citas(perfil_odontologo, pacientes)
        citas_atendidas = [c for c in citas if c.estado == 'ATENDIDA']
        
        # Paso 6: Episodios
        episodios = crear_episodios(citas_atendidas, perfil_odontologo)
        
        # Paso 7: Planes
        planes = crear_planes(pacientes, servicios, perfil_odontologo)
        
        # Paso 7b: Crear citas vinculadas a planes (citas tipo PLAN)
        citas_plan = crear_citas_plan(perfil_odontologo, pacientes, planes)
        
        # Paso 8: Facturas
        facturas = crear_facturas_pagos(citas_atendidas)
        
        # ============================================================================
        # RESUMEN FINAL
        # ============================================================================
        print('=' * 80)
        print('✅ SISTEMA POBLADO EXITOSAMENTE')
        print('=' * 80)
        print()
        
        print('📊 RESUMEN DE DATOS CREADOS:')
        print('-' * 80)
        print(f'   Usuarios (tenant):       {1 + len(pacientes)} (1 odontólogo + {len(pacientes)} pacientes)')
        print(f'  📦 Categorías Insumo:       4')
        print(f'  📦 Insumos:                 {len(insumos_inventario)}')
        print(f'  🦷 Servicios:               {len(servicios)}')
        print(f'  📅 Citas:                   {len(citas) + len(citas_plan)}')
        print(f'      • Normales:             {len(citas)}')
        print(f'      • Vinculadas a Plan:    {len(citas_plan)}')
        print(f'  📋 Episodios:               {len(episodios)}')
        print(f'  📝 Planes de tratamiento:   {len(planes)}')
        print(f'  💰 Facturas:                {len(facturas)}')
        print()
        
        print('🔑 CREDENCIALES:')
        print('-' * 80)
        print(f'  🦷 Odontólogo (tenant clinica-demo):')
        print(f'     📧 odontologo@clinica-demo.com')
        print(f'     🔑 odontologo123')
        print()
        print(f'  👤 Pacientes (tenant clinica-demo):')
        for i in range(1, 6):
            print(f'     📧 paciente{i}@test.com / 🔑 paciente123')
        print()
        
        print('🎯 ESTADO DE PLANES:')
        print('-' * 80)
        for plan in planes:
            total = sum(item.precio_total for item in plan.items.all())
            print(f'  📝 {plan.titulo}')
            print(f'     Estado: {plan.get_estado_display()}')
            print(f'     Ítems: {plan.items.count()}')
            print(f'     Total: ${total}')
            print(f'     Progreso: {plan.porcentaje_completado}%')
            print()
        
        print('💳 ESTADO DE FACTURAS:')
        print('-' * 80)
        total_facturado = sum(f.monto_total for f in facturas)
        total_pagado = sum(f.monto_pagado for f in facturas)
        print(f'  💰 Total Facturado:  Bs. {total_facturado}')
        print(f'  ✅ Total Pagado:     Bs. {total_pagado}')
        print(f'  ⏳ Total Pendiente:  Bs. {total_facturado - total_pagado}')
        print()
        
        print('=' * 80)
        print('🎉 ¡SISTEMA LISTO PARA USAR!')
        print('=' * 80)
        print()
        print('📌 PRÓXIMOS PASOS:')
        print('  1. Iniciar servidor: python manage.py runserver')
        print('  2. Login con credenciales del odontólogo')
        print('  3. Explorar agenda, pacientes, planes y facturas')
        print()
        
    except Exception as e:
        print()
        print('❌ ERROR AL POBLAR LA BASE DE DATOS:')
        print(f'   {str(e)}')
        print()
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
