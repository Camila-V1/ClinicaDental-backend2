# 02 - Dashboard del Paciente

## 🎯 Objetivo
Crear el dashboard principal del paciente mostrando próximas citas, resumen del historial clínico y accesos rápidos a funcionalidades principales.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Tokens guardados en localStorage
- ✅ Usuario autenticado como PACIENTE

---

## 🔌 Endpoints del Backend

### **GET** `/tenant/api/agenda/citas/mis-citas/`
Obtiene las citas del paciente autenticado

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit`: Número de resultados (default: 10)
- `estado`: Filtrar por estado (PENDIENTE, CONFIRMADA, etc.)

**Response 200:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 45,
      "fecha_hora": "2025-11-18T10:00:00-05:00",
      "duracion_minutos": 60,
      "estado": "CONFIRMADA",
      "motivo": "Control de ortodoncia",
      "odontologo": {
        "id": 5,
        "nombre": "Dr. Carlos",
        "apellido": "López",
        "full_name": "Dr. Carlos López"
      },
      "paciente": {
        "id": 104,
        "full_name": "María García"
      }
    }
  ]
}
```

### **GET** `/tenant/api/historial/pacientes/me/`
Obtiene el historial clínico del paciente

**Response 200:**
```json
{
  "id": 50,
  "paciente": {
    "id": 104,
    "full_name": "María García",
    "email": "paciente1@test.com"
  },
  "fecha_apertura": "2025-01-15",
  "estado": "ACTIVO",
  "diagnostico_principal": "Caries en piezas 16 y 26",
  "alergias": "Penicilina",
  "enfermedades_cronicas": "Ninguna",
  "medicacion_actual": "Ninguna",
  "episodios_count": 8,
  "documentos_count": 3,
  "ultimo_episodio": {
    "id": 120,
    "fecha": "2025-11-10",
    "motivo": "Control de rutina"
  }
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Dashboard.tsx          ← Implementar completo
│       └── components/
│           ├── ProximasCitas.tsx  ← Nuevo
│           ├── ResumenHistorial.tsx ← Nuevo
│           └── AccesosRapidos.tsx  ← Nuevo
├── services/
│   ├── citasService.ts            ← Nuevo
│   └── historialService.ts        ← Nuevo
└── types/
    ├── citas.types.ts             ← Nuevo
    └── historial.types.ts         ← Nuevo
```

---

## 💻 Código Paso a Paso

### **Paso 1: Crear tipos para Citas**

**Archivo:** `src/types/citas.types.ts`

```typescript
export type EstadoCita = 
  | 'PENDIENTE' 
  | 'CONFIRMADA' 
  | 'EN_CURSO' 
  | 'COMPLETADA' 
  | 'CANCELADA' 
  | 'NO_ASISTIO';

export interface Usuario {
  id: number;
  nombre: string;
  apellido: string;
  full_name: string;
  email?: string;
}

export interface Cita {
  id: number;
  fecha_hora: string; // ISO 8601
  duracion_minutos: number;
  estado: EstadoCita;
  motivo: string;
  observaciones?: string;
  odontologo: Usuario;
  paciente: Usuario;
  creado: string;
  modificado: string;
}

export interface CitasResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Cita[];
}

export interface MisCitasParams {
  limit?: number;
  estado?: EstadoCita;
  fecha_desde?: string;
  fecha_hasta?: string;
}
```

---

### **Paso 2: Crear tipos para Historial**

**Archivo:** `src/types/historial.types.ts`

```typescript
export interface Episodio {
  id: number;
  fecha: string;
  motivo: string;
  diagnostico?: string;
  tratamiento?: string;
}

export interface HistorialClinico {
  id: number;
  paciente: {
    id: number;
    full_name: string;
    email: string;
  };
  fecha_apertura: string;
  estado: 'ACTIVO' | 'INACTIVO';
  diagnostico_principal?: string;
  alergias?: string;
  enfermedades_cronicas?: string;
  medicacion_actual?: string;
  episodios_count: number;
  documentos_count: number;
  ultimo_episodio?: Episodio;
}
```

---

### **Paso 3: Crear servicio de Citas**

**Archivo:** `src/services/citasService.ts`

```typescript
import apiClient from '../config/apiConfig';
import type { CitasResponse, MisCitasParams } from '../types/citas.types';

const citasService = {
  /**
   * Obtener mis citas (del paciente autenticado)
   */
  async getMisCitas(params?: MisCitasParams): Promise<CitasResponse> {
    console.group('📅 [citasService] getMisCitas');
    console.log('Params:', params);
    
    try {
      const response = await apiClient.get<CitasResponse>(
        '/tenant/api/agenda/citas/mis-citas/',
        { params }
      );
      
      console.log('✅ Citas obtenidas:', response.data.count);
      console.groupEnd();
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo citas:', error);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Obtener próximas citas (solo PENDIENTE y CONFIRMADA)
   */
  async getProximasCitas(limit: number = 5): Promise<CitasResponse> {
    const params: MisCitasParams = {
      limit,
      fecha_desde: new Date().toISOString().split('T')[0] // Desde hoy
    };
    
    return this.getMisCitas(params);
  }
};

export default citasService;
```

