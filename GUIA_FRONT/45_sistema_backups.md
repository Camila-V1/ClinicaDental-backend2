# 📋 Guía Frontend: Sistema de Backups Automáticos

> **Módulo:** Backups y Restauración  
> **Rol:** ADMIN  
> **Prioridad:** Media  
> **Complejidad:** Media

---

## 📑 Índice

1. [Descripción General](#descripción-general)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Interfaces TypeScript](#interfaces-typescript)
4. [Servicios API](#servicios-api)
5. [Componentes](#componentes)
6. [Páginas](#páginas)
7. [Rutas](#rutas)
8. [Testing](#testing)

---

## 📋 Descripción General

Sistema completo de gestión de backups automáticos con:

- ✅ **Backups manuales** - Crear backup inmediato y descargarlo
- ✅ **Historial de backups** - Ver todos los backups con metadata
- ✅ **Configuración automática** - Programar backups recurrentes
- ✅ **Descarga de backups** - Recuperar backups desde Supabase
- ✅ **Programación flexible** - Diario, cada X horas, semanal, mensual, fecha única

### **Endpoints del Backend:**

```typescript
GET    /api/backups/history/              // Listar backups
POST   /api/backups/create/               // Crear backup manual
POST   /api/backups/create/?download=true // Crear y descargar
GET    /api/backups/history/{id}/download/ // Descargar backup
DELETE /api/backups/history/{id}/         // Eliminar backup
```

---

## 📁 Estructura de Archivos

```
src/
├── types/
│   └── backups.ts                    // Interfaces de backups
├── services/
│   └── backupService.ts              // API de backups
├── components/
│   ├── backups/
│   │   ├── BackupsList.tsx          // Tabla de historial
│   │   ├── BackupCard.tsx           // Card de backup individual
│   │   ├── ModalCrearBackup.tsx     // Modal para crear backup manual
│   │   └── ModalConfigBackups.tsx   // Modal de configuración automática
├── pages/
│   └── BackupsPage.tsx              // Página principal
└── routes/
    └── adminRoutes.tsx              // Ruta /admin/backups
```

---

## 🔷 Interfaces TypeScript

### **Archivo:** `src/types/backups.ts`

```typescript
/**
 * Registro de un backup individual
 */
export interface BackupRecord {
  id: number;
  file_name: string;
  file_path: string;
  file_size: number;        // En bytes
  file_size_mb: number;     // En MB (calculado)
  backup_type: 'manual' | 'automatic';
  created_by: {
    id: number;
    email: string;
    nombre: string;
  } | null;
  created_at: string;       // ISO 8601 datetime
}

/**
 * DTO para crear backup manual
 */
export interface CreateBackupDTO {
  download?: boolean;       // Si true, descarga directo
}

/**
 * Respuesta al crear backup
 */
export interface CreateBackupResponse {
  message: string;
  backup_info: BackupRecord;
}

/**
 * Configuración de backups automáticos
 */
export interface BackupConfig {
  backup_schedule: 'disabled' | 'daily' | 'every_12h' | 'every_6h' | 'weekly' | 'monthly' | 'scheduled';
  backup_time?: string;           // HH:MM:SS (ej: "02:00:00")
  backup_weekday?: number;        // 0-6 (0=Lunes, 6=Domingo)
  backup_day_of_month?: number;   // 1-28
  next_scheduled_backup?: string; // ISO 8601 datetime (solo para 'scheduled')
  last_backup_at?: string;        // ISO 8601 datetime (readonly)
}

/**
 * Filtros para historial
 */
export interface BackupFilters {
  tipo?: 'manual' | 'automatic';
  fecha_desde?: string;
  fecha_hasta?: string;
}
```

---

## 🔌 Servicios API

### **Archivo:** `src/services/backupService.ts`

```typescript
import axios from 'axios';
import { BackupRecord, CreateBackupResponse, BackupConfig } from '../types/backups';

const API_URL = '/api/backups';

/**
 * Servicio para gestión de backups
 */
export const backupService = {
  /**
   * Obtener historial de backups
   */
  async getHistorial(): Promise<BackupRecord[]> {
    const response = await axios.get(`${API_URL}/history/`);
    return response.data;
  },

  /**
   * Crear backup manual
   * @param download - Si true, descarga el archivo inmediatamente
   */
  async crearBackupManual(download: boolean = false): Promise<CreateBackupResponse | Blob> {
    const response = await axios.post(
      `${API_URL}/create/`,
      {},
      {
        params: { download },
        responseType: download ? 'blob' : 'json'
      }
    );
    
    return response.data;
  },

  /**
   * Descargar backup existente
   */
  async descargarBackup(backupId: number): Promise<Blob> {
    const response = await axios.get(
      `${API_URL}/history/${backupId}/download/`,
      { responseType: 'blob' }
    );
    
    return response.data;
  },

  /**
   * Eliminar backup
   */
  async eliminarBackup(backupId: number): Promise<void> {
    await axios.delete(`${API_URL}/history/${backupId}/`);
  },

  /**
   * Obtener configuración de backups automáticos
   */
  async getConfiguracion(): Promise<BackupConfig> {
    // Nota: Esto viene del endpoint de configuración de clínica
    const response = await axios.get('/api/admin/config/');
    return {
      backup_schedule: response.data.backup_schedule,
      backup_time: response.data.backup_time,
      backup_weekday: response.data.backup_weekday,
      backup_day_of_month: response.data.backup_day_of_month,
      next_scheduled_backup: response.data.next_scheduled_backup,
      last_backup_at: response.data.last_backup_at
    };
  },

  /**
   * Actualizar configuración de backups automáticos
   */
  async actualizarConfiguracion(config: Partial<BackupConfig>): Promise<BackupConfig> {
    const response = await axios.patch('/api/admin/config/', config);
    return response.data;
  }
};

/**
 * Utilidad: Descargar archivo Blob
 */
export const descargarArchivo = (blob: Blob, fileName: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Utilidad: Formatear tamaño de archivo
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Utilidad: Formatear fecha relativa
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Hace un momento';
  if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
  if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
  if (diffDays < 7) return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
  
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
```

---

## 🧩 Componentes

### **1. BackupCard.tsx** - Card de backup individual

```tsx
import React from 'react';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Chip, 
  IconButton, 
  Box,
  Tooltip 
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  CloudDownload as CloudIcon,
  Person as PersonIcon,
  Computer as ComputerIcon
} from '@mui/icons-material';
import { BackupRecord } from '../../types/backups';
import { formatFileSize, formatRelativeTime } from '../../services/backupService';

interface BackupCardProps {
  backup: BackupRecord;
  onDescargar: (backup: BackupRecord) => void;
  onEliminar: (backup: BackupRecord) => void;
  loading?: boolean;
}

export const BackupCard: React.FC<BackupCardProps> = ({
  backup,
  onDescargar,
  onEliminar,
  loading = false
}) => {
  const isManual = backup.backup_type === 'manual';
  const fileExtension = backup.file_name.split('.').pop()?.toUpperCase();

  return (
    <Card 
      variant="outlined"
      sx={{
        '&:hover': {
          boxShadow: 3,
          borderColor: 'primary.main'
        },
        transition: 'all 0.2s'
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <CloudIcon color="primary" />
            <Typography variant="h6" component="div">
              {fileExtension} Backup
            </Typography>
          </Box>
          
          <Chip
            label={isManual ? 'Manual' : 'Automático'}
            color={isManual ? 'primary' : 'secondary'}
            size="small"
            icon={isManual ? <PersonIcon /> : <ComputerIcon />}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {backup.file_name}
        </Typography>

        <Box mt={2} display="flex" gap={2} flexWrap="wrap">
          <Chip
            label={formatFileSize(backup.file_size)}
            size="small"
            variant="outlined"
          />
          
          <Chip
            label={formatRelativeTime(backup.created_at)}
            size="small"
            variant="outlined"
          />
          
          {backup.created_by && (
            <Chip
              label={backup.created_by.nombre}
              size="small"
              variant="outlined"
              icon={<PersonIcon />}
            />
          )}
        </Box>
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
        <Tooltip title="Descargar backup">
          <IconButton
            color="primary"
            onClick={() => onDescargar(backup)}
            disabled={loading}
          >
            <DownloadIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Eliminar backup">
          <IconButton
            color="error"
            onClick={() => onEliminar(backup)}
            disabled={loading}
          >
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};
```

### **2. BackupsList.tsx** - Tabla de historial

```tsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Tooltip,
  Box,
  Typography
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { BackupRecord } from '../../types/backups';
import { formatFileSize, formatRelativeTime } from '../../services/backupService';

interface BackupsListProps {
  backups: BackupRecord[];
  onDescargar: (backup: BackupRecord) => void;
  onEliminar: (backup: BackupRecord) => void;
  loading?: boolean;
}

export const BackupsList: React.FC<BackupsListProps> = ({
  backups,
  onDescargar,
  onEliminar,
  loading = false
}) => {
  if (backups.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="text.secondary">
          No hay backups disponibles
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Crea tu primer backup manual o configura backups automáticos
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Archivo</TableCell>
            <TableCell>Tipo</TableCell>
            <TableCell>Tamaño</TableCell>
            <TableCell>Creado por</TableCell>
            <TableCell>Fecha</TableCell>
            <TableCell align="right">Acciones</TableCell>
          </TableRow>
        </TableHead>
        
        <TableBody>
          {backups.map((backup) => (
            <TableRow
              key={backup.id}
              hover
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {backup.file_name}
                </Typography>
              </TableCell>

              <TableCell>
                <Chip
                  label={backup.backup_type === 'manual' ? 'Manual' : 'Automático'}
                  color={backup.backup_type === 'manual' ? 'primary' : 'secondary'}
                  size="small"
                />
              </TableCell>

              <TableCell>{formatFileSize(backup.file_size)}</TableCell>

              <TableCell>
                {backup.created_by ? backup.created_by.nombre : 'Sistema'}
              </TableCell>

              <TableCell>
                <Tooltip title={new Date(backup.created_at).toLocaleString('es-ES')}>
                  <span>{formatRelativeTime(backup.created_at)}</span>
                </Tooltip>
              </TableCell>

              <TableCell align="right">
                <Tooltip title="Descargar">
                  <IconButton
                    color="primary"
                    size="small"
                    onClick={() => onDescargar(backup)}
                    disabled={loading}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Eliminar">
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => onEliminar(backup)}
                    disabled={loading}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
```

### **3. ModalCrearBackup.tsx** - Modal para crear backup manual

```tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { backupService, descargarArchivo } from '../../services/backupService';
import { CreateBackupResponse } from '../../types/backups';

interface ModalCrearBackupProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ModalCrearBackup: React.FC<ModalCrearBackupProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [descargarDirecto, setDescargarDirecto] = useState(false);

  const handleCrearBackup = async () => {
    setLoading(true);
    setError(null);

    try {
      if (descargarDirecto) {
        // Crear y descargar directamente
        const blob = await backupService.crearBackupManual(true) as Blob;
        const fileName = `backup-${new Date().toISOString().split('T')[0]}.sql`;
        descargarArchivo(blob, fileName);
      } else {
        // Solo crear y registrar
        const response = await backupService.crearBackupManual(false) as CreateBackupResponse;
        console.log('Backup creado:', response);
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al crear el backup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Crear Backup Manual</DialogTitle>

      <DialogContent>
        <Box py={2}>
          <Typography variant="body1" gutterBottom>
            Se creará un backup completo de todos los datos de la clínica.
          </Typography>

          <Alert severity="info" sx={{ mt: 2 }}>
            El backup incluye:
            <ul>
              <li>Usuarios y pacientes</li>
              <li>Agenda y citas</li>
              <li>Historial clínico</li>
              <li>Tratamientos y presupuestos</li>
              <li>Facturación</li>
              <li>Inventario</li>
            </ul>
          </Alert>

          <FormControlLabel
            control={
              <Checkbox
                checked={descargarDirecto}
                onChange={(e) => setDescargarDirecto(e.target.checked)}
              />
            }
            label="Descargar backup inmediatamente"
            sx={{ mt: 2 }}
          />

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancelar
        </Button>
        
        <Button
          variant="contained"
          onClick={handleCrearBackup}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
        >
          {loading ? 'Creando...' : 'Crear Backup'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
```

### **4. ModalConfigBackups.tsx** - Modal de configuración automática

```tsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Typography,
  Chip
} from '@mui/material';
import { backupService } from '../../services/backupService';
import { BackupConfig } from '../../types/backups';

interface ModalConfigBackupsProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const DIAS_SEMANA = [
  { value: 0, label: 'Lunes' },
  { value: 1, label: 'Martes' },
  { value: 2, label: 'Miércoles' },
  { value: 3, label: 'Jueves' },
  { value: 4, label: 'Viernes' },
  { value: 5, label: 'Sábado' },
  { value: 6, label: 'Domingo' }
];

export const ModalConfigBackups: React.FC<ModalConfigBackupsProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [config, setConfig] = useState<BackupConfig>({
    backup_schedule: 'disabled',
    backup_time: '02:00:00',
    backup_weekday: 6,
    backup_day_of_month: 1
  });

  useEffect(() => {
    if (open) {
      cargarConfiguracion();
    }
  }, [open]);

  const cargarConfiguracion = async () => {
    setLoadingConfig(true);
    try {
      const configActual = await backupService.getConfiguracion();
      setConfig(configActual);
    } catch (err) {
      console.error('Error al cargar configuración:', err);
    } finally {
      setLoadingConfig(false);
    }
  };

  const handleGuardar = async () => {
    setLoading(true);
    setError(null);

    try {
      await backupService.actualizarConfiguracion(config);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al guardar configuración');
    } finally {
      setLoading(false);
    }
  };

  const renderCamposAdicionales = () => {
    switch (config.backup_schedule) {
      case 'daily':
      case 'every_12h':
      case 'every_6h':
        return (
          <TextField
            fullWidth
            label="Hora"
            type="time"
            value={config.backup_time?.slice(0, 5) || '02:00'}
            onChange={(e) => setConfig({
              ...config,
              backup_time: `${e.target.value}:00`
            })}
            InputLabelProps={{ shrink: true }}
            helperText={
              config.backup_schedule === 'daily' 
                ? 'Hora en la que se ejecutará el backup diario'
                : `Hora base desde la cual se ejecutará cada ${config.backup_schedule === 'every_12h' ? '12' : '6'} horas`
            }
          />
        );

      case 'weekly':
        return (
          <>
            <FormControl fullWidth>
              <InputLabel>Día de la Semana</InputLabel>
              <Select
                value={config.backup_weekday ?? 6}
                onChange={(e) => setConfig({
                  ...config,
                  backup_weekday: Number(e.target.value)
                })}
              >
                {DIAS_SEMANA.map(dia => (
                  <MenuItem key={dia.value} value={dia.value}>
                    {dia.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Hora"
              type="time"
              value={config.backup_time?.slice(0, 5) || '02:00'}
              onChange={(e) => setConfig({
                ...config,
                backup_time: `${e.target.value}:00`
              })}
              InputLabelProps={{ shrink: true }}
            />
          </>
        );

      case 'monthly':
        return (
          <>
            <TextField
              fullWidth
              label="Día del Mes"
              type="number"
              value={config.backup_day_of_month ?? 1}
              onChange={(e) => setConfig({
                ...config,
                backup_day_of_month: Number(e.target.value)
              })}
              inputProps={{ min: 1, max: 28 }}
              helperText="Día del mes (1-28)"
            />

            <TextField
              fullWidth
              label="Hora"
              type="time"
              value={config.backup_time?.slice(0, 5) || '02:00'}
              onChange={(e) => setConfig({
                ...config,
                backup_time: `${e.target.value}:00`
              })}
              InputLabelProps={{ shrink: true }}
            />
          </>
        );

      case 'scheduled':
        return (
          <TextField
            fullWidth
            label="Fecha y Hora Programada"
            type="datetime-local"
            value={config.next_scheduled_backup?.slice(0, 16) || ''}
            onChange={(e) => setConfig({
              ...config,
              next_scheduled_backup: new Date(e.target.value).toISOString()
            })}
            InputLabelProps={{ shrink: true }}
            helperText="Backup único que se ejecutará una sola vez"
          />
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Configurar Backups Automáticos</DialogTitle>

      <DialogContent>
        {loadingConfig ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Box display="flex" flexDirection="column" gap={3} py={2}>
            {config.last_backup_at && (
              <Alert severity="success">
                Último backup: {new Date(config.last_backup_at).toLocaleString('es-ES')}
              </Alert>
            )}

            <FormControl fullWidth>
              <InputLabel>Frecuencia</InputLabel>
              <Select
                value={config.backup_schedule}
                onChange={(e) => setConfig({
                  ...config,
                  backup_schedule: e.target.value as any
                })}
              >
                <MenuItem value="disabled">Desactivado</MenuItem>
                <MenuItem value="daily">Diario</MenuItem>
                <MenuItem value="every_12h">Cada 12 horas</MenuItem>
                <MenuItem value="every_6h">Cada 6 horas</MenuItem>
                <MenuItem value="weekly">Semanal</MenuItem>
                <MenuItem value="monthly">Mensual</MenuItem>
                <MenuItem value="scheduled">Programado (Fecha única)</MenuItem>
              </Select>
            </FormControl>

            {renderCamposAdicionales()}

            {config.backup_schedule !== 'disabled' && (
              <Alert severity="info">
                <Typography variant="body2">
                  {config.backup_schedule === 'daily' && 'Se ejecutará un backup cada día a la hora especificada'}
                  {config.backup_schedule === 'every_12h' && 'Se ejecutará un backup cada 12 horas desde la hora base'}
                  {config.backup_schedule === 'every_6h' && 'Se ejecutará un backup cada 6 horas desde la hora base'}
                  {config.backup_schedule === 'weekly' && `Se ejecutará un backup cada ${DIAS_SEMANA.find(d => d.value === config.backup_weekday)?.label} a las ${config.backup_time?.slice(0, 5)}`}
                  {config.backup_schedule === 'monthly' && `Se ejecutará un backup el día ${config.backup_day_of_month} de cada mes a las ${config.backup_time?.slice(0, 5)}`}
                  {config.backup_schedule === 'scheduled' && 'El backup se ejecutará una sola vez y luego se desactivará'}
                </Typography>
              </Alert>
            )}

            {error && (
              <Alert severity="error">{error}</Alert>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancelar
        </Button>
        
        <Button
          variant="contained"
          onClick={handleGuardar}
          disabled={loading || loadingConfig}
          startIcon={loading ? <CircularProgress size={20} /> : undefined}
        >
          {loading ? 'Guardando...' : 'Guardar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
```

---

## 📄 Páginas

### **BackupsPage.tsx** - Página principal

```tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { BackupsList } from '../components/backups/BackupsList';
import { ModalCrearBackup } from '../components/backups/ModalCrearBackup';
import { ModalConfigBackups } from '../components/backups/ModalConfigBackups';
import { backupService, descargarArchivo } from '../services/backupService';
import { BackupRecord } from '../types/backups';

export const BackupsPage: React.FC = () => {
  const [backups, setBackups] = useState<BackupRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Modals
  const [modalCrear, setModalCrear] = useState(false);
  const [modalConfig, setModalConfig] = useState(false);
  const [modalEliminar, setModalEliminar] = useState<BackupRecord | null>(null);

  useEffect(() => {
    cargarBackups();
  }, []);

  const cargarBackups = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await backupService.getHistorial();
      setBackups(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al cargar backups');
    } finally {
      setLoading(false);
    }
  };

  const handleDescargar = async (backup: BackupRecord) => {
    try {
      const blob = await backupService.descargarBackup(backup.id);
      descargarArchivo(blob, backup.file_name);
    } catch (err: any) {
      alert('Error al descargar backup: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleEliminarConfirmar = async () => {
    if (!modalEliminar) return;

    try {
      await backupService.eliminarBackup(modalEliminar.id);
      setModalEliminar(null);
      cargarBackups();
    } catch (err: any) {
      alert('Error al eliminar backup: ' + (err.response?.data?.error || err.message));
    }
  };

  const backupsManuales = backups.filter(b => b.backup_type === 'manual');
  const backupsAutomaticos = backups.filter(b => b.backup_type === 'automatic');

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1">
            Backups y Restauración
          </Typography>

          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={cargarBackups}
              disabled={loading}
            >
              Actualizar
            </Button>

            <Button
              variant="outlined"
              startIcon={<SettingsIcon />}
              onClick={() => setModalConfig(true)}
            >
              Configurar Automáticos
            </Button>

            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => setModalCrear(true)}
            >
              Crear Backup Manual
            </Button>
          </Box>
        </Box>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)}>
            <Tab label={`Todos (${backups.length})`} />
            <Tab label={`Manuales (${backupsManuales.length})`} />
            <Tab label={`Automáticos (${backupsAutomaticos.length})`} />
          </Tabs>
        </Paper>

        {/* Error */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading ? (
          <Box display="flex" justifyContent="center" py={8}>
            <CircularProgress />
          </Box>
        ) : (
          /* Lista de Backups */
          <BackupsList
            backups={
              tabValue === 0 ? backups :
              tabValue === 1 ? backupsManuales :
              backupsAutomaticos
            }
            onDescargar={handleDescargar}
            onEliminar={(backup) => setModalEliminar(backup)}
          />
        )}
      </Box>

      {/* Modal Crear Backup */}
      <ModalCrearBackup
        open={modalCrear}
        onClose={() => setModalCrear(false)}
        onSuccess={cargarBackups}
      />

      {/* Modal Configuración */}
      <ModalConfigBackups
        open={modalConfig}
        onClose={() => setModalConfig(false)}
        onSuccess={cargarBackups}
      />

      {/* Modal Confirmar Eliminación */}
      <Dialog
        open={!!modalEliminar}
        onClose={() => setModalEliminar(null)}
      >
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Estás seguro de eliminar el backup <strong>{modalEliminar?.file_name}</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Esta acción no se puede deshacer
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModalEliminar(null)}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleEliminarConfirmar}
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
```

---

## 🛣️ Rutas

### **Agregar en:** `src/routes/adminRoutes.tsx`

```tsx
import { BackupsPage } from '../pages/BackupsPage';

// ...dentro de las rutas de ADMIN
{
  path: 'backups',
  element: <BackupsPage />
}
```

### **Agregar en menú lateral:**

```tsx
{
  title: 'Backups',
  icon: <CloudUploadIcon />,
  path: '/admin/backups',
  roles: ['ADMIN']
}
```

---

## 🧪 Testing

### **Checklist de Pruebas:**

- [ ] **Listar backups** - Ver historial completo
- [ ] **Filtrar por tabs** - Todos, Manuales, Automáticos
- [ ] **Crear backup manual** - Sin descarga
- [ ] **Crear y descargar** - Con checkbox activado
- [ ] **Descargar backup existente** - Desde historial
- [ ] **Eliminar backup** - Con confirmación
- [ ] **Configurar diario** - A las 2:00 AM
- [ ] **Configurar cada 12h** - Desde las 3:00 PM
- [ ] **Configurar semanal** - Domingos a las 2:00 AM
- [ ] **Configurar mensual** - Día 1 a las 2:00 AM
- [ ] **Configurar fecha única** - Programar para mañana
- [ ] **Actualizar lista** - Botón refresh
- [ ] **Formato de fechas** - Relativas y absolutas
- [ ] **Formato de tamaños** - KB, MB correctos
- [ ] **Permisos** - Solo ADMIN puede acceder

---

## 📚 Notas Importantes

### **1. Permisos:**
Solo usuarios con rol `ADMIN` pueden acceder a esta funcionalidad.

### **2. Descarga de Archivos:**
Los archivos pueden ser `.sql` (pg_dump) o `.json` (fallback). El navegador los descargará automáticamente.

### **3. Programación de Backups:**
- **Diario:** Se ejecuta UNA vez al día a la hora especificada
- **Cada Xh:** Se ejecuta cada X horas DESDE la hora base configurada
- **Semanal:** Se ejecuta los días especificados (ej: solo domingos)
- **Mensual:** Se ejecuta el día del mes especificado (1-28)
- **Programado:** Se ejecuta UNA sola vez y luego se auto-desactiva

### **4. Formatos de Fecha:**
- Backend envía: `2025-11-26T14:05:30Z` (ISO 8601)
- Frontend muestra: "Hace 2 horas" o "26 nov 2025, 14:05"

### **5. Tamaños de Archivo:**
- Backend envía bytes
- Frontend calcula y muestra: "512 KB", "1.5 MB", etc.

---

## ✅ Checklist de Implementación

- [ ] Crear `src/types/backups.ts`
- [ ] Crear `src/services/backupService.ts`
- [ ] Crear `src/components/backups/BackupCard.tsx`
- [ ] Crear `src/components/backups/BackupsList.tsx`
- [ ] Crear `src/components/backups/ModalCrearBackup.tsx`
- [ ] Crear `src/components/backups/ModalConfigBackups.tsx`
- [ ] Crear `src/pages/BackupsPage.tsx`
- [ ] Agregar ruta en `adminRoutes.tsx`
- [ ] Agregar ítem en menú lateral
- [ ] Probar creación de backups
- [ ] Probar descarga de backups
- [ ] Probar configuración automática
- [ ] Probar eliminación de backups
- [ ] Verificar permisos de ADMIN

---

**¡Implementación completa del sistema de backups!** 🎉

Con esta guía tienes todo lo necesario para implementar la funcionalidad de backups en el frontend, con interfaces limpias y flujo completo de operaciones.
