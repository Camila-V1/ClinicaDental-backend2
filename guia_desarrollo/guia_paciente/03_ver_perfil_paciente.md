# 03 - Ver Perfil del Paciente

## 🎯 Objetivo
Implementar la página donde el paciente puede visualizar toda su información personal, incluyendo datos básicos, de contacto y perfil médico.

---

## 📋 Prerequisitos
- ✅ Login funcional (Guía 01)
- ✅ Dashboard funcional (Guía 02)
- ✅ Usuario autenticado con token válido

---

## 🔌 Endpoint del Backend

### **GET** `/tenant/api/usuarios/me/`
Obtiene los datos del usuario autenticado

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "id": 104,
  "email": "paciente1@test.com",
  "nombre": "María",
  "apellido": "García",
  "ci": "1234567-8",
  "sexo": "F",
  "telefono": "+591 77123456",
  "tipo_usuario": "PACIENTE",
  "is_active": true,
  "date_joined": "2025-01-15T10:30:00-05:00",
  "perfil_paciente": {
    "fecha_de_nacimiento": "1990-05-20",
    "direccion": "Av. América #123, Zona Central"
  },
  "perfil_odontologo": null
}
```

**Nota:** Este endpoint es **solo lectura**. La edición de perfil se implementará en guía posterior cuando se cree el endpoint PUT en el backend.

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       └── Perfil.tsx              ← Nuevo (solo vista)
├── services/
│   └── usuariosService.ts          ← Nuevo
└── types/
    └── usuario.types.ts            ← Nuevo
```

---

## 💻 Código Paso a Paso

### **Paso 1: Crear tipos de Usuario**

**Archivo:** `src/types/usuario.types.ts`

```typescript
export type TipoUsuario = 'PACIENTE' | 'ODONTOLOGO' | 'ADMIN';
export type Sexo = 'M' | 'F' | 'O';

export interface PerfilPaciente {
  fecha_de_nacimiento: string; // YYYY-MM-DD
  direccion?: string;
}

export interface PerfilOdontologo {
  especialidad: string;
  cedulaProfesional: string;
  experienciaProfesional?: string;
}

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  ci: string;
  sexo: Sexo;
  telefono: string;
  tipo_usuario: TipoUsuario;
  is_active: boolean;
  date_joined: string;
  perfil_paciente?: PerfilPaciente;
  perfil_odontologo?: PerfilOdontologo;
}
```

---

### **Paso 2: Crear servicio de Usuarios**

**Archivo:** `src/services/usuariosService.ts`

```typescript
import apiClient from '../config/apiConfig';
import type { Usuario } from '../types/usuario.types';

const usuariosService = {
  /**
   * Obtener datos del usuario autenticado
   */
  async getMiPerfil(): Promise<Usuario> {
    console.group('👤 [usuariosService] getMiPerfil');
    
    try {
      const response = await apiClient.get<Usuario>(
        '/tenant/api/usuarios/me/'
      );
      
      console.log('✅ Perfil obtenido');
      console.log('Usuario:', response.data.nombre, response.data.apellido);
      console.log('Email:', response.data.email);
      console.groupEnd();
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Error obteniendo perfil:', error);
      console.groupEnd();
      throw error;
    }
  }
  
  // Nota: La actualización de perfil se implementará cuando
  // se cree el endpoint PUT en el backend
};

export default usuariosService;
```

---

### **Paso 3: Página de Perfil**

**Archivo:** `src/pages/paciente/Perfil.tsx`

```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import usuariosService from '../../services/usuariosService';
import type { Usuario } from '../../types/usuario.types';

const Perfil = () => {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarPerfil();
  }, []);

  const cargarPerfil = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await usuariosService.getMiPerfil();
      setUsuario(data);
      
    } catch (err: any) {
      console.error('Error cargando perfil:', err);
      
      if (err.response?.status === 401) {
        navigate('/paciente/login');
      } else {
        setError('No se pudo cargar el perfil');
      }
      
    } finally {
      setLoading(false);
    }
  };

  const calcularEdad = (fechaNacimiento: string): number => {
    const hoy = new Date();
    const nacimiento = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    
    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad--;
    }
    
    return edad;
  };

  const formatearFecha = (fecha: string): string => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const getSexoTexto = (sexo: string): string => {
    switch (sexo) {
      case 'M': return 'Masculino';
      case 'F': return 'Femenino';
      case 'O': return 'Otro';
      default: return sexo;
    }
  };

  if (loading) {
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
            ⏳ Cargando perfil...
          </p>
        </div>
      </div>
    );
  }

  if (error || !usuario) {
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
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <p style={{ fontSize: '16px', color: '#ef4444', marginBottom: '16px' }}>
            ⚠️ {error || 'No se pudo cargar el perfil'}
          </p>
          <button
            onClick={cargarPerfil}
            style={{
              padding: '10px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            🔄 Reintentar
          </button>
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
          maxWidth: '1000px',
          margin: '0 auto'
        }}>
          <button
            onClick={() => navigate('/paciente/dashboard')}
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

          <h1 style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Mi Perfil
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '24px'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          {/* Header del Perfil */}
          <div style={{
            padding: '24px',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827',
              margin: '0 0 8px 0'
            }}>
              {usuario.nombre} {usuario.apellido}
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              👤 Paciente • Cuenta {usuario.is_active ? 'Activa' : 'Inactiva'}
            </p>
          </div>

          {/* Información Personal */}
          <div style={{ padding: '24px' }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '16px'
            }}>
              📋 Información Personal
            </h3>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px'
            }}>
              {/* Email */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  📧 Correo Electrónico
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {usuario.email}
                </p>
              </div>

              {/* CI */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  🆔 Cédula de Identidad
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {usuario.ci}
                </p>
              </div>

              {/* Teléfono */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  📱 Teléfono
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {usuario.telefono}
                </p>
              </div>

              {/* Sexo */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  ⚧ Sexo
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {getSexoTexto(usuario.sexo)}
                </p>
              </div>

              {/* Fecha de Nacimiento */}
              {usuario.perfil_paciente?.fecha_de_nacimiento && (
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '13px',
                    fontWeight: '500',
                    color: '#6b7280',
                    marginBottom: '6px'
                  }}>
                    🎂 Fecha de Nacimiento
                  </label>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: '0 0 4px 0'
                  }}>
                    {formatearFecha(usuario.perfil_paciente.fecha_de_nacimiento)}
                  </p>
                  <p style={{
                    fontSize: '12px',
                    color: '#6b7280',
                    margin: 0
                  }}>
                    ({calcularEdad(usuario.perfil_paciente.fecha_de_nacimiento)} años)
                  </p>
                </div>
              )}

              {/* Miembro desde */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  📅 Miembro desde
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {formatearFecha(usuario.date_joined)}
                </p>
              </div>
            </div>

            {/* Dirección */}
            {usuario.perfil_paciente?.direccion && (
              <div style={{
                marginTop: '20px',
                padding: '16px',
                backgroundColor: '#f9fafb',
                borderRadius: '6px'
              }}>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#6b7280',
                  marginBottom: '6px'
                }}>
                  📍 Dirección
                </label>
                <p style={{
                  fontSize: '14px',
                  color: '#111827',
                  margin: 0
                }}>
                  {usuario.perfil_paciente.direccion}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Nota informativa */}
        <div style={{
          marginTop: '20px',
          padding: '16px',
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '8px'
        }}>
          <p style={{
            fontSize: '14px',
            color: '#1e40af',
            margin: 0
          }}>
            ℹ️ <strong>Nota:</strong> Si necesitas actualizar tu información, contacta al administrador de la clínica.
          </p>
        </div>
      </main>
    </div>
  );
};

export default Perfil;
```

