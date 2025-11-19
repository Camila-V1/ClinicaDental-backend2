# ✅ CREDENCIALES REALES - TENANT CLINICA-DEMO

**Fecha:** 15 de Noviembre, 2025  
**Sistema:** Multi-Tenant - Django con EMAIL como username  
**Estado:** ✅ VERIFICADO EN BASE DE DATOS

---

## 🎯 INFORMACIÓN CRÍTICA

### ✅ **El sistema USA EMAIL para login**
```json
{
  "email": "paciente1@test.com",  ← Campo se llama "email", NO "username"
  "password": "password123"
}
```

### ✅ **Tenant correcto**
```
Subdomain: clinica-demo  (con guión -)
Schema: clinica_demo     (con guión bajo _)
URL: http://clinica-demo.localhost:8000/
```

---

## 👥 USUARIOS EXISTENTES EN CLINICA-DEMO

### 🦷 **PACIENTES**

#### **Paciente 1**
```json
{
  "email": "paciente1@test.com",
  "password": "password123"
}
```

#### **Paciente 2**
```json
{
  "email": "paciente2@test.com",
  "password": "password123"
}
```

#### **Paciente 3**
```json
{
  "email": "paciente3@test.com",
  "password": "password123"
}
```

#### **Paciente 4**
```json
{
  "email": "paciente4@test.com",
  "password": "password123"
}
```

#### **Paciente 5**
```json
{
  "email": "paciente5@test.com",
  "password": "password123"
}
```

---

### 👨‍⚕️ **ODONTÓLOGO**

```json
{
  "email": "odontologo@clinica-demo.com",
  "password": "password123"
}
```

---

## 🧪 PRUEBA INMEDIATA CON POWERSHELL

### **Test de Login con paciente1:**

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    email = "paciente1@test.com"    # ✅ Campo "email"
    password = "password123"
} | ConvertTo-Json

# ✅ URL CORRECTA (sin /public, sin /tenant)
Invoke-RestMethod `
    -Uri "http://clinica-demo.localhost:8000/api/token/" `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -Verbose
