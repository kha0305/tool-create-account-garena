@echo off
REM Build script for Garena Account Creator Desktop App (Windows)

echo ==================================================
echo Garena Account Creator - Build Script (Windows)
echo ==================================================
echo.

REM Step 1: Build Backend with PyInstaller
echo Step 1: Building backend with PyInstaller...
cd backend

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Build backend
echo Building backend executable...
python -m PyInstaller server.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo [OK] Backend built successfully
) else (
    echo [ERROR] Backend build failed
    exit /b 1
)

cd ..

REM Step 2: Build Frontend with React
echo.
echo Step 2: Building frontend with React...
cd frontend

REM Install dependencies if needed
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call yarn install
)

REM Build React app
echo Building React application...
call yarn build

if %errorlevel% equ 0 (
    echo [OK] Frontend built successfully
) else (
    echo [ERROR] Frontend build failed
    exit /b 1
)

REM Step 3: Package with Electron Builder
echo.
echo Step 3: Packaging with Electron Builder for Windows...
call yarn electron-build-win

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [OK] Build completed successfully!
    echo ==================================================
    echo.
    echo Installer is available in:
    echo   frontend/dist/
    echo.
    echo Windows installer: .exe file
) else (
    echo [ERROR] Electron build failed
    exit /b 1
)

cd ..

pause
