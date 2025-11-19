# 📊 Guía de Implementación: Dashboard con Métricas del Día

## 📋 Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Endpoint Backend](#endpoint-backend)
3. [Estructura de Componentes](#estructura-de-componentes)
4. [Paso 1: Servicio de API](#paso-1-servicio-de-api)
5. [Paso 2: Componente de Métricas](#paso-2-componente-de-métricas)
6. [Paso 3: Tarjetas de Estadísticas](#paso-3-tarjetas-de-estadísticas)
7. [Paso 4: Próxima Cita](#paso-4-próxima-cita)
8. [Paso 5: Integración en Dashboard](#paso-5-integración-en-dashboard)
9. [Estilos y Diseño](#estilos-y-diseño)
10. [Manejo de Errores](#manejo-de-errores)

---

## 📖 Descripción General

El Dashboard con Métricas del Día muestra información en tiempo real sobre las citas del odontólogo, incluyendo:

- 📊 **Estadísticas del día**: Total de citas, pendientes, confirmadas y atendidas
- 👥 **Pacientes atendidos**: Conteo de pacientes únicos
- ⏰ **Próxima cita**: Información de la siguiente cita con tiempo restante
- 🔄 **Actualización automática**: Datos actualizados cada minuto

---

## 🔌 Endpoint Backend

### **URL:**
```
GET /api/agenda/citas/metricas-dia/
```

### **Headers:**
```http
Authorization: Bearer {access_token}
Host: clinica-demo.localhost
```

### **Response (200 OK):**
```json
{
  "fecha": "2025-11-09",
  "citas_hoy": 5,
  "citas_pendientes": 2,
  "citas_confirmadas": 1,
  "citas_atendidas": 2,
  "pacientes_atendidos": 2,
  "proxima_cita": {
    "id": 1,
    "hora": "15:00",
    "paciente": "Juan Pérez",
    "motivo": "Revisión general",
    "estado": "CONFIRMADA",
    "minutos_restantes": 45
  }
}
```

### **Response (sin próxima cita):**
```json
{
  "fecha": "2025-11-09",
  "citas_hoy": 3,
  "citas_pendientes": 0,
  "citas_confirmadas": 0,
  "citas_atendidas": 3,
  "pacientes_atendidos": 3,
  "proxima_cita": null
}
```

### **Error (403 Forbidden):**
```json
{
  "error": "El usuario no tiene un perfil de odontólogo."
}
```

---

## 🏗️ Estructura de Componentes

```
src/
├── pages/
│   └── Dashboard/
│       └── DashboardOdontologo.jsx        # Página principal del dashboard
├── components/
│   └── Dashboard/
│       ├── MetricasDelDia.jsx             # Componente principal de métricas
│       ├── TarjetaMetrica.jsx             # Tarjeta individual de métrica
│       ├── ProximaCita.jsx                # Componente de próxima cita
│       └── ContadorTiempoReal.jsx         # Contador de minutos restantes
└── services/
    └── agendaService.js                   # Servicio de API
```

---

## 🔧 Paso 1: Servicio de API

### **Archivo:** `src/services/agendaService.js`

```javascript
import apiClient from './axios';

/**
 * Servicio para gestión de agenda y citas
 */
const agendaService = {
  /**
   * Obtiene métricas del día actual del odontólogo autenticado
   * @returns {Promise} Promesa con las métricas del día
   */
  async getMetricasDia() {
    try {
      const response = await apiClient.get('/agenda/citas/metricas-dia/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener métricas del día:', error);
      throw error;
    }
  },

  /**
   * Obtiene las citas del odontólogo (para referencia)
   * @param {Object} params - Parámetros de filtro
   * @returns {Promise} Promesa con las citas
   */
  async getCitas(params = {}) {
    try {
      const response = await apiClient.get('/agenda/citas/', { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener citas:', error);
      throw error;
    }
  },

  /**
   * Confirma una cita
   * @param {number} citaId - ID de la cita
   * @returns {Promise} Promesa con la cita actualizada
   */
  async confirmarCita(citaId) {
    try {
      const response = await apiClient.post(`/agenda/citas/${citaId}/confirmar/`);
      return response.data;
    } catch (error) {
      console.error('Error al confirmar cita:', error);
      throw error;
    }
  }
};

export default agendaService;
```

---

## 📦 Paso 2: Componente de Métricas

### **Archivo:** `src/components/Dashboard/MetricasDelDia.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import TarjetaMetrica from './TarjetaMetrica';
import ProximaCita from './ProximaCita';
import agendaService from '../../services/agendaService';

/**
 * Componente principal de métricas del día
 * Muestra estadísticas y próxima cita del odontólogo
 */
const MetricasDelDia = () => {
  const [metricas, setMetricas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  /**
   * Carga las métricas del día
   */
  const cargarMetricas = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agendaService.getMetricasDia();
      setMetricas(data);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err.response?.data?.error || 'Error al cargar las métricas');
      console.error('Error al cargar métricas:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Efecto: Cargar métricas al montar y actualizar cada minuto
   */
  useEffect(() => {
    cargarMetricas();

    // Actualizar cada 60 segundos
    const interval = setInterval(() => {
      cargarMetricas();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  /**
   * Renderizado de carga
   */
  if (loading && !metricas) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  /**
   * Renderizado de error
   */
  if (error) {
    return (
      <Alert 
        severity="error" 
        action={
          <IconButton color="inherit" size="small" onClick={cargarMetricas}>
            <RefreshIcon />
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  /**
   * Renderizado principal
   */
  return (
    <Box>
      {/* Encabezado */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          📊 Métricas del Día
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="caption" color="text.secondary">
            Última actualización: {lastUpdate?.toLocaleTimeString('es-ES')}
          </Typography>
          <Tooltip title="Actualizar">
            <IconButton 
              onClick={cargarMetricas} 
              size="small"
              disabled={loading}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tarjetas de métricas */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <TarjetaMetrica
            titulo="Citas de Hoy"
            valor={metricas?.citas_hoy || 0}
            icono="📅"
            color="primary"
            descripcion="Total de citas programadas"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <TarjetaMetrica
            titulo="Pendientes"
            valor={metricas?.citas_pendientes || 0}
            icono="⏰"
            color="warning"
            descripcion="Citas sin confirmar"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <TarjetaMetrica
            titulo="Atendidas"
            valor={metricas?.citas_atendidas || 0}
            icono="✅"
            color="success"
            descripcion="Citas completadas"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <TarjetaMetrica
            titulo="Pacientes Atendidos"
            valor={metricas?.pacientes_atendidos || 0}
            icono="👥"
            color="info"
            descripcion="Pacientes únicos"
          />
        </Grid>
      </Grid>

      {/* Próxima cita */}
      {metricas?.proxima_cita ? (
        <ProximaCita 
          cita={metricas.proxima_cita} 
          onActualizar={cargarMetricas}
        />
      ) : (
        <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            🎉 No hay más citas programadas para hoy
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default MetricasDelDia;
```

---

## 📊 Paso 3: Tarjetas de Estadísticas

### **Archivo:** `src/components/Dashboard/TarjetaMetrica.jsx`

```jsx
import React from 'react';
import { Paper, Box, Typography } from '@mui/material';

/**
 * Componente de tarjeta de métrica individual
 * @param {Object} props
 * @param {string} props.titulo - Título de la métrica
 * @param {number} props.valor - Valor numérico
 * @param {string} props.icono - Emoji del icono
 * @param {string} props.color - Color del tema (primary, success, warning, info)
 * @param {string} props.descripcion - Descripción breve
 */
const TarjetaMetrica = ({ 
  titulo, 
  valor, 
  icono, 
  color = 'primary', 
  descripcion 
}) => {
  // Mapeo de colores
  const colorMap = {
    primary: '#1976d2',
    success: '#2e7d32',
    warning: '#ed6c02',
    info: '#0288d1',
    error: '#d32f2f'
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6
        },
        borderTop: `4px solid ${colorMap[color]}`
      }}
    >
      {/* Icono y valor */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
        <Typography variant="h2" component="span">
          {icono}
        </Typography>
        <Typography 
          variant="h3" 
          component="div" 
          fontWeight="bold"
          color={colorMap[color]}
        >
          {valor}
        </Typography>
      </Box>

      {/* Título */}
      <Typography variant="h6" component="div" fontWeight="medium" gutterBottom>
        {titulo}
      </Typography>

      {/* Descripción */}
      <Typography variant="caption" color="text.secondary">
        {descripcion}
      </Typography>
    </Paper>
  );
};

export default TarjetaMetrica;
```

---

## ⏰ Paso 4: Próxima Cita

### **Archivo:** `src/components/Dashboard/ProximaCita.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import {
  Paper,
  Box,
  Typography,
  Button,
  Chip,
  Divider,
  Alert
} from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useNavigate } from 'react-router-dom';
import agendaService from '../../services/agendaService';

/**
 * Componente de próxima cita con contador en tiempo real
 * @param {Object} props
 * @param {Object} props.cita - Datos de la cita
 * @param {Function} props.onActualizar - Callback para actualizar métricas
 */
const ProximaCita = ({ cita, onActualizar }) => {
  const navigate = useNavigate();
  const [minutosRestantes, setMinutosRestantes] = useState(cita.minutos_restantes);
  const [confirmando, setConfirmando] = useState(false);

  /**
   * Efecto: Actualizar contador cada minuto
   */
  useEffect(() => {
    setMinutosRestantes(cita.minutos_restantes);

    const interval = setInterval(() => {
      setMinutosRestantes(prev => Math.max(0, prev - 1));
    }, 60000);

    return () => clearInterval(interval);
  }, [cita]);

  /**
   * Confirmar cita
   */
  const handleConfirmar = async () => {
    try {
      setConfirmando(true);
      await agendaService.confirmarCita(cita.id);
      onActualizar(); // Recargar métricas
    } catch (error) {
      console.error('Error al confirmar cita:', error);
      alert('Error al confirmar la cita');
    } finally {
      setConfirmando(false);
    }
  };

  /**
   * Formatear tiempo restante
   */
  const formatearTiempo = (minutos) => {
    if (minutos === 0) return 'En este momento';
    if (minutos < 60) return `En ${minutos} minutos`;
    
    const horas = Math.floor(minutos / 60);
    const mins = minutos % 60;
    return `En ${horas}h ${mins}min`;
  };

  /**
   * Color según urgencia
   */
  const getColorUrgencia = () => {
    if (minutosRestantes === 0) return 'error';
    if (minutosRestantes <= 15) return 'warning';
    return 'info';
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}
    >
      {/* Encabezado */}
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        ⏰ Próxima Cita
      </Typography>

      <Divider sx={{ bgcolor: 'rgba(255,255,255,0.3)', my: 2 }} />

      {/* Información de la cita */}
      <Box mb={2}>
        {/* Hora */}
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <AccessTimeIcon />
          <Typography variant="h6" fontWeight="bold">
            {cita.hora}
          </Typography>
          <Chip 
            label={formatearTiempo(minutosRestantes)}
            color={getColorUrgencia()}
            size="small"
            sx={{ ml: 'auto' }}
          />
        </Box>

        {/* Paciente */}
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <PersonIcon />
          <Typography variant="body1">
            {cita.paciente}
          </Typography>
        </Box>

        {/* Motivo */}
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Motivo: {cita.motivo}
        </Typography>
      </Box>

      {/* Alerta de urgencia */}
      {minutosRestantes <= 15 && minutosRestantes > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          ¡La cita está próxima a comenzar!
        </Alert>
      )}

      {minutosRestantes === 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          ¡La cita debe comenzar ahora!
        </Alert>
      )}

      {/* Acciones */}
      <Box display="flex" gap={2}>
        <Button
          variant="contained"
          color="inherit"
          fullWidth
          onClick={() => navigate(`/citas/${cita.id}`)}
        >
          Ver Detalles
        </Button>

        {cita.estado === 'PENDIENTE' && (
          <Button
            variant="outlined"
            color="inherit"
            fullWidth
            startIcon={<CheckCircleIcon />}
            onClick={handleConfirmar}
            disabled={confirmando}
          >
            {confirmando ? 'Confirmando...' : 'Confirmar'}
          </Button>
        )}
      </Box>
    </Paper>
  );
};

export default ProximaCita;
```

---

## 🎨 Paso 5: Integración en Dashboard

### **Archivo:** `src/pages/Dashboard/DashboardOdontologo.jsx`

```jsx
import React from 'react';
import { Container, Grid, Box, Typography } from '@mui/material';
import MetricasDelDia from '../../components/Dashboard/MetricasDelDia';
import CitasDelDia from '../../components/Dashboard/CitasDelDia';
import AccesosRapidos from '../../components/Dashboard/AccesosRapidos';

/**
 * Página principal del dashboard del odontólogo
 */
const DashboardOdontologo = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Encabezado */}
      <Box mb={4}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Dashboard Odontólogo
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bienvenido a tu panel de control
        </Typography>
      </Box>

      {/* Métricas del día */}
      <Box mb={4}>
        <MetricasDelDia />
      </Box>

      {/* Grid de contenido adicional */}
      <Grid container spacing={3}>
        {/* Citas del día */}
        <Grid item xs={12} md={8}>
          <CitasDelDia />
        </Grid>

        {/* Accesos rápidos */}
        <Grid item xs={12} md={4}>
          <AccesosRapidos />
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardOdontologo;
```

---

## 🎨 Estilos y Diseño

### **Paleta de Colores Recomendada:**

```javascript
const theme = {
  primary: '#1976d2',      // Azul principal
  success: '#2e7d32',      // Verde éxito
  warning: '#ed6c02',      // Naranja advertencia
  info: '#0288d1',         // Azul información
  error: '#d32f2f',        // Rojo error
  gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
};
```

### **Iconos Recomendados (Material-UI):**

```javascript
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RefreshIcon from '@mui/icons-material/Refresh';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
```

---

## ⚠️ Manejo de Errores

### **Casos de Error a Manejar:**

1. **Usuario sin perfil de odontólogo (403)**
```javascript
if (error.response?.status === 403) {
  setError('No tienes permisos para ver estas métricas');
}
```

2. **Token expirado (401)**
```javascript
if (error.response?.status === 401) {
  // Redirigir a login
  navigate('/login');
}
```

3. **Error de red**
```javascript
if (!error.response) {
  setError('Error de conexión. Verifica tu internet.');
}
```

4. **Sin datos**
```javascript
if (!metricas?.citas_hoy) {
  // Mostrar mensaje amigable
  return <Typography>No hay citas programadas para hoy</Typography>;
}
```

---

## 🔄 Actualización Automática

### **Estrategias de Actualización:**

1. **Polling cada 60 segundos** (implementado)
```javascript
useEffect(() => {
  const interval = setInterval(cargarMetricas, 60000);
  return () => clearInterval(interval);
}, []);
```

2. **Actualización manual**
```javascript
<IconButton onClick={cargarMetricas}>
  <RefreshIcon />
</IconButton>
```

3. **Actualización al volver a la pestaña**
```javascript
useEffect(() => {
  const handleFocus = () => cargarMetricas();
  window.addEventListener('focus', handleFocus);
  return () => window.removeEventListener('focus', handleFocus);
}, []);
```

---

## 🧪 Pruebas

### **Casos de Prueba:**

```javascript
// Test 1: Carga correcta de métricas
test('debe cargar métricas correctamente', async () => {
  const { getByText } = render(<MetricasDelDia />);
  await waitFor(() => {
    expect(getByText('Citas de Hoy')).toBeInTheDocument();
  });
});

// Test 2: Actualización automática
test('debe actualizar cada minuto', () => {
  jest.useFakeTimers();
  render(<MetricasDelDia />);
  
  jest.advanceTimersByTime(60000);
  expect(agendaService.getMetricasDia).toHaveBeenCalledTimes(2);
});

// Test 3: Manejo de errores
test('debe mostrar error si falla la carga', async () => {
  agendaService.getMetricasDia.mockRejectedValue(new Error('Error'));
  const { getByText } = render(<MetricasDelDia />);
  
  await waitFor(() => {
    expect(getByText(/error/i)).toBeInTheDocument();
  });
});
```

---

## 📱 Responsive Design

### **Breakpoints:**

```jsx
<Grid container spacing={3}>
  {/* Mobile: 1 columna, Tablet: 2 columnas, Desktop: 4 columnas */}
  <Grid item xs={12} sm={6} md={3}>
    <TarjetaMetrica />
  </Grid>
</Grid>
```

### **Consideraciones Móviles:**

- Fuentes más grandes para métricas
- Botones táctiles de al menos 48px
- Reducir padding en pantallas pequeñas
- Apilar tarjetas verticalmente

---

## ✅ Checklist de Implementación

- [ ] Crear servicio de API (`agendaService.js`)
- [ ] Crear componente `TarjetaMetrica.jsx`
- [ ] Crear componente `ProximaCita.jsx`
- [ ] Crear componente `MetricasDelDia.jsx`
- [ ] Integrar en `DashboardOdontologo.jsx`
- [ ] Agregar actualización automática (60s)
- [ ] Implementar manejo de errores
- [ ] Agregar botón de actualización manual
- [ ] Probar en diferentes resoluciones
- [ ] Validar permisos (solo odontólogos)
- [ ] Agregar tests unitarios
- [ ] Documentar código

---

## 🚀 Mejoras Futuras

1. **WebSockets** para actualizaciones en tiempo real
2. **Gráficos** de tendencias semanales/mensuales
3. **Notificaciones push** para citas próximas
4. **Comparación** con días anteriores
5. **Exportar** métricas a PDF/Excel
6. **Filtros** por rango de fechas
7. **Modo oscuro** con estilos personalizados

---

## 📚 Referencias

- [Material-UI Components](https://mui.com/components/)
- [React Hooks](https://react.dev/reference/react)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [Chart.js](https://www.chartjs.org/) - Para gráficos futuros

---

## 💡 Tips de Optimización

1. **Memoización**: Usar `React.memo()` en componentes pesados
2. **Lazy Loading**: Cargar componentes solo cuando se necesiten
3. **Cache**: Guardar métricas en localStorage temporalmente
4. **Debounce**: En la actualización manual para evitar spam
5. **Virtual Scrolling**: Si la lista de citas es muy larga

---

## 🎯 Resultado Final Esperado

Un dashboard moderno y funcional que muestre:

```
┌─────────────────────────────────────────────────────────┐
│  📊 Métricas del Día         🔄 Última actualización    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │ 📅 5 │  │ ⏰ 2 │  │ ✅ 2 │  │ 👥 2 │              │
│  │ Hoy  │  │Pend. │  │Atend.│  │Pacien│              │
│  └──────┘  └──────┘  └──────┘  └──────┘              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ⏰ Próxima Cita                                 │   │
│  │ 15:00 - Juan Pérez                     En 45min│   │
│  │ Revisión general                                │   │
│  │ [Ver Detalles] [Confirmar]                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📞 Soporte

Si encuentras problemas durante la implementación:

1. Verifica que el backend esté corriendo
2. Confirma que el token de autenticación sea válido
3. Revisa la consola del navegador para errores
4. Verifica que el usuario tenga perfil de odontólogo
5. Prueba el endpoint con Postman/REST Client primero

---

**¡Buena suerte con la implementación! 🚀**

Este componente es fundamental para la experiencia del odontólogo en el sistema.
