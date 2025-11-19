# 📄 Gestión de Documentos Clínicos - Parte 2: Subida de Archivos

## 🔧 Paso 3: Componente de Subida de Archivos

### **Archivo:** `src/components/Documentos/SubirDocumento.tsx`

```typescript
import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Typography,
  Alert,
  LinearProgress,
  IconButton,
  Chip
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CloseIcon from '@mui/icons-material/Close';

import {
  TipoDocumento,
  TIPOS_DOCUMENTO,
  validarArchivo,
  formatearTamano,
  TAMANO_MAXIMO_MB
} from '../../types/documentos.types';
import documentosService from '../../services/documentosService';

interface SubirDocumentoProps {
  historialId: number;
  episodioId?: number;
  onDocumentoSubido: () => void;
  onCancelar?: () => void;
}

/**
 * Componente para subir documentos clínicos
 */
const SubirDocumento: React.FC<SubirDocumentoProps> = ({
  historialId,
  episodioId,
  onDocumentoSubido,
  onCancelar
}) => {
  // Estado
  const [archivo, setArchivo] = useState<File | null>(null);
  const [tipo, setTipo] = useState<TipoDocumento>('radiografia');
  const [descripcion, setDescripcion] = useState('');
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  // Ref para el input de archivo
  const inputFileRef = useRef<HTMLInputElement>(null);

  /**
   * Handler: Seleccionar archivo desde input
   */
  const handleSeleccionarArchivo = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      procesarArchivo(files[0]);
    }
  };

  /**
   * Handler: Drag over
   */
  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(true);
  };

  /**
   * Handler: Drag leave
   */
  const handleDragLeave = () => {
    setDragOver(false);
  };

  /**
   * Handler: Drop archivo
   */
  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(false);

    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      procesarArchivo(files[0]);
    }
  };

  /**
   * Procesa y valida un archivo
   */
  const procesarArchivo = (file: File) => {
    console.log('📁 Procesando archivo:', file.name);

    // Validar archivo
    const validacion = validarArchivo(file);
    
    if (!validacion.valido) {
      setError(validacion.error || 'Archivo no válido');
      setArchivo(null);
      return;
    }

    // Archivo válido
    setArchivo(file);
    setError(null);
    console.log('✅ Archivo válido:', file.name);
  };

  /**
   * Handler: Quitar archivo seleccionado
   */
  const handleQuitarArchivo = () => {
    setArchivo(null);
    setError(null);
    if (inputFileRef.current) {
      inputFileRef.current.value = '';
    }
  };

  /**
   * Handler: Subir documento
   */
  const handleSubir = async () => {
    if (!archivo) {
      setError('Selecciona un archivo');
      return;
    }

    if (!descripcion.trim()) {
      setError('Ingresa una descripción');
      return;
    }

    try {
      setSubiendo(true);
      setError(null);

      await documentosService.subirDocumento(historialId, {
        archivo,
        tipo,
        descripcion: descripcion.trim(),
        episodio: episodioId
      });

      console.log('✅ Documento subido exitosamente');

      // Limpiar formulario
      setArchivo(null);
      setDescripcion('');
      setTipo('radiografia');
      if (inputFileRef.current) {
        inputFileRef.current.value = '';
      }

      // Notificar al padre
      onDocumentoSubido();
    } catch (err: any) {
      console.error('❌ Error al subir documento:', err);
      setError(err.response?.data?.error || 'Error al subir el documento');
    } finally {
      setSubiendo(false);
    }
  };

  /**
   * Renderizado
   */
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      {/* Título */}
      <Typography variant="h6" gutterBottom>
        📤 Subir Documento
      </Typography>

      {/* Zona de drag & drop */}
      <Box
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          border: `2px dashed ${dragOver ? '#1976d2' : '#ccc'}`,
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: dragOver ? 'action.hover' : 'transparent',
          transition: 'all 0.3s',
          mb: 3
        }}
        onClick={() => inputFileRef.current?.click()}
      >
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        
        <Typography variant="body1" gutterBottom>
          {dragOver 
            ? 'Suelta el archivo aquí' 
            : 'Arrastra un archivo aquí o haz clic para seleccionar'
          }
        </Typography>
        
        <Typography variant="caption" color="text.secondary">
          Formatos: JPG, PNG, PDF (máx. {TAMANO_MAXIMO_MB} MB)
        </Typography>

        {/* Input oculto */}
        <input
          ref={inputFileRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          style={{ display: 'none' }}
          onChange={handleSeleccionarArchivo}
        />
      </Box>

      {/* Archivo seleccionado */}
      {archivo && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 2,
            bgcolor: 'success.light',
            borderRadius: 1,
            mb: 3
          }}
        >
          <AttachFileIcon color="success" />
          <Box flex={1}>
            <Typography variant="body2" fontWeight="bold">
              {archivo.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatearTamano(archivo.size)}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleQuitarArchivo}>
            <CloseIcon />
          </IconButton>
        </Box>
      )}

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Formulario */}
      <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Tipo de documento */}
        <FormControl fullWidth>
          <InputLabel>Tipo de Documento</InputLabel>
          <Select
            value={tipo}
            label="Tipo de Documento"
            onChange={(e) => setTipo(e.target.value as TipoDocumento)}
            disabled={subiendo}
          >
            {Object.entries(TIPOS_DOCUMENTO).map(([key, label]) => (
              <MenuItem key={key} value={key}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Descripción */}
        <TextField
          label="Descripción"
          multiline
          rows={3}
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          placeholder="Ej: Radiografía panorámica inicial, vista lateral derecha..."
          disabled={subiendo}
          required
        />

        {/* Episodio vinculado (si existe) */}
        {episodioId && (
          <Chip
            label={`Vinculado al episodio #${episodioId}`}
            color="info"
            size="small"
            sx={{ alignSelf: 'flex-start' }}
          />
        )}

        {/* Barra de progreso */}
        {subiendo && <LinearProgress />}

        {/* Botones */}
        <Box display="flex" gap={2} justifyContent="flex-end">
          {onCancelar && (
            <Button
              variant="outlined"
              onClick={onCancelar}
              disabled={subiendo}
            >
              Cancelar
            </Button>
          )}

          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={handleSubir}
            disabled={!archivo || !descripcion.trim() || subiendo}
          >
            {subiendo ? 'Subiendo...' : 'Subir Documento'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default SubirDocumento;
```

---

## 🔧 Paso 4: Galería de Documentos

### **Archivo:** `src/components/Documentos/GaleriaDocumentos.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Chip,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ImageIcon from '@mui/icons-material/Image';
import SearchIcon from '@mui/icons-material/Search';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

import {
  DocumentoClinico,
  TipoDocumento,
  TIPOS_DOCUMENTO,
  COLORES_TIPO,
  formatearTamano,
  esImagen,
  esPDF
} from '../../types/documentos.types';
import documentosService from '../../services/documentosService';

interface GaleriaDocumentosProps {
  historialId: number;
  onActualizar?: () => void;
}

/**
 * Galería de documentos clínicos con vista previa
 */
const GaleriaDocumentos: React.FC<GaleriaDocumentosProps> = ({
  historialId,
  onActualizar
}) => {
  // Estado
  const [documentos, setDocumentos] = useState<DocumentoClinico[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroTipo, setFiltroTipo] = useState<TipoDocumento | 'todos'>('todos');
  const [busqueda, setBusqueda] = useState('');
  const [documentoSeleccionado, setDocumentoSeleccionado] = useState<DocumentoClinico | null>(null);
  const [modalEliminar, setModalEliminar] = useState(false);
  const [eliminando, setEliminando] = useState(false);

  /**
   * Efecto: Cargar documentos al montar
   */
  useEffect(() => {
    cargarDocumentos();
  }, [historialId, filtroTipo]);

  /**
   * Carga los documentos del historial
   */
  const cargarDocumentos = async () => {
    try {
      setLoading(true);
      setError(null);

      const filtros = filtroTipo !== 'todos' ? { tipo: filtroTipo } : undefined;
      const docs = await documentosService.listarDocumentos(historialId, filtros);

      setDocumentos(docs);
    } catch (err: any) {
      console.error('Error al cargar documentos:', err);
      setError(err.response?.data?.error || 'Error al cargar los documentos');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handler: Descargar documento
   */
  const handleDescargar = async (documento: DocumentoClinico) => {
    try {
      console.log('⬇️ Descargando:', documento.nombre_archivo);

      const blob = await documentosService.descargarDocumento(documento.id);
      
      // Crear enlace de descarga
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = documento.nombre_archivo;
      link.click();
      
      // Limpiar
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Descarga completada');
    } catch (err) {
      console.error('❌ Error al descargar:', err);
      alert('Error al descargar el documento');
    }
  };

  /**
   * Handler: Confirmar eliminación
   */
  const handleConfirmarEliminar = (documento: DocumentoClinico) => {
    setDocumentoSeleccionado(documento);
    setModalEliminar(true);
  };

  /**
   * Handler: Eliminar documento
   */
  const handleEliminar = async () => {
    if (!documentoSeleccionado) return;

    try {
      setEliminando(true);
      
      await documentosService.eliminarDocumento(documentoSeleccionado.id);
      
      console.log('✅ Documento eliminado');
      
      // Recargar lista
      await cargarDocumentos();
      
      // Cerrar modal
      setModalEliminar(false);
      setDocumentoSeleccionado(null);
      
      // Notificar
      if (onActualizar) {
        onActualizar();
      }
    } catch (err: any) {
      console.error('❌ Error al eliminar:', err);
      alert('Error al eliminar el documento');
    } finally {
      setEliminando(false);
    }
  };

  /**
   * Filtra documentos por búsqueda
   */
  const documentosFiltrados = documentos.filter(doc => {
    if (!busqueda) return true;
    
    const busquedaLower = busqueda.toLowerCase();
    return (
      doc.descripcion.toLowerCase().includes(busquedaLower) ||
      doc.nombre_archivo.toLowerCase().includes(busquedaLower)
    );
  });

  /**
   * Renderizado
   */
  return (
    <Box>
      {/* Filtros y búsqueda */}
      <Box display="flex" gap={2} mb={3}>
        {/* Filtro por tipo */}
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Tipo de Documento</InputLabel>
          <Select
            value={filtroTipo}
            label="Tipo de Documento"
            onChange={(e) => setFiltroTipo(e.target.value as TipoDocumento | 'todos')}
          >
            <MenuItem value="todos">Todos los tipos</MenuItem>
            {Object.entries(TIPOS_DOCUMENTO).map(([key, label]) => (
              <MenuItem key={key} value={key}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Búsqueda */}
        <TextField
          fullWidth
          placeholder="Buscar por descripción o nombre..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
          }}
        />
      </Box>

      {/* Loading */}
      {loading && (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Sin documentos */}
      {!loading && documentosFiltrados.length === 0 && (
        <Box textAlign="center" py={6}>
          <Typography variant="h6" color="text.secondary">
            📄 No hay documentos para mostrar
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {busqueda 
              ? 'No se encontraron documentos con ese criterio'
              : 'Sube tu primer documento para comenzar'
            }
          </Typography>
        </Box>
      )}

      {/* Grid de documentos */}
      <Grid container spacing={2}>
        {documentosFiltrados.map(documento => (
          <Grid item xs={12} sm={6} md={4} key={documento.id}>
            <Card
              elevation={2}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4
                }
              }}
            >
              {/* Vista previa */}
              <Box
                sx={{
                  height: 200,
                  bgcolor: 'grey.100',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  position: 'relative'
                }}
              >
                {esImagen(documento.nombre_archivo) ? (
                  <CardMedia
                    component="img"
                    image={documentosService.obtenerUrlArchivo(documento.archivo)}
                    alt={documento.descripcion}
                    sx={{ height: '100%', objectFit: 'cover' }}
                  />
                ) : esPDF(documento.nombre_archivo) ? (
                  <PictureAsPdfIcon sx={{ fontSize: 80, color: 'error.main' }} />
                ) : (
                  <ImageIcon sx={{ fontSize: 80, color: 'text.secondary' }} />
                )}

                {/* Chip de tipo */}
                <Chip
                  label={TIPOS_DOCUMENTO[documento.tipo]}
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    bgcolor: COLORES_TIPO[documento.tipo],
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                />
              </Box>

              {/* Contenido */}
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="body2" gutterBottom noWrap>
                  <strong>{documento.nombre_archivo}</strong>
                </Typography>
                
                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                  {formatearTamano(documento.tamano_bytes)} • {' '}
                  {format(new Date(documento.fecha_subida), "dd MMM yyyy", { locale: es })}
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {documento.descripcion}
                </Typography>

                {documento.episodio_info && (
                  <Chip
                    label={`Episodio #${documento.episodio}`}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                )}
              </CardContent>

              {/* Acciones */}
              <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                <IconButton
                  size="small"
                  color="primary"
                  onClick={() => handleDescargar(documento)}
                  title="Descargar"
                >
                  <DownloadIcon />
                </IconButton>

                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleConfirmarEliminar(documento)}
                  title="Eliminar"
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Modal de confirmación de eliminación */}
      <Dialog open={modalEliminar} onClose={() => !eliminando && setModalEliminar(false)}>
        <DialogTitle>¿Eliminar Documento?</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Estás seguro de que deseas eliminar este documento?
          </Typography>
          {documentoSeleccionado && (
            <Box mt={2}>
              <Typography variant="body2" fontWeight="bold">
                {documentoSeleccionado.nombre_archivo}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {documentoSeleccionado.descripcion}
              </Typography>
            </Box>
          )}
          <Alert severity="warning" sx={{ mt: 2 }}>
            Esta acción no se puede deshacer
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModalEliminar(false)} disabled={eliminando}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleEliminar}
            disabled={eliminando}
          >
            {eliminando ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GaleriaDocumentos;
```

---

*Continúa en la Parte 3 con el componente principal de integración...*

## 📚 Próximos Pasos

- **Parte 3**: Componente principal que integra subida y galería
- **Parte 4**: Integración en el historial clínico
- **Parte 5**: Pruebas y validación
