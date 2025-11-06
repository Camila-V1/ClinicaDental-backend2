from django.contrib import admin
from .models import Clinica, Domain


@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dominio', 'activo', 'creado')
    list_filter = ('activo',)
    search_fields = ('nombre', 'dominio')


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant')
