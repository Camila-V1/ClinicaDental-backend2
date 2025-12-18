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
python manage.py migrate
echo ""
echo "🔄 Ejecutando migraciones de base de datos..."
echo "   → Migraciones compartidas (public schema)..."
python manage.py migrate_schemas --shared

# ============================================================================
# 3.1. CREAR Y MIGRAR TENANT clinica_demo (SI NO EXISTE)
# ============================================================================
echo ""
echo "🏥 Verificando tenant clinica_demo..."

# Intentar migrar el tenant (creará el schema si no existe)
python manage.py migrate_schemas --schema=clinica_demo || {
    echo "   ⚠️  Tenant clinica_demo no existe, intentando crear..."
    python scripts_poblacion/poblar_todo.py
}

echo "   ✅ Tenant clinica_demo verificado"

# ============================================================================
# 3.2. AGREGAR DOMINIO DE RENDER A clinica_demo
# ============================================================================
echo ""
echo "🌐 Configurando dominio de Render..."
python agregar_dominio_render.py || echo "   ⚠️  Advertencia: No se pudo ejecutar agregar_dominio_render.py"

# ============================================================================
# 4. POBLAR DATOS INICIALES (COMENTADO - Ejecutar manualmente cuando necesites)
# ============================================================================
# Para poblar datos ejecuta manualmente:
# python scripts_poblacion/poblar_todo.py
echo ""
echo "📝 Para poblar datos ejecuta: python scripts_poblacion/poblar_todo.py"

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
echo ""
echo "📱 USUARIOS PARA FLUTTER APP:"
echo "   Paciente 1: paciente1@test.com / password123"
echo "   María García: maria.garcia@email.com / password123"
echo "   Dr. Martínez: dr.martinez@clinica.com / password123"
echo ""
echo "🎉 ¡El sistema está listo para usarse!"
echo "======================================================================"
