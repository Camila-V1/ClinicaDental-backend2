# 01 - Login del Paciente

## 🎯 Objetivo
Implementar el formulario de login específico para pacientes, con validación de credenciales, manejo de errores y redirección al dashboard.

---

## 📋 Prerequisitos
- ✅ Backend corriendo en `http://clinica-demo.localhost:8000`
- ✅ Axios configurado con multi-tenant
- ✅ Context de autenticación creado
- ✅ React Router configurado

---

## 🔌 Endpoint del Backend

### **POST** `/public/api/token/`
Autenticación JWT multi-tenant

**Request:**
```json
{
  "email": "paciente1@test.com",
  "password": "paciente123"
}
```

**Response 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 104,
    "email": "paciente1@test.com",
    "tipo_usuario": "PACIENTE",
    "nombre": "María",
    "apellido": "García",
    "full_name": "María García"
  }
}
```

**Response 401:**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

## 🧩 Componentes a Crear

```
src/
├── pages/
│   └── paciente/
│       ├── Login.tsx          ← Nuevo
│       └── Dashboard.tsx      ← Placeholder
├── services/
│   └── authService.ts         ← Usar existente
└── types/
    └── auth.types.ts          ← Extender existente
```

---

## 💻 Código Paso a Paso

### **Paso 1: Extender tipos de autenticación**

**Archivo:** `src/types/auth.types.ts`

```typescript
// Agregar al archivo existente

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    tipo_usuario: 'PACIENTE' | 'ODONTOLOGO' | 'ADMIN';
    nombre: string;
    apellido: string;
    full_name: string;
  };
}

export interface AuthError {
  detail?: string;
  error?: string;
  message?: string;
}
```

---

### **Paso 2: Verificar servicio de autenticación**

**Archivo:** `src/services/authService.ts` (debe existir)

```typescript
import apiClient from '../config/apiConfig';
import type { LoginCredentials, LoginResponse } from '../types/auth.types';

