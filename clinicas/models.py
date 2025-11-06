from django.db import models


class Clinica(models.Model):
    """Modelo que representa a un Tenant (Clínica)."""
    nombre = models.CharField(max_length=200)
    dominio = models.CharField(max_length=200, unique=True, help_text="Dominio/identificador del tenant")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"

    def __str__(self):
        return f"{self.nombre} ({self.dominio})"
