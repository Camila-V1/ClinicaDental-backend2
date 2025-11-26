# 20. Panel Multi-Tenant - Gestión de Clínicas

## 🎯 Objetivo
Implementar panel de super administrador para gestionar clínicas, aprobar solicitudes y administrar el sistema SaaS.

---

## 📁 Estructura de Archivos

```
src/
├── services/
│   └── tenantsService.ts (CREAR)
└── pages/
    └── superadmin/
        ├── Solicitudes.tsx (CREAR)
        ├── Clinicas.tsx (CREAR)
        └── Planes.tsx (CREAR)
```

---

## 1️⃣ Servicio de Tenants

**Archivo:** `src/services/tenantsService.ts`

```typescript
import { httpRequest } from './core/httpCore';

export interface SolicitudRegistro {
  id: number;
  nombre_clinica: string;
  dominio_deseado: string;
  nombre_contacto: string;
  email: string;
  telefono: string;
  plan_solicitado: any;
  estado: 'PENDIENTE' | 'PROCESADA' | 'RECHAZADA';
  fecha_solicitud: string;
}

export interface CrearSolicitudDTO {
  nombre_clinica: string;
  dominio_deseado: string;
  nombre_contacto: string;
  email: string;
  telefono: string;
  direccion: string;
  ciudad: string;
  pais: string;
  plan_solicitado: number;
}

// Usar URL pública (sin tenant)
const PUBLIC_API = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000/api/public';

export const tenantsService = {
  // Listar planes (público)
  getPlanes: () =>
    httpRequest<any[]>({
      method: 'GET',
      url: `${PUBLIC_API}/planes/`
    }),

  // Crear solicitud (público)
  crearSolicitud: (data: CrearSolicitudDTO) =>
    httpRequest<any>({
      method: 'POST',
      url: `${PUBLIC_API}/solicitudes/`,
      data
    }),

  // Listar solicitudes (admin)
  getSolicitudes: () =>
    httpRequest<SolicitudRegistro[]>({
      method: 'GET',
      url: `${PUBLIC_API}/solicitudes/`
    }),

  // Aprobar solicitud (admin)
  aprobarSolicitud: (id: number) =>
    httpRequest<any>({
      method: 'POST',
      url: `${PUBLIC_API}/solicitudes/${id}/aprobar/`
    }),

  // Rechazar solicitud (admin)
  rechazarSolicitud: (id: number, motivo: string) =>
    httpRequest<any>({
      method: 'POST',
      url: `${PUBLIC_API}/solicitudes/${id}/rechazar/`,
      data: { motivo }
    }),

  // Info de registro (público)
  getInfoRegistro: () =>
    httpRequest<any>({
      method: 'GET',
      url: `${PUBLIC_API}/info-registro/`
    })
};
```

---

## 2️⃣ Página de Solicitudes

**Archivo:** `src/pages/superadmin/Solicitudes.tsx`

