# 23. Bitácora Completa - Auditoría y Logs

## 🎯 Objetivo
Mejorar la página de bitácora con filtros avanzados, vista detallada y análisis de actividad.

---

## 📁 Actualizar Servicio Existente

**Archivo:** `src/services/bitacoraService.ts` (ACTUALIZAR)

```typescript
export const bitacoraService = {
  getLogs: (params?: {
    usuario?: number;
    accion?: 'CREATE' | 'UPDATE' | 'DELETE' | 'VIEW' | 'LOGIN' | 'LOGOUT';
    modelo?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
    page?: number;
    page_size?: number;
  }) =>
    httpRequest<any>({
      method: 'GET',
      url: '/reportes/bitacora/',
      params
    }),

  getLogDetalle: (id: number) =>
    httpRequest<any>({
      method: 'GET',
      url: `/reportes/bitacora/${id}/`
    }),

  // Exportar logs (implementación frontend)
  exportarLogs: async (params: any, formato: 'csv' | 'json') => {
    const data = await bitacoraService.getLogs(params);
    const logs = data.results || data;
    
    if (formato === 'json') {
      const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logs_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    } else if (formato === 'csv') {
      const csv = convertirACSV(logs);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    }
  }
};

// Helper para convertir a CSV
function convertirACSV(logs: any[]): string {
  if (logs.length === 0) return '';
  
  const headers = ['ID', 'Fecha', 'Usuario', 'Acción', 'Modelo', 'Descripción', 'IP'];
  const rows = logs.map(log => [
    log.id,
    new Date(log.fecha_hora).toLocaleString(),
    log.usuario?.nombre || 'Sistema',
    log.accion,
    log.modelo,
    log.descripcion,
    log.ip_address
  ]);
  
  return [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
}
```

---

## 1️⃣ Página Bitácora Mejorada

**Archivo:** `src/pages/admin/Bitacora.tsx` (ACTUALIZAR)

