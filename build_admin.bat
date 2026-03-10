@echo off
echo ============================================
echo   BUILDING admin.exe
echo   Supabase Admin Dashboard
echo ============================================
echo.

pip install pyinstaller supabase --quiet --disable-pip-version-check 2>nul

echo [BUILD] Creating admin.exe...
pyinstaller --onefile --noconsole --name admin admin_dashboard.py --clean -y --hidden-import=supabase --hidden-import=postgrest --hidden-import=gotrue --hidden-import=realtime --hidden-import=storage3 --hidden-import=httpx --hidden-import=pydantic

echo.
if exist "dist\admin.exe" (
    echo ============================================
    echo   [SUCCESS] admin.exe created!
    echo   Location: dist\admin.exe
    echo ============================================
    echo.
    echo   Login:  username = mahadev
    echo           password = mahadev
    echo.
    echo   Double-click admin.exe to open dashboard
    echo ============================================
) else (
    echo [ERROR] Build failed! Check output above.
)
echo.
pause
