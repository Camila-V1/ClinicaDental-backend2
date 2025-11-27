# 🎤 Integración con Reconocimiento de Voz

## 🔄 Reutilizar Hook de Voz

El chatbot puede reutilizar el **mismo hook** que se creó para reportes por voz:

```javascript
// Ya existe en: src/hooks/useVoiceRecognition.js
export const useVoiceRecognition = () => {
  // ... implementación del hook
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
```

---

## 📝 Uso en ChatInput

```javascript
// src/components/chatbot/ChatInput.jsx
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition';

const ChatInput = ({ onEnviarMensaje }) => {
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript
  } = useVoiceRecognition();

  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
      if (transcript) {
        onEnviarMensaje(transcript, true); // true = es_voz
        resetTranscript();
      }
    } else {
      startListening();
    }
  };

  return (
    <button onClick={handleVoiceClick}>
      🎤 {isListening ? 'Detener' : 'Hablar'}
    </button>
  );
};
```

---

## 🎯 Flujo de Voz

```
Usuario presiona 🎤
       ↓
Web Speech API escucha
       ↓
Transcribe a texto en español
       ↓
Muestra transcripción en input
       ↓
Usuario presiona 🎤 de nuevo (o envía)
       ↓
POST /api/chatbot/query/ {texto: "...", es_voz: true}
       ↓
Backend procesa NLP
       ↓
Respuesta estructurada
       ↓
Frontend renderiza respuesta
```

---

## 💡 Mejoras Opcionales

### 1. Auto-envío tras detener voz
```javascript
const handleVoiceClick = () => {
  if (isListening) {
    stopListening();
    // Auto-enviar al detener
    setTimeout(() => {
      if (transcript) {
        onEnviarMensaje(transcript, true);
        resetTranscript();
      }
    }, 500);
  } else {
    startListening();
  }
};
```

### 2. Feedback visual mientras escucha
```javascript
{isListening && (
  <div className="voice-indicator">
    <span className="pulse">🎤</span>
    Escuchando...
  </div>
)}
```

### 3. Confirmación antes de enviar
```javascript
{transcript && !isListening && (
  <div className="voice-preview">
    <p>Escuché: "{transcript}"</p>
    <button onClick={() => onEnviarMensaje(transcript, true)}>
      ✅ Enviar
    </button>
    <button onClick={resetTranscript}>
      ❌ Borrar
    </button>
  </div>
)}
```

---

## 🔗 Integración Completa

El chatbot y los reportes por voz comparten:
- ✅ Mismo hook `useVoiceRecognition`
- ✅ Misma configuración Web Speech API
- ✅ Mismo idioma (español)
- ✅ Misma lógica de transcripción

**Solo difieren en el endpoint:**
- Reportes: `/api/reportes/voice-query/`
- Chatbot: `/api/chatbot/query/`
