# 🔐 CREDENCIALES DEL SISTEMA

## 🌐 URLS

```
Backend:  https://clinica-dental-backend.onrender.com
Frontend: https://clinicademo1.dentaabcxy.store
Dominio:  clinicademo1.dentaabcxy.store
```

---

## 👤 USUARIOS DE PRUEBA

### 👨‍💼 Administrador

```
Email:    admin@clinicademo1.com
Password: admin123
Rol:      ADMIN
```

### 🦷 Odontólogos

**Odontólogo 1:**
```
Email:    odontologo@clinica-demo.com
Password: odontologo123
Rol:      ODONTOLOGO
Nombre:   Dr. Carlos Rodríguez
```

**Odontólogo 2:**
```
Email:    dra.lopez@clinica-demo.com
Password: odontologo123
Rol:      ODONTOLOGO
Nombre:   Dra. María López
```

### 🧑‍⚕️ Pacientes

**Paciente 1:**
```
Email:    paciente1@test.com
Password: paciente123
Rol:      PACIENTE
Nombre:   María García
```

**Paciente 2:**
```
Email:    paciente2@test.com
Password: paciente123
Rol:      PACIENTE
Nombre:   Juan Pérez
```

**Paciente 3:**
```
Email:    paciente3@test.com
Password: paciente123
Rol:      PACIENTE
Nombre:   Laura Sánchez
```

---

## 🏥 INFORMACIÓN DEL TENANT

```
Clínica:  Clínica Demo
RUC:      1234567890001
Schema:   clinica_demo
Dominio:  clinicademo1.dentaabcxy.store
Plan:     GRATUITO
Estado:   ACTIVO
```

---

## 📊 DATOS DE PRUEBA

- **6 Usuarios:** 1 admin, 2 odontólogos, 3 pacientes
- **20 Servicios:** 7 categorías (Odontología General, Endodoncia, etc.)
- **30 Insumos:** 8 categorías (Anestésicos, Instrumental, etc.)
- **40 Citas:** 16 atendidas, 15 confirmadas, 6 pendientes, 3 canceladas
- **3 Historiales Clínicos:** Con episodios y odontogramas
- **20 Pagos:** 15 completados (Bs. 620.00), 5 pendientes (Bs. 180.00)

---

## 🔄 RESETEAR DATOS

```powershell
# 1. Limpiar datos
python limpiar_tenant.py

# 2. Repoblar datos
python scripts_poblacion/poblar_todo.py
```

---

## 🚀 ACCESO RÁPIDO

**Admin Panel:**
```
https://clinica-dental-backend.onrender.com/admin/
Email: admin@clinicademo1.com
Pass:  admin123
```

**API Tenant:**
```
https://clinicademo1.dentaabcxy.store/api/
```

**API Public:**
```
https://clinica-dental-backend.onrender.com/api/public/
```
