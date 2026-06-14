# Spock - Shutdown Script
# Writes daily memory, pushes all changes to GitHub before Windows shuts down
# Registered as a Windows shutdown script via Group Policy

$ErrorActionPreference = "Continue"

# Use the real workspace path (not OneDrive placeholder)
$workspace = "C:\Users\thada\.openclaw\workspace"
Set-Location $workspace

Write-Host ""
Write-Host "============================================" -ForegroundColor DarkCyan
Write-Host "   SPOCK - END OF DAY MEMORY DUMP          " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 0: Write daily memory stamp ---
$today = Get-Date -Format "yyyy-MM-dd"
$memoryDir = Join-Path $workspace "memory"
$memoryFile = Join-Path $memoryDir "$today.md"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

if (-not (Test-Path $memoryFile)) {
    # Create today's memory file with a header
    "---`ncreated: $timestamp`n---" | Out-File -FilePath $memoryFile -Encoding utf8 -Force
    Write-Host "[0/5] Created memory file for $today" -ForegroundColor Green
} else {
    Write-Host "[0/5] Memory file exists for $today" -ForegroundColor Gray
}

# --- Step 1: Ensure we're on main branch ---
$currentBranch = git branch --show-current 2>$null
if ($currentBranch -ne "main") {
    Write-Host "[1/5] Switching to main branch..." -ForegroundColor Yellow
    git checkout main 2>$null
} else {
    Write-Host "[1/5] On main branch." -ForegroundColor Gray
}

# --- Step 2: Pull first ---
Write-Host "[2/5] Pulling latest from GitHub..." -ForegroundColor Yellow
git pull origin main 2>$null

# --- Step 3: Stage all changes ---
Write-Host "[3/5] Staging files..." -ForegroundColor Yellow
git add . 2>$null

# --- Step 4: Commit if needed ---
$status = git status --porcelain 2>$null
if ($status) {
    Write-Host "[4/5] Committing changes..." -ForegroundColor Yellow
    $commitTime = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "EOD sync: $commitTime" 2>$null
} else {
    Write-Host "[4/5] No changes to commit." -ForegroundColor Gray
}

# --- Step 5: Push to GitHub ---
Write-Host "[5/5] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Memory dump complete. Safe to shut down." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Push encountered issues, but local commit is safe." -ForegroundColor DarkYellow
}

Write-Host ""
Start-Sleep -Seconds 5