# historial_clinico/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HistorialClinicoViewSet, EpisodioAtencionViewSet,
    OdontogramaViewSet, DocumentoClinicoViewSet
)

router = DefaultRouter()
router.register(r'historiales', HistorialClinicoViewSet, basename='historial')
router.register(r'episodios', EpisodioAtencionViewSet, basename='episodio')
router.register(r'odontogramas', OdontogramaViewSet, basename='odontograma')
router.register(r'documentos', DocumentoClinicoViewSet, basename='documento')

urlpatterns = [
    path('', include(router.urls)),
]
