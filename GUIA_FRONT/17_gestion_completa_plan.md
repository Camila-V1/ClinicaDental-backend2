# 🦷 GUÍA 17: GESTIÓN COMPLETA DEL PLAN DE TRATAMIENTO

## 🎯 Objetivo

Implementar la **vista completa de gestión del plan** con todas las operaciones del ciclo de vida:

1. ✅ Ver detalle completo del plan
2. 📋 Presentar plan al paciente (PROPUESTO → PRESENTADO)
3. ✔️ Aceptar/Rechazar plan (PRESENTADO → ACEPTADO/RECHAZADO)
4. ✏️ Editar ítems del plan
5. 🗑️ Eliminar ítems
6. ✅ Completar ítems manualmente (sin episodio vinculado)
7. 📊 Visualizar progreso y estados
8. 📄 Generar presupuesto PDF (bonus)

Esta es la **interfaz principal de gestión** - desde crear el plan hasta completarlo.

---

## 📋 Transiciones de Estado del Plan

```
PROPUESTO ──► PRESENTADO ──► ACEPTADO ──► EN_PROGRESO ──► COMPLETADO
    │              │
    └──► RECHAZADO └──► RECHAZADO
```

### Estados Detallados

| Estado | Descripción | Puede Editar Ítems | Puede Vincular Episodios |
|--------|-------------|-------------------|-------------------------|
| **PROPUESTO** | Borrador inicial | ✅ Sí | ❌ No |
| **PRESENTADO** | Mostrado al paciente | ✅ Sí | ❌ No |
| **ACEPTADO** | Paciente aceptó | ❌ No* | ✅ Sí |
| **EN_PROGRESO** | En ejecución (automático) | ❌ No | ✅ Sí |
| **COMPLETADO** | Finalizado (automático) | ❌ No | ❌ No |
| **RECHAZADO** | Paciente rechazó | ❌ No | ❌ No |

*Nota: En ACEPTADO no se pueden editar ítems para mantener integridad del presupuesto aceptado.

---

## 🛠️ Implementación Frontend

### PASO 1: Actualizar Servicio de Planes

**Archivo:** `src/services/planesService.ts` (AGREGAR estas funciones)

```typescript
// ============================================================================
// NUEVAS FUNCIONES PARA GESTIÓN
// ============================================================================

/**
 * Presentar plan al paciente (PROPUESTO → PRESENTADO)
 */
export const presentarPlan = async (planId: number): Promise<PlanDeTratamiento> => {
  const response = await api.patch<PlanDeTratamiento>(
    `/api/tratamientos/planes/${planId}/`,
    { estado: 'PRESENTADO' }
  );
  return response.data;
};

/**
 * Aceptar plan (PRESENTADO → ACEPTADO)
 */
export const aceptarPlan = async (planId: number): Promise<PlanDeTratamiento> => {
  const response = await api.patch<PlanDeTratamiento>(
    `/api/tratamientos/planes/${planId}/`,
    { estado: 'ACEPTADO' }
  );
  return response.data;
};

/**
 * Rechazar plan (PROPUESTO/PRESENTADO → RECHAZADO)
 */
export const rechazarPlan = async (
  planId: number,
  motivoRechazo?: string
): Promise<PlanDeTratamiento> => {
  const response = await api.patch<PlanDeTratamiento>(
    `/api/tratamientos/planes/${planId}/`,
    { 
      estado: 'RECHAZADO',
      observaciones: motivoRechazo || undefined
    }
  );
  return response.data;
};

/**
 * Cancelar plan
 */
export const cancelarPlan = async (
  planId: number,
  motivoCancelacion?: string
): Promise<PlanDeTratamiento> => {
  const response = await api.patch<PlanDeTratamiento>(
    `/api/tratamientos/planes/${planId}/`,
    { 
      estado: 'CANCELADO',
      observaciones: motivoCancelacion || undefined
    }
  );
  return response.data;
};

/**
 * Eliminar ítem del plan
 */
export const eliminarItemPlan = async (itemId: number): Promise<void> => {
  await api.delete(`/api/tratamientos/items/${itemId}/`);
};

/**
 * Completar ítem manualmente (sin episodio vinculado)
 */
export const completarItemManual = async (itemId: number): Promise<ItemPlanTratamiento> => {
  const response = await api.patch<ItemPlanTratamiento>(
    `/api/tratamientos/items/${itemId}/`,
    { estado: 'COMPLETADO' }
  );
  return response.data;
};

/**
 * Actualizar ítem del plan
 */
export const actualizarItemPlan = async (
  itemId: number,
  datos: Partial<CrearItemPlanDTO>
): Promise<ItemPlanTratamiento> => {
  const response = await api.patch<ItemPlanTratamiento>(
    `/api/tratamientos/items/${itemId}/`,
    datos
  );
  return response.data;
};
```

