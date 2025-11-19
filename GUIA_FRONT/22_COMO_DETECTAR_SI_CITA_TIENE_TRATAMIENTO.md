# 🔍 ¿Cómo Saber si una Cita Tiene un Tratamiento?

## 🎯 Respuesta Rápida

Una cita tiene un tratamiento vinculado cuando:

```typescript
// En el frontend:
if (cita.es_cita_plan === true && cita.item_plan !== null) {
  console.log('✅ Esta cita SÍ tiene un tratamiento vinculado');
}
```

---

## 📊 Estructura de Datos de una Cita

### Cita del Backend (JSON)

```json
{
  "id": 82,
  "paciente": 5,
  "paciente_nombre": "Juan Pérez",
  "odontologo": 1,
  "odontologo_nombre": "Dr. María García",
  "fecha_hora": "2025-11-18T14:00:00",
  "motivo_tipo": "PLAN",           // ← Campo clave 1
  "motivo": "Primera sesión de endodoncia",
  "estado": "PENDIENTE",
  
  // 🔑 CAMPOS IMPORTANTES PARA DETECTAR TRATAMIENTO
  "es_cita_plan": true,             // ← Campo clave 2
  "item_plan": 25,                  // ← Campo clave 3 (ID del tratamiento)
  "item_plan_info": {               // ← Campo clave 4 (Info completa)
    "id": 25,
    "servicio_id": 3,
    "servicio_nombre": "Endodoncia",
    "servicio_descripcion": "Tratamiento de conducto",
    "plan_id": 15,
    "plan_nombre": "Rehabilitación Completa",
    "estado": "EN_PROGRESO",
    "notas": "Primera sesión, molar inferior derecho"
  }
}
```

---

## 🔑 Campos Clave para Detectar Tratamiento

### 1. `motivo_tipo` (string)
**Valores posibles:**
- `"CONSULTA"` - Cita normal de consulta
- `"URGENCIA"` - Atención de urgencia
- `"LIMPIEZA"` - Limpieza dental
- `"REVISION"` - Revisión de rutina
- `"PLAN"` ← **Este valor indica que es cita de plan**

**Uso:**
```typescript
if (cita.motivo_tipo === 'PLAN') {
  console.log('Esta cita es del tipo PLAN (puede tener tratamiento)');
}
```

---

### 2. `es_cita_plan` (boolean)
Campo calculado que indica si la cita está vinculada a un plan de tratamiento.

**Valores:**
- `true` - Cita vinculada a un tratamiento de plan
- `false` - Cita normal (sin tratamiento)

**Uso:**
```typescript
if (cita.es_cita_plan) {
  console.log('✅ Esta cita está vinculada a un plan de tratamiento');
}
```

---

### 3. `item_plan` (number | null)
ID del ítem del plan de tratamiento vinculado.

**Valores:**
- `number` - ID del tratamiento (ej: 25)
- `null` - Sin tratamiento vinculado

**Uso:**
```typescript
if (cita.item_plan !== null) {
  console.log(`Tratamiento vinculado: ID ${cita.item_plan}`);
}
```

---

### 4. `item_plan_info` (object | null)
Información completa del tratamiento vinculado.

**Valores:**
- `object` - Info expandida del tratamiento
- `null` - Sin información (puede ser cita antigua o error)

**Uso:**
```typescript
if (cita.item_plan_info) {
  console.log(`Plan: ${cita.item_plan_info.plan_nombre}`);
  console.log(`Tratamiento: ${cita.item_plan_info.servicio_nombre}`);
}
```

---

## ✅ Métodos de Detección

### Método 1: Simple (Recomendado)

```typescript
function tieneTratamiento(cita: Cita): boolean {
  return cita.es_cita_plan === true && cita.item_plan !== null;
}

// Uso:
if (tieneTratamiento(cita)) {
  console.log('✅ Cita con tratamiento');
} else {
  console.log('❌ Cita sin tratamiento');
}
```

---

