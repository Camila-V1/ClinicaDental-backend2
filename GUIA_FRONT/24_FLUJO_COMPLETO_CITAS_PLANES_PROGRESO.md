# 🏥 FLUJO COMPLETO: Citas Vinculadas a Planes de Tratamiento

## 🎯 Pregunta: ¿Cómo Funciona el Sistema de Progreso?

Cuando un paciente tiene un plan de tratamiento, el flujo es así:

---

## 📋 Paso a Paso del Flujo Completo

### 1️⃣ Odontólogo Crea el Plan de Tratamiento

```python
# El odontólogo crea un plan con varios ítems
plan = PlanDeTratamiento.objects.create(
    paciente=paciente,
    odontologo=odontologo,
    titulo="Plan de Ortodoncia Completa",
    estado='PROPUESTO'  # Inicialmente PROPUESTO
)

# Agrega los tratamientos al plan (cada uno es un ítem)
item1 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_brackets,  # "Instalación de brackets"
    orden=1,
    estado='PENDIENTE'
)

item2 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_control,  # "Control mensual"
    orden=2,
    estado='PENDIENTE'
)

item3 = ItemPlanTratamiento.objects.create(
    plan=plan,
    servicio=servicio_retiro,  # "Retiro de brackets"
    orden=3,
    estado='PENDIENTE'
)
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (PROPUESTO)
├─ Ítem 1: Instalación de brackets (PENDIENTE)
├─ Ítem 2: Control mensual (PENDIENTE)
└─ Ítem 3: Retiro de brackets (PENDIENTE)
```

---

### 2️⃣ Paciente Acepta el Plan

El paciente revisa y acepta el plan:

```python
plan.estado = 'ACEPTADO'
plan.save()
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (ACEPTADO) ✅
├─ Ítem 1: Instalación de brackets (PENDIENTE)
├─ Ítem 2: Control mensual (PENDIENTE)
└─ Ítem 3: Retiro de brackets (PENDIENTE)
```

---

### 3️⃣ Paciente Agenda Cita para UN Ítem Específico

**Aquí está la clave:** El paciente agenda una cita **para UN ítem específico del plan**.

```python
# El paciente (o secretaria) crea la cita
cita = Cita.objects.create(
    paciente=paciente,
    odontologo=odontologo,
    fecha_hora='2025-11-20 14:00',
    motivo_tipo='PLAN',  # ← Indica que es cita de plan
    motivo='Instalación de brackets según plan',
    item_plan=item1,  # ← VINCULA LA CITA AL ÍTEM #1
    estado='PENDIENTE'
)
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (ACEPTADO)
├─ Ítem 1: Instalación de brackets (PENDIENTE) 🔗 Cita #82 programada
├─ Ítem 2: Control mensual (PENDIENTE)
└─ Ítem 3: Retiro de brackets (PENDIENTE)
```

---

### 4️⃣ Odontólogo Atiende la Cita

El día de la cita, el odontólogo:

#### A) Marca la cita como ATENDIDA

```python
# POST /api/agenda/citas/82/atender/
cita.estado = 'ATENDIDA'
cita.save()

# El backend automáticamente marca el ítem como COMPLETADO
if cita.es_cita_plan and cita.item_plan:
    cita.item_plan.estado = 'COMPLETADO'
    cita.item_plan.fecha_realizada = timezone.now()
    cita.item_plan.save()
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (EN_PROGRESO) ← Cambió automáticamente
├─ Ítem 1: Instalación de brackets (COMPLETADO) ✅
├─ Ítem 2: Control mensual (PENDIENTE)
└─ Ítem 3: Retiro de brackets (PENDIENTE)

Progreso: 1/3 (33%)
```

#### B) Registra el Episodio Clínico

```python
# POST /api/historial/episodios/
episodio = EpisodioAtencion.objects.create(
    historial_clinico=historial,
    servicio=item1.servicio,  # "Instalación de brackets"
    item_plan_tratamiento=item1,  # ← Vincula al ítem del plan
    motivo_consulta='Instalación de brackets',
    diagnostico='Maloclusión clase II',
    descripcion_procedimiento='Instalación de brackets metálicos...',
    odontologo=odontologo
)
```

**Resultado:**
```
Historial Clínico del Paciente:
└─ Episodio #15: "Instalación de brackets"
   ├─ Vinculado a: Plan "Ortodoncia Completa" → Ítem 1
   ├─ Diagnóstico: Maloclusión clase II
   └─ Procedimiento: Instalación de brackets metálicos...
```

---

### 5️⃣ Paciente Agenda la Siguiente Cita

Para el siguiente tratamiento del plan:

