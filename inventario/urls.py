"""
URLs de la API de Inventario.

Endpoints disponibles:

Categorías:
- GET    /api/inventario/categorias/         - Listar categorías
- POST   /api/inventario/categorias/         - Crear categoría
- GET    /api/inventario/categorias/{id}/    - Ver detalle
- PUT    /api/inventario/categorias/{id}/    - Actualizar
- DELETE /api/inventario/categorias/{id}/    - Eliminar

Insumos:
- GET    /api/inventario/insumos/                  - Listar insumos
- POST   /api/inventario/insumos/                  - Crear insumo
- GET    /api/inventario/insumos/{id}/             - Ver detalle
- PUT    /api/inventario/insumos/{id}/             - Actualizar
- DELETE /api/inventario/insumos/{id}/             - Eliminar
- GET    /api/inventario/insumos/bajo_stock/       - Insumos con stock bajo
- POST   /api/inventario/insumos/{id}/ajustar_stock/ - Ajustar stock

Todos los endpoints requieren autenticación JWT.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categorias', views.CategoriaInsumoViewSet, basename='categoria-insumo')
router.register(r'insumos', views.InsumoViewSet, basename='insumo')

urlpatterns = [
    path('', include(router.urls)),
]
