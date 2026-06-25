<#
.SYNOPSIS
  Provisioniert die isolierte Windows-VM für den 4x-game-agent.
.DESCRIPTION
  Installiert Python, Android Platform-Tools (ADB) und die Projekt-Abhängigkeiten
  und prüft die ADB-Verbindung zum Android-Emulator. In einer Admin-PowerShell
  ausführen.  Setzt voraus, dass ein Android-Emulator (z. B. BlueStacks/LDPlayer/
  Android-Studio-AVD) bereits installiert ist und ADB-Debugging aktiviert wurde.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -EmulatorAddress 127.0.0.1:5555
#>
param(
    [string]$EmulatorAddress = "127.0.0.1:5555",
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Host "== 4x-game-agent: Windows-VM-Provisionierung ==" -ForegroundColor Cyan

# 1. Paketmanager (winget) prüfen
if (-not (Test-Command "winget")) {
    Write-Warning "winget nicht gefunden. Bitte Python und Android Platform-Tools manuell installieren."
} else {
    if (-not (Test-Command "python")) {
        Write-Host "Installiere Python..." -ForegroundColor Yellow
        winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    }
    if (-not (Test-Command "adb")) {
        Write-Host "Installiere Android Platform-Tools (ADB)..." -ForegroundColor Yellow
        winget install -e --id Google.PlatformTools --accept-source-agreements --accept-package-agreements
    }
}

# 2. Python-Abhängigkeiten
Write-Host "Installiere Python-Abhängigkeiten..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")

# 3. .env anlegen, falls nicht vorhanden
$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $ProjectRoot ".env.example") $envFile
    Write-Warning "Bitte $envFile mit echten Schlüsseln (GEMINI_API_KEY, TELEGRAM_*) befüllen."
}

# 4. ADB-Verbindung zum Emulator prüfen
Write-Host "Verbinde mit Emulator $EmulatorAddress ..." -ForegroundColor Yellow
adb connect $EmulatorAddress | Out-Host
adb devices | Out-Host

Write-Host "Fertig. Test:" -ForegroundColor Green
Write-Host "  python -m src.agent.main --profile config/game_profile.evony.json --serial $EmulatorAddress --no-send"