```python
# Cita para el ítem #2
cita2 = Cita.objects.create(
    paciente=paciente,
    odontologo=odontologo,
    fecha_hora='2025-12-20 14:00',
    motivo_tipo='PLAN',
    motivo='Control mensual de ortodoncia',
    item_plan=item2,  # ← VINCULA AL ÍTEM #2
    estado='PENDIENTE'
)
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (EN_PROGRESO)
├─ Ítem 1: Instalación de brackets (COMPLETADO) ✅
├─ Ítem 2: Control mensual (PENDIENTE) 🔗 Cita #85 programada
└─ Ítem 3: Retiro de brackets (PENDIENTE)

Progreso: 1/3 (33%)
```

---

### 6️⃣ Se Repite el Proceso

Cuando se atiende la cita del ítem #2:

```python
# Atender cita
cita2.estado = 'ATENDIDA'
cita2.save()

# Marca ítem como completado
item2.estado = 'COMPLETADO'
item2.save()

# Actualiza progreso del plan
plan.actualizar_progreso()  # Calcula 2/3 = 66%
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (EN_PROGRESO)
├─ Ítem 1: Instalación de brackets (COMPLETADO) ✅
├─ Ítem 2: Control mensual (COMPLETADO) ✅
└─ Ítem 3: Retiro de brackets (PENDIENTE)

Progreso: 2/3 (66%)
```

---

### 7️⃣ Plan Completo

Cuando se completan TODOS los ítems:

```python
# Atender última cita
cita3.estado = 'ATENDIDA'
item3.estado = 'COMPLETADO'

# El plan se marca automáticamente como COMPLETADO
if plan.todos_items_completados():
    plan.estado = 'COMPLETADO'
    plan.fecha_finalizacion = timezone.now()
    plan.save()
```

**Resultado:**
```
Plan: "Ortodoncia Completa" (COMPLETADO) 🎉
├─ Ítem 1: Instalación de brackets (COMPLETADO) ✅
├─ Ítem 2: Control mensual (COMPLETADO) ✅
└─ Ítem 3: Retiro de brackets (COMPLETADO) ✅

Progreso: 3/3 (100%) 🎉
```

---

## 🔑 Conceptos Clave

### 1. **Un Plan Tiene Múltiples Ítems**
```python
PlanDeTratamiento (1) ──────► ItemPlanTratamiento (N)
     "Plan Ortodoncia"             │
                                   ├─ Ítem 1: Instalación
                                   ├─ Ítem 2: Control 1
                                   ├─ Ítem 3: Control 2
                                   └─ Ítem 4: Retiro
```

### 2. **Cada Cita se Vincula a UN Ítem**
```python
Cita ──────► ItemPlanTratamiento
  │              │
  │              └─ Pertenece a ──► PlanDeTratamiento
  │
  └─ Al atender: Marca el ítem como COMPLETADO
```

### 3. **El Progreso se Calcula Automáticamente**
```python
progreso = items_completados / total_items * 100

Ejemplo:
- 1/3 completados = 33%
- 2/3 completados = 66%
- 3/3 completados = 100% → Plan COMPLETADO
```

---

## 📊 Diagrama de Flujo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                  CICLO DE VIDA DEL PLAN                      │
└─────────────────────────────────────────────────────────────┘

1. CREAR PLAN (Odontólogo)
   └─ Plan: PROPUESTO
      ├─ Ítem 1: PENDIENTE
      ├─ Ítem 2: PENDIENTE
      └─ Ítem 3: PENDIENTE

2. ACEPTAR PLAN (Paciente)
   └─ Plan: ACEPTADO ✅

3. AGENDAR CITA PARA ÍTEM 1 (Paciente)
   └─ Cita #82 → item_plan = Ítem 1

4. ATENDER CITA (Odontólogo)
   ├─ Cita: ATENDIDA ✅
   ├─ Ítem 1: COMPLETADO ✅
   ├─ Plan: EN_PROGRESO (automático)
   └─ Episodio: Creado con vinculación al ítem

5. AGENDAR CITA PARA ÍTEM 2 (Paciente)
   └─ Cita #85 → item_plan = Ítem 2

6. ATENDER CITA (Odontólogo)
   ├─ Cita: ATENDIDA ✅
   ├─ Ítem 2: COMPLETADO ✅
   ├─ Progreso: 66%
   └─ Episodio: Creado

7. COMPLETAR TODOS LOS ÍTEMS
   └─ Plan: COMPLETADO 🎉
```

---

## 💡 Ejemplo Real Paso a Paso

### Escenario: Plan de Rehabilitación

```python
# 1. Plan creado con 4 tratamientos
Plan: "Rehabilitación Completa"
├─ Ítem 1: Endodoncia pieza 26 ($150)
├─ Ítem 2: Corona pieza 26 ($300)
├─ Ítem 3: Resina pieza 15 ($80)
└─ Ítem 4: Limpieza general ($60)

Total: $590
Estado: PROPUESTO
```

```python
# 2. Paciente acepta
Estado → ACEPTADO
```

```python
# 3. Paciente agenda cita para endodoncia
POST /api/agenda/citas/agendar/
{
  "odontologo": 1,
  "fecha_hora": "2025-11-25 10:00",
  "motivo_tipo": "PLAN",
  "motivo": "Endodoncia según plan de tratamiento",
  "item_plan": 1  // ← Vincula al ítem de endodoncia
}

