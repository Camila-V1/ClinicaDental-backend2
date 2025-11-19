# 📘 Tipos TypeScript para Atención de Citas

## 🎯 Tipos de la Respuesta del Backend

```typescript
// types/agenda.ts

/**
 * Información del ítem del plan vinculado a la cita
 */
export interface ItemPlanInfo {
  id: number;
  servicio_id: number;
  servicio_nombre: string;
  servicio_descripcion: string;
  notas: string;
  precio_servicio: string;
  precio_servicio_snapshot: string;
  precio_laboratorio: string;
  precio_total: string;
  estado: 'PENDIENTE' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  completado: boolean;
  plan_id: number;
  plan_nombre: string;
  sesiones_previstas: number;
  sesiones_completadas: number;
}

/**
 * Tipo base de cita
 */
export interface Cita {
  id: number;
  odontologo: number;
  odontologo_nombre: string;
  paciente: number;
  paciente_nombre: string;
  fecha_hora: string;
  duracion_minutos: number;
  motivo_tipo: 'CONSULTA' | 'URGENCIA' | 'LIMPIEZA' | 'REVISION' | 'PLAN';
  motivo: string;
  estado: 'PENDIENTE' | 'CONFIRMADA' | 'ATENDIDA' | 'CANCELADA' | 'NO_ASISTIO';
  es_cita_plan: boolean;
  item_plan: number | null;
  item_plan_info: ItemPlanInfo | null;
  notas: string;
  precio_estimado: string;
  creado_en: string;
}

/**
 * Respuesta del endpoint /atender/
 */
export interface AtenderCitaResponse {
  message: string;
  cita: Cita;
  item_plan_completado?: {
    id: number;
    servicio: string;
    mensaje: string;
  };
}
```

---

## 🎨 Props del Modal

```typescript
// components/agenda/ModalRegistrarEpisodio.tsx

interface ModalRegistrarEpisodioProps {
  // Control del modal
  isOpen: boolean;
  onClose: () => void;
  onEpisodioCreado: () => void;
  
  // Datos del paciente y cita
  pacienteId: number;
  pacienteNombre: string;
  motivoCita: string;
  citaId: number;
  
  // Datos para citas vinculadas a planes
  esCitaPlan: boolean;
  servicioId: number | null;
  itemPlanId: number | null;
  itemPlanInfo?: ItemPlanInfo | null;  // 🆕 Información completa del plan
}
```

---

## 🔄 State del Formulario

```typescript
interface FormDataEpisodio {
  historial_clinico: number;
  servicio: number | null;
  item_plan_tratamiento: number | null;
  motivo_consulta: string;
  diagnostico: string;
  descripcion_procedimiento: string;
  notas_privadas: string;
}
```

---

## 🦷 Tipos de Servicios y Planes

```typescript
// types/tratamientos.ts

export interface Servicio {
  id: number;
  nombre: string;
  descripcion: string;
  categoria: string;
  precio_base: string;
  duracion_estimada_minutos: number;
  requiere_laboratorio: boolean;
  activo: boolean;
}

export interface ItemPlan {
  id: number;
  servicio: number;
  servicio_nombre: string;
  servicio_descripcion: string;
  estado: 'PENDIENTE' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  notas: string;
  precio_servicio_snapshot: string;
  precio_laboratorio: string;
  precio_total: string;
}

export interface PlanTratamiento {
  id: number;
  nombre: string;
  descripcion: string;
  estado: 'PROPUESTO' | 'ACEPTADO' | 'EN_PROGRESO' | 'COMPLETADO' | 'CANCELADO';
  items: ItemPlan[];
  fecha_creacion: string;
  fecha_inicio: string | null;
  fecha_finalizacion: string | null;
}
```

---

## 📝 Actualización de AgendaCitas.tsx

```typescript
// components/agenda/AgendaCitas.tsx

import { Cita, AtenderCitaResponse } from '../../types/agenda';

export default function AgendaCitas() {
  const [citaSeleccionada, setCitaSeleccionada] = useState<Cita | null>(null);
  const [modalAbierto, setModalAbierto] = useState(false);

  const handleAtender = async (cita: Cita) => {
    try {
      const response = await axiosInstance.post<AtenderCitaResponse>(
        `/api/agenda/citas/${cita.id}/atender/`
      );

      console.log('✅ Cita atendida:', response.data);
      
      // Actualizar la cita con la respuesta del backend
      setCitaSeleccionada(response.data.cita);
      setModalAbierto(true);
      
      // Mostrar notificación si se completó un ítem del plan
      if (response.data.item_plan_completado) {
        toast.success(response.data.item_plan_completado.mensaje);
      }
    } catch (error) {
      console.error('❌ Error al atender cita:', error);
      toast.error('Error al marcar la cita como atendida');
    }
  };

  return (
    <div>
      {/* Lista de citas */}
      {citas.map(cita => (
        <div key={cita.id}>
          {/* ... */}
          <button onClick={() => handleAtender(cita)}>
            🩺 Atender
          </button>
        </div>
      ))}

      {/* Modal con props correctas */}
      {citaSeleccionada && (
        <ModalRegistrarEpisodio
          isOpen={modalAbierto}
          onClose={() => {
            setModalAbierto(false);
            setCitaSeleccionada(null);
          }}
          pacienteId={citaSeleccionada.paciente}
          pacienteNombre={citaSeleccionada.paciente_nombre}
          motivoCita={citaSeleccionada.motivo}
          onEpisodioCreado={() => {
            setModalAbierto(false);
            setCitaSeleccionada(null);
            cargarCitas(); // Recargar lista
          }}
          
          // 🔑 Props para citas de plan
          esCitaPlan={citaSeleccionada.es_cita_plan ?? false}
          servicioId={citaSeleccionada.item_plan_info?.servicio_id ?? null}  // ✅ Correcto
          itemPlanId={citaSeleccionada.item_plan ?? null}
          citaId={citaSeleccionada.id}
          itemPlanInfo={citaSeleccionada.item_plan_info}  // 🆕 Nuevo
        />
      )}
    </div>
  );
}
```

