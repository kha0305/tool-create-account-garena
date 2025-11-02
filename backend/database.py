import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDatabase:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Create connection to MongoDB"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'garena_creator_db')
            
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"✅ MongoDB connected successfully to database: {db_name}")
            
            # Create indexes
            await self.create_indexes()
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def create_indexes(self):
        """Create indexes for better performance"""
        try:
            # Index on created_at for garena_accounts
            await self.db.garena_accounts.create_index([("created_at", DESCENDING)])
            await self.db.garena_accounts.create_index("status")
            
            # Index on created_at for creation_jobs
            await self.db.creation_jobs.create_index([("created_at", DESCENDING)])
            
            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create indexes: {e}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")

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
