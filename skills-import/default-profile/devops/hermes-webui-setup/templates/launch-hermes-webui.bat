@echo off
setlocal EnableDelayedExpansion

:: =============================================================================
:: Hermes WebUI Launcher (EKKOLearnAI repo)
:: =============================================================================
:: Target: C:\Users\thadd\Desktop\Launch Hermes WebUI.bat
:: Purpose: Check if server is running on 8648; start it if not; open browser.
::
:: This is the DEBUG-FIRST launcher. It is visible (not hidden) so you can see
:: status messages and errors. Once it works reliably, upgrade to a silent .lnk.
::
:: If AUTH_DISABLED=1 is set in WSL ~/.hermes/.env, the browser opens directly.
:: If auth is enabled, this .bat auto-injects the token from ~/.hermes-web-ui/.token.
:: =============================================================================

echo Checking Hermes WebUI on port 8648...

:: ---------------------------------------------------------------------------
:: Check if server is already running (health endpoint)
:: ---------------------------------------------------------------------------
curl -sf http://127.0.0.1:8648/health >nul 2>nul
if %errorlevel% == 0 (
    echo Server already running — opening browser...
    goto OPEN_BROWSER
)

:: ---------------------------------------------------------------------------
:: Server not running — start it via WSL
:: ---------------------------------------------------------------------------
echo Starting Hermes WebUI server...
wsl bash -lc "cd /mnt/c/Users/thadd/hermes-web-ui && nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &"

:: ---------------------------------------------------------------------------
:: Poll health endpoint up to 30 seconds
:: ---------------------------------------------------------------------------
echo Waiting for server to start...
set RETRIES=0
:WAIT_LOOP
    timeout /t 1 /nobreak >nul
    curl -sf http://127.0.0.1:8648/health >nul 2>nul
    if %errorlevel% == 0 goto OPEN_BROWSER
    set /a RETRIES+=1
    if !RETRIES! lss 30 goto WAIT_LOOP

echo ERROR: Server failed to start within 30 seconds.
echo Check logs: wsl tail -n 20 ~/.hermes-web-ui/server.log
pause
exit /b 1

:: ---------------------------------------------------------------------------
:: Open browser — with token injection if auth is enabled
:: ---------------------------------------------------------------------------
:OPEN_BROWSER
for /f "delims=" %%a in ('wsl cat ~/.hermes-web-ui/.token') do (
    set TOKEN=%%a
    goto GOT_TOKEN
)
:GOT_TOKEN
set TOKEN=!TOKEN: =!
if "!TOKEN!"=="" (
    echo Opening http://localhost:8648/
    start http://localhost:8648/
) else (
    echo Opening http://localhost:8648/?token=...
    start "http://localhost:8648/?token=!TOKEN!"
)
exit /b 0
