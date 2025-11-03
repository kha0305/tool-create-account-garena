# Hướng dẫn cài đặt MySQL cho Windows

## 1. Cài đặt MySQL trên Windows

### Tùy chọn 1: MySQL Community Server (Khuyên dùng)
1. Tải MySQL Community Server từ: https://dev.mysql.com/downloads/mysql/
2. Chạy file cài đặt (.msi)
3. Chọn "Developer Default" hoặc "Server only"
4. Thiết lập mật khẩu root (hoặc để trống nếu muốn)
5. Hoàn tất cài đặt

### Tùy chọn 2: XAMPP (Dễ hơn)
1. Tải XAMPP từ: https://www.apachefriends.org/download.html
2. Cài đặt XAMPP
3. Mở XAMPP Control Panel
4. Nhấn "Start" cho MySQL

## 2. Tạo Database

### Cách 1: Sử dụng MySQL Command Line
```bash
# Mở Command Prompt hoặc PowerShell
mysql -u root -p

# Trong MySQL prompt:
CREATE DATABASE garena_creator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Cách 2: Sử dụng phpMyAdmin (nếu dùng XAMPP)
1. Mở trình duyệt: http://localhost/phpmyadmin
2. Click "New" bên trái
3. Nhập tên database: `garena_creator_db`
4. Chọn Collation: `utf8mb4_unicode_ci`
5. Click "Create"

## 3. Cấu hình Backend

File `.env` đã được cập nhật với cấu hình MySQL:

```env
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD=""
MYSQL_DATABASE="garena_creator_db"
```

**Lưu ý:** 
- Nếu bạn đặt mật khẩu cho MySQL root, hãy cập nhật `MYSQL_PASSWORD="your_password"`
- Nếu MySQL chạy ở port khác, cập nhật `MYSQL_PORT`

## 4. Cài đặt Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 5. Chạy Backend

```bash
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

## 6. Kiểm tra kết nối

Khi backend khởi động, bạn sẽ thấy:
```
✅ MySQL connected successfully to database: garena_creator_db
✅ Database tables created successfully
```

Nếu thành công, các bảng sẽ được tự động tạo:
- `garena_accounts` - Lưu thông tin tài khoản
- `creation_jobs` - Theo dõi công việc tạo tài khoản

## 7. Kiểm tra Frontend

```bash
cd frontend
npm install  # hoặc yarn install
npm start    # hoặc yarn start
```

Frontend sẽ chạy tại: http://localhost:3000

## Xử lý lỗi thường gặp

### Lỗi: "Access denied for user 'root'@'localhost'"
**Giải pháp:**
1. Kiểm tra mật khẩu trong `.env` có đúng không
2. Reset mật khẩu MySQL root:
   ```bash
   # Dùng MySQL Command Line
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
   FLUSH PRIVILEGES;
   ```

### Lỗi: "Can't connect to MySQL server on 'localhost'"
**Giải pháp:**
1. Kiểm tra MySQL service đang chạy:
   - Windows + R → `services.msc`
   - Tìm "MySQL" → Nhấn chuột phải → Start
2. Hoặc dùng XAMPP Control Panel → Start MySQL

### Lỗi: "Unknown database 'garena_creator_db'"
**Giải pháp:**
```bash
mysql -u root -p
CREATE DATABASE garena_creator_db;
EXIT;
```

## Các lệnh MySQL hữu ích

```bash
# Xem tất cả databases
SHOW DATABASES;

# Chọn database
USE garena_creator_db;

# Xem tất cả tables
SHOW TABLES;

# Xem cấu trúc table
DESCRIBE garena_accounts;

# Xem dữ liệu
SELECT * FROM garena_accounts;

# Xóa tất cả dữ liệu (cẩn thận!)
TRUNCATE TABLE garena_accounts;
```

## Cấu trúc Tables

### Table: garena_accounts
- `id` (VARCHAR 255) - Primary Key
- `username` (VARCHAR 255)
- `email` (VARCHAR 255)
- `password` (VARCHAR 255)
- `phone` (VARCHAR 50)
- `status` (VARCHAR 50)
- `email_provider` (VARCHAR 100)
- `email_session_data` (JSON)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
- `error_message` (TEXT)

### Table: creation_jobs
- `job_id` (VARCHAR 255) - Primary Key
- `total` (INT)
- `completed` (INT)
- `failed` (INT)
- `status` (VARCHAR 50)
- `accounts` (JSON)
- `created_at` (DATETIME)

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. MySQL service đang chạy
2. Thông tin đăng nhập trong `.env` đúng
3. Database đã được tạo
4. Port 3306 không bị block bởi firewall
