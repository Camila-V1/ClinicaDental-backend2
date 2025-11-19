# 🎯 LÓGICA DE DETECCIÓN: Tipos de Citas y Modal

## 📋 Tabla de Decisión

El frontend debe usar esta tabla para determinar qué mostrar en el modal:

| `es_cita_plan` | `item_plan` | `item_plan_info` | Tipo de Cita | Acción del Modal |
|----------------|-------------|------------------|--------------|------------------|
| `false`        | `null`      | `null`           | **CITA SIMPLE** | Mostrar selectores editables |
| `true`         | `null`      | `null`           | ⚠️ ERROR | Configuración inválida |
| `true`         | `9`         | `null`           | **PLAN SIN INFO** | Cargar planes y mostrar selectores |
| `true`         | `9`         | `{...}`          | **PLAN COMPLETO** | Mostrar info solo lectura ✅ |

---

## 🔍 Casos Detallados

### Caso 1: Cita Simple (Normal)

**Datos del Backend:**
```json
{
  "id": 82,
  "motivo_tipo": "CONSULTA",
  "es_cita_plan": false,
  "item_plan": null,
  "item_plan_info": null
}
```

**Lógica Frontend:**
```typescript
if (!esCitaPlan) {
  // Es una cita simple
  // Mostrar:
  // - Dropdown de planes (opcional)
  // - Dropdown de servicios (requerido)
  return <ModoSimple />;
}
```

**UI Esperada:**
```
┌─────────────────────────────────────────┐
│ 📋 Vincular a Plan (Opcional)           │
│ [  Seleccionar plan...  ▼]             │
│                                         │
│ 🦷 Servicio Realizado *                │
│ [  Seleccionar servicio...  ▼]         │
│                                         │
│ 🩺 Diagnóstico *                        │
│ [Textarea editable]                     │
└─────────────────────────────────────────┘
```

---

### Caso 2: Plan Sin Info (Vinculación Manual)

**Datos del Backend:**
```json
{
  "id": 83,
  "motivo_tipo": "PLAN",
  "es_cita_plan": true,
  "item_plan": 9,
  "item_plan_info": null  // ← Backend no envió info expandida
}
```

**⚠️ Por qué pasa esto:**
- Cita antigua creada antes de implementar `item_plan_info`
- Bug en el serializer del backend
- Item del plan fue eliminado después de crear la cita

**Lógica Frontend:**
```typescript
if (esCitaPlan && itemPlanId && !itemPlanInfo) {
  // Es cita de plan pero sin información expandida
  // Necesitamos cargar los planes y pre-seleccionar el item
  console.warn('⚠️ Cita de plan sin item_plan_info');
  
  // Cargar planes del backend
  cargarPlanes();
  
  // Mostrar selectores editables (como cita simple)
  // pero con el item_plan pre-seleccionado
  return <ModoVinculacionManual itemPlanId={itemPlanId} />;
}
```

**UI Esperada:**
```
┌─────────────────────────────────────────┐
│ ⚠️ Cita vinculada a plan pero sin info │
│                                         │
│ 📋 Plan de Tratamiento *                │
│ [  Plan Ortodoncia  ▼]                 │
│                                         │
│ 🦷 Tratamiento del Plan *               │
│ [  Item #9 - Consulta  ▼]              │
│     ↑ Pre-seleccionado                  │
│                                         │
│ 🩺 Diagnóstico *                        │
│ [Textarea editable]                     │
└─────────────────────────────────────────┘
```

---

### Caso 3: Plan Completo (Solo Lectura) ✅

**Datos del Backend:**
```json
{
  "id": 84,
  "motivo_tipo": "PLAN",
  "es_cita_plan": true,
  "item_plan": 9,
  "item_plan_info": {
    "id": 9,
    "servicio_id": 5,
    "servicio_nombre": "Endodoncia",
    "plan_id": 15,
    "plan_nombre": "Rehabilitación Completa",
    "notas": "Primera sesión de endodoncia",
    "estado": "EN_PROGRESO"
  }
}
```

