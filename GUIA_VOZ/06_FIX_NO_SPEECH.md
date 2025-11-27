# 🔧 Fix: Error `no-speech` - Reconocimiento se Detiene

## 🚨 Problema

El sistema de voz genera errores `no-speech` constantemente y **detiene el reconocimiento**, requiriendo que el usuario presione el botón repetidamente:

```
🎙️ Iniciando reconocimiento de voz...
✅ Reconocimiento iniciado
❌ Error de reconocimiento: no-speech
⏸️ Pausa detectada (no-speech) - esperando voz...
⏹️ Reconocimiento finalizado  ← ❌ SE DETIENE
```

El usuario debe presionar el botón nuevamente para continuar. **Esto es molesto e incorrecto.**

---

## ✅ Solución: NO Detener en `no-speech`

El error `no-speech` **NO ES UN ERROR REAL**, es una notificación de que hay silencio momentáneo. Con `continuous: true`, el reconocimiento debe **continuar automáticamente**.

### Código CORRECTO en `useVoiceRecognition.js`

```javascript
// src/hooks/useVoiceRecognition.js
import { useState, useEffect, useRef } from 'react';

export const useVoiceRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // ✅ CONFIGURACIÓN CORRECTA
      recognitionRef.current.continuous = true;      // Escucha continua
      recognitionRef.current.interimResults = true;  // Resultados parciales
      recognitionRef.current.lang = 'es-ES';         // Español
      recognitionRef.current.maxAlternatives = 1;    // Una alternativa
      
      // ✅ EVENTO: onstart
      recognitionRef.current.onstart = () => {
        console.log('🎙️ Iniciando reconocimiento de voz...');
        console.log('📌 Configuración:', {
          lang: 'es-ES',
          continuous: true,
          interimResults: true
        });
        setIsListening(true);
        setError(null);
      };
      
      // ✅ EVENTO: onresult
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPart + ' ';
            console.log('✅ Resultado final:', transcriptPart);
          } else {
            interimTranscript += transcriptPart;
            console.log('⏳ Resultado parcial:', transcriptPart);
          }
        }
        
        setTranscript(prev => prev + finalTranscript || interimTranscript);
      };
      
      // ✅ EVENTO: onerror - CLAVE PARA SOLUCIONAR EL PROBLEMA
      recognitionRef.current.onerror = (event) => {
        console.error('❌ Error de reconocimiento:', event.error);
        
        // ⚠️ IMPORTANTE: 'no-speech' NO ES UN ERROR FATAL
        // Es normal cuando el usuario hace pausa o hay silencio momentáneo
        if (event.error === 'no-speech') {
          console.log('⏸️ Pausa detectada (no-speech) - continuando escucha...');
          // ✅ NO cambiar isListening
          // ✅ NO llamar setError
          // ✅ NO detener el reconocimiento
          // El reconocimiento continúa automáticamente con continuous: true
          return;
        }
        
        // Para OTROS errores sí detener y mostrar mensaje
        if (event.error === 'aborted') {
          console.log('⏹️ Reconocimiento abortado por el usuario');
          setIsListening(false);
          return;
        }
        
        // Errores reales (audio-capture, not-allowed, network, etc.)
        setError(getErrorMessage(event.error));
        setIsListening(false);
      };
      
      // ✅ EVENTO: onend
      recognitionRef.current.onend = () => {
        console.log('⏹️ Reconocimiento finalizado');
        setIsListening(false);
      };
      
      setIsSupported(true);
    } else {
      setIsSupported(false);
      setError('Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge.');
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setError(null);
      try {
        recognitionRef.current.start();
        console.log('✅ Reconocimiento iniciado');
      } catch (err) {
        console.error('❌ Error al iniciar:', err);
        if (err.message.includes('already started')) {
          console.warn('⚠️ Reconocimiento ya estaba activo');
        }
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
        console.log('🛑 Deteniendo reconocimiento...');
      } catch (err) {
        console.error('❌ Error al detener:', err);
      }
    }
  };

  const resetTranscript = () => {
    setTranscript('');
    setError(null);
  };

  return {
    isListening,
    transcript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript
  };
};

// Función auxiliar para mensajes de error
function getErrorMessage(error) {
  switch (error) {
    case 'no-speech':
      // Este error NO debería llegar aquí si se maneja correctamente arriba
      return 'No se detectó audio. Habla más cerca del micrófono.';
    case 'audio-capture':
      return 'No se pudo acceder al micrófono. Verifica los permisos.';
    case 'not-allowed':
      return 'Permiso denegado. Habilita el acceso al micrófono en la configuración.';
    case 'network':
      return 'Error de red. Verifica tu conexión a internet.';
    case 'service-not-allowed':
      return 'El servicio de reconocimiento está bloqueado.';
    default:
      return `Error de reconocimiento: ${error}`;
  }
}
```

---

## 📊 Comparación: Antes vs Después

### ❌ ANTES (Incorrecto)
```javascript
recognitionRef.current.onerror = (event) => {
  console.error('Error de reconocimiento:', event.error);
  setError(getErrorMessage(event.error));  // ❌ Muestra error en UI
  setIsListening(false);                    // ❌ Detiene el reconocimiento
};

// Resultado:
// - Usuario habla
// - Hace pausa de 2 segundos
// - Sistema lanza 'no-speech'
// - Reconocimiento SE DETIENE ❌
// - Usuario debe presionar botón nuevamente
```