---

## 🎨 Ejemplo Completo del Modal (Versión Simplificada)

```typescript
// components/agenda/ModalRegistrarEpisodio.tsx

import { useState, useEffect } from 'react';
import { ItemPlanInfo } from '../../types/agenda';
import { toast } from 'react-hot-toast';
import axiosInstance from '../../api/axios';

interface ModalRegistrarEpisodioProps {
  isOpen: boolean;
  onClose: () => void;
  pacienteId: number;
  pacienteNombre: string;
  motivoCita: string;
  onEpisodioCreado: () => void;
  esCitaPlan: boolean;
  servicioId: number | null;
  itemPlanId: number | null;
  citaId: number;
  itemPlanInfo?: ItemPlanInfo | null;
}

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
  itemPlanInfo
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

  const [loading, setLoading] = useState(false);

  // 🔑 Efecto: Pre-llenar datos cuando es cita de plan
  useEffect(() => {
    if (isOpen && esCitaPlan && servicioId && itemPlanId) {
      console.log('✅ Detectada cita vinculada a plan');
      console.log('📋 Plan:', itemPlanInfo?.plan_nombre);
      console.log('🦷 Servicio:', itemPlanInfo?.servicio_nombre);
      
      setFormData(prev => ({
        ...prev,
        servicio: servicioId,
        item_plan_tratamiento: itemPlanId,
        descripcion_procedimiento: itemPlanInfo?.notas || ''
      }));
    }
  }, [isOpen, esCitaPlan, servicioId, itemPlanId, itemPlanInfo]);

  // 🔑 Efecto: Obtener historial clínico del paciente
  useEffect(() => {
    if (isOpen && pacienteId) {
      obtenerHistorialClinico();
    }
  }, [isOpen, pacienteId]);

  const obtenerHistorialClinico = async () => {
    try {
      const response = await axiosInstance.get(
        `/api/historial/historiales/?paciente=${pacienteId}`
      );
      
      if (response.data.length > 0) {
        setFormData(prev => ({
          ...prev,
          historial_clinico: response.data[0].id
        }));
      }
    } catch (error) {
      console.error('Error al obtener historial:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.servicio) {
      toast.error('Debe seleccionar un servicio');
      return;
    }
    
    if (!formData.diagnostico.trim()) {
      toast.error('El diagnóstico es obligatorio');
      return;
    }

    setLoading(true);
    
    try {
      await axiosInstance.post('/api/historial/episodios/', formData);
      
      toast.success('Episodio registrado correctamente');
      onEpisodioCreado();
    } catch (error: any) {
      console.error('Error al crear episodio:', error);
      toast.error(error.response?.data?.error || 'Error al registrar episodio');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={modalOverlayStyles}>
      <div style={modalContentStyles}>
        {/* Header */}
        <div style={headerStyles}>
          <h2>📝 Registrar Episodio Clínico</h2>
          <button onClick={onClose} style={closeButtonStyles}>
            ✕
          </button>
        </div>

        {/* Paciente Info */}
        <div style={infoBoxStyles}>
          <strong>👤 Paciente:</strong> {pacienteNombre}
        </div>

        <form onSubmit={handleSubmit}>
          {/* SECCIÓN: Vinculación a Plan */}
          {esCitaPlan && itemPlanInfo ? (
            // ============ MODO 1: CITA DE PLAN (Solo Lectura) ============
            <PlanInfoReadOnly itemPlanInfo={itemPlanInfo} />
          ) : (
            // ============ MODO 2: CITA NORMAL (Campos Editables) ============
            <CamposEditables
              formData={formData}
              setFormData={setFormData}
            />
          )}

          {/* Motivo de Consulta */}
          <div style={fieldContainerStyles}>
            <label style={labelStyles}>
              📋 Motivo de Consulta
            </label>
            <textarea
              value={formData.motivo_consulta}
              onChange={(e) => setFormData({
                ...formData,
                motivo_consulta: e.target.value
              })}
              rows={2}
              style={textareaStyles}
            />
          </div>

          {/* Diagnóstico */}
          <div style={fieldContainerStyles}>
            <label style={labelStyles}>
              🩺 Diagnóstico <span style={{ color: '#dc2626' }}>*</span>
            </label>
            <textarea
              value={formData.diagnostico}
              onChange={(e) => setFormData({
                ...formData,
                diagnostico: e.target.value
              })}
              rows={3}
              style={textareaStyles}
              required
            />
          </div>

          {/* Descripción del Procedimiento */}
          <div style={fieldContainerStyles}>
            <label style={labelStyles}>
              🔧 Descripción del Procedimiento <span style={{ color: '#dc2626' }}>*</span>
            </label>
            <textarea
              value={formData.descripcion_procedimiento}
              onChange={(e) => setFormData({
                ...formData,
                descripcion_procedimiento: e.target.value
              })}
              rows={4}
              style={textareaStyles}
              required
            />
          </div>

          {/* Notas Privadas */}
          <div style={fieldContainerStyles}>
            <label style={labelStyles}>
              🔒 Notas Privadas (Internas)
            </label>
            <textarea
              value={formData.notas_privadas}
              onChange={(e) => setFormData({
                ...formData,
                notas_privadas: e.target.value
              })}
              rows={2}
              style={textareaStyles}
              placeholder="Notas internas del odontólogo..."
            />
          </div>

          {/* Botones */}
          <div style={buttonsContainerStyles}>
            <button
              type="button"
              onClick={onClose}
              style={cancelButtonStyles}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              style={submitButtonStyles}
              disabled={loading}
            >
              {loading ? '⏳ Guardando...' : '💾 Guardar Episodio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================================
// Componente: Información del Plan (Solo Lectura)
// ============================================================
function PlanInfoReadOnly({ itemPlanInfo }: { itemPlanInfo: ItemPlanInfo }) {
  return (
    <div style={{
      backgroundColor: '#d1fae5',
      border: '2px solid #10b981',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '24px'
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
        gap: '12px'
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
  );
}

// ============================================================
// Componente: Campos Editables (Citas Normales)
// ============================================================
interface CamposEditablesProps {
  formData: any;
  setFormData: (data: any) => void;
}

function CamposEditables({ formData, setFormData }: CamposEditablesProps) {
  // TODO: Cargar planes y servicios del backend
  return (
    <div style={{ marginBottom: '24px' }}>
      {/* Aquí irían los dropdowns de planes y servicios */}
      <p style={{ color: '#6b7280', fontSize: '14px' }}>
        Seleccione el servicio realizado y opcionalmente vincule a un plan.
      </p>
    </div>
  );
}

// ============================================================
// Estilos (puedes moverlos a un archivo CSS)
// ============================================================
const modalOverlayStyles: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000
};

const modalContentStyles: React.CSSProperties = {
  backgroundColor: 'white',
  borderRadius: '12px',
  maxWidth: '700px',
  width: '90%',
  maxHeight: '90vh',
  overflow: 'auto',
  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
};

const headerStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '20px 24px',
  borderBottom: '1px solid #e5e7eb'
};

const closeButtonStyles: React.CSSProperties = {
  background: 'none',
  border: 'none',
  fontSize: '24px',
  cursor: 'pointer',
  color: '#6b7280'
};

const infoBoxStyles: React.CSSProperties = {
  backgroundColor: '#f3f4f6',
  padding: '12px 16px',
  margin: '0 24px 24px',
  borderRadius: '8px'
};

const fieldContainerStyles: React.CSSProperties = {
  marginBottom: '20px',
  padding: '0 24px'
};

const labelStyles: React.CSSProperties = {
  display: 'block',
  fontSize: '14px',
  fontWeight: '500',
  color: '#374151',
  marginBottom: '8px'
};

const textareaStyles: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  border: '1px solid #d1d5db',
  borderRadius: '8px',
  fontSize: '14px',
  outline: 'none',
  fontFamily: 'inherit',
  resize: 'vertical'
};

const buttonsContainerStyles: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  padding: '20px 24px',
  borderTop: '1px solid #e5e7eb',
  justifyContent: 'flex-end'
};

const cancelButtonStyles: React.CSSProperties = {
  padding: '10px 20px',
  border: '1px solid #d1d5db',
  borderRadius: '8px',
  backgroundColor: 'white',
  color: '#374151',
  cursor: 'pointer',
  fontWeight: '500'
};

const submitButtonStyles: React.CSSProperties = {
  padding: '10px 20px',
  border: 'none',
  borderRadius: '8px',
  backgroundColor: '#3b82f6',
  color: 'white',
  cursor: 'pointer',
  fontWeight: '500'
};
```

---

## ✅ Resumen de Cambios Necesarios

1. **Crear archivo de tipos**: `types/agenda.ts`
2. **Actualizar AgendaCitas.tsx**:
   - Importar tipos
   - Pasar `itemPlanInfo` al modal
   - Usar `item_plan_info?.servicio_id` en lugar de `servicio`
3. **Actualizar ModalRegistrarEpisodio.tsx**:
   - Recibir prop `itemPlanInfo`
   - Implementar componente `PlanInfoReadOnly`
   - Renderizado condicional basado en `esCitaPlan`

¡Con estos cambios, el flujo de atención de citas quedará completo! 🎉
