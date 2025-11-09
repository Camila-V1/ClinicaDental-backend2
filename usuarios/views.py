from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .serializers import RegisterSerializer, UsuarioSerializer, PacienteListSerializer
from .models import Usuario


# --- VISTAS DE API (CU01, CU02) ---

class RegisterView(generics.CreateAPIView):
    """
    Endpoint para registrar un nuevo PACIENTE (CU01).
    Es público, no requiere token.
    
    POST /api/usuarios/register/
    Body: {
        "email": "paciente@example.com",
        "password": "password123",
        "password2": "password123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "fecha_de_nacimiento": "1990-01-15",
        "direccion": "Calle Principal 123"
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # Vista pública
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'usuario': {
                'id': usuario.id,
                'email': usuario.email,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'tipo_usuario': usuario.tipo_usuario
            }
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(generics.RetrieveAPIView):
    """
    Endpoint para obtener los datos del usuario que está logueado (con token).
    Requiere autenticación JWT.
    
    GET /api/usuarios/me/
    Headers: Authorization: Bearer <token>
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Devuelve el usuario que está haciendo la petición (identificado por el token)
        return self.request.user


class PacienteListView(generics.ListAPIView):
    """
    Vista para listar pacientes (sin paginación).
    Usado para selects y dropdowns en formularios.
    
    GET /api/usuarios/pacientes/
    Responde con un array directo: [{"id": 1, "nombre": "Juan", ...}, ...]
    """
    serializer_class = PacienteListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Desactivar paginación
    
    def get_queryset(self):
        # Solo devolver usuarios de tipo PACIENTE activos
        return Usuario.objects.filter(tipo_usuario='PACIENTE', is_active=True).order_by('nombre', 'apellido')


# --- VISTAS DE PRUEBA ---

def index(request):
	return JsonResponse({"status": "ok", "app": "usuarios"})


def health_check(request):
	"""
	Una vista simple para confirmar que la app 'usuarios' está conectada.
	"""
	return JsonResponse({"status": "ok", "app": "usuarios"})
