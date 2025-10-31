from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import random
import string
import asyncio
from ten_minute_mail import get_10minute_email_with_session, ten_minute_mail_service

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
    password: str
    phone: Optional[str] = None
    status: str = "creating"  # creating, created, verified, failed
    email_provider: str = "temp-mail"  # temp-mail or 10minutemail
    email_session_data: Optional[Dict[str, Any]] = None  # Session data for email checking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None

class CreateAccountRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)
    email_provider: str = Field(default="temp-mail")  # temp-mail or 10minutemail

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
    """Generate Vietnamese phone number (+84)"""
    # Vietnamese mobile prefixes: 03, 05, 07, 08, 09
    prefix = random.choice(['03', '05', '07', '08', '09'])
    # Generate 8 more digits
    middle = ''.join(random.choices(string.digits, k=4))
    end = ''.join(random.choices(string.digits, k=4))
    return f"+84-{prefix}{middle[:1]}-{middle[1:]}-{end}"

async def get_temp_email(provider: str = "temp-mail") -> Optional[Dict[str, Any]]:
    """
    Get temporary email using specified provider
    Args:
        provider: 'temp-mail' or '10minutemail'
    Returns:
        Dict with email and session_data or None
    """
    if provider == "10minutemail":
        # Use 10minutemail.one
        try:
            result = await get_10minute_email_with_session()
            if result and result.get('email'):
                return {
                    'email': result['email'],
                    'session_data': result
                }
            # Fallback to random email
            return {
                'email': f"temp{random.randint(10000, 99999)}@tempmail.com",
                'session_data': None
            }
        except Exception as e:
            logging.error(f"Error getting 10minutemail email: {e}")
            return {
                'email': f"temp{random.randint(10000, 99999)}@tempmail.com",
                'session_data': None
            }
    else:
        # Use temp-mail.io API (original)
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
                        email = f"{local_part}{domain}"
                        return {
                            'email': email,
                            'session_data': {'provider': 'temp-mail', 'email': email}
                        }
                
                # Fallback to random email if API fails
                return {
                    'email': f"temp{random.randint(10000, 99999)}@tempmail.com",
                    'session_data': None
                }
        except Exception as e:
            logging.error(f"Error getting temp email: {e}")
            # Fallback to random email
            return {
                'email': f"temp{random.randint(10000, 99999)}@tempmail.com",
                'session_data': None
            }

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

async def process_account_creation(job_id: str, quantity: int, email_provider: str = "temp-mail"):
    """Background task to create accounts"""
    job_data = await db.creation_jobs.find_one({"job_id": job_id})
    if not job_data:
        return
    
    for i in range(quantity):
        try:
            # Generate account details
            username = generate_username()
            email_data = await get_temp_email(email_provider)
            email = email_data['email']
            email_session = email_data.get('session_data')
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
                    status="created",
                    email_provider=email_provider,
                    email_session_data=email_session
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
    # Validate email provider
    if request.email_provider not in ["temp-mail", "10minutemail"]:
        raise HTTPException(status_code=400, detail="Invalid email provider. Use 'temp-mail' or '10minutemail'")
    
    # Create job
    job = CreationJob(total=request.quantity)
    job_dict = job.model_dump()
    job_dict['created_at'] = job_dict['created_at'].isoformat()
    
    await db.creation_jobs.insert_one(job_dict)
    
    # Start background task with email provider
    background_tasks.add_task(process_account_creation, job.job_id, request.quantity, request.email_provider)
    
    return {
        "job_id": job.job_id,
        "message": f"Started creating {request.quantity} accounts with {request.email_provider}",
        "status": "processing",
        "email_provider": request.email_provider
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

@api_router.post("/accounts/{account_id}/verify")
async def verify_account_login(account_id: str):
    """Mark account as ready for verification"""
    account = await db.garena_accounts.find_one({"id": account_id})
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update status to pending verification
    await db.garena_accounts.update_one(
        {"id": account_id},
        {"$set": {"status": "pending_verification"}}
    )
    
    return {
        "message": "Account ready for verification",
        "login_url": f"https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https://account.garena.com/?locale_name=SG&locale=vi-VN",
        "account": {
            "username": account["username"],
            "email": account["email"],
            "phone": account["phone"],
            "password": account["password"]
        }
    }

@api_router.put("/accounts/{account_id}/status")
async def update_account_status(account_id: str, status: str):
    """Update account verification status"""
    valid_statuses = ["created", "verified", "failed", "pending_verification"]
    
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    result = await db.garena_accounts.update_one(
        {"id": account_id},
        {"$set": {"status": status}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Status updated successfully", "status": status}

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