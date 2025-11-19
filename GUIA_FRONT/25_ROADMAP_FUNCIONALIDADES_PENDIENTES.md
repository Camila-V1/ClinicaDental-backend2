# 🚀 ROADMAP: Funcionalidades Pendientes - Módulo Odontólogo

## 📊 Estado Actual

### ✅ FUNCIONALIDADES IMPLEMENTADAS (Core Completo)
1. **Agenda de Citas** - Funcional al 100%
2. **Registro de Episodios** - Funcional al 100%
3. **Historiales Clínicos** - Vista completa
4. **Planes de Tratamiento** - CRUD completo

---

## 🎯 PRIORIDADES DE IMPLEMENTACIÓN

### 🔥 PRIORIDAD ALTA (Necesarias para Operación Completa)

#### 1. ** Calendario de Citas (Vista Mensual/Semanal)**
**Ruta propuesta:** `/odontologo/calendario`

**Por qué es prioritario:**
- Actualmente las citas se ven en lista
- Difícil visualizar disponibilidad horaria
- No hay vista de agenda tradicional

**Funcionalidades necesarias:**
```typescript
// Vista de Calendario
- Calendario mensual interactivo
- Vista semanal (por día)
- Vista diaria (por hora)
- Citas visibles en el calendario con colores por tipo
- Click en cita para ver detalle
- Drag & drop para reprogramar (opcional)

// Bloques de Tiempo
- Ver horarios disponibles
- Bloquear horarios (vacaciones, almuerzo)
- Configurar horario de atención

// Acciones Rápidas
- Crear cita desde el calendario
- Confirmar citas pendientes
- Ver detalles sin salir de la vista
```

**Librerías recomendadas:**
```bash
npm install react-big-calendar
npm install date-fns
```

**Backend necesario:**
```python
# Ya existe
- GET /api/agenda/citas/?fecha_inicio=X&fecha_fin=Y

# ✅ CREADO: Nuevo endpoint para reservas
- GET /api/agenda/citas/disponibilidad/?fecha=2025-11-20&odontologo_id=X
  # Retorna horarios libres del odontólogo para que pacientes puedan reservar
  # Response: { "horarios_disponibles": ["09:00", "09:30", "10:00", ...] }
```

**Estimación:** 3-4 días

---

#### 2. **🦷 Odontograma Interactivo (Edición)**
**Ruta propuesta:** `/odontologo/historiales/:id/odontograma`

**Por qué es prioritario:**
- Actualmente solo se muestra lista de odontogramas
- No se pueden crear o editar odontogramas
- Es funcionalidad core en clínicas dentales

**Funcionalidades necesarias:**
```typescript
// Vista del Odontograma
- Gráfico de 32 piezas dentales adulto
- Gráfico de 20 piezas dentales niño
- Nomenclatura internacional (FDI)
- Colores por estado: sano, caries, restaurado, extraído, etc.

// Edición Interactiva
- Click en pieza para marcar/editar
- Seleccionar hallazgo (caries, corona, endodoncia, etc.)
- Agregar notas por pieza
- Guardar snapshot del odontograma

// Historial de Odontogramas
- Ver evolución en el tiempo
- Comparar odontogramas (antes/después)
- Exportar a PDF

// Integración con Episodios
- Crear odontograma durante atención
- Vincular hallazgos a episodios
```

**Componente base:**
```typescript
interface PiezaDental {
  numero: number; // 11-48 (FDI)
  estado: 'sano' | 'caries' | 'restaurado' | 'corona' | 'endodoncia' | 'extraido';
  superficie?: string[]; // ['oclusal', 'mesial', 'distal', 'vestibular', 'lingual']
  notas?: string;
}

interface Odontograma {
  id: number;
  historial_clinico: number;
  fecha: string;
  piezas: PiezaDental[];
  notas_generales: string;
  odontologo: number;
}
```

**Backend necesario:**
```python
# Ya existe en historial_clinico/views.py
- GET /api/historial/odontogramas/
- POST /api/historial/odontogramas/
- GET /api/historial/odontogramas/{id}/
- PUT/PATCH /api/historial/odontogramas/{id}/

# Verificar estructura del modelo Odontograma
```

**Estimación:** 5-7 días (componente complejo)

---

### 🟡 PRIORIDAD MEDIA (Mejoran la Experiencia)

#### 3. **📊 Dashboard Mejorado con Estadísticas**
**Ruta:** `/dashboard` (mejorar existente)

**Funcionalidades adicionales:**
```typescript
// Métricas del Día (Para el Odontólogo)
- ✅ Citas de hoy (ya existe)
- Citas pendientes de confirmar
- Citas atendidas hoy
- Pacientes atendidos

// Acciones Rápidas
- Ver próxima cita
- Acceso rápido a historiales recientes
- Planes pendientes de completar

// Notificaciones
- Citas próximas (en 15 minutos)
- Pacientes sin atender
- Planes pendientes de aceptar
```

**Backend necesario:**
```python
# ✅ CREADO: Endpoint de métricas del día
- GET /api/agenda/citas/metricas-dia/
  {
    "fecha": "2025-11-09",
    "citas_hoy": 5,
    "citas_pendientes": 2,
    "citas_confirmadas": 1,
    "citas_atendidas": 2,
    "pacientes_atendidos": 2,
    "proxima_cita": {
      "id": 1,
      "hora": "15:00",
      "paciente": "Juan Pérez",
      "motivo": "Revisión",
      "minutos_restantes": 45
    }
  }
```

**Estimación:** 2 días

---

#### 4. **📄 Gestión de Documentos**
**Ruta propuesta:** `/odontologo/historiales/:id/documentos`

