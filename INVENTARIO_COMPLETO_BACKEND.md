# 📊 INVENTARIO COMPLETO DEL BACKEND - CLÍNICA DENTAL

**Fecha:** 26 de Noviembre de 2025  
**Estado:** ✅ 100% COMPLETO Y FUNCIONAL  
**Total de Endpoints:** 85+  
**Framework:** Django REST Framework + django-tenants

---

## 📑 TABLA DE CONTENIDOS

1. [Autenticación y Usuarios](#1-autenticación-y-usuarios)
2. [Gestión de Agenda y Citas](#2-gestión-de-agenda-y-citas)
3. [Historial Clínico](#3-historial-clínico)
4. [Odontogramas](#4-odontogramas)
5. [Episodios de Atención](#5-episodios-de-atención)
6. [Documentos Clínicos](#6-documentos-clínicos)
7. [Planes de Tratamiento](#7-planes-de-tratamiento)
8. [Tratamientos y Servicios](#8-tratamientos-y-servicios)
9. [Facturación](#9-facturación)
10. [Inventario](#10-inventario)
11. [Reportes y Estadísticas](#11-reportes-y-estadísticas)
12. [Bitácora del Sistema](#12-bitácora-del-sistema)
13. [Multi-Tenancy](#13-multi-tenancy)

---

## 1. AUTENTICACIÓN Y USUARIOS

### 🔐 Autenticación JWT

#### Token de Acceso
```http
POST /api/token/
```
**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```
**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refrescar Token
```http
POST /api/token/refresh/
```
**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 👤 Gestión de Usuarios

#### Listar Usuarios
```http
GET /api/usuarios/
```
**Filtros disponibles:**
- `?tipo_usuario=ODONTOLOGO|PACIENTE|ADMIN`
- `?search=nombre`
- `?is_active=true|false`

#### Crear Usuario
```http
POST /api/usuarios/
```
**Body:**
```json
{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "tipo_usuario": "PACIENTE",
  "telefono": "+591 70123456"
}
```

#### Ver Detalle de Usuario
```http
GET /api/usuarios/{id}/
```

#### Actualizar Usuario
```http
PUT /api/usuarios/{id}/
PATCH /api/usuarios/{id}/
```

#### Eliminar Usuario
```http
DELETE /api/usuarios/{id}/
```

#### Perfil del Usuario Autenticado
```http
GET /api/usuarios/me/
```
**Response:**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "tipo_usuario": "ODONTOLOGO",
  "telefono": "+591 70123456",
  "is_active": true
}
```

#### Actualizar Mi Perfil
```http
PUT /api/usuarios/me/
PATCH /api/usuarios/me/
```

#### Cambiar Contraseña
```http
POST /api/usuarios/cambiar_password/
```
**Body:**
```json
{
  "old_password": "contraseña_antigua",
  "new_password": "contraseña_nueva"
}
```

#### Listar Odontólogos
```http
GET /api/usuarios/odontologos/
```
**Response:**
```json
[
  {
    "id": 1,
    "usuario": {
      "id": 2,
      "email": "odontologo@ejemplo.com",
      "nombre": "Dr. Juan",
      "apellido": "Pérez"
    },
    "especialidad": "Ortodoncia",
    "numero_matricula": "12345",
    "telefono_consultorio": "+591 4-4567890"
  }
]
```

#### Listar Pacientes
```http
GET /api/usuarios/pacientes/
```
**Filtros:**
- `?search=nombre`
- `?fecha_nacimiento=YYYY-MM-DD`

---

## 2. GESTIÓN DE AGENDA Y CITAS

### 📅 CRUD de Citas

#### Listar Citas
```http
GET /api/agenda/citas/
```
**Filtros disponibles:**
- `?estado=PENDIENTE|CONFIRMADA|ATENDIDA|CANCELADA`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`
- `?odontologo={id}`
- `?paciente={id}`
- `?search=motivo`

**Response:**
```json
[
  {
    "id": 1,
    "paciente": {
      "id": 1,
      "nombre": "María García",
      "email": "maria@ejemplo.com"
    },
    "odontologo": {
      "id": 1,
      "nombre": "Dr. Juan Pérez",
      "especialidad": "Ortodoncia"
    },
    "fecha_hora": "2025-11-26T10:00:00Z",
    "motivo": "Revisión general",
    "motivo_tipo": "CONSULTA_GENERAL",
    "estado": "CONFIRMADA",
    "duracion_estimada": 30,
    "observaciones": "Paciente refiere dolor en molar superior derecho"
  }
]
```

#### Crear Cita
```http
POST /api/agenda/citas/
```
**Body:**
```json
{
  "paciente": 1,
  "odontologo": 1,
  "fecha_hora": "2025-11-27T14:00:00",
  "motivo": "Limpieza dental",
  "motivo_tipo": "LIMPIEZA",
  "duracion_estimada": 60,
  "observaciones": "Primera visita del paciente"
}
```

#### Ver Detalle de Cita
```http
GET /api/agenda/citas/{id}/
```

#### Actualizar Cita
```http
PUT /api/agenda/citas/{id}/
PATCH /api/agenda/citas/{id}/
```

#### Eliminar Cita
```http
DELETE /api/agenda/citas/{id}/
```

### 🎯 Acciones Especiales de Citas

#### Confirmar Cita
```http
POST /api/agenda/citas/{id}/confirmar/
```
**Response:**
```json
{
  "mensaje": "Cita confirmada exitosamente",
  "estado": "CONFIRMADA"
}
```

#### Cancelar Cita
```http
POST /api/agenda/citas/{id}/cancelar/
```
**Body (opcional):**
```json
{
  "motivo_cancelacion": "Paciente no puede asistir"
}
```

#### Atender Cita
```http
POST /api/agenda/citas/{id}/atender/
```
**Response:**
```json
{
  "mensaje": "Cita marcada como atendida",
  "estado": "ATENDIDA"
}
```

#### Completar Cita
```http
POST /api/agenda/citas/{id}/completar/
```
**Body:**
```json
{
  "observaciones_finales": "Tratamiento completado satisfactoriamente",
  "proxima_cita": "2025-12-26T10:00:00"
}
```

### 📊 Métricas y Disponibilidad

#### Métricas del Día (Dashboard)
```http
GET /api/agenda/citas/metricas-dia/
```
**Solo para odontólogos**

**Response:**
```json
{
  "fecha": "2025-11-26",
  "citas_hoy": 8,
  "citas_pendientes": 3,
  "citas_confirmadas": 2,
  "citas_atendidas": 3,
  "pacientes_atendidos": 3,
  "proxima_cita": {
    "id": 12,
    "hora": "15:00",
    "paciente": "María García",
    "motivo": "Control de ortodoncia",
    "estado": "CONFIRMADA",
    "minutos_restantes": 45
  }
}
```

#### Disponibilidad de Horarios (Para Calendario)
```http
GET /api/agenda/citas/disponibilidad/
```
**Query params:**
- `fecha` (requerido): YYYY-MM-DD
- `odontologo_id` (requerido): ID del odontólogo

**Response:**
```json
{
  "fecha": "2025-11-26",
  "odontologo": {
    "id": 1,
    "nombre": "Dr. Juan Pérez",
    "especialidad": "Ortodoncia"
  },
  "horarios_disponibles": [
    "09:00", "09:30", "10:00", "10:30",
    "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30"
  ],
  "horarios_ocupados": [
    "11:00", "11:30", "13:00"
  ],
  "horario_atencion": {
    "inicio": "09:00",
    "fin": "18:00"
  }
}
```

#### Horarios Disponibles (Alternativo)
```http
GET /api/agenda/citas/horarios_disponibles/
```
**Query params:**
- `odontologo` (requerido): ID del odontólogo
- `fecha` (requerido): YYYY-MM-DD
- `duracion` (opcional): Duración en minutos (default: 30)

**Response:**
```json
{
  "fecha": "2025-11-26",
  "odontologo": "Dr. Juan Pérez",
  "odontologo_id": 1,
  "total_disponibles": 18,
  "total_ocupados": 3,
  "horarios": [
    {"hora": "09:00", "disponible": true},
    {"hora": "09:30", "disponible": true},
    {"hora": "10:00", "disponible": false},
    {"hora": "10:30", "disponible": true}
  ]
}
```

#### Citas Próximas
```http
GET /api/agenda/citas/proximas/
```
**Response:** Citas futuras ordenadas por fecha

#### Citas de Hoy
```http
GET /api/agenda/citas/hoy/
```
**Response:** Citas del día actual

---

## 3. HISTORIAL CLÍNICO

### 📋 CRUD de Historiales

#### Listar Historiales Clínicos
```http
GET /api/historial/historiales/
```
**Filtros:**
- `?paciente={id}`
- `?search=diagnóstico`

**Response:**
```json
[
  {
    "id": 1,
    "paciente": {
      "id": 1,
      "nombre": "María García",
      "email": "maria@ejemplo.com",
      "fecha_nacimiento": "1990-05-15"
    },
    "motivo_consulta": "Dolor en molar superior derecho",
    "antecedentes_medicos": "Hipertensión controlada",
    "alergias": "Penicilina",
    "medicamentos_actuales": "Enalapril 10mg",
    "fecha_creacion": "2025-01-15T10:00:00Z",
    "total_episodios": 5,
    "total_odontogramas": 2,
    "ultimo_episodio": "2025-11-20T14:30:00Z"
  }
]
```

#### Crear Historial Clínico
```http
POST /api/historial/historiales/
```
**Body:**
```json
{
  "paciente": 1,
  "motivo_consulta": "Primera consulta - Revisión general",
  "antecedentes_medicos": "Ninguno",
  "alergias": "",
  "medicamentos_actuales": ""
}
```

#### Ver Detalle de Historial
```http
GET /api/historial/historiales/{id}/
```
**Response:** Incluye episodios, odontogramas y documentos

#### Actualizar Historial
```http
PUT /api/historial/historiales/{id}/
PATCH /api/historial/historiales/{id}/
```

#### Eliminar Historial
```http
DELETE /api/historial/historiales/{id}/
```

---

## 4. ODONTOGRAMAS

### 🦷 CRUD de Odontogramas

#### Listar Odontogramas
```http
GET /api/historial/odontogramas/
```
**Filtros:**
- `?historial_clinico={id}`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`

**Response:**
```json
[
  {
    "id": 1,
    "historial_clinico": 1,
    "fecha_snapshot": "2025-11-26T10:00:00Z",
    "estado_piezas": {
      "11": {"estado": "sano"},
      "12": {"estado": "sano"},
      "13": {"estado": "sano"},
      "16": {
        "estado": "restaurado",
        "material": "resina",
        "superficie": ["oclusal"],
        "notas": "Restauración reciente"
      },
      "18": {"estado": "extraido"},
      "21": {"estado": "caries", "superficie": ["mesial", "oclusal"]},
      "26": {
        "estado": "endodoncia",
        "notas": "Tratamiento de conducto completado"
      }
    },
    "notas": "Buen estado general de higiene oral",
    "total_dientes_registrados": 32,
    "resumen_estados": {
      "sano": 24,
      "restaurado": 3,
      "caries": 2,
      "extraido": 2,
      "endodoncia": 1
    },
    "paciente_info": {
      "id": 1,
      "nombre": "María García",
      "email": "maria@ejemplo.com"
    }
  }
]
```

#### Crear Odontograma
```http
POST /api/historial/odontogramas/
```
**Body:**
```json
{
  "historial_clinico": 1,
  "estado_piezas": {
    "11": {"estado": "sano"},
    "12": {"estado": "caries", "superficie": ["oclusal"], "notas": "Caries profunda"},
    "13": {"estado": "restaurado", "material": "resina"},
    "16": {"estado": "corona", "material": "porcelana"},
    "18": {"estado": "extraido", "fecha_extraccion": "2024-06-15"}
  },
  "notas": "Primera evaluación completa del paciente"
}
```

#### Ver Detalle de Odontograma
```http
GET /api/historial/odontogramas/{id}/
```

#### Actualizar Odontograma
```http
PUT /api/historial/odontogramas/{id}/
PATCH /api/historial/odontogramas/{id}/
```

#### Eliminar Odontograma
```http
DELETE /api/historial/odontogramas/{id}/
```

### 🎯 Acciones Especiales de Odontogramas

#### Configuración del Odontograma
```http
GET /api/historial/odontogramas/configuracion/
```
**Response completo con:**
- Cuadrantes (1, 2, 3, 4)
- Nomenclatura FDI (11-48 adultos, 51-85 niños)
- Estados disponibles (sano, caries, restaurado, corona, endodoncia, extraido, implante, protesis)
- Colores por estado
- Superficies (oclusal, mesial, distal, vestibular, lingual, palatina)
- Materiales (resina, amalgama, porcelana, zirconio, composite, oro, metal-porcelana, titanio)

**Response:**
```json
{
  "nomenclatura": "FDI",
  "sistema": "Internacional (FDI)",
  "total_dientes_adulto": 32,
  "total_dientes_nino": 20,
  "cuadrantes": {
    "1": {
      "numero": 1,
      "nombre": "Superior Derecho",
      "nombre_corto": "SD",
      "posicion": "top-right",
      "arcada": "superior",
      "lado": "derecho",
      "dientes": [
        {"numero": "18", "nombre": "Tercer Molar", "tipo": "molar"},
        {"numero": "17", "nombre": "Segundo Molar", "tipo": "molar"},
        {"numero": "16", "nombre": "Primer Molar", "tipo": "molar"},
        {"numero": "15", "nombre": "Segundo Premolar", "tipo": "premolar"},
        {"numero": "14", "nombre": "Primer Premolar", "tipo": "premolar"},
        {"numero": "13", "nombre": "Canino", "tipo": "canino"},
        {"numero": "12", "nombre": "Incisivo Lateral", "tipo": "incisivo"},
        {"numero": "11", "nombre": "Incisivo Central", "tipo": "incisivo"}
      ]
    }
  },
  "estados": [
    {
      "valor": "sano",
      "etiqueta": "Sano",
      "color": "#10b981",
      "color_fondo": "#d1fae5",
      "icono": "✓",
      "descripcion": "Diente sin patologías"
    },
    {
      "valor": "caries",
      "etiqueta": "Caries",
      "color": "#ef4444",
      "color_fondo": "#fee2e2",
      "icono": "⚠",
      "descripcion": "Diente con caries activa"
    }
  ],
  "superficies": [
    {"valor": "oclusal", "etiqueta": "Oclusal", "abreviatura": "O"},
    {"valor": "mesial", "etiqueta": "Mesial", "abreviatura": "M"},
    {"valor": "distal", "etiqueta": "Distal", "abreviatura": "D"}
  ],
  "materiales": [
    {"valor": "resina", "etiqueta": "Resina Compuesta"},
    {"valor": "amalgama", "etiqueta": "Amalgama"},
    {"valor": "porcelana", "etiqueta": "Porcelana"}
  ]
}
```

#### Duplicar Odontograma
```http
POST /api/historial/odontogramas/{id}/duplicar_odontograma/
```
**Response:** Nuevo odontograma con los mismos datos

---

## 5. EPISODIOS DE ATENCIÓN

### 📝 CRUD de Episodios

#### Listar Episodios de Atención
```http
GET /api/historial/episodios/
```
**Filtros:**
- `?historial_clinico={id}`
- `?cita={id}`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`

**Response:**
```json
[
  {
    "id": 1,
    "historial_clinico": 1,
    "cita": 5,
    "fecha_atencion": "2025-11-26T10:30:00Z",
    "motivo_consulta": "Control de ortodoncia",
    "sintomas": "Sin molestias",
    "diagnostico": "Tratamiento ortodóntico en progreso",
    "tratamiento_realizado": "Ajuste de brackets",
    "observaciones": "Paciente muestra buena evolución",
    "proxima_cita_sugerida": "2025-12-26",
    "odontologo": {
      "id": 1,
      "nombre": "Dr. Juan Pérez"
    }
  }
]
```

#### Crear Episodio de Atención
```http
POST /api/historial/episodios/
```
**Body:**
```json
{
  "historial_clinico": 1,
  "cita": 5,
  "motivo_consulta": "Dolor en molar",
  "sintomas": "Dolor agudo al masticar",
  "diagnostico": "Caries profunda en pieza 16",
  "tratamiento_realizado": "Obturación con resina",
  "observaciones": "Se recomienda uso de hilo dental",
  "proxima_cita_sugerida": "2026-01-26"
}
```

#### Ver Detalle de Episodio
```http
GET /api/historial/episodios/{id}/
```

#### Actualizar Episodio
```http
PUT /api/historial/episodios/{id}/
PATCH /api/historial/episodios/{id}/
```

#### Eliminar Episodio
```http
DELETE /api/historial/episodios/{id}/
```

---

## 6. DOCUMENTOS CLÍNICOS

### 📄 CRUD de Documentos

#### Listar Documentos
```http
GET /api/historial/documentos/
```
**Filtros:**
- `?historial_clinico={id}`
- `?episodio={id}`
- `?tipo_documento=RADIOGRAFIA|FOTO|PDF|CONSENTIMIENTO|RECETA|OTRO`

**Response:**
```json
[
  {
    "id": 1,
    "historial_clinico": 1,
    "episodio": 3,
    "tipo_documento": "RADIOGRAFIA",
    "titulo": "Radiografía panorámica",
    "descripcion": "Evaluación inicial del paciente",
    "archivo": "http://example.com/media/documentos/paciente_1/radiografia_001.jpg",
    "fecha_subida": "2025-11-26T09:00:00Z",
    "subido_por": {
      "id": 2,
      "nombre": "Dr. Juan Pérez"
    }
  }
]
```

#### Subir Documento
```http
POST /api/historial/documentos/
```
**Content-Type:** `multipart/form-data`

**Body:**
```
historial_clinico: 1
episodio: 3 (opcional)
tipo_documento: RADIOGRAFIA
titulo: Radiografía panorámica
descripcion: Evaluación inicial
archivo: [archivo binario]
```

#### Ver Detalle de Documento
```http
GET /api/historial/documentos/{id}/
```

#### Actualizar Documento (metadatos)
```http
PATCH /api/historial/documentos/{id}/
```

#### Eliminar Documento
```http
DELETE /api/historial/documentos/{id}/
```

#### Descargar Documento
```http
GET /api/historial/documentos/{id}/descargar/
```

---

## 7. PLANES DE TRATAMIENTO

### 📋 CRUD de Planes

#### Listar Planes de Tratamiento
```http
GET /api/tratamientos/planes/
```
**Filtros:**
- `?paciente={id}`
- `?estado=PROPUESTO|ACEPTADO|EN_PROGRESO|COMPLETADO|CANCELADO`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`

**Response:**
```json
[
  {
    "id": 1,
    "paciente": {
      "id": 1,
      "nombre": "María García"
    },
    "titulo": "Plan de Ortodoncia Completo",
    "descripcion": "Tratamiento ortodóntico con brackets metálicos",
    "fecha_inicio": "2025-01-15",
    "fecha_fin_estimada": "2026-01-15",
    "estado": "EN_PROGRESO",
    "total_tratamientos": 12,
    "costo_total": 15000.00,
    "costo_pagado": 5000.00,
    "saldo_pendiente": 10000.00,
    "progreso_porcentaje": 30,
    "items": [
      {
        "id": 1,
        "servicio": {
          "id": 5,
          "nombre": "Brackets Metálicos",
          "codigo": "ORTO-001"
        },
        "cantidad": 1,
        "precio_unitario": 8000.00,
        "descuento_porcentaje": 0,
        "subtotal": 8000.00,
        "completado": false,
        "fecha_programada": "2025-01-15"
      }
    ]
  }
]
```

#### Crear Plan de Tratamiento
```http
POST /api/tratamientos/planes/
```
**Body:**
```json
{
  "paciente": 1,
  "titulo": "Plan de Rehabilitación Dental",
  "descripcion": "Tratamiento integral de rehabilitación",
  "fecha_inicio": "2025-12-01",
  "fecha_fin_estimada": "2026-06-01",
  "items": [
    {
      "servicio": 3,
      "cantidad": 2,
      "precio_unitario": 500.00,
      "descuento_porcentaje": 10
    }
  ]
}
```

#### Ver Detalle de Plan
```http
GET /api/tratamientos/planes/{id}/
```

#### Actualizar Plan
```http
PUT /api/tratamientos/planes/{id}/
PATCH /api/tratamientos/planes/{id}/
```

#### Eliminar Plan
```http
DELETE /api/tratamientos/planes/{id}/
```

### 🎯 Acciones de Planes

#### Agregar Item al Plan
```http
POST /api/tratamientos/planes/{id}/agregar_item/
```
**Body:**
```json
{
  "servicio": 5,
  "cantidad": 1,
  "precio_unitario": 1200.00,
  "descuento_porcentaje": 0,
  "fecha_programada": "2025-12-15"
}
```

#### Marcar Item como Completado
```http
POST /api/tratamientos/planes/{id}/completar_item/
```
**Body:**
```json
{
  "item_id": 3
}
```

#### Cambiar Estado del Plan
```http
POST /api/tratamientos/planes/{id}/cambiar_estado/
```
**Body:**
```json
{
  "nuevo_estado": "ACEPTADO"
}
```

---

## 8. TRATAMIENTOS Y SERVICIOS

### 💊 CRUD de Servicios

#### Listar Servicios/Tratamientos
```http
GET /api/tratamientos/servicios/
```
**Filtros:**
- `?categoria=CONSULTA|LIMPIEZA|ORTODONCIA|ENDODONCIA|CIRUGIA|ESTETICA|OTRO`
- `?activo=true|false`
- `?search=nombre`

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Limpieza Dental Completa",
    "codigo": "LIMP-001",
    "descripcion": "Limpieza profunda con ultrasonido y pulido",
    "categoria": "LIMPIEZA",
    "precio_base": 250.00,
    "duracion_estimada": 60,
    "activo": true,
    "requiere_autorizacion": false
  }
]
```

#### Crear Servicio
```http
POST /api/tratamientos/servicios/
```
**Body:**
```json
{
  "nombre": "Blanqueamiento Dental",
  "codigo": "ESTE-001",
  "descripcion": "Blanqueamiento con peróxido de hidrógeno",
  "categoria": "ESTETICA",
  "precio_base": 800.00,
  "duracion_estimada": 90,
  "activo": true
}
```

#### Ver Detalle de Servicio
```http
GET /api/tratamientos/servicios/{id}/
```

#### Actualizar Servicio
```http
PUT /api/tratamientos/servicios/{id}/
PATCH /api/tratamientos/servicios/{id}/
```

#### Eliminar Servicio
```http
DELETE /api/tratamientos/servicios/{id}/
```

---

## 9. FACTURACIÓN

### 💰 CRUD de Facturas

#### Listar Facturas
```http
GET /api/facturacion/facturas/
```
**Filtros:**
- `?paciente={id}`
- `?estado=PENDIENTE|PAGADA|PARCIAL|VENCIDA|CANCELADA`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`

**Response:**
```json
[
  {
    "id": 1,
    "numero_factura": "FAC-2025-001",
    "paciente": {
      "id": 1,
      "nombre": "María García"
    },
    "plan_tratamiento": 1,
    "fecha_emision": "2025-11-26",
    "fecha_vencimiento": "2025-12-26",
    "subtotal": 1500.00,
    "descuento": 150.00,
    "impuestos": 0.00,
    "total": 1350.00,
    "monto_pagado": 500.00,
    "saldo_pendiente": 850.00,
    "estado": "PARCIAL",
    "items": [
      {
        "id": 1,
        "servicio": "Limpieza Dental",
        "cantidad": 1,
        "precio_unitario": 250.00,
        "descuento": 25.00,
        "subtotal": 225.00
      }
    ],
    "pagos": [
      {
        "id": 1,
        "fecha": "2025-11-26T10:00:00Z",
        "monto": 500.00,
        "metodo_pago": "EFECTIVO",
        "referencia": "PAG-001"
      }
    ]
  }
]
```

#### Crear Factura
```http
POST /api/facturacion/facturas/
```
**Body:**
```json
{
  "paciente": 1,
  "plan_tratamiento": 1,
  "fecha_vencimiento": "2025-12-26",
  "items": [
    {
      "servicio": 1,
      "cantidad": 1,
      "precio_unitario": 250.00,
      "descuento": 0
    }
  ],
  "observaciones": "Primera factura del plan"
}
```

#### Ver Detalle de Factura
```http
GET /api/facturacion/facturas/{id}/
```

#### Actualizar Factura
```http
PUT /api/facturacion/facturas/{id}/
PATCH /api/facturacion/facturas/{id}/
```

#### Eliminar Factura
```http
DELETE /api/facturacion/facturas/{id}/
```

### 💳 Gestión de Pagos

#### Registrar Pago
```http
POST /api/facturacion/facturas/{id}/registrar_pago/
```
**Body:**
```json
{
  "monto": 500.00,
  "metodo_pago": "EFECTIVO|TARJETA|TRANSFERENCIA|CHEQUE",
  "referencia": "PAG-001",
  "observaciones": "Pago parcial"
}
```

#### Anular Factura
```http
POST /api/facturacion/facturas/{id}/anular/
```
**Body:**
```json
{
  "motivo": "Error en facturación"
}
```

#### Generar PDF de Factura
```http
GET /api/facturacion/facturas/{id}/generar_pdf/
```
**Response:** Archivo PDF

---

## 10. INVENTARIO

### 📦 Categorías de Insumos

#### Listar Categorías
```http
GET /api/inventario/categorias/
```

#### Crear Categoría
```http
POST /api/inventario/categorias/
```
**Body:**
```json
{
  "nombre": "Material de Obturación",
  "descripcion": "Materiales para obturaciones dentales"
}
```

### 🧪 CRUD de Insumos

#### Listar Insumos
```http
GET /api/inventario/insumos/
```
**Filtros:**
- `?categoria={id}`
- `?search=nombre`
- `?stock_minimo=true` (solo insumos con stock bajo)

**Response:**
```json
[
  {
    "id": 1,
    "codigo": "INS-001",
    "nombre": "Resina Compuesta A2",
    "descripcion": "Resina fotopolimerizable tono A2",
    "categoria": {
      "id": 1,
      "nombre": "Material de Obturación"
    },
    "unidad_medida": "UNIDAD",
    "stock_actual": 15,
    "stock_minimo": 5,
    "stock_maximo": 50,
    "precio_unitario": 45.00,
    "proveedor": "Dental Supply SA",
    "fecha_vencimiento": "2026-12-31",
    "ubicacion": "Estante A, Fila 2",
    "activo": true
  }
]
```

#### Crear Insumo
```http
POST /api/inventario/insumos/
```
**Body:**
```json
{
  "codigo": "INS-002",
  "nombre": "Agujas Dentales 25G",
  "descripcion": "Agujas desechables calibre 25",
  "categoria": 2,
  "unidad_medida": "CAJA",
  "stock_actual": 10,
  "stock_minimo": 3,
  "stock_maximo": 20,
  "precio_unitario": 25.00,
  "proveedor": "MedSupply"
}
```

#### Ver Detalle de Insumo
```http
GET /api/inventario/insumos/{id}/
```

#### Actualizar Insumo
```http
PUT /api/inventario/insumos/{id}/
PATCH /api/inventario/insumos/{id}/
```

#### Eliminar Insumo
```http
DELETE /api/inventario/insumos/{id}/
```

### 📊 Acciones de Inventario

#### Insumos con Stock Bajo
```http
GET /api/inventario/insumos/bajo_stock/
```
**Query params:**
- `?page_size=10`

#### Ajustar Stock
```http
POST /api/inventario/insumos/{id}/ajustar_stock/
```
**Body:**
```json
{
  "cantidad": -5,
  "motivo": "Uso en tratamiento",
  "observaciones": "Utilizado en 5 obturaciones"
}
```

#### Movimientos de Inventario
```http
GET /api/inventario/movimientos/
```
**Filtros:**
- `?insumo={id}`
- `?tipo=ENTRADA|SALIDA|AJUSTE`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`

---

## 11. REPORTES Y ESTADÍSTICAS

### 📊 Reportes Generales

#### Dashboard KPIs
```http
GET /api/reportes/reportes/dashboard-kpis/
```
**Query params (opcionales):**
- `?formato=pdf` - Exportar a PDF
- `?formato=excel` - Exportar a Excel

**Response:**
```json
{
  "total_pacientes": 156,
  "total_citas_mes": 89,
  "ingresos_mes": 45000.00,
  "citas_pendientes": 12,
  "tasa_asistencia": 85.5,
  "pacientes_nuevos_mes": 8,
  "tratamientos_activos": 23
}
```

#### Tendencia de Citas
```http
GET /api/reportes/reportes/tendencia-citas/
```
**Query params:**
- `?dias=15` - Número de días a analizar (default: 15)
- `?formato=pdf|excel`

**Response:**
```json
[
  {
    "fecha": "2025-11-12",
    "cantidad": 8,
    "completadas": 6,
    "canceladas": 1,
    "pendientes": 1
  },
  {
    "fecha": "2025-11-13",
    "cantidad": 10,
    "completadas": 9,
    "canceladas": 0,
    "pendientes": 1
  }
]
```

#### Top Procedimientos
```http
GET /api/reportes/reportes/top-procedimientos/
```
**Query params:**
- `?limite=5` - Número de procedimientos (default: 5)
- `?formato=pdf|excel`

**Response:**
```json
[
  {
    "servicio": "Limpieza Dental",
    "cantidad": 45,
    "ingresos_totales": 11250.00
  },
  {
    "servicio": "Ortodoncia",
    "cantidad": 12,
    "ingresos_totales": 96000.00
  }
]
```

#### Estadísticas Generales
```http
GET /api/reportes/reportes/estadisticas-generales/
```
**Query params:**
- `?formato=pdf|excel`

**Response:**
```json
{
  "pacientes": {
    "total": 156,
    "activos": 142,
    "nuevos_mes": 8
  },
  "citas": {
    "total_mes": 89,
    "confirmadas": 45,
    "atendidas": 38,
    "canceladas": 6
  },
  "financiero": {
    "ingresos_mes": 45000.00,
    "pendiente_cobro": 12000.00,
    "facturado_mes": 57000.00
  },
  "inventario": {
    "insumos_bajo_stock": 5,
    "valor_total_inventario": 15600.00
  }
}
```

#### Reporte de Ingresos
```http
GET /api/reportes/reportes/ingresos/
```
**Query params:**
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`
- `?formato=pdf|excel`

#### Reporte de Pacientes Atendidos
```http
GET /api/reportes/reportes/pacientes-atendidos/
```
**Query params:**
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`
- `?odontologo={id}`
- `?formato=pdf|excel`

---

## 12. BITÁCORA DEL SISTEMA

### 📝 Registro de Actividad

#### Listar Bitácoras
```http
GET /api/reportes/bitacora/
```
**Filtros:**
- `?usuario={id}`
- `?accion=CREATE|UPDATE|DELETE|VIEW|LOGIN|LOGOUT`
- `?modelo=Cita|Paciente|Factura|etc`
- `?fecha_inicio=YYYY-MM-DD`
- `?fecha_fin=YYYY-MM-DD`
- `?page=1&page_size=10`

**Response:**
```json
{
  "count": 250,
  "next": "http://api/reportes/bitacora/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": {
        "id": 2,
        "nombre": "Dr. Juan Pérez",
        "email": "juan@clinica.com"
      },
      "accion": "UPDATE",
      "modelo": "Cita",
      "objeto_id": 45,
      "descripcion": "Actualizó el estado de la cita a ATENDIDA",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "fecha_hora": "2025-11-26T14:30:00Z",
      "detalles": {
        "cambios": {
          "estado": ["CONFIRMADA", "ATENDIDA"]
        }
      }
    }
  ]
}
```

#### Ver Detalle de Bitácora
```http
GET /api/reportes/bitacora/{id}/
```

---

## 13. MULTI-TENANCY

### 🏢 Gestión de Tenants (Solo Admin Público)

#### Listar Clínicas (Tenants)
```http
GET /api/public/tenants/
```
**Solo accesible desde dominio público**

#### Crear Clínica
```http
POST /api/public/tenants/
```
**Body:**
```json
{
  "schema_name": "clinica_demo",
  "nombre": "Clínica Dental Demo",
  "domain": "clinica-demo.localhost"
}
```

#### Ver Detalle de Clínica
```http
GET /api/public/tenants/{id}/
```

### 📋 Planes de Suscripción

#### Listar Planes
```http
GET /api/public/planes/
```

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Plan Básico",
    "descripcion": "Ideal para clínicas pequeñas",
    "precio_mensual": 99.00,
    "max_usuarios": 5,
    "max_pacientes": 100,
    "activo": true
  }
]
```

---

## 📊 RESUMEN ESTADÍSTICO

### Total de Endpoints por Módulo:

| Módulo | Endpoints | Estado |
|--------|-----------|--------|
| Autenticación y Usuarios | 12 | ✅ |
| Agenda y Citas | 15 | ✅ |
| Historial Clínico | 5 | ✅ |
| Odontogramas | 7 | ✅ |
| Episodios de Atención | 5 | ✅ |
| Documentos Clínicos | 6 | ✅ |
| Planes de Tratamiento | 8 | ✅ |
| Servicios/Tratamientos | 5 | ✅ |
| Facturación | 7 | ✅ |
| Inventario | 9 | ✅ |
| Reportes | 6 | ✅ |
| Bitácora | 2 | ✅ |
| Multi-Tenancy | 5 | ✅ |
| **TOTAL** | **92** | **100%** |

---

## 🔐 SISTEMA DE PERMISOS

### Roles Disponibles:
- **ADMIN**: Acceso completo a todas las funcionalidades
- **ODONTOLOGO**: Acceso a citas, historiales, tratamientos
- **PACIENTE**: Acceso limitado a sus propios datos

### Filtrado Automático por Rol:
- Los pacientes solo ven sus propios registros
- Los odontólogos ven todos los pacientes pero solo sus citas
- Los administradores tienen acceso completo

---

## 🧪 ARCHIVOS DE PRUEBA

Disponibles en `pruebas_http/`:
1. `00_autenticacion.http` - Login y tokens
2. `01_inventario.http` - Gestión de inventario
3. `02_tratamientos.http` - Servicios y planes
4. `03_agenda_historial.http` - Citas e historiales
5. `04_facturacion.http` - Facturas y pagos
6. `05_reportes.http` - Estadísticas y reportes
7. `06_permisos_paciente.http` - Pruebas de permisos
8. `07_casos_especiales.http` - Casos edge
9. `08_odontogramas.http` - CRUD de odontogramas
10. `09_metricas_dia.http` - Dashboard de métricas
11. `10_odontograma_configuracion.http` - Configuración completa

---

## 📚 DOCUMENTACIÓN ADICIONAL

### Guías de Implementación Frontend:
- Ubicación: `GUIA_FRONT/`
- Total: 30+ guías detalladas
- Incluye: Componentes React, TypeScript, servicios API

### Guías de Desarrollo Backend:
- Ubicación: `guias/`
- Incluye: Arquitectura, modelos, debugging

### Guías para Desarrollo Móvil:
- Ubicación: `guia_desarrollo/paciente_flutter/`
- Framework: Flutter/Dart

---

## ✅ ESTADO FINAL

**Backend: 100% COMPLETO Y FUNCIONAL**

- ✅ 13 módulos implementados
- ✅ 92+ endpoints activos
- ✅ Sistema multi-tenant funcionando
- ✅ Autenticación JWT implementada
- ✅ Permisos por rol configurados
- ✅ Archivos de prueba disponibles
- ✅ Documentación completa
- ✅ Listo para integración con frontend

**Última actualización:** 26 de Noviembre de 2025
