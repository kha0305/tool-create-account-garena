#!/usr/bin/env python3
"""
Debug script to test 10minutemail.one integration
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def debug_10minutemail():
    """Debug the 10minutemail.one service"""
    print("🔍 Debugging 10minutemail.one integration...")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            print("📡 Making request to 10minutemail.one...")
            response = await client.get("https://10minutemail.one")
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Length: {len(response.text)}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for email input fields
                print("\n🔍 Looking for email input fields...")
                email_inputs = soup.find_all('input', {'type': 'text'})
                for i, inp in enumerate(email_inputs):
                    print(f"Input {i+1}: value='{inp.get('value')}', placeholder='{inp.get('placeholder')}', readonly={inp.get('readonly')}")
                
                # Look for any text that looks like an email
                print("\n📧 Looking for email patterns in page...")
                email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                emails_found = re.findall(email_pattern, response.text)
                for email in emails_found:
                    if "example" not in email.lower() and "test" not in email.lower():
                        print(f"Found email: {email}")
                
                # Look for JavaScript that might contain email generation
                print("\n🔧 Looking for JavaScript...")
                scripts = soup.find_all('script')
                for i, script in enumerate(scripts):
                    if script.string and len(script.string) > 100:
                        print(f"Script {i+1}: {len(script.string)} characters")
                        # Look for email-related keywords
                        if any(keyword in script.string.lower() for keyword in ['email', 'mail', 'address']):
                            print(f"  Contains email-related code")
                            # Show first 200 chars
                            print(f"  Preview: {script.string[:200]}...")
                
                # Look for any divs or spans that might contain the email
                print("\n📋 Looking for email containers...")
                potential_containers = soup.find_all(['div', 'span', 'p'], string=re.compile(r'@'))
                for container in potential_containers:
                    print(f"Container: {container.name}, text: '{container.get_text().strip()}'")
                
                # Save a sample of the HTML for inspection
                with open('/app/10minutemail_sample.html', 'w') as f:
                    f.write(response.text[:5000])  # First 5000 chars
                print("\n💾 Saved first 5000 chars to /app/10minutemail_sample.html")
                
            else:
                print(f"❌ Failed to access 10minutemail.one: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_10minutemail())