from django.http import JsonResponse
from .models import Clinica


def index(request):
    # Simple public endpoint returning list of clinics (name + domain)
    data = list(Clinica.objects.values('id', 'nombre', 'dominio', 'activo'))
    return JsonResponse({'clinicas': data})
