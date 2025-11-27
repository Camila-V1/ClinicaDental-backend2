# 💬 Componente de Chat para Frontend

## 📁 Estructura de Archivos

```
src/
├── components/
│   └── chatbot/
│       ├── ChatWidget.jsx           ← Widget principal (burbuja flotante)
│       ├── ChatWindow.jsx           ← Ventana de chat
│       ├── ChatMessage.jsx          ← Mensaje individual
│       ├── ChatInput.jsx            ← Input de texto + voz
│       ├── QuickActions.jsx         ← Botones de acciones rápidas
│       └── ChatResponseRenderer.jsx ← Renderiza respuestas según tipo
├── services/
│   └── chatbotService.js            ← Servicio API
├── hooks/
│   └── useChatbot.js                ← Hook para gestionar estado del chat
└── styles/
    └── chatbot.css                  ← Estilos del chat
```

---

## 1️⃣ Servicio: `chatbotService.js`

```javascript
// src/services/chatbotService.js
import apiClient from './api'; // Tu cliente Axios configurado

export const chatbotService = {
  /**
   * Envía un mensaje al chatbot
   * @param {string} texto - Mensaje del usuario
   * @param {boolean} esVoz - Si viene de reconocimiento de voz
   */
  async enviarMensaje(texto, esVoz = false) {
    try {
      const response = await apiClient.post('/chatbot/query/', {
        texto: texto.trim(),
        es_voz: esVoz
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error en chatbot:', error);
      
      return {
        success: false,
        error: error.response?.data?.error || 'Error al procesar tu mensaje'
      };
    }
  },

  /**
   * Comandos sugeridos para mostrar al usuario
   */
  getComandosSugeridos() {
    return [
      { texto: 'Ver mis citas', icono: '📅' },
      { texto: 'Próxima cita', icono: '📆' },
      { texto: 'Mis tratamientos', icono: '🦷' },
      { texto: 'Cuánto debo', icono: '💰' },
      { texto: 'Ver mis pagos', icono: '📋' },
      { texto: 'Ayuda', icono: '💡' }
    ];
  }
};
```

---

## 2️⃣ Hook: `useChatbot.js`

```javascript
// src/hooks/useChatbot.js
import { useState, useEffect, useRef } from 'react';
import { chatbotService } from '../services/chatbotService';

export const useChatbot = () => {
  const [mensajes, setMensajes] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Cargar historial del localStorage
  useEffect(() => {
    const historial = localStorage.getItem('chatbot_historial');
    if (historial) {
      try {
        setMensajes(JSON.parse(historial));
      } catch (error) {
        console.error('Error cargando historial:', error);
      }
    } else {
      // Mensaje de bienvenida
      setMensajes([{
        id: Date.now(),
        tipo: 'bot',
        contenido: '👋 ¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
        timestamp: new Date(),
        sugerencias: ['Ver mis citas', 'Próxima cita', 'Ayuda']
      }]);
    }
  }, []);

  // Guardar historial en localStorage
  useEffect(() => {
    if (mensajes.length > 0) {
      localStorage.setItem('chatbot_historial', JSON.stringify(mensajes));
    }
  }, [mensajes]);

  // Scroll automático al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes]);

  /**
   * Envía un mensaje al chatbot
   */
  const enviarMensaje = async (texto, esVoz = false) => {
    if (!texto.trim()) return;

    // Agregar mensaje del usuario
    const mensajeUsuario = {
      id: Date.now(),
      tipo: 'usuario',
      contenido: texto,
      timestamp: new Date(),
      esVoz
    };
    setMensajes(prev => [...prev, mensajeUsuario]);

    // Mostrar indicador de "escribiendo..."
    setIsTyping(true);

    try {
      // Enviar al backend
      const resultado = await chatbotService.enviarMensaje(texto, esVoz);

      if (resultado.success) {
        const respuestaBot = {
          id: Date.now() + 1,
          tipo: 'bot',
          contenido: resultado.data.mensaje,
          timestamp: new Date(),
          datos: resultado.data.datos,
          tipoRespuesta: resultado.data.tipo_respuesta,
          sugerencias: resultado.data.sugerencias,
          intencion: resultado.data.intencion,
          requiereSeleccion: resultado.data.requiere_seleccion,
          accion: resultado.data.accion,
          redirectUrl: resultado.data.redirect_url
        };
        setMensajes(prev => [...prev, respuestaBot]);
      } else {
        // Error
        const errorMsg = {
          id: Date.now() + 1,
          tipo: 'bot',
          contenido: resultado.error,
          timestamp: new Date(),
          esError: true
        };
        setMensajes(prev => [...prev, errorMsg]);
      }
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      const errorMsg = {
        id: Date.now() + 1,
        tipo: 'bot',
        contenido: 'Lo siento, ocurrió un error. Por favor intenta de nuevo.',
        timestamp: new Date(),
        esError: true
      };
      setMensajes(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Limpia el historial de chat
   */
  const limpiarChat = () => {
    setMensajes([{
      id: Date.now(),
      tipo: 'bot',
      contenido: '👋 Historial limpiado. ¿En qué puedo ayudarte?',
      timestamp: new Date(),
      sugerencias: ['Ver mis citas', 'Próxima cita', 'Ayuda']
    }]);
    localStorage.removeItem('chatbot_historial');
  };

  /**
   * Abre/cierra el chat
   */
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return {
    mensajes,
    isTyping,
    isOpen,
    enviarMensaje,
    limpiarChat,
    toggleChat,
    messagesEndRef
  };
};
```

