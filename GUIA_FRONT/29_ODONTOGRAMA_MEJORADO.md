# 🦷 Guía: Odontograma Mejorado con Configuración Dinámica

## 📋 Resumen

Se agregó un nuevo endpoint `/api/historial/odontogramas/configuracion/` que proporciona toda la estructura del odontograma para el frontend, facilitando la implementación visual.

---

## 🎯 Nuevo Endpoint: Configuración del Odontograma

### **GET** `/api/historial/odontogramas/configuracion/`

**No requiere parámetros** - Solo autenticación

**Respuesta:**

```json
{
  "nomenclatura": "FDI",
  "sistema": "Internacional (FDI)",
  "total_dientes_adulto": 32,
  "total_dientes_nino": 20,
  
  "cuadrantes": {
    "1": {
      "numero": 1,
      "nombre": "Superior Derecho",
      "posicion": "top-right",
      "arcada": "superior",
      "lado": "derecho",
      "dientes": [
        {"numero": "18", "nombre": "Tercer Molar", "posicion": 8, "tipo": "molar"},
        {"numero": "17", "nombre": "Segundo Molar", "posicion": 7, "tipo": "molar"},
        // ... 8 dientes por cuadrante
      ]
    }
    // ... 4 cuadrantes
  },
  
  "estados": [
    {
      "valor": "sano",
      "etiqueta": "Sano",
      "color": "#10b981",
      "color_fondo": "#d1fae5",
      "icono": "✓"
    },
    {
      "valor": "caries",
      "etiqueta": "Caries",
      "color": "#ef4444",
      "color_fondo": "#fee2e2",
      "icono": "⚠"
    }
    // ... 11 estados disponibles
  ],
  
  "superficies": [
    {"valor": "oclusal", "etiqueta": "Oclusal", "abreviatura": "O"},
    {"valor": "mesial", "etiqueta": "Mesial", "abreviatura": "M"}
    // ... 6 superficies
  ],
  
  "materiales": [
    {"valor": "resina", "etiqueta": "Resina Compuesta"},
    {"valor": "amalgama", "etiqueta": "Amalgama"}
    // ... 8 materiales
  ],
  
  "ordenamiento_visual": {
    "superior_derecho": ["18", "17", "16", "15", "14", "13", "12", "11"],
    "superior_izquierdo": ["21", "22", "23", "24", "25", "26", "27", "28"],
    "inferior_derecho": ["48", "47", "46", "45", "44", "43", "42", "41"],
    "inferior_izquierdo": ["31", "32", "33", "34", "35", "36", "37", "38"]
  }
}
```

---

## 📊 Mejoras en el Serializer

El `OdontogramaSerializer` ahora incluye campos calculados:

```json
{
  "id": 1,
  "historial_clinico": 1,
  "fecha_snapshot": "2025-11-19T12:00:00Z",
  "estado_piezas": { /* ... */ },
  "notas": "Evaluación completa",
  
  // ✨ NUEVOS CAMPOS
  "total_dientes_registrados": 28,
  "resumen_estados": {
    "sano": 24,
    "caries": 2,
    "restaurado": 1,
    "extraido": 1
  },
  "paciente_info": {
    "id": 1,
    "nombre": "María García",
    "email": "maria@test.com"
  }
}
```

---

## 🎨 Implementación en React/TypeScript

### 1. Crear tipos TypeScript

