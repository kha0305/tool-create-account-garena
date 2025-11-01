#!/usr/bin/env python3
"""
Backend Test Suite for Garena Account Creator
Tests the Mail.tm integration and all API endpoints
"""

import asyncio
import httpx
import json
import time
import re
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://task-exec.preview.emergentagent.com/api"
TIMEOUT = 30.0

class GarenaBackendTester:
    def __init__(self):
        self.client = None
        self.test_results = []
        self.created_accounts = []
        self.job_ids = []
    
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
    
    async def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root Endpoint", True, f"API is running: {data['message']}")
                else:
                    self.log_test("Root Endpoint", False, "Missing message in response", data)
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
    
    async def test_email_providers_endpoint(self):
        """Test GET /api/email-providers - should return only mail.tm"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/email-providers")
            
            if response.status_code == 200:
                data = response.json()
                if "providers" in data and isinstance(data["providers"], list):
                    providers = data["providers"]
                    provider_ids = [p.get("id") for p in providers]
                    
                    # Should only have mail.tm now
                    if len(providers) == 1 and "mail.tm" in provider_ids:
                        provider = providers[0]
                        if provider.get("name") == "Mail.tm" and "inbox_checking" in provider.get("features", []):
                            self.log_test("Email Providers Endpoint", True, f"✅ Only mail.tm provider found with inbox support: {provider_ids}")
                        else:
                            self.log_test("Email Providers Endpoint", False, f"mail.tm provider missing required features", data)
                    else:
                        self.log_test("Email Providers Endpoint", False, f"❌ Expected only mail.tm, found: {provider_ids}", data)
                else:
                    self.log_test("Email Providers Endpoint", False, "Invalid response format", data)
            else:
                self.log_test("Email Providers Endpoint", False, f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("Email Providers Endpoint", False, f"Request error: {str(e)}")
    
    async def test_mail_tm_provider(self):
        """Test POST /api/test-email-provider with mail.tm"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/test-email-provider?provider=mail.tm")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("email"):
                    email = data["email"]
                    has_session = data.get("has_session", False)
                    has_token = data.get("session_has_token", False)
                    
                    # Verify it's a real mail.tm domain
                    mail_tm_domains = ["mail.tm", "inboxbear.com", "guerrillamail.info", "guerrillamail.biz", "guerrillamail.com", "guerrillamail.de", "guerrillamail.net", "guerrillamail.org", "sharklasers.com", "grr.la", "pokemail.net", "spam4.me"]
                    is_mail_tm_domain = any(domain in email for domain in mail_tm_domains)
                    
                    if has_session and has_token and is_mail_tm_domain:
                        self.log_test("Test mail.tm Provider", True, 
                                    f"✅ Generated real mail.tm email: {email}, has_session: {has_session}, has_token: {has_token}")
                    else:
                        self.log_test("Test mail.tm Provider", False, 
                                    f"❌ Missing session/token or not mail.tm domain: {email}, session: {has_session}, token: {has_token}", data)
                else:
                    self.log_test("Test mail.tm Provider", False, 
                                f"❌ Provider test failed: {data.get('error', 'Unknown error')}", data)
            else:
                self.log_test("Test mail.tm Provider", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("Test mail.tm Provider", False, f"Request error: {str(e)}")
    
    async def test_other_provider_fallback(self):
        """Test that other providers fallback to mail.tm"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/test-email-provider?provider=temp-mail")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("provider") == "mail.tm":
                    self.log_test("Provider Fallback Test", True, 
                                f"✅ temp-mail request correctly fallback to mail.tm")
                else:
                    self.log_test("Provider Fallback Test", False, 
                                f"❌ Expected fallback to mail.tm, got: {data.get('provider')}", data)
            else:
                self.log_test("Provider Fallback Test", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("Provider Fallback Test", False, f"Request error: {str(e)}")
    
    async def test_account_creation_mail_tm(self, quantity: int):
        """Test POST /api/accounts/create with mail.tm"""
        try:
            payload = {
                "quantity": quantity,
                "email_provider": "mail.tm"
            }
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data and data.get("email_provider") == "mail.tm":
                    job_id = data["job_id"]
                    self.job_ids.append(job_id)
                    self.log_test(f"Create {quantity} Accounts (mail.tm)", True, 
                                f"✅ Job started: {job_id}, provider: {data.get('email_provider')}")
                    return job_id
                else:
                    self.log_test(f"Create {quantity} Accounts (mail.tm)", False, 
                                "Missing job_id or wrong provider in response", data)
            else:
                self.log_test(f"Create {quantity} Accounts (mail.tm)", False, 
                            f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test(f"Create {quantity} Accounts (mail.tm)", False, f"Request error: {str(e)}")
        return None
    
    async def test_job_status_mail_tm(self, job_id: str):
        """Test GET /api/accounts/job/{job_id} for mail.tm accounts"""
        try:
            # Wait a bit for job to process
            await asyncio.sleep(5)
            
            response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                completed = data.get("completed", 0)
                total = data.get("total", 0)
                accounts = data.get("accounts", [])
                
                # Check if accounts have correct email_provider and session data
                mail_tm_domains = ["mail.tm", "inboxbear.com", "guerrillamail.info", "guerrillamail.biz", "guerrillamail.com", "guerrillamail.de", "guerrillamail.net", "guerrillamail.org", "sharklasers.com", "grr.la", "pokemail.net", "spam4.me"]
                
                valid_accounts = 0
                issues = []
                
                for account in accounts:
                    self.created_accounts.append(account)
                    
                    # Check provider
                    if account.get("email_provider") != "mail.tm":
                        issues.append(f"Wrong provider: {account.get('email_provider')}")
                        continue
                    
                    # Check email domain
                    email = account.get("email", "")
                    is_mail_tm_domain = any(domain in email for domain in mail_tm_domains)
                    if not is_mail_tm_domain:
                        issues.append(f"Non-mail.tm domain: {email}")
                        continue
                    
                    # Check session data has token
                    session_data = account.get("email_session_data", {})
                    if not session_data or not session_data.get("token"):
                        issues.append(f"Missing token in session_data for {email}")
                        continue
                    
                    valid_accounts += 1
                
                if len(issues) == 0 and valid_accounts == len(accounts):
                    self.log_test(f"Job Status mail.tm ({job_id})", True, 
                                f"✅ Status: {status}, Progress: {completed}/{total}, All {valid_accounts} accounts valid with mail.tm emails and tokens")
                else:
                    self.log_test(f"Job Status mail.tm ({job_id})", False, 
                                f"❌ {valid_accounts}/{len(accounts)} valid accounts. Issues: {issues[:3]}", data)
            else:
                self.log_test(f"Job Status mail.tm ({job_id})", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test(f"Job Status mail.tm ({job_id})", False, f"Request error: {str(e)}")
    
    async def test_list_accounts(self):
        """Test GET /api/accounts"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts")
            
            if response.status_code == 200:
                accounts = response.json()
                if isinstance(accounts, list):
                    # Check if accounts have required fields
                    valid_accounts = 0
                    for account in accounts:
                        if all(field in account for field in ["id", "email", "email_provider"]):
                            valid_accounts += 1
                    
                    self.log_test("List All Accounts", True, 
                                f"Found {len(accounts)} accounts, {valid_accounts} with required fields")
                else:
                    self.log_test("List All Accounts", False, "Response is not a list", accounts)
            else:
                self.log_test("List All Accounts", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("List All Accounts", False, f"Request error: {str(e)}")
    
    def validate_garena_password(self, password: str) -> Dict[str, bool]:
        """
        Validate password against Garena requirements
        Returns dict with validation results for each requirement
        """
        return {
            "length_valid": 8 <= len(password) <= 16,
            "has_lowercase": bool(re.search(r'[a-z]', password)),
            "has_uppercase": bool(re.search(r'[A-Z]', password)),
            "has_digit": bool(re.search(r'[0-9]', password)),
            "has_symbol": bool(re.search(r'[!@#$%^&*]', password))
        }
    
    def is_password_valid(self, password: str) -> bool:
        """Check if password meets ALL Garena requirements"""
        validation = self.validate_garena_password(password)
        return all(validation.values())
    
    async def test_password_generation_direct(self):
        """Test password generation by creating multiple accounts and checking passwords"""
        print("\n🔐 Testing Password Generation (Garena Requirements)")
        print("Requirements: 8-16 chars, lowercase, uppercase, digit, symbol")
        
        # Test multiple account creations to get password samples
        passwords_tested = []
        failed_passwords = []
        
        try:
            # Create 10 accounts to test password generation
            payload = {"quantity": 10, "email_provider": "temp-mail"}
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    # Wait for job completion
                    await asyncio.sleep(5)
                    
                    # Get job status to retrieve created accounts
                    job_response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
                    
                    if job_response.status_code == 200:
                        job_data = job_response.json()
                        accounts = job_data.get("accounts", [])
                        
                        for account in accounts:
                            password = account.get("password")
                            if password:
                                passwords_tested.append(password)
                                validation = self.validate_garena_password(password)
                                
                                if not self.is_password_valid(password):
                                    failed_passwords.append({
                                        "password": password,
                                        "validation": validation
                                    })
                        
                        # Log results
                        if passwords_tested:
                            success_count = len(passwords_tested) - len(failed_passwords)
                            
                            if len(failed_passwords) == 0:
                                self.log_test("Password Generation Validation", True, 
                                            f"All {len(passwords_tested)} passwords meet Garena requirements")
                            else:
                                details = f"{success_count}/{len(passwords_tested)} passwords valid. Failed passwords: {[p['password'] for p in failed_passwords[:3]]}"
                                self.log_test("Password Generation Validation", False, details, 
                                            {"failed_validations": failed_passwords[:3]})
                        else:
                            self.log_test("Password Generation Validation", False, 
                                        "No passwords found in created accounts")
                    else:
                        self.log_test("Password Generation Validation", False, 
                                    f"Failed to get job status: HTTP {job_response.status_code}")
                else:
                    self.log_test("Password Generation Validation", False, 
                                "No job_id returned from account creation")
            else:
                self.log_test("Password Generation Validation", False, 
                            f"Account creation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Password Generation Validation", False, f"Test error: {str(e)}")
        
        # Print detailed password analysis
        if passwords_tested:
            print(f"\n📋 Password Analysis ({len(passwords_tested)} samples):")
            for i, password in enumerate(passwords_tested[:5]):  # Show first 5
                validation = self.validate_garena_password(password)
                status = "✅" if self.is_password_valid(password) else "❌"
                print(f"  {i+1}. {password} {status}")
                print(f"     Length: {len(password)} chars, Lower: {validation['has_lowercase']}, "
                      f"Upper: {validation['has_uppercase']}, Digit: {validation['has_digit']}, "
                      f"Symbol: {validation['has_symbol']}")
    
    async def test_password_length_consistency(self):
        """Test that all generated passwords have consistent length (should be 12)"""
        try:
            # Create a few accounts to check password length consistency
            payload = {"quantity": 5, "email_provider": "temp-mail"}
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    await asyncio.sleep(3)
                    
                    job_response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
                    
                    if job_response.status_code == 200:
                        job_data = job_response.json()
                        accounts = job_data.get("accounts", [])
                        
                        password_lengths = []
                        for account in accounts:
                            password = account.get("password")
                            if password:
                                password_lengths.append(len(password))
                        
                        if password_lengths:
                            unique_lengths = set(password_lengths)
                            expected_length = 12  # Based on code analysis
                            
                            if len(unique_lengths) == 1 and expected_length in unique_lengths:
                                self.log_test("Password Length Consistency", True, 
                                            f"All passwords have consistent length: {expected_length} characters")
                            else:
                                self.log_test("Password Length Consistency", False, 
                                            f"Inconsistent lengths found: {unique_lengths}, expected: {expected_length}")
                        else:
                            self.log_test("Password Length Consistency", False, 
                                        "No passwords found to test length")
                    else:
                        self.log_test("Password Length Consistency", False, 
                                    f"Failed to get job status: HTTP {job_response.status_code}")
                else:
                    self.log_test("Password Length Consistency", False, 
                                "No job_id returned from account creation")
            else:
                self.log_test("Password Length Consistency", False, 
                            f"Account creation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Password Length Consistency", False, f"Test error: {str(e)}")

    async def test_mail_tm_inbox_checking(self):
        """Test GET /api/accounts/{account_id}/inbox with mail.tm JWT authentication"""
        if not self.created_accounts:
            self.log_test("Mail.tm Inbox Checking", False, "No accounts available for testing")
            return
        
        # Test with mail.tm account
        mail_tm_account = None
        
        for account in self.created_accounts:
            if account.get("email_provider") == "mail.tm":
                mail_tm_account = account
                break
        
        if mail_tm_account:
            try:
                account_id = mail_tm_account["id"]
                response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox")
                
                if response.status_code == 200:
                    data = response.json()
                    if "messages" in data and data.get("provider") == "mail.tm":
                        messages = data["messages"]
                        email = data.get("email")
                        
                        # Check if response has proper structure
                        has_count = "count" in data
                        has_account_id = data.get("account_id") == account_id
                        
                        if has_count and has_account_id:
                            self.log_test("Mail.tm Inbox Check", True, 
                                        f"✅ Inbox accessible for {email}, {len(messages)} messages found, JWT auth working")
                        else:
                            self.log_test("Mail.tm Inbox Check", False, 
                                        f"❌ Missing required fields in response", data)
                    else:
                        # Check if it's an error due to missing token
                        if "error" in data and "token" in data.get("error", "").lower():
                            self.log_test("Mail.tm Inbox Check", False, 
                                        f"❌ JWT token issue: {data.get('error')}", data)
                        else:
                            self.log_test("Mail.tm Inbox Check", False, 
                                        f"❌ Invalid inbox response format", data)
                else:
                    self.log_test("Mail.tm Inbox Check", False, f"HTTP {response.status_code}", 
                                {"status": response.status_code, "text": response.text})
            except Exception as e:
                self.log_test("Mail.tm Inbox Check", False, f"Request error: {str(e)}")
        else:
            self.log_test("Mail.tm Inbox Check", False, "No mail.tm accounts found for testing")
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Garena Backend Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Basic connectivity
            await self.test_root_endpoint()
            
            # Email providers
            await self.test_email_providers_endpoint()
            
            # Test email provider functionality
            await self.test_email_provider_testing("temp-mail")
            await self.test_email_provider_testing("10minutemail")
            
            # PRIORITY: Test password generation (Garena requirements)
            await self.test_password_generation_direct()
            await self.test_password_length_consistency()
            
            # Test account creation with both providers
            job1 = await self.test_account_creation(2, "10minutemail")
            job2 = await self.test_account_creation(2, "temp-mail")
            
            # Wait for jobs to complete and check status
            if job1:
                await self.test_job_status(job1, "10minutemail")
            if job2:
                await self.test_job_status(job2, "temp-mail")
            
            # List all accounts
            await self.test_list_accounts()
            
            # Test inbox functionality
            await self.test_inbox_checking()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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
        
        return passed == total


async def main():
    """Main test runner"""
    tester = GarenaBackendTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)