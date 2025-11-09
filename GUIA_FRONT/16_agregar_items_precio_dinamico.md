# 🦷 GUÍA 16: AGREGAR ÍTEMS AL PLAN CON PRECIO DINÁMICO

## 🎯 Objetivo

Implementar el **sistema de precios dinámicos** para agregar servicios al plan de tratamiento:
1. Seleccionar servicios del catálogo
2. Ver materiales fijos incluidos automáticamente
3. Seleccionar materiales opcionales (si el servicio los requiere)
4. **Calcular precio total en tiempo real** (honorarios + materiales fijos + material seleccionado)
5. Agregar ítem al plan con precios "congelados" (snapshots)

Este es el **corazón del sistema de presupuestos** - el precio se calcula dinámicamente según los materiales elegidos.

---

## 📋 Estructura de Datos Clave

### Servicio con Materiales
```typescript
interface MaterialServicioFijo {
  id: number;
  insumo: {
    id: number;
    nombre: string;
    codigo: string;
    precio_venta: string;
  };
  cantidad: number;
  es_obligatorio: boolean;
  costo_adicional: string;  // precio_venta * cantidad
  costo_material_formateado: string;
}

interface MaterialServicioOpcional {
  id: number;
  categoria_insumo: {
    id: number;
    nombre: string;
  };
  cantidad: number;
  nombre_personalizado: string | null;
  es_obligatorio: boolean;
  opciones_disponibles: Insumo[];  // Lista de insumos para elegir
  rango_precios: {
    minimo: string;
    maximo: string;
    promedio: string;
  };
}

interface Servicio {
  id: number;
  codigo_servicio: string;
  nombre: string;
  descripcion: string;
  categoria_nombre: string;
  precio_base: string;              // Honorarios del profesional
  duracion_formateada: string;
  
  // ⚡ MATERIALES (Recetas)
  materiales_fijos: MaterialServicioFijo[];
  materiales_opcionales: MaterialServicioOpcional[];
  costo_materiales_fijos: string;   // Suma de todos los materiales fijos
  tiene_materiales_opcionales: boolean;
}
```

### Cálculo del Precio Total
```typescript
// El precio final de un ítem se calcula como:
precio_total = 
  precio_base +                          // Honorarios (Ej: $150)
  suma(materiales_fijos.costo_adicional) + // Materiales fijos (Ej: $30)
  insumo_seleccionado.precio_venta       // Material opcional elegido (Ej: $75)

// Ejemplo: Endodoncia
// - Honorarios: $150
// - Materiales fijos (jeringa, anestesia): $30
// - Material opcional (Resina 3M A2): $75
// TOTAL: $255
```

---

## 🛠️ Implementación Frontend

### PASO 1: Crear Servicio de Servicios y Materiales

**Archivo:** `src/services/serviciosService.ts`

