# gateway_watchdog.ps1 - Windows-level gateway watchdog (runs every 15 min via Task Scheduler)
# Independent of the OpenClaw gateway: survives full gateway death.
# Logic: probe port 18789 up to 3x over ~100s; require 3 failures AND gateway
# process older than 3 min (still starting up = do nothing); 10-min flap breaker
# via marker file shared with the cron watchdog; APPEND-ONLY memory logging.
$ErrorActionPreference = 'SilentlyContinue'

function Test-GatewayPort {
    $code = & curl.exe -s -o NUL -w "%{http_code}" --max-time 8 "http://127.0.0.1:18789/" 2>$null
    return ($code -match '^\d{3}$' -and $code -ne '000')
}

if (Test-GatewayPort) { exit 0 }
Start-Sleep -Seconds 30
if (Test-GatewayPort) { exit 0 }
Start-Sleep -Seconds 60
if (Test-GatewayPort) { exit 0 }

$marker = "$env:USERPROFILE\.openclaw\workspace\.openclaw\tmp\watchdog_last_restart.txt"
if (Test-Path $marker) {
    $ageMin = [int]((Get-Date) - (Get-Content $marker)).TotalMinutes
    if ($ageMin -lt 10) { exit 0 }
}

# process age guard: a young node gateway is starting up, leave it alone
$gw = Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match 'openclaw' } | Select-Object -First 1
if ($gw) {
    $ageMin2 = [int]((Get-Date) - $gw.CreationDate).TotalMinutes
    if ($ageMin2 -lt 3) { exit 0 }
}

$stamp = Get-Date -Format 'M/d/yyyy h:mm tt'
$day   = Get-Date -Format 'yyyy-MM-dd'
$note  = "$stamp - gateway-watchdog(task): port 18789 down 3 probes over ~2 min, restarting gateway task"
Set-Content -LiteralPath $marker -Value (Get-Date)
Add-Content -LiteralPath "$env:USERPROFILE\.openclaw\workspace\memory\$day.md" -Value $note -Encoding utf8

schtasks /end /tn "OpenClaw Gateway" | Out-Null
Start-Sleep -Seconds 8
schtasks /run /tn "OpenClaw Gateway" | Out-Null
exit 0