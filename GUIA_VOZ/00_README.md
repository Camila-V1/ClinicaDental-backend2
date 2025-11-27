# 📢 Guía de Implementación: Reportes por Voz

## 📋 Índice

1. **[01_COMPONENTE_REACT.md](01_COMPONENTE_REACT.md)** - Componente de captura de voz con Web Speech API
2. **[02_INTEGRACION_REPORTES.md](02_INTEGRACION_REPORTES.md)** - Integración en la página de reportes
3. **[03_ESTILOS_UI.md](03_ESTILOS_UI.md)** - Diseño del botón de micrófono y modal
4. **[04_EJEMPLOS_USO.md](04_EJEMPLOS_USO.md)** - Ejemplos de comandos de voz
5. **[05_MANEJO_ERRORES.md](05_MANEJO_ERRORES.md)** - Gestión de errores y casos especiales
6. **[06_FIX_NO_SPEECH.md](06_FIX_NO_SPEECH.md)** - ⚡ **FIX: Error `no-speech` que detiene el reconocimiento**

---

## 🎯 Objetivo

Implementar un sistema de reportes por voz que permita a los usuarios:
- **Hablar** comandos en lenguaje natural español
- **Ver** la interpretación del comando en tiempo real
- **Obtener** reportes filtrados automáticamente
- **Exportar** los resultados en PDF/Excel

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    PÁGINA DE REPORTES                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  [🎤 Botón Micrófono]                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   MODAL DE CAPTURA VOZ                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  🎤 "Hablando..."                                   │    │
│  │  Transcripción: "dame las citas del 1 al 5..."     │    │
│  │  [Detener] [Enviar]                                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ POST /api/reportes/voice-query/
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (NLP PARSER)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Parse: "dame las citas del 1 al 5 de septiembre" │    │
│  │  → tipo: "citas"                                   │    │
│  │  → fecha_inicio: "2025-09-01"                      │    │
│  │  → fecha_fin: "2025-09-05"                         │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESPUESTA CON DATOS                         │
│  {                                                           │
│    "interpretacion": {...},                                 │
│    "datos": [...citas filtradas...],                        │
│    "resumen": {total: 10, periodo: "..."}                   │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              TABLA DE RESULTADOS + EXPORTAR                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementación

### Backend (✅ COMPLETADO)
- [x] Parser NLP en español (`reportes/nlp/voice_parser.py`)
- [x] Endpoint `/api/reportes/voice-query/` (`reportes/voice_views.py`)
- [x] Rutas configuradas (`reportes/urls.py`)
- [x] Detección de fechas en lenguaje natural
- [x] Filtros por estado, paciente, monto

### Frontend (⏳ POR IMPLEMENTAR)
- [ ] Componente `VoiceReportCapture.jsx`
- [ ] Integración en página de reportes
- [ ] Botón de micrófono con animación
- [ ] Modal de captura de voz
- [ ] Visualización de resultados
- [ ] Exportación de reportes

---

## 🚀 Estado Actual

### ✅ Backend Desplegado
- **URL:** `https://clinicadental-backend2.onrender.com/api/reportes/voice-query/`
- **Método:** POST
- **Headers:** `Authorization: Bearer {token}`, `x-tenant: clinica_demo`
- **Body:** `{"texto": "dame las citas del 1 al 5 de septiembre"}`

### 📝 Próximos Pasos
1. Crear componente React de captura de voz
2. Agregar botón de micrófono en página de reportes
3. Implementar visualización de resultados
4. Agregar animaciones y feedback visual
5. Probar con diferentes comandos de voz

---

## 📚 Comandos de Voz Soportados

### Tipos de Reporte
- ✅ **Citas:** "dame las citas de...", "mostrar citas de..."
- ✅ **Facturas:** "facturas de...", "mostrar facturas..."
- ✅ **Tratamientos:** "planes de tratamiento de...", "tratamientos de..."
- ✅ **Pacientes:** "pacientes registrados en...", "nuevos pacientes..."
- ✅ **Ingresos:** "ingresos de...", "pagos de...", "cobros de..."

### Rangos de Fecha
- ✅ **Exacto:** "del 1 al 5 de septiembre"
- ✅ **Relativo:** "esta semana", "semana pasada", "este mes", "mes pasado"
- ✅ **Simple:** "hoy", "ayer"
- ✅ **Período:** "últimos 7 días", "últimos 30 días"

### Filtros Adicionales
- ✅ **Estado:** "facturas pendientes", "citas confirmadas"
- ✅ **Paciente:** "de Juan Pérez"
- ✅ **Monto:** "facturas mayores a 1000"

---

## 🔗 Enlaces Rápidos

- [Componente React](01_COMPONENTE_REACT.md)
- [Integración en Reportes](02_INTEGRACION_REPORTES.md)
- [Estilos CSS](03_ESTILOS_UI.md)
- [Ejemplos de Uso](04_EJEMPLOS_USO.md)
- [Manejo de Errores](05_MANEJO_ERRORES.md)

---

## 📞 Soporte

Para más información sobre el backend:
- Ver `reportes/nlp/voice_parser.py`
- Ver `reportes/voice_views.py`
- Ejecutar `python test_voice_parser.py` para probar el parser
