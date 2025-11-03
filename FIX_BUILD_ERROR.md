# 🔧 Fix Lỗi Build Electron - Windows

## ❌ Lỗi Gặp Phải

```
ERROR: Cannot create symbolic link : A required privilege is not held by the client.
```

Lỗi này xảy ra vì:
- Windows cần quyền Administrator để tạo symbolic links
- electron-builder cố tạo symlinks cho macOS files trên Windows
- Không có quyền để extract code signing tools

## ✅ Giải Pháp

### Giải Pháp 1: Chạy Với Quyền Admin (Khuyến Nghị)

**Bước 1:** Đóng PowerShell/CMD hiện tại

**Bước 2:** Mở PowerShell với quyền Administrator:
- Tìm "PowerShell" trong Start Menu
- Chuột phải > "Run as Administrator"
- Hoặc nhấn `Win + X` > chọn "Windows PowerShell (Admin)"

**Bước 3:** Chạy build:
```bash
cd D:\build_tool_acc\tool-create-account-garena
.\fix_build.bat
```

### Giải Pháp 2: Xóa Cache và Build Lại (Nếu Giải Pháp 1 Không Được)

File `fix_build.bat` sẽ tự động:
1. ✅ Xóa cache electron-builder
2. ✅ Xóa build artifacts cũ  
3. ✅ Build backend với PyInstaller
4. ✅ Build frontend React
5. ✅ Package với Electron (không signing)

```bash
# Chạy script fix
.\fix_build.bat
```

### Giải Pháp 3: Build Từng Bước Thủ Công

Nếu vẫn gặp lỗi, build từng bước:

```bash
# 1. Xóa cache
rmdir /s /q "%LOCALAPPDATA%\electron-builder\Cache"

# 2. Build backend
cd backend
python -m PyInstaller server.spec --clean --noconfirm
cd ..

# 3. Build frontend
cd frontend
yarn build

# 4. Package Electron (không build backend nữa)
# Tạo thư mục backend/dist fake nếu cần
mkdir ..\backend\dist 2>nul
copy ..\backend\server.py ..\backend\dist\

# 5. Build Electron
yarn electron-build-win
```

## 🎯 Các Thay Đổi Đã Làm

### 1. Disable Code Signing
Đã update `frontend/package.json`:
```json
{
  "build": {
    "win": {
      "sign": false
    },
    "mac": {
      "identity": null
    }
  }
}
```

### 2. Fix PyInstaller Spec
Đã xóa requirement `.env` file trong `backend/server.spec` vì:
- Desktop app không cần `.env`
- Settings được quản lý bởi electron-store
- Environment variables được pass từ Electron

### 3. Tạo Fix Build Script
File `fix_build.bat` tự động xử lý:
- Clean cache
- Build backend
- Build frontend
- Package app

## 🚀 Quy Trình Build Đúng

### Windows (Khuyến Nghị):

```bash
# 1. Mở PowerShell/CMD với quyền Admin
# Win + X > Windows PowerShell (Admin)

# 2. Navigate đến project
cd D:\build_tool_acc\tool-create-account-garena

# 3. Chạy fix script
.\fix_build.bat

# 4. Đợi build hoàn tất (5-10 phút)
# Output: frontend\dist\Garena Account Creator Setup 1.0.0.exe
```

### Nếu Không Có Quyền Admin:

Bạn có thể:
1. **Enable Developer Mode** trong Windows Settings:
   - Settings > Update & Security > For developers
   - Bật "Developer Mode"
   - Restart máy
   - Chạy lại build

2. **Build trên Linux/Mac**: Copy code sang Linux/Mac để build

3. **Sử dụng WSL2**: Build trên WSL2 với Linux commands

## 📦 Kết Quả Build

Sau khi build thành công:

```
frontend/dist/
├── win-unpacked/              # App chưa đóng gói (có thể chạy trực tiếp)
├── Garena Account Creator Setup 1.0.0.exe  # Windows installer
└── latest.yml                 # Update manifest
```

**File installer**: 
- `Garena Account Creator Setup 1.0.0.exe` (~150-200MB)
- Người dùng chỉ cần file này để cài đặt

## ⚠️ Lưu Ý Quan Trọng

### 1. Backend Build
Backend được build thành executable trong `backend/dist/server.exe`:
```bash
cd backend
python -m PyInstaller server.spec --clean --noconfirm
```

### 2. Frontend Build  
React app được build trong `frontend/build/`:
```bash
cd frontend
yarn build
```

### 3. Electron Package
Electron đóng gói cả frontend build + backend executable:
```bash
cd frontend
yarn electron-build-win
```

### 4. Không Cần .env
Desktop app không cần file `.env` vì:
- Settings UI trong app
- electron-store lưu config
- Environment variables passed từ Electron

## 🐛 Troubleshooting

### Lỗi: "pyinstaller not found"
```bash
pip install pyinstaller
# Hoặc
python -m pip install pyinstaller
```

### Lỗi: "yarn not found"
```bash
npm install -g yarn
```

### Lỗi: Backend build failed
```bash
# Kiểm tra Python dependencies
cd backend
pip install -r requirements.txt

# Kiểm tra server.py chạy được
python server.py
```

### Lỗi: Frontend build failed
```bash
cd frontend

# Clear cache
yarn cache clean

# Reinstall
rm -rf node_modules
yarn install

# Build lại
yarn build
```

### Lỗi: electron-builder cache corrupt
```bash
# Xóa toàn bộ cache
rmdir /s /q "%LOCALAPPDATA%\electron-builder"
rmdir /s /q "%APPDATA%\electron-builder"

# Build lại
yarn electron-build-win
```

## 📝 Checklist Trước Khi Build

- [ ] Python 3.8+ đã cài
- [ ] Node.js 16+ và Yarn đã cài
- [ ] PyInstaller đã cài (`pip install pyinstaller`)
- [ ] Dependencies đã cài (pip install + yarn install)
- [ ] MongoDB connection string sẵn sàng (cho Settings)
- [ ] Chạy PowerShell/CMD với quyền Admin (hoặc Developer Mode enabled)
- [ ] Đã xóa cache cũ
- [ ] Backend test chạy OK (`python server.py`)
- [ ] Frontend test chạy OK (`yarn start`)

## ✨ Tips

1. **Build lần đầu**: Có thể mất 10-15 phút (download dependencies)
2. **Build lần sau**: Nhanh hơn ~5 phút (đã có cache)
3. **Test trước**: Luôn test app với `yarn electron-dev` trước khi build production
4. **Size**: Installer ~150-200MB là bình thường (bao gồm Node, Python runtime)
5. **Antivirus**: Tắt antivirus nếu build bị block
6. **Disk Space**: Cần ~2GB free space để build

## 🎉 Hoàn Thành!

Sau khi build xong:
```bash
# File installer ở đây:
frontend\dist\Garena Account Creator Setup 1.0.0.exe

# Test installer:
# 1. Double-click file .exe
# 2. Follow installation wizard
# 3. Chạy app
# 4. Cấu hình Settings (MongoDB URL)
# 5. Test tạo tài khoản
```

---

**Chúc bạn build thành công! 🚀**

Nếu vẫn gặp vấn đề, hãy:
1. Đảm bảo chạy với quyền Admin
2. Xóa toàn bộ cache
3. Build từng bước thủ công
4. Check logs để tìm lỗi cụ thể
