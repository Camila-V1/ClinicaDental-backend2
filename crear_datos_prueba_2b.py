"""
Script para crear datos de prueba del Paso 2.B
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from inventario.models import CategoriaInsumo, Insumo
from tratamientos.models import CategoriaServicio, Servicio, MaterialServicioFijo, MaterialServicioOpcional
from decimal import Decimal

def crear_datos_inventario():
    """Crear categorías e insumos de prueba"""
    print("🏗️ Creando datos de inventario...")
    
    # Crear categorías de insumos
    cat_resinas, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Resinas Dentales",
        defaults={'descripcion': 'Materiales de resina para restauraciones'}
    )
    
    cat_anestesicos, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Anestésicos",
        defaults={'descripcion': 'Anestésicos locales para procedimientos'}
    )
    
    cat_kits, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Kits y Conjuntos",
        defaults={'descripcion': 'Kits completos para procedimientos'}
    )
    
    # Crear insumos de prueba
    insumos = [
        # Resinas (diferentes precios para probar materiales opcionales)
        {
            'categoria': cat_resinas,
            'codigo': 'RES-001',
            'nombre': 'Resina 3M Filtek Z350 A1',
            'precio_costo': Decimal('45.00'),
            'precio_venta': Decimal('75.00'),
            'stock_actual': Decimal('20')
        },
        {
            'categoria': cat_resinas,
            'codigo': 'RES-002', 
            'nombre': 'Resina Genérica Universal A2',
            'precio_costo': Decimal('25.00'),
            'precio_venta': Decimal('40.00'),
            'stock_actual': Decimal('30')
        },
        {
            'categoria': cat_resinas,
            'codigo': 'RES-003',
            'nombre': 'Resina Premium Vita A3',
            'precio_costo': Decimal('65.00'),
            'precio_venta': Decimal('100.00'),
            'stock_actual': Decimal('15')
        },
        
        # Anestésicos
        {
            'categoria': cat_anestesicos,
            'codigo': 'ANES-001',
            'nombre': 'Lidocaína 2% con Epinefrina',
            'precio_costo': Decimal('12.00'),
            'precio_venta': Decimal('18.00'),
            'stock_actual': Decimal('50')
        },
        {
            'categoria': cat_anestesicos,
            'codigo': 'ANES-002',
            'nombre': 'Articaína 4%',
            'precio_costo': Decimal('18.00'),
            'precio_venta': Decimal('28.00'),
            'stock_actual': Decimal('25')
        },
        
        # Kits fijos
        {
            'categoria': cat_kits,
            'codigo': 'KIT-001',
            'nombre': 'Kit Limpieza Básica',
            'precio_costo': Decimal('5.00'),
            'precio_venta': Decimal('8.00'),
            'stock_actual': Decimal('100')
        },
        {
            'categoria': cat_kits,
            'codigo': 'KIT-002',
            'nombre': 'Kit Endodoncia Completo',
            'precio_costo': Decimal('35.00'),
            'precio_venta': Decimal('55.00'),
            'stock_actual': Decimal('40')
        },
    ]
    
    for insumo_data in insumos:
        insumo, created = Insumo.objects.get_or_create(
            codigo=insumo_data['codigo'],
            defaults=insumo_data
        )
        if created:
            print(f"  ✓ Creado insumo: {insumo.nombre}")
        else:
            print(f"  ↻ Ya existe: {insumo.nombre}")

def crear_datos_servicios():
    """Crear servicios y recetas de prueba"""
    print("\n🦷 Creando servicios y recetas...")
    
    # Crear categoría de servicio
    cat_general, _ = CategoriaServicio.objects.get_or_create(
        nombre="Odontología General",
        defaults={'descripcion': 'Servicios generales de odontología', 'orden': 1}
    )
    
    # Crear servicios
    servicios_data = [
        {
            'codigo_servicio': 'CONS-001',
            'nombre': 'Consulta de Diagnóstico',
            'descripcion': 'Evaluación inicial del paciente y diagnóstico',
            'categoria': cat_general,
            'precio_base': Decimal('30.00'),
            'tiempo_estimado': 30
        },
        {
            'codigo_servicio': 'REST-001', 
            'nombre': 'Restauración Simple',
            'descripcion': 'Restauración de caries con resina compuesta',
            'categoria': cat_general,
            'precio_base': Decimal('80.00'),
            'tiempo_estimado': 60
        },
        {
            'codigo_servicio': 'LIMPD-001',
            'nombre': 'Limpieza Dental',
            'descripcion': 'Profilaxis y limpieza dental profesional',
            'categoria': cat_general,
            'precio_base': Decimal('40.00'),
            'tiempo_estimado': 45
        }
    ]
    
    servicios_creados = []
    for servicio_data in servicios_data:
        servicio, created = Servicio.objects.get_or_create(
            codigo_servicio=servicio_data['codigo_servicio'],
            defaults=servicio_data
        )
        if created:
            print(f"  ✓ Creado servicio: {servicio.nombre}")
        else:
            print(f"  ↻ Ya existe: {servicio.nombre}")
        servicios_creados.append(servicio)
    
    return servicios_creados

def crear_recetas(servicios):
    """Crear las recetas de prueba"""
    print("\n📋 Creando recetas...")
    
    # Obtener insumos
    kit_limpieza = Insumo.objects.get(codigo='KIT-001')
    kit_endodoncia = Insumo.objects.get(codigo='KIT-002')
    lidocaina = Insumo.objects.get(codigo='ANES-001')
    
    # Obtener categorías
    cat_resinas = CategoriaInsumo.objects.get(nombre="Resinas Dentales")
    cat_anestesicos = CategoriaInsumo.objects.get(nombre="Anestésicos")
    
    # Buscar servicios
    consulta = next((s for s in servicios if s.codigo_servicio == 'CONS-001'), None)
    restauracion = next((s for s in servicios if s.codigo_servicio == 'REST-001'), None)
    limpieza = next((s for s in servicios if s.codigo_servicio == 'LIMPD-001'), None)
    
    # Recetas para Consulta (solo materiales fijos)
    if consulta:
        # Kit básico siempre incluido
        material_fijo, created = MaterialServicioFijo.objects.get_or_create(
            servicio=consulta,
            insumo=kit_limpieza,
            defaults={'cantidad': Decimal('0.5'), 'notas': 'Material básico para exploración'}
        )
        if created:
            print(f"  ✓ Receta fija: {material_fijo}")
    
    # Recetas para Restauración (fijos + opcionales)
    if restauracion:
        # Anestesia fija
        material_fijo, created = MaterialServicioFijo.objects.get_or_create(
            servicio=restauracion,
            insumo=lidocaina,
            defaults={'cantidad': Decimal('1.0'), 'notas': 'Anestesia local estándar'}
        )
        if created:
            print(f"  ✓ Receta fija: {material_fijo}")
        
        # Resina opcional (aquí es donde el doctor elige el tipo)
        material_opcional, created = MaterialServicioOpcional.objects.get_or_create(
            servicio=restauracion,
            categoria_insumo=cat_resinas,
            defaults={
                'cantidad': Decimal('1.0'), 
                'nombre_personalizado': 'Tipo de Resina',
                'notas': 'El doctor debe elegir el tipo y color de resina según el caso'
            }
        )
        if created:
            print(f"  ✓ Receta opcional: {material_opcional}")
    
    # Recetas para Limpieza
    if limpieza:
        # Kit de limpieza fijo
        material_fijo, created = MaterialServicioFijo.objects.get_or_create(
            servicio=limpieza,
            insumo=kit_limpieza,
            defaults={'cantidad': Decimal('1.0'), 'notas': 'Kit completo de limpieza'}
        )
        if created:
            print(f"  ✓ Receta fija: {material_fijo}")

def main():
    """Función principal"""
    print("🚀 Iniciando creación de datos de prueba para Paso 2.B...")
    
    # Trabajar en el esquema de la clínica demo
    with schema_context('clinica_demo'):
        crear_datos_inventario()
        servicios = crear_datos_servicios()
        crear_recetas(servicios)
        
        print("\n✅ Datos de prueba creados exitosamente!")
        print("\n📊 Resumen:")
        print(f"  - Categorías de insumos: {CategoriaInsumo.objects.count()}")
        print(f"  - Insumos: {Insumo.objects.count()}")
        print(f"  - Categorías de servicios: {CategoriaServicio.objects.count()}")
        print(f"  - Servicios: {Servicio.objects.count()}")
        print(f"  - Materiales fijos: {MaterialServicioFijo.objects.count()}")
        print(f"  - Materiales opcionales: {MaterialServicioOpcional.objects.count()}")

if __name__ == '__main__':
    main()