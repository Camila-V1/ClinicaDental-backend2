# 🩺 GUÍA COMPLETA: Atención de Citas y Registro de Episodios

## 🎯 Objetivo

Implementar correctamente el flujo de atención de citas, diferenciando entre:
1. **Citas normales** (CONSULTA, URGENCIA, LIMPIEZA, REVISIÓN)
2. **Citas vinculadas a planes** (tipo PLAN)

---

## 📊 Flujo General

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO DE ATENCIÓN                          │
└─────────────────────────────────────────────────────────────────┘

1. Odontólogo ve lista de citas
2. Click en "🩺 Atender"
3. Backend marca cita como ATENDIDA
4. Se abre modal para registrar episodio
5. Modal detecta tipo de cita:
   
   ├─ Si es CITA NORMAL:
   │  ├─ Muestra dropdown de planes (opcional)
   │  ├─ Muestra dropdown de servicios
   │  └─ Odontólogo completa campos
   │
   └─ Si es CITA DE PLAN:
      ├─ Muestra info del plan (SOLO LECTURA)
      ├─ Muestra servicio vinculado (SOLO LECTURA)
      ├─ Pre-llena campos automáticamente
      └─ Odontólogo solo agrega diagnóstico y notas

6. Guardar episodio
7. Backend crea EpisodioAtencion vinculado
```

---

## 🔄 Endpoint Backend: POST /api/agenda/citas/{id}/atender/

### Lo que hace:
1. ✅ Marca la cita como `ATENDIDA`
2. ✅ Si es cita de plan, marca el ítem como `COMPLETADO`
3. ✅ NO crea el episodio (eso lo hace el frontend desde el modal)

### Respuesta:
```json
{
  "message": "Cita marcada como atendida. Ahora puedes registrar el episodio clínico.",
  "cita": {
    "id": 82,
    "estado": "ATENDIDA",
    "es_cita_plan": true,
    "item_plan": 25,
    "item_plan_info": {
      "id": 25,
      "servicio_id": 3,              // 🔑 IMPORTANTE
      "servicio_nombre": "Endodoncia",
      "servicio_descripcion": "...",
      "plan_id": 15,                 // 🔑 IMPORTANTE
      "plan_nombre": "Plan de Ortodoncia",
      "estado": "COMPLETADO",
      "notas": "..."
    }
  }
}
```

---

## 🎨 Componente: AgendaCitas.tsx

### ✅ Cambio Necesario

**ANTES (Incorrecto):**
```typescript
<ModalRegistrarEpisodio
  isOpen={modalAbierto}
  onClose={() => { ... }}
  pacienteId={citaSeleccionada.paciente}
  pacienteNombre={citaSeleccionada.paciente_nombre}
  motivoCita={citaSeleccionada.motivo}
  onEpisodioCreado={handleEpisodioCreado}
  esCitaPlan={citaSeleccionada.es_cita_plan ?? false}
  servicioId={citaSeleccionada.servicio ?? null}  // ❌ INCORRECTO
  itemPlanId={citaSeleccionada.item_plan ?? null}
  citaId={citaSeleccionada.id}
/>
```

**DESPUÉS (Correcto):**
```typescript
<ModalRegistrarEpisodio
  isOpen={modalAbierto}
  onClose={() => { ... }}
  pacienteId={citaSeleccionada.paciente}
  pacienteNombre={citaSeleccionada.paciente_nombre}
  motivoCita={citaSeleccionada.motivo}
  onEpisodioCreado={handleEpisodioCreado}
  
  // 🔑 Campos para citas vinculadas a planes
  esCitaPlan={citaSeleccionada.es_cita_plan ?? false}
  servicioId={citaSeleccionada.item_plan_info?.servicio_id ?? null}  // ✅ CORRECTO
  itemPlanId={citaSeleccionada.item_plan ?? null}
  citaId={citaSeleccionada.id}
  
  // 🆕 NUEVO: Pasar toda la info del plan para mostrarla
  itemPlanInfo={citaSeleccionada.item_plan_info ?? null}
