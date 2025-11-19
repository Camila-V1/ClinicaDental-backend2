# 📅 Guía Calendario de Citas - Parte 2: Modal de Detalle

## 📋 Contenido
- Modal de Detalle de Cita
- Acciones sobre la Cita
- Formateo de Datos

---

## 🔧 Paso 7: Modal de Detalle de Cita

### **Archivo:** `src/components/Calendario/ModalDetalleCita.tsx`

```typescript
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  Divider,
  Grid,
  IconButton,
  Alert
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import EventIcon from '@mui/icons-material/Event';
import NotesIcon from '@mui/icons-material/Notes';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

import { CitaCalendario, COLORES_ESTADO } from '../../types/calendario.types';
import calendarioService from '../../services/calendarioService';

interface ModalDetalleCitaProps {
  abierto: boolean;
  cita: CitaCalendario | null;
  onCerrar: () => void;
  onActualizar: () => void;
}

/**
 * Modal que muestra el detalle de una cita del calendario
 */
const ModalDetalleCita: React.FC<ModalDetalleCitaProps> = ({
  abierto,
  cita,
  onCerrar,
  onActualizar
}) => {
  const [actualizando, setActualizando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handler: Confirmar cita
   */
  const handleConfirmar = async () => {
    if (!cita) return;

    try {
      setActualizando(true);
      setError(null);
      
      await calendarioService.actualizarEstadoCita(
        cita.id,
        'CONFIRMADA',
        'Cita confirmada desde el calendario'
      );
      
      onActualizar();
    } catch (err: any) {
      console.error('Error al confirmar cita:', err);
      setError(err.response?.data?.error || 'Error al confirmar la cita');
    } finally {
      setActualizando(false);
    }
  };

  /**
   * Handler: Cancelar cita
   */
  const handleCancelar = async () => {
    if (!cita) return;

    const confirmacion = window.confirm(
      '¿Está seguro de cancelar esta cita?'
    );

    if (!confirmacion) return;

    try {
      setActualizando(true);
      setError(null);
      
      await calendarioService.actualizarEstadoCita(
        cita.id,
        'CANCELADA',
        'Cita cancelada desde el calendario'
      );
      
      onActualizar();
    } catch (err: any) {
      console.error('Error al cancelar cita:', err);
      setError(err.response?.data?.error || 'Error al cancelar la cita');
    } finally {
      setActualizando(false);
    }
  };

  /**
   * Handler: Marcar como atendida
   */
  const handleAtender = async () => {
    if (!cita) return;

    try {
      setActualizando(true);
      setError(null);
      
      await calendarioService.actualizarEstadoCita(
        cita.id,
        'ATENDIDA',
        'Cita atendida desde el calendario'
      );
      
      onActualizar();
    } catch (err: any) {
      console.error('Error al atender cita:', err);
      setError(err.response?.data?.error || 'Error al marcar como atendida');
    } finally {
      setActualizando(false);
    }
  };

  if (!cita) return null;

  // Formatear fecha y hora
  const fechaHora = new Date(cita.fecha_hora);
  const fechaFormateada = format(fechaHora, "EEEE d 'de' MMMM yyyy", { locale: es });
  const horaFormateada = format(fechaHora, 'HH:mm', { locale: es });

  // Color del chip de estado
  const colorEstado = COLORES_ESTADO[cita.estado];

  return (
    <Dialog
      open={abierto}
      onClose={onCerrar}
      maxWidth="sm"
      fullWidth
    >
      {/* Título */}
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight="bold">
            Detalle de la Cita
          </Typography>
          <IconButton onClick={onCerrar} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      {/* Contenido */}
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Estado */}
          <Grid item xs={12}>
            <Box display="flex" justifyContent="center" mb={2}>
              <Chip
                label={cita.estado}
                sx={{
                  bgcolor: colorEstado,
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  px: 2
                }}
              />
            </Box>
          </Grid>

          {/* Paciente */}
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={1}>
              <PersonIcon color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Paciente
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {cita.paciente_nombre}
                </Typography>
                {cita.paciente_email && (
                  <Typography variant="caption" color="text.secondary">
                    {cita.paciente_email}
                  </Typography>
                )}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          {/* Fecha */}
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={1}>
              <EventIcon color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Fecha
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {fechaFormateada}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Hora */}
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={1}>
              <AccessTimeIcon color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Hora
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {horaFormateada}
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          {/* Motivo */}
          <Grid item xs={12}>
            <Box>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Motivo de la Cita
              </Typography>
              <Typography variant="body1">
                {cita.motivo}
              </Typography>
              {cita.motivo_tipo && (
                <Chip
                  label={cita.motivo_tipo}
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </Grid>

          {/* Observaciones */}
          {cita.observaciones && (
            <Grid item xs={12}>
              <Box display="flex" alignItems="start" gap={1}>
                <NotesIcon color="action" sx={{ mt: 0.5 }} />
                <Box>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Observaciones
                  </Typography>
                  <Typography variant="body2">
                    {cita.observaciones}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          )}

          {/* Odontólogo */}
          <Grid item xs={12}>
            <Box>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Odontólogo Asignado
              </Typography>
              <Typography variant="body2">
                {cita.odontologo_nombre}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      {/* Acciones */}
      <DialogActions sx={{ p: 2, gap: 1 }}>
        {/* Botón Cancelar Cita */}
        {(cita.estado === 'PENDIENTE' || cita.estado === 'CONFIRMADA') && (
          <Button
            variant="outlined"
            color="error"
            startIcon={<CancelIcon />}
            onClick={handleCancelar}
            disabled={actualizando}
          >
            Cancelar Cita
          </Button>
        )}

        {/* Botón Confirmar */}
        {cita.estado === 'PENDIENTE' && (
          <Button
            variant="contained"
            color="success"
            startIcon={<CheckCircleIcon />}
            onClick={handleConfirmar}
            disabled={actualizando}
          >
            {actualizando ? 'Confirmando...' : 'Confirmar'}
          </Button>
        )}

        {/* Botón Atender */}
        {cita.estado === 'CONFIRMADA' && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<CheckCircleIcon />}
            onClick={handleAtender}
            disabled={actualizando}
          >
            {actualizando ? 'Procesando...' : 'Marcar Atendida'}
          </Button>
        )}

        {/* Botón Cerrar */}
        <Button
          variant="outlined"
          onClick={onCerrar}
          disabled={actualizando}
        >
          Cerrar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModalDetalleCita;
```

