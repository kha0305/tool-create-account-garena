import aiomysql
import os
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables (nếu có file .env)
load_dotenv()

logger = logging.getLogger(__name__)

class MySQLDatabase:
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        
    async def connect(self):
        """Create connection pool to MySQL"""
        try:
            self.pool = await aiomysql.create_pool(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                port=int(os.environ.get('MYSQL_PORT', 3306)),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', '190705'),
                db=os.environ.get('MYSQL_DATABASE', 'garena_creator_db'),
                autocommit=True,
                charset='utf8mb4',
                minsize=1,
                maxsize=10
            )
            logger.info("✅ MySQL connection pool created successfully")
            await self.create_tables()
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            raise
    
    async def create_tables(self):
        """Create tables if they don't exist"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Table garena_accounts
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS garena_accounts (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        phone VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'creating',
                        email_provider VARCHAR(50) DEFAULT 'mail.tm',
                        email_session_data JSON,
                        created_at DATETIME NOT NULL,
                        error_message TEXT,
                        INDEX idx_created_at (created_at DESC),
                        INDEX idx_status (status)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # Table creation_jobs
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS creation_jobs (
                        job_id VARCHAR(36) PRIMARY KEY,
                        total INT NOT NULL,
                        completed INT DEFAULT 0,
                        failed INT DEFAULT 0,
                        status VARCHAR(50) DEFAULT 'processing',
                        accounts JSON,
                        created_at DATETIME NOT NULL,
                        INDEX idx_created_at (created_at DESC)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                logger.info("✅ Database tables created successfully")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("✅ MySQL connection pool closed")

    # ========== GARERA ACCOUNTS ==========
    async def insert_account(self, account_data: Dict[str, Any]) -> bool:
        """Insert a new account"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    created_at = account_data['created_at']
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                    email_session_data = account_data.get('email_session_data')
                    if email_session_data and not isinstance(email_session_data, str):
                        email_session_data = json.dumps(email_session_data)

                    await cursor.execute("""
                        INSERT INTO garena_accounts 
                        (id, username, email, password, phone, status, email_provider, email_session_data, created_at, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        account_data['id'],
                        account_data['username'],
                        account_data['email'],
                        account_data['password'],
                        account_data.get('phone'),
                        account_data.get('status', 'creating'),
                        account_data.get('email_provider', 'mail.tm'),
                        email_session_data,
                        created_at,
                        account_data.get('error_message')
                    ))
                    return True
        except Exception as e:
            logger.error(f"❌ Error inserting account: {e}")
            return False
    
    async def find_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Find account by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute("SELECT * FROM garena_accounts WHERE id = %s", (account_id,))
                    result = await cursor.fetchone()
                    if result:
                        if result.get('email_session_data'):
                            result['email_session_data'] = json.loads(result['email_session_data'])
                        if result.get('created_at'):
                            result['created_at'] = result['created_at'].isoformat()
                    return result
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
                    results = await cursor.fetchall()
                    for result in results:
                        if result.get('email_session_data'):
                            try:
                                result['email_session_data'] = json.loads(result['email_session_data'])
                            except Exception:
                                pass
                        if result.get('created_at'):
                            result['created_at'] = result['created_at'].isoformat()
                    return results
        except Exception as e:
            logger.error(f"❌ Error fetching accounts: {e}")
            return []

    async def update_account(self, account_id: str, update_data: Dict[str, Any]) -> bool:
        """Update account"""
        try:
            if not update_data:
                return False
            set_parts = [f"{k} = %s" for k in update_data.keys()]
            values = list(update_data.values()) + [account_id]
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"UPDATE garena_accounts SET {', '.join(set_parts)} WHERE id = %s", values)
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error updating account: {e}")
            return False

    async def delete_account(self, account_id: str) -> int:
        """Delete account by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("DELETE FROM garena_accounts WHERE id = %s", (account_id,))
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
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Error deleting all accounts: {e}")
            return 0

    # ========== CREATION JOBS ==========
    async def insert_job(self, job_data: Dict[str, Any]) -> bool:
        """Insert a new job"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    created_at = job_data['created_at']
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                    accounts = job_data.get('accounts', [])
                    if not isinstance(accounts, str):
                        accounts = json.dumps(accounts)

                    await cursor.execute("""
                        INSERT INTO creation_jobs 
                        (job_id, total, completed, failed, status, accounts, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        job_data['job_id'],
                        job_data['total'],
                        job_data.get('completed', 0),
                        job_data.get('failed', 0),
                        job_data.get('status', 'processing'),
                        accounts,
                        created_at
                    ))
                    return True
        except Exception as e:
            logger.error(f"❌ Error inserting job: {e}")
            return False

    async def find_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find job by ID"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute("SELECT * FROM creation_jobs WHERE job_id = %s", (job_id,))
                    result = await cursor.fetchone()
                    if result:
                        if result.get('accounts'):
                            try:
                                result['accounts'] = json.loads(result['accounts'])
                            except Exception:
                                result['accounts'] = []
                        if result.get('created_at'):
                            result['created_at'] = result['created_at'].isoformat()
                    return result
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
                    if '$inc' in update_data:
                        inc_data = update_data['$inc']
                        set_parts = [f"{k} = {k} + {v}" for k, v in inc_data.items()]
                        await cursor.execute(f"UPDATE creation_jobs SET {', '.join(set_parts)} WHERE job_id = %s", (job_id,))
                    if '$set' in update_data:
                        set_data = update_data['$set']
                        set_parts = [f"{k} = %s" for k in set_data.keys()]
                        values = list(set_data.values()) + [job_id]
                        await cursor.execute(f"UPDATE creation_jobs SET {', '.join(set_parts)} WHERE job_id = %s", values)
                    if '$push' in update_data:
                        push_data = update_data['$push']
                        if 'accounts' in push_data:
                            await cursor.execute("SELECT accounts FROM creation_jobs WHERE job_id = %s", (job_id,))
                            result = await cursor.fetchone()
                            if result:
                                current_accounts = json.loads(result[0]) if result[0] else []
                                current_accounts.append(push_data['accounts'])
                                await cursor.execute(
                                    "UPDATE creation_jobs SET accounts = %s WHERE job_id = %s",
                                    (json.dumps(current_accounts), job_id)
                                )
                    return True
        except Exception as e:
            logger.error(f"❌ Error updating job: {e}")
            return False


# Global database instance
db = MySQLDatabase()
