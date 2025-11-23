#!/usr/bin/env python
"""
Script para crear usuarios de prueba con credenciales conocidas
y probar login local
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context, get_tenant_model
from django.contrib.auth import get_user_model
from usuarios.models import PerfilPaciente, PerfilOdontologo

User = get_user_model()
Tenant = get_tenant_model()

def crear_usuarios():
    """Crea usuarios de prueba en el tenant clinica-demo"""
    
    print("\n" + "="*60)
    print("👥 CREANDO USUARIOS DE PRUEBA")
    print("="*60)
    
    # Obtener tenant clinica-demo
    try:
        tenant = Tenant.objects.get(schema_name='clinica_demo')
    except Tenant.DoesNotExist:
        print("\n❌ ERROR: No existe el tenant 'clinica_demo'")
        return
    
    print(f"\n🏥 Tenant: {tenant.nombre}")
    print(f"   Dominio: {tenant.dominio}")
    print(f"   Schema: {tenant.schema_name}")
    
    with schema_context(tenant.schema_name):
        usuarios_creados = []
        
        # 1. ADMINISTRADOR
        print("\n" + "-"*60)
        print("👨‍💼 CREANDO ADMINISTRADOR")
        print("-"*60)
        
        admin_email = "admin@clinica-demo.com"
        admin_password = "admin123"
        
        # Verificar si ya existe
        if User.objects.filter(email=admin_email).exists():
            admin = User.objects.get(email=admin_email)
            admin.set_password(admin_password)
            admin.is_active = True
            admin.tipo_usuario = 'ADMIN'
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            print(f"✅ Administrador actualizado: {admin_email}")
        else:
            admin = User.objects.create_user(
                email=admin_email,
                password=admin_password,
                nombre="Administrador",
                apellido="Principal",
                tipo_usuario='ADMIN',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            print(f"✅ Administrador creado: {admin_email}")
        
        usuarios_creados.append({
            'tipo': 'ADMINISTRADOR',
            'email': admin_email,
            'password': admin_password,
            'nombre': admin.full_name
        })
        
        # 2. ODONTÓLOGO
        print("\n" + "-"*60)
        print("🦷 CREANDO ODONTÓLOGO")
        print("-"*60)
        
        odontologo_email = "odontologo@clinica-demo.com"
        odontologo_password = "odontologo123"
        
        # Verificar si ya existe
        odontologo = User.objects.filter(tipo_usuario='ODONTOLOGO', is_active=True).first()
        if odontologo:
            # Actualizar credenciales
            odontologo.email = odontologo_email
            odontologo.set_password(odontologo_password)
            odontologo.save()
            print(f"✅ Odontólogo actualizado: {odontologo.email}")
        else:
            odontologo = User.objects.create_user(
                email=odontologo_email,
                password=odontologo_password,
                nombre="Dr. Juan",
                apellido="Pérez",
                tipo_usuario='ODONTOLOGO',
                is_active=True
            )
            print(f"✅ Odontólogo creado: {odontologo_email}")
        
        # Crear perfil de odontólogo si no existe
        perfil_odontologo, created = PerfilOdontologo.objects.get_or_create(
            usuario=odontologo,
            defaults={
                'especialidad': 'Odontología General',
                'numero_registro': 'REG-001'
            }
        )
        if created:
            print(f"   ➕ Perfil de odontólogo creado")
        else:
            print(f"   ✓ Perfil de odontólogo ya existía")
        
        usuarios_creados.append({
            'tipo': 'ODONTÓLOGO',
            'email': odontologo.email,
            'password': odontologo_password,
            'nombre': odontologo.full_name
        })
        
        # 3. PACIENTE
        print("\n" + "-"*60)
        print("🧑‍⚕️ CREANDO PACIENTE")
        print("-"*60)
        
        paciente_email = "paciente@clinica-demo.com"
        paciente_password = "paciente123"
        
        # Verificar si ya existe
        paciente = User.objects.filter(tipo_usuario='PACIENTE', is_active=True).first()
        if paciente:
            # Actualizar credenciales
            paciente.email = paciente_email
            paciente.set_password(paciente_password)
            paciente.save()
            print(f"✅ Paciente actualizado: {paciente.email}")
        else:
            paciente = User.objects.create_user(
                email=paciente_email,
                password=paciente_password,
                nombre="María",
                apellido="García",
                tipo_usuario='PACIENTE',
                is_active=True
            )
            print(f"✅ Paciente creado: {paciente_email}")
        
        # Crear perfil de paciente si no existe
        perfil_paciente, created = PerfilPaciente.objects.get_or_create(
            usuario=paciente,
            defaults={
                'fecha_nacimiento': '1990-01-15',
                'telefono': '71234567',
                'direccion': 'Calle Principal #123',
                'grupo_sanguineo': 'O+'
            }
        )
        if created:
            print(f"   ➕ Perfil de paciente creado")
        else:
            print(f"   ✓ Perfil de paciente ya existía")
        
        usuarios_creados.append({
            'tipo': 'PACIENTE',
            'email': paciente.email,
            'password': paciente_password,
            'nombre': paciente.full_name
        })
        
        # 4. PACIENTE 1 - PARA FLUTTER
        print("\n" + "-"*60)
        print("📱 CREANDO PACIENTE 1 (FLUTTER)")
        print("-"*60)
        
        paciente1_email = "paciente1@test.com"
        paciente1_password = "password123"
        
        if User.objects.filter(email=paciente1_email).exists():
            paciente1 = User.objects.get(email=paciente1_email)
            paciente1.set_password(paciente1_password)
            paciente1.is_active = True
            paciente1.tipo_usuario = 'PACIENTE'
            paciente1.save()
            print(f"✅ Paciente 1 actualizado: {paciente1_email}")
        else:
            paciente1 = User.objects.create_user(
                email=paciente1_email,
                password=paciente1_password,
                nombre="Juan",
                apellido="Pérez",
                tipo_usuario='PACIENTE',
                is_active=True
            )
            print(f"✅ Paciente 1 creado: {paciente1_email}")
        
        # Crear perfil de paciente
        perfil_paciente1, created = PerfilPaciente.objects.get_or_create(
            usuario=paciente1,
            defaults={
                'fecha_nacimiento': '1992-05-20',
                'telefono': '79876543',
                'direccion': 'Av. Siempre Viva 456',
                'grupo_sanguineo': 'A+'
            }
        )
        if created:
            print(f"   ➕ Perfil creado")
        else:
            print(f"   ✓ Perfil ya existía")
        
        usuarios_creados.append({
            'tipo': 'PACIENTE',
            'email': paciente1_email,
            'password': paciente1_password,
            'nombre': paciente1.full_name
        })
        
        # 5. MARÍA GARCÍA - PARA FLUTTER
        print("\n" + "-"*60)
        print("📱 CREANDO MARÍA GARCÍA (FLUTTER)")
        print("-"*60)
        
        maria_email = "maria.garcia@email.com"
        maria_password = "password123"
        
        if User.objects.filter(email=maria_email).exists():
            maria = User.objects.get(email=maria_email)
            maria.set_password(maria_password)
            maria.is_active = True
            maria.tipo_usuario = 'PACIENTE'
            maria.save()
            print(f"✅ María García actualizada: {maria_email}")
        else:
            maria = User.objects.create_user(
                email=maria_email,
                password=maria_password,
                nombre="María",
                apellido="García López",
                tipo_usuario='PACIENTE',
                is_active=True
            )
            print(f"✅ María García creada: {maria_email}")
        
        # Crear perfil de paciente
        perfil_maria, created = PerfilPaciente.objects.get_or_create(
            usuario=maria,
            defaults={
                'fecha_nacimiento': '1988-03-10',
                'telefono': '72345678',
                'direccion': 'Zona Central, Calle Las Flores 789',
                'grupo_sanguineo': 'B+',
                'alergias': 'Penicilina',
                'enfermedades_cronicas': 'Hipertensión controlada'
            }
        )
        if created:
            print(f"   ➕ Perfil creado")
        else:
            print(f"   ✓ Perfil ya existía")
        
        usuarios_creados.append({
            'tipo': 'PACIENTE',
            'email': maria_email,
            'password': maria_password,
            'nombre': maria.full_name
        })
        
        # 6. DR. MARTÍNEZ - ODONTÓLOGO PARA FLUTTER
        print("\n" + "-"*60)
        print("📱 CREANDO DR. MARTÍNEZ (FLUTTER)")
        print("-"*60)
        
        martinez_email = "dr.martinez@clinica.com"
        martinez_password = "password123"
        
        if User.objects.filter(email=martinez_email).exists():
            martinez = User.objects.get(email=martinez_email)
            martinez.set_password(martinez_password)
            martinez.is_active = True
            martinez.tipo_usuario = 'ODONTOLOGO'
            martinez.save()
            print(f"✅ Dr. Martínez actualizado: {martinez_email}")
        else:
            martinez = User.objects.create_user(
                email=martinez_email,
                password=martinez_password,
                nombre="Carlos",
                apellido="Martínez",
                tipo_usuario='ODONTOLOGO',
                is_active=True
            )
            print(f"✅ Dr. Martínez creado: {martinez_email}")
        
        # Crear perfil de odontólogo
        perfil_martinez, created = PerfilOdontologo.objects.get_or_create(
            usuario=martinez,
            defaults={
                'especialidad': 'Endodoncia',
                'numero_registro': 'REG-002'
            }
        )
        if created:
            print(f"   ➕ Perfil creado")
        else:
            print(f"   ✓ Perfil ya existía")
        
        usuarios_creados.append({
            'tipo': 'ODONTÓLOGO',
            'email': martinez_email,
            'password': martinez_password,
            'nombre': martinez.full_name
        })
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("🔑 CREDENCIALES CREADAS - GUARDAR PARA PRUEBAS")
        print("="*60)
        
        for user in usuarios_creados:
            print(f"\n📌 {user['tipo']}")
            print(f"   Nombre: {user['nombre']}")
            print(f"   Email: {user['email']}")
            print(f"   Password: {user['password']}")
        
        print("\n" + "="*60)
        print("📝 COMANDOS PARA PROBAR LOGIN (PowerShell)")
        print("="*60)
        
        # Comandos locales
        print("\n🔹 PRUEBA LOCAL (http://clinica-demo.localhost:8000):")
        print("\n# Administrador:")
        print(f"""$body = '{{"email": "{admin_email}", "password": "{admin_password}"}}'
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
""")
        
        print("# Odontólogo:")
        print(f"""$body = '{{"email": "{odontologo.email}", "password": "{odontologo_password}"}}'
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
""")
        
        print("# Paciente:")
        print(f"""$body = '{{"email": "{paciente.email}", "password": "{paciente_password}"}}'
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
""")
        
        print("# Paciente 1 (Flutter):")
        print(f"""$body = '{{"email": "paciente1@test.com", "password": "password123"}}'
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
""")
        
        print("# María García (Flutter):")
        print(f"""$body = '{{"email": "maria.garcia@email.com", "password": "password123"}}'
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
""")
        
        # Comandos producción
        print("\n🔹 PRUEBA PRODUCCIÓN (https://clinicademo1.dentaabcxy.store):")
        print("""
⚠️  IMPORTANTE: Las credenciales solo funcionarán en producción si:
   1. El deployment en Render ha completado exitosamente
   2. Se ejecutó el script poblar_sistema_completo.py en producción
   3. El dominio clinicademo1.dentaabcxy.store está configurado
""")
        
        print("\n" + "="*60)
        print("✅ USUARIOS CREADOS EXITOSAMENTE")
        print("="*60 + "\n")

if __name__ == '__main__':
    crear_usuarios()
