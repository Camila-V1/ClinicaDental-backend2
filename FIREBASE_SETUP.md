# 🔥 CONFIGURACIÓN DE FIREBASE PARA NOTIFICACIONES PUSH

## 📋 ARCHIVOS DE CREDENCIALES

Tienes 2 archivos JSON de Firebase en la raíz del proyecto:

### 1️⃣ `google-services (3).json` 
**Para:** Frontend (React Native / Flutter)
**Ubicación:** Copia a tu proyecto móvil en `android/app/google-services.json`
**Contiene:**
- API Key: `AIzaSyB9qQjVFTKfNiPn_P6iYUDje9dyWT0rloY`
- Project ID: `psicoadmin-94485`
- App IDs para Android

### 2️⃣ `psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json`
**Para:** Backend (Django)
**Contiene:** Credenciales de servicio para enviar notificaciones push
**IMPORTANTE:** Este archivo NO debe subirse a GitHub (ya está en .gitignore)

---

## 🖥️ CONFIGURACIÓN EN LOCAL (Desarrollo)

### Opción 1: Usar archivo JSON directamente (más fácil)

El archivo ya está en la raíz del proyecto. El código lo detecta automáticamente:

```python
# valoraciones/firebase_service.py línea 22
firebase_cred_path = Path(settings.BASE_DIR) / 'psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json'
```

✅ **No necesitas hacer nada más en local**

### Opción 2: Usar variable de entorno

1. Abre el archivo JSON
2. Copia TODO su contenido (desde `{` hasta `}`)
3. Agrégalo a tu `.env`:

```env
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"psicoadmin-94485",...todo el JSON...}
```

---

## ☁️ CONFIGURACIÓN EN RENDER (Producción)

### Paso 1: Copiar credenciales

1. Abre el archivo: `psicoadmin-94485-firebase-adminsdk-fbsvc-3581d8f111.json`
2. Selecciona TODO el contenido (Ctrl+A)
3. Copia (Ctrl+C)

### Paso 2: Agregar a Render

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio: `clinica-dental-backend`
3. Click en **"Environment"** (menú izquierdo)
4. Click en **"Add Environment Variable"**
5. Configura:
   ```
   Key:   FIREBASE_CREDENTIALS_JSON
   Value: [PEGA TODO EL JSON AQUÍ]
   ```
6. Click en **"Save Changes"**

⚠️ **IMPORTANTE:** El valor debe ser el JSON COMPLETO en una sola línea, incluyendo las llaves `{}`

### Paso 3: Verificar

Render reiniciará automáticamente. Busca en los logs:

```
✅ Firebase Admin SDK inicializado desde variable de entorno
```

Si ves esto, está funcionando:
```
⚠️ Archivo de credenciales Firebase no encontrado
```

---

## 🧪 PROBAR QUE FUNCIONA

### En Local:

```bash
python manage.py shell
```

```python
from valoraciones.firebase_service import FirebaseNotificationService

# Debería mostrar: ✅ Firebase Admin SDK inicializado
```

### En Producción (Render):

Revisa los logs al iniciar:
```
https://dashboard.render.com/web/[tu-servicio]/logs
```

Busca: `✅ Firebase Admin SDK inicializado`

---

## 📝 RESUMEN DE VARIABLES DE ENTORNO

### Para desarrollo local (`.env`):
```env
# Opcional - solo si no usas el archivo JSON directamente
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
```

### Para producción (Render Dashboard > Environment):
```
FIREBASE_CREDENTIALS_JSON = [TODO EL JSON]
```

---

## 🔐 SEGURIDAD

✅ **SÍ hacer:**
- Mantener el archivo JSON en local (está en .gitignore)
- Usar variable de entorno en producción
- Limitar acceso al dashboard de Render

❌ **NO hacer:**
- Subir el archivo JSON a GitHub
- Compartir las credenciales públicamente
- Hardcodear las credenciales en el código

---

## 🆘 TROUBLESHOOTING

### Error: "Firebase not initialized"
**Causa:** Variable de entorno no configurada
**Solución:** Verifica que `FIREBASE_CREDENTIALS_JSON` exista en Render

### Error: "Invalid JSON"
**Causa:** El JSON está mal formateado
**Solución:** Asegúrate de copiar TODO el archivo, incluyendo las llaves

### Error: "Permission denied"
**Causa:** El service account no tiene permisos
**Solución:** Verifica en Firebase Console que el service account tiene rol "Editor"

---

## 📱 PRÓXIMO PASO: CONFIGURAR FRONTEND

Una vez que el backend esté funcionando, ve a:
- `GUIA_SISTEMA_VALORACIONES.md` → Sección "PARTE 2: CONFIGURAR REACT NATIVE"

Necesitarás el archivo `google-services (3).json` para el frontend.
