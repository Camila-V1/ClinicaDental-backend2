# 🔧 CORRECCIÓN DE REPORTES - BACKEND

**Fecha:** 22 de Noviembre 2025  
**Problemas identificados:**
1. Tendencia de citas NO envía `completadas` y `canceladas` separadas
2. Ocupación de odontólogos NO envía detalles completos (solo `etiqueta` y `valor`)

---

## 📊 PROBLEMA 1: Tendencia de Citas

### ❌ Código Actual (Incompleto)

**Archivo:** `reportes/views.py` - Línea 206

```python
def tendencia_citas(self, request):
    dias_a_revisar = int(request.query_params.get('dias', 15))
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=dias_a_revisar - 1)
    
    data = []
    fecha_actual = fecha_inicio
    
    # ❌ PROBLEMA: Solo cuenta citas totales (excluyendo canceladas)
    citas_por_fecha = dict(
        Cita.objects
        .filter(fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin)
        .exclude(estado='CANCELADA')  # ← Excluye canceladas, no las cuenta
        .values('fecha_hora__date')
        .annotate(cantidad=Count('id'))
        .values_list('fecha_hora__date', 'cantidad')
    )
    
    while fecha_actual <= fecha_fin:
        cantidad = citas_por_fecha.get(fecha_actual, 0)
        data.append({
            'fecha': fecha_actual,
            'cantidad': cantidad  # ← Solo envía total
        })
        fecha_actual += timedelta(days=1)
    
    serializer = ReporteTendenciaSerializer(data, many=True)
    return Response(serializer.data)
```

### ✅ Código Corregido (Completo)

```python
def tendencia_citas(self, request):
    """
    Reporte para el gráfico de "Tendencia de citas por día".
    
    GET /api/reportes/reportes/tendencia-citas/?dias=15
    
    Retorna:
    {
        'fecha': '2025-11-07',
        'cantidad': 5,        # Total de citas del día
        'completadas': 3,     # Citas completadas
        'canceladas': 1       # Citas canceladas
    }
    """
    dias_a_revisar = int(request.query_params.get('dias', 15))
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=dias_a_revisar - 1)
    
    data = []
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        # ✅ SOLUCIÓN: Consultar TODAS las citas por estado
        citas_del_dia = Cita.objects.filter(
            fecha_hora__date=fecha_actual
        )
        
        total = citas_del_dia.count()
        completadas = citas_del_dia.filter(estado='COMPLETADA').count()
        canceladas = citas_del_dia.filter(estado='CANCELADA').count()
        
        data.append({
            'fecha': fecha_actual,
            'cantidad': total,              # Total de citas
            'completadas': completadas,     # ✅ Ahora envía completadas
            'canceladas': canceladas        # ✅ Ahora envía canceladas
        })
        
        fecha_actual += timedelta(days=1)
    
    serializer = ReporteTendenciaSerializer(data, many=True)
    return Response(serializer.data)
```

---

## 👨‍⚕️ PROBLEMA 2: Ocupación de Odontólogos

### ❌ Código Actual (Incompleto)

**Archivo:** `reportes/views.py` - Línea 504

```python
def ocupacion_odontologos(self, request):
    # ... código de fechas ...
    
    odontologos = PerfilOdontologo.objects.filter(
        usuario__is_active=True
    ).select_related('usuario')
    
    data = []
    
    for odontologo in odontologos:
        total_citas = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__year=anio,
            fecha_hora__month=mes
        ).count()
        
        citas_efectivas = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__year=anio,
            fecha_hora__month=mes,
            estado__in=['CONFIRMADA', 'COMPLETADA']
        ).count()
        
        if total_citas > 0:
            tasa_ocupacion = round((citas_efectivas / total_citas * 100), 2)
        else:
            tasa_ocupacion = 0.0
        
        # ❌ PROBLEMA: Solo envía etiqueta y valor genérico
        data.append({
            'etiqueta': odontologo.usuario.full_name,
            'valor': float(tasa_ocupacion)
        })
    
    data.sort(key=lambda x: x['valor'], reverse=True)
    
    serializer = ReporteSimpleSerializer(data, many=True)
    return Response(serializer.data)
```

### ✅ Código Corregido (Completo)

