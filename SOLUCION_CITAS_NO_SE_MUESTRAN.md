# 🐛 SOLUCIÓN: Citas no se muestran en el frontend

**Fecha:** 15 de Noviembre, 2025  
**Problema:** La API devuelve 3 citas correctamente, el componente las recibe, pero NO se muestran en pantalla.

---

## 🔍 Diagnóstico

### ✅ Backend funciona correctamente

**Logs de la API:**
```
✅ Response: {status: 200, url: '/api/agenda/citas/?fecha_inicio=2025-11-15&ordering=fecha_hora&limit=3', data: Array(3)}
✅ Próximas citas: 3
✅ Próximas citas cargadas: 3
```

**Endpoint:** `GET /api/agenda/citas/?fecha_inicio=2025-11-15&ordering=fecha_hora&limit=3`

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "paciente": 104,
    "paciente_nombre": "María",
    "paciente_email": "paciente1@test.com",
    "odontologo": 103,
    "odontologo_nombre": "Juan",
    "odontologo_email": "odontologo@clinica-demo.com",
    "fecha_hora": "2025-11-15T10:00:00Z",
    "estado": "CONFIRMADA",
    "motivo_tipo": "LIMPIEZA",
    "motivo_tipo_display": "Limpieza Dental",
    "motivo": "Limpieza dental y revisión general",
    "observaciones": null,
    "precio_display": "$60.00",
    "es_cita_plan": false,
    "item_plan": null,
    "item_plan_info": null
  },
  {
    "id": 2,
    "fecha_hora": "2025-11-14T14:30:00Z",
    "estado": "ATENDIDA",
    "motivo_tipo": "REVISION",
    "...": "..."
  },
  {
    "id": 3,
    "fecha_hora": "2025-11-22T09:00:00Z",
    "estado": "PENDIENTE",
    "motivo_tipo": "CONSULTA",
    "...": "..."
  }
]
```

---

## ❌ Problema en Frontend

### Posibles causas

El componente `ProximasCitas.tsx` **recibe los datos pero no los renderiza**. Los problemas más comunes son:

#### 1. **Error en el mapeo de datos**

**Problema:** El componente espera campos con nombres diferentes a los que devuelve la API.

**Ejemplo de error:**
```typescript
// ❌ INCORRECTO - La API devuelve "odontologo_nombre", no "doctor_nombre"
<p>{cita.doctor_nombre}</p>

// ✅ CORRECTO
<p>{cita.odontologo_nombre}</p>
```

**Campos correctos de la API:**
- `id`
- `paciente_nombre` (NO `nombre_paciente`)
- `paciente_email`
- `odontologo_nombre` (NO `doctor_nombre` o `medico_nombre`)
- `fecha_hora` (NO `fecha` o `hora` separados)
- `estado`
- `motivo_tipo` (NO `tipo`)
- `motivo_tipo_display` (NO `tipo_display`)
- `motivo` (descripción larga)
- `precio_display` (NO `precio` como número)
- `es_cita_plan`
- `item_plan_info` (objeto completo del plan si existe)

#### 2. **Array vacío por condición incorrecta**

**Problema:** El componente filtra las citas con una condición que nunca se cumple.

**Ejemplo de error:**
```typescript
// ❌ INCORRECTO - Si la fecha viene como ISO string
const citasHoy = citas.filter(c => c.fecha === '2025-11-15');

// ✅ CORRECTO - Usar fecha_hora y comparar strings ISO
const citasHoy = citas.filter(c => c.fecha_hora.startsWith('2025-11-15'));
```

#### 3. **Estado no se actualiza**

**Problema:** El componente guarda las citas en el estado pero no se re-renderiza.

**Ejemplo de error:**
```typescript
// ❌ INCORRECTO - Mutar el estado directamente
citas.push(nuevaCita);

