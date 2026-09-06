# setup-gateway-watchdog-task.ps1 - v3 (2026-09-06)
# (Re)registers the "OpenClaw Watchdog" scheduled task.
#   - every 5 minutes (was 15: the blind window ate tonight's outage)
#   - AllowStartIfOnBatteries + DontStopIfGoingOnBatteries (was battery-blocked!)
#   - StartWhenAvailable (catches up missed runs), IgnoreNew, 10-min execution limit
#   - runs scripts/gateway_watchdog.ps1 (v3)
# No elevation required: per-user interactive task.
# Idempotent: safe to re-run; -Force replaces the existing task.

$TaskName   = 'OpenClaw Watchdog'
$ScriptPath = "$env:USERPROFILE\.openclaw\workspace\scripts\gateway_watchdog.ps1"

if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: watchdog script missing at $ScriptPath" -ForegroundColor Red
    exit 1
}

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host 'Note: running without elevation - fine for per-user interactive tasks' -ForegroundColor Yellow
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force -ErrorAction Stop | Out-Null
    Write-Host "Registered '$TaskName': every 5 min, battery-safe, StartWhenAvailable" -ForegroundColor Green
} catch {
    Write-Host "ERROR: failed to register task: $_" -ForegroundColor Red
    exit 1
}

# Visible test run right away
Start-ScheduledTask -TaskName $TaskName
Write-Host 'Test run triggered. Verify with:' -ForegroundColor Cyan
Write-Host '  schtasks /query /tn "OpenClaw Watchdog" /fo LIST /v'
Write-Host '  Get-Content "$env:USERPROFILE\.openclaw\workspace\logs\gateway-watchdog.log" -Tail 10'