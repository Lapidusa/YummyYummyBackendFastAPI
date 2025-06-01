import os
import httpx
import random
from typing import Optional
from datetime import datetime, timedelta

import logger
from dotenv import load_dotenv, find_dotenv

from app.services.cache_service import ConnectRedis

load_dotenv(find_dotenv())
connect = ConnectRedis()

class SmsCode:
  def __init__(self, phone_number: str, code: str, expiration: timedelta):
    self.phone_number = phone_number
    self.code = code
    self.expiration_time = datetime.utcnow() + expiration

  def is_valid(self, code: str) -> bool:
    return self.code == code and datetime.utcnow() < self.expiration_time

class SmsService:
  API_URL = os.getenv("SMS_API_URL")
  API_KEY = os.getenv("SMS_API_KEY")

  def __init__(self):
      self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.API_KEY}"})

  async def send_sms(self, phone_number: str) -> Optional[dict]:
    verification_code = self.generate_verification_code()

    success = await connect.set_data_with_expiry(phone_number, verification_code, 5)
    if not success:
        return {"dev_bypass": True}

    return {"message": "Код успешно сохранён", "code": verification_code}

      # message = f"Ваш код подтверждения: {verification_code}. Никому не сообщайте код."
    # payload = {
    #   "number": "79856010277",
    #   "destination": phone_number,
    #   "text": message
    # }
    # try:
    #   response = await self.client.post(self.API_URL, json=payload)
    #   print(response)
    #   response.raise_for_status()
    #   return response.json()
    # except httpx.HTTPError as e:
    #   logger.error(f"Ошибка при отправке SMS: {e}")
    #   return None

  @staticmethod
  def generate_verification_code() -> str:
      return str("111111")
      # return str(random.randint(100000, 999999))