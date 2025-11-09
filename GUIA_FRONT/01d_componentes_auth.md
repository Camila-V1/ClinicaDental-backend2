# 🔐 FASE 1D: COMPONENTES DE AUTENTICACIÓN

## 🔒 1. Componente ProtectedRoute (components/ProtectedRoute.jsx)

```javascript
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function ProtectedRoute({ children, requiredRole = null }) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.tipo_usuario !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

export default ProtectedRoute;
```

## 📝 2. Componente de Login (components/LoginForm.jsx)

```javascript
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function LoginForm() {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const result = await login(credentials);
    
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              value={credentials.email}
              onChange={(e) => setCredentials({...credentials, email: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md disabled:opacity-50"
          >
            {isLoading ? 'Iniciando...' : 'Iniciar Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
```

## 📋 3. Componente de Registro (components/RegisterForm.jsx)

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function RegisterForm() {
  const [formData, setFormData] = useState({
    email: '', password: '', confirmPassword: '', first_name: '', last_name: '', tipo_usuario: 'paciente'
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      setIsLoading(false);
      return;
    }

    const { confirmPassword, ...userData } = formData;
    const result = await register(userData);
    
    if (result.success) {
      navigate('/login', { state: { message: 'Registro exitoso. Inicia sesión.' } });
    } else {
      setError(result.error);
    }
    setIsLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const inputClass = "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500";

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">Crear Cuenta</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Nombre</label>
              <input type="text" name="first_name" required className={inputClass} value={formData.first_name} onChange={handleChange} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Apellido</label>
              <input type="text" name="last_name" required className={inputClass} value={formData.last_name} onChange={handleChange} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" name="email" required className={inputClass} value={formData.email} onChange={handleChange} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Tipo de Usuario</label>
            <select name="tipo_usuario" className={inputClass} value={formData.tipo_usuario} onChange={handleChange}>
              <option value="PACIENTE">Paciente</option>
              <option value="ODONTOLOGO">Odontólogo</option>
              <option value="ADMIN">Administrador</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input type="password" name="password" required className={inputClass} value={formData.password} onChange={handleChange} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Confirmar Contraseña</label>
            <input type="password" name="confirmPassword" required className={inputClass} value={formData.confirmPassword} onChange={handleChange} />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md disabled:opacity-50"
          >
            {isLoading ? 'Registrando...' : 'Crear Cuenta'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <span className="text-gray-600">¿Ya tienes cuenta? </span>
          <button onClick={() => navigate('/login')} className="text-blue-600 hover:text-blue-800 font-medium">
            Inicia Sesión
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegisterForm;
```

## 🚀 4. Configuración en App.jsx

```javascript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/unauthorized" element={<div>No tienes permisos</div>} />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

## ✅ Implementación Completa

✅ **JWT Authentication** con refresh automático  
✅ **Context API** para estado global  
✅ **Protected Routes** con validación de roles  
✅ **Login Form** con manejo de errores  
✅ **Register Form** con validación  
✅ **Routing** completo configurado

**Continuar con:** `02_gestion_usuarios.md`

## 🔗 Resumen de la Fase 1 Completada

✅ **01a1_axios_core** - Configuración base HTTP + JWT  
✅ **01a2_axios_advanced** - Multi-tenant + Debug  
✅ **01a3_http_utils** - Utilidades HTTP genéricas  
✅ **01b_auth_service** - AuthService y hooks  
✅ **01c_context_auth** - Estado global de autenticación  
✅ **01d_componentes_auth** - Formularios y rutas protegidas

**Sistema de autenticación 100% funcional** 🚀