**Funcionalidades necesarias:**
```typescript
// Subir Documentos
- Radiografías (JPEG, PNG)
- Documentos médicos (PDF)
- Consentimientos informados (PDF)
- Recetas (PDF)
- Categorizar al subir

// Ver Documentos
- Galería de imágenes
- Visor de PDFs
- Filtrar por categoría
- Buscar por nombre

// Gestión
- Descargar documento
- Eliminar documento (con confirmación)
- Agregar notas al documento
- Vincular a episodio específico
```

**Backend necesario:**
```python
# Nuevo modelo en historial_clinico/models.py
class DocumentoClinico(models.Model):
    historial = models.ForeignKey(HistorialClinico)
    tipo = models.CharField(...)  # radiografia, pdf, receta
    archivo = models.FileField(upload_to='documentos/')
    descripcion = models.TextField()
    episodio = models.ForeignKey(EpisodioAtencion, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

# Endpoints
- POST /api/historial/historiales/{id}/documentos/
- GET /api/historial/historiales/{id}/documentos/
- DELETE /api/historial/documentos/{id}/
```

**Estimación:** 3-4 días

---

### 🟢 PRIORIDAD BAJA (Nice to Have)

#### 5. **⚙️ Configuración de Perfil**
**Ruta propuesta:** `/odontologo/perfil`

**Funcionalidades:**
```typescript
// Datos Personales
- Ver/editar nombre, apellido
- Cambiar email (con verificación)
- Actualizar teléfono
- Cambiar foto de perfil

// Datos Profesionales
- Especialidad
- Número de matrícula
- Horario de atención
- Días laborables

// Seguridad
- Cambiar contraseña
- Ver sesiones activas
- Configurar 2FA (opcional)

// Notificaciones
- Configurar alertas por email
- Configurar alertas en app
- Preferencias de notificación
```

**Backend necesario:**
```python
# Endpoints usuarios
- GET /api/usuarios/me/
- PUT/PATCH /api/usuarios/me/
- POST /api/usuarios/cambiar_password/
- POST /api/usuarios/actualizar_foto/
```

**Estimación:** 2-3 días

---

## � PLAN DE IMPLEMENTACIÓN RECOMENDADO

### Fase 1 (1 semana) - Visualización y Navegación
1. ✅ Calendario de Citas (vista mensual/semanal)
2. ✅ Dashboard Mejorado (métricas del día)

**Resultado:** Odontólogo puede ver su agenda visualmente y métricas en tiempo real

---

### Fase 2 (2 semanas) - Funcionalidad Clínica Core
3. ✅ Odontograma Interactivo (edición completa)
4. ✅ Gestión de Documentos (subir/ver archivos)

**Resultado:** Funcionalidad clínica completa

---

### Fase 3 (3-5 días) - Extras
5. ✅ Configuración de Perfil

**Resultado:** Sistema completo para odontólogo

---

## 🎯 RESUMEN DE ESFUERZO

| Funcionalidad | Prioridad | Estimación | Backend Requerido |
|---------------|-----------|------------|-------------------|
| Calendario Citas | 🔥 Alta | 3-4 días | ✅ **LISTO** - Endpoint `/disponibilidad/` creado |
| Odontograma | 🔥 Alta | 5-7 días | ✅ **LISTO** - Modelo y endpoints completos |
| Dashboard Mejorado | 🟡 Media | 2 días | ✅ **LISTO** - Endpoint `/metricas-dia/` creado |
| Documentos | 🟡 Media | 3-4 días | ✅ **LISTO** - Modelo y endpoints completos |
| Perfil | 🟢 Baja | 2-3 días | ✅ Ya existe |

**Total estimado:** 15-20 días (3-4 semanas de desarrollo)
**Backend pendiente:** ✅ **¡NINGUNO! Backend 100% completo** 🎉

---

## 🚀 RECOMENDACIÓN FINAL

### Para MVP (Mínimo Viable):
Implementar **Fase 1 + Fase 2**:
- Calendario con disponibilidad
- Dashboard con métricas
- Odontograma interactivo
- Gestión de documentos

**Esto da un módulo de odontólogo completamente funcional.**

---

## 💡 NOTA IMPORTANTE

### Funcionalidades EXCLUIDAS (son de otros roles):
- ❌ **CRUD Pacientes** → Función de ADMIN
- ❌ **Facturación completa** → ADMIN ve todas, PACIENTE ve las suyas
- ❌ **Inventario gestión** → Función de ADMIN
- ❌ **Reportes avanzados** → Función de ADMIN

### Backend 100% COMPLETO ✅:
1. ✅ **GET /api/agenda/citas/disponibilidad/** - Para reservas de pacientes (horarios disponibles)
2. ✅ **GET /api/agenda/citas/metricas-dia/** - ¡RECIÉN CREADO! Métricas del día para dashboard
3. ✅ **Modelo Odontograma** - Con JSONField para estado_piezas flexible
4. ✅ **Endpoints de Odontograma** - CRUD completo + duplicar odontograma
5. ✅ **Modelo DocumentoClinico** - Con subida de archivos organizada por paciente
6. ✅ **Endpoints de Documentos** - CRUD + filtro por tipo + endpoint de descarga
7. ✅ Agenda y citas completas
8. ✅ Historiales y episodios
9. ✅ Planes de tratamiento
10. ✅ Perfil de usuario

### 📂 Archivos de prueba HTTP creados:
- `pruebas_http/08_disponibilidad.http` - Pruebas del endpoint de disponibilidad
- `pruebas_http/09_metricas_dia.http` - Pruebas del endpoint de métricas del día

**¡El backend está 100% completo!** Todo está listo para que el frontend implemente las funcionalidades. 🎉🎉🎉
