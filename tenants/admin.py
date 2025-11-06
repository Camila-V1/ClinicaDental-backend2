from django.contrib import admin
from django.db import connection
from .models import Clinica, Domain


# --- SOLO REGISTRAR SI ESTAMOS EN EL ESQUEMA PÚBLICO ---
if connection.schema_name == 'public':

    @admin.register(Clinica)
    class ClinicaAdmin(admin.ModelAdmin):
        list_display = ('nombre', 'dominio', 'activo', 'creado')
        list_filter = ('activo',)
        search_fields = ('nombre', 'dominio')


    @admin.register(Domain)
    class DomainAdmin(admin.ModelAdmin):
        list_display = ('domain', 'tenant')
