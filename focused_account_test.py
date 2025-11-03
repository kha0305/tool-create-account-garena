#!/usr/bin/env python3
"""
Focused Account Creation Test for Garena Account Creator
Tests specifically the account creation functionality as requested
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://account-factory-2.preview.emergentagent.com/api"
TIMEOUT = 60.0

class FocusedAccountTester:
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def setup(self):
        """Setup HTTP client"""
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Response: {json.dumps(data, indent=2)}")
    
    async def test_single_account_creation(self):
        """Test creating a single account (quantity=1) as requested"""
        print("\n🎯 FOCUSED TEST: Single Account Creation (quantity=1)")
        
        try:
            # Step 1: Create single account
            payload = {
                "quantity": 1,
                "email_provider": "mail.tm"
            }
            
            print(f"📤 Creating 1 account with payload: {payload}")
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code != 200:
                self.log_test("Single Account Creation - Request", False, 
                            f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
                return None
            
            data = response.json()
            job_id = data.get("job_id")
            
            if not job_id:
                self.log_test("Single Account Creation - Request", False, 
                            "No job_id in response", data)
                return None
            
            self.log_test("Single Account Creation - Request", True, 
                        f"Job started: {job_id}")
            
            # Step 2: Poll job status until completion
            print(f"⏳ Polling job status for {job_id}...")
            max_wait_time = 60  # 60 seconds max
            poll_interval = 5   # Check every 5 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                await asyncio.sleep(poll_interval)
                
                job_response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
                
                if job_response.status_code != 200:
                    self.log_test("Job Status Polling", False, 
                                f"HTTP {job_response.status_code}", {"status": job_response.status_code})
                    return None
                
                job_data = job_response.json()
                status = job_data.get("status")
                completed = job_data.get("completed", 0)
                total = job_data.get("total", 0)
                failed = job_data.get("failed", 0)
                accounts = job_data.get("accounts", [])
                
                print(f"📊 Job Status: {status}, Progress: {completed}/{total}, Failed: {failed}")
                
                if status == "completed":
                    if completed == 1 and len(accounts) == 1:
                        account = accounts[0]
                        self.log_test("Job Status Polling", True, 
                                    f"Job completed successfully: 1 account created")
                        return account
                    else:
                        self.log_test("Job Status Polling", False, 
                                    f"Job completed but wrong account count: {len(accounts)}", job_data)
                        return None
                elif failed > 0:
                    self.log_test("Job Status Polling", False, 
                                f"Job failed: {failed} failures", job_data)
                    return None
            
            # Timeout
            self.log_test("Job Status Polling", False, 
                        f"Job timeout after {max_wait_time}s", job_data)
            return None
            
        except Exception as e:
            self.log_test("Single Account Creation", False, f"Exception: {str(e)}")
            return None
    
    async def test_account_in_database(self, account: Dict):
        """Test that the account is properly saved in database"""
        if not account:
            self.log_test("Account Database Storage", False, "No account to test")
            return
        
        try:
            account_id = account.get("id")
            email = account.get("email")
            
            # Get all accounts and verify our account is there
            response = await self.client.get(f"{BACKEND_URL}/accounts")
            
            if response.status_code != 200:
                self.log_test("Account Database Storage", False, 
                            f"HTTP {response.status_code}", {"status": response.status_code})
                return
            
            all_accounts = response.json()
            
            # Find our account
            found_account = None
            for acc in all_accounts:
                if acc.get("id") == account_id:
                    found_account = acc
                    break
            
            if found_account:
                # Verify account data
                required_fields = ["id", "username", "email", "password", "email_provider", "email_session_data"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in found_account or not found_account[field]:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_test("Account Database Storage", True, 
                                f"Account properly stored with all required fields: {email}")
                else:
                    self.log_test("Account Database Storage", False, 
                                f"Account missing fields: {missing_fields}", found_account)
            else:
                self.log_test("Account Database Storage", False, 
                            f"Account {account_id} not found in database")
                
        except Exception as e:
            self.log_test("Account Database Storage", False, f"Exception: {str(e)}")
    
    async def test_mail_tm_integration(self, account: Dict):
        """Test that mail.tm integration is working properly"""
        if not account:
            self.log_test("Mail.tm Integration", False, "No account to test")
            return
        
        try:
            email = account.get("email")
            email_provider = account.get("email_provider")
            session_data = account.get("email_session_data")
            
            # Check email domain
            mail_tm_domains = ["2200freefonts.com", "mail.tm", "inboxbear.com", "guerrillamail.info"]
            is_mail_tm_domain = any(domain in email for domain in mail_tm_domains)
            
            # Check session data has JWT token
            has_token = session_data and session_data.get("token")
            
            if email_provider == "mail.tm" and is_mail_tm_domain and has_token:
                self.log_test("Mail.tm Integration", True, 
                            f"Mail.tm integration working: {email} with JWT token")
            else:
                issues = []
                if email_provider != "mail.tm":
                    issues.append(f"Wrong provider: {email_provider}")
                if not is_mail_tm_domain:
                    issues.append(f"Wrong domain: {email}")
                if not has_token:
                    issues.append("Missing JWT token")
                
                self.log_test("Mail.tm Integration", False, 
                            f"Issues: {', '.join(issues)}", account)
                
        except Exception as e:
            self.log_test("Mail.tm Integration", False, f"Exception: {str(e)}")
    
    async def test_inbox_access(self, account: Dict):
        """Test that inbox checking works with JWT authentication"""
        if not account:
            self.log_test("Inbox Access", False, "No account to test")
            return
        
        try:
            account_id = account.get("id")
            
            response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox")
            
            if response.status_code == 200:
                data = response.json()
                
                if ("messages" in data and 
                    data.get("provider") == "mail.tm" and 
                    "count" in data and 
                    data.get("account_id") == account_id):
                    
                    message_count = data.get("count", 0)
                    self.log_test("Inbox Access", True, 
                                f"Inbox accessible: {message_count} messages found")
                else:
                    self.log_test("Inbox Access", False, 
                                "Invalid inbox response format", data)
            else:
                self.log_test("Inbox Access", False, 
                            f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
                
        except Exception as e:
            self.log_test("Inbox Access", False, f"Exception: {str(e)}")
    
    async def run_focused_tests(self):
        """Run focused account creation tests"""
        print("🎯 FOCUSED ACCOUNT CREATION TESTS")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Test Requirements:
            # 1. Test single account creation (quantity=1) 
            account = await self.test_single_account_creation()
            
            if account:
                # 2. Verify account is saved in database
                await self.test_account_in_database(account)
                
                # 3. Check that mail.tm integration is working
                await self.test_mail_tm_integration(account)
                
                # 4. Test that job status polling works (already tested in step 1)
                
                # 5. Verify accounts can be retrieved via GET /api/accounts (already tested in step 2)
                
                # Additional: Test inbox access
                await self.test_inbox_access(account)
                
                print(f"\n📋 CREATED ACCOUNT DETAILS:")
                print(f"   ID: {account.get('id')}")
                print(f"   Username: {account.get('username')}")
                print(f"   Email: {account.get('email')}")
                print(f"   Provider: {account.get('email_provider')}")
                print(f"   Has JWT Token: {bool(account.get('email_session_data', {}).get('token'))}")
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 All focused tests passed!")
        
        return passed == total


async def main():
    """Main test runner"""
    tester = FocusedAccountTester()
    success = await tester.run_focused_tests()
    
    if success:
        print("\n✅ Account creation functionality is working correctly!")
        return 0
    else:
        print("\n❌ Account creation functionality has issues!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)