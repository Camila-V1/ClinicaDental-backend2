"""
Módulo para poblar servicios dentales (tratamientos)
"""

from tratamientos.models import Servicio, CategoriaServicio
from decimal import Decimal


def poblar_tratamientos():
    """
    Crea servicios y categorías dentales
    
    Returns:
        list: Lista de servicios creados
    """
    servicios_creados = []
    
    print("\n  📋 Creando servicios dentales...")
    
    # =========================================================================
    # 1. CATEGORÍAS DE SERVICIOS
    # =========================================================================
    print("  → Categorías...")
    
    categorias_data = [
        {'nombre': 'Odontología General', 'descripcion': 'Tratamientos básicos y preventivos', 'orden': 1},
        {'nombre': 'Endodoncia', 'descripcion': 'Tratamiento de conducto y pulpa dental', 'orden': 2},
        {'nombre': 'Periodoncia', 'descripcion': 'Tratamiento de encías y soporte dental', 'orden': 3},
        {'nombre': 'Ortodoncia', 'descripcion': 'Corrección de posición dental', 'orden': 4},
        {'nombre': 'Odontopediatría', 'descripcion': 'Tratamientos para niños', 'orden': 5},
        {'nombre': 'Cirugía Oral', 'descripcion': 'Extracciones y procedimientos quirúrgicos', 'orden': 6},
        {'nombre': 'Estética Dental', 'descripcion': 'Blanqueamiento y cosmética dental', 'orden': 7},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria, created = CategoriaServicio.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'orden': cat_data['orden'],
                'activo': True
            }
        )
        categorias[cat_data['nombre']] = categoria
        if created:
            print(f"    ✓ Categoría: {categoria.nombre}")
    
    # =========================================================================
    # 2. SERVICIOS POR CATEGORÍA
    # =========================================================================
    print("  → Servicios...")
    
    servicios_data = [
        # ODONTOLOGÍA GENERAL
        {
            'categoria': 'Odontología General',
            'codigo_servicio': 'ODG-001',
            'nombre': 'Consulta Odontológica',
            'descripcion': 'Consulta general de diagnóstico',
            'precio_base': Decimal('150.00'),
            'tiempo_estimado': 30,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Odontología General',
            'codigo_servicio': 'ODG-002',
            'nombre': 'Limpieza Dental',
            'descripcion': 'Profilaxis y limpieza dental profesional',
            'precio_base': Decimal('250.00'),
            'tiempo_estimado': 45,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Odontología General',
            'codigo_servicio': 'ODG-003',
            'nombre': 'Obturación Simple',
            'descripcion': 'Restauración con resina compuesta',
            'precio_base': Decimal('300.00'),
            'tiempo_estimado': 60,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Odontología General',
            'codigo_servicio': 'ODG-004',
            'nombre': 'Fluorización',
            'descripcion': 'Aplicación de flúor preventivo',
            'precio_base': Decimal('100.00'),
            'tiempo_estimado': 15,
            'requiere_cita_previa': False
        },
        
        # ENDODONCIA
        {
            'categoria': 'Endodoncia',
            'codigo_servicio': 'ENDO-001',
            'nombre': 'Endodoncia Unirradicular',
            'descripcion': 'Tratamiento de conducto en diente de una raíz',
            'precio_base': Decimal('800.00'),
            'tiempo_estimado': 90,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Endodoncia',
            'codigo_servicio': 'ENDO-002',
            'nombre': 'Endodoncia Birradicular',
            'descripcion': 'Tratamiento de conducto en diente de dos raíces',
            'precio_base': Decimal('1000.00'),
            'tiempo_estimado': 120,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Endodoncia',
            'codigo_servicio': 'ENDO-003',
            'nombre': 'Endodoncia Multirradicular',
            'descripcion': 'Tratamiento de conducto en molar',
            'precio_base': Decimal('1200.00'),
            'tiempo_estimado': 150,
            'requiere_cita_previa': True
        },
        
        # PERIODONCIA
        {
            'categoria': 'Periodoncia',
            'codigo_servicio': 'PERIO-001',
            'nombre': 'Curetaje Dental',
            'descripcion': 'Limpieza profunda por cuadrante',
            'precio_base': Decimal('400.00'),
            'tiempo_estimado': 60,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Periodoncia',
            'codigo_servicio': 'PERIO-002',
            'nombre': 'Cirugía Periodontal',
            'descripcion': 'Cirugía de encías',
            'precio_base': Decimal('1500.00'),
            'tiempo_estimado': 120,
            'requiere_cita_previa': True,
            'requiere_autorizacion': True
        },
        
        # ORTODONCIA
        {
            'categoria': 'Ortodoncia',
            'codigo_servicio': 'ORTO-001',
            'nombre': 'Brackets Metálicos',
            'descripcion': 'Instalación de brackets metálicos completos',
            'precio_base': Decimal('2500.00'),
            'tiempo_estimado': 180,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Ortodoncia',
            'codigo_servicio': 'ORTO-002',
            'nombre': 'Control de Ortodoncia',
            'descripcion': 'Control mensual y ajuste de brackets',
            'precio_base': Decimal('200.00'),
            'tiempo_estimado': 30,
            'requiere_cita_previa': True
        },
        
        # ODONTOPEDIATRÍA
        {
            'categoria': 'Odontopediatría',
            'codigo_servicio': 'PEDIA-001',
            'nombre': 'Consulta Pediátrica',
            'descripcion': 'Consulta odontológica para niños',
            'precio_base': Decimal('120.00'),
            'tiempo_estimado': 30,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Odontopediatría',
            'codigo_servicio': 'PEDIA-002',
            'nombre': 'Sellantes Dentales',
            'descripcion': 'Sellado preventivo de fisuras',
            'precio_base': Decimal('80.00'),
            'tiempo_estimado': 20,
            'requiere_cita_previa': True
        },
        
        # CIRUGÍA ORAL
        {
            'categoria': 'Cirugía Oral',
            'codigo_servicio': 'CIR-001',
            'nombre': 'Extracción Simple',
            'descripcion': 'Extracción de pieza dental simple',
            'precio_base': Decimal('300.00'),
            'tiempo_estimado': 30,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Cirugía Oral',
            'codigo_servicio': 'CIR-002',
            'nombre': 'Extracción Compleja',
            'descripcion': 'Extracción quirúrgica de pieza dental',
            'precio_base': Decimal('600.00'),
            'tiempo_estimado': 60,
            'requiere_cita_previa': True,
            'requiere_autorizacion': True
        },
        {
            'categoria': 'Cirugía Oral',
            'codigo_servicio': 'CIR-003',
            'nombre': 'Extracción de Cordal',
            'descripcion': 'Extracción de muela del juicio',
            'precio_base': Decimal('800.00'),
            'tiempo_estimado': 90,
            'requiere_cita_previa': True,
            'requiere_autorizacion': True
        },
        
        # ESTÉTICA DENTAL
        {
            'categoria': 'Estética Dental',
            'codigo_servicio': 'EST-001',
            'nombre': 'Blanqueamiento Dental',
            'descripcion': 'Blanqueamiento profesional',
            'precio_base': Decimal('1200.00'),
            'tiempo_estimado': 90,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Estética Dental',
            'codigo_servicio': 'EST-002',
            'nombre': 'Carilla Dental',
            'descripcion': 'Carilla de porcelana por pieza',
            'precio_base': Decimal('2000.00'),
            'tiempo_estimado': 120,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Estética Dental',
            'codigo_servicio': 'EST-003',
            'nombre': 'Corona de Porcelana',
            'descripcion': 'Corona dental de porcelana',
            'precio_base': Decimal('1800.00'),
            'tiempo_estimado': 120,
            'requiere_cita_previa': True
        },
        {
            'categoria': 'Estética Dental',
            'codigo_servicio': 'EST-004',
            'nombre': 'Incrustación',
            'descripcion': 'Incrustación estética (inlay/onlay)',
            'precio_base': Decimal('1500.00'),
            'tiempo_estimado': 90,
            'requiere_cita_previa': True
        },
    ]
    
    for servicio_data in servicios_data:
        categoria_nombre = servicio_data.pop('categoria')
        categoria = categorias[categoria_nombre]
        
        servicio, created = Servicio.objects.get_or_create(
            codigo_servicio=servicio_data['codigo_servicio'],
            defaults={
                'categoria': categoria,
                **servicio_data,
                'activo': True
            }
        )
        
        if created:
            servicios_creados.append(servicio)
            print(f"    ✓ {servicio.codigo_servicio}: {servicio.nombre} - Bs. {servicio.precio_base}")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    total_servicios = Servicio.objects.count()
    print(f"\n  ✅ Total servicios: {total_servicios}")
    
    # Estadísticas por categoría
    for cat_nombre, categoria in categorias.items():
        count = categoria.servicios.count()
        print(f"     - {cat_nombre}: {count} servicios")
    
    return list(Servicio.objects.all())


# Funciones auxiliares
def obtener_servicios_por_categoria(nombre_categoria):
    """Obtiene servicios filtrados por categoría"""
    return Servicio.objects.filter(
        categoria__nombre=nombre_categoria,
        activo=True
    ).order_by('nombre')


def obtener_servicio_por_codigo(codigo):
    """Busca un servicio por su código"""
    return Servicio.objects.filter(codigo_servicio=codigo).first()


def obtener_servicios_populares():
    """Retorna los servicios más comunes"""
    codigos_populares = ['ODG-001', 'ODG-002', 'ODG-003', 'CIR-001']
    return Servicio.objects.filter(codigo_servicio__in=codigos_populares)
