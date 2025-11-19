# 🦷 Guía Paso a Paso: Odontograma Interactivo

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Backend Disponible](#backend-disponible)
3. [Paso 1: Tipos TypeScript](#paso-1-tipos-typescript)
4. [Paso 2: Constantes y Configuración](#paso-2-constantes-y-configuración)
5. [Paso 3: Servicio de API](#paso-3-servicio-de-api)
6. [Paso 4: Componente de Pieza Dental](#paso-4-componente-de-pieza-dental)
7. [Paso 5: Componente de Odontograma](#paso-5-componente-de-odontograma)
8. [Paso 6: Modal de Edición de Pieza](#paso-6-modal-de-edición-de-pieza)
9. [Paso 7: Integración](#paso-7-integración)

---

## 📖 Descripción General

El **Odontograma Interactivo** permite visualizar y editar el estado dental de los pacientes:

### Características:
- 🦷 **32 piezas dentales** (adulto) o 20 (niño)
- 🎨 **Colores por estado**: Sano, caries, restaurado, corona, endodoncia, extraído
- 📝 **Notas por pieza**: Agregar observaciones específicas
- 🔍 **Nomenclatura FDI**: Estándar internacional
- 📊 **Historial**: Ver evolución en el tiempo
- 📄 **Exportar**: PDF con el odontograma
- 🔗 **Vincular**: Con episodios de atención

**Estado Backend:** ✅ **100% LISTO** - Modelo y endpoints completos

---

## 🔌 Backend Disponible

### Endpoints ya implementados:

#### 1. Listar Odontogramas
```http
GET /api/historial/odontogramas/?historial_clinico=123
```

**Response:**
```json
[
  {
    "id": 1,
    "historial_clinico": 123,
    "fecha": "2025-11-10",
    "tipo_denticion": "ADULTO",
    "estado_piezas": {
      "11": {"estado": "sano", "notas": ""},
      "12": {"estado": "caries", "superficie": ["oclusal"], "notas": "Caries leve"},
      "21": {"estado": "restaurado", "material": "resina", "notas": "Restaurado en 2024"}
    },
    "notas_generales": "Primera evaluación del paciente",
    "odontologo": 3,
    "odontologo_nombre": "Dr. Juan Pérez"
  }
]
```

#### 2. Crear Odontograma
```http
POST /api/historial/odontogramas/
```

**Request Body:**
```json
{
  "historial_clinico": 123,
  "tipo_denticion": "ADULTO",
  "estado_piezas": {
    "11": {"estado": "sano"},
    "12": {"estado": "caries", "superficie": ["oclusal"]},
    "13": {"estado": "sano"}
  },
  "notas_generales": "Evaluación inicial"
}
```

#### 3. Actualizar Odontograma
```http
PUT /api/historial/odontogramas/{id}/
```

#### 4. Duplicar Odontograma
```http
POST /api/historial/odontogramas/{id}/duplicar/
```

---

## 🔧 Paso 1: Tipos TypeScript

### **Archivo:** `src/types/odontograma.types.ts`

```typescript
/**
 * Tipos para el Odontograma Interactivo
 */

// Tipo de dentición
export type TipoDenticion = 'ADULTO' | 'NIÑO';

// Estados posibles de una pieza dental
export type EstadoPieza = 
  | 'sano'
  | 'caries'
  | 'restaurado'
  | 'corona'
  | 'endodoncia'
  | 'extraido'
  | 'ausente'
  | 'implante'
  | 'protesis'
  | 'fractura';

// Superficies dentales (para marcar ubicación)
export type SuperficieDental = 
  | 'oclusal'    // Superficie de masticación
  | 'mesial'     // Lado hacia el centro
  | 'distal'     // Lado hacia afuera
  | 'vestibular' // Lado hacia labios/mejillas
  | 'lingual'    // Lado hacia lengua/paladar
  | 'palatino';  // Lado hacia paladar (dientes superiores)

// Materiales de restauración
export type MaterialRestauracion = 
  | 'resina'
  | 'amalgama'
  | 'porcelana'
  | 'oro'
  | 'zirconio'
  | 'otro';

// Estado de una pieza dental individual
export interface EstadoPiezaDental {
  estado: EstadoPieza;
  superficie?: SuperficieDental[]; // Superficies afectadas
  material?: MaterialRestauracion; // Si es restauración
  notas?: string; // Observaciones específicas
}

// Odontograma completo
export interface Odontograma {
  id?: number;
  historial_clinico: number;
  fecha: string; // ISO date
  tipo_denticion: TipoDenticion;
  estado_piezas: Record<string, EstadoPiezaDental>; // Key: número pieza (FDI)
  notas_generales?: string;
  odontologo?: number;
  odontologo_nombre?: string;
  creado?: string;
  actualizado?: string;
}

// Nomenclatura FDI (Federation Dentaire Internationale)
export interface PiezaFDI {
  numero: string; // "11", "12", etc.
  nombre: string; // "Incisivo central superior derecho"
  cuadrante: 1 | 2 | 3 | 4; // Cuadrante dental
  posicion: number; // Posición en el cuadrante (1-8)
  tipo: 'incisivo' | 'canino' | 'premolar' | 'molar';
}

// Configuración de colores por estado
export const COLORES_ESTADO: Record<EstadoPieza, string> = {
  sano: '#81C784',         // Verde claro
  caries: '#E57373',       // Rojo claro
  restaurado: '#64B5F6',   // Azul claro
  corona: '#FFD54F',       // Amarillo
  endodoncia: '#BA68C8',   // Púrpura
  extraido: '#757575',     // Gris
  ausente: '#BDBDBD',      // Gris claro
  implante: '#4DB6AC',     // Turquesa
  protesis: '#FF8A65',     // Naranja
  fractura: '#F06292'      // Rosa
};

// Íconos por estado (emojis)
export const ICONOS_ESTADO: Record<EstadoPieza, string> = {
  sano: '✓',
  caries: '⚠',
  restaurado: '🔧',
  corona: '👑',
  endodoncia: '🔴',
  extraido: '✕',
  ausente: '○',
  implante: '⚙',
  protesis: '🦷',
  fractura: '⚡'
};

// Descripciones de estados
export const DESCRIPCIONES_ESTADO: Record<EstadoPieza, string> = {
  sano: 'Diente sano, sin hallazgos',
  caries: 'Caries dental activa',
  restaurado: 'Restauración previa',
  corona: 'Corona o funda dental',
  endodoncia: 'Tratamiento de conducto',
  extraido: 'Pieza extraída',
  ausente: 'Ausente congénita',
  implante: 'Implante dental',
  protesis: 'Prótesis dental',
  fractura: 'Fractura dental'
};
```

---

## 🔧 Paso 2: Constantes y Configuración

### **Archivo:** `src/constants/odontograma.constants.ts`

```typescript
import { PiezaFDI } from '../types/odontograma.types';

/**
 * Nomenclatura FDI completa para dentición adulta (32 piezas)
 * 
 * Cuadrantes:
 * 1: Superior derecho (11-18)
 * 2: Superior izquierdo (21-28)
 * 3: Inferior izquierdo (31-38)
 * 4: Inferior derecho (41-48)
 */
export const PIEZAS_ADULTO: PiezaFDI[] = [
  // Cuadrante 1 (Superior derecho)
  { numero: '18', nombre: 'Tercer molar superior derecho', cuadrante: 1, posicion: 8, tipo: 'molar' },
  { numero: '17', nombre: 'Segundo molar superior derecho', cuadrante: 1, posicion: 7, tipo: 'molar' },
  { numero: '16', nombre: 'Primer molar superior derecho', cuadrante: 1, posicion: 6, tipo: 'molar' },
  { numero: '15', nombre: 'Segundo premolar superior derecho', cuadrante: 1, posicion: 5, tipo: 'premolar' },
  { numero: '14', nombre: 'Primer premolar superior derecho', cuadrante: 1, posicion: 4, tipo: 'premolar' },
  { numero: '13', nombre: 'Canino superior derecho', cuadrante: 1, posicion: 3, tipo: 'canino' },
  { numero: '12', nombre: 'Incisivo lateral superior derecho', cuadrante: 1, posicion: 2, tipo: 'incisivo' },
  { numero: '11', nombre: 'Incisivo central superior derecho', cuadrante: 1, posicion: 1, tipo: 'incisivo' },
  
  // Cuadrante 2 (Superior izquierdo)
  { numero: '21', nombre: 'Incisivo central superior izquierdo', cuadrante: 2, posicion: 1, tipo: 'incisivo' },
  { numero: '22', nombre: 'Incisivo lateral superior izquierdo', cuadrante: 2, posicion: 2, tipo: 'incisivo' },
  { numero: '23', nombre: 'Canino superior izquierdo', cuadrante: 2, posicion: 3, tipo: 'canino' },
  { numero: '24', nombre: 'Primer premolar superior izquierdo', cuadrante: 2, posicion: 4, tipo: 'premolar' },
  { numero: '25', nombre: 'Segundo premolar superior izquierdo', cuadrante: 2, posicion: 5, tipo: 'premolar' },
  { numero: '26', nombre: 'Primer molar superior izquierdo', cuadrante: 2, posicion: 6, tipo: 'molar' },
  { numero: '27', nombre: 'Segundo molar superior izquierdo', cuadrante: 2, posicion: 7, tipo: 'molar' },
  { numero: '28', nombre: 'Tercer molar superior izquierdo', cuadrante: 2, posicion: 8, tipo: 'molar' },
  
  // Cuadrante 3 (Inferior izquierdo)
  { numero: '38', nombre: 'Tercer molar inferior izquierdo', cuadrante: 3, posicion: 8, tipo: 'molar' },
  { numero: '37', nombre: 'Segundo molar inferior izquierdo', cuadrante: 3, posicion: 7, tipo: 'molar' },
  { numero: '36', nombre: 'Primer molar inferior izquierdo', cuadrante: 3, posicion: 6, tipo: 'molar' },
  { numero: '35', nombre: 'Segundo premolar inferior izquierdo', cuadrante: 3, posicion: 5, tipo: 'premolar' },
  { numero: '34', nombre: 'Primer premolar inferior izquierdo', cuadrante: 3, posicion: 4, tipo: 'premolar' },
  { numero: '33', nombre: 'Canino inferior izquierdo', cuadrante: 3, posicion: 3, tipo: 'canino' },
  { numero: '32', nombre: 'Incisivo lateral inferior izquierdo', cuadrante: 3, posicion: 2, tipo: 'incisivo' },
  { numero: '31', nombre: 'Incisivo central inferior izquierdo', cuadrante: 3, posicion: 1, tipo: 'incisivo' },
  
  // Cuadrante 4 (Inferior derecho)
  { numero: '41', nombre: 'Incisivo central inferior derecho', cuadrante: 4, posicion: 1, tipo: 'incisivo' },
  { numero: '42', nombre: 'Incisivo lateral inferior derecho', cuadrante: 4, posicion: 2, tipo: 'incisivo' },
  { numero: '43', nombre: 'Canino inferior derecho', cuadrante: 4, posicion: 3, tipo: 'canino' },
  { numero: '44', nombre: 'Primer premolar inferior derecho', cuadrante: 4, posicion: 4, tipo: 'premolar' },
  { numero: '45', nombre: 'Segundo premolar inferior derecho', cuadrante: 4, posicion: 5, tipo: 'premolar' },
  { numero: '46', nombre: 'Primer molar inferior derecho', cuadrante: 4, posicion: 6, tipo: 'molar' },
  { numero: '47', nombre: 'Segundo molar inferior derecho', cuadrante: 4, posicion: 7, tipo: 'molar' },
  { numero: '48', nombre: 'Tercer molar inferior derecho', cuadrante: 4, posicion: 8, tipo: 'molar' }
];

/**
 * Nomenclatura para dentición temporal (niños - 20 piezas)
 * 
 * Cuadrantes:
 * 5: Superior derecho (51-55)
 * 6: Superior izquierdo (61-65)
 * 7: Inferior izquierdo (71-75)
 * 8: Inferior derecho (81-85)
 */
export const PIEZAS_NINO: PiezaFDI[] = [
  // Cuadrante 5 (Superior derecho)
  { numero: '55', nombre: 'Segundo molar temporal superior derecho', cuadrante: 1, posicion: 5, tipo: 'molar' },
  { numero: '54', nombre: 'Primer molar temporal superior derecho', cuadrante: 1, posicion: 4, tipo: 'molar' },
  { numero: '53', nombre: 'Canino temporal superior derecho', cuadrante: 1, posicion: 3, tipo: 'canino' },
  { numero: '52', nombre: 'Incisivo lateral temporal superior derecho', cuadrante: 1, posicion: 2, tipo: 'incisivo' },
  { numero: '51', nombre: 'Incisivo central temporal superior derecho', cuadrante: 1, posicion: 1, tipo: 'incisivo' },
  
  // Cuadrante 6 (Superior izquierdo)
  { numero: '61', nombre: 'Incisivo central temporal superior izquierdo', cuadrante: 2, posicion: 1, tipo: 'incisivo' },
  { numero: '62', nombre: 'Incisivo lateral temporal superior izquierdo', cuadrante: 2, posicion: 2, tipo: 'incisivo' },
  { numero: '63', nombre: 'Canino temporal superior izquierdo', cuadrante: 2, posicion: 3, tipo: 'canino' },
  { numero: '64', nombre: 'Primer molar temporal superior izquierdo', cuadrante: 2, posicion: 4, tipo: 'molar' },
  { numero: '65', nombre: 'Segundo molar temporal superior izquierdo', cuadrante: 2, posicion: 5, tipo: 'molar' },
  
  // Cuadrante 7 (Inferior izquierdo)
  { numero: '75', nombre: 'Segundo molar temporal inferior izquierdo', cuadrante: 3, posicion: 5, tipo: 'molar' },
  { numero: '74', nombre: 'Primer molar temporal inferior izquierdo', cuadrante: 3, posicion: 4, tipo: 'molar' },
  { numero: '73', nombre: 'Canino temporal inferior izquierdo', cuadrante: 3, posicion: 3, tipo: 'canino' },
  { numero: '72', nombre: 'Incisivo lateral temporal inferior izquierdo', cuadrante: 3, posicion: 2, tipo: 'incisivo' },
  { numero: '71', nombre: 'Incisivo central temporal inferior izquierdo', cuadrante: 3, posicion: 1, tipo: 'incisivo' },
  
  // Cuadrante 8 (Inferior derecho)
  { numero: '81', nombre: 'Incisivo central temporal inferior derecho', cuadrante: 4, posicion: 1, tipo: 'incisivo' },
  { numero: '82', nombre: 'Incisivo lateral temporal inferior derecho', cuadrante: 4, posicion: 2, tipo: 'incisivo' },
  { numero: '83', nombre: 'Canino temporal inferior derecho', cuadrante: 4, posicion: 3, tipo: 'canino' },
  { numero: '84', nombre: 'Primer molar temporal inferior derecho', cuadrante: 4, posicion: 4, tipo: 'molar' },
  { numero: '85', nombre: 'Segundo molar temporal inferior derecho', cuadrante: 4, posicion: 5, tipo: 'molar' }
];

/**
 * Obtiene las piezas según el tipo de dentición
 */
export const obtenerPiezasPorTipo = (tipo: 'ADULTO' | 'NIÑO'): PiezaFDI[] => {
  return tipo === 'ADULTO' ? PIEZAS_ADULTO : PIEZAS_NINO;
};

/**
 * Agrupa las piezas por cuadrante
 */
export const agruparPorCuadrante = (piezas: PiezaFDI[]) => {
  const cuadrante1 = piezas.filter(p => p.cuadrante === 1);
  const cuadrante2 = piezas.filter(p => p.cuadrante === 2);
  const cuadrante3 = piezas.filter(p => p.cuadrante === 3);
  const cuadrante4 = piezas.filter(p => p.cuadrante === 4);

  return {
    superior: [...cuadrante1.reverse(), ...cuadrante2],
    inferior: [...cuadrante4.reverse(), ...cuadrante3]
  };
};
```

---

*Continuará en la siguiente parte con los componentes visuales...*

## 📚 Próximos Archivos

- Parte 2: Servicio de API y Componente de Pieza Dental
- Parte 3: Componente de Odontograma Completo
- Parte 4: Modal de Edición y Integración
