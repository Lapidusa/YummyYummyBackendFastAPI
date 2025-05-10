import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, Header, UploadFile
from fastapi.params import File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UpdateUserBase
from app.services.cache_service import ConnectRedis
from app.services.response_utils import ResponseUtils
from app.services.sms_service import SmsService
from app.services.user_service import UserService
from app.core.security import SecurityMiddleware
from pydantic import BaseModel, EmailStr
from app.db import get_db

sms_service = SmsService()
router = APIRouter()
connect = ConnectRedis()
class RegisterOrLoginRequest(BaseModel):
  phone_number: str

class VerifyCodeRequest(BaseModel):
  phone_number: str
  code: str

logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
@router.post("/send-sms/")
async def send_sms(request: RegisterOrLoginRequest):
  response = await sms_service.send_sms(request.phone_number)

  if response is None:
    return ResponseUtils.error(message="Ошибка при отправке SMS")

  return ResponseUtils.success(message="SMS отправлен успешно")

@router.post("/verify-code/")
async def verify_code(request: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):

  stored_code = await connect.verify_sms_code(request.phone_number, request.code)
  if stored_code:

    existing_user = await UserService.get_user_by_phone(db, request.phone_number)
    await connect.delete_data(request.phone_number)

    if existing_user:
      token = SecurityMiddleware.generate_jwt_token(str(existing_user.id))

      return ResponseUtils.success(
        token=token,
      )
    else:
      new_user = await UserService.create_new_user(db, request.phone_number)
      token = SecurityMiddleware.generate_jwt_token(str(new_user.id))

      return ResponseUtils.success(
        token=token,
      )

  else:
    return ResponseUtils.error(message="Неверный код или срок действия кода истёк")
@router.put("/update-user/")
async def update_user(
    token: str = Header(alias="token"),
    db: AsyncSession = Depends(get_db),
    email: EmailStr = Form(None),
    name: str = Form(None),
    phone_number: str = Form(None),
    date_of_birth: datetime = Form(None),
    image: UploadFile = File(None)):

  if token:

    image_url = None
    if image:
      if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return ResponseUtils.error(message="Только PNG и JPG изображения")

      save_path = f"media/avatars/{image.filename}"
      os.makedirs(os.path.dirname(save_path), exist_ok=True)
      with open(save_path, "wb") as f:
        content = await image.read()
        f.write(content)
      image_url = f"/media/avatars/{image.filename}"

    update_data = UpdateUserBase(
      email=email,
      name=name,
      phone_number=phone_number,
      date_of_birth=date_of_birth,
      image_url=image_url
    )
    new_user = await UserService.update_user(db, token, update_data)
    if new_user:
      return ResponseUtils.success(user = new_user)
  else:
    return ResponseUtils.error(message="Не найден пользователь")
@router.get("/get-user/")
async def get_user(token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  user = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if user:
    return ResponseUtils.success(user=user)
  else:
    return ResponseUtils.error(message="Не найден пользователь")

@router.post("/logout/")
async def logout_route(token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  user = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if user:
    await SecurityMiddleware.logout(token)
    return ResponseUtils.success(message="Вы успешно вышли из системы")
  else:
    return ResponseUtils.error(message="Не действительный токен")
