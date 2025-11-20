# 👥 Gestión de Usuarios (Equipo de Trabajo)

## 🎯 Objetivo
Crear la interfaz para administrar el equipo de trabajo de la clínica: odontólogos, recepcionistas y administradores. Cada admin solo verá los usuarios de su propia clínica.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Listar usuarios** del equipo con filtros
2. **Crear nuevos usuarios** (odontólogo, recepcionista, admin)
3. **Editar información** de usuarios existentes
4. **Desactivar/Activar** usuarios (soft delete)
5. **Asignar permisos** y roles
6. **Ver perfil detallado** con estadísticas

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Listar usuarios
GET /api/usuarios/usuarios/?tipo_usuario=ODONTOLOGO&is_active=true
Response: {
  count: 10,
  results: [
    {
      id: 1,
      email: "juan.perez@clinica.com",
      first_name: "Juan",
      last_name: "Pérez",
      full_name: "Juan Pérez",
      tipo_usuario: "ODONTOLOGO",
      is_active: true,
      date_joined: "2025-01-15T10:00:00Z",
      perfil_odontologo: {
        especialidad: "Ortodoncia",
        numero_licencia: "12345",
        telefono: "555-1234"
      }
    }
  ]
}

// 2. Crear usuario
POST /api/usuarios/usuarios/
Body: {
  email: "nuevo.doctor@clinica.com",
  password: "SecurePass123!",
  first_name: "María",
  last_name: "García",
  tipo_usuario: "ODONTOLOGO",
  perfil_odontologo: {
    especialidad: "Endodoncia",
    numero_licencia: "67890",
    telefono: "555-5678"
  }
}

// 3. Actualizar usuario
PATCH /api/usuarios/usuarios/{id}/
Body: {
  first_name: "María José",
  perfil_odontologo: {
    especialidad: "Endodoncia y Periodoncia"
  }
}

// 4. Desactivar usuario
PATCH /api/usuarios/usuarios/{id}/
Body: {
  is_active: false
}

// 5. Obtener detalle
GET /api/usuarios/usuarios/{id}/
Response: { /* datos completos del usuario */ }

// 6. Estadísticas del odontólogo
GET /api/reportes/reportes/reporte-citas-odontologo/?mes=2025-11
```

---

## 💻 Implementación Frontend

### 1. Página de Gestión de Usuarios

```typescript
// src/pages/admin/Usuarios.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Filter } from 'lucide-react';
import { usuariosService } from '@/services/admin/usuariosService';
import UserTable from '@/components/admin/users/UserTable';
import UserModal from '@/components/admin/users/UserModal';
import FilterPanel from '@/components/admin/FilterPanel';
import { toast } from 'react-hot-toast';

