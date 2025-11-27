#!/usr/bin/env python
"""
Script de prueba para el parser de voz de reportes.
Ejecutar: python test_voice_parser.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from reportes.nlp.voice_parser import parse_voice_command
import json

# Ejemplos de comandos de voz para probar
EJEMPLOS = [
    "dame las citas del 1 al 5 de septiembre",
    "mostrar facturas de la semana pasada",
    "reportes de tratamientos del mes actual",
    "citas de hoy",
    "facturas pendientes del 10 al 15 de diciembre",
    "ingresos de esta semana",
    "pacientes registrados este mes",
    "citas completadas del paciente Juan Pérez",
    "facturas mayores a 1000 del mes pasado",
    "tratamientos del 25 de agosto al 5 de septiembre",
    "citas de ayer",
    "facturas de enero",
    "reportes de los últimos 7 días",
]

print("=" * 80)
print("🧪 TEST DEL PARSER DE VOZ PARA REPORTES")
print("=" * 80)
print()

for i, comando in enumerate(EJEMPLOS, 1):
    print(f"\n{'─' * 80}")
    print(f"🎤 Ejemplo {i}: \"{comando}\"")
    print(f"{'─' * 80}")
    
    try:
        resultado = parse_voice_command(comando)
        
        print(f"\n📊 Tipo de reporte: {resultado['tipo_reporte']}")
        print(f"📅 Fecha inicio:    {resultado['fecha_inicio']}")
        print(f"📅 Fecha fin:       {resultado['fecha_fin']}")
        
        if resultado['filtros']:
            print(f"🔍 Filtros:         {json.dumps(resultado['filtros'], indent=2, ensure_ascii=False)}")
        else:
            print(f"🔍 Filtros:         (ninguno)")
        
        print(f"\n💡 Interpretación:")
        print(f"   \"{resultado['interpretacion']}\"")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)
print()
print("📝 INSTRUCCIONES PARA USO EN PRODUCCIÓN:")
print()
print("1. El frontend capta voz usando Web Speech API")
print("2. Transcribe el audio a texto")
print("3. Envía el texto al backend:")
print()
print("   POST /api/reportes/voice-query/")
print("   Headers: Authorization: Bearer <token>, x-tenant-id: <id>")
print("   Body: { \"texto\": \"dame las citas del 1 al 5 de septiembre\" }")
print()
print("4. El backend retorna:")
print("   - interpretacion: Lo que entendió")
print("   - datos: Resultados del reporte")
print("   - resumen: Estadísticas")
print()
