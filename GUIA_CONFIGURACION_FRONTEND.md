# 🎯 GUÍA DE CONFIGURACIÓN DEL FRONTEND

## 📋 Requisitos de Configuración

### 1. Variables de Entorno (.env)

Crea o actualiza el archivo `.env` en la raíz del proyecto frontend:

```env
# URL del Backend (SIN barra final, SIN /api, SIN /v1)
VITE_API_URL=https://clinica-dental-backend.onrender.com

# Configuración de Tenant (NO usar subdominios)
VITE_USE_SUBDOMAIN=false
VITE_BASE_DOMAIN=onrender.com

# Opcional: Configuración de desarrollo local
# VITE_API_URL=http://localhost:8000
```

### ⚠️ IMPORTANTE:
- ❌ **NO usar**: `https://clinica-dental-backend.onrender.com/api`
- ❌ **NO usar**: `https://clinica-dental-backend.onrender.com/api/v1`
- ✅ **CORRECTO**: `https://clinica-dental-backend.onrender.com`

---

## 🔧 Configuración de Axios

### 2. Archivo de Configuración Base (axios.config.js o similar)

```javascript
import axios from 'axios';

// Obtener la URL base del backend desde variables de entorno
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinica-dental-backend.onrender.com';

// Crear instancia de axios con configuración base
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,  // SIN /api, SIN /v1
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // No necesitamos cookies para JWT
});

// Interceptor para agregar token de autenticación
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el token expiró (401) y no hemos intentado refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          // Intentar renovar el token
          const response = await axios.post(
            `${API_BASE_URL}/api/token/refresh/`,
            { refresh: refreshToken }
          );

          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // Reintentar la petición original con el nuevo token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return axiosInstance(originalRequest);
        }
      } catch (refreshError) {
        // Si el refresh falla, limpiar tokens y redirigir a login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## 🔐 Servicio de Autenticación

### 3. authService.js

```javascript
import axiosInstance from './axios.config';

const authService = {
  /**
   * Login de usuario
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña
   * @returns {Promise} - Tokens y datos del usuario
   */
  async login(email, password) {
    console.log('🔑 authService: Iniciando login...');
    
    // Paso 1: Obtener tokens
    const tokenResponse = await axiosInstance.post('/api/token/', {
      email,
      password,
    });

    const { access, refresh } = tokenResponse.data;

    // Guardar tokens en localStorage
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    console.log('✅ Tokens guardados');

    // Paso 2: Obtener datos del usuario
    const userResponse = await axiosInstance.get('/api/usuarios/me/', {
      headers: {
        Authorization: `Bearer ${access}`,
      },
    });

    const userData = userResponse.data;

    // Guardar datos del usuario
    localStorage.setItem('user', JSON.stringify(userData));

    console.log('✅ Usuario autenticado:', userData.email);

    return {
      access,
      refresh,
      user: userData,
    };
  },

  /**
   * Logout - Limpiar sesión
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    console.log('🚪 Sesión cerrada');
  },

  /**
   * Obtener usuario actual del localStorage
   * @returns {Object|null}
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Verificar si el usuario está autenticado
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Renovar token de acceso
   * @returns {Promise<string>} - Nuevo access token
   */
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axiosInstance.post('/api/token/refresh/', {
      refresh: refreshToken,
    });

    const newAccessToken = response.data.access;
    localStorage.setItem('access_token', newAccessToken);

    return newAccessToken;
  },
};

export default authService;
```

---

## 📡 Servicios de API

### 4. agendaService.js (Ejemplo)

```javascript
import axiosInstance from './axios.config';

const agendaService = {
  /**
   * Obtener métricas del día
   */
  async getMetricasDia() {
    console.log('📊 Obteniendo métricas del día...');
    const response = await axiosInstance.get('/api/agenda/citas/metricas-dia/');
    return response.data;
  },

  /**
   * Obtener citas de hoy
   */
  async getCitasHoy() {
    const response = await axiosInstance.get('/api/agenda/citas/hoy/');
    return response.data;
  },

  /**
   * Obtener todas las citas
   */
  async getCitas(params = {}) {
    const response = await axiosInstance.get('/api/agenda/citas/', { params });
    return response.data;
  },

  /**
   * Crear nueva cita
   */
  async crearCita(citaData) {
    const response = await axiosInstance.post('/api/agenda/citas/', citaData);
    return response.data;
  },

  /**
   * Actualizar cita
   */
  async actualizarCita(citaId, citaData) {
    const response = await axiosInstance.patch(`/api/agenda/citas/${citaId}/`, citaData);
    return response.data;
  },

  /**
   * Confirmar cita
   */
  async confirmarCita(citaId) {
    const response = await axiosInstance.post(`/api/agenda/citas/${citaId}/confirmar/`);
    return response.data;
  },

  /**
   * Cancelar cita
   */
  async cancelarCita(citaId) {
    const response = await axiosInstance.post(`/api/agenda/citas/${citaId}/cancelar/`);
    return response.data;
  },

  /**
   * Obtener horarios disponibles
   */
  async getHorariosDisponibles(odontologoId, fecha) {
    const response = await axiosInstance.get('/api/agenda/citas/horarios_disponibles/', {
      params: {
        odontologo: odontologoId,
        fecha: fecha, // Formato: YYYY-MM-DD
      },
    });
    return response.data;
  },
};

