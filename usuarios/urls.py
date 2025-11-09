from django.urls import path
from . import views

urlpatterns = [
    # --- API Endpoints ---
    # CU01: Registro de nuevo paciente
    path('register/', views.RegisterView.as_view(), name='register_paciente'),
    # Obtener información del usuario actual (con token)
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    # Listar pacientes (para selects en formularios)
    path('pacientes/', views.PacienteListView.as_view(), name='pacientes_list'),
    
    # --- Rutas de Prueba ---
    path('health/', views.health_check, name='user_health_check'),
]
