// lib/features/chatbot/screens/chat_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chatbot_provider.dart';
import '../widgets/mensaje_bubble.dart';
import '../widgets/chat_input.dart';
import '../widgets/typing_indicator.dart';

class ChatScreen extends StatefulWidget {
  final int? conversacionId;

  const ChatScreen({Key? key, this.conversacionId}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ChatbotProvider>();
      
      if (widget.conversacionId != null) {
        // Cargar conversación existente
        provider.cargarConversacion(widget.conversacionId!);
      } else {
        // Nueva conversación
        provider.nuevaConversacion();
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DentalBot 🦷'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<ChatbotProvider>().nuevaConversacion();
            },
            tooltip: 'Nueva conversación',
          ),
        ],
      ),
      body: Consumer<ChatbotProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.mensajes.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          return Column(
            children: [
              // Mensajes
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: provider.mensajes.length + (provider.isTyping ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (provider.isTyping && index == provider.mensajes.length) {
                      return const TypingIndicator();
                    }

                    final mensaje = provider.mensajes[index];
                    return MensajeBubble(mensaje: mensaje);
                  },
                ),
              ),

              // Error message
              if (provider.error != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(8),
                  color: Colors.red[100],
                  child: Text(
                    provider.error!,
                    style: TextStyle(color: Colors.red[900]),
                    textAlign: TextAlign.center,
                  ),
                ),

              // Input de chat
              ChatInput(
                onSend: (mensaje) async {
                  await provider.enviarMensaje(mensaje);
                  _scrollToBottom();
                },
                enabled: !provider.isTyping,
              ),
            ],
          );
        },
      ),
    );
  }
}

// lib/features/chatbot/screens/conversaciones_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../providers/chatbot_provider.dart';
import 'chat_screen.dart';

class ConversacionesScreen extends StatefulWidget {
  const ConversacionesScreen({Key? key}) : super(key: key);

  @override
  State<ConversacionesScreen> createState() => _ConversacionesScreenState();
}

class _ConversacionesScreenState extends State<ConversacionesScreen> {
  @override
  void initState() {
    super.initState();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatbotProvider>().cargarConversaciones();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Conversaciones'),
      ),
      body: Consumer<ChatbotProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.conversaciones.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.chat_bubble_outline, size: 80, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text(
                    'No tienes conversaciones',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const ChatScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Iniciar conversación'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => provider.cargarConversaciones(),
            child: ListView.separated(
              itemCount: provider.conversaciones.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final conversacion = provider.conversaciones[index];
                final ultimoMensaje = conversacion.mensajes.isNotEmpty
                    ? conversacion.mensajes.last
                    : null;

                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Theme.of(context).primaryColor,
                    child: const Icon(Icons.smart_toy, color: Colors.white),
                  ),
                  title: Text(
                    conversacion.titulo,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: ultimoMensaje != null
                      ? Text(
                          ultimoMensaje.content,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        )
                      : null,
                  trailing: Text(
                    timeago.format(conversacion.updatedAt, locale: 'es'),
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ChatScreen(
                          conversacionId: conversacion.id,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => const ChatScreen(),
            ),
          );
        },
        child: const Icon(Icons.add_comment),
      ),
    );
  }
}
