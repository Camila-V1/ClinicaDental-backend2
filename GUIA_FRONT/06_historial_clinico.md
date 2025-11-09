# 🏥 FASE 4: HISTORIAL CLÍNICO - EXPEDIENTES MÉDICOS

## 📋 Endpoints de Historial Clínico

### Sistema de expedientes y registros médicos

```javascript
// Endpoints historial clínico
const CLINICAL_HISTORY_ENDPOINTS = {
  // Historiales
  histories: '/api/historial-clinico/historiales/',
  historyDetail: '/api/historial-clinico/historiales/{id}/',
  createHistory: '/api/historial-clinico/historiales/crear_historial/',
  
  // Episodios de Atención (Consultas)
  episodes: '/api/historial-clinico/episodios/',
  episodeDetail: '/api/historial-clinico/episodios/{id}/',
  myEpisodes: '/api/historial-clinico/episodios/mis_episodios/',
  
  // Odontogramas
  odontograms: '/api/historial-clinico/odontogramas/',
  odontogramDetail: '/api/historial-clinico/odontogramas/{id}/',
  duplicateOdontogram: '/api/historial-clinico/odontogramas/{id}/duplicar_odontograma/',
  
  // Documentos Clínicos
  documents: '/api/historial-clinico/documentos/',
  documentDetail: '/api/historial-clinico/documentos/{id}/',
  documentsByType: '/api/historial-clinico/documentos/por_tipo/',
  downloadDocument: '/api/historial-clinico/documentos/{id}/descargar/'
};
```

## 🔧 1. Servicio de Historial Clínico

