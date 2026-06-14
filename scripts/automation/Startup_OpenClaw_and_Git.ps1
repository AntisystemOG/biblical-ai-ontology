# Spock - Startup Script
# Optimized: launches gateway, pulls from GitHub, no version check overhead
# Memory features fully preserved — no compromises

$ErrorActionPreference = "Continue"
$workspace = "C:\Users\thada\.openclaw\workspace"

# ── Launch OpenClaw Gateway (do this first, it takes longest) ───────────────
$gatewayRunning = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like "*openclaw*entry.js*gateway*" }

if ($gatewayRunning) {
    Write-Host "OpenClaw gateway is already running." -ForegroundColor Green
} else {
    Write-Host "Starting OpenClaw gateway..." -ForegroundColor Yellow
    Start-Process "cmd.exe" -ArgumentList "/c `"C:\Users\thada\.openclaw\gateway.cmd`"" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "Gateway launched. Memory will index in background." -ForegroundColor Green
}

# ── Git Pull (runs while gateway is loading) ────────────────────────────────
Set-Location $workspace
Write-Host "Pulling latest from GitHub..." -ForegroundColor Cyan
git pull origin main 2>$null
Write-Host "Git sync complete." -ForegroundColor Green