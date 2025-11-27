# 📊 Integración en Página de Reportes

## 📍 Ubicación

```
src/pages/reportes/ReportesPage.jsx  ← Página principal de reportes
```

---

## 1️⃣ Importar el Componente

```javascript
// src/pages/reportes/ReportesPage.jsx
import React, { useState } from 'react';
import VoiceReportCapture from '../../components/reportes/VoiceReportCapture';
import { Download, Calendar, Filter, Mic } from 'lucide-react';
```

---

## 2️⃣ Agregar Estado para Reportes por Voz

```javascript
const ReportesPage = () => {
  // Estado existente
  const [tipoReporte, setTipoReporte] = useState('citas');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [datos, setDatos] = useState([]);
  
  // 🆕 NUEVO: Estado para reportes por voz
  const [esReporteVoz, setEsReporteVoz] = useState(false);
  const [interpretacionVoz, setInterpretacionVoz] = useState(null);
  const [resumenVoz, setResumenVoz] = useState(null);

  // ... resto del código
};
```

---

## 3️⃣ Manejador para Reportes por Voz

```javascript
const ReportesPage = () => {
  // ... estado ...

  /**
   * Maneja el reporte generado por comando de voz
   */
  const handleVoiceReportGenerated = (voiceData) => {
    const { tipo, datos, resumen, interpretacion } = voiceData;
    
    // Actualizar estado
    setTipoReporte(tipo);
    setDatos(datos);
    setResumenVoz(resumen);
    setInterpretacionVoz(interpretacion);
    setEsReporteVoz(true);
    
    // Actualizar fechas si existen
    if (interpretacion.fecha_inicio) {
      setFechaInicio(interpretacion.fecha_inicio);
    }
    if (interpretacion.fecha_fin) {
      setFechaFin(interpretacion.fecha_fin);
    }
    
    console.log('📊 Reporte por voz generado:', {
      tipo,
      cantidad: datos.length,
      periodo: resumen.periodo
    });
  };

  /**
   * Limpiar reporte de voz al cambiar filtros manualmente
   */
  const handleFiltrosChange = () => {
    setEsReporteVoz(false);
    setInterpretacionVoz(null);
    setResumenVoz(null);
  };

  // ... resto del código
};
```

---

## 4️⃣ Actualizar el JSX (Layout Completo)

