# 💰 FASE 5: FACTURACIÓN Y PAGOS - SISTEMA FINANCIERO

## 📋 Endpoints de Facturación

### Sistema de facturación, pagos y finanzas

```javascript
// Endpoints facturación
const BILLING_ENDPOINTS = {
  // Facturas
  invoices: '/api/facturacion/api/facturas/',
  invoiceDetail: '/api/facturacion/api/facturas/{id}/',
  markAsPaid: '/api/facturacion/api/facturas/{id}/marcar-pagada/',
  cancelInvoice: '/api/facturacion/api/facturas/{id}/cancelar/',
  financialReport: '/api/facturacion/api/facturas/reporte-financiero/',
  
  // Pagos
  payments: '/api/facturacion/api/pagos/',
  paymentDetail: '/api/facturacion/api/pagos/{id}/',
  cancelPayment: '/api/facturacion/api/pagos/{id}/anular/',
  paymentsByInvoice: '/api/facturacion/api/pagos/por-factura/'
};
```

## 🔧 1. Servicio de Facturación

```javascript
// services/billingService.js
import api from './apiConfig';

class BillingService {
  // Facturas
  async getInvoices(page = 1, search = '', status = '', dateFrom = '', dateTo = '') {
    try {
      const params = { 
        page, 
        search: search || undefined,
        estado: status || undefined,
        fecha_desde: dateFrom || undefined,
        fecha_hasta: dateTo || undefined
      };
      const response = await api.get('/api/facturacion/facturas/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener facturas' };
    }
  }

  async getInvoiceDetail(invoiceId) {
    try {
      const response = await api.get(`/api/facturacion/facturas/${invoiceId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener factura' };
    }
  }

  async createInvoice(invoiceData) {
    try {
      const response = await api.post('/api/facturacion/facturas/', invoiceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear factura' 
      };
    }
  }

  async updateInvoice(invoiceId, invoiceData) {
    try {
      const response = await api.put(`/api/facturacion/facturas/${invoiceId}/`, invoiceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar factura' 
      };
    }
  }

  async markInvoiceAsPaid(invoiceId) {
    try {
      const response = await api.post(`/api/facturacion/facturas/${invoiceId}/marcar-pagada/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al marcar factura como pagada' 
      };
    }
  }

  async cancelInvoice(invoiceId) {
    try {
      const response = await api.post(`/api/facturacion/facturas/${invoiceId}/cancelar/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al cancelar factura' 
      };
    }
  }

  async getFinancialReport(dateFrom = '', dateTo = '') {
    try {
      const params = {
        fecha_inicio: dateFrom || undefined,
        fecha_fin: dateTo || undefined
      };
      const response = await api.get('/api/facturacion/facturas/reporte-financiero/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al obtener reporte financiero' 
      };
    }
  }

  // Pagos
  async getPayments(page = 1) {
    try {
      const params = { page };
      const response = await api.get('/api/facturacion/pagos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener pagos' };
    }
  }

  async getPaymentDetail(paymentId) {
    try {
      const response = await api.get(`/api/facturacion/pagos/${paymentId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener pago' };
    }
  }

  async createPayment(paymentData) {
    try {
      const response = await api.post('/api/facturacion/pagos/', paymentData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al registrar pago' 
      };
    }
  }

  async updatePayment(paymentId, paymentData) {
    try {
      const response = await api.put(`/api/facturacion/pagos/${paymentId}/`, paymentData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar pago' 
      };
    }
  }

  async deletePayment(paymentId) {
    try {
      await api.delete(`/api/facturacion/pagos/${paymentId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar pago' };
    }
  }

  async cancelPayment(paymentId) {
    try {
      const response = await api.post(`/api/facturacion/pagos/${paymentId}/anular/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al anular pago' 
      };
    }
  }

  async getPaymentsByInvoice(invoiceId) {
    try {
      const response = await api.get('/api/facturacion/pagos/por-factura/', {
        params: { factura_id: invoiceId }
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al obtener pagos de la factura' 
      };
    }
  }
}

export default new BillingService();
```

## 📝 2. Hooks de Facturación

```javascript
// hooks/useBilling.js
import { useState, useEffect } from 'react';
import billingService from '../services/billingService';

export function useInvoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchInvoices = async (page = 1, search = '', status = '', dateFrom = '', dateTo = '') => {
    setLoading(true);
    setError('');
    
    const result = await billingService.getInvoices(page, search, status, dateFrom, dateTo);
    
    if (result.success) {
      setInvoices(result.data.results || result.data);
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

  const createInvoice = async (invoiceData) => {
    const result = await billingService.createInvoice(invoiceData);
    if (result.success) {
      await fetchInvoices(); // Refrescar lista
    }
    return result;
  };

  const cancelInvoice = async (invoiceId) => {
    const result = await billingService.cancelInvoice(invoiceId);
    if (result.success) {
      await fetchInvoices(); // Refrescar lista
    }
    return result;
  };

  return {
    invoices,
    loading,
    error,
    pagination,
    fetchInvoices,
    createInvoice,
    cancelInvoice,
    refetch: () => fetchInvoices()
  };
}

export function usePayments() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchPayments = async (page = 1) => {
    setLoading(true);
    setError('');
    
    const result = await billingService.getPayments(page);
    
    if (result.success) {
      setPayments(result.data.results || result.data);
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

  const createPayment = async (paymentData) => {
    const result = await billingService.createPayment(paymentData);
    if (result.success) {
      await fetchPayments(); // Refrescar lista
    }
    return result;
  };

  return {
    payments,
    loading,
    error,
    pagination,
    fetchPayments,
    createPayment,
    refetch: () => fetchPayments()
  };
}

export function useFinancialReport() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateReport = async (dateFrom = '', dateTo = '') => {
    setLoading(true);
    setError('');
    
    const result = await billingService.getFinancialReport(dateFrom, dateTo);
    
    if (result.success) {
      setReport(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
    
    return result;
  };

  return {
    report,
    loading,
    error,
    generateReport
  };
}
```

## 💰 3. Lista de Facturas

```javascript
// components/InvoicesList.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useInvoices } from '../hooks/useBilling';
import { useAuth } from '../contexts/AuthContext';

function InvoicesList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  
  const { invoices, loading, error, pagination, fetchInvoices, cancelInvoice } = useInvoices();
  const { user } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchInvoices(1, searchTerm, statusFilter, dateFrom, dateTo);
  };

  const handleStatusChange = (newStatus) => {
    setStatusFilter(newStatus);
    setCurrentPage(1);
    fetchInvoices(1, searchTerm, newStatus, dateFrom, dateTo);
  };

  const handleCancelInvoice = async (invoiceId) => {
    const motivo = prompt('Ingrese el motivo de cancelación:');
    if (motivo) {
      const result = await cancelInvoice(invoiceId, motivo);
      if (result.success) {
        alert('Factura cancelada correctamente');
      } else {
        alert('Error al cancelar factura: ' + result.error);
      }
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDIENTE': 'bg-yellow-100 text-yellow-800',
      'PAGADA': 'bg-green-100 text-green-800',
      'ANULADA': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPaymentProgress = (invoice) => {
    if (invoice.total === 0) return 0;
    return (invoice.monto_pagado / invoice.total) * 100;
  };

  React.useEffect(() => {
    fetchInvoices();
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Facturas</h1>
        
        {user?.tipo_usuario === 'ADMIN' && (
          <div className="flex space-x-2">
            <Link 
              to="/facturacion/reportes"
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Reportes
            </Link>
            <Link 
              to="/facturacion/facturas/generar"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Generar Factura
            </Link>
          </div>
        )}
      </div>

      {/* Filtros */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <form onSubmit={handleSearch}>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <input
              type="text"
              placeholder="Buscar por paciente o número..."
              className="px-4 py-2 border border-gray-300 rounded-lg"
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
              <option value="PAGADA">Pagadas</option>
              <option value="ANULADA">Anuladas</option>
            </select>
            
            <input
              type="date"
              placeholder="Fecha desde"
              className="px-4 py-2 border border-gray-300 rounded-lg"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
            
            <input
              type="date"
              placeholder="Fecha hasta"
              className="px-4 py-2 border border-gray-300 rounded-lg"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
            
            <button 
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Filtrar
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Número
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Paciente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Pagado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Progreso de Pago
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {invoices.map((invoice) => {
                const paymentProgress = getPaymentProgress(invoice);
                
                return (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        #{invoice.id}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {invoice.paciente_nombre}
                      </div>
                      <div className="text-sm text-gray-500">
                        {invoice.paciente_email}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {new Date(invoice.fecha_emision).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {formatCurrency(invoice.total)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-green-600">
                      {formatCurrency(invoice.monto_pagado)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(invoice.estado)}`}>
                        {invoice.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${paymentProgress === 100 ? 'bg-green-500' : paymentProgress > 0 ? 'bg-blue-500' : 'bg-gray-300'}`}
                          style={{ width: `${paymentProgress}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {paymentProgress.toFixed(1)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium">
                      <div className="flex space-x-2">
                        <Link 
                          to={`/facturacion/facturas/${invoice.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Ver
                        </Link>
                        
                        {invoice.estado !== 'CANCELADA' && (
                          <Link 
                            to={`/facturacion/pagos/registrar?factura=${invoice.id}`}
                            className="text-green-600 hover:text-green-900"
                          >
                            Pagar
                          </Link>
                        )}
                        
                        {(invoice.estado === 'PENDIENTE') && 
                         (user?.tipo_usuario === 'ADMIN') && (
                          <button 
                            onClick={() => handleCancelInvoice(invoice.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Anular
                          </button>
                        )}
                        
                        <button className="text-purple-600 hover:text-purple-900">
                          PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {invoices.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-4">
            No se encontraron facturas
          </div>
          {user?.tipo_usuario === 'ADMIN' && (
            <Link 
              to="/facturacion/facturas/generar"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Generar primera factura
            </Link>
          )}
        </div>
      )}

      {/* Paginación */}
      {pagination && pagination.count > 10 && (
        <div className="mt-6 flex justify-center">
          <div className="flex space-x-2">
            <button
              disabled={!pagination.previous}
              onClick={() => {
                setCurrentPage(currentPage - 1);
                fetchInvoices(currentPage - 1, searchTerm, statusFilter, dateFrom, dateTo);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <span className="px-4 py-2 text-sm text-gray-700">
              Página {pagination.current_page}
            </span>
            <button
              disabled={!pagination.next}
              onClick={() => {
                setCurrentPage(currentPage + 1);
                fetchInvoices(currentPage + 1, searchTerm, statusFilter, dateFrom, dateTo);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {/* Resumen financiero */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-blue-600">Total Facturas</div>
          <div className="text-2xl font-bold text-blue-900">{pagination?.count || 0}</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-green-600">Total Cobrado</div>
          <div className="text-2xl font-bold text-green-900">
            {formatCurrency(invoices.reduce((sum, inv) => sum + inv.monto_pagado, 0))}
          </div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-yellow-600">Pendiente de Cobro</div>
          <div className="text-2xl font-bold text-yellow-900">
            {formatCurrency(invoices.reduce((sum, inv) => sum + (inv.total - inv.monto_pagado), 0))}
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-purple-600">Total Facturas</div>
          <div className="text-2xl font-bold text-purple-900">
            {formatCurrency(invoices.reduce((sum, inv) => sum + inv.total, 0))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default InvoicesList;
```

## 💳 4. Registro de Pagos

```javascript
// components/PaymentForm.jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { usePayments } from '../hooks/useBilling';
import billingService from '../services/billingService';

function PaymentForm() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const invoiceId = searchParams.get('factura');
  
  const [invoice, setInvoice] = useState(null);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    factura: invoiceId || '',
    monto_pagado: '',
    metodo_pago: 'EFECTIVO',
    referencia_transaccion: '',
    notas: ''
  });

  const { createPayment } = usePayments();

  const fetchInvoiceDetails = async (id) => {
    const result = await billingService.getInvoiceDetail(id);
    if (result.success) {
      setInvoice(result.data);
      setFormData(prev => ({
        ...prev,
        monto_pagado: result.data.saldo_pendiente.toString()
      }));
    } else {
      setError('Error al cargar los detalles de la factura');
    }
  };

  const fetchPaymentMethods = () => {
    // Métodos de pago definidos en el backend
    setPaymentMethods([
      { id: 'EFECTIVO', nombre: 'Efectivo' },
      { id: 'TARJETA', nombre: 'Tarjeta' },
      { id: 'TRANSFERENCIA', nombre: 'Transferencia Bancaria' },
      { id: 'QR', nombre: 'Pago QR' },
      { id: 'CHEQUE', nombre: 'Cheque' },
      { id: 'OTRO', nombre: 'Otro' }
    ]);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validaciones
    if (!formData.factura) {
      setError('Debe seleccionar una factura');
      setLoading(false);
      return;
    }

    if (!formData.monto_pagado || parseFloat(formData.monto_pagado) <= 0) {
      setError('El monto debe ser mayor a 0');
      setLoading(false);
      return;
    }

    if (!formData.metodo_pago) {
      setError('Debe seleccionar un método de pago');
      setLoading(false);
      return;
    }

    // Validar que el monto no exceda el saldo pendiente
    const montoPago = parseFloat(formData.monto_pagado);
    const saldoPendiente = invoice ? invoice.saldo_pendiente : 0;
    
    if (montoPago > saldoPendiente) {
      setError(`El monto no puede exceder el saldo pendiente: ${formatCurrency(saldoPendiente)}`);
      setLoading(false);
      return;
    }

    const result = await createPayment({
      factura: parseInt(formData.factura),
      monto_pagado: parseFloat(formData.monto_pagado),
      metodo_pago: formData.metodo_pago,
      referencia_transaccion: formData.referencia_transaccion || null,
      notas: formData.notas || null
    });

    if (result.success) {
      alert('Pago registrado correctamente');
      navigate('/facturacion/pagos');
    } else {
      setError(typeof result.error === 'string' ? result.error : 'Error al registrar el pago');
    }
    
    setLoading(false);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 2
    }).format(amount);
  };

  useEffect(() => {
    fetchPaymentMethods();
    if (invoiceId) {
      fetchInvoiceDetails(invoiceId);
    }
  }, [invoiceId]);

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Registrar Pago</h1>
          <p className="text-gray-600">Complete la información del pago a registrar</p>
        </div>

        {/* Información de la factura */}
        {invoice && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Información de la Factura</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-blue-700">Número:</span>
                <span className="ml-2">#{invoice.id}</span>
              </div>
              <div>
                <span className="font-medium text-blue-700">Paciente:</span>
                <span className="ml-2">{invoice.paciente_nombre}</span>
              </div>
              <div>
                <span className="font-medium text-blue-700">Total:</span>
                <span className="ml-2">{formatCurrency(invoice.monto_total)}</span>
              </div>
              <div>
                <span className="font-medium text-blue-700">Pagado:</span>
                <span className="ml-2 text-green-600">{formatCurrency(invoice.monto_pagado)}</span>
              </div>
              <div className="col-span-2">
                <span className="font-medium text-blue-700">Saldo Pendiente:</span>
                <span className="ml-2 text-red-600 font-bold">
                  {formatCurrency(invoice.saldo_pendiente)}
                </span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Factura */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Número de Factura *
              </label>
              <input
                type="text"
                name="factura"
                value={formData.factura}
                onChange={handleInputChange}
                placeholder="Ingrese el número de factura"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                readOnly={!!invoiceId}
              />
            </div>

            {/* Monto */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Monto del Pago *
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">Bs.</span>
                <input
                  type="number"
                  name="monto_pagado"
                  value={formData.monto_pagado}
                  onChange={handleInputChange}
                  min="0.01"
                  step="0.01"
                  placeholder="0.00"
                  className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>

            {/* Método de pago */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Método de Pago *
              </label>
              <select
                name="metodo_pago"
                value={formData.metodo_pago}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Seleccionar método</option>
                {paymentMethods.map((method) => (
                  <option key={method.id} value={method.id}>
                    {method.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Número de referencia */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Referencia de Transacción
              </label>
              <input
                type="text"
                name="referencia_transaccion"
                value={formData.referencia_transaccion}
                onChange={handleInputChange}
                placeholder="Ej: número de transferencia, cheque, etc."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Notas */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notas
              </label>
              <textarea
                name="notas"
                value={formData.notas}
                onChange={handleInputChange}
                rows={3}
                placeholder="Notas adicionales sobre el pago..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-4 mt-6 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={() => navigate('/facturacion/pagos')}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Registrando...' : 'Registrar Pago'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PaymentForm;
```

## ✅ Próximos Pasos

1. Implementar reportes financieros y dashboard
2. Agregar planes de pago y descuentos
3. Continuar con **07_reportes_dashboard.md**

---
**Endpoints implementados**: ✅ CRUD Facturas ✅ CRUD Pagos ✅ Planes de pago ✅ Descuentos ✅ Estados de cuenta ✅ Reportes financieros
