# 📋 Lista Completa de Comandos del Chatbot

## 🎤 Comandos Disponibles

---

## 1️⃣ VER MIS CITAS

### Descripción
Ver todas las citas programadas del paciente (futuras).

### Comandos aceptados
```
"ver mis citas"
"mostrar mis citas"
"dame mis citas"
"cuales son mis citas"
"lista de citas"
"mis citas"
"citas programadas"
"citas agendadas"
```

### Respuesta
```json
{
  "intencion": "ver_citas",
  "mensaje": "📅 Tienes 3 citas programadas.",
  "datos": [
    {
      "id": 1,
      "fecha": "30/11/2025",
      "hora": "10:00",
      "odontologo": "Dr. Juan Pérez",
      "motivo_tipo": "Limpieza",
      "motivo": "Limpieza dental anual",
      "estado": "Confirmada",
      "puede_cancelar": true
    }
  ],
  "tipo_respuesta": "lista_citas",
  "total": 3
}
```

---

## 2️⃣ PRÓXIMA CITA

### Descripción
Ver la siguiente cita confirmada más cercana.

### Comandos aceptados
```
"próxima cita"
"siguiente cita"
"prox cita"
"mi próxima cita"
"cuando es mi cita"
"cual es mi siguiente cita"
"cita más cercana"
```

### Respuesta
```json
{
  "intencion": "proxima_cita",
  "mensaje": "📅 Tu próxima cita es en 3 días (30/11/2025 a las 10:00) con Dr. Juan Pérez.",
  "datos": {
    "id": 1,
    "fecha": "30/11/2025",
    "hora": "10:00",
    "odontologo": "Dr. Juan Pérez",
    "motivo_tipo": "Limpieza",
    "tiempo_restante": "en 3 días",
    "puede_cancelar": true
  },
  "tipo_respuesta": "proxima_cita"
}
```

**Casos especiales:**
- Si es hoy: "en menos de 1 hora" / "en 5 horas"
- Si es mañana: "mañana"
- Si es en días: "en 3 días"

---

## 3️⃣ VER MIS TRATAMIENTOS

### Descripción
Ver planes de tratamiento activos o aprobados.

### Comandos aceptados
```
"ver mis tratamientos"
"mostrar mis tratamientos"
"dame mis tratamientos"
"tratamientos activos"
"tratamientos en curso"
"mis planes de tratamiento"
"planes activos"
```

### Respuesta
```json
{
  "intencion": "tratamientos_activos",
  "mensaje": "🦷 Tienes 2 tratamientos activos.",
  "datos": [
    {
      "id": 5,
      "titulo": "Ortodoncia completa",
      "odontologo": "Dra. María López",
      "estado": "En progreso",
      "fecha_creacion": "01/10/2025",
      "total": 5000.00,
      "porcentaje_completado": 45,
      "cantidad_items": 8
    }
  ],
  "tipo_respuesta": "tratamientos",
  "total": 2
}
```

---

## 4️⃣ FACTURAS PENDIENTES

### Descripción
Ver facturas pendientes de pago y saldo total.

### Comandos aceptados
```
"cuánto debo"
"cuanto debo"
"cuanto tengo que pagar"
"facturas pendientes"
"deudas"
"saldo pendiente"
"que debo pagar"
"mis pagos pendientes"
```

### Respuesta con deudas
```json
{
  "intencion": "facturas_pendientes",
  "mensaje": "💰 Tienes 2 facturas pendientes por un total de Bs. 1500.00",
  "datos": [
    {
      "id": 10,
      "numero": "FAC-000010",
      "fecha": "15/11/2025",
      "monto_total": 1000.00,
      "monto_pagado": 0.00,
      "saldo": 1000.00,
      "estado": "Pendiente"
    }
  ],
  "tipo_respuesta": "facturas_pendientes",
  "total_deuda": 1500.00,
  "total": 2
}
```

### Respuesta sin deudas
```json
{
  "intencion": "facturas_pendientes",
  "mensaje": "✅ No tienes facturas pendientes. ¡Estás al día!",
  "datos": [],
  "tipo_respuesta": "facturas_pendientes",
  "total_deuda": 0,
  "sugerencias": ["ver mis pagos", "historial de pagos"]
}
```

---

## 5️⃣ HISTORIAL DE PAGOS

### Descripción
Ver pagos completados (últimos 10).

### Comandos aceptados
```
"ver mis pagos"
"mostrar mis pagos"
"historial de pagos"
"pagos realizados"
"mis pagos"
"pagos hechos"
```

### Respuesta
```json
{
  "intencion": "historial_pagos",
  "mensaje": "📋 Tienes 5 pagos registrados (últimos 10).",
  "datos": [
    {
      "id": 20,
      "fecha": "20/11/2025 14:30",
      "monto": 500.00,
      "metodo": "Tarjeta",
      "factura": "FAC-000010",
      "estado": "Completado"
    }
  ],
  "tipo_respuesta": "historial_pagos",
  "total_pagado": 2500.00,
  "total": 5
}
```

---

## 6️⃣ HISTORIAL CLÍNICO

### Descripción
Ver episodios clínicos registrados (últimos 10).

### Comandos aceptados
```
"ver mi historial"
"mostrar mi historial"
"mi historial clínico"
"mi historia clínica"
"mi expediente"
"historial médico"
"historial dental"
"mis episodios"
```

