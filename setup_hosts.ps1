# Script PowerShell para agregar entrada al archivo hosts
# DEBE EJECUTARSE COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$newEntry = "127.0.0.1   clinica-demo.localhost"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CONFIGURACIÓN DEL ARCHIVO HOSTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Verificar si el script se está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "❌ ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTRUCCIONES MANUALES:" -ForegroundColor Yellow
    Write-Host "========================" -ForegroundColor Yellow
    Write-Host "1. Abre el Bloc de notas como Administrador" -ForegroundColor White
    Write-Host "2. Abre el archivo: C:\Windows\System32\drivers\etc\hosts" -ForegroundColor White
    Write-Host "3. Agrega esta línea al final:" -ForegroundColor White
    Write-Host "   $newEntry" -ForegroundColor Green
    Write-Host "4. Guarda el archivo" -ForegroundColor White
    Write-Host ""
    Write-Host "O ejecuta este comando en PowerShell como Administrador:" -ForegroundColor Yellow
    Write-Host "   Add-Content -Path `"$hostsPath`" -Value `"$newEntry`"" -ForegroundColor Green
    Write-Host ""
    exit 1
}

# Leer el contenido actual del archivo hosts
$hostsContent = Get-Content $hostsPath

# Verificar si la entrada ya existe
$entryExists = $hostsContent | Where-Object { $_ -match "clinica-demo.localhost" }

if ($entryExists) {
    Write-Host ""
    Write-Host "✅ La entrada ya existe en el archivo hosts:" -ForegroundColor Green
    Write-Host "   $entryExists" -ForegroundColor Cyan
} else {
    # Agregar la nueva entrada
    try {
        Add-Content -Path $hostsPath -Value "`n# Django Multi-Tenant - Clinica Demo"
        Add-Content -Path $hostsPath -Value $newEntry
        Write-Host ""
        Write-Host "✅ Entrada agregada exitosamente al archivo hosts" -ForegroundColor Green
        Write-Host "   $newEntry" -ForegroundColor Cyan
    } catch {
        Write-Host ""
        Write-Host "❌ ERROR al modificar el archivo hosts: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Contenido actual relacionado con localhost:" -ForegroundColor Yellow
Get-Content $hostsPath | Where-Object { $_ -match "localhost" -or $_ -match "clinica" } | ForEach-Object {
    Write-Host "  $_" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASOS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Reinicia el servidor Django:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Green
Write-Host ""
Write-Host "2. Accede a los sitios:" -ForegroundColor White
Write-Host "   📍 Sitio Público:  http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "      Usuario: superadmin@sistema.com" -ForegroundColor Gray
Write-Host "      Password: superadmin123" -ForegroundColor Gray
Write-Host ""
Write-Host "   📍 Clínica Demo:   http://clinica-demo.localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "      Usuario: admin@clinica.com" -ForegroundColor Gray
Write-Host "      Password: 123456" -ForegroundColor Gray
Write-Host ""
