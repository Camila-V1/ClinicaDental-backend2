# 📄 Gestión de Documentos Clínicos - Parte 3: Integración y Pruebas

## 🔧 Paso 5: Componente Principal de Gestión

### **Archivo:** `src/components/Documentos/GestionDocumentos.tsx`

```typescript
import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Badge
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FolderIcon from '@mui/icons-material/Folder';

import SubirDocumento from './SubirDocumento';
import GaleriaDocumentos from './GaleriaDocumentos';

interface GestionDocumentosProps {
  historialId: number;
  episodioId?: number;
}

/**
 * Componente principal para gestión completa de documentos
 * Combina subida y visualización en tabs
 */
const GestionDocumentos: React.FC<GestionDocumentosProps> = ({
  historialId,
  episodioId
}) => {
  const [tabActual, setTabActual] = useState(0);
  const [actualizarGaleria, setActualizarGaleria] = useState(0);

  /**
   * Handler: Cambiar tab
   */
  const handleCambiarTab = (event: React.SyntheticEvent, nuevoValor: number) => {
    setTabActual(nuevoValor);
  };

  /**
   * Handler: Documento subido exitosamente
   */
  const handleDocumentoSubido = () => {
    // Forzar actualización de galería
    setActualizarGaleria(prev => prev + 1);
    
    // Cambiar a tab de galería
    setTabActual(1);
  };

  return (
    <Box>
      {/* Tabs */}
      <Paper elevation={1} sx={{ mb: 2 }}>
        <Tabs
          value={tabActual}
          onChange={handleCambiarTab}
          variant="fullWidth"
        >
          <Tab
            icon={<CloudUploadIcon />}
            label="Subir Documento"
            iconPosition="start"
          />
          <Tab
            icon={<FolderIcon />}
            label="Documentos"
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Contenido del tab */}
      <Box>
        {tabActual === 0 && (
          <SubirDocumento
            historialId={historialId}
            episodioId={episodioId}
            onDocumentoSubido={handleDocumentoSubido}
          />
        )}

        {tabActual === 1 && (
          <GaleriaDocumentos
            historialId={historialId}
            key={actualizarGaleria} // Forzar re-render
          />
        )}
      </Box>
    </Box>
  );
};

export default GestionDocumentos;
```

---

## 🔧 Paso 6: Integración en Historial Clínico

### **Opción A: Como Tab en HistorialDetalle**

**Archivo:** `src/pages/odontologo/HistorialDetalle.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Paper,
  Tabs,
  Tab,
  Box
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';
import AssignmentIcon from '@mui/icons-material/Assignment';
import FolderIcon from '@mui/icons-material/Folder'; // ← NUEVO

import DatosPaciente from '../../components/Historial/DatosPaciente';
import EpisodiosAtencion from '../../components/Historial/EpisodiosAtencion';
import PlanesActivos from '../../components/Historial/PlanesActivos';
import GestionDocumentos from '../../components/Documentos/GestionDocumentos'; // ← NUEVO

const HistorialDetalle: React.FC = () => {
  const { historialId } = useParams<{ historialId: string }>();
  const [tabActual, setTabActual] = useState(0);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper>
        {/* Tabs de navegación */}
        <Tabs
          value={tabActual}
          onChange={(e, val) => setTabActual(val)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<PersonIcon />} label="Datos del Paciente" />
          <Tab icon={<MedicalServicesIcon />} label="Episodios" />
          <Tab icon={<AssignmentIcon />} label="Planes" />
          <Tab icon={<FolderIcon />} label="Documentos" /> {/* ← NUEVO */}
        </Tabs>

        {/* Contenido de tabs */}
        <Box p={3}>
          {tabActual === 0 && <DatosPaciente historialId={Number(historialId)} />}
          {tabActual === 1 && <EpisodiosAtencion historialId={Number(historialId)} />}
          {tabActual === 2 && <PlanesActivos historialId={Number(historialId)} />}
          {tabActual === 3 && (
            <GestionDocumentos historialId={Number(historialId)} /> // ← NUEVO
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default HistorialDetalle;
```

### **Opción B: Como Página Independiente**

**Archivo:** `src/pages/odontologo/DocumentosClinico.tsx`