```

**Resultado esperado:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🔧 CONFIGURACIÓN FRONTEND

### **authService.ts - Login correcto:**

```typescript
// ✅ CORRECTO
export const login = async (email: string, password: string) => {
  const response = await apiClient.post('/api/token/', {
    email,      // ✅ Campo "email" (no username)
    password
  });
  
  return response.data;
};
```

### **LoginForm.tsx - Formulario correcto:**

```typescript
export function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',     // ✅ Campo "email"
    password: ''
  });

  return (
    <form onSubmit={handleSubmit}>
      {/* ✅ Input de EMAIL */}
      <input
        type="email"
        name="email"
        placeholder="Correo electrónico"
        value={formData.email}
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

---

## 📊 VERIFICACIÓN DEL MODELO

El modelo `Usuario` está configurado así:

```python
# usuarios/models.py

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # ✅ Email único
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    # ...

    USERNAME_FIELD = 'email'  # ✅ LOGIN CON EMAIL
    REQUIRED_FIELDS = ['nombre', 'apellido']
```

---

## 🎯 PRUEBA PASO A PASO

### **1. Verificar que el servidor esté corriendo:**
```powershell
# En una terminal
python manage.py runserver
```

### **2. Probar login desde PowerShell:**
```powershell
# Login con paciente1
$body = @{
    email = "paciente1@test.com"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://clinica-demo.localhost:8000/api/token/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### **3. Si funciona en PowerShell pero no en frontend:**

Revisar que el frontend envíe:
```typescript
// ✅ JSON CORRECTO
{
  "email": "paciente1@test.com",  // ← Debe decir "email"
  "password": "password123"
}

// ❌ JSON INCORRECTO
{
  "username": "paciente1@test.com",  // ← NO debe decir "username"
  "password": "password123"
}
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

### **En el Backend:**
- [x] Usuario existe: `paciente1@test.com` ✅
- [x] Password correcto: `password123` ✅
- [x] Usuario activo: `is_active=True` ✅
- [x] Tenant correcto: `clinica_demo` ✅
- [x] USERNAME_FIELD es 'email' ✅

### **En el Frontend:**
- [ ] URL correcta: `http://clinica-demo.localhost:8000/api/token/`
- [ ] Campo JSON es "email" (no "username")
- [ ] Valor es `paciente1@test.com`
- [ ] Password es `password123`
- [ ] Header `Content-Type: application/json`
- [ ] `withCredentials: true` en axios

---

## 🐛 ERRORES COMUNES Y SOLUCIONES

### **Error: "No active account found with the given credentials"**

**Posibles causas:**

#### 1️⃣ **Email incorrecto**
```
❌ Incorrecto: juan.perez@email.com  (no existe)
✅ Correcto:   paciente1@test.com    (existe)
```

#### 2️⃣ **Campo JSON incorrecto**
```javascript
// ❌ Incorrecto
{ "username": "paciente1@test.com", ... }

// ✅ Correcto
{ "email": "paciente1@test.com", ... }
```

#### 3️⃣ **Password incorrecto**
```
❌ Incorrecto: paciente123
✅ Correcto:   password123
```

#### 4️⃣ **Tenant incorrecto**
```
❌ URL: http://clinica1.localhost:8000/...
✅ URL: http://clinica-demo.localhost:8000/...
```

---

## 🔍 COMANDOS DE VERIFICACIÓN

### **Ver todos los usuarios del tenant:**

```powershell
python manage.py tenant_command shell --schema=clinica_demo -c "from usuarios.models import Usuario; [print(f'{u.email} | {u.tipo_usuario} | Activo: {u.is_active}') for u in Usuario.objects.all()]"
```

### **Ver si un usuario específico existe:**

```powershell
python manage.py tenant_command shell --schema=clinica_demo -c "from usuarios.models import Usuario; u = Usuario.objects.filter(email='paciente1@test.com').first(); print(f'Existe: {u is not None}') if u else print('NO EXISTE')"
```

### **Verificar password de un usuario:**

```powershell
python manage.py tenant_command shell --schema=clinica_demo -c "from usuarios.models import Usuario; u = Usuario.objects.get(email='paciente1@test.com'); print(f'Password válido: {u.check_password(\"password123\")}')"
```

---

## 📊 TABLA RESUMEN

| Email | Password | Tipo | Tenant | Estado |
|-------|----------|------|--------|--------|
| paciente1@test.com | password123 | PACIENTE | clinica-demo | ✅ Activo |
| paciente2@test.com | password123 | PACIENTE | clinica-demo | ✅ Activo |
| paciente3@test.com | password123 | PACIENTE | clinica-demo | ✅ Activo |
| paciente4@test.com | password123 | PACIENTE | clinica-demo | ✅ Activo |
| paciente5@test.com | password123 | PACIENTE | clinica-demo | ✅ Activo |
| odontologo@clinica-demo.com | password123 | ODONTOLOGO | clinica-demo | ✅ Activo |

---

## 🎯 SOLUCIÓN PARA EL FRONTEND

### **Cambio necesario en el código:**

```typescript
// ANTES (Incorrecto):
const handleLogin = async () => {
  await authService.login(
    formData.username,  // ❌ Enviando como "username"
    formData.password
  );
};

// DESPUÉS (Correcto):
const handleLogin = async () => {
  await authService.login(
    formData.email,     // ✅ Enviando como "email"
    formData.password
  );
};
```

### **authService debe enviar:**

```typescript
export const login = async (email: string, password: string) => {
  const response = await apiClient.post('/api/token/', {
    email,     // ✅ Clave "email"
    password
  });
  return response.data;
};
```

---

## ✅ PRUEBA FINAL

**En el formulario de login ingresar:**

```
Email: paciente1@test.com
Contraseña: password123
```

**Resultado esperado:**
- ✅ Login exitoso
- ✅ Tokens recibidos
- ✅ Redirección al dashboard

---

**📅 Última actualización:** 15 de Noviembre, 2025  
**🔧 Estado:** Credenciales verificadas en base de datos  
**✅ Listo para usar**