### Método 2: Con Validación Completa

```typescript
function analizarCita(cita: Cita) {
  // Caso 1: Cita sin tratamiento
  if (!cita.es_cita_plan) {
    return {
      tieneTratamiento: false,
      tipo: 'SIMPLE',
      mensaje: 'Cita normal sin tratamiento vinculado'
    };
  }
  
  // Caso 2: Cita con tratamiento (info completa)
  if (cita.es_cita_plan && cita.item_plan_info) {
    return {
      tieneTratamiento: true,
      tipo: 'PLAN_COMPLETO',
      mensaje: 'Cita con tratamiento vinculado',
      plan: cita.item_plan_info.plan_nombre,
      tratamiento: cita.item_plan_info.servicio_nombre
    };
  }
  
  // Caso 3: Cita con tratamiento (sin info completa)
  if (cita.es_cita_plan && cita.item_plan && !cita.item_plan_info) {
    return {
      tieneTratamiento: true,
      tipo: 'PLAN_SIN_INFO',
      mensaje: 'Cita vinculada pero sin información expandida',
      itemId: cita.item_plan
    };
  }
  
  // Caso 4: Configuración inválida
  return {
    tieneTratamiento: false,
    tipo: 'ERROR',
    mensaje: 'Configuración de cita inválida'
  };
}

// Uso:
const analisis = analizarCita(cita);
console.log(analisis);
// Output: { tieneTratamiento: true, tipo: 'PLAN_COMPLETO', ... }
```

---

### Método 3: Con Type Guard (TypeScript)

```typescript
interface CitaSimple {
  es_cita_plan: false;
  item_plan: null;
  item_plan_info: null;
}

interface CitaPlan {
  es_cita_plan: true;
  item_plan: number;
  item_plan_info: ItemPlanInfo | null;
}

type Cita = CitaSimple | CitaPlan;

// Type guard
function esCitaConTratamiento(cita: Cita): cita is CitaPlan {
  return cita.es_cita_plan === true && cita.item_plan !== null;
}

// Uso:
if (esCitaConTratamiento(cita)) {
  // TypeScript sabe que aquí cita.item_plan es number
  console.log(`ID del tratamiento: ${cita.item_plan}`);
  
  if (cita.item_plan_info) {
    // Y aquí sabemos que tiene info completa
    console.log(`Plan: ${cita.item_plan_info.plan_nombre}`);
  }
}
```

---

## 🎨 Ejemplos Visuales en el UI

### Ejemplo 1: Badge en Lista de Citas

```typescript
function CitaCard({ cita }: { cita: Cita }) {
  return (
    <div className="cita-card">
      <div className="cita-header">
        <h3>{cita.paciente_nombre}</h3>
        
        {/* Badge que muestra si tiene tratamiento */}
        {cita.es_cita_plan && cita.item_plan_info && (
          <span className="badge badge-plan">
            📋 {cita.item_plan_info.plan_nombre}
          </span>
        )}
      </div>
      
      <p>🦷 {cita.motivo}</p>
      
      {cita.item_plan_info && (
        <p className="tratamiento-info">
          🔧 Tratamiento: {cita.item_plan_info.servicio_nombre}
        </p>
      )}
    </div>
  );
}
```

**Resultado Visual:**
```
┌────────────────────────────────────────────┐
│ Juan Pérez     [📋 Rehabilitación Completa]│
│ 🦷 Primera sesión de endodoncia           │
│ 🔧 Tratamiento: Endodoncia                 │
└────────────────────────────────────────────┘
```

---

### Ejemplo 2: Icono Condicional

```typescript
function getIconoCita(cita: Cita): string {
  if (cita.es_cita_plan && cita.item_plan_info) {
    return '📋'; // Icono de plan
  }
  
  switch (cita.motivo_tipo) {
    case 'CONSULTA': return '🩺';
    case 'URGENCIA': return '🚨';
    case 'LIMPIEZA': return '🪥';
    case 'REVISION': return '🔍';
    default: return '📅';
  }
}

// Uso en componente:
<div className="cita-icon">
  {getIconoCita(cita)}
</div>
```

