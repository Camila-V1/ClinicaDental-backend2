from django.apps import AppConfig


class HistorialClinicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'historial_clinico'
    
    def ready(self):
        """
        Método que se ejecuta cuando Django inicia la aplicación.
        Aquí importamos los signals para que se registren automáticamente.
        """
        import historial_clinico.signals  # noqa