---

### **Paso 4: Agregar ruta en App.tsx**

**Archivo:** `src/App.tsx`

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPaciente from './pages/paciente/Login';
import DashboardPaciente from './pages/paciente/Dashboard';
import PerfilPaciente from './pages/paciente/Perfil'; // ← NUEVO

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas de Paciente */}
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        <Route path="/paciente/perfil" element={<PerfilPaciente />} /> {/* ← NUEVO */}
        
        {/* Ruta por defecto */}
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

### **Paso 5: Actualizar Dashboard para incluir link a Perfil**

**Archivo:** `src/pages/paciente/Dashboard.tsx` (modificar header)

Agregar botón de perfil junto al logout:

```typescript
<div style={{
  display: 'flex',
  gap: '12px'
}}>
  <button
    onClick={() => navigate('/paciente/perfil')}
    style={{
      padding: '8px 16px',
      backgroundColor: '#f3f4f6',
      color: '#374151',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'background-color 0.2s'
    }}
    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
  >
    👤 Mi Perfil
  </button>

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
```

---

## 🧪 Pruebas

### **Caso 1: Ver Perfil Completo**
1. Login con `paciente1@test.com` / `paciente123`
2. Click en "Mi Perfil" desde el dashboard
3. **Esperado**: 
   - Vista del perfil con todos los datos
   - Nombre completo en header
   - Todos los campos visibles (email, CI, teléfono, sexo, fecha nacimiento, dirección)
   - Edad calculada correctamente
4. **Verificar consola**: Logs de carga exitosa

### **Caso 2: Perfil sin Dirección**
1. Login con paciente que no tiene dirección
2. Ir a perfil
3. **Esperado**: Sección de dirección no se muestra

### **Caso 3: Botón Volver**
1. En vista de perfil, click en "← Volver"
2. **Esperado**: Regresa al dashboard

### **Caso 4: Acceso Sin Token**
1. Borrar token de localStorage
2. Navegar a `/paciente/perfil`
3. **Esperado**: Redirección automática a login

---

## ✅ Checklist de Verificación

- [ ] Página de perfil carga correctamente
- [ ] Todos los datos del usuario se muestran
- [ ] Edad se calcula correctamente desde fecha de nacimiento
- [ ] Sexo se muestra como texto legible (Masculino/Femenino/Otro)
- [ ] Fechas se formatean correctamente
- [ ] Dirección se muestra solo si existe
- [ ] Estado de loading se muestra durante carga
- [ ] Manejo de error funciona
- [ ] Botón "Volver" regresa al dashboard
- [ ] Botón "Mi Perfil" en dashboard funciona
- [ ] Responsive en móvil
- [ ] Console logs informativos

---

## 🐛 Errores Comunes

### **Error 1: 401 Unauthorized**
**Síntoma**: Redirección a login al abrir perfil
**Causa**: Token expirado o inválido
**Solución**: Hacer login nuevamente

### **Error 2: Edad negativa o incorrecta**
**Síntoma**: Edad muestra número incorrecto
**Causa**: Formato de fecha incorrecto o timezone
**Solución**: Verificar que `fecha_de_nacimiento` sea formato `YYYY-MM-DD`

### **Error 3: Perfil no carga**
**Síntoma**: Loading infinito
**Causa**: Endpoint incorrecto o CORS
**Solución**: Verificar URL `/tenant/api/usuarios/me/` y que backend esté corriendo

---

## 🔄 Siguiente Paso

✅ Ver perfil completado → Continuar con **`04_ver_mis_citas.md`** (Fase 2: Gestión de Citas)