/>
```

### 📝 Props Completas del Modal

```typescript
interface ModalRegistrarEpisodioProps {
  isOpen: boolean;
  onClose: () => void;
  pacienteId: number;
  pacienteNombre: string;
  motivoCita: string;
  onEpisodioCreado: () => void;
  
  // Para citas vinculadas a planes
  esCitaPlan: boolean;
  servicioId: number | null;
  itemPlanId: number | null;
  citaId: number;
  
  // 🆕 NUEVO
  itemPlanInfo?: {
    id: number;
    servicio_id: number;
    servicio_nombre: string;
    servicio_descripcion: string;
    plan_id: number;
    plan_nombre: string;
    notas: string;
  } | null;
}
```

---

## 🎨 Componente: ModalRegistrarEpisodio.tsx

### Lógica de Inicialización

```typescript
export default function ModalRegistrarEpisodio({
  isOpen,
  onClose,
  pacienteId,
  pacienteNombre,
  motivoCita,
  onEpisodioCreado,
  esCitaPlan,
  servicioId,
  itemPlanId,
  citaId,
  itemPlanInfo  // 🆕 NUEVO
}: ModalRegistrarEpisodioProps) {
  
  const [formData, setFormData] = useState({
    historial_clinico: 0,
    servicio: servicioId || null,
    item_plan_tratamiento: itemPlanId || null,
    motivo_consulta: motivoCita,
    diagnostico: '',
    descripcion_procedimiento: '',
    notas_privadas: ''
  });

  // 🔑 Efecto para inicializar cuando es cita de plan
  useEffect(() => {
    if (isOpen && esCitaPlan && servicioId && itemPlanId) {
      console.log('✅ Cita vinculada a plan detectada');
      console.log('📋 Plan:', itemPlanInfo?.plan_nombre);
      console.log('🦷 Servicio:', itemPlanInfo?.servicio_nombre);
      
      setFormData(prev => ({
        ...prev,
        servicio: servicioId,
        item_plan_tratamiento: itemPlanId,
        // Pre-llenar descripción con info del plan
        descripcion_procedimiento: itemPlanInfo?.notas || ''
      }));
    }
  }, [isOpen, esCitaPlan, servicioId, itemPlanId, itemPlanInfo]);

  // ... resto del código
}
```

---

## 🎨 Renderizado Condicional del Modal

### Sección de Vinculación a Plan

```typescript
{/* 📋 SECCIÓN: Vinculación a Plan */}
<div style={{ marginBottom: '24px' }}>
  {esCitaPlan && itemPlanInfo ? (
    // ============================================================
    // MODO 1: CITA YA VINCULADA A PLAN (Solo Lectura)
    // ============================================================
    <div style={{
      backgroundColor: '#d1fae5',
      border: '2px solid #10b981',
      borderRadius: '8px',
      padding: '16px'
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px',
        marginBottom: '12px'
      }}>
        <span style={{ fontSize: '20px' }}>✅</span>
        <strong style={{ color: '#065f46' }}>
          Cita Vinculada a Plan de Tratamiento
        </strong>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '12px',
        marginTop: '12px'
      }}>
        {/* Plan */}
        <div>
          <label style={{ 
            fontSize: '12px', 
            color: '#065f46',
            fontWeight: '600',
            display: 'block',
            marginBottom: '4px'
          }}>
            📋 Plan de Tratamiento
          </label>
          <div style={{
            backgroundColor: 'white',
            padding: '10px 12px',
            borderRadius: '6px',
            border: '1px solid #10b981',
            fontSize: '14px',
            color: '#111827'
          }}>
            {itemPlanInfo.plan_nombre}
          </div>
        </div>

        {/* Servicio */}
        <div>
          <label style={{ 
            fontSize: '12px', 
            color: '#065f46',
            fontWeight: '600',
            display: 'block',
            marginBottom: '4px'
          }}>
            🦷 Tratamiento
          </label>
          <div style={{
            backgroundColor: 'white',
            padding: '10px 12px',
            borderRadius: '6px',
            border: '1px solid #10b981',
            fontSize: '14px',
            color: '#111827'
          }}>
            {itemPlanInfo.servicio_nombre}
          </div>
        </div>
      </div>

      {/* Notas del Plan */}
      {itemPlanInfo.notas && (
        <div style={{ marginTop: '12px' }}>
          <label style={{ 
            fontSize: '12px', 
            color: '#065f46',
            fontWeight: '600',
            display: 'block',
            marginBottom: '4px'
          }}>
            📝 Notas del Plan
          </label>
          <div style={{
            backgroundColor: 'white',
            padding: '10px 12px',
            borderRadius: '6px',
            border: '1px solid #10b981',
            fontSize: '13px',
            color: '#6b7280',
            fontStyle: 'italic'
          }}>
            {itemPlanInfo.notas}
          </div>
        </div>
      )}

      <p style={{ 
        fontSize: '12px', 
        color: '#065f46',
        marginTop: '12px',
        marginBottom: 0 
      }}>
        ℹ️ El tratamiento y plan ya están vinculados. No es necesario seleccionarlos.
      </p>
    </div>
  ) : (
    // ============================================================
    // MODO 2: CITA NORMAL (Campos Editables)
    // ============================================================
    <>
      {/* Dropdown de Planes (Opcional) */}
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          fontSize: '14px',
          fontWeight: '500',
          color: '#374151',
          marginBottom: '8px'
        }}>
          📋 Vincular a Plan (Opcional)
        </label>
        <select
          value={formData.item_plan_tratamiento || ''}
          onChange={(e) => {
            const itemId = e.target.value ? Number(e.target.value) : null;
            setFormData({
              ...formData,
              item_plan_tratamiento: itemId
            });
          }}
          style={{
            width: '100%',
            padding: '10px 12px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none'
          }}
        >
          <option value="">No vincular a plan</option>
          {planesActivos.map(plan => (
            <optgroup key={plan.id} label={plan.nombre}>
              {plan.items
                .filter(item => item.estado !== 'COMPLETADO')
                .map(item => (
                  <option key={item.id} value={item.id}>
                    {item.servicio_nombre} ({item.estado})
                  </option>
                ))}
            </optgroup>
          ))}
        </select>
        <p style={{ 
          fontSize: '12px', 
          color: '#6b7280', 
          marginTop: '4px' 
        }}>
          Si este episodio corresponde a un tratamiento del plan, selecciónalo aquí
        </p>
      </div>

      {/* Dropdown de Servicios */}
      <div>
        <label style={{
          display: 'block',
          fontSize: '14px',
          fontWeight: '500',
          color: '#374151',
          marginBottom: '8px'
        }}>
          🦷 Servicio Realizado <span style={{ color: '#dc2626' }}>*</span>
        </label>
        <select
          value={formData.servicio || ''}
          onChange={(e) => {
            const servicioId = e.target.value ? Number(e.target.value) : null;
            setFormData({
              ...formData,
              servicio: servicioId
            });
          }}
          style={{
            width: '100%',
            padding: '10px 12px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none'
          }}
          required
        >
          <option value="">Seleccionar servicio...</option>
          {servicios.map(servicio => (
            <option key={servicio.id} value={servicio.id}>
              {servicio.nombre}
            </option>
          ))}
        </select>
      </div>
    </>
  )}
