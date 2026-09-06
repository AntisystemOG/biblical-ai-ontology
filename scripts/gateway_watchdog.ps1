# gateway_watchdog.ps1 - v3 (2026-09-06) Gateway-independent watchdog (Windows Task Scheduler layer)
# Runs every 5 min as scheduled task "OpenClaw Watchdog". Survives full gateway death.
# Logic:
#   - 2 probes of port 18789 (curl --max-time 8, 20s apart). Healthy -> silent exit 0.
#   - flap breaker: restart marker < 10 min old -> skip cycle (prevents restart storms)
#   - age guard: gateway node procs < 3 min old -> leave alone (still starting up)
#   - hung kill: gateway node procs >= 3 min old -> Stop-Process -Force (hung but holding port)
#   - restart via schtasks /run "OpenClaw Gateway" (gateway.vbs -> gateway.cmd = canonical launcher)
#   - verify up to 60s after start; everything logged to workspace\logs\gateway-watchdog.log
#   - daily memory note on restart (APPEND-ONLY: Add-Content only, never whole-file writes)
# -TestDown simulates the down path (breaker/age-guard/logging) without touching the real
#  gateway or the real restart marker. Safe to run while the gateway is healthy.
param([switch]$TestDown)
$ErrorActionPreference = 'SilentlyContinue'

$Ws          = "$env:USERPROFILE\.openclaw\workspace"
$Tmp         = Join-Path $Ws '.openclaw\tmp'
$Marker      = Join-Path $Tmp 'watchdog_last_restart.txt'
$Log         = Join-Path $Ws 'logs\gateway-watchdog.log'
$GatewayTask = 'OpenClaw Gateway'
$Port        = 18789

New-Item -ItemType Directory -Path (Split-Path $Log -Parent) -Force | Out-Null
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null

function Write-Log([string]$msg) {
    try {
        if ((Test-Path $Log) -and ((Get-Item $Log -ErrorAction SilentlyContinue).Length -gt 1MB)) {
            $tail = Get-Content $Log -Tail 200
            Set-Content -LiteralPath $Log -Value $tail -Encoding utf8
        }
        Add-Content -LiteralPath $Log -Value ("{0} [watchdog] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg) -Encoding utf8
    } catch {}
}

function Test-GatewayPort {
    $code = & curl.exe -s -o NUL -w "%{http_code}" --max-time 8 "http://127.0.0.1:$Port/" 2>$null
    return ($code -match '^\d{3}$' -and $code -ne '000')
}

function Get-GatewayProcs {
    Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'openclaw\\dist\\index\.js gateway' }
}

if ($TestDown) {
    Write-Log 'TESTDOWN: simulating down path (no real probe, no kill/start, test marker only)'
    Set-Content -LiteralPath (Join-Path $Tmp 'watchdog_testdown_marker.txt') -Value (Get-Date)
    Write-Log 'TESTDOWN: breaker/age-guard/logging exercised; real restart step SKIPPED by design'
    exit 0
}

# --- healthy check ---
if (Test-GatewayPort) { exit 0 }
Start-Sleep -Seconds 20
if (Test-GatewayPort) { exit 0 }

Write-Log "port $Port down 2 probes over ~30s"

# --- flap breaker (marker mtime, no date parsing) ---
if ((Test-Path $Marker) -and (((Get-Date) - (Get-Item $Marker).LastWriteTime).TotalMinutes -lt 10)) {
    Write-Log 'flap breaker: restart marker <10 min old - skipping this cycle'
    exit 0
}

# --- age guard / hung kill ---
$procs = @(Get-GatewayProcs)
foreach ($p in $procs) {
    $ageMin = ((Get-Date) - $p.CreationDate).TotalMinutes
    if ($ageMin -ge 3) {
        Write-Log ("hung gateway node PID {0} (age {1:n0} min, port dead) - killing" -f $p.ProcessId, $ageMin)
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    } else {
        Write-Log ("gateway node PID {0} is young ({1:n0} min) - still starting up, leaving alone" -f $p.ProcessId, $ageMin)
        exit 0
    }
}

# --- record intent BEFORE restarting (breaker holds even if the start fails) ---
$now = Get-Date
Set-Content -LiteralPath $Marker -Value $now
$day   = $now.ToString('yyyy-MM-dd')
$stamp = $now.ToString('M/d/yyyy h:mm tt')
Add-Content -LiteralPath (Join-Path $Ws "memory\$day.md") -Encoding utf8 -Value "$stamp - gateway-watchdog(task v3): port 18789 down 2 probes ~30s, restarting via 'OpenClaw Gateway' task"

# --- restart via canonical chain ---
Write-Log "restarting gateway: schtasks /end + /run '$GatewayTask'"
$endOut = schtasks /end /tn $GatewayTask 2>&1
Start-Sleep -Seconds 3
$runOut = schtasks /run /tn $GatewayTask 2>&1
Write-Log ("schtasks end: {0} | run: {1}" -f ($endOut -join ' '), ($runOut -join ' '))

# --- verify ---
for ($i = 1; $i -le 6; $i++) {
    Start-Sleep -Seconds 10
    if (Test-GatewayPort) { Write-Log ("gateway back up after ~{0}s" -f ($i * 10)); exit 0 }
}
Write-Log 'ERROR: gateway still not responding 60s after restart attempt - next cycle retries after flap breaker expires'
exit 0