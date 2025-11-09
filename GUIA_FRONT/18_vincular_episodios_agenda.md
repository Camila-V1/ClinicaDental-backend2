# 🦷 GUÍA 18: VINCULAR EPISODIOS DESDE LA AGENDA AL PLAN

## 🎯 Objetivo

Implementar la **conexión entre la agenda y los planes de tratamiento**:

1. 🔍 Detectar automáticamente si el paciente tiene planes activos (ACEPTADO o EN_PROGRESO)
2. 📋 Mostrar selector de ítems del plan disponibles
3. 🔗 Vincular el episodio de atención a un ítem específico del plan
4. 📊 Actualización automática del progreso (gracias a las signals del backend)
5. 🆓 Opción de crear "episodio libre" (sin vincular a plan)

Esta es la **integración final** - cuando un odontólogo atiende, puede registrar que está completando un servicio del plan.

---

## 🔄 Flujo Completo del Sistema

```
1. CREAR PLAN (Guía 15)
   └─► Agregar servicios (Guía 16)
       └─► Presentar → Aceptar (Guía 17)
           └─► 🎯 VINCULAR EPISODIOS DESDE AGENDA (Guía 18) ◄── ESTAMOS AQUÍ
               └─► Plan se completa automáticamente
```

---

## 📋 Lógica de Vinculación

### Cuando el odontólogo abre el modal de atención:

```typescript
1. GET /api/tratamientos/planes/?paciente={id}&estado=ACEPTADO,EN_PROGRESO
   └─► ¿Tiene planes activos?
       
       ✅ SÍ → Mostrar selector de ítems disponibles
                └─► Filtrar solo ítems PENDIENTE o EN_PROGRESO
                    └─► Al guardar: vincular episodio.item_plan_tratamiento = item.id
       
       ❌ NO → Episodio libre normal (sin vincular)
```

### Backend (Automático via Signals):

```python
# Cuando se guarda un episodio con item_plan_tratamiento:
1. Ítem: PENDIENTE → EN_PROGRESO (primer episodio)
2. Plan: ACEPTADO → EN_PROGRESO (primer episodio del plan)
3. Si el ítem requería N sesiones y ya se completaron: COMPLETADO
4. Si todos los ítems están completados: Plan → COMPLETADO
```

---

## 🛠️ Implementación Frontend

### PASO 1: Actualizar Servicio de Planes

**Archivo:** `src/services/planesService.ts` (AGREGAR esta función)

```typescript
/**
 * Obtener planes activos de un paciente (ACEPTADO o EN_PROGRESO)
 */
export const obtenerPlanesActivos = async (pacienteId: number): Promise<PlanDeTratamiento[]> => {
  const response = await api.get<PlanDeTratamiento[]>(
    `/api/tratamientos/planes/?paciente=${pacienteId}&estado=ACEPTADO,EN_PROGRESO`
  );
  return response.data;
};

/**
 * Obtener ítems disponibles para vincular de un plan
 * (solo PENDIENTE o EN_PROGRESO)
 */
export const obtenerItemsDisponibles = (plan: PlanDeTratamiento): ItemPlanTratamiento[] => {
  return plan.items.filter(item => 
    item.estado === 'PENDIENTE' || item.estado === 'EN_PROGRESO'
  );
};
```

---

### PASO 2: Actualizar Modal de Atención (Guía 13 - Modificada)

**Archivo:** `src/components/agenda/ModalAgregarEpisodio.tsx` (ACTUALIZAR COMPLETO)

