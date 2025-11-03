# Hướng dẫn sử dụng phpMyAdmin

## Bước 1: Cài đặt XAMPP (nếu chưa có)

### Tải XAMPP:
- Link: https://www.apachefriends.org/download.html
- Chọn phiên bản Windows
- Tải file installer (.exe)

### Cài đặt:
1. Chạy file installer
2. Chọn components: Apache, MySQL, phpMyAdmin
3. Chọn folder cài đặt (mặc định: C:\xampp)
4. Click "Next" và hoàn tất cài đặt

## Bước 2: Start MySQL và Apache

1. Mở **XAMPP Control Panel**
   - Tìm trong Start Menu: "XAMPP Control Panel"
   - Hoặc chạy: `C:\xampp\xampp-control.exe`

2. Trong XAMPP Control Panel:
   - Click nút **"Start"** bên cạnh **MySQL** (chữ xanh lá)
   - Click nút **"Start"** bên cạnh **Apache** (chữ xanh lá)
   
3. Đợi đến khi 2 services chuyển sang màu xanh lá cây
   - MySQL chạy trên port: **3306**
   - Apache chạy trên port: **80**

## Bước 3: Truy cập phpMyAdmin

### Mở trình duyệt và truy cập:
```
http://localhost/phpmyadmin
```

Hoặc:
```
http://127.0.0.1/phpmyadmin
```

### Giao diện phpMyAdmin:
- Bên trái: Danh sách databases
- Giữa: Các tabs (Structure, SQL, Search, etc.)
- Trên: Menu chính

## Bước 4: Tạo Database (nếu chưa có)

### Cách 1: Từ trang chủ
1. Click tab **"Databases"** ở trên
2. Nhập tên database: `garena_creator_db`
3. Chọn Collation: `utf8mb4_unicode_ci`
4. Click **"Create"**

### Cách 2: Dùng SQL
1. Click tab **"SQL"** ở trên
2. Paste lệnh sau:
```sql
CREATE DATABASE IF NOT EXISTS garena_creator_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```
3. Click **"Go"**

## Bước 5: Xóa và Tạo lại Tables (Fix lỗi)

### Chọn database:
1. Click vào **"garena_creator_db"** bên trái
2. Database sẽ được highlight màu vàng

### Xóa tables cũ:
1. Click tab **"SQL"** ở trên
2. Paste đoạn SQL sau:
```sql
DROP TABLE IF EXISTS garena_accounts;
DROP TABLE IF EXISTS creation_jobs;
```
3. Click **"Go"**
4. Sẽ thấy thông báo: "2 rows affected"

### Tạo lại tables mới:
1. Vẫn trong tab **"SQL"**
2. Paste đoạn SQL sau:
```sql
CREATE TABLE garena_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'creating',
    email_provider VARCHAR(100) DEFAULT 'mail.tm',
    email_session_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    error_message TEXT,
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE creation_jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    total INT NOT NULL,
    completed INT DEFAULT 0,
    failed INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing',
    accounts JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
3. Click **"Go"**
4. Sẽ thấy thông báo: "2 rows affected"

### Kiểm tra tables:
1. Click vào **"garena_creator_db"** bên trái (refresh)
2. Bạn sẽ thấy 2 tables:
   - `garena_accounts`
   - `creation_jobs`
3. Click vào từng table để xem cấu trúc

## Bước 6: Kiểm tra cấu trúc Table

### Xem cấu trúc garena_accounts:
1. Click vào table **"garena_accounts"** bên trái
2. Click tab **"Structure"**
3. Kiểm tra field **"id"**:
   - Type: `int(11)`
   - Extra: `AUTO_INCREMENT`
   - Key: `PRI` (Primary Key)

### Xem cấu trúc creation_jobs:
1. Click vào table **"creation_jobs"** bên trái
2. Click tab **"Structure"**
3. Kiểm tra field **"job_id"**:
   - Type: `int(11)`
   - Extra: `AUTO_INCREMENT`
   - Key: `PRI` (Primary Key)

## Bước 7: Restart Backend

Sau khi fix database, restart backend:

```bash
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Bạn sẽ thấy:
```
✅ MySQL connected successfully to database: garena_creator_db
✅ Database tables created successfully
```

## Các thao tác hữu ích trong phpMyAdmin:

### Xem dữ liệu trong table:
1. Click vào table name bên trái
2. Click tab **"Browse"**
3. Bạn sẽ thấy tất cả rows

### Xóa tất cả dữ liệu (giữ cấu trúc):
1. Click vào table name
2. Click tab **"Operations"**
3. Scroll xuống phần **"Table maintenance"**
4. Click **"Empty the table (TRUNCATE)"**

### Xóa table hoàn toàn:
1. Click vào table name
2. Click tab **"Operations"**
3. Scroll xuống cuối
4. Click **"Delete the table (DROP)"**
5. Confirm

### Export database (backup):
1. Click vào database name bên trái
2. Click tab **"Export"**
3. Chọn **"Quick"** export method
4. Click **"Go"**
5. File .sql sẽ được download

### Import database (restore):
1. Click vào database name bên trái
2. Click tab **"Import"**
3. Click **"Choose File"**
4. Chọn file .sql
5. Click **"Go"**

### Chạy SQL query tùy ý:
1. Click tab **"SQL"** ở trên
2. Nhập SQL query
3. Click **"Go"**

Ví dụ queries:
```sql
-- Xem tất cả accounts
SELECT * FROM garena_accounts;

-- Đếm số accounts
SELECT COUNT(*) FROM garena_accounts;

-- Xem accounts mới nhất
SELECT * FROM garena_accounts ORDER BY id DESC LIMIT 10;

-- Xóa account cụ thể
DELETE FROM garena_accounts WHERE id = 5;

-- Reset AUTO_INCREMENT về 1
ALTER TABLE garena_accounts AUTO_INCREMENT = 1;
```

## Xử lý lỗi thường gặp:

### Lỗi: "Cannot connect to MySQL"
**Giải pháp:**
1. Mở XAMPP Control Panel
2. Ensure MySQL đã Start (màu xanh)
3. Nếu không start được, check port 3306 có bị chiếm không

### Lỗi: "Access denied for user 'root'@'localhost'"
**Giải pháp:**
1. Mặc định XAMPP không có password cho root
2. Nếu đã đặt password, cần config:
   - File: `C:\xampp\phpMyAdmin\config.inc.php`
   - Sửa dòng: `$cfg['Servers'][$i]['password'] = 'your_password';`

### Lỗi: "Port 3306 is busy"
**Giải pháp:**
1. Có MySQL server khác đang chạy
2. Tắt MySQL service khác:
   - Windows + R → `services.msc`
   - Tìm "MySQL" → Stop
3. Hoặc đổi port trong XAMPP:
   - XAMPP Control Panel → MySQL → Config → my.ini
   - Tìm `port=3306` → Đổi thành `port=3307`

## Video hướng dẫn (YouTube):

Tìm kiếm trên YouTube:
- "How to use phpMyAdmin"
- "XAMPP phpMyAdmin tutorial"
- "Create MySQL database phpMyAdmin"

## Kết luận:

1. ✅ Cài XAMPP
2. ✅ Start MySQL và Apache
3. ✅ Truy cập http://localhost/phpmyadmin
4. ✅ Tạo/chọn database `garena_creator_db`
5. ✅ Chạy SQL để DROP và CREATE tables
6. ✅ Restart backend

Nếu làm đúng các bước trên, lỗi `Field 'job_id' doesn't have a default value` sẽ được fix!
