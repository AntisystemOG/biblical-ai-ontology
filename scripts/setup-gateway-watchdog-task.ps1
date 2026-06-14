# Setup Gateway Watchdog Scheduled Task (Fixed v2)
# Run as Administrator in PowerShell
# Uses Interactive logon so it can access user PATH and npm

$TaskName = "OpenClaw-Gateway-Watchdog"
$ScriptPath = "$env:USERPROFILE\.openclaw\workspace\scripts\gateway-watchdog-reliable.ps1"

Write-Host "Setting up Gateway Watchdog Scheduled Task..." -ForegroundColor Cyan

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: Run as Administrator!" -ForegroundColor Red
    exit 1
}

# Remove existing task
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Find openclaw
$openclawPath = (Get-Command openclaw -ErrorAction SilentlyContinue).Source
if (-not $openclawPath) {
    $openclawPath = "$env:APPDATA\npm\openclaw.cmd"
}

Write-Host "OpenClaw found at: $openclawPath" -ForegroundColor Gray

# Create action - run PowerShell with full user PATH
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Silent"

# Create trigger - every 5 minutes starting now
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)

# Settings - allow on battery, wake computer if needed
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2)

# Run as current user with highest privileges
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
    
    Write-Host ""
    Write-Host "✅ Task created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test it now:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "To check logs:" -ForegroundColor Yellow
    Write-Host "  notepad `$env:USERPROFILE\.openclaw\workspace\logs\gateway-watchdog.log" -ForegroundColor White
    Write-Host ""
    Write-Host "To test the watchdog script directly:" -ForegroundColor Yellow
    Write-Host "  & '$ScriptPath'" -ForegroundColor White
    
    # Run it once immediately
    Write-Host ""
    Write-Host "Running first check now..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $TaskName
    
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
    if ($_.Exception.Message -match "Interactive") {
        Write-Host ""
        Write-Host "Try manual setup:" -ForegroundColor Yellow
        Write-Host "1. Win+R → taskschd.msc" -ForegroundColor White
        Write-Host "2. Create Task → Run whether user is logged on or not" -ForegroundColor White
        Write-Host "3. Triggers: One time, repeat every 5 min indefinitely" -ForegroundColor White
        Write-Host "4. Actions: powershell.exe -File '$ScriptPath' -Silent" -ForegroundColor White
    }
    exit 1
}
