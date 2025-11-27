// lib/features/chatbot/models/mensaje_model.dart

class MensajeModel {
  final int? id;
  final String role; // 'user', 'assistant', 'system'
  final String content;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  MensajeModel({
    this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.metadata,
  });

  factory MensajeModel.fromJson(Map<String, dynamic> json) {
    return MensajeModel(
      id: json['id'],
      role: json['role'],
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'metadata': metadata,
    };
  }

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
}

// lib/features/chatbot/models/conversacion_model.dart

class ConversacionModel {
  final int id;
  final String titulo;
  final List<MensajeModel> mensajes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isActive;

  ConversacionModel({
    required this.id,
    required this.titulo,
    required this.mensajes,
    required this.createdAt,
    required this.updatedAt,
    this.isActive = true,
  });

  factory ConversacionModel.fromJson(Map<String, dynamic> json) {
    return ConversacionModel(
      id: json['id'],
      titulo: json['titulo'],
      mensajes: (json['mensajes'] as List? ?? [])
          .map((m) => MensajeModel.fromJson(m))
          .toList(),
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'titulo': titulo,
      'mensajes': mensajes.map((m) => m.toJson()).toList(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'is_active': isActive,
    };
  }
}

// lib/features/chatbot/models/chat_response_model.dart

class ChatResponseModel {
  final int conversacionId;
  final MensajeModel mensajeUsuario;
  final MensajeModel mensajeBot;
  final Map<String, dynamic>? metadata;

  ChatResponseModel({
    required this.conversacionId,
    required this.mensajeUsuario,
    required this.mensajeBot,
    this.metadata,
  });

  factory ChatResponseModel.fromJson(Map<String, dynamic> json) {
    return ChatResponseModel(
      conversacionId: json['conversacion_id'],
      mensajeUsuario: MensajeModel.fromJson(json['mensaje_usuario']),
      mensajeBot: MensajeModel.fromJson(json['mensaje_bot']),
      metadata: json['metadata'],
    );
  }
}
