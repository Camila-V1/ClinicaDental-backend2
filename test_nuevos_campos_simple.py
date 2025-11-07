#!/usr/bin/env python
"""
Script simple para probar los nuevos campos CI, sexo y teléfono en usuarios existentes.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo
from tenants.models import Clinica
from django.db import IntegrityError


def test_nuevos_campos():
    """Prueba simple de los nuevos campos."""
    
    print("\n🧪 === PRUEBA RÁPIDA DE NUEVOS CAMPOS ===")
    
    with schema_context('clinica_demo'):
        
        # 1. MOSTRAR USUARIOS EXISTENTES
        print("\n📋 1. USUARIOS EXISTENTES EN LA BASE DE DATOS:")
        usuarios = Usuario.objects.all()[:5]  # Solo los primeros 5
        
        for usuario in usuarios:
            print(f"   👤 {usuario.full_name} ({usuario.email})")
            print(f"      🆔 CI: {usuario.ci or 'No especificado'}")
            print(f"      👥 Sexo: {usuario.get_sexo_display() if usuario.sexo else 'No especificado'}")
            print(f"      📱 Teléfono: {usuario.telefono or 'No especificado'}")
            print(f"      🏥 Tipo: {usuario.get_tipo_usuario_display()}")
            print()
        
        # 2. ACTUALIZAR UN USUARIO EXISTENTE
        print("\n✏️  2. ACTUALIZANDO USUARIO EXISTENTE CON NUEVOS CAMPOS...")
        
        # Tomar el primer usuario que no sea superuser
        usuario_test = Usuario.objects.filter(is_superuser=False).first()
        
        if usuario_test:
            # Guardar valores originales
            ci_original = usuario_test.ci
            sexo_original = usuario_test.sexo
            telefono_original = usuario_test.telefono
            
            # Actualizar con nuevos valores
            usuario_test.ci = '9876543210'
            usuario_test.sexo = 'M'
            usuario_test.telefono = '+591-99999999'
            
            try:
                usuario_test.save()
                print(f"✅ Usuario actualizado: {usuario_test.full_name}")
                print(f"   🆔 CI: {ci_original} → {usuario_test.ci}")
                print(f"   👥 Sexo: {sexo_original or 'No especificado'} → {usuario_test.get_sexo_display()}")
                print(f"   📱 Teléfono: {telefono_original or 'No especificado'} → {usuario_test.telefono}")
                
                # Restaurar valores originales
                usuario_test.ci = ci_original
                usuario_test.sexo = sexo_original
                usuario_test.telefono = telefono_original
                usuario_test.save()
                print("   ↩️  Valores restaurados")
                
            except IntegrityError as e:
                print(f"❌ Error de integridad: {e}")
        
        # 3. CREAR USUARIO SIMPLE CON NUEVOS CAMPOS
        print("\n➕ 3. CREANDO USUARIO SIMPLE CON NUEVOS CAMPOS...")
        
        import uuid
        email_unico = f"test_{uuid.uuid4().hex[:8]}@test.com"
        ci_unico = f"CI{uuid.uuid4().hex[:8]}"
        
        try:
            usuario_nuevo = Usuario.objects.create_user(
                email=email_unico,
                nombre='Test',
                apellido='Usuario',
                ci=ci_unico,
                sexo='F',
                telefono='+591-77777777',
                password='password123',
                tipo_usuario='PACIENTE'
            )
            
            print(f"✅ Usuario creado exitosamente: {usuario_nuevo.full_name}")
            print(f"   📧 Email: {usuario_nuevo.email}")
            print(f"   🆔 CI: {usuario_nuevo.ci}")
            print(f"   👥 Sexo: {usuario_nuevo.get_sexo_display()}")
            print(f"   📱 Teléfono: {usuario_nuevo.telefono}")
            
            # Eliminar el usuario de prueba
            usuario_nuevo.delete()
            print("   🗑️  Usuario de prueba eliminado")
            
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
        
        # 4. ESTADÍSTICAS DE NUEVOS CAMPOS
        print("\n📊 4. ESTADÍSTICAS DE NUEVOS CAMPOS:")
        
        total = Usuario.objects.count()
        con_ci = Usuario.objects.exclude(ci__isnull=True).exclude(ci='').count()
        con_sexo = Usuario.objects.exclude(sexo__isnull=True).count()
        con_telefono = Usuario.objects.exclude(telefono__isnull=True).exclude(telefono='').count()
        
        print(f"   👥 Total usuarios: {total}")
        print(f"   🆔 Con CI: {con_ci} ({con_ci/total*100:.1f}%)")
        print(f"   👤 Con sexo: {con_sexo} ({con_sexo/total*100:.1f}%)")
        print(f"   📱 Con teléfono: {con_telefono} ({con_telefono/total*100:.1f}%)")
        
        # 5. VERIFICAR OPCIONES DE SEXO
        print("\n🎭 5. OPCIONES DE SEXO DISPONIBLES:")
        for codigo, nombre in Usuario.Sexo.choices:
            count = Usuario.objects.filter(sexo=codigo).count()
            print(f"   {nombre} ({codigo}): {count} usuarios")
    
    print("\n🎉 ¡PRUEBAS DE NUEVOS CAMPOS COMPLETADAS!")


if __name__ == "__main__":
    test_nuevos_campos()