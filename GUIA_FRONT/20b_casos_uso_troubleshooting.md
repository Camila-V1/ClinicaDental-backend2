# 🔍 Casos de Uso y Troubleshooting - Atención de Citas

## 📋 Índice
1. [Casos de Uso Comunes](#casos-de-uso-comunes)
2. [Debugging y Logs](#debugging-y-logs)
3. [Errores Comunes](#errores-comunes)
4. [Testing Manual](#testing-manual)

---

## 🎯 Casos de Uso Comunes

### Caso 1: Cita Normal de Consulta General

**Escenario:**
- Paciente agenda cita tipo CONSULTA
- Odontólogo atiende sin vincular a plan

**Pasos:**
1. Paciente llama y secretaria agenda cita tipo CONSULTA
2. Odontólogo ve lista de citas del día
3. Click en "🩺 Atender" → Backend marca como ATENDIDA
4. Modal se abre con campos vacíos
5. Odontólogo:
   - Selecciona servicio "Consulta General"
   - NO selecciona plan (campo opcional vacío)
   - Escribe diagnóstico: "Caries en molar inferior derecho"
   - Escribe procedimiento: "Evaluación clínica. Se recomienda resina"
   - Agrega notas privadas: "Paciente ansioso"
6. Guardar → Episodio creado sin vinculación a plan

**Resultado Esperado:**
```json
{
  "id": 150,
  "historial_clinico": 45,
  "servicio": 1,
  "item_plan_tratamiento": null,  // ← Sin vincular
  "diagnostico": "Caries en molar inferior derecho",
  "descripcion_procedimiento": "Evaluación clínica. Se recomienda resina",
  "notas_privadas": "Paciente ansioso"
}
```

---

### Caso 2: Cita Normal con Vinculación a Plan Existente

**Escenario:**
- Paciente tiene plan "Rehabilitación Completa" ACEPTADO
- Agenda cita tipo LIMPIEZA
- Durante la atención, odontólogo vincula a ítem del plan

**Pasos:**
1. Paciente agenda cita tipo LIMPIEZA (no vinculada a plan inicialmente)
2. Odontólogo atiende la cita
3. Modal se abre en modo normal (campos editables)
4. Odontólogo:
   - En dropdown "Vincular a Plan" selecciona:
     - Plan: "Rehabilitación Completa"
     - Ítem: "Profilaxis (EN_PROGRESO)"
   - Selecciona servicio "Limpieza Dental"
   - Completa diagnóstico y procedimiento
5. Guardar → Episodio vinculado al plan

**Resultado Esperado:**
```json
{
  "id": 151,
  "servicio": 5,
  "item_plan_tratamiento": 32,  // ← Vinculado a ítem del plan
  "diagnostico": "Limpieza dental completa",
  "descripcion_procedimiento": "Profilaxis con ultrasonido..."
}
```

Y el ítem del plan queda actualizado:
```json
{
  "id": 32,
  "estado": "COMPLETADO",  // ← Marcado como completado
  "sesiones_completadas": 1
}
```

---

### Caso 3: Cita Vinculada a Plan (Tipo PLAN)

**Escenario:**
- Paciente tiene plan "Ortodoncia" EN_PROGRESO
- Agenda cita tipo PLAN vinculada a "Consulta de control ortodóntico"
- Odontólogo atiende y modal muestra info pre-llenada

**Pasos:**
1. Paciente (desde su portal o vía secretaria) agenda cita:
   ```json
   {
     "motivo_tipo": "PLAN",
     "item_plan": 28,
     "motivo": "Consulta de control ortodóntico - Mes 3"
   }
   ```

2. Backend crea cita con vinculación:
   ```json
   {
     "id": 92,
     "es_cita_plan": true,
     "item_plan": 28,
     "item_plan_info": {
       "servicio_id": 8,
       "servicio_nombre": "Consulta Ortodóntica",
       "plan_id": 18,
       "plan_nombre": "Ortodoncia Completa",
       "estado": "EN_PROGRESO",
       "notas": "Control mensual, ajuste de brackets"
     }
   }
   ```

3. Odontólogo click "Atender" → Backend:
   - Marca cita como ATENDIDA
   - Marca ítem del plan como COMPLETADO
   - Devuelve cita actualizada con item_plan_info

4. Modal se abre en **modo solo lectura**:
   ```
   ┌────────────────────────────────────────────────────┐
   │ ✅ Cita Vinculada a Plan de Tratamiento           │
   ├────────────────────────────────────────────────────┤
   │ 📋 Plan: Ortodoncia Completa                       │
   │ 🦷 Tratamiento: Consulta Ortodóntica               │
   │ 📝 Notas: Control mensual, ajuste de brackets     │
   └────────────────────────────────────────────────────┘
   ```

5. Odontólogo solo necesita:
   - Confirmar diagnóstico: "Control ortodóntico. Ajuste en sector anterior"
   - Escribir procedimiento: "Revisión de tracción dental. Ajuste de ligaduras..."
   - Notas privadas: "Paciente cumple con higiene"

6. Guardar → Episodio creado con vinculación automática

**Resultado Esperado:**
```json
{
  "id": 152,
  "servicio": 8,                 // ← Pre-llenado automáticamente
  "item_plan_tratamiento": 28,   // ← Pre-llenado automáticamente
  "diagnostico": "Control ortodóntico. Ajuste en sector anterior",
  "descripcion_procedimiento": "Revisión de tracción dental..."
}
```

---

### Caso 4: Urgencia Fuera de Plan

**Escenario:**
- Paciente llama con dolor agudo
- Agenda cita tipo URGENCIA
- NO se vincula a ningún plan

**Pasos:**
1. Secretaria agenda cita URGENCIA
2. Odontólogo atiende inmediatamente
3. Modal en modo normal
4. Selecciona servicio "Atención de Urgencia"
5. Diagnóstico: "Pulpitis aguda en molar superior izquierdo"
6. Procedimiento: "Apertura de cámara pulpar, medicación temporal"
7. Guardar

**Resultado:**
- Episodio creado sin vinculación a plan
- Paciente puede recibir factura separada
- Posible creación de nuevo plan posteriormente

---

## 🐛 Debugging y Logs

### Logs en el Frontend

#### 1. Verificar Datos de la Cita

```typescript
// AgendaCitas.tsx - handleAtender()
const handleAtender = async (cita: Cita) => {
  console.group('🩺 ATENDIENDO CITA');
  console.log('ID Cita:', cita.id);
  console.log('Tipo:', cita.motivo_tipo);
  console.log('Es cita de plan:', cita.es_cita_plan);
  console.log('Item Plan ID:', cita.item_plan);
  console.log('Item Plan Info:', cita.item_plan_info);
  console.groupEnd();
  
  try {
    const response = await axiosInstance.post(/* ... */);
    
    console.group('✅ RESPUESTA BACKEND');
    console.log('Estado cita:', response.data.cita.estado);
    console.log('Item plan info actualizada:', response.data.cita.item_plan_info);
    if (response.data.item_plan_completado) {
      console.log('✅ Ítem completado:', response.data.item_plan_completado);
    }
    console.groupEnd();
  } catch (error) {
    console.error('❌ ERROR:', error);
  }
};
```

#### 2. Verificar Props del Modal

```typescript
// ModalRegistrarEpisodio.tsx
useEffect(() => {
  if (isOpen) {
    console.group('📝 MODAL ABIERTO');
    console.log('Paciente:', pacienteNombre);
    console.log('Es cita de plan:', esCitaPlan);
    console.log('Servicio ID:', servicioId);
    console.log('Item Plan ID:', itemPlanId);
    console.log('Item Plan Info:', itemPlanInfo);
    console.groupEnd();
  }
}, [isOpen]);
```

#### 3. Verificar Estado del Formulario

```typescript
// ModalRegistrarEpisodio.tsx
useEffect(() => {
  console.log('📋 Estado del formulario:', formData);
}, [formData]);
```

---

### Logs en el Backend

#### 1. Endpoint atender()

```python
# agenda/views.py
@action(detail=True, methods=['post'])
def atender(self, request, pk=None):
    cita = self.get_object()
    
    print(f"🩺 ATENDIENDO CITA #{cita.id}")
    print(f"   Tipo: {cita.motivo_tipo}")
    print(f"   Es cita de plan: {cita.es_cita_plan}")
    print(f"   Item plan: {cita.item_plan_id if cita.item_plan else None}")
    
    cita.estado = 'ATENDIDA'
    cita.save()
    
    if cita.es_cita_plan and marcar_completado and cita.item_plan:
        print(f"   ✅ Marcando ítem #{cita.item_plan.id} como COMPLETADO")
        cita.item_plan.estado = 'COMPLETADO'
        cita.item_plan.save()
    
    return Response(...)
```

#### 2. Serializer get_item_plan_info()

```python
# agenda/serializers.py
def get_item_plan_info(self, obj):
    if not obj.item_plan:
        print(f"   ℹ️ Cita #{obj.id} no tiene item_plan vinculado")
        return None
    
    item = obj.item_plan
    print(f"   📋 Cita #{obj.id} → Item Plan #{item.id}")
    print(f"      Servicio: {item.servicio.nombre if item.servicio else 'N/A'}")
    print(f"      Plan: {item.plan.titulo}")
    
    return { ... }
```

---

## ❌ Errores Comunes

### Error 1: Modal No Pre-llena Servicio en Citas de Plan

**Síntoma:**
```
Modal se abre pero dropdown de servicio está vacío
```

**Causa:**
```typescript
// AgendaCitas.tsx - INCORRECTO
servicioId={citaSeleccionada.servicio ?? null}  // ❌ servicio no existe en cita
```

**Solución:**
```typescript
// AgendaCitas.tsx - CORRECTO
servicioId={citaSeleccionada.item_plan_info?.servicio_id ?? null}  // ✅
```

---

### Error 2: Backend No Devuelve item_plan_info

**Síntoma:**
```json
{
  "cita": {
    "id": 82,
    "es_cita_plan": true,
    "item_plan": 25,
    "item_plan_info": null  // ❌ Debería tener datos
  }
}
```

**Causa:**
- Serializer no incluye `item_plan_info` en `fields`
- Método `get_item_plan_info()` no está definido

**Solución:**
```python
# agenda/serializers.py
class CitaSerializer(serializers.ModelSerializer):
    item_plan_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Cita
        fields = [
            'id', 'estado', 'es_cita_plan', 'item_plan',
            'item_plan_info',  # ← Debe estar en fields
            # ...
        ]
    
    def get_item_plan_info(self, obj):
        if not obj.item_plan:
            return None
        item = obj.item_plan
        return {
            'servicio_id': item.servicio.id if item.servicio else None,
            'servicio_nombre': item.servicio.nombre if item.servicio else None,
            # ...
        }
```

---

### Error 3: Modal Muestra Dropdown en Lugar de Solo Lectura

**Síntoma:**
- Modal siempre muestra dropdowns editables
- Nunca muestra la sección verde de "Cita Vinculada a Plan"

**Causa:**
```typescript
// ModalRegistrarEpisodio.tsx - INCORRECTO
{esCitaPlan ? (
  <PlanInfoReadOnly />
) : (
  <CamposEditables />
)}
```
Pero `esCitaPlan` es `false` o `undefined`

**Diagnóstico:**
```typescript
useEffect(() => {
  console.log('esCitaPlan:', esCitaPlan);           // false
  console.log('itemPlanInfo:', itemPlanInfo);       // null
  console.log('servicioId:', servicioId);           // null
}, [isOpen]);
```

**Solución:**
Verificar que AgendaCitas.tsx pasa las props correctas:
```typescript
esCitaPlan={citaSeleccionada.es_cita_plan ?? false}     // ✅
itemPlanInfo={citaSeleccionada.item_plan_info ?? null}   // ✅
```

---

### Error 4: 400 Bad Request al Crear Episodio

**Síntoma:**
```json
{
  "error": "servicio es requerido"
}
```

**Causa:**
```typescript
const formData = {
  servicio: null,  // ❌ Está null cuando debería tener valor
  // ...
}
```

**Diagnóstico:**
```typescript
useEffect(() => {
  console.log('Form Data al enviar:', formData);
  // Output: { servicio: null, ... }
}, [formData]);
```

**Solución:**
Asegurar que el efecto pre-llena correctamente:
```typescript
useEffect(() => {
  if (isOpen && esCitaPlan && servicioId) {
    console.log('Pre-llenando servicio:', servicioId);
    setFormData(prev => ({
      ...prev,
      servicio: servicioId  // ✅ Debe asignarse
    }));
  }
}, [isOpen, esCitaPlan, servicioId]);
```

---

### Error 5: Ítem del Plan No Se Marca como COMPLETADO

**Síntoma:**
- Cita queda como ATENDIDA ✅
- Episodio se crea correctamente ✅
- Pero ítem del plan sigue EN_PROGRESO ❌

**Causa:**
Request no envía `marcar_completado=true`:
```typescript
// INCORRECTO
await axiosInstance.post(`/api/agenda/citas/${id}/atender/`);
```

**Solución:**
```typescript
// CORRECTO
await axiosInstance.post(
  `/api/agenda/citas/${id}/atender/`,
  { marcar_completado: true }  // ← Agregar parámetro
);
```

O en el backend, hacerlo por defecto:
```python
# agenda/views.py
@action(detail=True, methods=['post'])
def atender(self, request, pk=None):
    marcar_completado = request.data.get('marcar_completado', True)  # ← Default True
    # ...
```

---

## 🧪 Testing Manual

### Test 1: Flujo Completo Cita Normal

**Checklist:**
- [ ] Crear cita tipo CONSULTA
- [ ] Atender cita
- [ ] Modal se abre con campos vacíos
- [ ] Seleccionar servicio
- [ ] Completar diagnóstico y procedimiento
- [ ] Guardar episodio
- [ ] Verificar episodio en historial del paciente
- [ ] Verificar estado de cita = ATENDIDA

**Comando de verificación:**
```bash
# Backend logs
python manage.py runserver

# Buscar en logs:
# "🩺 ATENDIENDO CITA #XX"
# "✅ Episodio creado con ID #YY"
```

---

### Test 2: Flujo Completo Cita de Plan

**Preparación:**
```python
# Crear plan y cita vinculada
plan = PlanTratamiento.objects.create(
    paciente_id=5,
    titulo='Test Plan',
    estado='EN_PROGRESO'
)

item = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio_id=3,
    estado='EN_PROGRESO'
)

cita = Cita.objects.create(
    paciente_id=5,
    odontologo_id=1,
    fecha_hora='2025-11-18 14:00',
    motivo_tipo='PLAN',
    item_plan=item
)
```

**Checklist:**
- [ ] Ver cita en lista
- [ ] Atender cita
- [ ] Backend marca ítem como COMPLETADO
- [ ] Modal se abre con info pre-llenada
- [ ] Verificar sección verde "Cita Vinculada"
- [ ] Plan y servicio en modo solo lectura
- [ ] Completar solo diagnóstico y procedimiento
- [ ] Guardar episodio
- [ ] Verificar episodio vinculado al plan
- [ ] Verificar ítem.estado = COMPLETADO

---

### Test 3: Vinculación Manual Durante Atención

**Checklist:**
- [ ] Crear cita tipo LIMPIEZA (sin plan)
- [ ] Crear plan con ítem EN_PROGRESO
- [ ] Atender cita
- [ ] Modal en modo normal
- [ ] Seleccionar plan y ítem en dropdown
- [ ] Seleccionar servicio
- [ ] Guardar episodio
- [ ] Verificar episodio.item_plan_tratamiento apunta al ítem
- [ ] Verificar ítem.estado = COMPLETADO

---

## 🔧 Herramientas de Debugging

### 1. React DevTools
- Inspeccionar props del modal
- Ver estado de formData en tiempo real
- Verificar re-renders

### 2. Network Tab
```
POST /api/agenda/citas/82/atender/
Response:
{
  "cita": {
    "item_plan_info": {
      "servicio_id": 3  ← Verificar que existe
    }
  }
}
```

### 3. Django Debug Toolbar
- Ver queries SQL ejecutadas
- Verificar que se actualiza item_plan.estado
- Ver serializer data

### 4. Console.log Estratégicos

**Ubicaciones clave:**
1. Antes de llamar `/atender/`
2. Después de recibir respuesta
3. Al abrir modal (verificar props)
4. Al inicializar formData
5. Antes de enviar formulario

---

## 📊 Matriz de Casos de Prueba

| Tipo Cita | Plan Existente | Vinculación | Resultado Esperado |
|-----------|----------------|-------------|-------------------|
| CONSULTA  | No             | No          | Episodio sin plan |
| CONSULTA  | Sí             | Manual      | Episodio vinculado, ítem COMPLETADO |
| LIMPIEZA  | Sí             | Manual      | Episodio vinculado, ítem COMPLETADO |
| URGENCIA  | Sí             | No          | Episodio sin plan (urgencia no planeada) |
| PLAN      | Sí             | Automática  | Episodio vinculado, modal solo lectura, ítem COMPLETADO |
| REVISION  | No             | No          | Episodio sin plan |

---

## 🎯 Resumen de Validaciones

### Frontend:
- ✅ `esCitaPlan` correctamente pasado
- ✅ `servicioId` viene de `item_plan_info?.servicio_id`
- ✅ `itemPlanInfo` completo pasado al modal
- ✅ Modal detecta correctamente modo solo lectura
- ✅ Formulario pre-llena campos automáticamente

### Backend:
- ✅ Endpoint `/atender/` marca cita como ATENDIDA
- ✅ Marca ítem del plan como COMPLETADO si aplica
- ✅ Serializer incluye `item_plan_info` con `servicio_id`
- ✅ Endpoint de episodios acepta `item_plan_tratamiento`

¡Con estos casos de uso y guías de troubleshooting, deberías poder implementar y debuggear el sistema completo! 🚀