```typescript
import { useState, useEffect } from 'react';
import { crearEpisodio, type CrearEpisodioDTO } from '../../services/historialService';
import { obtenerPlanesActivos, obtenerItemsDisponibles, type PlanDeTratamiento, type ItemPlanTratamiento } from '../../services/planesService';
import { obtenerServicios, type Servicio } from '../../services/serviciosService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  citaId: number;
  pacienteId: number;
  pacienteNombre: string;
  onEpisodioCreado: () => void;
}

export default function ModalAgregarEpisodio({ 
  isOpen, 
  onClose, 
  citaId, 
  pacienteId, 
  pacienteNombre,
  onEpisodioCreado 
}: Props) {
  // Estados básicos
  const [motivo, setMotivo] = useState('');
  const [diagnostico, setDiagnostico] = useState('');
  const [tratamiento, setTratamiento] = useState('');
  const [observaciones, setObservaciones] = useState('');
  const [loading, setLoading] = useState(false);

  // Estados para planes
  const [planesActivos, setPlanesActivos] = useState<PlanDeTratamiento[]>([]);
  const [cargandoPlanes, setCargandoPlanes] = useState(false);
  const [modoSeleccion, setModoSeleccion] = useState<'plan' | 'libre'>('libre');
  const [planSeleccionado, setPlanSeleccionado] = useState<PlanDeTratamiento | null>(null);
  const [itemSeleccionado, setItemSeleccionado] = useState<ItemPlanTratamiento | null>(null);

  // Estados para servicios (modo libre)
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [servicioSeleccionado, setServicioSeleccionado] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen) {
      cargarPlanesActivos();
      cargarServicios();
    } else {
      // Reset al cerrar
      resetForm();
    }
  }, [isOpen, pacienteId]);

  const cargarPlanesActivos = async () => {
    try {
      setCargandoPlanes(true);
      const planes = await obtenerPlanesActivos(pacienteId);
      setPlanesActivos(planes);
      
      // Si hay planes activos, sugerir modo plan
      if (planes.length > 0) {
        setModoSeleccion('plan');
      }
    } catch (error) {
      console.error('Error al cargar planes activos:', error);
      // No mostrar error, simplemente continuar sin planes
      setPlanesActivos([]);
    } finally {
      setCargandoPlanes(false);
    }
  };

  const cargarServicios = async () => {
    try {
      const data = await obtenerServicios({ activo: true });
      setServicios(data);
    } catch (error) {
      console.error('Error al cargar servicios:', error);
    }
  };

  const resetForm = () => {
    setMotivo('');
    setDiagnostico('');
    setTratamiento('');
    setObservaciones('');
    setModoSeleccion('libre');
    setPlanSeleccionado(null);
    setItemSeleccionado(null);
    setServicioSeleccionado(null);
  };

  const handleCrearEpisodio = async () => {
    // Validaciones
    if (!motivo.trim()) {
      alert('El motivo de consulta es obligatorio');
      return;
    }

    if (modoSeleccion === 'plan' && !itemSeleccionado) {
      alert('Debes seleccionar un servicio del plan');
      return;
    }

    if (modoSeleccion === 'libre' && !servicioSeleccionado) {
      alert('Debes seleccionar un servicio');
      return;
    }

    try {
      setLoading(true);

      const datos: CrearEpisodioDTO = {
        cita: citaId,
        motivo_consulta: motivo,
        diagnostico: diagnostico || undefined,
        tratamiento_realizado: tratamiento || undefined,
        observaciones: observaciones || undefined,
        // 🎯 CLAVE: Vincular a ítem del plan si está en modo plan
        item_plan_tratamiento: modoSeleccion === 'plan' && itemSeleccionado 
          ? itemSeleccionado.id 
          : undefined,
        // Si es episodio libre, vincular servicio directamente
        servicio: modoSeleccion === 'libre' && servicioSeleccionado
          ? servicioSeleccionado
          : undefined
      };

      await crearEpisodio(datos);

      alert('✅ Episodio de atención registrado exitosamente');
      
      onEpisodioCreado();
      onClose();
      resetForm();

    } catch (error: any) {
      console.error('Error al crear episodio:', error);
      alert('❌ Error al crear episodio: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const itemsDisponibles = planSeleccionado ? obtenerItemsDisponibles(planSeleccionado) : [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg sticky top-0 z-10">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">📋 Registrar Atención</h2>
              <p className="text-blue-100 text-sm mt-1">Paciente: {pacienteNombre}</p>
            </div>
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
          {/* Selector de Modo: Plan vs Libre */}
          {cargandoPlanes ? (
            <div className="text-center py-4 mb-6 bg-gray-50 rounded-lg">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-sm text-gray-500 mt-2">Verificando planes activos...</p>
            </div>
          ) : planesActivos.length > 0 ? (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                📋 Tipo de Atención
              </label>
              
              <div className="grid grid-cols-2 gap-4">
                {/* Opción: Vincular a Plan */}
                <button
                  type="button"
                  onClick={() => {
                    setModoSeleccion('plan');
                    setServicioSeleccionado(null);
                  }}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    modoSeleccion === 'plan'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-blue-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">📋</span>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">
                        Parte del Plan de Tratamiento
                      </h3>
                      <p className="text-sm text-gray-600">
                        Vincular a un servicio del plan aceptado
                      </p>
                      <p className="text-xs text-blue-600 mt-2 font-medium">
                        {planesActivos.length} plan{planesActivos.length !== 1 ? 'es' : ''} activo{planesActivos.length !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                </button>

                {/* Opción: Episodio Libre */}
                <button
                  type="button"
                  onClick={() => {
                    setModoSeleccion('libre');
                    setPlanSeleccionado(null);
                    setItemSeleccionado(null);
                  }}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    modoSeleccion === 'libre'
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 hover:border-green-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">🆓</span>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">
                        Atención Independiente
                      </h3>
                      <p className="text-sm text-gray-600">
                        No vinculado a ningún plan
                      </p>
                      <p className="text-xs text-green-600 mt-2 font-medium">
                        Episodio libre
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <div className="mb-6 bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
              <p className="text-sm text-blue-800">
                ℹ️ Este paciente no tiene planes de tratamiento activos. El episodio se registrará como atención independiente.
              </p>
            </div>
          )}

          {/* Selector de Plan e Ítem */}
          {modoSeleccion === 'plan' && planesActivos.length > 0 && (
            <div className="mb-6 space-y-4">
              {/* Selector de Plan */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Plan <span className="text-red-500">*</span>
                </label>
                <select
                  value={planSeleccionado?.id || ''}
                  onChange={(e) => {
                    const plan = planesActivos.find(p => p.id === Number(e.target.value));
                    setPlanSeleccionado(plan || null);
                    setItemSeleccionado(null);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="">-- Seleccionar plan --</option>
                  {planesActivos.map(plan => (
                    <option key={plan.id} value={plan.id}>
                      {plan.titulo} - {plan.estado_display} - {plan.porcentaje_completado}% completado
                    </option>
                  ))}
                </select>
              </div>

              {/* Selector de Ítem */}
              {planSeleccionado && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Servicio del Plan <span className="text-red-500">*</span>
                  </label>
                  
                  {itemsDisponibles.length === 0 ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-800">
                        ⚠️ No hay servicios disponibles en este plan. Todos los ítems ya están completados.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {itemsDisponibles.map(item => (
                        <div
                          key={item.id}
                          onClick={() => setItemSeleccionado(item)}
                          className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                            itemSeleccionado?.id === item.id
                              ? 'border-blue-500 bg-blue-50 shadow-md'
                              : 'border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-bold text-gray-900">{item.servicio_nombre}</h4>
                                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                                  {item.estado_display}
                                </span>
                              </div>
                              
                              {item.insumo_nombre && (
                                <p className="text-sm text-gray-600 mb-2">
                                  🎨 Material: {item.insumo_nombre}
                                </p>
                              )}
                              
                              {item.notas && (
                                <p className="text-sm text-gray-600 italic">
                                  📝 {item.notas}
                                </p>
                              )}
                            </div>
                            
                            <div className="text-right ml-4">
                              <p className="text-xl font-bold text-green-600">
                                {item.precio_total_formateado}
                              </p>
                              {itemSeleccionado?.id === item.id && (
                                <span className="text-blue-600 text-2xl">✓</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Info sobre vinculación */}
              {itemSeleccionado && (
                <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded">
                  <p className="text-sm text-green-800">
                    ✅ Al guardar, este episodio se vinculará al servicio "{itemSeleccionado.servicio_nombre}" del plan.
                    El progreso del plan se actualizará automáticamente.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Selector de Servicio (Modo Libre) */}
          {modoSeleccion === 'libre' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Servicio Realizado <span className="text-red-500">*</span>
              </label>
              <select
                value={servicioSeleccionado || ''}
                onChange={(e) => setServicioSeleccionado(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">-- Seleccionar servicio --</option>
                {servicios.map(servicio => (
                  <option key={servicio.id} value={servicio.id}>
                    {servicio.nombre} - {servicio.categoria_nombre}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Campos del Episodio */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motivo de Consulta <span className="text-red-500">*</span>
              </label>
              <textarea
                value={motivo}
                onChange={(e) => setMotivo(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="¿Por qué vino el paciente?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diagnóstico
              </label>
              <textarea
                value={diagnostico}
                onChange={(e) => setDiagnostico(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Hallazgos y diagnóstico..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tratamiento Realizado
              </label>
              <textarea
                value={tratamiento}
                onChange={(e) => setTratamiento(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Procedimientos realizados..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observaciones Adicionales
              </label>
              <textarea
                value={observaciones}
                onChange={(e) => setObservaciones(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Notas adicionales..."
              />
            </div>
          </div>

          {/* Botones */}
          <div className="flex justify-between mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleCrearEpisodio}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                '💾 Guardar Episodio'
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

### PASO 3: Actualizar Servicio de Historial Clínico

**Archivo:** `src/services/historialService.ts` (ACTUALIZAR interfaz)

```typescript
export interface CrearEpisodioDTO {
  cita: number;
  motivo_consulta: string;
  diagnostico?: string;
  tratamiento_realizado?: string;
  observaciones?: string;
  // 🎯 NUEVO: Campo para vincular a plan
  item_plan_tratamiento?: number;
  // Campo para episodios libres
  servicio?: number;
}
```

---

## ✅ Checklist de Implementación

- [ ] Actualizar `src/services/planesService.ts` con `obtenerPlanesActivos()`
- [ ] Actualizar `src/services/historialService.ts` (agregar campo `item_plan_tratamiento` al DTO)
- [ ] Actualizar `src/components/agenda/ModalAgregarEpisodio.tsx` (versión completa con selector de planes)
- [ ] Probar flujo completo:
  - [ ] Paciente SIN planes → Modal normal (episodio libre)
  - [ ] Paciente CON planes → Mostrar selector
  - [ ] Vincular episodio a ítem del plan
  - [ ] Verificar actualización automática de progreso
  - [ ] Opción de episodio libre incluso con planes activos

---

## 🧪 Cómo Probar

### Flujo Completo Integrado

**1. Preparación:**
- Crear plan de tratamiento con 3 servicios
- Presentar → Aceptar plan
- Crear cita para el paciente

**2. Atender sin Plan:**
- Abrir agenda
- Click en cita de paciente SIN planes activos
- Modal muestra: "Este paciente no tiene planes activos"
- Seleccionar servicio normal
- Guardar → Episodio libre ✅

**3. Atender con Plan (Vinculado):**
- Abrir agenda
- Click en cita de paciente CON plan ACEPTADO
- Modal muestra: Selector "Plan" vs "Libre"
- Seleccionar modo "Plan"
- Elegir plan
- Elegir ítem del plan (servicio)
- Completar campos (motivo, diagnóstico, etc.)
- Guardar

**4. Verificar Automática:**
- ✅ Episodio creado y vinculado al ítem
- ✅ Ítem cambia: PENDIENTE → EN_PROGRESO
- ✅ Plan cambia: ACEPTADO → EN_PROGRESO (si es el primer episodio)
- ✅ Progreso del plan se actualiza (ej: 33% si completó 1 de 3)
- ✅ En detalle del plan, ver ítem marcado como EN_PROGRESO

**5. Completar Plan:**
- Crear episodios para los otros 2 servicios del plan
- Al completar el último:
  - ✅ Ítem: EN_PROGRESO → COMPLETADO
  - ✅ Plan: EN_PROGRESO → COMPLETADO
  - ✅ Progreso: 100%
  - ✅ `fecha_finalizacion` registrada automáticamente

**6. Atender con Plan (Libre):**
- Paciente tiene plan activo
- Seleccionar modo "Libre" (episodio independiente)
- Seleccionar servicio del catálogo
- Guardar → Episodio NO vinculado al plan ✅

---

## 🎯 Características Clave Implementadas

### 🔍 Detección Automática
- ✅ Consulta automática de planes activos al abrir modal
- ✅ Sugerencia inteligente: si hay planes, sugiere modo "Plan"
- ✅ Mensaje claro si no hay planes activos

### 📋 Selector Intuitivo
- ✅ Toggle visual: "Plan" vs "Libre"
- ✅ Dropdown para seleccionar plan
- ✅ Cards visuales para seleccionar ítem
- ✅ Información completa: nombre, precio, material, estado

### 🔗 Vinculación Inteligente
- ✅ Solo muestra ítems PENDIENTE o EN_PROGRESO
- ✅ Mensaje de confirmación antes de guardar
- ✅ Envía `item_plan_tratamiento` al backend

### 📊 Actualización Automática
- ✅ Backend signals actualizan estados
- ✅ Progreso se calcula automáticamente
- ✅ Transiciones de estado sin intervención manual

### 🆓 Flexibilidad
- ✅ Opción de episodio libre SIEMPRE disponible
- ✅ Paciente con plan puede recibir atención no planificada
- ✅ No obliga a vincular si no corresponde

---

## 📝 Casos de Uso

### Caso 1: Ortodoncia Planificada
```
Plan: "Ortodoncia Completa"
Ítems:
1. Consulta inicial → Vincular episodio
2. Instalación de brackets → Vincular episodio
3. Control mes 1 → Vincular episodio
4. Control mes 2 → Vincular episodio
...
```

### Caso 2: Emergencia No Planificada
```
Paciente tiene plan activo de ortodoncia
PERO viene por dolor de muela
→ Crear episodio LIBRE (no vinculado)
→ Servicio: "Atención de Urgencia"
```

### Caso 3: Plan Multi-Sesión
```
Plan: "Tratamiento de Conducto"
Ítems:
1. Endodoncia (3 sesiones necesarias)
   → Episodio 1: PENDIENTE → EN_PROGRESO
   → Episodio 2: EN_PROGRESO (continúa)
   → Episodio 3: EN_PROGRESO → COMPLETADO ✅
