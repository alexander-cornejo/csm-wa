# CSM-WA Start Script (Windows PowerShell)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$venvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found. Run first: .\setup.ps1" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting CSM-WA at http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

& $venvPython app.py
