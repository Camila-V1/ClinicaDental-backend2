# 22. Exportación de Reportes - PDF y Excel

## 🎯 Objetivo
Implementar descarga de reportes en formato PDF y Excel utilizando los endpoints del backend.

---

## 📁 Actualizar Servicio Existente

**Archivo:** `src/services/reportesService.ts` (ACTUALIZAR)

Agregar métodos de exportación:

```typescript
export const reportesService = {
  // ... métodos existentes ...

  // Exportar reporte a PDF o Excel
  exportarReporte: async (
    endpoint: string, 
    params: any, 
    formato: 'pdf' | 'excel'
  ) => {
    const queryParams = new URLSearchParams({
      ...params,
      formato
    }).toString();

    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/reportes/reportes/${endpoint}/?${queryParams}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );

    if (!response.ok) throw new Error('Error al exportar');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_${endpoint}_${new Date().toISOString().split('T')[0]}.${formato === 'pdf' ? 'pdf' : 'xlsx'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  // Métodos específicos de exportación
  exportarDashboardKPIs: (formato: 'pdf' | 'excel') =>
    reportesService.exportarReporte('dashboard-kpis', {}, formato),

  exportarTendenciaCitas: (dias: number, formato: 'pdf' | 'excel') =>
    reportesService.exportarReporte('tendencia-citas', { dias }, formato),

  exportarTopProcedimientos: (limite: number, formato: 'pdf' | 'excel') =>
    reportesService.exportarReporte('top-procedimientos', { limite }, formato),

  exportarEstadisticas: (formato: 'pdf' | 'excel') =>
    reportesService.exportarReporte('estadisticas-generales', {}, formato),

  exportarIngresos: (fechaInicio: string, fechaFin: string, formato: 'pdf' | 'excel') =>
    reportesService.exportarReporte('ingresos', { fecha_inicio: fechaInicio, fecha_fin: fechaFin }, formato)
};
```

---

## 1️⃣ Componente Botones de Exportación

**Archivo:** `src/components/reportes/BotonesExportar.tsx` (CREAR)

```typescript
import { useState } from 'react';
import toast from 'react-hot-toast';

interface Props {
  onExportar: (formato: 'pdf' | 'excel') => Promise<void>;
  nombreReporte?: string;
}

export default function BotonesExportar({ onExportar, nombreReporte = 'reporte' }: Props) {
  const [exportando, setExportando] = useState(false);

  const handleExportar = async (formato: 'pdf' | 'excel') => {
    setExportando(true);
    try {
      await onExportar(formato);
      toast.success(`${nombreReporte} exportado a ${formato.toUpperCase()}`);
    } catch (error) {
      toast.error(`Error al exportar a ${formato.toUpperCase()}`);
    } finally {
      setExportando(false);
    }
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => handleExportar('pdf')}
        disabled={exportando}
        className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
      >
        📄 Exportar PDF
      </button>
      <button
        onClick={() => handleExportar('excel')}
        disabled={exportando}
        className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
      >
        📊 Exportar Excel
      </button>
    </div>
  );
}
```

---

## 2️⃣ Integración en Página de Reportes

**Archivo:** `src/pages/admin/Reportes.tsx` (ACTUALIZAR)

```typescript
import BotonesExportar from '../../components/reportes/BotonesExportar';
import { reportesService } from '../../services/reportesService';

export default function Reportes() {
  // ... código existente ...

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reportes y Estadísticas</h1>
        
        {/* Botones de exportación global */}
        <BotonesExportar
          onExportar={(formato) => reportesService.exportarEstadisticas(formato)}
          nombreReporte="Estadísticas Generales"
        />
      </div>

      {/* Dashboard KPIs */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Dashboard - KPIs</h2>
          <BotonesExportar
            onExportar={(formato) => reportesService.exportarDashboardKPIs(formato)}
            nombreReporte="Dashboard KPIs"
          />
        </div>
        {/* ... contenido del dashboard ... */}
      </div>

      {/* Tendencia de Citas */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Tendencia de Citas</h2>
          <BotonesExportar
            onExportar={(formato) => reportesService.exportarTendenciaCitas(15, formato)}
            nombreReporte="Tendencia de Citas"
          />
        </div>
        {/* ... gráfico de tendencia ... */}
      </div>

      {/* Top Procedimientos */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Top Procedimientos</h2>
          <BotonesExportar
            onExportar={(formato) => reportesService.exportarTopProcedimientos(5, formato)}
            nombreReporte="Top Procedimientos"
          />
        </div>
        {/* ... tabla de procedimientos ... */}
      </div>
    </div>
  );
}
```

---

## 3️⃣ Modal Exportación Personalizada

**Archivo:** `src/components/reportes/ModalExportarPersonalizado.tsx` (CREAR)

