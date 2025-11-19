import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
connection.set_schema('clinica_demo')

from historial_clinico.models import HistorialClinico
from historial_clinico.serializers import HistorialClinicoSerializer
from usuarios.models import Usuario

user = Usuario.objects.get(email='paciente1@test.com')
historial = HistorialClinico.objects.prefetch_related(
    'episodios', 'odontogramas', 'documentos'
).get(paciente=user.perfil_paciente)

serializer = HistorialClinicoSerializer(historial)
data = serializer.data

print("📊 VERIFICACIÓN COMPLETA:")
print(f"\nTotal documentos en BD (ORM): {historial.documentos.count()}")
print(f"Total documentos en serializer: {len(data.get('documentos', []))}")
print(f"Campo 'total_documentos': {data.get('total_documentos')}")

print(f"\n📄 Primeros 3 documentos en serializer:")
for i, doc in enumerate(data.get('documentos', [])[:3], 1):
    print(f"  {i}. {doc.get('tipo_documento')}: {doc.get('descripcion')[:50]}")

print(f"\n🔍 JSON resumido (primeros 500 chars):")
json_str = json.dumps(dict(data), indent=2, default=str)
print(json_str[:500] + "...")
