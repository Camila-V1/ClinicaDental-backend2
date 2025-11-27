# 🎯 Ejemplos de Uso: Comandos de Voz

## 📢 Comandos Soportados

---

## 1️⃣ REPORTES DE CITAS

### Rangos Exactos
```
"Dame las citas del 1 al 5 de septiembre"
"Mostrar citas del 10 al 15 de noviembre"
"Citas entre el 20 y el 25 de diciembre"
```

**Resultado esperado:**
- Tipo: `citas`
- Fecha inicio: `2025-09-01`
- Fecha fin: `2025-09-05`
- Datos: Lista de citas en ese rango exacto

---

### Rangos Relativos
```
"Citas de esta semana"
"Dame las citas de la semana pasada"
"Mostrar citas del mes actual"
"Citas del mes pasado"
```

**Resultado esperado:**
- Tipo: `citas`
- Fechas calculadas automáticamente según la fecha actual
- Ejemplo: Si hoy es 27/11/2025:
  - "esta semana" → 25/11/2025 al 01/12/2025 (lunes a domingo)
  - "semana pasada" → 18/11/2025 al 24/11/2025

---

### Fechas Simples
```
"Citas de hoy"
"Mostrar citas de ayer"
```

**Resultado esperado:**
- Tipo: `citas`
- Fecha única convertida a rango de 1 día

---

### Con Filtros Adicionales
```
"Citas confirmadas de esta semana"
"Dame las citas pendientes del mes pasado"
"Citas canceladas del 1 al 10 de octubre"
"Mostrar citas de Juan Pérez en septiembre"
```

**Resultado esperado:**
- Tipo: `citas`
- Filtros aplicados: `estado`, `paciente_nombre`

---

## 2️⃣ REPORTES DE FACTURAS

### Básicos
```
"Facturas de septiembre"
"Dame las facturas del mes pasado"
"Mostrar facturas de esta semana"
"Facturas del 1 al 15 de octubre"
```

**Resultado esperado:**
- Tipo: `facturas`
- Fechas interpretadas correctamente
- Campos: id, numero, fecha, paciente, total, pagado, saldo, estado

---

### Con Estado
```
"Facturas pendientes de este mes"
"Dame las facturas pagadas de septiembre"
"Mostrar facturas anuladas del mes pasado"
```

**Resultado esperado:**
- Tipo: `facturas`
- Filtro: `estado='PENDIENTE'` / `'PAGADA'` / `'ANULADA'`

---

### Con Monto
```
"Facturas mayores a 1000 del mes pasado"
"Dame facturas de más de 500 en septiembre"
"Mostrar facturas entre 1000 y 5000 de octubre"
```

**Resultado esperado:**
- Tipo: `facturas`
- Filtros: `monto_minimo=1000`, `monto_maximo=5000`

---

## 3️⃣ REPORTES DE TRATAMIENTOS

### Básicos
```
"Planes de tratamiento de septiembre"
"Dame los tratamientos del mes pasado"
"Mostrar planes del 1 al 30 de octubre"
"Tratamientos de esta semana"
```

**Resultado esperado:**
- Tipo: `tratamientos`
- Datos: planes con paciente, odontólogo, título, estado, total

---

### Con Estado
```
"Planes de tratamiento en progreso"
"Dame los tratamientos completados de septiembre"
"Mostrar planes propuestos del mes actual"
```

**Resultado esperado:**
- Tipo: `tratamientos`
- Filtro: `estado='EN_PROGRESO'` / `'COMPLETADO'` / `'PROPUESTO'`

---

## 4️⃣ REPORTES DE PACIENTES

### Básicos
```
"Pacientes registrados en septiembre"
"Dame los nuevos pacientes de este mes"
"Mostrar pacientes del mes pasado"
"Pacientes registrados esta semana"
```

**Resultado esperado:**
- Tipo: `pacientes`
- Filtro: fecha de registro (`date_joined`)
- Datos: nombre, email, teléfono, CI, fecha registro, estado

---

## 5️⃣ REPORTES DE INGRESOS

### Básicos
```
"Ingresos de septiembre"
"Dame los ingresos del mes pasado"
"Mostrar pagos de esta semana"
"Cobros del 1 al 15 de octubre"
```

**Resultado esperado:**
- Tipo: `ingresos`
- Filtro: `estado_pago='COMPLETADO'`
- Datos: fecha, monto, método pago, factura, paciente
- Resumen: total_ingresos, promedio

---

