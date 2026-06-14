# Daily Git Sync Script for Spock
# Run this at start and end of each session

param(
    [switch]$Push,
    [switch]$Pull,
    [switch]$Status
)

$workspace = "C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace"
Set-Location $workspace

if ($Status) {
    git status
    exit 0
}

if ($Pull) {
    Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
    git pull origin main
    Write-Host "✅ Done!" -ForegroundColor Green
    exit 0
}

if ($Push) {
    Write-Host "📤 Pushing changes..." -ForegroundColor Cyan
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git add .
    git commit -m "Update: $timestamp"
    git push origin main
    Write-Host "✅ Done!" -ForegroundColor Green
    exit 0
}

# Default: Pull then show status
Write-Host "📥 Pulling latest..." -ForegroundColor Cyan
git pull origin main
Write-Host ""
Write-Host "📊 Current status:" -ForegroundColor Cyan
git status