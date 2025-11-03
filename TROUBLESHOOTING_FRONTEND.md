# 🔍 Troubleshooting: Frontend không hiển thị

## ❌ Các triệu chứng thường gặp:

### 1. Màn hình trắng (White screen)
**Nguyên nhân:**
- Frontend build chưa đúng
- Đường dẫn file index.html sai
- Console có lỗi JavaScript

**Cách fix:**
```batch
cd frontend
rmdir /s /q build
yarn build
```

### 2. App không khởi động
**Nguyên nhân:**
- Backend không chạy được
- Port 8001 bị chiếm
- Lỗi trong electron.js

**Cách fix:**
- Kiểm tra MongoDB đã chạy chưa
- Kiểm tra port 8001: `netstat -ano | findstr :8001`
- Xem log trong Task Manager

### 3. "Cannot GET /"
**Nguyên nhân:**
- File index.html không tìm thấy
- Đường dẫn trong electron.js sai

**Cách fix:**
- Kiểm tra file `frontend/build/index.html` có tồn tại không
- Xem electron.js dòng loadFile

## 🛠️ Các bước kiểm tra:

### Bước 1: Kiểm tra build frontend
```batch
cd frontend
dir build\index.html
```

Nếu không có file → Cần build lại:
```batch
yarn build
```

### Bước 2: Kiểm tra electron.js
File: `frontend/public/electron.js`

Dòng 36 nên là:
```javascript
mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
```

### Bước 3: Kiểm tra backend
Backend phải được build trước:
```batch
cd backend
dir dist\server.exe
```

Nếu không có → Build backend:
```batch
python -m PyInstaller server.spec --clean --noconfirm
```

### Bước 4: Test từng phần

**Test backend riêng:**
```batch
cd backend\dist
server.exe
```

Mở browser: `http://localhost:8001/docs`

**Test frontend riêng (dev mode):**
```batch
cd frontend
yarn start
```

Mở browser: `http://localhost:3000`

## 🐛 Lỗi cụ thể và cách fix:

### Lỗi: "electron-store" error
→ Chạy: `.\fix_electron_store.bat`

### Lỗi: Backend không chạy
→ Cài MongoDB: https://www.mongodb.com/try/download/community
→ Hoặc dùng MongoDB Atlas (cloud)

### Lỗi: Port 8001 đã được sử dụng
```batch
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Lỗi: Cannot find module
```batch
cd frontend
yarn install
cd ..\backend
pip install -r requirements.txt
```

## 📋 Checklist build đúng cách:

- [ ] Backend đã build (`backend/dist/server.exe` tồn tại)
- [ ] Frontend đã build (`frontend/build/index.html` tồn tại)
- [ ] electron.js không có lỗi syntax
- [ ] Icon files tồn tại trong `frontend/public/`
- [ ] package.json cấu hình đúng
- [ ] MongoDB đang chạy (nếu cần)

## 🚀 Build lại từ đầu:

```batch
@echo off
echo === FULL REBUILD ===

echo Step 1: Clean
cd frontend
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q node_modules\.cache

echo Step 2: Install dependencies
yarn install

echo Step 3: Build backend
cd ..\backend
python -m PyInstaller server.spec --clean --noconfirm

echo Step 4: Build frontend
cd ..\frontend
yarn build

echo Step 5: Build Electron
yarn electron-builder --win

echo === DONE ===
pause
```

## 📞 Cần thêm thông tin:

Để giúp bạn tốt hơn, vui lòng cung cấp:

1. **Screenshot lỗi** (nếu có)
2. **Log từ console** (F12 trong app)
3. **Triệu chứng cụ thể**:
   - App mở nhưng màn hình trắng?
   - App không mở được?
   - App mở nhưng không load được data?
   - Khác?

4. **Đã thử những gì**:
   - Chạy `fix_build.bat` → Kết quả?
   - Chạy `fix_electron_store.bat` → Kết quả?
   - Test backend riêng → Có chạy không?
   - Test frontend dev mode → Có chạy không?

---

**Gửi thêm thông tin để tôi có thể giúp bạn fix chính xác hơn! 🔧**
