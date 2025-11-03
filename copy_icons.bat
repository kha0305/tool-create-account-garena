@echo off
echo ==================================================
echo Copy Icon Files - Garena Account Creator
echo ==================================================
echo.
echo This script will copy all icon files from the root
echo directory to frontend/public/ directory
echo.
echo Files to copy:
echo - icon.png (512x512 - main icon)
echo - icon.ico (Windows multi-size icon)
echo - icon-*.png (various sizes)
echo.
pause

cd /d "%~dp0"

echo.
echo Copying icon files...

copy /Y icon.png frontend\public\icon.png
copy /Y icon.ico frontend\public\icon.ico
copy /Y icon-16.png frontend\public\icon-16.png
copy /Y icon-32.png frontend\public\icon-32.png
copy /Y icon-64.png frontend\public\icon-64.png
copy /Y icon-128.png frontend\public\icon-128.png
copy /Y icon-256.png frontend\public\icon-256.png

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [OK] Icon files copied successfully!
    echo ==================================================
    echo.
    echo You can now run: .\fix_build.bat
) else (
    echo.
    echo [ERROR] Failed to copy some icon files
    pause
    exit /b 1
)

echo.
pause