// ✅ CORRECTO - Crear nuevo array
setCitas([...citas, nuevaCita]);
```

#### 4. **Renderizado condicional bloqueado**

**Problema:** El componente tiene condiciones que impiden mostrar las citas.

**Ejemplo de error:**
```typescript
// ❌ INCORRECTO - Si loading nunca se pone en false
if (loading) return <Spinner />;
if (citas.length === 0) return <NoData />;

// ✅ CORRECTO - Verificar que loading sea false
{!loading && citas.length > 0 && (
  <ul>
    {citas.map(c => <CitaItem key={c.id} cita={c} />)}
  </ul>
)}
```

---

## 🔧 SOLUCIÓN

### Paso 1: Verificar estructura de datos

Agrega un `console.log` en el componente para ver exactamente qué datos llegan:

```typescript
// ProximasCitas.tsx

useEffect(() => {
  const cargarCitas = async () => {
    try {
      const data = await agendaService.obtenerProximasCitas();
      
      // 🔍 DEBUGGING - Ver estructura completa
      console.log('📊 Datos recibidos:', data);
      console.log('📊 Número de citas:', data.length);
      if (data.length > 0) {
        console.log('📊 Primera cita:', data[0]);
        console.log('📊 Campos disponibles:', Object.keys(data[0]));
      }
      
      setCitas(data);
    } catch (error) {
      console.error('❌ Error:', error);
    }
  };
  
  cargarCitas();
}, []);
```

### Paso 2: Verificar el render

Revisa que el componente esté mapeando correctamente:

```typescript
// ProximasCitas.tsx - Ejemplo CORRECTO

