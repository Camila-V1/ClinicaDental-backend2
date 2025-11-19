#!/usr/bin/env python
"""
Verificar que los documentos clínicos se crearon correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from historial_clinico.models import DocumentoClinico, HistorialClinico

# Conectar al tenant
connection.set_schema('clinica_demo')

print('=' * 80)
print('📄 VERIFICACIÓN DE DOCUMENTOS CLÍNICOS')
print('=' * 80)
print()

# Obtener todos los documentos
documentos = DocumentoClinico.objects.all()

print(f'Total de documentos: {documentos.count()}')
print()

for doc in documentos:
    print(f'📄 Documento ID: {doc.id}')
    print(f'   Tipo: {doc.tipo_documento} ({doc.get_tipo_documento_display()})')
    print(f'   Descripción: {doc.descripcion}')
    print(f'   Archivo: {doc.archivo.name if doc.archivo else "Sin archivo"}')
    print(f'   Historial: {doc.historial_clinico.paciente.usuario.full_name}')
    print(f'   Creado: {doc.creado.strftime("%Y-%m-%d %H:%M")}')
    print()

print('=' * 80)
print('✅ Verificación completada')
print('=' * 80)
