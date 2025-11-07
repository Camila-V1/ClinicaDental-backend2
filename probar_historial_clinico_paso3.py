#!/usr/bin/env python
"""
Script de prueba completo para el módulo historial_clinico.
Prueba los CU08, CU09, CU10 y CU11.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo, Especialidad
from tratamientos.models import PlanDeTratamiento, ItemPlanTratamiento, Servicio
from historial_clinico.models import HistorialClinico, EpisodioAtencion, Odontograma, DocumentoClinico
from tenants.models import Clinica
from datetime import datetime, date
import json


def probar_historial_clinico():
    """Prueba completa del módulo historial_clinico."""
    
    print("\n🏥 === PROBANDO MÓDULO HISTORIAL CLÍNICO ===")
    print("CU08: Historial Clínico")
    print("CU09: Episodios de Atención") 
    print("CU10: Odontograma")
    print("CU11: Documentos Clínicos")
    
    with schema_context('clinica_demo'):
        
        # === CU08: HISTORIAL CLÍNICO ===
        print("\n📋 CU08: CREANDO HISTORIAL CLÍNICO...")
        
        # Buscar un paciente existente o crear uno
        paciente_usuario = Usuario.objects.filter(tipo_usuario='PACIENTE').first()
        if not paciente_usuario:
            # Crear un paciente de prueba
            paciente_usuario = Usuario.objects.create_user(
                email='paciente.historial@test.com',
                nombre='Ana',
                apellido='Martínez',
                ci='1111111111',
                sexo='F',
                telefono='+591-11111111',
                password='password123',
                tipo_usuario='PACIENTE'
            )
            
            PerfilPaciente.objects.create(
                usuario=paciente_usuario,
                fecha_de_nacimiento=date(1985, 3, 15),
                direccion='Calle Falsa 123'
            )
        
        # Obtener el perfil del paciente
        perfil_paciente = paciente_usuario.perfil_paciente
        
        # Crear o obtener historial clínico
        historial, created = HistorialClinico.objects.get_or_create(
            paciente=perfil_paciente,
            defaults={
                'antecedentes_medicos': 'Hipertensión arterial controlada. Alergia a la penicilina.',
                'alergias': 'Penicilina, Ibuprofeno',
                'medicamentos_actuales': 'Losartán 50mg (1 vez al día), Omeprazol 20mg (en ayunas)'
            }
        )
        
        if created:
            print(f"✅ Historial creado para {perfil_paciente.usuario.full_name}")
        else:
            print(f"✅ Historial encontrado para {perfil_paciente.usuario.full_name}")
        
        print(f"   🩺 Antecedentes: {historial.antecedentes_medicos[:50]}...")
        print(f"   ⚠️  Alergias: {historial.alergias}")
        print(f"   💊 Medicamentos: {historial.medicamentos_actuales[:50]}...")
        
        # === PREPARAR ODONTÓLOGO ===
        print("\n👨‍⚕️ PREPARANDO ODONTÓLOGO...")
        
        # Buscar odontólogo existente o crear uno
        odontologo_usuario = Usuario.objects.filter(tipo_usuario='ODONTOLOGO').first()
        
        if not odontologo_usuario:
            # Crear especialidad
            especialidad, _ = Especialidad.objects.get_or_create(
                nombre='Odontología General',
                defaults={
                    'descripcion': 'Práctica general de odontología',
                    'activo': True
                }
            )
            
            # Crear odontólogo
            odontologo_usuario = Usuario.objects.create_user(
                email='dr.historial@test.com',
                nombre='Dr. Carlos',
                apellido='Rodríguez',
                ci='2222222222',
                sexo='M',
                telefono='+591-22222222',
                password='password123',
                tipo_usuario='ODONTOLOGO',
                is_staff=True
            )
            
            # Crear perfil de odontólogo
            especialidad, _ = Especialidad.objects.get_or_create(
                nombre='Odontología General',
                defaults={
                    'descripcion': 'Práctica general de odontología',
                    'activo': True
                }
            )
            
            perfil_odontologo = PerfilOdontologo.objects.create(
                usuario=odontologo_usuario,
                especialidad=especialidad,
                cedulaProfesional='DOC-HIST-001',
                experienciaProfesional='15 años de experiencia en odontología general'
            )
        else:
            # Verificar si tiene perfil, si no, crearlo
            if hasattr(odontologo_usuario, 'perfil_odontologo'):
                perfil_odontologo = odontologo_usuario.perfil_odontologo
            else:
                # Crear especialidad si no existe
                especialidad, _ = Especialidad.objects.get_or_create(
                    nombre='Odontología General',
                    defaults={
                        'descripcion': 'Práctica general de odontología',
                        'activo': True
                    }
                )
                
                # Crear perfil
                perfil_odontologo = PerfilOdontologo.objects.create(
                    usuario=odontologo_usuario,
                    especialidad=especialidad,
                    cedulaProfesional='DOC-HIST-001',
                    experienciaProfesional='15 años de experiencia en odontología general'
                )
        print(f"✅ Odontólogo: {perfil_odontologo.usuario.full_name}")
        print(f"   🎓 Especialidad: {perfil_odontologo.especialidad.nombre}")
        
        # === PREPARAR PLAN DE TRATAMIENTO ===
        print("\n📋 PREPARANDO PLAN DE TRATAMIENTO...")
        
        # Buscar servicio existente o crear uno
        servicio, _ = Servicio.objects.get_or_create(
            nombre='Limpieza Dental',
            defaults={
                'descripcion': 'Profilaxis dental completa',
                'precio_base': 150.00,
                'activo': True
            }
        )
        
        # Crear plan de tratamiento si no existe
        plan, created = PlanDeTratamiento.objects.get_or_create(
            paciente=perfil_paciente,
            estado='PROPUESTO',
            defaults={
                'titulo': 'Plan de Limpieza Dental',
                'descripcion': 'Plan de tratamiento para limpieza y revisión general',
                'odontologo': perfil_odontologo
            }
        )
        
        # Crear ítem del plan
        item_plan, _ = ItemPlanTratamiento.objects.get_or_create(
            plan=plan,
            servicio=servicio,
            defaults={
                'orden': 1,
                'notas': 'Limpieza dental programada'
            }
        )
        
        print(f"✅ Plan de tratamiento creado")
        print(f"   🦷 Servicio: {item_plan.servicio.nombre}")
        print(f"   💰 Precio: ${item_plan.precio_servicio_snapshot or servicio.precio_base}")
        
        # === CU09: EPISODIO DE ATENCIÓN ===
        print("\n🏥 CU09: CREANDO EPISODIO DE ATENCIÓN...")
        
        episodio = EpisodioAtencion.objects.create(
            historial_clinico=historial,
            odontologo=perfil_odontologo,
            item_plan_tratamiento=item_plan,
            motivo_consulta='Limpieza dental programada y revisión general',
            diagnostico='Gingivitis leve. Sarro en molares inferiores. Estado general satisfactorio.',
            descripcion_procedimiento='Se realizó limpieza dental completa con ultrasonido. Aplicación de flúor. Pulido dental. Revisión de todas las piezas dentales. No se encontraron caries activas.',
            notas_privadas='Paciente colaboradora. Buena higiene oral. Recomendado control en 6 meses.'
        )
        
        print(f"✅ Episodio creado: {episodio.fecha_atencion.strftime('%Y-%m-%d %H:%M')}")
        print(f"   👨‍⚕️ Odontólogo: {episodio.odontologo.usuario.full_name}")
        print(f"   🎯 Motivo: {episodio.motivo_consulta}")
        print(f"   🔬 Diagnóstico: {episodio.diagnostico[:60]}...")
        print(f"   ⚡ Procedimiento: {episodio.descripcion_procedimiento[:60]}...")
        
        # === CU10: ODONTOGRAMA ===
        print("\n🦷 CU10: CREANDO ODONTOGRAMA...")
        
        # Estado ejemplo de piezas dentales
        estado_piezas_ejemplo = {
            # Cuadrante 1 (superior derecho)
            "18": {"estado": "ausente", "observaciones": "Extracción previa"},
            "17": {"estado": "obturado", "cara": "oclusal", "material": "amalgama"},
            "16": {"estado": "sano"},
            "15": {"estado": "sano"},
            "14": {"estado": "sano"},
            "13": {"estado": "sano"},
            "12": {"estado": "sano"},
            "11": {"estado": "sano"},
            
            # Cuadrante 2 (superior izquierdo)
            "21": {"estado": "sano"},
            "22": {"estado": "sano"},
            "23": {"estado": "sano"},
            "24": {"estado": "caries", "grado": "leve", "cara": "oclusal"},
            "25": {"estado": "sano"},
            "26": {"estado": "obturado", "cara": "oclusal", "material": "resina"},
            "27": {"estado": "sano"},
            "28": {"estado": "sano"},
            
            # Cuadrante 3 (inferior izquierdo)
            "38": {"estado": "sano"},
            "37": {"estado": "sano"},
            "36": {"estado": "obturado", "cara": "oclusal", "material": "amalgama"},
            "35": {"estado": "sano"},
            "34": {"estado": "sano"},
            "33": {"estado": "sano"},
            "32": {"estado": "sano"},
            "31": {"estado": "sano"},
            
            # Cuadrante 4 (inferior derecho)
            "41": {"estado": "sano"},
            "42": {"estado": "sano"},
            "43": {"estado": "sano"},
            "44": {"estado": "sano"},
            "45": {"estado": "sano"},
            "46": {"estado": "obturado", "cara": "mesio-oclusal", "material": "resina"},
            "47": {"estado": "caries", "grado": "moderada", "cara": "distal"},
            "48": {"estado": "sano"}
        }
        
        odontograma = Odontograma.objects.create(
            historial_clinico=historial,
            estado_piezas=estado_piezas_ejemplo,
            notas='Odontograma inicial. Se observa gingivitis leve generalizada. Presencia de sarro en sectores posteriores. Dos caries activas que requieren tratamiento.'
        )
        
        print(f"✅ Odontograma creado: {odontograma.fecha_snapshot.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🦷 Piezas registradas: {len(estado_piezas_ejemplo)}")
        
        # Estadísticas del odontograma
        piezas_sanas = sum(1 for p in estado_piezas_ejemplo.values() if p.get('estado') == 'sano')
        piezas_obturadas = sum(1 for p in estado_piezas_ejemplo.values() if p.get('estado') == 'obturado')
        piezas_caries = sum(1 for p in estado_piezas_ejemplo.values() if p.get('estado') == 'caries')
        piezas_ausentes = sum(1 for p in estado_piezas_ejemplo.values() if p.get('estado') == 'ausente')
        
        print(f"   ✅ Sanas: {piezas_sanas}")
        print(f"   🔨 Obturadas: {piezas_obturadas}")
        print(f"   ⚠️  Con caries: {piezas_caries}")
        print(f"   ❌ Ausentes: {piezas_ausentes}")
        
        # === CU11: DOCUMENTO CLÍNICO ===
        print("\n📄 CU11: CREANDO DOCUMENTOS CLÍNICOS...")
        
        # Simular documentos (sin archivos reales en esta prueba)
        documentos_ejemplo = [
            {
                'descripcion': 'Radiografía panorámica inicial',
                'tipo_documento': 'RADIOGRAFIA',
            },
            {
                'descripcion': 'Fotografía intraoral antes del tratamiento',
                'tipo_documento': 'FOTOGRAFIA',
            },
            {
                'descripcion': 'Consentimiento informado para limpieza dental',
                'tipo_documento': 'CONSENTIMIENTO',
            }
        ]
        
        documentos_creados = []
        for doc_data in documentos_ejemplo:
            # Nota: En una implementación real, aquí se subirían archivos reales
            # Por ahora solo creamos los registros sin archivo
            documento = DocumentoClinico.objects.create(
                historial_clinico=historial,
                descripcion=doc_data['descripcion'],
                tipo_documento=doc_data['tipo_documento']
                # archivo se omite para esta prueba
            )
            documentos_creados.append(documento)
            
            print(f"✅ Documento: {documento.get_tipo_documento_display()}")
            print(f"   📝 Descripción: {documento.descripcion}")
            print(f"   📅 Creado: {documento.creado.strftime('%Y-%m-%d %H:%M')}")
        
        # === ESTADÍSTICAS FINALES ===
        print("\n📊 ESTADÍSTICAS FINALES DEL HISTORIAL...")
        
        total_episodios = historial.episodios.count()
        total_odontogramas = historial.odontogramas.count() 
        total_documentos = historial.documentos.count()
        
        print(f"   📋 Total episodios de atención: {total_episodios}")
        print(f"   🦷 Total odontogramas: {total_odontogramas}")
        print(f"   📄 Total documentos: {total_documentos}")
        
        # Último episodio
        ultimo_episodio = historial.episodios.first()
        if ultimo_episodio:
            print(f"   🕒 Última atención: {ultimo_episodio.fecha_atencion.strftime('%Y-%m-%d')}")
            print(f"   👨‍⚕️ Por: {ultimo_episodio.odontologo.usuario.full_name}")
        
        # === PRUEBAS DE CONSULTA ===
        print("\n🔍 PROBANDO CONSULTAS Y FILTROS...")
        
        # Buscar episodios por odontólogo
        episodios_doctor = EpisodioAtencion.objects.filter(
            odontologo=perfil_odontologo
        ).count()
        print(f"✅ Episodios atendidos por {perfil_odontologo.usuario.full_name}: {episodios_doctor}")
        
        # Buscar documentos por tipo
        radiografias = DocumentoClinico.objects.filter(
            historial_clinico=historial,
            tipo_documento='RADIOGRAFIA'
        ).count()
        print(f"✅ Radiografías en el historial: {radiografias}")
        
        # Historial completo del paciente
        print(f"✅ Historial completo de {perfil_paciente.usuario.full_name}:")
        print(f"   👤 CI: {perfil_paciente.usuario.ci}")
        print(f"   📧 Email: {perfil_paciente.usuario.email}")
        print(f"   🎂 Fecha nacimiento: {perfil_paciente.fecha_de_nacimiento}")
        print(f"   📍 Dirección: {perfil_paciente.direccion}")
        print(f"   ⚠️  Alergias: {historial.alergias}")
        print(f"   💊 Medicamentos: {historial.medicamentos_actuales}")
        
        # === VERIFICAR RELACIONES ===
        print("\n🔗 VERIFICANDO RELACIONES ENTRE MODELOS...")
        
        print(f"✅ Historial → Episodios: {historial.episodios.count()}")
        print(f"✅ Historial → Odontogramas: {historial.odontogramas.count()}")
        print(f"✅ Historial → Documentos: {historial.documentos.count()}")
        print(f"✅ Episodio → Plan de Tratamiento: {episodio.item_plan_tratamiento.plan if episodio.item_plan_tratamiento else 'No vinculado'}")
        print(f"✅ Odontólogo → Episodios atendidos: {perfil_odontologo.episodios_atendidos.count()}")
        
    print("\n🎉 ¡TODAS LAS PRUEBAS DEL HISTORIAL CLÍNICO COMPLETADAS!")
    print("\n✅ FUNCIONALIDADES PROBADAS:")
    print("   • CU08: Historial Clínico ✅")
    print("   • CU09: Episodios de Atención ✅") 
    print("   • CU10: Odontograma ✅")
    print("   • CU11: Documentos Clínicos ✅")
    print("   • Relaciones entre modelos ✅")
    print("   • Consultas y filtros ✅")


if __name__ == "__main__":
    probar_historial_clinico()