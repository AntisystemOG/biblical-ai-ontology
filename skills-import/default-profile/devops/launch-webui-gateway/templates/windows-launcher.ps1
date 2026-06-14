# Spock WebUI Windows Launcher (PowerShell)
# Place on Windows Desktop. Ensures WSL + systemd services, then opens Chrome.
# Designed for WSL-based Hermes deployments where the WebUI runs inside systemd.

param(
    [string]$Browser = "C:\Program Files\Google\Chrome\Application\chrome.exe",
    [int]$MaxWaitSec = 15
)

$ErrorActionPreference = "Stop"

# ── 1. Ensure WSL is running ─────────────────────────────────────────────────
$wslCheck = wsl.exe --exec true 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[spock] Starting WSL..." -ForegroundColor Cyan
    wsl.exe --exec true
    Start-Sleep -Seconds 3
}

# ── 2. Get current WSL IP (dynamic) ────────────────────────────────────────
$wslIP = wsl.exe hostname -I | ForEach-Object { $_.Trim().Split(' ')[0] }
if (-not $wslIP -or $wslIP -notmatch '^\d+\.\d+\.\d+\.\d+$') {
    $wslIP = wsl.exe ip addr show eth0 | wsl.exe grep "inet " | wsl.exe awk '{print $2}' | wsl.exe cut -d/ -f1 | wsl.exe head -1
    $wslIP = $wslIP.Trim()
}
Write-Host "[spock] WSL IP: $wslIP" -ForegroundColor Cyan

# ── 3. Ensure systemd services are running ───────────────────────────────────
$services = @("hermes-gateway.service", "hermes-webui.service")
foreach ($svc in $services) {
    $status = wsl.exe -- systemctl --user is-active $svc 2>$null
    if ($status -ne "active") {
        Write-Host "[spock] Starting $svc ..." -ForegroundColor Yellow
        wsl.exe -- systemctl --user start $svc
        Start-Sleep -Seconds 2
    } else {
        Write-Host "[spock] $svc already running" -ForegroundColor Green
    }
}

# ── 4. Verify WebUI reachable ──────────────────────────────────────────────
$url = "http://${wslIP}:8648/"
$reachable = $false
for ($i = 0; $i -lt $MaxWaitSec; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $url -Method HEAD -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            $reachable = $true
            break
        }
    } catch {}
    Start-Sleep -Seconds 1
}

if (-not $reachable) {
    Write-Warning "[spock] WebUI not responding at $url — attempting to restart..."
    wsl.exe -- systemctl --user restart hermes-webui.service
    Start-Sleep -Seconds 4
}

# ── 5. Open browser ─────────────────────────────────────────────────────────
$browserArgs = "--app=$url"

if (Test-Path $Browser) {
    Start-Process $Browser -ArgumentList $browserArgs
} else {
    $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (Test-Path $edge) {
        Start-Process $edge -ArgumentList $browserArgs
    } else {
        Start-Process $url
    }
}
