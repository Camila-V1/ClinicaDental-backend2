"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API routes: redirect to app-level urlconfs
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agenda/', include('agenda.urls')),
    path('api/historial/', include('historial_clinico.urls')),
    path('api/tratamientos/', include('tratamientos.urls')),
    path('api/facturacion/', include('facturacion.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/reportes/', include('reportes.urls')),
    # En producción con django-tenants, la administración de tenants vive en la app 'tenants'
    path('api/clinicas/', include('tenants.urls')),
    # JWT auth endpoints (token obtain/refresh)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
