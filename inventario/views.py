"""
Vistas de la API de Inventario.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import CategoriaInsumo, Insumo
from .serializers import (
    CategoriaInsumoSerializer,
    InsumoSerializer,
    InsumoListSerializer
)
from reportes.models import BitacoraAccion


class CategoriaInsumoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de insumos.
    
    Endpoints:
    - GET    /api/inventario/categorias/         - Listar categorías
    - POST   /api/inventario/categorias/         - Crear categoría
    - GET    /api/inventario/categorias/{id}/    - Ver detalle
    - PUT    /api/inventario/categorias/{id}/    - Actualizar
    - DELETE /api/inventario/categorias/{id}/    - Eliminar
    """
    queryset = CategoriaInsumo.objects.all()
    serializer_class = CategoriaInsumoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creado']
    ordering = ['nombre']


class InsumoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar insumos/materiales.
    
    Endpoints:
    - GET    /api/inventario/insumos/                  - Listar insumos
    - POST   /api/inventario/insumos/                  - Crear insumo
    - GET    /api/inventario/insumos/{id}/             - Ver detalle
    - PUT    /api/inventario/insumos/{id}/             - Actualizar
    - DELETE /api/inventario/insumos/{id}/             - Eliminar
    - GET    /api/inventario/insumos/bajo_stock/       - Insumos con stock bajo
    - POST   /api/inventario/insumos/{id}/ajustar_stock/ - Ajustar stock
    """
    queryset = Insumo.objects.select_related('categoria').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion', 'proveedor']
    ordering_fields = ['nombre', 'precio_venta', 'stock_actual', 'creado']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para listado."""
        if self.action == 'list':
            return InsumoListSerializer
        return InsumoSerializer
    
    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """
        Endpoint para listar insumos con stock bajo (requieren reposición).
        GET /api/inventario/insumos/bajo_stock/
        """
        insumos_bajo_stock = [
            insumo for insumo in self.get_queryset()
            if insumo.requiere_reposicion
        ]
        serializer = InsumoListSerializer(insumos_bajo_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ajustar_stock(self, request, pk=None):
        """
        Endpoint para ajustar el stock de un insumo.
        POST /api/inventario/insumos/{id}/ajustar_stock/
        
        Body:
        {
            "cantidad": 10,      # Positivo = entrada, Negativo = salida
            "motivo": "Compra"   # Opcional
        }
        """
        insumo = self.get_object()
        cantidad = request.data.get('cantidad')
        motivo = request.data.get('motivo', '')
        
        if cantidad is None:
            return Response(
                {'error': 'Debe proporcionar la cantidad a ajustar'},
                status=400
            )
        
        try:
            cantidad = float(cantidad)
            stock_anterior = float(insumo.stock_actual)
            nuevo_stock = insumo.ajustar_stock(cantidad, motivo)
            
            # Registrar en bitácora
            accion = 'EDITAR' if cantidad != 0 else 'VER'
            tipo_movimiento = 'entrada' if cantidad > 0 else 'salida'
            BitacoraAccion.registrar(
                usuario=request.user,
                accion=accion,
                descripcion=f'Ajustó stock de {insumo.codigo} ({insumo.nombre}): {tipo_movimiento} de {abs(cantidad)} unidades',
                content_object=insumo,
                detalles={
                    'stock_anterior': stock_anterior,
                    'ajuste': cantidad,
                    'stock_nuevo': float(nuevo_stock),
                    'motivo': motivo
                }
            )
            
            return Response({
                'mensaje': 'Stock ajustado exitosamente',
                'insumo': insumo.nombre,
                'stock_anterior': stock_anterior,
                'ajuste': cantidad,
                'stock_actual': float(nuevo_stock),
                'motivo': motivo
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=400
            )
