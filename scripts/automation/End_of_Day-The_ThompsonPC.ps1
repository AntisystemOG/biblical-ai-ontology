# Spock Git Sync - End of Day
# Pushes changes to GitHub

$workspace = "C:\Users\thada\.openclaw\workspace"
Set-Location $workspace

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

git add .
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "Update: $timestamp"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Commit failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! Pushed to GitHub." -ForegroundColor Green
} else {
    Write-Host "`n❌ Push failed." -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")