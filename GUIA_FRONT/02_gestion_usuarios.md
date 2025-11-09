# 👥 FASE 2A: GESTIÓN DE USUARIOS - CRUD Y PERFILES

## 📋 Endpoints de Usuarios

### Continuación de Autenticación - Implementar SEGUNDO

```javascript
// Endpoints usuarios
const USER_ENDPOINTS = {
  list: '/api/usuarios/',              // GET - Listar usuarios
  create: '/api/usuarios/',            // POST - Crear usuario (admin)
  detail: '/api/usuarios/{id}/',       // GET - Detalle usuario
  update: '/api/usuarios/{id}/',       // PUT/PATCH - Actualizar
  delete: '/api/usuarios/{id}/',       // DELETE - Eliminar
  profile: '/api/usuarios/me/',        // GET/PUT - Mi perfil
  changePassword: '/api/usuarios/{id}/change-password/' // POST
};
```

## 🔧 1. Servicio de Usuarios

```javascript
// services/userService.js
import api from './apiConfig';

class UserService {
  async getUsers(page = 1, search = '') {
    try {
      const params = { page, search: search || undefined };
      const response = await api.get('/api/usuarios/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error al obtener usuarios' };
    }
  }

  async createUser(userData) {
    try {
      const response = await api.post('/api/usuarios/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear usuario' };
    }
  }

  async getUserDetail(userId) {
    try {
      const response = await api.get(`/api/usuarios/${userId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener detalle del usuario' };
    }
  }

  async updateUser(userId, userData) {
    try {
      const response = await api.put(`/api/usuarios/${userId}/`, userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar usuario' };
    }
  }

  async deleteUser(userId) {
    try {
      await api.delete(`/api/usuarios/${userId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar usuario' };
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await api.put('/api/usuarios/me/', profileData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar perfil' };
    }
  }

  async changePassword(userId, passwordData) {
    try {
      const response = await api.post(`/api/usuarios/${userId}/change-password/`, passwordData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error al cambiar contraseña' };
    }
  }
}

export default new UserService();
```

## 📝 2. Hook personalizado para Usuarios

```javascript
// hooks/useUsers.js
import { useState, useEffect } from 'react';
import userService from '../services/userService';

export function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchUsers = async (page = 1, search = '') => {
    setLoading(true);
    setError('');
    
    const result = await userService.getUsers(page, search);
    
    if (result.success) {
      setUsers(result.data.results || result.data);
      setPagination({
        count: result.data.count,
        next: result.data.next,
        previous: result.data.previous,
        current_page: page
      });
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return {
    users,
    loading,
    error,
    pagination,
    fetchUsers,
    refetch: () => fetchUsers()
  };
}

export function useUserDetail(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUser = async () => {
    if (!userId) return;
    
    setLoading(true);
    const result = await userService.getUserDetail(userId);
    
    if (result.success) {
      setUser(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUser();
  }, [userId]);

  return { user, loading, error, refetch: fetchUser };
}
```

## 📋 3. Componente Lista de Usuarios

```javascript
// components/UsersList.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUsers } from '../hooks/useUsers';
import { useAuth } from '../contexts/AuthContext';

function UsersList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const { users, loading, error, pagination, fetchUsers } = useUsers();
  const { user: currentUser } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchUsers(1, searchTerm);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchUsers(page, searchTerm);
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      'ADMIN': 'bg-red-100 text-red-800',
      'ODONTOLOGO': 'bg-blue-100 text-blue-800',
      'PACIENTE': 'bg-green-100 text-green-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading && currentPage === 1) {
    return <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gestión de Usuarios</h1>
        
        {(currentUser?.tipo_usuario === 'ADMIN') && (
          <Link 
            to="/usuarios/crear"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Crear Usuario
          </Link>
        )}
      </div>

      {/* Búsqueda */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Buscar por nombre o email..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button 
            type="submit"
            className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
          >
            Buscar
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Tabla de usuarios */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usuario
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {user.nombre} {user.apellido}
                    </div>
                    <div className="text-sm text-gray-500">{user.email}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(user.tipo_usuario)}`}>
                    {user.tipo_usuario}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <Link 
                    to={`/usuarios/${user.id}`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Ver
                  </Link>
                  {(currentUser?.tipo_usuario === 'ADMIN' || currentUser?.id === user.id) && (
                    <Link 
                      to={`/usuarios/${user.id}/editar`}
                      className="text-green-600 hover:text-green-900"
                    >
                      Editar
                    </Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Paginación */}
        {pagination && pagination.count > 10 && (
          <div className="bg-white px-6 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Mostrando página {pagination.current_page} de {Math.ceil(pagination.count / 10)}
            </div>
            <div className="flex space-x-2">
              <button
                disabled={!pagination.previous}
                onClick={() => handlePageChange(currentPage - 1)}
                className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                disabled={!pagination.next}
                onClick={() => handlePageChange(currentPage + 1)}
                className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UsersList;
```

## ✏️ 4. Formulario de Usuario

```javascript
// components/UserForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import userService from '../services/userService';
import { useUserDetail } from '../hooks/useUsers';

function UserForm() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const isEditing = !!userId;
  
  const { user: existingUser, loading: loadingUser } = useUserDetail(userId);
  
  const [formData, setFormData] = useState({
    email: '',
    nombre: '',
    apellido: '',
    ci: '',
    sexo: '',
    telefono: '',
    tipo_usuario: 'PACIENTE',
    is_active: true,
    fecha_de_nacimiento: '',
    direccion: '',
    password: '',
    password2: ''
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isEditing && existingUser) {
      setFormData({
        ...existingUser,
        fecha_de_nacimiento: existingUser.perfil_paciente?.fecha_de_nacimiento || '',
        direccion: existingUser.perfil_paciente?.direccion || '',
        password: '',
        password2: ''
      });
    }
  }, [existingUser, isEditing]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) newErrors.email = 'Email es requerido';
    if (!formData.nombre) newErrors.nombre = 'Nombre es requerido';
    if (!formData.apellido) newErrors.apellido = 'Apellido es requerido';
    
    if (!isEditing) {
      if (!formData.password) newErrors.password = 'Contraseña es requerida';
      if (formData.password !== formData.password2) {
        newErrors.password2 = 'Las contraseñas no coinciden';
      }
    }

    if (formData.tipo_usuario === 'PACIENTE' && !formData.fecha_de_nacimiento) {
      newErrors.fecha_de_nacimiento = 'Fecha de nacimiento es requerida para pacientes';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    
    const result = isEditing 
      ? await userService.updateUser(userId, formData)
      : await userService.createUser(formData);
    
    if (result.success) {
      navigate('/usuarios');
    } else {
      if (typeof result.error === 'object') {
        setErrors(result.error);
      } else {
        setErrors({ general: result.error });
      }
    }
    
    setIsSubmitting(false);
  };

  if (isEditing && loadingUser) {
    return <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">
        {isEditing ? 'Editar Usuario' : 'Crear Usuario'}
      </h1>

      {errors.general && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Usuario</label>
            <select
              name="tipo_usuario"
              value={formData.tipo_usuario}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="PACIENTE">Paciente</option>
              <option value="ODONTOLOGO">Odontólogo</option>
              <option value="ADMIN">Administrador</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input
              type="text"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${errors.nombre ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.nombre && <p className="text-red-500 text-sm mt-1">{errors.nombre}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Apellido *</label>
            <input
              type="text"
              name="apellido"
              value={formData.apellido}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${errors.apellido ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.apellido && <p className="text-red-500 text-sm mt-1">{errors.apellido}</p>}
          </div>
        </div>

        {!isEditing && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña *</label>
              <input
                type="password"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${errors.password2 ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.password2 && <p className="text-red-500 text-sm mt-1">{errors.password2}</p>}
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            onClick={() => navigate('/usuarios')}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>
    </div>
  );
}

export default UserForm;
```

## ✅ Próximos Pasos

1. Implementar componente de cambio de contraseña
2. Agregar validaciones adicionales
3. Continuar con **03_inventario.md**

---
**Endpoints implementados**: ✅ CRUD Usuarios ✅ Perfil ✅ Lista paginada ✅ Búsqueda