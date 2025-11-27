// lib/features/chatbot/providers/chatbot_provider.dart

import 'package:flutter/foundation.dart';
import '../models/mensaje_model.dart';
import '../models/conversacion_model.dart';
import '../services/chatbot_service.dart';

class ChatbotProvider with ChangeNotifier {
  final ChatbotService _chatbotService;

  ChatbotProvider(this._chatbotService);

  // Estado de la conversación actual
  ConversacionModel? _conversacionActual;
  List<MensajeModel> _mensajes = [];
  bool _isLoading = false;
  bool _isTyping = false;
  String? _error;

  // Lista de conversaciones
  List<ConversacionModel> _conversaciones = [];

  // Getters
  ConversacionModel? get conversacionActual => _conversacionActual;
  List<MensajeModel> get mensajes => _mensajes;
  bool get isLoading => _isLoading;
  bool get isTyping => _isTyping;
  String? get error => _error;
  List<ConversacionModel> get conversaciones => _conversaciones;

  /// Envía un mensaje al chatbot
  Future<void> enviarMensaje(String mensaje) async {
    if (mensaje.trim().isEmpty) return;

    _error = null;

    // Agregar mensaje del usuario a la UI inmediatamente
    final mensajeUsuario = MensajeModel(
      role: 'user',
      content: mensaje,
      timestamp: DateTime.now(),
    );

    _mensajes.add(mensajeUsuario);
    notifyListeners();

    // Mostrar indicador de escritura
    _isTyping = true;
    notifyListeners();

    try {
      // Enviar al backend
      final response = await _chatbotService.enviarMensaje(
        mensaje: mensaje,
        conversacionId: _conversacionActual?.id,
      );

      // Actualizar conversación actual si es nueva
      if (_conversacionActual == null) {
        _conversacionActual = ConversacionModel(
          id: response.conversacionId,
          titulo: mensaje.length > 50
              ? '${mensaje.substring(0, 50)}...'
              : mensaje,
          mensajes: [response.mensajeUsuario, response.mensajeBot],
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
      }

      // Agregar respuesta del bot
      _mensajes.add(response.mensajeBot);

      _isTyping = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isTyping = false;

      // Agregar mensaje de error
      _mensajes.add(
        MensajeModel(
          role: 'assistant',
          content:
              'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
          timestamp: DateTime.now(),
          metadata: {'error': true},
        ),
      );

      notifyListeners();
    }
  }

  /// Carga una conversación existente
  Future<void> cargarConversacion(int conversacionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final conversacion = await _chatbotService.obtenerConversacion(
        conversacionId,
      );

      _conversacionActual = conversacion;
      _mensajes = conversacion.mensajes;

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Carga la lista de conversaciones
  Future<void> cargarConversaciones() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _conversaciones = await _chatbotService.obtenerConversaciones();

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Inicia una nueva conversación
  void nuevaConversacion() {
    _conversacionActual = null;
    _mensajes = [];
    _error = null;
    notifyListeners();
  }

  /// Limpia el estado
  void limpiar() {
    _conversacionActual = null;
    _mensajes = [];
    _isLoading = false;
    _isTyping = false;
    _error = null;
    _conversaciones = [];
    notifyListeners();
  }
}

// Uso en main.dart:
/*
import 'package:provider/provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => ChatbotProvider(
            ChatbotService(
              baseUrl: 'https://tu-backend.com',
              tenantId: 'clinica_demo',
              getToken: () async => 'tu_token',
            ),
          ),
        ),
      ],
      child: MyApp(),
    ),
  );
}
*/
