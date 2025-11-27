from django.urls import path
from . import views

urlpatterns = [
    # --- API Endpoints ---
    # CU01: Registro de nuevo paciente
    path('register/', views.RegisterView.as_view(), name='register_paciente'),
    # Obtener información del usuario actual (con token)
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    # Dashboard del paciente
    path('dashboard/', views.DashboardPacienteView.as_view(), name='dashboard_paciente'),
    # Listar pacientes (para selects en formularios)
    path('pacientes/', views.PacienteListView.as_view(), name='pacientes_list'),
    # Listar odontólogos (para agendar citas)
    path('odontologos/', views.OdontologoListView.as_view(), name='odontologos_list'),
    
    # --- Rutas de Prueba ---
    path('health/', views.health_check, name='user_health_check'),
    path('fix-odontologo/', views.fix_odontologo, name='fix_odontologo'),
    path('poblar-especialidades/', views.poblar_especialidades, name='poblar_especialidades'),
    
    # --- Notificaciones Push ---
    path('registrar-fcm-token/', views.registrar_fcm_token, name='registrar_fcm_token'),
]
