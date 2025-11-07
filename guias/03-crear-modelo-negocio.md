# 03 - Crear Modelo de Negocio (Tenant)

## 🎯 Para: Agenda, Tratamientos, Facturación, etc.

Estos son los pasos para agregar **cualquier funcionalidad de clínica**.

---

## Paso 1: Crear el Modelo

**Archivo:** `<app>/models.py`

```python
# agenda/models.py
from django.db import models
from usuarios.models import Usuario, PerfilPaciente, PerfilOdontologo

class Cita(models.Model):
    """Cita médica en la agenda"""
    
    # Relaciones
    paciente = models.ForeignKey(
        PerfilPaciente,
        on_delete=models.CASCADE,
        related_name='citas'
    )
    odontologo = models.ForeignKey(
        PerfilOdontologo,
        on_delete=models.CASCADE,
        related_name='citas_atendidas'
    )
    
    # Datos de la cita
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    observaciones = models.TextField(blank=True)
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('CONFIRMADA', 'Confirmada'),
            ('ATENDIDA', 'Atendida'),
            ('CANCELADA', 'Cancelada'),
        ],
        default='PENDIENTE'
    )
    
    # Timestamps
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Agenda"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Cita {self.paciente} - {self.fecha_hora}"
```

---

## Paso 2: Registrar en Admin TENANT

**Archivo:** `<app>/admin.py`

```python
# agenda/admin.py
from django.contrib import admin
from .models import Cita

@admin.register(Cita)  # ← Esto lo registra en admin.site (tenant)
class CitaAdmin(admin.ModelAdmin):
    list_display = [
        'fecha_hora',
        'paciente',
        'odontologo',
        'estado',
        'motivo'
    ]
    list_filter = ['estado', 'fecha_hora', 'odontologo']
    search_fields = [
        'paciente__usuario__nombre',
        'paciente__usuario__apellido',
        'odontologo__usuario__nombre',
        'motivo'
    ]
    date_hierarchy = 'fecha_hora'
    
    fieldsets = (
        ('Información de la Cita', {
            'fields': ('paciente', 'odontologo', 'fecha_hora', 'motivo')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
    )
```

---

## Paso 3: Crear Serializer

**Archivo:** `<app>/serializers.py`

```python
# agenda/serializers.py
from rest_framework import serializers
from .models import Cita
from usuarios.serializers import UsuarioSerializer

class CitaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura con datos completos
    paciente_nombre = serializers.CharField(
        source='paciente.usuario.nombre',
        read_only=True
    )
    odontologo_nombre = serializers.CharField(
        source='odontologo.usuario.nombre',
        read_only=True
    )
    
    class Meta:
        model = Cita
        fields = [
            'id',
            'paciente',
            'paciente_nombre',
            'odontologo',
            'odontologo_nombre',
            'fecha_hora',
            'motivo',
            'observaciones',
            'estado',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']
    
    def validate_fecha_hora(self, value):
        """Validar que la fecha sea futura"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError(
                "La fecha de la cita debe ser futura"
            )
        return value
```

---

## Paso 4: Crear Views

**Archivo:** `<app>/views.py`

```python
# agenda/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Cita
from .serializers import CitaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    """
    API para gestión de citas.
    
    - GET /api/agenda/citas/ - Lista todas las citas
    - POST /api/agenda/citas/ - Crear nueva cita
    - GET /api/agenda/citas/{id}/ - Detalle de cita
    - PUT/PATCH /api/agenda/citas/{id}/ - Actualizar cita
    - DELETE /api/agenda/citas/{id}/ - Eliminar cita
    """
    serializer_class = CitaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtra citas según el tipo de usuario.
        El aislamiento por tenant es automático.
        """
        user = self.request.user
        
        # Si es paciente, solo sus citas
        if hasattr(user, 'perfilpaciente'):
            return Cita.objects.filter(
                paciente=user.perfilpaciente
            )
        
        # Si es odontólogo, solo sus citas
        elif hasattr(user, 'perfilodontologo'):
            return Cita.objects.filter(
                odontologo=user.perfilodontologo
            )
        
        # Si es admin/staff, todas las citas
        elif user.is_staff:
            return Cita.objects.all()
        
        # Otros casos
        return Cita.objects.none()
    
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """
        GET /api/agenda/citas/proximas/
        Retorna citas futuras del usuario
        """
        ahora = timezone.now()
        queryset = self.get_queryset().filter(
            fecha_hora__gte=ahora,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).order_by('fecha_hora')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """
        POST /api/agenda/citas/{id}/confirmar/
        Confirma una cita pendiente
        """
        cita = self.get_object()
        
        if cita.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden confirmar citas pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cita.estado = 'CONFIRMADA'
        cita.save()
        
        serializer = self.get_serializer(cita)
        return Response(serializer.data)
```

---

## Paso 5: Crear URLs de la App

**Archivo:** `<app>/urls.py`

```python
# agenda/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## Paso 6: ⚠️ IMPORTANTE - Incluir en URLs TENANT

**Archivo:** `core/urls_tenant.py`

```python
# core/urls_tenant.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs de TENANT (clínicas)
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),  # ← AGREGAR AQUÍ
    path('api/tratamientos/', include('tratamientos.urls')),
    # ... más apps
]
```

---

## Paso 7: Agregar a TENANT_APPS

**Archivo:** `core/settings.py`

```python
# core/settings.py

TENANT_APPS = [
    # Django core
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    
    # Third party
    'rest_framework',
    
    # Apps de negocio
    'usuarios',
    'agenda',  # ← AGREGAR AQUÍ
    'tratamientos',
    'historial_clinico',
    'facturacion',
    'inventario',
    'reportes',
]
```

---

## Paso 8: Crear Migraciones

```bash
# Crear migraciones
python manage.py makemigrations agenda

# Aplicar en TODOS los tenants
python manage.py migrate_schemas
```

---

## 🎯 URLs Resultantes

Después de completar estos pasos, tendrás:

```
http://clinica-demo.localhost:8000/api/agenda/citas/
├── GET     /           → Lista de citas
├── POST    /           → Crear cita
├── GET     /{id}/      → Detalle de cita
├── PUT     /{id}/      → Actualizar cita
├── DELETE  /{id}/      → Eliminar cita
├── GET     /proximas/  → Citas futuras (custom action)
└── POST    /{id}/confirmar/ → Confirmar cita (custom action)
```

---

## ✅ Verificación

1. **Admin:** Visita `http://clinica-demo.localhost:8000/admin/`
   - ✅ Debe aparecer sección "AGENDA" con "Citas"

2. **API:** Prueba en Postman/Thunder Client:
   ```
   GET http://clinica-demo.localhost:8000/api/agenda/citas/
   Authorization: Bearer <tu_token_jwt>
   ```

3. **Verificación automática:**
   ```bash
   python verificar_sistema.py
   ```

---

## 🎓 Próximo Paso

- Ver ejemplo completo: **[11-ejemplo-agenda.md](11-ejemplo-agenda.md)**
- Checklist completo: **[07-checklist-nueva-feature.md](07-checklist-nueva-feature.md)**
