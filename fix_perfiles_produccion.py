#!/usr/bin/env python
"""
Script de emergencia para crear perfiles de usuarios en producción
Ejecutar cuando los perfiles no se crearon durante el deployment
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

def fix_perfiles():
    """Crea perfiles faltantes para todos los usuarios existentes"""
    
    print("\n" + "="*70)
    print("🔧 REPARANDO PERFILES DE USUARIOS EN PRODUCCIÓN")
    print("="*70)
    
    # Obtener tenant clinica-demo
    try:
        tenant = Tenant.objects.get(schema_name='clinica_demo')
        print(f"\n✅ Tenant encontrado: {tenant.nombre}")
    except Tenant.DoesNotExist:
        print("\n❌ ERROR: No existe el tenant 'clinica_demo'")
        return
    
    with schema_context(tenant.schema_name):
        # Contar usuarios sin perfil
        odontologos = User.objects.filter(tipo_usuario='ODONTOLOGO', is_active=True)
        pacientes = User.objects.filter(tipo_usuario='PACIENTE', is_active=True)
        
        print(f"\n📊 Estadísticas:")
        print(f"   Odontólogos totales: {odontologos.count()}")
        print(f"   Pacientes totales: {pacientes.count()}")
        
        # Crear perfiles de odontólogos
        print("\n🦷 Creando perfiles de odontólogos...")
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
                print(f"   ✅ Perfil creado para: {odontologo.full_name}")
                odontologos_creados += 1
            else:
                print(f"   ✓ Perfil ya existía: {odontologo.full_name}")
        
        # Crear perfiles de pacientes
        print("\n🧑‍⚕️ Creando perfiles de pacientes...")
        pacientes_creados = 0
        for paciente in pacientes:
            perfil, created = PerfilPaciente.objects.get_or_create(
                usuario=paciente,
                defaults={
                    'fecha_nacimiento': '1990-01-01',
                    'telefono': '00000000',
                    'direccion': 'Sin dirección registrada',
                    'grupo_sanguineo': 'O+'
                }
            )
            if created:
                print(f"   ✅ Perfil creado para: {paciente.full_name}")
                pacientes_creados += 1
            else:
                print(f"   ✓ Perfil ya existía: {paciente.full_name}")
        
        # Resumen final
        print("\n" + "="*70)
        print("📋 RESUMEN DE LA REPARACIÓN")
        print("="*70)
        print(f"\n✅ Perfiles de odontólogos creados: {odontologos_creados}")
        print(f"✅ Perfiles de pacientes creados: {pacientes_creados}")
        
        # Verificar conteos finales
        total_perfiles_odontologo = PerfilOdontologo.objects.count()
        total_perfiles_paciente = PerfilPaciente.objects.count()
        
        print(f"\n📊 Total de perfiles en el sistema:")
        print(f"   PerfilOdontologo: {total_perfiles_odontologo}")
        print(f"   PerfilPaciente: {total_perfiles_paciente}")
        
        if odontologos_creados > 0 or pacientes_creados > 0:
            print("\n🎉 ¡Perfiles reparados exitosamente!")
            print("   Ahora el endpoint /api/reportes/reportes/dashboard-kpis/ debería funcionar")
        else:
            print("\n✓ Todos los perfiles ya existían, no se requirieron cambios")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    fix_perfiles()
