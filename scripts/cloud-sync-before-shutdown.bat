@echo off
REM cloud-sync-before-shutdown.bat
REM Run this before shutting down to ensure OneDrive sync completes

echo === Cloud Sync Before Shutdown ===
echo.

echo Starting OneDrive sync...
start "" "OneDrive.exe" /sync

echo.
echo Waiting for sync...
echo Close this window when done, or press Ctrl+C to cancel

timeout /t 30 /nobreak

echo.
echo Sync attempt complete.
echo You can now shutdown safely.
pause