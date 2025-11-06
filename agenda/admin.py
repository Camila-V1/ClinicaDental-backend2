from django.contrib import admin
from django.db import connection

# --- SOLO REGISTRAR SI NO ESTAMOS EN EL ESQUEMA PÚBLICO ---
if connection.schema_name != 'public':
    # Register your models here.
    # (Cuando tengas modelos en esta app, los registrarás aquí dentro)
    pass
