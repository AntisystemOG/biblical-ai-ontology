# schedule-watchdog.ps1
# Adds gateway watchdog to Task Scheduler for auto-start on login

$taskName = "OpenClawGatewayWatchdog"
$scriptPath = Join-Path $PSScriptRoot "gateway-watchdog.ps1"

# Check if task already exists
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existing) {
    Write-Host "Task '$taskName' already exists. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

# Create trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Register task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description "Restarts OpenClaw gateway every 5 minutes if not running"

Write-Host "Task registered!" -ForegroundColor Green