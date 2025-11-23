# Middleware para permitir apps móviles

class MobileAppMiddleware:
    """
    Middleware que permite peticiones desde apps móviles
    agregando headers necesarios para bypass de Cloudflare.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Agregar headers para identificar apps móviles
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Detectar si es app móvil (Flutter/Dart)
        is_mobile_app = any(agent in user_agent for agent in [
            'ClinicaDentalApp',
            'Dart',
            'Flutter',
            'okhttp',  # Cliente HTTP de Android
        ])
        
        if is_mobile_app:
            # Marcar como petición de app móvil
            request.is_mobile_app = True
        
        response = self.get_response(request)
        
        # Agregar headers de respuesta para apps móviles
        if is_mobile_app:
            response['X-Mobile-App'] = 'allowed'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Host, User-Agent'
        
        return response
