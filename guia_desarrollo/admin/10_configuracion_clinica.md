# ⚙️ Configuración de la Clínica

## 🎯 Objetivo
Gestionar la configuración general del tenant (clínica), incluyendo información básica, horarios, y preferencias del sistema.

---

## 📋 Requisitos Funcionales

### Funcionalidades:
1. **Información básica**: Nombre, logo, dirección, contacto
2. **Horarios de atención** por día de la semana
3. **Configuración de citas**: Duración por defecto, recordatorios
4. **Notificaciones**: Email, SMS (configuración)
5. **Preferencias del sistema**: Zona horaria, moneda, idioma
6. **Gestión de usuarios**: Activar/desactivar usuarios
7. **Backup**: Exportar datos de la clínica

---

## 🔌 Endpoints a Consumir

```typescript
// 1. Obtener configuración de la clínica
GET /api/tenants/configuracion/
Response: {
  id: 1,
  nombre: "Clínica Dental Dr. Pérez",
  logo: "https://...",
  direccion: "Av. Principal #123",
  telefono: "+591 1234567",
  email: "contacto@clinica.com",
  ciudad: "La Paz",
  pais: "Bolivia",
  zona_horaria: "America/La_Paz",
  moneda: "BOB",
  duracion_cita_default: 30,
  recordatorio_citas_horas: 24,
  horarios: [
    { dia_semana: 1, hora_inicio: "08:00", hora_fin: "18:00", activo: true },
    { dia_semana: 2, hora_inicio: "08:00", hora_fin: "18:00", activo: true }
  ]
}

// 2. Actualizar configuración
PATCH /api/tenants/configuracion/
Body: {
  nombre: "Nueva Clínica Dental",
  telefono: "+591 9876543",
  duracion_cita_default: 45
}

// 3. Subir logo
POST /api/tenants/configuracion/logo/
Body: FormData with file

// 4. Actualizar horarios
PATCH /api/tenants/horarios/{id}/
Body: {
  hora_inicio: "09:00",
  hora_fin: "17:00",
  activo: false
}

// 5. Listar usuarios del tenant
GET /api/usuarios/usuarios/
Response: {
  count: 15,
  results: [
    {
      id: 1,
      full_name: "Dr. Juan Pérez",
      email: "juan@clinica.com",
      tipo_usuario: "ODONTOLOGO",
      is_active: true,
      last_login: "2025-11-20T10:00:00Z"
    }
  ]
}

// 6. Activar/Desactivar usuario
PATCH /api/usuarios/usuarios/{id}/
Body: { is_active: false }

// 7. Exportar datos de la clínica
GET /api/tenants/exportar-datos/?formato=excel
Response: Binary Excel file
```

---

## 💻 Implementación Frontend

### 1. Página de Configuración

