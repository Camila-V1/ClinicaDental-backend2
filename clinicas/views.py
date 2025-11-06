from rest_framework import viewsets, permissions
from .models import Clinica
from .serializers import ClinicaSerializer


class ClinicaViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de Clinicas (tenants)."""
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer
    permission_classes = [permissions.IsAuthenticated]
