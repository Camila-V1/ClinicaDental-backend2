#!/usr/bin/env python
"""
Script de diagnóstico para probar el login desde el backend.
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import authenticate
from django_tenants.utils import schema_context
from usuarios.models import Usuario
from rest_framework.test import APIRequestFactory
from usuarios.jwt_views import CustomTokenObtainPairSerializer

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_usuario_existe():
    print_section("1️⃣  VERIFICANDO SI EL USUARIO EXISTE")
    
    with schema_context('clinica_demo'):
        try:
            user = Usuario.objects.get(email='admin@clinicademo1.com')
            print(f"✅ Usuario encontrado: {user.email}")
            print(f"   - ID: {user.id}")
            print(f"   - Nombre completo: {user.full_name}")
            print(f"   - Tipo: {user.tipo_usuario}")
            print(f"   - is_active: {user.is_active}")
            print(f"   - is_staff: {user.is_staff}")
            print(f"   - Password hash (primeros 20 chars): {user.password[:20]}...")
            return user
        except Usuario.DoesNotExist:
            print("❌ Usuario NO encontrado")
            return None

def test_password_check(user):
    print_section("2️⃣  VERIFICANDO CONTRASEÑA CON check_password()")
    
    with schema_context('clinica_demo'):
        result = user.check_password('admin123')
        if result:
            print("✅ check_password('admin123') = True")
        else:
            print("❌ check_password('admin123') = False")
            print("   ⚠️  La contraseña NO coincide - Problema de hash!")
        return result

def test_authenticate():
    print_section("3️⃣  PROBANDO authenticate() DE DJANGO")
    
    with schema_context('clinica_demo'):
        user = authenticate(email='admin@clinicademo1.com', password='admin123')
        if user:
            print(f"✅ authenticate() exitoso: {user.email}")
        else:
            print("❌ authenticate() falló - retorna None")
        return user

def test_jwt_serializer():
    print_section("4️⃣  PROBANDO JWT SERIALIZER (API)")
    
    with schema_context('clinica_demo'):
        factory = APIRequestFactory()
        request = factory.post('/api/token/', {
            'email': 'admin@clinicademo1.com',
            'password': 'admin123'
        }, format='json')
        
        serializer = CustomTokenObtainPairSerializer(data={
            'email': 'admin@clinicademo1.com',
            'password': 'admin123'
        }, context={'request': request})
        
        try:
            if serializer.is_valid():
                validated_data = serializer.validated_data
                print("✅ Serializer válido - Login exitoso")
                print(f"   - Access token generado: {validated_data.get('access')[:50]}...")
                print(f"   - Refresh token generado: {validated_data.get('refresh')[:50]}...")
                return True
            else:
                print("❌ Serializer inválido")
                print(f"   Errores: {serializer.errors}")
                return False
        except Exception as e:
            print(f"❌ Excepción en serializer: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

def test_settings():
    print_section("5️⃣  VERIFICANDO SETTINGS DE AUTENTICACIÓN")
    
    from django.conf import settings
    
    print("AUTHENTICATION_BACKENDS:")
    for backend in settings.AUTHENTICATION_BACKENDS:
        print(f"   - {backend}")
    
    print(f"\nAUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    
    if hasattr(settings, 'SIMPLE_JWT'):
        print("\nSIMPLE_JWT configuración:")
        jwt_config = settings.SIMPLE_JWT
        print(f"   - USER_ID_FIELD: {jwt_config.get('USER_ID_FIELD', 'id')}")
        print(f"   - USER_ID_CLAIM: {jwt_config.get('USER_ID_CLAIM', 'user_id')}")

def main():
    print("\n" + "🔐"*35)
    print("  TEST DE LOGIN - DIAGNÓSTICO COMPLETO")
    print("🔐"*35)
    
    # Test 1: Usuario existe
    user = test_usuario_existe()
    if not user:
        print("\n❌ FALLO CRÍTICO: Usuario no existe. Ejecutar poblar_usuarios.py")
        return
    
    # Test 2: Password check
    password_ok = test_password_check(user)
    
    # Test 3: Django authenticate
    auth_ok = test_authenticate()
    
    # Test 4: JWT Serializer
    jwt_ok = test_jwt_serializer()
    
    # Test 5: Settings
    test_settings()
    
    # Resumen final
    print_section("📊 RESUMEN")
    print(f"1. Usuario existe: {'✅' if user else '❌'}")
    print(f"2. Password check: {'✅' if password_ok else '❌'}")
    print(f"3. Django authenticate: {'✅' if auth_ok else '❌'}")
    print(f"4. JWT Serializer: {'✅' if jwt_ok else '❌'}")
    
    if password_ok and auth_ok and jwt_ok:
        print("\n🎉 TODOS LOS TESTS PASARON - Login debería funcionar")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON - Revisar arriba")
        if not password_ok:
            print("   → Problema: Contraseña mal hasheada")
            print("   → Solución: Ejecutar 'python limpiar_tenant.py' y 'python scripts_poblacion/poblar_todo.py'")

if __name__ == '__main__':
    main()