```typescript
// src/pages/admin/Configuracion.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { configuracionService } from '@/services/admin/configuracionService';
import InformacionBasica from '@/components/admin/configuracion/InformacionBasica';
import HorariosAtencion from '@/components/admin/configuracion/HorariosAtencion';
import UsuariosTab from '@/components/admin/configuracion/UsuariosTab';
import { toast } from 'react-hot-toast';

type Tab = 'informacion' | 'horarios' | 'usuarios' | 'preferencias';

export default function Configuracion() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>('informacion');

  // Fetch configuración
  const { data: config, isLoading } = useQuery({
    queryKey: ['configuracion-clinica'],
    queryFn: configuracionService.getConfiguracion,
  });

  // Actualizar configuración
  const updateMutation = useMutation({
    mutationFn: configuracionService.updateConfiguracion,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuracion-clinica'] });
      toast.success('Configuración actualizada');
    },
    onError: () => {
      toast.error('Error al actualizar configuración');
    },
  });

  // Subir logo
  const logoMutation = useMutation({
    mutationFn: configuracionService.uploadLogo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuracion-clinica'] });
      toast.success('Logo actualizado');
    },
  });

  // Exportar datos
  const handleExport = async () => {
    try {
      const blob = await configuracionService.exportarDatos();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `datos_clinica_${new Date().toISOString().split('T')[0]}.xlsx`;
      a.click();
      toast.success('Datos exportados');
    } catch (error) {
      toast.error('Error al exportar datos');
    }
  };

  if (isLoading) {
    return <div className="p-6">Cargando configuración...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Configuración de la Clínica</h1>
          <p className="text-gray-600">Gestiona la información y preferencias</p>
        </div>
        <button
          onClick={handleExport}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          📦 Exportar Datos
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('informacion')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'informacion'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Información Básica
          </button>
          <button
            onClick={() => setActiveTab('horarios')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'horarios'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Horarios de Atención
          </button>
          <button
            onClick={() => setActiveTab('usuarios')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'usuarios'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Usuarios
          </button>
          <button
            onClick={() => setActiveTab('preferencias')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'preferencias'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Preferencias
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow">
        {activeTab === 'informacion' && (
          <InformacionBasica
            config={config}
            onUpdate={(data) => updateMutation.mutate(data)}
            onUploadLogo={(file) => logoMutation.mutate(file)}
            isLoading={updateMutation.isPending || logoMutation.isPending}
          />
        )}
        {activeTab === 'horarios' && <HorariosAtencion config={config} />}
        {activeTab === 'usuarios' && <UsuariosTab />}
        {activeTab === 'preferencias' && (
          <PreferenciasTab
            config={config}
            onUpdate={(data) => updateMutation.mutate(data)}
            isLoading={updateMutation.isPending}
          />
        )}
      </div>
    </div>
  );
}

// Tab de Preferencias
function PreferenciasTab({ config, onUpdate, isLoading }: any) {
  const [formData, setFormData] = useState({
    zona_horaria: config.zona_horaria,
    moneda: config.moneda,
    duracion_cita_default: config.duracion_cita_default,
    recordatorio_citas_horas: config.recordatorio_citas_horas,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Zona Horaria
          </label>
          <select
            value={formData.zona_horaria}
            onChange={(e) => setFormData({ ...formData, zona_horaria: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="America/La_Paz">La Paz (GMT-4)</option>
            <option value="America/Lima">Lima (GMT-5)</option>
            <option value="America/Mexico_City">Ciudad de México (GMT-6)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Moneda</label>
          <select
            value={formData.moneda}
            onChange={(e) => setFormData({ ...formData, moneda: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="BOB">Bolivianos (BOB)</option>
            <option value="USD">Dólares (USD)</option>
            <option value="PEN">Soles (PEN)</option>
            <option value="MXN">Pesos (MXN)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Duración de Cita por Defecto (minutos)
          </label>
          <input
            type="number"
            value={formData.duracion_cita_default}
            onChange={(e) =>
              setFormData({ ...formData, duracion_cita_default: parseInt(e.target.value) })
            }
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            min="15"
            step="15"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recordatorio de Citas (horas antes)
          </label>
          <input
            type="number"
            value={formData.recordatorio_citas_horas}
            onChange={(e) =>
              setFormData({ ...formData, recordatorio_citas_horas: parseInt(e.target.value) })
            }
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            min="1"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar Preferencias'}
        </button>
      </div>
    </form>
  );
}
```

---

### 2. Componente de Información Básica

```typescript
// src/components/admin/configuracion/InformacionBasica.tsx
import React, { useState, useRef } from 'react';
import { Camera } from 'lucide-react';

interface InformacionBasicaProps {
  config: any;
  onUpdate: (data: any) => void;
  onUploadLogo: (file: File) => void;
  isLoading: boolean;
}

export default function InformacionBasica({
  config,
  onUpdate,
  onUploadLogo,
  isLoading,
}: InformacionBasicaProps) {
  const [formData, setFormData] = useState({
    nombre: config.nombre,
    direccion: config.direccion,
    telefono: config.telefono,
    email: config.email,
    ciudad: config.ciudad,
    pais: config.pais,
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadLogo(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-6">
      {/* Logo */}
      <div className="flex items-center gap-6">
        <div className="relative">
          {config.logo ? (
            <img
              src={config.logo}
              alt="Logo"
              className="w-32 h-32 object-contain border rounded-lg"
            />
          ) : (
            <div className="w-32 h-32 bg-gray-100 border rounded-lg flex items-center justify-center">
              <Camera className="w-8 h-8 text-gray-400" />
            </div>
          )}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="absolute bottom-0 right-0 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700"
          >
            <Camera className="w-4 h-4" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleLogoChange}
            className="hidden"
          />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">Logo de la Clínica</h3>
          <p className="text-sm text-gray-600">PNG, JPG hasta 2MB</p>
        </div>
      </div>

      {/* Formulario */}
      <div className="grid grid-cols-2 gap-6">
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre de la Clínica *
          </label>
          <input
            type="text"
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Dirección *
          </label>
          <input
            type="text"
            value={formData.direccion}
            onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
          <input
            type="tel"
            value={formData.telefono}
            onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
          <input
            type="text"
            value={formData.ciudad}
            onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">País</label>
          <input
            type="text"
            value={formData.pais}
            onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>
    </form>
  );
}
```

