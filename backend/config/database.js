const mysql = require('mysql2/promise');
require('dotenv').config();

const pool = mysql.createPool({
    host: process.env.MYSQL_HOST || 'localhost',
    user: process.env.MYSQL_USER || 'root',
    password: process.env.MYSQL_PASSWORD || '190705',
    database: process.env.MYSQL_DATABASE || 'garena_creator_db',
    port: process.env.MYSQL_PORT || 3306,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const connect = async () => {
    try {
        const connection = await pool.getConnection();
        console.log(`✅ MySQL connected successfully to database: ${process.env.MYSQL_DATABASE || 'garena_creator_db'}`);
        connection.release();
        
        // Create tables
        await createTables();
    } catch (error) {
        console.error(`❌ Failed to connect to MySQL: ${error.message}`);
        // Don't exit, reusable pool might recover or user might fix DB
    }
};

const createTables = async () => {
    try {
        const [rows] = await pool.query(`
            CREATE TABLE IF NOT EXISTS garena_accounts (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS creation_jobs (
                job_id INT AUTO_INCREMENT PRIMARY KEY,
                total INT NOT NULL,
                completed INT DEFAULT 0,
                failed INT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'processing',
                accounts JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        
        console.log("✅ Database tables created/verified");
    } catch (error) {
        console.error(`⚠️ Failed to create tables: ${error.message}`);
    }
};

module.exports = {
    pool,
    connect
};
