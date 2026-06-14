# cloud-sync-before-shutdown.ps1
# Forces OneDrive sync, then optionally shuts down the PC

param(
    [switch]$Shutdown,  # Add -Shutdown to shut down after sync
    [int]$Timeout = 120  # Max seconds to wait for sync
)

$ErrorActionPreference = "Stop"

Write-Host "=== Cloud Sync Before Shutdown ===" -ForegroundColor Cyan

# 1. Check if OneDrive is running
$oneDrive = Get-Process OneDrive -ErrorAction SilentlyContinue
if (-not $oneDrive) {
    Write-Host "[ERROR] OneDrive is not running. Starting..." -ForegroundColor Red
    Start-Process "C:\Program Files\Microsoft OneDrive\OneDrive.exe" -ArgumentList "/background"
    Start-Sleep -Seconds 5
}

# 2. Force OneDrive sync
Write-Host "[1/3] forcing OneDrive sync..." -ForegroundColor Yellow
Start-Process "OneDrive.exe" -ArgumentList "/sync" -WindowStyle Hidden

# 3. Monitor sync status
Write-Host "[2/3] Waiting for sync to complete (max $Timeout seconds)..." -ForegroundColor Yellow

$startTime = Get-Date
$syncComplete = $false

while (((Get-Date) - $startTime).TotalSeconds -lt $Timeout) {
    # Check OneDrive sync status via registry
    $syncState = Get-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\OneDrive\Accounts\Personal" -Name "UserFolderToLocalSync" -ErrorAction SilentlyContinue
    
    # Also check if there are recent file modifications in OneDrive folder
    $oneDrivePath = "$env:USERPROFILE\OneDrive"
    if (Test-Path $oneDrivePath) {
        $recentFiles = Get-ChildItem $oneDrivePath -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) }
        
        if ($recentFiles.Count -eq 0 -and $syncState) {
            $syncComplete = $true
            break
        }
    }
    
    Start-Sleep -Seconds 3
    Write-Host "." -NoNewline
}

Write-Host ""

if ($syncComplete) {
    Write-Host "[3/3] ✓ Sync complete!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Sync timeout ($Timeout seconds). Continuing anyway..." -ForegroundColor Yellow
}

# 4. Optional shutdown
if ($Shutdown) {
    Write-Host "[SHUTDOWN] Shutting down in 10 seconds..." -ForegroundColor Red
    Write-Host "Press Ctrl+C to cancel" -ForegroundColor Gray
    Start-Sleep -Seconds 10
    Stop-Computer -Force
} else {
    Write-Host "[DONE] Cloud synced. Ready for shutdown." -ForegroundColor Green
    Write-Host "Run with -Shutdown flag to auto-shutdown after sync." -ForegroundColor Gray
}