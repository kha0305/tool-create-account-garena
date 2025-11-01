#!/bin/bash
# Script to start MySQL/MariaDB service

echo "🚀 Starting MySQL/MariaDB service..."

# Check if MySQL/MariaDB is already running
if service mariadb status > /dev/null 2>&1; then
    echo "✅ MariaDB is already running"
else
    # Start MariaDB
    service mariadb start
    
    if [ $? -eq 0 ]; then
        echo "✅ MariaDB started successfully"
    else
        echo "❌ Failed to start MariaDB"
        exit 1
    fi
fi

# Verify connection
if mysql -u root -p190705 -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ MySQL connection verified"
else
    echo "❌ MySQL connection failed"
    exit 1
fi

# Ensure database exists
mysql -u root -p190705 -e "CREATE DATABASE IF NOT EXISTS garena_creator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" > /dev/null 2>&1

echo "✅ MySQL is ready for connections"