---

## 🔧 Paso 8: Integración en Rutas

### **Archivo:** `src/App.tsx` o archivo de rutas

```typescript
import CalendarioCitas from './components/Calendario/CalendarioCitas';

// Dentro de tus rutas protegidas para ODONTOLOGO:
<Route 
  path="/odontologo/calendario" 
  element={
    <ProtectedRoute requiredRole="ODONTOLOGO">
      <CalendarioCitas />
    </ProtectedRoute>
  } 
/>
```

### **Archivo:** `src/components/Layout/MenuOdontologo.tsx`

Agregar enlace al menú:

```typescript
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';

// En el array de opciones del menú:
{
  text: 'Calendario',
  icon: <CalendarMonthIcon />,
  path: '/odontologo/calendario'
}
```

---

## 🎨 Estilos Personalizados (Opcional)

### **Archivo:** `src/styles/calendario.css`

```css
/* Personalización del calendario */
.rbc-calendar {
  font-family: 'Roboto', sans-serif;
}

/* Encabezados */
.rbc-header {
  padding: 10px 5px;
  font-weight: 600;
  color: #1976d2;
}

/* Eventos */
.rbc-event {
  padding: 2px 5px;
  border-radius: 5px;
  font-size: 12px;
}

/* Día actual */
.rbc-today {
  background-color: #e3f2fd;
}

/* Slot seleccionado */
.rbc-selected-cell {
  background-color: #bbdefb;
}

/* Botones de navegación */
.rbc-toolbar button {
  color: #1976d2;
  border: 1px solid #1976d2;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.3s;
}

.rbc-toolbar button:hover {
  background-color: #1976d2;
  color: white;
}

.rbc-toolbar button.rbc-active {
  background-color: #1976d2;
  color: white;
}

/* Título del toolbar */
.rbc-toolbar-label {
  font-weight: 600;
  font-size: 18px;
  color: #333;
  text-transform: capitalize;
}

/* Vista de agenda */
.rbc-agenda-view {
  border: 1px solid #ddd;
}

.rbc-agenda-date-cell,
.rbc-agenda-time-cell {
  white-space: nowrap;
  padding: 8px;
}

.rbc-agenda-event-cell {
  padding: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .rbc-toolbar {
    flex-direction: column;
    gap: 10px;
  }

  .rbc-toolbar button {
    font-size: 12px;
    padding: 6px 12px;
  }
}
```

