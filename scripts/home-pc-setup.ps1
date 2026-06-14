# Home PC Setup Script
# Run this on the home PC after logging in
# Open PowerShell as Administrator first!

Write-Host "=== Spock Home PC Setup ===" -ForegroundColor Cyan

# 1. Pull latest workspace from GitHub
Write-Host "`n[1/7] Pulling workspace from GitHub..." -ForegroundColor Yellow
Set-Location "C:\Users\thada\.openclaw\workspace"
git pull origin main

# 2. Install Pandoc (if not already installed)
Write-Host "`n[2/7] Installing Pandoc..." -ForegroundColor Yellow
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    choco install pandoc -y
} else {
    Write-Host "Pandoc already installed: $(pandoc --version | Select-Object -First 1)"
}

# 3. Install Python packages
Write-Host "`n[3/7] Installing Python packages..." -ForegroundColor Yellow
& "C:\Python314\python.exe" -m pip install torch whisper numpy pandas pyannote.audio speechbrain torchaudio fpdf fpdf2 --quiet

# 4. Pull Ollama models
Write-Host "`n[4/7] Pulling Ollama models..." -ForegroundColor Yellow
ollama pull mistral
ollama pull deepseek-r1
ollama pull gemma3
ollama pull nomic-embed-text

# 5. Install OpenClaw skills
Write-Host "`n[5/7] Installing OpenClaw skills..." -ForegroundColor Yellow
openclaw skills install tavily
openclaw skills install free-ride
openclaw skills install browser-automation
openclaw skills install self-improving
openclaw skills install evoclaw

# 6. Install FreeRide CLI
Write-Host "`n[6/7] Installing FreeRide CLI..." -ForegroundColor Yellow
Set-Location "C:\Users\thada\.openclaw\workspace\skills\free-ride"
& "C:\Python314\python.exe" -m pip install -e . --quiet

# 7. Install Tavily Python package
Write-Host "`n[7/7] Installing Tavily Python package..." -ForegroundColor Yellow
& "C:\Python314\python.exe" -m pip install tavily-python --quiet

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Restart the OpenClaw gateway: openclaw gateway restart" -ForegroundColor Cyan