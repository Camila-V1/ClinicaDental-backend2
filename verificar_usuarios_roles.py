#!/usr/bin/env python
"""
Script para verificar usuarios y sus roles en el sistema
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context, get_tenant_model
from django.contrib.auth import get_user_model

User = get_user_model()
Tenant = get_tenant_model()

def verificar_usuarios():
    """Verifica todos los usuarios en todos los tenants"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE USUARIOS Y ROLES")
    print("="*60)
    
    # Listar todos los tenants (excluyendo public)
    tenants = Tenant.objects.exclude(schema_name='public')
    print(f"\n📋 Tenants encontrados: {tenants.count()}")
    
    for tenant in tenants:
        print(f"\n{'='*60}")
        print(f"🏥 TENANT: {tenant.nombre}")
        print(f"   Dominio: {tenant.dominio}")
        print(f"   Schema: {tenant.schema_name}")
        print(f"{'='*60}")
        
        with schema_context(tenant.schema_name):
            usuarios = User.objects.all()
            
            if usuarios.exists():
                print(f"\n👥 Total usuarios: {usuarios.count()}\n")
                
                # Agrupar por tipo
                tipos = {}
                for usuario in usuarios:
                    tipo = usuario.get_tipo_usuario_display()
                    if tipo not in tipos:
                        tipos[tipo] = []
                    tipos[tipo].append(usuario)
                
                # Mostrar por tipo
                for tipo, users in sorted(tipos.items()):
                    print(f"\n📌 {tipo.upper()}")
                    print(f"   {'─'*56}")
                    for u in users:
                        estado = "✅ Activo" if u.is_active else "❌ Inactivo"
                        print(f"   • {u.email}")
                        nombre = u.full_name if hasattr(u, 'full_name') and u.full_name else (u.email.split('@')[0])
                        print(f"     Nombre: {nombre}")
                        print(f"     Estado: {estado}")
                        print(f"     Password válido: {'✅ Sí' if u.has_usable_password() else '❌ No'}")
                        print()
                
                # Credenciales de prueba
                print("\n" + "="*60)
                print("🔑 CREDENCIALES PARA PRUEBAS DE LOGIN")
                print("="*60)
                
                admin = usuarios.filter(tipo_usuario='administrador', is_active=True).first()
                if admin:
                    print(f"\n👨‍💼 ADMINISTRADOR:")
                    print(f"   Email: {admin.email}")
                    print(f"   Password: admin123")
                    print(f"   Endpoint: POST https://clinicademo1.dentaabcxy.store/api/token/")
                
                odontologo = usuarios.filter(tipo_usuario='odontologo', is_active=True).first()
                if odontologo:
                    print(f"\n🦷 ODONTÓLOGO:")
                    print(f"   Email: {odontologo.email}")
                    print(f"   Password: odontologo123")
                    print(f"   Endpoint: POST https://clinicademo1.dentaabcxy.store/api/token/")
                
                paciente = usuarios.filter(tipo_usuario='paciente', is_active=True).first()
                if paciente:
                    print(f"\n🧑‍⚕️ PACIENTE:")
                    print(f"   Email: {paciente.email}")
                    print(f"   Password: paciente123")
                    print(f"   Endpoint: POST https://clinicademo1.dentaabcxy.store/api/token/")
                
                print("\n" + "="*60)
                print("📝 EJEMPLO DE REQUEST (PowerShell)")
                print("="*60)
                print("""
$body = '{"email": "admin@clinica-demo.com", "password": "admin123"}'
$response = Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/token/" -Method POST -ContentType "application/json" -Body $body
$token = $response.access
Write-Host "Token: $token"

# Usar el token
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://clinica-demo.localhost:8000/api/usuarios/" -Headers $headers
                """)
                
            else:
                print("\n⚠️  No hay usuarios en este tenant")
    
    print("\n" + "="*60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*60 + "\n")

if __name__ == '__main__':
    verificar_usuarios()
