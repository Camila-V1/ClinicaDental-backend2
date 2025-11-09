# 📅 GUÍA FRONTEND: Sistema de Agenda Mejorado

## 🎯 Resumen de Cambios Backend

El sistema de agenda ahora incluye:
- **5 tipos de cita** con precios automáticos
- **Vinculación con planes de tratamiento**
- **Flujo completo**: agendar → confirmar → atender → completar ítems del plan
- **Creación automática** de episodios en historial clínico

---

## 🔄 Endpoints Actualizados

### 1. **Listar Pacientes**
**CAMBIO IMPORTANTE**: El endpoint cambió de query params a URL dedicada.

#### ❌ Antes (Ya no usar):
```typescript
GET /api/usuarios/?tipo_usuario=PACIENTE
```

#### ✅ Ahora (Usar esto):
```typescript
GET /api/usuarios/pacientes/
```

**Respuesta**:
```json
[
  {
    "id": 2,
    "nombre": "María",
    "apellido": "García",
    "nombre_completo": "María García",
    "email": "paciente1@test.com",
    "telefono": "555123456",
    "ci": "7654321"
  },
  // ... más pacientes
]
```

**Archivos a actualizar**:
- `src/components/planes/PlanNuevo.tsx`
- `src/components/citas/CitaNueva.tsx` (si existe)
- Cualquier componente que liste pacientes

---

### 2. **Modelo de Cita Actualizado**

#### Nueva estructura de datos:
```typescript
interface Cita {
  id: number;
  
  // Relaciones básicas
  paciente: number;
  paciente_nombre: string;
  paciente_email: string;
  odontologo: number;
  odontologo_nombre: string;
  odontologo_email: string;
  odontologo_especialidad: string;
  
  // Fecha y estado
  fecha_hora: string; // ISO datetime
  estado: 'PENDIENTE' | 'CONFIRMADA' | 'ATENDIDA' | 'CANCELADA';
  
  // 🆕 NUEVOS CAMPOS - Tipo de cita
  motivo_tipo: 'CONSULTA' | 'URGENCIA' | 'LIMPIEZA' | 'REVISION' | 'PLAN';
  motivo_tipo_display: string; // "Consulta General", "Urgencia/Dolor", etc.
  motivo: string; // Descripción detallada
  observaciones: string;
  
  // 🆕 NUEVOS CAMPOS - Precios
  precio: string; // "30.00", "80.00", etc.
  precio_display: string; // "$30.00" o "Incluido en plan"
  es_cita_plan: boolean;
  requiere_pago: boolean;
  
  // 🆕 NUEVOS CAMPOS - Vinculación con plan
  item_plan: number | null;
  item_plan_info: ItemPlanInfo | null;
  
  // Timestamps
  creado: string;
  actualizado: string;
}

interface ItemPlanInfo {
  id: number;
  servicio_nombre: string;
  servicio_descripcion: string;
  descripcion: string;
  precio_unitario: string;
  cantidad: number;
  subtotal: string;
  completado: boolean;
  plan_id: number;
  plan_nombre: string;
  paciente_nombre: string;
}
```

---

## 📋 Catálogo de Tipos de Cita

```typescript
const MOTIVOS_CITA = [
  { value: 'CONSULTA', label: 'Consulta General', precio: 30.00 },
  { value: 'URGENCIA', label: 'Urgencia/Dolor', precio: 80.00 },
  { value: 'LIMPIEZA', label: 'Limpieza Dental', precio: 60.00 },
  { value: 'REVISION', label: 'Revisión/Control', precio: 20.00 },
  { value: 'PLAN', label: 'Tratamiento de mi Plan', precio: 0.00 }
];
```

---

## 🚀 Nuevo Endpoint: Agendar Cita

### `POST /api/agenda/citas/agendar/`

**Quién puede usar**: Solo pacientes autenticados

**Body** (cita normal):
```json
{
  "odontologo": 1,
  "fecha_hora": "2025-11-15T10:00:00",
  "motivo_tipo": "CONSULTA",
  "motivo": "Dolor en muela inferior derecha desde hace 3 días",
  "observaciones": "Primera consulta"
}
```

