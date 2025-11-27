# 🎨 Estilos CSS para Reportes por Voz

## 📁 Ubicación

```
src/styles/
├── components/
│   └── voice-report.css     ← Estilos del componente de voz
└── pages/
    └── reportes.css         ← Estilos de la página de reportes
```

---

## 1️⃣ Estilos del Componente de Voz

```css
/* src/styles/components/voice-report.css */

/* =====================================================
   BOTÓN DE MICRÓFONO
   ===================================================== */
.voice-report-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
}

.voice-report-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
}

.voice-report-button:active {
  transform: translateY(0);
}

.voice-report-button.listening {
  animation: pulse 1.5s infinite;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 6px rgba(245, 87, 108, 0.3);
  }
  50% {
    box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
  }
}

.mic-icon {
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}


/* =====================================================
   MODAL DE CAPTURA
   ===================================================== */
.voice-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.voice-modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
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
   HEADER DEL MODAL
   ===================================================== */
.voice-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.voice-modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.close-button {
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

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}


/* =====================================================
   BODY DEL MODAL
   ===================================================== */
.voice-modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

/* Estado del micrófono */
.mic-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  margin-bottom: 24px;
}

.mic-icon-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.mic-icon-large {
  color: #667eea;
  filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
}

.mic-icon-large.pulse {
  animation: micPulse 1.5s infinite;
}

@keyframes micPulse {
  0%, 100% {
    transform: scale(1);
    color: #667eea;
  }
  50% {
    transform: scale(1.1);
    color: #f5576c;
  }
}

/* Ondas de sonido */
.sound-wave {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 4px;
  align-items: center;
  margin-top: 60px;
}

.sound-wave span {
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 2px;
  animation: soundWave 1s infinite ease-in-out;
}

.sound-wave span:nth-child(1) { animation-delay: 0s; }
.sound-wave span:nth-child(2) { animation-delay: 0.2s; }
.sound-wave span:nth-child(3) { animation-delay: 0.4s; }

@keyframes soundWave {
  0%, 100% { height: 20px; }
  50% { height: 40px; }
}

.mic-status-text {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.mic-status.active .mic-status-text {
  color: #f5576c;
}


/* =====================================================
   TRANSCRIPCIÓN
   ===================================================== */
.transcript-container {
  margin-bottom: 24px;
}

.transcript-container label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.transcript-box {
  min-height: 100px;
  padding: 16px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  color: #111827;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.transcript-box .placeholder {
  color: #9ca3af;
  font-style: italic;
}


/* =====================================================
   EJEMPLOS
   ===================================================== */
.examples {
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  padding: 16px;
  border-radius: 8px;
  margin-top: 20px;
}

.examples-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e40af;
  margin: 0 0 12px 0;
}

.examples ul {
  margin: 0;
  padding-left: 20px;
  list-style: disc;
}

.examples li {
  font-size: 13px;
  color: #1e3a8a;
  margin-bottom: 6px;
  line-height: 1.5;
}


/* =====================================================
   ERRORES
   ===================================================== */
.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: #dc2626;
}

.error-message svg {
  margin-bottom: 16px;
}

.error-message p {
  margin: 4px 0;
  font-size: 15px;
}

.error-message .small {
  font-size: 13px;
  color: #9ca3af;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  margin-top: 16px;
}


/* =====================================================
   FOOTER DEL MODAL
   ===================================================== */
.voice-modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn-voice {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-start {
  background: #10b981;
  color: white;
}

.btn-start:hover {
  background: #059669;
}

.btn-stop {
  background: #ef4444;
  color: white;
}

.btn-stop:hover {
  background: #dc2626;
}

.btn-submit {
  flex: 1.5;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 640px) {
  .voice-modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .voice-modal-footer {
    flex-direction: column;
  }

  .btn-voice,
  .btn-submit {
    width: 100%;
  }

  .mic-icon-wrapper {
    width: 100px;
    height: 100px;
  }
}
```

---

## 2️⃣ Estilos de la Página de Reportes

```css
/* src/styles/pages/reportes.css */

/* =====================================================
   BANNER DE INTERPRETACIÓN
   ===================================================== */
.voice-interpretation-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.banner-icon {
  flex-shrink: 0;
  animation: bounce 1s ease-in-out infinite;
}

.banner-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.banner-text strong {
  font-size: 14px;
  font-weight: 700;
  opacity: 0.9;
}

.banner-text span {
  font-size: 16px;
  font-weight: 500;
}

.banner-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 24px;
  color: white;
  transition: all 0.2s;
  flex-shrink: 0;
}

.banner-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}


/* =====================================================
   TARJETA DE RESUMEN
   ===================================================== */
.voice-summary-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.voice-summary-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}


/* =====================================================
   TABLA DE REPORTES
   ===================================================== */
.report-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.report-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.report-table th {
  padding: 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.report-table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
  color: #374151;
}

.report-table tbody tr:hover {
  background: #f9fafb;
}

.report-table tbody tr:last-child td {
  border-bottom: none;
}

/* Badges de estado */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-confirmada,
.badge-completado,
.badge-activo {
  background: #d1fae5;
  color: #065f46;
}

.badge-pendiente {
  background: #fef3c7;
  color: #92400e;
}

.badge-cancelada,
.badge-inactivo {
  background: #fee2e2;
  color: #991b1b;
}

.text-success {
  color: #10b981;
  font-weight: 600;
}


/* =====================================================
   EMPTY STATE
   ===================================================== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 700;
  color: #374151;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}


/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 768px) {
  .banner-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-stats {
    grid-template-columns: 1fr;
  }

  .report-table {
    font-size: 12px;
  }

  .report-table th,
  .report-table td {
    padding: 12px 8px;
  }
}
```

---

## 3️⃣ Importar en tu Aplicación

```javascript
// src/App.jsx o src/index.jsx
import './styles/components/voice-report.css';
import './styles/pages/reportes.css';
```

O si usas Tailwind CSS, puedes adaptar estas clases a utilidades de Tailwind.

---

## 🔗 Siguiente Paso

Ver **[04_EJEMPLOS_USO.md](04_EJEMPLOS_USO.md)** para ejemplos de comandos de voz.