```python
def ocupacion_odontologos(self, request):
    """
    Tasa de ocupación por odontólogo con detalles completos.
    
    GET /api/reportes/reportes/ocupacion-odontologos/?mes=2025-11
    
    Retorna:
    {
        'usuario_id': 353,
        'nombre_completo': 'Dr. Juan Pérez',
        'total_citas': 7,
        'citas_completadas': 5,
        'citas_canceladas': 1,
        'horas_ocupadas': 14,
        'tasa_ocupacion': '71.43',
        'pacientes_atendidos': 5
    }
    """
    mes_param = request.query_params.get('mes')
    hoy = timezone.now().date()
    
    if mes_param:
        try:
            anio, mes = map(int, mes_param.split('-'))
        except ValueError:
            return Response(
                {'error': 'Formato de mes inválido. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        anio, mes = hoy.year, hoy.month
    
    # Obtener odontólogos activos
    odontologos = PerfilOdontologo.objects.filter(
        usuario__is_active=True
    ).select_related('usuario')
    
    data = []
    
    for odontologo in odontologos:
        # Base de citas del mes
        citas_mes = Cita.objects.filter(
            odontologo=odontologo,
            fecha_hora__year=anio,
            fecha_hora__month=mes
        )
        
        # ✅ SOLUCIÓN: Contar por estado
        total_citas = citas_mes.count()
        citas_completadas = citas_mes.filter(estado='COMPLETADA').count()
        citas_canceladas = citas_mes.filter(estado='CANCELADA').count()
        
        # Calcular horas ocupadas (asumiendo 2 horas por cita completada)
        horas_ocupadas = citas_completadas * 2
        
        # Pacientes únicos atendidos
        pacientes_atendidos = citas_mes.filter(
            estado='COMPLETADA'
        ).values('paciente').distinct().count()
        
        # Calcular tasa de ocupación
        if total_citas > 0:
            tasa_ocupacion = round((citas_completadas / total_citas * 100), 2)
        else:
            tasa_ocupacion = 0.0
        
        # ✅ SOLUCIÓN: Enviar estructura completa
        data.append({
            'usuario_id': odontologo.usuario.id,              # ✅ ID correcto
            'nombre_completo': odontologo.usuario.full_name,  # ✅ Nombre completo
            'total_citas': total_citas,                       # ✅ Total de citas
            'citas_completadas': citas_completadas,           # ✅ Completadas
            'citas_canceladas': citas_canceladas,             # ✅ Canceladas
            'horas_ocupadas': horas_ocupadas,                 # ✅ Horas trabajadas
            'tasa_ocupacion': str(tasa_ocupacion),            # ✅ Porcentaje
            'pacientes_atendidos': pacientes_atendidos        # ✅ Pacientes únicos
        })
    
    # Ordenar por tasa de ocupación descendente
    data.sort(key=lambda x: float(x['tasa_ocupacion']), reverse=True)
    
    # ✅ NO usar serializer genérico, retornar directamente
    return Response(data)
```

---

## 📝 INSTRUCCIONES DE APLICACIÓN

### Paso 1: Abrir el archivo

```bash
# En tu editor de VS Code, abre:
reportes/views.py
```

### Paso 2: Reemplazar función `tendencia_citas`

**Busca la línea 206** y reemplaza toda la función `tendencia_citas` con el código corregido de arriba.

**Antes (líneas 206-243):**
```python
def tendencia_citas(self, request):
    # ... código antiguo ...
    data.append({
        'fecha': fecha_actual,
        'cantidad': cantidad  # ← Solo esto
    })
```

**Después:**
```python
def tendencia_citas(self, request):
    # ... código corregido ...
    data.append({
        'fecha': fecha_actual,
        'cantidad': total,
        'completadas': completadas,  # ← Ahora incluye esto
        'canceladas': canceladas     # ← Y esto
    })
```

---

### Paso 3: Reemplazar función `ocupacion_odontologos`

**Busca la línea 504** y reemplaza toda la función `ocupacion_odontologos` con el código corregido de arriba.

**Antes (líneas 504-565):**
```python
def ocupacion_odontologos(self, request):
    # ... código antiguo ...
    data.append({
        'etiqueta': odontologo.usuario.full_name,
        'valor': float(tasa_ocupacion)  # ← Solo 2 campos
    })
    
    serializer = ReporteSimpleSerializer(data, many=True)
    return Response(serializer.data)
```

**Después:**
```python
def ocupacion_odontologos(self, request):
    # ... código corregido ...
    data.append({
        'usuario_id': odontologo.usuario.id,
        'nombre_completo': odontologo.usuario.full_name,
        'total_citas': total_citas,
        'citas_completadas': citas_completadas,
        'citas_canceladas': citas_canceladas,
        'horas_ocupadas': horas_ocupadas,
        'tasa_ocupacion': str(tasa_ocupacion),
        'pacientes_atendidos': pacientes_atendidos  # ← 8 campos completos
    })
    
    return Response(data)  # ← Sin serializer
```

---

### Paso 4: Probar localmente

```bash
# Correr servidor de desarrollo
python manage.py runserver
```

**Probar endpoints:**

```bash
# Tendencia (debe mostrar completadas y canceladas)
curl http://localhost:8000/api/reportes/reportes/tendencia-citas/?dias=30

# Ocupación (debe mostrar 8 campos)
curl http://localhost:8000/api/reportes/reportes/ocupacion-odontologos/
```

---

### Paso 5: Desplegar

```bash
git add reportes/views.py
git commit -m "Fix: Agregar completadas/canceladas en tendencia y detalles completos en ocupación"
git push origin main
```

Render desplegará automáticamente en 2-3 minutos.

---

## ✅ RESULTADO ESPERADO

### Tendencia de Citas

**Antes:**
```json
[
  {"fecha": "2025-11-07", "cantidad": 5}
]
```

**Después:**
```json
[
  {
    "fecha": "2025-11-07",
    "cantidad": 5,
    "completadas": 3,
    "canceladas": 1
  }
]
```

---

### Ocupación Odontólogos

**Antes:**
```json
[
  {"etiqueta": "Dr. Juan Pérez", "valor": 71.43}
]
```

**Después:**
```json
[
  {
    "usuario_id": 353,
    "nombre_completo": "Dr. Juan Pérez",
    "total_citas": 7,
    "citas_completadas": 5,
    "citas_canceladas": 1,
    "horas_ocupadas": 10,
    "tasa_ocupacion": "71.43",
    "pacientes_atendidos": 5
  }
]
```

---

## 🎯 VERIFICACIÓN

Después de aplicar los cambios:

1. ✅ Gráfico de tendencia mostrará 3 líneas (total, completadas, canceladas)
2. ✅ Card de ocupación mostrará todos los detalles del odontólogo
3. ✅ Eficiencia mostrará "5/7" (completadas/total)

---

**¿Necesitas que aplique estos cambios directamente en el código?** Dime "sí" y los implemento ahora mismo.
