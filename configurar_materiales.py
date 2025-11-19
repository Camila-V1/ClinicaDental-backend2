"""
Script para agregar materiales opcionales a los servicios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context, get_tenant_model
from tratamientos.models import Servicio, MaterialServicioOpcional, MaterialServicioFijo
from inventario.models import Insumo, CategoriaInsumo
from decimal import Decimal

# Obtener el tenant
Tenant = get_tenant_model()
tenant = Tenant.objects.get(schema_name='clinica_demo')

print(f"✅ Configurando materiales para tenant: {tenant.nombre}\n")

with schema_context(tenant.schema_name):
    
    print("="*80)
    print("🎨 CONFIGURANDO MATERIALES OPCIONALES")
    print("="*80 + "\n")
    
    # ========================================================================
    # 1. RESTAURACIÓN DENTAL - Seleccionar tipo de resina
    # ========================================================================
    try:
        servicio_restauracion = Servicio.objects.get(codigo_servicio='REST-001')
        cat_materiales = CategoriaInsumo.objects.get(nombre='Materiales Dentales')
        
        mat_opc, created = MaterialServicioOpcional.objects.get_or_create(
            servicio=servicio_restauracion,
            categoria_insumo=cat_materiales,
            defaults={
                'cantidad': 1,
                'nombre_personalizado': 'Selecciona el tipo de resina',
                'es_obligatorio': True,
                'notas': 'Elige la resina según el tono del diente'
            }
        )
        
        if created:
            print("✅ Restauración Dental - Material opcional configurado")
            print(f"   Categoría: {cat_materiales.nombre}")
            print(f"   Opciones disponibles:")
            for insumo in mat_opc.opciones_disponibles:
                print(f"      - {insumo.nombre} (${insumo.precio_venta})")
        else:
            print("ℹ️  Restauración Dental - Ya tenía material opcional configurado")
        print()
        
    except Exception as e:
        print(f"❌ Error en Restauración Dental: {e}\n")
    
    # ========================================================================
    # 2. ENDODONCIA - Seleccionar material de obturación
    # ========================================================================
    try:
        servicio_endo = Servicio.objects.get(codigo_servicio='ENDO-001')
        cat_materiales = CategoriaInsumo.objects.get(nombre='Materiales Dentales')
        
        mat_opc, created = MaterialServicioOpcional.objects.get_or_create(
            servicio=servicio_endo,
            categoria_insumo=cat_materiales,
            defaults={
                'cantidad': 1,
                'nombre_personalizado': 'Selecciona el material de obturación',
                'es_obligatorio': True,
                'notas': 'Material para sellar el conducto radicular'
            }
        )
        
        if created:
            print("✅ Endodoncia - Material opcional configurado")
            print(f"   Categoría: {cat_materiales.nombre}")
            print(f"   Opciones disponibles:")
            for insumo in mat_opc.opciones_disponibles:
                print(f"      - {insumo.nombre} (${insumo.precio_venta})")
        else:
            print("ℹ️  Endodoncia - Ya tenía material opcional configurado")
        print()
        
    except Exception as e:
        print(f"❌ Error en Endodoncia: {e}\n")
    
    # ========================================================================
    # 3. CORONA DENTAL - Seleccionar tipo de cemento
    # ========================================================================
    try:
        servicio_corona = Servicio.objects.get(codigo_servicio='CORO-001')
        cat_materiales = CategoriaInsumo.objects.get(nombre='Materiales Dentales')
        
        mat_opc, created = MaterialServicioOpcional.objects.get_or_create(
            servicio=servicio_corona,
            categoria_insumo=cat_materiales,
            defaults={
                'cantidad': 1,
                'nombre_personalizado': 'Selecciona el cemento dental',
                'es_obligatorio': True,
                'notas': 'Cemento para fijar la corona'
            }
        )
        
        if created:
            print("✅ Corona Dental - Material opcional configurado")
            print(f"   Categoría: {cat_materiales.nombre}")
            print(f"   Opciones disponibles:")
            for insumo in mat_opc.opciones_disponibles:
                print(f"      - {insumo.nombre} (${insumo.precio_venta})")
        else:
            print("ℹ️  Corona Dental - Ya tenía material opcional configurado")
        print()
        
    except Exception as e:
        print(f"❌ Error en Corona Dental: {e}\n")
    
    # ========================================================================
    # 4. AGREGAR MATERIALES FIJOS A ALGUNOS SERVICIOS
    # ========================================================================
    print("="*80)
    print("📦 CONFIGURANDO MATERIALES FIJOS")
    print("="*80 + "\n")
    
    # Endodoncia - Agregar anestesia y jeringa como materiales fijos
    try:
        servicio_endo = Servicio.objects.get(codigo_servicio='ENDO-001')
        lidocaina = Insumo.objects.get(codigo='ANE-LID-001')
        jeringa = Insumo.objects.get(codigo='JER-5ML-001')
        
        mat_fijo1, created1 = MaterialServicioFijo.objects.get_or_create(
            servicio=servicio_endo,
            insumo=lidocaina,
            defaults={
                'cantidad': 2,
                'es_obligatorio': True,
                'notas': 'Anestesia local para el procedimiento'
            }
        )
        
        mat_fijo2, created2 = MaterialServicioFijo.objects.get_or_create(
            servicio=servicio_endo,
            insumo=jeringa,
            defaults={
                'cantidad': 1,
                'es_obligatorio': True,
                'notas': 'Jeringa para administrar anestesia'
            }
        )
        
        if created1 or created2:
            print("✅ Endodoncia - Materiales fijos agregados")
            print(f"   • {lidocaina.nombre} x2 (${float(lidocaina.precio_venta) * 2})")
            print(f"   • {jeringa.nombre} x1 (${jeringa.precio_venta})")
        else:
            print("ℹ️  Endodoncia - Ya tenía materiales fijos configurados")
        print()
        
    except Exception as e:
        print(f"❌ Error agregando materiales fijos a Endodoncia: {e}\n")
    
    # Restauración - Agregar materiales fijos básicos
    try:
        servicio_rest = Servicio.objects.get(codigo_servicio='REST-001')
        lidocaina = Insumo.objects.get(codigo='ANE-LID-001')
        jeringa = Insumo.objects.get(codigo='JER-5ML-001')
        guantes = Insumo.objects.get(codigo='GLV-LAT-M')
        
        mat_fijo1, created1 = MaterialServicioFijo.objects.get_or_create(
            servicio=servicio_rest,
            insumo=lidocaina,
            defaults={
                'cantidad': 1,
                'es_obligatorio': True,
                'notas': 'Anestesia local'
            }
        )
        
        mat_fijo2, created2 = MaterialServicioFijo.objects.get_or_create(
            servicio=servicio_rest,
            insumo=jeringa,
            defaults={
                'cantidad': 1,
                'es_obligatorio': True,
                'notas': 'Jeringa descartable'
            }
        )
        
        mat_fijo3, created3 = MaterialServicioFijo.objects.get_or_create(
            servicio=servicio_rest,
            insumo=guantes,
            defaults={
                'cantidad': 1,
                'es_obligatorio': True,
                'notas': 'Guantes de látex'
            }
        )
        
        if created1 or created2 or created3:
            print("✅ Restauración Dental - Materiales fijos agregados")
            print(f"   • {lidocaina.nombre} x1 (${lidocaina.precio_venta})")
            print(f"   • {jeringa.nombre} x1 (${jeringa.precio_venta})")
            print(f"   • {guantes.nombre} x1 (${guantes.precio_venta})")
        else:
            print("ℹ️  Restauración Dental - Ya tenía materiales fijos configurados")
        print()
        
    except Exception as e:
        print(f"❌ Error agregando materiales fijos a Restauración: {e}\n")
    
    # ========================================================================
    # 5. VERIFICACIÓN FINAL
    # ========================================================================
    print("="*80)
    print("📊 VERIFICACIÓN FINAL")
    print("="*80 + "\n")
    
    servicios_con_fijos = 0
    servicios_con_opcionales = 0
    
    for servicio in Servicio.objects.all():
        tiene_fijos = servicio.materiales_fijos.exists()
        tiene_opcionales = servicio.materiales_opcionales.exists()
        
        if tiene_fijos:
            servicios_con_fijos += 1
        
        if tiene_opcionales:
            servicios_con_opcionales += 1
    
    total_servicios = Servicio.objects.count()
    
    print(f"✅ Servicios con materiales fijos: {servicios_con_fijos}/{total_servicios}")
    print(f"✅ Servicios con materiales opcionales: {servicios_con_opcionales}/{total_servicios}")
    
    if servicios_con_opcionales > 0:
        print("\n🎉 ¡ÉXITO! Ahora hay servicios con materiales opcionales")
        print("   El Paso 2 del modal ya debería aparecer para estos servicios:")
        for servicio in Servicio.objects.filter(materiales_opcionales__isnull=False).distinct():
            print(f"      • {servicio.nombre} ({servicio.codigo_servicio})")
    
    print("\n" + "="*80)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*80 + "\n")
    
    print("💡 PRÓXIMOS PASOS:")
    print("   1. Recarga el frontend (Ctrl + R)")
    print("   2. Ve a un plan de tratamiento")
    print("   3. Click en 'Agregar Servicio'")
    print("   4. Selecciona 'Restauración Dental' o 'Endodoncia'")
    print("   5. Deberías ver el Paso 2 con las opciones de materiales\n")
