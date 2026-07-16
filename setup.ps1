# CSM-WA Setup Script (Windows PowerShell)
# Instala dependencias y prepara el entorno para ejecutar la herramienta.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CSM-WA - Work Around Search Tool" -ForegroundColor Cyan
Write-Host "  Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = $null

foreach ($cmd in @("python", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $version -match "Python") {
            $pythonCmd = $cmd
            Write-Host "  OK: $version" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "  Python no encontrado. Instalando via winget..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        $pythonCmd = "python"
        Write-Host "  Python instalado correctamente." -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: No se pudo instalar Python." -ForegroundColor Red
        Write-Host "  Descarga manualmente desde: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
}

# Crear entorno virtual
Write-Host "[2/4] Creando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
    Write-Host "  Entorno virtual creado en ./venv" -ForegroundColor Green
} else {
    Write-Host "  Entorno virtual ya existe." -ForegroundColor Green
}

# Activar e instalar dependencias
Write-Host "[3/4] Instalando dependencias..." -ForegroundColor Yellow
$pip = Join-Path $ProjectRoot "venv\Scripts\pip.exe"
& $pip install --upgrade pip --quiet
& $pip install -r requirements.txt --quiet
Write-Host "  Dependencias instaladas." -ForegroundColor Green

# Crear directorio de datos si no existe
Write-Host "[4/4] Verificando estructura de datos..." -ForegroundColor Yellow
$dataDir = Join-Path $ProjectRoot "data\workarounds"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}
Write-Host "  Directorio data/workarounds/ listo." -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar la herramienta ejecuta:" -ForegroundColor White
Write-Host "  .\start.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "O manualmente:" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Abre en el navegador: http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
