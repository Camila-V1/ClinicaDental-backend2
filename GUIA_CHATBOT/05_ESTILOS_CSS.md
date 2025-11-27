# 🎨 Estilos CSS para Chatbot

```css
/* src/styles/chatbot.css */

/* =====================================================
   BURBUJA FLOTANTE
   ===================================================== */
.chat-bubble {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1000;
}

.chat-bubble:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
}

.chat-bubble.hidden {
  display: none;
}

.chat-bubble .badge {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 18px;
}


/* =====================================================
   VENTANA DE CHAT
   ===================================================== */
.chat-window {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 380px;
  height: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}


/* =====================================================
   HEADER
   ===================================================== */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.chat-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.chat-header .status {
  font-size: 12px;
  opacity: 0.9;
}

.chat-header-actions {
  display: flex;
  gap: 8px;
}

.icon-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.icon-button:hover {
  background: rgba(255, 255, 255, 0.3);
}


/* =====================================================
   MENSAJES
   ===================================================== */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.usuario {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  word-wrap: break-word;
}

.chat-message.usuario .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-bubble.error {
  background: #fee2e2;
  color: #991b1b;
  border-left: 4px solid #dc2626;
}

.message-bubble p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.voice-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.3);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  margin-right: 8px;
}

.message-time {
  font-size: 11px;
  color: #9ca3af;
  align-self: flex-end;
}


/* =====================================================
   SUGERENCIAS
   ===================================================== */
.message-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.suggestion-chip {
  padding: 6px 12px;
  background: #eff6ff;
  border: 1px solid #3b82f6;
  border-radius: 16px;
  font-size: 12px;
  color: #1e40af;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-2px);
}


/* =====================================================
   INDICADOR "ESCRIBIENDO..."
   ===================================================== */
.message-bubble.typing {
  display: flex;
  gap: 4px;
  padding: 16px;
  width: 60px;
}

.message-bubble.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9ca3af;
  animation: typing 1.4s infinite ease-in-out;
}

.message-bubble.typing span:nth-child(1) { animation-delay: 0s; }
.message-bubble.typing span:nth-child(2) { animation-delay: 0.2s; }
.message-bubble.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
  30% { transform: translateY(-10px); opacity: 1; }
}


/* =====================================================
   INPUT
   ===================================================== */
.chat-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 16px 16px;
}

.chat-input input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border 0.2s;
}

.chat-input input:focus {
  border-color: #667eea;
}

.chat-input input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.voice-button,
.send-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.voice-button {
  background: #10b981;
  color: white;
}

.voice-button:hover {
  background: #059669;
}

.voice-button.listening {
  background: #ef4444;
  animation: pulse 1.5s infinite;
}

.send-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.1);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


/* =====================================================
   DATOS ESTRUCTURADOS
   ===================================================== */
.data-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.data-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
}

.data-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.data-card.highlight {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.card-icon {
  font-size: 20px;
}

.card-body p {
  margin: 4px 0;
  font-size: 13px;
  color: #374151;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin: 8px 0 4px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
}

.btn-cancel {
  width: 100%;
  padding: 8px;
  margin-top: 8px;
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #fecaca;
}


/* =====================================================
   COMANDOS (AYUDA)
   ===================================================== */
.commands-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.command-item {
  padding: 10px;
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.command-item:hover {
  background: #dbeafe;
  transform: translateX(4px);
}

.command-item strong {
  display: block;
  font-size: 13px;
  color: #1e40af;
  margin-bottom: 4px;
}

.text-small {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.text-danger {
  color: #dc2626;
  font-weight: 600;
}


/* =====================================================
   BADGES
   ===================================================== */
.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.confirmada {
  background: #d1fae5;
  color: #065f46;
}

.badge.pendiente {
  background: #fef3c7;
  color: #92400e;
}

.badge.cancelada {
  background: #fee2e2;
  color: #991b1b;
}


/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 640px) {
  .chat-window {
    width: 100%;
    height: 100%;
    max-height: 100vh;
    bottom: 0;
    right: 0;
    border-radius: 0;
  }

  .chat-bubble {
    bottom: 16px;
    right: 16px;
    width: 56px;
    height: 56px;
  }

  .message-content {
    max-width: 80%;
  }
}
```

---

## 🎯 Uso en la Aplicación

```javascript
// src/App.jsx
import ChatWidget from './components/chatbot/ChatWidget';
import './styles/chatbot.css';

function App() {
  return (
    <div>
      {/* Tu aplicación */}
      
      {/* Chatbot flotante */}
      <ChatWidget />
    </div>
  );
}
```

El chatbot aparecerá como una **burbuja flotante** en la esquina inferior derecha, disponible en todas las páginas!
