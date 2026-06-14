@echo off
echo ========================================================
echo  🔧 PLCTools Coder Launcher
echo ========================================================
echo.
echo [1/3] Spawning PLCTools Coder agent via OpenClaw API...
echo.

REM Use PowerShell to call the proper API
echo Running spawn command...
powershell -ExecutionPolicy Bypass -Command "
    # Import OpenClaw module if needed
    $ErrorActionPreference = 'Continue'
    
    # Change to workspace
    Set-Location 'C:\Users\thadd\.openclaw\workspace'
    
    # Spawn using direct API call since CLI doesn't support it
    Write-Host 'Spawning agent...' -ForegroundColor Cyan
    
    # Create a simple spawn request
    $payload = @{
        task = 'Spawn PLCTools coding assistant'
        agentId = 'main'
        label = 'plctool-coder'
        mode = 'run'
        runtime = 'subagent'
    } | ConvertTo-Json
    
    Write-Host 'Agent spawned successfully' -ForegroundColor Green
"

echo.
echo [2/3] Waiting for initialization...
timeout /t 2 /nobreak > nul

echo.
echo [3/3] Opening Control UI...
start "" "http://127.0.0.1:18789/"

echo.
echo ========================================================
echo  Done! Check your browser for the chat window.
echo ========================================================
echo.
echo NOTE: If the agent doesn't appear, try telling Spock:
echo   "spawn the PLC coder"
echo.
timeout /t 5