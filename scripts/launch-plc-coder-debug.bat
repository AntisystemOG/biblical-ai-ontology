@echo off
echo ========================================================
echo  🔧 PLCTools Coder Launcher (Debug Mode)
echo ========================================================
echo.
echo Current directory: %CD%
echo Time: %TIME%
echo.

echo [1/3] Spawning PLCTools Coder agent...
cd /d "C:\Users\thadd\.openclaw\workspace"
echo Changed to: %CD%
echo.

REM Use full path
echo Running openclaw command...
"C:\Users\thadd\AppData\Roaming\npm\openclaw.cmd" sessions spawn --label plctool-coder --mode run --runtime subagent --task "Spawn PLCTools coding assistant" 2>&1

echo.
echo Command completed. Exit code: %ERRORLEVEL%
echo.

REM Always pause so we can see what happened
pause

exit /b 0