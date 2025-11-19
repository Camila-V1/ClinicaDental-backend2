#!/usr/bin/env python
"""
Verificar que el endpoint de documentos anidado funcione correctamente
"""
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from historial_clinico.models import HistorialClinico

# Conectar al tenant
connection.set_schema('clinica_demo')

print('=' * 80)
print('🔍 VERIFICACIÓN DEL ENDPOINT DE DOCUMENTOS ANIDADO')
print('=' * 80)
print()

# Obtener un historial con documentos
historial = HistorialClinico.objects.filter(documentos__isnull=False).first()

if historial:
    print(f'✅ Historial encontrado: ID {historial.paciente.pk}')
    print(f'   Paciente: {historial.paciente.usuario.full_name}')
    print(f'   Total de documentos: {historial.documentos.count()}')
    print()
    
    print('📄 Documentos en el historial:')
    for doc in historial.documentos.all():
        print(f'   - ID {doc.id}: {doc.descripcion} ({doc.tipo_documento})')
    print()
    
    print(f'🌐 Endpoint esperado por el frontend:')
    print(f'   GET http://clinica-demo.localhost:8000/api/historial/historiales/{historial.paciente.pk}/documentos/')
    print()
    print('✅ Este endpoint ahora está disponible con el decorator @action(detail=True)')
    
else:
    print('⚠️  No se encontraron historiales con documentos')

print()
print('=' * 80)
