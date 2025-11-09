# 📦 FASE 2B: INVENTARIO - CATEGORÍAS E INSUMOS

## 📋 Endpoints de Inventario

### Módulo fundamental para operaciones clínicas

```javascript
// Endpoints inventario
const INVENTORY_ENDPOINTS = {
  // Categorías
  categories: '/api/inventario/categorias/',
  categoryDetail: '/api/inventario/categorias/{id}/',
  
  // Insumos
  supplies: '/api/inventario/insumos/',
  supplyDetail: '/api/inventario/insumos/{id}/',
  lowStock: '/api/inventario/insumos/bajo_stock/',
  adjustStock: '/api/inventario/insumos/{id}/ajustar_stock/'
};
```

## 🔧 1. Servicio de Inventario

```javascript
// services/inventoryService.js
import api from './apiConfig';

class InventoryService {
  // Categorías
  async getCategories() {
    try {
      const response = await api.get('/api/inventario/categorias/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener categorías' };
    }
  }

  async createCategory(categoryData) {
    try {
      const response = await api.post('/api/inventario/categorias/', categoryData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear categoría' };
    }
  }

  async updateCategory(categoryId, categoryData) {
    try {
      const response = await api.put(`/api/inventario/categorias/${categoryId}/`, categoryData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar categoría' };
    }
  }

  async deleteCategory(categoryId) {
    try {
      await api.delete(`/api/inventario/categorias/${categoryId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar categoría' };
    }
  }

  // Insumos
  async getSupplies(page = 1, search = '', category = '') {
    try {
      const params = { 
        page, 
        search: search || undefined,
        categoria: category || undefined
      };
      const response = await api.get('/api/inventario/insumos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener insumos' };
    }
  }

  async getSupplyDetail(supplyId) {
    try {
      const response = await api.get(`/api/inventario/insumos/${supplyId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener insumo' };
    }
  }

  async createSupply(supplyData) {
    try {
      const response = await api.post('/api/inventario/insumos/', supplyData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al crear insumo' };
    }
  }

  async updateSupply(supplyId, supplyData) {
    try {
      const response = await api.put(`/api/inventario/insumos/${supplyId}/`, supplyData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data || 'Error al actualizar insumo' };
    }
  }

  async deleteSupply(supplyId) {
    try {
      await api.delete(`/api/inventario/insumos/${supplyId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar insumo' };
    }
  }

  async adjustStock(supplyId, adjustmentData) {
    try {
      const response = await api.post(`/api/inventario/insumos/${supplyId}/ajustar_stock/`, adjustmentData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error al ajustar stock' };
    }
  }

  async getLowStockSupplies() {
    try {
      const response = await api.get('/api/inventario/insumos/bajo_stock/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener insumos con stock bajo' };
    }
  }
}

export default new InventoryService();
```

## 📝 2. Hooks Personalizados

```javascript
// hooks/useInventory.js
import { useState, useEffect } from 'react';
import inventoryService from '../services/inventoryService';

export function useCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchCategories = async () => {
    setLoading(true);
    const result = await inventoryService.getCategories();
    
    if (result.success) {
      setCategories(result.data);
      setError('');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const createCategory = async (categoryData) => {
    const result = await inventoryService.createCategory(categoryData);
    if (result.success) {
      await fetchCategories(); // Refrescar lista
    }
    return result;
  };

  const updateCategory = async (categoryId, categoryData) => {
    const result = await inventoryService.updateCategory(categoryId, categoryData);
    if (result.success) {
      await fetchCategories();
    }
    return result;
  };

  const deleteCategory = async (categoryId) => {
    const result = await inventoryService.deleteCategory(categoryId);
    if (result.success) {
      await fetchCategories();
    }
    return result;
  };

  return {
    categories,
    loading,
    error,
    createCategory,
    updateCategory,
    deleteCategory,
    refetch: fetchCategories
  };
}

export function useSupplies() {
  const [supplies, setSupplies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchSupplies = async (page = 1, search = '', category = '') => {
    setLoading(true);
    const result = await inventoryService.getSupplies(page, search, category);
    
    if (result.success) {
      setSupplies(result.data.results || result.data);
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
    supplies,
    loading,
    error,
    pagination,
    fetchSupplies,
    refetch: () => fetchSupplies()
  };
}
```

## 📋 3. Componente Lista de Insumos

```javascript
// components/SuppliesList.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useSupplies, useCategories } from '../hooks/useInventory';
import inventoryService from '../services/inventoryService';

function SuppliesList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  
  const { supplies, loading, error, pagination, fetchSupplies } = useSupplies();
  const { categories } = useCategories();

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchSupplies(1, searchTerm, selectedCategory);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchSupplies(page, searchTerm, selectedCategory);
  };

  const getStockStatusColor = (stock, minStock) => {
    if (stock <= 0) return 'text-red-600 bg-red-100';
    if (stock <= minStock) return 'text-orange-600 bg-orange-100';
    return 'text-green-600 bg-green-100';
  };

  const getStockStatusText = (stock, minStock) => {
    if (stock <= 0) return 'Sin Stock';
    if (stock <= minStock) return 'Stock Bajo';
    return 'Disponible';
  };

  React.useEffect(() => {
    fetchSupplies();
  }, []);

  if (loading && currentPage === 1) {
    return <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gestión de Inventario</h1>
        
        <div className="flex space-x-2">
          <Link 
            to="/inventario/categorias"
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
          >
            Categorías
          </Link>
          <Link 
            to="/inventario/insumos/crear"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Crear Insumo
          </Link>
        </div>
      </div>

      {/* Filtros */}
      <form onSubmit={handleSearch} className="mb-6 bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
            <input
              type="text"
              placeholder="Nombre del insumo..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
            <select
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Todas las categorías</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.nombre}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button 
              type="submit"
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Filtrar
            </button>
          </div>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Tabla de insumos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Insumo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Categoría
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Stock
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {supplies.map((supply) => (
              <tr key={supply.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="font-medium text-gray-900">{supply.nombre}</div>
                    <div className="text-sm text-gray-500">{supply.descripcion}</div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {supply.categoria?.nombre || 'Sin categoría'}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-medium">{supply.stock_actual} {supply.unidad_medida}</div>
                    <div className="text-gray-500">Min: {supply.stock_minimo}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    getStockStatusColor(supply.stock_actual, supply.stock_minimo)
                  }`}>
                    {getStockStatusText(supply.stock_actual, supply.stock_minimo)}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-medium space-x-2">
                  <Link 
                    to={`/inventario/insumos/${supply.id}`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Ver
                  </Link>
                  <Link 
                    to={`/inventario/insumos/${supply.id}/editar`}
                    className="text-green-600 hover:text-green-900"
                  >
                    Editar
                  </Link>
                  <button 
                    onClick={() => openStockModal(supply)}
                    className="text-purple-600 hover:text-purple-900"
                  >
                    Ajustar Stock
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Paginación */}
        {pagination && pagination.count > 10 && (
          <div className="bg-white px-6 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Mostrando página {pagination.current_page} - Total: {pagination.count} insumos
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

export default SuppliesList;
```

## ⚙️ 4. Modal de Ajuste de Stock

```javascript
// components/StockAdjustmentModal.jsx
import React, { useState } from 'react';
import inventoryService from '../services/inventoryService';

function StockAdjustmentModal({ supply, isOpen, onClose, onSuccess }) {
  const [adjustment, setAdjustment] = useState({
    cantidad: '',
    motivo: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    const result = await inventoryService.adjustStock(supply.id, adjustment);
    
    if (result.success) {
      onSuccess();
      onClose();
      setAdjustment({ cantidad: '', motivo: '' });
    } else {
      setError(result.error);
    }
    setIsSubmitting(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-medium mb-4">
          Ajustar Stock - {supply?.nombre}
        </h3>

        <div className="mb-4 p-3 bg-gray-100 rounded">
          <p className="text-sm text-gray-600">
            Stock actual: <span className="font-medium">{supply?.stock_actual} {supply?.unidad_medida}</span>
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cantidad a ajustar *
            </label>
            <input
              type="number"
              step="0.01"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={adjustment.cantidad}
              onChange={(e) => setAdjustment({...adjustment, cantidad: e.target.value})}
              placeholder="Positivo para aumentar, negativo para reducir"
            />
            <p className="text-xs text-gray-500 mt-1">
              Ejemplo: +10 para agregar, -5 para quitar
            </p>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motivo
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows="3"
              value={adjustment.motivo}
              onChange={(e) => setAdjustment({...adjustment, motivo: e.target.value})}
              placeholder="Ej: Compra, uso en procedimiento, pérdida..."
            />
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Ajustando...' : 'Ajustar Stock'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default StockAdjustmentModal;
```

## ✅ Próximos Pasos

1. Implementar formulario de insumos
2. Agregar gestión de categorías
3. Continuar con **04_tratamientos.md**

---
**Endpoints implementados**: ✅ CRUD Categorías ✅ CRUD Insumos ✅ Ajuste Stock ✅ Stock Bajo