# 🎮 Garena Account Creator - Desktop Application

Công cụ tạo tài khoản Garena hàng loạt tự động với email tạm, được đóng gói thành Desktop App cho Windows, macOS và Linux.

## ✨ Tính Năng

- 🚀 **Tạo tài khoản tự động** - Tạo hàng loạt tài khoản Garena
- 📧 **Email tạm** - Sử dụng Mail.tm với JWT authentication
- 💾 **Export dữ liệu** - TXT, CSV, XLSX formats
- 📬 **Kiểm tra email** - Xem inbox và chi tiết email (Text/HTML)
- 📋 **Copy nhanh** - One-click copy username/email/password
- 🎨 **Dark/Light mode** - Giao diện tùy chỉnh
- ⚙️ **Settings UI** - Cấu hình MongoDB và API keys trong app
- 🖥️ **Desktop App** - Standalone app không cần cài Python/Node.js
- 🔄 **Auto retry** - Tự động retry khi lỗi với exponential backoff
- 🛡️ **Rate limiting protection** - Delay tự động tránh bị block

## 📦 Download

### Installer (Recommended)

**Windows**: [Download .exe installer](releases/latest)
**macOS**: [Download .dmg file](releases/latest)  
**Linux**: [Download .AppImage](releases/latest)

### Yêu Cầu

- **Windows**: Windows 10 trở lên
- **macOS**: macOS 10.13+ (High Sierra)
- **Linux**: Ubuntu 18.04+ / Debian 10+
- **MongoDB**: Local hoặc MongoDB Atlas (Cloud)

## 🚀 Quick Start (User)

### 1. Cài Đặt MongoDB

**Option A: MongoDB Local**
- Download từ: https://www.mongodb.com/try/download/community
- Cài đặt và chạy MongoDB

**Option B: MongoDB Atlas (Cloud - Free)**
- Tạo account tại: https://www.mongodb.com/cloud/atlas/register
- Tạo free cluster M0
- Copy connection string

### 2. Cài Đặt App

- Download installer từ [Releases](releases/latest)
- Windows: Chạy `.exe` file
- macOS: Kéo app vào Applications
- Linux: Chạy `.AppImage` file

### 3. Cấu Hình

1. Mở app
2. Click icon ⚙️ **Settings** (góc phải trên)
3. Nhập:
   - **MongoDB URL**: `mongodb://localhost:27017` (local) hoặc connection string của Atlas
   - **Database Name**: `garena_creator_db`
   - **API Key** (optional): Để trống nếu không có
4. Click **"Lưu Cài Đặt"**
5. **Restart app**

### 4. Sử Dụng

1. Chọn số lượng tài khoản (1-100)
2. Click **"Tạo Tài Khoản"**
3. Đợi quá trình hoàn tất
4. Export hoặc copy thông tin tài khoản

**Chi tiết**: Xem [USER_GUIDE.md](USER_GUIDE.md)

## 💻 For Developers

### Clone Repository

```bash
git clone https://github.com/kha0305/tool-create-account-garena
cd tool-create-account-garena
```

### Cài Đặt Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
yarn install
```

### Development Mode

**Test Electron App:**
```bash
cd frontend
yarn electron-dev
```

**Test Web App (Classic):**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd frontend
yarn start
```

### Build Desktop App

**Quick Build:**
```bash
# Windows
.\build.bat

# Linux/Mac
chmod +x build.sh
./build.sh
```

**Build Từng Platform:**
```bash
cd frontend
yarn electron-build-win    # Windows
yarn electron-build-mac    # macOS
yarn electron-build-linux  # Linux
```

**Output:** `frontend/dist/`

### 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Bắt đầu nhanh cho developers
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Hướng dẫn build chi tiết
- [USER_GUIDE.md](USER_GUIDE.md) - Hướng dẫn người dùng
- [FIX_BUILD_ERROR.md](FIX_BUILD_ERROR.md) - Fix lỗi build trên Windows
- [HUONG_DAN_LOCAL.md](HUONG_DAN_LOCAL.md) - Chạy app local

## 🏗️ Kiến Trúc

```
Desktop App (Electron)
├── Main Process (electron.js)
│   ├── Window management
│   ├── Backend server lifecycle
│   └── IPC communication
├── Renderer Process (React)
│   ├── UI/UX
│   └── API calls
└── Backend Process (Python FastAPI)
    ├── REST API
    ├── MongoDB operations
    └── Garena account creation
```

### Tech Stack

- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: Python 3.11 + FastAPI + Motor (async MongoDB)
- **Desktop**: Electron 39
- **Packaging**: electron-builder + PyInstaller
- **Database**: MongoDB

## 🔧 Configuration

### Environment Variables

**Backend** (managed by Electron):
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `TEMP_MAIL_API_KEY` - Temp mail API key (optional)

**Frontend**:
- `REACT_APP_BACKEND_URL` - Backend URL (auto-configured)

### Settings (In-App)

Settings được lưu với `electron-store`:
- **Windows**: `%APPDATA%\garena-account-creator\`
- **macOS**: `~/Library/Application Support/garena-account-creator/`
- **Linux**: `~/.config/garena-account-creator/`

## 📊 Features Details

### Account Creation
- Tự động generate username & password theo chuẩn Garena
- Tạo email tạm từ Mail.tm
- Delay tự động tránh rate limiting (2-3s/account)
- Retry logic với exponential backoff
- Status tracking real-time

### Email Management
- JWT-based authentication với Mail.tm
- Check inbox messages
- View email content (Text/HTML)
- Session persistence

### Export Options
- **TXT**: Plain text format
- **CSV**: Comma-separated values
- **XLSX**: Excel format với formatting

### Rate Limiting
- Auto delay giữa requests
- Exponential backoff khi lỗi
- Max 3 retry attempts
- Khuyến nghị: 5-10 accounts/batch

## ⚠️ Known Issues & Solutions

### Windows Build Error: "Cannot create symbolic link"

**Solution**: Xem [FIX_BUILD_ERROR.md](FIX_BUILD_ERROR.md)

Quick fix:
1. Chạy PowerShell/CMD với quyền Administrator
2. Hoặc chạy: `.\fix_build.bat`

### MongoDB Connection Error

**Solution**:
1. Đảm bảo MongoDB đang chạy
2. Check connection string trong Settings
3. Restart app sau khi thay đổi settings

### Rate Limiting

**Solution**:
1. Giảm số lượng accounts (5-10/lần)
2. Đợi 30-60 giây giữa các batch
3. App tự động delay, đừng spam create

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

This project is for educational purposes only. Please respect the Terms of Service of Garena and Mail.tm.

## 🎯 Roadmap

- [ ] Auto-update capability
- [ ] Proxy support
- [ ] Multi-language support
- [ ] Account verification automation
- [ ] Batch management
- [ ] Advanced filtering & search
- [ ] Cloud backup integration

## 🐛 Bug Reports

Found a bug? Please open an [issue](https://github.com/kha0305/tool-create-account-garena/issues) with:
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## 💬 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our server](#)
- 📖 Docs: See documentation files in root directory

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

**Made with ❤️ for the gaming community**

**⚠️ Disclaimer**: Công cụ này chỉ dùng cho mục đích test và development. Người dùng chịu trách nhiệm tuân thủ Terms of Service của các dịch vụ được sử dụng.
