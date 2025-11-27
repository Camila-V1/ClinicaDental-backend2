# ⚠️ Manejo de Errores y Casos Especiales

## 🔴 Tipos de Errores

---

## 1️⃣ ERRORES DEL NAVEGADOR

### Error: No se detecta el micrófono
**Causa:** Permisos no otorgados o micrófono no disponible

**Mensaje de error:**
```
"No se pudo acceder al micrófono. Verifica los permisos."
```

**Solución:**
```javascript
// En useVoiceRecognition.js
if (event.error === 'not-allowed') {
  setError('Permiso denegado. Habilita el acceso al micrófono en la configuración.');
  
  // Mostrar instrucciones según navegador
  const isChrome = /Chrome/.test(navigator.userAgent);
  if (isChrome) {
    toast.info('Chrome: Clic en el ícono de candado → Permisos → Micrófono → Permitir');
  }
}
```

**Prevención en el frontend:**
```javascript
// Verificar permisos antes de abrir modal
const checkMicrophonePermission = async () => {
  try {
    const result = await navigator.permissions.query({ name: 'microphone' });
    if (result.state === 'denied') {
      toast.error('El acceso al micrófono está bloqueado. Revisa la configuración del navegador.');
      return false;
    }
    return true;
  } catch (error) {
    console.warn('No se pudo verificar permisos:', error);
    return true; // Intentar de todas formas
  }
};
```

---

### Error: Navegador no soportado
**Causa:** Firefox u otros navegadores sin Web Speech API

**Mensaje de error:**
```
"Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge."
```

**Solución:**
```javascript
// Detectar navegador y mostrar alternativa
const VoiceReportButton = ({ onClick }) => {
  const isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  
  if (!isSupported) {
    return (
      <div className="voice-not-supported">
        <AlertCircle size={16} />
        <span>Voz no disponible</span>
        <Tooltip>
          Usa Google Chrome o Microsoft Edge para activar reportes por voz
        </Tooltip>
      </div>
    );
  }
  
  return <button onClick={onClick}>🎤 Reportes por Voz</button>;
};
```

---

### Error: No se detecta habla (`no-speech`)
**Causa:** Usuario hace pausa mientras habla o micrófono no detecta audio momentáneamente

**❌ INCORRECTO:** Detener el reconocimiento y mostrar error
```javascript
// ❌ NO HACER ESTO
if (event.error === 'no-speech') {
  setError('No se detectó audio');
  setIsListening(false); // ❌ Detiene la escucha
}
```

**✅ CORRECTO:** Ignorar el error y continuar escuchando
```javascript
// ✅ HACER ESTO
recognitionRef.current.onerror = (event) => {
  console.error('❌ Error de reconocimiento:', event.error);
  
  // 'no-speech' es NORMAL cuando el usuario hace pausa
  if (event.error === 'no-speech') {
    console.log('⏸️ Pausa detectada (no-speech) - continuando escucha...');
    // NO cambiar isListening ni mostrar error
    // El reconocimiento continúa automáticamente con continuous: true
    return;
  }
  
  // Para OTROS errores sí detener
  setError(getErrorMessage(event.error));
  setIsListening(false);
};
```

**Explicación:**
- `continuous: true` permite que el reconocimiento continúe después de pausas
- `no-speech` se dispara cuando hay silencio, pero **no es un error fatal**
- Si detienes el reconocimiento en cada pausa, el usuario debe presionar el botón repetidamente

**Timeout opcional (solo si realmente no hay audio en mucho tiempo):**
```javascript
// Timeout si NO hay transcripción en 30 segundos (no 10)
useEffect(() => {
  if (isListening) {
    const timeout = setTimeout(() => {
      if (!transcript) {
        stopListening();
        toast.warning('No se detectó voz por mucho tiempo. Intenta de nuevo.');
      }
    }, 30000); // 30 segundos, no 10
    
    return () => clearTimeout(timeout);
  }
}, [isListening, transcript]);
```

---

## 2️⃣ ERRORES DEL BACKEND

### Error: Comando muy corto
**Causa:** Usuario envía texto vacío o muy corto

