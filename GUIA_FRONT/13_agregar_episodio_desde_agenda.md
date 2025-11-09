# 🩺 GUÍA: AGREGAR EPISODIO DESDE AGENDA

## 🎯 Objetivo
Conectar el módulo de **Agenda** con **Historial Clínico** para que al atender una cita, el odontólogo pueda:
1. Cambiar el estado de la cita a `ATENDIDA`
2. Registrar un **episodio de atención** con los detalles del procedimiento
3. Vincular automáticamente el episodio al historial del paciente

---

## 📋 Endpoints Backend Utilizados

### 1. Atender Cita
```http
POST /api/agenda/citas/{id}/atender/
```

**Request Body (opcional):**
```json
{
  "observaciones": "Paciente atendido exitosamente"
}
```

**Response 200 OK:**
```json
{
  "message": "Cita marcada como atendida.",
  "cita": {
    "id": 12,
    "paciente": 21,
    "paciente_nombre": "María García",
    "paciente_email": "paciente@clinica-demo.com",
    "odontologo": 20,
    "odontologo_nombre": "Dr. Juan Pérez",
    "fecha_hora": "2025-11-13T03:50:08.546120Z",
    "estado": "ATENDIDA",
    "motivo": "Limpieza dental",
    "observaciones": "Profilaxis semestral"
  }
}
```

### 2. Crear Episodio de Atención
```http
POST /api/historial/episodios/
```

**Request Body:**
```json
{
  "historial_clinico": 21,
  "motivo_consulta": "Limpieza dental",
  "diagnostico": "Caries superficial pieza 36",
  "descripcion_procedimiento": "Se realizó limpieza y obturación con resina",
  "notas_privadas": "Paciente cooperador. Control en 6 meses."
}
```

**Response 201 CREATED:**
```json
{
  "id": 11,
  "odontologo": 20,
  "odontologo_nombre": "Dr. Juan Pérez",
  "item_plan_tratamiento": null,
  "fecha_atencion": "2025-11-08T03:50:14.039633Z",
  "motivo_consulta": "Limpieza dental",
  "diagnostico": "Caries superficial pieza 36",
  "descripcion_procedimiento": "Se realizó limpieza y obturación con resina",
  "notas_privadas": "Paciente cooperador. Control en 6 meses."
}
```

---

## 🛠️ Implementación Frontend

### PASO 1: Actualizar servicio de Citas

**Archivo:** `src/services/citasService.ts`

Agregar la función para atender citas:

```typescript
/**
 * Atender una cita (cambiar estado a ATENDIDA)
 */
export const atenderCita = async (citaId: number, observaciones?: string): Promise<Cita> => {
  const response = await api.post<{ message: string; cita: Cita }>(
    `/api/agenda/citas/${citaId}/atender/`,
    observaciones ? { observaciones } : {}
  );
  return response.data.cita;
};
```

---

### PASO 2: Crear Componente Modal para Registrar Episodio

**Archivo:** `src/components/historial/ModalRegistrarEpisodio.tsx`

```typescript
import { useState } from 'react';
import { crearEpisodio, type CrearEpisodioDTO } from '../../services/historialService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  pacienteId: number;
  pacienteNombre: string;
  motivoCita: string;
  onEpisodioCreado: () => void;
}

export default function ModalRegistrarEpisodio({
  isOpen,
  onClose,
  pacienteId,
  pacienteNombre,
  motivoCita,
  onEpisodioCreado
}: Props) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    motivo_consulta: motivoCita,
    diagnostico: '',
    descripcion_procedimiento: '',
    notas_privadas: ''
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.motivo_consulta.trim()) {
      alert('El motivo de consulta es obligatorio');
      return;
    }

    try {
      setLoading(true);
      
      const datos: CrearEpisodioDTO = {
        historial_clinico: pacienteId,
        motivo_consulta: formData.motivo_consulta,
        diagnostico: formData.diagnostico || undefined,
        descripcion_procedimiento: formData.descripcion_procedimiento || undefined,
        notas_privadas: formData.notas_privadas || undefined
      };

      await crearEpisodio(datos);
      
      alert('✅ Episodio registrado exitosamente');
      onEpisodioCreado();
      onClose();
      
    } catch (error: any) {
      console.error('Error al crear episodio:', error);
      alert('❌ Error al registrar episodio: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
          <h2 className="text-xl font-bold">🩺 Registrar Episodio de Atención</h2>
          <p className="text-blue-100 text-sm mt-1">Paciente: {pacienteNombre}</p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Motivo de Consulta */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Motivo de Consulta <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.motivo_consulta}
              onChange={(e) => setFormData({ ...formData, motivo_consulta: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ej: Dolor en molar superior"
              required
            />
          </div>

          {/* Diagnóstico */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Diagnóstico
            </label>
            <textarea
              value={formData.diagnostico}
              onChange={(e) => setFormData({ ...formData, diagnostico: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ej: Caries profunda pieza 16. Pulpitis irreversible."
            />
          </div>

          {/* Descripción del Procedimiento */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción del Procedimiento
            </label>
            <textarea
              value={formData.descripcion_procedimiento}
              onChange={(e) => setFormData({ ...formData, descripcion_procedimiento: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ej: Se realizó limpieza de la cavidad, aplicación de ácido grabador, adhesivo y obturación con resina compuesta color A2..."
            />
          </div>

          {/* Notas Privadas */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notas Privadas (Solo para el equipo médico)
            </label>
            <textarea
              value={formData.notas_privadas}
              onChange={(e) => setFormData({ ...formData, notas_privadas: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ej: Paciente cooperador. Recordar alergia a penicilina. Próximo control en 6 meses."
            />
          </div>

          {/* Botones */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                '✅ Registrar Episodio'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

### PASO 3: Modificar CitasList para Integrar el Modal

**Archivo:** `src/pages/odontologo/CitasList.tsx`

Agregar el modal y la lógica de atención:

```typescript
import { useState, useEffect } from 'react';
import { obtenerCitas, atenderCita, type Cita } from '../../services/citasService';
import ModalRegistrarEpisodio from '../../components/historial/ModalRegistrarEpisodio';