---

## 3️⃣ Componente: `ChatWidget.jsx`

```javascript
// src/components/chatbot/ChatWidget.jsx
import React from 'react';
import { MessageCircle, X } from 'lucide-react';
import ChatWindow from './ChatWindow';
import { useChatbot } from '../../hooks/useChatbot';

const ChatWidget = () => {
  const chatbot = useChatbot();

  return (
    <>
      {/* Ventana de chat */}
      {chatbot.isOpen && (
        <ChatWindow
          mensajes={chatbot.mensajes}
          isTyping={chatbot.isTyping}
          onEnviarMensaje={chatbot.enviarMensaje}
          onLimpiarChat={chatbot.limpiarChat}
          onCerrar={chatbot.toggleChat}
          messagesEndRef={chatbot.messagesEndRef}
        />
      )}

      {/* Burbuja flotante */}
      <button
        className={`chat-bubble ${chatbot.isOpen ? 'hidden' : ''}`}
        onClick={chatbot.toggleChat}
        aria-label="Abrir chat"
      >
        <MessageCircle size={24} />
        <span className="badge">💬</span>
      </button>
    </>
  );
};

export default ChatWidget;
```

---

## 4️⃣ Componente: `ChatWindow.jsx`

```javascript
// src/components/chatbot/ChatWindow.jsx
import React from 'react';
import { X, Trash2 } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

const ChatWindow = ({ 
  mensajes, 
  isTyping, 
  onEnviarMensaje, 
  onLimpiarChat, 
  onCerrar,
  messagesEndRef 
}) => {
  return (
    <div className="chat-window">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="bot-avatar">🤖</div>
          <div>
            <h3>Asistente Virtual</h3>
            <span className="status">● En línea</span>
          </div>
        </div>
        <div className="chat-header-actions">
          <button 
            onClick={onLimpiarChat} 
            className="icon-button"
            title="Limpiar chat"
          >
            <Trash2 size={18} />
          </button>
          <button 
            onClick={onCerrar} 
            className="icon-button"
            title="Cerrar"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {mensajes.map((mensaje) => (
          <ChatMessage 
            key={mensaje.id} 
            mensaje={mensaje}
            onEnviarMensaje={onEnviarMensaje}
          />
        ))}
        
        {isTyping && (
          <div className="chat-message bot">
            <div className="message-bubble typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onEnviarMensaje={onEnviarMensaje} />
    </div>
  );
};

export default ChatWindow;
```

---

## 5️⃣ Componente: `ChatMessage.jsx`

