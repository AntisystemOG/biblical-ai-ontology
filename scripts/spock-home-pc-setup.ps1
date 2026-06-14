<# 
.SYNOPSIS
    Spock Home PC Full Setup — Run as Administrator
.DESCRIPTION
    This script sets up a fresh Windows PC to match the laptop configuration.
    Run from an elevated PowerShell prompt.
    
    Usage: 
    1. Open PowerShell as Administrator
    2. Run: Set-ExecutionPolicy Bypass -Scope Process -Force
    3. Run: .\spock-home-pc-setup.ps1
#>

$ErrorActionPreference = "Stop"
Write-Host "=== Spock Home PC Full Setup ===" -ForegroundColor Cyan
Write-Host "This will install everything needed to match the laptop configuration." -ForegroundColor Yellow
Write-Host ""

# ── 0. Prerequisites ──
Write-Host "[0/9] Checking prerequisites..." -ForegroundColor Yellow

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Run this as Administrator!" -ForegroundColor Red
    exit 1
}

# ── 1. Install Chocolatey (if not installed) ──
Write-Host "`n[1/9] Checking Chocolatey..." -ForegroundColor Yellow
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
} else {
    Write-Host "Chocolatey already installed: $(choco --version)" -ForegroundColor Green
}

# ── 2. Install core tools ──
Write-Host "`n[2/9] Installing core tools (Git, Node.js, Pandoc, FFmpeg)..." -ForegroundColor Yellow
choco install git -y --no-progress
choco install nodejs-lts -y --no-progress
choco install pandoc -y --no-progress
choco install ffmpeg -y --no-progress
refreshenv

# ── 3. Install Python 3.14 ──
Write-Host "`n[3/9] Installing Python 3.14..." -ForegroundColor Yellow
if (-not (Test-Path "C:\Python314\python.exe")) {
    Write-Host "Downloading Python 3.14..." -ForegroundColor Yellow
    $pythonUrl = "https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-3.14.0-amd64.exe"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python314" -Wait
    Remove-Item $pythonInstaller
} else {
    Write-Host "Python 3.14 already installed" -ForegroundColor Green
}

# ── 4. Install OpenClaw ──
Write-Host "`n[4/9] Installing OpenClaw..." -ForegroundColor Yellow
if (-not (Get-Command openclaw -ErrorAction SilentlyContinue)) {
    npm install -g openclaw
} else {
    Write-Host "OpenClaw already installed: $(openclaw --version 2>$null)" -ForegroundColor Green
}

# ── 5. Install Ollama ──
Write-Host "`n[5/9] Installing Ollama..." -ForegroundColor Yellow
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    choco install ollama -y --no-progress
} else {
    Write-Host "Ollama already installed" -ForegroundColor Green
}

# ── 6. Pull Ollama models ──
Write-Host "`n[6/9] Pulling Ollama models..." -ForegroundColor Yellow
ollama pull mistral
ollama pull deepseek-r1
ollama pull gemma3
ollama pull nomic-embed-text

# ── 7. Clone workspace ──
Write-Host "`n[7/9] Cloning Spock workspace..." -ForegroundColor Yellow
$workspaceDir = "C:\Users\thada\.openclaw\workspace"
if (-not (Test-Path $workspaceDir)) {
    New-Item -ItemType Directory -Path "C:\Users\thada\.openclaw" -Force | Out-Null
    Set-Location "C:\Users\thada\.openclaw"
    git clone https://github.com/AntisystemOG/spock-workspace.git workspace
} else {
    Set-Location $workspaceDir
    git pull origin main
}
Set-Location $workspaceDir

# ── 8. Install Python packages ──
Write-Host "`n[8/9] Installing Python packages..." -ForegroundColor Yellow
& "C:\Python314\python.exe" -m pip install --upgrade pip --quiet
& "C:\Python314\python.exe" -m pip install torch whisper numpy pandas pyannote.audio speechbrain torchaudio fpdf fpdf2 tavily-python --quiet

# ── 9. Install OpenClaw skills ──
Write-Host "`n[9/9] Installing OpenClaw skills..." -ForegroundColor Yellow
openclaw skills install tavily
openclaw skills install free-ride
openclaw skills install browser-automation
openclaw skills install self-improving
openclaw skills install evoclaw

# ── FreeRide CLI ──
Set-Location "$workspaceDir\skills\free-ride"
& "C:\Python314\python.exe" -m pip install -e . --quiet
Set-Location $workspaceDir

# ── Done ──
Write-Host "`n" -NoNewline
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy openclaw.json from the laptop to C:\Users\thada\.openclaw\openclaw.json" -ForegroundColor White
Write-Host "   (This contains your API keys, model config, cron jobs, etc.)" -ForegroundColor Gray
Write-Host "2. Run: openclaw gateway start" -ForegroundColor White
Write-Host "3. Verify: openclaw status" -ForegroundColor White
Write-Host ""
Write-Host "Or just run: openclaw wizard" to set up from scratch." -ForegroundColor Yellow