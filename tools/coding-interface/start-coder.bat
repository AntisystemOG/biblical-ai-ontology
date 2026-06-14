@echo off
chcp 65001 >nul
title Coder Interface Server
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Starting Coder Interface...                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
cd /d "%~dp0"
echo Working directory: %cd%
echo.
echo Starting server on http://localhost:18790
echo.
echo The browser will open automatically when ready...
echo Press Ctrl+C to stop the server
echo.

:: Start the server
python server.py