```typescript
// types/odontograma.ts

export interface ConfiguracionOdontograma {
  nomenclatura: string;
  sistema: string;
  total_dientes_adulto: number;
  cuadrantes: {
    [key: string]: Cuadrante;
  };
  estados: EstadoDental[];
  superficies: Superficie[];
  materiales: Material[];
  ordenamiento_visual: OrdenamientoVisual;
}

export interface Cuadrante {
  numero: number;
  nombre: string;
  nombre_corto: string;
  posicion: 'top-right' | 'top-left' | 'bottom-left' | 'bottom-right';
  arcada: 'superior' | 'inferior';
  lado: 'derecho' | 'izquierdo';
  dientes: Diente[];
}

export interface Diente {
  numero: string;
  nombre: string;
  nombre_corto: string;
  posicion: number;
  tipo: 'molar' | 'premolar' | 'canino' | 'incisivo';
}

export interface EstadoDental {
  valor: string;
  etiqueta: string;
  color: string;
  color_fondo: string;
  icono: string;
  descripcion: string;
}

export interface Superficie {
  valor: string;
  etiqueta: string;
  descripcion: string;
  abreviatura: string;
}

export interface Material {
  valor: string;
  etiqueta: string;
}

export interface OrdenamientoVisual {
  superior_derecho: string[];
  superior_izquierdo: string[];
  inferior_derecho: string[];
  inferior_izquierdo: string[];
}

export interface EstadoPieza {
  estado: string;
  superficie?: string[];
  material?: string;
  notas?: string;
  fecha_extraccion?: string;
}

export interface Odontograma {
  id: number;
  historial_clinico: number;
  fecha_snapshot: string;
  estado_piezas: { [numero: string]: EstadoPieza };
  notas: string;
  total_dientes_registrados: number;
  resumen_estados: { [estado: string]: number };
  paciente_info: {
    id: number;
    nombre: string;
    email: string;
  };
}
```

### 2. Servicio para el odontograma