**Lógica Frontend:**
```typescript
if (esCitaPlan && itemPlanInfo) {
  // ✅ Es cita de plan CON información completa
  // El paciente YA seleccionó el plan al agendar la cita
  // NO mostrar selectores, todo es solo lectura
  console.log('✅ Cita de plan con info completa');
  
  // Pre-llenar el formulario automáticamente
  setFormData({
    servicio: itemPlanInfo.servicio_id,
    item_plan_tratamiento: itemPlanId,
    // ... resto
  });
  
  // Mostrar info en modo solo lectura
  return <ModoSoloLectura itemPlanInfo={itemPlanInfo} />;
}
```

**UI Esperada:**
```
┌─────────────────────────────────────────┐
│ ✅ Cita Vinculada a Plan de Tratamiento│
├─────────────────────────────────────────┤
│ 📋 Plan: Rehabilitación Completa        │
│ 🦷 Tratamiento: Endodoncia              │
│ 📝 Notas: Primera sesión de endodoncia │
├─────────────────────────────────────────┤
│ ℹ️ Plan seleccionado por el paciente   │
└─────────────────────────────────────────┘

🩺 Diagnóstico * (EDITABLE)
[Textarea para que odontólogo escriba]

🔧 Procedimiento * (EDITABLE)
[Textarea para que odontólogo escriba]
```

---

## 🔐 Código TypeScript Correcto

### Archivo: `ModalRegistrarEpisodio.tsx`

