#!/usr/bin/env python3
"""
Focused Password Generation Test for Garena Requirements
Tests the generate_password() function fix specifically
"""

import asyncio
import httpx
import re
from typing import Dict, List

BACKEND_URL = "https://task-exec.preview.emergentagent.com/api"

def validate_garena_password(password: str) -> Dict[str, bool]:
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

def is_password_valid(password: str) -> bool:
    """Check if password meets ALL Garena requirements"""
    validation = validate_garena_password(password)
    return all(validation.values())

async def test_password_generation_comprehensive():
    """Generate 15 accounts and test all passwords"""
    print("🔐 COMPREHENSIVE PASSWORD GENERATION TEST")
    print("=" * 60)
    print("Garena Requirements:")
    print("- Between 8-16 characters")
    print("- At least one lowercase letter (a-z)")
    print("- At least one uppercase letter (A-Z)")
    print("- At least one number (0-9)")
    print("- At least one symbol (!@#$%^&*)")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Create 15 accounts to get a good sample of passwords
            payload = {"quantity": 15, "email_provider": "temp-mail"}
            response = await client.post(f"{BACKEND_URL}/accounts/create", json=payload)
            
            if response.status_code != 200:
                print(f"❌ Failed to create accounts: HTTP {response.status_code}")
                return False
            
            data = response.json()
            job_id = data.get("job_id")
            
            if not job_id:
                print("❌ No job_id returned")
                return False
            
            print(f"✅ Account creation job started: {job_id}")
            print("⏳ Waiting for accounts to be created...")
            
            # Wait for job completion
            await asyncio.sleep(8)
            
            # Get job status to retrieve created accounts
            job_response = await client.get(f"{BACKEND_URL}/accounts/job/{job_id}")
            
            if job_response.status_code != 200:
                print(f"❌ Failed to get job status: HTTP {job_response.status_code}")
                return False
            
            job_data = job_response.json()
            accounts = job_data.get("accounts", [])
            
            if not accounts:
                print("❌ No accounts found in job")
                return False
            
            print(f"✅ Retrieved {len(accounts)} accounts")
            print("\n📋 PASSWORD ANALYSIS:")
            print("-" * 80)
            
            passwords_tested = []
            failed_passwords = []
            
            for i, account in enumerate(accounts, 1):
                password = account.get("password")
                if not password:
                    continue
                    
                passwords_tested.append(password)
                validation = validate_garena_password(password)
                is_valid = is_password_valid(password)
                
                if not is_valid:
                    failed_passwords.append({
                        "password": password,
                        "validation": validation
                    })
                
                # Display each password with validation details
                status = "✅" if is_valid else "❌"
                print(f"{i:2d}. {password:16s} {status} (Len:{len(password):2d}) "
                      f"L:{validation['has_lowercase']} U:{validation['has_uppercase']} "
                      f"D:{validation['has_digit']} S:{validation['has_symbol']}")
            
            print("-" * 80)
            
            # Summary
            success_count = len(passwords_tested) - len(failed_passwords)
            success_rate = (success_count / len(passwords_tested) * 100) if passwords_tested else 0
            
            print(f"\n📊 RESULTS SUMMARY:")
            print(f"Total passwords tested: {len(passwords_tested)}")
            print(f"Valid passwords: {success_count}")
            print(f"Invalid passwords: {len(failed_passwords)}")
            print(f"Success rate: {success_rate:.1f}%")
            
            # Check length consistency
            lengths = [len(p) for p in passwords_tested]
            unique_lengths = set(lengths)
            print(f"Password lengths: {unique_lengths}")
            
            if len(failed_passwords) > 0:
                print(f"\n❌ FAILED PASSWORDS:")
                for fail in failed_passwords:
                    pwd = fail["password"]
                    val = fail["validation"]
                    issues = []
                    if not val["length_valid"]: issues.append("length")
                    if not val["has_lowercase"]: issues.append("no lowercase")
                    if not val["has_uppercase"]: issues.append("no uppercase")
                    if not val["has_digit"]: issues.append("no digit")
                    if not val["has_symbol"]: issues.append("no symbol")
                    print(f"  {pwd} - Issues: {', '.join(issues)}")
                return False
            else:
                print(f"\n🎉 ALL PASSWORDS MEET GARENA REQUIREMENTS!")
                return True
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            return False

async def main():
    success = await test_password_generation_comprehensive()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)