```javascript
// src/components/chatbot/ChatMessage.jsx
import React from 'react';
import ChatResponseRenderer from './ChatResponseRenderer';

const ChatMessage = ({ mensaje, onEnviarMensaje }) => {
  const { tipo, contenido, timestamp, esVoz, esError, sugerencias } = mensaje;

  return (
    <div className={`chat-message ${tipo}`}>
      {tipo === 'bot' && <div className="message-avatar">🤖</div>}
      
      <div className="message-content">
        <div className={`message-bubble ${esError ? 'error' : ''}`}>
          {esVoz && tipo === 'usuario' && <span className="voice-badge">🎤</span>}
          
          <p>{contenido}</p>
          
          {/* Renderizar datos estructurados */}
          {mensaje.datos && (
            <ChatResponseRenderer 
              datos={mensaje.datos}
              tipoRespuesta={mensaje.tipoRespuesta}
              onEnviarMensaje={onEnviarMensaje}
            />
          )}
        </div>
        
        {/* Sugerencias */}
        {sugerencias && sugerencias.length > 0 && (
          <div className="message-suggestions">
            {sugerencias.map((sugerencia, index) => (
              <button
                key={index}
                className="suggestion-chip"
                onClick={() => onEnviarMensaje(sugerencia)}
              >
                {sugerencia}
              </button>
            ))}
          </div>
        )}
        
        <span className="message-time">
          {new Date(timestamp).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;
```

---

## 6️⃣ Componente: `ChatInput.jsx`

```javascript
// src/components/chatbot/ChatInput.jsx
import React, { useState } from 'react';
import { Send, Mic } from 'lucide-react';
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition'; // Reutilizar del sistema de voz

const ChatInput = ({ onEnviarMensaje }) => {
  const [texto, setTexto] = useState('');
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript
  } = useVoiceRecognition();

  const handleSubmit = (e) => {
    e.preventDefault();
    const mensaje = texto.trim() || transcript.trim();
    
    if (mensaje) {
      onEnviarMensaje(mensaje, !!transcript);
      setTexto('');
      resetTranscript();
    }
  };

  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
      // Enviar automáticamente después de detener
      if (transcript) {
        onEnviarMensaje(transcript, true);
        resetTranscript();
      }
    } else {
      startListening();
    }
  };

  // Sincronizar transcript con input
  const displayText = transcript || texto;

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <button
        type="button"
        className={`voice-button ${isListening ? 'listening' : ''}`}
        onClick={handleVoiceClick}
        title={isListening ? 'Detener' : 'Hablar'}
      >
        <Mic size={20} />
      </button>
      
      <input
        type="text"
        value={displayText}
        onChange={(e) => setTexto(e.target.value)}
        placeholder={isListening ? 'Escuchando...' : 'Escribe un mensaje...'}
        disabled={isListening}
      />
      
      <button
        type="submit"
        className="send-button"
        disabled={!displayText.trim()}
        title="Enviar"
      >
        <Send size={20} />
      </button>
    </form>
  );
};

export default ChatInput;
```

---

## 7️⃣ Componente: `ChatResponseRenderer.jsx`

```javascript
// src/components/chatbot/ChatResponseRenderer.jsx
import React from 'react';

const ChatResponseRenderer = ({ datos, tipoRespuesta, onEnviarMensaje }) => {
  if (!datos) return null;

  switch (tipoRespuesta) {
    case 'lista_citas':
      return <ListaCitas citas={datos} />;
    
    case 'proxima_cita':
      return <ProximaCita cita={datos} />;
    
    case 'tratamientos':
      return <ListaTratamientos tratamientos={datos} />;
    
    case 'facturas_pendientes':
      return <ListaFacturas facturas={datos} />;
    
    case 'historial_pagos':
      return <ListaPagos pagos={datos} />;
    
    case 'historial_clinico':
      return <ListaEpisodios episodios={datos} />;
    
    case 'cancelar_cita':
      return <CitasCancelables citas={datos} onEnviarMensaje={onEnviarMensaje} />;
    
    case 'ayuda':
      return <ListaComandos comandos={datos} onEnviarMensaje={onEnviarMensaje} />;
    
    default:
      return null;
  }
};

// Componente para lista de citas
const ListaCitas = ({ citas }) => (
  <div className="data-list">
    {citas.map((cita) => (
      <div key={cita.id} className="data-card">
        <div className="card-header">
          <span className="card-icon">📅</span>
          <strong>{cita.fecha} - {cita.hora}</strong>
        </div>
        <div className="card-body">
          <p>🏥 {cita.odontologo}</p>
          <p>📝 {cita.motivo_tipo}</p>
          <span className={`badge ${cita.estado.toLowerCase()}`}>
            {cita.estado}
          </span>
        </div>
      </div>
    ))}
  </div>
);

// Componente para próxima cita
const ProximaCita = ({ cita }) => (
  <div className="data-card highlight">
    <div className="card-header">
      <span className="card-icon">📆</span>
      <strong>{cita.fecha} a las {cita.hora}</strong>
    </div>
    <div className="card-body">
      <p>⏰ {cita.tiempo_restante}</p>
      <p>🏥 {cita.odontologo}</p>
      <p>📝 {cita.motivo_tipo}</p>
    </div>
  </div>
);

// Componente para tratamientos
const ListaTratamientos = ({ tratamientos }) => (
  <div className="data-list">
    {tratamientos.map((tratamiento) => (
      <div key={tratamiento.id} className="data-card">
        <div className="card-header">
          <span className="card-icon">🦷</span>
          <strong>{tratamiento.titulo}</strong>
        </div>
        <div className="card-body">
          <p>🏥 {tratamiento.odontologo}</p>
          <p>💰 Bs. {tratamiento.total.toFixed(2)}</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${tratamiento.porcentaje_completado}%` }}
            />
          </div>
          <p className="progress-text">{tratamiento.porcentaje_completado}% completado</p>
        </div>
      </div>
    ))}
  </div>
);