```typescript
import { useEffect, useState } from 'react';

interface ItemPlanInfo {
  id: number;
  servicio_id: number;
  servicio_nombre: string;
  plan_id: number;
  plan_nombre: string;
  notas?: string;
  estado: string;
}

interface ModalProps {
  isOpen: boolean;
  esCitaPlan: boolean;
  itemPlanId: number | null;
  itemPlanInfo?: ItemPlanInfo | null;
  // ... otras props
}

export default function ModalRegistrarEpisodio({
  isOpen,
  esCitaPlan,
  itemPlanId,
  itemPlanInfo,
  // ... otras props
}: ModalProps) {
  
  const [formData, setFormData] = useState({
    servicio: null as number | null,
    item_plan_tratamiento: null as number | null,
    diagnostico: '',
    descripcion_procedimiento: '',
  });

  const [planes, setPlanes] = useState([]);
  const [mostrarSelectores, setMostrarSelectores] = useState(false);

  // ========================================
  // PASO 1: Determinar modo del modal
  // ========================================
  useEffect(() => {
    if (!isOpen) return;

    console.group('🔍 ANÁLISIS DE CITA');
    console.log('es_cita_plan:', esCitaPlan);
    console.log('item_plan_id:', itemPlanId);
    console.log('item_plan_info:', itemPlanInfo);
    
    // Caso 1: Cita Simple
    if (!esCitaPlan) {
      console.log('📌 TIPO: Cita Simple (normal)');
      console.log('→ Mostrar selectores editables');
      setMostrarSelectores(true);
      cargarPlanes(); // Para poder vincular opcionalmente
    }
    
    // Caso 2: Plan Sin Info
    else if (esCitaPlan && itemPlanId && !itemPlanInfo) {
      console.warn('⚠️ TIPO: Plan Sin Info (vincular manual)');
      console.log('→ Cargar planes y pre-seleccionar item');
      setMostrarSelectores(true);
      cargarPlanes();
      // El item se pre-seleccionará después de cargar planes
    }
    
    // Caso 3: Plan Completo ✅
    else if (esCitaPlan && itemPlanInfo) {
      console.log('✅ TIPO: Plan Completo (solo lectura)');
      console.log('→ Pre-llenar y mostrar info del plan');
      setMostrarSelectores(false); // NO mostrar selectores
      
      // Pre-llenar formulario automáticamente
      setFormData(prev => ({
        ...prev,
        servicio: itemPlanInfo.servicio_id,
        item_plan_tratamiento: itemPlanId,
        descripcion_procedimiento: itemPlanInfo.notas || ''
      }));
    }
    
    // Caso Error
    else {
      console.error('❌ TIPO: Configuración Inválida');
      console.error('→ es_cita_plan=true pero sin item_plan');
    }
    
    console.groupEnd();
  }, [isOpen, esCitaPlan, itemPlanId, itemPlanInfo]);

  // ========================================
  // PASO 2: Cargar planes (solo si necesario)
  // ========================================
  const cargarPlanes = async () => {
    try {
      const response = await fetch(`/api/planes/?paciente=${pacienteId}`);
      const data = await response.json();
      setPlanes(data);
      
      console.log(`📋 Planes cargados: ${data.length}`);
    } catch (error) {
      console.error('❌ Error al cargar planes:', error);
    }
  };

  // ========================================
  // PASO 3: Renderizado Condicional
  // ========================================
  return (
    <div className="modal">
      <h2>📝 Registrar Episodio</h2>
      
      {/* ============ MODO 1: Plan Completo (Solo Lectura) ============ */}
      {esCitaPlan && itemPlanInfo && (
        <div className="plan-info-readonly">
          <div className="alert alert-success">
            <strong>✅ Cita Vinculada a Plan</strong>
          </div>
          
          <div className="grid-2-cols">
            <div>
              <label>📋 Plan</label>
              <div className="readonly-field">
                {itemPlanInfo.plan_nombre}
              </div>
            </div>
            
            <div>
              <label>🦷 Tratamiento</label>
              <div className="readonly-field">
                {itemPlanInfo.servicio_nombre}
              </div>
            </div>
          </div>
          
          {itemPlanInfo.notas && (
            <div>
              <label>📝 Notas del Plan</label>
              <div className="readonly-field">
                {itemPlanInfo.notas}
              </div>
            </div>
          )}
          
          <p className="info-text">
            ℹ️ El paciente seleccionó este plan al agendar la cita.
          </p>
        </div>
      )}
      
      {/* ============ MODO 2 y 3: Selectores Editables ============ */}
      {mostrarSelectores && (
        <>
          {/* Dropdown de Planes */}
          <div className="form-group">
            <label>📋 Plan (Opcional)</label>
            <select
              value={formData.item_plan_tratamiento || ''}
              onChange={(e) => {
                const itemId = e.target.value ? Number(e.target.value) : null;
                setFormData({ ...formData, item_plan_tratamiento: itemId });
              }}
            >
              <option value="">Sin vincular a plan</option>
              {planes.map(plan => (
                <optgroup key={plan.id} label={plan.nombre}>
                  {plan.items?.map(item => (
                    <option 
                      key={item.id} 
                      value={item.id}
                      selected={item.id === itemPlanId} // ← Pre-seleccionar si coincide
                    >
                      {item.servicio_nombre} ({item.estado})
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
          
          {/* Dropdown de Servicios */}
          <div className="form-group">
            <label>🦷 Servicio *</label>
            <select
              value={formData.servicio || ''}
              onChange={(e) => {
                const servicioId = e.target.value ? Number(e.target.value) : null;
                setFormData({ ...formData, servicio: servicioId });
              }}
              required
            >
              <option value="">Seleccionar...</option>
              {servicios.map(s => (
                <option key={s.id} value={s.id}>{s.nombre}</option>
              ))}
            </select>
          </div>
        </>
      )}
      
      {/* ============ CAMPOS COMUNES (Siempre Editables) ============ */}
      <div className="form-group">
        <label>🩺 Diagnóstico *</label>
        <textarea
          value={formData.diagnostico}
          onChange={(e) => setFormData({ 
            ...formData, 
            diagnostico: e.target.value 
          })}
          required
        />
      </div>
      
      <div className="form-group">
        <label>🔧 Procedimiento *</label>
        <textarea
          value={formData.descripcion_procedimiento}
          onChange={(e) => setFormData({ 
            ...formData, 
            descripcion_procedimiento: e.target.value 
          })}
          required
        />
      </div>
      
      <button type="submit">💾 Guardar</button>
    </div>
  );
}
```

---

## 🧪 Ejemplos de Logs Esperados

### Cita Simple:
```
🔍 ANÁLISIS DE CITA
  es_cita_plan: false
  item_plan_id: null
  item_plan_info: null
  📌 TIPO: Cita Simple (normal)
  → Mostrar selectores editables
📋 Planes cargados: 3
```

