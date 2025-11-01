# Hướng Dẫn Chạy Local với MySQL

## Đã Hoàn Thành

✅ App đã được migrate sang MySQL database
✅ MariaDB server đang chạy
✅ Database và tables đã được tạo
✅ Backend API hoạt động với MySQL

## Thông Tin Cấu Hình

### Database Configuration
- **Host**: localhost
- **Port**: 3306
- **Database**: garena_creator_db
- **User**: garena_user
- **Password**: garena_pass_2024

### Tables
- `garena_accounts`: Lưu trữ tài khoản Garena
- `creation_jobs`: Theo dõi tiến trình tạo tài khoản

## Để Chạy Local trên Máy Của Bạn

### 1. Yêu Cầu Hệ Thống
```bash
- Python 3.11+
- Node.js 18+
- MySQL/MariaDB 10.11+
- Git
```

### 2. Clone Code
```bash
# Download toàn bộ code về máy
git clone <repository-url>
cd app
```

### 3. Setup Backend

#### Cài đặt MySQL/MariaDB
```bash
# Ubuntu/Debian
sudo apt-get install mariadb-server mariadb-client

# macOS
brew install mariadb

# Windows
# Download từ: https://mariadb.org/download/
```

#### Tạo Database
```bash
sudo mysql -e "CREATE DATABASE garena_creator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'garena_user'@'localhost' IDENTIFIED BY 'garena_pass_2024';"
sudo mysql -e "GRANT ALL PRIVILEGES ON garena_creator_db.* TO 'garena_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

#### Cài đặt Python Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Cấu hình .env
File `/backend/.env` đã được cấu hình sẵn:
```env
# MySQL Configuration
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_USER="garena_user"
MYSQL_PASSWORD="garena_pass_2024"
MYSQL_DATABASE="garena_creator_db"
```

#### Chạy Backend
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Setup Frontend

#### Cài đặt Node Dependencies
```bash
cd frontend
yarn install  # hoặc npm install
```

#### Cấu hình .env
Tạo file `/frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### Chạy Frontend
```bash
cd frontend
yarn start  # hoặc npm start
```

### 5. Truy Cập App
Mở browser: `http://localhost:3000`

## Kiểm Tra Hệ Thống

### Test Database Connection
```bash
sudo mysql -D garena_creator_db -e "SHOW TABLES;"
```

### Test Backend API
```bash
curl http://localhost:8001/api/email-providers
```

### Test Account Creation
```bash
curl -X POST http://localhost:8001/api/accounts/create \
  -H "Content-Type: application/json" \
  -d '{"quantity": 1, "email_provider": "mail.tm"}'
```

## Lưu Ý Quan Trọng

### Rate Limiting
Mail.tm API có giới hạn:
- Mỗi account cần ~10-15 giây
- Tạo nhiều accounts cần kiên nhẫn
- System có retry logic tự động

### Database
- Tables được tạo tự động khi backend start
- Không cần chạy migration scripts
- Data được lưu persistent trong MySQL

### Troubleshooting

#### Backend không kết nối được MySQL
```bash
# Kiểm tra MySQL có đang chạy không
sudo service mariadb status

# Start MySQL nếu cần
sudo service mariadb start

# Test connection
mysql -u garena_user -pgarena_pass_2024 -D garena_creator_db -e "SELECT 1;"
```

#### Frontend không gọi được Backend
- Đảm bảo backend đang chạy trên port 8001
- Check REACT_APP_BACKEND_URL trong frontend/.env
- Clear browser cache và refresh

#### Mail.tm Rate Limiting
- Đây là hành vi bình thường
- Giảm số lượng accounts tạo mỗi lần
- Đợi 1-2 phút giữa các lần tạo

## Cấu Trúc Database

### Table: garena_accounts
```sql
CREATE TABLE garena_accounts (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'created',
    email_provider VARCHAR(50) DEFAULT 'mail.tm',
    email_session_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### Table: creation_jobs
```sql
CREATE TABLE creation_jobs (
    id VARCHAR(36) PRIMARY KEY,
    status VARCHAR(50) DEFAULT 'processing',
    total INT DEFAULT 0,
    completed INT DEFAULT 0,
    failed INT DEFAULT 0,
    email_provider VARCHAR(50) DEFAULT 'mail.tm',
    accounts JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

## Export Data

### Export Accounts to File
```bash
# TXT format
curl http://localhost:8001/api/accounts/export/txt -o accounts.txt

# CSV format
curl http://localhost:8001/api/accounts/export/csv -o accounts.csv

# XLSX format
curl http://localhost:8001/api/accounts/export/xlsx -o accounts.xlsx
```

### Export từ MySQL
```bash
sudo mysql -D garena_creator_db -e "SELECT * FROM garena_accounts;" > accounts_dump.txt
```

## Support

Nếu gặp vấn đề:
1. Check backend logs: `tail -f backend.log`
2. Check MySQL logs: `sudo tail -f /var/log/mysql/error.log`
3. Verify database connection
4. Đảm bảo tất cả dependencies đã được cài đặt
