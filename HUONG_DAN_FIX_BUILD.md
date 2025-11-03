# 🔧 Hướng Dẫn Fix Lỗi Build - Garena Account Creator

## ❌ Lỗi Đang Gặp Phải

```
ERROR: Cannot create symbolic link : A required privilege is not held by the client.
C:\Users\ASUS\AppData\Local\electron-builder\Cache\winCodeSign\...
```

## ✅ Các File Đã Được Sửa

### 1. **package.json** 
✅ Đã thêm:
- `"sign": false` - Tắt code signing
- `"signingHashAlgorithms": []` - Bỏ qua signing algorithms
- Cú pháp JSON đã đúng (đã thêm dấu phẩy)

### 2. **fix_build.bat**
✅ Đã cập nhật:
- Xóa cache electron-builder đầy đủ hơn
- Set biến `USE_HARD_LINKS=false` để tránh symlink
- Dùng command `electron-builder --win --config.win.sign=false` trực tiếp

---

## 🚀 Cách Sử Dụng - Copy Các File Này Về Máy Windows

### **Bước 1: Copy các file đã sửa**

Copy 2 files này từ `/app/` về máy Windows của bạn:

1. `/app/frontend/package.json` 
   → Copy về `D:\build_tool_acc\tool-create-account-garena\frontend\package.json`

2. `/app/fix_build.bat`
   → Copy về `D:\build_tool_acc\tool-create-account-garena\fix_build.bat`

### **Bước 2: Xóa cache cũ**

Mở PowerShell và chạy:
```powershell
# Xóa cache electron-builder
Remove-Item -Path "$env:LOCALAPPDATA\electron-builder" -Recurse -Force -ErrorAction SilentlyContinue

# Xóa cache electron
Remove-Item -Path "$env:LOCALAPPDATA\electron" -Recurse -Force -ErrorAction SilentlyContinue

# Xóa build cũ
cd D:\build_tool_acc\tool-create-account-garena\frontend
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
```

### **Bước 3: Chạy build script**

```powershell
cd D:\build_tool_acc\tool-create-account-garena
.\fix_build.bat
```

---

## 🎯 Nếu Vẫn Lỗi - Thử Các Cách Sau

### **Cách 1: Chạy với PowerShell Admin**

1. Mở PowerShell với quyền Administrator
2. Chạy:
```powershell
cd D:\build_tool_acc\tool-create-account-garena
.\fix_build.bat
```

### **Cách 2: Bật Developer Mode**

1. Mở **Settings** > **Update & Security** > **For developers**
2. Bật **Developer Mode**
3. Restart máy
4. Chạy lại build (không cần Admin)

### **Cách 3: Build thủ công từng bước**

```powershell
cd D:\build_tool_acc\tool-create-account-garena

# 1. Xóa cache
Remove-Item -Path "$env:LOCALAPPDATA\electron-builder" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Build backend
cd backend
python -m PyInstaller server.spec --clean --noconfirm
cd ..

# 3. Build frontend
cd frontend
yarn build

# 4. Build Electron với options đặc biệt
$env:USE_HARD_LINKS = "false"
yarn electron-builder --win --config.win.sign=false --config.compression=store

cd ..
```

### **Cách 4: Dùng NSIS thay vì electron-builder**

Nếu vẫn không được, có thể build bằng cách khác:

```powershell
cd frontend

# Build với portable mode (không cần installer)
yarn electron-builder --win portable --config.win.sign=false

# Hoặc build unpacked (folder app có thể chạy trực tiếp)
yarn electron-builder --win dir --config.win.sign=false
```

---

## 📋 Chi Tiết Config Đã Sửa

### package.json - Phần "build.win"

```json
"win": {
  "target": [
    {
      "target": "nsis",
      "arch": ["x64"]
    }
  ],
  "icon": "public/icon.png",
  "sign": false,                          // ← MỚI THÊM
  "signingHashAlgorithms": [],           // ← MỚI THÊM
  "signAndEditExecutable": false,
  "verifyUpdateCodeSignature": false
}
```

### fix_build.bat - Step 5

```batch
echo Step 5: Building Electron app (without signing)...
set USE_HARD_LINKS=false                           # ← MỚI THÊM
call yarn electron-builder --win --config.win.sign=false   # ← ĐÃ SỬA
```

