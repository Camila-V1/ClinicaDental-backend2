import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
connection.set_schema('clinica_demo')

from historial_clinico.models import HistorialClinico, DocumentoClinico
from historial_clinico.serializers import HistorialClinicoSerializer
from usuarios.models import Usuario

user = Usuario.objects.get(email='paciente1@test.com')
historial = HistorialClinico.objects.prefetch_related(
    'episodios', 'odontogramas', 'documentos'
).get(paciente=user.perfil_paciente)

# Verificar ORM
print("📊 VERIFICACIÓN EN ORM:")
print(f"  Documentos en BD: {historial.documentos.count()}")
print(f"  Episodios en BD: {historial.episodios.count()}")
print(f"  Odontogramas en BD: {historial.odontogramas.count()}")

# Verificar serializer
data = HistorialClinicoSerializer(historial).data
print("\n📊 VERIFICACIÓN EN SERIALIZER:")
print(f"  Documentos en respuesta: {len(data.get('documentos', []))}")
print(f"  Campo total_documentos: {data.get('total_documentos')}")
print(f"  Episodios en respuesta: {len(data.get('episodios', []))}")
print(f"  Campo total_episodios: {data.get('total_episodios')}")

if data.get('documentos'):
    print("\n📄 PRIMEROS 3 DOCUMENTOS:")
    for doc in data['documentos'][:3]:
        print(f"  - {doc['tipo_documento']}: {doc['descripcion'][:50]}")
