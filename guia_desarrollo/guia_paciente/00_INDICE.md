# 📋 GUÍA DE DESARROLLO - MÓDULO PACIENTE

## 🎯 Objetivo
Desarrollar el módulo completo del **Portal del Paciente** con enfoque incremental, probando cada funcionalidad antes de continuar.

---

## 📊 PROGRESO ACTUAL: 13/13 GUÍAS CORE (100%)

**Funcionalidades completadas:**
- ✅ Autenticación y perfil (3/3 guías)
- ✅ Gestión de citas completa (4/4 guías)
- ✅ Historial clínico (2/2 guías)
- ✅ Planes de tratamiento (2/2 guías)
- ✅ Facturación y pagos (2/2 guías)

---

## 📚 Estructura de las Guías

Cada guía corresponde a **UNA interacción específica** del paciente, permitiendo:
- ✅ Desarrollo incremental
- ✅ Pruebas inmediatas
- ✅ Detección temprana de errores
- ✅ Commits pequeños y controlados

---

## 🗂️ ÍNDICE DE GUÍAS IMPLEMENTADAS

### 🔐 **FASE 1: AUTENTICACIÓN Y PERFIL** ✅ COMPLETA

#### ✅ 01_login_paciente.md
- Login específico para pacientes con JWT
- Validación de tipo_usuario
- Redirección al dashboard
- Manejo de errores de autenticación
- **Estado**: Implementada (383 líneas)

#### ✅ 02_dashboard_paciente.md
- Vista principal del paciente
- 3 componentes: ProximasCitas, ResumenHistorial, AccesosRapidos
- Tarjetas de acceso rápido (citas, historial, facturas)
- Navegación entre secciones
- **Estado**: Implementada (1,129 líneas)

#### ✅ 03_ver_perfil_paciente.md
- Ver datos personales completos
- Ver datos médicos (alergias, antecedentes)
- Visualización solo lectura (backend no permite edición)
- **Estado**: Implementada (~700 líneas)

---

### 📅 **FASE 2: GESTIÓN DE CITAS** ✅ COMPLETA

#### ✅ 04_ver_mis_citas.md
- Lista de todas las citas del paciente
- CitaCard + CitasFiltros components
- Filtros por estado (PROGRAMADA, ATENDIDA, CANCELADA)
- Ordenamiento por fecha
- **Estado**: Implementada (803 líneas)

#### ✅ 05_solicitar_cita.md
- Formulario de solicitud de cita
- Date/time picker
- Selección de odontólogo
- Campo de motivo de consulta
- **Estado**: Implementada (620 líneas)

#### ✅ 06_cancelar_cita.md
- Modal de confirmación de cancelación
- Restricciones para citas ATENDIDA/CANCELADA
- Actualización de estado con endpoint custom
- **Estado**: Implementada (871 líneas)

#### ✅ 07_reprogramar_cita.md
- Seleccionar nueva fecha/hora
- PATCH endpoint para actualización
- Validación de fecha futura y diferente
- **Estado**: Implementada (939 líneas)

---

### 🦷 **FASE 3: HISTORIAL CLÍNICO** ✅ COMPLETA

#### ✅ 08_ver_historial_clinico.md
- Vista general del historial
- 3 tabs: Episodios, Documentos, Información General
- EpisodioCard con diagnóstico y procedimiento
- Alergias destacadas en amarillo
- **Estado**: Implementada (1,067 líneas)

#### ✅ 09_ver_documentos_clinicos.md
- Galería de documentos clínicos
- FiltrosDocumentos (6 tipos)
- DocumentoModal con preview de imágenes
- Descarga de archivos binarios con blob
- **Estado**: Implementada (1,012 líneas)

---

### 💰 **FASE 4: PLANES DE TRATAMIENTO** ✅ COMPLETA

#### ✅ 10_ver_planes_tratamiento.md
- Lista de planes del paciente
- PlanCard con estado, prioridad, progreso
- 6 estados de plan con colores
- BarraProgreso component reutilizable
- Filtros por estado
- **Estado**: Implementada (1,234 líneas)

