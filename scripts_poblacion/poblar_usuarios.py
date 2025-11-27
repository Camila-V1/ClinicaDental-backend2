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
    if not Usuario.objects.filter(email='admin@clinicademo1.com').exists():
        admin = Usuario.objects.create_user(
            email='admin@clinicademo1.com',
            password='admin123',
            nombre='Admin',
            apellido='Sistema',
            ci='12345678',
            sexo='M',
            telefono='70000000',
            tipo_usuario='ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        usuarios_creados.append(admin)
        print(f"    ✓ Admin creado: {admin.email} / admin123")
    else:
        admin = Usuario.objects.get(email='admin@clinicademo1.com')
        usuarios_creados.append(admin)
        print(f"    ✓ Admin ya existe: {admin.email}")
    
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
    
    if created:
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
    if not Usuario.objects.filter(email='dra.lopez@clinica-demo.com').exists():
        odontologo2 = Usuario.objects.create_user(
            email='dra.lopez@clinica-demo.com',
            password='odontologo123',
            nombre='Dra. María',
            apellido='López',
            ci='77665544',
            sexo='F',
            telefono='70444444',
            tipo_usuario='ODONTOLOGO',
            is_staff=True,
            is_active=True
        )
        
        # Crear perfil de odontólogo
        PerfilOdontologo.objects.create(
            usuario=odontologo2,
            especialidad=especialidad_endodoncia,
            cedulaProfesional='LIC-2024-002',
            experienciaProfesional='8 años de experiencia en endodoncia y cirugía oral'
        )
        
        usuarios_creados.append(odontologo2)
        print(f"    ✓ Odontólogo 2 creado: {odontologo2.email} / odontologo123")
    else:
        odontologo2 = Usuario.objects.get(email='dra.lopez@clinica-demo.com')
        usuarios_creados.append(odontologo2)
        print(f"    ✓ Odontólogo 2 ya existe: {odontologo2.email}")
    
    # =========================================================================
    # 5. PACIENTES
    # =========================================================================
    print("  → Pacientes...")
    
    # Paciente 1
    if not Usuario.objects.filter(email='paciente1@test.com').exists():
        paciente1 = Usuario.objects.create_user(
            email='paciente1@test.com',
            password='paciente123',
            nombre='María',
            apellido='García',
            ci='55667788',
            sexo='F',
            telefono='70333333',
            tipo_usuario='PACIENTE',
            is_active=True
        )
        
        # Crear perfil de paciente
        PerfilPaciente.objects.create(
            usuario=paciente1,
            fecha_de_nacimiento=date(1995, 3, 15),
            direccion='Zona Sur #321, La Paz'
        )
        
        usuarios_creados.append(paciente1)
        print(f"    ✓ Paciente 1 creado: {paciente1.email} / paciente123")
    else:
        paciente1 = Usuario.objects.get(email='paciente1@test.com')
        usuarios_creados.append(paciente1)
        print(f"    ✓ Paciente 1 ya existe: {paciente1.email}")
    
    # Paciente 2
    if not Usuario.objects.filter(email='paciente2@test.com').exists():
        paciente2 = Usuario.objects.create_user(
            email='paciente2@test.com',
            password='paciente123',
            nombre='Juan',
            apellido='Pérez',
            ci='99887766',
            sexo='M',
            telefono='70555555',
            tipo_usuario='PACIENTE',
            is_active=True
        )
        
        # Crear perfil de paciente
        PerfilPaciente.objects.create(
            usuario=paciente2,
            fecha_de_nacimiento=date(1988, 7, 22),
            direccion='Zona Norte #654, La Paz'
        )
        
        usuarios_creados.append(paciente2)
        print(f"    ✓ Paciente 2 creado: {paciente2.email} / paciente123")
    else:
        paciente2 = Usuario.objects.get(email='paciente2@test.com')
        usuarios_creados.append(paciente2)
        print(f"    ✓ Paciente 2 ya existe: {paciente2.email}")
    
    # Paciente 3
    if not Usuario.objects.filter(email='paciente3@test.com').exists():
        paciente3 = Usuario.objects.create_user(
            email='paciente3@test.com',
            password='paciente123',
            nombre='Laura',
            apellido='Sánchez',
            ci='44556677',
            sexo='F',
            telefono='70666666',
            tipo_usuario='PACIENTE',
            is_active=True
        )
        
        # Crear perfil de paciente
        PerfilPaciente.objects.create(
            usuario=paciente3,
            fecha_de_nacimiento=date(2000, 11, 10),
            direccion='Zona Centro #987, La Paz'
        )
        
        usuarios_creados.append(paciente3)
        print(f"    ✓ Paciente 3 creado: {paciente3.email} / paciente123")
    else:
        paciente3 = Usuario.objects.get(email='paciente3@test.com')
        usuarios_creados.append(paciente3)
        print(f"    ✓ Paciente 3 ya existe: {paciente3.email}")
    
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
