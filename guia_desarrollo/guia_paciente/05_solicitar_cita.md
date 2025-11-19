# 05 - Solicitar Nueva Cita

## 🎯 Objetivo
Implementar el formulario para que el paciente pueda solicitar una nueva cita, seleccionando fecha, hora, odontólogo (opcional) y motivo de consulta.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Ver citas funcional (Guía 04)
- ✅ Servicio de citas ya existe (citasService.ts)

---

## 🔌 Endpoints del Backend

### **POST** `/tenant/api/agenda/citas/`
Crea una nueva solicitud de cita

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "paciente": 3,
  "odontologo": 5,
  "fecha_hora": "2025-11-20T10:00:00-05:00",
  "motivo_tipo": "CONSULTA",
  "motivo": "Dolor en muela del juicio",
  "observaciones": "Prefiero atención en la mañana"
}
```

**Campos:**
- `paciente` (int, requerido): ID del perfil de paciente (se obtiene automáticamente del usuario autenticado)
- `odontologo` (int, opcional): ID del perfil del odontólogo. Si no se especifica, la clínica asignará uno
- `fecha_hora` (datetime, requerido): Fecha y hora deseada en formato ISO 8601
- `motivo_tipo` (string, requerido): Tipo de consulta (CONSULTA, LIMPIEZA, EXTRACCION, ORTODONCIA, ENDODONCIA, etc.)
- `motivo` (string, requerido): Descripción del motivo de la cita
- `observaciones` (string, opcional): Observaciones o preferencias adicionales

**Response 201:**
```json
{
  "id": 50,
  "paciente": 3,
  "paciente_nombre": "María García",
  "odontologo": 5,
  "odontologo_nombre": "Dr. Carlos López",
  "odontologo_especialidad": "Ortodoncia",
  "fecha_hora": "2025-11-20T10:00:00-05:00",
  "motivo_tipo": "CONSULTA",
  "motivo_tipo_display": "Consulta General",
  "motivo": "Dolor en muela del juicio",
  "observaciones": "Prefiero atención en la mañana",
  "estado": "PENDIENTE",
  "precio": "0.00",
  "creado": "2025-11-15T16:30:00-05:00"
}
```

### **GET** `/tenant/api/usuarios/odontologos/`
Lista odontólogos disponibles para seleccionar

**Response 200:**
```json
[
  {
    "id": 5,
    "nombre": "Carlos",
    "apellido": "López",
    "full_name": "Dr. Carlos López",
    "email": "carlos@clinica.com",
    "especialidad": "Ortodoncia"
  }
]
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── SolicitarCita.tsx       ← Nuevo
├── services/
│   ├── citasService.ts             ← Extender (agregar crear)
│   └── usuariosService.ts          ← Extender (agregar listar odontólogos)
└── types/
    └── citas.types.ts              ← Extender
```

---

## 💻 Código Paso a Paso

### **Paso 1: Extender tipos de Citas**

**Archivo:** `src/types/citas.types.ts` (agregar al final)

```typescript
// ... tipos existentes ...

export type MotivoTipo = 
  | 'CONSULTA'
  | 'LIMPIEZA'
  | 'EXTRACCION'
  | 'ORTODONCIA'
  | 'ENDODONCIA'
  | 'IMPLANTE'
  | 'ESTETICA'
  | 'URGENCIA'
  | 'CONTROL'
  | 'OTRO';

export interface CrearCitaData {
  paciente: number; // ID del perfil paciente
  odontologo?: number; // Opcional
  fecha_hora: string; // ISO 8601
  motivo_tipo: MotivoTipo;
  motivo: string;
  observaciones?: string;
}

export interface Odontologo {
  id: number;
  nombre: string;
  apellido: string;
  full_name: string;
  email: string;
  especialidad?: string;
}
```

---

### **Paso 2: Extender servicio de Citas**

**Archivo:** `src/services/citasService.ts` (agregar al objeto existente)

```typescript
// ... métodos existentes ...

/**
 * Crear nueva solicitud de cita
 */
async crearCita(data: CrearCitaData): Promise<Cita> {
  console.group('➕ [citasService] crearCita');
  console.log('Datos:', data);
  
  try {
    const response = await apiClient.post<Cita>(
      '/tenant/api/agenda/citas/',
      data
    );
    
    console.log('✅ Cita creada exitosamente');
    console.log('ID:', response.data.id);
    console.log('Estado:', response.data.estado);
    console.groupEnd();
    
    return response.data;
    
  } catch (error: any) {
    console.error('❌ Error creando cita:', error);
    console.error('Response:', error.response?.data);
    console.groupEnd();
    throw error;
  }
}
```

---

### **Paso 3: Extender servicio de Usuarios**

**Archivo:** `src/services/usuariosService.ts` (agregar al objeto existente)

```typescript
import type { Odontologo } from '../types/citas.types';

