"""
Script para crear un usuario staff en el esquema público usando SQL directo.
Ya que no tenemos AUTH_USER_MODEL en public, creamos un registro básico en auth_user.
"""
import os
import django
import psycopg2

# Configuración de la base de datos
DB_CONFIG = {
    'dbname': 'db_clinica_multitenant',
    'user': 'postgres',
    'password': '12345678',
    'host': '127.0.0.1',
    'port': '5432'
}

print("=" * 60)
print("CREANDO USUARIO STAFF EN ESQUEMA PÚBLICO (SQL RAW)")
print("=" * 60)

try:
    # Conectar a PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Establecer el search_path al esquema público
    cur.execute("SET search_path TO public;")
    
    # Verificar si la tabla auth_user existe
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'auth_user'
        );
    """)
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        print("\n⚠️  La tabla auth_user NO existe en el esquema público")
        print("   Esto es esperado porque AUTH_USER_MODEL apunta a usuarios.Usuario")
        print("   El admin público NO REQUIERE autenticación de usuarios")
        print("\n💡 SOLUCIÓN:")
        print("   - El admin público mostrará solo Clinicas y Dominios")
        print("   - NO necesita login (o puedes implementar autenticación HTTP básica)")
        print("   - Los administradores de clínicas usarán el admin del tenant")
    else:
        print("\n✅ La tabla auth_user existe en public")
        
        # Crear usuario (simplificado)
        from django.contrib.auth.hashers import make_password
        
        email = 'superadmin@sistema.com'
        password_hash = make_password('superadmin123')
        
        # Verificar si ya existe
        cur.execute("SELECT id FROM auth_user WHERE username = %s;", (email,))
        existing = cur.fetchone()
        
        if existing:
            print(f"\n⚠️  El usuario '{email}' ya existe (ID: {existing[0]})")
        else:
            cur.execute("""
                INSERT INTO auth_user 
                (username, email, password, is_staff, is_superuser, is_active, date_joined)
                VALUES (%s, %s, %s, TRUE, TRUE, TRUE, NOW())
                RETURNING id;
            """, (email, email, password_hash))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            
            print(f"\n✅ Usuario staff creado exitosamente! (ID: {user_id})")
            print(f"\n📋 CREDENCIALES:")
            print(f"   Email: {email}")
            print(f"   Password: superadmin123")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Script completado")
