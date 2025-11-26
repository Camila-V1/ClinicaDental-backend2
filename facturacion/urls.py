# facturacion/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, PagoViewSet
from .views_pagos import PagoViewSet as PagoStripeViewSet

# Configurar router para API REST
router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'pagos', PagoStripeViewSet, basename='pagos')  # Actualizado para usar views_pagos

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
]

"""
Endpoints disponibles:

FACTURAS:
- GET /api/facturacion/facturas/                    - Listar facturas
- POST /api/facturacion/facturas/                   - Crear factura
- GET /api/facturacion/facturas/{id}/               - Detalle de factura  
- PUT /api/facturacion/facturas/{id}/               - Actualizar factura
- DELETE /api/facturacion/facturas/{id}/            - Eliminar factura
- POST /api/facturacion/facturas/{id}/marcar-pagada/ - Marcar como pagada
- POST /api/facturacion/facturas/{id}/cancelar/     - Cancelar factura
- GET /api/facturacion/facturas/reporte-financiero/ - Reporte financiero

PAGOS CON STRIPE:
- POST /api/facturacion/pagos/crear-pago-cita/      - Crear pago para cita
- POST /api/facturacion/pagos/crear-pago-tratamiento/ - Crear pago para tratamiento
- POST /api/facturacion/pagos/crear-pago-plan/      - Crear pago para plan
- POST /api/facturacion/pagos/{id}/confirmar/       - Confirmar pago (webhook)
- GET /api/facturacion/pagos/{id}/estado/           - Verificar estado de pago
- GET /api/facturacion/pagos/                       - Listar historial de pagos

CASOS DE USO:
- CU30: Generar factura desde presupuesto
- CU31: Registrar pagos (efectivo, tarjeta, online)
- CU32: Consultar estado de cuenta
- CU33: Generar reportes financieros
- NUEVO: Pagos online con Stripe para citas y tratamientos
"""
