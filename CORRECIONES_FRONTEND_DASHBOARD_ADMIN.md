# 🔧 Correcciones Necesarias - Dashboard Administrador

**Fecha:** 20 de Noviembre, 2025  
**Problema:** Error 500 en dashboard-kpis y TypeError en tasa_ocupacion  
**Estado Backend:** ✅ Corregido (commits `0bb9fde` y `611e0f5`)  
**Estado Frontend:** ⚠️ Requiere correcciones

---

## 🐛 Problemas Identificados

### 1. ❌ Error 500 en `/api/reportes/reportes/dashboard-kpis/`

**Causa Raíz (Backend):** Faltaba crear perfiles de `PerfilPaciente` y `PerfilOdontologo`

**Solución Backend:** ✅ **YA CORREGIDO**
- Commit `611e0f5`: Modificado `crear_usuarios_prueba.py` para crear perfiles
- Script ahora crea automáticamente:
  - `PerfilOdontologo` con especialidad y número de registro
  - `PerfilPaciente` con datos personales completos
- Deploy en Render: ✅ En progreso (ETA: 2-3 minutos)

**Acción Frontend:** 
- ⏳ **Esperar** que Render complete el deployment
- 🔄 **Refrescar** la página después de 5 minutos
- ✅ El endpoint debería responder correctamente

---

### 2. ❌ TypeError: `e.tasa_ocupacion.toFixed is not a function`

**Causa Raíz (Backend):** El endpoint devolvía `int` en lugar de `float`

**Solución Backend:** ✅ **YA CORREGIDO**
- Commit `0bb9fde`: Modificado `reportes/views.py`
- Ahora `tasa_ocupacion` siempre retorna `float`:
  ```python
  if total_citas > 0:
      tasa_ocupacion = round((citas_efectivas / total_citas * 100), 2)
  else:
      tasa_ocupacion = 0.0
  
  data.append({
      'etiqueta': odontologo.usuario.full_name,
      'valor': float(tasa_ocupacion)  # Siempre float
  })
  ```

**Acción Frontend:**
- ⏳ **Esperar** deployment
- ✅ El TypeError debería desaparecer automáticamente

---

### 3. ⚠️ Error en Guía del Dashboard Admin

**Problema:** La guía `01_dashboard_admin.md` tiene un endpoint incorrecto

**Línea problemática:**
```typescript
// ❌ INCORRECTO (en la guía)
async getStockBajo() {
  const { data } = await api.get('/inventario/insumos/', {
    params: { stock_bajo: true, page_size: 10 }
  });
  return data;
}
```

**Corrección necesaria:**
```typescript
// ✅ CORRECTO
async getStockBajo() {
  const { data } = await api.get('/inventario/insumos/bajo_stock/', {
    params: { page_size: 10 }
  });
  return data;
}
```

**Razón:** El backend usa una **acción custom** `/bajo_stock/`, no un parámetro de query.

---

## 📝 Checklist de Correcciones para Frontend

### ✅ Correcciones Automáticas (Solo Esperar)
- [ ] Esperar 5 minutos a que Render complete el deployment
- [ ] Refrescar la página del frontend
- [ ] Verificar que desaparezca el error 500 en `dashboard-kpis`
- [ ] Verificar que desaparezca el TypeError de `tasa_ocupacion`

### 🔧 Correcciones Manuales Requeridas

#### Archivo: `src/services/admin/dashboardService.ts`

**Cambio 1 - Método getStockBajo:**
```diff
// Línea ~368 en la guía (aproximadamente)
async getStockBajo() {
-  const { data } = await api.get('/inventario/insumos/', {
-    params: { stock_bajo: true, page_size: 10 }
+  const { data } = await api.get('/inventario/insumos/bajo_stock/', {
+    params: { page_size: 10 }
  });
  return data;
}
```

#### Archivo: `src/pages/admin/Dashboard.tsx`

**Verificar manejo de errores:**
```typescript
const { data: kpis, isLoading: loadingKpis, error } = useQuery({
  queryKey: ['dashboard-kpis'],
  queryFn: dashboardService.getKPIs,
  refetchInterval: 30000,
  retry: 3, // ✅ Reintentar 3 veces
  retryDelay: 1000, // ✅ Esperar 1 segundo entre reintentos
});

// ✅ Mostrar error si persiste
if (error) {
  console.error('Error cargando KPIs:', error);
  return <div>Error cargando dashboard. Intente más tarde.</div>;
}
```

