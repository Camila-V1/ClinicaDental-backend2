# 🎤 GUÍA: SOLUCIÓN DE PROBLEMAS - MICRÓFONO NO CAPTA SONIDO

> **Problema:** El componente de reporte por voz no capta el audio del micrófono

---

## 🔍 DIAGNÓSTICO PASO A PASO

### 1️⃣ Verificar Permisos del Navegador

#### Chrome/Edge
1. Click en el **icono de candado** 🔒 en la barra de direcciones
2. Buscar **"Micrófono"**
3. Debe estar en **"Permitir"** ✅
4. Si dice **"Bloqueado" ❌**, cambiarlo a **"Permitir"**
5. **Recargar la página** (F5)

#### Firefox
1. Click en el **icono de escudo** o **candado** en la barra
2. Ver **Permisos → Usar el micrófono**
3. Debe estar **"Permitido"**
4. Si está bloqueado, click en la **X** para eliminar el bloqueo
5. **Recargar la página**

---

### 2️⃣ Verificar HTTPS

⚠️ **IMPORTANTE:** Web Speech API **SOLO funciona en HTTPS** (o en localhost)

**Verificar:**
- ✅ `https://clinica-dental.vercel.app` → **Funciona**
- ✅ `https://localhost:3000` → **Funciona**
- ❌ `http://192.168.1.100:3000` → **NO funciona** (HTTP no seguro)

**Solución si estás en desarrollo:**
```bash
# Opción 1: Usar localhost (siempre funciona)
npm start
# Abre: http://localhost:3000 ✅

# Opción 2: Habilitar HTTPS en desarrollo (Next.js)
# Agregar a package.json:
"dev": "next dev --experimental-https"

# Opción 3: Usar ngrok para obtener HTTPS
ngrok http 3000
# Te da una URL https://abc123.ngrok.io
```

---

### 3️⃣ Verificar Configuración del Sistema

#### Windows
1. **Abrir Configuración** → **Privacidad y seguridad** → **Micrófono**
2. **"Permitir que las aplicaciones accedan al micrófono"** debe estar **Activado** ✅
3. **"Permitir que las aplicaciones de escritorio accedan al micrófono"** → **Activado** ✅
4. Buscar tu navegador (Chrome/Edge/Firefox) y verificar que esté **Activado** ✅

#### macOS
1. **Preferencias del Sistema** → **Seguridad y privacidad** → **Privacidad** → **Micrófono**
2. Buscar tu navegador y marcar el checkbox ✅

#### Linux
```bash
# Verificar que el micrófono esté conectado
arecord -l

# Probar grabación
arecord -d 5 test.wav
aplay test.wav

# Si no funciona, instalar PulseAudio
sudo apt install pulseaudio
```

---

### 4️⃣ Verificar Código del Hook

**Archivo:** `src/hooks/useVoiceRecognition.js`

```javascript
import { useState, useEffect, useRef } from 'react';

export const useVoiceRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Verificar soporte
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // ✅ CONFIGURACIÓN CORRECTA
      recognitionRef.current.continuous = true;      // Escucha continua
      recognitionRef.current.interimResults = true;  // Resultados parciales
      recognitionRef.current.lang = 'es-ES';         // Español de España
      recognitionRef.current.maxAlternatives = 1;
      
      // ⚠️ IMPORTANTE: Manejar correctamente el error 'no-speech'
      recognitionRef.current.onerror = (event) => {
        console.error('❌ Error de reconocimiento:', event.error);
        
        // NO detener por 'no-speech' - es normal cuando hay silencio
        if (event.error === 'no-speech') {
          console.log('⏸️ Silencio detectado - continuando escucha...');
          return; // NO cambiar isListening
        }
        
        // Otros errores sí detienen
        setError(getErrorMessage(event.error));
        setIsListening(false);
      };
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const text = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += text + ' ';
          }
        }
        
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript);
        }
      };
      
      recognitionRef.current.onstart = () => {
        console.log('🎤 Micrófono iniciado');
        setIsListening(true);
        setError(null);
      };
      
      recognitionRef.current.onend = () => {
        console.log('🎤 Micrófono detenido');
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
        console.log('✅ Iniciando reconocimiento de voz...');
      } catch (err) {
        console.error('❌ Error al iniciar:', err);
        setError('No se pudo iniciar el micrófono');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
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

// Mensajes de error amigables
function getErrorMessage(error) {
  const messages = {
    'no-speech': 'No se detectó voz. Intenta hablar más cerca del micrófono.',
    'audio-capture': 'No se pudo acceder al micrófono. Verifica los permisos.',
    'not-allowed': 'Permiso denegado. Permite el acceso al micrófono.',
    'network': 'Error de red. Verifica tu conexión.',
    'aborted': 'Reconocimiento cancelado.',
    'service-not-allowed': 'Servicio de voz no permitido. Verifica HTTPS.'
  };
  
  return messages[error] || `Error desconocido: ${error}`;
}
```

---

### 5️⃣ Agregar Logs de Depuración

Modificar el componente modal para ver qué está pasando:

```javascript
// VoiceReportModal.jsx
const VoiceReportModal = ({ isOpen, onClose, onSubmit, isProcessing }) => {
  const {
    isListening,
    transcript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript
  } = useVoiceRecognition();

  useEffect(() => {
    console.log('📊 Estado actual:', {
      isOpen,
      isSupported,
      isListening,
      transcript,
      error
    });
    
    if (isOpen && isSupported) {
      console.log('🎤 Intentando iniciar micrófono...');
      startListening();
    }
    
    return () => {
      stopListening();
    };
  }, [isOpen, isSupported]);

  // Agregar indicador visual de permisos
  useEffect(() => {
    if (isOpen) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          console.log('✅ Permisos de micrófono concedidos');
        })
        .catch((err) => {
          console.error('❌ Error de permisos:', err);
          alert(`Error: ${err.message}. Verifica los permisos del navegador.`);
        });
    }
  }, [isOpen]);

  // ... resto del componente
};
```

---

### 6️⃣ Probar con Herramienta de Diagnóstico

Crear una página de prueba simple:

```javascript
// src/pages/TestMicrofono.jsx
import React, { useState, useEffect } from 'react';

const TestMicrofono = () => {
  const [status, setStatus] = useState('Cargando...');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  useEffect(() => {
    // Test 1: Verificar soporte
    if (!('webkitSpeechRecognition' in window)) {
      setStatus('❌ Navegador no soportado. Usa Chrome o Edge.');
      return;
    }
    
    setStatus('✅ Web Speech API disponible');
    
    // Test 2: Verificar permisos
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => {
        setStatus('✅ Permisos de micrófono OK');
      })
      .catch((err) => {
        setStatus(`❌ Error de permisos: ${err.message}`);
      });
  }, []);

  const handleTest = () => {
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'es-ES';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('Escuchando...');
    };
    
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(`Dijiste: "${text}"`);
    };
    
    recognition.onerror = (event) => {
      setTranscript(`Error: ${event.error}`);
      setIsListening(false);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognition.start();
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>🎤 Test de Micrófono</h1>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong>Estado:</strong> {status}
      </div>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong>URL:</strong> {window.location.protocol}//{window.location.host}
        {window.location.protocol === 'https:' ? ' ✅' : ' ❌ (requiere HTTPS)'}
      </div>
      
      <button 
        onClick={handleTest}
        disabled={isListening}
        style={{
          padding: '1rem 2rem',
          fontSize: '1.2rem',
          cursor: 'pointer',
          backgroundColor: isListening ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '8px'
        }}
      >
        {isListening ? '🎤 Escuchando...' : '▶️ Iniciar Test'}
      </button>
      
      <div style={{ 
        marginTop: '2rem', 
        padding: '1rem', 
        backgroundColor: '#f0f0f0',
        borderRadius: '8px',
        minHeight: '100px'
      }}>
        <strong>Transcripción:</strong>
        <div style={{ marginTop: '0.5rem' }}>{transcript}</div>
      </div>
    </div>
  );
};

export default TestMicrofono;
```

**Acceder a:** `http://localhost:3000/test-microfono`

---

## 🐛 ERRORES COMUNES Y SOLUCIONES

### Error: "not-allowed"
**Causa:** Permisos denegados  
**Solución:**
1. Borrar permisos del sitio en configuración del navegador
2. Recargar página
3. Dar permisos cuando pregunte

### Error: "audio-capture"
**Causa:** Micrófono no disponible  
**Solución:**
1. Verificar que el micrófono esté conectado
2. Verificar que no esté siendo usado por otra aplicación (Zoom, Teams, etc.)
3. En Windows: Configuración → Sonido → verificar dispositivo de entrada

### Error: "service-not-allowed"
**Causa:** No estás en HTTPS  
**Solución:**
- Usar `https://` en producción
- Usar `http://localhost:3000` en desarrollo (funciona sin HTTPS)
- NO usar IP local como `http://192.168.1.100`

### Transcripción vacía
**Causa:** Idioma incorrecto o volumen bajo  
**Solución:**
```javascript
// Cambiar idioma según tu región
recognition.lang = 'es-ES';  // España
recognition.lang = 'es-MX';  // México
recognition.lang = 'es-AR';  // Argentina
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] ¿Está en HTTPS o localhost?
- [ ] ¿Los permisos del navegador están en "Permitir"?
- [ ] ¿Los permisos del sistema operativo están activados?
- [ ] ¿El micrófono funciona en otras aplicaciones?
- [ ] ¿El código tiene `lang: 'es-ES'`?
- [ ] ¿El código tiene `continuous: true`?
- [ ] ¿Maneja correctamente el error 'no-speech'?
- [ ] ¿La consola muestra logs de inicio del micrófono?

---

## 📞 SOPORTE ADICIONAL

Si nada funciona:

1. **Probar en modo incógnito** (sin extensiones)
2. **Probar en otro navegador** (Chrome, Edge, Brave)
3. **Revisar la consola del navegador** (F12) para ver errores
4. **Verificar que no haya AdBlockers** bloqueando el micrófono

---

**Última actualización:** 27/11/2025
