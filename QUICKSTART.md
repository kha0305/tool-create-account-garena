# 🎯 Quick Start Guide - Garena Account Creator Desktop App

## 📝 Tóm Tắt

Bạn đã có tất cả các file cần thiết để đóng gói ứng dụng thành Desktop App!

## 🔧 Cài Đặt Dependencies

### Backend (Python):
```bash
cd backend
pip install -r requirements.txt
```

### Frontend (React/Electron):
```bash
cd frontend  
yarn install
```

## 🧪 Test Trước Khi Build

### Option 1: Test Electron Development Mode
```bash
cd frontend
yarn electron-dev
```
Điều này sẽ:
- Chạy React dev server
- Khởi động Electron
- Backend Python tự động start
- Có hot reload

### Option 2: Test Web Mode (như hiện tại)
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend  
cd frontend
yarn start
```

## 📦 Build Desktop App

### Cách Nhanh - Dùng Script:

**Windows:**
```bash
build.bat
```

**macOS/Linux:**
```bash
chmod +x build.sh
./build.sh
```

### Cách Từng Bước:

**1. Build Backend:**
```bash
cd backend
pyinstaller server.spec --clean --noconfirm
```

**2. Build Frontend + Package:**
```bash
cd frontend
yarn build
yarn electron-build-win    # For Windows
# hoặc
yarn electron-build-mac    # For macOS
# hoặc 
yarn electron-build-linux  # For Linux
```

## 📂 Output Files

Sau khi build, installer sẽ ở:
```
frontend/dist/
├── Garena Account Creator Setup 1.0.0.exe    # Windows
├── Garena Account Creator-1.0.0.dmg          # macOS
└── Garena Account Creator-1.0.0.AppImage     # Linux
```

## ⚙️ Settings Trong Desktop App

Người dùng có thể cấu hình:
- MongoDB URL (local hoặc cloud)
- API Keys
- Các settings khác

Truy cập qua nút ⚙️ Settings ở góc phải trên.

## 🎨 Tùy Chỉnh Icon

Hiện tại có icon SVG placeholder. Để tùy chỉnh:

1. **Tạo icon mới:**
   - Sử dụng công cụ online: https://www.icoconverter.com/
   - Upload logo của bạn
   - Generate .ico (Windows), .icns (Mac), .png (Linux)

2. **Thay thế:**
   - Copy vào `frontend/public/`
   - Update `package.json` nếu tên file khác

## 📚 Chi Tiết Đầy Đủ

Xem file `BUILD_GUIDE.md` để biết:
- Hướng dẫn chi tiết từng bước
- Troubleshooting
- Tùy chỉnh nâng cao
- Kiến trúc kỹ thuật

## 🚀 Các File Đã Tạo

1. **Electron Files:**
   - `frontend/public/electron.js` - Main process
   - `frontend/public/preload.js` - Preload script

2. **Settings UI:**
   - `frontend/src/components/Settings.js` - Settings component

3. **Build Config:**
   - `backend/server.spec` - PyInstaller config
   - `frontend/package.json` - Updated with Electron build config

4. **Build Scripts:**
   - `build.sh` - Linux/Mac build script
   - `build.bat` - Windows build script

5. **Documentation:**
   - `BUILD_GUIDE.md` - Chi tiết đầy đủ
   - `QUICKSTART.md` - File này

## ✅ Checklist Trước Khi Build

- [ ] MongoDB đã cài đặt (hoặc có MongoDB Atlas URL)
- [ ] Python 3.8+ đã cài
- [ ] Node.js 16+ và Yarn đã cài
- [ ] Đã cài dependencies (pip install, yarn install)
- [ ] Test app trong dev mode (yarn electron-dev)
- [ ] Update icon nếu cần
- [ ] Update app name/description trong package.json

## 🎯 Next Steps

1. **Test ngay:**
   ```bash
   cd frontend
   yarn electron-dev
   ```

2. **Nếu OK, build:**
   ```bash
   ./build.sh  # hoặc build.bat
   ```

3. **Phân phối:**
   - Installer ở `frontend/dist/`
   - Chia sẻ với người dùng!

## ❓ Cần Giúp?

- Xem `BUILD_GUIDE.md` cho troubleshooting
- Check logs trong DevTools (Ctrl+Shift+I)
- Test từng component riêng lẻ

---

**Chúc bạn build thành công! 🎉**
