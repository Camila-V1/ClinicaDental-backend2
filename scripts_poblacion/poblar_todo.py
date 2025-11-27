#!/usr/bin/env python
"""
============================================================================
SCRIPT PRINCIPAL DE POBLACIÓN DE BASE DE DATOS
============================================================================
Sistema modular para poblar la base de datos de Clínica Dental

Ejecutar: python scripts_poblacion/poblar_todo.py
============================================================================
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from tenants.models import Clinica, Domain
from django_tenants.utils import schema_context

# Importar módulos de población
from scripts_poblacion import (
    crear_tenant,
    poblar_usuarios,
    poblar_tratamientos,
    poblar_inventario,
    poblar_agenda,
    poblar_historial,
    poblar_facturacion,
    poblar_planes_tratamiento,
)


def print_header(mensaje):
    """Imprime un encabezado bonito"""
    print("\n" + "="*70)
    print(f"  {mensaje}")
    print("="*70)


def print_success(mensaje):
    """Imprime mensaje de éxito"""
    print(f"✅ {mensaje}")


def print_info(mensaje):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {mensaje}")


def limpiar_tenant_existente(schema_name):
    """Limpia un tenant existente (CUIDADO: Borra todos los datos)"""
    print_header(f"🗑️  LIMPIANDO TENANT: {schema_name}")
    
    try:
        # Verificar si existe
        clinica = Clinica.objects.filter(schema_name=schema_name).first()
        
        if clinica:
            print_info(f"Tenant encontrado: {clinica.nombre}")
            
            # Eliminar dominios asociados
            dominios = Domain.objects.filter(tenant=clinica)
            print_info(f"Eliminando {dominios.count()} dominios...")
            dominios.delete()
            
            # Eliminar el tenant (esto borra el schema completo)
            print_info("Eliminando tenant y su schema...")
            clinica.delete()
            
            print_success(f"Tenant {schema_name} eliminado correctamente")
        else:
            print_info(f"No existe tenant con schema {schema_name}")
            
    except Exception as e:
        print(f"⚠️  Error al limpiar tenant: {e}")


def main():
    """Función principal"""
    print_header("🚀 INICIANDO POBLACIÓN DE BASE DE DATOS")
    
    # Configuración del tenant a poblar
    DOMINIO_PRINCIPAL = 'clinicademo1.dentaabcxy.store'
    SCHEMA_NAME = 'clinica_demo'
    NOMBRE_CLINICA = 'Clínica Demo'
    
    # Opción 1: Limpiar tenant existente (CUIDADO: Borra todo)
    # Descomentar si quieres empezar desde cero
    # limpiar_tenant_existente(SCHEMA_NAME)
    
    # Paso 1: Crear/Verificar Tenant
    print_header("📋 PASO 1: CREAR/VERIFICAR TENANT")
    tenant = crear_tenant.crear_o_verificar_tenant(
        schema_name=SCHEMA_NAME,
        nombre=NOMBRE_CLINICA,
        dominio_principal=DOMINIO_PRINCIPAL
    )
    
    if not tenant:
        print("❌ Error: No se pudo crear el tenant")
        return
    
    print_success(f"Tenant configurado: {tenant.nombre}")
    
    # Trabajar dentro del schema del tenant
    with schema_context(SCHEMA_NAME):
        
        # Paso 2: Poblar Usuarios
        print_header("👥 PASO 2: POBLAR USUARIOS")
        usuarios = poblar_usuarios.poblar_usuarios()
        odontologos = poblar_usuarios.obtener_odontologos()
        pacientes = poblar_usuarios.obtener_pacientes()
        print_success(f"Creados {len(usuarios)} usuarios")
        
        # Paso 3: Poblar Servicios (antes Tratamientos)
        print_header("🦷 PASO 3: POBLAR SERVICIOS")
        servicios = poblar_tratamientos.poblar_tratamientos()
        print_success(f"Creados {len(servicios)} servicios")
        
        # Paso 4: Poblar Inventario (Insumos)
        print_header("📦 PASO 4: POBLAR INVENTARIO")
        categorias, insumos = poblar_inventario.poblar_inventario()
        print_success(f"Creadas {len(categorias)} categorías y {len(insumos)} insumos")
        
        # Paso 5: Poblar Agenda
        print_header("📅 PASO 5: POBLAR AGENDA")
        citas = poblar_agenda.poblar_agenda(odontologos, pacientes, servicios)
        citas_atendidas = [c for c in citas if c.estado == 'ATENDIDA']
        print_success(f"Creadas {len(citas)} citas")
        
        # Paso 6: Poblar Historial Clínico
        print_header("📋 PASO 6: POBLAR HISTORIAL CLÍNICO")
        historiales, episodios, odontogramas = poblar_historial.poblar_historial(
            odontologos, pacientes, citas_atendidas
        )
        print_success(f"Creados {len(historiales)} historiales, {len(episodios)} episodios y {len(odontogramas)} odontogramas")
        
        # Paso 7: Poblar Planes de Tratamiento
        print_header("🦷 PASO 7: POBLAR PLANES DE TRATAMIENTO")
        planes, items_plan = poblar_planes_tratamiento.poblar_planes_tratamiento(
            pacientes, odontologos, servicios
        )
        print_success(f"Creados {len(planes)} planes de tratamiento con {len(items_plan)} procedimientos")
        
        # Paso 8: Poblar Facturación
        print_header("💰 PASO 8: POBLAR FACTURACIÓN")
        facturas, pagos = poblar_facturacion.poblar_facturacion(
            pacientes, citas_atendidas
        )
        print_success(f"Creadas {len(facturas)} facturas y {len(pagos)} pagos")
    
    # Resumen Final
    print_header("✅ POBLACIÓN COMPLETADA EXITOSAMENTE")
    print(f"""
    📊 RESUMEN:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🏥 Clínica:           {NOMBRE_CLINICA}
    🌐 Dominio:           {DOMINIO_PRINCIPAL}
    📁 Schema:            {SCHEMA_NAME}
    
    👥 Usuarios:          {len(usuarios)}
    🦷 Servicios:         {len(servicios)}
    📦 Insumos:           {len(insumos)}
    📅 Citas:             {len(citas)}
    📋 Historiales:       {len(historiales)}
    📋 Episodios:         {len(episodios)}
    🦷 Planes Trat.:      {len(planes)}
    🔧 Procedimientos:    {len(items_plan)}
    💰 Facturas:          {len(facturas)}
    💰 Pagos:             {len(pagos)}
    
    🔐 CREDENCIALES DE ACCESO:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Admin:         admin@clinicademo1.com / admin123
    Odontólogo 1:  odontologo@clinica-demo.com / odontologo123
    Odontólogo 2:  dra.lopez@clinica-demo.com / odontologo123
    Paciente 1:    paciente1@test.com / paciente123
    Paciente 2:    paciente2@test.com / paciente123
    Paciente 3:    paciente3@test.com / paciente123
    
    🌐 ACCESO:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Frontend:  https://{DOMINIO_PRINCIPAL}
    Backend:   https://clinica-dental-backend.onrender.com
    
    🎉 ¡Sistema listo para usar!
    """)


if __name__ == '__main__':
    main()
