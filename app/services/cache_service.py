import os
from datetime import timedelta
import hashlib
import redis.asyncio as aioredis
import httpx

class ConnectRedis:
  API_URL = os.getenv("SMS_API_URL")
  API_KEY = os.getenv("SMS_API_KEY")

  def __init__(self):
    self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.API_KEY}"})
    self.redis_client = aioredis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)

  async def set_data_with_expiry(self, key: str, value: str, expiry_minutes: int) -> bool:
    hashed_value = hashlib.sha256(value.encode()).hexdigest()
    delta = timedelta(minutes=expiry_minutes)
    success = await self.redis_client.setex(key, delta, hashed_value)
    return bool(success)

  async def delete_data(self, key: str) -> bool:
    deleted_count = await self.redis_client.delete(key)
    return bool(deleted_count)

  async def verify_sms_code(self, phone_number: str, code: str) -> bool:
    stored_code = await self.redis_client.get(phone_number)
    hashed_input = hashlib.sha256(code.encode()).hexdigest()
    if stored_code:
      return stored_code == hashed_input
    return False

  async def get_value_by_key(self, key: str) -> str:
    value = await self.redis_client.get(key)
    return value