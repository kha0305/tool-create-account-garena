from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx
import random
import string
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Temp Mail API Configuration
TEMP_MAIL_API_KEY = os.getenv('TEMP_MAIL_API_KEY', 'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3')
TEMP_MAIL_BASE_URL = 'https://api.apilayer.com/temp_mail'

# Define Models
class GarenaAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    phone: str
    password: str
    status: str = "created"  # created, verified, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateAccountRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)

class CreationJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total: int
    completed: int = 0
    failed: int = 0
    status: str = "processing"  # processing, completed, failed
    accounts: List[str] = []  # List of account IDs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobStatus(BaseModel):
    job_id: str
    total: int
    completed: int
    failed: int
    status: str
    progress_percentage: float
    accounts: List[GarenaAccount] = []

# Helper Functions
def generate_username() -> str:
    """Generate random username"""
    prefix = random.choice(['gamer', 'player', 'user', 'pro', 'master'])
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"

def generate_password() -> str:
    """Generate secure random password"""
    chars = string.ascii_letters + string.digits + '!@#$%'
    return ''.join(random.choices(chars, k=12))

def generate_phone() -> str:
    """Generate mock phone number (TextNow simulation)"""
    area_code = random.choice(['555', '888', '777', '666'])
    exchange = ''.join(random.choices(string.digits, k=3))
    number = ''.join(random.choices(string.digits, k=4))
    return f"+1-{area_code}-{exchange}-{number}"

async def get_temp_email() -> Optional[str]:
    """Get temporary email using Temp Mail API"""
    try:
        async with httpx.AsyncClient() as client:
            # Get available domains
            response = await client.get(
                f"{TEMP_MAIL_BASE_URL}/domains",
                headers={"apikey": TEMP_MAIL_API_KEY},
                timeout=10.0
            )
            
            if response.status_code == 200:
                domains = response.json()
                if domains and len(domains) > 0:
                    domain = random.choice(domains)
                    local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                    return f"{local_part}{domain}"
            
            # Fallback to random email if API fails
            return f"temp{random.randint(10000, 99999)}@tempmail.com"
    except Exception as e:
        logging.error(f"Error getting temp email: {e}")
        # Fallback to random email
        return f"temp{random.randint(10000, 99999)}@tempmail.com"

async def create_garena_account(username: str, email: str, phone: str, password: str) -> dict:
    """Simulate Garena account creation"""
    # Simulate API delay
    await asyncio.sleep(random.uniform(1, 2))
    
    # Simulate 95% success rate
    success = random.random() > 0.05
    
    return {
        "success": success,
        "username": username,
        "email": email,
        "phone": phone,
        "password": password
    }

async def process_account_creation(job_id: str, quantity: int):
    """Background task to create accounts"""
    job_data = await db.creation_jobs.find_one({"job_id": job_id})
    if not job_data:
        return
    
    for i in range(quantity):
        try:
            # Generate account details
            username = generate_username()
            email = await get_temp_email()
            phone = generate_phone()
            password = generate_password()
            
            # Create Garena account
            result = await create_garena_account(username, email, phone, password)
            
            if result["success"]:
                # Save account to database
                account = GarenaAccount(
                    username=username,
                    email=email,
                    phone=phone,
                    password=password,
                    status="created"
                )
                
                account_dict = account.model_dump()
                account_dict['created_at'] = account_dict['created_at'].isoformat()
                await db.garena_accounts.insert_one(account_dict)
                
                # Update job
                await db.creation_jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$inc": {"completed": 1},
                        "$push": {"accounts": account.id}
                    }
                )
            else:
                await db.creation_jobs.update_one(
                    {"job_id": job_id},
                    {"$inc": {"failed": 1}}
                )
        except Exception as e:
            logging.error(f"Error creating account: {e}")
            await db.creation_jobs.update_one(
                {"job_id": job_id},
                {"$inc": {"failed": 1}}
            )
    
    # Mark job as completed
    await db.creation_jobs.update_one(
        {"job_id": job_id},
        {"$set": {"status": "completed"}}
    )

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Garena Account Creator API"}

@api_router.post("/accounts/create")
async def create_accounts(request: CreateAccountRequest, background_tasks: BackgroundTasks):
    """Start batch account creation"""
    # Create job
    job = CreationJob(total=request.quantity)
    job_dict = job.model_dump()
    job_dict['created_at'] = job_dict['created_at'].isoformat()
    
    await db.creation_jobs.insert_one(job_dict)
    
    # Start background task
    background_tasks.add_task(process_account_creation, job.job_id, request.quantity)
    
    return {
        "job_id": job.job_id,
        "message": f"Started creating {request.quantity} accounts",
        "status": "processing"
    }

@api_router.get("/accounts/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and created accounts"""
    job = await db.creation_jobs.find_one({"job_id": job_id}, {"_id": 0})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get accounts
    accounts = []
    if job.get('accounts'):
        for account_id in job['accounts']:
            account = await db.garena_accounts.find_one({"id": account_id}, {"_id": 0})
            if account:
                if isinstance(account.get('created_at'), str):
                    account['created_at'] = datetime.fromisoformat(account['created_at'])
                accounts.append(GarenaAccount(**account))
    
    progress = (job['completed'] / job['total'] * 100) if job['total'] > 0 else 0
    
    return JobStatus(
        job_id=job['job_id'],
        total=job['total'],
        completed=job['completed'],
        failed=job['failed'],
        status=job['status'],
        progress_percentage=progress,
        accounts=accounts
    )

@api_router.get("/accounts", response_model=List[GarenaAccount])
async def get_all_accounts():
    """Get all created accounts"""
    accounts = await db.garena_accounts.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for account in accounts:
        if isinstance(account.get('created_at'), str):
            account['created_at'] = datetime.fromisoformat(account['created_at'])
    
    return accounts

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    """Delete an account"""
    result = await db.garena_accounts.delete_one({"id": account_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Account deleted successfully"}

@api_router.delete("/accounts")
async def delete_all_accounts():
    """Delete all accounts"""
    result = await db.garena_accounts.delete_many({})
    return {"message": f"Deleted {result.deleted_count} accounts"}

@api_router.get("/temp-email/test")
async def test_temp_email():
    """Test temp email generation"""
    email = await get_temp_email()
    return {"email": email}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()