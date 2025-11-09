from rest_framework import serializers
from .models import (
    CategoriaServicio, Servicio, 
    MaterialServicioFijo, MaterialServicioOpcional,
    PlanDeTratamiento, ItemPlanTratamiento,
    Presupuesto, ItemPresupuesto  # Nuevos modelos del Paso 2.D
)
from inventario.serializers import InsumoSerializer, CategoriaInsumoSerializer
from usuarios.serializers import UsuarioSerializer


# ===============================================================================
# PASO 2.B: SERIALIZERS PARA LAS "RECETAS"
# ===============================================================================

class MaterialServicioFijoSerializer(serializers.ModelSerializer):
    """
    Serializer para materiales fijos de un servicio.
    Incluye información completa del insumo y cálculos de costo.
    """
    # Serializer anidado para mostrar el detalle del insumo
    insumo = InsumoSerializer(read_only=True)
    costo_adicional = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    costo_material_formateado = serializers.CharField(read_only=True)
    
    class Meta:
        model = MaterialServicioFijo
        fields = [
            'id', 'insumo', 'cantidad', 'es_obligatorio', 'notas',
            'costo_adicional', 'costo_material_formateado'
        ]


class MaterialServicioOpcionalSerializer(serializers.ModelSerializer):
    """
    Serializer para materiales opcionales de un servicio.
    Incluye información de la categoría y opciones disponibles.
    """
    # Serializer anidado para mostrar el detalle de la categoría
    categoria_insumo = CategoriaInsumoSerializer(read_only=True)
    opciones_disponibles = InsumoSerializer(many=True, read_only=True)
    rango_precios = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialServicioOpcional
        fields = [
            'id', 'categoria_insumo', 'cantidad', 'nombre_personalizado',
            'es_obligatorio', 'notas', 'opciones_disponibles', 'rango_precios'
        ]
    
    def get_rango_precios(self, obj):
        """Calcula el rango de precios para las opciones disponibles"""
        return obj.rango_precios


# Serializer simplificado para listados (sin tantos detalles)
class MaterialServicioFijoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para materiales fijos en listados"""
    insumo_nombre = serializers.CharField(source='insumo.nombre', read_only=True)
    insumo_codigo = serializers.CharField(source='insumo.codigo', read_only=True)
    costo_adicional = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = MaterialServicioFijo
        fields = ['id', 'insumo_nombre', 'insumo_codigo', 'cantidad', 'costo_adicional']


class MaterialServicioOpcionalSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para materiales opcionales en listados"""
    categoria_nombre = serializers.CharField(source='categoria_insumo.nombre', read_only=True)
    nombre_mostrar = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialServicioOpcional
        fields = ['id', 'categoria_nombre', 'nombre_mostrar', 'cantidad', 'es_obligatorio']
    
    def get_nombre_mostrar(self, obj):
        """Retorna el nombre personalizado o el nombre de la categoría"""
        return obj.nombre_personalizado or f"Elegir {obj.categoria_insumo.nombre}"


class CategoriaServicioSerializer(serializers.ModelSerializer):
    """
    Serializer para categorías de servicios odontológicos.
    """
    cantidad_servicios = serializers.SerializerMethodField()

    class Meta:
        model = CategoriaServicio
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activo',
            'orden',
            'cantidad_servicios',
            'creado',
            'actualizado'
        ]
        read_only_fields = ['creado', 'actualizado']

    def get_cantidad_servicios(self, obj):
        """Retorna la cantidad de servicios activos en esta categoría"""
        return obj.servicios.filter(activo=True).count()


class ServicioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar servicios (sin campos pesados).
    Incluye información básica de las recetas.
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    
    # --- PASO 2.B: INFORMACIÓN BÁSICA DE RECETAS ---
    materiales_fijos = MaterialServicioFijoSimpleSerializer(many=True, read_only=True)
    materiales_opcionales = MaterialServicioOpcionalSimpleSerializer(many=True, read_only=True)
    costo_materiales_fijos = serializers.SerializerMethodField()
    tiene_materiales_opcionales = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            'id',
            'codigo_servicio',
            'nombre',
            'categoria_nombre',
            'precio_base',
            'duracion_formateada',
            'requiere_cita_previa',
            'activo',
            # --- PASO 2.B: CAMPOS DE RECETA ---
            'materiales_fijos',
            'materiales_opcionales', 
            'costo_materiales_fijos',
            'tiene_materiales_opcionales'
        ]
    
    def get_costo_materiales_fijos(self, obj):
        """Calcula el costo total de los materiales fijos"""
        return sum(material.costo_adicional for material in obj.materiales_fijos.all())
    
    def get_tiene_materiales_opcionales(self, obj):
        """Indica si el servicio tiene materiales opcionales"""
        return obj.materiales_opcionales.exists()


