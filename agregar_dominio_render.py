"""
Script para agregar el dominio de Render a la clínica demo
Ejecutar esto en Render Console o localmente apuntando a la DB de producción
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Clinica, Domain

def agregar_dominio_render():
    """Agregar dominio de Render a clinica_demo"""
    
    # Obtener hostname de Render desde variable de entorno
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    
    if not render_hostname:
        print("ℹ️  RENDER_EXTERNAL_HOSTNAME no está configurado (probablemente desarrollo local)")
        print("   Saltando configuración de dominio Render...")
        return
    
    # Obtener la clínica demo
    try:
        clinica = Clinica.objects.filter(schema_name='clinica_demo').first()
        
        if not clinica:
            print("❌ No se encontró la clínica con schema_name='clinica_demo'")
            print("   El tenant se creará cuando se ejecute poblar_todo.py")
            return
        
        print(f"✅ Clínica encontrada: {clinica.nombre} ({clinica.schema_name})")
        
        # Agregar dominio de Render
        domain, created = Domain.objects.get_or_create(
            domain=render_hostname,
            defaults={
                'tenant': clinica,
                'is_primary': False
            }
        )
        
        if created:
            print(f"✅ Dominio Render creado: {render_hostname}")
        else:
            print(f"ℹ️  Dominio Render ya existía: {render_hostname}")
        
        # Mostrar todos los dominios de la clínica
        print(f"\nDominios registrados para {clinica.nombre}:")
        for d in Domain.objects.filter(tenant=clinica):
            primary_mark = " (principal)" if d.is_primary else ""
            print(f"  - {d.domain}{primary_mark}")
        
        print("\n✅ Configuración de dominios completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    agregar_dominio_render()