### Respuesta
```json
{
  "intencion": "historial_clinico",
  "mensaje": "📄 Tienes 8 episodios clínicos registrados (últimos 10).",
  "datos": [
    {
      "id": 15,
      "fecha": "10/11/2025",
      "tipo": "Consulta",
      "diagnostico": "Caries en molar superior izquierdo...",
      "odontologo": "Dr. Juan Pérez",
      "tratamiento_aplicado": "Limpieza y obturación..."
    }
  ],
  "tipo_respuesta": "historial_clinico",
  "total": 8
}
```

---

## 7️⃣ CANCELAR CITA

### Descripción
Iniciar flujo para cancelar una cita confirmada.

### Comandos aceptados
```
"cancelar cita"
"eliminar cita"
"borrar cita"
"no puedo asistir"
"no podré ir"
```

### Respuesta
```json
{
  "intencion": "cancelar_cita",
  "mensaje": "❌ Selecciona la cita que deseas cancelar:",
  "datos": [
    {
      "id": 1,
      "fecha": "30/11/2025",
      "hora": "10:00",
      "odontologo": "Dr. Juan Pérez",
      "motivo_tipo": "Limpieza"
    }
  ],
  "tipo_respuesta": "cancelar_cita",
  "requiere_seleccion": true
}
```

**Nota:** El frontend debe permitir que el usuario seleccione qué cita cancelar.

---

## 8️⃣ AGENDAR CITA

### Descripción
Redirigir al sistema de agendamiento.

### Comandos aceptados
```
"agendar cita"
"programar cita"
"reservar cita"
"pedir cita"
"nueva cita"
"quiero una cita"
```

### Respuesta
```json
{
  "intencion": "agendar_cita",
  "mensaje": "📅 Redirigiendo al sistema de agendamiento...",
  "datos": null,
  "tipo_respuesta": "agendar_cita",
  "accion": "redirect",
  "redirect_url": "/agenda"
}
```

**Nota:** El frontend debe redirigir a la página de agendamiento.

---

## 9️⃣ AYUDA

### Descripción
Mostrar lista de comandos disponibles.

### Comandos aceptados
```
"ayuda"
"help"
"qué puedes hacer"
"que puedes hacer"
"que haces"
"opciones"
"cómo funciona"
"comandos"
"que comandos"
"ver opciones"
"mostrar opciones"
```

### Respuesta
```json
{
  "intencion": "ayuda",
  "mensaje": "💡 Estos son los comandos que puedo entender:",
  "datos": [
    {
      "comando": "ver_citas",
      "descripcion": "Ver todas mis citas programadas",
      "ejemplo": "\"ver mis citas\" o \"mostrar mis citas\""
    },
    {
      "comando": "proxima_cita",
      "descripcion": "Ver mi próxima cita programada",
      "ejemplo": "\"próxima cita\" o \"cuál es mi siguiente cita\""
    }
    // ... resto de comandos
  ],
  "tipo_respuesta": "ayuda",
  "total": 9
}
```

---

## 🔟 SALUDO

### Descripción
Saludo inicial del chatbot.

### Comandos aceptados
```
"hola"
"buenos días"
"buenas tardes"
"buenas noches"
"hey"
"hi"
```

### Respuesta
```json
{
  "intencion": "saludo",
  "mensaje": "👋 ¡Hola Juan! Soy tu asistente virtual. Puedo ayudarte con tus citas, tratamientos, facturas y más. Escribe \"ayuda\" para ver todas las opciones.",
  "datos": null,
  "tipo_respuesta": "saludo",
  "sugerencias": ["ver mis citas", "próxima cita", "ayuda"]
}
```

---

## ❌ COMANDO DESCONOCIDO

### Descripción
Cuando no se reconoce la intención.

### Respuesta
```json
{
  "intencion": "desconocido",
  "texto_original": "dame información",
  "respuesta": "No entendí tu solicitud. Escribe \"ayuda\" para ver los comandos disponibles.",
  "tipo_respuesta": "error",
  "sugerencias": ["ver mis citas", "próxima cita", "ayuda"]
}
```

---

## 📊 Resumen de Comandos

| # | Comando | Descripción | Ejemplo |
|---|---------|-------------|---------|
| 1 | `ver_citas` | Ver citas programadas | "ver mis citas" |
| 2 | `proxima_cita` | Próxima cita confirmada | "próxima cita" |
| 3 | `tratamientos_activos` | Tratamientos en curso | "mis tratamientos" |
| 4 | `facturas_pendientes` | Deudas y saldo | "cuánto debo" |
| 5 | `historial_pagos` | Pagos realizados | "ver mis pagos" |
| 6 | `historial_clinico` | Episodios clínicos | "mi historial" |
| 7 | `cancelar_cita` | Cancelar cita | "cancelar cita" |
| 8 | `agendar_cita` | Nueva cita | "agendar cita" |
| 9 | `ayuda` | Lista de comandos | "ayuda" |
| 10 | `saludo` | Saludar | "hola" |

---

## 🎯 Mejores Prácticas

### Para el Usuario
- Ser claro y conciso
- Usar comandos simples
- Si no entiende, probar con sinónimos
- Usar "ayuda" para ver opciones

### Para el Frontend
- Mostrar sugerencias de comandos
- Autocompletar comandos comunes
- Botones rápidos con acciones frecuentes
- Historial de conversación

### Para el Backend
- Logs de comandos no reconocidos
- Análisis de patrones más usados
- Mejora continua del NLP