---

### PASO 2: Crear Vista Completa de Detalle del Plan

**Archivo:** `src/pages/odontologo/PlanDetalle.tsx` (VERSIÓN COMPLETA)

```typescript
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  obtenerPlan,
  presentarPlan,
  aceptarPlan,
  rechazarPlan,
  cancelarPlan,
  eliminarItemPlan,
  completarItemManual,
  type PlanDeTratamiento,
  type ItemPlanTratamiento
} from '../../services/planesService';
import ModalAgregarItem from '../../components/planes/ModalAgregarItem';
import ModalEditarItem from '../../components/planes/ModalEditarItem';

export default function PlanDetalle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [plan, setPlan] = useState<PlanDeTratamiento | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalAgregarAbierto, setModalAgregarAbierto] = useState(false);
  const [modalEditarAbierto, setModalEditarAbierto] = useState(false);
  const [itemAEditar, setItemAEditar] = useState<ItemPlanTratamiento | null>(null);
  const [procesando, setProcesando] = useState(false);

  useEffect(() => {
    if (id) {
      cargarPlan();
    }
  }, [id]);

  const cargarPlan = async () => {
    try {
      setLoading(true);
      const data = await obtenerPlan(Number(id));
      setPlan(data);
    } catch (error) {
      console.error('Error al cargar plan:', error);
      alert('Error al cargar plan de tratamiento');
      navigate('/odontologo/planes');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // ACCIONES DEL PLAN
  // ============================================================================

  const handlePresentarPlan = async () => {
    if (!plan) return;
    
    if (plan.cantidad_items === 0) {
      alert('⚠️ No puedes presentar un plan sin servicios. Agrega al menos un servicio.');
      return;
    }
    
    if (!confirm(`¿Presentar plan "${plan.titulo}" al paciente?\n\nEl plan quedará como PRESENTADO y podrás compartirlo con el paciente.`)) {
      return;
    }

    try {
      setProcesando(true);
      const planActualizado = await presentarPlan(plan.id);
      setPlan(planActualizado);
      alert('✅ Plan presentado exitosamente');
    } catch (error: any) {
      console.error('Error al presentar plan:', error);
      alert('❌ Error al presentar plan: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  const handleAceptarPlan = async () => {
    if (!plan) return;
    
    if (!confirm(`¿Marcar plan "${plan.titulo}" como ACEPTADO?\n\n⚠️ Una vez aceptado:\n- No podrás editar los ítems\n- Se podrán vincular episodios\n- El presupuesto queda CONGELADO`)) {
      return;
    }

    try {
      setProcesando(true);
      const planActualizado = await aceptarPlan(plan.id);
      setPlan(planActualizado);
      alert('✅ Plan aceptado. Ya puedes vincular episodios de atención.');
    } catch (error: any) {
      console.error('Error al aceptar plan:', error);
      alert('❌ Error al aceptar plan: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  const handleRechazarPlan = async () => {
    if (!plan) return;
    
    const motivo = prompt('¿Por qué se rechaza el plan? (Opcional)');
    
    if (motivo === null) return; // Canceló
    
    try {
      setProcesando(true);
      const planActualizado = await rechazarPlan(plan.id, motivo);
      setPlan(planActualizado);
      alert('❌ Plan marcado como RECHAZADO');
    } catch (error: any) {
      console.error('Error al rechazar plan:', error);
      alert('❌ Error al rechazar plan: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  const handleCancelarPlan = async () => {
    if (!plan) return;
    
    const motivo = prompt('¿Por qué se cancela el plan?');
    
    if (!motivo) {
      alert('Debes indicar un motivo de cancelación');
      return;
    }
    
    if (!confirm(`⚠️ ¿CANCELAR plan "${plan.titulo}"?\n\nEsta acción no se puede deshacer.`)) {
      return;
    }
    
    try {
      setProcesando(true);
      const planActualizado = await cancelarPlan(plan.id, motivo);
      setPlan(planActualizado);
      alert('🚫 Plan cancelado');
    } catch (error: any) {
      console.error('Error al cancelar plan:', error);
      alert('❌ Error al cancelar plan: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  // ============================================================================
  // ACCIONES DE ÍTEMS
  // ============================================================================

  const handleEliminarItem = async (item: ItemPlanTratamiento) => {
    if (!plan) return;
    
    if (item.estado !== 'PENDIENTE') {
      alert('⚠️ Solo puedes eliminar ítems en estado PENDIENTE');
      return;
    }
    
    if (!confirm(`¿Eliminar servicio "${item.servicio_nombre}"?\n\nEsta acción no se puede deshacer.`)) {
      return;
    }

    try {
      setProcesando(true);
      await eliminarItemPlan(item.id);
      await cargarPlan(); // Recargar plan completo
      alert('🗑️ Servicio eliminado del plan');
    } catch (error: any) {
      console.error('Error al eliminar ítem:', error);
      alert('❌ Error al eliminar ítem: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  const handleCompletarItem = async (item: ItemPlanTratamiento) => {
    if (!plan) return;
    
    if (!confirm(`¿Marcar "${item.servicio_nombre}" como COMPLETADO?\n\nUsa esta opción solo si el servicio se realizó sin registrar un episodio de atención.`)) {
      return;
    }

    try {
      setProcesando(true);
      await completarItemManual(item.id);
      await cargarPlan();
      alert('✅ Ítem marcado como completado');
    } catch (error: any) {
      console.error('Error al completar ítem:', error);
      alert('❌ Error al completar ítem: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcesando(false);
    }
  };

  const handleEditarItem = (item: ItemPlanTratamiento) => {
    setItemAEditar(item);
    setModalEditarAbierto(true);
  };

  // ============================================================================
  // UTILIDADES
  // ============================================================================

  const getEstadoBadgeClass = (estado: string) => {
    const classes = {
      'PROPUESTO': 'bg-gray-100 text-gray-800',
      'PRESENTADO': 'bg-blue-100 text-blue-800',
      'ACEPTADO': 'bg-green-100 text-green-800',
      'EN_PROGRESO': 'bg-yellow-100 text-yellow-800',
      'COMPLETADO': 'bg-purple-100 text-purple-800',
      'RECHAZADO': 'bg-red-100 text-red-800',
      'CANCELADO': 'bg-red-100 text-red-800'
    };
    return classes[estado as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  const getItemEstadoBadgeClass = (estado: string) => {
    const classes = {
      'PENDIENTE': 'bg-gray-100 text-gray-800',
      'EN_PROGRESO': 'bg-yellow-100 text-yellow-800',
      'COMPLETADO': 'bg-green-100 text-green-800'
    };
    return classes[estado as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (loading || !plan) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/odontologo/planes')}
          className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
        >
          ← Volver a Planes
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{plan.titulo}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEstadoBadgeClass(plan.estado)}`}>
                {plan.estado_display}
              </span>
            </div>
            <p className="text-gray-600">👤 {plan.paciente_info.nombre_completo}</p>
            <p className="text-sm text-gray-500 mt-1">
              Creado: {new Date(plan.creado).toLocaleDateString('es-ES', { 
                year: 'numeric', month: 'long', day: 'numeric' 
              })}
            </p>
          </div>
          
          {/* Botones de Acción */}
          <div className="flex gap-2">
            {plan.puede_ser_editado && (
              <button
                onClick={() => setModalAgregarAbierto(true)}
                disabled={procesando}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                ➕ Agregar Servicio
              </button>
            )}
            
            {plan.estado === 'PROPUESTO' && (
              <button
                onClick={handlePresentarPlan}
                disabled={procesando || plan.cantidad_items === 0}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
              >
                📋 Presentar Plan
              </button>
            )}
            
            {plan.estado === 'PRESENTADO' && (
              <>
                <button
                  onClick={handleAceptarPlan}
                  disabled={procesando}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  ✔️ Aceptar Plan
                </button>
                <button
                  onClick={handleRechazarPlan}
                  disabled={procesando}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  ✖️ Rechazar
                </button>
              </>
            )}
            
            {(['PROPUESTO', 'PRESENTADO'] as const).includes(plan.estado as any) && (
              <button
                onClick={handleRechazarPlan}
                disabled={procesando}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                ✖️ Rechazar
              </button>
            )}
            
            {(['ACEPTADO', 'EN_PROGRESO'] as const).includes(plan.estado as any) && (
              <button
                onClick={handleCancelarPlan}
                disabled={procesando}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                🚫 Cancelar Plan
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Observaciones */}
      {plan.observaciones && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>📝 Observaciones:</strong> {plan.observaciones}
          </p>
        </div>
      )}

      {/* Precio Total y Progreso */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Card Precio Total */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6 shadow-lg">
          <p className="text-green-100 text-sm mb-2">Precio Total del Plan</p>
          <p className="text-4xl font-bold">${parseFloat(plan.precio_total_plan).toFixed(2)}</p>
          <div className="mt-4 pt-4 border-t border-green-400">
            <p className="text-sm text-green-100">
              💰 {plan.cantidad_items} servicio{plan.cantidad_items !== 1 ? 's' : ''} incluido{plan.cantidad_items !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Card Progreso */}
        <div className="bg-white rounded-lg p-6 shadow-lg border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <p className="text-sm font-medium text-gray-600">Progreso del Tratamiento</p>
            <p className="text-3xl font-bold text-blue-600">{plan.porcentaje_completado}%</p>
          </div>
          
          {/* Barra de Progreso */}
          <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${plan.porcentaje_completado}%` }}
            ></div>
          </div>
          
          {/* Fechas */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            {plan.fecha_inicio && (
              <div>
                <p className="text-gray-500">Inicio:</p>
                <p className="font-semibold">{new Date(plan.fecha_inicio).toLocaleDateString('es-ES')}</p>
              </div>
            )}
            {plan.fecha_finalizacion && (
              <div>
                <p className="text-gray-500">Finalización:</p>
                <p className="font-semibold">{new Date(plan.fecha_finalizacion).toLocaleDateString('es-ES')}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Lista de Ítems */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          📋 Servicios del Plan ({plan.cantidad_items})
        </h2>
        
        {plan.items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-lg mb-2">Aún no hay servicios en este plan</p>
            <p className="text-sm mb-4">Agrega servicios para comenzar a construir el plan de tratamiento</p>
            {plan.puede_ser_editado && (
              <button
                onClick={() => setModalAgregarAbierto(true)}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                ➕ Agregar primer servicio
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {plan.items.map((item, index) => (
              <div 
                key={item.id} 
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
              >
                <div className="flex justify-between items-start">
                  {/* Info del Ítem */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        #{index + 1}
                      </span>
                      <h3 className="font-bold text-gray-900">{item.servicio_nombre}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getItemEstadoBadgeClass(item.estado)}`}>
                        {item.estado_display}
                      </span>
                    </div>
                    
                    {item.insumo_nombre && (
                      <p className="text-sm text-gray-600 mb-2">
                        🎨 Material: <span className="font-medium">{item.insumo_nombre}</span>
                      </p>
                    )}
                    
                    {item.notas && (
                      <p className="text-sm text-gray-600 italic mb-2">
                        📝 {item.notas}
                      </p>
                    )}
                    
                    {item.fecha_estimada && (
                      <p className="text-xs text-gray-500">
                        📅 Fecha estimada: {new Date(item.fecha_estimada).toLocaleDateString('es-ES')}
                      </p>
                    )}
                  </div>
                  
                  {/* Precio y Acciones */}
                  <div className="text-right ml-4">
                    <p className="text-2xl font-bold text-green-600 mb-3">
                      {item.precio_total_formateado}
                    </p>
                    
                    <div className="text-xs text-gray-500 mb-3">
                      <p>Honorarios: ${parseFloat(item.precio_servicio_snapshot).toFixed(2)}</p>
                      {parseFloat(item.precio_materiales_fijos_snapshot) > 0 && (
                        <p>Materiales fijos: ${parseFloat(item.precio_materiales_fijos_snapshot).toFixed(2)}</p>
                      )}
                      {item.insumo_nombre && parseFloat(item.precio_insumo_seleccionado_snapshot) > 0 && (
                        <p>Material: ${parseFloat(item.precio_insumo_seleccionado_snapshot).toFixed(2)}</p>
                      )}
                    </div>
                    
                    {/* Botones de Acción */}
                    {plan.puede_ser_editado && item.estado === 'PENDIENTE' && (
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => handleEditarItem(item)}
                          className="text-blue-600 hover:text-blue-700 text-sm px-2 py-1 border border-blue-300 rounded hover:bg-blue-50"
                          title="Editar ítem"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleEliminarItem(item)}
                          className="text-red-600 hover:text-red-700 text-sm px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                          title="Eliminar ítem"
                        >
                          🗑️
                        </button>
                      </div>
                    )}
                    
                    {plan.estado === 'EN_PROGRESO' && item.estado === 'EN_PROGRESO' && (
                      <button
                        onClick={() => handleCompletarItem(item)}
                        disabled={procesando}
                        className="text-green-600 hover:text-green-700 text-sm px-3 py-1 border border-green-300 rounded hover:bg-green-50 disabled:opacity-50"
                      >
                        ✅ Completar
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Información Adicional */}
      <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Información del Plan</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          {plan.estado === 'PROPUESTO' && (
            <>
              <li>• Puedes agregar, editar y eliminar servicios mientras el plan esté en estado PROPUESTO</li>
              <li>• Presenta el plan al paciente cuando esté listo</li>
            </>
          )}
          {plan.estado === 'PRESENTADO' && (
            <>
              <li>• El plan ha sido presentado al paciente</li>
              <li>• Marca como ACEPTADO cuando el paciente confirme, o RECHAZADO si no acepta</li>
            </>
          )}
          {plan.estado === 'ACEPTADO' && (
            <>
              <li>• El plan ha sido aceptado por el paciente - presupuesto CONGELADO</li>
              <li>• Ya puedes vincular episodios de atención desde la agenda</li>
              <li>• El plan pasará automáticamente a EN_PROGRESO cuando se cree el primer episodio</li>
            </>
          )}
          {plan.estado === 'EN_PROGRESO' && (
            <>
              <li>• Tratamiento en curso - {plan.porcentaje_completado}% completado</li>
              <li>• Los ítems se completarán automáticamente al vincular episodios</li>
              <li>• El plan se completará automáticamente cuando todos los ítems estén completados</li>
            </>
          )}
          {plan.estado === 'COMPLETADO' && (
            <li>✅ Tratamiento finalizado exitosamente el {plan.fecha_finalizacion ? new Date(plan.fecha_finalizacion).toLocaleDateString('es-ES') : ''}</li>
          )}
        </ul>
      </div>

      {/* Modales */}
      <ModalAgregarItem
        isOpen={modalAgregarAbierto}
        onClose={() => setModalAgregarAbierto(false)}
        planId={plan.id}
        onItemAgregado={cargarPlan}
      />
      
      {itemAEditar && (
        <ModalEditarItem
          isOpen={modalEditarAbierto}
          onClose={() => {
            setModalEditarAbierto(false);
            setItemAEditar(null);
          }}
          item={itemAEditar}
          onItemActualizado={cargarPlan}
        />
      )}
    </div>
  );
}
```

---

### PASO 3: Crear Modal para Editar Ítem

**Archivo:** `src/components/planes/ModalEditarItem.tsx`

```typescript
import { useState, useEffect } from 'react';
import { actualizarItemPlan, type ItemPlanTratamiento, type CrearItemPlanDTO } from '../../services/planesService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  item: ItemPlanTratamiento;
  onItemActualizado: () => void;
}