export default function Usuarios() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [filters, setFilters] = useState({
    tipo_usuario: '',
    is_active: 'true',
    search: '',
  });

  // Fetch usuarios
  const { data, isLoading } = useQuery({
    queryKey: ['usuarios', filters],
    queryFn: () => usuariosService.getUsuarios(filters),
  });

  // Crear/Editar usuario
  const mutation = useMutation({
    mutationFn: (userData: any) => 
      selectedUser 
        ? usuariosService.updateUsuario(selectedUser.id, userData)
        : usuariosService.createUsuario(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
      setIsModalOpen(false);
      setSelectedUser(null);
      toast.success(selectedUser ? 'Usuario actualizado' : 'Usuario creado');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al guardar usuario');
    },
  });

  // Desactivar usuario
  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      usuariosService.updateUsuario(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
      toast.success('Estado actualizado');
    },
  });

  const handleEdit = (user: any) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedUser(null);
    setIsModalOpen(true);
  };

  const handleToggleActive = (user: any) => {
    toggleActiveMutation.mutate({
      id: user.id,
      is_active: !user.is_active,
    });
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Equipo de Trabajo</h1>
          <p className="text-gray-600">Gestiona odontólogos, recepcionistas y administradores</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nuevo Usuario
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o email..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Tipo de usuario */}
          <select
            value={filters.tipo_usuario}
            onChange={(e) => setFilters({ ...filters, tipo_usuario: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los tipos</option>
            <option value="ODONTOLOGO">Odontólogos</option>
            <option value="RECEPCIONISTA">Recepcionistas</option>
            <option value="ADMIN">Administradores</option>
          </select>

          {/* Estado */}
          <select
            value={filters.is_active}
            onChange={(e) => setFilters({ ...filters, is_active: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los estados</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </select>

          {/* Limpiar filtros */}
          <button
            onClick={() => setFilters({ tipo_usuario: '', is_active: 'true', search: '' })}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Limpiar Filtros
          </button>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-lg shadow">
        <UserTable
          users={data?.results || []}
          isLoading={isLoading}
          onEdit={handleEdit}
          onToggleActive={handleToggleActive}
        />
      </div>

      {/* Modal */}
      <UserModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedUser(null);
        }}
        user={selectedUser}
        onSubmit={(data) => mutation.mutate(data)}
        isLoading={mutation.isPending}
      />
    </div>
  );
}
```

---

### 2. Componente Tabla de Usuarios

```typescript
// src/components/admin/users/UserTable.tsx
import React from 'react';
import { Edit, Power, Eye, MoreVertical } from 'lucide-react';
import { formatDate } from '@/lib/utils';

interface User {
  id: number;
  full_name: string;
  email: string;
  tipo_usuario: string;
  is_active: boolean;
  date_joined: string;
  perfil_odontologo?: {
    especialidad: string;
  };
}

interface UserTableProps {
  users: User[];
  isLoading: boolean;
  onEdit: (user: User) => void;
  onToggleActive: (user: User) => void;
}

export default function UserTable({ users, isLoading, onEdit, onToggleActive }: UserTableProps) {
  if (isLoading) {
    return <TableSkeleton />;
  }

  if (users.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No se encontraron usuarios</p>
      </div>
    );
  }

  const getRoleBadge = (tipo: string) => {
    const colors = {
      ODONTOLOGO: 'bg-blue-100 text-blue-800',
      RECEPCIONISTA: 'bg-green-100 text-green-800',
      ADMIN: 'bg-purple-100 text-purple-800',
    };
    const labels = {
      ODONTOLOGO: 'Odontólogo',
      RECEPCIONISTA: 'Recepcionista',
      ADMIN: 'Administrador',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[tipo]}`}>
        {labels[tipo]}
      </span>
    );
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Usuario
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Rol
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Especialidad
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Fecha Registro
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-blue-600 font-medium">
                      {user.full_name.charAt(0)}
                    </span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
              <td className="px-6 py-4">{getRoleBadge(user.tipo_usuario)}</td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {user.perfil_odontologo?.especialidad || '-'}
              </td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  user.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {user.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {formatDate(user.date_joined)}
              </td>
              <td className="px-6 py-4 text-right">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onEdit(user)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Editar"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onToggleActive(user)}
                    className={`p-2 rounded-lg ${
                      user.is_active 
                        ? 'text-red-600 hover:bg-red-50' 
                        : 'text-green-600 hover:bg-green-50'
                    }`}
                    title={user.is_active ? 'Desactivar' : 'Activar'}
                  >
                    <Power className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="p-6 space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
      ))}
    </div>
  );
}
```

---

### 3. Modal de Crear/Editar Usuario

```typescript
// src/components/admin/users/UserModal.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X } from 'lucide-react';
import Modal from '@/components/ui/Modal';

const userSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres').optional(),
  first_name: z.string().min(2, 'Requerido'),
  last_name: z.string().min(2, 'Requerido'),
  tipo_usuario: z.enum(['ODONTOLOGO', 'RECEPCIONISTA', 'ADMIN']),
  perfil_odontologo: z.object({
    especialidad: z.string().optional(),
    numero_licencia: z.string().optional(),
    telefono: z.string().optional(),
  }).optional(),
});

type UserFormData = z.infer<typeof userSchema>;

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any | null;
  onSubmit: (data: UserFormData) => void;
  isLoading: boolean;
}

export default function UserModal({ isOpen, onClose, user, onSubmit, isLoading }: UserModalProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: user || {
      tipo_usuario: 'ODONTOLOGO',
    },
  });

  const tipoUsuario = watch('tipo_usuario');
  const isOdontologo = tipoUsuario === 'ODONTOLOGO';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={user ? 'Editar Usuario' : 'Nuevo Usuario'}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Información Básica */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre
            </label>
            <input
              {...register('first_name')}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            {errors.first_name && (
              <p className="text-red-500 text-sm mt-1">{errors.first_name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Apellido
            </label>
            <input
              {...register('last_name')}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            {errors.last_name && (
              <p className="text-red-500 text-sm mt-1">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            {...register('email')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
          )}
        </div>

        {/* Contraseña (solo al crear) */}
        {!user && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              {...register('password')}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>
        )}

        {/* Tipo de Usuario */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Usuario
          </label>
          <select
            {...register('tipo_usuario')}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="ODONTOLOGO">Odontólogo</option>
            <option value="RECEPCIONISTA">Recepcionista</option>
            <option value="ADMIN">Administrador</option>
          </select>
        </div>

        {/* Campos específicos para Odontólogo */}
        {isOdontologo && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Especialidad
              </label>
              <input
                {...register('perfil_odontologo.especialidad')}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Ortodoncia, Endodoncia"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  N° Licencia
                </label>
                <input
                  {...register('perfil_odontologo.numero_licencia')}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Teléfono
                </label>
                <input
                  {...register('perfil_odontologo.telefono')}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </>
        )}

        {/* Botones */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Guardando...' : user ? 'Actualizar' : 'Crear'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
```

---

### 4. Servicio de Usuarios

```typescript
// src/services/admin/usuariosService.ts
import api from '@/lib/axios';

export const usuariosService = {
  // Listar usuarios
  async getUsuarios(filters: any = {}) {
    const params = new URLSearchParams();
    
    if (filters.tipo_usuario) params.append('tipo_usuario', filters.tipo_usuario);
    if (filters.is_active) params.append('is_active', filters.is_active);
    if (filters.search) params.append('search', filters.search);
    
    const { data } = await api.get(`/usuarios/usuarios/?${params.toString()}`);
    return data;
  },

  // Obtener un usuario
  async getUsuario(id: number) {
    const { data } = await api.get(`/usuarios/usuarios/${id}/`);
    return data;
  },

  // Crear usuario
  async createUsuario(userData: any) {
    const { data } = await api.post('/usuarios/usuarios/', userData);
    return data;
  },

  // Actualizar usuario
  async updateUsuario(id: number, userData: any) {
    const { data } = await api.patch(`/usuarios/usuarios/${id}/`, userData);
    return data;
  },

  // Eliminar usuario (soft delete)
  async deleteUsuario(id: number) {
    const { data } = await api.patch(`/usuarios/usuarios/${id}/`, { is_active: false });
    return data;
  },
};
```

---

## ✅ Checklist de Implementación

- [ ] Crear página Usuarios.tsx
- [ ] Crear componente UserTable
- [ ] Crear componente UserModal
- [ ] Crear usuariosService
- [ ] Implementar filtros
- [ ] Implementar búsqueda
- [ ] Implementar paginación
- [ ] Validación de formularios
- [ ] Manejo de errores
- [ ] Estados de carga
- [ ] Confirmar desactivación
- [ ] Vista responsive

---

**Siguiente:** `03_gestion_pacientes.md`
