from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='usuarios-index'),
    # Ruta de salud para comprobar la conectividad de la app
    path('health/', views.health_check, name='user_health_check'),
]
