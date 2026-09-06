@echo off
REM gateway-watchdog.bat
REM Starts the gateway watchdog (checks every 5 min)

echo Starting Gateway Watchdog...
echo Press Ctrl+C to stop.

powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0gateway-watchdog.ps1"

pause