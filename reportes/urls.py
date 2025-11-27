# reportes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportesViewSet, BitacoraViewSet
from .voice_views import VoiceReportQueryView

# Configurar router para API REST de reportes
router = DefaultRouter()
router.register(r'reportes', ReportesViewSet, basename='reportes')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),
    
    # Endpoint para reportes por voz con NLP
    path('voice-query/', VoiceReportQueryView.as_view(), name='voice-query'),
]

"""
Endpoints de Reportes Disponibles (CU37, CU38, CU39):

REPORTES BÁSICOS CON EXPORTACIÓN PDF/EXCEL:
- GET /api/reportes/reportes/dashboard-kpis/                          - KPIs principales del dashboard
- GET /api/reportes/reportes/estadisticas-generales/                  - Estadísticas completas del sistema
- GET /api/reportes/reportes/tendencia-citas/?dias=15                 - Gráfico de citas por día
- GET /api/reportes/reportes/top-procedimientos/?limite=5             - Procedimientos más realizados
- GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-11       - Tasa ocupación por doctor
- GET /api/reportes/reportes/reporte-financiero/?periodo=2025-11      - Resumen financiero detallado

NUEVOS REPORTES DINÁMICOS (CU37 - Personalización Total):
- GET /api/reportes/reportes/reporte-pacientes/?activo=true&desde=2025-01-01&formato=excel
- GET /api/reportes/reportes/reporte-tratamientos/?estado=EN_PROGRESO&formato=pdf
- GET /api/reportes/reportes/reporte-inventario/?stock_bajo=true&categoria=FARMACO&formato=excel
- GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11&estado=COMPLETADA&formato=pdf
- GET /api/reportes/reportes/reporte-ingresos-diarios/?desde=2025-11-01&hasta=2025-11-30&formato=excel
- GET /api/reportes/reportes/reporte-servicios-populares/?limite=20&formato=pdf

BITÁCORA/AUDITORÍA (CU39 - Implementado):
- GET /api/reportes/bitacora/ - Lista todas las acciones registradas
- GET /api/reportes/bitacora/?usuario=1&accion=CREAR&desde=2025-01-01&hasta=2025-12-31
  Filtros: usuario, accion, desde, hasta, modelo, ip, descripcion
- GET /api/reportes/bitacora/estadisticas/?dias=7 - Estadísticas de actividad
- GET /api/reportes/bitacora/exportar/?formato=excel&desde=2025-01-01 - Exportar bitácora

FORMATOS DE EXPORTACIÓN (CU38 - 100% Implementado):
TODOS los reportes soportan exportación añadiendo el parámetro ?formato=
- formato=json (por defecto)
- formato=pdf (archivo PDF con formato profesional)
- formato=excel (archivo XLSX con formato profesional)

Ejemplos:
  GET /api/reportes/reportes/dashboard-kpis/?formato=pdf
  GET /api/reportes/reportes/reporte-pacientes/?activo=true&formato=excel

AUTENTICACIÓN:
Todos los endpoints requieren autenticación JWT.
Incluir header: Authorization: Bearer <token>
"""