---

### **Paso 4: Crear servicio de Historial**

**Archivo:** `src/services/historialService.ts`

```typescript
import apiClient from '../config/apiConfig';
import type { HistorialClinico } from '../types/historial.types';

const historialService = {
  /**
   * Obtener mi historial clínico
   */
  async getMiHistorial(): Promise<HistorialClinico> {
    console.group('📋 [historialService] getMiHistorial');
    
    try {
      const response = await apiClient.get<HistorialClinico>(
        '/tenant/api/historial/pacientes/me/'
      );
      
      console.log('✅ Historial obtenido');
      console.log('Episodios:', response.data.episodios_count);
      console.log('Documentos:', response.data.documentos_count);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo historial:', error);
      console.groupEnd();
      throw error;
    }
  }
};

export default historialService;
```

---

### **Paso 5: Componente ProximasCitas**

**Archivo:** `src/pages/paciente/components/ProximasCitas.tsx`

```typescript
import { useEffect, useState } from 'react';
import citasService from '../../../services/citasService';
import type { Cita } from '../../../types/citas.types';

const ProximasCitas = () => {
  const [citas, setCitas] = useState<Cita[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarCitas();
  }, []);

  const cargarCitas = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await citasService.getProximasCitas(3);
      setCitas(response.results);
      
    } catch (err: any) {
      console.error('Error cargando citas:', err);
      setError('No se pudieron cargar las citas');
      
    } finally {
      setLoading(false);
    }
  };

  const formatearFecha = (fechaISO: string) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-ES', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatearHora = (fechaISO: string) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'CONFIRMADA': return '#10b981'; // Verde
      case 'PENDIENTE': return '#f59e0b'; // Amarillo
      case 'EN_CURSO': return '#3b82f6'; // Azul
      default: return '#6b7280'; // Gris
    }
  };

  const getEstadoTexto = (estado: string) => {
    switch (estado) {
      case 'CONFIRMADA': return 'Confirmada';
      case 'PENDIENTE': return 'Pendiente';
      case 'EN_CURSO': return 'En Curso';
      case 'COMPLETADA': return 'Completada';
      case 'CANCELADA': return 'Cancelada';
      default: return estado;
    }
  };

  if (loading) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{ color: '#6b7280' }}>⏳ Cargando citas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{ color: '#ef4444' }}>⚠️ {error}</p>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          margin: 0
        }}>
          📅 Próximas Citas
        </h2>
        <a
          href="/paciente/citas"
          style={{
            fontSize: '14px',
            color: '#3b82f6',
            textDecoration: 'none',
            fontWeight: '500'
          }}
        >
          Ver todas →
        </a>
      </div>

      {/* Lista de Citas */}
      {citas.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          color: '#6b7280'
        }}>
          <p style={{ fontSize: '16px', marginBottom: '8px' }}>📭</p>
          <p style={{ fontSize: '14px' }}>No tienes citas próximas</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {citas.map((cita) => (
            <div
              key={cita.id}
              style={{
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                padding: '16px',
                display: 'flex',
                gap: '16px',
                alignItems: 'flex-start'
              }}
            >
              {/* Fecha */}
              <div style={{
                backgroundColor: '#f3f4f6',
                borderRadius: '6px',
                padding: '12px',
                textAlign: 'center',
                minWidth: '80px'
              }}>
                <div style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#111827',
                  lineHeight: '1'
                }}>
                  {new Date(cita.fecha_hora).getDate()}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  marginTop: '4px'
                }}>
                  {new Date(cita.fecha_hora).toLocaleDateString('es-ES', {
                    month: 'short'
                  }).toUpperCase()}
                </div>
              </div>

              {/* Detalles */}
              <div style={{ flex: 1 }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '8px'
                }}>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#111827',
                    margin: 0
                  }}>
                    {formatearHora(cita.fecha_hora)}
                  </h3>
                  <span style={{
                    fontSize: '12px',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: `${getEstadoColor(cita.estado)}20`,
                    color: getEstadoColor(cita.estado),
                    fontWeight: '500'
                  }}>
                    {getEstadoTexto(cita.estado)}
                  </span>
                </div>

                <p style={{
                  fontSize: '14px',
                  color: '#374151',
                  margin: '4px 0'
                }}>
                  {cita.motivo}
                </p>

                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: '4px 0'
                }}>
                  👨‍⚕️ {cita.odontologo.full_name}
                </p>

                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: '4px 0'
                }}>
                  ⏱️ Duración: {cita.duracion_minutos} minutos
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProximasCitas;
```