```typescript
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import GestionDocumentos from '../../components/Documentos/GestionDocumentos';

const DocumentosClinico: React.FC = () => {
  const { historialId } = useParams<{ historialId: string }>();
  const navigate = useNavigate();

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/odontologo/historiales/${historialId}`)}
        >
          Volver
        </Button>
        <Typography variant="h4" fontWeight="bold">
          📄 Documentos Clínicos
        </Typography>
      </Box>

      {/* Componente de gestión */}
      <GestionDocumentos historialId={Number(historialId)} />
    </Container>
  );
};

export default DocumentosClinico;
```

**Agregar ruta en tu router:**

```typescript
import DocumentosClinico from './pages/odontologo/DocumentosClinico';

// En tus rutas protegidas:
<Route 
  path="/odontologo/historiales/:historialId/documentos" 
  element={<DocumentosClinico />} 
/>
```

---

## 🧪 Paso 7: Pruebas

### **Checklist de Pruebas**

```typescript
// ✅ Funcionalidades a probar:

// 1. Subida de Archivos
- [ ] Seleccionar archivo con botón
- [ ] Drag & drop de archivo
- [ ] Validación de tipo de archivo (solo imágenes y PDFs)
- [ ] Validación de tamaño (máx 10 MB)
- [ ] Mostrar vista previa del archivo seleccionado
- [ ] Quitar archivo seleccionado
- [ ] Subir con descripción
- [ ] Subir con tipo de documento
- [ ] Vincular a episodio (si aplica)
- [ ] Ver progreso de subida
- [ ] Manejo de errores

// 2. Visualización
- [ ] Cargar lista de documentos
- [ ] Mostrar vista previa de imágenes
- [ ] Mostrar icono de PDF
- [ ] Filtrar por tipo de documento
- [ ] Buscar por descripción/nombre
- [ ] Ver información del documento (fecha, tamaño)
- [ ] Ver episodio vinculado

// 3. Acciones
- [ ] Descargar documento
- [ ] Ver documento en modal (próximo paso)
- [ ] Eliminar documento con confirmación
- [ ] Actualizar lista después de eliminar

// 4. Responsive
- [ ] Funciona en desktop
- [ ] Funciona en tablet
- [ ] Funciona en móvil
- [ ] Grid se adapta al tamaño de pantalla

// 5. Edge Cases
- [ ] Sin documentos (mostrar mensaje)
- [ ] Error al cargar (mostrar error)
- [ ] Error al subir (mostrar error)
- [ ] Archivo muy grande (validación)
- [ ] Tipo no permitido (validación)
```

### **Ejemplo de Prueba Manual**

```bash
# 1. Ir al historial de un paciente
http://clinica-demo.localhost:3000/odontologo/historiales/123

# 2. Navegar a tab "Documentos"

# 3. Tab "Subir Documento"
   - Arrastra una imagen (JPG, PNG)
   - Verifica que se muestre el nombre y tamaño
   - Selecciona tipo: "Radiografía"
   - Escribe descripción: "Radiografía panorámica inicial"
   - Click "Subir Documento"
   - Verifica que cambie a tab "Documentos"

# 4. Tab "Documentos"
   - Verifica que aparezca el documento recién subido
   - Verifica la vista previa de la imagen
   - Verifica la información (fecha, tamaño)

# 5. Probar filtros
   - Filtrar por tipo: "Radiografía"
   - Buscar por descripción: "panorámica"

# 6. Probar acciones
   - Descargar documento
   - Eliminar documento (con confirmación)

# 7. Probar con PDF
   - Subir un archivo PDF
   - Verifica que se muestre el icono de PDF
   - Descargar y verificar que se descarga correctamente
```

---

## 🎨 Estilos Adicionales (Opcional)

### **Archivo:** `src/styles/documentos.css`

```css
/* Estilos para gestión de documentos */

/* Zona de drag & drop animada */
.dropzone-active {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    border-color: #1976d2;
  }
  50% {
    border-color: #42a5f5;
  }
}

/* Tarjetas de documento con hover */
.documento-card {
  transition: all 0.3s ease;
}

.documento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

/* Vista previa de imagen con zoom */
.imagen-preview {
  cursor: zoom-in;
  transition: transform 0.2s;
}