// ... métodos existentes ...

/**
 * Obtener lista de odontólogos disponibles
 */
async getOdontologos(): Promise<Odontologo[]> {
  console.group('👨‍⚕️ [usuariosService] getOdontologos');
  
  try {
    const response = await apiClient.get<Odontologo[]>(
      '/tenant/api/usuarios/odontologos/'
    );
    
    console.log('✅ Odontólogos obtenidos:', response.data.length);
    console.groupEnd();
    
    return response.data;
    
  } catch (error: any) {
    console.error('❌ Error obteniendo odontólogos:', error);
    console.groupEnd();
    throw error;
  }
}
```

---

### **Paso 4: Página SolicitarCita**

**Archivo:** `src/pages/paciente/SolicitarCita.tsx`

```typescript
import { useEffect, useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import citasService from '../../services/citasService';
import usuariosService from '../../services/usuariosService';
import type { CrearCitaData, MotivoTipo, Odontologo } from '../../types/citas.types';

const SolicitarCita = () => {
  const navigate = useNavigate();
  
  // Estados del formulario
  const [formData, setFormData] = useState<CrearCitaData>({
    paciente: 0, // Se obtendrá del usuario actual
    fecha_hora: '',
    motivo_tipo: 'CONSULTA',
    motivo: '',
    observaciones: ''
  });
  
  // Estados de UI
  const [odontologos, setOdontologos] = useState<Odontologo[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingOdontologos, setLoadingOdontologos] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoadingOdontologos(true);
      
      // Cargar usuario actual para obtener ID de perfil paciente
      const usuario = await usuariosService.getMiPerfil();
      
      // Asumiendo que el perfil_paciente tiene un ID
      // Si no, necesitarás endpoint específico o ajustar según tu estructura
      setFormData(prev => ({
        ...prev,
        paciente: usuario.id // O usuario.perfil_paciente.id según tu backend
      }));
      
      // Cargar odontólogos disponibles
      const odontologosData = await usuariosService.getOdontologos();
      setOdontologos(odontologosData);
      
    } catch (err: any) {
      console.error('Error cargando datos:', err);
      setError('No se pudieron cargar los datos necesarios');
      
    } finally {
      setLoadingOdontologos(false);
    }
  };

  const motivosTipo: Array<{ valor: MotivoTipo; texto: string }> = [
    { valor: 'CONSULTA', texto: 'Consulta General' },
    { valor: 'LIMPIEZA', texto: 'Limpieza Dental' },
    { valor: 'EXTRACCION', texto: 'Extracción' },
    { valor: 'ORTODONCIA', texto: 'Ortodoncia' },
    { valor: 'ENDODONCIA', texto: 'Endodoncia (Conducto)' },
    { valor: 'IMPLANTE', texto: 'Implante Dental' },
    { valor: 'ESTETICA', texto: 'Estética Dental' },
    { valor: 'URGENCIA', texto: 'Urgencia' },
    { valor: 'CONTROL', texto: 'Control / Seguimiento' },
    { valor: 'OTRO', texto: 'Otro' }
  ];

  const handleChange = (field: keyof CrearCitaData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Limpiar error del campo
    if (errores[field]) {
      setErrores(prev => {
        const newErrores = { ...prev };
        delete newErrores[field];
        return newErrores;
      });
    }
  };

  const validarFormulario = (): boolean => {
    const nuevosErrores: Record<string, string> = {};

    if (!formData.fecha_hora) {
      nuevosErrores.fecha_hora = 'La fecha y hora son requeridas';
    } else {
      // Validar que la fecha sea futura
      const fechaSeleccionada = new Date(formData.fecha_hora);
      const ahora = new Date();
      
      if (fechaSeleccionada <= ahora) {
        nuevosErrores.fecha_hora = 'La fecha debe ser futura';
      }
    }

    if (!formData.motivo.trim()) {
      nuevosErrores.motivo = 'El motivo es requerido';
    } else if (formData.motivo.length < 10) {
      nuevosErrores.motivo = 'El motivo debe tener al menos 10 caracteres';
    }

    setErrores(nuevosErrores);
    return Object.keys(nuevosErrores).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    console.group('📝 Solicitar Cita');
    console.log('Datos del formulario:', formData);

    if (!validarFormulario()) {
      console.warn('⚠️ Formulario con errores');
      console.groupEnd();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const citaCreada = await citasService.crearCita(formData);
      
      console.log('✅ Cita solicitada exitosamente');
      console.log('ID de cita:', citaCreada.id);
      console.groupEnd();

      // Mostrar mensaje de éxito y redirigir
      alert(`✅ Cita solicitada exitosamente!\n\nFecha: ${new Date(citaCreada.fecha_hora).toLocaleString('es-ES')}\nEstado: ${citaCreada.estado}\n\nTe notificaremos cuando sea confirmada.`);
      
      navigate('/paciente/citas');

    } catch (err: any) {
      console.error('❌ Error al solicitar cita');
      console.groupEnd();
      
      const errorData = err.response?.data;
      let errorMsg = 'Error al solicitar la cita. Intenta nuevamente.';
      
      if (errorData) {
        // Manejar errores específicos del backend
        if (typeof errorData === 'object') {
          errorMsg = Object.values(errorData).flat().join(', ');
        } else if (typeof errorData === 'string') {
          errorMsg = errorData;
        }
      }
      
      setError(errorMsg);

    } finally {
      setLoading(false);
    }
  };

  const getMinDateTime = (): string => {
    const ahora = new Date();
    ahora.setHours(ahora.getHours() + 1); // Al menos 1 hora en el futuro
    return ahora.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:mm
  };

  if (loadingOdontologos) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          textAlign: 'center'
        }}>
          <p style={{ fontSize: '16px', color: '#6b7280' }}>
            ⏳ Cargando formulario...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f3f4f6'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <button
            onClick={() => navigate('/paciente/citas')}
            style={{
              padding: '8px 12px',
              backgroundColor: '#f3f4f6',
              color: '#374151',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
          >
            ← Volver
          </button>

          <div>
            <h1 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              📅 Solicitar Nueva Cita
            </h1>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: '4px 0 0 0'
            }}>
              Completa el formulario para solicitar una cita
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Error Global */}
        {error && (
          <div style={{
            padding: '16px',
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#991b1b',
              margin: 0
            }}>
              ⚠️ {error}
            </p>
          </div>
        )}

        {/* Formulario */}
        <form onSubmit={handleSubmit}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            padding: '24px'
          }}>
            {/* Fecha y Hora */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                📅 Fecha y Hora <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="datetime-local"
                value={formData.fecha_hora}
                onChange={(e) => handleChange('fecha_hora', e.target.value)}
                min={getMinDateTime()}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: `1px solid ${errores.fecha_hora ? '#ef4444' : '#d1d5db'}`,
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              {errores.fecha_hora && (
                <p style={{
                  fontSize: '12px',
                  color: '#ef4444',
                  margin: '4px 0 0 0'
                }}>
                  {errores.fecha_hora}
                </p>
              )}
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                Selecciona la fecha y hora deseada para tu cita
              </p>
            </div>

            {/* Tipo de Motivo */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                🦷 Tipo de Consulta <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <select
                value={formData.motivo_tipo}
                onChange={(e) => handleChange('motivo_tipo', e.target.value as MotivoTipo)}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                {motivosTipo.map((tipo) => (
                  <option key={tipo.valor} value={tipo.valor}>
                    {tipo.texto}
                  </option>
                ))}
              </select>
            </div>

            {/* Motivo Detallado */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                📝 Motivo de la Cita <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <textarea
                value={formData.motivo}
                onChange={(e) => handleChange('motivo', e.target.value)}
                disabled={loading}
                placeholder="Describe brevemente el motivo de tu consulta..."
                rows={4}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: `1px solid ${errores.motivo ? '#ef4444' : '#d1d5db'}`,
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: 'inherit'
                }}
              />
              {errores.motivo && (
                <p style={{
                  fontSize: '12px',
                  color: '#ef4444',
                  margin: '4px 0 0 0'
                }}>
                  {errores.motivo}
                </p>
              )}
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                Mínimo 10 caracteres ({formData.motivo.length}/10)
              </p>
            </div>

            {/* Odontólogo (Opcional) */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                👨‍⚕️ Odontólogo (Opcional)
              </label>
              <select
                value={formData.odontologo || ''}
                onChange={(e) => handleChange('odontologo', e.target.value ? Number(e.target.value) : undefined)}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                <option value="">Sin preferencia (Asignación automática)</option>
                {odontologos.map((odontologo) => (
                  <option key={odontologo.id} value={odontologo.id}>
                    {odontologo.full_name}
                    {odontologo.especialidad && ` - ${odontologo.especialidad}`}
                  </option>
                ))}
              </select>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                Si no seleccionas, se asignará automáticamente
              </p>
            </div>

            {/* Observaciones */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                💬 Observaciones o Preferencias
              </label>
              <textarea
                value={formData.observaciones || ''}
                onChange={(e) => handleChange('observaciones', e.target.value)}
                disabled={loading}
                placeholder="Agrega cualquier información adicional que consideres importante..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: 'inherit'
                }}
              />
            </div>

            {/* Nota Informativa */}
            <div style={{
              padding: '16px',
              backgroundColor: '#eff6ff',
              border: '1px solid #bfdbfe',
              borderRadius: '8px',
              marginBottom: '24px'
            }}>
              <p style={{
                fontSize: '14px',
                color: '#1e40af',
                margin: 0
              }}>
                ℹ️ <strong>Nota:</strong> Tu cita quedará en estado PENDIENTE hasta que la clínica la confirme. Recibirás una notificación cuando sea confirmada.
              </p>
            </div>

            {/* Botones */}
            <div style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-end'
            }}>
              <button
                type="button"
                onClick={() => navigate('/paciente/citas')}
                disabled={loading}
                style={{
                  padding: '12px 24px',
                  backgroundColor: 'white',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!loading) e.currentTarget.style.backgroundColor = '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                }}
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '12px 24px',
                  backgroundColor: loading ? '#9ca3af' : '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!loading) e.currentTarget.style.backgroundColor = '#059669';
                }}
                onMouseLeave={(e) => {
                  if (!loading) e.currentTarget.style.backgroundColor = '#10b981';
                }}
              >
                {loading ? '⏳ Solicitando...' : '✓ Solicitar Cita'}
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};

