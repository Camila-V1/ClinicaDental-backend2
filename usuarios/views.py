from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .serializers import RegisterSerializer, UsuarioSerializer, PacienteListSerializer
from .models import Usuario, PerfilOdontologo
from reportes.models import BitacoraAccion


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
        
        # Registrar en bitácora
        BitacoraAccion.registrar(
            usuario=None,  # Registro público
            accion='CREAR',
            descripcion=f'Nuevo paciente registrado: {usuario.nombre} {usuario.apellido} ({usuario.email})',
            content_object=usuario,
            detalles={'email': usuario.email, 'tipo': 'PACIENTE'}
        )
        
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


class DashboardPacienteView(generics.GenericAPIView):
    """
    Endpoint para obtener el dashboard del paciente con resumen de datos.
    Requiere autenticación JWT.
    
    GET /api/usuarios/dashboard/
    Headers: Authorization: Bearer <token>
    
    Retorna:
    - proximas_citas: número de citas próximas
    - tratamientos_activos: número de tratamientos en progreso
    - saldo_pendiente: monto total pendiente de pago
    - proxima_cita: datos de la próxima cita si existe
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from django.utils import timezone
        from agenda.models import Cita
        from tratamientos.models import PlanDeTratamiento
        from facturacion.models import Factura
        from datetime import timedelta
        
        usuario = request.user
        
        # Solo pacientes pueden ver su dashboard
        if usuario.tipo_usuario != 'PACIENTE':
            return Response({
                'error': 'Solo pacientes pueden acceder a este endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el usuario tenga perfil de paciente
        try:
            perfil_paciente = usuario.perfil_paciente
        except:
            return Response({
                'error': 'Usuario no tiene perfil de paciente'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener próximas citas (futuras, pendientes o confirmadas)
        ahora = timezone.now()
        proximas_citas = Cita.objects.filter(
            paciente=perfil_paciente,
            fecha_hora__gte=ahora,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).count()
        
        # Obtener tratamientos activos
        tratamientos_activos = PlanDeTratamiento.objects.filter(
            paciente=perfil_paciente,
            estado='en_progreso'
        ).count()
        
        # Calcular saldo pendiente
        from django.db.models import Sum
        saldo_pendiente = Factura.objects.filter(
            paciente=perfil_paciente,
            estado='PENDIENTE'
        ).aggregate(
            total=Sum('monto_total')
        )['total'] or 0
        
        # Obtener la próxima cita más cercana
        proxima_cita_obj = Cita.objects.filter(
            paciente=perfil_paciente,
            fecha_hora__gte=ahora,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).order_by('fecha_hora').first()
        
        proxima_cita = None
        if proxima_cita_obj:
            odontologo_data = None
            if proxima_cita_obj.odontologo:
                odontologo_user = proxima_cita_obj.odontologo.usuario
                odontologo_data = {
                    'id': odontologo_user.id,
                    'nombre_completo': f"{odontologo_user.nombre} {odontologo_user.apellido}"
                }
            
            proxima_cita = {
                'id': proxima_cita_obj.id,
                'fecha_hora': proxima_cita_obj.fecha_hora,
                'motivo_tipo': proxima_cita_obj.motivo_tipo,
                'estado': proxima_cita_obj.estado,
                'odontologo': odontologo_data,
                'motivo': proxima_cita_obj.motivo
            }
        
        return Response({
            'proximas_citas': proximas_citas,
            'tratamientos_activos': tratamientos_activos,
            'saldo_pendiente': float(saldo_pendiente),
            'proxima_cita': proxima_cita
        }, status=status.HTTP_200_OK)


class PacienteListView(generics.ListAPIView):
    """
    Vista para listar pacientes (sin paginación).
    Usado para selects y dropdowns en formularios.
    
    GET /api/usuarios/pacientes/
    Query params opcionales:
    - is_active: 'true' | 'false' | '' (vacío = todos)
    - search: búsqueda por nombre, apellido o email
    
    Responde con un array directo: [{"id": 1, "nombre": "Juan", ...}, ...]
    """
    serializer_class = PacienteListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Desactivar paginación
    
    def get_queryset(self):
        queryset = Usuario.objects.filter(tipo_usuario='PACIENTE')
        
        # Filtro por is_active (query param)
        is_active_param = self.request.query_params.get('is_active', None)
        if is_active_param == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active_param == 'false':
            queryset = queryset.filter(is_active=False)
        # Si is_active_param es '' o None, no filtrar (devolver todos)
        
        # Filtro de búsqueda (opcional)
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('nombre', 'apellido')


class OdontologoListView(generics.ListAPIView):
    """
    Vista para listar odontólogos disponibles.
    Usado para selects al agendar citas.
    
    GET /api/usuarios/odontologos/
    Query params opcionales:
    - is_active: 'true' | 'false' | '' (vacío = todos)
    - search: búsqueda por nombre, apellido o email
    
    Responde con un array: [{"id": 103, "nombre": "Juan", "apellido": "Pérez", ...}, ...]
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Sin paginación
    
    def get(self, request, *args, **kwargs):
        # Filtrar por tipo ODONTOLOGO
        odontologos = Usuario.objects.filter(tipo_usuario='ODONTOLOGO')
        
        # Filtro por is_active (query param)
        is_active_param = request.query_params.get('is_active', None)
        if is_active_param == 'true':
            odontologos = odontologos.filter(is_active=True)
        elif is_active_param == 'false':
            odontologos = odontologos.filter(is_active=False)
        # Si is_active_param es '' o None, no filtrar (devolver todos)
        
        # Filtro de búsqueda (opcional)
        search = request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            odontologos = odontologos.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(email__icontains=search)
            )
        
        odontologos = odontologos.select_related('perfil_odontologo').order_by('nombre', 'apellido')
        
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
                
                # Extraer especialidad del texto de experiencia si existe
                especialidad_extraida = None
                if perfil.especialidad:
                    especialidad_extraida = perfil.especialidad.nombre
                elif perfil.experienciaProfesional and 'Especialidad:' in perfil.experienciaProfesional:
                    # Extraer "Odontología General" de "Especialidad: Odontología General. 5 años..."
                    inicio = perfil.experienciaProfesional.find('Especialidad:') + len('Especialidad:')
                    fin = perfil.experienciaProfesional.find('.', inicio)
                    if fin > inicio:
                        especialidad_extraida = perfil.experienciaProfesional[inicio:fin].strip()
                
                odontologo_data.update({
                    'especialidad': especialidad_extraida,
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
	try:
		usuario = Usuario.objects.get(email='odontologo@clinica-demo.com')
		
		cambios = []
		
		if usuario.tipo_usuario != 'ODONTOLOGO':
			usuario.tipo_usuario = 'ODONTOLOGO'
			cambios.append("tipo_usuario → ODONTOLOGO")
		
		if not usuario.is_active:
			usuario.is_active = True
			cambios.append("is_active → True")
		
		if cambios:
			usuario.save()
		
		# Actualizar o crear perfil de odontólogo
		if hasattr(usuario, 'perfil_odontologo'):
			perfil = usuario.perfil_odontologo
			
			if not perfil.cedulaProfesional:
				perfil.cedulaProfesional = "12345678"
				cambios.append("cedulaProfesional → 12345678")
				perfil.save()
			
			if not perfil.experienciaProfesional:
				perfil.experienciaProfesional = "5 años de experiencia en odontología general"
				cambios.append("experienciaProfesional → Agregada")
				perfil.save()
		else:
			# Crear perfil si no existe
			PerfilOdontologo.objects.create(
				usuario=usuario,
				cedulaProfesional="12345678",
				experienciaProfesional="5 años de experiencia en odontología general"
			)
			cambios.append("Perfil de odontólogo creado")
		
		# Refrescar el objeto para obtener los datos actualizados
		usuario.refresh_from_db()
		
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
				"cedula": usuario.perfil_odontologo.cedulaProfesional if hasattr(usuario, 'perfil_odontologo') else None,
				"experiencia": usuario.perfil_odontologo.experienciaProfesional if hasattr(usuario, 'perfil_odontologo') else None
			}
		})
	
	except Usuario.DoesNotExist:
		return JsonResponse({
			"status": "error",
			"message": "Usuario no encontrado"
		}, status=404)
	except Exception as e:
		return JsonResponse({
			"status": "error",
			"message": f"Error al actualizar: {str(e)}"
		}, status=500)


