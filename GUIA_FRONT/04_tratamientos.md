# 🦷 FASE 2C: TRATAMIENTOS - SERVICIOS Y PRESUPUESTOS

## 📋 Endpoints de Tratamientos

### Sistema de servicios dentales y planificación

```javascript
// Endpoints tratamientos
const TREATMENT_ENDPOINTS = {
  // Categorías de servicios
  categories: '/api/tratamientos/categorias/',
  categoryDetail: '/api/tratamientos/categorias/{id}/',
  
  // Servicios
  services: '/api/tratamientos/servicios/',
  serviceDetail: '/api/tratamientos/servicios/{id}/',
  
  // Planes de tratamiento
  plans: '/api/tratamientos/planes/',
  planDetail: '/api/tratamientos/planes/{id}/',
  
  // Items del plan
  planItems: '/api/tratamientos/items/',
  planItemDetail: '/api/tratamientos/items/{id}/',
  
  // Presupuestos
  budgets: '/api/tratamientos/presupuestos/',
  budgetDetail: '/api/tratamientos/presupuestos/{id}/',
  acceptBudget: '/api/tratamientos/presupuestos/{id}/aceptar/{token}/',
  rejectBudget: '/api/tratamientos/presupuestos/{id}/rechazar/'
};
```

## 🔧 1. Servicio de Tratamientos

