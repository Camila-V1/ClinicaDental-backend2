"""
Scripts de población de base de datos
"""

# Importar módulos
from . import crear_tenant
from . import poblar_usuarios
from . import poblar_tratamientos
from . import poblar_inventario
from . import poblar_agenda
from . import poblar_historial
from . import poblar_facturacion

__all__ = [
    'crear_tenant',
    'poblar_usuarios',
    'poblar_tratamientos',
    'poblar_inventario',
    'poblar_agenda',
    'poblar_historial',
    'poblar_facturacion',
]
