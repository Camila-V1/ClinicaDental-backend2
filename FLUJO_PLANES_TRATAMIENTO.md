# 📋 FLUJO COMPLETO: PLANES DE TRATAMIENTO

## 🎯 Problema Actual

**❌ Los ítems del plan NO están vinculados con citas en la agenda**

Resultado:
- El odontólogo ve citas simples en la agenda
- NO ve qué ítem del plan debe atender en cada cita
- No hay forma de marcar el progreso del plan desde la agenda

---

## ✅ Solución: Dos enfoques posibles

### **Opción 1: Vincular ítems existentes con citas** (RECOMENDADO)

Agregar campo `cita` opcional a `ItemPlanTratamiento`:

```python
# En tratamientos/models.py - ItemPlanTratamiento

cita = models.ForeignKey(
    'agenda.Cita',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='item_plan',
    help_text="Cita asociada para realizar este tratamiento"
)
```

**Flujo:**
1. Odontólogo crea plan con ítems (sin cita asignada)
2. Paciente acepta plan
3. **Odontólogo programa citas y las vincula con ítems del plan**
4. En la agenda, cada cita muestra el ítem del plan asociado
5. Al atender la cita, se marca el ítem como completado

**Ventajas:**
- ✅ Flexible: Un ítem puede requerir múltiples citas
- ✅ Separación de responsabilidades (plan ≠ agenda)
- ✅ Fácil de implementar

---

### **Opción 2: Crear citas automáticamente desde ítems del plan**

Cuando el paciente acepta el plan, crear citas automáticamente:

```python
# Al aceptar plan
def aceptar(self):
    self.estado = self.EstadoPlan.ACEPTADO
    self.fecha_aceptacion = timezone.now()
    self.save()
    
    # Crear citas para cada ítem
    for item in self.items.all():
        Cita.objects.create(
            paciente=self.paciente,
            odontologo=self.odontologo,
            fecha=item.fecha_estimada or (timezone.now() + timedelta(days=7)),
            motivo=f"Tratamiento: {item.servicio.nombre}",
            tipo='tratamiento',
            item_plan=item  # Vincular
        )
```

**Ventajas:**
- ✅ Automático
- ✅ Garantiza que todos los ítems tengan cita

**Desventajas:**
- ❌ Menos flexible
- ❌ Puede crear muchas citas de golpe

---

## 🔄 FLUJO RECOMENDADO (Opción 1)

### **1. Crear Plan (Odontólogo)**
```
Dashboard → Planes → Nuevo Plan
↓
Seleccionar paciente
↓
Agregar ítems (servicios + materiales)
↓
Presentar al paciente
```

### **2. Aceptar Plan (Paciente)**
```
Email/Portal → Ver plan
↓
Revisar ítems y precio
↓
Aceptar plan
↓
Plan cambia a ACEPTADO
```

### **3. Programar Citas (Odontólogo)**
```
Dashboard → Agenda → Nueva Cita
↓
Seleccionar paciente y fecha
↓
**NUEVO**: Campo "Ítem del Plan"
  → Select con ítems pendientes del plan del paciente
↓
Guardar cita vinculada
```

### **4. Atender Cita (Odontólogo)**
```
Agenda → Clic en cita
↓
Ver detalle con ítem del plan asociado
↓
Botón "Atender" → Muestra info del ítem
↓
**NUEVO**: Al completar cita:
  - Marcar ítem como COMPLETADO
  - Crear episodio (historial clínico)
  - Actualizar progreso del plan
```

### **5. Progreso Automático**
```
Sistema detecta ítem completado
↓
Plan cambia de ACEPTADO → EN_PROGRESO
↓
Cuando todos los ítems están completados
↓
Plan cambia a COMPLETADO
```

---

## 🛠️ Cambios necesarios en el Backend

### **1. Agregar campo `cita` a ItemPlanTratamiento**

```python
# tratamientos/models.py

class ItemPlanTratamiento(models.Model):
    # ... campos existentes ...
    
    # NUEVO: Vincular con cita
    cita = models.OneToOneField(
        'agenda.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='item_plan',
        help_text="Cita programada para realizar este tratamiento"
    )
```

### **2. Crear migración**

```bash
python manage.py makemigrations tratamientos
python manage.py migrate
```

### **3. Actualizar Serializer de Cita**

```python
# agenda/serializers.py

class CitaSerializer(serializers.ModelSerializer):
    # ... campos existentes ...
    
    # NUEVO: Mostrar ítem del plan
    item_plan_info = serializers.SerializerMethodField()
    
    def get_item_plan_info(self, obj):
        if hasattr(obj, 'item_plan') and obj.item_plan:
            return {
                'id': obj.item_plan.id,
                'servicio': obj.item_plan.servicio.nombre,
                'precio': str(obj.item_plan.precio_total),
                'plan_titulo': obj.item_plan.plan.titulo,
                'estado': obj.item_plan.get_estado_display()
            }
        return None
```

