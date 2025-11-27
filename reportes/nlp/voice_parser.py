"""
Procesador de Lenguaje Natural para Reportes por Voz.

Este módulo interpreta comandos en lenguaje natural español para generar reportes.
Ejemplos:
- "dame las citas del 1 al 5 de septiembre"
- "mostrar facturas de la semana pasada"
- "reportes de tratamientos del mes actual"
"""

import re
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
import calendar
import logging

logger = logging.getLogger(__name__)


class VoiceReportParser:
    """Parser de comandos de voz para reportes."""
    
    # Meses en español
    MESES = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    # Tipos de reportes reconocidos
    TIPOS_REPORTE = {
        'citas': ['cita', 'citas', 'agenda', 'agendas', 'consulta', 'consultas'],
        'facturas': ['factura', 'facturas', 'pago', 'pagos', 'cobro', 'cobros'],
        'tratamientos': ['tratamiento', 'tratamientos', 'plan', 'planes', 'servicio', 'servicios'],
        'pacientes': ['paciente', 'pacientes', 'cliente', 'clientes'],
        'ingresos': ['ingreso', 'ingresos', 'ganancia', 'ganancias', 'venta', 'ventas'],
        'inventario': ['inventario', 'stock', 'insumo', 'insumos', 'material', 'materiales']
    }
    
    def __init__(self):
        self.texto_original = ""
        self.tipo_reporte = None
        self.fecha_inicio = None
        self.fecha_fin = None
        self.filtros_adicionales = {}
    
    def parse(self, texto):
        """
        Procesa el texto de entrada y extrae información del reporte.
        
        Args:
            texto (str): Comando de voz transcrito
            
        Returns:
            dict: Información parseada del reporte
        """
        self.texto_original = texto.lower().strip()
        
        logger.info(f"🎤 Procesando comando: '{texto}'")
        
        # 1. Detectar tipo de reporte
        self.tipo_reporte = self._detectar_tipo_reporte()
        
        # 2. Extraer fechas
        self._extraer_fechas()
        
        # 3. Extraer filtros adicionales
        self._extraer_filtros()
        
        resultado = {
            'texto_original': texto,
            'tipo_reporte': self.tipo_reporte,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'filtros': self.filtros_adicionales,
            'interpretacion': self._generar_interpretacion()
        }
        
        logger.info(f"✅ Resultado: {resultado}")
        
        return resultado
    
    def _detectar_tipo_reporte(self):
        """Detecta qué tipo de reporte se está solicitando."""
        for tipo, palabras_clave in self.TIPOS_REPORTE.items():
            for palabra in palabras_clave:
                if palabra in self.texto_original:
                    return tipo
        
        # Si no se detecta, asumir 'citas' como default
        return 'citas'
    
    def _extraer_fechas(self):
        """Extrae fechas del texto en lenguaje natural."""
        texto = self.texto_original
        hoy = datetime.now().date()
        
        # Patrón: "del X al Y de MES"
        # Ejemplos: "del 1 al 5 de septiembre", "del 10 al 15 de diciembre"
        patron_rango_mes = r'del?\s+(\d{1,2})\s+al?\s+(\d{1,2})\s+de\s+(\w+)'
        match = re.search(patron_rango_mes, texto)
        
        if match:
            dia_inicio = int(match.group(1))
            dia_fin = int(match.group(2))
            mes_nombre = match.group(3)
            
            # Obtener número de mes
            mes = self.MESES.get(mes_nombre)
            
            if mes:
                # Determinar el año (si el mes ya pasó este año, asumir año siguiente)
                anio = hoy.year
                if mes < hoy.month or (mes == hoy.month and dia_inicio < hoy.day):
                    # Si hablan de un mes pasado, podría ser el año actual o pasado
                    # Por simplicidad, usar año actual
                    pass
                
                self.fecha_inicio = datetime(anio, mes, dia_inicio).date()
                self.fecha_fin = datetime(anio, mes, dia_fin).date()
                
                logger.info(f"📅 Rango detectado: {self.fecha_inicio} a {self.fecha_fin}")
                return
        
        # Patrón: "del X de MES al Y de MES"
        # Ejemplo: "del 25 de agosto al 5 de septiembre"
        patron_rango_meses = r'del?\s+(\d{1,2})\s+de\s+(\w+)\s+al?\s+(\d{1,2})\s+de\s+(\w+)'
        match = re.search(patron_rango_meses, texto)
        
        if match:
            dia_inicio = int(match.group(1))
            mes_inicio_nombre = match.group(2)
            dia_fin = int(match.group(3))
            mes_fin_nombre = match.group(4)
            
            mes_inicio = self.MESES.get(mes_inicio_nombre)
            mes_fin = self.MESES.get(mes_fin_nombre)
            
            if mes_inicio and mes_fin:
                anio = hoy.year
                self.fecha_inicio = datetime(anio, mes_inicio, dia_inicio).date()
                self.fecha_fin = datetime(anio, mes_fin, dia_fin).date()
                
                logger.info(f"📅 Rango detectado: {self.fecha_inicio} a {self.fecha_fin}")
                return
        
        # Patrón: "esta semana"
        if 'esta semana' in texto:
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            self.fecha_inicio = inicio_semana
            self.fecha_fin = inicio_semana + timedelta(days=6)
            logger.info(f"📅 Esta semana: {self.fecha_inicio} a {self.fecha_fin}")
            return
        
        # Patrón: "semana pasada"
        if 'semana pasada' in texto or 'última semana' in texto:
            inicio_semana_pasada = hoy - timedelta(days=hoy.weekday() + 7)
            self.fecha_inicio = inicio_semana_pasada
            self.fecha_fin = inicio_semana_pasada + timedelta(days=6)
            logger.info(f"📅 Semana pasada: {self.fecha_inicio} a {self.fecha_fin}")
            return
        
        # Patrón: "este mes"
        if 'este mes' in texto or 'mes actual' in texto:
            self.fecha_inicio = hoy.replace(day=1)
            ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
            self.fecha_fin = hoy.replace(day=ultimo_dia)
            logger.info(f"📅 Este mes: {self.fecha_inicio} a {self.fecha_fin}")
            return
        
        # Patrón: "mes pasado"
        if 'mes pasado' in texto or 'último mes' in texto:
            primer_dia_mes_pasado = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
            ultimo_dia_mes_pasado = hoy.replace(day=1) - timedelta(days=1)
            self.fecha_inicio = primer_dia_mes_pasado
            self.fecha_fin = ultimo_dia_mes_pasado
            logger.info(f"📅 Mes pasado: {self.fecha_inicio} a {self.fecha_fin}")
            return
        
        # Patrón: "hoy"
        if 'hoy' in texto:
            self.fecha_inicio = hoy
            self.fecha_fin = hoy
            logger.info(f"📅 Hoy: {self.fecha_inicio}")
            return
        
        # Patrón: "ayer"
        if 'ayer' in texto:
            ayer = hoy - timedelta(days=1)
            self.fecha_inicio = ayer
            self.fecha_fin = ayer
            logger.info(f"📅 Ayer: {self.fecha_inicio}")
            return
        
        # Patrón: "últimos X días"
        patron_ultimos_dias = r'(?:últimos?|ultimo)\s+(\d+)\s+días?'
        match = re.search(patron_ultimos_dias, texto)
        if match:
            dias = int(match.group(1))
            self.fecha_inicio = hoy - timedelta(days=dias)
            self.fecha_fin = hoy
            logger.info(f"📅 Últimos {dias} días: {self.fecha_inicio} a {self.fecha_fin}")
            return
        
        # Patrón: mes específico "de enero", "en febrero"
        for mes_nombre, mes_num in self.MESES.items():
            if mes_nombre in texto:
                anio = hoy.year
                self.fecha_inicio = datetime(anio, mes_num, 1).date()
                ultimo_dia = calendar.monthrange(anio, mes_num)[1]
                self.fecha_fin = datetime(anio, mes_num, ultimo_dia).date()
                logger.info(f"📅 Mes {mes_nombre}: {self.fecha_inicio} a {self.fecha_fin}")
                return
        
        # Si no se detecta ninguna fecha, usar un rango amplio (últimos 6 meses)
        logger.warning("⚠️ No se detectó fecha específica, usando últimos 6 meses")
        self.fecha_inicio = hoy - timedelta(days=180)  # 6 meses atrás
        self.fecha_fin = hoy
    
    def _extraer_filtros(self):
        """Extrae filtros adicionales del texto."""
        texto = self.texto_original
        
        # Detectar estado (pendiente, completado, cancelado)
        if 'pendiente' in texto or 'pendientes' in texto:
            self.filtros_adicionales['estado'] = 'pendiente'
        elif 'completado' in texto or 'completados' in texto or 'completada' in texto:
            self.filtros_adicionales['estado'] = 'completado'
        elif 'cancelado' in texto or 'cancelados' in texto or 'cancelada' in texto:
            self.filtros_adicionales['estado'] = 'cancelado'
        
        # Detectar nombre de paciente (muy básico)
        # Patrón: "del paciente Juan", "de la paciente María"
        patron_paciente = r'(?:del?|de la)\s+paciente\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)'
        match = re.search(patron_paciente, texto, re.IGNORECASE)
        if match:
            self.filtros_adicionales['paciente_nombre'] = match.group(1).title()
        
        # Detectar monto (para facturas)
        # Patrón: "mayor a 1000", "menor a 500", "más de 200"
        patron_monto = r'(?:mayor|mas|más)\s+(?:a|de|que)\s+(\d+)'
        match = re.search(patron_monto, texto)
        if match:
            self.filtros_adicionales['monto_minimo'] = float(match.group(1))
        
        patron_monto_menor = r'(?:menor|menos)\s+(?:a|de|que)\s+(\d+)'
        match = re.search(patron_monto_menor, texto)
        if match:
            self.filtros_adicionales['monto_maximo'] = float(match.group(1))
    
    def _generar_interpretacion(self):
        """Genera una descripción legible de lo que se interpretó."""
        partes = []
        
        # Tipo de reporte
        partes.append(f"Reporte de {self.tipo_reporte}")
        
        # Fechas
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio == self.fecha_fin:
                partes.append(f"del {self.fecha_inicio.strftime('%d/%m/%Y')}")
            else:
                # Verificar si es un rango muy amplio (indica búsqueda general)
                dias_diferencia = (self.fecha_fin - self.fecha_inicio).days
                if dias_diferencia > 150:  # Más de 5 meses = búsqueda general
                    partes.append("(todos los registros disponibles)")
                else:
                    partes.append(
                        f"desde el {self.fecha_inicio.strftime('%d/%m/%Y')} "
                        f"hasta el {self.fecha_fin.strftime('%d/%m/%Y')}"
                    )
        
        # Filtros
        if self.filtros_adicionales.get('estado'):
            partes.append(f"con estado: {self.filtros_adicionales['estado']}")
        
        if self.filtros_adicionales.get('paciente_nombre'):
            partes.append(f"del paciente: {self.filtros_adicionales['paciente_nombre']}")
        
        if self.filtros_adicionales.get('monto_minimo'):
            partes.append(f"con monto mayor a ${self.filtros_adicionales['monto_minimo']}")
        
        if self.filtros_adicionales.get('monto_maximo'):
            partes.append(f"con monto menor a ${self.filtros_adicionales['monto_maximo']}")
        
        return " ".join(partes)


def parse_voice_command(texto):
    """
    Función helper para parsear comandos de voz.
    
    Args:
        texto (str): Comando de voz transcrito
        
    Returns:
        dict: Información parseada
    """
    parser = VoiceReportParser()
    return parser.parse(texto)
