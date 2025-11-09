# ⚙️ FASE 7: CONFIGURACIÓN AVANZADA - ADMINISTRACIÓN DEL SISTEMA

## ⚠️ IMPORTANTE: ESTADO DE IMPLEMENTACIÓN

**Backend actual:** El sistema Django multi-tenant es un MVP que **NO incluye un app de configuración** (`configuracion/`).

Las siguientes funcionalidades **NO están implementadas en el backend**:
- ❌ Endpoints `/api/configuracion/*`
- ❌ Sistema de roles y permisos personalizados por API
- ❌ Gestión de backups desde la aplicación
- ❌ Sistema de logs consultables por API
- ❌ Configuración de plantillas de email
- ❌ Configuración de horarios y días festivos
- ❌ Import/Export de datos

**Este archivo contiene:**
1. ✅ Código de ejemplo para cuando se implemente el backend
2. ✅ Configuración actual disponible (Django Admin, variables de entorno)
3. ✅ Recomendaciones para desarrollo futuro

---

## 📋 Endpoints de Configuración (PARA IMPLEMENTACIÓN FUTURA)

> **Nota:** Estos endpoints NO existen actualmente. Se incluyen como referencia para desarrollo futuro.

```javascript
// Endpoints configuración (NO IMPLEMENTADOS - REFERENCIA)
const CONFIG_ENDPOINTS = {
  // Configuración general
  generalSettings: '/api/configuracion/general/',
  
  // Configuración de la clínica
  clinicSettings: '/api/configuracion/clinica/',
  clinicProfile: '/api/configuracion/clinica/perfil/',
  
  // Configuración de usuarios y permisos
  roles: '/api/configuracion/roles/',
  permissions: '/api/configuracion/permisos/',
  
  // Configuración de notificaciones
  notificationSettings: '/api/configuracion/notificaciones/',
  
  // Configuración de horarios
  scheduleSettings: '/api/configuracion/horarios/',
  holidays: '/api/configuracion/dias-festivos/',
  
  // Backup y restauración
  backup: '/api/configuracion/backup/',
  restore: '/api/configuracion/restore/',
  
  // Logs del sistema
  systemLogs: '/api/configuracion/logs/',
  auditLogs: '/api/configuracion/auditoria/'
};
```

## 🔧 1. Servicio de Configuración (CÓDIGO DE EJEMPLO PARA FUTURO)

> **Nota:** Este servicio NO funcionará hasta que se implemente el backend correspondiente.

```javascript
// services/configService.js
import api from './apiConfig';

class ConfigService {
  // Configuración general
  async getGeneralSettings() {
    try {
      const response = await api.get('/api/configuracion/general/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener configuración general' };
    }
  }

  async updateGeneralSettings(settings) {
    try {
      const response = await api.put('/api/configuracion/general/', settings);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al actualizar configuración' 
      };
    }
  }

  // Roles y permisos
  async getRoles() {
    try {
      const response = await api.get('/api/configuracion/roles/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener roles' };
    }
  }

  async createRole(roleData) {
    try {
      const response = await api.post('/api/configuracion/roles/', roleData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear rol' 
      };
    }
  }

  // Backup y restauración
  async createBackup(backupData) {
    try {
      const response = await api.post('/api/configuracion/backup/', backupData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Error al crear backup' 
      };
    }
  }

  async getBackups() {
    try {
      const response = await api.get('/api/configuracion/backup/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener lista de backups' };
    }
  }

  // Logs del sistema
  async getSystemLogs(page = 1, level = '', dateFrom = '', dateTo = '') {
    try {
      const params = { 
        page,
        level: level || undefined,
        fecha_desde: dateFrom || undefined,
        fecha_hasta: dateTo || undefined
      };
      const response = await api.get('/api/configuracion/logs/', { params });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener logs del sistema' };
    }
  }
}

export default new ConfigService();
```

---

## 🔧 2. CONFIGURACIÓN ACTUAL DISPONIBLE (IMPLEMENTADO)

El sistema actual utiliza configuración a nivel de infraestructura Django:

