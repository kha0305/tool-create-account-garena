#!/usr/bin/env python3
"""
Backend Test Suite for Garena Account Creator
Tests the 10minutemail.one integration and all API endpoints
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
        """Test GET /api/email-providers"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/email-providers")
            
            if response.status_code == 200:
                data = response.json()
                if "providers" in data and isinstance(data["providers"], list):
                    providers = data["providers"]
                    provider_ids = [p.get("id") for p in providers]
                    
                    if "temp-mail" in provider_ids and "10minutemail" in provider_ids:
                        self.log_test("Email Providers Endpoint", True, f"Found {len(providers)} providers: {provider_ids}")
                    else:
                        self.log_test("Email Providers Endpoint", False, f"Missing required providers. Found: {provider_ids}", data)
                else:
                    self.log_test("Email Providers Endpoint", False, "Invalid response format", data)
            else:
                self.log_test("Email Providers Endpoint", False, f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test("Email Providers Endpoint", False, f"Request error: {str(e)}")
    
    async def test_email_provider_testing(self, provider: str):
        """Test POST /api/test-email-provider"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/test-email-provider?provider={provider}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("email"):
                    email = data["email"]
                    has_session = data.get("has_session", False)
                    self.log_test(f"Test {provider} Provider", True, 
                                f"Generated email: {email}, has_session: {has_session}")
                else:
                    self.log_test(f"Test {provider} Provider", False, 
                                f"Provider test failed: {data.get('error', 'Unknown error')}", data)
            else:
                self.log_test(f"Test {provider} Provider", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test(f"Test {provider} Provider", False, f"Request error: {str(e)}")
    
    async def test_account_creation(self, quantity: int, email_provider: str):
        """Test POST /api/accounts/create"""
        try:
            payload = {
                "quantity": quantity,
                "email_provider": email_provider
            }
            response = await self.client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data:
                    job_id = data["job_id"]
                    self.job_ids.append(job_id)
                    self.log_test(f"Create {quantity} Accounts ({email_provider})", True, 
                                f"Job started: {job_id}")
                    return job_id
                else:
                    self.log_test(f"Create {quantity} Accounts ({email_provider})", False, 
                                "Missing job_id in response", data)
            else:
                self.log_test(f"Create {quantity} Accounts ({email_provider})", False, 
                            f"HTTP {response.status_code}", {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test(f"Create {quantity} Accounts ({email_provider})", False, f"Request error: {str(e)}")
        return None
    
    async def test_job_status(self, job_id: str, expected_provider: str):
        """Test GET /api/accounts/job/{job_id}"""
        try:
            # Wait a bit for job to process
            await asyncio.sleep(3)
            
            response = await self.client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                completed = data.get("completed", 0)
                total = data.get("total", 0)
                accounts = data.get("accounts", [])
                
                # Check if accounts have correct email_provider
                provider_check = True
                for account in accounts:
                    if account.get("email_provider") != expected_provider:
                        provider_check = False
                        break
                    self.created_accounts.append(account)
                
                if provider_check:
                    self.log_test(f"Job Status ({job_id})", True, 
                                f"Status: {status}, Progress: {completed}/{total}, Provider: {expected_provider}")
                else:
                    self.log_test(f"Job Status ({job_id})", False, 
                                f"Accounts have wrong email_provider", data)
            else:
                self.log_test(f"Job Status ({job_id})", False, f"HTTP {response.status_code}", 
                            {"status": response.status_code, "text": response.text})
        except Exception as e:
            self.log_test(f"Job Status ({job_id})", False, f"Request error: {str(e)}")
    
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

    async def test_inbox_checking(self):
        """Test GET /api/accounts/{account_id}/inbox"""
        if not self.created_accounts:
            self.log_test("Inbox Checking", False, "No accounts available for testing")
            return
        
        # Test with 10minutemail account
        minutemail_account = None
        tempmail_account = None
        
        for account in self.created_accounts:
            if account.get("email_provider") == "10minutemail":
                minutemail_account = account
            elif account.get("email_provider") == "temp-mail":
                tempmail_account = account
        
        # Test 10minutemail inbox
        if minutemail_account:
            try:
                account_id = minutemail_account["id"]
                response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox")
                
                if response.status_code == 200:
                    data = response.json()
                    if "messages" in data and data.get("provider") == "10minutemail":
                        messages = data["messages"]
                        self.log_test("10minutemail Inbox Check", True, 
                                    f"Inbox accessible, {len(messages)} messages found")
                    else:
                        self.log_test("10minutemail Inbox Check", False, 
                                    "Invalid inbox response format", data)
                else:
                    self.log_test("10minutemail Inbox Check", False, f"HTTP {response.status_code}", 
                                {"status": response.status_code, "text": response.text})
            except Exception as e:
                self.log_test("10minutemail Inbox Check", False, f"Request error: {str(e)}")
        
        # Test temp-mail inbox (should show info message)
        if tempmail_account:
            try:
                account_id = tempmail_account["id"]
                response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox")
                
                if response.status_code == 200:
                    data = response.json()
                    if "info" in data and data.get("provider") == "temp-mail":
                        self.log_test("Temp-mail Inbox Check", True, 
                                    f"Correct info message: {data['info']}")
                    else:
                        self.log_test("Temp-mail Inbox Check", False, 
                                    "Missing expected info message", data)
                else:
                    self.log_test("Temp-mail Inbox Check", False, f"HTTP {response.status_code}", 
                                {"status": response.status_code, "text": response.text})
            except Exception as e:
                self.log_test("Temp-mail Inbox Check", False, f"Request error: {str(e)}")
    
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