@echo off
echo ==================================================
echo Fix electron-store compatibility issue
echo ==================================================
echo.

echo This script will downgrade electron-store to version 8.1.0
echo which uses CommonJS and is compatible with Electron 39
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

cd frontend

echo.
echo Step 1: Removing current electron-store...
call yarn remove electron-store

echo.
echo Step 2: Installing electron-store@8.1.0...
call yarn add electron-store@8.1.0

echo.
echo Step 3: Restoring electron.js to CommonJS version...
copy /Y ..\electron.js.COMMONJS_VERSION public\electron.js

echo.
echo ==================================================
echo [OK] electron-store downgrade completed!
echo ==================================================
echo.
echo Now you can run: .\fix_build.bat
echo.

cd ..
pause