```typescript
import { useState } from 'react';
import { reportesService } from '../../services/reportesService';
import BotonesExportar from './BotonesExportar';

interface Props {
  onClose: () => void;
}

export default function ModalExportarPersonalizado({ onClose }: Props) {
  const [tipoReporte, setTipoReporte] = useState('dashboard-kpis');
  const [parametros, setParametros] = useState({
    fecha_inicio: '',
    fecha_fin: '',
    dias: 15,
    limite: 5
  });

  const handleExportar = async (formato: 'pdf' | 'excel') => {
    switch (tipoReporte) {
      case 'dashboard-kpis':
        await reportesService.exportarDashboardKPIs(formato);
        break;
      case 'tendencia-citas':
        await reportesService.exportarTendenciaCitas(parametros.dias, formato);
        break;
      case 'top-procedimientos':
        await reportesService.exportarTopProcedimientos(parametros.limite, formato);
        break;
      case 'ingresos':
        if (parametros.fecha_inicio && parametros.fecha_fin) {
          await reportesService.exportarIngresos(
            parametros.fecha_inicio, 
            parametros.fecha_fin, 
            formato
          );
        }
        break;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <h2 className="text-xl font-bold mb-4">Exportar Reporte Personalizado</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Tipo de Reporte</label>
          <select
            value={tipoReporte}
            onChange={(e) => setTipoReporte(e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="dashboard-kpis">Dashboard KPIs</option>
            <option value="tendencia-citas">Tendencia de Citas</option>
            <option value="top-procedimientos">Top Procedimientos</option>
            <option value="ingresos">Reporte de Ingresos</option>
          </select>
        </div>

        {/* Parámetros según tipo */}
        {tipoReporte === 'tendencia-citas' && (
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Días</label>
            <input
              type="number"
              min="1"
              max="90"
              value={parametros.dias}
              onChange={(e) => setParametros({ ...parametros, dias: parseInt(e.target.value) })}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        )}

        {tipoReporte === 'top-procedimientos' && (
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Límite</label>
            <input
              type="number"
              min="1"
              max="20"
              value={parametros.limite}
              onChange={(e) => setParametros({ ...parametros, limite: parseInt(e.target.value) })}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        )}

        {tipoReporte === 'ingresos' && (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Fecha Inicio</label>
              <input
                type="date"
                value={parametros.fecha_inicio}
                onChange={(e) => setParametros({ ...parametros, fecha_inicio: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Fecha Fin</label>
              <input
                type="date"
                value={parametros.fecha_fin}
                onChange={(e) => setParametros({ ...parametros, fecha_fin: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </>
        )}

        <div className="mb-4">
          <BotonesExportar
            onExportar={handleExportar}
            nombreReporte={tipoReporte}
          />
        </div>

        <button
          onClick={onClose}
          className="w-full bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Cerrar
        </button>
      </div>
    </div>
  );
}
```

---

## 4️⃣ Utilidad Helper para Exportación

**Archivo:** `src/utils/exportHelper.ts` (CREAR)

```typescript
/**
 * Descarga un archivo desde una URL con autenticación
 */
export const descargarArchivo = async (
  url: string,
  nombreArchivo: string,
  tipoContenido: string = 'application/octet-stream'
) => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(new Blob([blob], { type: tipoContenido }));
    
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = nombreArchivo;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Limpiar
    window.URL.revokeObjectURL(blobUrl);
    
    return true;
  } catch (error) {
    console.error('Error al descargar archivo:', error);
    throw error;
  }
};

/**
 * Obtener nombre de archivo con timestamp
 */
export const getNombreArchivoConFecha = (
  prefijo: string,
  extension: string
): string => {
  const fecha = new Date().toISOString().split('T')[0];
  const hora = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
  return `${prefijo}_${fecha}_${hora}.${extension}`;
};
```

Uso:

```typescript
import { descargarArchivo, getNombreArchivoConFecha } from '../../utils/exportHelper';

// Descargar PDF
await descargarArchivo(
  '/api/reportes/reportes/dashboard-kpis/?formato=pdf',
  getNombreArchivoConFecha('dashboard', 'pdf'),
  'application/pdf'
);

// Descargar Excel
await descargarArchivo(
  '/api/reportes/reportes/tendencia-citas/?dias=30&formato=excel',
  getNombreArchivoConFecha('tendencia_citas', 'xlsx'),
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
);
```

---

## ✅ Checklist

- [ ] Actualizar `reportesService.ts` con métodos de exportación
- [ ] Crear componente `BotonesExportar.tsx`
- [ ] Crear componente `ModalExportarPersonalizado.tsx`
- [ ] Crear utilidad `exportHelper.ts`
- [ ] Integrar en `Reportes.tsx`
- [ ] Probar exportación PDF
- [ ] Probar exportación Excel
- [ ] Verificar descarga automática
- [ ] Validar nombres de archivo

**Endpoints utilizados:**
- `GET /api/reportes/reportes/dashboard-kpis/?formato=pdf`
- `GET /api/reportes/reportes/dashboard-kpis/?formato=excel`
- `GET /api/reportes/reportes/tendencia-citas/?formato=pdf&dias=15`
- `GET /api/reportes/reportes/top-procedimientos/?formato=excel&limite=5`
- Y todos los demás endpoints de reportes con parámetro `formato`

**Nota:** El backend ya genera los archivos PDF y Excel. El frontend solo necesita descargarlos.