### 1. Django Admin Panel
Toda la configuración del sistema se realiza a través del panel de administración de Django (`/admin/`):

```javascript
// Acceso al panel de administración (no hay API)
const ADMIN_URL = '/admin/';

// Para acceder:
// 1. Usuario debe tener is_staff=True y is_superuser=True
// 2. Navegar directamente a /admin/ en el navegador
// 3. No existe API REST para estas funcionalidades
```

### 2. Configuración de Tenant (Clínica)
La información de la clínica se maneja mediante el modelo `TenantClient`:

```javascript
// services/tenantService.js
import api from './apiConfig';

class TenantService {
  // Obtener información del tenant actual
  async getCurrentTenant() {
    try {
      // Este endpoint NO existe - la info del tenant viene implícita en el subdominio
      // El frontend detecta el tenant por el subdomain en la URL
      const subdomain = window.location.hostname.split('.')[0];
      return { success: true, subdomain };
    } catch (error) {
      return { success: false, error: 'Error al detectar tenant' };
    }
  }
}

export default new TenantService();
```

### 3. Gestión de Usuarios y Permisos
El sistema actual usa los permisos nativos de Django basados en el campo `tipo_usuario`:

```javascript
// utils/permissions.js

// Tipos de usuario disponibles (VERIFICADOS EN BACKEND)
export const UserTypes = {
  ADMIN: 'ADMIN',
  ODONTOLOGO: 'ODONTOLOGO',
  PACIENTE: 'PACIENTE'
};

// Verificación de permisos en el frontend
export const hasPermission = (user, requiredType) => {
  if (!user) return false;
  
  // Jerarquía de permisos
  const hierarchy = {
    'ADMIN': 3,
    'ODONTOLOGO': 2,
    'PACIENTE': 1
  };
  
  return hierarchy[user.tipo_usuario] >= hierarchy[requiredType];
};

// Componente protegido por permisos
export const ProtectedRoute = ({ children, requiredType }) => {
  const { user } = useAuth();
  
  if (!hasPermission(user, requiredType)) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
};
```

### 4. Variables de Entorno (Frontend)
Configuración del frontend mediante variables de entorno:

```javascript
// src/config/environment.js

// Validación y carga de variables de entorno
export const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  
  // Multi-tenant
  tenantDomain: import.meta.env.VITE_TENANT_DOMAIN || 'localhost',
  publicDomain: import.meta.env.VITE_PUBLIC_DOMAIN || 'public.localhost',
  
  // Authentication
  tokenRefreshTime: parseInt(import.meta.env.VITE_TOKEN_REFRESH_TIME) || 14, // minutos
  
  // App Configuration
  appName: import.meta.env.VITE_APP_NAME || 'Sistema Clínica Dental',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Features Flags
  enableRegistration: import.meta.env.VITE_ENABLE_REGISTRATION === 'true',
  enableNotifications: import.meta.env.VITE_ENABLE_NOTIFICATIONS === 'true',
  
  // File Upload
  maxFileSize: parseInt(import.meta.env.VITE_MAX_FILE_SIZE) || 10485760, // 10MB
  allowedFileTypes: (import.meta.env.VITE_ALLOWED_FILE_TYPES || 'pdf,jpg,jpeg,png').split(','),
  
  // Locale
  defaultLocale: import.meta.env.VITE_DEFAULT_LOCALE || 'es-BO',
  timezone: import.meta.env.VITE_TIMEZONE || 'America/La_Paz',
  currency: import.meta.env.VITE_CURRENCY || 'BOB'
};

// Validar configuración requerida
export const validateConfig = () => {
  const required = ['apiUrl', 'tenantDomain'];
  const missing = required.filter(key => !config[key]);
  
  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing);
    return false;
  }
  
  return true;
};
```

### 5. Ejemplo de archivo .env para el Frontend