**Validación en frontend:**
```javascript
const handleSubmitCommand = async (transcript) => {
  const validation = voiceReportService.validateCommand(transcript);
  
  if (!validation.valid) {
    toast.error(validation.message);
    return;
  }
  
  // Continuar...
};

// En voiceReportService.js
validateCommand(texto) {
  if (!texto || texto.trim().length < 5) {
    return {
      valid: false,
      message: 'El comando es muy corto. Describe qué reporte necesitas.'
    };
  }
  
  return { valid: true };
}
```

---

### Error: Tipo de reporte no detectado
**Causa:** Comando ambiguo sin palabras clave

**Respuesta del backend:**
```json
{
  "interpretacion": {
    "tipo_reporte": "desconocido",
    "interpretacion": "No se pudo determinar el tipo de reporte"
  }
}
```

**Manejo en frontend:**
```javascript
if (result.data.interpretacion.tipo_reporte === 'desconocido') {
  toast.error('No entendí el comando. Intenta con: "Dame las citas de hoy"');
  
  // No cerrar modal, permitir reintentar
  return;
}
```

---

### Error: Sin fechas detectadas
**Causa:** Usuario no especifica período

**Respuesta del backend:**
```json
{
  "fecha_inicio": null,
  "fecha_fin": null,
  "interpretacion": "No se detectó un rango de fechas"
}
```

**Manejo en frontend:**
```javascript
if (!interpretacion.fecha_inicio || !interpretacion.fecha_fin) {
  toast.warning('No se detectó un rango de fechas. Usando el mes actual...');
  
  // Aplicar rango por defecto (ej: mes actual)
  const hoy = new Date();
  const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
  const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);
  
  // Reenviar comando con fechas explícitas
  // O usar las fechas por defecto del backend
}
```

---

### Error: Sin datos encontrados
**Causa:** Query válida pero sin resultados en BD

**Respuesta del backend:**
```json
{
  "datos": [],
  "resumen": {
    "total": 0
  }
}
```

**Manejo en frontend:**
```javascript
if (result.data.datos.length === 0) {
  toast.info(`No se encontraron ${interpretacion.tipo_reporte} en el período especificado`);
  
  // Mostrar empty state con sugerencias
  setEmptyState({
    message: `No hay ${interpretacion.tipo_reporte} en ${resumen.periodo}`,
    suggestions: [
      'Intenta con un rango de fechas más amplio',
      'Verifica que existan datos en ese período'
    ]
  });
}
```

---

## 3️⃣ ERRORES DE RED

### Error: Timeout de conexión
**Causa:** Backend tarda mucho o sin conexión

**Manejo:**
```javascript
const handleSubmitCommand = async (transcript) => {
  setIsProcessing(true);
  
  // Timeout de 30 segundos
  const timeoutId = setTimeout(() => {
    setIsProcessing(false);
    toast.error('La solicitud está tardando mucho. Verifica tu conexión.');
  }, 30000);
  
  try {
    const result = await voiceReportService.processVoiceCommand(transcript);
    clearTimeout(timeoutId);
    
    // Procesar resultado...
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.code === 'ECONNABORTED') {
      toast.error('Tiempo de espera agotado. Intenta nuevamente.');
    } else if (!navigator.onLine) {
      toast.error('Sin conexión a internet. Verifica tu conexión.');
    } else {
      toast.error('Error al procesar el comando. Intenta nuevamente.');
    }
  } finally {
    setIsProcessing(false);
  }
};
```

---

### Error: 401 Unauthorized
**Causa:** Token expirado o inválido

**Manejo:**
```javascript
// En voiceReportService.js
async processVoiceCommand(texto) {
  try {
    const response = await apiClient.post('/reportes/voice-query/', {
      texto: texto.trim()
    });
    
    return { success: true, data: response.data };
    
  } catch (error) {
    if (error.response?.status === 401) {
      // Redirigir a login
      localStorage.removeItem('token');
      window.location.href = '/login';
      
      return {
        success: false,
        error: 'Sesión expirada. Por favor, inicia sesión nuevamente.'
      };
    }
    
    return {
      success: false,
      error: error.response?.data?.error || 'Error al procesar el comando'
    };
  }
}
```

---

## 4️⃣ CASOS ESPECIALES

### Caso: Usuario interrumpe durante la captura
**Solución:** Limpiar estado correctamente

