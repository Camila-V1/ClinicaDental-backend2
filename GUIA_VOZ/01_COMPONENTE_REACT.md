# 🎤 Componente React: Captura de Voz

## 📁 Estructura de Archivos

```
src/
├── components/
│   └── reportes/
│       ├── VoiceReportCapture.jsx     ← Componente principal
│       ├── VoiceReportButton.jsx      ← Botón de micrófono
│       └── VoiceReportModal.jsx       ← Modal de captura
├── services/
│   └── voiceReportService.js          ← Servicio API
└── hooks/
    └── useVoiceRecognition.js         ← Hook para Web Speech API
```

---

## 1️⃣ Hook: `useVoiceRecognition.js`

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
    // Verificar si el navegador soporta Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // Configuración
      recognitionRef.current.continuous = true;  // Escucha continua
      recognitionRef.current.interimResults = true;  // Resultados parciales
      recognitionRef.current.lang = 'es-ES';  // Español
      
      // Eventos
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError(null);
      };
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPart + ' ';
          } else {
            interimTranscript += transcriptPart;
          }
        }
        
        setTranscript(prev => prev + finalTranscript || interimTranscript);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('❌ Error de reconocimiento:', event.error);
        
        // Manejar error 'no-speech' sin detener (es normal, solo pausa)
        if (event.error === 'no-speech') {
          console.log('⏸️ Pausa detectada (no-speech) - continuando escucha...');
          // NO cambiar isListening ni mostrar error
          // El reconocimiento continúa automáticamente
          return;
        }
        
        // Para otros errores, sí detener y mostrar mensaje
        setError(getErrorMessage(event.error));
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
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
      } catch (err) {
        console.error('Error al iniciar:', err);
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

// Función auxiliar para mensajes de error
function getErrorMessage(error) {
  switch (error) {
    case 'no-speech':
      return 'No se detectó ningún audio. Por favor, habla más cerca del micrófono.';
    case 'audio-capture':
      return 'No se pudo acceder al micrófono. Verifica los permisos.';
    case 'not-allowed':
      return 'Permiso denegado. Habilita el acceso al micrófono en la configuración.';
    case 'network':
      return 'Error de red. Verifica tu conexión a internet.';
    default:
      return `Error de reconocimiento: ${error}`;
  }
}
```

---

## 2️⃣ Servicio: `voiceReportService.js`

```javascript
// src/services/voiceReportService.js
import apiClient from './api'; // Tu cliente Axios configurado

export const voiceReportService = {
  /**
   * Envía el comando de voz al backend para procesamiento
   * @param {string} texto - Texto transcrito del comando de voz
   * @returns {Promise} Respuesta con interpretación y datos
   */
  async processVoiceCommand(texto) {
    try {
      const response = await apiClient.post('/reportes/voice-query/', {
        texto: texto.trim()
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error en comando de voz:', error);
      
      return {
        success: false,
        error: error.response?.data?.error || 'Error al procesar el comando de voz'
      };
    }
  },

  /**
   * Valida que el texto tenga contenido mínimo
   */
  validateCommand(texto) {
    if (!texto || texto.trim().length < 5) {
      return {
        valid: false,
        message: 'El comando es muy corto. Por favor, describe qué reporte necesitas.'
      };
    }
    
    return { valid: true };
  }
};
```

---

## 3️⃣ Componente: `VoiceReportButton.jsx`

```javascript
// src/components/reportes/VoiceReportButton.jsx
import React from 'react';
import { Mic } from 'lucide-react';

const VoiceReportButton = ({ onClick, isListening }) => {
  return (
    <button
      onClick={onClick}
      className={`voice-report-button ${isListening ? 'listening' : ''}`}
      title="Reportes por voz"
    >
      <Mic className="mic-icon" size={20} />
      <span>Reportes por Voz</span>
    </button>
  );
};

export default VoiceReportButton;
```

---

## 4️⃣ Componente: `VoiceReportModal.jsx`

```javascript
// src/components/reportes/VoiceReportModal.jsx
import React, { useEffect } from 'react';
import { X, Mic, Square, Send, AlertCircle } from 'lucide-react';
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition';

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

  // Auto-iniciar al abrir el modal
  useEffect(() => {
    if (isOpen && isSupported) {
      startListening();
    }
    
    return () => {
      stopListening();
    };
  }, [isOpen, isSupported]);

  const handleClose = () => {
    stopListening();
    resetTranscript();
    onClose();
  };

  const handleSubmit = () => {
    if (transcript.trim()) {
      stopListening();
      onSubmit(transcript);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="voice-modal-overlay" onClick={handleClose}>
      <div className="voice-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="voice-modal-header">
          <h3>🎤 Comando de Voz</h3>
          <button onClick={handleClose} className="close-button">
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="voice-modal-body">
          {!isSupported ? (
            <div className="error-message">
              <AlertCircle size={24} />
              <p>Tu navegador no soporta reconocimiento de voz.</p>
              <p className="small">Usa Google Chrome o Microsoft Edge.</p>
            </div>
          ) : (
            <>
              {/* Estado del micrófono */}
              <div className={`mic-status ${isListening ? 'active' : ''}`}>
                <div className="mic-icon-wrapper">
                  {isListening ? (
                    <>
                      <Mic size={48} className="mic-icon-large pulse" />
                      <div className="sound-wave">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </>
                  ) : (
                    <Mic size={48} className="mic-icon-large" />
                  )}
                </div>
                <p className="mic-status-text">
                  {isListening ? '🎙️ Escuchando...' : '🔇 Detenido'}
                </p>
              </div>

              {/* Transcripción */}
              <div className="transcript-container">
                <label>Transcripción:</label>
                <div className="transcript-box">
                  {transcript || (
                    <span className="placeholder">
                      {isListening 
                        ? 'Habla ahora...' 
                        : 'Presiona el botón para comenzar'}
                    </span>
                  )}
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="error-alert">
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              {/* Ejemplos */}
              <div className="examples">
                <p className="examples-title">Ejemplos:</p>
                <ul>
                  <li>"Dame las citas del 1 al 5 de septiembre"</li>
                  <li>"Mostrar facturas de la semana pasada"</li>
                  <li>"Ingresos del mes actual"</li>
                  <li>"Facturas pendientes mayores a 1000"</li>
                </ul>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        {isSupported && (
          <div className="voice-modal-footer">
            <button
              onClick={isListening ? stopListening : startListening}
              className={`btn-voice ${isListening ? 'btn-stop' : 'btn-start'}`}
              disabled={isProcessing}
            >
              {isListening ? (
                <>
                  <Square size={16} />
                  Detener
                </>
              ) : (
                <>
                  <Mic size={16} />
                  Iniciar
                </>
              )}
            </button>
            
            <button
              onClick={handleSubmit}
              className="btn-submit"
              disabled={!transcript.trim() || isProcessing}
            >
              <Send size={16} />
              {isProcessing ? 'Procesando...' : 'Generar Reporte'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceReportModal;
```

---

## 5️⃣ Componente Principal: `VoiceReportCapture.jsx`

```javascript
// src/components/reportes/VoiceReportCapture.jsx
import React, { useState } from 'react';
import VoiceReportButton from './VoiceReportButton';
import VoiceReportModal from './VoiceReportModal';
import { voiceReportService } from '../../services/voiceReportService';
import { toast } from 'react-hot-toast'; // o tu librería de notificaciones

const VoiceReportCapture = ({ onReportGenerated }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSubmitCommand = async (transcript) => {
    // Validar comando
    const validation = voiceReportService.validateCommand(transcript);
    if (!validation.valid) {
      toast.error(validation.message);
      return;
    }

    setIsProcessing(true);

    try {
      // Enviar al backend
      const result = await voiceReportService.processVoiceCommand(transcript);

      if (result.success) {
        const { interpretacion, datos, resumen } = result.data;
        
        // Mostrar interpretación al usuario
        toast.success(interpretacion.interpretacion);
        
        // Cerrar modal
        handleCloseModal();
        
        // Pasar datos al componente padre (página de reportes)
        if (onReportGenerated) {
          onReportGenerated({
            tipo: interpretacion.tipo_reporte,
            datos,
            resumen,
            interpretacion
          });
        }
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Error procesando comando:', error);
      toast.error('Error inesperado al procesar el comando');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <VoiceReportButton 
        onClick={handleOpenModal}
        isListening={false}
      />
      
      <VoiceReportModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmitCommand}
        isProcessing={isProcessing}
      />
    </>
  );
};

export default VoiceReportCapture;
```

---

## 📝 Notas de Implementación

### 🔒 Permisos del Navegador
- El usuario debe **permitir** el acceso al micrófono
- Chrome/Edge mostrarán un popup de permisos al iniciar
- Los permisos se guardan por dominio

### 🌐 Compatibilidad
- ✅ **Chrome/Edge:** Soporte completo
- ✅ **Safari:** Soporte parcial (iOS 14.5+)
- ❌ **Firefox:** No soportado (aún)

### 🎯 Mejores Prácticas
- Siempre mostrar estado visual del micrófono
- Permitir edición manual de la transcripción
- Proporcionar ejemplos de comandos
- Manejar errores de permisos gracefully
- Limitar duración máxima de grabación (2-3 minutos)

---

## 🔗 Siguiente Paso

Ver **[02_INTEGRACION_REPORTES.md](02_INTEGRACION_REPORTES.md)** para integrar este componente en la página de reportes.
