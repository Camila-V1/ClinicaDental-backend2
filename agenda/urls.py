from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

# Crear router para registrar viewsets
router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')

# Las URLs generadas automáticamente por el router:
# GET    /api/agenda/citas/          -> list (lista todas las citas)
# POST   /api/agenda/citas/          -> create (crear nueva cita)
# GET    /api/agenda/citas/{id}/     -> retrieve (detalle de una cita)
# PUT    /api/agenda/citas/{id}/     -> update (actualizar cita completa)
# PATCH  /api/agenda/citas/{id}/     -> partial_update (actualizar parcial)
# DELETE /api/agenda/citas/{id}/     -> destroy (eliminar cita)
#
# Custom actions:
# GET    /api/agenda/citas/proximas/ -> proximas (citas futuras)
# GET    /api/agenda/citas/hoy/      -> hoy (citas de hoy)
# POST   /api/agenda/citas/{id}/confirmar/ -> confirmar cita
# POST   /api/agenda/citas/{id}/cancelar/  -> cancelar cita
# POST   /api/agenda/citas/{id}/atender/   -> atender cita

urlpatterns = [
    path('', include(router.urls)),
]