---

### 3. Componente de Horarios

```typescript
// src/components/admin/configuracion/HorariosAtencion.tsx
import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { configuracionService } from '@/services/admin/configuracionService';
import { toast } from 'react-hot-toast';

const DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

interface HorariosAtencionProps {
  config: any;
}

export default function HorariosAtencion({ config }: HorariosAtencionProps) {
  const queryClient = useQueryClient();

  const updateHorarioMutation = useMutation({
    mutationFn: ({ id, data }: any) => configuracionService.updateHorario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuracion-clinica'] });
      toast.success('Horario actualizado');
    },
  });

  const handleToggle = (horario: any) => {
    updateHorarioMutation.mutate({
      id: horario.id,
      data: { activo: !horario.activo },
    });
  };

  const handleTimeChange = (horario: any, field: string, value: string) => {
    updateHorarioMutation.mutate({
      id: horario.id,
      data: { [field]: value },
    });
  };

  return (
    <div className="p-6">
      <div className="space-y-4">
        {config.horarios?.map((horario: any) => (
          <div key={horario.id} className="flex items-center gap-4 p-4 border rounded-lg">
            <div className="w-32">
              <span className="font-medium">{DIAS_SEMANA[horario.dia_semana - 1]}</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="time"
                value={horario.hora_inicio}
                onChange={(e) => handleTimeChange(horario, 'hora_inicio', e.target.value)}
                disabled={!horario.activo}
                className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              <span className="text-gray-600">hasta</span>
              <input
                type="time"
                value={horario.hora_fin}
                onChange={(e) => handleTimeChange(horario, 'hora_fin', e.target.value)}
                disabled={!horario.activo}
                className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
            <div className="ml-auto">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={horario.activo}
                  onChange={() => handleToggle(horario)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Activo</span>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 4. Servicio de Configuración

```typescript
// src/services/admin/configuracionService.ts
import api from '@/lib/axios';

export const configuracionService = {
  // Configuración general
  async getConfiguracion() {
    const { data } = await api.get('/tenants/configuracion/');
    return data;
  },

  async updateConfiguracion(configData: any) {
    const { data } = await api.patch('/tenants/configuracion/', configData);
    return data;
  },

  async uploadLogo(file: File) {
    const formData = new FormData();
    formData.append('logo', file);
    const { data } = await api.post('/tenants/configuracion/logo/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Horarios
  async updateHorario(id: number, horarioData: any) {
    const { data } = await api.patch(`/tenants/horarios/${id}/`, horarioData);
    return data;
  },

  // Exportar datos
  async exportarDatos() {
    const { data } = await api.get('/tenants/exportar-datos/?formato=excel', {
      responseType: 'blob',
    });
    return data;
  },
};
```

---

## ✅ Checklist

- [ ] Crear página Configuracion.tsx
- [ ] Crear InformacionBasica component
- [ ] Crear HorariosAtencion component
- [ ] Crear UsuariosTab component
- [ ] Crear PreferenciasTab
- [ ] Crear configuracionService
- [ ] Subida de logo
- [ ] Edición de horarios por día
- [ ] Gestión de usuarios (activar/desactivar)
- [ ] Exportación de datos de la clínica

---

**🎉 Guías Completadas:** Todas las 10 guías del panel de administración han sido creadas.