Cita creada: #90 → vinculada a Ítem 1
```

```python
# 4. Día de la cita - Odontólogo atiende
POST /api/agenda/citas/90/atender/

Backend automáticamente:
- Marca cita como ATENDIDA
- Marca Ítem 1 como COMPLETADO
- Cambia plan a EN_PROGRESO
- Calcula progreso: 1/4 = 25%
```

```python
# 5. Odontólogo registra episodio
POST /api/historial/episodios/
{
  "historial_clinico": 5,
  "servicio": 3,  // Endodoncia
  "item_plan_tratamiento": 1,  // ← Vincula al ítem
  "diagnostico": "Pulpitis irreversible",
  "descripcion_procedimiento": "Endodoncia pieza 26..."
}

Episodio creado y vinculado al plan
```

```python
# 6. Estado actual
Plan: "Rehabilitación Completa" (EN_PROGRESO)
├─ Ítem 1: Endodoncia (COMPLETADO) ✅ - Episodio #45
├─ Ítem 2: Corona (PENDIENTE)
├─ Ítem 3: Resina (PENDIENTE)
└─ Ítem 4: Limpieza (PENDIENTE)

Progreso: 25% (1/4 completado)
Monto pagado: $150 / $590
```

---

## 🔍 ¿Cómo se Marca el Progreso en el Código?

### Backend: `agenda/views.py` - Endpoint `atender()`

```python
@action(detail=True, methods=['post'])
def atender(self, request, pk=None):
    cita = self.get_object()
    
    with transaction.atomic():
        # 1. Marcar cita como atendida
        cita.estado = 'ATENDIDA'
        cita.save()
        
        # 2. Si es cita de plan, marcar ítem como completado
        if cita.es_cita_plan and cita.item_plan:
            item = cita.item_plan
            
            # Marcar ítem como completado
            item.estado = 'COMPLETADO'
            item.fecha_realizada = timezone.now()
            item.save()
            
            # 3. Actualizar estado del plan automáticamente
            plan = item.plan
            
            # Si es el primer ítem completado, cambiar a EN_PROGRESO
            if plan.estado == 'ACEPTADO':
                plan.estado = 'EN_PROGRESO'
                plan.fecha_inicio = timezone.now()
                plan.save()
            
            # Si se completaron TODOS los ítems, marcar plan como COMPLETADO
            if plan.items.filter(estado='COMPLETADO').count() == plan.items.count():
                plan.estado = 'COMPLETADO'
                plan.fecha_finalizacion = timezone.now()
                plan.save()
```

---

## 📊 Resumen en Tabla

| Acción | Actor | Resultado |
|--------|-------|-----------|
| Crear plan con ítems | Odontólogo | Plan: PROPUESTO, Ítems: PENDIENTE |
| Aceptar plan | Paciente | Plan: ACEPTADO |
| Agendar cita para ítem X | Paciente | Cita vinculada al ítem X |
| Atender cita | Odontólogo | Cita: ATENDIDA, Ítem: COMPLETADO |
| | | Plan: EN_PROGRESO (automático) |
| Registrar episodio | Odontólogo | Episodio vinculado al ítem |
| Completar todos los ítems | Sistema | Plan: COMPLETADO (automático) |

---

## 🎯 Respuestas Directas a tu Pregunta

### ¿Al sacar cita con un plan se saca cita para un ítem?
**Sí**, cada cita se vincula a **UN ítem específico del plan**. No se agenda "el plan completo", sino cada tratamiento individual.

### ¿Cómo marca el progreso del plan?
Se marca **automáticamente** cuando el odontólogo atiende la cita:
1. Cita → ATENDIDA
2. Ítem del plan → COMPLETADO
3. Plan → Recalcula progreso (items_completados / total_items)

### ¿Cómo marca el avance del tratamiento?
Cada vez que se completa un ítem:
- **Progreso numérico:** 1/5, 2/5, 3/5... (20%, 40%, 60%...)
- **Estado del plan:** PROPUESTO → ACEPTADO → EN_PROGRESO → COMPLETADO
- **Historial:** Cada episodio queda vinculado al ítem correspondiente

---

## 💡 Analogía Simple

Imagina que el plan de tratamiento es como una **lista de tareas**:

```
Plan: "Arreglar la casa"
☐ Pintar la sala
☐ Arreglar la cocina
☐ Cambiar las ventanas
```

Cada vez que agendas una cita, estás diciendo:
- "Quiero hacer la tarea de PINTAR LA SALA el 25 de noviembre"

Cuando el odontólogo te atiende:
- ✅ Pintar la sala (completado)
- ☐ Arreglar la cocina
- ☐ Cambiar las ventanas

Progreso: 33% ✅

¡Así funciona el sistema! 🎉
