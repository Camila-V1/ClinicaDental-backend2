# historial_clinico/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404

from .models import HistorialClinico, EpisodioAtencion, Odontograma, DocumentoClinico
from .serializers import (
    HistorialClinicoSerializer, HistorialClinicoListSerializer,
    EpisodioAtencionSerializer, EpisodioAtencionCreateSerializer,
    OdontogramaSerializer, DocumentoClinicoSerializer
)
from usuarios.models import PerfilPaciente
import os
import mimetypes


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
        - Odontólogos/Admins (staff o ODONTOLOGO): Ven todos los historiales.
        """
        user = self.request.user
        if user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(paciente=user.perfil_paciente)
        elif user.is_staff or user.tipo_usuario in ['ODONTOLOGO', 'ADMIN']:
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

    @action(detail=False, methods=['get'])
    def mi_historial(self, request):
        """
        GET /api/historial/historiales/mi_historial/
        
        Obtener el historial clínico completo del paciente autenticado.
        Solo para PACIENTES.
        """
        # Verificar que el usuario sea paciente
        if request.user.tipo_usuario != 'PACIENTE' or not hasattr(request.user, 'perfil_paciente'):
            return Response(
                {'error': 'Solo los pacientes pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el historial del paciente
        try:
            historial = HistorialClinico.objects.prefetch_related(
                'episodios__odontologo__usuario',
                'episodios__item_plan_tratamiento__servicio',
                'odontogramas',
                'documentos'
            ).get(paciente=request.user.perfil_paciente)
            
            serializer = HistorialClinicoSerializer(historial)
            return Response(serializer.data)
            
        except HistorialClinico.DoesNotExist:
            return Response(
                {'error': 'No se encontró historial clínico para este paciente'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        """
        Listar documentos de un historial específico.
        GET /api/historial/historiales/{id}/documentos/
        """
        historial = self.get_object()
        documentos = historial.documentos.all()
        
        # Filtrar por tipo si se proporciona
        tipo = request.query_params.get('tipo')
        if tipo:
            documentos = documentos.filter(tipo_documento=tipo)
        
        serializer = DocumentoClinicoSerializer(documentos, many=True)
        return Response(serializer.data)


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
        - Odontólogos/Admins: Ven todos.
        """
        user = self.request.user
        if user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff or user.tipo_usuario in ['ODONTOLOGO', 'ADMIN']:
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
    
    def create(self, request, *args, **kwargs):
        """
        Override create para devolver el episodio completo con todos los campos.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Obtener el episodio recién creado con el serializer completo
        episodio = serializer.instance
        output_serializer = EpisodioAtencionSerializer(episodio)
        
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def mis_episodios(self, request):
        """
        Obtener episodios según el tipo de usuario:
        - Odontólogos: episodios donde fueron el doctor
        - Pacientes: episodios de su historial clínico
        """
        if request.user.tipo_usuario == 'ODONTOLOGO' and hasattr(request.user, 'perfil_odontologo'):
            episodios = self.queryset.filter(odontologo=request.user.perfil_odontologo)
        elif request.user.tipo_usuario == 'PACIENTE' and hasattr(request.user, 'perfil_paciente'):
            episodios = self.queryset.filter(historial_clinico__paciente=request.user.perfil_paciente)
        else:
            return Response(
                {"error": "Usuario sin perfil de paciente u odontólogo."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
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
        if user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff or user.tipo_usuario in ['ODONTOLOGO', 'ADMIN']:
            return self.queryset
        return self.queryset.none()

    @action(detail=False, methods=['get'])
    def configuracion(self, request):
        """
        GET /api/historial/odontogramas/configuracion/
        
        Retorna la estructura completa del odontograma para el frontend.
        Incluye: cuadrantes, dientes, estados disponibles, colores, etc.
        """
        return Response({
            "nomenclatura": "FDI",
            "sistema": "Internacional (FDI)",
            "total_dientes_adulto": 32,
            "total_dientes_nino": 20,
            
            # Configuración de cuadrantes para adultos
            "cuadrantes": {
                "1": {
                    "numero": 1,
                    "nombre": "Superior Derecho",
                    "nombre_corto": "SD",
                    "posicion": "top-right",
                    "arcada": "superior",
                    "lado": "derecho",
                    "dientes": [
                        {"numero": "18", "nombre": "Tercer Molar", "nombre_corto": "3M", "posicion": 8, "tipo": "molar"},
                        {"numero": "17", "nombre": "Segundo Molar", "nombre_corto": "2M", "posicion": 7, "tipo": "molar"},
                        {"numero": "16", "nombre": "Primer Molar", "nombre_corto": "1M", "posicion": 6, "tipo": "molar"},
                        {"numero": "15", "nombre": "Segundo Premolar", "nombre_corto": "2PM", "posicion": 5, "tipo": "premolar"},
                        {"numero": "14", "nombre": "Primer Premolar", "nombre_corto": "1PM", "posicion": 4, "tipo": "premolar"},
                        {"numero": "13", "nombre": "Canino", "nombre_corto": "C", "posicion": 3, "tipo": "canino"},
                        {"numero": "12", "nombre": "Incisivo Lateral", "nombre_corto": "IL", "posicion": 2, "tipo": "incisivo"},
                        {"numero": "11", "nombre": "Incisivo Central", "nombre_corto": "IC", "posicion": 1, "tipo": "incisivo"}
                    ]
                },
                "2": {
                    "numero": 2,
                    "nombre": "Superior Izquierdo",
                    "nombre_corto": "SI",
                    "posicion": "top-left",
                    "arcada": "superior",
                    "lado": "izquierdo",
                    "dientes": [
                        {"numero": "21", "nombre": "Incisivo Central", "nombre_corto": "IC", "posicion": 1, "tipo": "incisivo"},
                        {"numero": "22", "nombre": "Incisivo Lateral", "nombre_corto": "IL", "posicion": 2, "tipo": "incisivo"},
                        {"numero": "23", "nombre": "Canino", "nombre_corto": "C", "posicion": 3, "tipo": "canino"},
                        {"numero": "24", "nombre": "Primer Premolar", "nombre_corto": "1PM", "posicion": 4, "tipo": "premolar"},
                        {"numero": "25", "nombre": "Segundo Premolar", "nombre_corto": "2PM", "posicion": 5, "tipo": "premolar"},
                        {"numero": "26", "nombre": "Primer Molar", "nombre_corto": "1M", "posicion": 6, "tipo": "molar"},
                        {"numero": "27", "nombre": "Segundo Molar", "nombre_corto": "2M", "posicion": 7, "tipo": "molar"},
                        {"numero": "28", "nombre": "Tercer Molar", "nombre_corto": "3M", "posicion": 8, "tipo": "molar"}
                    ]
                },
                "3": {
                    "numero": 3,
                    "nombre": "Inferior Izquierdo",
                    "nombre_corto": "II",
                    "posicion": "bottom-left",
                    "arcada": "inferior",
                    "lado": "izquierdo",
                    "dientes": [
                        {"numero": "31", "nombre": "Incisivo Central", "nombre_corto": "IC", "posicion": 1, "tipo": "incisivo"},
                        {"numero": "32", "nombre": "Incisivo Lateral", "nombre_corto": "IL", "posicion": 2, "tipo": "incisivo"},
                        {"numero": "33", "nombre": "Canino", "nombre_corto": "C", "posicion": 3, "tipo": "canino"},
                        {"numero": "34", "nombre": "Primer Premolar", "nombre_corto": "1PM", "posicion": 4, "tipo": "premolar"},
                        {"numero": "35", "nombre": "Segundo Premolar", "nombre_corto": "2PM", "posicion": 5, "tipo": "premolar"},
                        {"numero": "36", "nombre": "Primer Molar", "nombre_corto": "1M", "posicion": 6, "tipo": "molar"},
                        {"numero": "37", "nombre": "Segundo Molar", "nombre_corto": "2M", "posicion": 7, "tipo": "molar"},
                        {"numero": "38", "nombre": "Tercer Molar", "nombre_corto": "3M", "posicion": 8, "tipo": "molar"}
                    ]
                },
                "4": {
                    "numero": 4,
                    "nombre": "Inferior Derecho",
                    "nombre_corto": "ID",
                    "posicion": "bottom-right",
                    "arcada": "inferior",
                    "lado": "derecho",
                    "dientes": [
                        {"numero": "48", "nombre": "Tercer Molar", "nombre_corto": "3M", "posicion": 8, "tipo": "molar"},
                        {"numero": "47", "nombre": "Segundo Molar", "nombre_corto": "2M", "posicion": 7, "tipo": "molar"},
                        {"numero": "46", "nombre": "Primer Molar", "nombre_corto": "1M", "posicion": 6, "tipo": "molar"},
                        {"numero": "45", "nombre": "Segundo Premolar", "nombre_corto": "2PM", "posicion": 5, "tipo": "premolar"},
                        {"numero": "44", "nombre": "Primer Premolar", "nombre_corto": "1PM", "posicion": 4, "tipo": "premolar"},
                        {"numero": "43", "nombre": "Canino", "nombre_corto": "C", "posicion": 3, "tipo": "canino"},
                        {"numero": "42", "nombre": "Incisivo Lateral", "nombre_corto": "IL", "posicion": 2, "tipo": "incisivo"},
                        {"numero": "41", "nombre": "Incisivo Central", "nombre_corto": "IC", "posicion": 1, "tipo": "incisivo"}
                    ]
                }
            },
            
            # Estados disponibles para las piezas dentales
            "estados": [
                {
                    "valor": "sano",
                    "etiqueta": "Sano",
                    "color": "#10b981",
                    "color_fondo": "#d1fae5",
                    "icono": "✓",
                    "descripcion": "Diente sin patologías"
                },
                {
                    "valor": "caries",
                    "etiqueta": "Caries",
                    "color": "#ef4444",
                    "color_fondo": "#fee2e2",
                    "icono": "⚠",
                    "descripcion": "Diente con caries activa"
                },
                {
                    "valor": "tratado",
                    "etiqueta": "Tratado",
                    "color": "#f59e0b",
                    "color_fondo": "#fef3c7",
                    "icono": "◆",
                    "descripcion": "Diente en tratamiento"
                },
                {
                    "valor": "restaurado",
                    "etiqueta": "Restaurado",
                    "color": "#3b82f6",
                    "color_fondo": "#dbeafe",
                    "icono": "■",
                    "descripcion": "Diente con obturación/restauración"
                },
                {
                    "valor": "endodoncia",
                    "etiqueta": "Endodoncia",
                    "color": "#8b5cf6",
                    "color_fondo": "#ede9fe",
                    "icono": "◉",
                    "descripcion": "Tratamiento de conducto realizado"
                },
                {
                    "valor": "corona",
                    "etiqueta": "Corona",
                    "color": "#ec4899",
                    "color_fondo": "#fce7f3",
                    "icono": "♔",
                    "descripcion": "Diente con corona protésica"
                },
                {
                    "valor": "extraido",
                    "etiqueta": "Extraído",
                    "color": "#6b7280",
                    "color_fondo": "#f3f4f6",
                    "icono": "✕",
                    "descripcion": "Pieza dental ausente"
                },
                {
                    "valor": "implante",
                    "etiqueta": "Implante",
                    "color": "#14b8a6",
                    "color_fondo": "#ccfbf1",
                    "icono": "⬢",
                    "descripcion": "Implante dental"
                },
                {
                    "valor": "fracturado",
                    "etiqueta": "Fracturado",
                    "color": "#dc2626",
                    "color_fondo": "#fecaca",
                    "icono": "⚡",
                    "descripcion": "Diente fracturado"
                },
                {
                    "valor": "movilidad",
                    "etiqueta": "Movilidad",
                    "color": "#f97316",
                    "color_fondo": "#ffedd5",
                    "icono": "↔",
                    "descripcion": "Diente con movilidad"
                },
                {
                    "valor": "protesis",
                    "etiqueta": "Prótesis",
                    "color": "#a855f7",
                    "color_fondo": "#f3e8ff",
                    "icono": "⌂",
                    "descripcion": "Prótesis dental"
                }
            ],
            
            # Superficies dentales disponibles
            "superficies": [
                {
                    "valor": "oclusal",
                    "etiqueta": "Oclusal",
                    "descripcion": "Superficie de masticación",
                    "abreviatura": "O"
                },
                {
                    "valor": "mesial",
                    "etiqueta": "Mesial",
                    "descripcion": "Cara hacia el centro de la boca",
                    "abreviatura": "M"
                },
                {
                    "valor": "distal",
                    "etiqueta": "Distal",
                    "descripcion": "Cara hacia el exterior",
                    "abreviatura": "D"
                },
                {
                    "valor": "vestibular",
                    "etiqueta": "Vestibular",
                    "descripcion": "Cara externa (hacia labios/mejillas)",
                    "abreviatura": "V"
                },
                {
                    "valor": "lingual",
                    "etiqueta": "Lingual",
                    "descripcion": "Cara interna (hacia lengua)",
                    "abreviatura": "L"
                },
                {
                    "valor": "palatina",
                    "etiqueta": "Palatina",
                    "descripcion": "Cara interna superior (hacia paladar)",
                    "abreviatura": "P"
                }
            ],
            
            # Materiales comunes
            "materiales": [
                {"valor": "resina", "etiqueta": "Resina Compuesta"},
                {"valor": "amalgama", "etiqueta": "Amalgama"},
                {"valor": "porcelana", "etiqueta": "Porcelana"},
                {"valor": "zirconio", "etiqueta": "Zirconio"},
                {"valor": "composite", "etiqueta": "Composite"},
                {"valor": "oro", "etiqueta": "Oro"},
                {"valor": "metal_porcelana", "etiqueta": "Metal-Porcelana"},
                {"valor": "titanio", "etiqueta": "Titanio"}
            ],
            
            # Información adicional para el frontend
            "ordenamiento_visual": {
                "superior_derecho": ["18", "17", "16", "15", "14", "13", "12", "11"],
                "superior_izquierdo": ["21", "22", "23", "24", "25", "26", "27", "28"],
                "inferior_derecho": ["48", "47", "46", "45", "44", "43", "42", "41"],
                "inferior_izquierdo": ["31", "32", "33", "34", "35", "36", "37", "38"]
            },
            
            # Metainformación
            "version": "1.0",
            "idioma": "es"
        })

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
        if user.tipo_usuario == 'PACIENTE' and hasattr(user, 'perfil_paciente'):
            return self.queryset.filter(historial_clinico__paciente=user.perfil_paciente)
        elif user.is_staff or user.tipo_usuario in ['ODONTOLOGO', 'ADMIN']:
            return self.queryset
        return self.queryset.none()
    
    def create(self, request, *args, **kwargs):
        """
        Crear un documento clínico.
        El frontend envía 'historialId' en el FormData, necesitamos mapearlo a 'historial_clinico'.
        """
        # DEBUG: Imprimir información del request
        print("\n" + "="*80)
        print("🔍 DEBUG - DocumentoClinicoViewSet.create()")
        print("="*80)
        print(f"📋 request.POST.keys(): {list(request.POST.keys())}")
        print(f"📋 request.POST: {dict(request.POST)}")
        print(f"📋 request.data.keys(): {list(request.data.keys()) if hasattr(request.data, 'keys') else 'N/A'}")
        print(f"📁 request.FILES.keys(): {list(request.FILES.keys())}")
        print(f"📋 request.content_type: {request.content_type}")
        print("="*80 + "\n")
        
        # El frontend puede enviar 'historialId' o 'historial_clinico'
        # Django FormData parser puede devolver valores como listas
        historial_id = None
        
        # Intentar obtener de request.data primero (puede ser string directo)
        historial_id = request.data.get('historialId') or request.data.get('historial_clinico')
        
        # Si no está en data, buscar en POST
        if not historial_id:
            historial_id = request.POST.get('historialId') or request.POST.get('historial_clinico')
            # Si viene como lista (comportamiento de Django con FormData), extraer primer elemento
            if isinstance(historial_id, list) and len(historial_id) > 0:
                historial_id = historial_id[0]
        
        print(f"🔑 historial_id obtenido: {historial_id} (tipo: {type(historial_id).__name__})")
        
        if not historial_id:
            return Response(
                {"error": "Se requiere historialId"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el historial existe
        try:
            historial = HistorialClinico.objects.get(pk=historial_id)
        except HistorialClinico.DoesNotExist:
            return Response(
                {"error": f"Historial clínico con ID {historial_id} no encontrado."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Crear diccionario con los datos del request
        # Combinar POST (campos texto) y FILES (archivos)
        data = {}
        
        # Copiar campos de texto desde POST
        # Django puede devolver listas para valores de FormData, extraer primer elemento
        for key in request.POST.keys():
            value = request.POST[key]
            # Si es una lista con un solo elemento, extraer el elemento
            if isinstance(value, list) and len(value) == 1:
                data[key] = value[0]
            else:
                data[key] = value
        
        # Copiar campos adicionales desde data si no están en POST
        for key in request.data.keys():
            if key not in data and key != 'archivo':  # archivo se maneja aparte
                data[key] = request.data[key]
        
        # Agregar el archivo desde FILES
        if 'archivo' in request.FILES:
            data['archivo'] = request.FILES['archivo']
        
        # Asegurar que historial_clinico esté presente con el ID correcto
        data['historial_clinico'] = historial.pk
        
        # Asegurar que tipo_documento esté presente (puede venir como 'tipo' del frontend)
        if 'tipo' in data and 'tipo_documento' not in data:
            data['tipo_documento'] = data.pop('tipo')
        
        # Manejar episodio opcional (si viene del frontend)
        if 'episodio' in data:
            # Validar que el episodio existe y pertenece al mismo historial
            try:
                episodio_id = data['episodio']
                if isinstance(episodio_id, list):
                    episodio_id = episodio_id[0]
                
                episodio = EpisodioAtencion.objects.get(pk=episodio_id)
                if episodio.historial_clinico.pk != historial.pk:
                    return Response(
                        {"error": "El episodio no pertenece al historial clínico especificado."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                data['episodio'] = episodio.pk
            except EpisodioAtencion.DoesNotExist:
                return Response(
                    {"error": f"Episodio con ID {episodio_id} no encontrado."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        print(f"📦 Datos preparados para serializer: {list(data.keys())}")
        print(f"   - historial_clinico: {data.get('historial_clinico')}")
        print(f"   - tipo_documento: {data.get('tipo_documento')}")
        print(f"   - descripcion: {data.get('descripcion')}")
        print(f"   - episodio: {data.get('episodio', 'No vinculado')}")
        print(f"   - archivo: {'✓' if 'archivo' in data else '✗'}")
        
        # Crear el serializer con los datos modificados
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        Retorna el archivo como FileResponse (Blob) para descarga directa.
        """
        documento = self.get_object()
        
        if not documento.archivo:
            return Response(
                {"error": "Este documento no tiene archivo adjunto."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Obtener la ruta física del archivo
            archivo_path = documento.archivo.path
            
            # Verificar que el archivo existe
            if not os.path.exists(archivo_path):
                raise Http404("Archivo no encontrado en el sistema de archivos.")
            
            # Obtener el tipo MIME del archivo
            content_type, _ = mimetypes.guess_type(archivo_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Obtener el nombre del archivo
            nombre_archivo = os.path.basename(documento.archivo.name)
            
            # Abrir el archivo y retornarlo como FileResponse
            archivo = open(archivo_path, 'rb')
            response = FileResponse(archivo, content_type=content_type)
            
            # Headers para forzar descarga con nombre original
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            response['Content-Length'] = os.path.getsize(archivo_path)
            
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Error al descargar el archivo: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
