@echo off
title PC_RESTORE_PRO_V4
color 0E
echo.
echo  =====================================================
echo     NEURAL LINK - PC RESTORE ENGINE
echo  =====================================================
echo.

echo  -----------------------------------------
echo     [1/8] RESTORING VISUAL EFFECTS
echo  -----------------------------------------
echo.
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 0 /f
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "1" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v "EnableTransparency" /t REG_DWORD /d 1 /f
reg delete "HKCU\Control Panel\Desktop" /v "SmoothScroll" /f >nul 2>&1
reg delete "HKCU\Control Panel\Desktop" /v "CursorShadow" /f >nul 2>&1
echo  [OK] Visual effects restored
echo.

echo  -----------------------------------------
echo     [2/8] RESTORING NETWORK DEFAULTS
echo  -----------------------------------------
echo.
powershell -command "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; foreach($a in $adapters){ $guid = $a.InterfaceGuid; $path = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\' + $guid; Remove-ItemProperty -Path $path -Name 'TcpAckFrequency' -ErrorAction SilentlyContinue; Remove-ItemProperty -Path $path -Name 'TCPNoDelay' -ErrorAction SilentlyContinue; Write-Host '  [OK] Restored:' $a.Name }"
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 10 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 20 /f
echo  [OK] Network defaults restored
echo.

echo  -----------------------------------------
echo     [3/8] RESTORING GPU ^& GAME SETTINGS
echo  -----------------------------------------
echo.
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 1 /f
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /f >nul 2>&1
echo  [OK] GPU/Game settings restored
echo.

echo  -----------------------------------------
echo     [4/8] RESTORING BACKGROUND APPS
echo  -----------------------------------------
echo.
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v "GlobalUserDisabled" /t REG_DWORD /d 0 /f
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338389Enabled" /f >nul 2>&1
echo  [OK] Background apps restored
echo.

echo  -----------------------------------------
echo     [5/8] RESTORING CPU PRIORITY
echo  -----------------------------------------
echo.
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 2 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 2 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "Medium" /f
echo  [OK] CPU priority restored
echo.

echo  -----------------------------------------
echo     [6/8] RESTORING MEMORY SERVICES
echo  -----------------------------------------
echo.
sc config "SysMain" start= auto >nul 2>&1
net start "SysMain" >nul 2>&1 && echo  [OK] SysMain started || echo  [INFO] SysMain already running
sc config "WSearch" start= delayed-auto >nul 2>&1
net start "WSearch" >nul 2>&1 && echo  [OK] WSearch started || echo  [INFO] WSearch already running
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d 0 /f
echo.

echo  -----------------------------------------
echo     [7/8] RESTORING BALANCED POWER PLAN
echo  -----------------------------------------
echo.
powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e 2>nul && echo  [SUCCESS] Balanced Power Plan Active || echo  [INFO] Power plan unchanged
powercfg -setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 1 >nul 2>&1
powercfg -setactive SCHEME_CURRENT >nul 2>&1
echo  [OK] USB Selective Suspend Enabled
echo.

echo  -----------------------------------------
echo     [8/8] RESTORING SERVICES
echo  -----------------------------------------
echo.
sc config "Spooler" start= auto >nul 2>&1
net start "Spooler" >nul 2>&1 && echo  [OK] Print Spooler started || echo  [INFO] Already running
sc config "Fax" start= auto >nul 2>&1
echo  [OK] Fax service restored
echo.

echo  =====================================================
echo     ALL PC SETTINGS RESTORED TO DEFAULTS
echo  =====================================================
echo.
echo     Visual Effects:      DEFAULT
echo     Network:             DEFAULT
echo     GPU/Game:            DEFAULT
echo     Background Apps:     ENABLED
echo     Telemetry:           DEFAULT
echo     CPU Priority:        DEFAULT
echo     Memory Services:     RUNNING
echo     Power Plan:          BALANCED
echo.
echo  =====================================================
echo.
echo  NOTE: Some changes require a RESTART to fully apply.
echo.
pause
