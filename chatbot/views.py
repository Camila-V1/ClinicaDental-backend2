"""
Vista API para el chatbot asistente.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta

from .nlp_processor import chatbot_processor
from agenda.models import Cita
from facturacion.models import Factura, Pago
from tratamientos.models import PlanDeTratamiento
from historial_clinico.models import EpisodioClinico
from usuarios.models import PerfilPaciente

import logging

logger = logging.getLogger(__name__)


class ChatbotQueryView(APIView):
    """
    Endpoint principal del chatbot.
    
    POST /api/chatbot/query/
    
    Body:
    {
        "texto": "ver mis citas",
        "es_voz": false  // opcional
    }
    
    Response:
    {
        "intencion": "ver_citas",
        "mensaje": "Encontré 3 citas programadas",
        "datos": [...],
        "tipo_respuesta": "lista_citas"
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        texto = request.data.get('texto', '').strip()
        es_voz = request.data.get('es_voz', False)
        
        if not texto:
            return Response(
                {'error': 'El campo "texto" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = request.user
            
            # 1. Procesar comando con NLP
            interpretacion = chatbot_processor.procesar_comando(texto, user)
            
            logger.info(f"👤 {user.email} | 🤖 Chatbot | Intención: {interpretacion.get('intencion')}")
            
            # 2. Si es comando desconocido, retornar error con sugerencias
            if interpretacion.get('tipo_respuesta') == 'error':
                return Response(interpretacion, status=status.HTTP_200_OK)
            
            # 3. Si es ayuda, retornar lista de comandos
            if interpretacion['intencion'] == 'ayuda':
                return self._handle_ayuda()
            
            # 4. Si es saludo, retornar saludo
            if interpretacion['intencion'] == 'saludo':
                return self._handle_saludo(user)
            
            # 5. Ejecutar acción según la intención
            resultado = self._ejecutar_accion(interpretacion, user)
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error en chatbot: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Error al procesar tu solicitud',
                    'mensaje': 'Lo siento, ocurrió un error. Por favor intenta de nuevo.',
                    'tipo_respuesta': 'error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _ejecutar_accion(self, interpretacion, user):
        """Ejecuta la acción correspondiente según la intención."""
        intencion = interpretacion['intencion']
        
        # Verificar que el usuario sea paciente
        if not hasattr(user, 'perfil_paciente'):
            return {
                'intencion': intencion,
                'mensaje': 'Esta función es solo para pacientes.',
                'tipo_respuesta': 'error',
                'datos': None
            }
        
        paciente = user.perfil_paciente
        
        acciones = {
            'ver_citas': self._get_citas,
            'proxima_cita': self._get_proxima_cita,
            'tratamientos_activos': self._get_tratamientos,
            'facturas_pendientes': self._get_facturas_pendientes,
            'historial_pagos': self._get_historial_pagos,
            'historial_clinico': self._get_historial_clinico,
            'cancelar_cita': self._iniciar_cancelar_cita,
            'agendar_cita': self._iniciar_agendar_cita,
        }
        
        accion = acciones.get(intencion)
        if accion:
            return accion(paciente, interpretacion)
        
        return {
            'intencion': intencion,
            'mensaje': 'Función no implementada aún.',
            'tipo_respuesta': 'error',
            'datos': None
        }
    
    # ==================== ACCIONES ====================
    
    def _get_citas(self, paciente, interpretacion):
        """Obtiene todas las citas del paciente."""
        ahora = timezone.now()
        
        citas = Cita.objects.filter(
            paciente=paciente,
            fecha_hora__gte=ahora
        ).select_related('odontologo__usuario').order_by('fecha_hora')[:10]
        
        if not citas.exists():
            return {
                'intencion': 'ver_citas',
                'mensaje': 'No tienes citas programadas actualmente.',
                'datos': [],
                'tipo_respuesta': 'lista_citas',
                'sugerencias': ['agendar cita', 'ver mis tratamientos']
            }
        
        datos = [{
            'id': cita.id,
            'fecha': cita.fecha_hora.strftime('%d/%m/%Y'),
            'hora': cita.fecha_hora.strftime('%H:%M'),
            'odontologo': cita.odontologo.usuario.full_name if cita.odontologo else 'No asignado',
            'motivo_tipo': cita.get_motivo_tipo_display(),
            'motivo': cita.motivo or '',
            'estado': cita.get_estado_display(),
            'puede_cancelar': cita.estado == 'CONFIRMADA'
        } for cita in citas]
        
        mensaje = f"📅 Tienes {len(datos)} cita{'s' if len(datos) > 1 else ''} programada{'s' if len(datos) > 1 else ''}."
        
        return {
            'intencion': 'ver_citas',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'lista_citas',
            'total': len(datos)
        }
    
    def _get_proxima_cita(self, paciente, interpretacion):
        """Obtiene la próxima cita del paciente."""
        ahora = timezone.now()
        
        cita = Cita.objects.filter(
            paciente=paciente,
            fecha_hora__gte=ahora,
            estado='CONFIRMADA'
        ).select_related('odontologo__usuario').order_by('fecha_hora').first()
        
        if not cita:
            return {
                'intencion': 'proxima_cita',
                'mensaje': 'No tienes citas confirmadas próximamente.',
                'datos': None,
                'tipo_respuesta': 'proxima_cita',
                'sugerencias': ['agendar cita', 'ver mis citas']
            }
        
        # Calcular tiempo restante
        tiempo_restante = cita.fecha_hora - ahora
        dias = tiempo_restante.days
        horas = tiempo_restante.seconds // 3600
        
        if dias == 0:
            if horas < 1:
                tiempo_texto = "en menos de 1 hora"
            elif horas == 1:
                tiempo_texto = "en 1 hora"
            else:
                tiempo_texto = f"en {horas} horas"
        elif dias == 1:
            tiempo_texto = "mañana"
        else:
            tiempo_texto = f"en {dias} días"
        
        datos = {
            'id': cita.id,
            'fecha': cita.fecha_hora.strftime('%d/%m/%Y'),
            'hora': cita.fecha_hora.strftime('%H:%M'),
            'odontologo': cita.odontologo.usuario.full_name if cita.odontologo else 'No asignado',
            'motivo_tipo': cita.get_motivo_tipo_display(),
            'motivo': cita.motivo or '',
            'estado': cita.get_estado_display(),
            'tiempo_restante': tiempo_texto,
            'puede_cancelar': True
        }
        
        mensaje = f"📅 Tu próxima cita es {tiempo_texto} ({datos['fecha']} a las {datos['hora']}) con {datos['odontologo']}."
        
        return {
            'intencion': 'proxima_cita',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'proxima_cita'
        }
    
    def _get_tratamientos(self, paciente, interpretacion):
        """Obtiene los tratamientos activos del paciente."""
        planes = PlanDeTratamiento.objects.filter(
            paciente=paciente,
            estado__in=['EN_PROGRESO', 'ACEPTADO', 'APROBADO']
        ).select_related('odontologo__usuario').order_by('-fecha_creacion')[:5]
        
        if not planes.exists():
            return {
                'intencion': 'tratamientos_activos',
                'mensaje': 'No tienes tratamientos activos actualmente.',
                'datos': [],
                'tipo_respuesta': 'tratamientos',
                'sugerencias': ['ver mis citas', 'historial clínico']
            }
        
        datos = [{
            'id': plan.id,
            'titulo': plan.titulo,
            'odontologo': plan.odontologo.usuario.full_name if plan.odontologo else 'No asignado',
            'estado': plan.get_estado_display(),
            'fecha_creacion': plan.fecha_creacion.strftime('%d/%m/%Y'),
            'total': float(plan.precio_total_plan),
            'porcentaje_completado': plan.porcentaje_completado,
            'cantidad_items': plan.cantidad_items
        } for plan in planes]
        
        mensaje = f"🦷 Tienes {len(datos)} tratamiento{'s' if len(datos) > 1 else ''} activo{'s' if len(datos) > 1 else ''}."
        
        return {
            'intencion': 'tratamientos_activos',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'tratamientos',
            'total': len(datos)
        }
    
    def _get_facturas_pendientes(self, paciente, interpretacion):
        """Obtiene las facturas pendientes del paciente."""
        facturas = Factura.objects.filter(
            paciente=paciente,
            estado='PENDIENTE'
        ).order_by('fecha_emision')[:10]
        
        if not facturas.exists():
            return {
                'intencion': 'facturas_pendientes',
                'mensaje': '✅ No tienes facturas pendientes. ¡Estás al día!',
                'datos': [],
                'tipo_respuesta': 'facturas_pendientes',
                'total_deuda': 0,
                'sugerencias': ['ver mis pagos', 'historial de pagos']
            }
        
        datos = [{
            'id': factura.id,
            'numero': f"FAC-{factura.id:06d}",
            'fecha': factura.fecha_emision.strftime('%d/%m/%Y'),
            'monto_total': float(factura.monto_total),
            'monto_pagado': float(factura.monto_pagado),
            'saldo': float(factura.saldo_pendiente),
            'estado': factura.get_estado_display()
        } for factura in facturas]
        
        total_deuda = sum(f['saldo'] for f in datos)
        
        mensaje = f"💰 Tienes {len(datos)} factura{'s' if len(datos) > 1 else ''} pendiente{'s' if len(datos) > 1 else ''} por un total de Bs. {total_deuda:.2f}"
        
        return {
            'intencion': 'facturas_pendientes',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'facturas_pendientes',
            'total_deuda': total_deuda,
            'total': len(datos)
        }
    
    def _get_historial_pagos(self, paciente, interpretacion):
        """Obtiene el historial de pagos del paciente."""
        pagos = Pago.objects.filter(
            paciente=paciente,
            estado_pago='COMPLETADO'
        ).select_related('factura').order_by('-fecha_pago')[:10]
        
        if not pagos.exists():
            return {
                'intencion': 'historial_pagos',
                'mensaje': 'No tienes pagos registrados aún.',
                'datos': [],
                'tipo_respuesta': 'historial_pagos'
            }
        
        datos = [{
            'id': pago.id,
            'fecha': pago.fecha_pago.strftime('%d/%m/%Y %H:%M'),
            'monto': float(pago.monto_pagado),
            'metodo': pago.get_metodo_pago_display(),
            'factura': f"FAC-{pago.factura.id:06d}" if pago.factura else 'N/A',
            'estado': pago.get_estado_pago_display()
        } for pago in pagos]
        
        total_pagado = sum(p['monto'] for p in datos)
        
        mensaje = f"📋 Tienes {len(datos)} pago{'s' if len(datos) > 1 else ''} registrado{'s' if len(datos) > 1 else ''} (últimos 10)."
        
        return {
            'intencion': 'historial_pagos',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'historial_pagos',
            'total_pagado': total_pagado,
            'total': len(datos)
        }
    
    def _get_historial_clinico(self, paciente, interpretacion):
        """Obtiene el historial clínico del paciente."""
        episodios = EpisodioClinico.objects.filter(
            paciente=paciente
        ).select_related('odontologo__usuario').order_by('-fecha')[:10]
        
        if not episodios.exists():
            return {
                'intencion': 'historial_clinico',
                'mensaje': 'No tienes episodios clínicos registrados aún.',
                'datos': [],
                'tipo_respuesta': 'historial_clinico'
            }
        
        datos = [{
            'id': episodio.id,
            'fecha': episodio.fecha.strftime('%d/%m/%Y'),
            'tipo': episodio.get_tipo_display(),
            'diagnostico': episodio.diagnostico[:100] + '...' if len(episodio.diagnostico) > 100 else episodio.diagnostico,
            'odontologo': episodio.odontologo.usuario.full_name if episodio.odontologo else 'No asignado',
            'tratamiento_aplicado': episodio.tratamiento_aplicado[:100] + '...' if episodio.tratamiento_aplicado and len(episodio.tratamiento_aplicado) > 100 else episodio.tratamiento_aplicado or ''
        } for episodio in episodios]
        
        mensaje = f"📄 Tienes {len(datos)} episodio{'s' if len(datos) > 1 else ''} clínico{'s' if len(datos) > 1 else ''} registrado{'s' if len(datos) > 1 else ''} (últimos 10)."
        
        return {
            'intencion': 'historial_clinico',
            'mensaje': mensaje,
            'datos': datos,
            'tipo_respuesta': 'historial_clinico',
            'total': len(datos)
        }
    
    def _iniciar_cancelar_cita(self, paciente, interpretacion):
        """Inicia el flujo para cancelar una cita."""
        # Obtener citas cancelables
        ahora = timezone.now()
        citas = Cita.objects.filter(
            paciente=paciente,
            fecha_hora__gte=ahora,
            estado='CONFIRMADA'
        ).select_related('odontologo__usuario').order_by('fecha_hora')[:5]
        
        if not citas.exists():
            return {
                'intencion': 'cancelar_cita',
                'mensaje': 'No tienes citas confirmadas para cancelar.',
                'datos': [],
                'tipo_respuesta': 'cancelar_cita',
                'sugerencias': ['ver mis citas', 'agendar cita']
            }
        
        datos = [{
            'id': cita.id,
            'fecha': cita.fecha_hora.strftime('%d/%m/%Y'),
            'hora': cita.fecha_hora.strftime('%H:%M'),
            'odontologo': cita.odontologo.usuario.full_name if cita.odontologo else 'No asignado',
            'motivo_tipo': cita.get_motivo_tipo_display(),
        } for cita in citas]
        
        return {
            'intencion': 'cancelar_cita',
            'mensaje': '❌ Selecciona la cita que deseas cancelar:',
            'datos': datos,
            'tipo_respuesta': 'cancelar_cita',
            'requiere_seleccion': True
        }
    
    def _iniciar_agendar_cita(self, paciente, interpretacion):
        """Inicia el flujo para agendar una cita."""
        return {
            'intencion': 'agendar_cita',
            'mensaje': '📅 Redirigiendo al sistema de agendamiento...',
            'datos': None,
            'tipo_respuesta': 'agendar_cita',
            'accion': 'redirect',
            'redirect_url': '/agenda'  # URL del frontend
        }
    
    def _handle_ayuda(self):
        """Maneja el comando de ayuda."""
        comandos = chatbot_processor.get_lista_comandos()
        
        return Response({
            'intencion': 'ayuda',
            'mensaje': '💡 Estos son los comandos que puedo entender:',
            'datos': comandos,
            'tipo_respuesta': 'ayuda',
            'total': len(comandos)
        })
    
    def _handle_saludo(self, user):
        """Maneja el saludo."""
        nombre = user.nombre if hasattr(user, 'nombre') else 'Usuario'
        
        return Response({
            'intencion': 'saludo',
            'mensaje': f'👋 ¡Hola {nombre}! Soy tu asistente virtual. Puedo ayudarte con tus citas, tratamientos, facturas y más. Escribe "ayuda" para ver todas las opciones.',
            'datos': None,
            'tipo_respuesta': 'saludo',
            'sugerencias': ['ver mis citas', 'próxima cita', 'ayuda']
        })
