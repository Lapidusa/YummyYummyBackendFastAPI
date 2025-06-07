import logging
import os
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Header, UploadFile, Query
from fastapi.params import File, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UpdateUserForm, UserPayload, UserPayloadWithId
from app.services.cache_service import ConnectRedis
from app.services.response_utils import ResponseUtils
from app.services.sms_service import SmsService
from app.services.user_service import UserService
from app.core.security import SecurityMiddleware
from pydantic import BaseModel
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

@router.get("/get-all-users/")
async def get_all_users(token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin(token, db)
  users = await UserService.get_all_users(db)
  return ResponseUtils.success(users=users)

@router.post("/create-user/")
async def create_user(request: UserPayload, token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin(token, db)

  try:
    return ResponseUtils.success(user=await UserService.create_for_admin(db, request))
  except IntegrityError as e:
    if "users_phone_number_key" in str(e.orig):
      return ResponseUtils.error(message="Пользователь с таким номером телефона уже существует.")
    return ResponseUtils.error(message="Произошла ошибка при создании пользователя.")
  except Exception as e:
    return ResponseUtils.error(message=str(e))

@router.put("/update-user/")
async def update_user(
  form_data: UpdateUserForm = Depends(UpdateUserForm.as_form),
  image: UploadFile = File(None),
  token: str = Header(alias="token"),
  db: AsyncSession = Depends(get_db)):

  image_url = None
  if image:
    filename = os.path.basename(image.filename)

    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
      return ResponseUtils.error(message="Только PNG и JPG изображения")

    save_dir = os.path.join("media", "avatars")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as f:
      content = await image.read()
      f.write(content)
    image_url = f"/media/avatars/{filename}"

  update_data = UpdateUserForm(**form_data.model_dump())
  update_data.image_url = image_url

  new_user = await UserService.update_user(db, token, update_data)
  if new_user:
    return ResponseUtils.success(user = new_user)
  else:
    return ResponseUtils.error(message="Не найден пользователь")

@router.put("/update-admin")
async def update_admin(user_data: UserPayloadWithId, token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin(token, db)

  res = await UserService.update_user_for_admin(db, user_data)
  if isinstance(res, dict):
    return res
  return ResponseUtils.success(user=res)

@router.delete("/delete-user/{user_id}")
async def delete_user(
    user_id: UUID,
    token:str=Header(None, alias="token"),
    db: AsyncSession = Depends(get_db))-> dict:
  if token is None and user_id is None:
    return ResponseUtils.error(message="Ошибка валидации, передайте одно значение")
  if user_id is not None:
    await SecurityMiddleware.is_admin(token, db)
    return ResponseUtils.success(res=await UserService.delete_user_by_id(db, user_id))
  else:
    return ResponseUtils.success(res=await UserService.delete_user_by_token(db, token))

@router.get("/get-user/")
async def get_user(token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  user = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if isinstance(user, dict):
    return user
  if user:
    return ResponseUtils.success(user=user)
  else:
    return ResponseUtils.error(message="Не найден пользователь")

@router.post("/logout/")
async def logout_route(token: str = Header(alias="token"), db: AsyncSession = Depends(get_db)):
  user = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if isinstance(user, dict):
    return user
  if user:
    await SecurityMiddleware.logout(token)
    return ResponseUtils.success(message="Вы успешно вышли из системы")
  else:
    return ResponseUtils.error(message="Не действительный токен")
