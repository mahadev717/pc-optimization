@echo off
title AIM_OPTIMIZER_PRO_V4
color 0A
echo.
echo  =========================================
echo     NEURAL LINK - AIM OPTIMIZER ENGINE
echo  =========================================
echo.

echo  [*] Reading current mouse settings...
reg query "HKCU\Control Panel\Mouse" /v MouseSpeed
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold1
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold2
reg query "HKCU\Control Panel\Mouse" /v MouseSensitivity
echo.

echo  -----------------------------------------
echo     APPLYING OPTIMIZATIONS...
echo  -----------------------------------------
echo.

echo  [1/5] Setting MouseSensitivity = 10 (RAW 1:1)
reg add "HKCU\Control Panel\Mouse" /v "MouseSensitivity" /t REG_SZ /d "10" /f
echo.

echo  [2/5] Setting MouseSpeed = 0 (Acceleration OFF)
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f
echo.

echo  [3/5] Setting MouseThreshold1 = 0
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f
echo.

echo  [4/5] Setting MouseThreshold2 = 0
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f
echo.

echo  [5/5] Disabling Mouse Trails
reg add "HKCU\Control Panel\Mouse" /v "MouseTrails" /t REG_SZ /d "0" /f
echo.

echo  -----------------------------------------
echo     APPLYING INSTANT REFRESH (SPI_SETMOUSE)
echo  -----------------------------------------
echo.
powershell -command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, int[] pvParam, uint fWinIni); }'; $result = [Win32]::SystemParametersInfo(0x0004, 0, @(0, 0, 0), 3); if($result){'  [SUCCESS] Enhance Pointer Precision = OFF (Applied Instantly)'}else{'  [FAILED] Could not apply SPI_SETMOUSE'}"
echo.

echo  -----------------------------------------
echo     SWITCHING TO HIGH PERFORMANCE POWER PLAN
echo  -----------------------------------------
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>nul && echo  [SUCCESS] High Performance Power Plan Active || echo  [INFO] Power plan unchanged

echo.
echo  -----------------------------------------
echo     VERIFYING CHANGES...
echo  -----------------------------------------
echo.
reg query "HKCU\Control Panel\Mouse" /v MouseSpeed
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold1
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold2
reg query "HKCU\Control Panel\Mouse" /v MouseSensitivity
echo.
echo  =========================================
echo     ALL OPTIMIZATIONS APPLIED
echo     Acceleration: OFF
echo     Pointer Precision: OFF
echo     Input Latency: MINIMAL
echo  =========================================
echo.
echo  You can close this window now.
echo.
pause
