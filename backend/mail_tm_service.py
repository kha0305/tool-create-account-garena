"""
Mail.tm Service - Temporary Email Provider (Async robust)
API Docs: https://docs.mail.tm
"""
import httpx
import random
import string
from typing import Dict, List, Optional
from datetime import datetime
import logging

class MailTmService:
    BASE_URL = "https://api.mail.tm"

    async def _client(self):
        # HTTP2 không bắt buộc; timeout để tránh treo
        return httpx.AsyncClient(timeout=30.0)

    async def get_domains(self) -> List[str]:
        try:
            async with await self._client() as client:
                resp = await client.get(f"{self.BASE_URL}/domains")
                if resp.status_code == 200:
                    data = resp.json()
                    domains = [d.get("domain") for d in data.get("hydra:member", []) if d.get("domain")]
                    if domains:
                        logging.info(f"📚 mail.tm domains: {domains}")
                        return domains
                logging.warning(f"⚠️ get_domains status={resp.status_code} body={resp.text[:200]}")
                return ["mail.tm"]  # fallback tên thôi; create_account sẽ fail nếu domain thật ko hợp lệ
        except Exception as e:
            logging.warning(f"⚠️ get_domains error: {e}")
            return ["mail.tm"]

    async def create_account(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        domains = await self.get_domains()
        # Ưu tiên domain thực (nếu API trả về), nếu không thì dùng fallback — sẽ bị 400 và được log rõ.
        domain = random.choice(domains)

        username = username or ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        password = password or ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        email_address = f"{username}@{domain}"

        payload = {"address": email_address, "password": password}

        async with await self._client() as client:
            # Create account
            resp = await client.post(f"{self.BASE_URL}/accounts", json=payload)
            if resp.status_code not in (200, 201):
                logging.error(f"❌ create_account status={resp.status_code} body={resp.text[:500]}")
                raise Exception(f"create_account failed {resp.status_code}")

            # Get token
            tok = await client.post(f"{self.BASE_URL}/token", json=payload)
            if tok.status_code != 200:
                logging.error(f"❌ get_token status={tok.status_code} body={tok.text[:500]}")
                raise Exception(f"get_token failed {tok.status_code}")

            token_data = tok.json()
            token = token_data.get("token", "")

            logging.info(f"✅ mail.tm account: {email_address}")

            return {
                "email": email_address,
                "password": password,
                "session_data": {
                    "email": email_address,
                    "password": password,
                    "token": token,
                    "created_at": datetime.utcnow().isoformat()
                }
            }

    async def get_messages(self, token: str):
        try:
            async with await self._client() as client:
                resp = await client.get(f"{self.BASE_URL}/messages", headers={"Authorization": f"Bearer {token}"})
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("hydra:member", [])
                logging.warning(f"⚠️ get_messages status={resp.status_code} body={resp.text[:300]}")
                return []
        except Exception as e:
            logging.error(f"get_messages error: {e}")
            return []

    async def get_message_content(self, message_id: str, token: str) -> Optional[Dict]:
        try:
            async with await self._client() as client:
                resp = await client.get(
                    f"{self.BASE_URL}/messages/{message_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code == 200:
                    return resp.json()
                logging.warning(f"⚠️ get_message_content status={resp.status_code} body={resp.text[:300]}")
                return None
        except Exception as e:
            logging.error(f"get_message_content error: {e}")
            return None
