#!/usr/bin/env python3
"""
Test account creation endpoint to verify passwords meet Garena requirements
"""

import asyncio
import httpx
import re

BACKEND_URL = "https://task-exec.preview.emergentagent.com/api"

def validate_garena_password(password: str) -> dict:
    """Validate password against Garena requirements"""
    return {
        "length_valid": 8 <= len(password) <= 16,
        "has_lowercase": bool(re.search(r'[a-z]', password)),
        "has_uppercase": bool(re.search(r'[A-Z]', password)),
        "has_digit": bool(re.search(r'[0-9]', password)),
        "has_symbol": bool(re.search(r'[!@#$%^&*]', password))
    }

async def test_account_creation_passwords():
    """Test POST /api/accounts/create and verify passwords in response"""
    print("🧪 TESTING ACCOUNT CREATION ENDPOINT")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test creating 3 accounts
            for provider in ["temp-mail", "10minutemail"]:
                print(f"\n📧 Testing with {provider} provider:")
                
                payload = {"quantity": 3, "email_provider": provider}
                response = await client.post(f"{BACKEND_URL}/accounts/create", json=payload)
                
                if response.status_code != 200:
                    print(f"❌ Account creation failed: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                job_id = data.get("job_id")
                print(f"✅ Job created: {job_id}")
                
                # Wait for completion
                await asyncio.sleep(5)
                
                # Get accounts
                job_response = await client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
                if job_response.status_code != 200:
                    print(f"❌ Failed to get job status")
                    continue
                
                job_data = job_response.json()
                accounts = job_data.get("accounts", [])
                
                print(f"📋 Checking {len(accounts)} accounts:")
                
                all_valid = True
                for i, account in enumerate(accounts, 1):
                    password = account.get("password", "")
                    validation = validate_garena_password(password)
                    is_valid = all(validation.values())
                    
                    status = "✅" if is_valid else "❌"
                    print(f"  {i}. {password} {status}")
                    
                    if not is_valid:
                        all_valid = False
                        issues = [k for k, v in validation.items() if not v]
                        print(f"     Issues: {issues}")
                
                if all_valid:
                    print(f"🎉 All {provider} passwords are valid!")
                else:
                    print(f"❌ Some {provider} passwords failed validation")
                    
        except Exception as e:
            print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_account_creation_passwords())