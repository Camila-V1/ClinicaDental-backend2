# reportes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportesViewSet

# Configurar router para API REST de reportes
router = DefaultRouter()
router.register(r'', ReportesViewSet, basename='reportes')

urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),
]

"""
Endpoints de Reportes Disponibles (CU38):

DASHBOARD Y KPIs:
- GET /api/reportes/dashboard-kpis/           - KPIs principales del dashboard
- GET /api/reportes/estadisticas-generales/  - Estadísticas completas del sistema

TENDENCIAS Y GRÁFICOS:
- GET /api/reportes/tendencia-citas/?dias=15        - Gráfico de citas por día
- GET /api/reportes/top-procedimientos/?limite=5    - Procedimientos más realizados
- GET /api/reportes/ocupacion-odontologos/?mes=2025-11  - Tasa ocupación por doctor

REPORTES FINANCIEROS:
- GET /api/reportes/reporte-financiero/?periodo=2025-11  - Resumen financiero detallado

EJEMPLOS DE USO:

1. Dashboard Principal:
   GET /api/reportes/dashboard-kpis/
   Respuesta: [
     {"etiqueta": "Pacientes Activos", "valor": 150},
     {"etiqueta": "Citas Hoy", "valor": 8},
     {"etiqueta": "Ingresos Este Mes", "valor": 25000.00},
     {"etiqueta": "Saldo Pendiente", "valor": 5000.00}
   ]

2. Gráfico de Tendencias:
   GET /api/reportes/tendencia-citas/?dias=7
   Respuesta: [
     {"fecha": "2025-11-01", "cantidad": 5},
     {"fecha": "2025-11-02", "cantidad": 8},
     {"fecha": "2025-11-03", "cantidad": 3}
   ]

3. Top Procedimientos:
   GET /api/reportes/top-procedimientos/?limite=3
   Respuesta: [
     {"etiqueta": "Limpieza Dental", "valor": 25},
     {"etiqueta": "Endodoncia", "valor": 15},
     {"etiqueta": "Restauración", "valor": 12}
   ]

4. Reporte Financiero:
   GET /api/reportes/reporte-financiero/?periodo=2025-11
   Respuesta: {
     "periodo": "2025-11",
     "total_facturado": 30000.00,
     "total_pagado": 25000.00,
     "saldo_pendiente": 5000.00,
     "numero_facturas": 45
   }

AUTENTICACIÓN:
Todos los endpoints requieren autenticación JWT.
Incluir header: Authorization: Bearer <token>

PERMISOS:
- Todos los usuarios autenticados pueden ver reportes
- Los datos se filtran automáticamente según el tipo de usuario:
  - Admin: Ve todos los datos del tenant
  - Odontólogo: Ve datos relacionados con sus pacientes
  - Paciente: Ve solo sus datos personales (limitado)
"""
