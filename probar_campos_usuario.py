#!/usr/bin/env python
"""
Script para probar los nuevos campos CI, sexo y teléfono en el modelo Usuario.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo, Especialidad
from tenants.models import Clinica


def probar_campos_usuario():
    """Prueba los nuevos campos en el modelo Usuario."""
    
    print("\n🧪 === PROBANDO NUEVOS CAMPOS DE USUARIO ===")
    
    # Usar el tenant de demostración
    try:
        tenant = Clinica.objects.get(schema_name='clinica_demo')
        print(f"✅ Usando tenant: {tenant.nombre}")
    except Clinica.DoesNotExist:
        print("❌ Tenant 'clinica_demo' no encontrado")
        return
    
    with schema_context('clinica_demo'):
        
        # 1. CREAR UN PACIENTE CON NUEVOS CAMPOS
        print("\n📋 1. CREANDO PACIENTE CON NUEVOS CAMPOS...")
        
        # Verificar si ya existe y eliminarlo completamente
        email_paciente = 'paciente_test@test.com'
        if Usuario.objects.filter(email=email_paciente).exists():
            usuario_existente = Usuario.objects.get(email=email_paciente)
            # Eliminar perfil si existe
            if hasattr(usuario_existente, 'perfil_paciente'):
                usuario_existente.perfil_paciente.delete()
            usuario_existente.delete()
        
        paciente = Usuario.objects.create_user(
            email=email_paciente,
            nombre='María',
            apellido='González',
            ci='1234567890',
            sexo='F',
            telefono='+591-12345678',
            password='password123',
            tipo_usuario='PACIENTE'
        )
        
        # Crear perfil de paciente
        PerfilPaciente.objects.create(
            usuario=paciente,
            fecha_de_nacimiento='1990-05-15',
            direccion='Av. Siempre Viva 123'
        )
        
        print(f"✅ Paciente creado: {paciente.full_name}")
        print(f"   📧 Email: {paciente.email}")
        print(f"   🆔 CI: {paciente.ci}")
        print(f"   👤 Sexo: {paciente.get_sexo_display()}")
        print(f"   📱 Teléfono: {paciente.telefono}")
        
        # 2. CREAR UN ODONTÓLOGO CON NUEVOS CAMPOS
        print("\n🦷 2. CREANDO ODONTÓLOGO CON NUEVOS CAMPOS...")
        
        # Verificar si ya existe y eliminarlo completamente
        email_odontologo = 'odontologo_test@test.com'
        if Usuario.objects.filter(email=email_odontologo).exists():
            usuario_existente = Usuario.objects.get(email=email_odontologo)
            # Eliminar perfil si existe
            if hasattr(usuario_existente, 'perfil_odontologo'):
                usuario_existente.perfil_odontologo.delete()
            usuario_existente.delete()
        
        # Obtener o crear especialidad
        especialidad, created = Especialidad.objects.get_or_create(
            nombre='Ortodoncia',
            defaults={
                'descripcion': 'Especialidad en corrección dental',
                'activo': True
            }
        )
        
        odontologo = Usuario.objects.create_user(
            email=email_odontologo,
            nombre='Dr. Carlos',
            apellido='Pérez',
            ci='0987654321',
            sexo='M',
            telefono='+591-87654321',
            password='password123',
            tipo_usuario='ODONTOLOGO'
        )
        
        # Crear perfil de odontólogo
        PerfilOdontologo.objects.create(
            usuario=odontologo,
            especialidad=especialidad,
            cedulaProfesional='DOC-123456',
            experienciaProfesional='10 años de experiencia en ortodoncia'
        )
        
        print(f"✅ Odontólogo creado: {odontologo.full_name}")
        print(f"   📧 Email: {odontologo.email}")
        print(f"   🆔 CI: {odontologo.ci}")
        print(f"   👤 Sexo: {odontologo.get_sexo_display()}")
        print(f"   📱 Teléfono: {odontologo.telefono}")
        print(f"   🎓 Especialidad: {odontologo.perfil_odontologo.especialidad.nombre}")
        
        # 3. CREAR ADMIN CON NUEVOS CAMPOS
        print("\n👨‍💼 3. CREANDO ADMIN CON NUEVOS CAMPOS...")
        
        # Verificar si ya existe y eliminarlo completamente
        email_admin = 'admin_test@test.com'
        if Usuario.objects.filter(email=email_admin).exists():
            Usuario.objects.get(email=email_admin).delete()
        
        admin = Usuario.objects.create_user(
            email=email_admin,
            nombre='Ana',
            apellido='López',
            ci='5555555555',
            sexo='F',
            telefono='+591-55555555',
            password='password123',
            tipo_usuario='ADMIN',
            is_staff=True
        )
        
        print(f"✅ Admin creado: {admin.full_name}")
        print(f"   📧 Email: {admin.email}")
        print(f"   🆔 CI: {admin.ci}")
        print(f"   👤 Sexo: {admin.get_sexo_display()}")
        print(f"   📱 Teléfono: {admin.telefono}")
        
        # 4. VERIFICAR BÚSQUEDAS
        print("\n🔍 4. PROBANDO BÚSQUEDAS POR NUEVOS CAMPOS...")
        
        # Buscar por CI
        usuario_por_ci = Usuario.objects.filter(ci='1234567890').first()
        print(f"✅ Búsqueda por CI: {usuario_por_ci.full_name if usuario_por_ci else 'No encontrado'}")
        
        # Buscar por sexo
        usuarios_femeninos = Usuario.objects.filter(sexo='F').count()
        print(f"✅ Usuarios femeninos: {usuarios_femeninos}")
        
        # Buscar por teléfono
        usuario_por_telefono = Usuario.objects.filter(telefono__contains='+591-12345678').first()
        print(f"✅ Búsqueda por teléfono: {usuario_por_telefono.full_name if usuario_por_telefono else 'No encontrado'}")
        
        # 5. VERIFICAR VALIDACIONES
        print("\n✅ 5. PROBANDO VALIDACIONES...")
        
        try:
            # Intentar crear usuario con CI duplicado
            Usuario.objects.create_user(
                email='duplicado@test.com',
                nombre='Test',
                apellido='Duplicado',
                ci='1234567890',  # CI ya existe
                password='password123'
            )
            print("❌ ERROR: Se permitió CI duplicado")
        except Exception as e:
            print("✅ Validación CI único: Funcionando correctamente")
        
        # 6. MOSTRAR ESTADÍSTICAS
        print("\n📊 6. ESTADÍSTICAS FINALES...")
        
        total_usuarios = Usuario.objects.count()
        usuarios_con_ci = Usuario.objects.exclude(ci__isnull=True).exclude(ci='').count()
        usuarios_con_sexo = Usuario.objects.exclude(sexo__isnull=True).count()
        usuarios_con_telefono = Usuario.objects.exclude(telefono__isnull=True).exclude(telefono='').count()
        
        print(f"   👥 Total usuarios: {total_usuarios}")
        print(f"   🆔 Con CI: {usuarios_con_ci}")
        print(f"   👤 Con sexo: {usuarios_con_sexo}")
        print(f"   📱 Con teléfono: {usuarios_con_telefono}")
        
        # Mostrar distribución por sexo
        for sexo_code, sexo_nombre in Usuario.Sexo.choices:
            count = Usuario.objects.filter(sexo=sexo_code).count()
            if count > 0:
                print(f"   {sexo_nombre}: {count}")
    
    print("\n🎉 ¡PRUEBAS COMPLETADAS EXITOSAMENTE!")


if __name__ == "__main__":
    probar_campos_usuario()