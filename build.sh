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
python manage.py migrate_schemas --shared

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
