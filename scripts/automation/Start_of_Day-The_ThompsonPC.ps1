# Spock Git Sync - Start of Day
# Pulls latest from GitHub

$workspace = "C:\Users\thada\.openclaw\workspace"
Set-Location $workspace

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "📥 Pulling from GitHub..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
git pull origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! All synced." -ForegroundColor Green
} else {
    Write-Host "`n❌ ERROR occurred." -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")