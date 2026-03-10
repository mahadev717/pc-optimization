@echo off
title HACKER CONTROL CENTER - SERVER
color 0B
echo.
echo  =========================================
echo     HACKER CONTROL CENTER v6.0
echo  =========================================
echo.

cd /d "%~dp0"

echo  [*] Killing old server processes on port 5050...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5050.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo  [*] Port 5050 cleared.
echo.

echo  [*] Checking Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  [ERROR] Download from https://python.org and install.
    echo  [ERROR] Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  [*] Installing/verifying Flask...
pip install flask flask-cors --quiet --disable-pip-version-check
echo  [*] Flask ready.
echo.

echo  [*] Starting server...
echo  [*] DO NOT CLOSE THIS WINDOW
echo  =========================================
echo.

REM Start server in the background
start /B python server.py

REM Wait until port 5050 is actually listening (max 30 seconds)
echo  [*] Waiting for server to be ready...
set /a TRIES=0
:WAIT_LOOP
    netstat -ano 2>nul | findstr ":5050.*LISTENING" >nul 2>&1
    if %errorLevel% == 0 goto SERVER_READY
    set /a TRIES+=1
    if %TRIES% GEQ 30 goto TIMEOUT
    timeout /t 1 /nobreak >nul
    goto WAIT_LOOP

:TIMEOUT
    echo  [ERROR] Server did not start after 30 seconds.
    echo  [ERROR] Check that Python and Flask are installed correctly.
    pause
    exit /b 1

:SERVER_READY
echo  [*] Server is ONLINE. Opening browser...
start "" http://127.0.0.1:5050

echo.
echo  [*] Running. Keep this window open.
echo  [*] Press Ctrl+C to stop the server.
echo.

REM Keep window alive (server runs in background via start /B)
:KEEP_ALIVE
    timeout /t 5 /nobreak >nul
    netstat -ano 2>nul | findstr ":5050.*LISTENING" >nul 2>&1
    if %errorLevel% neq 0 (
        echo  [!] Server stopped unexpectedly.
        pause
        exit /b
    )
    goto KEEP_ALIVE