---

## 🔍 Kiểm Tra Build Thành Công

Sau khi build xong, kiểm tra:

```powershell
# File installer phải tồn tại
dir D:\build_tool_acc\tool-create-account-garena\frontend\dist\*.exe

# Kích thước khoảng 150-250MB là bình thường
```

File output:
```
frontend\dist\
├── Garena Account Creator Setup 1.0.0.exe    ← FILE NÀY
├── win-unpacked\                             ← Folder app chưa đóng gói
└── latest.yml                                ← Update metadata
```

---

## 💡 Giải Thích Lỗi

**Tại sao lỗi symlink?**
- electron-builder tải xuống code signing tools cho cả Windows + macOS + Linux
- Các file macOS (darwin) dùng symbolic links
- Windows cần quyền Administrator để tạo symlinks
- Khi không có quyền → lỗi "privilege is not held by the client"

**Giải pháp:**
- Tắt code signing hoàn toàn (`sign: false`)
- Set `USE_HARD_LINKS=false` để dùng hard links thay vì symlinks
- Hoặc chạy với quyền Admin

---

## 📦 Các Loại Build Khác Nhau

### 1. **NSIS Installer** (Mặc định)
```powershell
yarn electron-builder --win
```
→ Tạo file `.exe` installer (~150MB)

### 2. **Portable**
```powershell
yarn electron-builder --win portable
```
→ Tạo file `.exe` chạy trực tiếp, không cần cài đặt

### 3. **Unpacked/Dir**
```powershell
yarn electron-builder --win dir
```
→ Tạo folder chứa app, chạy file `.exe` trong folder

### 4. **MSI Installer**
```powershell
yarn electron-builder --win --config.win.target=msi
```
→ Tạo file `.msi` installer (enterprise)

---

## ⚠️ Lưu Ý Quan Trọng

### Backend Phải Build Trước
```powershell
cd backend
python -m PyInstaller server.spec --clean --noconfirm
```
→ Tạo `backend/dist/server.exe`

### Frontend Build Riêng
```powershell
cd frontend
yarn build
```
→ Tạo `frontend/build/` (React static files)

### Electron Package Kết Hợp
```powershell
cd frontend
yarn electron-builder --win
```
→ Đóng gói `frontend/build/` + `backend/dist/` vào Electron app

---

## 🐛 Debug Nếu Vẫn Lỗi

### Xem logs chi tiết:
```powershell
cd frontend
set DEBUG=electron-builder
yarn electron-builder --win --config.win.sign=false
```

### Kiểm tra backend có build không:
```powershell
cd backend\dist
dir server.exe
.\server.exe
```

### Kiểm tra frontend có build không:
```powershell
cd frontend\build
dir index.html
```

### Test electron local trước:
```powershell
cd frontend
yarn electron-dev
```

---

## 📞 Checklist Cuối Cùng

Trước khi build, đảm bảo:

- [ ] Python 3.8+ đã cài
- [ ] Node.js 16+ đã cài  
- [ ] Yarn đã cài (`npm install -g yarn`)
- [ ] PyInstaller đã cài (`pip install pyinstaller`)
- [ ] Backend dependencies đã cài (`cd backend && pip install -r requirements.txt`)
- [ ] Frontend dependencies đã cài (`cd frontend && yarn install`)
- [ ] File `package.json` đã sửa đúng (có dấu phẩy, có `sign: false`)
- [ ] Cache đã xóa sạch
- [ ] Backend test chạy OK (`python backend/server.py`)
- [ ] Có 2GB+ dung lượng trống

---

## 🎉 Hoàn Thành!

Nếu làm đúng các bước trên, bạn sẽ có:

✅ File installer: `frontend\dist\Garena Account Creator Setup 1.0.0.exe`
✅ Kích thước: ~150-250MB
✅ Chạy được trên Windows 10+ (64-bit)
✅ Không cần cài Python/Node.js
✅ Có UI Settings để config MongoDB

**Test installer:**
1. Double-click file `.exe`
2. Follow wizard cài đặt
3. Chạy app
4. Vào Settings → Nhập MongoDB URL
5. Test tạo tài khoản

---

**Chúc bạn thành công! 🚀**