### ✅ DESPUÉS (Correcto)
```javascript
recognitionRef.current.onerror = (event) => {
  console.error('❌ Error de reconocimiento:', event.error);
  
  if (event.error === 'no-speech') {
    console.log('⏸️ Pausa detectada - continuando...');
    return; // ✅ Ignora el error y continúa
  }
  
  setError(getErrorMessage(event.error));
  setIsListening(false);
};

// Resultado:
// - Usuario habla
// - Hace pausa de 2 segundos
// - Sistema lanza 'no-speech' pero NO hace nada
// - Reconocimiento CONTINÚA ✅
// - Usuario puede seguir hablando
```

---

## 🎯 Comportamiento Esperado

### Flujo Correcto:

1. **Usuario presiona botón 🎤**
   ```
   🎙️ Iniciando reconocimiento de voz...
   ✅ Reconocimiento iniciado
   ```

2. **Usuario habla: "Dame las citas"**
   ```
   ⏳ Resultado parcial: dame
   ⏳ Resultado parcial: dame las
   ✅ Resultado final: dame las citas
   ```

3. **Usuario hace pausa de 3 segundos**
   ```
   ⏸️ Pausa detectada (no-speech) - continuando escucha...
   ```
   ⚠️ **El reconocimiento NO se detiene, sigue activo**

4. **Usuario continúa: "de la semana"**
   ```
   ⏳ Resultado parcial: de la
   ✅ Resultado final: de la semana
   ```
   ⚠️ **Transcript ahora es: "dame las citas de la semana"**

5. **Usuario presiona "Enviar" o botón 🛑**
   ```
   🛑 Deteniendo reconocimiento...
   ⏹️ Reconocimiento finalizado
   ```

---

## 🔍 Debugging: Verificar que Funciona

### 1. Abrir Consola del Navegador
Presiona `F12` → Pestaña "Console"

### 2. Presionar Botón de Voz
Deberías ver:
```
🎙️ Iniciando reconocimiento de voz...
📌 Configuración: {lang: 'es-ES', continuous: true, interimResults: true}
✅ Reconocimiento iniciado
```

### 3. Hablar y Hacer Pausa
Al hablar verás:
```
⏳ Resultado parcial: hola
✅ Resultado final: hola mundo
```

Al hacer pausa verás:
```
⏸️ Pausa detectada (no-speech) - continuando escucha...
```
⚠️ **El botón 🎤 debe seguir rojo/activo**

### 4. Verificar que NO Aparece
❌ **NO debería aparecer:**
```
⏹️ Reconocimiento finalizado  ← Si ves esto, el bug persiste
```

---

## 🐛 Otros Problemas Comunes

### Problema: El reconocimiento se reinicia solo
**Síntoma:** Se ven múltiples "Iniciando reconocimiento..."

**Causa:** Llamar `start()` múltiples veces

**Solución:**
```javascript
const startListening = () => {
  if (recognitionRef.current && !isListening) {  // ✅ Verificar !isListening
    try {
      recognitionRef.current.start();
    } catch (err) {
      if (err.message.includes('already started')) {
        console.warn('⚠️ Reconocimiento ya activo');
        return;
      }
    }
  }
};
```

---

### Problema: No funciona en móviles
**Causa:** Algunos navegadores móviles no soportan `continuous: true`

**Solución:**
```javascript
// Detectar móvil
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (isMobile) {
  recognitionRef.current.continuous = false;  // ❌ No continuo en móviles
  // Usuario deberá presionar botón para cada comando
} else {
  recognitionRef.current.continuous = true;   // ✅ Continuo en desktop
}
```

---

### Problema: Se corta después de 60 segundos
**Causa:** Límite del navegador

**Solución:** Reiniciar automáticamente
```javascript
recognitionRef.current.onend = () => {
  console.log('⏹️ Reconocimiento finalizado');
  
  // Si el usuario NO detuvo manualmente, reiniciar
  if (isListening) {
    console.log('🔄 Reiniciando reconocimiento automáticamente...');
    setTimeout(() => {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error('Error al reiniciar:', err);
        setIsListening(false);
      }
    }, 100);
  } else {
    setIsListening(false);
  }
};
```

---

## 📋 Checklist de Verificación

Antes de considerar el bug resuelto, verifica:

- [ ] Al presionar 🎤, se inicia el reconocimiento
- [ ] Al hablar, se transcribe correctamente
- [ ] Al hacer pausa, el botón 🎤 sigue activo (rojo)
- [ ] Al hacer pausa, aparece "continuando escucha..." en consola
- [ ] Al seguir hablando después de pausa, continúa transcribiendo
- [ ] Al presionar 🛑, se detiene el reconocimiento
- [ ] NO aparecen errores en la UI por `no-speech`
- [ ] Funciona en Chrome y Edge
- [ ] Funciona con pausas naturales (2-5 segundos)

---

## 🎯 Resumen

**El error `no-speech` es NORMAL y NO debe detener el reconocimiento.**

| Error | Acción |
|-------|--------|
| `no-speech` | ✅ **Ignorar** - El usuario solo hizo pausa |
| `audio-capture` | ❌ Detener - No hay micrófono |
| `not-allowed` | ❌ Detener - Permisos denegados |
| `network` | ❌ Detener - Sin conexión |
| `aborted` | ✅ Ignorar - Usuario detuvo manualmente |

**Cambio clave:**
```javascript
if (event.error === 'no-speech') {
  return; // ✅ No hacer nada
}
```

¡Con esto el sistema de voz funciona correctamente! 🎉
