# chatbot/ia_service.py (con OpenAI)

import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Servicio de chatbot usando OpenAI GPT.
    """
    
    def __init__(self):
        self.api_key = settings.CHATBOT_CONFIG.get('OPENAI_API_KEY')
        self.model = settings.CHATBOT_CONFIG.get('MODEL', 'gpt-3.5-turbo')
        self.temperature = settings.CHATBOT_CONFIG.get('TEMPERATURE', 0.7)
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def generar_respuesta(self, mensaje_usuario, historial, usuario, contexto):
        """
        Genera una respuesta del chatbot usando OpenAI.
        
        Args:
            mensaje_usuario: Texto del mensaje del usuario
            historial: Lista de mensajes anteriores [{'role': 'user', 'content': '...'}]
            usuario: Objeto Usuario de Django
            contexto: Dict con información adicional
        
        Returns:
            Dict con 'mensaje' y 'metadata'
        """
        try:
            # Crear prompt del sistema con contexto
            system_prompt = self._crear_system_prompt(usuario, contexto)
            
            # Preparar mensajes para OpenAI
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            
            # Agregar historial (últimos 10 mensajes)
            messages.extend(historial[-10:])
            
            # Agregar mensaje actual
            messages.append({
                'role': 'user',
                'content': mensaje_usuario
            })
            
            # Llamar a OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            
            respuesta = response.choices[0].message.content
            
            # Metadata adicional
            metadata = {
                'model': self.model,
                'tokens_usados': response.usage.total_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
            
            logger.info(f"✅ Respuesta generada con OpenAI ({metadata['tokens_usados']} tokens)")
            
            return {
                'mensaje': respuesta,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"❌ Error con OpenAI: {str(e)}")
            
            # Fallback a respuesta predefinida
            return self._respuesta_fallback(mensaje_usuario)
    
    def _crear_system_prompt(self, usuario, contexto):
        """Crea el prompt del sistema con contexto del usuario."""
        
        prompt = f"""Eres un asistente virtual de una clínica dental. Tu nombre es DentalBot.

INFORMACIÓN DEL USUARIO:
- Nombre: {usuario.nombre} {usuario.apellido}
- Tipo: {usuario.tipo_usuario}
- Email: {usuario.email}

TUS RESPONSABILIDADES:
1. Responder preguntas sobre servicios dentales
2. Ayudar con agendamiento de citas
3. Proporcionar información sobre tratamientos
4. Recordar cuidados post-tratamiento
5. Responder preguntas frecuentes

REGLAS IMPORTANTES:
- Sé amable, profesional y empático
- Si no sabes algo, admítelo y ofrece contactar con personal
- No diagnostiques ni des consejos médicos específicos
- Mantén respuestas concisas (max 200 palabras)
- Usa emojis ocasionalmente para ser más amigable 😊
- Si el usuario necesita atención urgente, recomienda llamar o ir a la clínica

HORARIOS DE ATENCIÓN:
- Lunes a Viernes: 8:00 AM - 8:00 PM
- Sábados: 9:00 AM - 2:00 PM
- Domingos: Cerrado

SERVICIOS PRINCIPALES:
- Limpieza dental
- Ortodoncia
- Implantes
- Endodoncia
- Estética dental
- Cirugía oral

Responde siempre en español de manera clara y útil."""

        return prompt
    
    def _respuesta_fallback(self, mensaje_usuario):
        """Respuesta de respaldo cuando falla la IA."""
        
        # Buscar en intentos predefinidos
        from .models import IntentoChatbot
        
        mensaje_lower = mensaje_usuario.lower()
        
        # Palabras clave comunes
        if any(palabra in mensaje_lower for palabra in ['horario', 'hora', 'abierto', 'cerrado']):
            respuesta = """🕐 Nuestros horarios de atención son:

📅 Lunes a Viernes: 8:00 AM - 8:00 PM
📅 Sábados: 9:00 AM - 2:00 PM
📅 Domingos: Cerrado

¿Te gustaría agendar una cita?"""
        
        elif any(palabra in mensaje_lower for palabra in ['precio', 'costo', 'cuanto', 'valor']):
            respuesta = """💰 Los precios varían según el tratamiento. Algunos de nuestros servicios:

• Limpieza dental: $30-50
• Obturación simple: $40-80
• Extracción: $50-100
• Implante dental: $800-1500

¿Sobre qué tratamiento te gustaría más información?"""
        
        elif any(palabra in mensaje_lower for palabra in ['cita', 'agendar', 'reservar']):
            respuesta = """📅 ¡Perfecto! Para agendar tu cita puedes:

1. Llamar al: (123) 456-7890
2. Usar nuestra app en la sección "Agendar Cita"
3. Visitar nuestra clínica

¿Prefieres que te contactemos?"""
        
        elif any(palabra in mensaje_lower for palabra in ['hola', 'buenos', 'buenas']):
            respuesta = """¡Hola! 👋 Soy DentalBot, tu asistente virtual.

¿En qué puedo ayudarte hoy?

• Información sobre servicios
• Agendar una cita
• Preguntas sobre tratamientos
• Horarios y ubicación"""
        
        else:
            respuesta = """Lo siento, no tengo suficiente información para responder eso con precisión. 😔

¿Podrías reformular tu pregunta o elegir una de estas opciones?

• Horarios de atención
• Precios de servicios
• Agendar una cita
• Ubicación de la clínica

O puedes llamarnos al (123) 456-7890"""
        
        return {
            'mensaje': respuesta,
            'metadata': {'tipo': 'fallback', 'fuente': 'local'}
        }


# Ejemplo de uso en views.py:
"""
from .ia_service import ChatbotService

chatbot = ChatbotService()
respuesta = chatbot.generar_respuesta(
    mensaje_usuario="¿Cuáles son los horarios?",
    historial=[],
    usuario=request.user,
    contexto={}
)
"""
