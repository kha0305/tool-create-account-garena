# Hướng Dẫn Chạy App Local

## 🎯 Yêu Cầu Hệ Thống

- Node.js 16+ và Yarn
- Python 3.8+
- MongoDB
- Git

## 📦 Cài Đặt

### 1. Clone Repository
```bash
cd /app
```

### 2. Cài Đặt Backend
```bash
cd /app/backend
pip install -r requirements.txt
```

### 3. Cài Đặt Frontend
```bash
cd /app/frontend
yarn install
```

## ⚙️ Cấu Hình

### Backend (.env)
File: `/app/backend/.env`
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="garena_creator_db"
CORS_ORIGINS="*"
TEMP_MAIL_API_KEY="TZvExfsiaNZBBfi3z047GsrfUEgNRWp3"
```

### Frontend (.env)
File: `/app/frontend/.env`
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

## 🚀 Khởi Động Ứng Dụng

### Cách 1: Sử dụng Supervisor (Khuyên Dùng)
```bash
# Start tất cả services
sudo supervisorctl restart all

# Kiểm tra trạng thái
sudo supervisorctl status

# Xem logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

### Cách 2: Chạy Thủ Công

#### Terminal 1 - MongoDB
```bash
mongod --dbpath /data/db
```

#### Terminal 2 - Backend
```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 3 - Frontend
```bash
cd /app/frontend
yarn start
```

## 🌐 Truy Cập

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 📝 Sử Dụng

### 1. Tạo Tài Khoản
- Chọn số lượng tài khoản muốn tạo (1-100)
- Email provider mặc định: Mail.tm
- Click "Tạo Tài Khoản"
- Đợi quá trình hoàn tất (khoảng 3 giây/tài khoản)

### 2. Xuất Dữ Liệu
- Chọn format: TXT, CSV, hoặc XLSX
- Click "Export Tài Khoản"
- File sẽ tự động download

### 3. Kiểm Tra Email
- Click icon 📧 ở cột "Actions"
- Xem danh sách email nhận được
- Click vào email để xem chi tiết

## ⚠️ Lưu Ý Quan Trọng

### Rate Limiting
Mail.tm API có giới hạn số request:
- **Khuyên dùng**: Tạo 1-10 tài khoản mỗi lần
- **Tối đa**: 20 tài khoản/lần (có thể chậm)
- **Delay tự động**: 2-3 giây giữa mỗi tài khoản

### Xử Lý Lỗi
Nếu gặp lỗi khi tạo tài khoản:
1. **Đợi 30 giây** trước khi thử lại
2. Giảm số lượng tài khoản xuống 3-5
3. Kiểm tra kết nối internet
4. Xem logs để debug

### Thời Gian Tạo Dự Kiến
- 1 tài khoản: ~3 giây
- 5 tài khoản: ~15-20 giây
- 10 tài khoản: ~30-40 giây
- 20 tài khoản: ~1-2 phút

## 🛠️ Troubleshooting

### Backend không khởi động
```bash
# Kiểm tra logs
tail -n 50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend

# Kiểm tra MongoDB
sudo supervisorctl status mongodb
```

### Frontend không kết nối được Backend
```bash
# Kiểm tra backend URL trong .env
cat /app/frontend/.env | grep BACKEND_URL

# Kiểm tra backend đang chạy
curl http://localhost:8001/api/

# Restart frontend
sudo supervisorctl restart frontend
```

### Lỗi "Cannot create account"
1. Đợi 30 giây
2. Thử tạo chỉ 1 tài khoản để test
3. Kiểm tra logs backend
4. Kiểm tra kết nối internet

### Database lỗi
```bash
# Khởi động MongoDB
sudo supervisorctl restart mongodb

# Kiểm tra kết nối
mongo garena_creator_db --eval "db.stats()"
```

## 🔍 Kiểm Tra Log

### Backend Logs
```bash
# Error logs
tail -f /var/log/supervisor/backend.err.log

# Output logs
tail -f /var/log/supervisor/backend.out.log

# Tìm lỗi cụ thể
grep -i "error" /var/log/supervisor/backend.err.log | tail -20
```

### Frontend Logs
```bash
# Error logs
tail -f /var/log/supervisor/frontend.err.log

# Build logs
tail -f /var/log/supervisor/frontend.out.log
```

## 📊 Database

### Truy cập MongoDB
```bash
# Kết nối MongoDB
mongo garena_creator_db

# Xem collections
show collections

# Đếm tài khoản
db.garena_accounts.count()

# Xem tài khoản mới nhất
db.garena_accounts.find().sort({created_at: -1}).limit(5).pretty()

# Xóa tất cả tài khoản
db.garena_accounts.deleteMany({})
```

## 🎨 Features

### ✅ Đã Có
- Tạo tài khoản Garena tự động
- Email tạm từ Mail.tm với JWT authentication
- Export TXT/CSV/XLSX
- Kiểm tra hộp thư đến
- Xem chi tiết email (Text/HTML)
- Copy nhanh username/email/password
- Dark/Light mode
- Retry tự động khi lỗi
- Delay tự động để tránh rate limiting

### 🔧 Tính Năng Kỹ Thuật
- Rate limiting protection
- Exponential backoff khi lỗi
- Auto retry (3 lần)
- Connection pooling với MongoDB
- Async/await cho performance
- Error logging chi tiết

## 💡 Tips

1. **Tạo nhiều tài khoản**: Chia nhỏ thành nhiều batch 5-10 tài khoản
2. **Kiểm tra email**: Đợi 1-2 phút sau khi tạo trước khi check inbox
3. **Export dữ liệu**: Export ngay sau khi tạo để backup
4. **Performance**: Đóng tab khác khi tạo nhiều tài khoản

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs
2. Restart services
3. Đợi 30 giây và thử lại
4. Giảm số lượng tài khoản

## 🔄 Updates

### Version 1.0 (Current)
- ✅ Migration từ temp-mail/10minutemail sang Mail.tm
- ✅ Rate limiting protection
- ✅ Auto retry mechanism
- ✅ Better error handling
- ✅ Improved logging
- ✅ MongoDB integration
- ✅ Export multiple formats (TXT/CSV/XLSX)
- ✅ Email content viewer (Text/HTML)

---
**Lưu ý**: App này chỉ dùng cho mục đích test và development. Tôn trọng Terms of Service của các dịch vụ.
