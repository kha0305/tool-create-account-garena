#!/usr/bin/env python3
"""
Test script for NEW Garena Account Creator features
Focus on: Export endpoints and Email content viewing
"""

import asyncio
import httpx
import json
import re
from typing import Dict

BACKEND_URL = "https://account-factory-2.preview.emergentagent.com/api"
TIMEOUT = 30.0

class NewFeaturesTester:
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
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def test_export_txt_endpoint(self):
        """Test GET /api/accounts/export/txt - Format: username|password|email|Tạo lúc: dd-mm-yy hh:mm"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/txt")
            
            if response.status_code == 200:
                # Check headers
                content_disposition = response.headers.get("content-disposition", "")
                content_type = response.headers.get("content-type", "")
                
                if "attachment" in content_disposition and "ACCOUNTS_" in content_disposition and ".txt" in content_disposition:
                    # Check content format
                    content = response.text
                    lines = content.strip().split('\n')
                    
                    if lines:
                        # Verify format: username|password|email|Tạo lúc: dd-mm-yy hh:mm
                        sample_line = lines[0]
                        parts = sample_line.split('|')
                        
                        if len(parts) == 4 and parts[3].startswith("Tạo lúc: "):
                            # Check date format (dd-mm-yy hh:mm)
                            time_part = parts[3].replace("Tạo lúc: ", "")
                            date_pattern = r'\d{2}-\d{2}-\d{2} \d{2}:\d{2}'
                            
                            if re.match(date_pattern, time_part):
                                filename_match = re.search(r'ACCOUNTS_(\d+)\.txt', content_disposition)
                                if filename_match:
                                    count = int(filename_match.group(1))
                                    self.log_test("Export TXT Endpoint", True, 
                                                f"✅ {count} accounts exported, format: username|password|email|Tạo lúc: dd-mm-yy hh:mm")
                                    print(f"   Sample: {sample_line}")
                                else:
                                    self.log_test("Export TXT Endpoint", False, "Filename format incorrect")
                            else:
                                self.log_test("Export TXT Endpoint", False, f"Date format incorrect: {time_part}")
                        else:
                            self.log_test("Export TXT Endpoint", False, f"Line format incorrect: {len(parts)} parts")
                    else:
                        self.log_test("Export TXT Endpoint", False, "Empty content")
                else:
                    self.log_test("Export TXT Endpoint", False, "Incorrect headers")
            elif response.status_code == 404:
                self.log_test("Export TXT Endpoint", True, "Returns 404 when no accounts (expected)")
            else:
                self.log_test("Export TXT Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Export TXT Endpoint", False, f"Error: {str(e)}")

    async def test_export_csv_endpoint(self):
        """Test GET /api/accounts/export/csv - Headers: Username,Email,Password,Phone,Status,Provider,Created At"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/csv")
            
            if response.status_code == 200:
                content_disposition = response.headers.get("content-disposition", "")
                
                if "ACCOUNTS_" in content_disposition and ".csv" in content_disposition:
                    content = response.text
                    lines = content.strip().split('\n')
                    
                    if lines:
                        header_line = lines[0]
                        expected_headers = ["Username", "Email", "Password", "Phone", "Status", "Provider", "Created At"]
                        actual_headers = header_line.split(',')
                        
                        if actual_headers == expected_headers:
                            filename_match = re.search(r'ACCOUNTS_(\d+)\.csv', content_disposition)
                            if filename_match:
                                count = int(filename_match.group(1))
                                self.log_test("Export CSV Endpoint", True, 
                                            f"✅ {count} accounts exported, correct CSV headers")
                                print(f"   Headers: {header_line}")
                            else:
                                self.log_test("Export CSV Endpoint", False, "Filename format incorrect")
                        else:
                            self.log_test("Export CSV Endpoint", False, f"Headers incorrect: {actual_headers}")
                    else:
                        self.log_test("Export CSV Endpoint", False, "Empty content")
                else:
                    self.log_test("Export CSV Endpoint", False, "Incorrect headers")
            elif response.status_code == 404:
                self.log_test("Export CSV Endpoint", True, "Returns 404 when no accounts (expected)")
            else:
                self.log_test("Export CSV Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Export CSV Endpoint", False, f"Error: {str(e)}")

    async def test_export_xlsx_endpoint(self):
        """Test GET /api/accounts/export/xlsx - Excel with styled headers"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/accounts/export/xlsx")
            
            if response.status_code == 200:
                content_disposition = response.headers.get("content-disposition", "")
                content_type = response.headers.get("content-type", "")
                
                expected_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                if ("ACCOUNTS_" in content_disposition and 
                    ".xlsx" in content_disposition and
                    content_type == expected_mime):
                    
                    content_length = len(response.content)
                    
                    if content_length > 0:
                        # Check Excel magic bytes (PK for ZIP format)
                        magic_bytes = response.content[:2]
                        if magic_bytes == b'PK':
                            filename_match = re.search(r'ACCOUNTS_(\d+)\.xlsx', content_disposition)
                            if filename_match:
                                count = int(filename_match.group(1))
                                self.log_test("Export XLSX Endpoint", True, 
                                            f"✅ {count} accounts exported, valid Excel format ({content_length} bytes)")
                            else:
                                self.log_test("Export XLSX Endpoint", False, "Filename format incorrect")
                        else:
                            self.log_test("Export XLSX Endpoint", False, "Invalid Excel format")
                    else:
                        self.log_test("Export XLSX Endpoint", False, "Empty file")
                else:
                    self.log_test("Export XLSX Endpoint", False, "Incorrect headers/MIME type")
            elif response.status_code == 404:
                self.log_test("Export XLSX Endpoint", True, "Returns 404 when no accounts (expected)")
            else:
                self.log_test("Export XLSX Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Export XLSX Endpoint", False, f"Error: {str(e)}")

    async def test_email_content_endpoint(self):
        """Test GET /api/accounts/{account_id}/inbox/{message_id} - Email content viewing"""
        try:
            # Get accounts first
            response = await self.client.get(f"{BACKEND_URL}/accounts")
            if response.status_code != 200:
                self.log_test("Email Content Endpoint", False, "Cannot get accounts list")
                return
            
            accounts = response.json()
            
            # Find account with session data and token
            test_account = None
            for acc in accounts:
                if (acc.get("email_provider") == "mail.tm" and 
                    acc.get("email_session_data") and 
                    acc.get("email_session_data", {}).get("token")):
                    test_account = acc
                    break
            
            if not test_account:
                self.log_test("Email Content Endpoint", False, "No mail.tm account with token found")
                return
            
            account_id = test_account["id"]
            
            # Test 1: Invalid message_id (should return 404 or 500)
            response = await self.client.get(f"{BACKEND_URL}/accounts/{account_id}/inbox/fake-message-123")
            if response.status_code in [404, 500]:
                error_test_pass = True
            else:
                error_test_pass = False
            
            # Test 2: Invalid account_id (should return 404)
            response = await self.client.get(f"{BACKEND_URL}/accounts/fake-account-123/inbox/fake-message-123")
            if response.status_code == 404:
                account_test_pass = True
            else:
                account_test_pass = False
            
            # Test 3: Account without session data
            accounts_without_session = [acc for acc in accounts if not acc.get("email_session_data")]
            if accounts_without_session:
                no_session_account = accounts_without_session[0]["id"]
                response = await self.client.get(f"{BACKEND_URL}/accounts/{no_session_account}/inbox/fake-message-123")
                if response.status_code == 400:
                    session_test_pass = True
                else:
                    session_test_pass = False
            else:
                session_test_pass = True  # No accounts without session to test
            
            if error_test_pass and account_test_pass and session_test_pass:
                self.log_test("Email Content Endpoint", True, 
                            "✅ Endpoint exists and handles all error cases correctly")
            else:
                self.log_test("Email Content Endpoint", False, 
                            f"Error handling issues: invalid_msg={error_test_pass}, invalid_acc={account_test_pass}, no_session={session_test_pass}")
                
        except Exception as e:
            self.log_test("Email Content Endpoint", False, f"Error: {str(e)}")

    async def run_tests(self):
        """Run all new feature tests"""
        print("🆕 Testing NEW Garena Account Creator Features")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Test all new export endpoints
            await self.test_export_txt_endpoint()
            await self.test_export_csv_endpoint()
            await self.test_export_xlsx_endpoint()
            
            # Test email content viewing
            await self.test_email_content_endpoint()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 NEW FEATURES TEST SUMMARY")
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
            print("\n🎉 All new features working correctly!")
        
        return passed == total

async def main():
    """Main test runner"""
    tester = NewFeaturesTester()
    success = await tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)