// Componente para facturas
const ListaFacturas = ({ facturas }) => (
  <div className="data-list">
    {facturas.map((factura) => (
      <div key={factura.id} className="data-card">
        <div className="card-header">
          <span className="card-icon">💰</span>
          <strong>{factura.numero}</strong>
        </div>
        <div className="card-body">
          <p>📅 {factura.fecha}</p>
          <p>Total: Bs. {factura.monto_total.toFixed(2)}</p>
          <p className="text-danger">Saldo: Bs. {factura.saldo.toFixed(2)}</p>
        </div>
      </div>
    ))}
  </div>
);

// Componente para pagos
const ListaPagos = ({ pagos }) => (
  <div className="data-list">
    {pagos.map((pago) => (
      <div key={pago.id} className="data-card">
        <div className="card-header">
          <span className="card-icon">✅</span>
          <strong>Bs. {pago.monto.toFixed(2)}</strong>
        </div>
        <div className="card-body">
          <p>📅 {pago.fecha}</p>
          <p>💳 {pago.metodo}</p>
          <p>📄 {pago.factura}</p>
        </div>
      </div>
    ))}
  </div>
);

// Componente para episodios clínicos
const ListaEpisodios = ({ episodios }) => (
  <div className="data-list">
    {episodios.map((episodio) => (
      <div key={episodio.id} className="data-card">
        <div className="card-header">
          <span className="card-icon">📄</span>
          <strong>{episodio.tipo}</strong>
        </div>
        <div className="card-body">
          <p>📅 {episodio.fecha}</p>
          <p>🏥 {episodio.odontologo}</p>
          <p className="text-small">{episodio.diagnostico}</p>
        </div>
      </div>
    ))}
  </div>
);

// Componente para lista de comandos (ayuda)
const ListaComandos = ({ comandos, onEnviarMensaje }) => (
  <div className="commands-list">
    {comandos.map((comando, index) => (
      <div 
        key={index} 
        className="command-item"
        onClick={() => onEnviarMensaje(comando.ejemplo.split('"')[1])}
      >
        <strong>{comando.descripcion}</strong>
        <p className="text-small">{comando.ejemplo}</p>
      </div>
    ))}
  </div>
);

// Componente para cancelar citas
const CitasCancelables = ({ citas, onEnviarMensaje }) => (
  <div className="data-list">
    {citas.map((cita) => (
      <div key={cita.id} className="data-card cancelable">
        <div className="card-body">
          <p>📅 {cita.fecha} - {cita.hora}</p>
          <p>🏥 {cita.odontologo}</p>
          <p>📝 {cita.motivo_tipo}</p>
          <button 
            className="btn-cancel"
            onClick={() => alert(`Confirmar cancelación de cita ${cita.id}`)}
          >
            ❌ Cancelar esta cita
          </button>
        </div>
      </div>
    ))}
  </div>
);

export default ChatResponseRenderer;
```

---

## 🔗 Archivos Relacionados

- **[04_VOZ_INTEGRATION.md](04_VOZ_INTEGRATION.md)** - Integración con reconocimiento de voz
- **[05_ESTILOS_CSS.md](05_ESTILOS_CSS.md)** - CSS completo con animaciones
- **[02_COMANDOS.md](02_COMANDOS.md)** - Lista de todos los comandos disponibles