```typescript
import { useState, useEffect } from 'react';
import { bitacoraService } from '../../services/bitacoraService';
import { usuariosService } from '../../services/usuariosService';
import toast from 'react-hot-toast';

export default function Bitacora() {
  const [logs, setLogs] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [logSeleccionado, setLogSeleccionado] = useState(null);
  const [paginacion, setPaginacion] = useState({ count: 0, next: null, previous: null });
  const [filtros, setFiltros] = useState({
    usuario: '',
    accion: '',
    modelo: '',
    fecha_inicio: '',
    fecha_fin: '',
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    cargarDatos();
  }, [filtros]);

  const cargarDatos = async () => {
    try {
      const [logsData, usersData] = await Promise.all([
        bitacoraService.getLogs(filtros),
        usuariosService.getUsuarios()
      ]);
      setLogs(logsData.results || logsData);
      setPaginacion({
        count: logsData.count || 0,
        next: logsData.next,
        previous: logsData.previous
      });
      setUsuarios(usersData.results || usersData);
    } catch (error) {
      toast.error('Error al cargar logs');
    }
  };

  const handleExportar = async (formato: 'csv' | 'json') => {
    try {
      await bitacoraService.exportarLogs(filtros, formato);
      toast.success(`Logs exportados a ${formato.toUpperCase()}`);
    } catch (error) {
      toast.error('Error al exportar logs');
    }
  };

  const verDetalle = async (log: any) => {
    try {
      const detalle = await bitacoraService.getLogDetalle(log.id);
      setLogSeleccionado(detalle);
    } catch (error) {
      toast.error('Error al cargar detalle');
    }
  };

  const getAccionColor = (accion: string) => {
    switch (accion) {
      case 'CREATE': return 'bg-green-100 text-green-800';
      case 'UPDATE': return 'bg-blue-100 text-blue-800';
      case 'DELETE': return 'bg-red-100 text-red-800';
      case 'VIEW': return 'bg-gray-100 text-gray-800';
      case 'LOGIN': return 'bg-purple-100 text-purple-800';
      case 'LOGOUT': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAccionIcon = (accion: string) => {
    switch (accion) {
      case 'CREATE': return '➕';
      case 'UPDATE': return '✏️';
      case 'DELETE': return '🗑️';
      case 'VIEW': return '👁️';
      case 'LOGIN': return '🔓';
      case 'LOGOUT': return '🔒';
      default: return '📝';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Bitácora del Sistema</h1>
        <div className="flex gap-2">
          <button
            onClick={() => handleExportar('csv')}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            📊 Exportar CSV
          </button>
          <button
            onClick={() => handleExportar('json')}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            📄 Exportar JSON
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Usuario</label>
            <select
              value={filtros.usuario}
              onChange={(e) => setFiltros({ ...filtros, usuario: e.target.value, page: 1 })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Todos</option>
              {usuarios.map(u => (
                <option key={u.id} value={u.id}>{u.nombre} {u.apellido}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Acción</label>
            <select
              value={filtros.accion}
              onChange={(e) => setFiltros({ ...filtros, accion: e.target.value, page: 1 })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Todas</option>
              <option value="CREATE">Crear</option>
              <option value="UPDATE">Actualizar</option>
              <option value="DELETE">Eliminar</option>
              <option value="VIEW">Ver</option>
              <option value="LOGIN">Login</option>
              <option value="LOGOUT">Logout</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Modelo</label>
            <input
              type="text"
              value={filtros.modelo}
              onChange={(e) => setFiltros({ ...filtros, modelo: e.target.value, page: 1 })}
              placeholder="Cita, Paciente, etc."
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Desde</label>
            <input
              type="date"
              value={filtros.fecha_inicio}
              onChange={(e) => setFiltros({ ...filtros, fecha_inicio: e.target.value, page: 1 })}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Hasta</label>
            <input
              type="date"
              value={filtros.fecha_fin}
              onChange={(e) => setFiltros({ ...filtros, fecha_fin: e.target.value, page: 1 })}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Tabla de logs */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modelo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {logs.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {new Date(log.fecha_hora).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {log.usuario?.nombre || 'Sistema'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-xs ${getAccionColor(log.accion)}`}>
                    {getAccionIcon(log.accion)} {log.accion}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {log.modelo}
                </td>
                <td className="px-6 py-4 text-sm">
                  {log.descripcion}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {log.ip_address}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => verDetalle(log)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    Ver detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Paginación */}
        <div className="bg-gray-50 px-6 py-3 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Total: {paginacion.count} registros
          </div>
          <div className="flex gap-2">
            <button
              disabled={!paginacion.previous}
              onClick={() => setFiltros({ ...filtros, page: filtros.page - 1 })}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Anterior
            </button>
            <span className="px-3 py-1">Página {filtros.page}</span>
            <button
              disabled={!paginacion.next}
              onClick={() => setFiltros({ ...filtros, page: filtros.page + 1 })}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>

      {/* Modal Detalle */}
      {logSeleccionado && (
        <ModalDetalleLog
          log={logSeleccionado}
          onClose={() => setLogSeleccionado(null)}
        />
      )}
    </div>
  );
}
```

---

## 2️⃣ Modal Detalle de Log

**Archivo:** `src/components/bitacora/ModalDetalleLog.tsx` (CREAR)

```typescript
interface Props {
  log: any;
  onClose: () => void;
}

export default function ModalDetalleLog({ log, onClose }: Props) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-2xl max-h-[80vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Detalle del Log</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Fecha y Hora</p>
              <p className="font-medium">{new Date(log.fecha_hora).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Usuario</p>
              <p className="font-medium">{log.usuario?.nombre || 'Sistema'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Acción</p>
              <p className="font-medium">{log.accion}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Modelo</p>
              <p className="font-medium">{log.modelo}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">ID del Objeto</p>
              <p className="font-medium">{log.objeto_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">IP Address</p>
              <p className="font-medium">{log.ip_address}</p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-2">Descripción</p>
            <p className="bg-gray-50 p-3 rounded">{log.descripcion}</p>
          </div>

          {log.user_agent && (
            <div>
              <p className="text-sm text-gray-600 mb-2">User Agent</p>
              <p className="bg-gray-50 p-3 rounded text-xs">{log.user_agent}</p>
            </div>
          )}

          {log.detalles && Object.keys(log.detalles).length > 0 && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Detalles Adicionales</p>
              <pre className="bg-gray-50 p-3 rounded overflow-x-auto text-xs">
                {JSON.stringify(log.detalles, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="mt-6 w-full bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Cerrar
        </button>
      </div>
    </div>
  );
}
```

---

## ✅ Checklist

- [ ] Actualizar `bitacoraService.ts` con exportación
- [ ] Actualizar página `Bitacora.tsx` con filtros avanzados
- [ ] Crear componente `ModalDetalleLog.tsx`
- [ ] Implementar paginación
- [ ] Probar filtros
- [ ] Probar exportación CSV y JSON
- [ ] Verificar vista de detalles

**Endpoints utilizados:**
- `GET /api/reportes/bitacora/`
- `GET /api/reportes/bitacora/{id}/`