No olvides importar este archivo en tu componente:

```typescript
import '../../styles/calendario.css';
```

---

## 🧪 Pruebas

### Checklist de Pruebas

```typescript
// ✅ Funcionalidades a probar:

// 1. Navegación
- [ ] Cambiar entre vistas (Mes, Semana, Día, Agenda)
- [ ] Navegar hacia adelante (botón Siguiente)
- [ ] Navegar hacia atrás (botón Anterior)
- [ ] Volver a hoy (botón Hoy)

// 2. Visualización
- [ ] Las citas se muestran en las fechas correctas
- [ ] Los colores corresponden al estado correcto
- [ ] La hora se muestra correctamente
- [ ] El nombre del paciente es visible

// 3. Interacción
- [ ] Click en evento abre el modal
- [ ] Modal muestra información completa
- [ ] Cerrar modal funciona

// 4. Acciones
- [ ] Confirmar cita (desde PENDIENTE)
- [ ] Cancelar cita (desde PENDIENTE/CONFIRMADA)
- [ ] Marcar como atendida (desde CONFIRMADA)
- [ ] Actualización refleja en calendario

// 5. Responsive
- [ ] Funciona en desktop
- [ ] Funciona en tablet
- [ ] Funciona en móvil
- [ ] Botones accesibles en pantalla pequeña

// 6. Edge Cases
- [ ] Sin citas (muestra mensaje apropiado)
- [ ] Muchas citas en un día (scroll funciona)
- [ ] Error de red (muestra mensaje de error)
- [ ] Carga lenta (muestra spinner)
```

### Ejemplo de Prueba Manual

```bash
# 1. Login como odontólogo
Email: odontologo@clinica-demo.com
Password: odontologo123

# 2. Navegar a /odontologo/calendario

# 3. Verificar que se cargan las citas

# 4. Cambiar a vista semanal

# 5. Click en una cita

# 6. Confirmar la cita

# 7. Verificar que el estado cambió en el calendario
```

---

## 📚 Recursos Adicionales

### Documentación

- [React Big Calendar](https://jquense.github.io/react-big-calendar/examples/index.html)
- [date-fns](https://date-fns.org/docs/Getting-Started)
- [Material-UI Dialog](https://mui.com/material-ui/react-dialog/)

### Mejoras Futuras

```typescript
// 🚀 Mejoras opcionales:

// 1. Drag & Drop para reprogramar citas
// 2. Click en slot vacío para crear cita
// 3. Vista de múltiples odontólogos
// 4. Exportar calendario a PDF
// 5. Sincronización con Google Calendar
// 6. Recordatorios automáticos
// 7. Filtros por tipo de cita
// 8. Vista de disponibilidad en tiempo real
```

---

## ✅ Checklist de Implementación

- [ ] Instalar dependencias (react-big-calendar, date-fns)
- [ ] Crear tipos TypeScript
- [ ] Crear servicio de calendario
- [ ] Crear componente CalendarioCitas
- [ ] Crear componente ModalDetalleCita
- [ ] Agregar estilos personalizados
- [ ] Integrar en rutas
- [ ] Agregar al menú del odontólogo
- [ ] Probar navegación
- [ ] Probar acciones (confirmar, cancelar, atender)
- [ ] Probar en diferentes dispositivos
- [ ] Verificar colores y leyenda
- [ ] Documentar uso para el equipo

---

**¡Calendario de Citas completado! 🎉**

Continúa con la siguiente guía: **29_ODONTOGRAMA_INTERACTIVO.md**