---

## 🔍 Verificación del Fix

### Prueba 1: Dashboard KPIs
```bash
# En el navegador, después del deploy
# Debería ver en consola:
✅ authService: Tokens recibidos
✅ authService: Usuario obtenido: admin@clinica-demo.com
✅ AuthContext: Login exitoso
🔍 DashboardPage - userType: ADMIN

# NO debería ver:
❌ GET .../dashboard-kpis/ 500 (Internal Server Error)
```

### Prueba 2: Ocupación Odontólogos
```bash
# El componente de gráfico debería renderizar sin errores
# NO debería ver:
❌ TypeError: e.tasa_ocupacion.toFixed is not a function
```

### Prueba 3: Stock Bajo
```bash
# Después de corregir el endpoint
GET /api/inventario/insumos/bajo_stock/?page_size=10

# Debería retornar:
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

---

## 📊 Endpoints Correctos del Backend

### Reportes
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/reportes/reportes/dashboard-kpis/` | GET | ✅ KPIs principales |
| `/api/reportes/reportes/tendencia-citas/?dias=15` | GET | ✅ Gráfico de tendencia |
| `/api/reportes/reportes/top-procedimientos/?limite=5` | GET | ✅ Top procedimientos |
| `/api/reportes/reportes/estadisticas-generales/` | GET | ✅ Estadísticas completas |
| `/api/reportes/reportes/ocupacion-odontologos/?mes=2025-11` | GET | ✅ Ocupación por doctor |
| `/api/reportes/bitacora/?page=1&page_size=10` | GET | ✅ Actividad reciente |

### Inventario
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/inventario/insumos/` | GET | Listar todos los insumos |
| `/api/inventario/insumos/bajo_stock/` | GET | ⚠️ **Insumos con stock bajo** (CORREGIR) |
| `/api/inventario/insumos/{id}/` | GET | Detalle de un insumo |
| `/api/inventario/insumos/{id}/ajustar_stock/` | POST | Ajustar stock manualmente |

---

## 🚀 Pasos para Resolución Final

### Para el Equipo Frontend:

1. **Esperar Deployment (5 minutos)**
   - No hacer cambios aún
   - Dejar que Render termine de desplegar

2. **Probar sin cambios**
   - Refrescar navegador
   - Hacer login nuevamente
   - Verificar si los errores 500 y TypeError desaparecieron

3. **Si los errores persisten:**
   - Revisar consola del navegador
   - Compartir logs completos
   - Verificar que la URL del backend sea correcta

4. **Aplicar corrección del endpoint de inventario:**
   - Modificar `dashboardService.ts`
   - Cambiar `/inventario/insumos/?stock_bajo=true` → `/inventario/insumos/bajo_stock/`

5. **Testing final:**
   - Login con `admin@clinica-demo.com` / `admin123`
   - Verificar que todos los componentes del dashboard carguen
   - Confirmar que no hay errores en consola

---

## 📞 Soporte

### Si el error 500 persiste después de 10 minutos:

1. **Verificar estado del deployment en Render:**
   - Ir a: https://dashboard.render.com
   - Revisar logs del último deploy

2. **Probar endpoint directamente:**
   ```bash
   # PowerShell
   $token = (Invoke-RestMethod -Uri "https://clinica-dental-backend.onrender.com/api/token/" -Method POST -ContentType "application/json" -Body '{"email": "admin@clinica-demo.com", "password": "admin123"}').access
   
   Invoke-RestMethod -Uri "https://clinica-dental-backend.onrender.com/api/reportes/reportes/dashboard-kpis/" -Method GET -Headers @{Authorization="Bearer $token"}
   ```

3. **Revisar respuesta:**
   - Si retorna 200: ✅ Backend funciona, problema en frontend
   - Si retorna 500: ❌ Problema en backend, reportar logs

---

## ✅ Resumen de Cambios Backend Aplicados

| Commit | Archivo | Cambio |
|--------|---------|--------|
| `0bb9fde` | `reportes/views.py` | Corregir cálculo de `saldo_pendiente` y `tasa_ocupacion` |
| `611e0f5` | `crear_usuarios_prueba.py` | Crear `PerfilOdontologo` y `PerfilPaciente` automáticamente |

**Estado:** ✅ Ambos commits pusheados y desplegándose en Render  
**ETA:** ⏳ 2-3 minutos desde este documento

---

**Última actualización:** 20/11/2025 12:20 PM  
**Preparado por:** GitHub Copilot