export default agendaService;
```

### 5. reportesService.js (Ejemplo)

```javascript
import axiosInstance from './axios.config';

const reportesService = {
  /**
   * Obtener KPIs del dashboard
   */
  async getDashboardKPIs() {
    const response = await axiosInstance.get('/api/reportes/dashboard-kpis/');
    return response.data;
  },

  /**
   * Obtener estadísticas generales
   */
  async getEstadisticasGenerales() {
    const response = await axiosInstance.get('/api/reportes/estadisticas-generales/');
    return response.data;
  },

  /**
   * Obtener tendencia de citas
   */
  async getTendenciaCitas(dias = 15) {
    const response = await axiosInstance.get('/api/reportes/tendencia-citas/', {
      params: { dias },
    });
    return response.data;
  },

  /**
   * Obtener top procedimientos
   */
  async getTopProcedimientos(limite = 5) {
    const response = await axiosInstance.get('/api/reportes/top-procedimientos/', {
      params: { limite },
    });
    return response.data;
  },
};

export default reportesService;
```

### 6. usuariosService.js

```javascript
import axiosInstance from './axios.config';

const usuariosService = {
  /**
   * Obtener perfil del usuario actual
   */
  async getMe() {
    const response = await axiosInstance.get('/api/usuarios/me/');
    return response.data;
  },

  /**
   * Obtener lista de odontólogos
   */
  async getOdontologos() {
    const response = await axiosInstance.get('/api/usuarios/odontologos/');
    return response.data;
  },

  /**
   * Obtener lista de pacientes
   */
  async getPacientes() {
    const response = await axiosInstance.get('/api/usuarios/pacientes/');
    return response.data;
  },

  /**
   * Registrar nuevo paciente
   */
  async registrarPaciente(pacienteData) {
    const response = await axiosInstance.post('/api/usuarios/register/', pacienteData);
    return response.data;
  },
};

export default usuariosService;
```

---

## 🎨 Componente de Login (React)

### 7. LoginPage.jsx

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await authService.login(email, password);
      console.log('✅ Login exitoso:', result.user.email);
      
      // Redirigir según tipo de usuario
      if (result.user.tipo_usuario === 'ODONTOLOGO') {
        navigate('/dashboard');
      } else if (result.user.tipo_usuario === 'PACIENTE') {
        navigate('/paciente/dashboard');
      } else {
        navigate('/admin/dashboard');
      }
    } catch (err) {
      console.error('❌ Error en login:', err);
      
      if (err.response?.status === 401) {
        setError('Email o contraseña incorrectos');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Error al iniciar sesión. Intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Iniciar Sesión</h1>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Iniciando sesión...' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
```

---

## 🛡️ Rutas Protegidas

### 8. ProtectedRoute.jsx

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

