@echo off
echo ==================================================
echo Fix Build Issues - Garena Account Creator
echo ==================================================
echo.

echo Step 1: Cleaning electron-builder cache...
rmdir /s /q "%LOCALAPPDATA%\electron-builder\Cache" 2>nul
rmdir /s /q "%LOCALAPPDATA%\electron" 2>nul
rmdir /s /q "%APPDATA%\electron-builder" 2>nul
echo Cache cleared!
echo.

echo Step 2: Cleaning frontend build artifacts...
cd frontend
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
echo Build artifacts cleaned!
echo.

echo Step 3: Building backend...
cd ..\backend
python -m PyInstaller server.spec --clean --noconfirm
if %errorlevel% equ 0 (
    echo [OK] Backend built successfully
) else (
    echo [ERROR] Backend build failed
    pause
    exit /b 1
)
cd ..
echo.

echo Step 4: Building frontend...
cd frontend
call yarn build
if %errorlevel% equ 0 (
    echo [OK] Frontend built successfully
) else (
    echo [ERROR] Frontend build failed
    pause
    exit /b 1
)
echo.

echo Step 5: Building Electron app for Windows only (without signing)...
set USE_HARD_LINKS=false
call yarn electron-builder --win
if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [OK] Build completed successfully!
    echo ==================================================
    echo.
    echo Installer is available in:
    echo   frontend\dist\
) else (
    echo [ERROR] Electron build failed
    pause
    exit /b 1
)

cd ..
pause
