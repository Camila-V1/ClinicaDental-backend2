# reportes/views.py

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Avg, Q, F, Max, Min
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

# Configurar logger
logger = logging.getLogger(__name__)

# Importamos los modelos que vamos a consultar
from agenda.models import Cita
from tratamientos.models import ItemPlanTratamiento, Servicio, PlanDeTratamiento
from facturacion.models import Factura, Pago
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo
from inventario.models import Insumo, CategoriaInsumo
from historial_clinico.models import DocumentoClinico, HistorialClinico

# Importamos nuestros serializers de reportes
from .serializers import (
    ReporteSimpleSerializer, 
    ReporteTendenciaSerializer,
    ReporteFinancieroSerializer,
    ReporteEstadisticasGeneralesSerializer,
    BitacoraSerializer
)

# Importamos las utilidades de exportación
from .utils import PDFReportGenerator, ExcelReportGenerator, format_currency, format_date
from .models import BitacoraAccion


class ReportesViewSet(viewsets.ViewSet):
    """
    API para generar reportes y estadísticas (CU37 y CU38).
    
    Este ViewSet no tiene un modelo base, solo acciones personalizadas
    que consultan múltiples modelos para generar estadísticas.
    
    TODOS LOS ENDPOINTS SOPORTAN EXPORTACIÓN A PDF Y EXCEL:
    - Añadir parámetro ?formato=pdf para exportar a PDF
    - Añadir parámetro ?formato=excel para exportar a Excel
    - Sin parámetro: Devuelve JSON (por defecto)
    
    Endpoints disponibles:
    - GET /api/reportes/dashboard-kpis/ - KPIs principales
    - GET /api/reportes/tendencia-citas/ - Gráfico de tendencia de citas
    - GET /api/reportes/top-procedimientos/ - Procedimientos más realizados
    - GET /api/reportes/estadisticas-generales/ - Estadísticas del sistema
    - GET /api/reportes/reporte-financiero/ - Resumen financiero detallado
    - GET /api/reportes/ocupacion-odontologos/ - Tasa de ocupación por doctor
    - GET /api/reportes/reporte-pacientes/ - Reporte detallado de pacientes
    - GET /api/reportes/reporte-tratamientos/ - Reporte de tratamientos
    - GET /api/reportes/reporte-inventario/ - Reporte de estado de inventario
    - GET /api/reportes/reporte-citas-odontologo/ - Citas por odontólogo
    - GET /api/reportes/reporte-ingresos-diarios/ - Ingresos día a día
    - GET /api/reportes/reporte-servicios-populares/ - Servicios más demandados
    """
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios logueados

    def get_queryset(self):
        # Este método es requerido por el router, pero no lo usamos
        return None
    
    def _get_tenant_name(self, request):
        """Obtiene el nombre del tenant actual"""
        return getattr(request.tenant, 'nombre', 'Clínica Dental')
    
    def _export_report(self, request, title, data, metrics=None):
        """
        Método auxiliar para exportar reportes a PDF o Excel
        
        Args:
            request: Request object
            title: Título del reporte
            data: Lista de diccionarios con datos
            metrics: Diccionario opcional con métricas clave
        """
        formato = request.query_params.get('formato', '').lower()
        
        logger.info(f"📊 _export_report llamado: formato={formato}, title={title}")
        
        if formato not in ['pdf', 'excel']:
            logger.info("📊 Formato no es pdf/excel, devolviendo None para JSON")
            return None  # Devolver JSON por defecto
        
        try:
            tenant_name = self._get_tenant_name(request)
            
            if formato == 'pdf':
                logger.info(f"📄 Generando PDF: {title}")
                pdf = PDFReportGenerator(title, tenant_name)
                pdf.add_header()
                
                if metrics:
                    pdf.add_key_metrics(metrics)
                
                if data:
                    # Convertir lista de diccionarios a tabla
                    if len(data) > 0:
                        headers = list(data[0].keys())
                        rows = [headers] + [[str(item.get(k, '')) for k in headers] for item in data]
                        pdf.add_table(rows, title="Datos del Reporte")
                
                response = pdf.generate()
                logger.info(f"✅ PDF generado exitosamente")
                return response
            
            elif formato == 'excel':
                logger.info(f"📊 Generando Excel: {title}")
                excel = ExcelReportGenerator(title, tenant_name)
                excel.add_header()
                
                if metrics:
                    excel.add_key_metrics(metrics)
                
                if data:
                    # Convertir lista de diccionarios a tabla
                    if len(data) > 0:
                        headers = list(data[0].keys())
                        rows = [headers] + [[item.get(k, '') for k in headers] for item in data]
                        excel.add_table(rows, title="Datos del Reporte")
                
                response = excel.generate()
                logger.info(f"✅ Excel generado exitosamente")
                return response
        
        except Exception as e:
            logger.error(f"❌ Error en _export_report: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
        return None

    @action(detail=False, methods=['get'], url_path='dashboard-kpis')
    def dashboard_kpis(self, request):
        """
        Devuelve los KPIs principales para el dashboard.
        
        GET /api/reportes/dashboard-kpis/
        GET /api/reportes/dashboard-kpis/?formato=pdf
        GET /api/reportes/dashboard-kpis/?formato=excel
        
        Respuesta JSON: Objeto con dos formatos para flexibilidad
        {
            "items": [  # Array de objetos {etiqueta, valor} para tablas
                {"etiqueta": "Pacientes Activos", "valor": 3},
                {"etiqueta": "Citas Hoy", "valor": 5},
                ...
            ],
            "kpis": {  # Objeto plano para acceso directo en frontend
                "total_pacientes": 3,
                "citas_hoy": 5,
                "ingresos_mes": 510.00,
                "saldo_pendiente": 260.00,
                "tratamientos_activos": 12,
                "planes_completados": 7,
                "promedio_factura": 38.50,
                "facturas_vencidas": 0,
                "total_procedimientos": 38,
                "pacientes_nuevos_mes": 3
            }
        }
        
        VERSIÓN: 3.2 - Formato dual (array + objeto) para mejor usabilidad
        """
        # Inicializar variables con valores por defecto
        total_pacientes = 0
        citas_hoy = 0
        ingresos_mes = Decimal('0.00')
        saldo_pendiente = Decimal('0.00')
        tratamientos_activos = 0
        planes_completados = 0
        promedio_factura = Decimal('0.00')
        facturas_vencidas = 0
        total_procedimientos = 0
        pacientes_nuevos_mes = 0
        
        try:
            hoy = timezone.now().date()
            mes_actual = hoy.month
            anio_actual = hoy.year
            
            # 1. Total Pacientes Activos
            total_pacientes = PerfilPaciente.objects.filter(
                usuario__is_active=True
            ).count()
            
            # 2. Citas del día (confirmadas y completadas)
            citas_hoy = Cita.objects.filter(
                fecha_hora__date=hoy,
                estado__in=['CONFIRMADA', 'ATENDIDA']
            ).count()
            
            # 3. Ingresos del Mes (Pagos completados este mes)
            ingresos_mes = Pago.objects.filter(
                fecha_pago__year=anio_actual,
                fecha_pago__month=mes_actual,
                estado_pago='COMPLETADO'
            ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')
            
            # 4. Saldo Pendiente (Total de facturas pendientes)
            facturas_pendientes = Factura.objects.filter(estado='PENDIENTE')
            saldo_pendiente = Decimal('0.00')
            for factura in facturas_pendientes:
                try:
                    saldo_pendiente += factura.saldo_pendiente
                except Exception as e:
                    # Si una factura tiene problemas, continuar con las demás
                    continue
            
            # 5. Tratamientos Activos (Planes en progreso)
            tratamientos_activos = PlanDeTratamiento.objects.filter(
                estado__in=['en_progreso', 'propuesto', 'aprobado']
            ).count()
            
            # 6. Planes Completados (este mes)
            planes_completados = PlanDeTratamiento.objects.filter(
                estado='completado',
                fecha_creacion__year=anio_actual,
                fecha_creacion__month=mes_actual
            ).count()
            
            # 7. Promedio por Factura (del mes actual)
            facturas_mes = Factura.objects.filter(
                fecha_emision__year=anio_actual,
                fecha_emision__month=mes_actual
            )
            total_facturado = facturas_mes.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            num_facturas = facturas_mes.count()
            promedio_factura = (total_facturado / num_facturas) if num_facturas > 0 else Decimal('0.00')
            
            # 8. Facturas Vencidas (pendientes del mes pasado o anteriores)
            # Como no hay fecha_vencimiento, consideramos facturas PENDIENTES de meses anteriores
            inicio_mes = timezone.datetime(anio_actual, mes_actual, 1).date()
            facturas_vencidas = Factura.objects.filter(
                estado='PENDIENTE',
                fecha_emision__date__lt=inicio_mes
            ).count()
            
            # 9. Total Procedimientos Completados (este mes)
            # El campo correcto es fecha_realizada, no fecha_realizacion
            total_procedimientos = ItemPlanTratamiento.objects.filter(
                estado='COMPLETADO',
                fecha_realizada__year=anio_actual,
                fecha_realizada__month=mes_actual
            ).count()
            
            # 10. Pacientes Nuevos del Mes
            pacientes_nuevos_mes = Usuario.objects.filter(
                date_joined__year=anio_actual,
                date_joined__month=mes_actual,
                perfil_paciente__isnull=False
            ).count()

        except Exception as e:
            # En caso de cualquier error, usar los valores por defecto ya inicializados
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en dashboard_kpis: {str(e)}", exc_info=True)
        
        # Construir respuesta con los valores (ya sea calculados o por defecto)
        data = [
            {"etiqueta": "Pacientes Activos", "valor": total_pacientes},
            {"etiqueta": "Citas Hoy", "valor": citas_hoy},
            {"etiqueta": "Ingresos Este Mes", "valor": float(ingresos_mes)},
            {"etiqueta": "Saldo Pendiente", "valor": float(saldo_pendiente)},
            {"etiqueta": "Tratamientos Activos", "valor": tratamientos_activos},
            {"etiqueta": "Planes Completados", "valor": planes_completados},
            {"etiqueta": "Promedio por Factura", "valor": float(promedio_factura)},
            {"etiqueta": "Facturas Vencidas", "valor": facturas_vencidas},
            {"etiqueta": "Total Procedimientos", "valor": total_procedimientos},
            {"etiqueta": "Pacientes Nuevos Mes", "valor": pacientes_nuevos_mes},
        ]
        
        # Exportar si se solicita
        export_response = self._export_report(
            request, 
            "KPIs del Dashboard",
            data,
            metrics={
                "Pacientes Activos": total_pacientes,
                "Citas Hoy": citas_hoy,
                "Ingresos Este Mes": format_currency(Decimal(str(ingresos_mes))),
                "Saldo Pendiente": format_currency(Decimal(str(saldo_pendiente))),
                "Tratamientos Activos": tratamientos_activos,
                "Planes Completados": planes_completados,
                "Promedio por Factura": format_currency(Decimal(str(promedio_factura))),
                "Facturas Vencidas": facturas_vencidas,
                "Total Procedimientos": total_procedimientos,
                "Pacientes Nuevos Mes": pacientes_nuevos_mes
            }
        )
        if export_response:
            return export_response
        
        # Devolver tanto el formato de array (para compatibilidad)
        # como un objeto plano (para facilitar el uso en frontend)
        response_data = {
            'items': data,  # Array original
            'kpis': {  # Objeto plano para acceso directo
                'total_pacientes': total_pacientes,
                'citas_hoy': citas_hoy,
                'ingresos_mes': float(ingresos_mes),
                'saldo_pendiente': float(saldo_pendiente),
                'tratamientos_activos': tratamientos_activos,
                'planes_completados': planes_completados,
                'promedio_factura': float(promedio_factura),
                'facturas_vencidas': facturas_vencidas,
                'total_procedimientos': total_procedimientos,
                'pacientes_nuevos_mes': pacientes_nuevos_mes
            }
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='tendencia-citas')
    def tendencia_citas(self, request):
        """
        Reporte para el gráfico de "Tendencia de citas por día".
        
        GET /api/reportes/tendencia-citas/?dias=15
        
        Parámetros:
        - dias: Número de días a analizar (default: 15)
        
        Retorna:
        [
            {
                'fecha': '2025-11-07',
                'cantidad': 5,
                'completadas': 3,
                'canceladas': 1
            }
        ]
        """
        dias_a_revisar = int(request.query_params.get('dias', 15))
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=dias_a_revisar - 1)
        
        # Generar todos los días del rango (incluso sin citas)
        data = []
        fecha_actual = fecha_inicio
        
        # Llenar todos los días del rango con desglose por estado
        while fecha_actual <= fecha_fin:
            citas_del_dia = Cita.objects.filter(
                fecha_hora__date=fecha_actual
            )
            
            total = citas_del_dia.count()
            completadas = citas_del_dia.filter(estado='ATENDIDA').count()
            canceladas = citas_del_dia.filter(estado='CANCELADA').count()
            
            data.append({
                'fecha': fecha_actual,
                'cantidad': total,
                'completadas': completadas,
                'canceladas': canceladas
            })
            fecha_actual += timedelta(days=1)
        
        # Intentar exportar si se solicitó formato
        export_data = [
            {
                'Fecha': format_date(item['fecha']),
                'Total Citas': item['cantidad'],
                'Completadas': item['completadas'],
                'Canceladas': item['canceladas']
            }
            for item in data
        ]
        
        metrics = {
            'Total de Días': len(data),
            'Total Citas': sum(item['cantidad'] for item in data),
            'Completadas': sum(item['completadas'] for item in data),
            'Canceladas': sum(item['canceladas'] for item in data)
        }
        
        export_response = self._export_report(
            request,
            f"Tendencia de Citas - Últimos {dias_a_revisar} días",
            export_data,
            metrics
        )
        
        if export_response:
            return export_response
        
        serializer = ReporteTendenciaSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top-procedimientos')
    def top_procedimientos(self, request):
        """
        Reporte de los procedimientos más realizados.
        
        GET /api/reportes/top-procedimientos/?limite=5
        
        Parámetros:
        - limite: Número de procedimientos a mostrar (default: 5)
        """
        limite = int(request.query_params.get('limite', 5))
        
        # Contar ítems por servicio en planes de tratamiento
        top_servicios = (
            ItemPlanTratamiento.objects
            .select_related('servicio')
            .values('servicio__nombre')
            .annotate(valor=Count('id'))
            .order_by('-valor')[:limite]
        )
        
        data = [
            {
                'etiqueta': item['servicio__nombre'] or 'Sin nombre', 
                'valor': item['valor']
            } 
            for item in top_servicios
        ]
        
        # Intentar exportar si se solicitó formato
        export_data = [
            {
                'Procedimiento': item['etiqueta'],
                'Cantidad Realizada': item['valor']
            }
            for item in data
        ]
        
        metrics = {
            'Total Procedimientos': sum(item['valor'] for item in data),
            'Procedimientos Únicos': len(data)
        }
        
        export_response = self._export_report(
            request,
            f"Top {limite} Procedimientos Más Realizados",
            export_data,
            metrics
        )
        
        if export_response:
            return export_response
        
        serializer = ReporteSimpleSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='estadisticas-generales')
    def estadisticas_generales(self, request):
        """
        Estadísticas generales completas del sistema.
        
        GET /api/reportes/estadisticas-generales/
        
        Devuelve métricas completas del sistema incluyendo:
        - Pacientes (total, activos, nuevos del mes)
        - Citas (total mes, completadas, pendientes, canceladas)
        - Financiero (ingresos, pendiente, facturas vencidas)
        - Tratamientos (planes activos, completados, procedimientos totales)
        """
        hoy = timezone.now().date()
        mes_actual = hoy.month
        anio_actual = hoy.year
        inicio_mes = date(anio_actual, mes_actual, 1)
        
        # ====== ESTADÍSTICAS DE PACIENTES ======
        total_pacientes_activos = PerfilPaciente.objects.filter(
            usuario__is_active=True
        ).count()
        
        # Pacientes nuevos del mes (usuarios creados en mes actual que tienen perfil paciente)
        pacientes_nuevos_mes = Usuario.objects.filter(
            date_joined__year=anio_actual,
            date_joined__month=mes_actual,
            perfil_paciente__isnull=False
        ).count()
        
        # ====== ESTADÍSTICAS DE ODONTÓLOGOS ======
        total_odontologos = PerfilOdontologo.objects.filter(
            usuario__is_active=True
        ).count()
        
        # ====== ESTADÍSTICAS DE CITAS ======
        # Total de citas del mes (excluyendo canceladas)
        citas_mes_actual = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual
        ).exclude(estado='CANCELADA').count()
        
        # Citas completadas del mes
        citas_completadas = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual,
            estado='ATENDIDA'
        ).count()
        
        # Citas pendientes del mes (PENDIENTE o CONFIRMADA)
        citas_pendientes = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).count()
        
        # Citas canceladas del mes
        citas_canceladas = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual,
            estado='CANCELADA'
        ).count()
        
        # ====== ESTADÍSTICAS DE TRATAMIENTOS ======
        # Planes completados
        tratamientos_completados = PlanDeTratamiento.objects.filter(
            estado='completado'
        ).count()
        
        # Planes activos (en_progreso, propuesto, aprobado)
        planes_activos = PlanDeTratamiento.objects.filter(
            estado__in=['en_progreso', 'propuesto', 'aprobado']
        ).count()
        
        # Total de procedimientos realizados
        total_procedimientos = ItemPlanTratamiento.objects.filter(
            estado='COMPLETADO'
        ).count()
        
        # ====== ESTADÍSTICAS FINANCIERAS ======
        # Ingresos del mes (pagos completados)
        ingresos_mes = Pago.objects.filter(
            fecha_pago__year=anio_actual,
            fecha_pago__month=mes_actual,
            estado_pago='COMPLETADO'
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')
        
        # Monto pendiente de cobro (facturas emitidas - pagado)
        facturas_mes = Factura.objects.filter(
            fecha_emision__year=anio_actual,
            fecha_emision__month=mes_actual
        )
        
        total_facturado_mes = facturas_mes.aggregate(
            total=Sum('monto_total')
        )['total'] or Decimal('0.00')
        
        total_pagado_mes = facturas_mes.aggregate(
            total=Sum('monto_pagado')
        )['total'] or Decimal('0.00')
        
        monto_pendiente = total_facturado_mes - total_pagado_mes
        
        # Facturas pendientes (estado PENDIENTE con saldo > 0)
        facturas_vencidas = Factura.objects.filter(
            estado='PENDIENTE',
            monto_pagado__lt=F('monto_total')
        ).count()
        
        # Promedio de factura
        promedio_factura = Factura.objects.aggregate(
            promedio=Avg('monto_total')
        )['promedio'] or Decimal('0.00')
        
        # ====== TASA DE OCUPACIÓN ======
        total_citas_mes = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual
        ).count()
        
        citas_efectivas = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual,
            estado__in=['CONFIRMADA', 'ATENDIDA']
        ).count()
        
        tasa_ocupacion = (
            (citas_efectivas / total_citas_mes * 100) 
            if total_citas_mes > 0 else 0
        )
        
        # ====== RESPUESTA COMPLETA ======
        data = {
            # Pacientes
            'total_pacientes_activos': total_pacientes_activos,
            'pacientes_nuevos_mes': pacientes_nuevos_mes,
            
            # Odontólogos
            'total_odontologos': total_odontologos,
            
            # Citas
            'citas_mes_actual': citas_mes_actual,
            'citas_completadas': citas_completadas,
            'citas_pendientes': citas_pendientes,
            'citas_canceladas': citas_canceladas,
            
            # Tratamientos
            'planes_completados': tratamientos_completados,
            'planes_activos': planes_activos,
            'total_procedimientos': total_procedimientos,
            
            # Financiero
            'ingresos_mes_actual': float(ingresos_mes),
            'monto_pendiente': float(monto_pendiente),
            'facturas_vencidas': facturas_vencidas,
            'promedio_factura': float(promedio_factura),
            
            # Ocupación
            'tasa_ocupacion': round(tasa_ocupacion, 2)
        }
        
        # Exportar si se solicita
        export_response = self._export_report(
            request,
            "Estadísticas Generales del Sistema",
            [
                {"Métrica": "Pacientes Activos", "Valor": total_pacientes_activos},
                {"Métrica": "Pacientes Nuevos (Mes)", "Valor": pacientes_nuevos_mes},
                {"Métrica": "Total Odontólogos", "Valor": total_odontologos},
                {"Métrica": "Citas del Mes", "Valor": citas_mes_actual},
                {"Métrica": "Citas Completadas", "Valor": citas_completadas},
                {"Métrica": "Citas Pendientes", "Valor": citas_pendientes},
                {"Métrica": "Citas Canceladas", "Valor": citas_canceladas},
                {"Métrica": "Planes Completados", "Valor": tratamientos_completados},
                {"Métrica": "Planes Activos", "Valor": planes_activos},
                {"Métrica": "Total Procedimientos", "Valor": total_procedimientos},
                {"Métrica": "Ingresos Mes Actual", "Valor": format_currency(ingresos_mes)},
                {"Métrica": "Monto Pendiente", "Valor": format_currency(monto_pendiente)},
                {"Métrica": "Facturas Vencidas", "Valor": facturas_vencidas},
                {"Métrica": "Promedio por Factura", "Valor": format_currency(promedio_factura)},
                {"Métrica": "Tasa de Ocupación", "Valor": f"{round(tasa_ocupacion, 2)}%"},
            ],
            metrics={
                "Pacientes Activos": total_pacientes_activos,
                "Odontólogos": total_odontologos,
                "Citas del Mes": citas_mes_actual,
                "Ingresos Mes": format_currency(ingresos_mes),
                "Tasa Ocupación": f"{round(tasa_ocupacion, 2)}%"
            }
        )
        if export_response:
            return export_response
        
        return Response(data)

    @action(detail=False, methods=['get'], url_path='reporte-financiero')
    def reporte_financiero(self, request):
        """
        Reporte financiero detallado por período.
        
        GET /api/reportes/reporte-financiero/?periodo=2025-11
        
        Parámetros:
        - periodo: YYYY-MM para mensual, YYYY para anual (default: mes actual)
        """
        hoy = timezone.now().date()
        periodo_param = request.query_params.get('periodo')
        
        if periodo_param:
            try:
                if len(periodo_param) == 4:  # Año (YYYY)
                    anio = int(periodo_param)
                    filtro_fecha = Q(fecha_emision__year=anio)
                    periodo_label = periodo_param
                elif len(periodo_param) == 7:  # Mes (YYYY-MM)
                    anio, mes = map(int, periodo_param.split('-'))
                    filtro_fecha = Q(fecha_emision__year=anio, fecha_emision__month=mes)
                    periodo_label = periodo_param
                else:
                    raise ValueError("Formato inválido")
            except ValueError:
                return Response(
                    {'error': 'Formato de período inválido. Use YYYY-MM o YYYY'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Período por defecto: mes actual
            filtro_fecha = Q(
                fecha_emision__year=hoy.year, 
                fecha_emision__month=hoy.month
            )
            periodo_label = f"{hoy.year}-{hoy.month:02d}"
        
        # Calcular métricas financieras
        facturas_periodo = Factura.objects.filter(filtro_fecha)
        
        total_facturado = facturas_periodo.aggregate(
            total=Sum('monto_total')
        )['total'] or Decimal('0.00')
        
        total_pagado = facturas_periodo.aggregate(
            total=Sum('monto_pagado')
        )['total'] or Decimal('0.00')
        
        saldo_pendiente = total_facturado - total_pagado
        numero_facturas = facturas_periodo.count()
        
        data = {
            'periodo': periodo_label,
            'total_facturado': float(total_facturado),
            'total_pagado': float(total_pagado),
            'saldo_pendiente': float(saldo_pendiente),
            'numero_facturas': numero_facturas
        }
        
        serializer = ReporteFinancieroSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='ocupacion-odontologos')
    def ocupacion_odontologos(self, request):
        """
        Tasa de ocupación por odontólogo con detalles completos.
        
        GET /api/reportes/ocupacion-odontologos/?mes=2025-11
        
        Parámetros:
        - mes: YYYY-MM (default: mes actual)
        
        Retorna:
        [
            {
                'usuario_id': 353,
                'nombre_completo': 'Dr. Juan Pérez',
                'total_citas': 7,
                'citas_completadas': 5,
                'citas_canceladas': 1,
                'horas_ocupadas': 10,
                'tasa_ocupacion': '71.43',
                'pacientes_atendidos': 5
            }
        ]
        """
        mes_param = request.query_params.get('mes')
        hoy = timezone.now().date()
        
        if mes_param:
            try:
                anio, mes = map(int, mes_param.split('-'))
            except ValueError:
                return Response(
                    {'error': 'Formato de mes inválido. Use YYYY-MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            anio, mes = hoy.year, hoy.month
        
        # Obtener odontólogos activos
        odontologos = PerfilOdontologo.objects.filter(
            usuario__is_active=True
        ).select_related('usuario')
        
        data = []
        
        for odontologo in odontologos:
            # Base de citas del mes
            citas_mes = Cita.objects.filter(
                odontologo=odontologo,
                fecha_hora__year=anio,
                fecha_hora__month=mes
            )
            
            # Contar por estado
            total_citas = citas_mes.count()
            citas_completadas = citas_mes.filter(estado='ATENDIDA').count()
            citas_canceladas = citas_mes.filter(estado='CANCELADA').count()
            
            # Calcular horas ocupadas (asumiendo 2 horas por cita completada)
            horas_ocupadas = citas_completadas * 2
            
            # Pacientes únicos atendidos
            pacientes_atendidos = citas_mes.filter(
                estado='ATENDIDA'
            ).values('paciente').distinct().count()
            
            # Calcular tasa de ocupación
            if total_citas > 0:
                tasa_ocupacion = round((citas_completadas / total_citas * 100), 2)
            else:
                tasa_ocupacion = 0.0
            
            # Enviar estructura completa
            data.append({
                'usuario_id': odontologo.usuario.id,
                'nombre_completo': odontologo.usuario.full_name,
                'total_citas': total_citas,
                'citas_completadas': citas_completadas,
                'citas_canceladas': citas_canceladas,
                'horas_ocupadas': horas_ocupadas,
                'tasa_ocupacion': str(tasa_ocupacion),
                'pacientes_atendidos': pacientes_atendidos
            })
        
        # Ordenar por tasa de ocupación descendente
        data.sort(key=lambda x: float(x['tasa_ocupacion']), reverse=True)
        
        # Retornar directamente sin serializer genérico
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-pacientes')
    def reporte_pacientes(self, request):
        """
        Reporte detallado de pacientes con filtros dinámicos.
        
        GET /api/reportes/reporte-pacientes/?activo=true&desde=2025-01-01&hasta=2025-12-31&formato=excel
        
        Parámetros:
        - activo: true/false (filtrar por estado)
        - desde: Fecha de registro desde (YYYY-MM-DD)
        - hasta: Fecha de registro hasta (YYYY-MM-DD)
        - formato: json/pdf/excel
        """
        queryset = PerfilPaciente.objects.select_related('usuario').all()
        
        # Filtros dinámicos
        activo = request.query_params.get('activo')
        if activo:
            queryset = queryset.filter(usuario__is_active=activo.lower() == 'true')
        
        desde = request.query_params.get('desde')
        if desde:
            queryset = queryset.filter(usuario__date_joined__gte=desde)
        
        hasta = request.query_params.get('hasta')
        if hasta:
            queryset = queryset.filter(usuario__date_joined__lte=hasta)
        
        # Preparar datos
        data = []
        for paciente in queryset:
            # Calcular estadísticas del paciente
            total_citas = Cita.objects.filter(paciente=paciente).count()
            facturas = Factura.objects.filter(paciente=paciente)
            total_gastado = facturas.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            
            data.append({
                'nombre': paciente.usuario.full_name,
                'email': paciente.usuario.email,
                'telefono': paciente.telefono or 'N/A',
                'fecha_nacimiento': format_date(paciente.fecha_nacimiento),
                'fecha_registro': format_date(paciente.usuario.date_joined),
                'activo': 'Sí' if paciente.usuario.is_active else 'No',
                'total_citas': total_citas,
                'total_gastado': format_currency(total_gastado)
            })
        
        # Exportar si se solicita
        export_response = self._export_report(
            request,
            "Reporte de Pacientes",
            data
        )
        if export_response:
            return export_response
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-tratamientos')
    def reporte_tratamientos(self, request):
        """
        Reporte de tratamientos con filtros dinámicos.
        
        GET /api/reportes/reporte-tratamientos/?estado=EN_PROGRESO&desde=2025-01-01&formato=pdf
        
        Parámetros:
        - estado: PROPUESTO/EN_PROGRESO/COMPLETADO/CANCELADO
        - desde: Fecha desde (YYYY-MM-DD)
        - hasta: Fecha hasta (YYYY-MM-DD)
        - formato: json/pdf/excel
        """
        queryset = PlanDeTratamiento.objects.select_related('paciente__usuario', 'odontologo__usuario').all()
        
        # Filtros
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        desde = request.query_params.get('desde')
        if desde:
            queryset = queryset.filter(fecha_creacion__gte=desde)
        
        hasta = request.query_params.get('hasta')
        if hasta:
            queryset = queryset.filter(fecha_creacion__lte=hasta)
        
        # Preparar datos
        data = []
        for plan in queryset:
            items = ItemPlanTratamiento.objects.filter(plan_tratamiento=plan)
            total_items = items.count()
            completados = items.filter(estado='COMPLETADO').count()
            progreso = (completados / total_items * 100) if total_items > 0 else 0
            
            data.append({
                'paciente': plan.paciente.usuario.full_name,
                'odontologo': plan.odontologo.usuario.full_name,
                'fecha_creacion': format_date(plan.fecha_creacion),
                'estado': plan.get_estado_display(),
                'total_items': total_items,
                'completados': completados,
                'progreso': f"{progreso:.1f}%",
                'costo_total': format_currency(plan.costo_total)
            })
        
        export_response = self._export_report(request, "Reporte de Tratamientos", data)
        if export_response:
            return export_response
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-inventario')
    def reporte_inventario(self, request):
        """
        Reporte del estado actual del inventario.
        
        GET /api/reportes/reporte-inventario/?stock_bajo=true&formato=excel
        
        Parámetros:
        - stock_bajo: true (solo insumos con stock bajo)
        - categoria: Filtrar por ID de categoría
        - formato: json/pdf/excel
        """
        queryset = Insumo.objects.select_related('categoria').all()
        
        # Filtros
        stock_bajo = request.query_params.get('stock_bajo')
        if stock_bajo and stock_bajo.lower() == 'true':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        
        categoria_id = request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Preparar datos
        data = []
        for insumo in queryset:
            estado_stock = 'NORMAL'
            if insumo.stock_actual == 0:
                estado_stock = 'AGOTADO'
            elif insumo.stock_actual <= insumo.stock_minimo:
                estado_stock = 'BAJO'
            
            data.append({
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'categoria': insumo.categoria.nombre,
                'stock_actual': float(insumo.stock_actual),
                'stock_minimo': float(insumo.stock_minimo),
                'estado_stock': estado_stock,
                'unidad_medida': insumo.unidad_medida,
                'precio_costo': format_currency(insumo.precio_costo),
                'precio_venta': format_currency(insumo.precio_venta),
                'valor_total': format_currency(insumo.stock_actual * insumo.precio_costo),
                'proveedor': insumo.proveedor or 'N/A'
            })
        
        export_response = self._export_report(request, "Reporte de Inventario", data)
        if export_response:
            return export_response
        
        return Response(data)
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-citas-odontologo')
    def reporte_citas_odontologo(self, request):
        """
        Reporte de citas agrupadas por odontólogo.
        
        GET /api/reportes/reporte-citas-odontologo/?mes=2025-11&estado=ATENDIDA&formato=pdf
        
        Parámetros:
        - mes: YYYY-MM (default: mes actual)
        - estado: Filtrar por estado de cita
        - formato: json/pdf/excel
        """
        hoy = timezone.now().date()
        mes_param = request.query_params.get('mes', f"{hoy.year}-{hoy.month:02d}")
        
        try:
            anio, mes = map(int, mes_param.split('-'))
        except:
            return Response({'error': 'Formato de mes inválido'}, status=400)
        
        odontologos = PerfilOdontologo.objects.filter(usuario__is_active=True).select_related('usuario')
        
        data = []
        for odontologo in odontologos:
            queryset = Cita.objects.filter(
                odontologo=odontologo,
                fecha_hora__year=anio,
                fecha_hora__month=mes
            )
            
            # Filtro opcional por estado
            estado = request.query_params.get('estado')
            if estado:
                queryset = queryset.filter(estado=estado.upper())
            
            total_citas = queryset.count()
            confirmadas = queryset.filter(estado='CONFIRMADA').count()
            completadas = queryset.filter(estado='ATENDIDA').count()
            canceladas = queryset.filter(estado='CANCELADA').count()
            
            data.append({
                'odontologo': odontologo.usuario.full_name,
                'especialidad': odontologo.especialidad or 'General',
                'total_citas': total_citas,
                'confirmadas': confirmadas,
                'completadas': completadas,
                'canceladas': canceladas,
                'tasa_completado': f"{(completadas/total_citas*100):.1f}%" if total_citas > 0 else "0%"
            })
        
        export_response = self._export_report(request, "Reporte de Citas por Odontólogo", data)
        if export_response:
            return export_response
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-ingresos-diarios')
    def reporte_ingresos_diarios(self, request):
        """
        Reporte de ingresos día a día.
        
        GET /api/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30&formato=excel
        
        Parámetros:
        - desde: Fecha inicio (YYYY-MM-DD)
        - hasta: Fecha fin (YYYY-MM-DD)
        - formato: json/pdf/excel
        """
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        
        if not desde or not hasta:
            # Por defecto: últimos 30 días
            hasta_date = timezone.now().date()
            desde_date = hasta_date - timedelta(days=30)
        else:
            try:
                desde_date = timezone.datetime.strptime(desde, '%Y-%m-%d').date()
                hasta_date = timezone.datetime.strptime(hasta, '%Y-%m-%d').date()
            except:
                return Response({'error': 'Formato de fecha inválido'}, status=400)
        
        # Agrupar pagos por día
        pagos_por_dia = (
            Pago.objects
            .filter(fecha_pago__date__gte=desde_date, fecha_pago__date__lte=hasta_date, estado_pago='COMPLETADO')
            .values('fecha_pago__date')
            .annotate(
                total=Sum('monto_pagado'),
                num_pagos=Count('id')
            )
            .order_by('fecha_pago__date')
        )
        
        # Crear diccionario de pagos
        pagos_dict = {item['fecha_pago__date']: item for item in pagos_por_dia}
        
        # Generar todos los días del rango
        data = []
        fecha_actual = desde_date
        while fecha_actual <= hasta_date:
            pago_data = pagos_dict.get(fecha_actual, {'total': Decimal('0.00'), 'num_pagos': 0})
            
            data.append({
                'fecha': format_date(fecha_actual),
                'ingresos': format_currency(pago_data['total']),
                'num_pagos': pago_data['num_pagos']
            })
            fecha_actual += timedelta(days=1)
        
        export_response = self._export_report(request, "Ingresos Diarios", data)
        if export_response:
            return export_response
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='reporte-servicios-populares')
    def reporte_servicios_populares(self, request):
        """
        Reporte de servicios más solicitados con estadísticas.
        
        GET /api/reportes/reporte-servicios-populares/?limite=20&formato=pdf
        
        Parámetros:
        - limite: Número de servicios a mostrar (default: 10)
        - formato: json/pdf/excel
        """
        limite = int(request.query_params.get('limite', 10))
        
        servicios = Servicio.objects.all()
        
        data = []
        for servicio in servicios:
            items = ItemPlanTratamiento.objects.filter(servicio=servicio)
            total_veces = items.count()
            total_ingreso = items.aggregate(total=Sum('costo'))['total'] or Decimal('0.00')
            completados = items.filter(estado='COMPLETADO').count()
            
            if total_veces > 0:
                data.append({
                    'servicio': servicio.nombre,
                    'categoria': servicio.categoria,
                    'total_veces': total_veces,
                    'completados': completados,
                    'tasa_completado': f"{(completados/total_veces*100):.1f}%",
                    'precio_base': format_currency(servicio.precio_base),
                    'ingreso_total': format_currency(total_ingreso),
                    'ingreso_promedio': format_currency(total_ingreso / total_veces) if total_veces > 0 else "$0.00"
                })
        
        # Ordenar por total de veces y limitar
        data.sort(key=lambda x: x['total_veces'], reverse=True)
        data = data[:limite]
        
        export_response = self._export_report(request, "Servicios Más Populares", data)
        if export_response:
            return export_response
        
        return Response(data)


class BitacoraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consultar la bitácora/auditoría del sistema (CU39).
    
    Endpoints:
    - GET /api/bitacora/ - Listar todas las acciones
    - GET /api/bitacora/{id}/ - Detalle de una acción
    - GET /api/bitacora/?usuario=1&accion=CREAR&desde=2025-01-01 - Filtros
    
    Filtros disponibles:
    - usuario: ID del usuario
    - accion: CREAR/EDITAR/ELIMINAR/VER/LOGIN/LOGOUT/EXPORTAR/IMPRIMIR
    - desde: Fecha desde (YYYY-MM-DD)
    - hasta: Fecha hasta (YYYY-MM-DD)
    - modelo: Nombre del modelo (ej: 'paciente', 'cita', 'factura')
    - ip: Dirección IP
    - descripcion: Búsqueda en descripción
    """
    queryset = BitacoraAccion.objects.select_related('usuario', 'content_type').all()
    serializer_class = BitacoraSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination  # Paginación solo para bitácora
    filterset_fields = ['usuario', 'accion']
    search_fields = ['descripcion', 'ip_address']
    ordering_fields = ['fecha_hora', 'accion']
    ordering = ['-fecha_hora']
    
    def get_queryset(self):
        """Aplicar filtros dinámicos a la bitácora"""
        queryset = super().get_queryset()
        
        # Filtro por rango de fechas
        desde = self.request.query_params.get('desde')
        if desde:
            queryset = queryset.filter(fecha_hora__date__gte=desde)
        
        hasta = self.request.query_params.get('hasta')
        if hasta:
            queryset = queryset.filter(fecha_hora__date__lte=hasta)
        
        # Filtro por modelo
        modelo = self.request.query_params.get('modelo')
        if modelo:
            queryset = queryset.filter(content_type__model=modelo.lower())
        
        # Filtro por IP
        ip = self.request.query_params.get('ip')
        if ip:
            queryset = queryset.filter(ip_address=ip)
        
        # Búsqueda en descripción
        descripcion = self.request.query_params.get('descripcion')
        if descripcion:
            queryset = queryset.filter(descripcion__icontains=descripcion)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Estadísticas de la bitácora.
        
        GET /api/bitacora/estadisticas/?dias=7
        """
        dias = int(request.query_params.get('dias', 7))
        fecha_desde = timezone.now() - timedelta(days=dias)
        
        queryset = self.get_queryset().filter(fecha_hora__gte=fecha_desde)
        
        # Acciones por tipo
        acciones_por_tipo = list(
            queryset.values('accion')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        
        # Usuarios más activos
        usuarios_activos = list(
            queryset.values('usuario__first_name', 'usuario__last_name')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )
        
        # Actividad por día
        actividad_diaria = list(
            queryset.values('fecha_hora__date')
            .annotate(total=Count('id'))
            .order_by('fecha_hora__date')
        )
        
        return Response({
            'periodo': f'Últimos {dias} días',
            'total_acciones': queryset.count(),
            'acciones_por_tipo': acciones_por_tipo,
            'usuarios_mas_activos': usuarios_activos,
            'actividad_diaria': actividad_diaria
        })
    
    @action(detail=False, methods=['get'], url_path='exportar')
    def exportar(self, request):
        """
        Exportar bitácora a PDF o Excel.
        
        GET /api/bitacora/exportar/?formato=excel&desde=2025-01-01&hasta=2025-12-31
        """
        queryset = self.get_queryset()
        formato = request.query_params.get('formato', 'excel').lower()
        
        # Preparar datos
        data = []
        for registro in queryset[:1000]:  # Limitar a 1000 registros
            data.append({
                'fecha_hora': format_date(registro.fecha_hora),
                'usuario': registro.usuario.full_name if registro.usuario else 'Sistema',
                'accion': registro.get_accion_display(),
                'descripcion': registro.descripcion,
                'ip': registro.ip_address or 'N/A'
            })
        
        tenant_name = getattr(request.tenant, 'nombre', 'Clínica Dental')
        
        if formato == 'pdf':
            pdf = PDFReportGenerator("Bitácora de Auditoría", tenant_name)
            pdf.add_header()
            
            if data:
                headers = list(data[0].keys())
                rows = [headers] + [[str(item.get(k, '')) for k in headers] for item in data]
                pdf.add_table(rows, title="Registros de Bitácora")
            
            return pdf.generate()
        
        else:  # Excel
            excel = ExcelReportGenerator("Bitácora de Auditoría", tenant_name)
            excel.add_header()
            
            if data:
                headers = list(data[0].keys())
                rows = [headers] + [[item.get(k, '') for k in headers] for item in data]
                excel.add_table(rows, title="Registros de Bitácora")
            
            return excel.generate()

