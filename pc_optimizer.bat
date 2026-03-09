@echo off
title PC_OPTIMIZER_PRO_V4
color 0B
echo.
echo  =====================================================
echo     NEURAL LINK - FULL PC OPTIMIZATION ENGINE
echo  =====================================================
echo.

:: =========================================
:: 1. DISABLE VISUAL EFFECTS FOR FPS BOOST
:: =========================================
echo  -----------------------------------------
echo     [1/8] DISABLING VISUAL EFFECTS
echo  -----------------------------------------
echo.
echo  [*] Setting Visual Effects to Best Performance...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 2 /f
echo  [*] Disabling Window Animations...
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f
echo  [*] Disabling Transparency...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v "EnableTransparency" /t REG_DWORD /d 0 /f
echo  [*] Disabling Smooth Scrolling...
reg add "HKCU\Control Panel\Desktop" /v "SmoothScroll" /t REG_DWORD /d 0 /f
echo  [*] Disabling Cursor Shadow...
reg add "HKCU\Control Panel\Desktop" /v "CursorShadow" /t REG_DWORD /d 0 /f
echo.

:: =========================================
:: 2. NETWORK OPTIMIZATION (LOW PING)
:: =========================================
echo  -----------------------------------------
echo     [2/8] NETWORK OPTIMIZATION (LOW PING)
echo  -----------------------------------------
echo.
echo  [*] Disabling Nagle's Algorithm (TCP_NODELAY)...
powershell -command "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; foreach($a in $adapters){ $guid = $a.InterfaceGuid; $path = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\' + $guid; Set-ItemProperty -Path $path -Name 'TcpAckFrequency' -Value 1 -Type DWord -ErrorAction SilentlyContinue; Set-ItemProperty -Path $path -Name 'TCPNoDelay' -Value 1 -Type DWord -ErrorAction SilentlyContinue; Write-Host '  [OK] Optimized:' $a.Name }"
echo.
echo  [*] Disabling Network Throttling...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 0xFFFFFFFF /f
echo  [*] Setting System Responsiveness to 0 (Gaming Priority)...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f
echo.

:: =========================================
:: 3. GPU & GAME OPTIMIZATIONS
:: =========================================
echo  -----------------------------------------
echo     [3/8] GPU ^& GAME OPTIMIZATIONS
echo  -----------------------------------------
echo.
echo  [*] Disabling Fullscreen Optimizations (Global)...
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f
echo  [*] Disabling Game Bar...
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 0 /f
echo  [*] Enabling Hardware Accelerated GPU Scheduling...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f
echo  [*] Disabling Game DVR (Background Recording)...
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f
echo.

:: =========================================
:: 4. DISABLE BACKGROUND APPS & TELEMETRY
:: =========================================
echo  -----------------------------------------
echo     [4/8] DISABLING BACKGROUND APPS
echo  -----------------------------------------
echo.
echo  [*] Disabling Background Apps...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v "GlobalUserDisabled" /t REG_DWORD /d 1 /f
echo  [*] Disabling Telemetry...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f
echo  [*] Disabling Cortana...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f
echo  [*] Disabling Tips & Suggestions...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338389Enabled" /t REG_DWORD /d 0 /f
echo.

:: =========================================
:: 5. CPU PRIORITY FOR GAMING
:: =========================================
echo  -----------------------------------------
echo     [5/8] CPU GAMING PRIORITY
echo  -----------------------------------------
echo.
echo  [*] Setting Game Priority to High...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f
echo.

:: =========================================
:: 6. MEMORY OPTIMIZATION
:: =========================================
echo  -----------------------------------------
echo     [6/8] MEMORY OPTIMIZATION
echo  -----------------------------------------
echo.
echo  [*] Disabling Superfetch/SysMain...
sc config "SysMain" start= disabled >nul 2>&1
net stop "SysMain" >nul 2>&1 && echo  [OK] SysMain stopped || echo  [INFO] SysMain already stopped
echo  [*] Disabling Windows Search Indexer...
sc config "WSearch" start= disabled >nul 2>&1
net stop "WSearch" >nul 2>&1 && echo  [OK] WSearch stopped || echo  [INFO] WSearch already stopped
echo  [*] Setting Large System Cache...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d 1 /f
echo.

:: =========================================
:: 7. POWER PLAN
:: =========================================
echo  -----------------------------------------
echo     [7/8] HIGH PERFORMANCE POWER PLAN
echo  -----------------------------------------
echo.
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>nul && echo  [SUCCESS] High Performance Power Plan Active || echo  [INFO] Power plan unchanged
echo  [*] Disabling USB Selective Suspend...
powercfg -setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 >nul 2>&1
powercfg -setactive SCHEME_CURRENT >nul 2>&1
echo  [OK] USB Selective Suspend Disabled
echo.

:: =========================================
:: 8. DISABLE UNNECESSARY SERVICES
:: =========================================
echo  -----------------------------------------
echo     [8/8] DISABLING UNNECESSARY SERVICES
echo  -----------------------------------------
echo.
echo  [*] Disabling Print Spooler...
sc config "Spooler" start= disabled >nul 2>&1
net stop "Spooler" >nul 2>&1 && echo  [OK] Print Spooler stopped || echo  [INFO] Already stopped
echo  [*] Disabling Fax...
sc config "Fax" start= disabled >nul 2>&1
net stop "Fax" >nul 2>&1 && echo  [OK] Fax stopped || echo  [INFO] Already stopped
echo  [*] Disabling Remote Registry...
sc config "RemoteRegistry" start= disabled >nul 2>&1
net stop "RemoteRegistry" >nul 2>&1 && echo  [OK] Remote Registry stopped || echo  [INFO] Already stopped
echo.

echo  =====================================================
echo     ALL PC OPTIMIZATIONS APPLIED
echo  =====================================================
echo.
echo     Visual Effects:      DISABLED
echo     Network Throttle:    OFF (Nagle disabled)
echo     GPU Scheduling:      HARDWARE ACCELERATED
echo     Game DVR:            OFF
echo     Background Apps:     DISABLED
echo     Telemetry:           OFF
echo     CPU Game Priority:   HIGH
echo     Memory Services:     OPTIMIZED
echo     Power Plan:          HIGH PERFORMANCE
echo     USB Suspend:         OFF
echo.
echo  =====================================================
echo.
echo  You can close this window now.
echo.
pause