```typescript
import api from './axios';

// ============================================================================
// TIPOS
// ============================================================================

export interface Insumo {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  precio_venta: string;
  stock_actual: number;
  activo: boolean;
}

export interface MaterialServicioFijo {
  id: number;
  insumo: Insumo;
  cantidad: number;
  es_obligatorio: boolean;
  costo_adicional: string;
  costo_material_formateado: string;
}

export interface MaterialServicioOpcional {
  id: number;
  categoria_insumo: {
    id: number;
    nombre: string;
  };
  cantidad: number;
  nombre_personalizado: string | null;
  es_obligatorio: boolean;
  opciones_disponibles: Insumo[];
  rango_precios: {
    minimo: string;
    maximo: string;
    promedio: string;
  };
}

export interface Servicio {
  id: number;
  codigo_servicio: string;
  nombre: string;
  descripcion: string;
  categoria: number;
  categoria_nombre: string;
  precio_base: string;
  tiempo_estimado: number;
  duracion_formateada: string;
  requiere_cita_previa: boolean;
  requiere_autorizacion: boolean;
  activo: boolean;
  materiales_fijos: MaterialServicioFijo[];
  materiales_opcionales: MaterialServicioOpcional[];
  costo_materiales_fijos: string;
  tiene_materiales_opcionales: boolean;
  creado: string;
  actualizado: string;
}

// ============================================================================
// API CALLS
// ============================================================================

/**
 * Listar servicios disponibles
 */
export const obtenerServicios = async (filtros?: {
  categoria?: number;
  activo?: boolean;
  buscar?: string;
}): Promise<Servicio[]> => {
  const params = new URLSearchParams();
  if (filtros?.categoria) params.append('categoria', filtros.categoria.toString());
  if (filtros?.activo !== undefined) params.append('activo', filtros.activo.toString());
  if (filtros?.buscar) params.append('search', filtros.buscar);
  
  const response = await api.get<Servicio[]>(
    `/api/tratamientos/servicios/${params.toString() ? '?' + params.toString() : ''}`
  );
  return response.data;
};

/**
 * Obtener detalle de un servicio
 */
export const obtenerServicio = async (id: number): Promise<Servicio> => {
  const response = await api.get<Servicio>(`/api/tratamientos/servicios/${id}/`);
  return response.data;
};

/**
 * Calcular precio total de un servicio con material seleccionado
 */
export const calcularPrecioServicio = (
  servicio: Servicio,
  insumoSeleccionadoId?: number
): number => {
  let total = parseFloat(servicio.precio_base);
  
  // Sumar materiales fijos
  total += parseFloat(servicio.costo_materiales_fijos);
  
  // Sumar material opcional si se seleccionó uno
  if (insumoSeleccionadoId && servicio.materiales_opcionales.length > 0) {
    servicio.materiales_opcionales.forEach(materialOpcional => {
      const insumo = materialOpcional.opciones_disponibles.find(
        opt => opt.id === insumoSeleccionadoId
      );
      if (insumo) {
        total += parseFloat(insumo.precio_venta) * materialOpcional.cantidad;
      }
    });
  }
  
  return total;
};
```

---

### PASO 2: Crear Componente Modal para Agregar Ítem

**Archivo:** `src/components/planes/ModalAgregarItem.tsx`