const ProtectedRoute = ({ children, requiredRole }) => {
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getCurrentUser();

  if (!isAuthenticated) {
    // Redirigir a login si no está autenticado
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.tipo_usuario !== requiredRole) {
    // Redirigir si no tiene el rol requerido
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### 9. Uso de ProtectedRoute en App.jsx

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PacienteDashboard from './pages/PacienteDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute requiredRole="ODONTOLOGO">
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/paciente/dashboard"
          element={
            <ProtectedRoute requiredRole="PACIENTE">
              <PacienteDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Variables de Entorno
- [ ] Crear archivo `.env` en la raíz del proyecto
- [ ] Configurar `VITE_API_URL=https://clinica-dental-backend.onrender.com`
- [ ] Configurar `VITE_USE_SUBDOMAIN=false`
- [ ] Verificar que NO haya `/api` ni `/v1` en `VITE_API_URL`

### Configuración de Axios
- [ ] Crear archivo de configuración de axios (`axios.config.js`)
- [ ] Configurar `baseURL` usando `VITE_API_URL`
- [ ] Implementar interceptor para agregar token automáticamente
- [ ] Implementar interceptor para manejar refresh de tokens

### Servicios
- [ ] Crear `authService.js` con métodos login, logout, etc.
- [ ] Crear servicios para cada módulo (agenda, reportes, usuarios, etc.)
- [ ] Usar rutas SIN `/v1/` (ejemplo: `/api/agenda/citas/`)

### Autenticación
- [ ] Implementar página de login
- [ ] Implementar componente de rutas protegidas
- [ ] Guardar tokens en `localStorage`
- [ ] Implementar logout

### Pruebas
- [ ] Probar login con credenciales válidas
- [ ] Verificar que el token se guarda correctamente
- [ ] Probar acceso a endpoints protegidos
- [ ] Verificar refresh automático de tokens
- [ ] Probar logout

---

## 🔗 ENDPOINTS DISPONIBLES

### Autenticación
- `POST /api/token/` - Login
- `POST /api/token/refresh/` - Refresh token

### Usuarios
- `GET /api/usuarios/me/` - Perfil actual
- `GET /api/usuarios/odontologos/` - Lista odontólogos
- `GET /api/usuarios/pacientes/` - Lista pacientes
- `POST /api/usuarios/register/` - Registrar paciente

### Agenda
- `GET /api/agenda/citas/` - Lista de citas
- `POST /api/agenda/citas/` - Crear cita
- `GET /api/agenda/citas/{id}/` - Detalle de cita
- `PATCH /api/agenda/citas/{id}/` - Actualizar cita
- `GET /api/agenda/citas/metricas-dia/` - Métricas del día
- `GET /api/agenda/citas/hoy/` - Citas de hoy
- `POST /api/agenda/citas/{id}/confirmar/` - Confirmar cita
- `POST /api/agenda/citas/{id}/cancelar/` - Cancelar cita

### Reportes
- `GET /api/reportes/dashboard-kpis/` - KPIs del dashboard
- `GET /api/reportes/estadisticas-generales/` - Estadísticas
- `GET /api/reportes/tendencia-citas/` - Tendencia de citas
- `GET /api/reportes/top-procedimientos/` - Top procedimientos

### Historial Clínico
- `GET /api/historial/historiales/` - Lista historiales
- `GET /api/historial/episodios/` - Lista episodios
- `GET /api/historial/odontogramas/` - Lista odontogramas
- `GET /api/historial/documentos/` - Lista documentos

### Tratamientos
- `GET /api/tratamientos/servicios/` - Lista servicios
- `GET /api/tratamientos/planes/` - Lista planes
- `GET /api/tratamientos/presupuestos/` - Lista presupuestos

### Facturación
- `GET /api/facturacion/facturas/` - Lista facturas
- `GET /api/facturacion/pagos/` - Lista pagos

### Inventario
- `GET /api/inventario/insumos/` - Lista insumos
- `GET /api/inventario/categorias/` - Lista categorías

---

## 🔑 CREDENCIALES DE PRUEBA

```javascript
// Odontólogo
{
  email: 'odontologo@clinica-demo.com',
  password: 'odontologo123',
  tipo: 'ODONTOLOGO'
}

// Pacientes
{
  email: 'paciente1@test.com',  // hasta paciente5@test.com
  password: 'paciente123',
  tipo: 'PACIENTE'
}
```

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### Error 404 en endpoints
❌ **Problema**: `GET /api/v1/agenda/citas/` → 404
✅ **Solución**: Remover `/v1/` → `GET /api/agenda/citas/`

### Error CORS
❌ **Problema**: CORS policy error
✅ **Solución**: Verificar que el frontend esté en `dentaabcxy.store` o dominio permitido

### Token expirado
❌ **Problema**: 401 Unauthorized después de 5 minutos
✅ **Solución**: Implementar interceptor de refresh (ver ejemplo arriba)

### BaseURL incorrecta
❌ **Problema**: URLs duplicadas `/api/api/token/`
✅ **Solución**: No incluir `/api` en `VITE_API_URL`, solo usar `https://clinica-dental-backend.onrender.com`

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa la consola del navegador
2. Verifica las variables de entorno
3. Confirma que las rutas NO incluyan `/v1/`
4. Revisa que el token se esté enviando en el header `Authorization`

---

✅ **SISTEMA LISTO PARA INTEGRACIÓN**
