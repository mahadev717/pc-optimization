@echo off
title NEURAL LINK - BUILDER
color 0B
echo.
echo  =========================================
echo    BUILDING NATIVE ADMIN EXECUTABLE...
echo  =========================================
echo.

set "CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

if not exist "%CSC_PATH%" (
    echo [ERROR] C# Compiler not found! Falling back to backup launcher...
    pause
    exit /b
)

"%CSC_PATH%" /target:winexe /out:optimize.exe /reference:System.Windows.Forms.dll /reference:System.dll launcher.cs

if %errorlevel% equ 0 (
    echo.
    echo  [SUCCESS] NeuralLink.exe generated!
    echo.
) else (
    echo.
    echo  [ERROR] Compilation failed.
    echo.
)
pause
