"""
Módulo para poblar usuarios en el tenant

CREDENCIALES:
- Admin:         admin@clinicademo1.com / admin123
- Odontólogo:    odontologo@clinica-demo.com / odontologo123  
- Paciente 1:    paciente1@test.com / paciente123
- Paciente 2:    paciente2@test.com / paciente123
"""

from usuarios.models import Usuario, PerfilOdontologo, PerfilPaciente, Especialidad
from datetime import date


def poblar_usuarios():
    """
    Crea todos los usuarios necesarios para el tenant
    
    Returns:
        list: Lista de todos los usuarios creados
    """
    usuarios_creados = []
    
    print("\n  📋 Creando usuarios...")
    
    # =========================================================================
    # 1. CREAR ESPECIALIDADES PRIMERO
    # =========================================================================
    print("  → Especialidades odontológicas...")
    
    especialidad_general, _ = Especialidad.objects.get_or_create(
        nombre='Odontología General',
        defaults={
            'descripcion': 'Diagnóstico, prevención y tratamiento de enfermedades bucales',
            'activo': True
        }
    )
    
    especialidad_endodoncia, _ = Especialidad.objects.get_or_create(
        nombre='Endodoncia',
        defaults={
            'descripcion': 'Especialidad en tratamiento de conductos',
            'activo': True
        }
    )
    
    print("    ✓ Especialidades creadas")
    
    # =========================================================================
    # 2. USUARIO ADMINISTRADOR
    # =========================================================================
    print("  → Admin...")
    admin, created = Usuario.objects.get_or_create(
        email='admin@clinicademo1.com',
        defaults={
            'nombre': 'Admin',
            'apellido': 'Sistema',
            'ci': '12345678',
            'sexo': 'M',
            'telefono': '70000000',
            'tipo_usuario': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    admin.set_password('admin123')
    admin.save()
    
    usuarios_creados.append(admin)
    if created:
        print(f"    ✓ Admin creado: {admin.email} / admin123")
    else:
        print(f"    ✓ Admin actualizado: {admin.email} / admin123")
    
    # =========================================================================
    # 3. ODONTÓLOGO 1
    # =========================================================================
    print("  → Odontólogo 1...")
    odontologo, created = Usuario.objects.get_or_create(
        email='odontologo@clinica-demo.com',
        defaults={
            'nombre': 'Dr. Carlos',
            'apellido': 'Rodríguez',
            'ci': '87654321',
            'sexo': 'M',
            'telefono': '70111111',
            'tipo_usuario': 'ODONTOLOGO',
            'is_staff': True,
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    odontologo.set_password('odontologo123')
    odontologo.save()
    
    # Crear perfil si no existe
    if not hasattr(odontologo, 'perfil_odontologo'):
        PerfilOdontologo.objects.create(
            usuario=odontologo,
            especialidad=especialidad_general,
            cedulaProfesional='LIC-2024-001',
            experienciaProfesional='5 años de experiencia en odontología general y preventiva'
        )
    
    usuarios_creados.append(odontologo)
    print(f"    ✓ Odontólogo {'creado' if created else 'ya existe'}: {odontologo.email} / odontologo123")
    
    # =========================================================================
    # 4. ODONTÓLOGO 2
    # =========================================================================
    print("  → Odontólogo 2...")
    odontologo2, created = Usuario.objects.get_or_create(
        email='dra.lopez@clinica-demo.com',
        defaults={
            'nombre': 'Dra. María',
            'apellido': 'López',
            'ci': '77665544',
            'sexo': 'F',
            'telefono': '70444444',
            'tipo_usuario': 'ODONTOLOGO',
            'is_staff': True,
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    odontologo2.set_password('odontologo123')
    odontologo2.save()
    
    # Crear perfil si no existe
    if not hasattr(odontologo2, 'perfil_odontologo'):
        PerfilOdontologo.objects.create(
            usuario=odontologo2,
            especialidad=especialidad_endodoncia,
            cedulaProfesional='LIC-2024-002',
            experienciaProfesional='8 años de experiencia en endodoncia y cirugía oral'
        )
    
    usuarios_creados.append(odontologo2)
    print(f"    ✓ Odontólogo 2 {'creado' if created else 'ya existe'}: {odontologo2.email} / odontologo123")
    
    # =========================================================================
    # 5. PACIENTES
    # =========================================================================
    print("  → Pacientes...")
    
    # Paciente 1
    paciente1, created = Usuario.objects.get_or_create(
        email='paciente1@test.com',
        defaults={
            'nombre': 'María',
            'apellido': 'García',
            'ci': '55667788',
            'sexo': 'F',
            'telefono': '70333333',
            'tipo_usuario': 'PACIENTE',
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    paciente1.set_password('paciente123')
    paciente1.save()
    
    # Crear perfil si no existe
    if not hasattr(paciente1, 'perfil_paciente'):
        PerfilPaciente.objects.create(
            usuario=paciente1,
            fecha_de_nacimiento=date(1995, 3, 15),
            direccion='Zona Sur #321, La Paz'
        )
    
    usuarios_creados.append(paciente1)
    print(f"    ✓ Paciente 1 {'creado' if created else 'ya existe'}: {paciente1.email} / paciente123")
    
    # Paciente 2
    paciente2, created = Usuario.objects.get_or_create(
        email='paciente2@test.com',
        defaults={
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'ci': '99887766',
            'sexo': 'M',
            'telefono': '70555555',
            'tipo_usuario': 'PACIENTE',
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    paciente2.set_password('paciente123')
    paciente2.save()
    
    # Crear perfil si no existe
    if not hasattr(paciente2, 'perfil_paciente'):
        PerfilPaciente.objects.create(
            usuario=paciente2,
            fecha_de_nacimiento=date(1988, 7, 22),
            direccion='Zona Norte #654, La Paz'
        )
    
    usuarios_creados.append(paciente2)
    print(f"    ✓ Paciente 2 {'creado' if created else 'ya existe'}: {paciente2.email} / paciente123")
    
    # Paciente 3
    paciente3, created = Usuario.objects.get_or_create(
        email='paciente3@test.com',
        defaults={
            'nombre': 'Laura',
            'apellido': 'Sánchez',
            'ci': '44556677',
            'sexo': 'F',
            'telefono': '70666666',
            'tipo_usuario': 'PACIENTE',
            'is_active': True
        }
    )
    
    # SIEMPRE actualizar la contraseña (hashear correctamente)
    paciente3.set_password('paciente123')
    paciente3.save()
    
    # Crear perfil si no existe
    if not hasattr(paciente3, 'perfil_paciente'):
        PerfilPaciente.objects.create(
            usuario=paciente3,
            fecha_de_nacimiento=date(2000, 11, 10),
            direccion='Zona Centro #987, La Paz'
        )
    
    usuarios_creados.append(paciente3)
    print(f"    ✓ Paciente 3 {'creado' if created else 'ya existe'}: {paciente3.email} / paciente123")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print(f"\n  ✅ Total usuarios creados/verificados: {len(usuarios_creados)}")
    print(f"     - Admin: 1")
    print(f"     - Odontólogos: 2")
    print(f"     - Pacientes: 3")
    
    return usuarios_creados


# Funciones auxiliares para usar en otros módulos
def obtener_odontologos():
    """Obtiene todos los perfiles de odontólogos"""
    return PerfilOdontologo.objects.all()


def obtener_pacientes():
    """Obtiene todos los perfiles de pacientes"""
    return PerfilPaciente.objects.all()


def obtener_admin():
    """Obtiene el usuario administrador"""
    return Usuario.objects.filter(tipo_usuario='ADMIN').first()


# Información de credenciales para mostrar
CREDENCIALES_INFO = """
🔐 CREDENCIALES DE ACCESO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Admin:         admin@clinicademo1.com / admin123
Odontólogo 1:  odontologo@clinica-demo.com / odontologo123
Odontólogo 2:  dra.lopez@clinica-demo.com / odontologo123
Paciente 1:    paciente1@test.com / paciente123
Paciente 2:    paciente2@test.com / paciente123
Paciente 3:    paciente3@test.com / paciente123
"""