```typescript
import { useState, useEffect } from 'react';
import { obtenerServicios, calcularPrecioServicio, type Servicio } from '../../services/serviciosService';
import { crearItemPlan, type CrearItemPlanDTO } from '../../services/planesService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  planId: number;
  onItemAgregado: () => void;
}

export default function ModalAgregarItem({ isOpen, onClose, planId, onItemAgregado }: Props) {
  const [step, setStep] = useState<'seleccionar_servicio' | 'seleccionar_materiales' | 'confirmar'>('seleccionar_servicio');
  
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [servicioSeleccionado, setServicioSeleccionado] = useState<Servicio | null>(null);
  const [insumoSeleccionado, setInsumoSeleccionado] = useState<number | null>(null);
  const [notas, setNotas] = useState('');
  const [fechaEstimada, setFechaEstimada] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [buscandoServicios, setBuscandoServicios] = useState(true);
  const [busqueda, setBusqueda] = useState('');

  useEffect(() => {
    if (isOpen) {
      cargarServicios();
    }
  }, [isOpen]);

  const cargarServicios = async () => {
    try {
      setBuscandoServicios(true);
      const data = await obtenerServicios({ activo: true });
      setServicios(data);
    } catch (error) {
      console.error('Error al cargar servicios:', error);
      alert('Error al cargar catálogo de servicios');
    } finally {
      setBuscandoServicios(false);
    }
  };

  const handleSeleccionarServicio = (servicio: Servicio) => {
    setServicioSeleccionado(servicio);
    
    // Si el servicio tiene materiales opcionales, ir al paso 2
    if (servicio.tiene_materiales_opcionales) {
      setStep('seleccionar_materiales');
    } else {
      // Si no tiene materiales opcionales, ir directo a confirmar
      setStep('confirmar');
    }
  };

  const handleAgregarItem = async () => {
    if (!servicioSeleccionado) return;

    // Validar que se seleccionó material si es obligatorio
    const tieneOpcionalesObligatorios = servicioSeleccionado.materiales_opcionales.some(
      mat => mat.es_obligatorio
    );
    
    if (tieneOpcionalesObligatorios && !insumoSeleccionado) {
      alert('Debes seleccionar un material para este servicio');
      return;
    }

    try {
      setLoading(true);
      
      const datos: CrearItemPlanDTO = {
        plan: planId,
        servicio: servicioSeleccionado.id,
        insumo_seleccionado: insumoSeleccionado || undefined,
        notas: notas || undefined,
        fecha_estimada: fechaEstimada || undefined
      };

      await crearItemPlan(datos);
      
      alert('✅ Servicio agregado al plan exitosamente');
      
      // Reset y cerrar
      setServicioSeleccionado(null);
      setInsumoSeleccionado(null);
      setNotas('');
      setFechaEstimada('');
      setStep('seleccionar_servicio');
      
      onItemAgregado();
      onClose();
      
    } catch (error: any) {
      console.error('Error al agregar ítem:', error);
      alert('❌ Error al agregar servicio: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const precioCalculado = servicioSeleccionado
    ? calcularPrecioServicio(servicioSeleccionado, insumoSeleccionado || undefined)
    : 0;

  const serviciosFiltrados = servicios.filter(servicio =>
    servicio.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    servicio.codigo_servicio.toLowerCase().includes(busqueda.toLowerCase()) ||
    servicio.categoria_nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg sticky top-0 z-10">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">➕ Agregar Servicio al Plan</h2>
              <p className="text-blue-100 text-sm mt-1">
                {step === 'seleccionar_servicio' && 'Paso 1: Selecciona un servicio'}
                {step === 'seleccionar_materiales' && 'Paso 2: Selecciona materiales'}
                {step === 'confirmar' && 'Paso 3: Confirmar y agregar'}
              </p>
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
          {/* STEP 1: Seleccionar Servicio */}
          {step === 'seleccionar_servicio' && (
            <div>
              {/* Búsqueda */}
              <div className="mb-4">
                <input
                  type="text"
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  placeholder="🔍 Buscar por nombre, código o categoría..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              {/* Lista de Servicios */}
              {buscandoServicios ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="text-gray-500 mt-4">Cargando servicios...</p>
                </div>
              ) : serviciosFiltrados.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  📭 No se encontraron servicios
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto">
                  {serviciosFiltrados.map(servicio => (
                    <div
                      key={servicio.id}
                      onClick={() => handleSeleccionarServicio(servicio)}
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-gray-900">{servicio.nombre}</h3>
                        <span className="text-sm text-gray-500">{servicio.codigo_servicio}</span>
                      </div>
                      
                      <p className="text-xs text-gray-600 mb-3">{servicio.categoria_nombre}</p>
                      
                      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                        <div>
                          <span className="text-gray-500">Honorarios:</span>
                          <span className="font-semibold ml-1">${parseFloat(servicio.precio_base).toFixed(2)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Duración:</span>
                          <span className="font-semibold ml-1">{servicio.duracion_formateada}</span>
                        </div>
                      </div>

                      {/* Info de Materiales */}
                      <div className="flex gap-2 text-xs">
                        {servicio.materiales_fijos.length > 0 && (
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                            📦 {servicio.materiales_fijos.length} materiales incluidos
                          </span>
                        )}
                        {servicio.tiene_materiales_opcionales && (
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            🎨 Materiales opcionales
                          </span>
                        )}
                      </div>

                      {/* Precio Estimado */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Precio desde:</span>
                          <span className="text-lg font-bold text-green-600">
                            ${(parseFloat(servicio.precio_base) + parseFloat(servicio.costo_materiales_fijos)).toFixed(2)}
                          </span>
                        </div>
                        {servicio.tiene_materiales_opcionales && (
                          <p className="text-xs text-gray-500 mt-1">
                            * El precio final dependerá del material seleccionado
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STEP 2: Seleccionar Materiales */}
          {step === 'seleccionar_materiales' && servicioSeleccionado && (
            <div>
              {/* Info del Servicio */}
              <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
                <h3 className="font-bold text-lg text-gray-900 mb-2">
                  {servicioSeleccionado.nombre}
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Honorarios:</span>
                    <span className="font-semibold ml-2">${parseFloat(servicioSeleccionado.precio_base).toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Materiales fijos:</span>
                    <span className="font-semibold ml-2">${parseFloat(servicioSeleccionado.costo_materiales_fijos).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Materiales Fijos (Solo info) */}
              {servicioSeleccionado.materiales_fijos.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    📦 Materiales Incluidos
                    <span className="text-xs text-gray-500 font-normal">(Ya incluidos en el precio)</span>
                  </h4>
                  <div className="space-y-2">
                    {servicioSeleccionado.materiales_fijos.map(material => (
                      <div key={material.id} className="flex justify-between items-center bg-gray-50 p-3 rounded border border-gray-200">
                        <div>
                          <p className="font-medium text-gray-900">{material.insumo.nombre}</p>
                          <p className="text-xs text-gray-600">Cantidad: {material.cantidad}</p>
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {material.costo_material_formateado}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Materiales Opcionales (Selector) */}
              {servicioSeleccionado.materiales_opcionales.map(materialOpcional => (
                <div key={materialOpcional.id} className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    🎨 {materialOpcional.nombre_personalizado || `Seleccionar ${materialOpcional.categoria_insumo.nombre}`}
                    {materialOpcional.es_obligatorio && (
                      <span className="text-red-500 text-sm">*</span>
                    )}
                  </h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {materialOpcional.opciones_disponibles.map(insumo => (
                      <div
                        key={insumo.id}
                        onClick={() => setInsumoSeleccionado(insumo.id)}
                        className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                          insumoSeleccionado === insumo.id
                            ? 'border-blue-500 bg-blue-50 shadow-md'
                            : 'border-gray-200 hover:border-blue-300'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-900">{insumo.nombre}</h5>
                            <p className="text-xs text-gray-600">{insumo.codigo}</p>
                          </div>
                          {insumoSeleccionado === insumo.id && (
                            <span className="text-blue-600 text-xl">✓</span>
                          )}
                        </div>
                        
                        <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-200">
                          <span className="text-sm text-gray-600">Cantidad: {materialOpcional.cantidad}</span>
                          <span className="text-lg font-bold text-green-600">
                            ${(parseFloat(insumo.precio_venta) * materialOpcional.cantidad).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              {/* Botones */}
              <div className="flex justify-between mt-6">
                <button
                  onClick={() => {
                    setStep('seleccionar_servicio');
                    setServicioSeleccionado(null);
                    setInsumoSeleccionado(null);
                  }}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  ← Volver
                </button>
                <button
                  onClick={() => setStep('confirmar')}
                  disabled={servicioSeleccionado.materiales_opcionales.some(m => m.es_obligatorio) && !insumoSeleccionado}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continuar →
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Confirmar */}
          {step === 'confirmar' && servicioSeleccionado && (
            <div>
              {/* Resumen */}
              <div className="bg-gray-50 rounded-lg p-6 mb-6 border border-gray-200">
                <h3 className="font-bold text-xl text-gray-900 mb-4">📋 Resumen del Servicio</h3>
                
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between items-center pb-2 border-b border-gray-300">
                    <span className="text-gray-700">Servicio:</span>
                    <span className="font-semibold text-gray-900">{servicioSeleccionado.nombre}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Honorarios profesionales:</span>
                    <span className="font-mono">${parseFloat(servicioSeleccionado.precio_base).toFixed(2)}</span>
                  </div>
                  
                  {parseFloat(servicioSeleccionado.costo_materiales_fijos) > 0 && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Materiales incluidos:</span>
                      <span className="font-mono">${parseFloat(servicioSeleccionado.costo_materiales_fijos).toFixed(2)}</span>
                    </div>
                  )}
                  
                  {insumoSeleccionado && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Material seleccionado:</span>
                      <span className="font-mono">
                        ${(() => {
                          const material = servicioSeleccionado.materiales_opcionales[0];
                          const insumo = material.opciones_disponibles.find(i => i.id === insumoSeleccionado);
                          return insumo ? (parseFloat(insumo.precio_venta) * material.cantidad).toFixed(2) : '0.00';
                        })()}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between items-center pt-3 border-t-2 border-gray-400">
                    <span className="text-lg font-bold text-gray-900">TOTAL:</span>
                    <span className="text-2xl font-bold text-green-600">
                      ${precioCalculado.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="bg-blue-50 p-3 rounded border border-blue-200 mt-4">
                  <p className="text-xs text-blue-800">
                    ℹ️ Este precio se "congelará" al agregar el ítem. Cambios futuros en el catálogo no afectarán este presupuesto.
                  </p>
                </div>
              </div>

              {/* Notas y Fecha Estimada */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notas (Opcional)
                  </label>
                  <textarea
                    value={notas}
                    onChange={(e) => setNotas(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="Notas adicionales sobre este procedimiento..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fecha Estimada (Opcional)
                  </label>
                  <input
                    type="date"
                    value={fechaEstimada}
                    onChange={(e) => setFechaEstimada(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Botones */}
              <div className="flex justify-between">
                <button
                  onClick={() => {
                    if (servicioSeleccionado.tiene_materiales_opcionales) {
                      setStep('seleccionar_materiales');
                    } else {
                      setStep('seleccionar_servicio');
                      setServicioSeleccionado(null);
                    }
                  }}
                  disabled={loading}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  ← Volver
                </button>
                <button
                  onClick={handleAgregarItem}
                  disabled={loading}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Agregando...
                    </>
                  ) : (
                    '✅ Agregar al Plan'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### PASO 3: Integrar Modal en Vista de Detalle del Plan

**Archivo:** `src/pages/odontologo/PlanDetalle.tsx` (Fragmento)

```typescript
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { obtenerPlan, type PlanDeTratamiento } from '../../services/planesService';
import ModalAgregarItem from '../../components/planes/ModalAgregarItem';

