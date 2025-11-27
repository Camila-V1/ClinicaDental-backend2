"""
Procesador NLP para el chatbot asistente.
Interpreta comandos en texto o voz y los convierte en acciones.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ChatbotNLPProcessor:
    """
    Procesa comandos en lenguaje natural para el chatbot.
    Soporta español con detección de intenciones.
    """
    
    # Definición de intenciones y sus patrones
    INTENCIONES = {
        'ver_citas': {
            'patrones': [
                r'\b(ver|mostrar|dame|cuales son|lista)\b.*\b(mis citas|citas)\b',
                r'\b(mis citas|citas mias)\b',
                r'\b(citas programadas|citas agendadas)\b',
            ],
            'respuesta_type': 'lista_citas',
            'descripcion': 'Ver todas mis citas programadas'
        },
        'proxima_cita': {
            'patrones': [
                r'\b(proxima|siguiente|próxima|prox)\b.*\bcita\b',
                r'\b(mi proxima cita|cuando es mi cita|cual es mi cita)\b',
                r'\b(cita mas cercana|cita próxima)\b',
            ],
            'respuesta_type': 'proxima_cita',
            'descripcion': 'Ver mi próxima cita programada'
        },
        'tratamientos_activos': {
            'patrones': [
                r'\b(ver|mostrar|dame|cuales son)\b.*\b(mis tratamientos|tratamientos)\b',
                r'\b(tratamientos activos|tratamientos en curso)\b',
                r'\b(mis planes|planes de tratamiento)\b',
            ],
            'respuesta_type': 'tratamientos',
            'descripcion': 'Ver mis tratamientos activos'
        },
        'facturas_pendientes': {
            'patrones': [
                r'\b(ver|mostrar|cuanto debo|cuanto tengo que pagar)\b',
                r'\b(facturas pendientes|deudas|saldo pendiente)\b',
                r'\b(cuanto debo|que debo pagar|mis pagos)\b',
            ],
            'respuesta_type': 'facturas_pendientes',
            'descripcion': 'Ver mis facturas pendientes de pago'
        },
        'historial_pagos': {
            'patrones': [
                r'\b(ver|mostrar|historial de)\b.*\bpagos\b',
                r'\b(pagos realizados|mis pagos|pagos hechos)\b',
            ],
            'respuesta_type': 'historial_pagos',
            'descripcion': 'Ver mi historial de pagos'
        },
        'historial_clinico': {
            'patrones': [
                r'\b(ver|mostrar|mi)\b.*\b(historial|historia clinica|expediente)\b',
                r'\b(historial medico|historial dental|mis episodios)\b',
            ],
            'respuesta_type': 'historial_clinico',
            'descripcion': 'Ver mi historial clínico'
        },
        'cancelar_cita': {
            'patrones': [
                r'\b(cancelar|eliminar|borrar)\b.*\bcita\b',
                r'\b(no puedo asistir|no podre ir)\b',
            ],
            'respuesta_type': 'cancelar_cita',
            'descripcion': 'Cancelar una cita programada'
        },
        'agendar_cita': {
            'patrones': [
                r'\b(agendar|programar|reservar|pedir)\b.*\bcita\b',
                r'\b(nueva cita|quiero una cita)\b',
            ],
            'respuesta_type': 'agendar_cita',
            'descripcion': 'Agendar una nueva cita'
        },
        'ayuda': {
            'patrones': [
                r'\b(ayuda|help|que puedes hacer|que haces|opciones)\b',
                r'\b(como funciona|comandos|que comandos)\b',
                r'\b(ver opciones|mostrar opciones)\b',
            ],
            'respuesta_type': 'ayuda',
            'descripcion': 'Ver lista de comandos disponibles'
        },
        'saludo': {
            'patrones': [
                r'\b(hola|buenos dias|buenas tardes|buenas noches|hey|hi)\b',
            ],
            'respuesta_type': 'saludo',
            'descripcion': 'Saludar'
        }
    }
    
    def procesar_comando(self, texto: str, user) -> Dict[str, Any]:
        """
        Procesa un comando en texto y retorna la acción a ejecutar.
        
        Args:
            texto: Comando en lenguaje natural
            user: Usuario que ejecuta el comando
            
        Returns:
            Dict con la interpretación y acción a ejecutar
        """
        texto_lower = texto.lower().strip()
        
        # Detectar intención
        intencion = self._detectar_intencion(texto_lower)
        
        if not intencion:
            return {
                'intencion': 'desconocido',
                'texto_original': texto,
                'respuesta': 'No entendí tu solicitud. Escribe "ayuda" para ver los comandos disponibles.',
                'tipo_respuesta': 'error',
                'sugerencias': self._get_sugerencias_similares(texto_lower)
            }
        
        return {
            'intencion': intencion,
            'texto_original': texto,
            'tipo_respuesta': self.INTENCIONES[intencion]['respuesta_type'],
            'requiere_datos': intencion not in ['ayuda', 'saludo'],
            'mensaje': self._generar_mensaje_procesamiento(intencion)
        }
    
    def _detectar_intencion(self, texto: str) -> Optional[str]:
        """Detecta la intención del usuario basándose en patrones."""
        for intencion, config in self.INTENCIONES.items():
            for patron in config['patrones']:
                if re.search(patron, texto, re.IGNORECASE):
                    return intencion
        return None
    
    def _generar_mensaje_procesamiento(self, intencion: str) -> str:
        """Genera un mensaje de procesamiento según la intención."""
        mensajes = {
            'ver_citas': '🔍 Buscando tus citas programadas...',
            'proxima_cita': '📅 Buscando tu próxima cita...',
            'tratamientos_activos': '🦷 Consultando tus tratamientos activos...',
            'facturas_pendientes': '💰 Verificando tus facturas pendientes...',
            'historial_pagos': '📋 Obteniendo tu historial de pagos...',
            'historial_clinico': '📄 Consultando tu historial clínico...',
            'cancelar_cita': '❌ Preparando cancelación de cita...',
            'agendar_cita': '📅 Abriendo sistema de agendamiento...',
            'ayuda': '💡 Mostrando comandos disponibles...',
            'saludo': '👋 ¡Hola! ¿En qué puedo ayudarte?'
        }
        return mensajes.get(intencion, 'Procesando...')
    
    def _get_sugerencias_similares(self, texto: str) -> list:
        """Genera sugerencias basadas en el texto ingresado."""
        sugerencias = []
        
        palabras_clave = {
            'cita': ['ver mis citas', 'próxima cita', 'agendar cita'],
            'tratamiento': ['ver mis tratamientos', 'tratamientos activos'],
            'pago': ['facturas pendientes', 'historial de pagos'],
            'historial': ['ver mi historial clínico']
        }
        
        for palabra, comandos in palabras_clave.items():
            if palabra in texto:
                sugerencias.extend(comandos)
        
        if not sugerencias:
            sugerencias = ['ver mis citas', 'próxima cita', 'ver mis tratamientos', 'ayuda']
        
        return sugerencias[:3]
    
    def get_lista_comandos(self) -> list:
        """Retorna la lista completa de comandos disponibles."""
        comandos = []
        for intencion, config in self.INTENCIONES.items():
            if intencion not in ['saludo']:  # Excluir comandos internos
                comandos.append({
                    'comando': intencion,
                    'descripcion': config['descripcion'],
                    'ejemplo': self._get_ejemplo(intencion)
                })
        return comandos
    
    def _get_ejemplo(self, intencion: str) -> str:
        """Retorna un ejemplo de comando para cada intención."""
        ejemplos = {
            'ver_citas': '"ver mis citas" o "mostrar mis citas"',
            'proxima_cita': '"próxima cita" o "cuál es mi siguiente cita"',
            'tratamientos_activos': '"ver mis tratamientos" o "tratamientos activos"',
            'facturas_pendientes': '"cuánto debo" o "facturas pendientes"',
            'historial_pagos': '"ver mis pagos" o "historial de pagos"',
            'historial_clinico': '"ver mi historial" o "mi historia clínica"',
            'cancelar_cita': '"cancelar cita"',
            'agendar_cita': '"agendar cita" o "pedir cita"',
            'ayuda': '"ayuda" o "ver opciones"'
        }
        return ejemplos.get(intencion, '')


# Instancia global
chatbot_processor = ChatbotNLPProcessor()
