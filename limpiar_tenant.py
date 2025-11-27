#!/usr/bin/env python
"""
Script para limpiar todos los datos de un tenant específico
Mantiene el schema y las tablas, solo borra los datos
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from tenants.models import Clinica
from django.db import connection


def limpiar_tenant(schema_name='clinica_demo'):
    """
    Limpia todos los datos del tenant especificado
    
    Args:
        schema_name: Nombre del schema a limpiar (default: clinica_demo)
    """
    print(f"\n{'='*70}")
    print(f"🗑️  LIMPIANDO DATOS DEL TENANT: {schema_name}")
    print(f"{'='*70}\n")
    
    try:
        # Verificar que el tenant existe
        clinica = Clinica.objects.get(schema_name=schema_name)
        print(f"✓ Tenant encontrado: {clinica.nombre}")
        print(f"  Dominio: {clinica.dominio}")
        print(f"  Estado: {clinica.estado}")
        
        # Cambiar al schema del tenant
        with schema_context(schema_name):
            # Importar modelos
            from usuarios.models import Usuario, PerfilOdontologo, PerfilPaciente, Especialidad
            from agenda.models import Cita
            from historial_clinico.models import HistorialClinico, EpisodioAtencion, Odontograma
            from tratamientos.models import Servicio, CategoriaServicio, PlanDeTratamiento, ItemPlanTratamiento
            from inventario.models import Insumo, CategoriaInsumo
            from facturacion.models import Pago, Factura
            
            # Contar registros antes
            print("\n📊 Contando registros existentes...")
            conteos = {
                'Usuarios': Usuario.objects.count(),
                'Perfiles Odontólogo': PerfilOdontologo.objects.count(),
                'Perfiles Paciente': PerfilPaciente.objects.count(),
                'Especialidades': Especialidad.objects.count(),
                'Citas': Cita.objects.count(),
                'Historiales Clínicos': HistorialClinico.objects.count(),
                'Episodios': EpisodioAtencion.objects.count(),
                'Odontogramas': Odontograma.objects.count(),
                'Planes de Tratamiento': PlanDeTratamiento.objects.count(),
                'Items Plan Tratamiento': ItemPlanTratamiento.objects.count(),
                'Servicios': Servicio.objects.count(),
                'Categorías Servicio': CategoriaServicio.objects.count(),
                'Insumos': Insumo.objects.count(),
                'Categorías Insumo': CategoriaInsumo.objects.count(),
                'Pagos': Pago.objects.count(),
                'Facturas': Factura.objects.count(),
            }
            
            total_antes = sum(conteos.values())
            
            if total_antes == 0:
                print("\n⚠️  El tenant ya está vacío. No hay nada que borrar.")
                return
            
            print(f"\nRegistros encontrados:")
            for modelo, cantidad in conteos.items():
                if cantidad > 0:
                    print(f"  • {modelo}: {cantidad}")
            
            print(f"\n  📍 TOTAL: {total_antes} registros")
            
            # Confirmar borrado
            print("\n⚠️  ADVERTENCIA: Esta acción borrará todos los datos del tenant")
            respuesta = input("\n¿Deseas continuar? (escribe 'SI' para confirmar): ")
            
            if respuesta.upper() != 'SI':
                print("\n❌ Operación cancelada por el usuario")
                return
            
            print("\n🗑️  Borrando datos en orden correcto...\n")
            
            # Borrar en orden para evitar errores de Foreign Key
            try:
                # 1. Pagos (depende de Factura y Cita)
                cantidad = Pago.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Pagos: {cantidad} registros eliminados")
                
                # 2. Facturas
                cantidad = Factura.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Facturas: {cantidad} registros eliminados")
                
                # 3. Items de Planes de Tratamiento (depende de PlanTratamiento y Servicio)
                cantidad = ItemPlanTratamiento.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Items de Plan de Tratamiento: {cantidad} registros eliminados")
                
                # 4. Planes de Tratamiento (depende de HistorialClinico)
                cantidad = PlanDeTratamiento.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Planes de Tratamiento: {cantidad} registros eliminados")
                
                # 5. Odontogramas (depende de HistorialClinico)
                cantidad = Odontograma.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Odontogramas: {cantidad} registros eliminados")
                
                # 6. Episodios (depende de HistorialClinico)
                cantidad = EpisodioAtencion.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Episodios de Atención: {cantidad} registros eliminados")
                
                # 7. Historiales Clínicos (depende de PerfilPaciente)
                cantidad = HistorialClinico.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Historiales Clínicos: {cantidad} registros eliminados")
                
                # 8. Citas (depende de PerfilOdontologo y PerfilPaciente)
                cantidad = Cita.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Citas: {cantidad} registros eliminados")
                
                # 9. Servicios (depende de CategoriaServicio)
                cantidad = Servicio.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Servicios: {cantidad} registros eliminados")
                
                cantidad = CategoriaServicio.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Categorías de Servicio: {cantidad} registros eliminados")
                
                # 10. Insumos (depende de CategoriaInsumo)
                cantidad = Insumo.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Insumos: {cantidad} registros eliminados")
                
                cantidad = CategoriaInsumo.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Categorías de Insumo: {cantidad} registros eliminados")
                
                # 11. Perfiles (dependen de Usuario)
                cantidad = PerfilOdontologo.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Perfiles de Odontólogo: {cantidad} registros eliminados")
                
                cantidad = PerfilPaciente.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Perfiles de Paciente: {cantidad} registros eliminados")
                
                # 12. Especialidades
                cantidad = Especialidad.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Especialidades: {cantidad} registros eliminados")
                
                # 13. Usuarios (base, debe ser último)
                cantidad = Usuario.objects.all().delete()[0]
                if cantidad > 0:
                    print(f"  ✓ Usuarios: {cantidad} registros eliminados")
                
                print(f"\n{'='*70}")
                print(f"✅ TENANT '{schema_name}' LIMPIADO EXITOSAMENTE")
                print(f"{'='*70}\n")
                print("📝 Próximos pasos:")
                print("   1. Ejecutar: python scripts_poblacion/poblar_todo.py")
                print("   2. O poblar módulos individuales según necesites\n")
                
            except Exception as e:
                print(f"\n❌ Error durante el borrado: {e}")
                print("   Puede haber restricciones de FK pendientes")
                raise
        
    except Clinica.DoesNotExist:
        print(f"\n❌ ERROR: No existe tenant con schema '{schema_name}'")
        print("\nTenants disponibles:")
        for tenant in Clinica.objects.all():
            print(f"  • {tenant.schema_name} ({tenant.nombre})")
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Permitir especificar el schema como argumento
    schema_name = sys.argv[1] if len(sys.argv) > 1 else 'clinica_demo'
    
    limpiar_tenant(schema_name)