```javascript
// services/treatmentService.js
import api from './apiConfig';

class TreatmentService {
  // Categorías de servicios
  async getServiceCategories() {
    try {
      const response = await api.get('/api/tratamientos/categorias/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener categorías de servicios' };
    }
  }

  async createServiceCategory(categoryData) {
    try {
      const response = await api.post('/api/tratamientos/categorias/', categoryData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear categoría' };
    }
  }

  // Servicios
  async getServices(page = 1, search = '', category = '') {
    try {
      const params = { 
        page, 
        search: search || undefined,
        categoria: category || undefined
      };
      const response = await api.get('/api/tratamientos/servicios/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener servicios' };
    }
  }

  async getServiceDetail(serviceId) {
    try {
      const response = await api.get(`/api/tratamientos/servicios/${serviceId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener servicio' };
    }
  }

  async createService(serviceData) {
    try {
      const response = await api.post('/api/tratamientos/servicios/', serviceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear servicio' };
    }
  }

  async updateService(serviceId, serviceData) {
    try {
      const response = await api.put(`/api/tratamientos/servicios/${serviceId}/`, serviceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar servicio' };
    }
  }

  // Planes de tratamiento
  async getPlans(page = 1, search = '', paciente = '') {
    try {
      const params = { 
        page, 
        search: search || undefined,
        paciente: paciente || undefined
      };
      const response = await api.get('/api/tratamientos/planes/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener planes' };
    }
  }

  async createPlan(planData) {
    try {
      const response = await api.post('/api/tratamientos/planes/', planData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear plan' };
    }
  }

  async getPlanDetail(planId) {
    try {
      const response = await api.get(`/api/tratamientos/planes/${planId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener plan' };
    }
  }

  // Items del plan
  async createPlanItem(itemData) {
    try {
      const response = await api.post('/api/tratamientos/items/', itemData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al agregar item' };
    }
  }

  async updatePlanItem(itemId, itemData) {
    try {
      const response = await api.put(`/api/tratamientos/items/${itemId}/`, itemData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar item' };
    }
  }

  async deletePlanItem(itemId) {
    try {
      await api.delete(`/api/tratamientos/items/${itemId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar item' };
    }
  }

  // Presupuestos
  async getBudgets(page = 1, search = '', estado = '') {
    try {
      const params = { 
        page, 
        search: search || undefined,
        estado: estado || undefined
      };
      const response = await api.get('/api/tratamientos/presupuestos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener presupuestos' };
    }
  }

  async createBudget(budgetData) {
    try {
      const response = await api.post('/api/tratamientos/presupuestos/', budgetData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear presupuesto' };
    }
  }

  async getBudgetDetail(budgetId) {
    try {
      const response = await api.get(`/api/tratamientos/presupuestos/${budgetId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener presupuesto' };
    }
  }

  async acceptBudget(budgetId, token) {
    try {
      const response = await api.post(`/api/tratamientos/presupuestos/${budgetId}/aceptar/${token}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error al aceptar presupuesto' };
    }
  }

  async rejectBudget(budgetId, motivo = '') {
    try {
      const response = await api.post(`/api/tratamientos/presupuestos/${budgetId}/rechazar/`, {
        motivo
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error al rechazar presupuesto' };
    }
  }
}

export default new TreatmentService();
```

## 📝 2. Hooks de Tratamientos

```javascript
// hooks/useTreatments.js
import { useState, useEffect } from 'react';
import treatmentService from '../services/treatmentService';

export function useServices() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchServices = async (page = 1, search = '', category = '') => {
    setLoading(true);
    const result = await treatmentService.getServices(page, search, category);
    
    if (result.success) {
      setServices(result.data.results || result.data);
      setPagination({
        count: result.data.count,
        next: result.data.next,
        previous: result.data.previous,
        current_page: page
      });
      setError('');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return {
    services,
    loading,
    error,
    pagination,
    fetchServices,
    refetch: () => fetchServices()
  };
}

export function usePlans() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchPlans = async (page = 1, search = '', paciente = '') => {
    setLoading(true);
    const result = await treatmentService.getPlans(page, search, paciente);
    
    if (result.success) {
      setPlans(result.data.results || result.data);
      setPagination({
        count: result.data.count,
        next: result.data.next,
        previous: result.data.previous,
        current_page: page
      });
      setError('');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return {
    plans,
    loading,
    error,
    pagination,
    fetchPlans,
    refetch: () => fetchPlans()
  };
}

export function useBudgets() {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchBudgets = async (page = 1, search = '', estado = '') => {
    setLoading(true);
    const result = await treatmentService.getBudgets(page, search, estado);
    
    if (result.success) {
      setBudgets(result.data.results || result.data);
      setPagination({
        count: result.data.count,
        next: result.data.next,
        previous: result.data.previous,
        current_page: page
      });
      setError('');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return {
    budgets,
    loading,
    error,
    pagination,
    fetchBudgets,
    refetch: () => fetchBudgets()
  };
}
```

## 📋 3. Lista de Servicios

```javascript
// components/ServicesList.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useServices } from '../hooks/useTreatments';
import { useAuth } from '../contexts/AuthContext';

function ServicesList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  
  const { services, loading, error, pagination, fetchServices } = useServices();
  const { user } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchServices(1, searchTerm);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchServices(page, searchTerm);
  };

  React.useEffect(() => {
    fetchServices();
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getDurationText = (duration) => {
    if (duration >= 60) {
      const hours = Math.floor(duration / 60);
      const minutes = duration % 60;
      return `${hours}h ${minutes > 0 ? `${minutes}m` : ''}`;
    }
    return `${duration}m`;
  };

  if (loading && currentPage === 1) {
    return <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Servicios Dentales</h1>
        
        {(user?.tipo_usuario === 'ADMIN' || user?.tipo_usuario === 'ODONTOLOGO') && (
          <div className="flex space-x-2">
            <Link 
              to="/tratamientos/categorias"
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Categorías
            </Link>
            <Link 
              to="/tratamientos/servicios/crear"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Crear Servicio
            </Link>
          </div>
        )}
      </div>

      {/* Búsqueda */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Buscar servicios..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button 
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
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

      {/* Grid de servicios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service) => (
          <div key={service.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                  {service.nombre}
                </h3>
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {service.categoria?.nombre || 'Sin categoría'}
                </span>
              </div>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {service.descripcion}
              </p>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Precio:</span>
                  <span className="font-medium text-green-600">
                    {formatPrice(service.precio_base)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Duración:</span>
                  <span className="font-medium">
                    {getDurationText(service.duracion_estimada)}
                  </span>
                </div>
                {service.requiere_anestesia && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Anestesia:</span>
                    <span className="text-orange-600 text-xs bg-orange-100 px-2 py-0.5 rounded">
                      Requerida
                    </span>
                  </div>
                )}
              </div>
              
              <div className="flex justify-between items-center pt-4 border-t">
                <Link 
                  to={`/tratamientos/servicios/${service.id}`}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Ver detalles
                </Link>
                
                {(user?.tipo_usuario === 'ADMIN' || user?.tipo_usuario === 'ODONTOLOGO') && (
                  <div className="flex space-x-2">
                    <Link 
                      to={`/tratamientos/servicios/${service.id}/editar`}
                      className="text-green-600 hover:text-green-800 text-sm"
                    >
                      Editar
                    </Link>
                    <button className="text-purple-600 hover:text-purple-800 text-sm">
                      Agregar a Plan
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {services.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-4">
            No se encontraron servicios
          </div>
          {(user?.tipo_usuario === 'ADMIN' || user?.tipo_usuario === 'ODONTOLOGO') && (
            <Link 
              to="/tratamientos/servicios/crear"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Crear primer servicio
            </Link>
          )}
        </div>
      )}

      {/* Paginación */}
      {pagination && pagination.count > 9 && (
        <div className="mt-8 flex justify-center">
          <div className="flex space-x-2">
            <button
              disabled={!pagination.previous}
              onClick={() => handlePageChange(currentPage - 1)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <span className="px-4 py-2 text-sm text-gray-700">
              Página {pagination.current_page}
            </span>
            <button
              disabled={!pagination.next}
              onClick={() => handlePageChange(currentPage + 1)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ServicesList;
```

## 📋 4. Lista de Presupuestos

```javascript
// components/BudgetsList.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useBudgets } from '../hooks/useTreatments';
import treatmentService from '../services/treatmentService';

function BudgetsList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  
  const { budgets, loading, error, pagination, fetchBudgets } = useBudgets();

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchBudgets(1, searchTerm, statusFilter);
  };

  const handleStatusChange = (newStatus) => {
    setStatusFilter(newStatus);
    setCurrentPage(1);
    fetchBudgets(1, searchTerm, newStatus);
  };

  const handleAccept = async (budgetId, token) => {
    if (window.confirm('¿Está seguro de aceptar este presupuesto?')) {
      const result = await treatmentService.acceptBudget(budgetId, token);
      if (result.success) {
        fetchBudgets(currentPage, searchTerm, statusFilter);
      } else {
        alert('Error al aceptar presupuesto: ' + result.error);
      }
    }
  };

  const handleReject = async (budgetId) => {
    const motivo = prompt('Ingrese el motivo del rechazo:');
    if (motivo !== null) {
      const result = await treatmentService.rejectBudget(budgetId, motivo);
      if (result.success) {
        fetchBudgets(currentPage, searchTerm, statusFilter);
      } else {
        alert('Error al rechazar presupuesto: ' + result.error);
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDIENTE': 'bg-yellow-100 text-yellow-800',
      'ACEPTADO': 'bg-green-100 text-green-800',
      'RECHAZADO': 'bg-red-100 text-red-800',
      'VENCIDO': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 0
    }).format(price);
  };

  React.useEffect(() => {
    fetchBudgets();
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Presupuestos</h1>
        <Link 
          to="/tratamientos/presupuestos/crear"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Crear Presupuesto
        </Link>
      </div>

      {/* Filtros */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <form onSubmit={handleSearch} className="flex gap-4">
          <input
            type="text"
            placeholder="Buscar por paciente..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg"
            value={statusFilter}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendientes</option>
            <option value="ACEPTADO">Aceptados</option>
            <option value="RECHAZADO">Rechazados</option>
            <option value="VENCIDO">Vencidos</option>
          </select>
          
          <button 
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Filtrar
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Lista de presupuestos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Paciente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Plan de Tratamiento
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Total
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fecha
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {budgets.map((budget) => (
              <tr key={budget.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">
                    {budget.plan_tratamiento?.paciente_nombre || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {budget.plan_tratamiento?.paciente_email || ''}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">
                    {budget.plan_tratamiento?.nombre || 'Plan sin nombre'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {budget.plan_tratamiento?.items_count || 0} servicios
                  </div>
                </td>
                <td className="px-6 py-4 text-sm font-medium text-green-600">
                  {formatPrice(budget.total)}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(budget.estado)}`}>
                    {budget.estado}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {new Date(budget.fecha_creacion).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-sm font-medium">
                  <div className="flex space-x-2">
                    <Link 
                      to={`/tratamientos/presupuestos/${budget.id}`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Ver
                    </Link>
                    
                    {budget.estado === 'PENDIENTE' && (
                      <>
                        <button 
                          onClick={() => handleAccept(budget.id, budget.token_aceptacion)}
                          className="text-green-600 hover:text-green-900"
                        >
                          Aceptar
                        </button>
                        <button 
                          onClick={() => handleReject(budget.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Rechazar
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default BudgetsList;
```

## ✅ Próximos Pasos

1. Implementar formularios de servicios y planes
2. Agregar creación de presupuestos
3. Continuar con **05_agenda_citas.md**

---
**Endpoints implementados**: ✅ CRUD Servicios ✅ CRUD Planes ✅ CRUD Presupuestos ✅ Aprobación