**Body** (cita de plan):
```json
{
  "odontologo": 1,
  "fecha_hora": "2025-11-18T14:00:00",
  "motivo_tipo": "PLAN",
  "motivo": "Primera sesión de endodoncia según plan de tratamiento",
  "item_plan": 25,
  "observaciones": "Tratamiento incluido en plan aceptado"
}
```

**Respuesta exitosa**:
```json
{
  "message": "Cita agendada exitosamente.",
  "cita": { /* objeto Cita completo */ },
  "requiere_pago": true,
  "monto_a_pagar": "30.00",
  "mensaje_pago": "Esta cita requiere un pago de $30.00. Proceda con el pago para confirmar la cita."
}
```

**Respuesta (cita de plan)**:
```json
{
  "message": "Cita agendada exitosamente.",
  "cita": { /* objeto Cita completo */ },
  "requiere_pago": false,
  "mensaje": "Cita de tratamiento agendada. Este servicio está incluido en su plan."
}
```

**Validaciones automáticas**:
- ✅ Si `motivo_tipo='PLAN'` → requiere `item_plan`
- ✅ Verifica que el ítem no esté completado
- ✅ Verifica que el plan esté ACEPTADO
- ✅ No permite `item_plan` si no es tipo PLAN

---

## 🩺 Endpoint Mejorado: Atender Cita

### `POST /api/agenda/citas/{id}/atender/`

**Quién puede usar**: Solo odontólogos (de su propia cita)

**Body** (opcional):
```json
{
  "marcar_item_completado": true,
  "notas_atencion": "Paciente presenta dolor en molar inferior derecho. Se realiza evaluación y se indica tratamiento."
}
```

**Respuesta** (cita normal):
```json
{
  "message": "Cita atendida exitosamente.",
  "cita": { /* objeto Cita con estado ATENDIDA */ },
  "episodio_id": 42
}
```

**Respuesta** (cita de plan):
```json
{
  "message": "Cita atendida exitosamente.",
  "cita": { /* objeto Cita con estado ATENDIDA */ },
  "episodio_id": 42,
  "item_plan_completado": {
    "id": 25,
    "servicio": "Endodoncia",
    "mensaje": "Tratamiento \"Endodoncia\" marcado como completado."
  }
}
```

**Acciones automáticas**:
1. Cambia estado de cita a `ATENDIDA`
2. Si `es_cita_plan=true` → marca `item_plan.completado=true`
3. Crea episodio en historial clínico automáticamente
4. Vincula episodio con ítem del plan (si aplica)

---

## 🎨 Componentes Frontend a Crear/Actualizar

### 1. **Componente: `CitaNueva.tsx`**