```javascript
return (
  <div className="reportes-page">
    {/* Header */}
    <div className="reportes-header">
      <div className="header-left">
        <h1>📊 Reportes</h1>
        <p className="subtitle">Genera y exporta reportes de tu clínica</p>
      </div>
      
      <div className="header-right">
        {/* 🆕 BOTÓN DE VOZ */}
        <VoiceReportCapture 
          onReportGenerated={handleVoiceReportGenerated}
        />
        
        <button className="btn-export" onClick={handleExportPDF}>
          <Download size={16} />
          Exportar PDF
        </button>
      </div>
    </div>

    {/* 🆕 Banner de Interpretación de Voz */}
    {esReporteVoz && interpretacionVoz && (
      <div className="voice-interpretation-banner">
        <div className="banner-content">
          <Mic className="banner-icon" size={20} />
          <div className="banner-text">
            <strong>Comando interpretado:</strong>
            <span>{interpretacionVoz.interpretacion}</span>
          </div>
          <button 
            className="banner-close"
            onClick={() => {
              setEsReporteVoz(false);
              setInterpretacionVoz(null);
            }}
          >
            ×
          </button>
        </div>
      </div>
    )}

    {/* Filtros Manuales */}
    <div className="reportes-filters">
      <div className="filter-group">
        <label>Tipo de Reporte</label>
        <select 
          value={tipoReporte} 
          onChange={(e) => {
            setTipoReporte(e.target.value);
            handleFiltrosChange();
          }}
        >
          <option value="citas">Citas</option>
          <option value="facturas">Facturas</option>
          <option value="tratamientos">Tratamientos</option>
          <option value="pacientes">Pacientes</option>
          <option value="ingresos">Ingresos</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Fecha Inicio</label>
        <input 
          type="date" 
          value={fechaInicio}
          onChange={(e) => {
            setFechaInicio(e.target.value);
            handleFiltrosChange();
          }}
        />
      </div>

      <div className="filter-group">
        <label>Fecha Fin</label>
        <input 
          type="date" 
          value={fechaFin}
          onChange={(e) => {
            setFechaFin(e.target.value);
            handleFiltrosChange();
          }}
        />
      </div>

      <button 
        className="btn-filter" 
        onClick={handleGenerarReporte}
      >
        <Filter size={16} />
        Generar Reporte
      </button>
    </div>

    {/* 🆕 Resumen del Reporte de Voz */}
    {esReporteVoz && resumenVoz && (
      <div className="voice-summary-card">
        <h3>📈 Resumen</h3>
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Total:</span>
            <span className="stat-value">{resumenVoz.total}</span>
          </div>
          {resumenVoz.periodo && (
            <div className="stat-item">
              <span className="stat-label">Período:</span>
              <span className="stat-value">{resumenVoz.periodo}</span>
            </div>
          )}
          {resumenVoz.total_ingresos && (
            <div className="stat-item">
              <span className="stat-label">Ingresos:</span>
              <span className="stat-value">Bs. {resumenVoz.total_ingresos.toFixed(2)}</span>
            </div>
          )}
          {resumenVoz.total_facturado && (
            <div className="stat-item">
              <span className="stat-label">Facturado:</span>
              <span className="stat-value">Bs. {resumenVoz.total_facturado.toFixed(2)}</span>
            </div>
          )}
          {resumenVoz.saldo_pendiente !== undefined && (
            <div className="stat-item">
              <span className="stat-label">Saldo Pendiente:</span>
              <span className="stat-value">Bs. {resumenVoz.saldo_pendiente.toFixed(2)}</span>
            </div>
          )}
        </div>
      </div>
    )}

    {/* Tabla de Resultados */}
    <div className="reportes-table">
      {datos.length > 0 ? (
        <TablaReporte tipo={tipoReporte} datos={datos} />
      ) : (
        <div className="empty-state">
          <Mic size={48} className="empty-icon" />
          <h3>Sin resultados</h3>
          <p>Usa el botón de voz o los filtros para generar un reporte</p>
        </div>
      )}
    </div>
  </div>
);
```

---

## 5️⃣ Componente Auxiliar: `TablaReporte.jsx`

