from django.shortcuts import render
from django.http import JsonResponse


def index(request):
	return JsonResponse({"status": "ok", "app": "usuarios"})


def health_check(request):
	"""
	Una vista simple para confirmar que la app 'usuarios' está conectada.
	"""
	return JsonResponse({"status": "ok", "app": "usuarios"})