class ServicioSerializer(serializers.ModelSerializer):
    """
    Serializer completo para servicios odontológicos.
    Incluye todos los campos para operaciones CRUD y las "recetas" (Paso 2.B).
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    categoria_info = CategoriaServicioSerializer(source='categoria', read_only=True)
    
    # --- PASO 2.B: AÑADIR LAS RECETAS ANIDADAS ---
    materiales_fijos = MaterialServicioFijoSerializer(many=True, read_only=True)
    materiales_opcionales = MaterialServicioOpcionalSerializer(many=True, read_only=True)
    
    # Campos calculados
    costo_materiales_fijos = serializers.SerializerMethodField()
    tiene_materiales_opcionales = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            'id',
            'codigo_servicio',
            'nombre',
            'descripcion',
            'categoria',
            'categoria_nombre',
            'categoria_info',
            'precio_base',
            'tiempo_estimado',
            'duracion_formateada',
            'requiere_cita_previa',
            'requiere_autorizacion',
            'activo',
            'notas_internas',
            # --- PASO 2.B: CAMPOS DE RECETA ---
            'materiales_fijos',
            'materiales_opcionales',
            'costo_materiales_fijos',
            'tiene_materiales_opcionales',
            'creado',
            'actualizado'
        ]
        read_only_fields = [
            'creado', 'actualizado', 'duracion_formateada', 
            'materiales_fijos', 'materiales_opcionales',
            'costo_materiales_fijos', 'tiene_materiales_opcionales'
        ]
    
    def get_costo_materiales_fijos(self, obj):
        """Calcula el costo total de los materiales fijos"""
        return sum(material.costo_adicional for material in obj.materiales_fijos.all())
    
    def get_tiene_materiales_opcionales(self, obj):
        """Indica si el servicio tiene materiales opcionales"""
        return obj.materiales_opcionales.exists()

    def validate_codigo_servicio(self, value):
        """
        Validar que el código sea único y tenga el formato correcto.
        """
        # Convertir a uppercase y quitar espacios
        value = value.upper().replace(' ', '')
        
        # Verificar formato básico (letras-números)
        import re
        if not re.match(r'^[A-Z]+-\d+$', value):
            raise serializers.ValidationError(
                "El código debe tener el formato 'LETRAS-NUMEROS' (ej: CONS-001, REST-001)"
            )
        
        # Verificar unicidad (excluyendo el objeto actual en caso de edición)
        queryset = Servicio.objects.filter(codigo_servicio=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f"Ya existe un servicio con el código '{value}'"
            )
        
        return value

    def validate_precio_base(self, value):
        """Validar que el precio base sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio base debe ser mayor a 0")
        return value

    def validate_tiempo_estimado(self, value):
        """Validar tiempo estimado"""
        if value < 5:
            raise serializers.ValidationError("El tiempo mínimo es de 5 minutos")
        if value > 480:  # 8 horas
            raise serializers.ValidationError("El tiempo máximo es de 8 horas (480 minutos)")
        return value