---

### Ejemplo 3: Descripción Completa

```typescript
function DescripcionCita({ cita }: { cita: Cita }) {
  if (cita.es_cita_plan && cita.item_plan_info) {
    return (
      <div className="cita-plan-info">
        <h4>📋 Cita de Plan de Tratamiento</h4>
        <dl>
          <dt>Plan:</dt>
          <dd>{cita.item_plan_info.plan_nombre}</dd>
          
          <dt>Tratamiento:</dt>
          <dd>{cita.item_plan_info.servicio_nombre}</dd>
          
          <dt>Estado:</dt>
          <dd>
            <span className={`badge badge-${cita.item_plan_info.estado.toLowerCase()}`}>
              {cita.item_plan_info.estado}
            </span>
          </dd>
          
          {cita.item_plan_info.notas && (
            <>
              <dt>Notas:</dt>
              <dd>{cita.item_plan_info.notas}</dd>
            </>
          )}
        </dl>
      </div>
    );
  }
  
  // Cita normal
  return (
    <div className="cita-simple-info">
      <h4>📅 Cita de {cita.motivo_tipo}</h4>
      <p>{cita.motivo}</p>
    </div>
  );
}
```

---

## 🔄 Flujo Completo de Detección

```typescript
// 1. Obtener cita del backend
const response = await fetch(`/api/agenda/citas/${citaId}/`);
const cita = await response.json();

// 2. Analizar la cita
console.group('🔍 ANÁLISIS DE CITA');
console.log('ID:', cita.id);
console.log('Tipo:', cita.motivo_tipo);
console.log('Es cita de plan:', cita.es_cita_plan);
console.log('Item plan ID:', cita.item_plan);
console.log('Tiene info completa:', !!cita.item_plan_info);

// 3. Determinar acción
if (cita.es_cita_plan && cita.item_plan_info) {
  console.log('✅ CITA CON TRATAMIENTO - INFO COMPLETA');
  console.log('Plan:', cita.item_plan_info.plan_nombre);
  console.log('Tratamiento:', cita.item_plan_info.servicio_nombre);
  
  // Mostrar modal con info pre-llenada
  abrirModalSoloLectura(cita);
  
} else if (cita.es_cita_plan && cita.item_plan) {
  console.warn('⚠️ CITA CON TRATAMIENTO - SIN INFO');
  console.log('Item plan ID:', cita.item_plan);
  
  // Cargar planes manualmente
  abrirModalConSelectores(cita);
  
} else {
  console.log('📌 CITA SIMPLE - SIN TRATAMIENTO');
  
  // Mostrar modal normal
  abrirModalSimple(cita);
}

console.groupEnd();
```

---

## 🧪 Testing en Consola del Navegador

Abre la consola y ejecuta:

```javascript
// Test 1: Verificar todas las citas
const citas = await fetch('/api/agenda/citas/').then(r => r.json());
citas.forEach(cita => {
  const tieneTratamiento = cita.es_cita_plan && cita.item_plan !== null;
  console.log(`Cita #${cita.id}: ${tieneTratamiento ? '✅ CON' : '❌ SIN'} tratamiento`);
});

// Test 2: Filtrar solo citas con tratamiento
const citasConTratamiento = citas.filter(c => c.es_cita_plan && c.item_plan !== null);
console.log(`Total citas con tratamiento: ${citasConTratamiento.length}`);
console.table(citasConTratamiento.map(c => ({
  id: c.id,
  paciente: c.paciente_nombre,
  plan: c.item_plan_info?.plan_nombre || 'Sin info',
  tratamiento: c.item_plan_info?.servicio_nombre || 'Sin info'
})));