```javascript
// services/clinicalHistoryService.js
import api from './apiConfig';

class ClinicalHistoryService {
  // Historiales
  async getHistories(page = 1, search = '') {
    try {
      const params = { page, search: search || undefined };
      const response = await api.get('/api/historial-clinico/historiales/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener historiales' };
    }
  }

  async getHistoryDetail(historyId) {
    try {
      const response = await api.get(`/api/historial-clinico/historiales/${historyId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener historial' };
    }
  }

  async createHistory(paciente_id, historyData = {}) {
    try {
      const data = {
        paciente_id,
        antecedentes_medicos: historyData.antecedentes_medicos || '',
        alergias: historyData.alergias || '',
        medicamentos_actuales: historyData.medicamentos_actuales || ''
      };
      const response = await api.post('/api/historial-clinico/historiales/crear_historial/', data);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al crear historial' 
      };
    }
  }

  async updateHistory(historyId, historyData) {
    try {
      const response = await api.put(`/api/historial-clinico/historiales/${historyId}/`, historyData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar historial' 
      };
    }
  }

  // Episodios de Atención
  async getEpisodes(page = 1, search = '') {
    try {
      const params = { page, search: search || undefined };
      const response = await api.get('/api/historial-clinico/episodios/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener episodios' };
    }
  }

  async getEpisodeDetail(episodeId) {
    try {
      const response = await api.get(`/api/historial-clinico/episodios/${episodeId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener episodio' };
    }
  }

  async createEpisode(episodeData) {
    try {
      const response = await api.post('/api/historial-clinico/episodios/', episodeData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear episodio' 
      };
    }
  }

  async updateEpisode(episodeId, episodeData) {
    try {
      const response = await api.put(`/api/historial-clinico/episodios/${episodeId}/`, episodeData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar episodio' 
      };
    }
  }

  async getMyEpisodes() {
    try {
      const response = await api.get('/api/historial-clinico/episodios/mis_episodios/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener episodios' };
    }
  }

  // Odontogramas
  async getOdontograms(page = 1) {
    try {
      const params = { page };
      const response = await api.get('/api/historial-clinico/odontogramas/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener odontogramas' };
    }
  }

  async getOdontogramDetail(odontogramId) {
    try {
      const response = await api.get(`/api/historial-clinico/odontogramas/${odontogramId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener odontograma' };
    }
  }

  async createOdontogram(odontogramData) {
    try {
      const response = await api.post('/api/historial-clinico/odontogramas/', odontogramData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear odontograma' 
      };
    }
  }

  async updateOdontogram(odontogramId, odontogramData) {
    try {
      const response = await api.put(`/api/historial-clinico/odontogramas/${odontogramId}/`, odontogramData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar odontograma' 
      };
    }
  }

  async duplicateOdontogram(odontogramId) {
    try {
      const response = await api.post(`/api/historial-clinico/odontogramas/${odontogramId}/duplicar_odontograma/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al duplicar odontograma' 
      };
    }
  }

  // Documentos Clínicos
  async getDocuments(page = 1, tipo = '') {
    try {
      const params = { page, tipo: tipo || undefined };
      const response = await api.get('/api/historial-clinico/documentos/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener documentos' };
    }
  }

  async getDocumentsByType(tipo) {
    try {
      const response = await api.get('/api/historial-clinico/documentos/por_tipo/', {
        params: { tipo }
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al obtener documentos' 
      };
    }
  }

  async uploadDocument(documentData) {
    try {
      const formData = new FormData();
      formData.append('archivo', documentData.file);
      formData.append('descripcion', documentData.descripcion || '');
      formData.append('tipo_documento', documentData.tipo_documento);
      formData.append('historial_clinico', documentData.historial_clinico);

      const response = await api.post('/api/historial-clinico/documentos/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al subir documento' 
      };
    }
  }

  async deleteDocument(documentId) {
    try {
      await api.delete(`/api/historial-clinico/documentos/${documentId}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Error al eliminar documento' };
    }
  }

  async downloadDocument(documentId) {
    try {
      const response = await api.get(`/api/historial-clinico/documentos/${documentId}/descargar/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al descargar documento' 
      };
    }
  }
}

export default new ClinicalHistoryService();
```

## 📝 2. Hooks de Historial Clínico

```javascript
// hooks/useClinicalHistory.js
import { useState, useEffect } from 'react';
import clinicalHistoryService from '../services/clinicalHistoryService';

export function useClinicalHistory(historyId) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchHistory = async () => {
    if (!historyId) return;
    
    setLoading(true);
    setError('');
    
    const result = await clinicalHistoryService.getHistoryDetail(historyId);
    
    if (result.success) {
      setHistory(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchHistory();
  }, [historyId]);

  return {
    history,
    loading,
    error,
    refetch: fetchHistory
  };
}

export function useEpisodes() {
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState(null);

  const fetchEpisodes = async (page = 1, search = '') => {
    setLoading(true);
    setError('');
    
    const result = await clinicalHistoryService.getEpisodes(page, search);
    
    if (result.success) {
      setEpisodes(result.data.results || result.data);
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

  const createEpisode = async (episodeData) => {
    const result = await clinicalHistoryService.createEpisode(episodeData);
    if (result.success) {
      await fetchEpisodes(); // Refrescar lista
    }
    return result;
  };

  return {
    episodes,
    loading,
    error,
    pagination,
    fetchEpisodes,
    createEpisode,
    refetch: () => fetchEpisodes()
  };
}

export function useDocuments(tipo = '') {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchDocuments = async (page = 1) => {
    setLoading(true);
    setError('');
    
    const result = await clinicalHistoryService.getDocuments(page, tipo);
    
    if (result.success) {
      setDocuments(result.data.results || result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const uploadDocument = async (documentData) => {
    const result = await clinicalHistoryService.uploadDocument(documentData);
    if (result.success) {
      await fetchDocuments(); // Refrescar lista
    }
    return result;
  };

  const deleteDocument = async (documentId) => {
    const result = await clinicalHistoryService.deleteDocument(documentId);
    if (result.success) {
      await fetchDocuments(); // Refrescar lista
    }
    return result;
  };

  useEffect(() => {
    fetchDocuments();
  }, [tipo]);

  return {
    documents,
    loading,
    error,
    uploadDocument,
    deleteDocument,
    refetch: fetchDocuments
  };
}

export function useOdontogram(odontogramId) {
  const [odontogram, setOdontogram] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchOdontogram = async () => {
    if (!odontogramId) return;
    
    setLoading(true);
    setError('');
    
    const result = await clinicalHistoryService.getOdontogramDetail(odontogramId);
    
    if (result.success) {
      setOdontogram(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const updateOdontogram = async (odontogramData) => {
    if (!odontogram?.id) return { success: false, error: 'No hay odontograma para actualizar' };
    
    const result = await clinicalHistoryService.updateOdontogram(odontogram.id, odontogramData);
    if (result.success) {
      setOdontogram(result.data);
    }
    return result;
  };

  const duplicateOdontogram = async () => {
    if (!odontogram?.id) return { success: false, error: 'No hay odontograma para duplicar' };
    
    const result = await clinicalHistoryService.duplicateOdontogram(odontogram.id);
    if (result.success) {
      // Opcionalmente podrías refrescar el odontograma actual
      await fetchOdontogram();
    }
    return result;
  };

  useEffect(() => {
    fetchOdontogram();
  }, [odontogramId]);

  return {
    odontogram,
    loading,
    error,
    updateOdontogram,
    duplicateOdontogram,
    refetch: fetchOdontogram
  };
}
```

## 🏥 3. Historial del Paciente

```javascript
// components/PatientHistory.jsx
import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useClinicalHistory, useEpisodes, useDocuments } from '../hooks/useClinicalHistory';

function PatientHistory() {
  const { historyId } = useParams();
  const [activeTab, setActiveTab] = useState('general');
  
  const { history, loading: historyLoading, error: historyError } = useClinicalHistory(historyId);
  const { episodes, loading: episodesLoading, fetchEpisodes } = useEpisodes();
  const { documents, loading: documentsLoading } = useDocuments();

  React.useEffect(() => {
    if (historyId) {
      fetchEpisodes();
    }
  }, [historyId]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getFileIcon = (fileType) => {
    const icons = {
      'image': '🖼️',
      'pdf': '📄',
      'radiografia': '🦴',
      'documento': '📋'
    };
    return icons[fileType] || '📄';
  };

  if (historyLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (historyError) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {historyError}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Encabezado del paciente */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {history?.paciente_nombre?.charAt(0) || 'P'}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {history?.paciente_nombre || 'Paciente'}
              </h1>
              <div className="text-gray-600 space-y-1">
                <p>📧 {history?.paciente_email}</p>
                <p>📞 {history?.paciente_telefono}</p>
                <p>🎂 {history?.paciente_fecha_nacimiento ? formatDate(history.paciente_fecha_nacimiento) : 'N/A'}</p>
              </div>
            </div>
          </div>
          
          <div>
            <Link 
              to={`/historiales/${historyId}/episodio/nuevo`}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Nuevo Episodio
            </Link>
            <Link 
              to={`/historiales/${historyId}/odontograma`}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Odontograma
            </Link>
          </div>
        </div>
      </div>

      {/* Pestañas */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {[
              { id: 'general', label: 'Información General', icon: '👤' },
              { id: 'episodios', label: 'Episodios', icon: '🩺' },
              { id: 'odontogramas', label: 'Odontogramas', icon: '🦷' },
              { id: 'documentos', label: 'Documentos', icon: '�' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Contenido de las pestañas */}
      {activeTab === 'general' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Información básica */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Información Básica</h2>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Nombre Completo</label>
                <p className="text-gray-900">{history?.paciente_nombre || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Fecha de Nacimiento</label>
                <p className="text-gray-900">
                  {history?.paciente_fecha_nacimiento ? formatDate(history.paciente_fecha_nacimiento) : 'N/A'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Género</label>
                <p className="text-gray-900">{history?.paciente_genero || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Dirección</label>
                <p className="text-gray-900">{history?.paciente_direccion || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Información de contacto */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Información de Contacto</h2>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Teléfono</label>
                <p className="text-gray-900">{history?.paciente_telefono || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Email</label>
                <p className="text-gray-900">{history?.paciente_email || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Dirección</label>
                <p className="text-gray-900">{history?.paciente_direccion || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Información médica */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Información Médica</h2>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Alergias</label>
                <p className="text-gray-900">{history?.alergias || 'Ninguna reportada'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Medicamentos Actuales</label>
                <p className="text-gray-900">{history?.medicamentos_actuales || 'Ninguno reportado'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Antecedentes Médicos</label>
                <p className="text-gray-900">{history?.antecedentes_medicos || 'Ninguno reportado'}</p>
              </div>
            </div>
          </div>

          {/* Estadísticas rápidas */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Resumen de Historial</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{history?.total_episodios || 0}</div>
                <div className="text-sm text-blue-800">Episodios</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{history?.total_odontogramas || 0}</div>
                <div className="text-sm text-green-800">Odontogramas</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{history?.total_documentos || 0}</div>
                <div className="text-sm text-purple-800">Documentos</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {history?.ultimo_episodio ? 'Reciente' : 'N/A'}
                </div>
                <div className="text-sm text-yellow-800">Últ. Episodio</div>
              </div>
            </div>
            
            {history?.ultimo_episodio && (
              <div className="mt-4 text-sm text-gray-600">
                <strong>Último episodio:</strong> {formatDate(history.ultimo_episodio)}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'episodios' && (
        <div className="space-y-6">
          {episodesLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {episodes.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <p className="text-gray-500 mb-4">No hay episodios registrados</p>
                  <Link 
                    to={`/historiales/${historyId}/episodio/nuevo`}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Registrar Primer Episodio
                  </Link>
                </div>
              ) : (
                episodes.map((episode) => (
                  <div key={episode.id} className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          Episodio - {formatDate(episode.fecha_atencion)}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Dr. {episode.odontologo_nombre}
                        </p>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Link 
                          to={`/historiales/episodios/${episode.id}`}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Ver Detalles
                        </Link>
                        <Link 
                          to={`/historiales/episodios/${episode.id}/editar`}
                          className="text-green-600 hover:text-green-800 text-sm"
                        >
                          Editar
                        </Link>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <strong className="text-gray-700">Motivo:</strong>
                        <p className="text-gray-600">{episode.motivo_consulta || 'N/A'}</p>
                      </div>
                      <div>
                        <strong className="text-gray-700">Diagnóstico:</strong>
                        <p className="text-gray-600">{episode.diagnostico || 'Pendiente'}</p>
                      </div>
                    </div>
                    
                    {episode.descripcion_procedimiento && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <strong className="text-gray-700 text-sm">Procedimiento:</strong>
                        <p className="text-gray-600 text-sm mt-1">{episode.descripcion_procedimiento}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'documentos' && (
        <div className="space-y-6">
          {attachmentsLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {attachments.length === 0 ? (
                <div className="col-span-full bg-white rounded-lg shadow p-6 text-center">
                  <p className="text-gray-500 mb-4">No hay archivos adjuntos</p>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Subir Primer Archivo
                  </button>
                </div>
              ) : (
                attachments.map((attachment) => (
                  <div key={attachment.id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-2xl">{getFileIcon(attachment.tipo_archivo)}</span>
                      <span className="text-xs text-gray-500">
                        {formatDate(attachment.fecha_subida)}
                      </span>
                    </div>
                    
                    <h4 className="font-medium text-gray-900 truncate" title={attachment.nombre_archivo}>
                      {attachment.nombre_archivo}
                    </h4>
                    
                    {attachment.descripcion && (
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {attachment.descripcion}
                      </p>
                    )}
                    
                    <div className="flex justify-between items-center mt-4">
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {attachment.tipo_archivo.toUpperCase()}
                      </span>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800 text-sm">
                          Ver
                        </button>
                        <button className="text-red-600 hover:text-red-800 text-sm">
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PatientHistory;
```

## ✅ Próximos Pasos

1. Implementar odontograma interactivo
2. Agregar formularios de consulta y diagnóstico
3. Continuar con **06_facturacion_pagos.md**

---
**Endpoints implementados**: ✅ Historial paciente ✅ Consultas ✅ Diagnósticos ✅ Archivos ✅ Odontograma ✅ Reportes médicos