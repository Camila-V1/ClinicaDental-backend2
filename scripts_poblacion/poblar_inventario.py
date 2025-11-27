"""
Módulo para poblar inventario de insumos dentales
"""

from inventario.models import Insumo, CategoriaInsumo
from decimal import Decimal


def poblar_inventario():
    """
    Crea categorías e insumos dentales
    
    Returns:
        tuple: (categorias_creadas, insumos_creados)
    """
    categorias_creadas = []
    insumos_creados = []
    
    print("\n  📦 Creando inventario...")
    
    # =========================================================================
    # 1. CATEGORÍAS DE INSUMOS
    # =========================================================================
    print("  → Categorías...")
    
    categorias_data = [
        {'nombre': 'Instrumental', 'descripcion': 'Instrumentos y herramientas dentales'},
        {'nombre': 'Materiales de Obturación', 'descripcion': 'Resinas, amalgamas y materiales de restauración'},
        {'nombre': 'Anestésicos', 'descripcion': 'Anestesia local y complementos'},
        {'nombre': 'Material de Endodoncia', 'descripcion': 'Materiales para tratamiento de conductos'},
        {'nombre': 'Material de Impresión', 'descripcion': 'Siliconas, alginatos y materiales de moldeo'},
        {'nombre': 'Desinfección y Esterilización', 'descripcion': 'Productos de limpieza y esterilización'},
        {'nombre': 'Consumibles', 'descripcion': 'Guantes, mascarillas, gasas y descartables'},
        {'nombre': 'Radiología', 'descripcion': 'Materiales para rayos X dental'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'activo': True
            }
        )
        categorias[cat_data['nombre']] = categoria
        if created:
            categorias_creadas.append(categoria)
            print(f"    ✓ {categoria.nombre}")
    
    # =========================================================================
    # 2. INSUMOS POR CATEGORÍA
    # =========================================================================
    print("  → Insumos...")
    
    insumos_data = [
        # INSTRUMENTAL
        {'categoria': 'Instrumental', 'codigo': 'INST-001', 'nombre': 'Espejo Bucal #5',
         'precio_costo': Decimal('15.00'), 'precio_venta': Decimal('25.00'), 
         'stock_actual': Decimal('50'), 'stock_minimo': Decimal('10'), 'unidad_medida': 'unidad'},
        {'categoria': 'Instrumental', 'codigo': 'INST-002', 'nombre': 'Pinza Porta-Amalgama',
         'precio_costo': Decimal('80.00'), 'precio_venta': Decimal('120.00'),
         'stock_actual': Decimal('20'), 'stock_minimo': Decimal('5'), 'unidad_medida': 'unidad'},
        {'categoria': 'Instrumental', 'codigo': 'INST-003', 'nombre': 'Excavador Dental',
         'precio_costo': Decimal('45.00'), 'precio_venta': Decimal('70.00'),
         'stock_actual': Decimal('30'), 'stock_minimo': Decimal('8'), 'unidad_medida': 'unidad'},
        
        # MATERIALES DE OBTURACIÓN
        {'categoria': 'Materiales de Obturación', 'codigo': 'OBT-001', 'nombre': 'Resina Compuesta A2 (Jeringa 4g)',
         'precio_costo': Decimal('120.00'), 'precio_venta': Decimal('180.00'),
         'stock_actual': Decimal('45'), 'stock_minimo': Decimal('15'), 'unidad_medida': 'jeringa'},
        {'categoria': 'Materiales de Obturación', 'codigo': 'OBT-002', 'nombre': 'Resina Compuesta A3 (Jeringa 4g)',
         'precio_costo': Decimal('120.00'), 'precio_venta': Decimal('180.00'),
         'stock_actual': Decimal('38'), 'stock_minimo': Decimal('15'), 'unidad_medida': 'jeringa'},
        {'categoria': 'Materiales de Obturación', 'codigo': 'OBT-003', 'nombre': 'Adhesivo Dental Universal',
         'precio_costo': Decimal('200.00'), 'precio_venta': Decimal('300.00'),
         'stock_actual': Decimal('25'), 'stock_minimo': Decimal('10'), 'unidad_medida': 'frasco'},
        {'categoria': 'Materiales de Obturación', 'codigo': 'OBT-004', 'nombre': 'Ácido Grabador 37%',
         'precio_costo': Decimal('80.00'), 'precio_venta': Decimal('120.00'),
         'stock_actual': Decimal('30'), 'stock_minimo': Decimal('10'), 'unidad_medida': 'frasco'},
        
        # ANESTÉSICOS
        {'categoria': 'Anestésicos', 'codigo': 'ANES-001', 'nombre': 'Lidocaína 2% con Epinefrina (Caja x 50)',
         'precio_costo': Decimal('150.00'), 'precio_venta': Decimal('220.00'),
         'stock_actual': Decimal('80'), 'stock_minimo': Decimal('20'), 'unidad_medida': 'caja'},
        {'categoria': 'Anestésicos', 'codigo': 'ANES-002', 'nombre': 'Articaína 4% (Caja x 50)',
         'precio_costo': Decimal('280.00'), 'precio_venta': Decimal('400.00'),
         'stock_actual': Decimal('40'), 'stock_minimo': Decimal('15'), 'unidad_medida': 'caja'},
        {'categoria': 'Anestésicos', 'codigo': 'ANES-003', 'nombre': 'Agujas Dentales Cortas 27G (Caja x 100)',
         'precio_costo': Decimal('60.00'), 'precio_venta': Decimal('90.00'),
         'stock_actual': Decimal('120'), 'stock_minimo': Decimal('30'), 'unidad_medida': 'caja'},
        
        # MATERIAL DE ENDODONCIA
        {'categoria': 'Material de Endodoncia', 'codigo': 'ENDO-001', 'nombre': 'Limas Endodónticas K-File Set',
         'precio_costo': Decimal('250.00'), 'precio_venta': Decimal('380.00'),
         'stock_actual': Decimal('15'), 'stock_minimo': Decimal('5'), 'unidad_medida': 'set'},
        {'categoria': 'Material de Endodoncia', 'codigo': 'ENDO-002', 'nombre': 'Gutapercha Puntas (Caja x 120)',
         'precio_costo': Decimal('120.00'), 'precio_venta': Decimal('180.00'),
         'stock_actual': Decimal('35'), 'stock_minimo': Decimal('10'), 'unidad_medida': 'caja'},
        {'categoria': 'Material de Endodoncia', 'codigo': 'ENDO-003', 'nombre': 'Sellador de Conductos',
         'precio_costo': Decimal('180.00'), 'precio_venta': Decimal('270.00'),
         'stock_actual': Decimal('20'), 'stock_minimo': Decimal('8'), 'unidad_medida': 'tubo'},
        {'categoria': 'Material de Endodoncia', 'codigo': 'ENDO-004', 'nombre': 'Hipoclorito de Sodio 5.25%',
         'precio_costo': Decimal('45.00'), 'precio_venta': Decimal('70.00'),
         'stock_actual': Decimal('50'), 'stock_minimo': Decimal('15'), 'unidad_medida': 'litro'},
        
        # MATERIAL DE IMPRESIÓN
        {'categoria': 'Material de Impresión', 'codigo': 'IMP-001', 'nombre': 'Silicona Pesada (Kit)',
         'precio_costo': Decimal('280.00'), 'precio_venta': Decimal('420.00'),
         'stock_actual': Decimal('18'), 'stock_minimo': Decimal('6'), 'unidad_medida': 'kit'},
        {'categoria': 'Material de Impresión', 'codigo': 'IMP-002', 'nombre': 'Silicona Liviana (Kit)',
         'precio_costo': Decimal('250.00'), 'precio_venta': Decimal('380.00'),
         'stock_actual': Decimal('22'), 'stock_minimo': Decimal('6'), 'unidad_medida': 'kit'},
        {'categoria': 'Material de Impresión', 'codigo': 'IMP-003', 'nombre': 'Alginato (Bolsa 450g)',
         'precio_costo': Decimal('85.00'), 'precio_venta': Decimal('130.00'),
         'stock_actual': Decimal('40'), 'stock_minimo': Decimal('12'), 'unidad_medida': 'bolsa'},
        
        # DESINFECCIÓN Y ESTERILIZACIÓN
        {'categoria': 'Desinfección y Esterilización', 'codigo': 'DES-001', 'nombre': 'Glutaraldehído 2% (Litro)',
         'precio_costo': Decimal('120.00'), 'precio_venta': Decimal('180.00'),
         'stock_actual': Decimal('30'), 'stock_minimo': Decimal('10'), 'unidad_medida': 'litro'},
        {'categoria': 'Desinfección y Esterilización', 'codigo': 'DES-002', 'nombre': 'Alcohol 70% (Litro)',
         'precio_costo': Decimal('25.00'), 'precio_venta': Decimal('40.00'),
         'stock_actual': Decimal('100'), 'stock_minimo': Decimal('25'), 'unidad_medida': 'litro'},
        {'categoria': 'Desinfección y Esterilización', 'codigo': 'DES-003', 'nombre': 'Bolsas para Autoclave (Caja x 200)',
         'precio_costo': Decimal('180.00'), 'precio_venta': Decimal('270.00'),
         'stock_actual': Decimal('45'), 'stock_minimo': Decimal('15'), 'unidad_medida': 'caja'},
        
        # CONSUMIBLES
        {'categoria': 'Consumibles', 'codigo': 'CONS-001', 'nombre': 'Guantes Látex Talla M (Caja x 100)',
         'precio_costo': Decimal('85.00'), 'precio_venta': Decimal('130.00'),
         'stock_actual': Decimal('200'), 'stock_minimo': Decimal('50'), 'unidad_medida': 'caja'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-002', 'nombre': 'Guantes Látex Talla L (Caja x 100)',
         'precio_costo': Decimal('85.00'), 'precio_venta': Decimal('130.00'),
         'stock_actual': Decimal('180'), 'stock_minimo': Decimal('50'), 'unidad_medida': 'caja'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-003', 'nombre': 'Mascarillas Quirúrgicas (Caja x 50)',
         'precio_costo': Decimal('40.00'), 'precio_venta': Decimal('65.00'),
         'stock_actual': Decimal('250'), 'stock_minimo': Decimal('60'), 'unidad_medida': 'caja'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-004', 'nombre': 'Baberos Desechables (Paquete x 125)',
         'precio_costo': Decimal('55.00'), 'precio_venta': Decimal('85.00'),
         'stock_actual': Decimal('100'), 'stock_minimo': Decimal('25'), 'unidad_medida': 'paquete'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-005', 'nombre': 'Vasos Desechables (Paquete x 100)',
         'precio_costo': Decimal('20.00'), 'precio_venta': Decimal('35.00'),
         'stock_actual': Decimal('150'), 'stock_minimo': Decimal('40'), 'unidad_medida': 'paquete'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-006', 'nombre': 'Rollos de Algodón (Bolsa x 500)',
         'precio_costo': Decimal('35.00'), 'precio_venta': Decimal('55.00'),
         'stock_actual': Decimal('80'), 'stock_minimo': Decimal('20'), 'unidad_medida': 'bolsa'},
        {'categoria': 'Consumibles', 'codigo': 'CONS-007', 'nombre': 'Gasas Estériles (Caja x 100)',
         'precio_costo': Decimal('60.00'), 'precio_venta': Decimal('90.00'),
         'stock_actual': Decimal('70'), 'stock_minimo': Decimal('20'), 'unidad_medida': 'caja'},
        
        # RADIOLOGÍA
        {'categoria': 'Radiología', 'codigo': 'RAD-001', 'nombre': 'Películas Radiográficas Periapicales (Caja x 150)',
         'precio_costo': Decimal('420.00'), 'precio_venta': Decimal('620.00'),
         'stock_actual': Decimal('25'), 'stock_minimo': Decimal('8'), 'unidad_medida': 'caja'},
        {'categoria': 'Radiología', 'codigo': 'RAD-002', 'nombre': 'Líquido Revelador (Litro)',
         'precio_costo': Decimal('180.00'), 'precio_venta': Decimal('270.00'),
         'stock_actual': Decimal('15'), 'stock_minimo': Decimal('5'), 'unidad_medida': 'litro'},
        {'categoria': 'Radiología', 'codigo': 'RAD-003', 'nombre': 'Líquido Fijador (Litro)',
         'precio_costo': Decimal('180.00'), 'precio_venta': Decimal('270.00'),
         'stock_actual': Decimal('15'), 'stock_minimo': Decimal('5'), 'unidad_medida': 'litro'},
    ]
    
    for insumo_data in insumos_data:
        categoria_nombre = insumo_data.pop('categoria')
        categoria = categorias[categoria_nombre]
        
        insumo, created = Insumo.objects.get_or_create(
            codigo=insumo_data['codigo'],
            defaults={
                'categoria': categoria,
                **insumo_data,
                'activo': True
            }
        )
        
        if created:
            insumos_creados.append(insumo)
            print(f"    ✓ {insumo.codigo}: {insumo.nombre}")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    total_categorias = CategoriaInsumo.objects.count()
    total_insumos = Insumo.objects.count()
    
    print(f"\n  ✅ Total: {total_categorias} categorías, {total_insumos} insumos")
    
    # Estadísticas por categoría
    for cat_nombre, categoria in categorias.items():
        count = categoria.insumos.count()
        print(f"     - {cat_nombre}: {count} insumos")
    
    return (list(CategoriaInsumo.objects.all()), list(Insumo.objects.all()))


# Funciones auxiliares
def obtener_insumos_bajo_stock():
    """Retorna insumos con stock por debajo del mínimo"""
    from django.db.models import F
    return Insumo.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        activo=True
    )


def obtener_consumibles():
    """Retorna solo consumibles"""
    return Insumo.objects.filter(
        categoria__nombre='Consumibles',
        activo=True
    ).order_by('nombre')


def obtener_insumos_por_categoria(nombre_categoria):
    """Filtra insumos por categoría"""
    return Insumo.objects.filter(
        categoria__nombre=nombre_categoria,
        activo=True
    ).order_by('nombre')
