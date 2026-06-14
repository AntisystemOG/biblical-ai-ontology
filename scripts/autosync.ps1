# Auto-sync script - integrates with Spock startup
# Run this at STARTUP (before any work) and SHUTDOWN (after session)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("startup", "shutdown")]
    [string]$Mode
)

$workspace = "C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace"
Set-Location $workspace

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

if ($Mode -eq "startup") {
    Write-Host "🖖 Spock starting up..." -ForegroundColor Cyan
    Write-Host "📥 Pulling latest changes..." -ForegroundColor Yellow
    git pull origin main 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Synced with remote." -ForegroundColor Green
    } else {
        Write-Host "⚠️  No remote or pull failed (may be first run)." -ForegroundColor Yellow
    }
}

if ($Mode -eq "shutdown") {
    Write-Host "🖖 Spock shutting down..." -ForegroundColor Cyan
    Write-Host "📤 Pushing changes..." -ForegroundColor Yellow
    git add .
    git commit -m "Session end: $timestamp" 2>$null
    git push origin main 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Synced to remote." -ForegroundColor Green
    } else {
        Write-Host "⚠️  No remote or push failed." -ForegroundColor Yellow
    }
}

Write-Host "🖖 Goodbye!" -ForegroundColor Cyan