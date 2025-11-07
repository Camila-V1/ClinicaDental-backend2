# reportes/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

# Importamos los modelos que vamos a consultar
from agenda.models import Cita
from tratamientos.models import ItemPlanTratamiento, Servicio, PlanDeTratamiento
from facturacion.models import Factura, Pago
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo

# Importamos nuestros serializers de reportes
from .serializers import (
    ReporteSimpleSerializer, 
    ReporteTendenciaSerializer,
    ReporteFinancieroSerializer,
    ReporteEstadisticasGeneralesSerializer
)


class ReportesViewSet(viewsets.ViewSet):
    """
    API para generar reportes y estadísticas (CU38).
    
    Este ViewSet no tiene un modelo base, solo acciones personalizadas
    que consultan múltiples modelos para generar estadísticas.
    
    Endpoints disponibles:
    - GET /api/reportes/dashboard-kpis/ - KPIs principales
    - GET /api/reportes/tendencia-citas/ - Gráfico de tendencia de citas
    - GET /api/reportes/top-procedimientos/ - Procedimientos más realizados
    - GET /api/reportes/estadisticas-generales/ - Estadísticas del sistema
    - GET /api/reportes/reporte-financiero/ - Resumen financiero detallado
    - GET /api/reportes/ocupacion-odontologos/ - Tasa de ocupación por doctor
    """
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios logueados

    def get_queryset(self):
        # Este método es requerido por el router, pero no lo usamos
        return None

    @action(detail=False, methods=['get'], url_path='dashboard-kpis')
    def dashboard_kpis(self, request):
        """
        Devuelve los 4 KPIs principales para el dashboard.
        
        GET /api/reportes/dashboard-kpis/
        
        Respuesta: Lista de objetos con etiqueta y valor
        """
        hoy = timezone.now().date()
        
        # 1. Total Pacientes Activos
        total_pacientes = PerfilPaciente.objects.filter(
            usuario__is_active=True
        ).count()
        
        # 2. Citas del día (confirmadas y completadas)
        citas_hoy = Cita.objects.filter(
            fecha_hora__date=hoy,
            estado__in=['CONFIRMADA', 'COMPLETADA']
        ).count()
        
        # 3. Ingresos del Mes (Facturas Pagadas este mes)
        mes_actual = hoy.month
        anio_actual = hoy.year
        ingresos_mes = Pago.objects.filter(
            fecha_pago__year=anio_actual,
            fecha_pago__month=mes_actual,
            estado_pago='COMPLETADO'
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')
        
        # 4. Saldo Pendiente (Facturas pendientes menos lo ya pagado)
        facturas_pendientes = Factura.objects.filter(estado='PENDIENTE')
        saldo_pendiente = sum(f.saldo_pendiente for f in facturas_pendientes)

        data = [
            {"etiqueta": "Pacientes Activos", "valor": total_pacientes},
            {"etiqueta": "Citas Hoy", "valor": citas_hoy},
            {"etiqueta": "Ingresos Este Mes", "valor": float(ingresos_mes)},
            {"etiqueta": "Saldo Pendiente", "valor": float(saldo_pendiente)},
        ]
        
        serializer = ReporteSimpleSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='tendencia-citas')
    def tendencia_citas(self, request):
        """
        Reporte para el gráfico de "Tendencia de citas por día".
        
        GET /api/reportes/tendencia-citas/?dias=15
        
        Parámetros:
        - dias: Número de días a analizar (default: 15)
        """
        dias_a_revisar = int(request.query_params.get('dias', 15))
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=dias_a_revisar - 1)
        
        # Generar todos los días del rango (incluso sin citas)
        data = []
        fecha_actual = fecha_inicio
        
        # Obtener citas agrupadas por fecha
        citas_por_fecha = dict(
            Cita.objects
            .filter(fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin)
            .exclude(estado='CANCELADA')
            .values('fecha_hora__date')
            .annotate(cantidad=Count('id'))
            .values_list('fecha_hora__date', 'cantidad')
        )
        
        # Llenar todos los días del rango
        while fecha_actual <= fecha_fin:
            cantidad = citas_por_fecha.get(fecha_actual, 0)
            data.append({
                'fecha': fecha_actual,
                'cantidad': cantidad
            })
            fecha_actual += timedelta(days=1)
        
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
        
        serializer = ReporteSimpleSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='estadisticas-generales')
    def estadisticas_generales(self, request):
        """
        Estadísticas generales completas del sistema.
        
        GET /api/reportes/estadisticas-generales/
        """
        hoy = timezone.now().date()
        mes_actual = hoy.month
        anio_actual = hoy.year
        
        # Calcular estadísticas
        total_pacientes_activos = PerfilPaciente.objects.filter(
            usuario__is_active=True
        ).count()
        
        total_odontologos = PerfilOdontologo.objects.filter(
            usuario__is_active=True
        ).count()
        
        citas_mes_actual = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual
        ).exclude(estado='CANCELADA').count()
        
        # Planes completados (asumimos estado 'COMPLETADO')
        tratamientos_completados = PlanDeTratamiento.objects.filter(
            estado='COMPLETADO'
        ).count()
        
        # Ingresos del mes
        ingresos_mes = Pago.objects.filter(
            fecha_pago__year=anio_actual,
            fecha_pago__month=mes_actual,
            estado_pago='COMPLETADO'
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')
        
        # Promedio de factura
        promedio_factura = Factura.objects.aggregate(
            promedio=Avg('monto_total')
        )['promedio'] or Decimal('0.00')
        
        # Tasa de ocupación (citas confirmadas/completadas vs total de citas)
        total_citas_mes = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual
        ).count()
        
        citas_efectivas = Cita.objects.filter(
            fecha_hora__year=anio_actual,
            fecha_hora__month=mes_actual,
            estado__in=['CONFIRMADA', 'COMPLETADA']
        ).count()
        
        tasa_ocupacion = (
            (citas_efectivas / total_citas_mes * 100) 
            if total_citas_mes > 0 else 0
        )
        
        data = {
            'total_pacientes_activos': total_pacientes_activos,
            'total_odontologos': total_odontologos,
            'citas_mes_actual': citas_mes_actual,
            'tratamientos_completados': tratamientos_completados,
            'ingresos_mes_actual': float(ingresos_mes),
            'promedio_factura': float(promedio_factura),
            'tasa_ocupacion': round(tasa_ocupacion, 2)
        }
        
        serializer = ReporteEstadisticasGeneralesSerializer(data)
        return Response(serializer.data)

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
        Tasa de ocupación por odontólogo.
        
        GET /api/reportes/ocupacion-odontologos/?mes=2025-11
        
        Parámetros:
        - mes: YYYY-MM (default: mes actual)
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
            # Citas totales del odontólogo en el mes
            total_citas = Cita.objects.filter(
                odontologo=odontologo,
                fecha_hora__year=anio,
                fecha_hora__month=mes
            ).count()
            
            # Citas efectivas (confirmadas/completadas)
            citas_efectivas = Cita.objects.filter(
                odontologo=odontologo,
                fecha_hora__year=anio,
                fecha_hora__month=mes,
                estado__in=['CONFIRMADA', 'COMPLETADA']
            ).count()
            
            # Calcular tasa de ocupación
            tasa_ocupacion = (
                (citas_efectivas / total_citas * 100) 
                if total_citas > 0 else 0
            )
            
            data.append({
                'etiqueta': odontologo.usuario.full_name,
                'valor': round(tasa_ocupacion, 2)
            })
        
        # Ordenar por tasa de ocupación descendente
        data.sort(key=lambda x: x['valor'], reverse=True)
        
        serializer = ReporteSimpleSerializer(data, many=True)
        return Response(serializer.data)
