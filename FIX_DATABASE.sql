-- Script để fix database sau khi thay đổi schema
-- Chạy script này trong MySQL để tạo lại tables với AUTO_INCREMENT

-- Xóa tables cũ (cảnh báo: mất data!)
DROP TABLE IF EXISTS garena_accounts;
DROP TABLE IF EXISTS creation_jobs;

-- Tạo lại table garena_accounts với ID AUTO_INCREMENT
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

-- Tạo lại table creation_jobs với job_id AUTO_INCREMENT
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

-- Kiểm tra tables đã được tạo
SHOW TABLES;

-- Kiểm tra cấu trúc
DESCRIBE garena_accounts;
DESCRIBE creation_jobs;