```typescript
import { useState, useEffect } from 'react';
import { agendaAPI } from '@/services/agendaService';
import { planesAPI } from '@/services/planesService';

const MOTIVOS_CITA = [
  { value: 'CONSULTA', label: 'Consulta General', precio: 30 },
  { value: 'URGENCIA', label: 'Urgencia/Dolor', precio: 80 },
  { value: 'LIMPIEZA', label: 'Limpieza Dental', precio: 60 },
  { value: 'REVISION', label: 'Revisión/Control', precio: 20 },
  { value: 'PLAN', label: 'Tratamiento de mi Plan', precio: 0 }
];

export default function CitaNueva() {
  const [motivoTipo, setMotivoTipo] = useState('CONSULTA');
  const [itemPlanSeleccionado, setItemPlanSeleccionado] = useState<number | null>(null);
  const [misPlanesAceptados, setMisPlanesAceptados] = useState([]);
  const [itemsDisponibles, setItemsDisponibles] = useState([]);
  
  useEffect(() => {
    // Cargar planes ACEPTADOS del paciente al montar
    cargarPlanesAceptados();
  }, []);
  
  useEffect(() => {
    // Si cambia a PLAN, cargar ítems disponibles
    if (motivoTipo === 'PLAN') {
      cargarItemsDisponibles();
    } else {
      setItemPlanSeleccionado(null);
    }
  }, [motivoTipo]);
  
  const cargarPlanesAceptados = async () => {
    const response = await planesAPI.listar({ estado: 'ACEPTADO' });
    setMisPlanesAceptados(response.data);
  };
  
  const cargarItemsDisponibles = () => {
    // Extraer todos los ítems NO completados de planes ACEPTADOS
    const items = misPlanesAceptados.flatMap(plan => 
      plan.items
        .filter(item => !item.completado)
        .map(item => ({
          ...item,
          plan_nombre: plan.nombre
        }))
    );
    setItemsDisponibles(items);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      odontologo: selectedOdontologoId,
      fecha_hora: selectedDateTime,
      motivo_tipo: motivoTipo,
      motivo: motivoDescripcion,
      observaciones: observaciones
    };
    
    // Solo agregar item_plan si es tipo PLAN
    if (motivoTipo === 'PLAN' && itemPlanSeleccionado) {
      payload.item_plan = itemPlanSeleccionado;
    }
    
    try {
      const response = await agendaAPI.agendar(payload);
      
      if (response.data.requiere_pago) {
        // Redirigir a pasarela de pago
        mostrarPasarelaPago(response.data);
      } else {
        // Cita de plan - ya está lista
        mostrarMensajeExito(response.data.mensaje);
      }
    } catch (error) {
      // Manejar errores de validación
      mostrarErrores(error.response.data);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Selector de odontólogo */}
      <SelectOdontologo 
        value={selectedOdontologoId}
        onChange={setSelectedOdontologoId}
      />
      
      {/* Fecha y hora */}
      <DateTimePicker 
        value={selectedDateTime}
        onChange={setSelectedDateTime}
      />
      
      {/* 🆕 Selector de tipo de motivo */}
      <div className="form-group">
        <label>Tipo de Cita</label>
        <select 
          value={motivoTipo}
          onChange={(e) => setMotivoTipo(e.target.value)}
          className="form-control"
        >
          {MOTIVOS_CITA.map(motivo => (
            <option key={motivo.value} value={motivo.value}>
              {motivo.label} 
              {motivo.precio > 0 ? ` - $${motivo.precio}` : ' - Incluido'}
            </option>
          ))}
        </select>
      </div>
      
      {/* 🆕 Selector de ítem del plan (solo si tipo=PLAN) */}
      {motivoTipo === 'PLAN' && (
        <div className="form-group">
          <label>Tratamiento del Plan</label>
          {itemsDisponibles.length === 0 ? (
            <p className="text-warning">
              No tienes planes aceptados con tratamientos pendientes
            </p>
          ) : (
            <select 
              value={itemPlanSeleccionado || ''}
              onChange={(e) => setItemPlanSeleccionado(Number(e.target.value))}
              className="form-control"
              required
            >
              <option value="">Seleccionar tratamiento...</option>
              {itemsDisponibles.map(item => (
                <option key={item.id} value={item.id}>
                  {item.plan_nombre} - {item.servicio_nombre}
                </option>
              ))}
            </select>
          )}
        </div>
      )}
      
      {/* Descripción del motivo */}
      <div className="form-group">
        <label>Descripción del Motivo</label>
        <textarea 
          value={motivoDescripcion}
          onChange={(e) => setMotivoDescripcion(e.target.value)}
          className="form-control"
          rows={3}
          required
        />
      </div>
      
      {/* Observaciones */}
      <div className="form-group">
        <label>Observaciones (Opcional)</label>
        <textarea 
          value={observaciones}
          onChange={(e) => setObservaciones(e.target.value)}
          className="form-control"
          rows={2}
        />
      </div>
      
      {/* 🆕 Mostrar precio total */}
      <div className="alert alert-info">
        <strong>Costo de la cita:</strong>{' '}
        {motivoTipo === 'PLAN' ? (
          <span className="text-success">Incluido en tu plan de tratamiento</span>
        ) : (
          <span>${MOTIVOS_CITA.find(m => m.value === motivoTipo)?.precio}</span>
        )}
      </div>
      
      <button type="submit" className="btn btn-primary">
        Agendar Cita
      </button>
    </form>
  );
}
```

---

### 2. **Componente: `AgendaOdontologo.tsx`**