// Test 3: Verificar una cita específica
const citaId = 82;
const cita = await fetch(`/api/agenda/citas/${citaId}/`).then(r => r.json());
console.log('Análisis de cita:', {
  id: cita.id,
  tieneTratamiento: cita.es_cita_plan && cita.item_plan !== null,
  tieneInfoCompleta: !!cita.item_plan_info,
  plan: cita.item_plan_info?.plan_nombre,
  tratamiento: cita.item_plan_info?.servicio_nombre
});
```

---

## 📋 Checklist de Verificación

Al revisar una cita, verifica:

- [ ] `es_cita_plan` es `true` → Indica que ES cita de plan
- [ ] `item_plan` NO es `null` → Tiene ID del tratamiento vinculado
- [ ] `item_plan_info` NO es `null` → Tiene información completa del tratamiento
- [ ] `item_plan_info.servicio_id` existe → Tiene servicio vinculado
- [ ] `item_plan_info.plan_nombre` existe → Nombre del plan visible

**Si todos están ✅:** Cita con tratamiento completo  
**Si solo 1 y 2 están ✅:** Cita con tratamiento pero sin info  
**Si ninguno está ✅:** Cita simple sin tratamiento

---

## ⚠️ Errores Comunes

### Error 1: Asumir que `motivo_tipo === 'PLAN'` es suficiente

```typescript
// ❌ INCORRECTO
if (cita.motivo_tipo === 'PLAN') {
  // Esto NO garantiza que tenga item_plan
  console.log(cita.item_plan_info.plan_nombre); // Puede ser undefined!
}

// ✅ CORRECTO
if (cita.es_cita_plan && cita.item_plan_info) {
  console.log(cita.item_plan_info.plan_nombre); // Seguro
}
```

---

### Error 2: No verificar `item_plan_info` antes de acceder

```typescript
// ❌ INCORRECTO
if (cita.es_cita_plan) {
  console.log(cita.item_plan_info.servicio_nombre); // Puede ser null!
}

// ✅ CORRECTO
if (cita.es_cita_plan && cita.item_plan_info) {
  console.log(cita.item_plan_info.servicio_nombre); // Seguro
}

// ✅ MEJOR (Optional chaining)
console.log(cita.item_plan_info?.servicio_nombre ?? 'Sin tratamiento');
```

---

### Error 3: Confundir `item_plan` con `item_plan_info`

```typescript
// ❌ INCORRECTO
if (cita.item_plan) {
  // item_plan es solo un número (ID)
  console.log(cita.item_plan.nombre); // ERROR: number no tiene .nombre
}

// ✅ CORRECTO
if (cita.item_plan_info) {
  // item_plan_info es el objeto con información
  console.log(cita.item_plan_info.servicio_nombre); // ✅
}
```

---

## 🎯 Resumen Ultra-Rápido

```typescript
// La forma MÁS SIMPLE de saber si tiene tratamiento:

const tieneTratamiento = cita.es_cita_plan && cita.item_plan !== null;

// Si quieres mostrar el nombre del tratamiento:
const nombreTratamiento = cita.item_plan_info?.servicio_nombre ?? 'Sin especificar';

// Si quieres todo el contexto:
if (cita.item_plan_info) {
  const { plan_nombre, servicio_nombre, estado, notas } = cita.item_plan_info;
  console.log(`Plan: ${plan_nombre} | Tratamiento: ${servicio_nombre}`);
}
```

---

## 📊 Tabla Resumen

| Condición | Tiene Tratamiento | Info Completa | Acción |
|-----------|-------------------|---------------|--------|
| `es_cita_plan=false` | ❌ No | N/A | Modal normal |
| `es_cita_plan=true` + `item_plan=null` | ❌ No | N/A | Error de config |
| `es_cita_plan=true` + `item_plan=9` + `info=null` | ✅ Sí | ❌ No | Cargar planes |
| `es_cita_plan=true` + `item_plan=9` + `info={...}` | ✅ Sí | ✅ Sí | Modal solo lectura |

¡Con esto sabrás siempre si una cita tiene un tratamiento vinculado! 🚀
