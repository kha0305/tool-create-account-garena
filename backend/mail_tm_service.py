"""
Mail.tm Service - Temporary Email Provider
API Documentation: https://docs.mail.tm
"""
import httpx
import random
import string
from typing import Dict, List, Optional
from datetime import datetime


class MailTmService:
    """Service for managing temporary emails using mail.tm API"""
    
    BASE_URL = "https://api.mail.tm"
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
    
    def __del__(self):
        """Close HTTP client when object is destroyed"""
        try:
            self.client.close()
        except:
            pass
    
    async def get_domains(self) -> List[str]:
        """Get available email domains from mail.tm"""
        try:
            response = self.client.get(f"{self.BASE_URL}/domains")
            if response.status_code == 200:
                data = response.json()
                # Extract domain names from hydra:member array
                domains = [d['domain'] for d in data.get('hydra:member', [])]
                return domains if domains else ['mail.tm']
            return ['mail.tm']
        except Exception as e:
            print(f"Error getting domains: {e}")
            return ['mail.tm']
    
    async def create_account(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Create new temporary email account
        
        Returns:
            {
                'email': 'user@mail.tm',
                'password': 'password123',
                'account_id': 'account_id',
                'token': 'jwt_token',
                'session_data': {...}
            }
        """
        try:
            # Get available domains
            domains = await self.get_domains()
            domain = random.choice(domains)
            
            # Generate username if not provided
            if not username:
                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            
            # Generate password if not provided
            if not password:
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            email_address = f"{username}@{domain}"
            
            # Create account
            account_data = {
                "address": email_address,
                "password": password
            }
            
            response = self.client.post(
                f"{self.BASE_URL}/accounts",
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                account_info = response.json()
                account_id = account_info.get('id')
                
                # Get JWT token for this account
                token = await self.get_token(email_address, password)
                
                return {
                    'email': email_address,
                    'password': password,
                    'account_id': account_id,
                    'token': token,
                    'session_data': {
                        'account_id': account_id,
                        'token': token,
                        'email': email_address,
                        'password': password,
                        'created_at': datetime.utcnow().isoformat()
                    }
                }
            else:
                raise Exception(f"Failed to create account: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error creating mail.tm account: {e}")
            raise
    
    async def get_token(self, email: str, password: str) -> str:
        """Get JWT authentication token for an account"""
        try:
            token_data = {
                "address": email,
                "password": password
            }
            
            response = self.client.post(
                f"{self.BASE_URL}/token",
                json=token_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('token', '')
            else:
                raise Exception(f"Failed to get token: {response.status_code}")
                
        except Exception as e:
            print(f"Error getting token: {e}")
            raise
    
    async def get_messages(self, token: str) -> List[Dict]:
        """
        Get all messages for an account
        
        Returns list of messages with:
            - id: message ID
            - from: sender info
            - subject: email subject
            - intro: email preview
            - createdAt: timestamp
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/messages",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('hydra:member', [])
                
                # Format messages
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        'id': msg.get('id'),
                        'from': msg.get('from', {}).get('address', 'Unknown'),
                        'subject': msg.get('subject', 'No Subject'),
                        'intro': msg.get('intro', ''),
                        'created_at': msg.get('createdAt', ''),
                        'seen': msg.get('seen', False)
                    })
                
                return formatted_messages
            else:
                print(f"Error getting messages: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    async def get_message_content(self, message_id: str, token: str) -> Dict:
        """
        Get full content of a specific message
        
        Returns:
            {
                'id': message_id,
                'from': sender,
                'subject': subject,
                'text': plain text body,
                'html': html body,
                'created_at': timestamp
            }
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/messages/{message_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                msg = response.json()
                
                return {
                    'id': msg.get('id'),
                    'from': msg.get('from', {}).get('address', 'Unknown'),
                    'subject': msg.get('subject', 'No Subject'),
                    'text': msg.get('text', ''),
                    'html': msg.get('html', []),
                    'created_at': msg.get('createdAt', ''),
                    'attachments': msg.get('attachments', [])
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting message content: {e}")
            return {}
    
    async def delete_account(self, account_id: str, token: str) -> bool:
        """Delete a temporary email account"""
        try:
            response = self.client.delete(
                f"{self.BASE_URL}/accounts/{account_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False
