import jwt
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User, Roles
from fastapi import HTTPException, APIRouter
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
      "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

  @staticmethod
  async def get_user_or_error_dict(token: str, db: AsyncSession):
    if token in TOKEN_BLACKLIST:
      return ResponseUtils.error(message="Токен отозван")

    try:
      payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
      user_id = payload.get("user_id")
      if not user_id:
        return ResponseUtils.error(message="Недействительный токен")

      async with db as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
          return ResponseUtils.error(message="Пользователь не найден")

    except jwt.PyJWTError:
      return ResponseUtils.error(message="Недействительный токен")

    return user

  @staticmethod
  async def logout(token: str):
    TOKEN_BLACKLIST.add(token)
    return ResponseUtils.success(message="Токен успешно отозван")

  @staticmethod
  async def check_roles(token: str, db: AsyncSession, allowed_roles: set[Roles]):
    user = await SecurityMiddleware.get_user_or_error_dict(token, db)

    if isinstance(user, dict):
      return user

    if user.role not in allowed_roles:
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