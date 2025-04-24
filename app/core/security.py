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
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token

  @staticmethod
  async def get_current_user(token: str, db: AsyncSession):
    if token in TOKEN_BLACKLIST:
      return ResponseUtils.error(message="Токен отозван")

    try:
      payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
      user_id = payload.get("user_id")
      if user_id is None:
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
    return {"message": "Токен успешно отозван"}

  @staticmethod
  async def is_manager(token: str, db: AsyncSession):
    user = await SecurityMiddleware.get_current_user(token, db)
    return user.role == Roles.MANAGER

  @staticmethod
  async def is_admin(token: str, db: AsyncSession):
    user = await SecurityMiddleware.get_current_user(token, db)
    if not user:
      raise HTTPException(status_code=403, detail="Пользователь не найден")
    if user.role != Roles.ADMIN:
      raise HTTPException(status_code=403, detail="У вас недостаточно прав!")

  @staticmethod
  async def is_admin_or_manager(token: str, db: AsyncSession):
    user = await SecurityMiddleware.get_current_user(token, db)
    if not user:
      raise HTTPException(status_code=403, detail="Пользователь не найден")
    if user.role not in {Roles.ADMIN, Roles.MANAGER}:
      raise HTTPException(status_code=403, detail="У вас недостаточно прав!")

  @staticmethod
  async def is_admin_or_courier(token: str, db: AsyncSession):
    user = await SecurityMiddleware.get_current_user(token, db)
    if not user:
      raise HTTPException(status_code=403, detail="Пользователь не найден")
    if user.role not in {Roles.ADMIN, Roles.COURIER}:
      raise HTTPException(status_code=403, detail="У вас недостаточно прав!")