---

### **Paso 6: Componente ResumenHistorial**

**Archivo:** `src/pages/paciente/components/ResumenHistorial.tsx`

```typescript
import { useEffect, useState } from 'react';
import historialService from '../../../services/historialService';
import type { HistorialClinico } from '../../../types/historial.types';

const ResumenHistorial = () => {
  const [historial, setHistorial] = useState<HistorialClinico | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarHistorial();
  }, []);

  const cargarHistorial = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await historialService.getMiHistorial();
      setHistorial(data);
      
    } catch (err: any) {
      console.error('Error cargando historial:', err);
      setError('No se pudo cargar el historial');
      
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{ color: '#6b7280' }}>⏳ Cargando historial...</p>
      </div>
    );
  }

  if (error || !historial) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{ color: '#ef4444' }}>⚠️ {error || 'Sin historial'}</p>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          margin: 0
        }}>
          📋 Mi Historial Clínico
        </h2>
        <a
          href="/paciente/historial"
          style={{
            fontSize: '14px',
            color: '#3b82f6',
            textDecoration: 'none',
            fontWeight: '500'
          }}
        >
          Ver completo →
        </a>
      </div>

      {/* Estadísticas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div style={{
          backgroundColor: '#eff6ff',
          borderRadius: '6px',
          padding: '16px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#3b82f6',
            marginBottom: '4px'
          }}>
            {historial.episodios_count}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            Episodios
          </div>
        </div>

        <div style={{
          backgroundColor: '#f0fdf4',
          borderRadius: '6px',
          padding: '16px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#10b981',
            marginBottom: '4px'
          }}>
            {historial.documentos_count}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            Documentos
          </div>
        </div>
      </div>

      {/* Último Episodio */}
      {historial.ultimo_episodio && (
        <div style={{
          borderTop: '1px solid #e5e7eb',
          paddingTop: '16px'
        }}>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '12px'
          }}>
            Última Consulta
          </h3>
          <div style={{
            backgroundColor: '#f9fafb',
            borderRadius: '6px',
            padding: '12px'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#111827',
              margin: '0 0 6px 0',
              fontWeight: '500'
            }}>
              {historial.ultimo_episodio.motivo}
            </p>
            <p style={{
              fontSize: '13px',
              color: '#6b7280',
              margin: 0
            }}>
              📅 {new Date(historial.ultimo_episodio.fecha).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'long',
                year: 'numeric'
              })}
            </p>
          </div>
        </div>
      )}

      {/* Información Importante */}
      {(historial.alergias || historial.enfermedades_cronicas) && (
        <div style={{
          borderTop: '1px solid #e5e7eb',
          paddingTop: '16px',
          marginTop: '16px'
        }}>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '12px'
          }}>
            Información Importante
          </h3>
          {historial.alergias && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '16px' }}>⚠️</span>
              <div>
                <p style={{
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#dc2626',
                  margin: '0 0 2px 0'
                }}>
                  Alergias
                </p>
                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: 0
                }}>
                  {historial.alergias}
                </p>
              </div>
            </div>
          )}
          {historial.enfermedades_cronicas && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px'
            }}>
              <span style={{ fontSize: '16px' }}>🏥</span>
              <div>
                <p style={{
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#374151',
                  margin: '0 0 2px 0'
                }}>
                  Enfermedades Crónicas
                </p>
                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: 0
                }}>
                  {historial.enfermedades_cronicas}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumenHistorial;
```

---

### **Paso 7: Componente AccesosRapidos**

**Archivo:** `src/pages/paciente/components/AccesosRapidos.tsx`

