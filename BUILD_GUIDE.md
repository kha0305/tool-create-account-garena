# 📦 Garena Account Creator - Hướng Dẫn Đóng Gói Desktop App

## 🎯 Tổng Quan

Tài liệu này hướng dẫn cách đóng gói ứng dụng Garena Account Creator thành Desktop Application cho Windows, macOS và Linux sử dụng Electron.

## 📋 Yêu Cầu Hệ Thống

### Windows
- Windows 10 trở lên
- Python 3.8+
- Node.js 16+ và Yarn
- Git Bash (optional, để chạy script .sh)

### macOS
- macOS 10.13 trở lên
- Python 3.8+
- Node.js 16+ và Yarn
- Xcode Command Line Tools

### Linux
- Ubuntu 18.04+ / Debian 10+ hoặc tương đương
- Python 3.8+
- Node.js 16+ và Yarn

## 🚀 Hướng Dẫn Build Nhanh

### Cách 1: Sử Dụng Script Tự Động (Khuyến Nghị)

#### Windows:
```bash
# Chạy từ thư mục gốc của project
build.bat
```

#### macOS/Linux:
```bash
# Cấp quyền thực thi
chmod +x build.sh

# Chạy script
./build.sh
```

### Cách 2: Build Từng Bước Thủ Công

#### Bước 1: Build Backend (Python)

```bash
cd backend

# Cài đặt PyInstaller nếu chưa có
pip install pyinstaller

# Build backend executable
pyinstaller server.spec --clean --noconfirm

# Kết quả sẽ ở trong thư mục backend/dist/
cd ..
```

#### Bước 2: Build Frontend (React)

```bash
cd frontend

# Cài đặt dependencies
yarn install

# Build React app
yarn build

# Kết quả sẽ ở trong thư mục frontend/build/
```

#### Bước 3: Package với Electron

```bash
# Vẫn trong thư mục frontend/

# Build cho Windows
yarn electron-build-win

# Hoặc build cho macOS
yarn electron-build-mac

# Hoặc build cho Linux
yarn electron-build-linux

# Hoặc build cho tất cả platforms
yarn dist
```

## 📦 Kết Quả Build

Sau khi build thành công, các file installer sẽ được tạo trong thư mục `frontend/dist/`:

- **Windows**: `Garena Account Creator Setup x.x.x.exe`
- **macOS**: `Garena Account Creator-x.x.x.dmg`
- **Linux**: `Garena Account Creator-x.x.x.AppImage` hoặc `.deb`

## ⚙️ Cấu Hình Ứng Dụng

### Settings trong Desktop App

Sau khi cài đặt, người dùng có thể cấu hình:

1. **MongoDB Connection URL**:
   - Local: `mongodb://localhost:27017`
   - Cloud: `mongodb+srv://username:password@cluster.mongodb.net/dbname`

2. **API Keys** (optional):
   - Temp Mail API Key từ apilayer.com

### File Cấu Hình

Settings được lưu tự động bởi `electron-store`:
- **Windows**: `%APPDATA%\garena-account-creator\`
- **macOS**: `~/Library/Application Support/garena-account-creator/`
- **Linux**: `~/.config/garena-account-creator/`

## 🔧 Tùy Chỉnh Build

### Thay Đổi Icon Ứng Dụng

1. Tạo file icon:
   - **Windows**: `icon.ico` (256x256 px)
   - **macOS**: `icon.icns` (512x512 px)
   - **Linux**: `icon.png` (512x512 px)

2. Đặt file vào `frontend/public/`

3. Update `package.json`:
```json
{
  "build": {
    "win": {
      "icon": "public/icon.ico"
    },
    "mac": {
      "icon": "public/icon.icns"
    },
    "linux": {
      "icon": "public/icon.png"
    }
  }
}
```

### Thay Đổi Tên Ứng Dụng

Update trong `frontend/package.json`:
```json
{
  "name": "your-app-name",
  "productName": "Your App Display Name",
  "description": "Your app description",
  "build": {
    "appId": "com.yourcompany.yourapp"
  }
}
```

### Build Options

Trong `frontend/package.json`, bạn có thể tùy chỉnh:

```json
{
  "build": {
    "nsis": {
      "oneClick": false,              // Cho phép chọn thư mục cài đặt
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    },
    "compression": "maximum",         // Nén tối đa
    "asar": true                      // Đóng gói source code
  }
}
```

## 🐛 Xử Lý Sự Cố

### Lỗi: "Backend not starting"

1. Kiểm tra PyInstaller build thành công:
```bash
cd backend/dist
# Windows
./server.exe

