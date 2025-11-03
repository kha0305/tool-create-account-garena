# 📱 Garena Account Creator - Hướng Dẫn Sử Dụng

## 🎯 Tổng Quan

Garena Account Creator là ứng dụng desktop giúp bạn tạo hàng loạt tài khoản Garena một cách tự động với email ảo.

## 💻 Yêu Cầu Hệ Thống

### Windows
- Windows 10 hoặc mới hơn
- 4GB RAM
- 500MB dung lượng trống

### macOS
- macOS 10.13 (High Sierra) hoặc mới hơn
- 4GB RAM
- 500MB dung lượng trống

### Linux
- Ubuntu 18.04+ / Debian 10+ hoặc tương đương
- 4GB RAM
- 500MB dung lượng trống

## 📦 Cài Đặt

### Windows
1. Download file `Garena Account Creator Setup.exe`
2. Double-click để chạy installer
3. Làm theo hướng dẫn trên màn hình
4. Chọn thư mục cài đặt (mặc định: C:\Program Files\Garena Account Creator)
5. Chờ cài đặt hoàn tất

### macOS
1. Download file `Garena Account Creator.dmg`
2. Double-click để mount
3. Kéo icon ứng dụng vào thư mục Applications
4. Mở Applications và chạy ứng dụng

### Linux
1. Download file `Garena Account Creator.AppImage`
2. Cấp quyền thực thi:
   ```bash
   chmod +x Garena-Account-Creator.AppImage
   ```
3. Double-click hoặc chạy từ terminal:
   ```bash
   ./Garena-Account-Creator.AppImage
   ```

## ⚙️ Cấu Hình Lần Đầu

### 1. Cài Đặt MongoDB (Bắt Buộc)

Ứng dụng cần MongoDB để lưu trữ dữ liệu. Bạn có 2 lựa chọn:

#### Option A: MongoDB Local (Khuyến Nghị Cho Người Mới)

**Windows:**
1. Download MongoDB Community từ: https://www.mongodb.com/try/download/community
2. Cài đặt với các tùy chọn mặc định
3. MongoDB sẽ tự động chạy sau khi cài đặt

**macOS:**
```bash
# Cài đặt với Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### Option B: MongoDB Atlas (Cloud - Miễn Phí)

1. Tạo tài khoản tại: https://www.mongodb.com/cloud/atlas/register
2. Tạo cluster miễn phí (Free Tier - M0)
3. Tạo database user (ghi nhớ username & password)
4. Whitelist IP address của bạn (hoặc cho phép tất cả: 0.0.0.0/0)
5. Copy connection string (dạng: `mongodb+srv://username:password@cluster.mongodb.net`)

### 2. Cấu Hình Ứng Dụng

1. Mở ứng dụng
2. Click vào icon ⚙️ **Settings** ở góc phải trên
3. Điền thông tin:

   **MongoDB Connection URL:**
   - Local: `mongodb://localhost:27017`
   - Cloud: `mongodb+srv://username:password@cluster.mongodb.net`

   **Database Name:**
   - Mặc định: `garena_creator_db`
   - Hoặc tên bạn muốn

   **API Key (Tùy Chọn):**
   - Để trống nếu không có
   - Lấy từ: https://apilayer.com/marketplace/temp_mail-api

4. Click **"Lưu Cài Đặt"**
5. **Khởi động lại** ứng dụng

## 🚀 Sử Dụng

### Tạo Tài Khoản

1. **Chọn Số Lượng:**
   - Click vào dropdown "Chọn số lượng"
   - Chọn từ 1-100 tài khoản

2. **Email Provider:**
   - Mặc định: Mail.tm (Miễn phí)
   - Không cần thay đổi

3. **Bắt Đầu Tạo:**
   - Click nút **"Tạo Tài Khoản"**
   - Theo dõi tiến trình trên thanh progress bar
   - Chờ hoàn tất

### Xem Thông Tin Tài Khoản

