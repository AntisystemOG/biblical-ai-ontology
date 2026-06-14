@echo off
echo ========================================================
echo  🔧 PLCTools Coder Launcher
echo ========================================================
echo.

echo [1/3] Spawning PLCTools Coder agent...
echo Working directory: C:\Users\thadd\.openclaw\workspace
cd /d "C:\Users\thadd\.openclaw\workspace"

REM Use full path to openclaw.cmd to avoid any path issues
set "OPENCLAW=C:\Users\thadd\AppData\Roaming\npm\openclaw.cmd"

echo Running: %OPENCLAW% sessions spawn ...

REM Run the spawn command
"%OPENCLAW%" sessions spawn --label plctool-coder --mode run --runtime subagent --task "Spawn PLCTools coding assistant"

set "EXITCODE=%ERRORLEVEL%"
echo.
echo Exit code: %EXITCODE%

if %EXITCODE% NEQ 0 (
    echo.
    echo ERROR: Failed to spawn agent.
    echo.
    echo Troubleshooting:
    echo 1. Check if gateway is running: openclaw status
    echo 2. Check if openclaw is installed: where openclaw
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Waiting for agent to initialize...
timeout /t 2 /nobreak > nul

echo.
echo [3/3] Opening Control UI...
start "" "http://127.0.0.1:18789/"

echo.
echo ========================================================
echo  Done! Check your browser for the chat window.
echo ========================================================
echo.
timeout /t 5