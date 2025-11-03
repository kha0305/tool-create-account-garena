import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from dotenv import load_dotenv
import aiomysql
import json

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MySQLDatabase:
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        
    async def connect(self):
        """Create connection pool to MySQL"""
        try:
            host = os.environ.get('MYSQL_HOST', 'localhost')
            port = int(os.environ.get('MYSQL_PORT', '3306'))
            user = os.environ.get('MYSQL_USER', 'root')
            password = os.environ.get('MYSQL_PASSWORD', '')
            database = os.environ.get('MYSQL_DATABASE', 'garena_creator_db')
            
            self.pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=database,
                charset='utf8mb4',
                autocommit=True,
                minsize=1,
                maxsize=10
            )
            
            logger.info(f"✅ MySQL connected successfully to database: {database}")
            
            # Create tables if they don't exist
            await self.create_tables()
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            raise
    
    async def create_tables(self):
        """Create tables if they don't exist"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Create garena_accounts table
                    await cursor.execute("""
                        CREATE TABLE IF NOT EXISTS garena_accounts (
                            id VARCHAR(255) PRIMARY KEY,
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
                    """)
                    
                    # Create creation_jobs table
                    await cursor.execute("""
                        CREATE TABLE IF NOT EXISTS creation_jobs (
                            job_id VARCHAR(255) PRIMARY KEY,
                            total INT NOT NULL,
                            completed INT DEFAULT 0,
                            failed INT DEFAULT 0,
                            status VARCHAR(50) DEFAULT 'processing',
                            accounts JSON,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            INDEX idx_created_at (created_at)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """)
                    
                    await conn.commit()
            
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create tables: {e}")
    
    async def close(self):
        """Close MySQL connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("✅ MySQL connection closed")

    # ========== GARENA ACCOUNTS ==========
    async def insert_account(self, account_data: Dict[str, Any]) -> bool:
        """Insert a new account"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Convert datetime to string if needed
                    created_at = account_data.get('created_at')
                    if isinstance(created_at, datetime):
                        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Convert email_session_data to JSON string
                    session_data = account_data.get('email_session_data')
                    if session_data:
                        session_data = json.dumps(session_data)
                    
                    await cursor.execute("""
                        INSERT INTO garena_accounts 
                        (id, username, email, password, phone, status, email_provider, email_session_data, created_at, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        account_data.get('id'),
                        account_data.get('username'),
                        account_data.get('email'),
                        account_data.get('password'),
                        account_data.get('phone'),
                        account_data.get('status', 'creating'),
                        account_data.get('email_provider', 'mail.tm'),
                        session_data,
                        created_at,
                        account_data.get('error_message')
                    ))
                    await conn.commit()
                    return True
        except Exception as e:
            logger.error(f"❌ Error inserting account: {e}")
            return False
    
    async def find_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Find account by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        "SELECT * FROM garena_accounts WHERE id = %s",
                        (account_id,)
                    )
                    account = await cursor.fetchone()
                    
                    if account and account.get('email_session_data'):
                        # Parse JSON field
                        if isinstance(account['email_session_data'], str):
                            account['email_session_data'] = json.loads(account['email_session_data'])
                    
                    return account
        except Exception as e:
            logger.error(f"❌ Error finding account: {e}")
            return None

    async def find_all_accounts(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all accounts"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        "SELECT * FROM garena_accounts ORDER BY created_at DESC LIMIT %s",
                        (limit,)
                    )
                    accounts = await cursor.fetchall()
                    
                    # Parse JSON fields
                    for account in accounts:
                        if account.get('email_session_data') and isinstance(account['email_session_data'], str):
                            account['email_session_data'] = json.loads(account['email_session_data'])
                    
                    return accounts
        except Exception as e:
            logger.error(f"❌ Error fetching accounts: {e}")
            return []

    async def update_account(self, account_id: str, update_data: Dict[str, Any]) -> bool:
        """Update account"""
        try:
            if not update_data:
                return False
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Build SET clause dynamically
                    set_clauses = []
                    values = []
                    
                    for key, value in update_data.items():
                        if key == 'email_session_data' and isinstance(value, dict):
                            value = json.dumps(value)
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                    
                    values.append(account_id)
                    
                    query = f"UPDATE garena_accounts SET {', '.join(set_clauses)} WHERE id = %s"
                    await cursor.execute(query, values)
                    await conn.commit()
                    
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error updating account: {e}")
            return False

    async def delete_account(self, account_id: str) -> int:
        """Delete account by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "DELETE FROM garena_accounts WHERE id = %s",
                        (account_id,)
                    )
                    await conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Error deleting account: {e}")
            return 0

    async def delete_all_accounts(self) -> int:
        """Delete all accounts"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("DELETE FROM garena_accounts")
                    await conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Error deleting all accounts: {e}")
            return 0

    async def delete_multiple_accounts(self, account_ids: list) -> int:
        """Delete multiple accounts by IDs"""
        try:
            if not account_ids:
                return 0
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(account_ids))
                    query = f"DELETE FROM garena_accounts WHERE id IN ({placeholders})"
                    await cursor.execute(query, account_ids)
                    await conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Error deleting multiple accounts: {e}")
            return 0


    # ========== CREATION JOBS ==========
    async def insert_job(self, job_data: Dict[str, Any]) -> bool:
        """Insert a new job"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Convert datetime to string if needed
                    created_at = job_data.get('created_at')
                    if isinstance(created_at, datetime):
                        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Convert accounts list to JSON string
                    accounts = job_data.get('accounts', [])
                    if accounts:
                        accounts = json.dumps(accounts)
                    else:
                        accounts = json.dumps([])
                    
                    await cursor.execute("""
                        INSERT INTO creation_jobs 
                        (job_id, total, completed, failed, status, accounts, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        job_data.get('job_id'),
                        job_data.get('total'),
                        job_data.get('completed', 0),
                        job_data.get('failed', 0),
                        job_data.get('status', 'processing'),
                        accounts,
                        created_at
                    ))
                    await conn.commit()
                    return True
        except Exception as e:
            logger.error(f"❌ Error inserting job: {e}")
            return False

    async def find_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find job by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        "SELECT * FROM creation_jobs WHERE job_id = %s",
                        (job_id,)
                    )
                    job = await cursor.fetchone()
                    
                    if job and job.get('accounts'):
                        # Parse JSON field
                        if isinstance(job['accounts'], str):
                            job['accounts'] = json.loads(job['accounts'])
                    
                    return job
        except Exception as e:
            logger.error(f"❌ Error finding job: {e}")
            return None

    async def update_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update job fields"""
        try:
            if not update_data:
                return False
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Handle MongoDB-style update operators
                    if "$inc" in update_data:
                        # Handle increment operations
                        for field, value in update_data["$inc"].items():
                            await cursor.execute(
                                f"UPDATE creation_jobs SET {field} = {field} + %s WHERE job_id = %s",
                                (value, job_id)
                            )
                    
                    if "$push" in update_data:
                        # Handle array push operations
                        for field, value in update_data["$push"].items():
                            if field == "accounts":
                                # Get current accounts
                                await cursor.execute(
                                    "SELECT accounts FROM creation_jobs WHERE job_id = %s",
                                    (job_id,)
                                )
                                result = await cursor.fetchone()
                                if result:
                                    current_accounts = json.loads(result[0]) if result[0] else []
                                    current_accounts.append(value)
                                    await cursor.execute(
                                        "UPDATE creation_jobs SET accounts = %s WHERE job_id = %s",
                                        (json.dumps(current_accounts), job_id)
                                    )
                    
                    if "$set" in update_data:
                        # Handle set operations
                        set_clauses = []
                        values = []
                        for field, value in update_data["$set"].items():
                            set_clauses.append(f"{field} = %s")
                            values.append(value)
                        
                        if set_clauses:
                            values.append(job_id)
                            query = f"UPDATE creation_jobs SET {', '.join(set_clauses)} WHERE job_id = %s"
                            await cursor.execute(query, values)
                    
                    await conn.commit()
                    return True
        except Exception as e:
            logger.error(f"❌ Error updating job: {e}")
            return False


# Global database instance
db = MySQLDatabase()
