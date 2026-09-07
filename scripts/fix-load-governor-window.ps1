# fix-load-governor-window.ps1 (2026-09-07)
# Swaps the "OpenClaw Load Governor" task action from direct powershell.exe
# (console flash every 5 min) to the hidden wscript launcher.
# Set-ScheduledTask with only -Action preserves the existing trigger/settings/principal.
$ErrorActionPreference = 'Stop'

$Launcher = "$env:USERPROFILE\.openclaw\workspace\scripts\load_governor_launcher.vbs"
if (-not (Test-Path $Launcher)) {
    Write-Host "ERROR: launcher missing at $Launcher" -ForegroundColor Red
    exit 1
}

$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "//B `"$Launcher`""
Set-ScheduledTask -TaskName 'OpenClaw Load Governor' -Action $action | Out-Null
Write-Host "Load Governor action swapped to hidden wscript launcher" -ForegroundColor Green

Start-ScheduledTask -TaskName 'OpenClaw Load Governor'
Write-Host 'Test run triggered.'