```typescript
import { useState, useEffect } from 'react';
import { tenantsService, SolicitudRegistro } from '../../services/tenantsService';
import toast from 'react-hot-toast';

export default function Solicitudes() {
  const [solicitudes, setSolicitudes] = useState<SolicitudRegistro[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState<'TODAS' | 'PENDIENTE' | 'PROCESADA' | 'RECHAZADA'>('PENDIENTE');

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  const cargarSolicitudes = async () => {
    try {
      const data = await tenantsService.getSolicitudes();
      setSolicitudes(data);
    } catch (error) {
      toast.error('Error al cargar solicitudes');
    } finally {
      setLoading(false);
    }
  };

  const handleAprobar = async (id: number) => {
    if (!confirm('¿Aprobar esta solicitud y crear la clínica?')) return;
    
    try {
      await tenantsService.aprobarSolicitud(id);
      toast.success('Solicitud aprobada. Clínica creada exitosamente.');
      cargarSolicitudes();
    } catch (error) {
      toast.error('Error al aprobar solicitud');
    }
  };

  const handleRechazar = async (id: number) => {
    const motivo = prompt('Motivo del rechazo:');
    if (!motivo) return;
    
    try {
      await tenantsService.rechazarSolicitud(id, motivo);
      toast.success('Solicitud rechazada');
      cargarSolicitudes();
    } catch (error) {
      toast.error('Error al rechazar solicitud');
    }
  };

  const solicitudesFiltradas = filtro === 'TODAS' 
    ? solicitudes 
    : solicitudes.filter(s => s.estado === filtro);

  const getBadgeColor = (estado: string) => {
    switch (estado) {
      case 'PENDIENTE': return 'bg-yellow-100 text-yellow-800';
      case 'PROCESADA': return 'bg-green-100 text-green-800';
      case 'RECHAZADA': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Solicitudes de Registro</h1>
        
        <div className="flex gap-2">
          {['TODAS', 'PENDIENTE', 'PROCESADA', 'RECHAZADA'].map(estado => (
            <button
              key={estado}
              onClick={() => setFiltro(estado as any)}
              className={`px-4 py-2 rounded ${
                filtro === estado 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {estado}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4">
        {solicitudesFiltradas.map(solicitud => (
          <div key={solicitud.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold">{solicitud.nombre_clinica}</h3>
                <p className="text-gray-600">Dominio: {solicitud.dominio_deseado}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm ${getBadgeColor(solicitud.estado)}`}>
                {solicitud.estado}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Contacto</p>
                <p className="font-medium">{solicitud.nombre_contacto}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{solicitud.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Teléfono</p>
                <p className="font-medium">{solicitud.telefono}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Plan</p>
                <p className="font-medium">{solicitud.plan_solicitado?.nombre}</p>
              </div>
            </div>

            {solicitud.estado === 'PENDIENTE' && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleAprobar(solicitud.id)}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                  ✓ Aprobar
                </button>
                <button
                  onClick={() => handleRechazar(solicitud.id)}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  ✕ Rechazar
                </button>
              </div>
            )}
          </div>
        ))}

        {solicitudesFiltradas.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No hay solicitudes {filtro !== 'TODAS' && filtro.toLowerCase()}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 3️⃣ Página Pública de Registro

**Archivo:** `src/pages/public/RegistroClinica.tsx`

```typescript
import { useState, useEffect } from 'react';
import { tenantsService } from '../../services/tenantsService';
import toast from 'react-hot-toast';

export default function RegistroClinica() {
  const [planes, setPlanes] = useState([]);
  const [formData, setFormData] = useState({
    nombre_clinica: '',
    dominio_deseado: '',
    nombre_contacto: '',
    email: '',
    telefono: '',
    direccion: '',
    ciudad: '',
    pais: 'Bolivia',
    plan_solicitado: ''
  });

  useEffect(() => {
    cargarPlanes();
  }, []);

  const cargarPlanes = async () => {
    try {
      const data = await tenantsService.getPlanes();
      setPlanes(data);
    } catch (error) {
      toast.error('Error al cargar planes');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await tenantsService.crearSolicitud({
        ...formData,
        plan_solicitado: parseInt(formData.plan_solicitado)
      });
      
      toast.success('Solicitud enviada. Te contactaremos pronto.');
      // Resetear formulario
      setFormData({
        nombre_clinica: '',
        dominio_deseado: '',
        nombre_contacto: '',
        email: '',
        telefono: '',
        direccion: '',
        ciudad: '',
        pais: 'Bolivia',
        plan_solicitado: ''
      });
    } catch (error) {
      toast.error('Error al enviar solicitud');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-2">Registra tu Clínica</h1>
        <p className="text-center text-gray-600 mb-8">
          Completa el formulario y te contactaremos pronto
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nombre de la Clínica *</label>
              <input
                type="text"
                required
                value={formData.nombre_clinica}
                onChange={(e) => setFormData({ ...formData, nombre_clinica: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Dominio Deseado *</label>
              <div className="flex items-center">
                <input
                  type="text"
                  required
                  pattern="[a-z0-9-]+"
                  value={formData.dominio_deseado}
                  onChange={(e) => setFormData({ ...formData, dominio_deseado: e.target.value.toLowerCase() })}
                  className="flex-1 border rounded-l px-3 py-2"
                  placeholder="mi-clinica"
                />
                <span className="bg-gray-100 border border-l-0 rounded-r px-3 py-2 text-sm">
                  .clinica.com
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nombre Contacto *</label>
              <input
                type="text"
                required
                value={formData.nombre_contacto}
                onChange={(e) => setFormData({ ...formData, nombre_contacto: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Email *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Plan de Suscripción *</label>
            <select
              required
              value={formData.plan_solicitado}
              onChange={(e) => setFormData({ ...formData, plan_solicitado: e.target.value })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Selecciona un plan</option>
              {planes.map(plan => (
                <option key={plan.id} value={plan.id}>
                  {plan.nombre} - Bs. {plan.precio}/mes
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            Enviar Solicitud
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## 4️⃣ Configuración de Variables de Entorno

**Archivo:** `.env`

```env
VITE_API_URL=http://localhost:8000/api
VITE_PUBLIC_API_URL=http://localhost:8000/api/public
```

---

## ✅ Checklist

- [ ] Crear `tenantsService.ts`
- [ ] Crear página `Solicitudes.tsx` (superadmin)
- [ ] Crear página `RegistroClinica.tsx` (pública)
- [ ] Configurar variables de entorno
- [ ] Agregar rutas en `App.tsx`
- [ ] Probar flujo completo: solicitud → aprobación → creación
- [ ] Validar emails automáticos

**Endpoints utilizados:**
- `GET /api/public/planes/`
- `POST /api/public/solicitudes/`
- `GET /api/public/solicitudes/`
- `POST /api/public/solicitudes/{id}/aprobar/`
- `POST /api/public/solicitudes/{id}/rechazar/`
