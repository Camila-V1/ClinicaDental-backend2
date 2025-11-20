#!/usr/bin/env bash
# ============================================================================
# SCRIPT DE BUILD PARA RENDER
# ============================================================================
# Este script se ejecuta automáticamente en cada deploy
# ============================================================================

set -o errexit  # Exit on error

echo "======================================================================"
echo "🚀 INICIANDO BUILD DEL BACKEND - CLÍNICA DENTAL"
echo "======================================================================"

# ============================================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================================
echo ""
echo "📦 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# ============================================================================
# 2. RECOLECTAR ARCHIVOS ESTÁTICOS
# ============================================================================
echo ""
echo "📂 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

# ============================================================================
# 3. EJECUTAR MIGRACIONES
# ============================================================================
echo ""
echo "🔄 Ejecutando migraciones de base de datos..."
echo "   → Migraciones compartidas (public schema)..."
python manage.py migrate_schemas --shared

echo ""
echo "   → Creando tenant clinica-demo..."
python manage.py shell << 'PYTHON_SCRIPT'
from tenants.models import Clinica, Domain
from django.db import connection
import os

# ============================================================================
# 1. CREAR/VERIFICAR SCHEMA PÚBLICO
# ============================================================================
# El schema público necesita un tenant y dominio para que django-tenants funcione
if not Clinica.objects.filter(schema_name='public').exists():
    print("      ✓ Creando schema público...")
    public_tenant = Clinica.objects.create(
        schema_name='public',
        nombre='Sistema Principal',
        dominio='public',
        activo=True
    )
else:
    print("      ✓ Schema público ya existe")
    public_tenant = Clinica.objects.get(schema_name='public')

# Agregar dominios para el schema público
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')
public_domains = [
    render_hostname,  # clinica-dental-backend.onrender.com
    'localhost',
    '127.0.0.1',
]

for domain_name in public_domains:
    if not Domain.objects.filter(domain=domain_name).exists():
        is_primary = (domain_name == render_hostname)
        Domain.objects.create(
            domain=domain_name,
            tenant=public_tenant,
            is_primary=is_primary
        )
        print(f"      ✓ Dominio público creado: {domain_name}")
    else:
        print(f"      ✓ Dominio público existe: {domain_name}")

# ============================================================================
# 2. CREAR/VERIFICAR TENANT DE DEMO
# ============================================================================
if not Clinica.objects.filter(schema_name='clinica_demo').exists():
    print("\n      ✓ Creando tenant clinica-demo...")
    tenant = Clinica.objects.create(
        schema_name='clinica_demo',
        nombre='Clínica Demo',
        dominio='clinicademo1',
        activo=True
    )
    
    # Crear dominios para el tenant de demo
    demo_domains = [
        'clinica-demo.localhost',
        'clinicademo1.dentaabcxy.store',
        f'clinica-demo.{render_hostname}' if render_hostname != 'localhost' else None,
    ]
    
    for domain_name in filter(None, demo_domains):
        if not Domain.objects.filter(domain=domain_name).exists():
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=(domain_name == 'clinicademo1.dentaabcxy.store')
            )
            print(f"      ✓ Dominio demo creado: {domain_name}")
    
    print(f"      ✓ Tenant creado: {tenant.nombre}")
else:
    tenant = Clinica.objects.get(schema_name='clinica_demo')
    print(f"\n      ✓ Tenant clinica_demo ya existe (dominio: {tenant.dominio})")
    
    # Verificar/agregar dominio del subdominio si no existe
    if not Domain.objects.filter(domain='clinicademo1.dentaabcxy.store').exists():
        Domain.objects.create(
            domain='clinicademo1.dentaabcxy.store',
            tenant=tenant,
            is_primary=True
        )
        print(f"      ✓ Dominio agregado: clinicademo1.dentaabcxy.store")

print("\n      ✅ Tenants configurados correctamente")
PYTHON_SCRIPT

echo ""
echo "   → Migraciones del tenant (clinica_demo schema)..."
python manage.py migrate_schemas --schema=clinica_demo

# ============================================================================
# 4. POBLAR DATOS INICIALES
# ============================================================================
echo ""
echo "🌱 Poblando datos iniciales del sistema..."

# Poblar planes de suscripción (NUEVO - Sistema Multi-Tenant)
echo "   → Creando planes de suscripción..."
python poblar_planes_suscripcion.py

# Ejecutar el script de población completa
python poblar_sistema_completo.py

# Crear usuarios con credenciales actualizadas
echo "   → Creando/actualizando usuarios de prueba..."
python crear_usuarios_prueba.py

echo ""
echo "✅ Datos iniciales creados correctamente:"
echo "   - Tenant: clinica-demo"
echo "   - Admin: admin@clinica-demo.com / admin123"
echo "   - Odontólogo: odontologo@clinica-demo.com / odontologo123"
echo "   - Paciente: paciente@clinica-demo.com / paciente123"
echo "   - 5 Pacientes adicionales con datos completos"
echo "   - Servicios y tratamientos"
echo "   - Inventario de insumos"
echo "   - Citas, episodios, odontogramas"
echo "   - Planes de tratamiento y facturación"

# ============================================================================
# 5. VERIFICAR CONFIGURACIÓN
# ============================================================================
echo ""
echo "🔍 Verificando configuración del sistema..."
python manage.py check --deploy

# ============================================================================
# 6. INFORMACIÓN FINAL
# ============================================================================
echo ""
echo "======================================================================"
echo "✅ BUILD COMPLETADO EXITOSAMENTE"
echo "======================================================================"
echo ""
echo "📋 INFORMACIÓN IMPORTANTE:"
echo "   🌐 URL: https://$RENDER_EXTERNAL_HOSTNAME"
echo "   🔐 Panel Admin: https://$RENDER_EXTERNAL_HOSTNAME/admin/"
echo "   📡 API Base: https://$RENDER_EXTERNAL_HOSTNAME/api/"
echo ""
echo "👥 CREDENCIALES DE ACCESO:"
echo "   Admin: admin@clinica-demo.com / admin123"
echo "   Odontólogo: odontologo@clinica-demo.com / odontologo123"
echo "   Paciente: paciente@clinica-demo.com / paciente123"
echo "   Paciente 1: paciente1@test.com / password123"
echo ""
echo "🎉 ¡El sistema está listo para usarse!"
echo "======================================================================"