#### ✅ 11_ver_detalle_plan.md
- Detalle completo del plan
- ItemPlanCard con estado de cada servicio
- LineaTiempoPlan con eventos
- ResumenPresupuesto con desglose
- Layout 2 columnas (contenido + sidebar)
- **Estado**: Implementada (1,237 líneas)
---

### 💳 **FASE 5: FACTURACIÓN Y PAGOS** ✅ COMPLETA

#### ✅ 12_ver_facturas.md
- Lista de todas las facturas del paciente
- Resumen financiero (Total, Pagado, Pendiente)
- AlertaVencimiento component
- FacturaCard con progreso de pago
- Filtros por estado (pendiente, pagada, vencida)
- **Estado**: Implementada (1,383 líneas)

#### ✅ 13_ver_detalle_factura.md
- Información completa de la factura
- PagoCard para historial de pagos
- ItemPresupuestoCard para servicios
- InfoPlanFactura con navegación
- Layout 2 columnas con resumen
- Items facturados
- Métodos de pago aplicados
- Saldo pendiente
- Botón de descarga/impresión
- **Probar**: Detalles completos

#### 18_descargar_factura.md
- Generación de PDF
- Descarga automática
- Formato profesional
- **Probar**: Descarga exitosa

---

## 📦 COMPONENTES REUTILIZABLES CREADOS

### Layout & UI
- `BarraProgreso.tsx` - Barra de progreso con porcentaje y colores dinámicos
- `AlertaVencimiento.tsx` - Alertas para facturas próximas/vencidas

### Citas
- `CitaCard.tsx` - Card de cita con estado, fecha, odontólogo
- `CitasFiltros.tsx` - Filtros por estado de cita
- `ModalConfirmarCancelar.tsx` - Modal de confirmación

### Historial Clínico
- `EpisodioCard.tsx` - Card de episodio de atención
- `DocumentoModal.tsx` - Modal con preview de documentos
- `DocumentoGaleria.tsx` - Grid de documentos clínicos
- `FiltrosDocumentos.tsx` - Filtros por tipo de documento

### Planes de Tratamiento
- `PlanCard.tsx` - Card de plan con progreso y presupuesto
- `ItemPlanCard.tsx` - Card de servicio dentro del plan
- `LineaTiempoPlan.tsx` - Timeline visual de eventos del plan
- `ResumenPresupuesto.tsx` - Desglose financiero del plan

### Facturación
- `FacturaCard.tsx` - Card de factura con progreso de pago
- `PagoCard.tsx` - Card de pago individual
- `ItemPresupuestoCard.tsx` - Item del presupuesto
- `InfoPlanFactura.tsx` - Info del plan relacionado

---

## 🛠️ SERVICIOS IMPLEMENTADOS

```typescript
authService.ts          // Login, logout, token management
usuariosService.ts      // Perfil, odontólogos list
citasService.ts         // CRUD completo de citas
historialService.ts     // Historial clínico del paciente
documentosService.ts    // Lista y descarga de documentos
planesService.ts        // Planes de tratamiento
facturasService.ts      // Facturas del paciente
pagosService.ts         // Historial de pagos
```

---

## 📋 TYPES DEFINIDOS

```typescript
auth.types.ts           // LoginCredentials, LoginResponse, Usuario
citas.types.ts          // Cita, EstadoCita, Odontologo
historial.types.ts      // HistorialClinico, Episodio, Documento
planes.types.ts         // PlanTratamiento, ItemPlan, EstadoPlan
facturacion.types.ts    // Factura, Pago, EstadoFactura, MetodoPago
```

---

## 🎯 FUNCIONALIDADES CORE DEL MÓDULO

### ✅ Autenticación
- Login con JWT
- Validación de tipo_usuario = 'paciente'
- Redirección automática al dashboard

### ✅ Gestión de Citas
- Ver todas las citas (filtradas automáticamente)
- Solicitar nueva cita
- Cancelar cita (con validaciones)
- Reprogramar cita

### ✅ Historial Clínico
- Ver historial completo con episodios
- Ver documentos clínicos (radiografías, fotos, etc.)
- Previsualizar y descargar documentos

### ✅ Planes de Tratamiento
- Ver lista de planes asignados
- Ver detalle completo de cada plan
- Ver progreso de servicios
- Ver presupuesto y costos

