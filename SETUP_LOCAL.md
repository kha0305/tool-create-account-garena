# 🚀 Hướng Dẫn Setup Chạy Local

## 📋 Yêu Cầu Hệ Thống

- **Node.js**: >= 14.x
- **Python**: >= 3.9
- **MySQL/MariaDB**: >= 5.7 / >= 10.3
- **Yarn**: Package manager cho frontend

## ⚙️ Cấu Hình

### 1. Database Setup (MySQL)

#### Cài đặt MySQL/MariaDB (nếu chưa có):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y mariadb-server

# Start service
sudo service mariadb start
```

#### Tạo Database và Set Password:
```bash
# Set root password
mysql -u root -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('190705'); FLUSH PRIVILEGES;"

# Create database
mysql -u root -p190705 -e "CREATE DATABASE IF NOT EXISTS garena_creator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. Backend Setup

#### Install Dependencies:
```bash
cd /app/backend
pip install -r requirements.txt
```

#### Environment Variables (`.env`):
```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=190705
MYSQL_DATABASE=garena_creator_db

# CORS
CORS_ORIGINS=*

# API Keys
TEMP_MAIL_API_KEY=TZvExfsiaNZBBfi3z047GsrfUEgNRWp3
```

#### Start Backend:
```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

#### Install Dependencies:
```bash
cd /app/frontend
yarn install
```

#### Environment Variables (`.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### Start Frontend:
```bash
cd /app/frontend
yarn start
```

## 🎯 Kiểm Tra Kết Nối

### Backend API:
```bash
curl http://localhost:8001/api/
# Response: {"message":"Garena Account Creator API"}
```

### MySQL Connection:
```bash
mysql -u root -p190705 garena_creator_db -e "SHOW TABLES;"
# Should show: garena_accounts, creation_jobs
```

### Frontend:
Truy cập: `http://localhost:3000`

## 📦 Database Tables

### `garena_accounts`
Lưu trữ thông tin tài khoản Garena đã tạo:
- `id` (VARCHAR 36) - Primary Key
- `username` - Tên đăng nhập
- `email` - Email tạm thời
- `password` - Mật khẩu
- `phone` - Số điện thoại
- `status` - Trạng thái (creating, created, verified, failed)
- `email_provider` - Nhà cung cấp email (mail.tm)
- `email_session_data` - JSON data cho session
- `created_at` - Thời gian tạo
- `error_message` - Thông báo lỗi (nếu có)

### `creation_jobs`
Lưu trạng thái job tạo hàng loạt:
- `job_id` (VARCHAR 36) - Primary Key
- `total` - Tổng số tài khoản cần tạo
- `completed` - Số tài khoản đã tạo thành công
- `failed` - Số tài khoản tạo thất bại
- `status` - Trạng thái job
- `accounts` - JSON array chứa account IDs
- `created_at` - Thời gian tạo job

## 🔧 Troubleshooting

### MySQL Connection Error:
```bash
# Check if MySQL is running
sudo service mariadb status

# Restart MySQL
sudo service mariadb restart

# Verify password
mysql -u root -p190705 -e "SELECT 1;"
```

### Backend Not Starting:
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Verify Python dependencies
cd /app/backend && pip install -r requirements.txt
```

### Frontend Not Connecting:
- Kiểm tra `REACT_APP_BACKEND_URL` trong `/app/frontend/.env`
- Phải là `http://localhost:8001` (không có trailing slash)
- Clear cache: `yarn cache clean`

## ✨ Features

### Email Provider
- **Mail.tm**: Email tạm thời với hỗ trợ inbox đầy đủ
- Tự động tạo account và lấy JWT token
- Hỗ trợ xem nội dung email (text/html)

### Export Options
- **TXT**: Format `username|password|email|Tạo lúc: dd-mm-yy hh:mm`
- **CSV**: Format chuẩn với headers
- **XLSX**: Excel với styling

### API Endpoints
- `POST /api/accounts/create` - Tạo hàng loạt tài khoản
- `GET /api/accounts/job/{job_id}` - Kiểm tra trạng thái job
- `GET /api/accounts` - Lấy tất cả tài khoản
- `GET /api/accounts/{id}/inbox` - Xem inbox email
- `GET /api/accounts/{id}/inbox/{message_id}` - Xem chi tiết email
- `GET /api/accounts/export/txt` - Export TXT
- `GET /api/accounts/export/csv` - Export CSV
- `GET /api/accounts/export/xlsx` - Export XLSX
- `DELETE /api/accounts/{id}` - Xóa tài khoản
- `DELETE /api/accounts` - Xóa tất cả

## 🔒 Security Notes

- Password được generate theo yêu cầu Garena: 8-16 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt
- Email session data được encrypt trong JWT token
- MySQL password nên thay đổi trong production environment

## 📝 Maintenance

### Backup Database:
```bash
mysqldump -u root -p190705 garena_creator_db > backup_$(date +%Y%m%d).sql
```

### Restore Database:
```bash
mysql -u root -p190705 garena_creator_db < backup_20251101.sql
```

### Clear All Data:
```bash
mysql -u root -p190705 garena_creator_db -e "TRUNCATE TABLE garena_accounts; TRUNCATE TABLE creation_jobs;"
```

## 🎉 Hoàn Tất!

Ứng dụng đã sẵn sàng chạy trên local với MySQL database!

- Backend: http://localhost:8001
- Frontend: http://localhost:3000
- API Docs: http://localhost:8001/docs
