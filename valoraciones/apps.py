from django.apps import AppConfig


class ValoracionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'valoraciones'
    
    def ready(self):
        # Importar las señales cuando la app esté lista
        import valoraciones.signals
