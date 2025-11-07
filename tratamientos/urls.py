from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar rutas de API REST con DefaultRouter
router = DefaultRouter()
router.register(r'categorias', views.CategoriaServicioViewSet, basename='categoria-servicio')
router.register(r'servicios', views.ServicioViewSet, basename='servicio')

# ¡PASO 2.C! - Endpoints para el sistema de precio dinámico
router.register(r'planes', views.PlanDeTratamientoViewSet, basename='plan-tratamiento')
router.register(r'items', views.ItemPlanTratamientoViewSet, basename='item-plan')

# ¡PASO 2.D! - Endpoints para presupuestos (CU20, CU21)
router.register(r'presupuestos', views.PresupuestoViewSet, basename='presupuesto')

urlpatterns = [
    # Vista de prueba/health check
    path('', views.index, name='tratamientos-index'),
    
    # API REST endpoints
    path('', include(router.urls)),
]
