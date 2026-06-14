# Gateway Watchdog - restarts gateway if down
$gatewayPid = Get-Content "C:\Users\thada\AppData\Local\Temp\openclaw\gateway.pid" -ErrorAction SilentlyContinue
$isRunning = $false

if ($gatewayPid) {
    $proc = Get-Process -Id $gatewayPid -ErrorAction SilentlyContinue
    if ($proc -and -not $proc.HasExited) {
        $isRunning = $true
    }
}

# Also check by port
$portCheck = Netstat -ano | Select-String ":18789.*LISTENING"
if ($portCheck) {
    $isRunning = $true
}

if (-not $isRunning) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Gateway down, restarting..."
    Start-Process "C:\Users\thada\.openclaw\gateway.cmd" -WindowStyle Hidden
    Start-Sleep 3
    $newPid = (Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*openclaw*gateway*" } | Select-Object -First 1).Id
    if ($newPid) {
        $newPid | Set-Content "C:\Users\thada\AppData\Local\Temp\openclaw\gateway.pid"
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Gateway restarted, PID: $newPid"
    }
} else {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Gateway OK"
}