```typescript
// services/odontogramaService.ts

import axiosInstance from './axiosCore';
import { ConfiguracionOdontograma, Odontograma } from '../types/odontograma';

class OdontogramaService {
  private configuracion: ConfiguracionOdontograma | null = null;

  /**
   * Obtiene la configuración del odontograma (cachea el resultado)
   */
  async getConfiguracion(): Promise<ConfiguracionOdontograma> {
    if (this.configuracion) {
      return this.configuracion;
    }

    const response = await axiosInstance.get<ConfiguracionOdontograma>(
      '/historial/odontogramas/configuracion/'
    );
    
    this.configuracion = response.data;
    return this.configuracion;
  }

  /**
   * Lista todos los odontogramas
   */
  async listar(): Promise<Odontograma[]> {
    const response = await axiosInstance.get<Odontograma[]>(
      '/historial/odontogramas/'
    );
    return response.data;
  }

  /**
   * Obtiene un odontograma por ID
   */
  async obtenerPorId(id: number): Promise<Odontograma> {
    const response = await axiosInstance.get<Odontograma>(
      `/historial/odontogramas/${id}/`
    );
    return response.data;
  }

  /**
   * Crea un nuevo odontograma
   */
  async crear(data: {
    historial_clinico: number;
    estado_piezas: { [numero: string]: any };
    notas?: string;
  }): Promise<Odontograma> {
    const response = await axiosInstance.post<Odontograma>(
      '/historial/odontogramas/',
      data
    );
    return response.data;
  }

  /**
   * Actualiza un odontograma completo (PUT)
   */
  async actualizar(id: number, data: any): Promise<Odontograma> {
    const response = await axiosInstance.put<Odontograma>(
      `/historial/odontogramas/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Actualiza parcialmente un odontograma (PATCH)
   */
  async actualizarParcial(id: number, data: any): Promise<Odontograma> {
    const response = await axiosInstance.patch<Odontograma>(
      `/historial/odontogramas/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Duplica un odontograma para seguimiento
   */
  async duplicar(id: number): Promise<Odontograma> {
    const response = await axiosInstance.post<Odontograma>(
      `/historial/odontogramas/${id}/duplicar_odontograma/`
    );
    return response.data;
  }

  /**
   * Elimina un odontograma
   */
  async eliminar(id: number): Promise<void> {
    await axiosInstance.delete(`/historial/odontogramas/${id}/`);
  }
}

export default new OdontogramaService();
```

### 3. Hook personalizado para usar la configuración

```typescript
// hooks/useOdontogramaConfig.ts

import { useState, useEffect } from 'react';
import odontogramaService from '../services/odontogramaService';
import { ConfiguracionOdontograma } from '../types/odontograma';

export const useOdontogramaConfig = () => {
  const [config, setConfig] = useState<ConfiguracionOdontograma | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await odontogramaService.getConfiguracion();
        setConfig(data);
      } catch (err: any) {
        setError(err.message || 'Error al cargar configuración');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  return { config, loading, error };
};
```

### 4. Componente visual del odontograma

```typescript
// components/OdontogramaVisual.tsx

import React from 'react';
import { useOdontogramaConfig } from '../hooks/useOdontogramaConfig';
import { Odontograma, EstadoPieza } from '../types/odontograma';

interface Props {
  odontograma: Odontograma | null;
  onPiezaClick?: (numero: string, estadoActual: EstadoPieza | undefined) => void;
  editable?: boolean;
}

export const OdontogramaVisual: React.FC<Props> = ({
  odontograma,
  onPiezaClick,
  editable = false
}) => {
  const { config, loading, error } = useOdontogramaConfig();

  if (loading) return <div>Cargando configuración...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!config) return <div>No se pudo cargar la configuración</div>;

  const getEstadoPieza = (numero: string): EstadoPieza | undefined => {
    return odontograma?.estado_piezas[numero];
  };

  const getColorEstado = (estado: string | undefined): string => {
    if (!estado) return '#e5e7eb'; // Gris por defecto
    const estadoConfig = config.estados.find(e => e.valor === estado);
    return estadoConfig?.color_fondo || '#e5e7eb';
  };

  const renderDiente = (numero: string, nombre: string) => {
    const estadoPieza = getEstadoPieza(numero);
    const color = getColorEstado(estadoPieza?.estado);
    const estadoTexto = estadoPieza?.estado || 'sano';

    return (
      <div
        key={numero}
        className={`diente ${editable ? 'cursor-pointer' : ''}`}
        style={{
          backgroundColor: color,
          border: `2px solid ${getColorEstado(estadoPieza?.estado).replace('fae5', '0000')}`,
          borderRadius: '8px',
          padding: '12px',
          textAlign: 'center',
          minWidth: '70px',
          transition: 'all 0.2s'
        }}
        onClick={() => editable && onPiezaClick?.(numero, estadoPieza)}
      >
        <div className="font-bold text-lg">{numero}</div>
        <div className="text-xs text-gray-600">{nombre}</div>
        <div className="text-xs mt-1 font-semibold">
          {config.estados.find(e => e.valor === estadoTexto)?.etiqueta}
        </div>
        {estadoPieza?.superficie && estadoPieza.superficie.length > 0 && (
          <div className="text-xs text-gray-500 mt-1">
            {estadoPieza.superficie.map(s => 
              config.superficies.find(sf => sf.valor === s)?.abreviatura
            ).join('-')}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="odontograma-container p-6 bg-white rounded-lg shadow">
      {/* Superior Derecho */}
      <div className="mb-6">
        <h3 className="text-center font-bold mb-2">Superior Derecho</h3>
        <div className="flex gap-2 justify-center">
          {config.ordenamiento_visual.superior_derecho.map(numero => {
            const diente = config.cuadrantes["1"].dientes.find(d => d.numero === numero);
            return renderDiente(numero, diente?.nombre_corto || '');
          })}
        </div>
      </div>

      {/* Superior Izquierdo */}
      <div className="mb-6">
        <h3 className="text-center font-bold mb-2">Superior Izquierdo</h3>
        <div className="flex gap-2 justify-center">
          {config.ordenamiento_visual.superior_izquierdo.map(numero => {
            const diente = config.cuadrantes["2"].dientes.find(d => d.numero === numero);
            return renderDiente(numero, diente?.nombre_corto || '');
          })}
        </div>
      </div>

      <div className="border-t-2 border-gray-300 my-4"></div>

      {/* Inferior Izquierdo */}
      <div className="mb-6">
        <h3 className="text-center font-bold mb-2">Inferior Izquierdo</h3>
        <div className="flex gap-2 justify-center">
          {config.ordenamiento_visual.inferior_izquierdo.map(numero => {
            const diente = config.cuadrantes["3"].dientes.find(d => d.numero === numero);
            return renderDiente(numero, diente?.nombre_corto || '');
          })}
        </div>
      </div>

      {/* Inferior Derecho */}
      <div className="mb-6">
        <h3 className="text-center font-bold mb-2">Inferior Derecho</h3>
        <div className="flex gap-2 justify-center">
          {config.ordenamiento_visual.inferior_derecho.map(numero => {
            const diente = config.cuadrantes["4"].dientes.find(d => d.numero === numero);
            return renderDiente(numero, diente?.nombre_corto || '');
          })}
        </div>
      </div>

      {/* Leyenda de estados */}
      <div className="mt-6 pt-4 border-t">
        <h4 className="font-bold mb-2">Leyenda:</h4>
        <div className="flex flex-wrap gap-2">
          {config.estados.map(estado => (
            <div
              key={estado.valor}
              className="flex items-center gap-2 px-3 py-1 rounded"
              style={{ backgroundColor: estado.color_fondo }}
            >
              <span>{estado.icono}</span>
              <span className="text-sm">{estado.etiqueta}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Resumen de estados */}
      {odontograma && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <h4 className="font-bold mb-2">Resumen:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            {Object.entries(odontograma.resumen_estados).map(([estado, cantidad]) => {
              const estadoConfig = config.estados.find(e => e.valor === estado);
              return (
                <div key={estado} className="flex items-center gap-2">
                  <span style={{ color: estadoConfig?.color }}>●</span>
                  <span>{estadoConfig?.etiqueta}: {cantidad}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🔄 Flujo de Trabajo Completo

### 1. **Cargar configuración al inicio**
```typescript
// En App.tsx o layout principal
useEffect(() => {
  odontogramaService.getConfiguracion(); // Cachea la config
}, []);
```

### 2. **Crear odontograma**
```typescript
const crearOdontograma = async (historialId: number) => {
  const odontograma = await odontogramaService.crear({
    historial_clinico: historialId,
    estado_piezas: {
      "16": {
        estado: "caries",
        superficie: ["oclusal"],
        notas: "Caries profunda"
      }
      // Solo registrar dientes con problemas
    },
    notas: "Primera evaluación"
  });
};
```

### 3. **Editar odontograma**
```typescript
const actualizarPieza = async (
  odontogramaId: number,
  numeroPieza: string,
  nuevoEstado: EstadoPieza
) => {
  // Obtener odontograma actual
  const actual = await odontogramaService.obtenerPorId(odontogramaId);
  
  // Actualizar solo la pieza modificada
  await odontogramaService.actualizarParcial(odontogramaId, {
    estado_piezas: {
      ...actual.estado_piezas,
      [numeroPieza]: nuevoEstado
    }
  });
};
```

### 4. **Comparar evolución**
```typescript
const compararEvolucion = async (odontogramaAnteriorId: number) => {
  // Duplicar odontograma anterior
  const nuevo = await odontogramaService.duplicar(odontogramaAnteriorId);
  
  // Mostrar ambos para comparación
  return {
    anterior: await odontogramaService.obtenerPorId(odontogramaAnteriorId),
    actual: nuevo
  };
};
```

---

## ✅ Ventajas de Esta Implementación

1. **✅ Una sola fuente de verdad**: La configuración viene del backend
2. **✅ Fácil mantenimiento**: Cambios en estados/colores no requieren redeployar frontend
3. **✅ Internacionalización**: Fácil agregar idiomas
4. **✅ Consistencia**: Mismo sistema en todo el sistema
5. **✅ Performance**: La configuración se cachea en el servicio
6. **✅ Flexible**: Soporta nomenclatura FDI y futuros sistemas
7. **✅ Visual claro**: Los cuadrantes se organizan como se ven en la boca

---

## 📝 Notas Importantes

- **32 dientes adultos**: No confundir con 48 (que es el último número FDI)
- **Cuadrantes**: 4 cuadrantes × 8 dientes = 32 total
- **Nomenclatura FDI**: Primer dígito = cuadrante, segundo = posición
- **Dientes opcionales**: Solo registrar los que tienen condiciones especiales

---

## 🎉 Resultado Final

Con esta implementación, el frontend tendrá:
- ✅ Odontograma visual con 32 dientes
- ✅ Colores consistentes según el estado
- ✅ Edición fácil con modal por diente
- ✅ Comparación de evolución
- ✅ Resumen automático de estados
- ✅ Leyenda visual con todos los estados