</div>
```

---

## 🔄 Flujo de Datos Completo

### Paso 1: Paciente Agenda Cita de Plan

```http
POST /api/agenda/citas/agendar/
{
  "odontologo": 1,
  "fecha_hora": "2025-11-18T14:00:00",
  "motivo_tipo": "PLAN",
  "motivo": "Primera sesión de endodoncia",
  "item_plan": 25  // ← Vincula con ítem del plan
}
```

**Respuesta:**
```json
{
  "cita": {
    "id": 82,
    "es_cita_plan": true,
    "item_plan": 25,
    "item_plan_info": {
      "servicio_id": 3,
      "servicio_nombre": "Endodoncia",
      "plan_id": 15,
      "plan_nombre": "Plan de Ortodoncia"
    }
  }
}
```

### Paso 2: Odontólogo Atiende la Cita

```http
POST /api/agenda/citas/82/atender/
{}
```

**Respuesta:**
```json
{
  "message": "Cita marcada como atendida",
  "cita": {
    "estado": "ATENDIDA",
    "es_cita_plan": true,
    "item_plan_info": {
      "servicio_id": 3,
      "plan_id": 15,
      ...
    }
  },
  "item_plan_completado": {
    "id": 25,
    "servicio": "Endodoncia",
    "mensaje": "Tratamiento 'Endodoncia' marcado como completado."
  }
}
```

### Paso 3: Modal se Abre con Datos Pre-llenados

El frontend detecta:
- `esCitaPlan = true`
- `itemPlanInfo` tiene datos
- Pre-llena campos automáticamente
- Muestra info del plan en modo SOLO LECTURA

### Paso 4: Odontólogo Completa y Guarda

```http
POST /api/historial/episodios/
{
  "historial_clinico": 5,
  "servicio": 3,                    // ← Ya estaba pre-llenado
  "item_plan_tratamiento": 25,      // ← Ya estaba pre-llenado
  "motivo_consulta": "Primera sesión de endodoncia",
  "diagnostico": "Caries profunda en molar inferior",
  "descripcion_procedimiento": "Endodoncia completa...",
  "notas_privadas": "Paciente toleró bien el procedimiento"
}
```

---

## ✅ Checklist de Implementación

### Backend (Ya implementado)
- [x] Endpoint `/atender/` marca cita como ATENDIDA
- [x] Marca ítem del plan como COMPLETADO
- [x] Serializer incluye `servicio_id` en `item_plan_info`
- [x] NO crea episodio automáticamente

### Frontend (Por implementar)
- [ ] Actualizar `AgendaCitas.tsx`:
  - [ ] Pasar `servicioId` correcto al modal
  - [ ] Pasar `itemPlanInfo` completo
- [ ] Actualizar `ModalRegistrarEpisodio.tsx`:
  - [ ] Recibir prop `itemPlanInfo`
  - [ ] Detectar si es cita de plan
  - [ ] Renderizar condicional (solo lectura vs editable)
  - [ ] Pre-llenar campos cuando es cita de plan
  - [ ] NO mostrar dropdown de planes si ya está vinculado
- [ ] Actualizar tipos TypeScript para incluir `itemPlanInfo`

---

## 🧪 Casos de Prueba

### Caso 1: Atender Cita Normal (CONSULTA)
1. Login como odontólogo
2. Ver lista de citas
3. Click "Atender" en cita tipo CONSULTA
4. Modal se abre con campos vacíos
5. Seleccionar servicio manualmente
6. Opcionalmente vincular a plan
7. Completar diagnóstico y procedimiento
8. Guardar

**Resultado Esperado:**
- ✅ Modal muestra dropdowns editables
- ✅ Episodio se crea correctamente

### Caso 2: Atender Cita de Plan
1. Login como odontólogo
2. Ver lista de citas
3. Click "Atender" en cita tipo PLAN
4. Modal se abre con información pre-llenada
5. Ver plan y servicio (solo lectura)
6. Completar solo diagnóstico y notas
7. Guardar

**Resultado Esperado:**
- ✅ Modal muestra plan/servicio pre-llenados
- ✅ Campos están en modo solo lectura
- ✅ Episodio se crea vinculado al plan
- ✅ Ítem del plan queda COMPLETADO

---

## 📞 Soporte

Si tienes dudas:
1. Revisa logs de consola para ver qué datos llegan al modal
2. Verifica que `item_plan_info` tenga `servicio_id`
3. Usa React DevTools para inspeccionar props del modal

¡Éxito con la implementación! 🚀