```typescript
const AccesosRapidos = () => {
  const accesos = [
    {
      id: 1,
      titulo: 'Solicitar Cita',
      descripcion: 'Agenda una nueva cita',
      icono: '📅',
      url: '/paciente/citas/solicitar',
      color: '#3b82f6'
    },
    {
      id: 2,
      titulo: 'Mi Historial',
      descripcion: 'Ver historial completo',
      icono: '📋',
      url: '/paciente/historial',
      color: '#10b981'
    },
    {
      id: 3,
      titulo: 'Mis Tratamientos',
      descripcion: 'Planes de tratamiento',
      icono: '🦷',
      url: '/paciente/tratamientos',
      color: '#8b5cf6'
    },
    {
      id: 4,
      titulo: 'Facturas',
      descripcion: 'Consultar pagos',
      icono: '💳',
      url: '/paciente/facturas',
      color: '#f59e0b'
    }
  ];

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      <h2 style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#111827',
        marginBottom: '20px'
      }}>
        ⚡ Accesos Rápidos
      </h2>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '12px'
      }}>
        {accesos.map((acceso) => (
          <a
            key={acceso.id}
            href={acceso.url}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '20px 16px',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              textDecoration: 'none',
              transition: 'all 0.2s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = acceso.color;
              e.currentTarget.style.backgroundColor = `${acceso.color}10`;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e5e7eb';
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{
              fontSize: '32px',
              marginBottom: '12px'
            }}>
              {acceso.icono}
            </div>
            <div style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '4px'
            }}>
              {acceso.titulo}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280'
            }}>
              {acceso.descripcion}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default AccesosRapidos;
```

---

### **Paso 8: Dashboard Principal (Actualizado)**

**Archivo:** `src/pages/paciente/Dashboard.tsx`

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import ProximasCitas from './components/ProximasCitas';
import ResumenHistorial from './components/ResumenHistorial';
import AccesosRapidos from './components/AccesosRapidos';

const Dashboard = () => {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState<any>(null);

  useEffect(() => {
    verificarAutenticacion();
  }, []);

  const verificarAutenticacion = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('⚠️ No hay token, redirigiendo a login...');
      navigate('/paciente/login');
      return;
    }

    // Obtener usuario desde localStorage (guardado en login)
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      setUsuario(user);
      console.log('👤 Usuario cargado:', user.full_name);
    }
  };

  const handleLogout = () => {
    if (confirm('¿Deseas cerrar sesión?')) {
      console.log('👋 Cerrando sesión...');
      authService.logout();
      navigate('/paciente/login');
    }
  };

  if (!usuario) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>⏳ Cargando...</p>
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
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <div>
            <h1 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              🦷 Portal del Paciente
            </h1>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: '4px 0 0 0'
            }}>
              Bienvenido, {usuario.nombre} 👋
            </p>
          </div>

          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#dc2626'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#ef4444'}
          >
            🚪 Cerrar Sesión
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px'
      }}>
        {/* Grid Layout */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '24px'
        }}>
          <ProximasCitas />
          <ResumenHistorial />
        </div>

        <AccesosRapidos />
      </main>
    </div>
  );
};

export default Dashboard;
```

---

## 🧪 Pruebas

### **Caso 1: Dashboard con Datos**
1. Login con `paciente1@test.com` / `paciente123`
2. Verificar dashboard carga:
   - Nombre del usuario en header
   - Próximas 3 citas
   - Resumen del historial (episodios, documentos)
   - 4 accesos rápidos
3. **Esperado**: Todo renderiza correctamente

### **Caso 2: Sin Citas Próximas**
1. Login con paciente sin citas
2. **Esperado**: Mensaje "No tienes citas próximas" con ícono 📭

### **Caso 3: Logout**
1. Click en "Cerrar Sesión"
2. Confirmar en el alert
3. **Esperado**: Redirección a `/paciente/login`
4. **Verificar**: Tokens eliminados de localStorage

### **Caso 4: Acceso Directo sin Login**
1. Navegar a `/paciente/dashboard` sin login
2. **Esperado**: Redirección automática a `/paciente/login`

---

## ✅ Checklist de Verificación

- [ ] Dashboard renderiza correctamente
- [ ] Header muestra nombre del usuario
- [ ] Próximas citas se cargan correctamente
- [ ] Resumen de historial se carga correctamente
- [ ] Accesos rápidos son clickeables
- [ ] Botón de logout funciona
- [ ] Redirección a login si no hay token
- [ ] Estados de loading se muestran
- [ ] Estados de error se manejan
- [ ] Responsive en móvil
- [ ] Console logs informativos

---

## 🐛 Errores Comunes

### **Error 1: 401 Unauthorized**
**Síntoma**: API retorna 401 en todas las peticiones
**Causa**: Token no está siendo enviado en headers
**Solución**: Verificar configuración de axios interceptors

### **Error 2: Usuario undefined**
**Síntoma**: Header muestra "Bienvenido, undefined"
**Causa**: No se guardó el user en localStorage durante login
**Solución**: Revisar Guía 01, paso de guardar datos del usuario

### **Error 3: Redirección infinita**
**Síntoma**: Dashboard redirige constantemente a login
**Causa**: Token existe pero formato incorrecto
**Solución**: Limpiar localStorage y hacer login nuevamente

---

## 🔄 Siguiente Paso

✅ Dashboard completado → Continuar con **`03_ver_perfil_paciente.md`**