class ServicioCatalogoSerializer(serializers.ModelSerializer):
    """
    Serializer específico para el endpoint del catálogo público (CU22).
    Solo incluye información relevante para consultar servicios disponibles.
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)

    class Meta:
        model = Servicio
        fields = [
            'id',
            'codigo_servicio',
            'nombre',
            'descripcion',
            'categoria_nombre',
            'precio_base',
            'duracion_formateada',
            'requiere_cita_previa',
            'requiere_autorizacion'
        ]


# ===============================================================================
# PASO 2.C: SERIALIZERS PARA PLANES DE TRATAMIENTO
# ===============================================================================

class ItemPlanTratamientoSerializer(serializers.ModelSerializer):
    """
    Serializer para ítems de plan de tratamiento.
    ¡Aquí se materializa tu idea del precio dinámico!
    """
    # Información del servicio
    servicio_info = ServicioSerializer(source='servicio', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    
    # Información del insumo seleccionado
    insumo_seleccionado_info = InsumoSerializer(source='insumo_seleccionado', read_only=True)
    insumo_nombre = serializers.CharField(source='insumo_seleccionado.nombre', read_only=True, allow_null=True)
    
    # Precios calculados
    precio_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    precio_total_formateado = serializers.CharField(read_only=True)
    
    # Estado formateado
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ItemPlanTratamiento
        fields = [
            'id',
            'plan',
            'servicio',
            'servicio_nombre',
            'servicio_info',
            'insumo_seleccionado',
            'insumo_nombre',
            'insumo_seleccionado_info',
            # Snapshots de precios
            'precio_servicio_snapshot',
            'precio_materiales_fijos_snapshot',
            'precio_insumo_seleccionado_snapshot',
            # Precios calculados
            'precio_total',
            'precio_total_formateado',
            # Estado e información adicional
            'estado',
            'estado_display',
            'orden',
            'notas',
            'fecha_estimada',
            'fecha_realizada',
            'creado',
            'actualizado'
        ]
        read_only_fields = [
            'precio_servicio_snapshot',
            'precio_materiales_fijos_snapshot', 
            'precio_insumo_seleccionado_snapshot',
            'precio_total',
            'precio_total_formateado',
            'creado',
            'actualizado'
        ]

    def validate(self, data):
        """
        Validaciones personalizadas para el ítem.
        Verifica que si el servicio tiene materiales opcionales, se haya seleccionado uno.
        """
        servicio = data.get('servicio')
        insumo_seleccionado = data.get('insumo_seleccionado')
        
        if servicio:
            # Verificar si el servicio tiene materiales opcionales que requieren selección
            materiales_opcionales_obligatorios = servicio.materiales_opcionales.filter(es_obligatorio=True)
            
            if materiales_opcionales_obligatorios.exists() and not insumo_seleccionado:
                raise serializers.ValidationError(
                    f"El servicio '{servicio.nombre}' requiere seleccionar un material específico."
                )
            
            # Verificar que el insumo seleccionado pertenezca a una categoría válida para el servicio
            if insumo_seleccionado:
                categorias_validas = materiales_opcionales_obligatorios.values_list('categoria_insumo', flat=True)
                if insumo_seleccionado.categoria.id not in categorias_validas:
                    raise serializers.ValidationError(
                        f"El insumo seleccionado no es válido para este servicio."
                    )
        
        return data


class ItemPlanTratamientoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para ítems en listados"""
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    insumo_nombre = serializers.CharField(source='insumo_seleccionado.nombre', read_only=True, allow_null=True)
    precio_total_formateado = serializers.CharField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ItemPlanTratamiento
        fields = [
            'id',
            'servicio_nombre',
            'insumo_nombre', 
            'precio_total_formateado',
            'estado',
            'estado_display',
            'orden'
        ]


class PlanDeTratamientoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para planes de tratamiento.
    Incluye todos los ítems anidados con el precio dinámico calculado.
    """
    # Información de relaciones
    paciente_info = serializers.SerializerMethodField()
    odontologo_info = serializers.SerializerMethodField()
    
    # Ítems del plan (anidados)
    items = ItemPlanTratamientoSerializer(many=True, read_only=True)
    
    # Campos calculados
    precio_total_plan = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    porcentaje_completado = serializers.IntegerField(read_only=True)
    
    # Estado formateado
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    # Información de fechas
    puede_ser_editado = serializers.BooleanField(read_only=True)

    class Meta:
        model = PlanDeTratamiento
        fields = [
            'id',
            'titulo',
            'descripcion',
            'paciente',
            'paciente_info',
            'odontologo',
            'odontologo_info',
            'estado',
            'estado_display',
            'prioridad',
            'prioridad_display',
            # Fechas
            'fecha_creacion',
            'fecha_presentacion',
            'fecha_aceptacion',
            'fecha_inicio',
            'fecha_finalizacion',
            # Ítems y cálculos
            'items',
            'precio_total_plan',
            'cantidad_items',
            'porcentaje_completado',
            'puede_ser_editado',
            # Notas
            'notas_internas',
            'creado',
            'actualizado'
        ]
        read_only_fields = [
            'precio_total_plan',
            'cantidad_items',
            'porcentaje_completado',
            'puede_ser_editado',
            'fecha_presentacion',
            'fecha_aceptacion', 
            'fecha_inicio',
            'fecha_finalizacion',
            'creado',
            'actualizado'
        ]

    def get_paciente_info(self, obj):
        """Información básica del paciente"""
        return {
            'id': obj.paciente.usuario.id,
            'nombre_completo': f"{obj.paciente.usuario.nombre} {obj.paciente.usuario.apellido}",
            'email': obj.paciente.usuario.email
        }

    def get_odontologo_info(self, obj):
        """Información básica del odontólogo"""
        especialidad_nombre = None
        if hasattr(obj.odontologo, 'especialidad') and obj.odontologo.especialidad:
            especialidad_nombre = obj.odontologo.especialidad.nombre
        
        return {
            'id': obj.odontologo.usuario.id,
            'nombre_completo': f"Dr. {obj.odontologo.usuario.nombre} {obj.odontologo.usuario.apellido}",
            'especialidad': especialidad_nombre
        }


class PlanDeTratamientoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de planes"""
    paciente_nombre = serializers.SerializerMethodField()
    odontologo_nombre = serializers.SerializerMethodField()
    items_simples = ItemPlanTratamientoSimpleSerializer(source='items', many=True, read_only=True)
    precio_total_plan = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    porcentaje_completado = serializers.IntegerField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = PlanDeTratamiento
        fields = [
            'id',
            'titulo',
            'paciente_nombre',
            'odontologo_nombre',
            'estado',
            'estado_display',
            'prioridad',
            'precio_total_plan',
            'cantidad_items',
            'porcentaje_completado',
            'fecha_creacion',
            'items_simples'
        ]

    def get_paciente_nombre(self, obj):
        return f"{obj.paciente.usuario.nombre} {obj.paciente.usuario.apellido}"

    def get_odontologo_nombre(self, obj):
        return f"Dr. {obj.odontologo.usuario.nombre} {obj.odontologo.usuario.apellido}"


# ===============================================================================
# PASO 2.D: SERIALIZERS PARA PRESUPUESTOS (CU20, CU21)
# ===============================================================================

class ItemPresupuestoSerializer(serializers.ModelSerializer):
    """
    Serializer para los ítems "congelados" del presupuesto.
    
    ¡ESTOS SON DE SOLO LECTURA! Una vez creados, representan precios inmutables.
    El paciente ve exactamente estos precios al aceptar el presupuesto.
    """
    # Campos calculados para mejor presentación
    precio_total_formateado = serializers.CharField(read_only=True)
    
    class Meta:
        model = ItemPresupuesto
        fields = [
            'id',
            'orden', 
            'nombre_servicio', 
            'nombre_insumo_seleccionado',
            # Precios congelados
            'precio_servicio', 
            'precio_materiales_fijos',
            'precio_insumo_seleccionado', 
            'precio_total_item',
            'precio_total_formateado',
            'creado'
        ]
        read_only_fields = '__all__'  # TODO es de solo lectura


