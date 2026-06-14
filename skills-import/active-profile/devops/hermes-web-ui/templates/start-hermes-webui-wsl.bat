@echo off
REM Start Hermes Web UI on WSL and open browser
REM Node 26 server at ~/hermes-web-ui-ekko/dist/server/index.js

REM === CONFIG ===
REM Set AUTH_DISABLED=1 before starting the server to skip login.
REM When AUTH_DISABLED is set, remove the `/#/?token=... fragment from the URL.
REM When auth IS enabled, fill in TOKEN below and keep the `/#/?token=... URL.

set WSL_IP=172.24.60.180
set PORT=8648

REM Set TOKEN only when auth is enabled; leave blank when AUTH_DISABLED=1
set TOKEN=

REM Optional: append token when auth is on; leave empty when auth is disabled
if defined TOKEN (
    set URL_SUFFIX=`/#/?token=%TOKEN%
) else (
    set URL_SUFFIX=
)

echo Starting Hermes Web UI...

REM Check if already running
wsl ss -tlnp 2^>nul ^| findstr ":%PORT%" ^>nul
if %errorlevel% == 0 (
    echo Web UI already running.
    start http://%WSL_IP%:%PORT%%URL_SUFFIX%
    exit /b 0
)

REM Start the Web UI server in background via WSL
REM CRITICAL: Use wsl bash -c with nohup. The old ^> /dev/null 2^>^&1 ^& pattern
REM fails because ^ escapes are CMD-only; wsl passes them literally to bash.
wsl bash -c "export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=%PORT% BIND_HOST=0.0.0.0 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace AUTH_DISABLED=1; nohup /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js > /dev/null 2>&1 &"

REM Wait 5 seconds for startup
timeout /t 5 /nobreak ^>nul

REM Open browser
echo Opening http://%WSL_IP%:%PORT%...
start http://%WSL_IP%:%PORT%%URL_SUFFIX%

REM Keep window open briefly so user sees status, then auto-close
timeout /t 3 /nobreak ^>nul
exit /b 0
