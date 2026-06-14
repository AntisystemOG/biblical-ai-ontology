@echo off
REM Start EKKOLearnAI Hermes WebUI on WSL and open browser

set WSL_IP=172.24.60.180
set PORT=8648

echo Checking WebUI status...

wsl bash -c "curl -s http://127.0.0.1:%PORT%/ | grep -q 'Spock'"
if %errorlevel% == 0 (
    echo WebUI is running. Opening browser...
    start http://%WSL_IP%:%PORT%/
    exit /b 0
)

echo Starting WebUI server in WSL...
wsl bash -c "cd /home/thadd/hermes-web-ui-ekko && export PORT=%PORT% BIND_HOST=0.0.0.0 AUTH_DISABLED=1 HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace && nohup /home/thadd/node26/bin/node dist/server/index.js > /dev/null 2>&1 &"

echo Waiting for server startup...
timeout /t 5 /nobreak >nul

echo Opening http://%WSL_IP%:%PORT%...
start http://%WSL_IP%:%PORT%/

timeout /t 2 /nobreak >nul
exit /b 0