const authService = {
  /**
   * Login de usuario (paciente, odontólogo, admin)
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    console.group('🔐 [authService] login');
    console.log('📧 Email:', credentials.email);
    
    try {
      const response = await apiClient.post<LoginResponse>(
        '/public/api/token/',
        credentials
      );
      
      console.log('✅ Login exitoso');
      console.log('👤 Usuario:', response.data.user.full_name);
      console.log('🏷️ Tipo:', response.data.user.tipo_usuario);
      
      // Guardar tokens en localStorage
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      console.groupEnd();
      return response.data;
      
    } catch (error: any) {
      console.group('❌ [authService] Error en login');
      console.error('Error completo:', error);
      console.error('Response:', error.response?.data);
      console.groupEnd();
      throw error;
    }
  },

  /**
   * Logout - limpia tokens
   */
  logout(): void {
    console.log('👋 Cerrando sesión...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

export default authService;
```

---

### **Paso 3: Crear componente de Login**

**Archivo:** `src/pages/paciente/Login.tsx`

```typescript
import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import type { LoginCredentials, AuthError } from '../../types/auth.types';

const Login = () => {
  const navigate = useNavigate();
  
  // Estado del formulario
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: ''
  });
  
  // Estados de UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handler: Submit del formulario
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    console.group('🔐 Login - Iniciando');
    console.log('📧 Email:', credentials.email);
    
    // Validaciones básicas
    if (!credentials.email || !credentials.password) {
      setError('Por favor completa todos los campos');
      console.warn('⚠️ Campos incompletos');
      console.groupEnd();
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Llamar al servicio de login
      const response = await authService.login(credentials);
      
      console.log('✅ Login exitoso');
      console.log('👤 Usuario:', response.user.full_name);
      console.log('🏷️ Tipo:', response.user.tipo_usuario);
      
      // Verificar que sea paciente
      if (response.user.tipo_usuario !== 'PACIENTE') {
        setError('Este portal es solo para pacientes');
        authService.logout();
        console.error('❌ Usuario no es paciente');
        console.groupEnd();
        return;
      }
      
      // Redireccionar al dashboard
      console.log('🔄 Redirigiendo a dashboard...');
      console.groupEnd();
      navigate('/paciente/dashboard');
      
    } catch (err: any) {
      console.group('❌ Error en login');
      console.error('Error completo:', err);
      
      const errorData = err.response?.data as AuthError;
      const errorMessage = 
        errorData?.detail || 
        errorData?.error || 
        errorData?.message || 
        'Error al iniciar sesión. Verifica tus credenciales.';
      
      setError(errorMessage);
      console.error('Mensaje de error:', errorMessage);
      console.groupEnd();
      
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handler: Cambio en inputs
   */
  const handleChange = (field: keyof LoginCredentials, value: string) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpiar error al escribir
    if (error) setError(null);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f3f4f6',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: '32px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '8px'
          }}>
            🦷 Portal del Paciente
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Ingresa con tu cuenta para continuar
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit}>
          {/* Email */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Correo Electrónico
            </label>
            <input
              type="email"
              value={credentials.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="ejemplo@correo.com"
              disabled={loading}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>

          {/* Password */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Contraseña
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => handleChange('password', e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '6px',
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

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: loading ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#2563eb';
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#3b82f6';
            }}
          >
            {loading ? '⏳ Iniciando sesión...' : '🔓 Iniciar Sesión'}
          </button>
        </form>

        {/* Footer */}
        <div style={{
          marginTop: '24px',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            ¿Olvidaste tu contraseña?{' '}
            <a
              href="#"
              style={{
                color: '#3b82f6',
                textDecoration: 'none',
                fontWeight: '500'
              }}
              onClick={(e) => {
                e.preventDefault();
                alert('Funcionalidad próximamente');
              }}
            >
              Recuperar
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

---

### **Paso 4: Crear Dashboard placeholder**

**Archivo:** `src/pages/paciente/Dashboard.tsx`

```typescript
const Dashboard = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>🏠 Dashboard del Paciente</h1>
      <p>Bienvenido al portal del paciente</p>
      <p style={{ color: '#6b7280', fontSize: '14px' }}>
        Esta página se desarrollará en la siguiente guía
      </p>
    </div>
  );
};

export default Dashboard;
```

---

### **Paso 5: Configurar rutas**

**Archivo:** `src/App.tsx` (agregar rutas)

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPaciente from './pages/paciente/Login';
import DashboardPaciente from './pages/paciente/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas de Paciente */}
        <Route path="/paciente/login" element={<LoginPaciente />} />
        <Route path="/paciente/dashboard" element={<DashboardPaciente />} />
        
        {/* Ruta por defecto */}
        <Route path="/" element={<LoginPaciente />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 🧪 Pruebas

### **Caso 1: Login Exitoso**
1. Navegar a `http://clinica-demo.localhost:3000/paciente/login`
2. Ingresar credenciales:
   - Email: `paciente1@test.com`
   - Password: `paciente123`
3. Click en "Iniciar Sesión"
4. **Esperado**: Redirección a `/paciente/dashboard`
5. **Verificar consola**:
   ```
   🔐 [authService] login
   ✅ Login exitoso
   👤 Usuario: María García
   🏷️ Tipo: PACIENTE
   🔄 Redirigiendo a dashboard...
   ```

### **Caso 2: Credenciales Incorrectas**
1. Ingresar email: `paciente1@test.com`
2. Ingresar password incorrecta: `wrongpassword`
3. Click en "Iniciar Sesión"
4. **Esperado**: Mensaje de error rojo
5. **Verificar**: "No active account found with the given credentials"

### **Caso 3: Usuario No Paciente**
1. Ingresar credenciales de odontólogo:
   - Email: `odontologo@clinica-demo.com`
   - Password: `odontologo123`
2. Click en "Iniciar Sesión"
3. **Esperado**: Error "Este portal es solo para pacientes"
4. **Verificar**: Tokens eliminados de localStorage

### **Caso 4: Campos Vacíos**
1. Dejar campos vacíos
2. Click en "Iniciar Sesión"
3. **Esperado**: Mensaje "Por favor completa todos los campos"
4. **Verificar**: No se hace llamada al backend

---

## ✅ Checklist de Verificación

- [ ] Formulario renderiza correctamente
- [ ] Inputs funcionan (email y password)
- [ ] Validación de campos vacíos funciona
- [ ] Login exitoso guarda tokens en localStorage
- [ ] Redirección al dashboard funciona
- [ ] Error de credenciales incorrectas se muestra
- [ ] Validación de tipo_usuario=PACIENTE funciona
- [ ] Loading state se muestra durante la petición
- [ ] Botón se deshabilita durante loading
- [ ] Error desaparece al escribir de nuevo
- [ ] Consola muestra logs correctos
- [ ] Responsive en móvil

---

## 🐛 Errores Comunes

### **Error 1: CORS - Network Error**
**Síntoma**: `Network Error` en consola
**Causa**: Backend no acepta peticiones desde el frontend
**Solución**:
```python
# backend/core/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://clinica-demo.localhost:3000',
    'http://localhost:3000',
]
```

### **Error 2: 404 Not Found**
**Síntoma**: `POST /public/api/token/ 404`
**Causa**: URL incorrecta del endpoint
**Solución**: Verificar que sea `/public/api/token/` (con `/public/`)

### **Error 3: Tokens no se guardan**
**Síntoma**: Redirección exitosa pero no hay tokens
**Causa**: localStorage.setItem dentro del catch
**Solución**: Mover `setItem` al bloque try después de response exitosa

### **Error 4: Redirección no funciona**
**Síntoma**: Login exitoso pero no redirige
**Causa**: `useNavigate` no está dentro de `<BrowserRouter>`
**Solución**: Verificar que App.tsx tenga BrowserRouter wrapping

---

## 📊 Verificación en Backend

Ver logs del servidor Django:
```
[15/Nov/2025 10:30:00] "OPTIONS /public/api/token/ HTTP/1.1" 200 0
[15/Nov/2025 10:30:00] "POST /public/api/token/ HTTP/1.1" 200 246
```

Si ves `200`, el login fue exitoso. Si ves `401`, credenciales incorrectas.

---

## 🔄 Siguiente Paso

✅ Login completado → Continuar con **`02_dashboard_paciente.md`**

