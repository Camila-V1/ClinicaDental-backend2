#!/usr/bin/env python
"""
Script para limpiar y repoblar completamente el tenant de demo

ADVERTENCIA: Este script ELIMINA TODOS LOS DATOS del tenant especificado
y vuelve a crear datos de demo desde cero.

Uso:
    python limpiar_y_repoblar.py
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain
from django_tenants.utils import schema_context
from scripts_poblacion.poblar_todo import main as poblar_todo


def limpiar_datos_tenant(schema_name):
    """
    Limpia todos los datos de un tenant SIN eliminar el tenant
    """
    print(f"\n🗑️  Limpiando datos del tenant: {schema_name}")
    print("="*70)
    
    try:
        clinica = Clinica.objects.filter(schema_name=schema_name).first()
        
        if not clinica:
            print(f"❌ No existe el tenant con schema: {schema_name}")
            return False
        
        print(f"✅ Tenant encontrado: {clinica.nombre}")
        
        with schema_context(schema_name):
            from django.apps import apps
            
            # ORDEN CORRECTO: De dependientes a independientes
            # Primero eliminar los modelos que dependen de otros
            modelos_orden = [
                # 1. Facturación (depende de pacientes y citas)
                ('facturacion', 'Pago'),
                ('facturacion', 'Factura'),
                
                # 2. Historial clínico (depende de pacientes y citas)
                ('historial_clinico', 'DocumentoClinico'),
                ('historial_clinico', 'Odontograma'),
                ('historial_clinico', 'DetalleOdontograma'),
                ('historial_clinico', 'EpisodioClinico'),
                ('historial_clinico', 'HistorialClinico'),
                
                # 3. Tratamientos - Items de planes (dependen de planes y servicios)
                ('tratamientos', 'ItemPlanTratamiento'),
                ('tratamientos', 'PlanDeTratamiento'),
                ('tratamientos', 'ItemPresupuesto'),
                ('tratamientos', 'Presupuesto'),
                
                # 4. Agenda (depende de pacientes y odontólogos)
                ('agenda', 'Cita'),
                
                # 5. Servicios (dependen de categorías)
                ('tratamientos', 'Servicio'),
                ('tratamientos', 'CategoriaServicio'),
                
                # 6. Inventario
                ('inventario', 'MovimientoInventario'),
                ('inventario', 'Insumo'),
                ('inventario', 'CategoriaInsumo'),
                
                # 7. Usuarios (al final porque muchos dependen de ellos)
                ('usuarios', 'PerfilOdontologo'),
                ('usuarios', 'PerfilPaciente'),
                ('usuarios', 'Usuario'),
                
                # 8. Reportes
                ('reportes', 'BitacoraAccion'),
            ]
            
            print("\n📦 Limpiando datos en orden correcto:")
            total_eliminados = 0
            
            for app_name, modelo_name in modelos_orden:
                try:
                    app_config = apps.get_app_config(app_name)
                    modelo = app_config.get_model(modelo_name)
                    
                    count = modelo.objects.count()
                    if count > 0:
                        modelo.objects.all().delete()
                        total_eliminados += count
                        print(f"   ✓ {app_name}.{modelo_name}: {count} registros eliminados")
                
                except LookupError:
                    # App o modelo no encontrado, continuar
                    continue
                except Exception as e:
                    # Si hay error en un modelo específico, continuar con los demás
                    print(f"   ⚠️  Error en {app_name}.{modelo_name}: {str(e)[:100]}")
                    continue
            
            print(f"\n✅ Total de registros eliminados: {total_eliminados}")
        
        print("\n✅ Datos del tenant limpiados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al limpiar datos: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("  🔄 LIMPIAR Y REPOBLAR TENANT DE DEMO")
    print("="*70)
    
    SCHEMA_NAME = 'clinica_demo'
    
    # Confirmar acción
    print(f"\n⚠️  ADVERTENCIA: Se eliminarán TODOS los datos del tenant '{SCHEMA_NAME}'")
    print("   Esta acción NO SE PUEDE DESHACER.")
    
    respuesta = input("\n¿Deseas continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != 'SI':
        print("\n❌ Operación cancelada por el usuario")
        return
    
    # Paso 1: Limpiar datos
    if not limpiar_datos_tenant(SCHEMA_NAME):
        print("\n❌ Error al limpiar datos. Abortando.")
        return
    
    print("\n" + "="*70)
    print("  ⏳ Esperando un momento antes de repoblar...")
    print("="*70)
    import time
    time.sleep(2)
    
    # Paso 2: Repoblar
    print("\n" + "="*70)
    print("  🚀 REPOBLANDO TENANT CON DATOS NUEVOS")
    print("="*70)
    
    try:
        poblar_todo()
        
        print("\n" + "="*70)
        print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print("\n🎉 El tenant ha sido limpiado y repoblado con datos frescos")
        
    except Exception as e:
        print(f"\n❌ Error al repoblar: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
