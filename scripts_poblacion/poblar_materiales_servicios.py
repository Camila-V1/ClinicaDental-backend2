"""
Módulo para poblar materiales de servicios (fijos y opcionales)
Asocia insumos con servicios para cálculo de precios dinámicos
"""

from tratamientos.models import (
    Servicio, MaterialServicioFijo, MaterialServicioOpcional
)
from inventario.models import Insumo, CategoriaInsumo
from decimal import Decimal


def poblar_materiales_servicios(servicios, insumos):
    """
    Crea relaciones entre servicios e insumos
    
    Args:
        servicios: Lista de Servicio
        insumos: Lista de Insumo
    
    Returns:
        tuple: (materiales_fijos, materiales_opcionales)
    """
    materiales_fijos = []
    materiales_opcionales = []
    
    print("\n  🧰 Creando materiales para servicios...")
    
    if not servicios or not insumos:
        print("  ⚠️  Faltan datos para crear materiales")
        return (materiales_fijos, materiales_opcionales)
    
    # Obtener categorías de insumos
    cat_anestesicos = CategoriaInsumo.objects.filter(nombre='Anestésicos').first()
    cat_obturacion = CategoriaInsumo.objects.filter(nombre='Materiales de Obturación').first()
    cat_endodoncia = CategoriaInsumo.objects.filter(nombre='Material de Endodoncia').first()
    cat_consumibles = CategoriaInsumo.objects.filter(nombre='Consumibles').first()
    
    # Obtener insumos específicos por código
    insumos_dict = {insumo.codigo: insumo for insumo in insumos}
    
    # =========================================================================
    # MATERIALES FIJOS: Insumos que SIEMPRE se usan en ciertos servicios
    # =========================================================================
    print("  → Materiales fijos...")
    
    # Mapeo de servicios a insumos fijos
    materiales_fijos_config = {
        'ODG-001': [  # Consulta Odontológica
            ('CONS-001', 1),  # Guantes
            ('CONS-003', 1),  # Mascarilla
        ],
        'ODG-002': [  # Limpieza Dental
            ('CONS-001', 2),  # Guantes
            ('CONS-003', 1),  # Mascarilla
            ('CONS-004', 1),  # Babero
        ],
        'ODG-003': [  # Obturación Simple
            ('ANES-001', 1),  # Lidocaína
            ('ANES-003', 2),  # Agujas
            ('CONS-001', 2),  # Guantes
            ('CONS-003', 1),  # Mascarilla
        ],
        'ENDO-001': [  # Endodoncia Unirradicular
            ('ANES-001', 2),  # Lidocaína
            ('ANES-003', 3),  # Agujas
            ('ENDO-001', 1),  # Limas
            ('ENDO-002', 3),  # Gutapercha
            ('ENDO-003', 1),  # Sellador
            ('ENDO-004', 0.1),  # Hipoclorito
            ('CONS-001', 3),  # Guantes
        ],
        'ENDO-002': [  # Endodoncia Birradicular
            ('ANES-001', 2),
            ('ANES-003', 3),
            ('ENDO-001', 1),
            ('ENDO-002', 5),
            ('ENDO-003', 1),
            ('ENDO-004', 0.15),
            ('CONS-001', 4),
        ],
        'ENDO-003': [  # Endodoncia Multirradicular
            ('ANES-001', 3),
            ('ANES-003', 4),
            ('ENDO-001', 1.5),
            ('ENDO-002', 8),
            ('ENDO-003', 1),
            ('ENDO-004', 0.2),
            ('CONS-001', 5),
        ],
        'CIR-001': [  # Extracción Simple
            ('ANES-001', 2),
            ('ANES-003', 2),
            ('CONS-001', 2),
            ('CONS-003', 1),
            ('CONS-007', 5),  # Gasas
        ],
        'CIR-002': [  # Extracción Compleja
            ('ANES-001', 3),
            ('ANES-003', 3),
            ('CONS-001', 3),
            ('CONS-003', 2),
            ('CONS-007', 10),
        ],
        'CIR-003': [  # Extracción de Cordal
            ('ANES-002', 4),  # Articaína (más potente)
            ('ANES-003', 4),
            ('CONS-001', 4),
            ('CONS-003', 2),
            ('CONS-007', 15),
        ],
        'EST-001': [  # Blanqueamiento
            ('CONS-001', 2),
            ('CONS-003', 1),
            ('CONS-004', 1),
        ],
        'EST-002': [  # Carilla Dental
            ('IMP-001', 0.5),  # Silicona pesada
            ('IMP-002', 0.5),  # Silicona liviana
            ('CONS-001', 2),
        ],
        'EST-003': [  # Corona de Porcelana
            ('IMP-001', 1),
            ('IMP-002', 1),
            ('CONS-001', 2),
        ],
    }
    
    for codigo_servicio, materiales in materiales_fijos_config.items():
        servicio = next((s for s in servicios if s.codigo_servicio == codigo_servicio), None)
        
        if not servicio:
            continue
        
        for codigo_insumo, cantidad in materiales:
            insumo = insumos_dict.get(codigo_insumo)
            
            if insumo:
                material, created = MaterialServicioFijo.objects.get_or_create(
                    servicio=servicio,
                    insumo=insumo,
                    defaults={
                        'cantidad': Decimal(str(cantidad)),
                        'es_obligatorio': True,
                        'notas': f'Material necesario para {servicio.nombre}'
                    }
                )
                
                if created:
                    materiales_fijos.append(material)
    
    print(f"    ✓ {len(materiales_fijos)} materiales fijos creados")
    
    # =========================================================================
    # MATERIALES OPCIONALES: Categorías de insumos entre las que elegir
    # =========================================================================
    print("  → Materiales opcionales...")
    
    # Mapeo de servicios a categorías opcionales
    materiales_opcionales_config = [
        # Servicios que requieren materiales de obturación
        ('ODG-003', cat_obturacion, 1, 'Tipo de Resina', 'Elegir resina según tono dental'),
        ('ODG-004', cat_obturacion, 0.5, 'Material de Fluorización', 'Elegir material'),
        
        # Servicios que permiten elegir anestésico
        ('PERIO-001', cat_anestesicos, 2, 'Tipo de Anestésico', 'Elegir según sensibilidad'),
        ('PERIO-002', cat_anestesicos, 3, 'Tipo de Anestésico', 'Elegir según procedimiento'),
    ]
    
    for config in materiales_opcionales_config:
        codigo_servicio, categoria, cantidad, nombre, notas = config
        
        if not categoria:
            continue
        
        servicio = next((s for s in servicios if s.codigo_servicio == codigo_servicio), None)
        
        if servicio:
            material, created = MaterialServicioOpcional.objects.get_or_create(
                servicio=servicio,
                categoria_insumo=categoria,
                defaults={
                    'cantidad': Decimal(str(cantidad)),
                    'es_obligatorio': False,
                    'nombre_personalizado': nombre,
                    'notas': notas
                }
            )
            
            if created:
                materiales_opcionales.append(material)
    
    print(f"    ✓ {len(materiales_opcionales)} materiales opcionales creados")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print(f"\n  ✅ Total materiales configurados:")
    print(f"     • Materiales fijos: {len(materiales_fijos)}")
    print(f"     • Materiales opcionales: {len(materiales_opcionales)}")
    
    # Estadísticas
    servicios_con_materiales = set()
    for mat in materiales_fijos:
        servicios_con_materiales.add(mat.servicio.codigo_servicio)
    for mat in materiales_opcionales:
        servicios_con_materiales.add(mat.servicio.codigo_servicio)
    
    print(f"     • Servicios configurados: {len(servicios_con_materiales)}")
    
    return (materiales_fijos, materiales_opcionales)
