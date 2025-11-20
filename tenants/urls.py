from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para las APIs REST
router = DefaultRouter()
router.register(r'planes', views.PlanSuscripcionViewSet, basename='plan-suscripcion')
router.register(r'solicitudes', views.SolicitudRegistroViewSet, basename='solicitud-registro')

urlpatterns = [
    # Vista principal del índice
    path('', views.index, name='tenants-index'),
    
    # Endpoint informativo público
    path('registro/info/', views.info_registro, name='info-registro'),
    
    # APIs REST (las rutas del router)
    path('', include(router.urls)),
]
