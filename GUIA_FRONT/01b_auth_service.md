# 🔐 FASE 1B: AUTH SERVICE Y HOOKS

## 🔑 Servicio de Autenticación (services/authService.js)

```javascript
import api from './apiConfig';
import { get, post } from './httpUtils';

class AuthService {
  // Login: email + password → JWT tokens
  async login(credentials) {
    const result = await post('/api/token/', credentials);
    
    if (result.success) {
      const { access, refresh, user } = result.data;
      
      // Guardar tokens y usuario en localStorage
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, data: result.data };
    }
    
    return result;
  }

  // Registro: crear nuevo usuario
  async register(userData) {
    return await post('/api/usuarios/register/', userData);
  }

  // Obtener perfil del usuario actual
  async getProfile() {
    return await get('/api/usuarios/me/');
  }

  // Actualizar perfil del usuario
  async updateProfile(userData) {
    const result = await post('/api/usuarios/me/', userData);
    
    if (result.success) {
      // Actualizar usuario en localStorage
      localStorage.setItem('user', JSON.stringify(result.data));
    }
    
    return result;
  }

  // Cambiar contraseña
  async changePassword(passwordData) {
    return await post('/api/usuarios/change-password/', passwordData);
  }

  // Logout: limpiar localStorage y redirigir
  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  // Verificar si está autenticado
  isAuthenticated() {
    const token = localStorage.getItem('accessToken');
    return !!token && !this.isTokenExpired();
  }

  // Obtener usuario desde localStorage
  getCurrentUser() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }

  // Validar si el token está expirado
  isTokenExpired() {
    const token = localStorage.getItem('accessToken');
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp < now;
    } catch (error) {
      console.error('Error parsing token:', error);
      return true;
    }
  }

  // Obtener tiempo restante del token (en segundos)
  getTokenExpiryTime() {
    const token = localStorage.getItem('accessToken');
    if (!token) return 0;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return Math.max(0, payload.exp - now);
    } catch {
      return 0;
    }
  }

  // Verificar roles del usuario
  hasRole(requiredRole) {
    const user = this.getCurrentUser();
    return user?.tipo_usuario === requiredRole;
  }

  // Verificar si tiene alguno de los roles especificados
  hasAnyRole(roles) {
    const user = this.getCurrentUser();
    return roles.includes(user?.tipo_usuario);
  }

  // Obtener permisos basados en el tipo de usuario
  getPermissions() {
    const user = this.getCurrentUser();
    if (!user) return [];

    switch (user.tipo_usuario) {
      case 'admin':
        return ['all'];
      case 'doctor':
      case 'odontologo':
        return ['view_patients', 'edit_patients', 'view_appointments', 'edit_appointments', 'view_treatments'];
      case 'paciente':
        return ['view_own_appointments', 'view_own_treatments'];
      default:
        return [];
    }
  }

  // Verificar si tiene un permiso específico
  hasPermission(permission) {
    const permissions = this.getPermissions();
    return permissions.includes('all') || permissions.includes(permission);
  }
}

export default new AuthService();
```

## 🎣 Hook useAuth (hooks/useAuth.js)

```javascript
import { useState, useEffect } from 'react';
import authService from '../services/authService';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Inicializar autenticación
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const result = await authService.getProfile();
          if (result.success) {
            setUser(result.data);
            setIsAuthenticated(true);
          } else {
            authService.logout();
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (credentials) => {
    setIsLoading(true);
    setError(null);
    const result = await authService.login(credentials);
    if (result.success) {
      setUser(result.data.user);
      setIsAuthenticated(true);
    } else {
      setError(result.error);
    }
    setIsLoading(false);
    return result;
  };

  const register = async (userData) => {
    setIsLoading(true);
    setError(null);
    const result = await authService.register(userData);
    if (!result.success) setError(result.error);
    setIsLoading(false);
    return result;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  return {
    user, isAuthenticated, isLoading, error,
    login, register, logout,
    clearError: () => setError(null),
    hasRole: authService.hasRole,
    hasPermission: authService.hasPermission
  };
};
```

## 🛡️ Hooks Adicionales (hooks/authHooks.js)

```javascript
import { useMemo, useEffect, useCallback } from 'react';
import authService from '../services/authService';

// Hook para verificar permisos
export const usePermissions = (userType) => {
  return useMemo(() => {
    if (!userType) return {};
    
    return {
      isAdmin: userType === 'ADMIN',
      isDoctor: ['ODONTOLOGO', 'doctor'].includes(userType),
      isPaciente: userType === 'PACIENTE',
      isStaff: ['ADMIN', 'ODONTOLOGO', 'doctor'].includes(userType),
      canManageUsers: userType === 'ADMIN',
      canViewAllPatients: ['ADMIN', 'ODONTOLOGO', 'doctor'].includes(userType),
      canManageAppointments: ['ADMIN', 'ODONTOLOGO', 'doctor'].includes(userType),
      canViewReports: ['ADMIN', 'ODONTOLOGO', 'doctor'].includes(userType),
      canManageInventory: ['ADMIN', 'ODONTOLOGO', 'doctor'].includes(userType)
    };
  }, [userType]);
};

// Hook para monitorear expiración de token
export const useTokenMonitor = () => {
  const checkTokenExpiry = useCallback(() => {
    if (!authService.isAuthenticated()) return;
    
    const timeLeft = authService.getTokenExpiryTime();
    
    // Si quedan menos de 1 minuto, forzar logout
    if (timeLeft > 0 && timeLeft < 60) {
      console.log('Token por expirar, cerrando sesión...');
      authService.logout();
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(checkTokenExpiry, 30000); // Check cada 30 segundos
    checkTokenExpiry(); // Check inmediato
    return () => clearInterval(interval);
  }, [checkTokenExpiry]);
};

// Hook para validar roles
export const useRoleValidation = (requiredRoles = []) => {
  const user = authService.getCurrentUser();
  
  return useMemo(() => {
    if (!user || !requiredRoles.length) return false;
    return requiredRoles.includes(user.tipo_usuario);
  }, [user, requiredRoles]);
};
```

## ✅ AuthService y Hooks Completados

✅ **AuthService completo** con todos los métodos necesarios  
✅ **Hook useAuth** para estado de autenticación  
✅ **Hook usePermissions** para verificación de roles  
✅ **Hook useTokenRefresh** para monitorear expiración  
✅ **Manejo de permisos** granular por tipo de usuario

**Continuar con:** `01c_context_auth.md` (Context de React)