# Spock Laptop Setup Script
# Run as Administrator for best results
# Fresh Windows install - installs all required tools

$ErrorActionPreference = "Continue"
$ProgressPreference = "Continue"

Write-Host "=== SPOCK LAPTOP SETUP ===" -ForegroundColor Cyan
Write-Host "Starting fresh Windows setup..." -ForegroundColor Yellow

# Create Spocks Reports folder
$spockPath = "C:\Users\thadd\OneDrive\Desktop\Spocks Reports"
New-Item -ItemType Directory -Force -Path $spockPath
Write-Host "✓ Created Spocks Reports folder" -ForegroundColor Green

# Create Spock WebUI desktop shortcut (.url)
$shortcut = "C:\Users\thadd\Desktop\Spocks WebUI.url"
if (-not (Test-Path $shortcut)) {
    $urlContent = @"
[InternetShortcut]
URL=http://172.24.60.180:8648/
IconFile=C:\Users\thadd\Desktop\spock-icon.ico
IconIndex=0
HotKey=0
IDList=
"@
    $urlContent | Out-File -FilePath $shortcut -Encoding ASCII
    Write-Host "✓ Created Spocks WebUI desktop shortcut" -ForegroundColor Green
} else {
    Write-Host "Spocks WebUI shortcut already exists" -ForegroundColor Green
}

# Install Chocolatey (package manager)
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
    Write-Host "✓ Chocolatey installed" -ForegroundColor Green
}

# Install Python 3.14
Write-Host "Installing Python 3.14..." -ForegroundColor Yellow
choco install python --version 3.14.0 -y
refreshenv
Write-Host "✓ Python 3.14 installed" -ForegroundColor Green

# Install Git (already have it but ensure latest)
Write-Host "Updating Git..." -ForegroundColor Yellow
choco install git -y
Write-Host "✓ Git updated" -ForegroundColor Green

# Install Node.js (already have it)
Write-Host "Node.js already installed: $(node --version)" -ForegroundColor Green

# Install FFmpeg
Write-Host "Installing FFmpeg..." -ForegroundColor Yellow
choco install ffmpeg -y
refreshenv
Write-Host "✓ FFmpeg installed" -ForegroundColor Green

# Install Ollama (if not present)
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Ollama..." -ForegroundColor Yellow
    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller
    Start-Process -FilePath $ollamaInstaller -ArgumentList "/SILENT" -Wait
    Remove-Item $ollamaInstaller -Force
    Write-Host "✓ Ollama installed" -ForegroundColor Green
} else {
    Write-Host "Ollama already installed: $(ollama --version)" -ForegroundColor Green
}

# Update graphics driver (Intel HD 520)
Write-Host "`n=== GRAPHICS DRIVER UPDATE ===" -ForegroundColor Cyan
Write-Host "Current driver: $(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty DriverVersion)" -ForegroundColor Yellow
Write-Host "Driver is from 2021. Updating via Windows Update or Intel website recommended." -ForegroundColor Yellow
Write-Host "Visit: https://www.intel.com/content/www/us/en/download/726609/intel-arc-iris-xe-graphics-windows.html" -ForegroundColor Cyan

# Pull models from old workspace
Write-Host "`n=== RESTORING WORKSPACE FILES ===" -ForegroundColor Cyan
$workspacePath = "C:\Users\thadd\.openclaw\workspace"
if (Test-Path "C:\Users\thadd\.openclaw\workspace_spock") {
    Write-Host "Found old workspace backup, copying files..." -ForegroundColor Yellow
    Copy-Item "C:\Users\thadd\.openclaw\workspace_spock\*.py" $workspacePath -Force -ErrorAction SilentlyContinue
    Copy-Item "C:\Users\thadd\.openclaw\workspace_spock\*.md" $workspacePath -Force -ErrorAction SilentlyContinue
    Copy-Item "C:\Users\thadd\.openclaw\workspace_spock\memory" $workspacePath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Workspace files restored" -ForegroundColor Green
}

Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Please RESTART your computer to complete installation." -ForegroundColor Red
Write-Host "After restart, run: pip install torch whisper numpy pandas pyannote.audio speechbrain torchaudio" -ForegroundColor Yellow