```typescript
// Mostrar badges según tipo de cita
const TipoCitaBadge = ({ cita }) => {
  const badges = {
    'CONSULTA': { color: 'primary', icon: '👤' },
    'URGENCIA': { color: 'danger', icon: '🚨' },
    'LIMPIEZA': { color: 'info', icon: '🦷' },
    'REVISION': { color: 'success', icon: '✓' },
    'PLAN': { color: 'warning', icon: '📋' }
  };
  
  const badge = badges[cita.motivo_tipo];
  
  return (
    <div>
      <span className={`badge badge-${badge.color}`}>
        {badge.icon} {cita.motivo_tipo_display}
      </span>
      
      {cita.es_cita_plan && (
        <span className="badge badge-secondary ml-2">
          Plan: {cita.item_plan_info?.plan_nombre}
        </span>
      )}
      
      <div className="text-muted small mt-1">
        {cita.precio_display}
      </div>
    </div>
  );
};

// Al atender la cita
const AtenderCitaModal = ({ cita, onClose, onSuccess }) => {
  const [marcarCompletado, setMarcarCompletado] = useState(true);
  const [notasAtencion, setNotasAtencion] = useState('');
  
  const handleAtender = async () => {
    try {
      const response = await agendaAPI.atender(cita.id, {
        marcar_item_completado: marcarCompletado,
        notas_atencion: notasAtencion
      });
      
      if (response.data.item_plan_completado) {
        toast.success(
          `✅ ${response.data.item_plan_completado.mensaje}`
        );
      }
      
      toast.success('Cita atendida exitosamente');
      onSuccess();
    } catch (error) {
      toast.error(error.response.data.error);
    }
  };
  
  return (
    <Modal>
      <h3>Atender Cita</h3>
      
      {/* Mostrar info de la cita */}
      <div className="mb-3">
        <strong>Paciente:</strong> {cita.paciente_nombre}<br/>
        <strong>Tipo:</strong> {cita.motivo_tipo_display}<br/>
        <strong>Motivo:</strong> {cita.motivo}
      </div>
      
      {/* 🆕 Checkbox para marcar ítem como completado (solo si es cita de plan) */}
      {cita.es_cita_plan && (
        <div className="alert alert-warning">
          <div className="form-check">
            <input 
              type="checkbox"
              checked={marcarCompletado}
              onChange={(e) => setMarcarCompletado(e.target.checked)}
              className="form-check-input"
              id="marcarCompletado"
            />
            <label className="form-check-label" htmlFor="marcarCompletado">
              <strong>Marcar tratamiento como completado</strong>
              <div className="small text-muted">
                {cita.item_plan_info?.servicio_nombre}
              </div>
            </label>
          </div>
          
          {!marcarCompletado && (
            <p className="small text-info mt-2 mb-0">
              ℹ️ Se creará el episodio pero el tratamiento quedará pendiente
              para completarse en otra sesión.
            </p>
          )}
        </div>
      )}
      
      {/* Notas de atención */}
      <div className="form-group">
        <label>Notas de Atención</label>
        <textarea 
          value={notasAtencion}
          onChange={(e) => setNotasAtencion(e.target.value)}
          className="form-control"
          rows={4}
          placeholder="Descripción del procedimiento realizado..."
        />
      </div>
      
      <button onClick={handleAtender} className="btn btn-success">
        Confirmar Atención
      </button>
    </Modal>
  );
};
```

---

### 3. **Service: `agendaService.ts`**

```typescript
import { axiosCore } from './axios-core';

export const agendaAPI = {
  listar: () => axiosCore.get('/agenda/citas/'),
  
  proximas: () => axiosCore.get('/agenda/citas/proximas/'),
  
  hoy: () => axiosCore.get('/agenda/citas/hoy/'),
  
  detalle: (id: number) => axiosCore.get(`/agenda/citas/${id}/`),
  
  // 🆕 Nuevo endpoint
  agendar: (data: AgendarCitaPayload) => 
    axiosCore.post('/agenda/citas/agendar/', data),
  
  confirmar: (id: number) => 
    axiosCore.post(`/agenda/citas/${id}/confirmar/`),
  
  cancelar: (id: number) => 
    axiosCore.post(`/agenda/citas/${id}/cancelar/`),
  
  // 🆕 Endpoint mejorado
  atender: (id: number, data: AtenderCitaPayload) => 
    axiosCore.post(`/agenda/citas/${id}/atender/`, data)
};

interface AgendarCitaPayload {
  odontologo: number;
  fecha_hora: string; // ISO datetime
  motivo_tipo: 'CONSULTA' | 'URGENCIA' | 'LIMPIEZA' | 'REVISION' | 'PLAN';
  motivo: string;
  item_plan?: number; // Solo si motivo_tipo='PLAN'
  observaciones?: string;
}

interface AtenderCitaPayload {
  marcar_item_completado?: boolean; // Default: true
  notas_atencion?: string;
}
```

