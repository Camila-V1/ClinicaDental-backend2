#!/usr/bin/env python
"""
SCRIPT: Crear perfiles de usuarios para demostrar el Paso 2.C

Este script crea los perfiles de odontólogo y paciente necesarios
para probar el sistema de precios dinámicos.
"""

import os
import sys
import django
from datetime import date

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from usuarios.models import Usuario, PerfilOdontologo, PerfilPaciente, Especialidad


def main():
    """Crear perfiles necesarios para la demostración"""
    print("👥 CREANDO PERFILES DE USUARIO PARA PASO 2.C")
    
    # Obtener clínica demo
    try:
        clinica_demo = Clinica.objects.get(schema_name='clinica_demo')
    except Clinica.DoesNotExist:
        print("❌ Error: No existe la clínica de demostración")
        return
    
    with tenant_context(clinica_demo):
        # Crear especialidad si no existe
        especialidad, created = Especialidad.objects.get_or_create(
            nombre="Odontología General",
            defaults={
                'descripcion': 'Especialidad general en odontología',
                'activa': True
            }
        )
        
        if created:
            print(f"✅ Especialidad creada: {especialidad.nombre}")
        else:
            print(f"ℹ️  Especialidad existente: {especialidad.nombre}")
        
        # Buscar usuario admin existente
        admin_user = Usuario.objects.filter(email='admin@clinica.com').first()
        
        if admin_user:
            # Crear perfil odontólogo para el admin si no existe
            odontologo, created = PerfilOdontologo.objects.get_or_create(
                usuario=admin_user,
                defaults={
                    'cedulaProfesional': 'LIC001',
                    'especialidad': especialidad,
                    'experienciaProfesional': '5 años de experiencia en odontología general'
                }
            )
            
            if created:
                print(f"✅ Perfil odontólogo creado para: Dr. {admin_user.nombre} {admin_user.apellido}")
            else:
                print(f"ℹ️  Perfil odontólogo existente: Dr. {admin_user.nombre} {admin_user.apellido}")
        
        # Crear un usuario paciente de prueba
        paciente_user, created = Usuario.objects.get_or_create(
            email='paciente@demo.com',
            defaults={
                'nombre': 'Juan Carlos',
                'apellido': 'Pérez García',
                'is_active': True
            }
        )
        
        if created:
            paciente_user.set_password('demo123')
            paciente_user.save()
            print(f"✅ Usuario paciente creado: {paciente_user.nombre} {paciente_user.apellido}")
        else:
            print(f"ℹ️  Usuario paciente existente: {paciente_user.nombre} {paciente_user.apellido}")
        
        # Crear perfil paciente
        paciente, created = PerfilPaciente.objects.get_or_create(
            usuario=paciente_user,
            defaults={
                'fecha_de_nacimiento': date(1985, 3, 15),
                'direccion': 'Calle Principal 123, Ciudad'
            }
        )
        
        if created:
            print(f"✅ Perfil paciente creado para: {paciente_user.nombre} {paciente_user.apellido}")
        else:
            print(f"ℹ️  Perfil paciente existente: {paciente_user.nombre} {paciente_user.apellido}")
        
        # Resumen final
        print("\n📊 RESUMEN DE PERFILES:")
        print(f"   🦷 Odontólogos: {PerfilOdontologo.objects.count()}")
        print(f"   🧑‍⚕️ Pacientes: {PerfilPaciente.objects.count()}")
        print(f"   🏥 Especialidades: {Especialidad.objects.count()}")
        
        print("\n✅ ¡Perfiles creados correctamente!")
        print("   Ahora puedes ejecutar: python crear_datos_prueba_2c.py")


if __name__ == '__main__':
    main()