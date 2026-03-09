@echo off
title HACKER CONTROL CENTER - SERVER
color 0B
echo.
echo  =========================================
echo     HACKER CONTROL CENTER v5.0
echo  =========================================
echo.

cd /d "%~dp0"

echo  [*] Killing old server processes on port 5050...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5050.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo  [*] Port 5050 cleared.
echo.

echo  [*] Checking Python...
python --version
if %errorLevel% neq 0 (
    echo  [ERROR] Python not found! Install Python first.
    pause
    exit /b
)

echo  [*] Checking Flask...
python -c "import flask" 2>nul
if %errorLevel% neq 0 (
    echo  [WARN] Flask not installed. Installing now...
    pip install flask flask-cors
)

echo.
echo  [*] Starting server on http://127.0.0.1:5050
echo  [*] Opening browser...
echo  [*] DO NOT CLOSE THIS WINDOW
echo  =========================================
echo.

start "" http://127.0.0.1:5050
python server.py
pause
