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
    API_URL = "https://web.10minutemail.one/api/v1"
    
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
                # Try to use the API directly first
                try:
                    # Try to get a new email session via API
                    api_response = await client.post(f"{self.API_URL}/session")
                    if api_response.status_code == 200:
                        session_data = api_response.json()
                        if 'email' in session_data:
                            self.email_address = session_data['email']
                            self.session_cookies = dict(api_response.cookies)
                            logger.info(f"Got new email via API: {self.email_address}")
                            return {
                                'email': self.email_address,
                                'cookies': self.session_cookies,
                                'session_data': session_data,
                                'provider': '10minutemail'
                            }
                except Exception as api_error:
                    logger.warning(f"API approach failed: {api_error}")
                
                # Fallback to web scraping approach
                response = await client.get(self.BASE_URL)
                
                if response.status_code != 200:
                    logger.error(f"Failed to access 10minutemail.one: {response.status_code}")
                    return None
                
                # Save cookies for session
                self.session_cookies = dict(response.cookies)
                
                # Parse HTML to find email address or API endpoints
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for JavaScript configuration that might contain API info
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'apiBaseUrl' in script.string:
                        # Try to extract API configuration
                        api_match = re.search(r'"apiBaseUrl":"([^"]+)"', script.string)
                        if api_match:
                            api_base = api_match.group(1)
                            logger.info(f"Found API base URL: {api_base}")
                            
                            # Try to get email from API
                            try:
                                api_response = await client.get(f"{api_base}/session", cookies=self.session_cookies)
                                if api_response.status_code == 200:
                                    session_data = api_response.json()
                                    if 'email' in session_data:
                                        self.email_address = session_data['email']
                                        logger.info(f"Got email from discovered API: {self.email_address}")
                                        return {
                                            'email': self.email_address,
                                            'cookies': self.session_cookies,
                                            'session_data': session_data,
                                            'provider': '10minutemail'
                                        }
                            except Exception as e:
                                logger.warning(f"Discovered API failed: {e}")
                
                # If all else fails, generate a fallback email with the domain from the config
                domains_match = re.search(r'"emailDomains":"(\[.*?\])"', response.text)
                if domains_match:
                    try:
                        domains_str = domains_match.group(1).replace('\\"', '"')
                        domains = json.loads(domains_str)
                        if domains:
                            import random
                            import string
                            domain = random.choice(domains)
                            local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                            fallback_email = f"{local_part}@{domain}"
                            logger.info(f"Generated fallback email: {fallback_email}")
                            return {
                                'email': fallback_email,
                                'cookies': self.session_cookies,
                                'provider': '10minutemail'
                            }
                    except Exception as e:
                        logger.warning(f"Fallback email generation failed: {e}")
                
                logger.error("Could not get email from 10minutemail.one")
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
            session_data = email_data.get('session_data', {})
            
            if not email:
                return []
            
            async with httpx.AsyncClient(
                follow_redirects=True, 
                timeout=30.0,
                cookies=cookies
            ) as client:
                messages = []
                
                # Try API approach first
                api_endpoints = [
                    f"{self.API_URL}/messages",
                    f"{self.API_URL}/inbox",
                    f"{self.API_URL}/session/messages"
                ]
                
                for api_endpoint in api_endpoints:
                    try:
                        api_response = await client.get(api_endpoint)
                        if api_response.status_code == 200:
                            data = api_response.json()
                            if isinstance(data, list):
                                messages = data
                                break
                            elif isinstance(data, dict) and 'messages' in data:
                                messages = data['messages']
                                break
                            elif isinstance(data, dict) and 'data' in data:
                                messages = data['data']
                                break
                    except Exception as e:
                        logger.debug(f"API endpoint {api_endpoint} failed: {e}")
                        continue
                
                # If API didn't work, try web scraping
                if not messages:
                    response = await client.get(self.BASE_URL)
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to check inbox: {response.status_code}")
                        return []
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for API configuration in JavaScript
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'apiBaseUrl' in script.string:
                            # Try to extract API configuration
                            api_match = re.search(r'"apiBaseUrl":"([^"]+)"', script.string)
                            if api_match:
                                api_base = api_match.group(1)
                                
                                # Try to get messages from discovered API
                                try:
                                    api_response = await client.get(f"{api_base}/messages")
                                    if api_response.status_code == 200:
                                        data = api_response.json()
                                        if isinstance(data, list):
                                            messages = data
                                        elif isinstance(data, dict) and 'messages' in data:
                                            messages = data['messages']
                                except Exception as e:
                                    logger.debug(f"Discovered API messages failed: {e}")
                
                # Format messages to consistent structure
                formatted_messages = []
                for msg in messages:
                    if isinstance(msg, dict):
                        formatted_messages.append({
                            'sender': msg.get('from', msg.get('sender', 'Unknown')),
                            'subject': msg.get('subject', 'No Subject'),
                            'body': msg.get('body', msg.get('content', '')),
                            'received': msg.get('received', msg.get('timestamp', 'Unknown'))
                        })
                
                logger.info(f"Found {len(formatted_messages)} messages in inbox")
                return formatted_messages
                
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
