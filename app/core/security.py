from typing import Union

import jwt
from datetime import datetime, timedelta, UTC
from uuid import UUID as UUID_PY
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User, Roles
from fastapi import APIRouter
from sqlalchemy import select

from app.core.config import settings
from app.services.response_utils import ResponseUtils

TOKEN_BLACKLIST = set()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SecurityMiddleware:
  @staticmethod
  def generate_jwt_token(user_id: str):
    payload = {
      "user_id": user_id,
      "exp": datetime.now(UTC) + timedelta(days=1)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

  @staticmethod
  async def get_user_or_error_dict(token: str, db: AsyncSession) -> Union[User, dict]:
    if token in TOKEN_BLACKLIST:
      return ResponseUtils.error(message="Токен отозван")


    try:
      payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=["HS256"]
      )
    except jwt.PyJWTError:
      return ResponseUtils.error(message="Недействительный токен")

    user_id_str = payload.get("user_id")
    if not isinstance(user_id_str, str):
      return ResponseUtils.error(message="Недействительный токен")

    try:
      user_uuid = UUID_PY(user_id_str)
    except ValueError:
      return ResponseUtils.error(message="Недействительный токен")

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
      return ResponseUtils.error(message="Пользователь не найден")

    return user

  @staticmethod
  async def logout(token: str):
    TOKEN_BLACKLIST.add(token)
    return ResponseUtils.success(message="Токен успешно отозван")

  @staticmethod
  async def check_roles(token: str, db: AsyncSession, allowed_roles: set[Roles]) -> Union[User, dict]:
    user_or_error = await SecurityMiddleware.get_user_or_error_dict(token, db)

    if isinstance(user_or_error, dict):
      return user_or_error

    user: User = user_or_error

    if user and user.role not in allowed_roles:
      return ResponseUtils.error(message="У вас недостаточно прав!")

    return user

  @staticmethod
  async def is_admin(token: str, db: AsyncSession):
    return await SecurityMiddleware.check_roles(token, db, {Roles.ADMIN})

  @staticmethod
  async def is_manager(token: str, db: AsyncSession):
    return await SecurityMiddleware.check_roles(token, db, {Roles.MANAGER})

  @staticmethod
  async def is_admin_or_manager(token: str, db: AsyncSession):
    return await SecurityMiddleware.check_roles(token, db, {Roles.ADMIN, Roles.MANAGER})

  @staticmethod
  async def is_admin_or_courier(token: str, db: AsyncSession):
    return await SecurityMiddleware.check_roles(token, db, {Roles.ADMIN, Roles.COURIER})