@echo off
REM 🔧 PLCTools Coder Launcher
REM Spawns the PLC Coder agent and opens the chat window

echo Spawning PLCTools Coder agent...
cd /d "C:\Users\thadd\.openclaw\workspace"
powershell -ExecutionPolicy Bypass -Command "openclaw sessions spawn --label plctool-coder --mode run --runtime subagent --task 'Spawn PLCTools coding assistant'"

timeout /t 3 /nobreak > nul

echo Opening Control UI...
start "" "http://127.0.0.1:18789/"

echo Done! Check your browser for the chat window.