```

---

## 🔒 Validaciones Implementadas

### Frontend
- ✅ Motivo de consulta obligatorio
- ✅ Si modo "Plan": ítem obligatorio
- ✅ Si modo "Libre": servicio obligatorio
- ✅ No permitir guardar sin selecciones requeridas

### Backend (Ya implementado)
- ✅ Verificar que el ítem pertenezca a un plan del paciente
- ✅ Verificar que el ítem esté en estado PENDIENTE o EN_PROGRESO
- ✅ Actualizar automáticamente estados (signals)

---

## 📊 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────┐
│ Usuario: Click "Atender" en cita                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Modal: GET /api/tratamientos/planes/?paciente=X         │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ ¿Tiene       │   │ ¿Tiene       │
│ planes?      │   │ planes?      │
│ NO           │   │ SÍ           │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────────────────┐
│ Mostrar      │   │ Mostrar opciones:        │
│ mensaje      │   │ □ Plan (sugerido)        │
│ "Sin planes" │   │ □ Libre                  │
└──────┬───────┘   └──────┬───────────────────┘
       │                  │
       │         ┌────────┴────────┐
       │         │                 │
       │         ▼                 ▼
       │  ┌─────────────┐   ┌─────────────┐
       │  │ Modo PLAN   │   │ Modo LIBRE  │
       │  ├─────────────┤   ├─────────────┤
       │  │ Select plan │   │ Select srv  │
       │  │ Select ítem │   │             │
       │  └─────┬───────┘   └─────┬───────┘
       │        │                 │
       └────────┴─────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│ Completar campos: motivo, diagnóstico, tratamiento...   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ POST /api/historial-clinico/episodios/                  │
│ {                                                        │
│   item_plan_tratamiento: 15  ◄── Si modo plan           │
│   servicio: 8                ◄── Si modo libre          │
│   motivo_consulta: "..."                                │
│   ...                                                    │
│ }                                                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ BACKEND: Signal detecta item_plan_tratamiento           │
│ └─► Actualizar ítem: PENDIENTE → EN_PROGRESO            │
│ └─► Actualizar plan: ACEPTADO → EN_PROGRESO             │
│ └─► Calcular progreso: 33%                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend: Mostrar "✅ Episodio creado"                   │
│ Recargar agenda y planes                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Resultado Final

### Sistema Completo Funcionando:

1. ✅ **Crear planes** con servicios y precios dinámicos
2. ✅ **Gestionar planes** (presentar, aceptar, editar)
3. ✅ **Vincular episodios** desde la agenda
4. ✅ **Actualización automática** de progreso y estados
5. ✅ **Completar planes** automáticamente
6. ✅ **Flexibilidad** (episodios libres cuando sea necesario)

### Beneficios:

- 📊 **Trazabilidad completa**: saber qué episodios corresponden a qué servicio del plan
- 💰 **Presupuestos congelados**: precios no cambian después de aceptar
- 🎯 **Progreso visual**: ver avance del tratamiento en tiempo real
- 🔄 **Automatización**: estados y progreso se actualizan solos
- 📈 **Reportes precisos**: saber qué se facturó de cada plan

---

## 📝 Notas Finales

### ⚡ Backend Ya Implementado
Todo el sistema de signals y actualización automática YA ESTÁ FUNCIONANDO desde la Guía 2b (MODELO_HIBRIDO_IMPLEMENTADO.md). Esta guía solo conecta el frontend.

### 🎨 Personalización
Puedes agregar:
- Confirmación visual con animación al vincular
- Toast notifications en lugar de alerts
- Vista previa del ítem seleccionado
- Historial de episodios del ítem en el modal

### 🔮 Mejoras Futuras
- Sugerir automáticamente el siguiente ítem del plan
- Calcular tiempo restante estimado del plan
- Notificaciones push cuando un plan se completa
- Generar reporte PDF del plan completado

---

## ✅ Checklist Final del Sistema Completo

- [x] **Guía 15**: Crear planes de tratamiento
- [x] **Guía 16**: Agregar ítems con precio dinámico
- [x] **Guía 17**: Gestión completa del plan
- [x] **Guía 18**: Vincular episodios desde agenda ◄── ESTA GUÍA
- [ ] **Guía 14**: Lista de pacientes (opcional)

---

**🎉 SISTEMA DE TRATAMIENTOS COMPLETADO AL 100%! 🎉**

Ahora tienes un **sistema profesional de gestión de tratamientos dentales** con:
- Planes de tratamiento estructurados
- Precios dinámicos con materiales opcionales
- Vinculación agenda-plan-episodios
- Actualización automática de progreso
- Gestión completa del ciclo de vida

**¡Felicitaciones! El sistema está listo para producción.** 🚀