export default SolicitarCita;
```

---

### **Paso 5: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import SolicitarCitaPaciente from './pages/paciente/SolicitarCita'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        <Route path="/paciente/perfil" element={<PerfilPaciente />} />
        <Route path="/paciente/citas" element={<CitasPaciente />} />
        <Route path="/paciente/citas/solicitar" element={<SolicitarCitaPaciente />} /> {/* ← NUEVO */}
        
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🧪 Pruebas

### **Caso 1: Solicitar Cita Completa**
1. Login con `paciente1@test.com` / `paciente123`
2. Ir a "Mis Citas" → Click "Solicitar Cita"
3. Llenar formulario:
   - Fecha: Mañana a las 10:00 AM
   - Tipo: Consulta General
   - Motivo: "Dolor en muela del juicio izquierda"
   - Odontólogo: Seleccionar uno
   - Observaciones: "Prefiero atención en la mañana"
4. Click "Solicitar Cita"
5. **Esperado**:
   - Alert de confirmación
   - Redirección a lista de citas
   - Nueva cita visible con estado PENDIENTE

### **Caso 2: Validación de Campos**
1. Dejar fecha vacía → Click "Solicitar"
2. **Esperado**: Error "La fecha y hora son requeridas"
3. Llenar fecha pasada
4. **Esperado**: Error "La fecha debe ser futura"
5. Motivo con menos de 10 caracteres
6. **Esperado**: Error "El motivo debe tener al menos 10 caracteres"

### **Caso 3: Sin Odontólogo Seleccionado**
1. Llenar formulario sin seleccionar odontólogo
2. Click "Solicitar Cita"
3. **Esperado**: Cita creada exitosamente (se asignará automáticamente)

### **Caso 4: Cancelar Solicitud**
1. Empezar a llenar formulario
2. Click "Cancelar"
3. **Esperado**: Volver a lista de citas sin crear cita

---

## ✅ Checklist de Verificación

- [ ] Formulario renderiza correctamente
- [ ] Campos de fecha/hora funcionan
- [ ] Select de tipo de consulta funciona
- [ ] Textarea de motivo funciona
- [ ] Select de odontólogos carga y funciona
- [ ] Validación de fecha futura funciona
- [ ] Validación de motivo mínimo funciona
- [ ] Botón "Solicitar" crea la cita
- [ ] Alert de confirmación se muestra
- [ ] Redirección a lista de citas funciona
- [ ] Nueva cita aparece en la lista
- [ ] Estados de loading funcionan
- [ ] Botón "Cancelar" funciona
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: ID de paciente incorrecto**
**Síntoma**: Error 400 "paciente inválido"
**Causa**: El ID enviado no corresponde al perfil_paciente
**Solución**: Verificar estructura de Usuario y PerfilPaciente en backend

### **Error 2: Formato de fecha incorrecto**
**Síntoma**: Error 400 en fecha_hora
**Causa**: Formato datetime-local no es ISO 8601 completo
**Solución**: Agregar timezone: `${fecha}:00-05:00`

### **Error 3: Odontólogos no cargan**
**Síntoma**: Select vacío
**Causa**: Endpoint `/tenant/api/usuarios/odontologos/` no existe
**Solución**: Verificar que el backend tenga este endpoint o ajustar URL

### **Error 4: Cita no aparece en lista**
**Síntoma**: Cita creada pero no se ve
**Causa**: Lista no se refresca automáticamente
**Solución**: La redirección hace que se recargue la lista

---

## 🔄 Siguiente Paso

✅ Solicitar cita completado → Continuar con **`06_cancelar_cita.md`** (Cancelar citas)
