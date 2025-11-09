# 🔐 FASE 1C: CONTEXT DE AUTENTICACIÓN

## 🎯 Context de Autenticación (contexts/AuthContext.js)

```javascript
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService from '../services/authService';

// Crear contexto
const AuthContext = createContext();

// Estado inicial
const initialState = { 
  user: null, 
  isAuthenticated: false, 
  isLoading: true 
};

// Reducer para manejar acciones
function authReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
      
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        user: action.payload, 
        isAuthenticated: true, 
        isLoading: false 
      };
      
    case 'LOGOUT':
      return { ...initialState, isLoading: false };
      
    case 'UPDATE_USER':
      return { ...state, user: action.payload };
      
    default:
      return state;
  }
}

// Provider del contexto
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Inicializar autenticación al cargar la app
  useEffect(() => {
    const initAuth = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      if (authService.isAuthenticated()) {
        // Verificar si el token está expirado
        if (authService.isTokenExpired()) {
          authService.logout();
          dispatch({ type: 'LOGOUT' });
          return;
        }

        // Obtener perfil del usuario
        const result = await authService.getProfile();
        if (result.success) {
          dispatch({ type: 'LOGIN_SUCCESS', payload: result.data });
        } else {
          authService.logout();
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initAuth();
  }, []);

  // Función de login
  const login = async (credentials) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    const result = await authService.login(credentials);
    
    if (result.success) {
      dispatch({ type: 'LOGIN_SUCCESS', payload: result.data.user });
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
    
    return result;
  };

  // Función de registro
  const register = async (userData) => {
    return await authService.register(userData);
  };

  // Función de logout
  const logout = () => {
    authService.logout();
    dispatch({ type: 'LOGOUT' });
  };

  // Función para actualizar perfil
  const updateProfile = async () => {
    const result = await authService.getProfile();
    if (result.success) {
      dispatch({ type: 'UPDATE_USER', payload: result.data });
    }
    return result;
  };

  // Verificar permisos del usuario
  const hasRole = (requiredRole) => {
    return state.user?.tipo_usuario === requiredRole;
  };

  const hasAnyRole = (roles) => {
    return roles.includes(state.user?.tipo_usuario);
  };

  // Valor del contexto
  const contextValue = {
    // Estado
    ...state,
    
    // Acciones
    login,
    register,
    logout,
    updateProfile,
    
    // Utilidades
    hasRole,
    hasAnyRole,
    
    // Info del usuario
    userType: state.user?.tipo_usuario || null,
    userName: state.user ? `${state.user.first_name} ${state.user.last_name}` : null,
    userEmail: state.user?.email || null
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  
  return context;
};

// Hook para verificar roles específicos
export const useRoleCheck = () => {
  const { hasRole, hasAnyRole, userType } = useAuth();
  
  return {
    isAdmin: hasRole('ADMIN'),
    isDoctor: hasRole('ODONTOLOGO'),
    isPaciente: hasRole('PACIENTE'),
    
    isStaff: hasAnyRole(['ADMIN', 'ODONTOLOGO']),
    canManageUsers: hasAnyRole(['ADMIN']),
    canManageCitas: hasAnyRole(['ADMIN', 'ODONTOLOGO']),
    canViewReports: hasAnyRole(['ADMIN', 'ODONTOLOGO']),
    
    userType
  };
};
```

## 🛡️ Componente de Error Boundary

```javascript
// components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error en AuthProvider:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md text-center">
            <h2 className="text-xl font-bold text-red-600 mb-4">Error de Autenticación</h2>
            <p className="text-gray-600 mb-4">Ha ocurrido un error en el sistema de autenticación.</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Recargar Página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## 📱 Ejemplo de uso en App.jsx

```javascript
import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';

// Componente que usa el contexto
function AppContent() {
  const { user, isAuthenticated, isLoading, userType } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <h1>Bienvenido, {user?.first_name}!</h1>
          <p>Tipo de usuario: {userType}</p>
        </div>
      ) : (
        <div>No autenticado</div>
      )}
    </div>
  );
}

// App principal
function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
```

## ✅ Context de Autenticación Completado

✅ **AuthContext** con estado global completo  
✅ **Hooks personalizados** para roles y permisos  
✅ **Error Boundary** para manejo de errores  
✅ **Inicialización automática** del estado  
✅ **Verificación de tokens** expirados

**Continuar con:** `01d_componentes_auth.md` (Login/Register Forms)