---

### 4. **Actualizar: `usuariosService.ts`**

```typescript
export const usuariosAPI = {
  // ... otros métodos ...
  
  // ✅ Usar el nuevo endpoint
  listarPacientes: () => axiosCore.get('/usuarios/pacientes/'),
  
  // ❌ Ya no usar esto:
  // listar: (params) => axiosCore.get('/usuarios/', { params })
};
```

---

### 5. **Actualizar: `PlanNuevo.tsx`**

```typescript
// Cambiar esta línea:
// const response = await usuariosAPI.listar({ tipo_usuario: 'PACIENTE' });

// Por esta:
const response = await usuariosAPI.listarPacientes();

// El resto del código permanece igual
```

---

## 🧪 Flujo de Pruebas Frontend

### Flujo 1: Agendar Consulta Normal
1. Login como paciente
2. Ir a "Agendar Cita"
3. Seleccionar odontólogo
4. Seleccionar fecha/hora
5. Tipo: "Consulta General" ($30)
6. Describir motivo
7. Click "Agendar"
8. Ver mensaje: "Requiere pago de $30.00"
9. Proceder con pago (mock o real)

### Flujo 2: Agendar Tratamiento del Plan
1. Login como paciente con plan ACEPTADO
2. Ir a "Agendar Cita"
3. Seleccionar odontólogo
4. Seleccionar fecha/hora
5. Tipo: "Tratamiento de mi Plan"
6. Seleccionar tratamiento del dropdown (ej: "Endodoncia")
7. Describir motivo
8. Click "Agendar"
9. Ver mensaje: "Incluido en su plan" (sin pago)

### Flujo 3: Odontólogo Atiende Cita de Plan
1. Login como odontólogo
2. Ver agenda del día
3. Click en cita con badge "📋 Plan"
4. Click "Atender"
5. Ver checkbox "Marcar tratamiento como completado"
6. Escribir notas de atención
7. Click "Confirmar Atención"
8. Ver mensaje: "Tratamiento 'Endodoncia' marcado como completado"
9. Verificar que plan se actualiza (progreso aumenta)

---

## ✅ Checklist de Integración

### Backend
- [x] Modelo `Cita` actualizado con `motivo_tipo` e `item_plan`
- [x] Migración aplicada
- [x] Serializer actualizado con nuevos campos
- [x] Endpoint `POST /agendar/` creado
- [x] Endpoint `POST /atender/` mejorado
- [x] Endpoint `GET /usuarios/pacientes/` creado
- [x] Validaciones de coherencia implementadas
- [x] Creación automática de episodios
- [x] Poblador actualizado con datos de prueba

### Frontend (Pendiente)
- [ ] Actualizar `usuariosService.ts` con nuevo endpoint
- [ ] Actualizar `PlanNuevo.tsx` para usar `/usuarios/pacientes/`
- [ ] Crear/Actualizar tipos TypeScript para `Cita`
- [ ] Implementar componente `CitaNueva.tsx`
- [ ] Implementar selector de tipo de cita
- [ ] Implementar selector de ítem del plan
- [ ] Implementar lógica de mostrar precio
- [ ] Implementar modal de atención con checkbox
- [ ] Agregar badges visuales por tipo de cita
- [ ] Probar flujo completo end-to-end

---

## 📞 Contacto y Soporte

Si tienes dudas durante la integración:
1. Revisa el archivo `pruebas_http/08_agenda_mejorada.http`
2. Verifica los logs del servidor Django
3. Usa las herramientas de desarrollo del navegador

¡Éxito con la integración! 🚀
