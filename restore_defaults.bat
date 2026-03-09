@echo off
title SYSTEM_RESTORE_PRO_V4
color 0C
echo.
echo  =========================================
echo     NEURAL LINK - SYSTEM RESTORE ENGINE
echo  =========================================
echo.

echo  [*] Reading current mouse settings...
reg query "HKCU\Control Panel\Mouse" /v MouseSpeed
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold1
reg query "HKCU\Control Panel\Mouse" /v MouseThreshold2
reg query "HKCU\Control Panel\Mouse" /v MouseSensitivity
echo.

echo  -----------------------------------------
echo     RESTORING DEFAULTS...
echo  -----------------------------------------
echo.

echo  [1/5] Restoring MouseSensitivity = 10
reg add "HKCU\Control Panel\Mouse" /v "MouseSensitivity" /t REG_SZ /d "10" /f
echo.

echo  [2/5] Restoring MouseSpeed = 1 (Acceleration ON)
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f
echo.

echo  [3/5] Restoring MouseThreshold1 = 6
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "6" /f
echo.

echo  [4/5] Restoring MouseThreshold2 = 10
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "10" /f
echo.

echo  [5/5] Resetting Mouse Trails
reg add "HKCU\Control Panel\Mouse" /v "MouseTrails" /t REG_SZ /d "0" /f
echo.

echo  -----------------------------------------
echo     APPLYING INSTANT REFRESH (SPI_SETMOUSE)
echo  -----------------------------------------
echo.
powershell -command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, int[] pvParam, uint fWinIni); }'; $result = [Win32]::SystemParametersInfo(0x0004, 0, @(6, 10, 1), 3); if($result){'  [SUCCESS] Enhance Pointer Precision = DEFAULT (Applied Instantly)'}else{'  [FAILED] Could not apply SPI_SETMOUSE'}"
echo.

echo  -----------------------------------------
echo     RESTORING BALANCED POWER PLAN
echo  -----------------------------------------
powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e 2>nul && echo  [SUCCESS] Balanced Power Plan Active || echo  [INFO] Power plan unchanged

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
echo     SYSTEM DEFAULTS RESTORED
echo     Acceleration: DEFAULT
echo     Pointer Precision: DEFAULT
echo     Power Plan: BALANCED
echo  =========================================
echo.
echo  You can close this window now.
echo.
pause
