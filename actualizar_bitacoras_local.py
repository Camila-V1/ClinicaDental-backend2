"""
Script para actualizar registros de bitácora asignando el usuario admin.
Se conecta directamente a la base de datos de producción.
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from reportes.models import BitacoraAccion
from usuarios.models import Usuario
from django_tenants.utils import schema_context

def actualizar_bitacoras():
    """Actualiza bitácoras sin usuario asignándoles el admin."""
    
    print("=" * 70)
    print("🔄 ACTUALIZANDO BITÁCORAS SIN USUARIO")
    print("=" * 70)
    
    # Usar el schema del tenant clinica_demo
    with schema_context('clinica_demo'):
        # Obtener el usuario admin
        try:
            admin = Usuario.objects.filter(
                email='admin@clinica-demo.com',
                tipo_usuario='ADMIN'
            ).first()
            
            if not admin:
                print("❌ No se encontró el usuario admin")
                return
            
            print(f"✅ Usuario admin encontrado: {admin.full_name} (ID: {admin.id})")
            
            # Obtener bitácoras sin usuario
            bitacoras_sin_usuario = BitacoraAccion.objects.filter(usuario__isnull=True)
            total = bitacoras_sin_usuario.count()
            
            print(f"\n📋 {total} registros de bitácora sin usuario")
            
            if total == 0:
                print("✅ No hay registros para actualizar")
                return
            
            print("\n🔄 Actualizando registros...\n")
            
            actualizados = 0
            for bitacora in bitacoras_sin_usuario:
                bitacora.usuario = admin
                bitacora.save()
                print(f"✅ #{bitacora.id}: {bitacora.descripcion[:60]}...")
                actualizados += 1
            
            print(f"\n" + "=" * 70)
            print(f"✅ COMPLETADO: {actualizados} de {total} registros actualizados")
            print("=" * 70)
            
            # Verificar
            sin_usuario = BitacoraAccion.objects.filter(usuario__isnull=True).count()
            print(f"\n📊 Registros restantes sin usuario: {sin_usuario}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    try:
        actualizar_bitacoras()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