class PresupuestoSerializer(serializers.ModelSerializer):
    """
    Serializer para el Presupuesto - El corazón del CU20 y CU21.
    
    Este serializer maneja:
    - Lectura de presupuestos existentes
    - Creación de nuevos presupuestos (desde PlanDeTratamiento)
    - Visualización de ítems congelados
    """
    # Ítems anidados (congelados)
    items = ItemPresupuestoSerializer(many=True, read_only=True)
    
    # Información del plan para contexto
    plan_titulo = serializers.CharField(source='plan_tratamiento.titulo', read_only=True)
    plan_paciente = serializers.SerializerMethodField()
    plan_odontologo = serializers.SerializerMethodField()
    
    # Estado y fechas con información adicional
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    puede_ser_aceptado = serializers.BooleanField(read_only=True)
    
    # Precios formateados para presentación
    total_formateado = serializers.SerializerMethodField()
    
    # URL de aceptación para CU21
    url_aceptacion = serializers.SerializerMethodField()
    
    class Meta:
        model = Presupuesto
        fields = [
            'id', 
            'plan_tratamiento', 
            'plan_titulo',
            'plan_paciente',
            'plan_odontologo',
            'version', 
            'estado',
            'estado_display',
            # Snapshots de totales
            'subtotal_servicios', 
            'subtotal_materiales_fijos',
            'subtotal_materiales_opcionales', 
            'descuento_total',
            'total_presupuestado',
            'total_formateado',
            # Fechas importantes
            'fecha_presentacion', 
            'fecha_vencimiento',
            'fecha_aceptacion',
            # Estado y validaciones
            'esta_vencido',
            'puede_ser_aceptado',
            'url_aceptacion',
            # Token para aceptación (CU21)
            'token_aceptacion', 
            # Ítems congelados
            'items',
            # Metadatos
            'creado'
        ]
        read_only_fields = (
            'id', 'version', 'estado', 
            'subtotal_servicios', 'subtotal_materiales_fijos',
            'subtotal_materiales_opcionales', 'descuento_total', 
            'total_presupuestado', 'total_formateado',
            'fecha_aceptacion', 'token_aceptacion', 'creado', 
            'items', 'plan_titulo', 'plan_paciente', 'plan_odontologo',
            'esta_vencido', 'puede_ser_aceptado', 'url_aceptacion',
            'estado_display'
        )

    def get_plan_paciente(self, obj):
        """Información del paciente"""
        paciente = obj.plan_tratamiento.paciente
        return {
            'id': paciente.id,
            'nombre_completo': f"{paciente.usuario.nombre} {paciente.usuario.apellido}",
            'email': paciente.usuario.email
        }

    def get_plan_odontologo(self, obj):
        """Información del odontólogo"""
        odontologo = obj.plan_tratamiento.odontologo
        return {
            'id': odontologo.id,
            'nombre_completo': f"Dr. {odontologo.usuario.nombre} {odontologo.usuario.apellido}",
            'especialidad': odontologo.especialidad.nombre if odontologo.especialidad else None
        }

    def get_total_formateado(self, obj):
        """Total formateado para mostrar"""
        return f"${obj.total_presupuestado:,.2f}"

    def get_url_aceptacion(self, obj):
        """URL para que el paciente acepte el presupuesto (CU21)"""
        if obj.puede_ser_aceptado:
            # En producción sería una URL completa, aquí ponemos la ruta de la API
            return f"/api/tratamientos/presupuestos/{obj.id}/aceptar/{obj.token_aceptacion}/"
        return None


class PresupuestoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de presupuestos"""
    plan_titulo = serializers.CharField(source='plan_tratamiento.titulo', read_only=True)
    plan_paciente = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    total_formateado = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)
    puede_ser_aceptado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Presupuesto
        fields = [
            'id',
            'plan_titulo',
            'plan_paciente', 
            'version',
            'estado',
            'estado_display',
            'total_formateado',
            'fecha_presentacion',
            'fecha_vencimiento',
            'esta_vencido',
            'puede_ser_aceptado'
        ]

    def get_plan_paciente(self, obj):
        paciente = obj.plan_tratamiento.paciente
        return f"{paciente.usuario.nombre} {paciente.usuario.apellido}"

    def get_total_formateado(self, obj):
        return f"${obj.total_presupuestado:,.2f}"


class PresupuestoCreacionSerializer(serializers.Serializer):
    """
    Serializer especial para crear presupuestos desde un PlanDeTratamiento.
    Se usa en la acción 'generar-presupuesto' del PlanDeTratamientoViewSet.
    """
    fecha_vencimiento = serializers.DateField(
        required=False,
        help_text="Fecha límite para aceptar (opcional, por defecto 30 días)"
    )
    notas = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Notas adicionales para el presupuesto"
    )

    def create(self, validated_data):
        """
        Crea un presupuesto desde el plan de tratamiento.
        Esta lógica se ejecuta en el ViewSet.
        """
        # Esta lógica se maneja en el ViewSet
        pass