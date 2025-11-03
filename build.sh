#!/bin/bash

# Build script for Garena Account Creator Desktop App
# This script packages the application for Windows, Mac, and Linux

echo "=================================================="
echo "Garena Account Creator - Build Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build Backend with PyInstaller
echo -e "${YELLOW}Step 1: Building backend with PyInstaller...${NC}"
cd backend

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
fi

# Build backend
echo "Building backend executable..."
pyinstaller server.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed${NC}"
    exit 1
fi

cd ..

# Step 2: Build Frontend with React
echo ""
echo -e "${YELLOW}Step 2: Building frontend with React...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    yarn install
fi

# Build React app
echo "Building React application..."
yarn build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend built successfully${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

# Step 3: Package with Electron Builder
echo ""
echo -e "${YELLOW}Step 3: Packaging with Electron Builder...${NC}"

# Check platform
PLATFORM=$(uname -s)
echo "Detected platform: $PLATFORM"

case $PLATFORM in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        echo "Building for Windows..."
        yarn electron-build-win
        ;;
    Darwin)
        echo "Building for macOS..."
        yarn electron-build-mac
        ;;
    Linux)
        echo "Building for Linux..."
        yarn electron-build-linux
        ;;
    *)
        echo "Building for all platforms..."
        yarn dist
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=================================================="
    echo -e "✓ Build completed successfully!"
    echo -e "==================================================${NC}"
    echo ""
    echo "Installers are available in:"
    echo "  frontend/dist/"
    echo ""
    echo "Windows: .exe installer"
    echo "macOS:   .dmg file"
    echo "Linux:   .AppImage or .deb file"
else
    echo -e "${RED}✗ Electron build failed${NC}"
    exit 1
fi

cd ..
