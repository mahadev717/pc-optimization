@echo off
setlocal
title Free Fire Headshot Optimizer - LOGIN
color 0B

:LOGIN_SCREEN
cls
echo.
echo  =========================================
echo       S E N S I   M A S T E R   V 1.0
echo  =========================================
echo.
echo           [ LOGIN REQUIRED ]
echo.
set /p "user=Username: "
set /p "pass=Password: "

:: --- SECURITY CONFIGURATION ---
set "correct_user=1"
set "correct_pass=1"
:: ------------------------------

if "%user%"=="%correct_user%" (
    if "%pass%"=="%correct_pass%" (
        goto SUCCESS
    )
)

:FAIL
cls
color 0C
echo.
echo  [ ERROR ] Invalid Username or Password!
echo.
pause
color 0B
goto LOGIN_SCREEN

:SUCCESS
cls
color 0A
echo.
echo  =========================================
echo       L O G I N   S U C C E S S F U L
echo  =========================================
echo.
echo  Welcome, %user%!
echo  Initializing headshot optimization modules...
echo.
timeout /t 2 >nul

:MENU
cls
echo  =========================================
echo         M A I N   M E N U
echo  =========================================
echo.
echo  1. Launch 3D Neural Link (Web API)
echo  2. Apply Mouse Registry Fix
echo  3. Open Sensitivity Guide
echo  4. Exit
echo.
set /p "choice=Select an option: "

if "%choice%"=="1" (
    echo Starting Python Server...
    start python server.py
    timeout /t 3 >nul
    start http://127.0.0.1:5000
    goto MENU
)

if "%choice%"=="2" (
    echo Applying registry fix...
    start "" "mouse_optimizer.reg"
    goto MENU
)

if "%choice%"=="3" (
    start notepad "headshot_guide.md"
    goto MENU
)

if "%choice%"=="4" exit

goto MENU
