"""
Management command para reparar perfiles de usuarios
Ejecutar: python manage.py fix_perfiles
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_tenant_model
from django.contrib.auth import get_user_model
from usuarios.models import PerfilPaciente, PerfilOdontologo

User = get_user_model()
Tenant = get_tenant_model()


class Command(BaseCommand):
    help = 'Crea perfiles faltantes para usuarios odontólogos y pacientes'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🔧 REPARANDO PERFILES DE USUARIOS"))
        self.stdout.write("="*70)
        
        # Obtener tenant clinica-demo
        try:
            tenant = Tenant.objects.get(schema_name='clinica_demo')
            self.stdout.write(f"\n✅ Tenant: {tenant.nombre}")
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ ERROR: No existe el tenant 'clinica_demo'"))
            return
        
        with schema_context(tenant.schema_name):
            # Obtener usuarios
            odontologos = User.objects.filter(tipo_usuario='ODONTOLOGO', is_active=True)
            pacientes = User.objects.filter(tipo_usuario='PACIENTE', is_active=True)
            
            self.stdout.write(f"\n📊 Estadísticas:")
            self.stdout.write(f"   Odontólogos: {odontologos.count()}")
            self.stdout.write(f"   Pacientes: {pacientes.count()}")
            
            # Crear perfiles de odontólogos
            self.stdout.write("\n🦷 Creando perfiles de odontólogos...")
            odontologos_creados = 0
            for odontologo in odontologos:
                perfil, created = PerfilOdontologo.objects.get_or_create(
                    usuario=odontologo,
                    defaults={
                        'especialidad': 'Odontología General',
                        'numero_registro': f'REG-{odontologo.id:03d}'
                    }
                )
                if created:
                    self.stdout.write(f"   ✅ {odontologo.full_name}")
                    odontologos_creados += 1
            
            # Crear perfiles de pacientes
            self.stdout.write("\n🧑‍⚕️ Creando perfiles de pacientes...")
            pacientes_creados = 0
            for paciente in pacientes:
                perfil, created = PerfilPaciente.objects.get_or_create(
                    usuario=paciente,
                    defaults={
                        'fecha_nacimiento': '1990-01-01',
                        'telefono': '00000000',
                        'direccion': 'Sin dirección',
                        'grupo_sanguineo': 'O+'
                    }
                )
                if created:
                    self.stdout.write(f"   ✅ {paciente.full_name}")
                    pacientes_creados += 1
            
            # Resumen
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("📋 RESUMEN"))
            self.stdout.write("="*70)
            self.stdout.write(f"\n✅ Perfiles de odontólogos creados: {odontologos_creados}")
            self.stdout.write(f"✅ Perfiles de pacientes creados: {pacientes_creados}")
            
            total_perfiles_odontologo = PerfilOdontologo.objects.count()
            total_perfiles_paciente = PerfilPaciente.objects.count()
            
            self.stdout.write(f"\n📊 Total en sistema:")
            self.stdout.write(f"   PerfilOdontologo: {total_perfiles_odontologo}")
            self.stdout.write(f"   PerfilPaciente: {total_perfiles_paciente}")
            
            if odontologos_creados > 0 or pacientes_creados > 0:
                self.stdout.write(self.style.SUCCESS("\n🎉 ¡Perfiles reparados!"))
            else:
                self.stdout.write("\n✓ Todos los perfiles ya existían")
            
            self.stdout.write("\n" + "="*70 + "\n")
