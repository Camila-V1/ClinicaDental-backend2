"""
Vista API para procesamiento de reportes por voz.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import datetime

from .nlp.voice_parser import parse_voice_command
from agenda.models import Cita
from facturacion.models import Factura, Pago
from tratamientos.models import PlanDeTratamiento
from usuarios.models import Usuario

import logging

logger = logging.getLogger(__name__)


class VoiceReportQueryView(APIView):
    """
    Endpoint para procesar comandos de voz y generar reportes.
    
    POST /api/reportes/voice-query/
    
    Body:
    {
        "texto": "dame las citas del 1 al 5 de septiembre"
    }
    
    Response:
    {
        "interpretacion": {
            "texto_original": "dame las citas del 1 al 5 de septiembre",
            "tipo_reporte": "citas",
            "fecha_inicio": "2025-09-01",
            "fecha_fin": "2025-09-05",
            "filtros": {},
            "interpretacion": "Reporte de citas desde el 01/09/2025 hasta el 05/09/2025"
        },
        "datos": [...],
        "resumen": {
            "total": 10,
            "periodo": "01/09/2025 - 05/09/2025"
        }
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        texto = request.data.get('texto', '').strip()
        
        if not texto:
            return Response(
                {'error': 'El campo "texto" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 1. Parsear el comando de voz
            interpretacion = parse_voice_command(texto)
            
            logger.info(f"👤 Usuario {request.user.email} solicitó: {texto}")
            logger.info(f"🧠 Interpretación: {interpretacion['interpretacion']}")
            
            # 2. Obtener datos según el tipo de reporte
            datos = self._obtener_datos(interpretacion, request.user)
            
            # 3. Generar resumen
            resumen = self._generar_resumen(interpretacion, datos)
            
            return Response({
                'interpretacion': interpretacion,
                'datos': datos,
                'resumen': resumen
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error procesando comando de voz: {str(e)}")
            return Response(
                {'error': f'Error al procesar el comando: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _obtener_datos(self, interpretacion, user):
        """Obtiene los datos según el tipo de reporte y filtros."""
        tipo_reporte = interpretacion['tipo_reporte']
        fecha_inicio = interpretacion['fecha_inicio']
        fecha_fin = interpretacion['fecha_fin']
        filtros = interpretacion['filtros']
        
        # Convertir strings de fecha a objetos datetime
        if fecha_inicio:
            fecha_inicio = datetime.fromisoformat(fecha_inicio).date()
        if fecha_fin:
            fecha_fin = datetime.fromisoformat(fecha_fin).date()
        
        if tipo_reporte == 'citas':
            return self._obtener_citas(fecha_inicio, fecha_fin, filtros)
        elif tipo_reporte == 'facturas':
            return self._obtener_facturas(fecha_inicio, fecha_fin, filtros)
        elif tipo_reporte == 'tratamientos':
            return self._obtener_tratamientos(fecha_inicio, fecha_fin, filtros)
        elif tipo_reporte == 'pacientes':
            return self._obtener_pacientes(fecha_inicio, fecha_fin, filtros)
        elif tipo_reporte == 'ingresos':
            return self._obtener_ingresos(fecha_inicio, fecha_fin, filtros)
        else:
            return []
    
    def _obtener_citas(self, fecha_inicio, fecha_fin, filtros):
        """Obtiene citas filtradas."""
        queryset = Cita.objects.all()
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            )
        
        if filtros.get('estado'):
            queryset = queryset.filter(estado=filtros['estado'])
        
        if filtros.get('paciente_nombre'):
            queryset = queryset.filter(
                paciente__nombre__icontains=filtros['paciente_nombre']
            )
        
        citas = queryset.select_related('paciente', 'odontologo').order_by('fecha', 'hora')
        
        return [{
            'id': cita.id,
            'fecha': cita.fecha.strftime('%d/%m/%Y'),
            'hora': cita.hora.strftime('%H:%M'),
            'paciente': cita.paciente.nombre_completo if cita.paciente else 'N/A',
            'odontologo': cita.odontologo.nombre_completo if cita.odontologo else 'N/A',
            'motivo': cita.motivo or 'N/A',
            'estado': cita.get_estado_display(),
            'tipo_cita': cita.get_tipo_cita_display()
        } for cita in citas[:100]]  # Limitar a 100 resultados
    
    def _obtener_facturas(self, fecha_inicio, fecha_fin, filtros):
        """Obtiene facturas filtradas."""
        queryset = Factura.objects.all()
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_emision__gte=fecha_inicio,
                fecha_emision__lte=fecha_fin
            )
        
        if filtros.get('estado'):
            queryset = queryset.filter(estado=filtros['estado'])
        
        if filtros.get('monto_minimo'):
            queryset = queryset.filter(monto_total__gte=filtros['monto_minimo'])
        
        if filtros.get('monto_maximo'):
            queryset = queryset.filter(monto_total__lte=filtros['monto_maximo'])
        
        facturas = queryset.select_related('paciente').order_by('-fecha_emision')
        
        return [{
            'id': factura.id,
            'numero': factura.numero_factura,
            'fecha': factura.fecha_emision.strftime('%d/%m/%Y'),
            'paciente': factura.paciente.nombre_completo if factura.paciente else 'N/A',
            'monto_total': float(factura.monto_total),
            'monto_pagado': float(factura.monto_pagado),
            'saldo': float(factura.saldo),
            'estado': factura.get_estado_display()
        } for factura in facturas[:100]]
    
    def _obtener_tratamientos(self, fecha_inicio, fecha_fin, filtros):
        """Obtiene planes de tratamiento filtrados."""
        queryset = PlanDeTratamiento.objects.all()
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_creacion__date__gte=fecha_inicio,
                fecha_creacion__date__lte=fecha_fin
            )
        
        if filtros.get('estado'):
            queryset = queryset.filter(estado=filtros['estado'])
        
        planes = queryset.select_related('paciente', 'odontologo').order_by('-fecha_creacion')
        
        return [{
            'id': plan.id,
            'fecha': plan.fecha_creacion.strftime('%d/%m/%Y'),
            'paciente': plan.paciente.nombre_completo if plan.paciente else 'N/A',
            'odontologo': plan.odontologo.nombre_completo if plan.odontologo else 'N/A',
            'titulo': plan.titulo,
            'estado': plan.get_estado_display(),
            'total': float(plan.total)
        } for plan in planes[:100]]
    
    def _obtener_pacientes(self, fecha_inicio, fecha_fin, filtros):
        """Obtiene pacientes registrados."""
        queryset = Usuario.objects.filter(rol='PACIENTE')
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                date_joined__date__gte=fecha_inicio,
                date_joined__date__lte=fecha_fin
            )
        
        pacientes = queryset.order_by('-date_joined')
        
        return [{
            'id': paciente.id,
            'nombre': paciente.nombre_completo,
            'email': paciente.email,
            'telefono': paciente.telefono or 'N/A',
            'fecha_registro': paciente.date_joined.strftime('%d/%m/%Y'),
            'activo': paciente.is_active
        } for paciente in pacientes[:100]]
    
    def _obtener_ingresos(self, fecha_inicio, fecha_fin, filtros):
        """Obtiene resumen de ingresos."""
        queryset = Pago.objects.filter(estado='completado')
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_pago__date__gte=fecha_inicio,
                fecha_pago__date__lte=fecha_fin
            )
        
        pagos = queryset.select_related('factura__paciente').order_by('-fecha_pago')
        
        return [{
            'id': pago.id,
            'fecha': pago.fecha_pago.strftime('%d/%m/%Y %H:%M'),
            'monto': float(pago.monto),
            'metodo_pago': pago.get_metodo_pago_display(),
            'factura': pago.factura.numero_factura if pago.factura else 'N/A',
            'paciente': pago.factura.paciente.nombre_completo if pago.factura and pago.factura.paciente else 'N/A'
        } for pago in pagos[:100]]
    
    def _generar_resumen(self, interpretacion, datos):
        """Genera un resumen del reporte."""
        tipo_reporte = interpretacion['tipo_reporte']
        fecha_inicio = interpretacion['fecha_inicio']
        fecha_fin = interpretacion['fecha_fin']
        
        resumen = {
            'total': len(datos),
            'tipo': tipo_reporte
        }
        
        if fecha_inicio and fecha_fin:
            fi = datetime.fromisoformat(fecha_inicio).strftime('%d/%m/%Y')
            ff = datetime.fromisoformat(fecha_fin).strftime('%d/%m/%Y')
            resumen['periodo'] = f"{fi} - {ff}"
        
        # Agregar estadísticas específicas por tipo
        if tipo_reporte == 'ingresos' and datos:
            total_ingresos = sum(d['monto'] for d in datos)
            resumen['total_ingresos'] = round(total_ingresos, 2)
            resumen['promedio'] = round(total_ingresos / len(datos), 2)
        
        if tipo_reporte == 'facturas' and datos:
            total_monto = sum(d['monto_total'] for d in datos)
            total_pagado = sum(d['monto_pagado'] for d in datos)
            resumen['total_facturado'] = round(total_monto, 2)
            resumen['total_cobrado'] = round(total_pagado, 2)
            resumen['saldo_pendiente'] = round(total_monto - total_pagado, 2)
        
        return resumen