```javascript
// src/components/reportes/TablaReporte.jsx
import React from 'react';

const TablaReporte = ({ tipo, datos }) => {
  if (!datos || datos.length === 0) return null;

  // Renderizar según el tipo
  switch (tipo) {
    case 'citas':
      return <TablaCitas datos={datos} />;
    case 'facturas':
      return <TablaFacturas datos={datos} />;
    case 'tratamientos':
      return <TablaTratamientos datos={datos} />;
    case 'pacientes':
      return <TablaPacientes datos={datos} />;
    case 'ingresos':
      return <TablaIngresos datos={datos} />;
    default:
      return <p>Tipo de reporte no soportado</p>;
  }
};

// Tabla para Citas
const TablaCitas = ({ datos }) => (
  <table className="report-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Fecha</th>
        <th>Hora</th>
        <th>Paciente</th>
        <th>Odontólogo</th>
        <th>Motivo</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {datos.map((cita) => (
        <tr key={cita.id}>
          <td>{cita.id}</td>
          <td>{cita.fecha}</td>
          <td>{cita.hora}</td>
          <td>{cita.paciente}</td>
          <td>{cita.odontologo}</td>
          <td>{cita.motivo_tipo}</td>
          <td>
            <span className={`badge badge-${cita.estado.toLowerCase()}`}>
              {cita.estado}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Tabla para Facturas
const TablaFacturas = ({ datos }) => (
  <table className="report-table">
    <thead>
      <tr>
        <th>Número</th>
        <th>Fecha</th>
        <th>Paciente</th>
        <th>Total</th>
        <th>Pagado</th>
        <th>Saldo</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {datos.map((factura) => (
        <tr key={factura.id}>
          <td>{factura.numero}</td>
          <td>{factura.fecha}</td>
          <td>{factura.paciente}</td>
          <td>Bs. {factura.monto_total.toFixed(2)}</td>
          <td>Bs. {factura.monto_pagado.toFixed(2)}</td>
          <td>Bs. {factura.saldo.toFixed(2)}</td>
          <td>
            <span className={`badge badge-${factura.estado.toLowerCase()}`}>
              {factura.estado}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Tabla para Tratamientos
const TablaTratamientos = ({ datos }) => (
  <table className="report-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Fecha</th>
        <th>Paciente</th>
        <th>Odontólogo</th>
        <th>Título</th>
        <th>Total</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {datos.map((plan) => (
        <tr key={plan.id}>
          <td>{plan.id}</td>
          <td>{plan.fecha}</td>
          <td>{plan.paciente}</td>
          <td>{plan.odontologo}</td>
          <td>{plan.titulo}</td>
          <td>Bs. {plan.total.toFixed(2)}</td>
          <td>
            <span className={`badge badge-${plan.estado.toLowerCase()}`}>
              {plan.estado}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Tabla para Pacientes
const TablaPacientes = ({ datos }) => (
  <table className="report-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Nombre</th>
        <th>Email</th>
        <th>Teléfono</th>
        <th>CI</th>
        <th>Fecha Registro</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {datos.map((paciente) => (
        <tr key={paciente.id}>
          <td>{paciente.id}</td>
          <td>{paciente.nombre}</td>
          <td>{paciente.email}</td>
          <td>{paciente.telefono}</td>
          <td>{paciente.ci}</td>
          <td>{paciente.fecha_registro}</td>
          <td>
            <span className={`badge ${paciente.activo ? 'badge-activo' : 'badge-inactivo'}`}>
              {paciente.activo ? 'Activo' : 'Inactivo'}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Tabla para Ingresos
const TablaIngresos = ({ datos }) => (
  <table className="report-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Fecha</th>
        <th>Monto</th>
        <th>Método</th>
        <th>Factura</th>
        <th>Paciente</th>
      </tr>
    </thead>
    <tbody>
      {datos.map((pago) => (
        <tr key={pago.id}>
          <td>{pago.id}</td>
          <td>{pago.fecha}</td>
          <td className="text-success">Bs. {pago.monto.toFixed(2)}</td>
          <td>{pago.metodo_pago}</td>
          <td>{pago.factura}</td>
          <td>{pago.paciente}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

export default TablaReporte;
```

---

## 6️⃣ Función de Exportación

```javascript
// En ReportesPage.jsx

const handleExportPDF = async () => {
  if (datos.length === 0) {
    toast.error('No hay datos para exportar');
    return;
  }

  try {
    // Si es un reporte de voz, incluir la interpretación
    const metadata = esReporteVoz && interpretacionVoz ? {
      comando: interpretacionVoz.texto_original,
      interpretacion: interpretacionVoz.interpretacion,
      periodo: resumenVoz?.periodo
    } : null;

    // Llamar a tu servicio de exportación
    await exportService.exportarPDF({
      tipo: tipoReporte,
      datos,
      metadata
    });

    toast.success('Reporte exportado exitosamente');
  } catch (error) {
    console.error('Error exportando:', error);
    toast.error('Error al exportar el reporte');
  }
};
```

---

## 📝 Resumen de Cambios

### Archivos Modificados
- ✅ `src/pages/reportes/ReportesPage.jsx`
- ✅ `src/components/reportes/TablaReporte.jsx` (nuevo)

### Funcionalidades Añadidas
1. **Botón de micrófono** en el header
2. **Banner de interpretación** cuando se usa voz
3. **Resumen estadístico** para reportes de voz
4. **Sincronización** entre filtros manuales y voz
5. **Tablas dinámicas** según tipo de reporte
6. **Exportación** con metadata de voz

---

## 🔗 Siguiente Paso

Ver **[03_ESTILOS_UI.md](03_ESTILOS_UI.md)** para los estilos CSS del componente.