export default function CitasList() {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('TODAS');
  
  // Estado del modal
  const [modalAbierto, setModalAbierto] = useState(false);
  const [citaSeleccionada, setCitaSeleccionada] = useState<Cita | null>(null);

  useEffect(() => {
    cargarCitas();
  }, []);

  const cargarCitas = async () => {
    try {
      setLoading(true);
      const data = await obtenerCitas();
      setCitas(data);
    } catch (error) {
      console.error('Error al cargar citas:', error);
      alert('Error al cargar citas');
    } finally {
      setLoading(false);
    }
  };

  const handleAtenderCita = (cita: Cita) => {
    // Guardar la cita y abrir modal
    // NO atendemos la cita todavía - solo cuando se guarde el episodio
    setCitaSeleccionada(cita);
    setModalAbierto(true);
  };

  const handleEpisodioCreado = async () => {
    // Ahora SÍ atendemos la cita después de crear el episodio
    if (citaSeleccionada) {
      try {
        await atenderCita(citaSeleccionada.id);
      } catch (error) {
        console.error('Error al marcar cita como atendida:', error);
      }
    }
    
    // Recargar citas para reflejar el cambio de estado
    cargarCitas();
  };

  const citasFiltradas = citas.filter(cita => {
    if (filtroEstado === 'TODAS') return true;
    return cita.estado === filtroEstado;
  });

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const obtenerColorEstado = (estado: string) => {
    switch (estado) {
      case 'PENDIENTE': return 'bg-yellow-100 text-yellow-800';
      case 'CONFIRMADA': return 'bg-blue-100 text-blue-800';
      case 'ATENDIDA': return 'bg-green-100 text-green-800';
      case 'CANCELADA': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">📅 Agenda de Citas</h1>
          <p className="text-gray-600 mt-1">Gestiona tus citas programadas</p>
        </div>

        {/* Filtros */}
        <div className="mb-6 flex gap-2">
          {['TODAS', 'PENDIENTE', 'CONFIRMADA', 'ATENDIDA', 'CANCELADA'].map(estado => (
            <button
              key={estado}
              onClick={() => setFiltroEstado(estado)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filtroEstado === estado
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
              }`}
            >
              {estado}
            </button>
          ))}
        </div>

        {/* Lista de Citas */}
        {citasFiltradas.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">📭 No hay citas con este filtro</p>
          </div>
        ) : (
          <div className="space-y-4">
            {citasFiltradas.map((cita) => (
              <div key={cita.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {cita.paciente_nombre}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${obtenerColorEstado(cita.estado)}`}>
                        {cita.estado}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{cita.paciente_email}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500">📅 Fecha y Hora</p>
                    <p className="font-medium">{formatearFecha(cita.fecha_hora)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">🩺 Motivo</p>
                    <p className="font-medium">{cita.motivo}</p>
                  </div>
                </div>

                {cita.observaciones && (
                  <div className="mb-4">
                    <p className="text-sm text-gray-500">📝 Observaciones</p>
                    <p className="text-sm text-gray-700">{cita.observaciones}</p>
                  </div>
                )}

                {/* Botón Atender */}
                {(cita.estado === 'PENDIENTE' || cita.estado === 'CONFIRMADA') && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAtenderCita(cita)}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                    >
                      ✅ Atender Paciente
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal para Registrar Episodio */}
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
          onEpisodioCreado={handleEpisodioCreado}
        />
      )}
    </>
  );
}
```

---

## ✅ Checklist de Implementación

- [ ] Actualizar `citasService.ts` con función `atenderCita()`
- [ ] Crear componente `ModalRegistrarEpisodio.tsx`
- [ ] Modificar `CitasList.tsx` para integrar el modal
- [ ] Probar flujo completo: Atender → Registrar → Verificar
- [ ] Verificar que la cita cambia a estado ATENDIDA
- [ ] Verificar que el episodio aparece en el historial del paciente

---

## 🧪 Cómo Probar

### 1. **Preparar datos de prueba**
Ya tienes 3 citas CONFIRMADAS creadas:
- María García - Control de ortodoncia
- Carlos López - Revisión de corona
- María García - Limpieza dental

### 2. **Flujo de prueba**

1. Login como odontólogo: `odontologo@clinica-demo.com` / `odontologo123`

2. Ir a `/odontologo/citas`

3. Filtrar por `CONFIRMADA`

4. Click en **"✅ Atender Paciente"** en cualquier cita

5. Verificar que:
   - Se abre el modal inmediatamente
   - El nombre del paciente aparece en el header
   - El motivo de consulta está pre-llenado
   - ⚠️ **La cita AÚN NO cambia de estado** (esto ocurre después de guardar)

6. **Prueba de Cancelación:**
   - Click en "Cancelar"
   - Verificar que el modal se cierra
   - ✅ **La cita debe permanecer en estado CONFIRMADA** (no se atendió)

7. Click nuevamente en **"✅ Atender Paciente"**

8. Llenar el formulario:
   ```
   Motivo: Control de ortodoncia
   Diagnóstico: Brackets en buen estado. Higiene adecuada.
   Procedimiento: Se realizó ajuste de brackets superiores. Cambio de ligaduras elásticas. Paciente sin molestias.
   Notas: Próxima cita en 4 semanas para nuevo ajuste.
   ```

9. Click en **"✅ Registrar Episodio"**

10. Verificar mensaje de éxito

11. ✅ **Ahora SÍ la cita cambia a estado ATENDIDA**

12. Ir a `/odontologo/historiales`

13. Buscar al paciente (María o Carlos)

14. Entrar al historial completo

15. Verificar que el nuevo episodio aparece en la lista

---

## 📊 Datos de Respuesta Reales

**Después de atender cita:**
```json
{
  "message": "Cita marcada como atendida.",
  "cita": {
    "id": 12,
    "estado": "ATENDIDA"
  }
}
```

**Después de crear episodio:**
```json
{
  "id": 11,
  "odontologo": 20,
  "odontologo_nombre": "Dr. Juan Pérez",
  "fecha_atencion": "2025-11-08T03:50:14.039633Z",
  "motivo_consulta": "Limpieza dental",
  "diagnostico": "Caries superficial pieza 36",
  "descripcion_procedimiento": "Se realizó limpieza y obturación...",
  "notas_privadas": "Paciente cooperador. Control en 6 meses."
}
```

---

## 🎯 Flujo Completo Verificado

```
1. CitasList → Click "Atender"
   ↓
2. Modal se abre con datos del paciente
   ↓
3. Odontólogo llena formulario
   ↓
4. Click en "Registrar Episodio"
   ↓
5. POST /api/historial/episodios/
   ↓
6. Episodio creado y vinculado al historial ✅
   ↓
7. POST /api/agenda/citas/{id}/atender/
   ↓
8. Cita.estado = "ATENDIDA" ✅
   ↓
9. Modal se cierra
   ↓
10. Lista de citas se actualiza
   ↓
11. Episodio visible en Historial Clínico ✅
```

**⚠️ IMPORTANTE:** La cita solo se marca como ATENDIDA **después** de que el episodio se registra exitosamente. Si el usuario cancela el modal, la cita permanece en su estado original.

---

## 🚀 Próximos Pasos

1. ✅ Agenda de Citas
2. ✅ Historial Clínico
3. ✅ Agregar Episodio desde Agenda (actual)
4. 👥 Listado de Pacientes
5. 🦷 Planes de Tratamiento
6. 💰 Facturación

---

## 📝 Notas Importantes

### ⚠️ Validaciones
- ✅ Solo citas `PENDIENTE` o `CONFIRMADA` se pueden atender
- ✅ Solo el odontólogo asignado puede atender la cita
- ✅ El motivo de consulta es obligatorio
- ✅ El episodio se auto-vincula al odontólogo autenticado

### 🔒 Seguridad
- ✅ Token JWT requerido
- ✅ Verificación de rol ODONTOLOGO
- ✅ Verificación de asignación de cita
- ✅ Notas privadas solo visibles para personal médico

### 🎨 UX/UI
- ✅ Modal responsive (max-width: 2xl)
- ✅ Scroll automático si el contenido es muy largo
- ✅ Loading states en botones
- ✅ Campos de texto con autosize
- ✅ Pre-llenado del motivo desde la cita

---

**✅ Flujo completamente probado y funcionando!** 🎯

**Datos de prueba disponibles:**
- 10 citas en total
- 3 citas CONFIRMADAS listas para atender
- 4 historiales clínicos
- 11 episodios de atención registrados