.imagen-preview:hover {
  transform: scale(1.05);
}

/* Badge de tipo de documento */
.tipo-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 1;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* Loading overlay */
.documento-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* Responsive */
@media (max-width: 600px) {
  .documento-card {
    margin-bottom: 16px;
  }
  
  .dropzone {
    padding: 24px 16px;
  }
}
```

---

## 📊 Arquitectura de Archivos

```
src/
├── types/
│   └── documentos.types.ts           ✅ Tipos y constantes
├── services/
│   └── documentosService.ts          ✅ Servicio de API
├── components/
│   └── Documentos/
│       ├── SubirDocumento.tsx        ✅ Subida con drag & drop
│       ├── GaleriaDocumentos.tsx     ✅ Galería con filtros
│       └── GestionDocumentos.tsx     ✅ Integración completa
└── pages/
    └── odontologo/
        ├── HistorialDetalle.tsx      ✅ Con tab de documentos
        └── DocumentosClinico.tsx     ✅ Página independiente (opcional)
```

---

## ✅ Checklist de Implementación

### **Backend (ya está listo)**
- [x] ✅ Modelo `DocumentoClinico` creado
- [x] ✅ Endpoints de CRUD completos
- [x] ✅ Subida de archivos configurada
- [x] ✅ Endpoint de descarga funcionando
- [x] ✅ Filtros por tipo y episodio

### **Frontend (a implementar)**
- [ ] Crear tipos TypeScript (`documentos.types.ts`)
- [ ] Crear servicio de API (`documentosService.ts`)
- [ ] Crear componente `SubirDocumento.tsx`
- [ ] Crear componente `GaleriaDocumentos.tsx`
- [ ] Crear componente `GestionDocumentos.tsx`
- [ ] Integrar en `HistorialDetalle.tsx`
- [ ] Probar subida de imágenes
- [ ] Probar subida de PDFs
- [ ] Probar filtros y búsqueda
- [ ] Probar descarga de documentos
- [ ] Probar eliminación con confirmación
- [ ] Validar responsive design

---

## 🚀 Mejoras Futuras (Opcional)

### **Fase 2: Mejoras Avanzadas**

```typescript
// 1. Visor de Imágenes en Modal
- Zoom in/out
- Navegación entre imágenes
- Fullscreen
- Rotación de imagen

// 2. Visor de PDF Integrado
- react-pdf o PDF.js
- Navegación entre páginas
- Zoom
- Descarga desde el visor

// 3. Editor de Imágenes Básico
- Recortar
- Rotar
- Ajustar brillo/contraste
- Agregar anotaciones

// 4. Compartir Documentos
- Generar enlace temporal
- Enviar por email
- Exportar conjunto de documentos

// 5. Organización Avanzada
- Carpetas/categorías personalizadas
- Etiquetas
- Favoritos
- Ordenar por fecha, tipo, etc.
```

---

## 📚 Recursos Adicionales

### **Librerías Útiles (Opcional)**

```bash
# Para visor de PDF
npm install react-pdf

# Para editor de imágenes
npm install react-image-crop

# Para lightbox (galería con zoom)
npm install yet-another-react-lightbox
```

---

## 🎯 Resumen Final

Has implementado un sistema completo de gestión de documentos clínicos que incluye:

✅ **Subida de archivos:**
- Drag & drop
- Validación de tipo y tamaño
- Vista previa
- Categorización

✅ **Visualización:**
- Galería con cards
- Vista previa de imágenes
- Iconos para PDFs
- Filtros y búsqueda

✅ **Acciones:**
- Descargar documentos
- Eliminar con confirmación
- Información detallada

✅ **Integración:**
- En historial clínico
- Vinculación con episodios
- Actualización en tiempo real

---

## 🎉 **¡Sistema de Documentos Completo!**

**Tiempo estimado de implementación:** 3-4 días

**Resultado:** Sistema profesional de gestión documental para clínicas dentales, con todas las funcionalidades necesarias para manejar radiografías, recetas, consentimientos informados y documentación médica.

---

**¿Listo para implementar?** Tienes toda la guía paso a paso con código completo. ¡Comienza con los tipos y el servicio, luego los componentes! 🚀
