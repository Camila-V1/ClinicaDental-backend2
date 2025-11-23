# 🚨 Solución Cloudflare 403 - Apps Móviles

## Problema
```
Login response status: 403
<h1>403 Forbidden</h1>
<center>cloudflare</center>
```

**Causa:** Cloudflare está bloqueando las peticiones desde Flutter antes de que lleguen a Django.

---

## ✅ Solución 1: Desactivar Cloudflare en Render (RECOMENDADO)

### Pasos en Dashboard de Render:

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio: `clinica-dental-backend`
3. Ve a **Settings** → **Environment**
4. Busca o agrega la variable:
   ```
   CLOUDFLARE_PROTECTION = false
   ```
5. Guarda y **Manual Deploy** → **Deploy latest commit**

### O usa la URL directa de Render (sin Cloudflare):

En Flutter, cambia la baseUrl a:
```dart
const String baseUrl = 'https://clinica-dental-backend.onrender.com';
// A: https://clinica-dental-backend-XXXXX.onrender.com
//    (reemplaza XXXXX con tu ID de servicio de Render)
```

**Cómo encontrar la URL directa:**
- Dashboard Render → Tu servicio → **Settings** → **URL without Cloudflare**

---

## ✅ Solución 2: Modificar User-Agent en Flutter

Cambiar el User-Agent para que Cloudflare no lo detecte como bot:

```dart
// En tu servicio de autenticación (auth_service.dart)
Future<Map<String, dynamic>> login(String email, String password, String tenant) async {
  final url = Uri.parse('$baseUrl/api/token/');
  
  final response = await http.post(
    url,
    headers: {
      'Host': '$tenant.localhost',
      'Content-Type': 'application/json',
      'User-Agent': 'ClinicaDentalApp/1.0 (Android; Mobile)', // ✅ Custom User-Agent
    },
    body: json.encode({
      'email': email,
      'password': password,
    }),
  );
  
  // ...resto del código
}
```

**Agregar a TODAS las peticiones:**
```dart
// En api_client.dart o donde configures http
Map<String, String> get headers => {
  'Content-Type': 'application/json',
  'User-Agent': 'ClinicaDentalApp/1.0 (Android; Mobile)', // ✅ Simula navegador móvil
  if (token != null) 'Authorization': 'Bearer $token',
  if (tenant != null) 'Host': '$tenant.localhost',
};
```

---

## ✅ Solución 3: Backend Local (Para desarrollo)

### En tu PC (Windows):

```powershell
# 1. Iniciar servidor Django
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\PAUL PROYECTO\ClinicaDental-backend2"
python manage.py runserver 0.0.0.0:8000

# 2. Permitir en Firewall (ejecutar como Administrador)
New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Obtener IP de tu PC:

```powershell
ipconfig
# Busca: IPv4 Address. . . . . . . : 192.168.X.X
```

### En Flutter:

```dart
// Cambiar baseUrl temporalmente
const String baseUrl = 'http://192.168.26.1:8000'; // ✅ Tu IP local

// Mantener headers normales
headers: {
  'Host': '$tenant.localhost',
  'Content-Type': 'application/json',
}
```

**Ventajas:**
- ✅ Bypass total de Cloudflare
- ✅ Debugging en tiempo real
- ✅ Sin límites de rate limiting

**Desventajas:**
- ❌ Solo funciona en la misma red WiFi
- ❌ Tu PC debe estar encendida

---

## 🎯 Recomendación Final

### Para Producción (App publicada):
- **Opción 1:** Desactivar Cloudflare o usar URL directa de Render
- **Opción 2:** Configurar Cloudflare para permitir tu app móvil

### Para Desarrollo (Testing):
- **Opción 3:** Backend local en tu PC (más rápido y sin limitaciones)

---

## 📝 Notas Importantes

### ¿Por qué el middleware no funcionó?

```
Flutter App → Cloudflare → ❌ BLOQUEADO AQUÍ (403)
                ↓
            Django nunca recibe la petición
                ↓
            Middleware nunca se ejecuta
```

El middleware solo funciona si la petición **llega a Django**, pero Cloudflare la bloquea antes.

### ¿Cómo funciona Cloudflare?

Cloudflare analiza:
- User-Agent: `Dart/3.x`, `Flutter`
- Patrones de peticiones automatizadas
- Headers sospechosos

Si detecta un bot, bloquea con 403 **antes** de reenviar a Render.

---

## 🔧 Siguiente Paso

**Elige UNA solución y aplícala:**

1. **Más fácil:** Backend local (Opción 3)
2. **Mejor para testing:** Desactivar Cloudflare (Opción 1)
3. **Requiere código:** Cambiar User-Agent (Opción 2)

Una vez aplicada, intenta login nuevamente:
- Email: `paciente1@test.com`
- Password: `password123`
- Clínica: `clinicademo1`