export default function ModalEditarItem({ isOpen, onClose, item, onItemActualizado }: Props) {
  const [notas, setNotas] = useState(item.notas || '');
  const [fechaEstimada, setFechaEstimada] = useState(
    item.fecha_estimada ? item.fecha_estimada.split('T')[0] : ''
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setNotas(item.notas || '');
      setFechaEstimada(item.fecha_estimada ? item.fecha_estimada.split('T')[0] : '');
    }
  }, [isOpen, item]);

  const handleActualizar = async () => {
    try {
      setLoading(true);
      
      const datos: Partial<CrearItemPlanDTO> = {
        notas: notas || undefined,
        fecha_estimada: fechaEstimada || undefined
      };

      await actualizarItemPlan(item.id, datos);
      
      alert('✅ Ítem actualizado exitosamente');
      onItemActualizado();
      onClose();
      
    } catch (error: any) {
      console.error('Error al actualizar ítem:', error);
      alert('❌ Error al actualizar ítem: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        {/* Header */}
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">✏️ Editar Servicio</h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Info del Servicio */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
            <h3 className="font-bold text-lg text-gray-900 mb-2">{item.servicio_nombre}</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Precio Total:</span>
                <span className="font-semibold ml-2">{item.precio_total_formateado}</span>
              </div>
              {item.insumo_nombre && (
                <div>
                  <span className="text-gray-600">Material:</span>
                  <span className="font-semibold ml-2">{item.insumo_nombre}</span>
                </div>
              )}
            </div>
          </div>

          {/* Formulario */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notas
              </label>
              <textarea
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Notas adicionales sobre este procedimiento..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha Estimada
              </label>
              <input
                type="date"
                value={fechaEstimada}
                onChange={(e) => setFechaEstimada(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Info */}
          <div className="mt-6 bg-yellow-50 p-3 rounded border border-yellow-200">
            <p className="text-xs text-yellow-800">
              ⚠️ No puedes cambiar el servicio ni el material seleccionado. Solo puedes editar notas y fecha estimada.
            </p>
          </div>

          {/* Botones */}
          <div className="flex justify-between mt-6">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleActualizar}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                '💾 Guardar Cambios'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## ✅ Checklist de Implementación

- [ ] Actualizar `src/services/planesService.ts` con nuevas funciones de gestión
- [ ] Actualizar `src/pages/odontologo/PlanDetalle.tsx` (versión completa)
- [ ] Crear `src/components/planes/ModalEditarItem.tsx`
- [ ] Probar flujo completo:
  - [ ] Crear plan → Agregar ítems → Presentar → Aceptar → Vincular episodios → Completar
  - [ ] Editar ítems en estado PROPUESTO
  - [ ] Eliminar ítems en estado PENDIENTE
  - [ ] Completar ítems manualmente
  - [ ] Rechazar/Cancelar planes

---

## 🧪 Cómo Probar

### Flujo Completo de Vida del Plan

1. **Crear plan** (Guía 15)
   - Estado inicial: PROPUESTO

2. **Agregar servicios** (Guía 16)
   - Agregar 3-4 servicios diferentes
   - Verificar que se calculen precios correctamente

3. **Editar ítem**
   - Click en ✏️ en un ítem
   - Cambiar notas y fecha estimada
   - Guardar y verificar cambios

4. **Presentar plan**
   - Click en "📋 Presentar Plan"
   - Estado cambia a: PRESENTADO
   - Nota: Ya no puedes agregar más ítems (solo si lo aceptas o rechazas primero)

5. **Aceptar plan**
   - Click en "✔️ Aceptar Plan"
   - Estado cambia a: ACEPTADO
   - ⚠️ Ahora NO puedes editar ítems (presupuesto congelado)

6. **Vincular episodio** (Guía 18 - próxima)
   - Ir a agenda y crear episodio vinculado
   - Plan cambia automáticamente a: EN_PROGRESO

7. **Completar ítems**
   - Opción A: Vincular episodios (automático)
   - Opción B: Completar manualmente (button ✅ Completar)

8. **Plan completado**
   - Cuando todos los ítems estén completados
   - Estado cambia automáticamente a: COMPLETADO

### Flujos Alternativos

**Rechazar plan:**
- Desde PROPUESTO o PRESENTADO
- Click en "✖️ Rechazar"
- Ingresar motivo
- Estado: RECHAZADO

**Cancelar plan:**
- Desde ACEPTADO o EN_PROGRESO
- Click en "🚫 Cancelar Plan"
- Ingresar motivo obligatorio
- Estado: CANCELADO

---

## 🎯 Características Clave Implementadas

### ✅ Gestión de Estados
- ✅ Transiciones automáticas y manuales
- ✅ Validaciones según estado actual
- ✅ Botones contextuales (solo aparecen cuando aplica)

### 📊 Visualización
- ✅ Card de precio total con desglose
- ✅ Barra de progreso animada
- ✅ Badges de estados con colores
- ✅ Fechas de inicio y finalización

### ✏️ Edición de Ítems
- ✅ Editar notas y fecha estimada
- ✅ Eliminar ítems en PENDIENTE
- ✅ Completar ítems manualmente
- ✅ Desglose de precios por ítem

### 🔒 Validaciones
- ✅ No presentar plan vacío
- ✅ No editar ítems en plan ACEPTADO
- ✅ Solo eliminar ítems PENDIENTES
- ✅ Confirmaciones para acciones críticas

---

## 📝 Notas Importantes

### ⚡ Transiciones Automáticas (Backend via Signals)

```python
# Automáticas desde el backend:
ACEPTADO → EN_PROGRESO  # Cuando se crea primer episodio vinculado
EN_PROGRESO → COMPLETADO  # Cuando todos los ítems están completados
PENDIENTE → EN_PROGRESO  # Ítem cuando se vincula primer episodio
EN_PROGRESO → COMPLETADO  # Ítem cuando se completa
```

### 🔐 Permisos por Estado

| Acción | PROPUESTO | PRESENTADO | ACEPTADO | EN_PROGRESO |
|--------|-----------|------------|----------|-------------|
| Agregar ítems | ✅ | ✅ | ❌ | ❌ |
| Editar ítems | ✅ | ✅ | ❌ | ❌ |
| Eliminar ítems | ✅ | ✅ | ❌ | ❌ |
| Presentar | ✅ | ❌ | ❌ | ❌ |
| Aceptar | ❌ | ✅ | ❌ | ❌ |
| Rechazar | ✅ | ✅ | ❌ | ❌ |
| Cancelar | ❌ | ❌ | ✅ | ✅ |
| Vincular episodios | ❌ | ❌ | ✅ | ✅ |

### 💡 Mejores Prácticas

1. **Presupuesto Congelado:** Una vez aceptado, NO se editan precios ni servicios
2. **Completar Manual:** Solo usar cuando NO se registró episodio de atención
3. **Observaciones:** Siempre agregar motivo al rechazar/cancelar
4. **Validar antes de Presentar:** Revisar que todos los ítems tengan sentido

---

## 🚀 Próximos Pasos

**Guía 18:** Vincular Episodios desde la Agenda
- Detectar planes activos del paciente
- Mostrar selector de ítems del plan
- Vincular episodio a ítem específico
- Actualización automática de progreso

---

**✅ Sistema de Gestión Completa del Plan Implementado!** 🎉

El plan ahora tiene un ciclo de vida completo desde creación hasta finalización, con todas las validaciones y transiciones necesarias.