```javascript
const handleCloseModal = () => {
  // Detener reconocimiento
  stopListening();
  
  // Limpiar transcripción
  resetTranscript();
  
  // Limpiar estado de procesamiento
  setIsProcessing(false);
  
  // Cerrar modal
  onClose();
};
```

---

### Caso: Usuario habla muy rápido
**Solución:** Permitir edición manual

```javascript
<div className="transcript-container">
  <label>Transcripción:</label>
  <textarea
    value={transcript}
    onChange={(e) => setTranscript(e.target.value)}
    placeholder="Edita la transcripción si es necesario"
    rows={4}
  />
  <p className="hint">
    💡 Puedes editar la transcripción antes de enviar
  </p>
</div>
```

---

### Caso: Transcripción incorrecta
**Solución:** Mostrar ejemplos y permitir reintentar

```javascript
{transcript && (
  <div className="transcript-actions">
    <button onClick={resetTranscript} className="btn-reset">
      🔄 Reintentar
    </button>
    <button onClick={handleSubmit} className="btn-use">
      ✅ Usar esta transcripción
    </button>
  </div>
)}
```

---

## 5️⃣ LOGGING Y DEBUGGING

### Logging en Producción
```javascript
// Enviar logs al backend para análisis
const logVoiceCommand = async (command, result) => {
  try {
    await apiClient.post('/logs/voice-commands/', {
      comando: command,
      interpretacion: result.interpretacion,
      exitoso: result.success,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.warn('No se pudo registrar log:', error);
  }
};
```

---

### Debugging en Desarrollo
```javascript
// Modo debug para desarrolladores
const isDev = process.env.NODE_ENV === 'development';

if (isDev) {
  console.group('🎤 Voice Command Debug');
  console.log('Transcript:', transcript);
  console.log('Interpretation:', interpretacion);
  console.log('Data count:', datos.length);
  console.log('Resumen:', resumen);
  console.groupEnd();
}
```

---

## 📊 Resumen de Mejores Prácticas

| Práctica | Descripción |
|----------|-------------|
| ✅ **Validar permisos** | Verificar acceso al micrófono antes de abrir modal |
| ✅ **Timeouts** | Límite de 30s para solicitudes al backend |
| ✅ **Feedback visual** | Mostrar estado de "Procesando..." claramente |
| ✅ **Permitir edición** | Usuario puede corregir transcripción |
| ✅ **Ejemplos visibles** | Mostrar comandos de ejemplo en el modal |
| ✅ **Manejo de 401** | Redirigir a login si token expiró |
| ✅ **Logging** | Registrar comandos fallidos para mejorar NLP |
| ✅ **Reintentar** | Permitir reintentar sin cerrar modal |

---

## 🎯 Checklist de Testing

### Pruebas de Navegador
- [ ] Chrome: Funciona correctamente
- [ ] Edge: Funciona correctamente
- [ ] Safari iOS: Probar en dispositivos móviles
- [ ] Firefox: Mostrar mensaje de "no soportado"

### Pruebas de Audio
- [ ] Micrófono USB
- [ ] Micrófono de laptop integrado
- [ ] Auriculares con micrófono
- [ ] Ambiente ruidoso (oficina)
- [ ] Ambiente silencioso

### Pruebas de Comandos
- [ ] Comandos válidos retornan datos
- [ ] Comandos ambiguos muestran error claro
- [ ] Comandos sin fechas usan rango por defecto
- [ ] Filtros adicionales se aplican correctamente

### Pruebas de Error
- [ ] Sin conexión a internet
- [ ] Token expirado (401)
- [ ] Backend caído (500)
- [ ] Timeout (30s)
- [ ] Permisos denegados

---

## 🔗 Documentación Completa

- [00_README.md](00_README.md) - Índice general
- [01_COMPONENTE_REACT.md](01_COMPONENTE_REACT.md) - Componentes React
- [02_INTEGRACION_REPORTES.md](02_INTEGRACION_REPORTES.md) - Integración en página
- [03_ESTILOS_UI.md](03_ESTILOS_UI.md) - Estilos CSS
- [04_EJEMPLOS_USO.md](04_EJEMPLOS_USO.md) - Ejemplos de comandos
