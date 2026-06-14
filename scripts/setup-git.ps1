# Git Setup Script for Spock Workspace
# Run this when you get home on the machine you want as the primary

Write-Host "🖖 Spock Git Setup" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

# 1. Check if Git is installed
Write-Host "`n[1/5] Checking Git installation..." -ForegroundColor Yellow
$gitPath = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $gitPath) {
    Write-Host "❌ Git not found. Install it first:" -ForegroundColor Red
    Write-Host "   - Download from: https://git-scm.com"
    Write-Host "   - Or: choco install git (if Chocolatey installed)"
    Write-Host "   - Or: winget install Git.Git"
    exit 1
}
Write-Host "✅ Git found at: $gitPath" -ForegroundColor Green

# 2. Check if already a repo
Write-Host "`n[2/5] Checking repository status..." -ForegroundColor Yellow
$workspace = "C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace"
Set-Location $workspace
if (Test-Path ".git") {
    Write-Host "⚠️  Already a Git repository. Skipping init." -ForegroundColor Yellow
} else {
    Write-Host "Initializing new repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Repository initialized." -ForegroundColor Green
}

# 3. Create .gitignore
Write-Host "`n[3/5] Creating .gitignore..." -ForegroundColor Yellow
$gitignore = @"
# OpenClaw
.openclaw/
*.log

# Python
__pycache__/
*.pyc
.env/

# OS
Thumbs.db
.DS_Store

# Temporary
*.tmp
"@
Set-Content -Path ".gitignore" -Value $gitignore -ErrorAction SilentlyContinue
Write-Host "✅ .gitignore created." -ForegroundColor Green

# 4. Add and commit everything
Write-Host "`n[4/5] Creating initial commit..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit - Spock workspace"
Write-Host "✅ Initial commit created." -ForegroundColor Green

# 5. Instructions for remote
Write-Host "`n[5/5] Remote Setup (OPTIONAL)" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host "To sync across machines, create a GitHub/GitLab remote:"
Write-Host ""
Write-Host "1. Create a private repo at: https://github.com/new"
Write-Host "2. Run these commands:"
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/spock-workspace.git"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "Then on OTHER machines, clone instead of using OneDrive:"
Write-Host "   git clone https://github.com/YOUR_USERNAME/spock-workspace.git"
Write-Host ""
Write-Host "Daily workflow:"
Write-Host "   git pull origin main  (start of day)"
Write-Host "   git add . && git commit -m 'daily update'"
Write-Host "   git push origin main  (end of day)"
Write-Host ""
Write-Host "🖖 Setup complete!" -ForegroundColor Cyan