Sau khi tạo xong, bảng tài khoản sẽ hiển thị:
- ✉️ **Email**: Email tạm thời
- 👤 **Username**: Tên đăng nhập Garena  
- 🔑 **Password**: Mật khẩu (click 👁️ để hiện)
- 📅 **Ngày tạo**: Thời gian tạo
- ⚡ **Hành động**: Copy, Delete, Check Inbox

### Copy Thông Tin

- Click icon 📋 để copy email, username hoặc password
- Thông báo "Đã copy!" sẽ xuất hiện

### Kiểm Tra Email

1. Click icon 📨 **"Check Inbox"** ở cột hành động
2. Xem danh sách email nhận được
3. Click vào email để đọc nội dung chi tiết

### Xuất Dữ Liệu

1. Chọn định dạng: **TXT**, **CSV**, hoặc **XLSX**
2. Click nút **"Export"** 📥
3. File sẽ được tải xuống tự động

### Xóa Tài Khoản

- **Xóa 1 tài khoản**: Click icon 🗑️ ở hàng tương ứng
- **Xóa tất cả**: Click nút **"Xóa Tất Cả"** (⚠️ cẩn thận!)

## 🎨 Tùy Chỉnh

### Chế Độ Giao Diện

- Click icon 🌙/☀️ ở góc phải trên
- Chuyển đổi giữa Dark Mode và Light Mode

## ❓ Câu Hỏi Thường Gặp

### Q: Ứng dụng không khởi động được?
**A:** 
- Kiểm tra MongoDB đã chạy chưa
- Xem Settings và đảm bảo MongoDB URL đúng
- Thử khởi động lại ứng dụng

### Q: Không tạo được tài khoản?
**A:**
- Kiểm tra kết nối internet
- Đảm bảo MongoDB đã được cấu hình đúng
- Thử giảm số lượng tài khoản tạo cùng lúc

### Q: Email không nhận được?
**A:**
- Email tạm thời có thể mất vài phút
- Click "Check Inbox" sau 1-2 phút
- Một số email có thể không gửi tới (tùy thuộc dịch vụ email)

### Q: Muốn thay đổi MongoDB URL?
**A:**
- Click ⚙️ Settings
- Cập nhật MongoDB URL
- Lưu và khởi động lại ứng dụng

### Q: Dữ liệu được lưu ở đâu?
**A:**
- Tài khoản: Trong MongoDB database
- Settings: 
  - Windows: `%APPDATA%\garena-account-creator\`
  - macOS: `~/Library/Application Support/garena-account-creator/`
  - Linux: `~/.config/garena-account-creator/`

### Q: Có thể dùng không cần MongoDB Atlas không?
**A:** 
- Có! Cài MongoDB local là đủ
- MongoDB local nhanh hơn và không cần internet

### Q: Ứng dụng có an toàn không?
**A:**
- Hoàn toàn an toàn
- Không thu thập dữ liệu cá nhân
- Mã nguồn có thể kiểm tra
- Tất cả dữ liệu lưu local

## 🔒 Bảo Mật

- **KHÔNG** chia sẻ MongoDB connection string có password
- **KHÔNG** public API keys
- Dữ liệu của bạn chỉ lưu trên máy/cloud của bạn
- Ứng dụng không gửi dữ liệu đi đâu khác

## 🐛 Báo Lỗi

Nếu gặp lỗi:
1. Mở DevTools: Ctrl+Shift+I (Windows/Linux) hoặc Cmd+Option+I (Mac)
2. Xem tab Console để tìm thông báo lỗi
3. Báo cáo lỗi kèm:
   - Hệ điều hành
   - Thông báo lỗi
   - Các bước tái hiện lỗi

## 📞 Hỗ Trợ

- GitHub Issues: [Link to repo]
- Email: your-email@example.com
- Documentation: Xem BUILD_GUIDE.md

## 📝 Ghi Chú

- Tài khoản Garena được tạo chỉ để test/dev
- Tuân thủ Terms of Service của Garena
- Không sử dụng cho mục đích thương mại trái phép

---

**Chúc bạn sử dụng hiệu quả! 🎮**