### ✅ Facturación
- Ver todas las facturas
- Ver detalle con items y pagos
- Ver estado de cuenta
- Alertas de vencimiento

---

## 🚀 PRÓXIMOS PASOS (OPCIONALES)

Las siguientes funcionalidades son **opcionales** según las necesidades del proyecto:

### 📧 Notificaciones (Fase 6)
- Ver notificaciones del sistema
- Configurar preferencias de notificaciones
- Marcar como leídas

### ⚙️ Configuración (Fase 7)
- Cambiar contraseña
- Configurar recordatorios
- Gestionar contactos de emergencia
- Cerrar sesión

---

## 📝 Formato de Cada Guía

Cada guía incluirá:

```markdown
# XX_nombre_interaccion.md

## 🎯 Objetivo
Descripción clara de la funcionalidad

## 📋 Prerequisitos
- Guías anteriores completadas
- Datos de prueba necesarios

## 🔌 Endpoint del Backend
- URL
- Método
- Headers
- Body (request)
- Response esperada

## 🧩 Componentes a Crear
- Listado de archivos
- Estructura de carpetas

## 💻 Código Paso a Paso
1. Crear servicio API
2. Crear tipos TypeScript
3. Crear componente principal
4. Agregar al routing
5. Integrar con layout

## 🧪 Pruebas
- Caso 1: Flujo exitoso
- Caso 2: Error común
- Caso 3: Validaciones

## ✅ Checklist de Verificación
- [ ] Componente renderiza correctamente
- [ ] API se llama sin errores
- [ ] Datos se muestran correctamente
- [ ] Manejo de errores funciona
- [ ] Loading states implementados
- [ ] Responsive en móvil

## 🐛 Errores Comunes
- Error típico 1: Solución
- Error típico 2: Solución

## 🔄 Siguiente Paso
Link a la siguiente guía
```

---

## 🚀 Metodología de Desarrollo

### Por Cada Guía:

1. **Leer** la guía completa
2. **Crear** los archivos necesarios
3. **Escribir** el código paso a paso
4. **Probar** en el navegador
5. **Verificar** el checklist
6. **Commit** con mensaje descriptivo
7. **Continuar** con la siguiente guía

### Ventajas:

- ✅ **Incremental**: Funcionalidad por funcionalidad
- ✅ **Testeable**: Cada paso es verificable
- ✅ **Debuggeable**: Errores aislados por guía
- ✅ **Documentado**: Cada guía explica el "por qué"
- ✅ **Reproducible**: Otros desarrolladores pueden seguirla

---

## 📊 Estado de Desarrollo

| Fase | Guías | Estado | Prioridad |
|------|-------|--------|-----------|
| Fase 1: Autenticación | 4 guías | 🔜 Pendiente | 🔴 Crítica |
| Fase 2: Citas | 4 guías | 🔜 Pendiente | 🔴 Crítica |
| Fase 3: Historial | 4 guías | 🔜 Pendiente | 🟡 Alta |
| Fase 4: Planes | 3 guías | 🔜 Pendiente | 🟡 Alta |
| Fase 5: Facturación | 4 guías | 🔜 Pendiente | 🟡 Alta |
| Fase 6: Notificaciones | 2 guías | 🔜 Pendiente | 🟢 Media |
| Fase 7: Configuración | 3 guías | 🔜 Pendiente | 🟢 Media |

**Total**: 24 guías

---

## 🎯 Orden de Implementación Recomendado

1. **Fase 1 completa** → Base funcional
2. **Fase 2 completa** → Funcionalidad crítica
3. **Fase 3 (09, 10)** → Visualización básica
4. **Fase 5 (16, 17)** → Información financiera
5. **Fase 4 completa** → Planes de tratamiento
6. **Fase 3 (11, 12)** → Documentos y odontograma
7. **Fase 6 completa** → Notificaciones
8. **Fase 7 completa** → Configuración

---

## 📞 Soporte

Si encuentras errores o necesitas aclaraciones:
1. Revisa la sección "Errores Comunes" de la guía
2. Verifica el checklist de prerequisitos
3. Consulta los logs del backend
4. Revisa la consola del navegador

---

**🚀 Comienza con: `01_login_paciente.md`**
