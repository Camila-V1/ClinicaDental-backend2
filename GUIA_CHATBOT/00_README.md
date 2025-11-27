# 🤖 Guía de Implementación: Chatbot Asistente

## 📋 Índice

1. **[02_COMANDOS.md](02_COMANDOS.md)** - Lista completa de comandos (10 intenciones)
2. **[03_FRONTEND_CHAT.md](03_FRONTEND_CHAT.md)** - Componentes React completos
3. **[04_VOZ_INTEGRATION.md](04_VOZ_INTEGRATION.md)** - Integración con Web Speech API
4. **[05_ESTILOS_CSS.md](05_ESTILOS_CSS.md)** - CSS completo con animaciones

---

## 🎯 Objetivo

Implementar un chatbot asistente que permita a los pacientes:
- 📅 **Ver sus citas** y próxima cita
- 🦷 **Consultar tratamientos** activos
- 💰 **Ver facturas pendientes** y saldo
- 📋 **Revisar historial** de pagos
- 📄 **Acceder al historial clínico**
- ❌ **Cancelar citas**
- ➕ **Agendar nuevas citas**
- 💡 **Ver opciones** disponibles

**Modos de interacción:**
- ✍️ **Texto:** Escribir comandos en chat
- 🎤 **Voz:** Hablar comandos usando Web Speech API

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ DE USUARIO                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  [💬 Chat Widget]  [🎤 Botón Voz]                  │    │
│  │  Usuario: "ver mis citas"                          │    │
│  │  Bot: 📅 Tienes 3 citas programadas                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ POST /api/chatbot/query/
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (CHATBOT NLP)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  nlp_processor.py                                  │    │
│  │  - Detecta intención: "ver_citas"                  │    │
│  │  - Extrae entidades (fechas, nombres, etc)        │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  views.py                                          │    │
│  │  - Ejecuta acción según intención                  │    │
│  │  - Consulta base de datos                          │    │
│  │  - Formatea respuesta                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESPUESTA CON DATOS                         │
│  {                                                           │
│    "intencion": "ver_citas",                                │
│    "mensaje": "📅 Tienes 3 citas programadas",              │
│    "datos": [...],                                          │
│    "tipo_respuesta": "lista_citas"                          │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementación

### Backend (✅ COMPLETADO)
- [x] Procesador NLP (`chatbot/nlp_processor.py`)
- [x] Endpoint `/api/chatbot/query/` (`chatbot/views.py`)
- [x] Rutas configuradas (`chatbot/urls.py`)
- [x] Detección de 10 intenciones
- [x] Acciones para ver citas, tratamientos, facturas, etc.
- [x] Sistema de ayuda con lista de comandos

### Frontend (⏳ POR IMPLEMENTAR)
- [ ] Componente `ChatWidget.jsx`
- [ ] Modal/sidebar de chat
- [ ] Integración con Web Speech API para voz
- [ ] Visualización de respuestas estructuradas
- [ ] Historial de conversación

---

## 🎯 Funcionalidades Implementadas

### 1. Ver Citas (`ver_citas`)
**Comandos:**
- "ver mis citas"
- "mostrar mis citas"
- "cuales son mis citas"

**Respuesta:**
```json
{
  "mensaje": "📅 Tienes 3 citas programadas.",
  "datos": [
    {
      "id": 1,
      "fecha": "30/11/2025",
      "hora": "10:00",
      "odontologo": "Dr. Juan Pérez",
      "motivo_tipo": "Limpieza",
      "puede_cancelar": true
    }
  ]
}
```

---

### 2. Próxima Cita (`proxima_cita`)
**Comandos:**
- "próxima cita"
- "cuál es mi siguiente cita"
- "cuando es mi cita"

**Respuesta:**
```json
{
  "mensaje": "📅 Tu próxima cita es en 3 días (30/11/2025 a las 10:00) con Dr. Juan Pérez.",
  "datos": {
    "fecha": "30/11/2025",
    "hora": "10:00",
    "tiempo_restante": "en 3 días"
  }
}
```

---

### 3. Tratamientos Activos (`tratamientos_activos`)
**Comandos:**
- "ver mis tratamientos"
- "tratamientos activos"
- "mis planes de tratamiento"

**Respuesta:**
```json
{
  "mensaje": "🦷 Tienes 2 tratamientos activos.",
  "datos": [
    {
      "titulo": "Ortodoncia",
      "odontologo": "Dra. María López",
      "estado": "En progreso",
      "porcentaje_completado": 45,
      "total": 5000.00
    }
  ]
}
```

---

### 4. Facturas Pendientes (`facturas_pendientes`)
**Comandos:**
- "cuánto debo"
- "facturas pendientes"
- "saldo pendiente"

**Respuesta:**
```json
{
  "mensaje": "💰 Tienes 2 facturas pendientes por un total de Bs. 1500.00",
  "datos": [...],
  "total_deuda": 1500.00
}
```

---

### 5. Historial de Pagos (`historial_pagos`)
**Comandos:**
- "ver mis pagos"
- "historial de pagos"

---

### 6. Historial Clínico (`historial_clinico`)
**Comandos:**
- "ver mi historial"
- "mi historia clínica"

---

### 7. Cancelar Cita (`cancelar_cita`)
**Comandos:**
- "cancelar cita"
- "no puedo asistir"

**Respuesta:**
```json
{
  "mensaje": "❌ Selecciona la cita que deseas cancelar:",
  "datos": [...citas cancelables...],
  "requiere_seleccion": true
}
```

---

### 8. Agendar Cita (`agendar_cita`)
**Comandos:**
- "agendar cita"
- "pedir una cita"

**Respuesta:**
```json
{
  "mensaje": "📅 Redirigiendo al sistema de agendamiento...",
  "accion": "redirect",
  "redirect_url": "/agenda"
}
```

---

### 9. Ayuda (`ayuda`)
**Comandos:**
- "ayuda"
- "qué puedes hacer"
- "ver opciones"

**Respuesta:**
```json
{
  "mensaje": "💡 Estos son los comandos que puedo entender:",
  "datos": [
    {
      "comando": "ver_citas",
      "descripcion": "Ver todas mis citas programadas",
      "ejemplo": "\"ver mis citas\" o \"mostrar mis citas\""
    }
  ]
}
```

---

## 🚀 Estado Actual

### ✅ Backend Implementado
- **Endpoint:** `/api/chatbot/query/`
- **Método:** POST
- **Headers:** `Authorization: Bearer {token}`, `x-tenant: clinica_demo`
- **Body:** `{"texto": "ver mis citas", "es_voz": false}`

### 📝 Archivos Creados
```
chatbot/
├── __init__.py
├── apps.py
├── admin.py
├── tests.py
├── nlp_processor.py     ← Procesador NLP
├── views.py             ← Vista API
└── urls.py              ← Rutas
```

### 🧪 Script de Prueba
```bash
python test_chatbot.py
```

---

## 📚 Próximos Pasos

1. **Probar backend:** `python test_chatbot.py`
2. **Implementar frontend:** Widget de chat con React
3. **Integrar voz:** Reutilizar Web Speech API de reportes por voz
4. **Agregar botón flotante:** Chat bubble en esquina inferior derecha
5. **Historial:** Guardar conversación en localStorage
6. **Notificaciones:** Avisar de próximas citas

---

## 🔗 Enlaces Rápidos

- [Comandos Disponibles](02_COMANDOS.md) - 10 intenciones con ejemplos
- [Frontend React](03_FRONTEND_CHAT.md) - Componentes, hooks y servicios
- [Integración Voz](04_VOZ_INTEGRATION.md) - Reutilizar Web Speech API
- [Estilos CSS](05_ESTILOS_CSS.md) - CSS completo responsive

---

## 📞 Testing

**Endpoint de prueba:**
```bash
POST https://clinicadental-backend2.onrender.com/api/chatbot/query/
Headers:
  Authorization: Bearer {token}
  x-tenant: clinica_demo
  Content-Type: application/json
Body:
  {"texto": "ver mis citas"}
```

**Respuesta esperada:**
```json
{
  "intencion": "ver_citas",
  "mensaje": "📅 Tienes X citas programadas.",
  "datos": [...],
  "tipo_respuesta": "lista_citas"
}
```
