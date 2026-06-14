#Requires -Version 5.1
# PLC Coder Launcher

$LogFile = "C:\Users\thadd\.openclaw\workspace\scripts\plc-launcher-log.txt"

function Write-Log($Message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Tee-Object -FilePath $LogFile -Append
}

"Started at $(Get-Date)" | Set-Content $LogFile

Write-Log "=== PLCTools Coder Launcher ==="
Set-Location "C:\Users\thadd\.openclaw\workspace"
Write-Log "Directory: $(Get-Location)"

# Check openclaw
$oc = Get-Command "openclaw" -ErrorAction SilentlyContinue
if (-not $oc) {
    Write-Log "ERROR: openclaw not found"
    Read-Host "Press Enter"
    exit 1
}

Write-Log "[1/3] Spawning agent..."
# Correct syntax for sessions_spawn
$output = openclaw sessions spawn plctool-coder "Spawn PLCTools coding assistant" 2>&1
Write-Log "Output: $output"
Write-Log "Exit: $LASTEXITCODE"

Write-Log "[2/3] Waiting..."
Start-Sleep -Seconds 2

Write-Log "[3/3] Opening browser..."
Start-Process "http://127.0.0.1:18789/"

Write-Log "Done"
Start-Sleep -Seconds 3