### Con Período
```
"Ingresos de los últimos 7 días"
"Dame los pagos de los últimos 30 días"
"Mostrar ingresos de los últimos 15 días"
```

**Resultado esperado:**
- Tipo: `ingresos`
- Fechas: desde hace N días hasta hoy

---

## 🎤 Casos de Uso Completos

### Caso 1: Revisión Diaria
**Usuario dice:**  
*"Dame las citas de hoy"*

**Sistema responde:**
```json
{
  "interpretacion": {
    "texto_original": "Dame las citas de hoy",
    "tipo_reporte": "citas",
    "fecha_inicio": "2025-11-27",
    "fecha_fin": "2025-11-27",
    "interpretacion": "Reporte de citas del día 27/11/2025"
  },
  "datos": [
    {
      "id": 45,
      "fecha": "27/11/2025",
      "hora": "09:00",
      "paciente": "María González",
      "odontologo": "Dr. Juan Pérez",
      "motivo_tipo": "Limpieza",
      "estado": "Confirmada"
    }
  ],
  "resumen": {
    "total": 1,
    "periodo": "27/11/2025 - 27/11/2025"
  }
}
```

---

### Caso 2: Análisis Mensual
**Usuario dice:**  
*"Mostrar facturas pendientes del mes pasado"*

**Sistema responde:**
```json
{
  "interpretacion": {
    "texto_original": "Mostrar facturas pendientes del mes pasado",
    "tipo_reporte": "facturas",
    "fecha_inicio": "2025-10-01",
    "fecha_fin": "2025-10-31",
    "filtros": {
      "estado": "PENDIENTE"
    },
    "interpretacion": "Reporte de facturas desde el 01/10/2025 hasta el 31/10/2025, filtradas por estado: PENDIENTE"
  },
  "datos": [...],
  "resumen": {
    "total": 8,
    "periodo": "01/10/2025 - 31/10/2025",
    "total_facturado": 12500.00,
    "total_cobrado": 3200.00,
    "saldo_pendiente": 9300.00
  }
}
```

---

### Caso 3: Reporte de Ingresos
**Usuario dice:**  
*"Ingresos de los últimos 30 días"*

**Sistema responde:**
```json
{
  "interpretacion": {
    "tipo_reporte": "ingresos",
    "fecha_inicio": "2025-10-28",
    "fecha_fin": "2025-11-27",
    "interpretacion": "Reporte de ingresos desde el 28/10/2025 hasta el 27/11/2025"
  },
  "datos": [...],
  "resumen": {
    "total": 42,
    "periodo": "28/10/2025 - 27/11/2025",
    "total_ingresos": 28450.50,
    "promedio": 677.39
  }
}
```

---

## 🔍 Patrones de Fechas Detectados

| Patrón | Ejemplo | Interpretación |
|--------|---------|---------------|
| **Del X al Y de MES** | "del 1 al 5 de septiembre" | 2025-09-01 al 2025-09-05 |
| **Esta semana** | "esta semana" | Lunes actual al domingo actual |
| **Semana pasada** | "semana pasada" | Lunes pasado al domingo pasado |
| **Este mes** | "este mes" | Día 1 al último día del mes actual |
| **Mes pasado** | "mes pasado" | Día 1 al último día del mes anterior |
| **Hoy** | "hoy" | Fecha actual |
| **Ayer** | "ayer" | Fecha de ayer |
| **Últimos N días** | "últimos 7 días" | Desde hace 7 días hasta hoy |
| **De MES** | "de septiembre", "en octubre" | Todo el mes especificado |

---

## 📊 Filtros Adicionales Soportados

| Filtro | Palabras Clave | Ejemplo |
|--------|---------------|---------|
| **Estado** | pendiente, confirmada, cancelada, pagada, completado | "facturas pendientes" |
| **Paciente** | de [nombre], del paciente [nombre] | "citas de Juan Pérez" |
| **Monto** | mayores a, más de, entre X y Y | "facturas mayores a 1000" |

---

## ⚠️ Comandos No Válidos

Estos comandos **NO** funcionarán correctamente:

❌ "Dame todo"  
❌ "Reportes"  
❌ "Necesito información"  
❌ "Cuántas citas tengo" (sin rango de fecha)  

**Solución:** Ser específico con el tipo y período.

✅ "Dame las citas de hoy"  
✅ "Cuántas citas tengo esta semana"  
✅ "Facturas del mes actual"  

---

## 🔗 Siguiente Paso

Ver **[05_MANEJO_ERRORES.md](05_MANEJO_ERRORES.md)** para gestión de errores y casos especiales.
