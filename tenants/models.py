from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Clinica(TenantMixin):
    """Modelo que representa un Tenant (Clínica).

    Usamos TenantMixin que añade los campos necesarios para django-tenants
    y gestion del schema.
    """
    nombre = models.CharField(max_length=200)
    dominio = models.CharField(max_length=200, unique=True, help_text="Dominio/identificador del tenant")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    # Si se crea esta instancia desde el admin, auto_create_schema=True
    auto_create_schema = True

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"

    def __str__(self):
        return f"{self.nombre} ({self.dominio})"


class Domain(DomainMixin):
    """Modelo Domain para mapear subdominios a tenants.

    Extiende DomainMixin proporcionado por django-tenants.
    """
    pass