```bash
# .env.development
VITE_API_URL=http://localhost:8000
VITE_TENANT_DOMAIN=localhost:5173
VITE_PUBLIC_DOMAIN=public.localhost:5173
VITE_APP_NAME=Sistema Clínica Dental
VITE_APP_VERSION=1.0.0
VITE_ENABLE_REGISTRATION=false
VITE_ENABLE_NOTIFICATIONS=true
VITE_MAX_FILE_SIZE=10485760
VITE_ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,doc,docx
VITE_DEFAULT_LOCALE=es-BO
VITE_TIMEZONE=America/La_Paz
VITE_CURRENCY=BOB
VITE_TOKEN_REFRESH_TIME=14

# .env.production
VITE_API_URL=https://api.clinicadental.com
VITE_TENANT_DOMAIN=clinicadental.com
VITE_PUBLIC_DOMAIN=public.clinicadental.com
VITE_APP_NAME=Sistema Clínica Dental
VITE_APP_VERSION=1.0.0
VITE_ENABLE_REGISTRATION=false
VITE_ENABLE_NOTIFICATIONS=true
```

## 📋 Desarrollo Futuro Recomendado

Si se desea implementar un sistema de configuración avanzada, se recomienda:

### 1. Crear App Django `configuracion`
```python
# configuracion/models.py
from django.db import models
from tenants.models import TenantClient

class ConfiguracionTenant(models.Model):
    """Configuración específica por tenant"""
    tenant = models.OneToOneField(TenantClient, on_delete=models.CASCADE)
    
    # Información general
    nombre_clinica = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField()
    
    # Horarios
    hora_apertura = models.TimeField(default='08:00')
    hora_cierre = models.TimeField(default='18:00')
    duracion_cita_defecto = models.IntegerField(default=30)  # minutos
    
    # Notificaciones
    enviar_recordatorios = models.BooleanField(default=True)
    horas_anticipacion_recordatorio = models.IntegerField(default=24)
    
    # Facturación
    moneda = models.CharField(max_length=3, default='BOB')
    prefijo_factura = models.CharField(max_length=10, default='FAC-')
    
    class Meta:
        verbose_name = 'Configuración del Tenant'
```

### 2. Crear ViewSet para Configuración
```python
# configuracion/views.py
from rest_framework import viewsets
from rest_framework.decorators import action

class ConfiguracionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        return ConfiguracionTenant.objects.filter(
            tenant=self.request.tenant
        )
    
    @action(detail=False, methods=['get'])
    def actual(self, request):
        """Obtener configuración del tenant actual"""
        config = self.get_queryset().first()
        if config:
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        return Response({'error': 'No hay configuración'}, status=404)
```

### 3. Componente Frontend de Ejemplo
```javascript
// components/ConfigSettings.jsx (EJEMPLO PARA FUTURO)
import React, { useState, useEffect } from 'react';
import configService from '../services/configService';

function ConfigSettings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const result = await configService.getGeneralSettings();
    if (result.success) {
      setSettings(result.data);
    }
    setLoading(false);
  };

  const handleSave = async (newSettings) => {
    const result = await configService.updateGeneralSettings(newSettings);
    if (result.success) {
      alert('Configuración guardada correctamente');
      setSettings(result.data);
    } else {
      alert('Error: ' + result.error);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Configuración del Sistema</h1>
      {/* Formulario de configuración */}
    </div>
  );
}

export default ConfigSettings;
```

## ✅ Resumen

**Configuración Actual (Implementada):**
- ✅ Django Admin Panel para superusuarios
- ✅ Variables de entorno del frontend
- ✅ Detección automática de tenant por subdomain
- ✅ Permisos basados en `tipo_usuario`

**Configuración Avanzada (NO Implementada):**
- ❌ API REST de configuración
- ❌ Panel de configuración en el frontend
- ❌ Sistema de roles personalizados
- ❌ Gestión de backups por API
- ❌ Logs consultables
- ❌ Plantillas de email
- ❌ Días festivos y horarios

**Recomendación:** Usar el Django Admin para configuración del sistema y crear el app `configuracion` solo si el cliente lo requiere específicamente en fases futuras del proyecto.

---
**Estado actual**: Sistema funcional con configuración básica ✅  
**Próxima fase**: Desarrollo de módulo de configuración avanzada (opcional) 🔄

---
**Estado actual**: Sistema funcional con configuración básica ✅  
**Próxima fase**: Desarrollo de módulo de configuración avanzada (opcional) 🔄