### **4. Endpoint para vincular cita con ítem**

```python
# agenda/views.py

@action(detail=True, methods=['post'])
def vincular_item_plan(self, request, pk=None):
    """
    POST /api/agenda/citas/{id}/vincular_item_plan/
    Body: {"item_plan_id": 123}
    """
    cita = self.get_object()
    item_id = request.data.get('item_plan_id')
    
    if not item_id:
        return Response({'error': 'item_plan_id requerido'}, 
                       status=400)
    
    try:
        item = ItemPlanTratamiento.objects.get(
            id=item_id,
            plan__paciente=cita.paciente
        )
        
        # Verificar que el ítem no esté vinculado a otra cita
        if hasattr(item, 'cita') and item.cita:
            return Response({'error': 'Este ítem ya está vinculado a otra cita'}, 
                           status=400)
        
        # Vincular
        item.cita = cita
        item.save()
        
        return Response({
            'message': 'Ítem vinculado exitosamente',
            'item': ItemPlanTratamientoSerializer(item).data
        })
        
    except ItemPlanTratamiento.DoesNotExist:
        return Response({'error': 'Ítem no encontrado'}, 
                       status=404)
```

### **5. Al atender cita, completar ítem**

```python
# agenda/views.py

@action(detail=True, methods=['post'])
def atender(self, request, pk=None):
    """POST /api/agenda/citas/{id}/atender/"""
    cita = self.get_object()
    
    # ... lógica existente ...
    
    # NUEVO: Si tiene ítem del plan vinculado, marcarlo como completado
    if hasattr(cita, 'item_plan') and cita.item_plan:
        cita.item_plan.marcar_como_completado()
        cita.item_plan.plan.actualizar_progreso()
    
    # ... continuar con lógica existente ...
```

---

## 🎨 Cambios necesarios en el Frontend

### **1. Vista de Agenda mejorada**

```tsx
// Mostrar badge si la cita tiene ítem del plan vinculado
{cita.item_plan_info && (
  <Badge color="primary">
    Plan: {cita.item_plan_info.plan_titulo}
  </Badge>
)}
```

### **2. Modal de detalle de cita**

```tsx
{cita.item_plan_info && (
  <Card>
    <CardHeader>Tratamiento del Plan</CardHeader>
    <CardBody>
      <p>Servicio: {cita.item_plan_info.servicio}</p>
      <p>Precio: {cita.item_plan_info.precio}</p>
      <p>Estado: {cita.item_plan_info.estado}</p>
    </CardBody>
  </Card>
)}
```

### **3. Al crear cita, permitir seleccionar ítem del plan**

```tsx
// Obtener ítems pendientes del plan del paciente
const { data: itemsPendientes } = useQuery(
  ['items-pendientes', pacienteId],
  () => planesService.obtenerItemsPendientes(pacienteId)
);

<Select 
  label="Vincular con ítem del plan (opcional)"
  options={itemsPendientes}
  onChange={setItemPlanId}
/>
```

---

## 📊 Resumen de Beneficios

| Antes | Después |
|-------|---------|
| ❌ Citas y planes separados | ✅ Citas vinculadas con ítems del plan |
| ❌ Progreso manual del plan | ✅ Progreso automático al atender |
| ❌ No se ve el plan en agenda | ✅ Agenda muestra info del plan |
| ❌ Odontólogo no sabe qué hacer | ✅ Agenda muestra servicio a realizar |

---

## 🚀 Implementación Rápida (Mínima)

Si quieres implementar solo lo esencial:

1. **Agregar campo `cita` a ItemPlanTratamiento** ✅
2. **Migración** ✅  
3. **En frontend: Al atender cita, preguntar si completar ítem del plan** ✅

Esto ya permitiría vincular manualmente y hacer progreso.

---

## 🎯 Alternativa SIMPLE sin modificar modelos

Si NO quieres modificar el modelo ahora:

**Usar el campo `episodio` que ya existe en ItemPlanTratamiento:**

```python
# Al crear episodio desde una cita:
episodio = EpisodioAtencion.objects.create(
    historial=historial,
    cita=cita,
    # ... otros campos ...
)

# Vincular con ítem del plan
if item_plan_id:
    item = ItemPlanTratamiento.objects.get(id=item_plan_id)
    item.episodio = episodio  # ¡Ya existe este campo!
    item.marcar_como_completado()
    item.plan.actualizar_progreso()
```

Esto funciona AHORA sin cambios en el modelo! 🎉

---

## ¿Cuál prefieres implementar?

1. **Opción Simple**: Usar campo `episodio` existente (sin cambios de modelo)
2. **Opción Completa**: Agregar campo `cita` para mayor control
