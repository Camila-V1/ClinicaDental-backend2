"""
Script simple para ver el error exacto del admin público
"""
import requests

print("Intentando acceder a http://localhost:8000/admin/...")

try:
    response = requests.get("http://localhost:8000/admin/", allow_redirects=True)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 500:
        print("\n❌ ERROR 500 - Contenido de la respuesta:")
        print("=" * 70)
        # Buscar el mensaje de error en el HTML
        content = response.text
        
        # Buscar la excepción
        if "ProgrammingError" in content:
            import re
            # Extraer el mensaje del error
            pattern = r'ProgrammingError.*?LINE \d+:.*?(?=</)'
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                for match in matches:
                    print("\n🔍 Error encontrado:")
                    # Limpiar HTML
                    clean_match = re.sub(r'<.*?>', '', match)
                    clean_match = clean_match.replace('&quot;', '"').replace('&#x27;', "'")
                    print(clean_match[:500])  # Primeros 500 caracteres
        
        # Buscar también en el traceback
        if "Traceback" in content:
            print("\n📍 Hay un traceback en la respuesta")
            # Intentar extraer la última línea del error
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'no existe la relación' in line or 'relation' in line and 'does not exist' in line:
                    print(f"Línea del error: {line[:200]}")
                    
    elif response.status_code == 200:
        print("\n✅ Admin público funciona correctamente!")
        print(f"Título encontrado: {'Administración del Sistema Multi-Tenant' in response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ No se puede conectar al servidor")
    print("Asegúrate de que el servidor esté corriendo: python manage.py runserver")
except Exception as e:
    print(f"\n❌ Error: {e}")
