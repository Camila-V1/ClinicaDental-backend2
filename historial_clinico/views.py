# historial_clinico/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import HistorialClinico, EpisodioAtencion, Odontograma, DocumentoClinico
from .serializers import (
    HistorialClinicoSerializer, HistorialClinicoListSerializer,
    EpisodioAtencionSerializer, EpisodioAtencionCreateSerializer,
    OdontogramaSerializer, DocumentoClinicoSerializer
)
from usuarios.models import PerfilPaciente


class HistorialClinicoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar el Historial Clínico (CU08).
    """
    queryset = HistorialClinico.objects.all().prefetch_related(
        'episodios__odontologo__usuario',
        'episodios__item_plan_tratamiento__servicio',
        'odontogramas',
        'documentos',
        'paciente__usuario'
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usar serializer simplificado para listas."""
        if self.action == 'list':
            return HistorialClinicoListSerializer
        return HistorialClinicoSerializer

    def get_queryset(self):
        """
        Filtra el historial:
        - Pacientes: Solo ven su propio historial.
        - Odontólogos/Admins (staff): Ven todos los historiales.
        """
        user = self.request.user
        if not user.is_staff and user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(paciente=user.perfil_paciente)
        elif user.is_staff:
            return self.queryset
        return self.queryset.none() # Denegar por defecto

    @action(detail=False, methods=['post'])
    def crear_historial(self, request):
        """
        Crear un historial para un paciente específico.
        Solo para staff.
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Solo el personal autorizado puede crear historiales."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        paciente_id = request.data.get('paciente_id')
        if not paciente_id:
            return Response(
                {"error": "Se requiere el ID del paciente."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            paciente = PerfilPaciente.objects.get(pk=paciente_id)
        except PerfilPaciente.DoesNotExist:
            return Response(
                {"error": "Paciente no encontrado."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si ya existe un historial
        if hasattr(paciente, 'historial_clinico'):
            return Response(
                {"error": "Este paciente ya tiene un historial clínico."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el historial
        historial = HistorialClinico.objects.create(
            paciente=paciente,
            antecedentes_medicos=request.data.get('antecedentes_medicos', ''),
            alergias=request.data.get('alergias', ''),
            medicamentos_actuales=request.data.get('medicamentos_actuales', '')
        )
        
        serializer = HistorialClinicoSerializer(historial)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EpisodioAtencionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Episodios de Atención (CU09).
    """
    queryset = EpisodioAtencion.objects.all().select_related(
        'historial_clinico__paciente__usuario',
        'odontologo__usuario',
        'odontologo__especialidad',
        'item_plan_tratamiento__servicio'
    )
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar serializer específico para creación."""
        if self.action in ['create', 'update', 'partial_update']:
            return EpisodioAtencionCreateSerializer
        return EpisodioAtencionSerializer
    
    def get_queryset(self):
        """
        Filtra episodios:
        - Pacientes: Solo ven episodios de su propio historial.
        - Odontólogos/Admins (staff): Ven todos.
        """
        user = self.request.user
        if not user.is_staff and user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff:
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        """
        Si el que crea es un Odontólogo, se auto-asigna.
        """
        if self.request.user.tipo_usuario == 'ODONTOLOGO' and hasattr(self.request.user, 'perfil_odontologo'):
            serializer.save(odontologo=self.request.user.perfil_odontologo)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def mis_episodios(self, request):
        """
        Obtener episodios donde el odontólogo logueado fue el que atendió.
        Solo para odontólogos.
        """
        if request.user.tipo_usuario != 'ODONTOLOGO' or not hasattr(request.user, 'perfil_odontologo'):
            return Response(
                {"error": "Solo los odontólogos pueden acceder a sus episodios."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        episodios = self.queryset.filter(odontologo=request.user.perfil_odontologo)
        serializer = self.get_serializer(episodios, many=True)
        return Response(serializer.data)


class OdontogramaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Odontogramas (CU10).
    """
    queryset = Odontograma.objects.all().select_related('historial_clinico__paciente__usuario')
    serializer_class = OdontogramaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_staff and user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff:
            return self.queryset
        return self.queryset.none()

    @action(detail=True, methods=['post'])
    def duplicar_odontograma(self, request, pk=None):
        """
        Crear una copia del odontograma actual como nueva versión.
        Útil para hacer seguimiento de la evolución.
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Solo el personal autorizado puede duplicar odontogramas."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        odontograma_original = self.get_object()
        
        # Crear nueva instancia con los mismos datos
        nuevo_odontograma = Odontograma.objects.create(
            historial_clinico=odontograma_original.historial_clinico,
            estado_piezas=odontograma_original.estado_piezas.copy(),
            notas=f"Copia de odontograma del {odontograma_original.fecha_snapshot.strftime('%Y-%m-%d')}"
        )
        
        serializer = self.get_serializer(nuevo_odontograma)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentoClinicoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Documentos Clínicos (CU11).
    """
    queryset = DocumentoClinico.objects.all().select_related('historial_clinico__paciente__usuario')
    serializer_class = DocumentoClinicoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_staff and user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff:
            return self.queryset
        return self.queryset.none()

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """
        Filtrar documentos por tipo.
        """
        tipo_documento = request.query_params.get('tipo')
        if not tipo_documento:
            return Response(
                {"error": "Se requiere el parámetro 'tipo'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        documentos = self.get_queryset().filter(tipo_documento=tipo_documento)
        serializer = self.get_serializer(documentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """
        Endpoint para descargar el archivo del documento.
        """
        documento = self.get_object()
        
        if not documento.archivo:
            return Response(
                {"error": "Este documento no tiene archivo adjunto."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Aquí podrías implementar lógica adicional de seguridad
        # Por ahora, devolvemos la URL del archivo
        return Response({
            "url": documento.archivo.url,
            "nombre": documento.descripcion,
            "tipo": documento.get_tipo_documento_display()
        })
