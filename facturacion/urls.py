# facturacion/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, PagoViewSet

# Configurar router para API REST
router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'pagos', PagoViewSet, basename='pagos')

urlpatterns = [
    # API REST endpoints (ya incluido en urls_tenant como /api/facturacion/)
    path('', include(router.urls)),
    
    # Endpoints personalizados adicionales
    path('facturas/<int:pk>/marcar-pagada/', 
         FacturaViewSet.as_view({'post': 'marcar_pagada'}), 
         name='factura-marcar-pagada'),
    
    path('facturas/<int:pk>/cancelar/', 
         FacturaViewSet.as_view({'post': 'cancelar'}), 
         name='factura-cancelar'),
    
    path('facturas/reporte-financiero/', 
         FacturaViewSet.as_view({'get': 'reporte_financiero'}), 
         name='factura-reporte-financiero'),
    
    path('pagos/<int:pk>/anular/', 
         PagoViewSet.as_view({'post': 'anular'}), 
         name='pago-anular'),
    
    path('pagos/por-factura/', 
         PagoViewSet.as_view({'get': 'por_factura'}), 
         name='pagos-por-factura'),
]

"""
Endpoints disponibles:

FACTURAS:
- GET /api/facturas/                    - Listar facturas (filtradas por usuario)
- POST /api/facturas/                   - Crear nueva factura desde presupuesto
- GET /api/facturas/{id}/               - Detalle de factura específica  
- PUT /api/facturas/{id}/               - Actualizar factura
- DELETE /api/facturas/{id}/            - Eliminar factura
- POST /api/facturas/{id}/marcar-pagada/ - Marcar como completamente pagada
- POST /api/facturas/{id}/cancelar/     - Cancelar factura (solo admin)
- GET /api/facturas/reporte-financiero/ - Reporte financiero (admin/doctor)

PAGOS:
- GET /api/pagos/                       - Listar pagos (filtrados por usuario)
- POST /api/pagos/                      - Registrar nuevo pago
- GET /api/pagos/{id}/                  - Detalle de pago específico
- PUT /api/pagos/{id}/                  - Actualizar pago
- DELETE /api/pagos/{id}/               - Eliminar pago
- POST /api/pagos/{id}/anular/          - Anular pago (solo admin)
- GET /api/pagos/por-factura/?factura_id={id} - Pagos de una factura específica

PERMISOS POR ROL:
- Admin: Acceso completo a todas las facturas y pagos del tenant
- Doctor: Ve facturas/pagos de sus pacientes solamente
- Paciente: Solo ve sus propias facturas y pagos

CASOS DE USO IMPLEMENTADOS:
- CU30: Generar factura desde presupuesto aceptado
- CU31: Registrar pagos parciales o totales
- CU32: Consultar estado de cuenta del paciente
- CU33: Generar reportes financieros
"""
