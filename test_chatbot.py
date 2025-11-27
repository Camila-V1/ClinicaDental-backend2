"""
Script de prueba para el chatbot NLP.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chatbot.nlp_processor import chatbot_processor


def probar_comando(texto):
    """Prueba un comando y muestra el resultado."""
    print("─" * 80)
    print(f"🎤 Comando: \"{texto}\"")
    print("─" * 80)
    
    # Procesar (sin usuario real, solo NLP)
    class MockUser:
        email = "test@test.com"
    
    resultado = chatbot_processor.procesar_comando(texto, MockUser())
    
    print(f"✅ Intención:    {resultado.get('intencion', 'N/A')}")
    print(f"📊 Tipo:         {resultado.get('tipo_respuesta', 'N/A')}")
    print(f"💬 Mensaje:      {resultado.get('mensaje', 'N/A')}")
    
    if resultado.get('sugerencias'):
        print(f"💡 Sugerencias:  {', '.join(resultado['sugerencias'])}")
    
    print()


def main():
    print("=" * 80)
    print("🤖 TEST DEL CHATBOT NLP")
    print("=" * 80)
    print()
    
    # Lista de comandos a probar
    comandos = [
        # Citas
        "ver mis citas",
        "cuál es mi próxima cita",
        "cuando es mi siguiente cita",
        
        # Tratamientos
        "mostrar mis tratamientos",
        "tratamientos activos",
        
        # Facturas
        "cuánto debo",
        "facturas pendientes",
        "ver mis pagos",
        
        # Historial
        "ver mi historial clínico",
        "mi historia clínica",
        
        # Acciones
        "agendar una cita",
        "cancelar cita",
        
        # Ayuda
        "ayuda",
        "qué puedes hacer",
        
        # Saludos
        "hola",
        "buenos días",
        
        # Comandos desconocidos
        "dame información",
        "xyz123",
    ]
    
    for comando in comandos:
        probar_comando(comando)
    
    print("=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    print()
    print("📋 LISTA DE COMANDOS DISPONIBLES:")
    print()
    
    comandos_disponibles = chatbot_processor.get_lista_comandos()
    for i, cmd in enumerate(comandos_disponibles, 1):
        print(f"{i}. {cmd['descripcion']}")
        print(f"   Ejemplo: {cmd['ejemplo']}")
        print()


if __name__ == '__main__':
    main()
