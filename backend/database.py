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
            # Convert datetime to string if needed
            if isinstance(account_data.get('created_at'), datetime):
                account_data['created_at'] = account_data['created_at'].isoformat()
            
            result = await self.db.garena_accounts.insert_one(account_data)
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"❌ Error inserting account: {e}")
            return False
    
    async def find_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Find account by ID"""
        try:
            account = await self.db.garena_accounts.find_one({"id": account_id})
            if account:
                account.pop('_id', None)  # Remove MongoDB's _id
            return account
        except Exception as e:
            logger.error(f"❌ Error finding account: {e}")
            return None

    async def find_all_accounts(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all accounts"""
        try:
            cursor = self.db.garena_accounts.find().sort("created_at", DESCENDING).limit(limit)
            accounts = await cursor.to_list(length=limit)
            
            # Remove MongoDB's _id from each account
            for account in accounts:
                account.pop('_id', None)
            
            return accounts
        except Exception as e:
            logger.error(f"❌ Error fetching accounts: {e}")
            return []

    async def update_account(self, account_id: str, update_data: Dict[str, Any]) -> bool:
        """Update account"""
        try:
            if not update_data:
                return False
            
            result = await self.db.garena_accounts.update_one(
                {"id": account_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Error updating account: {e}")
            return False

    async def delete_account(self, account_id: str) -> int:
        """Delete account by ID"""
        try:
            result = await self.db.garena_accounts.delete_one({"id": account_id})
            return result.deleted_count
        except Exception as e:
            logger.error(f"❌ Error deleting account: {e}")
            return 0

    async def delete_all_accounts(self) -> int:
        """Delete all accounts"""
        try:
            result = await self.db.garena_accounts.delete_many({})
            return result.deleted_count
        except Exception as e:
            logger.error(f"❌ Error deleting all accounts: {e}")
            return 0

    async def delete_multiple_accounts(self, account_ids: list) -> int:
        """Delete multiple accounts by IDs"""
        try:
            if not account_ids:
                return 0
            result = await self.db.garena_accounts.delete_many({"id": {"$in": account_ids}})
            return result.deleted_count
        except Exception as e:
            logger.error(f"❌ Error deleting multiple accounts: {e}")
            return 0


    # ========== CREATION JOBS ==========
    async def insert_job(self, job_data: Dict[str, Any]) -> bool:
        """Insert a new job"""
        try:
            # Convert datetime to string if needed
            if isinstance(job_data.get('created_at'), datetime):
                job_data['created_at'] = job_data['created_at'].isoformat()
            
            result = await self.db.creation_jobs.insert_one(job_data)
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"❌ Error inserting job: {e}")
            return False

    async def find_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find job by ID"""
        try:
            job = await self.db.creation_jobs.find_one({"job_id": job_id})
            if job:
                job.pop('_id', None)  # Remove MongoDB's _id
            return job
        except Exception as e:
            logger.error(f"❌ Error finding job: {e}")
            return None

    async def update_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update job fields"""
        try:
            if not update_data:
                return False
            
            result = await self.db.creation_jobs.update_one(
                {"job_id": job_id},
                update_data
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            logger.error(f"❌ Error updating job: {e}")
            return False


# Global database instance
db = MongoDatabase()