# macOS/Linux
./server
```

2. Kiểm tra logs trong Developer Tools (Ctrl+Shift+I)

### Lỗi: "ENOENT: no such file"

- Đảm bảo `homepage: "./"` có trong `package.json`
- Build lại frontend: `yarn build`

### Lỗi: PyInstaller Missing Modules

Thêm module vào `hiddenimports` trong `backend/server.spec`:
```python
hiddenimports=[
    'your_missing_module',
    ...
]
```

### Lỗi: MongoDB Connection

- Kiểm tra MongoDB đang chạy
- Kiểm tra connection string trong Settings
- Restart ứng dụng sau khi thay đổi settings

## 📚 Chi Tiết Kỹ Thuật

### Kiến Trúc Ứng Dụng

```
Desktop App (Electron)
├── Main Process (electron.js)
│   ├── Quản lý window
│   ├── Khởi động backend server
│   └── IPC communication
├── Renderer Process (React)
│   ├── UI/UX
│   └── API calls to backend
└── Backend Process (Python FastAPI)
    ├── REST API endpoints
    ├── Database operations
    └── Business logic
```

### Luồng Hoạt Động

1. Electron main process khởi động
2. Backend Python server được spawn
3. React UI được load
4. Frontend gọi API đến backend qua localhost:8001
5. Backend xử lý và trả về kết quả

### Files Quan Trọng

- `frontend/public/electron.js` - Main process của Electron
- `frontend/public/preload.js` - Preload script cho IPC
- `backend/server.spec` - PyInstaller configuration
- `frontend/package.json` - Build configuration

## 🔐 Bảo Mật

### API Keys

- KHÔNG hardcode API keys trong code
- Sử dụng electron-store để lưu settings
- Settings được encrypt tự động

### Source Code Protection

- Code được đóng gói trong ASAR archive
- Python code được compile thành bytecode
- Sử dụng code obfuscation nếu cần (optional)

## 📝 Development vs Production

### Development Mode
```bash
cd frontend
yarn electron-dev
```
- Hot reload enabled
- DevTools tự động mở
- Backend chạy từ Python source

### Production Build
```bash
./build.sh  # hoặc build.bat
```
- Optimized build
- Backend là executable
- Không có DevTools
- Smaller package size

## 🎨 Tùy Chỉnh UI

Settings component có thể được tùy chỉnh trong:
- `frontend/src/components/Settings.js`

Thêm settings mới:
1. Update UI trong Settings.js
2. Update IPC handlers trong electron.js
3. Update backend để sử dụng settings mới

## 📄 License & Distribution

- Đảm bảo có license cho tất cả dependencies
- Kiểm tra terms of service của các API được sử dụng
- Update license information trong package.json

## 🤝 Contributing

Để đóng góp:
1. Fork repository
2. Tạo feature branch
3. Test kỹ trước khi commit
4. Submit pull request

## 📞 Support

Nếu gặp vấn đề trong quá trình build:
1. Kiểm tra logs trong console
2. Xem Developer Tools (Ctrl+Shift+I)
3. Kiểm tra backend logs
4. Tham khảo documentation của Electron và PyInstaller

---

## 🎉 Hoàn Thành!

Sau khi build xong, bạn sẽ có:
- ✅ File installer cho Windows (.exe)
- ✅ File installer cho macOS (.dmg)
- ✅ File installer cho Linux (.AppImage/.deb)
- ✅ Ứng dụng standalone không cần cài đặt Python/Node.js
- ✅ UI Settings để cấu hình
- ✅ Auto-update capability (có thể thêm sau)

**Chúc bạn build thành công! 🚀**
