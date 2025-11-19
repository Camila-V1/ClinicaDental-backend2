"""
Script para agregar documentos clínicos al historial de María García
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.files import File
from django.db import connection
from django.contrib.auth import get_user_model
from usuarios.models import PerfilPaciente
from historial_clinico.models import HistorialClinico, DocumentoClinico

Usuario = get_user_model()

def agregar_documentos():
    # Configurar schema del tenant
    connection.set_schema('clinica_demo')
    
    print("\n" + "="*60)
    print("📄 AGREGANDO DOCUMENTOS AL HISTORIAL DE MARÍA GARCÍA")
    print("="*60 + "\n")
    
    # Buscar a María García
    try:
        usuario = Usuario.objects.get(email='paciente1@test.com')
        paciente = usuario.perfil_paciente
        historial = HistorialClinico.objects.get(paciente=paciente)
        
        print(f"✅ Paciente encontrado: {usuario.nombre} {usuario.apellido}")
        print(f"✅ Historial - Paciente ID: {historial.paciente_id}")
        
    except Exception as e:
        print(f"❌ Error al buscar paciente: {e}")
        return
    
    # Ruta del PDF
    pdf_path = Path(__file__).parent / 'Informe de Auxiliares - Octubre[1].pdf'
    
    if not pdf_path.exists():
        print(f"❌ No se encontró el archivo PDF en: {pdf_path}")
        return
    
    print(f"✅ PDF encontrado: {pdf_path.name}")
    print(f"📁 Ruta completa: {pdf_path}")
    
    # Documentos a crear
    documentos = [
        {
            'descripcion': 'Informe de Valoración Inicial - Evaluación dental completa con diagnóstico de caries',
            'tipo_documento': 'INFORME'
        },
        {
            'descripcion': 'Radiografía Panorámica - Estado general de la dentadura',
            'tipo_documento': 'RADIOGRAFIA'
        },
        {
            'descripcion': 'Consentimiento Informado - Procedimiento de restauración dental',
            'tipo_documento': 'CONSENTIMIENTO'
        },
        {
            'descripcion': 'Receta Médica Post-Endodoncia - Analgésicos y antibióticos',
            'tipo_documento': 'RECETA'
        },
        {
            'descripcion': 'Examen de Laboratorio - Análisis de sangre pre-operatorio',
            'tipo_documento': 'LABORATORIO'
        },
        {
            'descripcion': 'Fotografía Intraoral - Estado inicial de caries en piezas 36 y 46',
            'tipo_documento': 'FOTOGRAFIA'
        }
    ]
    
    print(f"\n📋 Creando {len(documentos)} documentos...\n")
    
    documentos_creados = 0
    
    for doc_data in documentos:
        try:
            # Abrir el PDF
            with open(pdf_path, 'rb') as pdf_file:
                # Nombre del archivo según el tipo
                filename = f"{doc_data['tipo_documento'].lower()}_{historial.paciente_id}.pdf"
                
                # Crear el documento
                documento = DocumentoClinico.objects.create(
                    historial_clinico=historial,
                    descripcion=doc_data['descripcion'],
                    tipo_documento=doc_data['tipo_documento'],
                    archivo=File(pdf_file, name=filename)
                )
                
                documentos_creados += 1
                print(f"  ✅ {doc_data['tipo_documento']}: {doc_data['descripcion'][:50]}...")
                print(f"     📄 Archivo: {documento.archivo.name}")
                
        except Exception as e:
            print(f"  ❌ Error al crear {doc_data['descripcion'][:30]}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Proceso completado: {documentos_creados}/{len(documentos)} documentos creados")
    print(f"{'='*60}\n")
    
    # Verificar total de documentos
    total = DocumentoClinico.objects.filter(historial_clinico=historial).count()
    print(f"📊 Total de documentos en historial: {total}")
    
    # Mostrar lista
    if total > 0:
        print("\n📋 Documentos en el historial:")
        for doc in DocumentoClinico.objects.filter(historial_clinico=historial).order_by('-creado'):
            print(f"  • {doc.tipo_documento}: {doc.descripcion[:60]}")
            print(f"    📅 {doc.creado.strftime('%d/%m/%Y %H:%M')}")
            print(f"    📁 {doc.archivo.name}")
            print()

if __name__ == '__main__':
    agregar_documentos()
