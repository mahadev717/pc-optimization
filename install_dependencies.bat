@echo off
title NEURAL_LINK | DEEP_CORE_INSTALLER
color 0B
echo.
echo  ================================================
echo     NEURAL LINK | DEPENDENCY DEPLOYMENT v2.1
echo  ================================================
echo.

:: 1. Check for Admin Privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] ERROR: PLEASE RUN THIS AS ADMINISTRATOR.
    echo.
    pause
    exit /b 1
)

echo  [*] INITIATING DEPCORE_SCAN...
echo.

:: 2. Enable .NET Framework 4.8 (Standard for optimize.exe)
echo  [*] ENABLING .NET_FRAMEWORK_4.8 FEATURES...
dism /online /Enable-Feature /FeatureName:NetFx4-AdvSrvs /All /NoRestart /Quiet
if %errorLevel% equ 0 (
    echo  [SUCCESS] .NET_CORE_4.8_ACTIVE
) else (
    echo  [WARN] .NET_4.8_ALREADY_ACTIVE_OR_PENDING
)

:: 3. Enable .NET Framework 3.5 (Legacy Support)
echo  [*] ENABLING .NET_FRAMEWORK_3.5 (LEGACY)...
dism /online /Enable-Feature /FeatureName:NetFx3 /All /NoRestart /Quiet
if %errorLevel% equ 0 (
    echo  [SUCCESS] .NET_CORE_3.5_ACTIVE
) else (
    echo  [WARN] .NET_3.5_NOT_FOUND_ON_CORE_IMAGE (WINDOWS_UPDATE_MAY_BE_REQUIRED)
)

:: 4. Verify/Install Python Requirements
echo.
echo  [*] SYNCING_PYTHON_NEURAL_UPLINK...
pip install -r requirements.txt --quiet
if %errorLevel% equ 0 (
    echo  [SUCCESS] PYTHON_LIBRARIES_SYNCED
) else (
    echo  [!] ERROR: PIP_SYNC_FAILED. VERIFY PYTHON INSTALLATION.
)

echo.
echo  ================================================
echo     DEPLOYMENT_COMPLETE | SYSTEM_OPTIMIZED
echo  ================================================
echo.
echo  System is now ready for Neural Link Deployment.
echo.
pause
exit /b 0
