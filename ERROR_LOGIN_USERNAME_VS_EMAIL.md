# 🔧 ERROR DE LOGIN - USERNAME vs EMAIL

**Fecha:** 15 de Noviembre, 2025  
**Error:** "No active account found with the given credentials"

---

## 🐛 PROBLEMA IDENTIFICADO

### **Error en Consola:**
```
❌ Error en login: No active account found with the given credentials
```

### **Causa Raíz:**
El **frontend está enviando EMAIL** pero el **backend espera USERNAME**

```typescript
// ❌ Frontend está enviando:
{
  "username": "juan.perez@email.com",  // ← Esto es un EMAIL
  "password": "paciente123"
}

// ✅ Backend necesita:
{
  "username": "juan_perez",  // ← USERNAME real
  "password": "paciente123"
}
```

---

## ✅ SOLUCIÓN

### **Opción 1: Cambiar el frontend para pedir USERNAME**

```typescript
// LoginForm.tsx

export function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',  // ✅ Cambiar de "email" a "username"
    password: ''
  });

  return (
    <form onSubmit={handleSubmit}>
      {/* ✅ Input de USERNAME */}
      <input
        type="text"
        name="username"
        placeholder="Usuario (ej: juan_perez)"
        value={formData.username}
        onChange={handleChange}
      />
      
      <input
        type="password"
        name="password"
        placeholder="Contraseña"
        value={formData.password}
        onChange={handleChange}
      />
      
      <button type="submit">Iniciar Sesión</button>
    </form>
  );
}
```

### **Opción 2: Modificar el backend para aceptar EMAIL**

Si prefieres que el login sea con email, necesitas crear un serializer custom:

```python
# usuarios/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer que permite login con email además de username
    """
    username_field = 'email_or_username'
    
    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        
        # Intentar encontrar por email
        try:
            user = User.objects.get(email=email_or_username)
            attrs['username'] = user.username
        except User.DoesNotExist:
            # Si no existe por email, asumir que es username
            attrs['username'] = email_or_username
        
        # Remover el campo custom antes de llamar al padre
        attrs.pop('email_or_username', None)
        
        return super().validate(attrs)
```

```python
# usuarios/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

```python
# core/urls_tenant.py

from usuarios.views import CustomTokenObtainPairView

urlpatterns = [
    # Reemplazar el endpoint de token
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # ... resto de URLs
]
```

---

## 🎯 RECOMENDACIÓN: Usar USERNAME (Opción 1)

**Es más simple y estándar:**

1. El frontend pide "Usuario" en lugar de "Email"
2. El usuario ingresa: `juan_perez`
3. El backend lo reconoce inmediatamente

---

## 📋 CREDENCIALES CORRECTAS PARA PRUEBAS

### **Usar USERNAME, NO EMAIL**

```bash
# ✅ CORRECTO
POST http://clinica-demo.localhost:8000/api/token/
{
  "username": "juan_perez",  ← USERNAME
  "password": "paciente123"
}

# ❌ INCORRECTO (actual del frontend)
POST http://clinica-demo.localhost:8000/api/token/
{
  "username": "juan.perez@email.com",  ← EMAIL (no funciona)
  "password": "paciente123"
}
```

---

## 🧪 PRUEBA RÁPIDA

### **Con PowerShell:**

```powershell
# ✅ Test con USERNAME correcto
$body = @{
    username = "juan_perez"  # ← USERNAME
    password = "paciente123"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://clinica-demo.localhost:8000/api/token/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Resultado esperado:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📊 TABLA DE USUARIOS

| Nombre | Username (LOGIN) | Email (Información) | Password |
|--------|------------------|---------------------|----------|
| Juan Pérez | `juan_perez` ✅ | juan.perez@email.com | paciente123 |
| María González | `maria_gonzalez` ✅ | maria.gonzalez@email.com | paciente123 |
| Pedro Rodríguez | `pedro_rodriguez` ✅ | pedro.rodriguez@email.com | paciente123 |
| Admin | `admin_clinica` ✅ | admin@clinica1.com | admin123 |
| Odontólogo | `odontologo1` ✅ | odontologo@clinica1.com | odonto123 |
| Recepcionista | `recepcionista1` ✅ | recepcion@clinica1.com | recep123 |

---

## 🔍 VERIFICAR EN EL FRONTEND

### **Buscar en el código del frontend:**

```typescript
// LoginForm.tsx o similar

// ❌ Si dice esto:
const [email, setEmail] = useState('');
// O
<input type="email" name="email" .../>

// ✅ Debe decir:
const [username, setUsername] = useState('');
// Y
<input type="text" name="username" placeholder="Usuario" .../>
```

### **authService.ts debe enviar:**

```typescript
// ✅ CORRECTO
export const login = async (username: string, password: string) => {
  const response = await apiClient.post('/api/token/', {
    username,  // ← Campo "username"
    password
  });
  return response.data;
};

// ❌ INCORRECTO
export const login = async (email: string, password: string) => {
  const response = await apiClient.post('/api/token/', {
    username: email,  // ← Está enviando email en campo username
    password
  });
  return response.data;
};
```

---

## ✅ SOLUCIÓN INMEDIATA

**En el formulario de login del frontend, ingresar:**

```
Usuario: juan_perez
Contraseña: paciente123
```

**NO ingresar:**
```
Usuario: juan.perez@email.com  ← ESTO NO FUNCIONA
```

---

## 🎯 RESUMEN

| Aspecto | Valor Correcto | Valor Incorrecto |
|---------|---------------|------------------|
| Campo del formulario | `username` (tipo text) | `email` (tipo email) |
| Valor a enviar | `juan_perez` | `juan.perez@email.com` |
| Placeholder | "Usuario" o "Nombre de usuario" | "Correo electrónico" |
| JSON al backend | `{"username": "juan_perez", ...}` | `{"username": "juan.perez@email.com", ...}` |

---

**📅 Última actualización:** 15 de Noviembre, 2025  
**🔧 Estado:** Error identificado - Frontend envía email en lugar de username
