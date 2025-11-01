#!/usr/bin/env python3
"""
Focused Backend Test for User Requirements
Tests 3 account creation with rate limiting protection and retry logic
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
TIMEOUT = 60.0

class FocusedTester:
    def __init__(self):
        self.client = None
        self.start_time = None
        
    async def setup(self):
        """Setup HTTP client"""
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.start_time = time.time()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    def log(self, message: str):
        """Log with timestamp"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.1f}s] {message}")
    
    async def test_3_account_creation_with_timing(self):
        """Test creating 3 accounts and monitor timing/delays"""
        self.log("🚀 Starting 3 Account Creation Test")
        
        try:
            # Create 3 accounts
            payload = {
                "quantity": 3,
                "email_provider": "mail.tm"
            }
            
            creation_start = time.time()
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                self.log(f"✅ Job created: {job_id}")
                self.log(f"📧 Email provider: {data.get('email_provider')}")
                
                # Monitor job progress
                await self.monitor_job_progress(job_id, creation_start)
                
            else:
                self.log(f"❌ Account creation failed: HTTP {response.status_code}")
                self.log(f"Response: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error during account creation: {str(e)}")
    
    async def monitor_job_progress(self, job_id: str, start_time: float):
        """Monitor job progress and timing"""
        self.log("📊 Monitoring job progress...")
        
        completed_accounts = 0
        check_count = 0
        
        while True:
            check_count += 1
            await asyncio.sleep(2)  # Check every 2 seconds
            
            try:
                response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    total = data.get("total", 0)
                    completed = data.get("completed", 0)
                    failed = data.get("failed", 0)
                    status = data.get("status", "unknown")
                    progress = data.get("progress_percentage", 0)
                    
                    elapsed = time.time() - start_time
                    
                    # Log progress if there's a change
                    if completed > completed_accounts:
                        self.log(f"📈 Progress: {completed}/{total} completed, {failed} failed ({progress:.1f}%) - {elapsed:.1f}s elapsed")
                        completed_accounts = completed
                    
                    # Check if job is complete
                    if status == "completed" or (completed + failed) >= total:
                        final_elapsed = time.time() - start_time
                        self.log(f"🏁 Job completed in {final_elapsed:.1f} seconds")
                        
                        # Analyze the accounts
                        await self.analyze_created_accounts(data.get("accounts", []), final_elapsed)
                        break
                    
                    # Timeout after 2 minutes
                    if elapsed > 120:
                        self.log("⏰ Timeout reached (2 minutes)")
                        break
                        
                else:
                    self.log(f"❌ Failed to get job status: HTTP {response.status_code}")
                    break
                    
            except Exception as e:
                self.log(f"❌ Error checking job status: {str(e)}")
                break
    
    async def analyze_created_accounts(self, accounts: list, total_time: float):
        """Analyze the created accounts"""
        self.log(f"\n📋 ACCOUNT CREATION ANALYSIS")
        self.log(f"Total time: {total_time:.1f} seconds")
        self.log(f"Accounts created: {len(accounts)}")
        
        if len(accounts) > 0:
            avg_time_per_account = total_time / len(accounts)
            self.log(f"Average time per account: {avg_time_per_account:.1f} seconds")
        
        # Analyze each account
        for i, account in enumerate(accounts, 1):
            email = account.get("email", "N/A")
            provider = account.get("email_provider", "N/A")
            status = account.get("status", "N/A")
            password = account.get("password", "N/A")
            
            # Check password requirements
            password_valid = self.validate_password(password)
            
            # Check email domain
            is_mail_tm = any(domain in email for domain in ["2200freefonts.com", "mail.tm", "inboxbear.com"])
            
            self.log(f"  Account {i}:")
            self.log(f"    Email: {email} ({'✅' if is_mail_tm else '❌'} mail.tm domain)")
            self.log(f"    Provider: {provider}")
            self.log(f"    Status: {status}")
            self.log(f"    Password: {password} ({'✅' if password_valid else '❌'} Garena compliant)")
            
            # Check session data
            session_data = account.get("email_session_data", {})
            has_token = bool(session_data.get("token"))
            self.log(f"    JWT Token: {'✅' if has_token else '❌'} Present")
    
    def validate_password(self, password: str) -> bool:
        """Validate password against Garena requirements"""
        if not password or len(password) < 8 or len(password) > 16:
            return False
        
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*" for c in password)
        
        return has_lower and has_upper and has_digit and has_symbol
    
    async def test_export_endpoints(self):
        """Test all export endpoints"""
        self.log("\n📤 Testing Export Endpoints")
        
        # Test TXT export
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/txt")
            if response.status_code == 200:
                content_disposition = response.headers.get("content-disposition", "")
                if "ACCOUNTS_" in content_disposition and ".txt" in content_disposition:
                    self.log("✅ TXT Export: Working")
                else:
                    self.log("❌ TXT Export: Invalid headers")
            else:
                self.log(f"❌ TXT Export: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ TXT Export: Error {str(e)}")
        
        # Test CSV export
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/csv")
            if response.status_code == 200:
                content_disposition = response.headers.get("content-disposition", "")
                if "ACCOUNTS_" in content_disposition and ".csv" in content_disposition:
                    self.log("✅ CSV Export: Working")
                else:
                    self.log("❌ CSV Export: Invalid headers")
            else:
                self.log(f"❌ CSV Export: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ CSV Export: Error {str(e)}")
        
        # Test XLSX export
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/xlsx")
            if response.status_code == 200:
                content_disposition = response.headers.get("content-disposition", "")
                content_type = response.headers.get("content-type", "")
                expected_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                if ("ACCOUNTS_" in content_disposition and 
                    ".xlsx" in content_disposition and 
                    content_type == expected_mime):
                    self.log("✅ XLSX Export: Working")
                else:
                    self.log("❌ XLSX Export: Invalid headers")
            else:
                self.log(f"❌ XLSX Export: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ XLSX Export: Error {str(e)}")
    
    async def test_inbox_checking(self):
        """Test inbox checking functionality"""
        self.log("\n📬 Testing Inbox Checking")
        
        try:
            # Get all accounts first
            response = await self.client.get(f"{BACKEND_URL}/accounts")
            
            if response.status_code == 200:
                accounts = response.json()
                
                if accounts:
                    # Test inbox for first account
                    account = accounts[0]
                    account_id = account.get("id")
                    email = account.get("email")
                    
                    inbox_response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox")
                    
                    if inbox_response.status_code == 200:
                        inbox_data = inbox_response.json()
                        messages = inbox_data.get("messages", [])
                        provider = inbox_data.get("provider", "unknown")
                        
                        self.log(f"✅ Inbox Check: {email} ({provider}) - {len(messages)} messages")
                    else:
                        self.log(f"❌ Inbox Check: HTTP {inbox_response.status_code}")
                else:
                    self.log("❌ Inbox Check: No accounts found")
            else:
                self.log(f"❌ Inbox Check: Failed to get accounts - HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Inbox Check: Error {str(e)}")
    
    async def run_focused_tests(self):
        """Run focused tests as requested by user"""
        print("🎯 FOCUSED BACKEND TESTING - LOCAL STABILITY")
        print("=" * 60)
        print("Testing Requirements:")
        print("1. Create 3 accounts with rate limiting protection")
        print("2. Verify delays between account creation")
        print("3. Check logging displays correctly")
        print("4. Test export TXT/CSV/XLSX")
        print("5. Test inbox checking")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Main test: Create 3 accounts with timing analysis
            await self.test_3_account_creation_with_timing()
            
            # Test export functionality
            await self.test_export_endpoints()
            
            # Test inbox checking
            await self.test_inbox_checking()
            
        finally:
            await self.cleanup()
        
        total_elapsed = time.time() - self.start_time
        self.log(f"\n🏁 All tests completed in {total_elapsed:.1f} seconds")

async def main():
    """Main test runner"""
    tester = FocusedTester()
    await tester.run_focused_tests()

if __name__ == "__main__":
    asyncio.run(main())