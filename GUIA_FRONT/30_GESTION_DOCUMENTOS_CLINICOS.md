# 📄 Guía Paso a Paso: Gestión de Documentos Clínicos

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Backend Disponible](#backend-disponible)
3. [Paso 1: Tipos TypeScript](#paso-1-tipos-typescript)
4. [Paso 2: Servicio de API](#paso-2-servicio-de-api)
5. [Paso 3: Componente de Subida](#paso-3-componente-de-subida)
6. [Paso 4: Galería de Documentos](#paso-4-galería-de-documentos)
7. [Paso 5: Visor de Imágenes](#paso-5-visor-de-imágenes)
8. [Paso 6: Visor de PDFs](#paso-6-visor-de-pdfs)
9. [Paso 7: Integración](#paso-7-integración)
10. [Pruebas](#pruebas)

---

## 📖 Descripción General

La **Gestión de Documentos Clínicos** permite al odontólogo:

### Funcionalidades:
- 📤 **Subir documentos**: Radiografías, PDFs, recetas, consentimientos
- 🖼️ **Galería de imágenes**: Vista previa de radiografías
- 📄 **Visor de PDFs**: Ver documentos sin descargar
- 🏷️ **Categorización**: Por tipo de documento
- 🔍 **Búsqueda**: Filtrar por nombre o tipo
- ⬇️ **Descargar**: Obtener archivo original
- 🗑️ **Eliminar**: Con confirmación de seguridad
- 📝 **Notas**: Agregar descripción a cada documento
- 🔗 **Vincular**: Con episodios específicos de atención

**Estado Backend:** ✅ **100% LISTO** - Modelo y endpoints completos

---

## 🔌 Backend Disponible

### Endpoints ya implementados:

#### 1. Subir Documento
```http
POST /api/historial/historiales/{historial_id}/documentos/
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```javascript
{
  archivo: File,           // Archivo (imagen o PDF)
  tipo: string,           // "radiografia" | "receta" | "consentimiento" | "informe" | "otro"
  descripcion: string,    // Descripción del documento
  episodio: number       // ID del episodio (opcional)
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "historial_clinico": 123,
  "tipo": "radiografia",
  "archivo": "/media/documentos_clinicos/123/radiografia_2025-11-10_abc123.jpg",
  "descripcion": "Radiografía panorámica inicial",
  "episodio": 5,
  "episodio_info": {
    "id": 5,
    "fecha": "2025-11-10",
    "motivo": "Primera consulta"
  },
  "fecha_subida": "2025-11-10T10:30:00Z",
  "nombre_archivo": "radiografia_2025-11-10_abc123.jpg",
  "tamano_bytes": 2456789
}
```

#### 2. Listar Documentos
```http
GET /api/historial/historiales/{historial_id}/documentos/
```

**Query Params (opcionales):**
- `?tipo=radiografia` - Filtrar por tipo
- `?episodio=5` - Filtrar por episodio

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "tipo": "radiografia",
    "archivo": "/media/documentos_clinicos/123/radiografia.jpg",
    "descripcion": "Radiografía panorámica",
    "episodio": 5,
    "episodio_info": {...},
    "fecha_subida": "2025-11-10T10:30:00Z",
    "nombre_archivo": "radiografia.jpg",
    "tamano_bytes": 2456789
  }
]
```

#### 3. Obtener Detalle de Documento
```http
GET /api/historial/documentos/{documento_id}/
```

#### 4. Descargar Documento
```http
GET /api/historial/documentos/{documento_id}/descargar/
```

**Response:** Archivo para descargar

#### 5. Eliminar Documento
```http
DELETE /api/historial/documentos/{documento_id}/
```

**Response (204 No Content)**

---

## 🔧 Paso 1: Tipos TypeScript

### **Archivo:** `src/types/documentos.types.ts`

```typescript
/**
 * Tipos para Gestión de Documentos Clínicos
 */

// Tipos de documento
export type TipoDocumento = 
  | 'radiografia'
  | 'receta'
  | 'consentimiento'
  | 'informe'
  | 'otro';

// Información de episodio
export interface EpisodioInfo {
  id: number;
  fecha: string;
  motivo: string;
}

// Documento clínico
export interface DocumentoClinico {
  id: number;
  historial_clinico: number;
  tipo: TipoDocumento;
  archivo: string; // URL del archivo
  descripcion: string;
  episodio?: number;
  episodio_info?: EpisodioInfo;
  fecha_subida: string; // ISO string
  nombre_archivo: string;
  tamano_bytes: number;
}

// Datos para subir documento
export interface SubirDocumentoData {
  archivo: File;
  tipo: TipoDocumento;
  descripcion: string;
  episodio?: number;
}

// Filtros de búsqueda
export interface FiltrosDocumentos {
  tipo?: TipoDocumento;
  episodio?: number;
  busqueda?: string;
}

// Configuración de tipos
export const TIPOS_DOCUMENTO: Record<TipoDocumento, string> = {
  radiografia: 'Radiografía',
  receta: 'Receta Médica',
  consentimiento: 'Consentimiento Informado',
  informe: 'Informe Médico',
  otro: 'Otro Documento'
};

// Colores por tipo
export const COLORES_TIPO: Record<TipoDocumento, string> = {
  radiografia: '#2196F3',   // Azul
  receta: '#4CAF50',        // Verde
  consentimiento: '#FF9800', // Naranja
  informe: '#9C27B0',       // Púrpura
  otro: '#607D8B'           // Gris
};

// Iconos por tipo (Material-UI)
export const ICONOS_TIPO: Record<TipoDocumento, string> = {
  radiografia: 'CameraAlt',
  receta: 'Receipt',
  consentimiento: 'Gavel',
  informe: 'Description',
  otro: 'InsertDriveFile'
};

// Extensiones permitidas
export const EXTENSIONES_PERMITIDAS = {
  imagenes: ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
  documentos: ['.pdf'],
  todos: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf']
};

// Tamaño máximo de archivo (10 MB)
export const TAMANO_MAXIMO_MB = 10;
export const TAMANO_MAXIMO_BYTES = TAMANO_MAXIMO_MB * 1024 * 1024;

/**
 * Verifica si un archivo es una imagen
 */
export const esImagen = (nombreArchivo: string): boolean => {
  const extension = nombreArchivo.toLowerCase().substring(nombreArchivo.lastIndexOf('.'));
  return EXTENSIONES_PERMITIDAS.imagenes.includes(extension);
};

/**
 * Verifica si un archivo es un PDF
 */
export const esPDF = (nombreArchivo: string): boolean => {
  return nombreArchivo.toLowerCase().endsWith('.pdf');
};

/**
 * Formatea el tamaño de archivo en formato legible
 */
export const formatearTamano = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Valida un archivo antes de subirlo
 */
export const validarArchivo = (archivo: File): { valido: boolean; error?: string } => {
  // Validar tamaño
  if (archivo.size > TAMANO_MAXIMO_BYTES) {
    return {
      valido: false,
      error: `El archivo es demasiado grande. Máximo ${TAMANO_MAXIMO_MB} MB.`
    };
  }
  
  // Validar extensión
  const extension = archivo.name.toLowerCase().substring(archivo.name.lastIndexOf('.'));
  if (!EXTENSIONES_PERMITIDAS.todos.includes(extension)) {
    return {
      valido: false,
      error: 'Tipo de archivo no permitido. Solo se permiten imágenes y PDFs.'
    };
  }
  
  return { valido: true };
};
```

---

## 🔧 Paso 2: Servicio de API

### **Archivo:** `src/services/documentosService.ts`

```typescript
import apiClient from './axios';
import {
  DocumentoClinico,
  SubirDocumentoData,
  FiltrosDocumentos
} from '../types/documentos.types';

/**
 * Servicio para gestión de documentos clínicos
 */
const documentosService = {
  /**
   * Sube un nuevo documento al historial clínico
   * @param historialId - ID del historial clínico
   * @param data - Datos del documento (archivo, tipo, descripción, episodio)
   * @returns Promesa con el documento creado
   */
  async subirDocumento(
    historialId: number,
    data: SubirDocumentoData
  ): Promise<DocumentoClinico> {
    try {
      console.log('📤 Subiendo documento al historial:', historialId);
      console.log('📄 Tipo:', data.tipo);
      console.log('📝 Descripción:', data.descripcion);
      console.log('📁 Archivo:', data.archivo.name, '-', data.archivo.size, 'bytes');

      // Crear FormData
      const formData = new FormData();
      formData.append('archivo', data.archivo);
      formData.append('tipo', data.tipo);
      formData.append('descripcion', data.descripcion);
      
      if (data.episodio) {
        formData.append('episodio', data.episodio.toString());
      }

      // Hacer request con FormData
      const response = await apiClient.post(
        `/historial/historiales/${historialId}/documentos/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      console.log('✅ Documento subido exitosamente:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error al subir documento:', error);
      throw error;
    }
  },

  /**
   * Obtiene la lista de documentos de un historial clínico
   * @param historialId - ID del historial clínico
   * @param filtros - Filtros opcionales (tipo, episodio)
   * @returns Promesa con array de documentos
   */
  async listarDocumentos(
    historialId: number,
    filtros?: FiltrosDocumentos
  ): Promise<DocumentoClinico[]> {
    try {
      console.log('📋 Listando documentos del historial:', historialId);
      
      const params = new URLSearchParams();
      
      if (filtros?.tipo) {
        params.append('tipo', filtros.tipo);
      }
      
      if (filtros?.episodio) {
        params.append('episodio', filtros.episodio.toString());
      }

      const url = `/historial/historiales/${historialId}/documentos/${
        params.toString() ? '?' + params.toString() : ''
      }`;

      const response = await apiClient.get(url);
      
      console.log('✅ Documentos obtenidos:', response.data.length);
      return response.data;
    } catch (error) {
      console.error('❌ Error al listar documentos:', error);
      throw error;
    }
  },

  /**
   * Obtiene el detalle de un documento específico
   * @param documentoId - ID del documento
   * @returns Promesa con los datos del documento
   */
  async obtenerDocumento(documentoId: number): Promise<DocumentoClinico> {
    try {
      const response = await apiClient.get(`/historial/documentos/${documentoId}/`);
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener documento:', error);
      throw error;
    }
  },

  /**
   * Descarga un documento
   * @param documentoId - ID del documento
   * @returns Promesa con el Blob del archivo
   */
  async descargarDocumento(documentoId: number): Promise<Blob> {
    try {
      console.log('⬇️ Descargando documento:', documentoId);
      
      const response = await apiClient.get(
        `/historial/documentos/${documentoId}/descargar/`,
        {
          responseType: 'blob'
        }
      );
      
      console.log('✅ Documento descargado');
      return response.data;
    } catch (error) {
      console.error('❌ Error al descargar documento:', error);
      throw error;
    }
  },

  /**
   * Elimina un documento
   * @param documentoId - ID del documento
   * @returns Promesa sin contenido
   */
  async eliminarDocumento(documentoId: number): Promise<void> {
    try {
      console.log('🗑️ Eliminando documento:', documentoId);
      
      await apiClient.delete(`/historial/documentos/${documentoId}/`);
      
      console.log('✅ Documento eliminado exitosamente');
    } catch (error) {
      console.error('❌ Error al eliminar documento:', error);
      throw error;
    }
  },

  /**
   * Obtiene la URL completa de un archivo
   * @param rutaArchivo - Ruta relativa del archivo
   * @returns URL completa
   */
  obtenerUrlArchivo(rutaArchivo: string): string {
    // Si la ruta ya es una URL completa, devolverla
    if (rutaArchivo.startsWith('http')) {
      return rutaArchivo;
    }
    
    // Obtener base URL del backend
    const baseURL = apiClient.defaults.baseURL || 'http://localhost:8000';
    
    // Construir URL completa
    return `${baseURL}${rutaArchivo}`;
  }
};

export default documentosService;
```

---

*Continúa en la siguiente parte con los componentes visuales...*

## 📚 Próximos Pasos

En las siguientes partes veremos:
- **Parte 2**: Componente de subida de archivos con drag & drop
- **Parte 3**: Galería de documentos con vista previa
- **Parte 4**: Visores de imágenes y PDFs
- **Parte 5**: Integración completa y pruebas
