# Temporary Gateway Watchdog
# Manual watchdog - run this when you need temporary monitoring
# Press Ctrl+C to stop

param(
    [int]$CheckIntervalSeconds = 30,
    [string]$LogPath = "$env:USERPROFILE\.openclaw\workspace\logs\temp-watchdog.log"
)

$ErrorActionPreference = "SilentlyContinue"
$watchdogActive = $true

function Test-GatewayRunning {
    $portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 18789 -WarningAction SilentlyContinue
    $nodeProcess = Get-Process -Name "node" | Where-Object { $_.CommandLine -like "*openclaw*" }
    return ($portTest.TcpTestSucceeded -or $nodeProcess)
}

function Start-Gateway {
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Starting OpenClaw gateway..." -ForegroundColor Yellow
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting gateway..." | Out-File -FilePath $LogPath -Append
    
    $gatewayCmd = "$env:USERPROFILE\.openclaw\gateway.cmd"
    if (Test-Path $gatewayCmd) {
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$gatewayCmd`"" -WindowStyle Minimized
        Start-Sleep -Seconds 5
        return $true
    } else {
        Write-Host "ERROR: gateway.cmd not found at $gatewayCmd" -ForegroundColor Red
        return $false
    }
}

# Header
Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEMPORARY GATEWAY WATCHDOG" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking every $CheckIntervalSeconds seconds..." -ForegroundColor Gray
Write-Host "Log: $LogPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

"=== Temporary Watchdog Started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $LogPath -Append
"Check interval: $CheckIntervalSeconds seconds" | Out-File -FilePath $LogPath -Append
"" | Out-File -FilePath $LogPath -Append

# Initial check
if (Test-GatewayRunning) {
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Gateway is already RUNNING" -ForegroundColor Green
    "[$(Get-Date -Format 'HH:mm:ss')] Initial status: Gateway RUNNING" | Out-File -FilePath $LogPath -Append
} else {
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Gateway is STOPPED" -ForegroundColor Red
    Start-Gateway
}

Write-Host ""

# Watchdog loop
try {
    while ($watchdogActive) {
        $timestamp = Get-Date -Format 'HH:mm:ss'
        $isRunning = Test-GatewayRunning
        
        if (-not $isRunning) {
            Write-Host "$timestamp - Gateway DOWN detected! Restarting..." -ForegroundColor Red
            "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ALERT: Gateway DOWN - attempting restart" | Out-File -FilePath $LogPath -Append
            Start-Gateway
            
            # Verify restart
            Start-Sleep -Seconds 5
            if (Test-GatewayRunning) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - Gateway RESTARTED successfully" -ForegroundColor Green
                "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Gateway restarted successfully" | Out-File -FilePath $LogPath -Append
            } else {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - FAILED to restart gateway" -ForegroundColor Red
                "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: Failed to restart gateway" | Out-File -FilePath $LogPath -Append
            }
        } else {
            Write-Host "$timestamp - Gateway OK" -ForegroundColor DarkGray
        }
        
        Start-Sleep -Seconds $CheckIntervalSeconds
    }
} catch {
    # Ctrl+C or error
    Write-Host ""
    Write-Host "Watchdog stopped." -ForegroundColor Yellow
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Watchdog stopped by user" | Out-File -FilePath $LogPath -Append
}

Write-Host ""
Write-Host "Log saved to: $LogPath" -ForegroundColor Gray
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
