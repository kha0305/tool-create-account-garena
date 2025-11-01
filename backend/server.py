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
from mail_tm_service import MailTmService

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
    email_provider: str = "mail.tm"  # Using mail.tm for temporary emails
    email_session_data: Optional[Dict[str, Any]] = None  # Session data for email checking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None

class CreateAccountRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)
    email_provider: str = Field(default="mail.tm")  # Using mail.tm

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
    """
    Generate secure random password for Garena
    Requirements: 8-16 characters with at least:
    - One lowercase letter (a-z)
    - One uppercase letter (A-Z)
    - One number (0-9)
    - One symbol
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = '!@#$%^&*'
    
    # Ensure at least one character from each required set
    password_chars = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols)
    ]
    
    # Fill the rest with random characters (total length: 12)
    all_chars = lowercase + uppercase + digits + symbols
    password_chars.extend(random.choices(all_chars, k=8))
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

def generate_phone() -> str:
    """Generate Vietnamese phone number (+84)"""
    # Vietnamese mobile prefixes: 03, 05, 07, 08, 09
    prefix = random.choice(['03', '05', '07', '08', '09'])
    # Generate 8 more digits
    middle = ''.join(random.choices(string.digits, k=4))
    end = ''.join(random.choices(string.digits, k=4))
    return f"+84-{prefix}{middle[:1]}-{middle[1:]}-{end}"

async def get_temp_email(provider: str = "mail.tm") -> Optional[Dict[str, Any]]:
    """
    Get temporary email using mail.tm API
    Returns:
        Dict with email and session_data or None
    """
    try:
        mail_tm = MailTmService()
        result = await mail_tm.create_account()
        
        if result and result.get('email'):
            return {
                'email': result['email'],
                'session_data': result['session_data']
            }
        else:
            raise Exception("Failed to create mail.tm account")
            
    except Exception as e:
        logging.error(f"Error creating mail.tm account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create temporary email: {str(e)}")

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

@api_router.get("/email-providers")
async def get_email_providers():
    """Get list of available email providers"""
    return {
        "providers": [
            {
                "id": "temp-mail",
                "name": "Temp Mail API",
                "description": "Official temp-mail.io API service",
                "reliable": True
            },
            {
                "id": "10minutemail",
                "name": "10 Minute Mail",
                "description": "10minutemail.one service",
                "reliable": True,
                "features": ["inbox_checking"]
            }
        ]
    }

@api_router.get("/accounts/{account_id}/inbox")
async def check_account_inbox(account_id: str):
    """Check inbox for account's temporary email"""
    account = await db.garena_accounts.find_one({"id": account_id})
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    email_provider = account.get('email_provider', 'temp-mail')
    email_session = account.get('email_session_data')
    
    if not email_session:
        return {
            "account_id": account_id,
            "email": account.get('email'),
            "provider": email_provider,
            "messages": [],
            "error": "No session data available for this email"
        }
    
    # Check inbox based on provider
    messages = []
    if email_provider == "10minutemail":
        try:
            messages = await ten_minute_mail_service.check_inbox(email_session)
        except Exception as e:
            logging.error(f"Error checking 10minutemail inbox: {e}")
            return {
                "account_id": account_id,
                "email": account.get('email'),
                "provider": email_provider,
                "messages": [],
                "error": str(e)
            }
    else:
        # Temp-mail.io doesn't have easy inbox checking in free tier
        return {
            "account_id": account_id,
            "email": account.get('email'),
            "provider": email_provider,
            "messages": [],
            "info": "Inbox checking not available for temp-mail provider"
        }
    
    return {
        "account_id": account_id,
        "email": account.get('email'),
        "provider": email_provider,
        "messages": messages,
        "count": len(messages)
    }

@api_router.post("/test-email-provider")
async def test_email_provider(provider: str):
    """Test email provider functionality"""
    if provider not in ["temp-mail", "10minutemail"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'temp-mail' or '10minutemail'")
    
    try:
        email_data = await get_temp_email(provider)
        
        return {
            "success": True,
            "provider": provider,
            "email": email_data['email'],
            "has_session": email_data.get('session_data') is not None,
            "message": f"Successfully generated email from {provider}"
        }
    except Exception as e:
        logging.error(f"Error testing provider {provider}: {e}")
        return {
            "success": False,
            "provider": provider,
            "error": str(e)
        }

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