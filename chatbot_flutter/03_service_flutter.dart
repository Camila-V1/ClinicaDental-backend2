// lib/features/chatbot/services/chatbot_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/mensaje_model.dart';
import '../models/conversacion_model.dart';
import '../models/chat_response_model.dart';

class ChatbotService {
  final String baseUrl;
  final String tenantId;
  final Function() getToken; // Función para obtener el token JWT

  ChatbotService({
    required this.baseUrl,
    required this.tenantId,
    required this.getToken,
  });

  Future<Map<String, String>> _getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
      'X-Tenant-ID': tenantId,
    };
  }

  /// Envía un mensaje al chatbot
  Future<ChatResponseModel> enviarMensaje({
    required String mensaje,
    int? conversacionId,
    Map<String, dynamic>? contexto,
  }) async {
    try {
      final headers = await _getHeaders();

      final body = jsonEncode({
        'mensaje': mensaje,
        if (conversacionId != null) 'conversacion_id': conversacionId,
        if (contexto != null) 'contexto': contexto,
      });

      final response = await http.post(
        Uri.parse('$baseUrl/api/chatbot/chat/'),
        headers: headers,
        body: body,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ChatResponseModel.fromJson(data);
      } else {
        throw Exception('Error al enviar mensaje: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de red: $e');
    }
  }

  /// Obtiene la lista de conversaciones del usuario
  Future<List<ConversacionModel>> obtenerConversaciones() async {
    try {
      final headers = await _getHeaders();

      final response = await http.get(
        Uri.parse('$baseUrl/api/chatbot/conversaciones/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => ConversacionModel.fromJson(json)).toList();
      } else {
        throw Exception(
          'Error al obtener conversaciones: ${response.statusCode}',
        );
      }
    } catch (e) {
      throw Exception('Error de red: $e');
    }
  }

  /// Obtiene el detalle de una conversación específica
  Future<ConversacionModel> obtenerConversacion(int id) async {
    try {
      final headers = await _getHeaders();

      final response = await http.get(
        Uri.parse('$baseUrl/api/chatbot/conversaciones/$id/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ConversacionModel.fromJson(data);
      } else {
        throw Exception(
          'Error al obtener conversación: ${response.statusCode}',
        );
      }
    } catch (e) {
      throw Exception('Error de red: $e');
    }
  }

  /// Obtiene las capacidades/intentos disponibles del chatbot
  Future<List<Map<String, dynamic>>> obtenerIntentos() async {
    try {
      final headers = await _getHeaders();

      final response = await http.get(
        Uri.parse('$baseUrl/api/chatbot/intentos/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        throw Exception('Error al obtener intentos: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de red: $e');
    }
  }
}

// Ejemplo de uso:
/*
final chatbotService = ChatbotService(
  baseUrl: 'https://clinica-dental-backend.onrender.com',
  tenantId: 'clinica_demo',
  getToken: () async {
    // Implementar obtención del token desde SharedPreferences o similar
    return 'tu_token_jwt';
  },
);

// Enviar mensaje
final response = await chatbotService.enviarMensaje(
  mensaje: '¿Cuáles son los horarios?',
  conversacionId: 1,
);

// Obtener conversaciones
final conversaciones = await chatbotService.obtenerConversaciones();
*/
