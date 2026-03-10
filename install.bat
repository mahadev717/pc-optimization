@echo off
setlocal
title HACKER CONTROL CENTER - INSTALLER
color 0B

:: Force working directory to where the bat file is located
cd /d "%~dp0"

echo.
echo  =====================================================
echo     HACKER CONTROL CENTER - ONE CLICK INSTALLER
echo  =====================================================
echo.
echo  This will install everything needed to run the tool.
echo  Press any key to start installation...
echo.
pause
echo.
echo  [*] Starting installation...
echo.

:: =========================================
:: 1. CHECK/INSTALL PYTHON
:: =========================================
echo  -----------------------------------------
echo     [1/4] CHECKING PYTHON
echo  -----------------------------------------
echo.
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Python not found. Downloading Python 3.12...
    echo  [*] This may take a few minutes...
    echo.
    powershell -command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    if not exist "%TEMP%\python_installer.exe" (
        echo.
        echo  [ERROR] Failed to download Python.
        echo  Please install Python manually from https://www.python.org
        echo  IMPORTANT: Check "Add Python to PATH" during installation!
        echo.
        pause
        exit /b
    )
    echo  [*] Installing Python 3.12 silently...
    echo  [*] Please wait, this takes 1-2 minutes...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    echo.
    echo  [*] Refreshing PATH...
    set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
    echo  [OK] Python installed successfully
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v already installed
)
echo.

:: =========================================
:: 2. INSTALL PIP PACKAGES
:: =========================================
echo  -----------------------------------------
echo     [2/4] INSTALLING PYTHON PACKAGES
echo  -----------------------------------------
echo.
echo  [*] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo  [*] Installing Flask...
python -m pip install flask
echo.
echo  [*] Installing Flask-CORS...
python -m pip install flask-cors
echo.

:: =========================================
:: 3. CHECK .NET FRAMEWORK (for optimize.exe)
:: =========================================
echo  -----------------------------------------
echo     [3/4] CHECKING .NET FRAMEWORK
echo  -----------------------------------------
echo.
reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Release >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] .NET Framework 4.x not found. Downloading...
    powershell -command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/?LinkId=2085155' -OutFile '%TEMP%\dotnet_installer.exe'"
    if exist "%TEMP%\dotnet_installer.exe" (
        echo  [*] Installing .NET Framework...
        "%TEMP%\dotnet_installer.exe" /quiet /norestart
        echo  [OK] .NET Framework installed
    ) else (
        echo  [WARN] Could not download .NET installer
        echo  You can still use run_server.bat without optimize.exe
    )
) else (
    echo  [OK] .NET Framework already installed
)
echo.

:: =========================================
:: 4. COMPILE optimize.exe
:: =========================================
echo  -----------------------------------------
echo     [4/4] BUILDING OPTIMIZE.EXE
echo  -----------------------------------------
echo.
if exist "%~dp0launcher.cs" (
    set "CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" (
        echo  [*] Compiling optimize.exe...
        C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:winexe /out:"%~dp0optimize.exe" /reference:System.Windows.Forms.dll /reference:System.dll "%~dp0launcher.cs"
        if exist "%~dp0optimize.exe" (
            echo  [OK] optimize.exe compiled successfully
        ) else (
            echo  [WARN] Compilation failed - use run_server.bat instead
        )
    ) else (
        echo  [INFO] C# compiler not found - using pre-built optimize.exe
    )
) else (
    if exist "%~dp0optimize.exe" (
        echo  [OK] Using pre-built optimize.exe
    ) else (
        echo  [INFO] No launcher.cs found - use run_server.bat to start
    )
)
echo.

:: =========================================
:: VERIFY INSTALLATION
:: =========================================
echo  =====================================================
echo     VERIFYING INSTALLATION
echo  =====================================================
echo.

python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo  [OK] Python .............. READY
) else (
    echo  [X]  Python .............. MISSING
)

python -c "import flask" >nul 2>&1
if %errorLevel% equ 0 (
    echo  [OK] Flask ............... READY
) else (
    echo  [X]  Flask ............... MISSING
)

python -c "import flask_cors" >nul 2>&1
if %errorLevel% equ 0 (
    echo  [OK] Flask-CORS .......... READY
) else (
    echo  [X]  Flask-CORS .......... MISSING
)

if exist "%~dp0optimize.exe" (
    echo  [OK] optimize.exe ........ READY
) else (
    echo  [--] optimize.exe ........ NOT FOUND (use run_server.bat)
)

if exist "%~dp0server.py" (
    echo  [OK] server.py ........... READY
) else (
    echo  [X]  server.py ........... MISSING
)

if exist "%~dp0run_server.bat" (
    echo  [OK] run_server.bat ...... READY
) else (
    echo  [X]  run_server.bat ...... MISSING
)

echo.
echo  =====================================================
echo     INSTALLATION COMPLETE!
echo.
echo     To start the tool:
echo       Option 1: Double-click optimize.exe
echo       Option 2: Right-click run_server.bat - Run as Admin
echo  =====================================================
echo.
echo  Press any key to exit...
pause >nul
