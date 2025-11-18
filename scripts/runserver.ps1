# Runserver helper — activates the project .venv and runs manage.py
# Usage (PowerShell):
#    .\scripts\runserver.ps1

$venvPath = Join-Path $PSScriptRoot '..\.venv\Scripts\Activate.ps1'
if (Test-Path $venvPath) {
    Write-Host "Activating virtualenv at .venv..."
    . $venvPath
} else {
    Write-Warning "Activate script not found at $venvPath — ensure your venv is at .venv or modify this script."
}

# Use the venv's python executable explicitly to avoid the py launcher selecting system Python
$pythonExe = Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python executable not found at $pythonExe"
    exit 1
}

Write-Host "Starting Django dev server using: $pythonExe"
& $pythonExe "..\manage.py" runserver
