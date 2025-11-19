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

# Verificar si el tenant ya existe
if not Clinica.objects.filter(dominio='clinica-demo').exists():
    print("      ✓ Creando tenant clinica-demo")
    tenant = Clinica.objects.create(
        schema_name='clinica_demo',
        nombre='Clínica Demo',
        dominio='clinica-demo',
        activo=True
    )
    
    # Crear el dominio asociado
    Domain.objects.create(
        domain='clinica-demo.localhost',  # Para desarrollo
        tenant=tenant,
        is_primary=True
    )
    print(f"      ✓ Tenant creado: {tenant.nombre}")
    print(f"      ✓ Dominio: clinica-demo.localhost")
else:
    print("      ✓ Tenant clinica-demo ya existe")
PYTHON_SCRIPT

echo ""
echo "   → Migraciones del tenant (clinica_demo schema)..."
python manage.py migrate_schemas --schema=clinica_demo

# ============================================================================
# 4. POBLAR DATOS INICIALES
# ============================================================================
echo ""
echo "🌱 Poblando datos iniciales del sistema..."

# Ejecutar el script de población completa
python poblar_sistema_completo.py

echo ""
echo "✅ Datos iniciales creados correctamente:"
echo "   - Tenant: clinica-demo"
echo "   - Admin: admin@clinica-demo.com / admin123"
echo "   - Odontólogo: odontologo@clinica-demo.com / password123"
echo "   - 5 Pacientes con datos completos"
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
echo "   Odontólogo: odontologo@clinica-demo.com / password123"
echo "   Paciente 1: paciente1@test.com / password123"
echo ""
echo "🎉 ¡El sistema está listo para usarse!"
echo "======================================================================"
