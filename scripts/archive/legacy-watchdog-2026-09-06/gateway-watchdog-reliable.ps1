# Gateway Watchdog - PowerShell Script (Fixed v3)
# Checks if OpenClaw gateway is alive, starts it if not
# Uses direct node command (bypasses npm wrapper issues)

param(
    [switch]$Silent,
    [switch]$TestMode
)

$LogFile = "$env:USERPROFILE\.openclaw\workspace\logs\gateway-watchdog.log"
$LockFile = "$env:USERPROFILE\.openclaw\workspace\.gateway-watchdog.lock"
$GatewayUrl = "http://127.0.0.1:18789"

# Direct paths from openclaw gateway status
$NodeExe = "C:\Program Files\nodejs\node.exe"
$OpenClawJs = "C:\Users\thadd\AppData\Roaming\npm\node_modules\openclaw\dist\index.js"
$GatewayPort = "18789"

# Ensure log directory exists
$LogDir = Split-Path $LogFile -Parent
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    try { Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue } catch {}
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
            "WARN"  { Write-Host $LogEntry -ForegroundColor Yellow }
            "OK"    { Write-Host $LogEntry -ForegroundColor Green }
            "START" { Write-Host $LogEntry -ForegroundColor Cyan }
            default { Write-Host $LogEntry }
        }
    }
}

function Test-GatewayRunning {
    try {
        # Quick TCP port check (fast)
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 18789)
        $tcp.Close()
        Write-Log "Port 18789: Listening" "OK"
        return $true
    } catch {
        Write-Log "Port 18789: Not listening" "WARN"
        return $false
    }
}

function Start-Gateway {
    try {
        Write-Log "=== Starting OpenClaw Gateway ===" "START"
        
        if (-not (Test-Path $NodeExe)) {
            Write-Log "node.exe not found at: $NodeExe" "ERROR"
            return $false
        }
        if (-not (Test-Path $OpenClawJs)) {
            Write-Log "openclaw index.js not found at: $OpenClawJs" "ERROR"
            return $false
        }
        
        Write-Log "Command: $NodeExe $OpenClawJs gateway --port $GatewayPort" "START"
        
        # Start gateway in background - do NOT wait
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $NodeExe
        $psi.Arguments = "`"$OpenClawJs`" gateway --port $GatewayPort"
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
        $psi.WorkingDirectory = Split-Path $OpenClawJs -Parent
        
        $process = [System.Diagnostics.Process]::Start($psi)
        $pid = $process.Id
        
        Write-Log "Launched gateway (PID: $pid)" "OK"
        
        # Wait up to 60 seconds
        $timeout = 60
        $elapsed = 0
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            
            if (Test-GatewayRunning) {
                Write-Log "Gateway started after ${elapsed}s" "OK"
                $process.Dispose()
                return $true
            }
            
            # Check if process died
            if ($process.HasExited) {
                Write-Log "Gateway process exited (code: $($process.ExitCode))" "ERROR"
                $process.Dispose()
                return $false
            }
            
            Write-Log "Waiting... (${elapsed}s)" "INFO"
        }
        
        Write-Log "Gateway not responding after ${timeout}s (PID $pid still running)" "WARN"
        $process.Dispose()
        return $false
    } catch {
        Write-Log "Exception: $_" "ERROR"
        return $false
    }
}

# Prevent duplicate runs
if (Test-Path $LockFile) {
    $lockAge = ((Get-Date) - (Get-Item $LockFile).LastWriteTime).TotalSeconds
    if ($lockAge -lt 240) { exit 0 }
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType File -Path $LockFile -Force | Out-Null

try {
    Write-Log "=== Watchdog Check ===" "START"
    
    if ($TestMode) {
        Write-Log "TEST MODE" "WARN"
        Start-Gateway
    } elseif (Test-GatewayRunning) {
        Write-Log "Gateway OK" "OK"
    } else {
        Write-Log "Gateway DOWN" "ERROR"
        Start-Gateway
    }
    
    Write-Log "=== Complete ==="
} finally {
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