return (
  <div className="proximas-citas">
    <h2>Próximas Citas</h2>
    
    {/* Mostrar estado de carga */}
    {loading && <p>Cargando...</p>}
    
    {/* Mostrar errores */}
    {error && <p className="error">{error}</p>}
    
    {/* Mostrar citas */}
    {!loading && !error && citas.length === 0 && (
      <p>No tienes citas programadas</p>
    )}
    
    {!loading && !error && citas.length > 0 && (
      <ul className="lista-citas">
        {citas.map((cita) => (
          <li key={cita.id} className="cita-item">
            {/* ✅ Usar campos correctos de la API */}
            <div className="fecha">
              {new Date(cita.fecha_hora).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
            
            <div className="info">
              <p className="tipo">{cita.motivo_tipo_display}</p>
              <p className="motivo">{cita.motivo}</p>
              <p className="doctor">Dr. {cita.odontologo_nombre}</p>
            </div>
            
            <div className="estado">
              <span className={`badge ${cita.estado.toLowerCase()}`}>
                {cita.estado}
              </span>
            </div>
            
            {/* Mostrar precio si no es cita de plan */}
            {!cita.es_cita_plan && cita.precio_display && (
              <div className="precio">{cita.precio_display}</div>
            )}
            
            {/* Mostrar info del plan si existe */}
            {cita.item_plan_info && (
              <div className="plan-info">
                <small>📋 {cita.item_plan_info.plan_nombre}</small>
                <small>🦷 {cita.item_plan_info.servicio_nombre}</small>
              </div>
            )}
          </li>
        ))}
      </ul>
    )}
  </div>
);
```

### Paso 3: Verificar tipos TypeScript (si aplica)

Si usas TypeScript, asegúrate de que la interfaz coincida con la API:

```typescript
// types/cita.ts

export interface Cita {
  id: number;
  paciente: number;
  paciente_nombre: string;
  paciente_email: string;
  odontologo: number;
  odontologo_nombre: string;
  odontologo_email: string;
  odontologo_especialidad: string | null;
  fecha_hora: string;  // ISO 8601: "2025-11-15T10:00:00Z"
  motivo_tipo: string;  // "CONSULTA" | "LIMPIEZA" | "REVISION" | "URGENCIA" | "PLAN"
  motivo_tipo_display: string;  // "Limpieza Dental"
  motivo: string;
  observaciones: string | null;
  estado: string;  // "PENDIENTE" | "CONFIRMADA" | "ATENDIDA" | "CANCELADA"
  precio_display: string;  // "$60.00"
  es_cita_plan: boolean;
  item_plan: number | null;
  item_plan_info: ItemPlanInfo | null;
  creado: string;
  actualizado: string;
}

export interface ItemPlanInfo {
  id: number;
  servicio_id: number | null;
  servicio_nombre: string | null;
  servicio_descripcion: string | null;
  notas: string;
  precio_servicio: string;
  precio_materiales: string;
  precio_insumo: string;
  precio_total: string;
  estado: string;
  completado: boolean;
  plan_id: number;
  plan_nombre: string;
  paciente_nombre: string;
}
```

### Paso 4: Verificar el servicio

Revisa que `agendaService.ts` retorne los datos sin transformarlos:

```typescript
// agendaService.ts

export const obtenerProximasCitas = async (limit: number = 3): Promise<Cita[]> => {
  try {
    const hoy = new Date().toISOString().split('T')[0];
    
    const response = await api.get<Cita[]>('/api/agenda/citas/', {
      params: {
        fecha_inicio: hoy,
        ordering: 'fecha_hora',
        limit: limit
      }
    });
    
    console.log('✅ Próximas citas:', response.data.length);
    
    // ✅ Retornar los datos tal cual vienen de la API
    return response.data;
    
  } catch (error) {
    console.error('❌ Error al obtener citas:', error);
    throw error;
  }
};
```

---

## 🧪 PRUEBA

### 1. Probar en consola del navegador

Abre las DevTools (F12) y ejecuta:

```javascript
// Ver el estado del componente
console.log('Citas:', window.React.useState); // Si tienes React DevTools
```

### 2. Probar endpoint directo

Abre en el navegador (con sesión iniciada):

```
http://clinica-demo.localhost:8000/api/agenda/citas/?fecha_inicio=2025-11-15&ordering=fecha_hora&limit=3
```

Deberías ver el JSON con las 3 citas.

### 3. Probar con React DevTools

1. Instala React DevTools (extensión del navegador)
2. Abre el componente `ProximasCitas`
3. Revisa el estado `citas` - debería tener 3 elementos

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] ✅ La API devuelve 200 con datos (verificado en logs)
- [ ] ✅ El servicio recibe los datos sin errores
- [ ] ✅ El componente guarda las citas en el estado
- [ ] ❓ El componente mapea los campos correctos (`odontologo_nombre`, `fecha_hora`, etc.)
- [ ] ❓ El componente no tiene condiciones que bloqueen el render
- [ ] ❓ No hay errores en la consola del navegador
- [ ] ❓ El estado `loading` se pone en `false` después de cargar

---

## 🎯 PRÓXIMOS PASOS

1. **Abre el componente `ProximasCitas.tsx`** en tu proyecto frontend
2. **Agrega los console.log** del Paso 1
3. **Recarga la página** y abre la consola (F12)
4. **Revisa los logs** para ver qué estructura tienen los datos
5. **Compara** los campos que usas en el render con los que realmente vienen de la API
6. **Corrige** los nombres de campos si no coinciden

---

## 🔗 REFERENCIAS

**Backend:**
- Serializer: `agenda/serializers.py` → `CitaSerializer`
- Vista: `agenda/views.py` → `CitaViewSet.proximas()`

**Estructura de la Cita:**
```json
{
  "id": 1,
  "fecha_hora": "2025-11-15T10:00:00Z",
  "estado": "CONFIRMADA",
  "motivo_tipo": "LIMPIEZA",
  "motivo_tipo_display": "Limpieza Dental",
  "motivo": "Limpieza dental y revisión general",
  "paciente_nombre": "María",
  "odontologo_nombre": "Juan",
  "precio_display": "$60.00",
  "es_cita_plan": false,
  "item_plan_info": null
}
```

---

**💡 RESUMEN:** El backend funciona perfectamente. El problema está en el frontend - probablemente en los nombres de campos o condiciones de renderizado.

**📅 Última actualización:** 15 de Noviembre, 2025
