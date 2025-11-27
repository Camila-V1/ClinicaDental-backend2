"""
Módulo para crear y verificar tenants
"""
import os
from tenants.models import Clinica, Domain, PlanSuscripcion


def crear_o_verificar_tenant(schema_name, nombre, dominio_principal):
    """
    Crea o verifica que existe un tenant
    
    Args:
        schema_name: Nombre del schema (ej: 'clinica_demo')
        nombre: Nombre de la clínica
        dominio_principal: Dominio principal (ej: 'clinicademo1.dentaabcxy.store')
    
    Returns:
        Objeto Clinica
    """
    # Verificar si ya existe
    tenant = Clinica.objects.filter(schema_name=schema_name).first()
    
    if tenant:
        print(f"  ✓ Tenant ya existe: {tenant.nombre}")
        
        # Verificar dominio principal
        dominio_existe = Domain.objects.filter(
            domain=dominio_principal,
            tenant=tenant
        ).exists()
        
        if not dominio_existe:
            Domain.objects.create(
                domain=dominio_principal,
                tenant=tenant,
                is_primary=True
            )
            print(f"  ✓ Dominio agregado: {dominio_principal}")
        else:
            print(f"  ✓ Dominio ya existe: {dominio_principal}")
        
        return tenant
    
    # Crear plan si no existe
    plan, _ = PlanSuscripcion.objects.get_or_create(
        tipo='GRATUITO',
        defaults={
            'nombre': 'Plan Gratuito',
            'precio': 0.00,
            'duracion_dias': 365,
            'max_usuarios': 10,
            'max_pacientes': 100,
        }
    )
    
    # Crear nuevo tenant
    print(f"  → Creando tenant: {nombre}...")
    tenant = Clinica.objects.create(
        schema_name=schema_name,
        nombre=nombre,
        dominio=schema_name.replace('_', ''),  # clinica_demo -> clinicademo
        plan=plan
    )
    
    # Crear dominios
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')
    dominios = [
        (dominio_principal, True),  # Principal
        (f'{schema_name}.{render_hostname}', False),  # Alternativo
        (f'{schema_name}.localhost', False),  # Desarrollo
    ]
    
    for dominio, es_primario in dominios:
        if dominio and not dominio.startswith('localhost.') and dominio != 'localhost.localhost':
            Domain.objects.create(
                domain=dominio,
                tenant=tenant,
                is_primary=es_primario
            )
            print(f"  ✓ Dominio creado: {dominio} {'(principal)' if es_primario else ''}")
    
    print(f"  ✅ Tenant creado exitosamente")
    return tenant
