# 🎨 Hướng dẫn Icon cho Garena Account Creator

## ✅ Đã hoàn thành

### 📦 Icon đã tạo trong `frontend/public/`:

1. **icon.png** (512x512) - Icon chính cho ứng dụng
2. **icon.ico** - Icon cho Windows (multi-size: 256, 128, 64, 48, 32, 16)
3. **icon-256.png** - Icon 256x256
4. **icon-128.png** - Icon 128x128
5. **icon-64.png** - Icon 64x64
6. **icon-32.png** - Icon 32x32
7. **icon-16.png** - Icon 16x16

### 🔧 Cấu hình đã cập nhật trong `package.json`:

```json
{
  "build": {
    "win": {
      "icon": "public/icon.ico"
    },
    "nsis": {
      "installerIcon": "public/icon.ico",
      "uninstallerIcon": "public/icon.ico"
    }
  }
}
```

## 📍 Icon sẽ xuất hiện ở đâu?

### Sau khi build:
- ✅ **Desktop shortcut** - Icon Garena trên desktop
- ✅ **Start Menu** - Icon trong Start Menu
- ✅ **Taskbar** - Icon khi app đang chạy
- ✅ **Installer** - Icon của file cài đặt `.exe`
- ✅ **Uninstaller** - Icon của chương trình gỡ cài đặt
- ✅ **Window title bar** - Icon trên thanh tiêu đề cửa sổ
- ✅ **File Explorer** - Icon khi xem file .exe

## 🚀 Cách build với icon mới

### Bước 1: Copy các file icon
Đảm bảo các file sau có trong `frontend/public/`:
- icon.png
- icon.ico
- icon-*.png (tất cả các size)

### Bước 2: Build app
```batch
.\fix_build.bat
```

Hoặc build từng bước:
```batch
cd backend
python -m PyInstaller server.spec --clean --noconfirm
cd ..\frontend
yarn build
yarn electron-builder --win
```

### Bước 3: Kiểm tra icon
Sau khi cài đặt, kiểm tra:
1. Icon trên Desktop
2. Icon trong Start Menu
3. Icon khi app đang chạy
4. Icon trong Task Manager

## 🎨 Tùy chỉnh icon

### Thay đổi icon khác:

1. **Chuẩn bị ảnh gốc**:
   - Format: PNG, JPG, hoặc SVG
   - Kích thước khuyến nghị: ít nhất 512x512 pixels
   - Nền trong suốt (transparent) nếu có thể

2. **Tạo icon.png**:
   ```bash
   convert your-icon.png -resize 512x512 frontend/public/icon.png
   ```

3. **Tạo icon.ico cho Windows**:
   ```bash
   convert your-icon.png -define icon:auto-resize=256,128,64,48,32,16 frontend/public/icon.ico
   ```

4. **Build lại app**

### Công cụ online để tạo icon:
- https://www.icoconverter.com/
- https://convertio.co/png-ico/
- https://www.favicon-generator.org/

## 🐛 Troubleshooting

### Icon không hiển thị sau khi cài đặt:

1. **Clear icon cache của Windows**:
   ```batch
   ie4uinit.exe -show
   ```

2. **Gỡ cài đặt và cài lại app**:
   - Gỡ app cũ hoàn toàn
   - Restart Windows Explorer
   - Cài lại app mới

3. **Kiểm tra file icon.ico**:
   - Đảm bảo file icon.ico tồn tại trong `frontend/public/`
   - Mở file icon.ico bằng trình xem ảnh để đảm bảo nó không bị lỗi

### Icon bị mờ hoặc vỡ:

- Sử dụng ảnh gốc có độ phân giải cao hơn (ít nhất 512x512)
- Đảm bảo ảnh gốc có chất lượng tốt, không bị pixelated

### Build lỗi do icon:

```
Error: icon.ico not found
```

**Giải pháp**:
- Kiểm tra đường dẫn icon trong package.json
- Đảm bảo file icon.ico có trong thư mục `frontend/public/`

## 📋 Thông tin kỹ thuật

### Định dạng icon cho Windows:
- **.ico**: Multi-size icon file (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- Electron Builder tự động tạo các size nhỏ hơn từ icon gốc nếu cần

### Định dạng icon cho app window:
- **.png**: Icon hiển thị trên window và taskbar
- Kích thước: 512x512 hoặc 1024x1024

## ✨ Tips

1. **Nền trong suốt**: Nên sử dụng PNG với nền trong suốt để icon đẹp hơn
2. **Kích thước**: Icon càng lớn càng tốt (512x512 hoặc 1024x1024)
3. **Đơn giản**: Icon đơn giản, dễ nhận biết sẽ đẹp hơn khi scale xuống size nhỏ
4. **Kiểm tra**: Test icon ở nhiều size khác nhau trước khi build final

---

**Icon Garena đã được cấu hình và sẵn sàng cho build! 🎮**
