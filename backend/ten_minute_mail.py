"""
10 Minute Mail Integration Module
Provides functionality to get temporary emails from 10minutemail.one
"""
import httpx
import logging
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import asyncio
import json

logger = logging.getLogger(__name__)

class TenMinuteMail:
    """Class to interact with 10minutemail.one service"""
    
    BASE_URL = "https://10minutemail.one"
    
    def __init__(self):
        self.session_cookies = None
        self.email_address = None
        self.session_id = None
    
    async def get_new_email(self) -> Optional[Dict[str, str]]:
        """
        Get a new temporary email address from 10minutemail.one
        Returns: Dict with email address and session data
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                # First request to get the page and email
                response = await client.get(self.BASE_URL)
                
                if response.status_code != 200:
                    logger.error(f"Failed to access 10minutemail.one: {response.status_code}")
                    return None
                
                # Save cookies for session
                self.session_cookies = dict(response.cookies)
                
                # Parse HTML to find email address
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the email input field
                email_input = soup.find('input', {'type': 'text', 'readonly': True})
                
                if email_input and email_input.get('value'):
                    self.email_address = email_input.get('value')
                    logger.info(f"Got new email: {self.email_address}")
                    
                    return {
                        'email': self.email_address,
                        'cookies': self.session_cookies,
                        'provider': '10minutemail'
                    }
                else:
                    # Try to find email in script tags or other places
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # Look for email pattern in JavaScript
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', script.string)
                            if email_match:
                                self.email_address = email_match.group(0)
                                logger.info(f"Found email in script: {self.email_address}")
                                return {
                                    'email': self.email_address,
                                    'cookies': self.session_cookies,
                                    'provider': '10minutemail'
                                }
                    
                    logger.error("Could not find email address on page")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting email from 10minutemail.one: {e}")
            return None
    
    async def check_inbox(self, email_data: Dict) -> List[Dict]:
        """
        Check inbox for messages
        Args:
            email_data: Dict containing email and session cookies
        Returns: List of messages
        """
        try:
            cookies = email_data.get('cookies', {})
            email = email_data.get('email')
            
            if not email:
                return []
            
            async with httpx.AsyncClient(
                follow_redirects=True, 
                timeout=30.0,
                cookies=cookies
            ) as client:
                # Try to get the inbox page
                response = await client.get(self.BASE_URL)
                
                if response.status_code != 200:
                    logger.error(f"Failed to check inbox: {response.status_code}")
                    return []
                
                soup = BeautifulSoup(response.text, 'html.parser')
                messages = []
                
                # Look for message elements
                # The structure may vary, so we'll try multiple approaches
                
                # Try to find API endpoint in page source
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'api' in script.string.lower():
                        # Look for API endpoints in JavaScript
                        api_match = re.search(r'["\'](/api/[^"\']+)["\']', script.string)
                        if api_match:
                            api_endpoint = api_match.group(1)
                            logger.info(f"Found API endpoint: {api_endpoint}")
                            
                            # Try to call the API
                            api_response = await client.get(f"{self.BASE_URL}{api_endpoint}")
                            if api_response.status_code == 200:
                                try:
                                    data = api_response.json()
                                    if isinstance(data, list):
                                        messages = data
                                    elif isinstance(data, dict) and 'messages' in data:
                                        messages = data['messages']
                                except:
                                    pass
                
                # If no messages found via API, try parsing HTML
                if not messages:
                    # Look for message divs/cards
                    message_elements = soup.find_all(['div', 'li'], class_=re.compile(r'message|mail|email', re.I))
                    
                    for elem in message_elements:
                        # Try to extract message info
                        sender = elem.find(text=re.compile(r'from|sender', re.I))
                        subject = elem.find(text=re.compile(r'subject', re.I))
                        
                        if sender or subject:
                            messages.append({
                                'sender': sender if sender else 'Unknown',
                                'subject': subject if subject else 'No Subject',
                                'received': 'Just now'
                            })
                
                logger.info(f"Found {len(messages)} messages in inbox")
                return messages
                
        except Exception as e:
            logger.error(f"Error checking inbox: {e}")
            return []
    
    async def get_message_content(self, email_data: Dict, message_id: str) -> Optional[Dict]:
        """
        Get full content of a specific message
        Args:
            email_data: Dict containing email and session cookies
            message_id: ID of the message to fetch
        Returns: Message content dict
        """
        try:
            cookies = email_data.get('cookies', {})
            
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=30.0,
                cookies=cookies
            ) as client:
                # Try common API patterns
                api_patterns = [
                    f"/api/messages/{message_id}",
                    f"/message/{message_id}",
                    f"/api/mail/{message_id}"
                ]
                
                for pattern in api_patterns:
                    response = await client.get(f"{self.BASE_URL}{pattern}")
                    if response.status_code == 200:
                        try:
                            return response.json()
                        except:
                            return {'body': response.text}
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting message content: {e}")
            return None


# Singleton instance
ten_minute_mail_service = TenMinuteMail()


async def get_10minute_email() -> Optional[str]:
    """
    Helper function to get a new email from 10minutemail.one
    Returns: email address string or None
    """
    result = await ten_minute_mail_service.get_new_email()
    if result:
        return result['email']
    return None


async def get_10minute_email_with_session() -> Optional[Dict]:
    """
    Helper function to get a new email with session data
    Returns: Dict with email and session data or None
    """
    return await ten_minute_mail_service.get_new_email()
