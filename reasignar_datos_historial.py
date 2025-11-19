import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
connection.set_schema('clinica_demo')

from historial_clinico.models import HistorialClinico, DocumentoClinico, EpisodioAtencion
from usuarios.models import Usuario

# Buscar historial de María
user = Usuario.objects.get(email='paciente1@test.com')
historial_maria = HistorialClinico.objects.get(paciente=user.perfil_paciente)

print(f"✅ Historial de María García: ID {historial_maria.paciente_id}")
print(f"\n📊 Estado actual:")
print(f"  - Episodios: {historial_maria.episodios.count()}")
print(f"  - Documentos: {historial_maria.documentos.count()}")

# Buscar episodios huérfanos
episodios_huerfanos = EpisodioAtencion.objects.exclude(historial_clinico=historial_maria)
documentos_huerfanos = DocumentoClinico.objects.exclude(historial_clinico=historial_maria)

print(f"\n🔍 Encontrados:")
print(f"  - Episodios huérfanos: {episodios_huerfanos.count()}")
print(f"  - Documentos huérfanos: {documentos_huerfanos.count()}")

# Reasignar episodios
if episodios_huerfanos.exists():
    print(f"\n🔄 Reasignando {episodios_huerfanos.count()} episodios...")
    episodios_huerfanos.update(historial_clinico=historial_maria)
    print(f"  ✅ Episodios reasignados")

# Reasignar documentos
if documentos_huerfanos.exists():
    print(f"\n🔄 Reasignando {documentos_huerfanos.count()} documentos...")
    documentos_huerfanos.update(historial_clinico=historial_maria)
    print(f"  ✅ Documentos reasignados")

# Verificar resultado
print(f"\n📊 Estado final:")
print(f"  - Episodios: {historial_maria.episodios.count()}")
print(f"  - Documentos: {historial_maria.documentos.count()}")
print(f"  - Odontogramas: {historial_maria.odontogramas.count()}")
