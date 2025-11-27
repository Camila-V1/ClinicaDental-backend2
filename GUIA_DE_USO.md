# 🚀 GUÍA RÁPIDA - BORRAR Y REPOBLAR DATOS

## 📊 LIMPIAR Y REPOBLAR BASE DE DATOS

### Paso 1: Limpiar Datos

```powershell
# Limpiar todos los datos del tenant
python limpiar_tenant.py
python limpiar_y_repoblar.py
# Cuando pregunte, escribir: SI
```

### Paso 2: Repoblar Datos

```powershell
# Poblar toda la base de datos
python scripts_poblacion/poblar_todo.py
```

### Paso 3: Verificar

```powershell
# Iniciar servidor
python manage.py runserver

# Acceder a:
# http://clinicademo1.localhost:8000/admin/
# Usuario: admin@clinicademo1.com
# Password: admin123
```

---

## 📝 DATOS QUE SE CREAN

- **6 Usuarios:** 1 admin, 2 odontólogos, 3 pacientes
- **20 Servicios:** Limpieza, obturaciones, endodoncia, etc.
- **35+ Insumos:** Anestésicos, instrumental, materiales
- **~38 Citas:** 15 atendidas, 20 futuras, 3 canceladas
- **Historiales Clínicos:** 1 por paciente con episodios
- **20 Pagos:** 15 completados, 5 pendientes

---

## 🔐 CREDENCIALES

```
Admin:
  Email: admin@clinicademo1.com
  Password: admin123

Odontólogo:
  Email: odontologo@clinica-demo.com
  Password: odontologo123

Paciente:
  Email: paciente1@test.com
  Password: paciente123
```