export default function PlanDetalle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [plan, setPlan] = useState<PlanDeTratamiento | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);

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
            <h1 className="text-3xl font-bold text-gray-900">{plan.titulo}</h1>
            <p className="text-gray-600 mt-1">👤 {plan.paciente_info.nombre_completo}</p>
          </div>
          {plan.puede_ser_editado && (
            <button
              onClick={() => setModalAbierto(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              ➕ Agregar Servicio
            </button>
          )}
        </div>
      </div>

      {/* Precio Total */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6 mb-6 shadow-lg">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-green-100 text-sm">Precio Total del Plan</p>
            <p className="text-4xl font-bold">${parseFloat(plan.precio_total_plan).toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-green-100 text-sm">Progreso</p>
            <p className="text-3xl font-bold">{plan.porcentaje_completado}%</p>
          </div>
        </div>
      </div>

      {/* Lista de Ítems */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Servicios del Plan ({plan.cantidad_items})
        </h2>
        
        {plan.items.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>📭 Aún no hay servicios en este plan</p>
            <button
              onClick={() => setModalAbierto(true)}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Agregar primer servicio
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {plan.items.map((item, index) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-bold text-gray-500">#{index + 1}</span>
                      <h3 className="font-bold text-gray-900">{item.servicio_nombre}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.estado === 'COMPLETADO' ? 'bg-green-100 text-green-800' :
                        item.estado === 'EN_PROGRESO' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {item.estado_display}
                      </span>
                    </div>
                    
                    {item.insumo_nombre && (
                      <p className="text-sm text-gray-600 mb-2">
                        🎨 Material: {item.insumo_nombre}
                      </p>
                    )}
                    
                    {item.notas && (
                      <p className="text-sm text-gray-600 italic">📝 {item.notas}</p>
                    )}
                  </div>
                  
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">
                      {item.precio_total_formateado}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Honorarios: ${parseFloat(item.precio_servicio_snapshot).toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      <ModalAgregarItem
        isOpen={modalAbierto}
        onClose={() => setModalAbierto(false)}
        planId={plan.id}
        onItemAgregado={cargarPlan}
      />
    </div>
  );
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear `src/services/serviciosService.ts` con tipos y funciones
- [ ] Crear `src/components/planes/ModalAgregarItem.tsx` (modal completo)
- [ ] Crear/Actualizar `src/pages/odontologo/PlanDetalle.tsx`
- [ ] Agregar ruta en el router:
  ```tsx
  <Route path="/odontologo/planes/:id" element={<PlanDetalle />} />
  ```
- [ ] Probar flujo completo de agregar ítems

---

## 🧪 Cómo Probar

1. Crear un plan de tratamiento (o usar uno existente)

2. En el detalle del plan, click en "➕ Agregar Servicio"

3. **Paso 1:** Seleccionar servicio
   - Buscar "Endodoncia"
   - Ver precio estimado: $150 (honorarios) + $30 (materiales fijos) = $180

4. **Paso 2:** Seleccionar materiales (si aplica)
   - Elegir "Resina 3M A2" - $75
   - Ver precio actualizado en tiempo real

5. **Paso 3:** Confirmar
   - Ver resumen con desglose:
     * Honorarios: $150
     * Materiales fijos: $30
     * Material seleccionado: $75
     * **TOTAL: $255**

6. Click en "✅ Agregar al Plan"

7. Verificar que:
   - El ítem aparece en la lista
   - El precio total del plan se actualizó automáticamente
   - Los precios están "congelados" (snapshots)

---

## 🎯 Características Clave Implementadas

### ✨ Precio Dinámico en Tiempo Real
- ✅ Calcula automáticamente según materiales seleccionados
- ✅ Muestra desglose completo (honorarios + materiales fijos + opcionales)
- ✅ Actualización en tiempo real al cambiar selección

### 🔒 Snapshots de Precios
- ✅ Precios se "congelan" al agregar al plan
- ✅ Cambios futuros en el catálogo NO afectan planes existentes
- ✅ Garantiza presupuestos inmutables

### 🎨 Materiales Opcionales
- ✅ Permite elegir entre diferentes materiales
- ✅ Cada material tiene su propio precio
- ✅ Validación de selección obligatoria

### 📦 Materiales Fijos
- ✅ Se incluyen automáticamente en el precio
- ✅ No requieren selección manual
- ✅ Transparencia en costos

---

## 📝 Notas Importantes

### ⚠️ Validaciones
- ✅ Servicio obligatorio
- ✅ Material opcional obligatorio si el servicio lo requiere
- ✅ Prevención de duplicados

### 🔒 Seguridad
- ✅ Solo planes editables permiten agregar ítems
- ✅ Precios se calculan en backend (no confiar en frontend)
- ✅ Snapshots inmutables

### 💰 Lógica de Precios
```
Precio Total = 
  precio_servicio_snapshot +           // Honorarios
  precio_materiales_fijos_snapshot +   // Suma de materiales fijos
  precio_insumo_seleccionado_snapshot  // Material opcional elegido

Ejemplo Real:
  $150 (Endodoncia) + 
  $30 (Jeringa + Anestesia) + 
  $75 (Resina 3M A2) 
  = $255 TOTAL
```

---

## 🚀 Próximos Pasos

1. **Guía 17:** Vista completa de gestión del plan (editar, presentar, aceptar, completar)
2. **Guía 18:** Vincular episodios desde la agenda al plan

---

**✅ Sistema de Precios Dinámicos Implementado Completamente!** 🎉
