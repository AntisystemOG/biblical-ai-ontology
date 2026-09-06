# Spock Auto-Git Script
# Handles automatic pulls/pushes for memory sync

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pull", "push", "sync", "status")]
    [string]$Action
)

$workspace = "C:\Users\thadd\.openclaw\workspace"
$repoUrl = "https://github.com/AntisystemOG/spock-workspace.git"

# Check if git exists
$gitPath = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $gitPath) {
    Write-Host "❌ Git not installed"
    exit 1
}

Set-Location $workspace

switch ($Action) {
    "pull" {
        Write-Host "📥 Pulling from GitHub..." -ForegroundColor Cyan
        git fetch origin
        git pull origin main
        Write-Host "✅ Pull complete" -ForegroundColor Green
    }
    
    "push" {
        Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        git add .
        git commit -m "Update: $timestamp" 2>$null
        if ($LASTEXITCODE -eq 0) {
            git push origin main
            Write-Host "✅ Push complete" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Nothing to commit" -ForegroundColor Yellow
        }
    }
    
    "sync" {
        Write-Host "🔄 Syncing with GitHub..." -ForegroundColor Cyan
        # Pull first to get latest
        git fetch origin
        git pull origin main
        
        # Then push any local changes
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        git add .
        git commit -m "Sync: $timestamp" 2>$null
        if ($LASTEXITCODE -eq 0) {
            git push origin main
            Write-Host "✅ Sync complete" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Already in sync" -ForegroundColor Yellow
        }
    }
    
    "status" {
        git status --short
    }
}