"""
Script para verificar que los servicios tengan materiales opcionales configurados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context, get_tenant_model
from tratamientos.models import Servicio, MaterialServicioOpcional, MaterialServicioFijo
from inventario.models import Insumo, CategoriaInsumo

# Obtener el tenant
Tenant = get_tenant_model()
try:
    tenant = Tenant.objects.get(schema_name='clinica_demo')
    print(f"✅ Usando tenant: {tenant.nombre} (schema: {tenant.schema_name})\n")
except Tenant.DoesNotExist:
    print("❌ ERROR: No existe el tenant 'clinica_demo'")
    print("   Ejecuta primero: python manage.py create_tenant\n")
    exit(1)

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE SERVICIOS Y MATERIALES")
print("="*80 + "\n")

# Ejecutar todo dentro del schema del tenant
with schema_context(tenant.schema_name):
    # 1. Verificar servicios
    servicios = Servicio.objects.all()
    print(f"📊 Total de servicios: {servicios.count()}\n")

    if servicios.count() == 0:
        print("❌ NO HAY SERVICIOS CONFIGURADOS")
        print("   Necesitas ejecutar el script de población primero.\n")
    else:
        for servicio in servicios:
            print(f"\n{'='*60}")
            print(f"🦷 Servicio: {servicio.nombre}")
            print(f"   Código: {servicio.codigo_servicio}")
            print(f"   Precio base: ${servicio.precio_base}")
            print(f"   Categoría: {servicio.categoria.nombre}")
            
            # Materiales fijos
            materiales_fijos = servicio.materiales_fijos.all()
            print(f"\n   📦 Materiales Fijos: {materiales_fijos.count()}")
            for mat in materiales_fijos:
                print(f"      • {mat.insumo.nombre} (Cantidad: {mat.cantidad}) - ${mat.costo_adicional}")
            
            # Materiales opcionales
            materiales_opcionales = servicio.materiales_opcionales.all()
            print(f"\n   🎨 Materiales Opcionales: {materiales_opcionales.count()}")
            
            if materiales_opcionales.count() == 0:
                print(f"      ⚠️  NO HAY MATERIALES OPCIONALES")
            else:
                for mat_opc in materiales_opcionales:
                    print(f"\n      • Categoría: {mat_opc.categoria_insumo.nombre}")
                    print(f"        Nombre personalizado: {mat_opc.nombre_personalizado or 'N/A'}")
                    print(f"        Cantidad: {mat_opc.cantidad}")
                    print(f"        Obligatorio: {'✅ Sí' if mat_opc.es_obligatorio else '❌ No'}")
                    
                    opciones = mat_opc.opciones_disponibles
                    print(f"        Opciones disponibles: {opciones.count()}")
                    for insumo in opciones:
                        print(f"           - {insumo.nombre} (${insumo.precio_venta})")
            
            print(f"\n   ✅ tiene_materiales_opcionales: {servicio.materiales_opcionales.exists()}")

    # 2. Verificar categorías de insumos
    print("\n\n" + "="*80)
    print("📦 CATEGORÍAS DE INSUMOS")
    print("="*80 + "\n")

    categorias = CategoriaInsumo.objects.all()
    print(f"Total: {categorias.count()}\n")

    for cat in categorias:
        insumos_count = cat.insumos.filter(activo=True).count()
        print(f"• {cat.nombre}: {insumos_count} insumos activos")

    # 3. Verificar insumos
    print("\n\n" + "="*80)
    print("💊 INSUMOS DISPONIBLES")
    print("="*80 + "\n")

    insumos = Insumo.objects.filter(activo=True)
    print(f"Total: {insumos.count()}\n")

    for insumo in insumos[:10]:  # Mostrar solo los primeros 10
        print(f"• {insumo.codigo} - {insumo.nombre}")
        print(f"  Categoría: {insumo.categoria.nombre}")
        print(f"  Precio: ${insumo.precio_venta}")
        print(f"  Stock: {insumo.stock_actual} {insumo.unidad_medida}")
        print()

    if insumos.count() > 10:
        print(f"... y {insumos.count() - 10} insumos más\n")

    # 4. Resumen
    print("\n" + "="*80)
    print("📋 RESUMEN")
    print("="*80 + "\n")

    servicios_sin_materiales = 0
    servicios_con_fijos = 0
    servicios_con_opcionales = 0

    for servicio in Servicio.objects.all():
        tiene_fijos = servicio.materiales_fijos.exists()
        tiene_opcionales = servicio.materiales_opcionales.exists()
        
        if not tiene_fijos and not tiene_opcionales:
            servicios_sin_materiales += 1
        
        if tiene_fijos:
            servicios_con_fijos += 1
        
        if tiene_opcionales:
            servicios_con_opcionales += 1

    print(f"✅ Servicios con materiales fijos: {servicios_con_fijos}/{servicios.count()}")
    print(f"✅ Servicios con materiales opcionales: {servicios_con_opcionales}/{servicios.count()}")
    print(f"⚠️  Servicios sin materiales: {servicios_sin_materiales}/{servicios.count()}")

    if servicios_sin_materiales > 0:
        print(f"\n⚠️  ATENCIÓN: Hay {servicios_sin_materiales} servicios sin materiales configurados.")
        print("   El frontend NO mostrará el Paso 2 (selección de materiales) para estos servicios.")

    if servicios_con_opcionales == 0:
        print("\n❌ PROBLEMA DETECTADO:")
        print("   NO HAY SERVICIOS CON MATERIALES OPCIONALES")
        print("   El Paso 2 del modal NUNCA se mostrará.")
        print("\n💡 SOLUCIÓN:")
        print("   1. Ejecuta: python poblar_sistema_completo.py")
        print("   2. O crea materiales opcionales manualmente en el admin de Django")

print("\n" + "="*80 + "\n")