### Plan Sin Info:
```
🔍 ANÁLISIS DE CITA
  es_cita_plan: true
  item_plan_id: 9
  item_plan_info: null
  ⚠️ TIPO: Plan Sin Info (vincular manual)
  → Cargar planes y pre-seleccionar item
📋 Planes cargados: 3
```

### Plan Completo:
```
🔍 ANÁLISIS DE CITA
  es_cita_plan: true
  item_plan_id: 9
  item_plan_info: { servicio_id: 5, plan_nombre: "Rehabilitación", ... }
  ✅ TIPO: Plan Completo (solo lectura)
  → Pre-llenar y mostrar info del plan
```

---

## ✅ Validaciones Recomendadas

### Backend (Ya Implementado):
```python
# agenda/serializers.py
def get_item_plan_info(self, obj):
    if not obj.item_plan:
        return None  # ← Es cita simple
    
    item = obj.item_plan
    
    # Verificar que el item tenga servicio
    if not item.servicio:
        logger.warning(f"Item plan #{item.id} sin servicio vinculado")
        return None  # ← Backend enviará null
    
    return {
        'id': item.id,
        'servicio_id': item.servicio.id,
        'servicio_nombre': item.servicio.nombre,
        'plan_id': item.plan.id,
        'plan_nombre': item.plan.titulo,
        'notas': item.notas or '',
        'estado': item.estado
    }
```

### Frontend:
```typescript
// Validar que los datos sean consistentes
if (esCitaPlan && !itemPlanId) {
  console.error('❌ ERROR: es_cita_plan=true pero item_plan=null');
  toast.error('Configuración de cita inválida');
  onClose();
  return;
}

if (itemPlanInfo && !itemPlanInfo.servicio_id) {
  console.error('❌ ERROR: item_plan_info sin servicio_id');
  toast.error('Información del plan incompleta');
  // Tratar como "Plan Sin Info"
}
```

---

## 🎯 Resumen Ejecutivo

### Para el Frontend:

1. **Verificar 3 campos:**
   - `es_cita_plan` (boolean)
   - `item_plan` (number | null)
   - `item_plan_info` (object | null)

2. **Usar esta lógica:**
   ```typescript
   if (!esCitaPlan) {
     // CITA SIMPLE → Selectores editables
   } else if (!itemPlanInfo) {
     // PLAN SIN INFO → Cargar planes y pre-seleccionar
   } else {
     // PLAN COMPLETO → Solo lectura ✅
   }
   ```

3. **NUNCA:**
   - Asumir que `item_plan_info` existe si `es_cita_plan=true`
   - Llamar funciones con datos null/undefined sin verificar
   - Mostrar selectores cuando `itemPlanInfo` existe

4. **SIEMPRE:**
   - Verificar que los datos existan antes de usarlos
   - Usar optional chaining: `itemPlanInfo?.servicio_id`
   - Loguear el tipo de cita detectado
   - Manejar el caso "Plan Sin Info" como fallback

---

## 🐛 Debugging Rápido

Si el modal no se muestra correctamente:

```typescript
// Agregar al inicio del componente
useEffect(() => {
  if (isOpen) {
    console.log('=================================');
    console.log('DATOS RECIBIDOS EN MODAL:');
    console.log('esCitaPlan:', esCitaPlan);
    console.log('itemPlanId:', itemPlanId);
    console.log('itemPlanInfo:', itemPlanInfo);
    console.log('Tipo detectado:', 
      !esCitaPlan ? 'SIMPLE' :
      !itemPlanInfo ? 'PLAN_SIN_INFO' :
      'PLAN_COMPLETO'
    );
    console.log('=================================');
  }
}, [isOpen, esCitaPlan, itemPlanId, itemPlanInfo]);
```

Salida esperada:
```
=================================
DATOS RECIBIDOS EN MODAL:
esCitaPlan: true
itemPlanId: 9
itemPlanInfo: { servicio_id: 5, ... }
Tipo detectado: PLAN_COMPLETO
=================================
```

¡Con esta guía el frontend sabrá exactamente cómo detectar y manejar cada tipo de cita! 🚀