def poblar_especialidades(request):
	"""
	Endpoint temporal para poblar especialidades y asignar al odontólogo.
	PÚBLICO - No requiere autenticación (solo para setup inicial)
	"""
	from tratamientos.models import CategoriaServicio
	
	try:
		# Crear categorías de servicio (que funcionan como especialidades)
		categorias_data = [
			{'nombre': 'Odontología General', 'descripcion': 'Atención dental integral y preventiva'},
			{'nombre': 'Ortodoncia', 'descripcion': 'Corrección de malposiciones dentales y maxilares'},
			{'nombre': 'Endodoncia', 'descripcion': 'Tratamiento de conductos radiculares'},
			{'nombre': 'Periodoncia', 'descripcion': 'Tratamiento de enfermedades de las encías'},
			{'nombre': 'Cirugía Oral', 'descripcion': 'Procedimientos quirúrgicos en boca y maxilares'},
			{'nombre': 'Odontopediatría', 'descripcion': 'Odontología especializada en niños'},
			{'nombre': 'Implantología', 'descripcion': 'Colocación de implantes dentales'},
			{'nombre': 'Estética Dental', 'descripcion': 'Tratamientos de embellecimiento dental'}
		]
		
		categorias_creadas = []
		categorias_existentes = []
		
		for idx, cat_data in enumerate(categorias_data, start=1):
			categoria, created = CategoriaServicio.objects.get_or_create(
				nombre=cat_data['nombre'],
				defaults={
					'descripcion': cat_data['descripcion'],
					'activo': True,
					'orden': idx
				}
			)
			
			if created:
				categorias_creadas.append(categoria.nombre)
			else:
				categorias_existentes.append(categoria.nombre)
		
		# Actualizar perfil del odontólogo con especialidad en descripción
		usuario = Usuario.objects.get(email='odontologo@clinica-demo.com')
		especialidad_texto = "Odontología General"
		
		if hasattr(usuario, 'perfil_odontologo'):
			perfil = usuario.perfil_odontologo
			# Guardar la especialidad como texto en experienciaProfesional
			if not perfil.experienciaProfesional or 'Especialidad' not in perfil.experienciaProfesional:
				perfil.experienciaProfesional = f"Especialidad: {especialidad_texto}. 5 años de experiencia en odontología general"
				perfil.save()
		
		return JsonResponse({
			"status": "success",
			"message": "Categorías de servicio pobladas exitosamente",
			"categorias_creadas": categorias_creadas,
			"categorias_existentes": categorias_existentes,
			"total_categorias": CategoriaServicio.objects.count(),
			"odontologo": {
				"email": usuario.email,
				"especialidad": especialidad_texto
			}
		})
	
	except Usuario.DoesNotExist:
		return JsonResponse({
			"status": "error",
			"message": "Usuario odontólogo no encontrado"
		}, status=404)
	except Exception as e:
		return JsonResponse({
			"status": "error",
			"message": f"Error al poblar especialidades: {str(e)}"
		}, status=500)
