from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .serializers import RegisterSerializer, UsuarioSerializer, PacienteListSerializer
from .models import Usuario, PerfilOdontologo


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


class OdontologoListView(generics.ListAPIView):
    """
    Vista para listar odontólogos disponibles.
    Usado para selects al agendar citas.
    
    GET /api/usuarios/odontologos/
    Responde con un array: [{"id": 103, "nombre": "Juan", "apellido": "Pérez", ...}, ...]
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Sin paginación
    
    def get(self, request, *args, **kwargs):
        # Obtener solo usuarios ODONTOLOGO activos
        odontologos = Usuario.objects.filter(
            tipo_usuario='ODONTOLOGO',
            is_active=True
        ).select_related('perfil_odontologo').order_by('nombre', 'apellido')
        
        # Serializar manualmente para incluir datos del perfil
        data = []
        for odontologo in odontologos:
            odontologo_data = {
                'id': odontologo.id,
                'email': odontologo.email,
                'nombre': odontologo.nombre,
                'apellido': odontologo.apellido,
                'nombre_completo': f"{odontologo.nombre} {odontologo.apellido}",
                'tipo_usuario': odontologo.tipo_usuario,
                'is_active': odontologo.is_active,
                'telefono': odontologo.telefono,
            }
            
            # Agregar datos del perfil si existe
            if hasattr(odontologo, 'perfil_odontologo'):
                perfil = odontologo.perfil_odontologo
                odontologo_data.update({
                    'especialidad': perfil.especialidad.nombre if perfil.especialidad else None,
                    'cedula_profesional': perfil.cedulaProfesional,
                    'experiencia': perfil.experienciaProfesional,
                })
            
            data.append(odontologo_data)
        
        return Response(data, status=status.HTTP_200_OK)


# --- VISTAS DE PRUEBA ---

def index(request):
	return JsonResponse({"status": "ok", "app": "usuarios"})


def health_check(request):
	"""
	Una vista simple para confirmar que la app 'usuarios' está conectada.
	"""
	return JsonResponse({"status": "ok", "app": "usuarios"})


def fix_odontologo(request):
	"""
	Endpoint temporal para corregir el odontólogo en Render.
	Cambia tipo_usuario a ODONTOLOGO y lo activa.
	PÚBLICO - No requiere autenticación (solo para corrección inicial)
	"""
	from django.views.decorators.csrf import csrf_exempt
	from tratamientos.models import Especialidad
	
	try:
		usuario = Usuario.objects.get(email='odontologo@clinica-demo.com')
		
		cambios = []
		estado_anterior = {
			'tipo_usuario': usuario.tipo_usuario,
			'is_active': usuario.is_active
		}
		
		if usuario.tipo_usuario != 'ODONTOLOGO':
			usuario.tipo_usuario = 'ODONTOLOGO'
			cambios.append("tipo_usuario → ODONTOLOGO")
		
		if not usuario.is_active:
			usuario.is_active = True
			cambios.append("is_active → True")
		
		if cambios:
			usuario.save()
		
		# Actualizar o crear perfil de odontólogo
		perfil_actualizado = False
		if hasattr(usuario, 'perfil_odontologo'):
			perfil = usuario.perfil_odontologo
			
			# Buscar o crear especialidad "Odontología General"
			especialidad, _ = Especialidad.objects.get_or_create(
				nombre="Odontología General",
				defaults={'descripcion': 'Especialidad general en odontología'}
			)
			
			if not perfil.especialidad:
				perfil.especialidad = especialidad
				cambios.append("especialidad → Odontología General")
				perfil_actualizado = True
			
			if not perfil.cedulaProfesional:
				perfil.cedulaProfesional = "12345678"
				cambios.append("cedulaProfesional → 12345678")
				perfil_actualizado = True
			
			if not perfil.experienciaProfesional:
				perfil.experienciaProfesional = "5 años de experiencia en odontología general"
				cambios.append("experienciaProfesional → Agregada")
				perfil_actualizado = True
			
			if perfil_actualizado:
				perfil.save()
		else:
			# Crear perfil si no existe
			especialidad, _ = Especialidad.objects.get_or_create(
				nombre="Odontología General",
				defaults={'descripcion': 'Especialidad general en odontología'}
			)
			
			PerfilOdontologo.objects.create(
				usuario=usuario,
				especialidad=especialidad,
				cedulaProfesional="12345678",
				experienciaProfesional="5 años de experiencia en odontología general"
			)
			cambios.append("Perfil de odontólogo creado")
		
		return JsonResponse({
			"status": "success",
			"message": "Usuario y perfil actualizados exitosamente",
			"usuario_id": usuario.id,
			"email": usuario.email,
			"cambios_aplicados": cambios if cambios else ["Sin cambios necesarios"],
			"estado_actual": {
				"tipo_usuario": usuario.tipo_usuario,
				"is_active": usuario.is_active,
				"tiene_perfil": hasattr(usuario, 'perfil_odontologo'),
				"especialidad": usuario.perfil_odontologo.especialidad.nombre if hasattr(usuario, 'perfil_odontologo') and usuario.perfil_odontologo.especialidad else None,
				"cedula": usuario.perfil_odontologo.cedulaProfesional if hasattr(usuario, 'perfil_odontologo') else None
			}
		})
	
	except Usuario.DoesNotExist:
		return JsonResponse({
			"status": "error",
			"message": "Usuario no encontrado"
		}, status=404)
