@echo off
:: Launcher for cleanup-services.ps1 (runs as admin)
echo This will stop Dell/Intel bloatware services to free ~1.6GB RAM
echo.
powershell -ExecutionPolicy Bypass -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File ""%~dp0cleanup-services.ps1""' -Verb RunAs"
pause
