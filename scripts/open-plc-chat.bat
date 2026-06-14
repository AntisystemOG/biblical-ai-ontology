@echo off
echo ========================================================
echo  🔧 PLCTools Coder Launcher
echo ========================================================
echo.
echo This will open the Control UI where you can type:
echo.
echo     spawn the PLC coder
echo.
echo Or simply start typing your coding request.
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak > nul

echo Opening Control UI...
start "" "http://127.0.0.1:18789/"

echo.
echo ========================================================
echo  Done! Switch to your browser to continue.
echo ========================================================