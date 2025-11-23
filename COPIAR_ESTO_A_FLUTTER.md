# 🔥 INSTRUCCIONES URGENTES - Corregir Error de Parsing

## ❌ ERROR ACTUAL
```
type 'String' is not a subtype of type 'int' of 'index'
en línea 59 de tratamientos_service.dart
```

## 🎯 CAUSA
Tu código Flutter tiene la **versión VIEJA** del modelo `PlanTratamiento.fromJson()`. El backend devuelve `odontologo_nombre` como string, pero tu código intenta acceder a `odontologo_info['nombre_completo']` (objeto que NO existe).

---

## 📋 PASO 1: Abrir Archivo

Abre: `lib/models/tratamiento.dart` en tu proyecto Flutter

---

## 📋 PASO 2: Reemplazar `PlanTratamiento.fromJson()`

**BUSCA esta línea en tu código:**
```dart
factory PlanTratamiento.fromJson(Map<String, dynamic> json) {
```

**REEMPLAZA TODO EL MÉTODO con esto:**

```dart
factory PlanTratamiento.fromJson(Map<String, dynamic> json) {
  return PlanTratamiento(
    id: json['id'],
    nombre: json['titulo'] ?? json['nombre'] ?? '',
    descripcion: json['descripcion'] ?? '',
    costoTotal: double.parse(json['precio_total_plan']?.toString() ?? '0'),
    montoAbonado: 0.0,
    estado: json['estado'] ?? '',
    fechaInicio: json['fecha_inicio'] != null
        ? DateTime.parse(json['fecha_inicio'])
        : DateTime.now(),
    fechaFin: json['fecha_finalizacion'] != null
        ? DateTime.parse(json['fecha_finalizacion'])
        : null,
    // 🔥 FIX CRÍTICO: Primero string (list), luego objeto (detail)
    odontologoNombre: json['odontologo_nombre'] ??
                     json['odontologo_info']?['nombre_completo'] ??
                     '',
    items: (json['items_simples'] as List?)
        ?.map((e) => ItemTratamiento.fromJson(e))
        .toList() ??
        (json['items'] as List?)
        ?.map((e) => ItemTratamiento.fromJson(e))
        .toList() ?? [],
    progresoPercentage: json['porcentaje_completado'] ?? 0,
  );
}
```

**🔑 CAMBIO CLAVE:**
- ❌ VIEJO: `json['odontologo_info']?['nombre_completo']` (PRIMERO objeto)
- ✅ NUEVO: `json['odontologo_nombre']` (PRIMERO string)

---

## 📋 PASO 3: Reemplazar `ItemTratamiento.fromJson()`

**BUSCA esta línea en tu código:**
```dart
factory ItemTratamiento.fromJson(Map<String, dynamic> json) {
```

**REEMPLAZA TODO EL MÉTODO con esto:**

```dart
factory ItemTratamiento.fromJson(Map<String, dynamic> json) {
  return ItemTratamiento(
    id: json['id'],
    // 🔥 FIX CRÍTICO: Primero string (list), luego objeto (detail)
    servicio: json['servicio_nombre'] ??
             json['servicio_info']?['nombre'] ??
             '',
    piezaDental: json['pieza_dental'],
    // 🔥 FIX CRÍTICO: Manejar formato "$50.00"
    costo: double.parse(
      json['precio_total_formateado']?.toString().replaceAll(r'$', '').replaceAll(',', '') ?? 
      json['precio_total']?.toString() ?? '0'
    ),
    estado: json['estado'] ?? '',
    sesionesRequeridas: 1,
    sesionesCompletadas: json['estado'] == 'COMPLETADO' ? 1 : 0,
    fechaInicio: json['fecha_realizada'] != null
        ? DateTime.parse(json['fecha_realizada'])
        : null,
    fechaFin: json['fecha_realizada'] != null && json['estado'] == 'COMPLETADO'
        ? DateTime.parse(json['fecha_realizada'])
        : null,
    notas: json['notas'],
  );
}
```

**🔑 CAMBIOS CLAVE:**
- ❌ VIEJO: `json['servicio_info']?['nombre']` (PRIMERO objeto)
- ✅ NUEVO: `json['servicio_nombre']` (PRIMERO string)
- ✅ NUEVO: Maneja `"$50.00"` quitando el símbolo `$`

---

## 📋 PASO 4: Guardar y Reiniciar

1. **Guarda el archivo** `tratamiento.dart`
2. **En el terminal de Flutter, presiona:** `R` (Hot Restart completo)
3. **Verifica los logs:**
   - ✅ Debe decir: `✅ 1 planes encontrados`
   - ✅ NO debe decir: `ERROR en getMisTratamientos`

---

## 🔍 VERIFICACIÓN

**Backend devuelve:**
```json
{
  "odontologo_nombre": "Dr. Dr. Juan Pérez",  // ← String directo
  "items_simples": [
    {
      "servicio_nombre": "Consulta General",  // ← String directo
      "precio_total_formateado": "$50.00"  // ← Con símbolo $
    }
  ]
}
```

**Código NUEVO maneja:**
1. `json['odontologo_nombre']` → Captura el string
2. `json['servicio_nombre']` → Captura el string
3. `.replaceAll(r'$', '')` → Quita el símbolo $

---

## ⚠️ IMPORTANTE

- **NO uses `r` (hot reload)**, usa **`R` (hot restart)**
- **NO copies solo una parte**, copia **TODO EL MÉTODO**
- **Verifica que no haya errores de sintaxis** (paréntesis, comas)

---

## ✅ RESULTADO ESPERADO

Después de aplicar los cambios:

```
I/flutter: Response status: 200
I/flutter: ✅ 1 planes encontrados
I/flutter: Planes results: 1
```

✅ **La pantalla de tratamientos debe cargar sin errores**

---

## 🆘 SI SIGUE FALLANDO

1. **Copia TODO el código de los modelos** desde la guía 09 actualizada
2. **Borra el archivo** `tratamiento.dart` actual
3. **Crea uno nuevo** con el código de la guía
4. **Haz Hot Restart** con `R`

---

**Archivo generado el:** 23/11/2025 15:32:26
**Guía de referencia:** `guia_desarrollo/paciente_flutter/09_tratamientos.md`
