"""
Script para verificar el estado actual de las bitácoras.
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from reportes.models import BitacoraAccion
from django_tenants.utils import schema_context

def verificar_bitacoras():
    """Verifica el estado de las bitácoras."""
    
    print("=" * 70)
    print("📊 ESTADO DE BITÁCORAS")
    print("=" * 70)
    
    # Usar el schema del tenant clinica_demo
    with schema_context('clinica_demo'):
        total = BitacoraAccion.objects.count()
        con_usuario = BitacoraAccion.objects.filter(usuario__isnull=False).count()
        sin_usuario = BitacoraAccion.objects.filter(usuario__isnull=True).count()
        
        print(f"\n📋 Total de registros: {total}")
        print(f"✅ Con usuario: {con_usuario}")
        print(f"❌ Sin usuario: {sin_usuario}")
        
        print("\n" + "=" * 70)
        print("ÚLTIMOS 15 REGISTROS:")
        print("=" * 70)
        
        for bitacora in BitacoraAccion.objects.order_by('-fecha_hora')[:15]:
            usuario_info = f"{bitacora.usuario.full_name} ({bitacora.usuario.email})" if bitacora.usuario else "❌ SIN USUARIO"
            print(f"\n#{bitacora.id} - {bitacora.accion}")
            print(f"   Usuario: {usuario_info}")
            print(f"   Descripción: {bitacora.descripcion[:80]}...")
            print(f"   Fecha: {bitacora.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    verificar_bitacoras()
